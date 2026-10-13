---
title: "Global mismatch between cancer burden and digital twin readiness across 204 countries and territories: an ecological analysis using Global Burden of Disease data"
---

**Running title:** Cancer burden and digital twin readiness

**Authors:** [Author names, affiliations]

**Corresponding author:** [Name, address, email]

**Word count:** [main text] · **Tables:** 4 · **Figures:** 6 · **Supplementary material:** Tables S1–S3

---

## Abstract

**Background:** Digital twins are patient-specific computational models that are continuously updated with imaging, molecular and clinical data. They are moving from proof-of-concept towards clinical use in oncology. Whether the infrastructure needed to build them is available where cancer burden is highest has not been quantified. We aimed to measure country-level readiness for oncology digital twins and its alignment with the burden of cancers for which digital-twin applications exist.

**Methods:** In this ecological study we constructed a Digital Twin Readiness Index (DTRI) for {n_countries} countries and territories. The index draws on {n_indicators} indicators across four domains: imaging and radiotherapy, digital infrastructure, health-system capacity, and research and computational capacity. Missing values were handled by multiple imputation, and uncertainty was propagated by Monte Carlo simulation over imputations and domain weights. We obtained age-standardised disability-adjusted life-year (DALY) rates for DT-applicable cancers (breast, prostate, lung, colorectal, brain and CNS, pancreatic, and head and neck) from the Global Burden of Disease Study (GBD) {gbd_year}. We quantified the burden–readiness mismatch with a percentile-based mismatch index, a 3 × 3 bivariate classification, population-weighted concentration indices, a quantile-regression readiness frontier on the Socio-demographic Index (SDI), and mixed-effects regression.

**Findings:** DTRI ranged from {dtri_min} to {dtri_max} and rose steeply with SDI (median {dtri_med_low} in low-SDI vs {dtri_med_high} in high-SDI countries; concentration index by SDI {ci_dtri_sdi}). The concentration index of DT-applicable cancer DALY rates ranked by readiness was {ci_burden}. Countries in the lowest readiness quintile accounted for {q1_daly_share}% of global DT-applicable cancer DALYs but held {q1_ct_share}% of CT and {q1_rt_share}% of radiotherapy units. {hb_lr_n} countries, home to {hb_lr_pop} million people, combined high burden with low readiness. After adjustment for SDI, burden was {burden_assoc_phrase} with readiness (standardised β {beta_mixed}). Mismatch rankings were robust to alternative weighting, aggregation and burden measures (Spearman ρ ≥ {sens_min_rho}).

**Interpretation:** Readiness for oncology digital twins follows development rather than need. Unless capacity building, interoperable data infrastructure and model transferability are addressed together, digital twins risk widening global inequalities in cancer outcomes. The country rankings and the open index provide a baseline for targeting investment and for monitoring progress.

**Funding:** [ ]

---

## Research in context

**Evidence before this study:** We searched PubMed, Scopus and Web of Science from inception to [date] for ("digital twin" OR "in silico patient" OR "virtual patient") AND (cancer OR oncology OR tumour), combined with (global OR readiness OR infrastructure OR inequality OR "low- and middle-income"), without language restrictions. Most publications were narrative or scoping reviews, conceptual frameworks, or single-centre modelling studies from high-income countries. Infrastructure benchmarking studies in cancer control have quantified gaps in imaging and radiotherapy, either regionally or for groups of countries. One survey examined digital-twin adoption in a single country. We identified no study that measured readiness for digital twins across countries or related it to cancer burden.

**Added value of this study:** To our knowledge, this is the first global, country-level index of readiness for oncology digital twins and the first quantification of its mismatch with the burden of cancers for which digital-twin applications exist. The index combines imaging, radiotherapy, digital, health-system and research-capacity indicators, with explicit uncertainty. Linking it to GBD estimates identifies where burden and readiness diverge most.

**Implications of all the available evidence:** Without deliberate action, digital twins are positioned to benefit the populations with the most diagnostic and computational capacity rather than those with the greatest burden. Investment in imaging, radiotherapy and interoperable health data in high-mismatch countries, and multinational validation of models trained in high-income settings, are prerequisites for equitable translation.

---

## Introduction

