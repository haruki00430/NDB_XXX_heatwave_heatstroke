"""
Script 04: Stepwise selection and univariate regression (variable selection)

Runs stepwise forward selection and exhaustive univariate regression to
evaluate the independent association of each predictor with infusion therapy
utilization, bypassing multicollinearity by examining one predictor at a time.
Model selection uses AIC/BIC criteria.

Data source:
  - population_adjusted_dataset.csv (population-adjusted rates)

This script generates Table 2 of the manuscript (univariate regression results).

---

スクリプト 04: ステップワイズ回帰と単回帰分析（変数選択）

多重共線性を回避するため、各変数を個別に検討する単回帰と
前進法ステップワイズ選択を実行します。モデル選択には AIC/BIC を使用します。

データソース:
  - population_adjusted_dataset.csv（人口調整済みレート）

本スクリプトが論文 Table 2（単回帰結果）を生成します。
"""

import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
from itertools import combinations

# パス設定
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "02_Data" / "interim"
RESULTS_DIR = PROJECT_ROOT / "03_Analysis" / "results"
OUTPUT_DIR = RESULTS_DIR / "stepwise_univariate"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 80)
print("ステップワイズ回帰と単回帰分析")
print("=" * 80)

# ===============================
# Phase 1: データ読み込み
# ===============================
print("\n[Phase 1] データ読み込み...")

df = pd.read_csv(RESULTS_DIR / "population_adjusted_dataset.csv", encoding='utf-8-sig')
print(f"  データ件数: {len(df)} 都道府県")

# 特徴量と目的変数を定義
feature_names = ['猛暑日数', 'WBGT平均', '高齢者単独世帯率', 'エアコン普及率']
target_names = ['救急医療管理加算_per100k', '点滴注射_per100k']

X = df[feature_names]
y1 = df['救急医療管理加算_per100k']
y2 = df['点滴注射_per100k']

# ===============================
# Phase 2: 単回帰分析
# ===============================
print("\n[Phase 2] 単回帰分析（各変数の独立した効果）...")

def univariate_regression(X, y, feature_names, model_name):
    """単回帰分析を実行"""
    results = []

    for feature in feature_names:
        X_single = sm.add_constant(X[[feature]])
        model = sm.OLS(y, X_single).fit()

        results.append({
            '変数': feature,
            '係数': model.params[1],
            '標準誤差': model.bse[1],
            't値': model.tvalues[1],
            'p値': model.pvalues[1],
            'R^2': model.rsquared,
            'Adj_R^2': model.rsquared_adj,
            'AIC': model.aic,
            'BIC': model.bic
        })

    df_results = pd.DataFrame(results)
    df_results = df_results.sort_values('p値')

    print(f"\n  {model_name}:")
    print(df_results.to_string(index=False))

    return df_results

# Model 1: 救急医療管理加算
univariate_results1 = univariate_regression(X, y1, feature_names, "Model 1 (救急医療管理加算)")

# Model 2: 点滴注射
univariate_results2 = univariate_regression(X, y2, feature_names, "Model 2 (点滴注射)")

# ===============================
# Phase 3: 前進選択法（Forward Selection）
# ===============================
print("\n[Phase 3] 前進選択法（Forward Selection）...")

def forward_selection(X, y, feature_names, criterion='aic'):
    """前進選択法でモデル選択"""
    selected_features = []
    remaining_features = feature_names.copy()

    best_criterion = np.inf
    history = []

    while remaining_features:
        criterion_values = []

        for feature in remaining_features:
            features_to_test = selected_features + [feature]
            X_test = sm.add_constant(X[features_to_test])
            model = sm.OLS(y, X_test).fit()

            if criterion == 'aic':
                crit = model.aic
            elif criterion == 'bic':
                crit = model.bic
            else:
                crit = -model.rsquared_adj

            criterion_values.append((feature, crit, model.rsquared, model.rsquared_adj))

        # 最小のAIC/BICを持つ変数を選択
        best_feature, best_crit, r2, adj_r2 = min(criterion_values, key=lambda x: x[1])

        # 改善がない場合は停止
        if best_crit >= best_criterion:
            break

        selected_features.append(best_feature)
        remaining_features.remove(best_feature)
        best_criterion = best_crit

        history.append({
            'Step': len(selected_features),
            '追加変数': best_feature,
            '選択変数': ', '.join(selected_features),
            criterion.upper(): best_crit,
            'R^2': r2,
            'Adj_R^2': adj_r2
        })

    return selected_features, pd.DataFrame(history)

