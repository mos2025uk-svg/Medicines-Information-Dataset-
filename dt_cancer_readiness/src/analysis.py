"""Burden-readiness mismatch analyses.

 A. Mismatch index (MI) = percentile(DT-applicable DALY ASR) - percentile(DTRI), with UI
 B. 3x3 bivariate classification (tertiles) -> 'high burden / low readiness' countries
 C. Distributional: share of global DT-applicable DALYs vs share of imaging/RT units
    by DTRI quintile; Gini of readiness capacity
 D. Concentration indices (population-weighted, bootstrap CI)
      - DT-applicable DALY rate ranked by DTRI
      - DTRI ranked by SDI
 E. Frontier: 90th-percentile quantile regression of DTRI on SDI (B-spline),
    readiness gap = frontier - observed
 F. Mixed model: z(DTRI) ~ z(log DALY ASR) + z(SDI) + (1 | World Bank region);
    Spearman correlations overall / within SDI quintile
 G. Sensitivity: alternative aggregation, leave-one-domain-out, alternative burden
    measures (deaths, incidence, all cancers), complete-case
Output: outputs/tables/*.csv, outputs/results.json, data/processed/final_country.csv
"""
import json
import warnings

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats

from config import PROC, ROOT, SEED, TAB

warnings.filterwarnings("ignore", category=FutureWarning)
rng = np.random.default_rng(SEED)
SDI_Q = ["Low", "Low-middle", "Middle", "High-middle", "High"]


def pct(x):
    return 100 * stats.rankdata(x, nan_policy="omit") / np.sum(~np.isnan(x))


def conc_index(h, rank_var, w):
    """Weighted concentration index (Wagstaff): 2*cov_w(h, R)/mean_w(h)."""
    h, rank_var, w = map(np.asarray, (h, rank_var, w))
    o = np.argsort(rank_var, kind="mergesort")
    h, w = h[o], w[o] / w.sum()
    R = np.cumsum(w) - w / 2
    mu = np.sum(w * h)
    return 2 * np.sum(w * (h - mu) * (R - np.sum(w * R))) / mu


def conc_curve(h, rank_var, w):
    o = np.argsort(rank_var, kind="mergesort")
    hw = (np.asarray(h) * np.asarray(w))[o]
    ww = np.asarray(w)[o]
    return np.r_[0, np.cumsum(ww) / ww.sum()], np.r_[0, np.cumsum(hw) / hw.sum()]


def boot_ci(fn, n, B=1000):
    vals = [fn(rng.integers(0, n, n)) for _ in range(B)]
    return np.percentile(vals, [2.5, 97.5]).tolist()


def gini(x, w):
    o = np.argsort(x)
    x, w = np.asarray(x)[o], np.asarray(w)[o]
    cw = np.cumsum(w) / w.sum()
    cx = np.cumsum(x * w) / np.sum(x * w)
    return 1 - np.sum((cx[1:] + cx[:-1]) * np.diff(cw)) - cx[0] * cw[0]


