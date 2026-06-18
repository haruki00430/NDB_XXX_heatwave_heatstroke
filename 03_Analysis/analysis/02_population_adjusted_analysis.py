"""
Script 02: Population-adjusted OLS regression (rates per 100,000 population)

Recalculates all outcome and exposure variables as population-adjusted rates
using 2020 Census population denominators, then re-runs OLS regression.
This is the primary analysis model reported in the manuscript.

Data sources:
  1. prefecture_heatwave_summary.csv   - Weather data (heatwave days, WBGT)
  2. elderly_solo_household_rate.csv   - Elderly solo household rate
  3. aircon_prevalence_2014.csv        - Air conditioning prevalence
  4. emergency_infusion_prefecture.csv - NDB infusion therapy claims (G004)
  5. prefecture_population_2020.csv    - Prefecture population (Census 2020)

---

スクリプト 02: 人口調整済み OLS 回帰（人口 10 万人あたり）

2020 年国勢調査の人口を分母として全変数を人口調整率に換算し、
OLS 回帰を再実行します。本スクリプトが論文の主解析モデルに対応します。

データソース:
  1. prefecture_heatwave_summary.csv   - 気象データ（猛暑日数・WBGT）
  2. elderly_solo_household_rate.csv   - 高齢者単独世帯率
  3. aircon_prevalence_2014.csv        - エアコン普及率
  4. emergency_infusion_prefecture.csv - NDB 輸液算定回数（G004）
  5. prefecture_population_2020.csv    - 都道府県別人口（国勢調査 2020）
"""

import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor

# パス設定
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "02_Data" / "interim"
OUTPUT_DIR = PROJECT_ROOT / "03_Analysis" / "results"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 80)
print("人口調整済みOLS回帰分析")
print("=" * 80)

# ===============================
# Phase 1: データ読み込み
# ===============================
print("\n[Phase 1] データ読み込み中...")

# 1. 気象データ
weather = pd.read_csv(DATA_DIR / "prefecture_heatwave_summary.csv", encoding='utf-8-sig')
print(f"  [OK] 気象データ: {len(weather)} 都道府県")

# 2. 高齢者単独世帯率
elderly = pd.read_csv(DATA_DIR / "elderly_solo_household_rate.csv", encoding='utf-8-sig')
print(f"  [OK] 高齢者単独世帯率: {len(elderly)} 都道府県")

# 3. エアコン普及率
aircon = pd.read_csv(DATA_DIR / "aircon_prevalence_2014.csv", encoding='utf-8-sig')
print(f"  [OK] エアコン普及率: {len(aircon)} 都道府県")

# 4. NDB医療データ
ndb = pd.read_csv(DATA_DIR / "emergency_infusion_prefecture.csv", encoding='utf-8-sig')
print(f"  [OK] NDB医療データ: {len(ndb)} 都道府県")

# 5. 人口データ（NEW）
population = pd.read_csv(DATA_DIR / "prefecture_population_2020.csv", encoding='utf-8-sig')
print(f"  [OK] 人口データ: {len(population)} 都道府県")

# ===============================
# Phase 2: データ統合
# ===============================
print("\n[Phase 2] データ統合中...")

# 気象データをベースに統合
df = weather[['都道府県', '猛暑日数', 'WBGT平均']].copy()

# 高齢者単独世帯率を結合
df = df.merge(elderly[['都道府県', '高齢者単独世帯率']], on='都道府県', how='left')

# エアコン普及率を結合
df = df.merge(aircon[['都道府県', 'エアコン普及率']], on='都道府県', how='left')

# NDB医療データを結合
df = df.merge(ndb[['都道府県', '夜間休日救急搬送医学管理料_算定回数', '点滴注射500mL以上_算定回数']],
              on='都道府県', how='left')

# 人口データを結合
df = df.merge(population[['都道府県', '総人口']], on='都道府県', how='left')

