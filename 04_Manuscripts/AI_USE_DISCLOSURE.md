# 生成AI・エージェント利用開示（論文別）

> 本ファイルは [00_Docs/templates/AI_USE_DISCLOSURE.template.md](../../../00_Docs/templates/AI_USE_DISCLOSURE.template.md) に基づく。運用は [CIRCS_NDB_MANUSCRIPT_AI_RULEBOOK.md](../../../00_Docs/07_Setup/CIRCS_NDB_MANUSCRIPT_AI_RULEBOOK.md) を参照。

---

## メタデータ

| 項目 | 内容 |
|------|------|
| 論文仮題 | 高齢者単独世帯率と熱中症関連医療利用（輸液療法）の生態学的関連 |
| 論文仮題（英語） | Ecological association of older adult living-alone rate and heat-related fluid therapy utilization |
| プロジェクトパス | `projects/NDB_XXX_heatwave_heatstroke/` |
| 対象誌（候補） | （追記） |
| 最終更新日 | 2026-04-08 |
| 記録責任者 | 通信著者（`Manuscript_heatwave_social_isolation.qmd` の YAML `author` と同一。投稿前に実名へ） |

**原稿の正本**: `04_Manuscripts/Manuscript_heatwave_social_isolation.qmd`（`Manuscript_heatwave_social_isolation_cleaned.qmd` 等と併存する場合は投稿用1本に決め [README.md](../README.md) を更新）

---

## 使用ツール一覧

| ツール・サービス | 区分 | モデル・バージョン（分かる範囲） | 主な用途 |
|------------------|------|----------------------------------|----------|
| Cursor | クラウドエージェント（設定依存） | 利用時点のエージェントモデル | `03_Analysis`・感度分析・Quarto の支援 |
| LM Studio 等 | ローカル | — | 使用時は追記 |

**注**: AIを著者にしない。

---

## 研究段階別の利用

### 1. データ整備・ETL・スクリプト生成

| 日付 | ツール | 実施内容（1行） | 備考 |
|------|--------|-----------------|------|
| （追記） | Cursor 等 | 国勢調査・気象・NDB G004 等の統合 | `03_Analysis/analysis/` |

### 2. 探索的スクリーニング／ローカルLLM

| 日付 | ツール | 実施内容（1行） | 備考 |
|------|--------|-----------------|------|
| — | — | **該当なし**（用いた場合は追記） |  |

### 3. 確証的分析・感度分析

| 日付 | ツール | 実施内容（1行） | 備考 |
|------|--------|-----------------|------|
| （追記） | Cursor 等 | 単変量回帰・感度（外れ値・東京除外等） | `03_Analysis/results/` |

### 4. 原稿

| 日付 | ツール | 実施内容（1行） | 備考 |
|------|--------|-----------------|------|
| （追記） | Cursor 等 | Quarto 推敲 |  |

### 5. 参考文献

| 日付 | ツール | 実施内容（1行） | 備考 |
|------|--------|-----------------|------|
| （追記） | Cursor 等 | 引用・検証ログがあればファイル名を記載 | `03_Analysis/results/` に検証ログの記載あり得る |

---

## データ境界

### 外部クラウドLLMに**送らなかった**もの

- [x] NDB 生データの実数値・スクリーンショット
- [x] 個票・再識別可能な細集計の丸貼り

### 送ったもの（機微度が低い範囲）

| 種別 | 例 |
|------|-----|
| メタデータ・コード | 列名、スクリプト、パス |

### ローカルLLMに入力したもの

| 種別 | 例 |
|------|-----|
| （追記） |  |

---

## 人間による検証

| 段階 | 確認内容 | 実施者 | 日付 |
|------|----------|--------|------|
| コード・数値・引用・解釈 | 熱中症代理指標・気象交絡の解釈 | 著者 | （追記） |

---

## 投稿用短文ドラフト

### 日本語（案）

本研究の原稿作成および解析に生成AI支援ツールを用いた。手法・解釈・結論は著者が検証した。AIは著者としていない。

### English (draft)

The authors used AI-assisted tools, verified outputs, and accept full responsibility. AI was not listed as an author.

---

## 変更履歴

| 日付 | 変更内容 |
|------|----------|
| 2026-04-08 | 初版（プロジェクト一括整備） |