# Model 1: AICによる前進選択
print("\n  Model 1 (救急医療管理加算) - AIC基準:")
selected_features1_aic, history1_aic = forward_selection(X, y1, feature_names, criterion='aic')
print(history1_aic.to_string(index=False))
print(f"\n  最終選択変数: {', '.join(selected_features1_aic)}")

# Model 2: AICによる前進選択
print("\n  Model 2 (点滴注射) - AIC基準:")
selected_features2_aic, history2_aic = forward_selection(X, y2, feature_names, criterion='aic')
print(history2_aic.to_string(index=False))
print(f"\n  最終選択変数: {', '.join(selected_features2_aic)}")

# ===============================
# Phase 4: 後退選択法（Backward Elimination）
# ===============================
print("\n[Phase 4] 後退選択法（Backward Elimination）...")

def backward_elimination(X, y, feature_names, criterion='aic', alpha=0.05):
    """後退選択法でモデル選択"""
    selected_features = feature_names.copy()
    history = []

    while len(selected_features) > 0:
        X_test = sm.add_constant(X[selected_features])
        model = sm.OLS(y, X_test).fit()

        if criterion == 'aic':
            crit = model.aic
        elif criterion == 'bic':
            crit = model.bic
        else:
            crit = -model.rsquared_adj

        history.append({
            'Step': len(history) + 1,
            '削除変数': '-' if len(selected_features) == len(feature_names) else removed_feature,
            '残存変数': ', '.join(selected_features),
            criterion.upper(): crit,
            'R^2': model.rsquared,
            'Adj_R^2': model.rsquared_adj
        })

        # p値が最大の変数を削除
        pvalues = model.pvalues[1:]  # 定数項を除く
        max_pvalue_idx = pvalues.argmax()
        max_pvalue = pvalues.iloc[max_pvalue_idx]

        # すべての変数が有意な場合は停止
        if max_pvalue < alpha:
            break

        removed_feature = selected_features[max_pvalue_idx]
        selected_features.pop(max_pvalue_idx)

        # 変数が1つもなくなった場合は停止
        if len(selected_features) == 0:
            break

    return selected_features, pd.DataFrame(history)

# Model 1: 後退選択
print("\n  Model 1 (救急医療管理加算) - p値基準（α=0.05）:")
selected_features1_back, history1_back = backward_elimination(X, y1, feature_names, alpha=0.05)
print(history1_back.to_string(index=False))
print(f"\n  最終選択変数: {', '.join(selected_features1_back) if selected_features1_back else '（なし）'}")

# Model 2: 後退選択
print("\n  Model 2 (点滴注射) - p値基準（α=0.05）:")
selected_features2_back, history2_back = backward_elimination(X, y2, feature_names, alpha=0.05)
print(history2_back.to_string(index=False))
print(f"\n  最終選択変数: {', '.join(selected_features2_back) if selected_features2_back else '（なし）'}")

# ===============================
# Phase 5: 最適モデルの構築
# ===============================
print("\n[Phase 5] 最適モデルの構築...")

def build_final_model(X, y, selected_features, model_name):
    """選択された変数で最終モデルを構築"""
    if not selected_features:
        print(f"\n  {model_name}: 選択された変数がありません")
        return None

    X_final = sm.add_constant(X[selected_features])
    model = sm.OLS(y, X_final).fit()

    print(f"\n  {model_name}:")
    print(f"    選択変数: {', '.join(selected_features)}")
    print(f"    R^2: {model.rsquared:.4f}")
    print(f"    Adj R^2: {model.rsquared_adj:.4f}")
    print(f"    AIC: {model.aic:.2f}")
    print(f"    BIC: {model.bic:.2f}")
    print(f"    F統計量: {model.fvalue:.2f} (p={model.f_pvalue:.4f})")

    # VIFチェック
    if len(selected_features) > 1:
        vif_data = pd.DataFrame()
        vif_data["変数"] = selected_features
        vif_data["VIF"] = [variance_inflation_factor(X[selected_features].values, i)
                          for i in range(len(selected_features))]
        print(f"\n    VIF:")
        print(vif_data.to_string(index=False))

    return model