Cancer caused an estimated [N] million deaths and [N] million DALYs worldwide in {gbd_year}. The largest projected increases to 2050 are in countries with low and middle SDI.^1,2^ At the same time, oncology is being reshaped by computational approaches that move from population-average to individualised prediction. Among these, the *digital twin* is a virtual representation of an individual patient's tumour and host, continuously updated with that patient's data. It has been proposed as a paradigm shift for precision oncology.^3–6^ Mechanistic models calibrated to serial MRI have forecast response to neoadjuvant therapy in breast cancer,^7^ image-informed models of glioma growth have been used to personalise radiotherapy, and in-silico trials are increasingly used to emulate treatment comparisons.^5,8^ The US National Academies have described digital twins as a priority area for foundational research.^9^

Digital twins in oncology rest on specific infrastructure. They need serial high-quality imaging (CT, MRI, PET), access to radiotherapy for the interventions they are often designed to optimise, interoperable electronic health records and connectivity to move data, and research and computational capacity to build, calibrate and validate models.^5,6,9^ These resources are unevenly distributed. The *Lancet Oncology* Commissions on radiotherapy and on medical imaging documented large shortfalls in low- and middle-income countries,^10,11^ and WHO's Global Strategy on Digital Health highlights persistent digital divides.^12^ Recent benchmarking of cancer-control infrastructure in Commonwealth countries reported the largest deficits in CT, surgery and radiation oncology.^13^

Technologies that depend on scarce infrastructure tend to be adopted first where that infrastructure is concentrated. In the absence of countervailing policy, this can widen existing inequalities, a pattern described for earlier health technologies as the *inverse equity hypothesis*. Whether this is the trajectory for digital twins has not been examined quantitatively. Published work on digital twins in oncology consists largely of conceptual reviews and single-centre models,^4–6,14^ and we found no global assessment of readiness or of its alignment with need.

We therefore aimed to (1) construct a transparent, uncertainty-quantified Digital Twin Readiness Index (DTRI) for all countries with available data; (2) relate readiness to the burden of cancers for which digital-twin applications exist, using GBD {gbd_year}; (3) identify countries with the greatest burden–readiness mismatch; and (4) test whether readiness tracks burden independently of socio-demographic development.

## Methods

### Study design and reporting

This was a cross-sectional ecological study with countries and territories as the unit of analysis. It is reported in accordance with the Guidelines for Accurate and Transparent Health Estimates Reporting (GATHER)^15^ (checklist in the appendix). All analyses used publicly available, aggregated data, so ethical approval was not required.

### Cancer burden

We extracted estimates for {gbd_year} from the GBD Results Tool:^1,16^ DALYs, deaths and incidence, as age-standardised rates per 100 000 and as all-age counts, for both sexes combined, in 204 countries and territories. GBD methods for cancer estimation have been described in detail elsewhere.^1^

We defined **DT-applicable cancers** as those with published patient-specific digital-twin or mechanistic forecasting applications that use routinely acquired clinical data (Supplementary Table S2):^4–8,14^ breast; prostate; tracheal, bronchus and lung; colon and rectum; brain and central nervous system; pancreatic; and head and neck (lip and oral cavity, nasopharynx, other pharynx, larynx). Age-standardised rates use a common standard population and are therefore additive, so the primary burden measure was the sum of age-standardised DALY rates across these causes. In sensitivity analyses we used deaths, incidence, and DALYs from all cancers. SDI values for {gbd_year} were obtained from GBD.

### Digital Twin Readiness Index

We built the DTRI following the OECD–JRC handbook on composite indicators.^17^ The conceptual framework (appendix) specifies four domains, each representing a necessary input for building and using an oncology digital twin:

1. **Imaging and radiotherapy:** CT, MRI and PET units per million population, and radiotherapy units (linear accelerators and cobalt-60) per million population, from the WHO Global Atlas of Medical Devices / Global Health Observatory (GHO),^18^ which incorporates IAEA DIRAC data on radiotherapy.
2. **Digital infrastructure:** internet users (% population), fixed broadband subscriptions per 100 people, secure internet servers per million, and access to electricity (%), from ITU and World Bank data distributed through the World Development Indicators (WDI).
3. **Health-system capacity:** current health expenditure per capita (US$), physicians per 1000 population, and the UHC service coverage index (WDI/WHO).
4. **Research and computational capacity:** gross domestic expenditure on R&D (% GDP), researchers in R&D per million, and gross tertiary enrolment (WDI/UNESCO). Country-comparable data on genomic sequencing capacity were not available, so this domain serves as a proxy for the capacity to develop and validate models.

