# NDB_XXX_heatwave_heatstroke 実装計画書

**プロジェクト名**: 猛暑日数と熱中症医療の都道府県別関連分析

**作成日**: 2026-02-28

**研究テーマ**: 猛暑日数（最高気温35℃以上日数）と熱中症関連診療行為の都道府県別関連を分析し、高齢者脆弱性（高齢者単独世帯率）の効果修飾を検討する

---

## 📋 研究概要

### 研究デザイン
- **研究タイプ**: 都道府県単位の横断的研究（Ecological study）
- **対象期間**: 2023年夏季（6-9月）
- **対象**: 日本47都道府県
- **主要曝露**: 猛暑日数（最高気温35℃以上の日数）
- **主要アウトカム**: 熱中症関連診療行為算定回数/10万人

### 仮説
1. **主仮説**: 猛暑日数が多い都道府県では、年齢・社会経済要因調整後も熱中症関連診療行為が有意に多い
2. **交互作用仮説**: 高齢者単独世帯率が高い都道府県では、猛暑日数と熱中症の関連がより強い（効果修飾）
3. **感度分析仮説**: エアコン普及率が高い都道府県では、猛暑日数と熱中症の関連が弱まる

### 統計手法
- OLS線形回帰分析
- 交互作用項: 猛暑日数 × 高齢者単独世帯率
- 感度分析: エアコン普及率による層別解析

---

## 🗂️ データソース

### 1. 気象庁「過去の気象データ検索」
- **取得データ**: 都道府県庁所在地の日別最高気温（2023年6-9月）、月別平均気温・湿度
- **URL**: https://www.data.jma.go.jp/obd/stats/etrn/index.php
- **取得方法**: Pythonスクリプトで自動ダウンロード（47都道府県×4ヶ月）
- **算出指標**:
  - 猛暑日数（最高気温≥35℃の日数）
  - WBGT指数（暑さ指数）= 0.7 × 湿球温度 + 0.3 × 乾球温度

### 2. NDB第10回オープンデータ
- **取得データ**: 救急医療管理加算、輸液算定回数（月別：2023年6-9月）
- **ファイルパス**: `02_Data/raw/NDB_OpenData/No.10/01_医科診療行為（算定回数）/月別/`
- **診療行為コード**:
  - B001 特定疾患療養管理料（救急医療管理加算）
  - G004 点滴注射（輸液）

### 3. e-Stat
- **高齢者単独世帯率**: 国勢調査2020年
- **エアコン普及率**: 全国消費実態調査2019年（または家計調査）
- **URL**: https://www.e-stat.go.jp/

---

## 🔄 Phase別実装計画

### ✅ Phase 1: データ収集（2026-02-28）

#### Phase 1a: 気象庁データ ✅
- [x] 東京都テストダウンロード成功
- [x] データ構造解析（MultiIndexヘッダー）
- [x] 猛暑日数算出ロジック検証（東京都7月: 13日）
- [x] 47都道府県自動ダウンロードスクリプト作成
- [実行中] 47都道府県×4ヶ月分ダウンロード

**スクリプト**:
- `03_Analysis/etl/01_jma_weather_data_download.py`
- `03_Analysis/etl/test_jma_download_tokyo.py`（テスト用）
- `03_Analysis/etl/02_process_jma_data.py`（処理・検証用）

**出力**:
- `02_Data/raw/jma_weather/jma_daily_temperature_2023_summer.csv`（日別気温）
- `02_Data/raw/jma_weather/jma_monthly_climate_2023.csv`（月別気温・湿度）

#### Phase 1b: e-Statデータ
- [ ] 高齢者単独世帯率ダウンロード（国勢調査2020年）
- [ ] エアコン普及率ダウンロード（全国消費実態調査2019年）

**出力**:
- `02_Data/raw/estat/elderly_solo_household_rate.csv`
- `02_Data/raw/estat/aircon_penetration_rate.csv`

#### Phase 1c: NDB第10回データ
- [ ] 熱中症関連診療行為（救急医療管理加算、輸液）月別データ抽出
- [ ] 都道府県別集計（6-9月合計）

**出力**:
- `02_Data/raw/ndb/heatstroke_medical_acts_2023_summer.csv`

---

### Phase 2: データクリーニング・統合

#### Phase 2a: 気象データ処理
- [ ] 猛暑日数を都道府県別に集計（6-9月合計）
- [ ] WBGT指数を計算（月別平均 → 夏季平均）
- [ ] 異常値チェック（気温データの妥当性検証）

