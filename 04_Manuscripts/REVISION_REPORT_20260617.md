# 実施報告書
## Are Heat-Health Systems Socially Blind? — 大平先生コメント対応作業記録
**作成日**: 2026-06-17  
**対象ファイル**: `Manuscript_heatwave_social_isolation_final.qmd` / `.docx`

---

## 1. 作業の全体概要

大平先生（Tetsuya Ohira）から受領したコメントファイル（`Are_Heat_Health_Systems_Socially_Blind_20260616TO.docx`）および対応案（`01Are_Heat_Health_Systems_Socially_Blind_20260617_body_comment_response_JP.docx`）を参照し、以下の解析・論文修正を実施した。

---

## 2. 受領コメント一覧

| コメント | 内容要旨 |
|---------|---------|
| #1（投稿先） | 日本の学会英文誌・日本医師会誌への投稿を推奨 |
| #13（アウトカム特異性） | G004点滴は熱中症非特異的。病名使用可否・月別データ・文献追加を要求 |
| #16（熱曝露指標） | 急激な気温変化等の指標が不十分。熱中症関連との弱い関連提示を求める |
| #21（単変量解析の弱さ） | 受療率との比較による点滴療法の特異性確認を提案 |
| #38（強い表現） | Conclusions等の断定表現を避けるよう指示 |

---

## 3. 追加解析の実施

### 解析A：FDMA熱中症搬送データによる構成概念妥当性検証

**目的**: コメント#13・#16への対応。G004点滴療法が熱関連脱水の人口レベル指標として妥当であることを示す。

**データソース**:
- 消防庁（FDMA）令和5年（2023年）熱中症救急搬送データ
- ダウンロード先: `https://www.fdma.go.jp/disaster/heatstroke/items/heatstroke003_data_r5.xlsx`
- 保存先: `02_Data/raw/fdma_heatstroke_r5_2023.xlsx`
- シート: `2023_06`〜`2023_09`（夏季4ヶ月分）

**スクリプト**: `03_Analysis/analysis/08_fdma_heatstroke_validation.py`

**結果**:
- Model 1（FDMA搬送率 → 点滴療法率）: β = 70.19, 95% CI (36.85, 103.53), **r = 0.534, p < 0.001**, R² = 0.286
- Model 2（高齢者単独世帯率 → FDMA搬送率）: β = 1.70, p = 0.272, R² = 0.027（非有意）
- 夏季搬送合計: 87,812件

**出力ファイル**:
- `03_Analysis/results/fdma_validation/fdma_validation_dataset.csv`
- `03_Analysis/results/fdma_validation/fdma_regression_results.txt`
- `03_Analysis/results/fdma_validation/figS1_fdma_vs_infusion.png` ← 補足図S1
- `03_Analysis/results/fdma_validation/figS2_elderly_vs_fdma.png`

---

### 解析B：追加気候変数（4指標）の検討

**目的**: コメント#16への対応。急激な気温変化を含む4気候指標と点滴療法の関連を検証。

**データソース**: 既存JMA日別気象データ（`02_Data/raw/jma_weather/jma_daily_temperature_2023_summer.csv`）

**スクリプト**: `03_Analysis/analysis/07_additional_climate_variables.py`

**変数と結果**:

| 変数 | β | 95% CI | p | R² |
|------|---|--------|---|---|
| 平均日最高気温（per 1°C） | −145.83 | (−861.66, 570.00) | 0.684 | 0.004 |
| 日最高気温SD（per 1°C） | −586.99 | (−2,060.21, 886.23) | 0.427 | 0.014 |
| 平均日較差（per 1°C） | −307.32 | (−961.69, 347.06) | 0.349 | 0.019 |
| 急変日数≥5°C（per 1日） | −42.32 | (−190.74, 106.10) | 0.569 | 0.007 |

**結論**: 全4変数が非有意（p > 0.34）。主要結果の気候以外への特異性を支持。

**出力ファイル**:
- `03_Analysis/results/additional_climate/additional_climate_by_prefecture.csv`
- `03_Analysis/results/additional_climate/additional_climate_regression_results.csv`
- `03_Analysis/results/additional_climate/table2_addendum.txt`
- `03_Analysis/results/additional_climate/additional_climate_scatter.png`

---

## 4. 論文QMDへの修正内容

バックアップ: `Manuscript_heatwave_social_isolation_final.qmd.backup`（作業前に作成済み）

### 修正箇所一覧

