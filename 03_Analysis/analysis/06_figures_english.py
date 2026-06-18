"""
Figure generation script (English labels) for final manuscript submission.

Generates:
  - Figure 1: Cook's distance plot (outlier detection)
  - Figure 2: Stratified scatter plot by median elderly solo household rate
  - Figure 3: Main scatter plot (all 47 prefectures, labeled)
"""

import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import OLSInfluence

# ── paths ──────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR  = PROJECT_ROOT / "03_Analysis" / "results"
OUTPUT_DIR   = RESULTS_DIR / "sensitivity_analysis"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── prefecture name → English romanization ─────────────────────────────────
PREF_EN = {
    '北海道': 'Hokkaido',   '青森県': 'Aomori',    '岩手県': 'Iwate',
    '宮城県': 'Miyagi',     '秋田県': 'Akita',     '山形県': 'Yamagata',
    '福島県': 'Fukushima',  '茨城県': 'Ibaraki',   '栃木県': 'Tochigi',
    '群馬県': 'Gunma',      '埼玉県': 'Saitama',   '千葉県': 'Chiba',
    '東京都': 'Tokyo',      '神奈川県': 'Kanagawa', '新潟県': 'Niigata',
    '富山県': 'Toyama',     '石川県': 'Ishikawa',  '福井県': 'Fukui',
    '山梨県': 'Yamanashi',  '長野県': 'Nagano',    '岐阜県': 'Gifu',
    '静岡県': 'Shizuoka',   '愛知県': 'Aichi',     '三重県': 'Mie',
    '滋賀県': 'Shiga',      '京都府': 'Kyoto',     '大阪府': 'Osaka',
    '兵庫県': 'Hyogo',      '奈良県': 'Nara',      '和歌山県': 'Wakayama',
    '鳥取県': 'Tottori',    '島根県': 'Shimane',   '岡山県': 'Okayama',
    '広島県': 'Hiroshima',  '山口県': 'Yamaguchi', '徳島県': 'Tokushima',
    '香川県': 'Kagawa',     '愛媛県': 'Ehime',     '高知県': 'Kochi',
    '福岡県': 'Fukuoka',    '佐賀県': 'Saga',      '長崎県': 'Nagasaki',
    '熊本県': 'Kumamoto',   '大分県': 'Oita',      '宮崎県': 'Miyazaki',
    '鹿児島県': 'Kagoshima','沖縄県': 'Okinawa',
}

# ── matplotlib defaults (English, no Japanese font) ────────────────────────
plt.rcParams.update({
    'font.family':       'DejaVu Sans',
    'axes.unicode_minus': False,
    'axes.spines.top':   False,
    'axes.spines.right': False,
})

# ── data & base model ──────────────────────────────────────────────────────
df = pd.read_csv(RESULTS_DIR / "population_adjusted_dataset.csv", encoding='utf-8-sig')
df['pref_en'] = df['都道府県'].map(PREF_EN).fillna(df['都道府県'])

X_col = '高齢者単独世帯率'
Y_col = '点滴注射_per100k'

X_base = sm.add_constant(df[[X_col]])
base_model = sm.OLS(df[Y_col], X_base).fit()

# Cook's distance
influence   = OLSInfluence(base_model)
cooks_d     = influence.cooks_distance[0]
threshold   = 4 / len(df)
outlier_idx = np.where(cooks_d > threshold)[0]

# Stratification
median_rate  = df[X_col].median()
df_high      = df[df[X_col] >= median_rate]
df_low       = df[df[X_col] <  median_rate]
X_h = sm.add_constant(df_high[[X_col]])
X_l = sm.add_constant(df_low[[X_col]])
model_high = sm.OLS(df_high[Y_col], X_h).fit()
model_low  = sm.OLS(df_low[Y_col],  X_l).fit()

print(f"Base model: beta={base_model.params.iloc[1]:.2f}, p={base_model.pvalues.iloc[1]:.4f}, R2={base_model.rsquared:.3f}")
print(f"Outlier prefectures: {[df.iloc[i]['pref_en'] for i in outlier_idx]}")
print(f"Stratification median: {median_rate:.2f}%")

# ════════════════════════════════════════════════════════════════════════════
# Figure 1 — Cook's Distance
# ════════════════════════════════════════════════════════════════════════════
fig1, ax1 = plt.subplots(figsize=(12, 5))

markerline, stemlines, baseline = ax1.stem(
    range(len(cooks_d)), cooks_d, linefmt='grey', markerfmt='o', basefmt=' ')
markerline.set_markersize(5)
stemlines.set_linewidth(0.8)

ax1.axhline(y=threshold, color='red', linestyle='--', linewidth=1.8,
            label=f"Threshold (4/N = {threshold:.3f})")

for i in outlier_idx:
    ax1.annotate(
        df.iloc[i]['pref_en'],
        xy=(i, cooks_d[i]),
        xytext=(8, 4), textcoords='offset points',
        fontsize=9, color='red', fontweight='bold')

ax1.set_xlabel("Prefecture index", fontsize=12)
ax1.set_ylabel("Cook's Distance", fontsize=12)
ax1.set_title("Figure 1. Cook's Distance: Outlier Detection", fontsize=13, fontweight='bold')
ax1.legend(fontsize=11)
ax1.grid(axis='y', alpha=0.3)