**スクリプト**: `03_Analysis/etl/03_aggregate_weather_data.py`

**出力**:
- `02_Data/interim/prefecture_heatwave_summary.csv`
  - カラム: prefecture, heatwave_days, max_temp_avg, wbgt_avg

#### Phase 2b: NDBデータ標準化
- [ ] 人口10万人あたり算定回数に標準化
- [ ] 年齢階級調整（必要に応じて）

**スクリプト**: `03_Analysis/etl/04_standardize_ndb_data.py`

**出力**:
- `02_Data/interim/prefecture_heatstroke_rate.csv`
  - カラム: prefecture, heatstroke_rate_per100k

#### Phase 2c: データ統合
- [ ] 全データソースを都道府県キーで結合
- [ ] 欠損値処理
- [ ] 最終データセット作成（N=47）

**スクリプト**: `03_Analysis/etl/05_integrate_datasets.py`

**出力**:
- `02_Data/interim/analysis_dataset.csv`
  - カラム:
    - prefecture（都道府県名）
    - heatwave_days（猛暑日数）
    - wbgt_avg（WBGT平均）
    - heatstroke_rate（熱中症診療行為/10万人）
    - elderly_solo_rate（高齢者単独世帯率, %）
    - aircon_rate（エアコン普及率, %）
    - aging_rate（高齢化率, %）※国勢調査から取得

---

### Phase 3: 統計解析

#### Phase 3a: 記述統計
- [ ] 変数の分布確認（ヒストグラム、Q-Qプロット）
- [ ] 都道府県別ランキング作成
- [ ] 相関行列作成

**スクリプト**: `03_Analysis/analysis/01_descriptive_statistics.py`

**出力**:
- `03_Analysis/results/descriptive_stats_table.csv`
- `03_Analysis/results/figures/histogram_heatwave_days.png`
- `03_Analysis/results/figures/correlation_matrix.png`

#### Phase 3b: OLS回帰分析
- [ ] モデル1: 単回帰（猛暑日数のみ）
- [ ] モデル2: 多重回帰（猛暑日数 + 高齢化率）
- [ ] モデル3: 交互作用項追加（猛暑日数 × 高齢者単独世帯率）
- [ ] 診断: VIF（多重共線性）、Shapiro-Wilk（残差の正規性）

**スクリプト**: `03_Analysis/analysis/02_regression_analysis.py`

**出力**:
- `03_Analysis/results/regression_results.csv`（回帰係数テーブル）
- `03_Analysis/results/regression_diagnostics.txt`（モデル診断）

#### Phase 3c: 感度分析
- [ ] エアコン普及率による層別解析（高/低で2群に分割）
- [ ] WBGT指数を説明変数とした追加解析

**スクリプト**: `03_Analysis/analysis/03_sensitivity_analysis.py`

**出力**:
- `03_Analysis/results/sensitivity_analysis_results.csv`

---

### Phase 4: 可視化

#### Phase 4a: 主要図表
- [ ] Figure 1: 都道府県別猛暑日数のマップ（choropleth map）
- [ ] Figure 2: 猛暑日数 vs 熱中症診療行為の散布図（回帰直線付き）
- [ ] Figure 3: 交互作用プロット（高齢者単独世帯率で層別化）
- [ ] Table 1: 記述統計表（平均±SD、範囲）
- [ ] Table 2: 回帰分析結果表（β, 95%CI, p値）

**スクリプト**: `03_Analysis/analysis/04_visualization.py`

**出力**:
- `03_Analysis/results/figures/figure1_heatwave_map.png`
- `03_Analysis/results/figures/figure2_scatter_plot.png`
- `03_Analysis/results/figures/figure3_interaction_plot.png`
- `03_Analysis/results/tables/table1_descriptive_stats.csv`
- `03_Analysis/results/tables/table2_regression_results.csv`

---

### Phase 5: 論文執筆（Quarto）

#### Phase 5a: 原稿作成
- [ ] Abstract（250語以内）
- [ ] Introduction（背景、目的）
- [ ] Methods（研究デザイン、データソース、統計手法）
- [ ] Results（記述統計、回帰分析結果、図表）
- [ ] Discussion（主要知見、先行研究との比較、限界、政策提言）
- [ ] References（Vancouver style）

**ファイル**: `04_Manuscripts/Manuscript_heatwave_heatstroke.qmd`