# Model 1: 前進選択法で選ばれた変数
model1_forward = build_final_model(X, y1, selected_features1_aic, "Model 1 (前進選択法)")

# Model 2: 前進選択法で選ばれた変数
model2_forward = build_final_model(X, y2, selected_features2_aic, "Model 2 (前進選択法)")

# ===============================
# Phase 6: 可視化
# ===============================
print("\n[Phase 6] 可視化...")

# 日本語フォント設定
plt.rcParams['font.sans-serif'] = ['MS Gothic', 'Yu Gothic', 'Meiryo']
plt.rcParams['axes.unicode_minus'] = False

# 6-1. 単回帰の結果（係数プロット）
fig1, (ax1a, ax1b) = plt.subplots(1, 2, figsize=(14, 6))

# Model 1
x_pos = np.arange(len(univariate_results1))
colors1 = ['red' if p < 0.05 else 'gray' for p in univariate_results1['p値']]
ax1a.barh(x_pos, univariate_results1['係数'], color=colors1, alpha=0.7)
ax1a.set_yticks(x_pos)
ax1a.set_yticklabels(univariate_results1['変数'])
ax1a.set_xlabel('係数', fontsize=12)
ax1a.set_title('Model 1: 単回帰係数（赤=p<0.05）', fontsize=14, fontweight='bold')
ax1a.axvline(x=0, color='black', linestyle='-', linewidth=0.5)
ax1a.grid(True, alpha=0.3, axis='x')

# Model 2
colors2 = ['red' if p < 0.05 else 'gray' for p in univariate_results2['p値']]
ax1b.barh(x_pos, univariate_results2['係数'], color=colors2, alpha=0.7)
ax1b.set_yticks(x_pos)
ax1b.set_yticklabels(univariate_results2['変数'])
ax1b.set_xlabel('係数', fontsize=12)
ax1b.set_title('Model 2: 単回帰係数（赤=p<0.05）', fontsize=14, fontweight='bold')
ax1b.axvline(x=0, color='black', linestyle='-', linewidth=0.5)
ax1b.grid(True, alpha=0.3, axis='x')

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "univariate_coefficients.png", dpi=300, bbox_inches='tight')
print(f"  [OK] 単回帰係数プロット保存")
plt.close()

# 6-2. 前進選択法の履歴（AICの変化）
fig2, (ax2a, ax2b) = plt.subplots(1, 2, figsize=(14, 6))

# Model 1
ax2a.plot(history1_aic['Step'], history1_aic['AIC'], 'o-', linewidth=2, markersize=8)
ax2a.set_xlabel('ステップ', fontsize=12)
ax2a.set_ylabel('AIC', fontsize=12)
ax2a.set_title('Model 1: 前進選択法（AIC）', fontsize=14, fontweight='bold')
ax2a.grid(True, alpha=0.3)
# 変数名を注釈
for i, row in history1_aic.iterrows():
    ax2a.annotate(row['追加変数'],
                 xy=(row['Step'], row['AIC']),
                 xytext=(5, 5),
                 textcoords='offset points',
                 fontsize=9)

# Model 2
ax2b.plot(history2_aic['Step'], history2_aic['AIC'], 'o-', linewidth=2, markersize=8)
ax2b.set_xlabel('ステップ', fontsize=12)
ax2b.set_ylabel('AIC', fontsize=12)
ax2b.set_title('Model 2: 前進選択法（AIC）', fontsize=14, fontweight='bold')
ax2b.grid(True, alpha=0.3)
# 変数名を注釈
for i, row in history2_aic.iterrows():
    ax2b.annotate(row['追加変数'],
                 xy=(row['Step'], row['AIC']),
                 xytext=(5, 5),
                 textcoords='offset points',
                 fontsize=9)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "forward_selection_aic.png", dpi=300, bbox_inches='tight')
