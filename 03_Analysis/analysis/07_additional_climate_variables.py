"""
Analysis B: Additional climate variables (#14 response)

Calculates from existing JMA daily data:
  1. Mean daily maximum temperature (°C)
  2. SD of daily maximum temperature (temperature variability)
  3. Mean diurnal temperature range (daily max − daily min)
  4. Rapid-change days (|day-to-day max temp change| ≥ 5°C)

Runs univariate regressions against infusion therapy rate,
appended to the existing Table 2 results.
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
JMA_PATH     = PROJECT_ROOT / "02_Data" / "raw" / "jma_weather" / "jma_daily_temperature_2023_summer.csv"
DATASET_PATH = PROJECT_ROOT / "03_Analysis" / "results" / "population_adjusted_dataset.csv"
OUT_DIR      = PROJECT_ROOT / "03_Analysis" / "results" / "additional_climate"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ── load & clean JMA data ────────────────────────────────────────────────────
jma = pd.read_csv(JMA_PATH, encoding='utf-8-sig')
jma['気温最高'] = pd.to_numeric(jma['気温最高'], errors='coerce')
jma['気温最低'] = pd.to_numeric(jma['気温最低'], errors='coerce')

# ── prefecture-level climate variable computation ────────────────────────────
records = []
for pref, grp in jma.groupby('都道府県'):
    grp = grp.sort_values(['月', '日']).reset_index(drop=True)

    tmax = grp['気温最高'].dropna()
    tmin = grp['気温最低'].dropna()

    mean_tmax   = tmax.mean()                               # mean daily max temp
    sd_tmax     = tmax.std(ddof=1)                          # SD of daily max temp
    mean_dtr    = (grp['気温最高'] - grp['気温最低']).mean()  # mean diurnal range

    # Rapid change: |Tmax[d] - Tmax[d-1]| ≥ 5°C
    delta_tmax       = tmax.diff().abs()
    rapid_change_days = int((delta_tmax >= 5).sum())

    records.append({
        '都道府県':          pref,
        '気温最高_平均':     round(mean_tmax, 2),
        '気温最高_SD':      round(sd_tmax, 2),
        '日較差_平均':       round(mean_dtr, 2),
        '急変日数_5deg':    rapid_change_days,
    })

df_clim = pd.DataFrame(records)
df_clim.to_csv(OUT_DIR / "additional_climate_by_prefecture.csv", index=False, encoding='utf-8-sig')
print(f"[OK] Climate variables saved: {len(df_clim)} prefectures")

# ── merge with main dataset ──────────────────────────────────────────────────
main = pd.read_csv(DATASET_PATH, encoding='utf-8-sig')
df   = main.merge(df_clim, on='都道府県', how='inner')
print(f"[OK] Merged dataset: {len(df)} rows")

Y_col = '点滴注射_per100k'
Y     = df[Y_col]

# ── univariate regressions ───────────────────────────────────────────────────
new_vars = {
    '気温最高_平均':  'Mean daily max temperature (per 1°C)',
    '気温最高_SD':   'SD of daily max temperature (per 1°C)',
    '日較差_平均':    'Mean diurnal temperature range (per 1°C)',
    '急変日数_5deg': 'Rapid-change days (≥5°C change, per 1 day)',
}

rows = []
for col, label in new_vars.items():
    X  = sm.add_constant(df[[col]])
    m  = sm.OLS(Y, X).fit()
    ci = m.conf_int(alpha=0.05)
    rows.append({
        'Variable':       label,
        'beta':           round(m.params[col], 2),
        'CI_lower':       round(ci.loc[col, 0], 2),
        'CI_upper':       round(ci.loc[col, 1], 2),
        'p':              round(m.pvalues[col], 4),
        'R2':             round(m.rsquared, 3),
        'adj_R2':         round(m.rsquared_adj, 3),
        'N':              int(m.nobs),
    })
    print(f"  {col}: beta={m.params[col]:.2f}, p={m.pvalues[col]:.4f}, R2={m.rsquared:.3f}")

df_res = pd.DataFrame(rows)
df_res.to_csv(OUT_DIR / "additional_climate_regression_results.csv", index=False, encoding='utf-8-sig')
print(f"[OK] Regression results saved")

# ── supplementary scatter: mean daily max temp vs infusion ───────────────────
plt.rcParams.update({'font.family': 'DejaVu Sans', 'axes.unicode_minus': False,
                     'axes.spines.top': False, 'axes.spines.right': False})

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
axes = axes.flatten()

for ax, (col, label) in zip(axes, new_vars.items()):
    X_plt = sm.add_constant(df[[col]])
    m_plt = sm.OLS(Y, X_plt).fit()

    ax.scatter(df[col], Y, s=70, alpha=0.65, color='steelblue',
               edgecolors='#333', linewidth=0.5)
    x_line = np.linspace(df[col].min(), df[col].max(), 100)
    X_line = sm.add_constant(pd.DataFrame({col: x_line}))
    y_pred = m_plt.predict(X_line)
    ci_df  = m_plt.get_prediction(X_line).summary_frame(alpha=0.05)
    ax.plot(x_line, y_pred, 'r-', linewidth=2)
    ax.fill_between(x_line, ci_df['mean_ci_lower'], ci_df['mean_ci_upper'],
                    alpha=0.2, color='red')

    p_str = f"p = {m_plt.pvalues[col]:.3f}" if m_plt.pvalues[col] >= 0.001 else "p < 0.001"
    ax.set_xlabel(label, fontsize=10)
    ax.set_ylabel("Infusion therapy rate (per 100,000)", fontsize=10)
    ax.set_title(f"beta={m_plt.params[col]:.2f}, {p_str}, R²={m_plt.rsquared:.3f}",
                 fontsize=10)
    ax.grid(alpha=0.25)

fig.suptitle("Supplementary Figure. Additional Climate Variables vs Infusion Therapy Rate\n(N = 47 prefectures, June–September 2023)",
             fontsize=12, fontweight='bold')
plt.tight_layout()
fig.savefig(OUT_DIR / "additional_climate_scatter.png", dpi=300, bbox_inches='tight')
print(f"[OK] Supplementary figure saved: additional_climate_scatter.png")
plt.close(fig)

# ── print Table 2 addendum ───────────────────────────────────────────────────
with open(OUT_DIR / "table2_addendum.txt", 'w', encoding='utf-8') as f:
    f.write("=== Table 2 addendum: Additional Climate Variables ===\n\n")
    f.write(f"{'Variable':<55} {'beta':>10} {'95% CI':>25} {'p':>8} {'R2':>6}\n")
    f.write("-" * 110 + "\n")
    for _, r in df_res.iterrows():
        ci_str = f"({r['CI_lower']:.2f}, {r['CI_upper']:.2f})"
        f.write(f"{r['Variable']:<55} {r['beta']:>10.2f} {ci_str:>25} {r['p']:>8.4f} {r['R2']:>6.3f}\n")

with open(OUT_DIR / "table2_addendum.txt", 'r', encoding='utf-8') as f:
    content = f.read()
# Print safely
import sys
sys.stdout.buffer.write(content.encode('utf-8', errors='replace'))
sys.stdout.buffer.write(b'\n')

print("\n[DONE] Analysis B complete.")
