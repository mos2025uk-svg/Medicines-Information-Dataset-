"""Download WHO Global Health Observatory indicators matched by name pattern.

Indicator codes are resolved from the GHO catalogue at run time and written to
data/raw/gho_indicator_map.csv so the exact codes used are auditable.
Output: data/raw/gho_long.csv (iso3, indicator, year, value)
"""
import re
import time

import pandas as pd
import requests

from config import INDICATORS, RAW

API = "https://ghoapi.azureedge.net/api"


def _get(url, params=None):
    for attempt in range(5):
        try:
            r = requests.get(url, params=params, timeout=90)
            r.raise_for_status()
            return r.json()["value"]
        except Exception as exc:
            if attempt == 4:
                raise RuntimeError(f"WHO GHO API failed for {url}: {exc}") from exc
            time.sleep(2 ** (attempt + 1))


def main():
    catalogue = pd.DataFrame(_get(f"{API}/Indicator"))
    catalogue.to_csv(RAW / "gho_catalogue.csv", index=False)
    mapping, frames = [], []
    for ind in (i for i in INDICATORS if i["source"] == "gho"):
        patterns = ind["pattern"] if isinstance(ind["pattern"], list) else [ind["pattern"]]
        hits = catalogue.iloc[0:0]
        for pat in patterns:  # first pattern with matches wins
            hits = catalogue[catalogue.IndicatorName.str.contains(pat, flags=re.I, regex=True, na=False)]
            if not hits.empty:
                break
        if hits.empty:
            print(f"WARNING: no GHO indicator matches {ind['key']} ({ind['pattern']})")
            continue
        if len(hits) > 1:
            print(f"NOTE: {ind['key']} matched {len(hits)} indicators; summing densities:")
        codes = hits.IndicatorCode.tolist()
        for code, name in zip(codes, hits.IndicatorName):
            print(f"  {ind['key']} <- {code}: {name}")
            mapping.append(dict(key=ind["key"], code=code, name=name))
        parts = []
        for code in codes:
            vals = pd.DataFrame(_get(f"{API}/{code}", {"$filter": "SpatialDimType eq 'COUNTRY'"}))
            if vals.empty:
                continue
            parts.append(vals[["SpatialDim", "TimeDim", "NumericValue"]].dropna())
        if not parts:
            continue
        # most recent year per country per code, then sum across codes
        # (e.g. linear accelerators + telecobalt = radiotherapy units)
        latest = [p.sort_values("TimeDim").groupby("SpatialDim").tail(1) for p in parts]
        df = (pd.concat(latest).groupby("SpatialDim")
              .agg(year=("TimeDim", "max"), value=("NumericValue", "sum")).reset_index()
              .rename(columns={"SpatialDim": "iso3"}))
        df["indicator"] = ind["key"]
        frames.append(df)
    pd.DataFrame(mapping).to_csv(RAW / "gho_indicator_map.csv", index=False)
    pd.concat(frames, ignore_index=True).to_csv(RAW / "gho_long.csv", index=False)


if __name__ == "__main__":
    main()