print(f"  [OK] 前進選択法AIC曲線保存")
plt.close()

# ===============================
# Phase 7: 結果保存
# ===============================
print("\n[Phase 7] 結果保存...")

with open(OUTPUT_DIR / "stepwise_univariate_results.txt", 'w', encoding='utf-8') as f:
    f.write("=" * 80 + "\n")
    f.write("ステップワイズ回帰と単回帰分析結果\n")
    f.write("=" * 80 + "\n\n")

    f.write("【1. 単回帰分析】\n")
    f.write("-" * 80 + "\n")
    f.write("Model 1 (救急医療管理加算):\n")
    f.write(univariate_results1.to_string(index=False) + "\n\n")
    f.write("Model 2 (点滴注射):\n")
    f.write(univariate_results2.to_string(index=False) + "\n\n")

    f.write("【2. 前進選択法（AIC基準）】\n")
    f.write("-" * 80 + "\n")
    f.write("Model 1 (救急医療管理加算):\n")
    f.write(history1_aic.to_string(index=False) + "\n")
    f.write(f"最終選択変数: {', '.join(selected_features1_aic)}\n\n")
    f.write("Model 2 (点滴注射):\n")
    f.write(history2_aic.to_string(index=False) + "\n")
    f.write(f"最終選択変数: {', '.join(selected_features2_aic)}\n\n")

    f.write("【3. 後退選択法（p値基準, α=0.05）】\n")
    f.write("-" * 80 + "\n")
    f.write("Model 1 (救急医療管理加算):\n")
    f.write(history1_back.to_string(index=False) + "\n")
    f.write(f"最終選択変数: {', '.join(selected_features1_back) if selected_features1_back else '（なし）'}\n\n")
    f.write("Model 2 (点滴注射):\n")
    f.write(history2_back.to_string(index=False) + "\n")
    f.write(f"最終選択変数: {', '.join(selected_features2_back) if selected_features2_back else '（なし）'}\n\n")

    if model1_forward:
        f.write("【4. 最終モデル（前進選択法）】\n")
        f.write("-" * 80 + "\n")
        f.write("Model 1 (救急医療管理加算):\n")
        f.write(str(model1_forward.summary()) + "\n\n")

    if model2_forward:
        f.write("Model 2 (点滴注射):\n")
        f.write(str(model2_forward.summary()) + "\n\n")

print(f"  [OK] 結果ファイル保存: {OUTPUT_DIR / 'stepwise_univariate_results.txt'}")

# CSVで保存
univariate_results1.to_csv(OUTPUT_DIR / "univariate_model1.csv", index=False, encoding='utf-8-sig')
univariate_results2.to_csv(OUTPUT_DIR / "univariate_model2.csv", index=False, encoding='utf-8-sig')
history1_aic.to_csv(OUTPUT_DIR / "forward_selection_model1.csv", index=False, encoding='utf-8-sig')
history2_aic.to_csv(OUTPUT_DIR / "forward_selection_model2.csv", index=False, encoding='utf-8-sig')
print(f"  [OK] CSV保存完了")

# ===============================
# 完了
# ===============================
print("\n" + "=" * 80)
print("ステップワイズ回帰と単回帰分析が完了しました！")
print("=" * 80)
print(f"\n出力ディレクトリ: {OUTPUT_DIR}")
print(f"\n主要な結果:")
print(f"  - 単回帰で有意な変数（Model 1）:")
for _, row in univariate_results1[univariate_results1['p値'] < 0.05].iterrows():
    print(f"      {row['変数']}: β={row['係数']:.2f}, p={row['p値']:.4f}")
print(f"  - 単回帰で有意な変数（Model 2）:")
for _, row in univariate_results2[univariate_results2['p値'] < 0.05].iterrows():
    print(f"      {row['変数']}: β={row['係数']:.2f}, p={row['p値']:.4f}")
print(f"\n  - 前進選択法で選択された変数:")
print(f"      Model 1: {', '.join(selected_features1_aic)}")
print(f"      Model 2: {', '.join(selected_features2_aic)}")
