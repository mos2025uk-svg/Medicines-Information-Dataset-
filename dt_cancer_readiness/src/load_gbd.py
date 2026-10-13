"""Parse GBD Results Tool exports + SDI file into a country-level burden table.

Inputs (place in data/user_inputs/):
  gbd/*.csv   one or more GBD Results Tool CSV exports (see GBD_DOWNLOAD.md)
  sdi.csv     GBD SDI estimates (GHDx); columns incl. location name, year, SDI value
Output: data/processed/gbd_country.csv
  iso3, location_name, year, measure, metric, burden_<group> columns
"""
import re
import unicodedata

import pandas as pd
import pycountry

from config import ALL_CANCER_ALIASES, DT_CANCERS, PROC, USER

# GBD location names that pycountry does not resolve unambiguously.
MANUAL_ISO3 = {
    "Bolivia (Plurinational State of)": "BOL", "Venezuela (Bolivarian Republic of)": "VEN",
    "Iran (Islamic Republic of)": "IRN", "Micronesia (Federated States of)": "FSM",
    "Taiwan (Province of China)": "TWN", "Taiwan": "TWN", "Palestine": "PSE",
    "Democratic People's Republic of Korea": "PRK", "Republic of Korea": "KOR",
    "Lao People's Democratic Republic": "LAO", "Viet Nam": "VNM", "Russian Federation": "RUS",
    "Republic of Moldova": "MDA", "United Republic of Tanzania": "TZA",
    "Syrian Arab Republic": "SYR", "Cabo Verde": "CPV", "Eswatini": "SWZ",
    "North Macedonia": "MKD", "Czechia": "CZE", "Türkiye": "TUR", "Turkey": "TUR",
    "Côte d'Ivoire": "CIV", "Cote d'Ivoire": "CIV", "Congo": "COG",
    "Democratic Republic of the Congo": "COD", "United States of America": "USA",
    "United Kingdom": "GBR", "United States Virgin Islands": "VIR",
    "Saint Vincent and the Grenadines": "VCT", "Sao Tome and Principe": "STP",
    "São Tomé and Príncipe": "STP", "Gambia": "GMB", "Bahamas": "BHS", "Niger": "NER",
    "Brunei Darussalam": "BRN", "Timor-Leste": "TLS", "Kyrgyzstan": "KGZ",
}

SDI_QUINTILES = ["Low SDI", "Low-middle SDI", "Middle SDI", "High-middle SDI", "High SDI"]


def to_iso3(name):
    if name in MANUAL_ISO3:
        return MANUAL_ISO3[name]
    try:
        return pycountry.countries.lookup(name).alpha_3
    except LookupError:
        pass
    # exact lookup only: fuzzy matching would silently map region names
    plain = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    try:
        return pycountry.countries.lookup(plain).alpha_3
    except LookupError:
        return None


def _norm_cols(df):
    df = df.rename(columns=lambda c: c.strip().lower())
    # results tool exports either *_name columns or plain columns
    ren = {f"{k}_name": k for k in ("measure", "location", "sex", "age", "cause", "metric")}
    return df.rename(columns=ren)


def load_exports():
    files = sorted((USER / "gbd").glob("*.csv"))
    if not files:
        raise FileNotFoundError(f"No GBD exports in {USER/'gbd'} - see GBD_DOWNLOAD.md")
    df = pd.concat([_norm_cols(pd.read_csv(f)) for f in files], ignore_index=True)
    need = {"measure", "location", "sex", "age", "cause", "metric", "year", "val"}
    missing = need - set(df.columns)
    if missing:
        raise ValueError(f"GBD export missing columns: {missing}")
    df = df[df.sex.str.lower().isin(["both", "both sexes"])]
    return df.drop_duplicates(subset=list(need - {"val"}))


def burden_table(df):
    """Wide table per location/year/measure/metric/age with DT-applicable sum."""
    df = df.copy()
    df["group"] = df.cause.map(DT_CANCERS)
    df.loc[df.cause.isin(ALL_CANCER_ALIASES), "group"] = "all_cancer"
    df = df.dropna(subset=["group"])
    keys = ["location", "year", "measure", "metric", "age"]
    # age-standardised rates are additive across causes (same standard population)
    by_group = df.groupby(keys + ["group"], as_index=False)["val"].sum()
    wide = by_group.pivot_table(index=keys, columns="group", values="val").reset_index()
    dt_groups = sorted(set(DT_CANCERS.values()))
    present = [g for g in dt_groups if g in wide.columns]
    if set(present) != set(dt_groups):
        print(f"WARNING: DT cancer groups missing from export: {set(dt_groups) - set(present)}")
    wide["dt_total"] = wide[present].sum(axis=1, min_count=len(present))
    wide.columns.name = None
    return wide


def load_sdi():
    f = USER / "sdi.csv"
    if not f.exists():
        print("WARNING: data/user_inputs/sdi.csv not found - SDI analyses will use GDP rank")
        return None
    sdi = pd.read_csv(f)
    sdi.columns = [c.strip().lower() for c in sdi.columns]
    loc = next(c for c in sdi.columns if c in ("location_name", "location"))
    year_cols = [c for c in sdi.columns if re.fullmatch(r"\d{4}", c)]
    if year_cols:  # wide GHDx format: one column per year
        sdi = sdi.melt(id_vars=[loc], value_vars=year_cols, var_name="year", value_name="sdi")
    else:
        val = next(c for c in sdi.columns if c in ("mean_value", "sdi", "val", "value"))
        sdi = sdi.rename(columns={val: "sdi"})
    sdi = sdi.rename(columns={loc: "location"})
    sdi["year"] = sdi.year.astype(int)
    sdi["sdi"] = pd.to_numeric(sdi.sdi.astype(str).str.replace("·", "."), errors="coerce")
    return sdi[["location", "year", "sdi"]]


def main():
    df = load_exports()
    wide = burden_table(df)
    countries = wide[~wide.location.isin(SDI_QUINTILES + ["Global"])].copy()
    countries["iso3"] = countries.location.map(to_iso3)
    unmapped = sorted(countries.loc[countries.iso3.isna(), "location"].unique())
    if unmapped:
        print(f"Non-country / unmapped locations dropped ({len(unmapped)}): {unmapped}")
    countries = countries.dropna(subset=["iso3"])
    sdi = load_sdi()
    if sdi is not None:
        countries = countries.merge(sdi, on=["location", "year"], how="left")
        print(f"SDI matched for {countries.drop_duplicates('iso3').sdi.notna().sum()} countries")
    countries.to_csv(PROC / "gbd_country.csv", index=False)
    wide[wide.location.isin(SDI_QUINTILES + ["Global"])].to_csv(PROC / "gbd_aggregates.csv", index=False)
    print(f"{countries.iso3.nunique()} countries written")


if __name__ == "__main__":
    main()