For each indicator we used the most recent value between 2015 and 2024 (indicator coverage and years in Supplementary Table S1). Indicator codes from the WHO GHO were resolved programmatically and archived.

**Treatment of missing data.** Countries missing more than half of the indicators were excluded ({n_excluded} countries). Remaining missing values were imputed by multiple imputation with chained equations (Bayesian ridge regression with posterior draws, m = 20).^19^ The auxiliary predictors were log GDP per capita (PPP) and SDI, which were not themselves index components.

**Normalisation and aggregation.** Skewed density indicators were log-transformed. Each indicator was rescaled to 0–100 using goalposts at the 2.5th and 97.5th percentiles of observed values, which limits the influence of outliers. Domain scores were the arithmetic mean of their indicators. In the primary specification, the DTRI was the equally weighted geometric mean of the four domain scores. Geometric aggregation limits compensation between domains, reflecting that a digital twin cannot be built if any one input is absent.

**Uncertainty.** We generated {n_draws} Monte Carlo draws. Each draw combined one imputed dataset with domain weights sampled from a Dirichlet distribution centred on equal weights (concentration parameter 10). We report 95% uncertainty intervals (UIs) for DTRI scores and ranks as the 2.5th and 97.5th percentiles of the draws.

### Burden–readiness mismatch

We used five complementary approaches.

1. **Mismatch index (MI):** a country's percentile rank of DT-applicable DALY rate minus its percentile rank of DTRI (range −100 to 100; positive values indicate burden exceeding readiness). UIs were derived from the DTRI draws. Countries whose lower UI bound exceeded zero were classed as having a robust mismatch.
2. **Bivariate classification:** countries were cross-classified by tertiles of burden and readiness. Countries in the top burden tertile and bottom readiness tertile were labelled *high burden – low readiness*.
3. **Distributional analysis:** global DT-applicable DALYs, population, and absolute numbers of CT, MRI and radiotherapy units (density × population), by DTRI quintile. We calculated population-weighted Gini coefficients for device densities.
4. **Concentration indices:** population-weighted concentration indices (Wagstaff)^20,21^ for (a) DT-applicable DALY rates ranked by DTRI and (b) DTRI ranked by SDI, with 95% CIs from 1000 bootstrap resamples of countries. A negative value in (a) indicates that burden is concentrated in countries with lower readiness.
5. **Readiness frontier:** in line with GBD frontier analyses, we estimated the maximum readiness achieved at each level of SDI with 90th-percentile quantile regression^22^ of DTRI on a cubic B-spline of SDI. Each country's readiness gap was its distance below the frontier.

### Statistical analysis

We assessed the association between burden and readiness with Spearman correlation, overall and within SDI quintiles. We also fitted linear mixed-effects models of standardised DTRI on standardised log DALY rate and SDI, with a random intercept for World Bank region; ordinary least squares with HC3 robust standard errors was used as a check. Our prespecified hypothesis was that readiness would not increase with burden after adjustment for SDI.

**Sensitivity analyses** examined the agreement of mismatch rankings (Spearman ρ and overlap among the top 20 countries) under: arithmetic aggregation; weights derived from principal component analysis; leaving out each domain in turn; deaths or incidence instead of DALYs; all cancers instead of DT-applicable cancers; and complete-case analysis without imputation.

Analyses used Python 3 (pandas, scikit-learn, statsmodels, geopandas). All code is openly available at [repository URL/DOI] and reproduces every table and figure from the source data.

### Role of the funding source

[ ]

## Results

### Readiness

