"""
Ridge回帰分析（多重共線性に対処）

目的:
- OLS回帰で検出された強い多重共線性（VIF > 10）に対処
- L2正則化により係数の推定を安定化
- クロスバリデーションで最適な正則化パラメータ（alpha）を選択

Data Source:
- population_adjusted_dataset.csv（人口調整済み）
"""

import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from sklearn.linear_model import Ridge, RidgeCV
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score
from sklearn.metrics import r2_score, mean_squared_error
import statsmodels.api as sm

# パス設定
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "02_Data" / "interim"
RESULTS_DIR = PROJECT_ROOT / "03_Analysis" / "results"
OUTPUT_DIR = RESULTS_DIR / "ridge_regression"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 80)
print("Ridge回帰分析（多重共線性対処）")
print("=" * 80)

# ===============================
# Phase 1: データ読み込み
# ===============================
print("\n[Phase 1] データ読み込み...")

df = pd.read_csv(RESULTS_DIR / "population_adjusted_dataset.csv", encoding='utf-8-sig')
print(f"  データ件数: {len(df)} 都道府県")
print(f"  変数数: {len(df.columns)}")

# ===============================
# Phase 2: データ準備
# ===============================
print("\n[Phase 2] データ準備...")

# 特徴量と目的変数を定義
feature_names = ['猛暑日数', 'WBGT平均', '高齢者単独世帯率', 'エアコン普及率']
target_names = ['救急医療管理加算_per100k', '点滴注射_per100k']

X = df[feature_names].values
y1 = df['救急医療管理加算_per100k'].values  # Model 1
y2 = df['点滴注射_per100k'].values          # Model 2

print(f"  特徴量: {feature_names}")
print(f"  目的変数1: 救急医療管理加算（10万人あたり）")
print(f"  目的変数2: 点滴注射（10万人あたり）")

# 標準化（Ridge回帰では必須）
scaler_X = StandardScaler()
X_scaled = scaler_X.fit_transform(X)

scaler_y1 = StandardScaler()
y1_scaled = scaler_y1.fit_transform(y1.reshape(-1, 1)).ravel()

scaler_y2 = StandardScaler()
y2_scaled = scaler_y2.fit_transform(y2.reshape(-1, 1)).ravel()

print(f"\n  [OK] 標準化完了")
print(f"    X_scaled: mean={X_scaled.mean():.2f}, std={X_scaled.std():.2f}")
print(f"    y1_scaled: mean={y1_scaled.mean():.2f}, std={y1_scaled.std():.2f}")
print(f"    y2_scaled: mean={y2_scaled.mean():.2f}, std={y2_scaled.std():.2f}")

# ===============================
# Phase 3: 最適alphaの選択（クロスバリデーション）
# ===============================
print("\n[Phase 3] 最適alpha選択（5-fold CV）...")

# alphaの候補（対数スケール）
# より小さい範囲で探索（多重共線性対処には小さめのalphaが適切）
alphas = np.logspace(-2, 2, 100)  # 0.01 から 100 まで

# Model 1: 救急医療管理加算
ridge_cv1 = RidgeCV(alphas=alphas, cv=5, scoring='r2')
ridge_cv1.fit(X_scaled, y1_scaled)
best_alpha1 = ridge_cv1.alpha_
print(f"\n  Model 1 (救急医療管理加算):")
print(f"    最適alpha: {best_alpha1:.4f}")
print(f"    CV R^2: {ridge_cv1.best_score_:.4f}")

# Model 2: 点滴注射
ridge_cv2 = RidgeCV(alphas=alphas, cv=5, scoring='r2')
ridge_cv2.fit(X_scaled, y2_scaled)
best_alpha2 = ridge_cv2.alpha_
print(f"\n  Model 2 (点滴注射):")
print(f"    最適alpha: {best_alpha2:.4f}")
print(f"    CV R^2: {ridge_cv2.best_score_:.4f}")

# ===============================
# Phase 4: Ridge回帰の実行
# ===============================
print("\n[Phase 4] Ridge回帰実行...")

# Model 1: 最適alphaでRidge回帰
ridge1 = Ridge(alpha=best_alpha1)
ridge1.fit(X_scaled, y1_scaled)
y1_pred_scaled = ridge1.predict(X_scaled)
y1_pred = scaler_y1.inverse_transform(y1_pred_scaled.reshape(-1, 1)).ravel()

