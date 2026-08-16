import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os, warnings, argparse

# Command Line Arguments
parser = argparse.ArgumentParser()
parser.add_argument('--data', required=True, help='Path to the survival curve CSV file')
parser.add_argument('--output_dir', default='output/png', help='Directory to save the output plots')
args = parser.parse_args()

DATA_CSV = args.data
OUTPUT_DIR = args.output_dir
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Library Setup
warnings.filterwarnings("ignore")
pd.set_option('display.max_columns', None)

# Plot Survival Curve
def plot_survival_curve(
        time, s_median, s_lower, s_upper,
        title=None,
        xlabel='Time (Months)', 
        xlim=[0, 120],
        xticks=np.arange(0, 121, 12),
        ylabel='Survival Probability',
        ylim=[0, 1],
        yticks=np.arange(0, 1.1, 0.1),
        plot_median_surv=True,
        ax=None
    ):
    if ax is None:
        _, ax = plt.subplots(figsize=(6,4))

    ax.plot(time, s_median, label='Survival Probability')
    ax.fill_between(time, s_lower, s_upper, alpha=0.3, label='95% CI')
    if title: ax.set_title(title)
    ax.set_xlabel(xlabel); ax.set_xlim(xlim); ax.set_xticks(xticks)
    ax.set_ylabel(ylabel); ax.set_ylim(ylim); ax.set_yticks(yticks)

    if plot_median_surv:
        ax.axhline(0.5, color='red', linestyle='--')

    ax.legend(loc='upper right')
    return ax

# Main
df = pd.read_csv(DATA_CSV)
_, ax = plt.subplots(figsize=(6, 4))
plot_survival_curve(
    time=df['time'],
    s_median=df['S_median'],
    s_lower=df['S_lower'],
    s_upper=df['S_upper'],
    ax=ax
)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, os.path.basename(DATA_CSV).replace('.csv', '.png')), dpi=300)
