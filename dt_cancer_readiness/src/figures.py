"""Publication figures (PNG 300 dpi + PDF).

 Fig 1  World maps: DTRI and DT-applicable cancer DALY ASR
 Fig 2  Bivariate 3x3 choropleth: burden x readiness (headline figure)
 Fig 3  Scatter DTRI vs burden, coloured by SDI quintile, tertile guides
 Fig 4  Concentration curve of DT-applicable DALYs ranked by DTRI
 Fig 5  Readiness frontier on SDI
 Fig 6  Top-30 mismatch countries with 95% UI
"""
import json

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from config import FIG, PROC, RAW, ROOT

NE_URL = ("https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/"
          "geojson/ne_110m_admin_0_countries.geojson")
BURDEN = "daly_asr_dt_total"
SDI_COL = {"Low": "#b2182b", "Low-middle": "#ef8a62", "Middle": "#bababa",
           "High-middle": "#67a9cf", "High": "#2166ac"}
# Stevens 3x3 bivariate palette: rows = burden tertile (1..3), cols = readiness tertile (1..3)
BIVAR = {(1, 1): "#e8e8e8", (1, 2): "#b5c0da", (1, 3): "#6c83b5",
         (2, 1): "#dfb0d6", (2, 2): "#a5add3", (2, 3): "#5698b9",
         (3, 1): "#be64ac", (3, 2): "#8c62aa", (3, 3): "#3b4994"}

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.spines.top": False,
                     "axes.spines.right": False})


def world():
    f = RAW / "ne_110m_countries.geojson"
    if not f.exists():
        gpd.read_file(NE_URL).to_file(f, driver="GeoJSON")
    w = gpd.read_file(f)
    w["iso3"] = w["ISO_A3"].where(w["ISO_A3"] != "-99", w["ADM0_A3"])
    w.loc[w.ADMIN == "France", "iso3"] = "FRA"
    w.loc[w.ADMIN == "Norway", "iso3"] = "NOR"
    w.loc[w.ADMIN == "Kosovo", "iso3"] = "XKX"
    return w[w.ADMIN != "Antarctica"].to_crs("ESRI:54030")  # Robinson


def save(fig, name):
    fig.savefig(FIG / f"{name}.png", dpi=300, bbox_inches="tight")
    fig.savefig(FIG / f"{name}.pdf", bbox_inches="tight")
    plt.close(fig)


def fig1(df, w):
    m = w.merge(df, on="iso3", how="left")
    fig, axes = plt.subplots(2, 1, figsize=(9, 9))
    for ax, col, title, cmap in ((axes[0], "dtri", "A  Digital Twin Readiness Index (0-100)", "viridis"),
                                 (axes[1], BURDEN, "B  DT-applicable cancer DALYs, age-standardised per 100 000", "magma_r")):
        m.plot(column=col, ax=ax, cmap=cmap, legend=True, edgecolor="white", linewidth=0.2,
               missing_kwds=dict(color="#dddddd", hatch="///", edgecolor="white", label="No data"),
               legend_kwds=dict(shrink=0.6, orientation="horizontal", pad=0.02))
        ax.set_title(title, loc="left", fontweight="bold")
        ax.set_axis_off()
    save(fig, "fig1_maps")


def fig2(df, w):
    m = w.merge(df, on="iso3", how="left")
    m["col"] = [BIVAR.get((b, r), "#dddddd") if pd.notna(b) else "#dddddd"
                for b, r in zip(m.burden_t, m.dtri_t)]
    fig = plt.figure(figsize=(10, 5.6))
    ax = fig.add_axes([0, 0, 1, 1])
    m.plot(color=m.col, ax=ax, edgecolor="white", linewidth=0.2)
    ax.set_axis_off()
    lg = fig.add_axes([0.04, 0.12, 0.13, 0.22])
    for (b, r), c in BIVAR.items():
        lg.add_patch(plt.Rectangle((r - 1, b - 1), 1, 1, color=c))
    lg.set_xlim(0, 3); lg.set_ylim(0, 3)
    lg.set_xticks([]); lg.set_yticks([])
    lg.set_xlabel("Readiness →", fontsize=8); lg.set_ylabel("Burden →", fontsize=8)
    lg.text(0.5, 2.5, "★", ha="center", va="center", fontsize=10)
    for s in lg.spines.values():
        s.set_visible(False)
    fig.suptitle("Mismatch between DT-applicable cancer burden and digital twin readiness  "
                 "(★ = high burden, low readiness)", x=0.02, ha="left", fontweight="bold")
    save(fig, "fig2_bivariate_map")