r2_ridge1 = r2_score(y1, y1_pred)
rmse_ridge1 = np.sqrt(mean_squared_error(y1, y1_pred))

print(f"\n  Model 1 (Ridge):")
print(f"    R^2: {r2_ridge1:.4f}")
print(f"    RMSE: {rmse_ridge1:.2f}")

# Model 2: 最適alphaでRidge回帰
ridge2 = Ridge(alpha=best_alpha2)
ridge2.fit(X_scaled, y2_scaled)
y2_pred_scaled = ridge2.predict(X_scaled)
y2_pred = scaler_y2.inverse_transform(y2_pred_scaled.reshape(-1, 1)).ravel()

r2_ridge2 = r2_score(y2, y2_pred)
rmse_ridge2 = np.sqrt(mean_squared_error(y2, y2_pred))

print(f"\n  Model 2 (Ridge):")
print(f"    R^2: {r2_ridge2:.4f}")
print(f"    RMSE: {rmse_ridge2:.2f}")

# ===============================
# Phase 5: OLS回帰との比較
# ===============================
print("\n[Phase 5] OLS回帰との比較...")

# OLS Model 1
X_const = sm.add_constant(X)
ols1 = sm.OLS(y1, X_const).fit()
r2_ols1 = ols1.rsquared

# OLS Model 2
ols2 = sm.OLS(y2, X_const).fit()
r2_ols2 = ols2.rsquared

print(f"\n  Model 1 比較:")
print(f"    OLS R^2: {r2_ols1:.4f}")
print(f"    Ridge R^2: {r2_ridge1:.4f}")
print(f"    差分: {r2_ridge1 - r2_ols1:+.4f}")

print(f"\n  Model 2 比較:")
print(f"    OLS R^2: {r2_ols2:.4f}")
print(f"    Ridge R^2: {r2_ridge2:.4f}")
print(f"    差分: {r2_ridge2 - r2_ols2:+.4f}")

# ===============================
# Phase 6: 係数の比較
# ===============================
print("\n[Phase 6] 係数の比較...")

# Ridge係数を元のスケールに戻す
ridge1_coefs_scaled = ridge1.coef_
ridge1_coefs = ridge1_coefs_scaled * scaler_y1.scale_ / scaler_X.scale_

ridge2_coefs_scaled = ridge2.coef_
ridge2_coefs = ridge2_coefs_scaled * scaler_y2.scale_ / scaler_X.scale_

# OLS係数（既にnumpy.ndarray）
ols1_coefs = ols1.params[1:]  # 定数項を除く
ols2_coefs = ols2.params[1:]

# 結果をDataFrameにまとめる
coef_comparison1 = pd.DataFrame({
    '変数': feature_names,
    'OLS係数': ols1_coefs,
    'Ridge係数': ridge1_coefs,
    '差分': ridge1_coefs - ols1_coefs,
    '縮小率(%)': ((ols1_coefs - ridge1_coefs) / ols1_coefs * 100)
})

coef_comparison2 = pd.DataFrame({
    '変数': feature_names,
    'OLS係数': ols2_coefs,
    'Ridge係数': ridge2_coefs,
    '差分': ridge2_coefs - ols2_coefs,
    '縮小率(%)': ((ols2_coefs - ridge2_coefs) / ols2_coefs * 100)
})

print("\n  Model 1 (救急医療管理加算):")
print(coef_comparison1.to_string(index=False))

print("\n  Model 2 (点滴注射):")
print(coef_comparison2.to_string(index=False))

# ===============================
# Phase 7: 可視化
# ===============================
print("\n[Phase 7] 可視化...")

# 日本語フォント設定
plt.rcParams['font.sans-serif'] = ['MS Gothic', 'Yu Gothic', 'Meiryo']
plt.rcParams['axes.unicode_minus'] = False

# 7-1. 係数の比較（Model 1）
fig1, ax1 = plt.subplots(figsize=(12, 6))
x_pos = np.arange(len(feature_names))
width = 0.35

ax1.bar(x_pos - width/2, ols1_coefs, width, label='OLS', alpha=0.8, color='steelblue')
ax1.bar(x_pos + width/2, ridge1_coefs, width, label='Ridge', alpha=0.8, color='coral')

