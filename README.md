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
* These CSV files contain baseline cumulative hazard ($H_{0}(t)$) for compact and complex models.
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