def fig3(df):
    fig, ax = plt.subplots(figsize=(7, 5.5))
    for q, c in SDI_COL.items():
        s = df[df.sdi_q == q]
        ax.scatter(s.dtri, s[BURDEN], s=np.sqrt(s["pop"]) / 60 + 6, c=c, alpha=0.8,
                   edgecolor="white", linewidth=0.4, label=f"{q} SDI")
    for v in df.dtri.quantile([1 / 3, 2 / 3]):
        ax.axvline(v, color="grey", ls=":", lw=0.8)
    for v in df[BURDEN].quantile([1 / 3, 2 / 3]):
        ax.axhline(v, color="grey", ls=":", lw=0.8)
    for _, r in df.nsmallest(12, "mismatch_rank").iterrows():
        ax.annotate(r.location, (r.dtri, r[BURDEN]), fontsize=6.5, xytext=(3, 2), textcoords="offset points")
    ax.set_yscale("log")
    ax.set_xlabel("Digital Twin Readiness Index")
    ax.set_ylabel("DT-applicable cancer DALYs per 100 000 (age-standardised, log)")
    from matplotlib.lines import Line2D
    handles = [Line2D([], [], marker="o", ls="", color=c, ms=6, label=f"{q} SDI") for q, c in SDI_COL.items()]
    ax.legend(handles=handles, frameon=False, fontsize=7, loc="lower right", title="Point size ∝ √population",
              title_fontsize=7)
    save(fig, "fig3_scatter")


def fig4(res):
    cc = pd.read_csv(ROOT / "outputs" / "tables" / "conc_curve_burden_by_dtri.csv")
    ci = res["ci_burden_by_dtri"]
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.plot([0, 1], [0, 1], color="grey", lw=0.8, ls="--", label="Line of equality")
    ax.plot(cc.cum_pop, cc.cum_burden, color="#b2182b", lw=1.8, label="Concentration curve")
    ax.set_xlabel("Cumulative population share, ranked by DTRI (lowest → highest)")
    ax.set_ylabel("Cumulative share of DT-applicable cancer DALYs")
    ax.text(0.55, 0.12, f"CI = {ci['ci']:.3f}\n(95% CI {ci['boot95'][0]:.3f} to {ci['boot95'][1]:.3f})",
            fontsize=8)
    ax.legend(frameon=False, loc="upper left", fontsize=8)
    save(fig, "fig4_concentration_curve")


def fig5(df, res):
    x = res["sdi_var"]
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(df[x], df.dtri, s=12, c=[SDI_COL[q] for q in df.sdi_q], alpha=0.8)
    s = df.sort_values(x)
    ax.plot(s[x], s.frontier, color="black", lw=1.5, label="Readiness frontier (90th percentile)")
    for _, r in df.nlargest(10, "frontier_gap").iterrows():
        ax.annotate(r.location, (r[x], r.dtri), fontsize=6.5, xytext=(3, -6), textcoords="offset points")
    ax.set_xlabel("Socio-demographic Index" if x == "sdi" else "GDP per capita (PPP)")
    ax.set_ylabel("Digital Twin Readiness Index")
    ax.legend(frameon=False, fontsize=8)
    save(fig, "fig5_frontier")


def fig6(df):
    top = df.nsmallest(30, "mismatch_rank").iloc[::-1]
    fig, ax = plt.subplots(figsize=(6, 8))
    y = np.arange(len(top))
    ax.errorbar(top.mismatch, y, xerr=[top.mismatch - top.mismatch_lo, top.mismatch_hi - top.mismatch],
                fmt="o", color="#b2182b", ecolor="#999999", ms=4, capsize=0)
    ax.axvline(0, color="grey", lw=0.8)
    ax.set_yticks(y, top.location, fontsize=7)
    ax.set_xlabel("Mismatch index (burden percentile − readiness percentile), 95% UI")
    save(fig, "fig6_top_mismatch")


def main():
    df = pd.read_csv(PROC / "final_country.csv")
    res = json.load(open(ROOT / "outputs" / "results.json"))
    try:
        w = world()
        fig1(df, w)
        fig2(df, w)
    except Exception as exc:
        print(f"Maps skipped: {exc}")
    fig3(df)
    fig4(res)
    fig5(df, res)
    fig6(df)
    print("figures written to", FIG)


if __name__ == "__main__":
    main()
