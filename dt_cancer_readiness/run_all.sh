#!/usr/bin/env bash
# Full pipeline. Requires network access to api.worldbank.org, ghoapi.azureedge.net,
# raw.githubusercontent.com and the GBD exports in data/user_inputs/ (see GBD_DOWNLOAD.md).
set -euo pipefail
cd "$(dirname "$0")/src"
python3 fetch_worldbank.py
python3 fetch_who_gho.py
python3 load_gbd.py
python3 build_dataset.py
python3 dtri.py
python3 analysis.py
python3 figures.py
python3 render_manuscript.py
