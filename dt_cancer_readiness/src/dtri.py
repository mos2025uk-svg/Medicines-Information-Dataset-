"""Construct the Digital Twin Readiness Index (DTRI) with uncertainty.

Steps
 1. transform indicators (log1p for skewed densities)
 2. exclude countries missing > MAX_MISSING_SHARE of indicators
 3. multiple imputation by chained equations (m = N_IMPUTATIONS, posterior draws),
    auxiliary predictors: log GDP per capita PPP, SDI
 4. rescale each indicator to 0-100 with winsorised goalposts (P2.5, P97.5)
 5. domain score = mean of its indicators; DTRI = geometric mean of domain scores
    (equal weights, primary) ; alternatives: arithmetic mean, PCA weights
 6. Monte Carlo: N_DRAWS draws over imputations x Dirichlet domain weights
Outputs: data/processed/dtri_point.csv, dtri_draws.npy, dtri_meta.json
"""
import json

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.experimental import enable_iterative_imputer  # noqa: F401
from sklearn.impute import IterativeImputer
from sklearn.linear_model import BayesianRidge

from config import (DOMAINS, INDICATORS, MAX_MISSING_SHARE, N_DRAWS, N_IMPUTATIONS,
                    OPTIONAL_USER_INDICATORS, PROC, SEED)

FLOOR = 1.0  # avoids zero in geometric mean


def indicator_specs(df):
    specs = [i for i in INDICATORS + OPTIONAL_USER_INDICATORS if i["key"] in df and df[i["key"]].notna().any()]
    return specs


def transform(df, specs):
    X = pd.DataFrame(index=df.index)
    for s in specs:
        x = pd.to_numeric(df[s["key"]], errors="coerce")
        X[s["key"]] = np.log1p(x.clip(lower=0)) if s["transform"] == "log1p" else x
    return X


def impute(X, aux, m, seed):
    """Return list of m imputed DataFrames (posterior sampling)."""
    Z = pd.concat([X, aux], axis=1)
    out = []
    for k in range(m):
        imp = IterativeImputer(estimator=BayesianRidge(), sample_posterior=True, max_iter=25,
                               random_state=seed + k, skip_complete=True)
        arr = imp.fit_transform(Z)
        out.append(pd.DataFrame(arr[:, : X.shape[1]], index=X.index, columns=X.columns))
    return out


def rescale(X, goalposts):
    S = pd.DataFrame(index=X.index)
    for c in X:
        lo, hi = goalposts[c]
        S[c] = (100 * (X[c].clip(lo, hi) - lo) / (hi - lo)) if hi > lo else 50.0
    return S


def domain_scores(S, specs):
    out = {}
    for d in DOMAINS:
        cols = [s["key"] for s in specs if s["domain"] == d and s["key"] in S]
        if cols:
            out[d] = S[cols].mean(axis=1)
    return pd.DataFrame(out)


def aggregate(D, w, method="geometric"):
    w = np.asarray(w, float) / np.sum(w)
    if method == "geometric":
        return np.exp((np.log(D.clip(lower=FLOOR)) * w).sum(axis=1))
    return (D * w).sum(axis=1)


def pca_weights(D):
    """Weights from squared loadings of PC1 on standardised domain scores."""
    Z = (D - D.mean()) / D.std(ddof=0)
    pc = PCA(n_components=1).fit(Z)
    load = pc.components_[0] ** 2
    return load / load.sum(), float(pc.explained_variance_ratio_[0])


def build(df, n_draws=N_DRAWS, m=N_IMPUTATIONS, seed=SEED):
    rng = np.random.default_rng(seed)
    specs = indicator_specs(df)
    X = transform(df, specs)
    miss = X.isna().mean(axis=1)
    keep = miss <= MAX_MISSING_SHARE
    X = X[keep]
    aux = pd.DataFrame(index=X.index)
    if "gdp_pc_ppp" in df:
        aux["log_gdp"] = np.log(pd.to_numeric(df.loc[X.index, "gdp_pc_ppp"], errors="coerce"))
    if "sdi" in df and df["sdi"].notna().any():
        aux["sdi"] = df.loc[X.index, "sdi"]
    aux = aux.loc[:, aux.notna().any()]

    imps = impute(X, aux, m, seed)
    # goalposts fixed from observed (non-imputed) data so they do not move across draws
    goal = {c: (np.nanpercentile(X[c], 2.5), np.nanpercentile(X[c], 97.5)) for c in X}
    Ds = [domain_scores(rescale(Xi, goal), specs) for Xi in imps]
    nd = Ds[0].shape[1]
    eq = np.ones(nd)

    D_mean = sum(Ds) / m
    point = pd.DataFrame(index=X.index)
    point["dtri"] = np.mean([aggregate(D, eq) for D in Ds], axis=0)
    point["dtri_arith"] = np.mean([aggregate(D, eq, "arithmetic") for D in Ds], axis=0)
    w_pca, ev = pca_weights(D_mean)
    point["dtri_pca"] = np.mean([aggregate(D, w_pca) for D in Ds], axis=0)
    for d in D_mean:
        point[f"dom_{d}"] = D_mean[d]
        # leave-one-domain-out
        others = [c for c in D_mean if c != d]
        point[f"dtri_drop_{d}"] = np.mean([aggregate(D[others], np.ones(nd - 1)) for D in Ds], axis=0)
    # complete-case (no imputation) where all indicators observed
    cc = X.notna().all(axis=1)
    point["complete_case"] = cc
    point["missing_share"] = miss[keep]

    draws = np.empty((n_draws, len(X)))
    for k in range(n_draws):
        w = rng.dirichlet(10 * eq)  # concentrated around equal weights
        draws[k] = aggregate(Ds[k % m], w)
    point["dtri_lo"] = np.percentile(draws, 2.5, axis=0)
    point["dtri_hi"] = np.percentile(draws, 97.5, axis=0)
    ranks = (-draws).argsort(axis=1).argsort(axis=1) + 1
    point["rank"] = point.dtri.rank(ascending=False, method="min").astype(int)
    point["rank_lo"] = np.percentile(ranks, 2.5, axis=0).astype(int)
    point["rank_hi"] = np.percentile(ranks, 97.5, axis=0).astype(int)

    meta = dict(n_countries=int(keep.sum()), n_excluded=int((~keep).sum()),
                excluded=df.loc[~keep, "iso3"].tolist() if "iso3" in df else [],
                indicators=[s["key"] for s in specs], domains=list(D_mean.columns),
                pca_weights=dict(zip(D_mean.columns, map(float, w_pca))), pca_ev1=ev,
                n_complete_case=int(cc.sum()),
                goalposts={k: [float(a), float(b)] for k, (a, b) in goal.items()})
    return point, draws, meta


def main():
    df = pd.read_csv(PROC / "analysis_country.csv")
    point, draws, meta = build(df)
    out = df[["iso3", "location"]].join(point, how="inner")
    out.to_csv(PROC / "dtri_point.csv", index=False)
    np.save(PROC / "dtri_draws.npy", draws)
    json.dump(meta, open(PROC / "dtri_meta.json", "w"), indent=2)
    print(f"DTRI built for {meta['n_countries']} countries ({meta['n_excluded']} excluded)")


if __name__ == "__main__":
    main()