plt.tight_layout()
fig1.savefig(OUTPUT_DIR / "cooks_distance.png", dpi=300, bbox_inches='tight')
print("[OK] Figure 1 saved: cooks_distance.png")
plt.close(fig1)

# ════════════════════════════════════════════════════════════════════════════
# Figure 2 — Stratified Analysis
# ════════════════════════════════════════════════════════════════════════════
fig2, (ax2a, ax2b) = plt.subplots(1, 2, figsize=(16, 6), sharey=False)

def _plot_stratum(ax, df_s, model_s, color, title):
    ax.scatter(df_s[X_col], df_s[Y_col],
               s=80, alpha=0.65, color=color, edgecolors='#333333', linewidth=0.5)
    x_line = np.linspace(df_s[X_col].min(), df_s[X_col].max(), 100)
    X_line = sm.add_constant(pd.DataFrame({X_col: x_line}))
    y_pred = model_s.predict(X_line)
    pred_ci = model_s.get_prediction(X_line).summary_frame(alpha=0.05)
    ax.plot(x_line, y_pred, color='darkred', linewidth=2)
    ax.fill_between(x_line,
                    pred_ci['mean_ci_lower'], pred_ci['mean_ci_upper'],
                    alpha=0.20, color='darkred')
    p_str = f"p = {model_s.pvalues.iloc[1]:.3f}" if model_s.pvalues.iloc[1] >= 0.001 else "p < 0.001"
    ax.set_title(
        f"{title}\n"
        f"β = {model_s.params.iloc[1]:.1f}, {p_str}, R² = {model_s.rsquared:.3f}",
        fontsize=12, fontweight='bold')
    ax.set_xlabel("Elderly solo household rate (%)", fontsize=11)
    ax.set_ylabel("Infusion therapy rate (per 100,000)", fontsize=11)
    ax.grid(alpha=0.25)

_plot_stratum(ax2a, df_high, model_high, '#E07070',
              f"High elderly solo HH rate (≥{median_rate:.1f}%, N = {len(df_high)})")
_plot_stratum(ax2b, df_low,  model_low,  '#5B9BD5',
              f"Low elderly solo HH rate (<{median_rate:.1f}%, N = {len(df_low)})")

fig2.suptitle(
    "Figure 2. Stratified Analysis by Median Elderly Solo Household Rate",
    fontsize=13, fontweight='bold', y=1.02)
plt.tight_layout()
fig2.savefig(OUTPUT_DIR / "stratified_analysis.png", dpi=300, bbox_inches='tight')
print("[OK] Figure 2 saved: stratified_analysis.png")
plt.close(fig2)

# ════════════════════════════════════════════════════════════════════════════
# Figure 3 — Main Scatter Plot (all 47 prefectures, labeled)
# ════════════════════════════════════════════════════════════════════════════
fig3, ax3 = plt.subplots(figsize=(14, 10))

ax3.scatter(df[X_col], df[Y_col],
            s=90, alpha=0.65, color='steelblue', edgecolors='#333333', linewidth=0.5)

# Label top-5 and bottom-5 prefectures by infusion rate
top5    = df.nlargest(5,  Y_col)
bottom5 = df.nsmallest(5, Y_col)
label_df = pd.concat([top5, bottom5])

for _, row in label_df.iterrows():
    ax3.annotate(
        row['pref_en'],
        xy=(row[X_col], row[Y_col]),
        xytext=(6, 4), textcoords='offset points',
        fontsize=8.5, color='#222222', alpha=0.85)

# Regression line + 95 % mean CI
x_line  = np.linspace(df[X_col].min(), df[X_col].max(), 200)
X_line  = sm.add_constant(pd.DataFrame({X_col: x_line}))
y_pred  = base_model.predict(X_line)
mean_ci = base_model.get_prediction(X_line).summary_frame(alpha=0.05)

ax3.plot(x_line, y_pred, color='red', linewidth=2, label='Regression line')
ax3.fill_between(x_line,
                 mean_ci['mean_ci_lower'], mean_ci['mean_ci_upper'],
                 alpha=0.20, color='red', label='95% CI')

p_label = "p < 0.001" if base_model.pvalues.iloc[1] < 0.001 else f"p = {base_model.pvalues.iloc[1]:.4f}"
ax3.set_xlabel("Elderly solo household rate (%)", fontsize=13)
ax3.set_ylabel("Infusion therapy rate (per 100,000 population)", fontsize=13)
ax3.set_title(
    f"Figure 3. Elderly Solo Household Rate and Infusion Therapy Utilization\n"
    f"β = {base_model.params.iloc[1]:.2f}, {p_label}, R² = {base_model.rsquared:.3f}  (N = 47 prefectures)",
    fontsize=13, fontweight='bold')
ax3.legend(fontsize=11)
ax3.grid(alpha=0.25)

plt.tight_layout()
fig3.savefig(OUTPUT_DIR / "scatter_elderly_infusion_labeled.png", dpi=300, bbox_inches='tight')
print("[OK] Figure 3 saved: scatter_elderly_infusion_labeled.png")
plt.close(fig3)

print("\nAll 3 figures generated successfully (English labels, 300 dpi).")