The DTRI was computed for {n_countries} countries and territories. {n_complete_case} had complete data on all indicators, and the median proportion of imputed indicators was {median_missing}%. In PCA, the first component explained {pca_ev1}% of the variance in the domain scores. DTRI scores ranged from {dtri_min} to {dtri_max}. The highest scores were in {dtri_top} and the lowest in {dtri_bottom} (Supplementary Table S3; Figure 1A). Median DTRI {sdi_trend_phrase} across SDI quintiles, from {dtri_med_low} in low-SDI to {dtri_med_high} in high-SDI countries (Table 1). The concentration index of DTRI ranked by SDI was {ci_dtri_sdi}. Device capacity was even more unequally distributed than the composite index: population-weighted Gini coefficients were {gini_ct} for CT, {gini_mri} for MRI and {gini_rt} for radiotherapy units, compared with {gini_dtri} for the DTRI.

### Burden–readiness mismatch

The median age-standardised DALY rate from DT-applicable cancers was {burden_med} per 100 000 (Figure 1B). Burden and readiness were {spearman_phrase} correlated (Spearman ρ {spearman_rho}, p {spearman_p}; Figure 3). The concentration index of DT-applicable DALY rates ranked by DTRI was {ci_burden}; across DTRI draws its 95% UI was {ci_burden_draws} (Figure 4).

By DTRI quintile (Table 2), countries in the lowest readiness quintile accounted for {q1_pop_share}% of the population and {q1_daly_share}% of global DT-applicable cancer DALYs, but {q1_ct_share}% of CT units, {q1_mri_share}% of MRI units and {q1_rt_share}% of radiotherapy units. The highest quintile held {q5_ct_share}% of CT and {q5_rt_share}% of radiotherapy units and accounted for {q5_daly_share}% of DALYs.

{hb_lr_n} countries combined high burden with low readiness (Figure 2). Together they had {hb_lr_pop} million inhabitants and {hb_lr_share}% of global DT-applicable cancer DALYs. They were {hb_lr_list}. Mismatch was robust (lower UI bound > 0) in {n_mismatch_robust} countries. The 10 largest mismatch indices were in {top_mismatch} (Figure 6).

Relative to the SDI frontier, the median readiness gap was {frontier_median_gap} DTRI points. The largest gaps, indicating readiness well below that achieved by countries of similar development, were in {frontier_top} (Figure 5).

### Association models

In unadjusted analysis, a one-SD higher log burden was associated with a {beta_unadj} SD difference in DTRI. After adjustment for SDI in the mixed-effects model, the association was {beta_mixed} SD, whereas SDI was strongly associated with readiness ({beta_sdi} SD per SD; Table 3). Within SDI quintiles, Spearman correlations between burden and readiness were {spearman_within}.

### Sensitivity analyses

Mismatch rankings were robust to alternative specifications (Table 4). Spearman correlations with the primary ranking were at least {sens_min_rho} for arithmetic aggregation, PCA weighting and leave-one-domain-out indices, and at least {sens_min_overlap} of the 20 highest-mismatch countries were retained. Using deaths or incidence gave similar rankings. Using all cancers gave ρ = {sens_all_cancer_rho}, showing that the choice of DT-applicable cancers [does / does not] materially change which countries are identified.

## Discussion

To our knowledge, this study provides the first global quantification of readiness for oncology digital twins and of its alignment with cancer burden. Readiness was strongly graded by socio-demographic development. Burden from cancers for which digital twins are being developed was [concentrated in / not aligned with] countries with the least capacity to build and use them. A group of countries, home to {hb_lr_pop} million people, combined high burden with low readiness. After accounting for SDI, readiness was not higher where burden was higher, consistent with our prespecified hypothesis that capacity follows development rather than need. **[AUTHOR CHECK: confirm direction and wording against final results.]**

These findings extend earlier infrastructure benchmarking in three ways. First, they cover all countries with data rather than a regional subset.^13^ Second, they add the digital and research-capacity inputs that distinguish digital twins from conventional imaging-based care. Third, they relate capacity directly to the specific burden a technology is meant to address. The pronounced inequality in imaging and radiotherapy units, which exceeded that of the composite index, is consistent with the shortfalls reported by the *Lancet Oncology* Commissions.^10,11^ It indicates that physical data-acquisition capacity, more than connectivity, is the binding constraint in many high-mismatch countries.

