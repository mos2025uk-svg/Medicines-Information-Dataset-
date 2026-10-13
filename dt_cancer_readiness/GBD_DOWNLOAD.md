# GBD data download (GBD Results Tool)

GBD data require a free IHME login, so this step must be done by a GBD collaborator.
URL: https://vizhub.healthdata.org/gbd-results/

## Download 1 — burden (save every CSV in `data/user_inputs/gbd/`)

| Field | Selection |
|---|---|
| GBD estimate | Cause of death or injury |
| Measure | DALYs, Deaths, Incidence |
| Metric | Number **and** Rate |
| Cause | Total cancers (in GBD 2021: Neoplasms); Breast cancer; Prostate cancer; Tracheal, bronchus, and lung cancer; Colon and rectum cancer; Brain and central nervous system cancer; Pancreatic cancer; Lip and oral cavity cancer; Nasopharynx cancer; Other pharynx cancer; Larynx cancer |
| Location | All countries and territories (204) + Global + the 5 SDI quintiles |
| Age | Age-standardized **and** All ages |
| Sex | Both |
| Year | 2023 (latest available) — optionally also 1990 for trends |

Download in CSV format with **names** (not IDs only). If the file is very large it may be split across several CSVs; that's fine, put all of them in the folder.

## Download 2 — SDI

GHDx → "Global Burden of Disease Study 2023 (GBD 2023) Socio-Demographic Index (SDI)" → CSV.
Save it as `data/user_inputs/sdi.csv`. Both the wide format (one column per year) and the long format are supported.

## Optional

- `data/user_inputs/ehr_national.csv` (columns `iso3,value`): national EHR system from the WHO Global Observatory for eHealth / Global Digital Health Monitor
- `data/user_inputs/genomic_seq.csv` (columns `iso3,value`): genomic sequencing capacity score

## Data-use note
Under the IHME Free-of-Charge Non-commercial User Agreement, raw GBD data must not be redistributed in the public repository. `data/user_inputs/` is listed in `.gitignore`.
