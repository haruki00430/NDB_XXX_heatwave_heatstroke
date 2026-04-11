> **正本リポジトリ（GitHub Private）：** https://github.com/haruki00430/NDB_XXX_heatwave_heatstroke

# 高齢者単独世帯率と熱中症関連医療利用の生態学的関連
(NDB_XXX_heatwave_heatstroke)

## ステータス（2026-04-05 リポジトリ照合）

- **原稿**: `04_Manuscripts/Manuscript_heatwave_social_isolation.qmd`（`Manuscript_heatwave_social_isolation_cleaned.qmd` 等の別版あり）
- **備考**: 正本を変える場合は本節を更新。`analysis/`・`results/` の実体を優先。

## プロジェクトの目的

都道府県単位（N=47）の生態学研究により、**高齢者単独世帯率**（社会的孤立の地域指標）が**熱中症関連の輸液療法実施率**（NDBの手技コードG004：500mL以上輸液）と関連するかを検証する。気象要因（熱波日数・WBGT）を共変量として調整し、社会的脆弱性が熱被害の地域差に与える影響を定量化する。感度分析（外れ値除外・東京除外・高齢化率層別）で結果の頑健性を評価する。

## データソース

- **内部データ:** NDBオープンデータ第10回（2020年度診療分）
  - 医科診療行為の算定回数（G004：500mL以上輸液、熱中症等の脱水時の輸液の代理指標）
- **外部データ:**
  - 令和2年国勢調査（高齢者単独世帯率、高齢化率）
  - 気象庁データ（夏季の猛暑日数・WBGT）
  - 家計調査（エアコン普及率）

## 構造

- `03_Analysis/analysis/`: データ統合、単変量回帰、感度分析用スクリプト
- `03_Analysis/results/`: 感度分析サマリ、ステップワイズ結果、参考文献検証ログ等
- `04_Manuscripts/`: 論文原稿（Manuscript_heatwave_social_isolation.qmd）、references.bib、vancouver.csl、引用・参考文献検証用スクリプト・レポート

## 注意事項

- NDB生データは読取専用。実データを外部AIに送信しないこと（CLAUDE.md準拠）。
- アウトカムは熱中症特異的ではなく輸液療法学算定の代理指標であることを解釈に反映すること。
