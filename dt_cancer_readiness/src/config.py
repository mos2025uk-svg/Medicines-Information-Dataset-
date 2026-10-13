"""Central configuration: indicators, cancer causes, paths, analysis settings."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROC = ROOT / "data" / "processed"
USER = ROOT / "data" / "user_inputs"
FIG = ROOT / "outputs" / "figures"
TAB = ROOT / "outputs" / "tables"
for p in (RAW, PROC, USER, FIG, TAB):
    p.mkdir(parents=True, exist_ok=True)

SEED = 20261013
N_DRAWS = 1000          # Monte Carlo draws (weights x imputation)
N_IMPUTATIONS = 20      # multiple imputation datasets
MAX_MISSING_SHARE = 0.5 # countries missing > 50% of DTRI indicators are excluded
LOOKBACK = (2015, 2024) # most-recent-value window for covariates

# ---------------------------------------------------------------------------
# Cancers with established digital-twin applications (primary burden outcome).
# Names follow GBD cause hierarchy (level 3). Rationale and citations in the
# manuscript Methods / Supplementary Table S2.
# ---------------------------------------------------------------------------
DT_CANCERS = {
    "Breast cancer": "breast",
    "Prostate cancer": "prostate",
    "Tracheal, bronchus, and lung cancer": "lung",
    "Colon and rectum cancer": "colorectal",
    "Brain and central nervous system cancer": "brain_cns",
    "Pancreatic cancer": "pancreas",
    "Lip and oral cavity cancer": "head_neck",
    "Nasopharynx cancer": "head_neck",
    "Other pharynx cancer": "head_neck",
    "Larynx cancer": "head_neck",
}
ALL_CANCER_CAUSE = "Total cancers"  # GBD 2023 label; GBD 2021 used "Neoplasms"
ALL_CANCER_ALIASES = {"Total cancers", "Neoplasms", "Malignant neoplasms"}

# ---------------------------------------------------------------------------
# DTRI domains and indicators.
# source: "wb" = World Bank WDI code; "gho" = WHO GHO indicator matched by
# regex on IndicatorName (codes are resolved at fetch time and logged);
# "user" = optional CSV supplied in data/user_inputs.
# transform: "log1p" for right-skewed densities; direction +1 = higher is better.
# ---------------------------------------------------------------------------
DOMAINS = {
    "imaging_rt": "Imaging and radiotherapy",
    "digital": "Digital infrastructure",
    "health_system": "Health-system and workforce capacity",
    "research": "Research and computational capacity",
}

INDICATORS = [
    # Imaging & radiotherapy (WHO Global Atlas of Medical Devices / DIRAC via GHO)
    dict(key="ct_pm", domain="imaging_rt", source="gho",
         pattern=r"total density per million population.*computed tomography",
         label="CT units per million", transform="log1p"),
    dict(key="mri_pm", domain="imaging_rt", source="gho",
         pattern=r"total density per million population.*magnetic resonance",
         label="MRI units per million", transform="log1p"),
    dict(key="pet_pm", domain="imaging_rt", source="gho",
         pattern=r"total density per million population.*positron emission",
         label="PET units per million", transform="log1p"),
    dict(key="rt_pm", domain="imaging_rt", source="gho",
         # prefer an aggregate radiotherapy indicator; otherwise linac + telecobalt
         pattern=[r"total density per million population.*radiotherapy",
                  r"total density per million population.*(linear accelerator|telecobalt)"],
         label="Radiotherapy units per million", transform="log1p"),
    # Digital infrastructure (ITU data distributed via WDI)
    dict(key="internet", domain="digital", source="wb", code="IT.NET.USER.ZS",
         label="Internet users (% population)", transform=None),
    dict(key="broadband", domain="digital", source="wb", code="IT.NET.BBND.P2",
         label="Fixed broadband subscriptions per 100", transform="log1p"),
    dict(key="secure_servers", domain="digital", source="wb", code="IT.NET.SECR.P6",
         label="Secure internet servers per million", transform="log1p"),
    dict(key="electricity", domain="digital", source="wb", code="EG.ELC.ACCS.ZS",
         label="Access to electricity (% population)", transform=None),
    # Health system & workforce
    dict(key="che_pc", domain="health_system", source="wb", code="SH.XPD.CHEX.PC.CD",
         label="Current health expenditure per capita (US$)", transform="log1p"),
    dict(key="physicians", domain="health_system", source="wb", code="SH.MED.PHYS.ZS",
         label="Physicians per 1000", transform="log1p"),
    dict(key="uhc_sci", domain="health_system", source="wb", code="SH.UHC.SRVS.CV.XD",
         label="UHC service coverage index", transform=None),
    # Research & computational capacity (genomic-sequencing proxy)
    dict(key="rd_gdp", domain="research", source="wb", code="GB.XPD.RSDV.GD.ZS",
         label="R&D expenditure (% GDP)", transform="log1p"),
    dict(key="researchers", domain="research", source="wb", code="SP.POP.SCIE.RD.P6",
         label="Researchers in R&D per million", transform="log1p"),
    dict(key="tertiary", domain="research", source="wb", code="SE.TER.ENRR",
         label="Tertiary school enrolment (% gross)", transform=None),
]

# Optional user-supplied indicators (e.g. WHO Global Digital Health Monitor,
# genomic sequencing capacity). CSV columns: iso3,value  -> data/user_inputs/<key>.csv
OPTIONAL_USER_INDICATORS = [
    dict(key="ehr_national", domain="digital", source="user",
         label="National EHR system (WHO eHealth survey, 0/1)", transform=None),
    dict(key="genomic_seq", domain="research", source="user",
         label="Genomic sequencing capacity score", transform=None),
]

# Covariates (not in index)
COVARIATES = {
    "pop": "SP.POP.TOTL",
    "gdp_pc_ppp": "NY.GDP.PCAP.PP.KD",
}
