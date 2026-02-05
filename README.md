# Spinal Metastasis Risk Stratification in Non-Small Cell Lung Cancer (NSCLC)
This repository provides script for risk stratification of spinal metastasis in patients diagnosed with non-small cell lung cancer (NSCLC).

# File Structure
```
src/
  |- baseline_cumulative_hazard_compact.csv
  |- baseline_cumulative_hazard_complex.csv
  |- model_compact.pth
  |- model_complex.pth
  |- sample_data.csv
requirements.txt
risk_stratification_xgb.ipynb
```
`src/baseline_cumulative_hazard_{suffix}.csv`
* These CSV files contain baseline cumulative hazard ($CH_{0}(t)$) for compact and complex models.
* 95% Confidence intervals were generated using bootstrap resampling (n=2000)

`src/model_{suffix}.pth`
* Each model file is a `dict` object containing five distinct XGBoost regressors trained for each cross-validation fold.
 
`src/sample_data.csv`
* This CSV file contains six synthesized patient data.
* Brief characteristics of the sample patients are summarized in the following sections.
 
`requirements.txt`
* This file includes python libraries to build the virtual environment

`risk_stratification_xgb.ipynb`
* This Jupyter Notebook file contains script for predicting survival curves for each sample patient.

# Sample Data Description

## Column Names
Demographic Features
* `AGE`: age in years
* `SEX`: male(`M`) or female(`F`)
* `BMI`: body mass index in $kg/m^2$
* `CHARLSON`: Charlson comorbidity index

Classical Tumor Features
* `CANCER_TYPE`: histological subtype categorized into adenocarcinoma (`ADC`), squamous cell carcinoma (`SQCC`), and other (`OTHER`)
* `CANCER_STAGE`: clinical stage of NSCLC at the time of initial diagnosis
* `SUV_MAX`: maximum standardized uptake value at initial PET/CT if available

Molecular Tumor Features
* `EGFR_ANY`: presence of any EGFR mutation (0-not present/1-present)
* `EGFR_{mutation_type}`: presence of specific `mutation_type` of the EGFR gene (0/1)
* `ALK`: presence of any ALK mutation (0/1)
* `PD_L1`: expression levels of PD-L1 gene normalized to range $[0, 1]$.

Initial Treatment Features - Surgical
* `OP_RESECTION`: whether the patient has undergone surgical resection of primary tumor (0/1)
* `OP_NEOADJ`: whether the patient has undergone neoadjuvant therapy prior to surgery (0/1)

Initial Treatment Features - Pharmacological Therapy
* `CYTO_PLAT`: platinum agent administration (0/1)
* `CYTO_ALKYL`: alkylating agent administration (0/1)
* `CYTO_TOPO`: topoisomerate inhibitor administration (0/1)
* `CYTO_METABOL`: antimetabolite administration (0/1)
* `CYTO_MITO`: anti-mitotic agent administration (0/1)
* `EGFR_TKI`: 0-not administered / 1-1st generation / 2-2nd generation / 3-3rd generation
* `ALK_TKI`: 0-not administered / 1-administered
* `OTHER_TARGET`: administration of other targeting agents (0/1)
* `IMMUNE`: administration of monoclonal antibodies (mAb)

Initial Treatment Features - Radiotherapy
* `RT`: whether radiotherapy to the primary tumor was applied (0/1)
* `RT_GY`: total radiation dose in Gy
* `RT_FX`: number of fractionation

Initial Treatment Response
* `RECIST`: combination of RECIST(`CR`, `PR`, `SD`, `PD`) and `NED` (for patients who underwent complete surgical resection of the primary tumor)
* `SUV_MAX_POST`: maximum standardized uptake value after initial treatment, if PET/CT was conducted.

## Sample Case Description
| **Case** | **Age/Sex** | **Clinical Staging** | **Molecular Features** | **Initial Treatment** | **Response** |
| :---: | :---: | :---: | :--- | :--- | :--- |
| #1 | 74/M | Stage IB Adenoca. | EGFR e19del(+) / ALK(-) / PD-L1 not available | Surgical resection without adjuvant treatment | NED |
| #2 | 61/F | Stage IIA Adenoca. | EGFR(-) / ALK(+) / PD-L1 expr. 0% | Surgical resection with adjuvant chemotherapy | PR |
| #3 | 55/F | Stage IIIA Adenoca. | EGFR(-) / ALK(-) / PD-L1 expr. 0% | Concurrent chemoradiotherapy (cytotoxic agent) | SD |
| #4 | 60/F | Stage IVB Adenoca. | EGFR e19del(+) / ALK(-) / PD-L1 not available | EGFR TKI (1st gen.) | PR |
| #5 | 64/M | Stage IVB Adenoca. | EGFR L861Q(+) / ALK(-) / PD-L1 not available | EGFR TKI (1st gen.) | PD |
| #6 | 59/M | Stage IVB Adenoca. | EGFR(-) / ALK(-) / PD-L1 expr. 0% | Cytotoxic chemotherapy | PD |

# Risk Stratification
## Model Description
* Input features are defined as follows:
  * _Compact Model_: Demographics + Classical & Molecular Features
  * _Complex Model_: Demographis + Classical & Molecular Features + Initial Treatment & Response
* Each model file is a Python `dict` object of five distinct XGBoost regressors trained off each cross-validation fold.
* They predict the natural log of relative hazard, and as a result, the cumulative hazard and survival curve.

## Survival Curve Estimation
* Baseline cumulative hazard function was estimated using Breslow's method.
* Confidence intervals were obtained using bootstrap resampling (n=2000)
* Procedures to obtaining the survival curve are as follows, where $K$ is the number of operations and $f(x)$ denotes XGBoost regressor trained from each fold.

$$CH(t|x) = CH_{0}(t) \cdot \exp\left(\frac{1}{K}\sum_{i=1}^{K} \hat{f}_{i}(x)\right)$$

$$S(t|x) = \exp(-CH(t|x))$$

## Sample Survival Curves
* Survival curves for the sample cases are shown below:
[](survival_curve_results.png)
