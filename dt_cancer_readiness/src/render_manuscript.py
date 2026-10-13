"""Fill manuscript_template.md with numbers from outputs/results.json.

Writes manuscript/manuscript.md and manuscript/manuscript.docx (via pandoc if
available). Unfilled placeholders are left as [[name]] so they are easy to spot.
"""
import json
import shutil
import subprocess

import numpy as np
import pandas as pd

from config import N_DRAWS, PROC, ROOT

MS = ROOT / "manuscript"


class Safe(dict):
    def __missing__(self, k):
        return f"[[{k}]]"


def f1(x):
    return f"{x:.1f}"


def ci_str(d):
    return f"{d['ci']:.3f} (95% CI {d['boot95'][0]:.3f} to {d['boot95'][1]:.3f})"


def beta_str(d):
    p = "p<0.001" if d["p"] < 0.001 else f"p={d['p']:.3f}"
    return f"{d['beta']:.2f} (95% CI {d['lo']:.2f} to {d['hi']:.2f}; {p})"


def names(lst, k=10):
    lst = list(lst)[:k]
    return ", ".join(lst[:-1]) + (", and " if len(lst) > 2 else " and ") + lst[-1] if len(lst) > 1 else "".join(lst)


def build_context():
    R = json.load(open(ROOT / "outputs" / "results.json"))
    meta = json.load(open(PROC / "dtri_meta.json"))
    df = pd.read_csv(PROC / "final_country.csv")
    c = Safe()
    c.update(n_countries=R["n_countries"], gbd_year=R["gbd_year"], n_indicators=len(meta["indicators"]),
             n_excluded=meta["n_excluded"], n_draws=N_DRAWS, n_complete_case=meta["n_complete_case"],
             pca_ev1=f1(100 * meta["pca_ev1"]), median_missing=f1(100 * df.missing_share.median()),
             dtri_min=f1(df.dtri.min()), dtri_max=f1(df.dtri.max()),
             burden_med=f"{df.daly_asr_dt_total.median():.0f}")
    fmt = lambda r: f"{r['location']} ({r['dtri']:.1f}, 95% UI {r['dtri_lo']:.1f}–{r['dtri_hi']:.1f})"
    c["dtri_top"] = names([fmt(r) for r in R["top_dtri"][:3]])
    c["dtri_bottom"] = names([fmt(r) for r in R["bottom_dtri"][:3]])

    sq = {r["sdi_q"]: r for r in R["by_sdi_quintile"]}
    meds = [sq[q]["dtri"] for q in ["Low", "Low-middle", "Middle", "High-middle", "High"] if q in sq]
    c["dtri_med_low"], c["dtri_med_high"] = f1(meds[0]), f1(meds[-1])
    c["sdi_trend_phrase"] = ("increased monotonically" if all(np.diff(meds) > 0)
                             else "increased" if meds[-1] > meds[0] else "did not increase")
    c["ci_dtri_sdi"] = ci_str(R["ci_dtri_by_sdi"])
    c["ci_burden"] = ci_str(R["ci_burden_by_dtri"])
    c["ci_burden_draws"] = "{:.3f} to {:.3f}".format(*R["ci_burden_by_dtri"]["dtri_draws95"])

    q = {r["dtri_q"]: r for r in R["by_dtri_quintile"]}
    for qq, tag in (("Q1", "q1"), ("Q5", "q5")):
        r = q[qq]
        c[f"{tag}_daly_share"] = f1(r["daly_n_dt_total_share"])
        c[f"{tag}_pop_share"] = f1(r["pop_share"])
        for dev in ("ct", "mri", "rt"):
            k = f"{dev}_pm_units_share"
            if k in r and r[k] == r[k]:
                c[f"{tag}_{dev}_share"] = f1(r[k])
    g = R["gini"]
    for dev in ("ct", "mri", "rt"):
        if f"{dev}_pm_units" in g:
            c[f"gini_{dev}"] = f"{g[f'{dev}_pm_units']:.2f}"
    c["gini_dtri"] = f"{g['dtri']:.2f}"

    h = R["hb_lr"]
    c.update(hb_lr_n=h["n"], hb_lr_pop=f"{h['pop_millions']:.0f}", hb_lr_share=f1(100 * h["share_global_dt_dalys"]),
             hb_lr_list=names(h["countries"], 50) if h["countries"] else "none")
    c["n_mismatch_robust"] = R["n_mismatch_robust"]
    c["top_mismatch"] = names([f"{r['location']} (MI {r['mismatch']:.0f}, 95% UI {r['mismatch_lo']:.0f} to {r['mismatch_hi']:.0f})"
                               for r in R["top_mismatch"][:10]])
    fr = R["frontier"]
    c["frontier_median_gap"] = f1(fr["median_gap"])
    c["frontier_top"] = names([f"{r['location']} ({r['frontier_gap']:.1f})" for r in fr["top_gap"][:5]])

    s = R["spearman_overall"]
    c["spearman_rho"] = f"{s['rho']:.2f}"
    c["spearman_p"] = "<0.001" if s["p"] < 0.001 else f"={s['p']:.3f}"
    mag = abs(s["rho"])
    strength = "weakly" if mag < 0.3 else "moderately" if mag < 0.6 else "strongly"
    c["spearman_phrase"] = ("not significantly" if s["p"] >= 0.05 else
                            f"{strength} {'positively' if s['rho'] > 0 else 'negatively'}")
    c["spearman_within"] = "; ".join(f"{k} {v:.2f}" for k, v in R["spearman_by_sdi_q"].items())

    m = R["models"]
    c.update(beta_unadj=beta_str(m["unadjusted"]), beta_mixed=beta_str(m["mixed_burden"]),
             beta_sdi=beta_str(m["mixed_sdi"]))
    mb = m["mixed_burden"]
    c["burden_assoc_phrase"] = ("not significantly associated" if mb["lo"] <= 0 <= mb["hi"] else
                                "positively associated" if mb["beta"] > 0 else "inversely associated")

    sens = {k: v for k, v in R["sensitivity"].items() if v}
    spec = [v for k, v in sens.items() if k.startswith("dtri_")]
    if spec:
        c["sens_min_rho"] = f"{min(v['rho'] for v in spec):.2f}"
        c["sens_min_overlap"] = int(min(v["top20_overlap"] for v in spec))
    if "daly_asr_all_cancer" in sens:
        c["sens_all_cancer_rho"] = f"{sens['daly_asr_all_cancer']['rho']:.2f}"
    return c


def main():
    tpl = (MS / "manuscript_template.md").read_text()
    ctx = build_context()
    out = tpl.format_map(ctx)
    (MS / "manuscript.md").write_text(out)
    left = sorted(set(__import__("re").findall(r"\[\[(\w+)\]\]", out)))
    if left:
        print("Unfilled placeholders:", left)
    if shutil.which("pandoc"):
        subprocess.run(["pandoc", str(MS / "manuscript.md"), "-o", str(MS / "manuscript.docx")], check=True)
    print("manuscript written to", MS)


if __name__ == "__main__":
    main()
