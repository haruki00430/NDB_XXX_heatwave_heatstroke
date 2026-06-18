"""
Script 01: Data integration and initial OLS regression analysis

Integrates prefecture-level datasets and fits simple OLS regression models
examining the association between climatic/social predictors and
dehydration-related healthcare utilization.

Data sources:
  1. prefecture_heatwave_summary.csv   - Weather data (heatwave days, WBGT)
  2. elderly_solo_household_rate.csv   - Elderly solo household rate (Census 2020)
  3. aircon_prevalence_2014.csv        - Air conditioning prevalence
  4. emergency_infusion_prefecture.csv - NDB infusion therapy claims (G004)

Outcome (Y): Infusion therapy rate ≥500 mL (G004), per 100,000 population
Predictors (X): Heatwave days, WBGT, elderly solo household rate, AC prevalence

---

スクリプト 01: データ統合と初期 OLS 回帰分析

都道府県別データセットを統合し、気候・社会指標と脱水関連医療利用との
関連を検討するシンプル OLS 回帰モデルを実行します。

データソース:
  1. prefecture_heatwave_summary.csv   - 気象データ（猛暑日数・WBGT指数）
  2. elderly_solo_household_rate.csv   - 高齢者単独世帯率（国勢調査 2020）
  3. aircon_prevalence_2014.csv        - エアコン普及率
  4. emergency_infusion_prefecture.csv - NDB 輸液算定回数（G004）

従属変数（Y）: 輸液療法実施率（G004、500 mL 以上）、人口 10 万人あたり
独立変数（X）: 猛暑日数、WBGT、高齢者単独世帯率、エアコン普及率
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import statsmodels.api as sm
from scipy import stats

# 日本語フォント設定
plt.rcParams['font.family'] = ['MS Gothic', 'Yu Gothic', 'Meiryo']
plt.rcParams['axes.unicode_minus'] = False

# パス設定（projects/NDB_XXX_heatwave_heatstroke/ がプロジェクトルート）
PROJECT_ROOT = Path(__file__).resolve().parents[2]  # 03_Analysis/analysis/ から2階層上
DATA_DIR = PROJECT_ROOT / "02_Data" / "interim"
OUTPUT_DIR = PROJECT_ROOT / "03_Analysis" / "results"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 80)
print("猛暑・熱中症データの統合とOLS回帰分析")
print("=" * 80)

# ==============================================================================
# 1. データ読み込み
# ==============================================================================
print("\n[1/5] データ読み込み")
print("-" * 80)

# 気象データ
df_weather = pd.read_csv(DATA_DIR / "prefecture_heatwave_summary.csv", encoding='utf-8-sig')
print(f"[OK] 気象データ: {len(df_weather)} 都道府県")
print(f"     カラム: {df_weather.columns.tolist()}")

# 高齢者単独世帯率
df_elderly = pd.read_csv(DATA_DIR / "elderly_solo_household_rate.csv", encoding='utf-8-sig')
print(f"[OK] 高齢者単独世帯率: {len(df_elderly)} 都道府県")
print(f"     カラム: {df_elderly.columns.tolist()}")

# エアコン普及率
df_aircon = pd.read_csv(DATA_DIR / "aircon_prevalence_2014.csv", encoding='utf-8-sig')
print(f"[OK] エアコン普及率: {len(df_aircon)} 都道府県")
print(f"     カラム: {df_aircon.columns.tolist()}")

# NDB救急医療管理加算・輸液
df_ndb = pd.read_csv(DATA_DIR / "emergency_infusion_prefecture.csv", encoding='utf-8-sig')
print(f"[OK] NDB救急医療管理加算・輸液: {len(df_ndb)} 都道府県")
print(f"     カラム: {df_ndb.columns.tolist()}")

# ==============================================================================
# 2. データ統合
# ==============================================================================
print("\n[2/5] データ統合")
print("-" * 80)

# 都道府県名でマージ
df_merged = df_weather.copy()
df_merged = df_merged.merge(df_elderly, on='都道府県', how='left')
df_merged = df_merged.merge(df_aircon, on='都道府県', how='left')
df_merged = df_merged.merge(df_ndb, on='都道府県', how='left')

print(f"[OK] 統合データ: {len(df_merged)} 都道府県 × {len(df_merged.columns)} 変数")
print(f"\n統合後のカラム:")
for i, col in enumerate(df_merged.columns, 1):
    print(f"  {i:2d}. {col}")

# 欠損値チェック
print("\n欠損値チェック:")
missing = df_merged.isnull().sum()
if missing.sum() > 0:
    print(missing[missing > 0])
else:
    print("  欠損値なし")

# 統合データを保存
output_integrated = OUTPUT_DIR / "integrated_heatwave_data.csv"
df_merged.to_csv(output_integrated, index=False, encoding='utf-8-sig')
print(f"\n[OK] 統合データ保存: {output_integrated}")

# ==============================================================================
# 3. 記述統計
# ==============================================================================
print("\n[3/5] 記述統計")
print("-" * 80)

# 主要変数の記述統計
key_vars = [
    '猛暑日数',
    'WBGT平均',
    '高齢者単独世帯率',
    'エアコン普及率',
    '夜間休日救急搬送医学管理料_算定回数',
    '点滴注射500mL以上_算定回数'
]

desc_stats = df_merged[key_vars].describe().T
desc_stats['missing'] = df_merged[key_vars].isnull().sum()
print("\n記述統計:")
print(desc_stats.to_string())

# ==============================================================================
# 4. OLS回帰分析
# ==============================================================================
print("\n[4/5] OLS回帰分析")
print("-" * 80)

# モデル1: 夜間休日救急搬送医学管理料を従属変数とする
print("\n" + "=" * 80)
print("モデル1: 夜間休日救急搬送医学管理料 ~ 猛暑日数 + WBGT + 高齢者率 + エアコン普及率")
print("=" * 80)

# 欠損値を除外
df_model1 = df_merged[[
    '都道府県',
    '猛暑日数',
    'WBGT平均',
    '高齢者単独世帯率',
    'エアコン普及率',
    '夜間休日救急搬送医学管理料_算定回数'
]].dropna()

print(f"\n分析対象: {len(df_model1)} 都道府県")

# 独立変数・従属変数の設定
X1 = df_model1[[
    '猛暑日数',
    'WBGT平均',
    '高齢者単独世帯率',
    'エアコン普及率'
]]
y1 = df_model1['夜間休日救急搬送医学管理料_算定回数']

# 定数項を追加
X1_const = sm.add_constant(X1)

# OLS回帰
model1 = sm.OLS(y1, X1_const).fit()
print("\n" + model1.summary().as_text())

# 結果をテキストファイルに保存
with open(OUTPUT_DIR / "regression_model1_emergency.txt", "w", encoding='utf-8') as f:
    f.write("モデル1: 夜間休日救急搬送医学管理料 ~ 猛暑日数 + WBGT + 高齢者率 + エアコン普及率\n")
    f.write("=" * 80 + "\n\n")
    f.write(model1.summary().as_text())

# モデル2: 点滴注射500mL以上を従属変数とする
print("\n\n" + "=" * 80)
print("モデル2: 点滴注射500mL以上 ~ 猛暑日数 + WBGT + 高齢者率 + エアコン普及率")
print("=" * 80)

df_model2 = df_merged[[
    '都道府県',
    '猛暑日数',
    'WBGT平均',
    '高齢者単独世帯率',
    'エアコン普及率',
    '点滴注射500mL以上_算定回数'
]].dropna()

print(f"\n分析対象: {len(df_model2)} 都道府県")

X2 = df_model2[[
    '猛暑日数',
    'WBGT平均',
    '高齢者単独世帯率',
    'エアコン普及率'
]]
y2 = df_model2['点滴注射500mL以上_算定回数']

X2_const = sm.add_constant(X2)
model2 = sm.OLS(y2, X2_const).fit()
print("\n" + model2.summary().as_text())

# 結果をテキストファイルに保存
with open(OUTPUT_DIR / "regression_model2_infusion.txt", "w", encoding='utf-8') as f:
    f.write("モデル2: 点滴注射500mL以上 ~ 猛暑日数 + WBGT + 高齢者率 + エアコン普及率\n")
    f.write("=" * 80 + "\n\n")
    f.write(model2.summary().as_text())

# ==============================================================================
# 5. 可視化
# ==============================================================================
print("\n[5/5] 可視化")
print("-" * 80)

# 5-1. 相関ヒートマップ
fig1, ax1 = plt.subplots(figsize=(10, 8))
corr_matrix = df_merged[key_vars].corr()
sns.heatmap(corr_matrix, annot=True, fmt='.3f', cmap='coolwarm', center=0,
            square=True, linewidths=1, cbar_kws={"shrink": 0.8}, ax=ax1)
ax1.set_title('相関ヒートマップ', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "correlation_heatmap.png", dpi=300, bbox_inches='tight')
print("[OK] 相関ヒートマップ保存: correlation_heatmap.png")
plt.close()

# 5-2. 散布図（猛暑日数 vs 救急搬送医学管理料）
fig2, ax2 = plt.subplots(figsize=(10, 6))
ax2.scatter(df_model1['猛暑日数'], df_model1['夜間休日救急搬送医学管理料_算定回数'], alpha=0.6)

# 回帰直線
z = np.polyfit(df_model1['猛暑日数'], df_model1['夜間休日救急搬送医学管理料_算定回数'], 1)
p = np.poly1d(z)
ax2.plot(df_model1['猛暑日数'], p(df_model1['猛暑日数']), "r--", alpha=0.8, linewidth=2)

# Pearson相関係数
r, p_val = stats.pearsonr(df_model1['猛暑日数'], df_model1['夜間休日救急搬送医学管理料_算定回数'])
ax2.text(0.05, 0.95, f'r = {r:.3f}, p = {p_val:.4f}',
         transform=ax2.transAxes, fontsize=12, verticalalignment='top',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

ax2.set_xlabel('猛暑日数（日）', fontsize=12)
ax2.set_ylabel('夜間休日救急搬送医学管理料（算定回数）', fontsize=12)
ax2.set_title('猛暑日数 vs 救急搬送医学管理料', fontsize=14, fontweight='bold')
ax2.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "scatter_heatdays_emergency.png", dpi=300, bbox_inches='tight')
print("[OK] 散布図保存: scatter_heatdays_emergency.png")
plt.close()

# 5-3. 散布図（WBGT vs 点滴注射）
fig3, ax3 = plt.subplots(figsize=(10, 6))
ax3.scatter(df_model2['WBGT平均'], df_model2['点滴注射500mL以上_算定回数'], alpha=0.6)

# 回帰直線
z2 = np.polyfit(df_model2['WBGT平均'], df_model2['点滴注射500mL以上_算定回数'], 1)
p2 = np.poly1d(z2)
ax3.plot(df_model2['WBGT平均'], p2(df_model2['WBGT平均']), "r--", alpha=0.8, linewidth=2)

# Pearson相関係数
r2, p_val2 = stats.pearsonr(df_model2['WBGT平均'], df_model2['点滴注射500mL以上_算定回数'])
ax3.text(0.05, 0.95, f'r = {r2:.3f}, p = {p_val2:.4f}',
         transform=ax3.transAxes, fontsize=12, verticalalignment='top',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

ax3.set_xlabel('WBGT指数（℃）', fontsize=12)
ax3.set_ylabel('点滴注射500mL以上（算定回数）', fontsize=12)
ax3.set_title('WBGT指数 vs 点滴注射', fontsize=14, fontweight='bold')
ax3.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "scatter_wbgt_infusion.png", dpi=300, bbox_inches='tight')
print("[OK] 散布図保存: scatter_wbgt_infusion.png")
plt.close()

# ==============================================================================
# 完了
# ==============================================================================
print("\n" + "=" * 80)
print("分析完了！")
print("=" * 80)
print(f"\n出力ファイル:")
print(f"  1. {output_integrated}")
print(f"  2. {OUTPUT_DIR / 'regression_model1_emergency.txt'}")
print(f"  3. {OUTPUT_DIR / 'regression_model2_infusion.txt'}")
print(f"  4. {OUTPUT_DIR / 'correlation_heatmap.png'}")
print(f"  5. {OUTPUT_DIR / 'scatter_heatdays_emergency.png'}")
print(f"  6. {OUTPUT_DIR / 'scatter_wbgt_infusion.png'}")
print("\n主要結果:")
print(f"  モデル1 R-squared: {model1.rsquared:.4f}")
print(f"  モデル2 R-squared: {model2.rsquared:.4f}")
