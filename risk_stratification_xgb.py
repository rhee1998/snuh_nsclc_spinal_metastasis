import numpy as np
import pandas as pd
import pickle, os, warnings, argparse

import xgboost as xgb
from xgboost import XGBRegressor

# Command Line Arguments
parser = argparse.ArgumentParser()
parser.add_argument('--model_type', default='complex', help='complex or compact')
parser.add_argument('--data_csv', default='src/sample_data.csv', help='Path to the sample data CSV file')
parser.add_argument('--output_dir', default='output', help='Directory to save the output CSV files')
args = parser.parse_args()

IS_COMPLEX = (args.model_type.lower() == 'complex')
SAMPLE_DATA_CSV = args.data_csv
OUTPUT_DIR = args.output_dir
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Library Setup
warnings.filterwarnings("ignore")
pd.set_option('display.max_columns', None)

# Column Names and Mapping
DEMO_FEATURES       = ['AGE', 'SEX', 'BMI', 'CHARLSON']
CANCER_FEATURES     = ['CANCER_TYPE', 'CANCER_STAGE', 'SUV_MAX']
MOLECULAR_FEATURES  = ['EGFR_ANY', 'EGFR_G719X', 'EGFR_E19DEL', 'EGFR_T790M', 'EGFR_S768I', 'EGFR_E20INS', 'EGFR_L858R', 'EGFR_L861Q', 'ALK', 'PD_L1']
OP_FEATURES         = ['OP_RESECTION', 'OP_NEOADJ']
CHEMO_FEATURES      = ['CYTO_PLAT', 'CYTO_ALKYL', 'CYTO_TOPO', 'CYTO_METABOL', 'CYTO_MITO', 'EGFR_TKI', 'ALK_TKI', 'OTHER_TARGET', 'IMMUNE']
RT_FEATURES         = ['RT', 'RT_GY', 'RT_FX']
RESPONSE_FEATURES   = ['RECIST', 'SUV_MAX_POST']

INP_FEATURES = DEMO_FEATURES + CANCER_FEATURES + MOLECULAR_FEATURES
if IS_COMPLEX:
    INP_FEATURES += OP_FEATURES + CHEMO_FEATURES + RT_FEATURES + RESPONSE_FEATURES

CANCER_TYPE_MAP = {
    'ADC': 1, 'ADENO': 1, 'ADENOCA':1, 'ADENOCARCINOMA': 1,
    'SQC': 2, 'SQCC': 2, 'SQUAMOUS CELL CARCINOMA': 2,
}
CANCER_STAGE_MAP = {
    'IA': 1, 'IB': 2, 'IIA': 3, 'IIB': 4,
    'IIIA': 5, 'IIIB': 6, 'IIIC': 7, 'IVA': 8, 'IVB': 9
}
RECIST_MAP = {
    'NED': 1, 'CR': 1, 'PR': 2, 'SD': 3, 'PD': 4
}

# Load Data and Preprocess
def load_data(filename):
    df = pd.read_csv(filename, encoding='utf-8')
    
    df['SEX']           = df['SEX'].map({'M': 0, 'F': 1})
    df['CANCER_TYPE']   = df['CANCER_TYPE'].apply(lambda x: CANCER_TYPE_MAP.get(x.upper(), 2))
    df['CANCER_STAGE']  = df['CANCER_STAGE'].apply(lambda x: CANCER_STAGE_MAP[x.upper()])
    df['RECIST']        = df['RECIST'].apply(lambda x: RECIST_MAP[x.upper()])
    
    return df

# Load Model and Make Inference
def load_model_dict(is_complex=IS_COMPLEX):
    if is_complex:
        best_filename = 'src/model_complex.pth'
    else:
        best_filename = 'src/model_compact.pth'
    
    model_dict = pickle.load(open(best_filename, 'rb'))
    return model_dict

def run_model(X, model_dict):
    y_pred_list = []
    
    for fold in range(len(model_dict)):
        model = model_dict[fold]
        y_pred = model.predict(X)
        y_pred_list.append(y_pred)

    y_pred_mean = np.mean(y_pred_list, axis=0)
    return y_pred_mean

# Load Baseline Cumulative Hazard
def load_baseline_cumulative_hazard(is_complex=IS_COMPLEX):
    if is_complex:
        base_filename = 'src/baseline_cumulative_hazard_complex.csv'
    else:
        base_filename = 'src/baseline_cumulative_hazard_compact.csv'
    
    df_base = pd.read_csv(base_filename, encoding='utf-8')
    return df_base

# Full Pipeline
df = load_data(filename=SAMPLE_DATA_CSV)
X = df[INP_FEATURES]
pid_list = df['PID'].astype(str).tolist()
model_dict = load_model_dict(is_complex=IS_COMPLEX)
rh_pred_list = np.exp(run_model(X, model_dict))

df_base_hz = load_baseline_cumulative_hazard(is_complex=IS_COMPLEX)

for pid, idx in zip(pid_list, range(len(rh_pred_list))):
    rh_pred = rh_pred_list[idx]
    df_hz = df_base_hz.copy()

    df_hz['H_median'] = df_hz['H0_median'] * rh_pred
    df_hz['H_lower']  = df_hz['H0_lower']  * rh_pred
    df_hz['H_upper']  = df_hz['H0_upper']  * rh_pred

    df_hz['S_median'] = np.exp(-df_hz['H_median'])
    df_hz['S_lower']  = np.exp(-df_hz['H_upper'])
    df_hz['S_upper']  = np.exp(-df_hz['H_lower'])

    df_hz.drop(columns=['H0_median', 'H0_lower', 'H0_upper'], inplace=True)
    df_hz.to_csv(os.path.join(OUTPUT_DIR, f'{pid}.csv'), index=False)