print(f"  統合後のデータ: {len(df)} 都道府県 × {len(df.columns)} 変数")

# ===============================
# Phase 3: 人口調整（10万人あたり）
# ===============================
print("\n[Phase 3] 人口調整中（10万人あたり）...")

# 10万人あたりに変換
df['救急医療管理加算_per100k'] = (df['夜間休日救急搬送医学管理料_算定回数'] / df['総人口']) * 100000
df['点滴注射_per100k'] = (df['点滴注射500mL以上_算定回数'] / df['総人口']) * 100000

print(f"  [OK] 救急医療管理加算（10万人あたり）: {df['救急医療管理加算_per100k'].notna().sum()} 都道府県")
print(f"  [OK] 点滴注射（10万人あたり）: {df['点滴注射_per100k'].notna().sum()} 都道府県")

# ===============================
# Phase 4: 欠損値確認
# ===============================
print("\n[Phase 4] 欠損値確認...")
missing = df.isnull().sum()
print(missing[missing > 0])

# 欠損値がある場合は除外
df_clean = df.dropna()
print(f"\n  欠損値除外後: {len(df_clean)} 都道府県")

# ===============================
# Phase 5: 記述統計
# ===============================
print("\n[Phase 5] 記述統計...")
print("\n【人口調整前】")
print(df_clean[['夜間休日救急搬送医学管理料_算定回数', '点滴注射500mL以上_算定回数']].describe())

print("\n【人口調整後（10万人あたり）】")
print(df_clean[['救急医療管理加算_per100k', '点滴注射_per100k']].describe())

# ===============================
# Phase 6: OLS回帰分析（人口調整済み）
# ===============================
print("\n[Phase 6] OLS回帰分析（人口調整済み）...")

# Model 1: 救急医療管理加算（10万人あたり） vs 気象・社会経済要因
y1 = df_clean['救急医療管理加算_per100k']
X1 = df_clean[['猛暑日数', 'WBGT平均', '高齢者単独世帯率', 'エアコン普及率']]
X1_const = sm.add_constant(X1)

model1 = sm.OLS(y1, X1_const).fit()

print("\n" + "=" * 80)
print("Model 1: 救急医療管理加算（10万人あたり） vs 気象・社会経済要因")
print("=" * 80)
print(model1.summary())

# Model 2: 点滴注射（10万人あたり） vs 気象・社会経済要因
y2 = df_clean['点滴注射_per100k']
X2 = df_clean[['猛暑日数', 'WBGT平均', '高齢者単独世帯率', 'エアコン普及率']]
X2_const = sm.add_constant(X2)

model2 = sm.OLS(y2, X2_const).fit()

print("\n" + "=" * 80)
print("Model 2: 点滴注射（10万人あたり） vs 気象・社会経済要因")
print("=" * 80)
print(model2.summary())

# ===============================
# Phase 7: 多重共線性チェック（VIF）
# ===============================
print("\n[Phase 7] 多重共線性チェック（VIF）...")
vif_data = pd.DataFrame()
vif_data["変数"] = X1.columns
vif_data["VIF"] = [variance_inflation_factor(X1.values, i) for i in range(X1.shape[1])]
print(vif_data)

if (vif_data['VIF'] > 10).any():
    print("\n  [!] 警告: VIF > 10 の変数があります（多重共線性の可能性）")
else:
    print("\n  [OK] 多重共線性の問題なし（VIF < 10）")

# ===============================
# Phase 8: 結果保存
# ===============================
print("\n[Phase 8] 結果保存中...")