ax1.set_xlabel('変数', fontsize=12)
ax1.set_ylabel('係数', fontsize=12)
ax1.set_title(f'Model 1: 係数の比較（救急医療管理加算）\nRidge alpha={best_alpha1:.4f}', fontsize=14, fontweight='bold')
ax1.set_xticks(x_pos)
ax1.set_xticklabels(feature_names, rotation=45, ha='right')
ax1.legend()
ax1.grid(True, alpha=0.3, axis='y')
ax1.axhline(y=0, color='black', linestyle='-', linewidth=0.5)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "ridge_coefficients_model1.png", dpi=300, bbox_inches='tight')
print(f"  [OK] 係数比較図（Model 1）保存")
plt.close()

# 7-2. 係数の比較（Model 2）
fig2, ax2 = plt.subplots(figsize=(12, 6))

ax2.bar(x_pos - width/2, ols2_coefs, width, label='OLS', alpha=0.8, color='steelblue')
ax2.bar(x_pos + width/2, ridge2_coefs, width, label='Ridge', alpha=0.8, color='coral')

ax2.set_xlabel('変数', fontsize=12)
ax2.set_ylabel('係数', fontsize=12)
ax2.set_title(f'Model 2: 係数の比較（点滴注射）\nRidge alpha={best_alpha2:.4f}', fontsize=14, fontweight='bold')
ax2.set_xticks(x_pos)
ax2.set_xticklabels(feature_names, rotation=45, ha='right')
ax2.legend()
ax2.grid(True, alpha=0.3, axis='y')
ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "ridge_coefficients_model2.png", dpi=300, bbox_inches='tight')
print(f"  [OK] 係数比較図（Model 2）保存")
plt.close()

# 7-3. alphaの選択過程（CV曲線）
fig3, (ax3a, ax3b) = plt.subplots(1, 2, figsize=(14, 5))

# Model 1のCV曲線
cv_scores1 = []
for alpha in alphas:
    scores = cross_val_score(Ridge(alpha=alpha), X_scaled, y1_scaled, cv=5, scoring='r2')
    cv_scores1.append(scores.mean())

ax3a.semilogx(alphas, cv_scores1, 'b-', linewidth=2)
ax3a.axvline(best_alpha1, color='r', linestyle='--', linewidth=2, label=f'最適alpha={best_alpha1:.4f}')
ax3a.set_xlabel('正則化パラメータ（alpha）', fontsize=12)
ax3a.set_ylabel('CV R^2', fontsize=12)
ax3a.set_title('Model 1: 正則化パラメータの選択', fontsize=14, fontweight='bold')
ax3a.legend()
ax3a.grid(True, alpha=0.3)

# Model 2のCV曲線
cv_scores2 = []
for alpha in alphas:
    scores = cross_val_score(Ridge(alpha=alpha), X_scaled, y2_scaled, cv=5, scoring='r2')
    cv_scores2.append(scores.mean())

ax3b.semilogx(alphas, cv_scores2, 'b-', linewidth=2)
ax3b.axvline(best_alpha2, color='r', linestyle='--', linewidth=2, label=f'最適alpha={best_alpha2:.4f}')
ax3b.set_xlabel('正則化パラメータ（alpha）', fontsize=12)
ax3b.set_ylabel('CV R^2', fontsize=12)
ax3b.set_title('Model 2: 正則化パラメータの選択', fontsize=14, fontweight='bold')
ax3b.legend()
ax3b.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "ridge_alpha_selection.png", dpi=300, bbox_inches='tight')
print(f"  [OK] alpha選択曲線保存")
plt.close()

# 7-4. 予測値 vs 実測値
fig4, (ax4a, ax4b) = plt.subplots(1, 2, figsize=(14, 6))

# Model 1
ax4a.scatter(y1, y1_pred, alpha=0.6, s=100)
ax4a.plot([y1.min(), y1.max()], [y1.min(), y1.max()], 'r--', lw=2)
ax4a.set_xlabel('実測値（10万人あたり）', fontsize=12)
ax4a.set_ylabel('Ridge予測値（10万人あたり）', fontsize=12)
ax4a.set_title(f'Model 1: 予測精度\nR^2={r2_ridge1:.4f}, RMSE={rmse_ridge1:.2f}', fontsize=14, fontweight='bold')
ax4a.grid(True, alpha=0.3)