Our results have three main implications. **First, investment targeting.** Countries with high mismatch and large readiness gaps relative to the SDI frontier are those where investment in imaging, radiotherapy and data infrastructure could yield the greatest return. Such investment brings near-term benefit for conventional cancer care, independent of digital twins, and creates the preconditions for later digital-twin adoption. Countries that lie well below the frontier have achieved less readiness than peers at similar development, which suggests that the gap is modifiable through policy rather than determined by resources alone.

**Second, model transferability.** Digital twins are calibrated to the data on which they are developed, which today are overwhelmingly from high-income settings. Differences in case-mix, stage at presentation, imaging protocols and treatment availability mean that models may not transfer to high-mismatch settings without recalibration. Multinational validation consortia that include low-readiness countries, as well as federated and lower-data modelling approaches that work with CT rather than multiparametric MRI, should be research priorities.

**Third, monitoring.** The DTRI is transparent, built from routinely updated public sources and fully reproducible. It can therefore be re-estimated as data are updated and used to track whether the readiness gap narrows. It could complement existing monitoring frameworks, such as WHO's Global Strategy on Digital Health^12^ and national cancer control plans.

### Limitations

This study has limitations. First, it is ecological: country-level associations do not describe within-country distributions, and readiness in national averages can mask concentrated capacity in tertiary centres, which is where digital-twin pilots are most likely to occur. Second, no standard definition of digital-twin readiness exists. Our index is a theory-driven proxy. We could not include direct measures of electronic health record interoperability, genomic sequencing capacity or high-performance computing because comparable global data were not available. Third, medical-device data in the WHO Global Atlas are self-reported, irregularly updated and incomplete. We addressed this with multiple imputation and complete-case sensitivity analyses, but measurement error remains. Fourth, the set of DT-applicable cancers reflects the current literature and will expand; we therefore also analysed all cancers. Fifth, GBD estimates for countries with sparse vital registration and cancer registry data rely heavily on modelling and covariates, and their uncertainty was not propagated into the mismatch index. Finally, indicators from different years (2015–2024) were combined, and the most recent values were assumed to represent current capacity.

### Conclusion

Readiness for oncology digital twins is concentrated in high-SDI countries and is misaligned with the global distribution of the cancers these technologies target. Without deliberate investment and inclusive model development, digital twins could widen rather than narrow global inequalities in cancer outcomes. The open DTRI provides a baseline to target investment and monitor progress.

---

## Declarations

**Contributors:** [CRediT statement]

**Declaration of interests:** [ ]

**Data sharing:** All source data are publicly available from the cited sources. GBD estimates are available from the GBD Results Tool under the IHME data-use agreement. Analysis code and derived index values are available at [repository URL/DOI].

**Use of AI-assisted technologies:** Drafting of this manuscript and analysis code was assisted by an AI language model (Claude, Anthropic). The authors reviewed, verified and take full responsibility for all content. **[Required by ICMJE and most journals; edit as needed.]**

**Acknowledgments:** [ ]

---

## Tables and figures

**Table 1.** DTRI, domain scores and DT-applicable cancer burden by SDI quintile. → `outputs/tables/table1_by_sdi_quintile.csv`

**Table 2.** Distribution of population, DT-applicable cancer DALYs and imaging/radiotherapy units by DTRI quintile. → `table2_by_dtri_quintile.csv`

**Table 3.** Association between DT-applicable cancer burden and readiness: unadjusted, OLS and mixed-effects models. → `table3_models.csv`

**Table 4.** Sensitivity analyses: agreement of mismatch rankings with the primary specification. → `table4_sensitivity.csv`

**Figure 1.** Global distribution of (A) the Digital Twin Readiness Index and (B) age-standardised DALY rates from DT-applicable cancers, {gbd_year}.

**Figure 2.** Bivariate map of DT-applicable cancer burden and digital twin readiness (tertiles). ★ marks high burden – low readiness.

**Figure 3.** DTRI versus DT-applicable cancer DALY rate, coloured by SDI quintile and sized by population. Dotted lines mark tertiles; the 12 countries with the highest mismatch are labelled.

**Figure 4.** Concentration curve of DT-applicable cancer DALYs, with countries ranked by DTRI.

**Figure 5.** Readiness frontier: DTRI versus SDI, with the 90th-percentile quantile-regression frontier.

**Figure 6.** The 30 countries with the highest mismatch index, with 95% uncertainty intervals.

