# Cancer burden vs Digital Twin readiness (204 countries, GBD)

Reproducible pipeline + manuscript for:
*Global mismatch between cancer burden and digital twin readiness across 204 countries and territories: an ecological analysis using Global Burden of Disease data.*

## Status
- Code: complete; tested end-to-end on **synthetic** fixtures only (no synthetic numbers are in the repo or manuscript).
- Data: not yet downloaded (see below).
- Manuscript: `manuscript/manuscript_template.md` — Introduction, Methods, Discussion, Limitations and references written; Abstract/Results numbers are filled automatically from `outputs/results.json` by `src/render_manuscript.py` -> `manuscript/manuscript.md` + `.docx`.

## Run
```bash
pip install -r requirements.txt
# 1. put GBD exports + SDI file in data/user_inputs/  (GBD_DOWNLOAD.md)
# 2. needs network access to api.worldbank.org, ghoapi.azureedge.net, raw.githubusercontent.com
./run_all.sh
```

## Pipeline
| Step | Script | Output |
|---|---|---|
| World Bank WDI (digital, health system, research, covariates) | `src/fetch_worldbank.py` | `data/raw/worldbank_long.csv` |
| WHO GHO (CT, MRI, PET, radiotherapy densities) | `src/fetch_who_gho.py` | `data/raw/gho_long.csv`, `gho_indicator_map.csv` |
| GBD exports -> country burden (DT-applicable cancers) | `src/load_gbd.py` | `data/processed/gbd_country.csv` |
| Merge | `src/build_dataset.py` | `analysis_country.csv`, Table S1 |
| DTRI (MICE m=20, geometric mean, 1000 MC draws) | `src/dtri.py` | `dtri_point.csv`, draws |
| Mismatch, concentration index, frontier, mixed models, sensitivity | `src/analysis.py` | Tables 1–4, S3, `results.json` |
| Figures 1–6 | `src/figures.py` | `outputs/figures/` |
| Manuscript | `src/render_manuscript.py` | `manuscript/manuscript.md/.docx` |

Settings (indicator list, cancers, draws) are in `src/config.py`.