# 回帰結果をテキストファイルに保存
with open(OUTPUT_DIR / "population_adjusted_regression_results.txt", 'w', encoding='utf-8') as f:
    f.write("=" * 80 + "\n")
    f.write("人口調整済みOLS回帰分析結果\n")
    f.write("=" * 80 + "\n\n")

    f.write("Model 1: 救急医療管理加算（10万人あたり） vs 気象・社会経済要因\n")
    f.write("-" * 80 + "\n")
    f.write(str(model1.summary()) + "\n\n")

    f.write("=" * 80 + "\n")
    f.write("Model 2: 点滴注射（10万人あたり） vs 気象・社会経済要因\n")
    f.write("-" * 80 + "\n")
    f.write(str(model2.summary()) + "\n\n")

    f.write("=" * 80 + "\n")
    f.write("多重共線性チェック（VIF）\n")
    f.write("-" * 80 + "\n")
    f.write(str(vif_data) + "\n")

print(f"  [OK] 回帰結果保存: {OUTPUT_DIR / 'population_adjusted_regression_results.txt'}")

# データセット保存
df_clean.to_csv(OUTPUT_DIR / "population_adjusted_dataset.csv", index=False, encoding='utf-8-sig')
print(f"  [OK] データセット保存: {OUTPUT_DIR / 'population_adjusted_dataset.csv'}")

# ===============================
# Phase 9: 可視化
# ===============================
print("\n[Phase 9] 可視化中...")

# 日本語フォント設定
plt.rcParams['font.sans-serif'] = ['MS Gothic', 'Yu Gothic', 'Meiryo']
plt.rcParams['axes.unicode_minus'] = False

# 散布図マトリックス
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Model 1の散布図
axes[0, 0].scatter(df_clean['猛暑日数'], df_clean['救急医療管理加算_per100k'], alpha=0.6)
axes[0, 0].set_xlabel('猛暑日数（日）')
axes[0, 0].set_ylabel('救急医療管理加算（10万人あたり）')
axes[0, 0].set_title(f'R² = {model1.rsquared:.3f}')

axes[0, 1].scatter(df_clean['WBGT平均'], df_clean['救急医療管理加算_per100k'], alpha=0.6)
axes[0, 1].set_xlabel('WBGT平均（℃）')
axes[0, 1].set_ylabel('救急医療管理加算（10万人あたり）')

# Model 2の散布図
axes[1, 0].scatter(df_clean['猛暑日数'], df_clean['点滴注射_per100k'], alpha=0.6)
axes[1, 0].set_xlabel('猛暑日数（日）')
axes[1, 0].set_ylabel('点滴注射（10万人あたり）')
axes[1, 0].set_title(f'R² = {model2.rsquared:.3f}')

axes[1, 1].scatter(df_clean['WBGT平均'], df_clean['点滴注射_per100k'], alpha=0.6)
axes[1, 1].set_xlabel('WBGT平均（℃）')
axes[1, 1].set_ylabel('点滴注射（10万人あたり）')

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "population_adjusted_scatter_matrix.png", dpi=300, bbox_inches='tight')
print(f"  [OK] 散布図保存: {OUTPUT_DIR / 'population_adjusted_scatter_matrix.png'}")

plt.close()

# ===============================
# 完了
# ===============================
print("\n" + "=" * 80)
print("人口調整済み回帰分析が完了しました！")
print("=" * 80)
print(f"\n出力ファイル:")
print(f"  1. 回帰結果: {OUTPUT_DIR / 'population_adjusted_regression_results.txt'}")
print(f"  2. データセット: {OUTPUT_DIR / 'population_adjusted_dataset.csv'}")
print(f"  3. 散布図: {OUTPUT_DIR / 'population_adjusted_scatter_matrix.png'}")
print("\n主要な発見:")
print(f"  - Model 1 R^2: {model1.rsquared:.4f} (Adj. R^2: {model1.rsquared_adj:.4f})")
print(f"  - Model 2 R^2: {model2.rsquared:.4f} (Adj. R^2: {model2.rsquared_adj:.4f})")
print(f"  - F統計量 (Model 1): {model1.fvalue:.2f} (p={model1.f_pvalue:.4f})")
print(f"  - F統計量 (Model 2): {model2.fvalue:.2f} (p={model2.f_pvalue:.4f})")
