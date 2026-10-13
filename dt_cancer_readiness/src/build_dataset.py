"""Merge GBD burden, WDI and GHO indicators into one country-level analysis file.

Output: data/processed/analysis_country.csv  (one row per GBD country)
        outputs/tables/tableS1_indicator_coverage.csv
"""
import pandas as pd

from config import COVARIATES, INDICATORS, OPTIONAL_USER_INDICATORS, PROC, RAW, TAB, USER

MEASURES = {"DALYs": "daly", "Deaths": "deaths", "Incidence": "inc", "Prevalence": "prev"}


def _measure_key(m):
    return next((v for k, v in MEASURES.items() if str(m).startswith(k)), None)


def gbd_wide():
    g = pd.read_csv(PROC / "gbd_country.csv")
    year = g.year.max()
    g = g[g.year == year].copy()
    g["m"] = g.measure.map(_measure_key)
    g["age_std"] = g.age.str.lower().str.startswith("age-standardi")
    groups = [c for c in g.columns if c in
              ("dt_total", "all_cancer", "breast", "prostate", "lung", "colorectal",
               "brain_cns", "pancreas", "head_neck")]
    rows = []
    rate = g[(g.metric == "Rate") & g.age_std]
    num = g[(g.metric == "Number") & (g.age.str.lower() == "all ages")]
    for tag, sub in (("asr", rate), ("n", num)):
        for m in sub.m.dropna().unique():
            s = sub[sub.m == m].set_index("iso3")[groups]
            s.columns = [f"{m}_{tag}_{c}" for c in s.columns]
            rows.append(s)
    out = pd.concat(rows, axis=1)
    meta = g.drop_duplicates("iso3").set_index("iso3")[["location"] + (["sdi"] if "sdi" in g else [])]
    out = meta.join(out).reset_index()
    out["gbd_year"] = year
    return out


def indicator_wide():
    parts = []
    wb = pd.read_csv(RAW / "worldbank_long.csv")
    wb_latest = wb.sort_values("year").groupby(["iso3", "indicator"]).tail(1)
    code2key = {i["code"]: i["key"] for i in INDICATORS if i["source"] == "wb"}
    code2key.update({v: k for k, v in COVARIATES.items()})
    wb_latest = wb_latest.assign(key=wb_latest.indicator.map(code2key))
    parts.append(wb_latest[["iso3", "key", "year", "value"]])
    gho_f = RAW / "gho_long.csv"
    if gho_f.exists():
        gho = pd.read_csv(gho_f).rename(columns={"indicator": "key"})
        parts.append(gho[["iso3", "key", "year", "value"]])
    for ind in OPTIONAL_USER_INDICATORS:
        f = USER / f"{ind['key']}.csv"
        if f.exists():
            u = pd.read_csv(f).assign(key=ind["key"], year=pd.NA)
            parts.append(u[["iso3", "key", "year", "value"]])
    long = pd.concat(parts, ignore_index=True)
    vals = long.pivot_table(index="iso3", columns="key", values="value", aggfunc="first")
    years = long.pivot_table(index="iso3", columns="key", values="year", aggfunc="first")
    return vals, years


def main():
    burden = gbd_wide()
    vals, years = indicator_wide()
    countries = pd.read_csv(RAW / "worldbank_countries.csv")[["iso3", "region", "income"]]
    df = burden.merge(vals.reset_index(), on="iso3", how="left").merge(countries, on="iso3", how="left")
    df["region"] = df.region.fillna("Unclassified")
    df.to_csv(PROC / "analysis_country.csv", index=False)

    all_inds = INDICATORS + [i for i in OPTIONAL_USER_INDICATORS if i["key"] in vals.columns]
    cov = []
    for ind in all_inds:
        k = ind["key"]
        if k not in df:
            cov.append(dict(key=k, label=ind["label"], domain=ind["domain"], n=0))
            continue
        y = years.reindex(df.iso3)[k] if k in years else pd.Series(dtype=float)
        cov.append(dict(key=k, label=ind["label"], domain=ind["domain"], source=ind["source"],
                        n=int(df[k].notna().sum()), pct=round(100 * df[k].notna().mean(), 1),
                        year_min=pd.to_numeric(y, errors="coerce").min(),
                        year_max=pd.to_numeric(y, errors="coerce").max(),
                        median=df[k].median()))
    pd.DataFrame(cov).to_csv(TAB / "tableS1_indicator_coverage.csv", index=False)
    print(f"analysis file: {len(df)} countries, GBD year {df.gbd_year.iat[0]}")


if __name__ == "__main__":
    main()