def main():
    base = pd.read_csv(PROC / "analysis_country.csv")
    dt = pd.read_csv(PROC / "dtri_point.csv")
    draws = np.load(PROC / "dtri_draws.npy")
    df = dt.merge(base.drop(columns=["location"]), on="iso3", how="left")
    burden = "daly_asr_dt_total"
    df = df[df[burden].notna()].copy()
    keep_idx = df.index.to_numpy()  # dt rows align with draws columns
    draws = draws[:, keep_idx]
    df = df.reset_index(drop=True)
    has_sdi = "sdi" in df and df.sdi.notna().sum() > 0.8 * len(df)
    sdi_var = "sdi" if has_sdi else "gdp_pc_ppp"
    df["sdi_q"] = pd.qcut(df[sdi_var].rank(method="first"), 5, labels=SDI_Q)
    df["pop"] = df["pop"].fillna(df["pop"].median())
    R = {"n_countries": len(df), "gbd_year": int(df.gbd_year.iat[0]), "sdi_var": sdi_var}

    # A. mismatch index with uncertainty
    b_pct = pct(df[burden].to_numpy())
    df["burden_pct"] = b_pct
    df["dtri_pct"] = pct(df.dtri.to_numpy())
    df["mismatch"] = df.burden_pct - df.dtri_pct
    mi_draws = np.array([b_pct - pct(d) for d in draws])
    df["mismatch_lo"], df["mismatch_hi"] = np.percentile(mi_draws, [2.5, 97.5], axis=0)
    df["mismatch_rank"] = df.mismatch.rank(ascending=False, method="min").astype(int)
    df["mismatch_robust"] = df.mismatch_lo > 0

    # B. bivariate tertiles
    df["burden_t"] = pd.qcut(df[burden], 3, labels=[1, 2, 3]).astype(int)
    df["dtri_t"] = pd.qcut(df.dtri, 3, labels=[1, 2, 3]).astype(int)
    df["hb_lr"] = (df.burden_t == 3) & (df.dtri_t == 1)
    hb = df[df.hb_lr]
    R["hb_lr"] = dict(n=len(hb), countries=hb.sort_values("mismatch", ascending=False).location.tolist(),
                      pop_millions=float(hb["pop"].sum() / 1e6),
                      share_global_dt_dalys=float(hb.daly_n_dt_total.sum() / df.daly_n_dt_total.sum()))

    # C. distribution of burden vs capacity by DTRI quintile
    df["dtri_q"] = pd.qcut(df.dtri.rank(method="first"), 5, labels=[f"Q{i}" for i in range(1, 6)])
    for k in ("ct_pm", "mri_pm", "rt_pm"):
        if k in df:
            df[f"{k}_units"] = df[k] * df["pop"] / 1e6
    agg = {"daly_n_dt_total": "sum", "pop": "sum", "iso3": "count", "dtri": "median",
           burden: "median"}
    agg.update({c: "sum" for c in df if c.endswith("_units")})
    tq = df.groupby("dtri_q", observed=True).agg(agg).rename(columns={"iso3": "n_countries"})
    for c in ["daly_n_dt_total", "pop"] + [c for c in df if c.endswith("_units")]:
        tq[f"{c}_share"] = 100 * tq[c] / tq[c].sum()
    tq.to_csv(TAB / "table2_by_dtri_quintile.csv")
    R["by_dtri_quintile"] = tq.reset_index().to_dict(orient="records")
    unit_cols = [c for c in df if c.endswith("_units")]
    # observed device data only (no zero-filling of missing countries)
    R["gini"] = {c: float(gini(df.loc[df[c].notna(), c] / df.loc[df[c].notna(), "pop"],
                               df.loc[df[c].notna(), "pop"])) for c in unit_cols}
    R["gini"]["dtri"] = float(gini(df.dtri, df["pop"]))

    # D. concentration indices
    w = df["pop"].to_numpy()
    h = df[burden].to_numpy()
    n = len(df)
    ci1 = conc_index(h, df.dtri, w)
    ci1_ci = boot_ci(lambda i: conc_index(h[i], df.dtri.to_numpy()[i], w[i]), n)
    ci2 = conc_index(df.dtri.to_numpy(), df[sdi_var].to_numpy(), w)
    ci2_ci = boot_ci(lambda i: conc_index(df.dtri.to_numpy()[i], df[sdi_var].to_numpy()[i], w[i]), n)
    ci_draws = [conc_index(h, d, w) for d in draws[:200]]
    R["ci_burden_by_dtri"] = dict(ci=ci1, boot95=ci1_ci, dtri_draws95=np.percentile(ci_draws, [2.5, 97.5]).tolist())
    R["ci_dtri_by_sdi"] = dict(ci=ci2, boot95=ci2_ci)
    x, y = conc_curve(h, df.dtri, w)
    pd.DataFrame({"cum_pop": x, "cum_burden": y}).to_csv(TAB / "conc_curve_burden_by_dtri.csv", index=False)

    # E. frontier
    fr = smf.quantreg(f"dtri ~ bs({sdi_var}, df=4, degree=3)", df).fit(q=0.9, max_iter=5000)
    df["frontier"] = fr.predict(df)
    df["frontier_gap"] = (df.frontier - df.dtri).clip(lower=0)
    R["frontier"] = dict(median_gap=float(df.frontier_gap.median()),
                         median_gap_by_sdi_q=df.groupby("sdi_q", observed=True).frontier_gap.median().to_dict(),
                         top_gap=df.nlargest(15, "frontier_gap")[["location", "frontier_gap"]].to_dict("records"))

    # F. association models
    m = df.assign(z_dtri=stats.zscore(df.dtri), z_burden=stats.zscore(np.log(df[burden])),
                  z_sdi=stats.zscore(df[sdi_var] if has_sdi else np.log(df[sdi_var])))
    ols = smf.ols("z_dtri ~ z_burden + z_sdi", m).fit(cov_type="HC3")
    ols_u = smf.ols("z_dtri ~ z_burden", m).fit(cov_type="HC3")
    mix = smf.mixedlm("z_dtri ~ z_burden + z_sdi", m, groups=m["region"]).fit(reml=True)
    coef = lambda f, t: dict(beta=float(f.params[t]), lo=float(f.conf_int().loc[t, 0]),
                             hi=float(f.conf_int().loc[t, 1]), p=float(f.pvalues[t]))
    R["models"] = dict(unadjusted=coef(ols_u, "z_burden"), ols_adj_burden=coef(ols, "z_burden"),
                       ols_adj_sdi=coef(ols, "z_sdi"), mixed_burden=coef(mix, "z_burden"),
                       mixed_sdi=coef(mix, "z_sdi"), ols_r2=float(ols.rsquared))
    pd.concat({"unadjusted": ols_u.summary2().tables[1], "ols_adjusted": ols.summary2().tables[1],
               "mixed": mix.summary().tables[1]}).to_csv(TAB / "table3_models.csv")
    rho, p = stats.spearmanr(df.dtri, df[burden])
    R["spearman_overall"] = dict(rho=float(rho), p=float(p))
    R["spearman_by_sdi_q"] = {str(q): float(stats.spearmanr(g.dtri, g[burden])[0])
                              for q, g in df.groupby("sdi_q", observed=True) if len(g) > 4}

    # G. sensitivity: rank agreement of mismatch under alternatives
    sens = {}
    def mis(dtri_col=None, burden_col=burden, sub=None):
        d = df if sub is None else df[sub]
        bb = d[burden_col].to_numpy()
        ok = ~np.isnan(bb)
        mm = pct(bb[ok]) - pct(d[dtri_col or "dtri"].to_numpy()[ok])
        prim = d.mismatch.to_numpy()[ok]
        top_p = set(d.iso3.to_numpy()[ok][np.argsort(-prim)[:20]])
        top_a = set(d.iso3.to_numpy()[ok][np.argsort(-mm)[:20]])
        return dict(rho=float(stats.spearmanr(prim, mm)[0]), top20_overlap=len(top_p & top_a), n=int(ok.sum()))
    for col in [c for c in df if c.startswith("dtri_drop_")] + ["dtri_arith", "dtri_pca"]:
        sens[col] = mis(dtri_col=col)
    for bcol in ("deaths_asr_dt_total", "inc_asr_dt_total", "daly_asr_all_cancer"):
        if bcol in df:
            sens[bcol] = mis(burden_col=bcol)
    sens["complete_case"] = mis(sub=df.complete_case.astype(bool)) if df.complete_case.sum() > 20 else None
    R["sensitivity"] = sens
    pd.DataFrame(sens).T.to_csv(TAB / "table4_sensitivity.csv")

    # Table 1: summary by SDI quintile
    cols = {"dtri": "median"} | {c: "median" for c in df if c.startswith("dom_")} | {
        burden: "median", "daly_n_dt_total": "sum", "pop": "sum", "iso3": "count", "hb_lr": "sum"}
    t1 = df.groupby("sdi_q", observed=True).agg(cols).rename(columns={"iso3": "n_countries"})
    t1.to_csv(TAB / "table1_by_sdi_quintile.csv")
    R["by_sdi_quintile"] = t1.reset_index().to_dict(orient="records")

    # Supplementary country table
    keep = ["location", "iso3", "region", sdi_var, "sdi_q", "dtri", "dtri_lo", "dtri_hi", "rank",
            "rank_lo", "rank_hi"] + [c for c in df if c.startswith("dom_")] + [
            burden, "daly_n_dt_total", "mismatch", "mismatch_lo", "mismatch_hi", "mismatch_rank",
            "hb_lr", "frontier_gap", "missing_share"]
    df.sort_values("mismatch", ascending=False)[keep].to_csv(TAB / "tableS3_country_results.csv", index=False)
    R["top_mismatch"] = df.nsmallest(20, "mismatch_rank")[
        ["location", "mismatch", "mismatch_lo", "mismatch_hi", "dtri", burden]].to_dict("records")
    R["top_dtri"] = df.nsmallest(10, "rank")[["location", "dtri", "dtri_lo", "dtri_hi"]].to_dict("records")
    R["bottom_dtri"] = df.nlargest(10, "rank")[["location", "dtri", "dtri_lo", "dtri_hi"]].to_dict("records")
    R["n_mismatch_robust"] = int(df.mismatch_robust.sum())
    df.to_csv(PROC / "final_country.csv", index=False)
    json.dump(R, open(ROOT / "outputs" / "results.json", "w"), indent=2, default=str)
    print(json.dumps({k: R[k] for k in ("n_countries", "ci_burden_by_dtri", "models")}, indent=1, default=str))


if __name__ == "__main__":
    main()