# Model 2
ax4b.scatter(y2, y2_pred, alpha=0.6, s=100)
ax4b.plot([y2.min(), y2.max()], [y2.min(), y2.max()], 'r--', lw=2)
ax4b.set_xlabel('実測値（10万人あたり）', fontsize=12)
ax4b.set_ylabel('Ridge予測値（10万人あたり）', fontsize=12)
ax4b.set_title(f'Model 2: 予測精度\nR^2={r2_ridge2:.4f}, RMSE={rmse_ridge2:.2f}', fontsize=14, fontweight='bold')
ax4b.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "ridge_predictions.png", dpi=300, bbox_inches='tight')
print(f"  [OK] 予測精度図保存")
plt.close()

# ===============================
# Phase 8: 結果保存
# ===============================
print("\n[Phase 8] 結果保存...")

# 結果テキストファイル
with open(OUTPUT_DIR / "ridge_regression_results.txt", 'w', encoding='utf-8') as f:
    f.write("=" * 80 + "\n")
    f.write("Ridge回帰分析結果（多重共線性対処）\n")
    f.write("=" * 80 + "\n\n")

    f.write("【データ】\n")
    f.write(f"  サンプルサイズ: {len(df)} 都道府県\n")
    f.write(f"  特徴量: {', '.join(feature_names)}\n\n")

    f.write("【Model 1: 救急医療管理加算（10万人あたり）】\n")
    f.write("-" * 80 + "\n")
    f.write(f"  最適alpha: {best_alpha1:.4f}\n")
    f.write(f"  R^2 (Ridge): {r2_ridge1:.4f}\n")
    f.write(f"  R^2 (OLS): {r2_ols1:.4f}\n")
    f.write(f"  RMSE: {rmse_ridge1:.2f}\n\n")
    f.write("  係数の比較:\n")
    f.write(coef_comparison1.to_string(index=False) + "\n\n")

    f.write("【Model 2: 点滴注射（10万人あたり）】\n")
    f.write("-" * 80 + "\n")
    f.write(f"  最適alpha: {best_alpha2:.4f}\n")
    f.write(f"  R^2 (Ridge): {r2_ridge2:.4f}\n")
    f.write(f"  R^2 (OLS): {r2_ols2:.4f}\n")
    f.write(f"  RMSE: {rmse_ridge2:.2f}\n\n")
    f.write("  係数の比較:\n")
    f.write(coef_comparison2.to_string(index=False) + "\n\n")

    f.write("【解釈】\n")
    f.write("-" * 80 + "\n")
    f.write("1. Ridge回帰により、多重共線性による係数の不安定性を軽減\n")
    f.write("2. L2正則化により、大きな係数が縮小され、過学習を防止\n")
    f.write("3. クロスバリデーションにより最適な正則化強度を選択\n")
    f.write("4. R^2はOLSとほぼ同等（説明力を維持しながら安定化）\n")

print(f"  [OK] 結果ファイル保存: {OUTPUT_DIR / 'ridge_regression_results.txt'}")

# 係数比較をCSVで保存
coef_comparison1.to_csv(OUTPUT_DIR / "ridge_coefficients_model1.csv", index=False, encoding='utf-8-sig')
coef_comparison2.to_csv(OUTPUT_DIR / "ridge_coefficients_model2.csv", index=False, encoding='utf-8-sig')
print(f"  [OK] 係数比較（CSV）保存")

# 予測値をCSVで保存
predictions = pd.DataFrame({
    '都道府県': df['都道府県'],
    '救急医療管理加算_実測値': y1,
    '救急医療管理加算_Ridge予測値': y1_pred,
    '点滴注射_実測値': y2,
    '点滴注射_Ridge予測値': y2_pred
})
predictions.to_csv(OUTPUT_DIR / "ridge_predictions.csv", index=False, encoding='utf-8-sig')
print(f"  [OK] 予測値（CSV）保存")

# ===============================
# 完了
# ===============================
print("\n" + "=" * 80)
print("Ridge回帰分析が完了しました！")
print("=" * 80)
print(f"\n出力ディレクトリ: {OUTPUT_DIR}")
print(f"\n主要な結果:")
print(f"  - Model 1 (救急医療管理加算):")
print(f"      最適alpha: {best_alpha1:.4f}")
print(f"      R^2 (Ridge): {r2_ridge1:.4f}")
print(f"      R^2 (OLS): {r2_ols1:.4f}")
print(f"  - Model 2 (点滴注射):")
print(f"      最適alpha: {best_alpha2:.4f}")
print(f"      R^2 (Ridge): {r2_ridge2:.4f}")
print(f"      R^2 (OLS): {r2_ols2:.4f}")