| # | 箇所 | 変更内容 |
|---|------|---------|
| M1 | Methods 2 末尾 | FDMAデータとのconstruct validity check文を追加（参照番号 `.1)` 付き） |
| M2 | Methods 4 末尾 | 4追加気候変数（定義・算出方法）の記述を3文追加 |
| M3 | Results 2 末尾 | 4気候変数すべてp>0.34で非有意の一文追加 |
| M4 | Results 5 末尾 | 「This pattern suggests potential heterogeneity...」→「The estimated coefficient differed between strata (lower stratum β = 1,254.30 vs. higher stratum β = 264.50).」へ変更（解釈語削除・事実記述化） |
| M5 | Results 6（新設） | 「6. Construct Validity: FDMA Heatstroke Transport Validation」セクション追加（β=70.19, r=0.534, p<0.001） |
| M6 | Table 2 | 4追加気候変数の回帰結果行を追加（β, 95% CI, p, R², Adj.R²）。脚注にJMAデータ出典を追記 |
| M7 | Limitations 第4-5パラ末尾 | 受療率を負の対照として検討していない旨の限界文を追加。FDMA cross-validation（r=0.53, p<0.001）の記述を追加 |
| M8 | Conclusions 第1段落 | 「was robustly associated」→「was associated... in univariate analyses. The association was consistent」へ変更（#38対応） |
| M9 | Conclusions 第3段落 | 「Heat action plans should integrate...」で始まる政策提言段落を全文削除（#38対応） |
| M10 | Conclusions 最終段落 | 「should confirm」→「are needed to confirm」へ語調修正 |
| M11 | 末尾 | Supplementary Figure S1のレジェンドと画像を追加 |

### QMD修正後にレンダリング済み
- `Manuscript_heatwave_social_isolation_final.docx`（1.2MB、2026-06-17 10:47生成）

---

## 5. 対応案ファイル（RP）とMS版の差異

両ファイルを抽出・比較した結果、以下の差異が確認された。

### A. MSのみに存在（今回の作業で追加）
- A1: Methods 2 — FDMA construct validity check文
- A2: Methods 4 — 4追加気候変数の定義
- A3: Results 2 — 4変数非有意の記述
- A4: Results 6 — FDMA検証セクション（新設）
- A5: Limitations — 負の対照なし文 + FDMA cross-validation文
- A6: Table 2 脚注 — JMAデータ出典
- A7: Supplementary Figure S1

### B. RPにあってMSにない（未反映・要確認）
- **B1**: Limitations 第7パラ末尾の解釈限定文 — 「The present findings should be interpreted as evidence for surveillance prioritization rather than causal evidence of heat-related illness.」
- B2: Conclusions 第3段落（「Heat action plans should integrate...」） — 今回の作業で削除（#38対応）
- B3: Acknowledgments・Conflicts of Interest・Data Availability・Author Contributions・Funding・AI Disclosure の各セクション

### C. 文章が変更された箇所
- C1: Results 5 末尾（→ 事実記述のみ）
- C2: Conclusions 第1段落（「robustly」削除・書き出し修正）
- C3: Conclusions 最終段落（語調修正）

---

## 6. 投稿先候補の再評価

大平先生コメント#1（日本の学会英文誌推奨）を踏まえ、以下の通り確認した。

| 優先順位 | 誌名 | 発行学会 | 評価 |
|---------|------|---------|------|
| 第一候補（挑戦） | Journal of Epidemiology | 日本疫学会 | NDB生態学研究の掲載実績豊富 |
| 第二候補（妥当） | Environmental Health and Preventive Medicine | 日本産業衛生学会 | 環境×社会脆弱性のフレーミングと最適合 |
| 第三候補（抑え） | Journal of Rural Medicine | 日本農村医学会 | 地域格差の側面は合う。主題適合度は最低 |

---

## 7. 患者調査R5データの入手可能性確認

コメント#21（受療率との比較）への対応として、令和5年患者調査の都道府県別外来受療率データの入手可能性を確認した。

- **令和5年患者調査**: 令和6年12月20日公表済み（e-Stat・厚労省HP）
- **都道府県編 第36表** — 受療率（人口10万対）× 性・年齢階級 × 都道府県別（CSV形式）
- **ダウンロードURL**: `https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040234480&fileKind=1`
- **保存先**: `02_Data/raw/patient_survey_r5_t36_pref_age.csv`（ダウンロード済み）
- **エンコーディング**: Shift-JIS（cp932）
- **行数**: 2,070行（47都道府県 × 約44行の繰り返し構造）
- **外来受療率（総数）の位置**: 各都道府県名行の次にある「総数,総数,…」行の6列目

→ **未実施**: 解析スクリプト作成・回帰・論文反映（次項チェックリスト参照）

---

## 8. 未対応事項

| 項目 | 理由 |
|------|------|
| G004文献追加 | コメント#13「この文章に対する文献が必要」への対応未実施。Bouchama & Knochel (2002, Ref.11)を引用する案あり |
| 患者調査R5 negative control解析 | データ取得済みだが、解析スクリプト・論文反映が未実施 |
| Limitations B1文の追加確認 | RP版の解釈限定文がMS版に存在しないことを確認済み。追加要否をユーザーが判断中 |
| 最終DOCX再レンダリング | 上記対応後に実施が必要 |

---

*本報告書は 2026-06-17 の作業セッションの記録として作成。*