#### Phase 5b: 参考文献整理
- [ ] 先行研究（熱中症と気温、高齢者脆弱性）10-15件
- [ ] 方法論（生態学的研究、交互作用分析）5件
- [ ] 政策文書（厚労省熱中症対策、環境省WBGT警報）3件

**ファイル**: `04_Manuscripts/references.bib`

#### Phase 5c: 出力
- [ ] HTML出力（プレビュー用）
- [ ] DOCX出力（投稿用）
- [ ] PDF出力（最終版）

**コマンド**:
```bash
quarto render 04_Manuscripts/Manuscript_heatwave_heatstroke.qmd --to html
quarto render 04_Manuscripts/Manuscript_heatwave_heatstroke.qmd --to docx
```

---

## 📊 期待される結果

### 主要仮説の検証
- 猛暑日数が1日増加すると、熱中症診療行為が **X%** 増加（95%CI: Y-Z%, p<0.05）
- 高齢者単独世帯率との交互作用が有意（p<0.05）

### 政策提言
1. **高齢者見守り強化**: 高齢者単独世帯率が高い都道府県では、猛暑日の見回り・連絡体制を強化
2. **エアコン設置支援**: エアコン普及率が低い地域への補助金制度拡充
3. **WBGT警報の活用**: 熱中症警戒アラート（環境省）の周知徹底

---

## 🎯 投稿候補ジャーナル

### 第1候補: Environmental Research（IF: 8.3）
- **理由**: 環境曝露と健康アウトカムの疫学研究を掲載
- **投稿形式**: Original Article

### 第2候補: International Journal of Environmental Research and Public Health（IF: 4.6）
- **理由**: 公衆衛生・環境疫学のオープンアクセス誌
- **投稿形式**: Article

### 第3候補: Journal of Epidemiology（IF: 3.0）
- **理由**: 日本疫学会の英文誌、国内データの論文に強い
- **投稿形式**: Original Article

---

## 📁 ファイル構造

```
projects/NDB_XXX_heatwave_heatstroke/
├── 02_Data/
│   ├── raw/
│   │   ├── jma_weather/               # 気象庁データ
│   │   ├── estat/                      # e-Statデータ
│   │   └── ndb/                        # NDBデータ
│   └── interim/                        # 中間データ
│       ├── prefecture_heatwave_summary.csv
│       ├── prefecture_heatstroke_rate.csv
│       └── analysis_dataset.csv        # 最終データセット
├── 03_Analysis/
│   ├── etl/                            # ETLスクリプト
│   │   ├── 01_jma_weather_data_download.py
│   │   ├── 02_process_jma_data.py
│   │   ├── 03_aggregate_weather_data.py
│   │   ├── 04_standardize_ndb_data.py
│   │   └── 05_integrate_datasets.py
│   ├── analysis/                       # 統計解析スクリプト
│   │   ├── 01_descriptive_statistics.py
│   │   ├── 02_regression_analysis.py
│   │   ├── 03_sensitivity_analysis.py
│   │   └── 04_visualization.py
│   └── results/                        # 解析結果
│       ├── figures/
│       ├── tables/
│       └── regression_results.csv
├── 04_Manuscripts/
│   ├── Manuscript_heatwave_heatstroke.qmd
│   ├── references.bib
│   └── vancouver.csl
├── config/
│   └── config.yaml                     # 設定ファイル
└── docs/
    ├── implementation_plan.md          # この実装計画書
    └── data_dictionary.md              # データディクショナリ

```

---

## ✅ チェックリスト

### Phase 1: データ収集
- [x] 気象庁データ構造解析
- [x] 東京都テストダウンロード
- [実行中] 47都道府県気象データダウンロード
- [ ] e-Stat高齢者単独世帯率
- [ ] e-Statエアコン普及率
- [ ] NDB熱中症診療行為データ

### Phase 2: データ統合
- [ ] 猛暑日数集計
- [ ] WBGT指数計算
- [ ] NDBデータ標準化
- [ ] 最終データセット作成

### Phase 3: 統計解析
- [ ] 記述統計
- [ ] OLS回帰分析
- [ ] 交互作用分析
- [ ] 感度分析

### Phase 4: 可視化
- [ ] Figure 1-3作成
- [ ] Table 1-2作成

### Phase 5: 論文執筆
- [ ] Quarto原稿作成
- [ ] 参考文献整理
- [ ] HTML/DOCX出力

---

## 📝 更新履歴

- **2026-02-28**: 初版作成（Phase 1a進行中）

---

**次のアクション**: Phase 1aの完了確認後、Phase 1b（e-Statデータ取得）に進む
