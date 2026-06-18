"""
Analysis A: FDMA heatstroke ambulance transport validation (#11 response)

Aggregates FDMA R5 (2023) daily ambulance transport data for summer (June–September)
by prefecture, normalizes per 100,000 population, and examines:
  1. Correlation with infusion therapy rate (construct validity check)
  2. Correlation with elderly solo household rate

Generates:
  - Supplementary Figure S1: FDMA transport rate vs infusion therapy rate
  - Supplementary Figure S2: FDMA transport rate vs elderly solo household rate
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path

PROJECT_ROOT  = Path(__file__).resolve().parents[2]
FDMA_PATH     = PROJECT_ROOT / "02_Data" / "raw" / "fdma_heatstroke_r5_2023.xlsx"
DATASET_PATH  = PROJECT_ROOT / "03_Analysis" / "results" / "population_adjusted_dataset.csv"
OUT_DIR       = PROJECT_ROOT / "03_Analysis" / "results" / "fdma_validation"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ── JIS X 0401 prefecture code → name mapping ───────────────────────────────
PREF_CODE = {
    1: '北海道',  2: '青森県',  3: '岩手県',  4: '宮城県',  5: '秋田県',
    6: '山形県',  7: '福島県',  8: '茨城県',  9: '栃木県', 10: '群馬県',
   11: '埼玉県', 12: '千葉県', 13: '東京都', 14: '神奈川県',15: '新潟県',
   16: '富山県', 17: '石川県', 18: '福井県', 19: '山梨県', 20: '長野県',
   21: '岐阜県', 22: '静岡県', 23: '愛知県', 24: '三重県', 25: '滋賀県',
   26: '京都府', 27: '大阪府', 28: '兵庫県', 29: '奈良県', 30: '和歌山県',
   31: '鳥取県', 32: '島根県', 33: '岡山県', 34: '広島県', 35: '山口県',
   36: '徳島県', 37: '香川県', 38: '愛媛県', 39: '高知県', 40: '福岡県',
   41: '佐賀県', 42: '長崎県', 43: '熊本県', 44: '大分県', 45: '宮崎県',
   46: '鹿児島県',47: '沖縄県',
}

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
    '福岡県': 'Fukuoka',    '佐賀県': 'Saga',       '長崎県': 'Nagasaki',
    '熊本県': 'Kumamoto',   '大分県': 'Oita',      '宮崎県': 'Miyazaki',
    '鹿児島県': 'Kagoshima','沖縄県': 'Okinawa',
}

# ── aggregate FDMA summer data by prefecture ─────────────────────────────────
summer_sheets = ['2023_06', '2023_07', '2023_08', '2023_09']
dfs = []
for sh in summer_sheets:
    df_m = pd.read_excel(FDMA_PATH, sheet_name=sh, header=0)
    dfs.append(df_m[['都道府県コード', '搬送人員（計）']])
df_fdma = pd.concat(dfs, ignore_index=True)

# Sum summer transports per prefecture
fdma_sum = (df_fdma.groupby('都道府県コード')['搬送人員（計）']
                   .sum()
                   .reset_index()
                   .rename(columns={'搬送人員（計）': 'heatstroke_transport_summer'}))

fdma_sum['都道府県'] = fdma_sum['都道府県コード'].map(PREF_CODE)
print(f"[OK] FDMA aggregated: {len(fdma_sum)} prefectures, "
      f"total summer transports = {fdma_sum['heatstroke_transport_summer'].sum():,}")

# ── merge with main dataset ──────────────────────────────────────────────────
main = pd.read_csv(DATASET_PATH, encoding='utf-8-sig')
df   = main.merge(fdma_sum[['都道府県', 'heatstroke_transport_summer']], on='都道府県', how='inner')

# Normalize FDMA transports per 100,000 population
df['fdma_per100k'] = df['heatstroke_transport_summer'] / df['総人口'] * 100_000
print(f"[OK] Merged: {len(df)} rows")
print(f"     FDMA per 100k: mean={df['fdma_per100k'].mean():.1f}, "
      f"min={df['fdma_per100k'].min():.1f}, max={df['fdma_per100k'].max():.1f}")

# Save merged data
df[['都道府県', 'heatstroke_transport_summer', 'fdma_per100k',
    '点滴注射_per100k', '高齢者単独世帯率']].to_csv(
    OUT_DIR / "fdma_validation_dataset.csv", index=False, encoding='utf-8-sig')

# ── regressions ──────────────────────────────────────────────────────────────
def run_reg(y, x_col, df):
    X = sm.add_constant(df[[x_col]])
    m = sm.OLS(y, X).fit()
    ci = m.conf_int(alpha=0.05)
    from scipy import stats
    r, p_r = stats.pearsonr(df[x_col], y)
    return m, ci, r, p_r

Y_infusion = df['点滴注射_per100k']
Y_fdma     = df['fdma_per100k']

# Model 1: FDMA → infusion (construct validity)
m1, ci1, r1, p_r1 = run_reg(Y_infusion, 'fdma_per100k', df)
# Model 2: elderly solo rate → FDMA (shows same predictor explains heatstroke transport too)
m2, ci2, r2, p_r2 = run_reg(Y_fdma, '高齢者単独世帯率', df)

with open(OUT_DIR / "fdma_regression_results.txt", 'w', encoding='utf-8') as f:
    f.write("=== FDMA Validation Regression Results ===\n\n")
    f.write("Model 1: Heatstroke transport rate → Infusion therapy rate\n")
    f.write(f"  beta={m1.params['fdma_per100k']:.2f}, "
            f"95%CI=({ci1.loc['fdma_per100k',0]:.2f}, {ci1.loc['fdma_per100k',1]:.2f}), "
            f"p={m1.pvalues['fdma_per100k']:.4f}, R2={m1.rsquared:.3f}\n")
    f.write(f"  Pearson r={r1:.3f}, p={p_r1:.4f}\n\n")
    f.write("Model 2: Elderly solo household rate → Heatstroke transport rate\n")
    f.write(f"  beta={m2.params['高齢者単独世帯率']:.2f}, "
            f"95%CI=({ci2.loc['高齢者単独世帯率',0]:.2f}, {ci2.loc['高齢者単独世帯率',1]:.2f}), "
            f"p={m2.pvalues['高齢者単独世帯率']:.4f}, R2={m2.rsquared:.3f}\n")
    f.write(f"  Pearson r={r2:.3f}, p={p_r2:.4f}\n")

with open(OUT_DIR / "fdma_regression_results.txt", 'r', encoding='utf-8') as f:
    print("\n" + f.read())

# ── figures ──────────────────────────────────────────────────────────────────
plt.rcParams.update({'font.family': 'DejaVu Sans', 'axes.unicode_minus': False,
                     'axes.spines.top': False, 'axes.spines.right': False})

df['pref_en'] = df['都道府県'].map(PREF_EN).fillna(df['都道府県'])

# ── Figure S1: FDMA transport vs infusion therapy ────────────────────────────
fig1, ax1 = plt.subplots(figsize=(10, 7))
ax1.scatter(df['fdma_per100k'], Y_infusion, s=80, alpha=0.65, color='steelblue',
            edgecolors='#333', linewidth=0.5)

x_line = np.linspace(df['fdma_per100k'].min(), df['fdma_per100k'].max(), 100)
X_line = sm.add_constant(pd.DataFrame({'fdma_per100k': x_line}))
y_pred = m1.predict(X_line)
ci_df  = m1.get_prediction(X_line).summary_frame(alpha=0.05)
ax1.plot(x_line, y_pred, 'r-', linewidth=2, label='Regression line')
ax1.fill_between(x_line, ci_df['mean_ci_lower'], ci_df['mean_ci_upper'],
                 alpha=0.2, color='red', label='95% CI')

# Label top/bottom 5 by FDMA rate
top5    = df.nlargest(5,  'fdma_per100k')
bottom5 = df.nsmallest(5, 'fdma_per100k')
for _, row in pd.concat([top5, bottom5]).iterrows():
    ax1.annotate(row['pref_en'], xy=(row['fdma_per100k'], row['点滴注射_per100k']),
                 xytext=(5, 3), textcoords='offset points', fontsize=8.5, alpha=0.85)

p_str1 = f"p = {m1.pvalues['fdma_per100k']:.3f}" if m1.pvalues['fdma_per100k'] >= 0.001 else "p < 0.001"
ax1.set_xlabel("Heatstroke ambulance transport rate (per 100,000, June–Sep 2023)", fontsize=12)
ax1.set_ylabel("Infusion therapy rate (per 100,000)", fontsize=12)
ax1.set_title(
    f"Supplementary Figure S1. Heatstroke Ambulance Transport Rate and Infusion Therapy Utilization\n"
    f"beta = {m1.params['fdma_per100k']:.2f}, {p_str1}, r = {r1:.3f}, R² = {m1.rsquared:.3f}  (N = 47 prefectures)",
    fontsize=11, fontweight='bold')
ax1.legend(fontsize=10)
ax1.grid(alpha=0.25)
plt.tight_layout()
fig1.savefig(OUT_DIR / "figS1_fdma_vs_infusion.png", dpi=300, bbox_inches='tight')
print("[OK] Figure S1 saved: figS1_fdma_vs_infusion.png")
plt.close(fig1)

# ── Figure S2: elderly solo rate vs FDMA transport ───────────────────────────
fig2, ax2 = plt.subplots(figsize=(10, 7))
ax2.scatter(df['高齢者単独世帯率'], Y_fdma, s=80, alpha=0.65, color='#E07070',
            edgecolors='#333', linewidth=0.5)

x_line2 = np.linspace(df['高齢者単独世帯率'].min(), df['高齢者単独世帯率'].max(), 100)
X_line2 = sm.add_constant(pd.DataFrame({'高齢者単独世帯率': x_line2}))
y_pred2 = m2.predict(X_line2)
ci_df2  = m2.get_prediction(X_line2).summary_frame(alpha=0.05)
ax2.plot(x_line2, y_pred2, 'r-', linewidth=2, label='Regression line')
ax2.fill_between(x_line2, ci_df2['mean_ci_lower'], ci_df2['mean_ci_upper'],
                 alpha=0.2, color='red', label='95% CI')

for _, row in pd.concat([df.nlargest(5, 'fdma_per100k'), df.nsmallest(5, 'fdma_per100k')]).iterrows():
    ax2.annotate(row['pref_en'], xy=(row['高齢者単独世帯率'], row['fdma_per100k']),
                 xytext=(5, 3), textcoords='offset points', fontsize=8.5, alpha=0.85)

p_str2 = f"p = {m2.pvalues['高齢者単独世帯率']:.3f}" if m2.pvalues['高齢者単独世帯率'] >= 0.001 else "p < 0.001"
ax2.set_xlabel("Elderly solo household rate (%)", fontsize=12)
ax2.set_ylabel("Heatstroke ambulance transport rate (per 100,000)", fontsize=12)
ax2.set_title(
    f"Supplementary Figure S2. Elderly Solo Household Rate and Heatstroke Ambulance Transport Rate\n"
    f"beta = {m2.params['高齢者単独世帯率']:.2f}, {p_str2}, r = {r2:.3f}, R² = {m2.rsquared:.3f}  (N = 47 prefectures)",
    fontsize=11, fontweight='bold')
ax2.legend(fontsize=10)
ax2.grid(alpha=0.25)
plt.tight_layout()
fig2.savefig(OUT_DIR / "figS2_elderly_vs_fdma.png", dpi=300, bbox_inches='tight')
print("[OK] Figure S2 saved: figS2_elderly_vs_fdma.png")
plt.close(fig2)

print("\n[DONE] Analysis A (FDMA validation) complete.")
