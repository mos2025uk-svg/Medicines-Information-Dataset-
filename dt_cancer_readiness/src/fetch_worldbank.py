"""Download World Bank WDI indicators (most recent value in LOOKBACK window).

Output: data/raw/worldbank_long.csv (iso3, indicator, year, value)
        data/raw/worldbank_countries.csv (iso3, name, region, income)
"""
import time

import pandas as pd
import requests

from config import COVARIATES, INDICATORS, LOOKBACK, RAW

API = "https://api.worldbank.org/v2"


def _get(url, params):
    for attempt in range(5):
        try:
            r = requests.get(url, params=params, timeout=60)
            r.raise_for_status()
            return r.json()
        except Exception as exc:  # network/proxy errors
            if attempt == 4:
                raise RuntimeError(f"World Bank API failed for {url}: {exc}") from exc
            time.sleep(2 ** (attempt + 1))


def fetch_countries():
    js = _get(f"{API}/country", {"format": "json", "per_page": 400})
    rows = [
        dict(iso3=c["id"], name=c["name"], region=c["region"]["value"],
             income=c["incomeLevel"]["value"])
        for c in js[1] if c["region"]["value"] != "Aggregates"
    ]
    return pd.DataFrame(rows)


def fetch_indicator(code):
    params = {"format": "json", "per_page": 20000, "date": f"{LOOKBACK[0]}:{LOOKBACK[1]}"}
    js = _get(f"{API}/country/all/indicator/{code}", params)
    if len(js) < 2 or js[1] is None:
        return pd.DataFrame(columns=["iso3", "indicator", "year", "value"])
    return pd.DataFrame(
        [dict(iso3=d["countryiso3code"], indicator=code, year=int(d["date"]), value=d["value"])
         for d in js[1] if d["value"] is not None and d["countryiso3code"]]
    )


def main():
    codes = [i["code"] for i in INDICATORS if i["source"] == "wb"] + list(COVARIATES.values())
    countries = fetch_countries()
    countries.to_csv(RAW / "worldbank_countries.csv", index=False)
    frames = []
    for code in codes:
        df = fetch_indicator(code)
        print(f"{code}: {df.iso3.nunique()} countries")
        frames.append(df)
    long = pd.concat(frames, ignore_index=True)
    long = long[long.iso3.isin(countries.iso3)]
    long.to_csv(RAW / "worldbank_long.csv", index=False)


if __name__ == "__main__":
    main()