**Supplementary Table S1.** DTRI indicators: source, coverage, years. **S2.** Evidence base for DT-applicable cancers. **S3.** Full country results.

---

## References

*All references must be checked against PubMed/DOI before submission. Items marked [verify] need confirmation of the author list or volume and pages.*

1. GBD 2023 Cancer Collaborators. The global, regional, and national burden of cancer, 1990–2023, with forecasts to 2050: a systematic analysis for the Global Burden of Disease Study 2023. *Lancet* 2025. [verify volume/pages]
2. Bray F, Laversanne M, Sung H, et al. Global cancer statistics 2022: GLOBOCAN estimates of incidence and mortality worldwide for 36 cancers in 185 countries. *CA Cancer J Clin* 2024; 74: 229–63.
3. Björnsson B, Borrebaeck C, Elander N, et al. Digital twins to personalize medicine. *Genome Med* 2020; 12: 4.
4. Hernandez-Boussard T, Macklin P, Greenspan EJ, et al. Digital twins for predictive oncology will be a paradigm shift for precision cancer care. *Nat Med* 2021; 27: 2065–66.
5. Wu C, Lorenzo G, Hormuth DA, et al. Integrating mechanism-based modeling with biomedical imaging to build practical digital twins for clinical oncology. *Biophys Rev* 2022; 3: 021304.
6. Katsoulakis E, Wang Q, Wu H, et al. Digital twins for health: a scoping review. *NPJ Digit Med* 2024; 7: 77.
7. Jarrett AM, Hormuth DA, Wu C, et al. Quantitative magnetic resonance imaging and tumor forecasting of breast cancer patients in the community setting. *Nat Protoc* 2021; 16: 5309–38. [verify]
8. [In-silico trial / FarrSight-Twin preprint, medRxiv 2024, doi:10.1101/2024.01.17.24301444] [verify]
9. National Academies of Sciences, Engineering, and Medicine. Foundational research gaps and future directions for digital twins. Washington, DC: The National Academies Press, 2024.
10. Atun R, Jaffray DA, Barton MB, et al. Expanding global access to radiotherapy. *Lancet Oncol* 2015; 16: 1153–86.
11. Hricak H, Abdel-Wahab M, Atun R, et al. Medical imaging and nuclear medicine: a Lancet Oncology Commission. *Lancet Oncol* 2021; 22: e136–72.
12. WHO. Global strategy on digital health 2020–2025. Geneva: World Health Organization, 2021.
13. [Benchmarking infrastructure for cancer control in Commonwealth countries: a population-based observational study. *Lancet Oncol* 2025. PMID 40480237] [verify authors]
14. Laubenbacher R, Niarakis A, Helikar T, et al. Building digital twins of the human immune system: toward a roadmap. *NPJ Digit Med* 2022; 5: 64.
15. Stevens GA, Alkema L, Black RE, et al. Guidelines for Accurate and Transparent Health Estimates Reporting: the GATHER statement. *Lancet* 2016; 388: e19–23.
16. GBD 2021 Diseases and Injuries Collaborators. Global incidence, prevalence, years lived with disability (YLDs), disability-adjusted life-years (DALYs), and healthy life expectancy (HALE) for 371 diseases and injuries in 204 countries and territories and 811 subnational locations, 1990–2021. *Lancet* 2024; 403: 2133–61.
17. OECD, European Commission Joint Research Centre. Handbook on constructing composite indicators: methodology and user guide. Paris: OECD Publishing, 2008.
18. WHO. Global atlas of medical devices 2022. Geneva: World Health Organization, 2022.
19. van Buuren S, Groothuis-Oudshoorn K. mice: multivariate imputation by chained equations in R. *J Stat Softw* 2011; 45: 1–67.
20. Wagstaff A, Paci P, van Doorslaer E. On the measurement of inequalities in health. *Soc Sci Med* 1991; 33: 545–57.
21. Kakwani N, Wagstaff A, van Doorslaer E. Socioeconomic inequalities in health: measurement, computation, and statistical inference. *J Econom* 1997; 77: 87–103.
22. Koenker R, Bassett G. Regression quantiles. *Econometrica* 1978; 46: 33–50.
