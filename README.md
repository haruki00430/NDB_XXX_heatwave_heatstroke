# Are Heat-Health Systems Socially Blind?
**Social Isolation and Dehydration-Related Healthcare Utilization Across Japan**

**熱中症サーベイランスは社会的孤立を見落としているか？**
高齢者単独世帯率と脱水関連医療利用の全国生態学研究（日本）

---

## Overview / 概要

### English

This repository contains analysis code for a nationwide ecological study examining whether **prefecture-level elderly solo household rate** — a community-level marker of social isolation — is associated with **dehydration-related healthcare utilization** (infusion therapy ≥500 mL, NDB procedure code G004) across Japan's 47 prefectures.

**Key finding**: Elderly solo household rate was the only significant ecological predictor of infusion therapy utilization (β = 723.37; 95% CI, 376.52–1,070.21; R² = 0.282; *p* = 0.0001), whereas heatwave days, mean WBGT, and air conditioning prevalence were not significantly associated.

**Study design**: Ecological study | N = 47 prefectures | Fiscal Year 2023

**Manuscript**: Saito H, Ohira T. Are Heat-Health Systems Socially Blind? Social Isolation and Dehydration-Related Healthcare Utilization Across Japan. *(In submission, 2026)*

### 日本語

本リポジトリは、都道府県単位（N = 47）の全国生態学研究の解析コードを公開するものです。**高齢者単独世帯率**（社会的孤立の地域指標）が**脱水関連医療利用**（500 mL 以上輸液療法、NDB 手技コード G004）と関連するかを検証しました。

**主要結果**: 高齢者単独世帯率のみが輸液療法実施率と有意な関連を示しました（β = 723.37、95% CI: 376.52–1,070.21、R² = 0.282、*p* = 0.0001）。猛暑日数・WBGT・エアコン普及率は有意な関連を示しませんでした。

**研究デザイン**: 生態学的研究 | N = 47 都道府県 | 2023 年度（令和 5 年度）

---

## Data Sources / データソース

| Source | Variables | 説明 |
|---|---|---|
| NDB Open Data No.10 (MHLW) | Infusion therapy rate (G004, ≥500 mL) | 輸液療法算定回数（FY2023） |
| National Census 2020 (Statistics Bureau) | Elderly solo household rate, population | 高齢者単独世帯率・人口 |
| Japan Meteorological Agency (JMA) | Heatwave days (≥35°C), mean WBGT (Jun–Sep 2023) | 猛暑日数・WBGT（2023 年 6–9 月） |
| National Survey of Family Income and Expenditure 2014 (MIC) | Air conditioning prevalence | エアコン普及率 |
| Fire and Disaster Management Agency (FDMA) | Heatstroke ambulance transport (external validation) | 熱中症救急搬送件数（外的妥当性確認） |
| R5 Patient Survey (MHLW) | General outpatient rate (negative control) | 外来受療率（陰性対照） |

> **Note / 注意**: NDB raw data are not included in this repository and are not redistributable. Aggregate open data are available from the Ministry of Health, Labour and Welfare: https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000177182.html
>
> NDB 生データは本リポジトリに含まれておらず、再配布できません。集計オープンデータは厚生労働省ウェブサイトから入手可能です。

---

## Repository Structure / リポジトリ構造

```
NDB_XXX_heatwave_heatstroke/
├── 02_Data/
│   └── interim/                    # Intermediate data (CSV; excluded from repo)
│                                   # 中間データ（CSV; リポジトリ除外）
├── 03_Analysis/
│   ├── etl/                        # Data acquisition and preprocessing
│   │   ├── 01_jma_weather_data_download.py   # JMA weather data download / 気象データ取得
│   │   ├── 02_process_jma_data.py            # JMA data processing / 気象データ処理
│   │   ├── 03_aggregate_weather_data.py      # Prefecture-level aggregation / 都道府県別集計
│   │   └── 04_extract_elderly_solo_rate.py   # Census elderly solo household rate / 国勢調査データ抽出
│   ├── analysis/                   # Statistical analysis (run scripts 01–09 in order)
│   │   ├── 01_integrate_and_analyze.py       # Data integration + initial OLS regression
│   │   ├── 02_population_adjusted_analysis.py # Population-adjusted OLS regression
│   │   ├── 03_ridge_regression_analysis.py   # Ridge regression (multicollinearity)
│   │   ├── 04_stepwise_univariate_analysis.py # Stepwise / univariate regression
│   │   ├── 05_sensitivity_analysis.py        # Sensitivity analysis (Cook's distance, stratification)
│   │   ├── 06_figures_english.py             # English figure generation
│   │   ├── 07_additional_climate_variables.py # Additional climate variable analysis
│   │   ├── 08_fdma_heatstroke_validation.py  # FDMA external validation (Supplementary Figure S1)
│   │   └── 09_negative_control_outpatient.py # Negative control analysis (Supplementary Figure S2)
│   └── results/                    # Output figures and result tables
│       ├── sensitivity_analysis/   # Cook's distance plot, stratified scatter plot
│       ├── fdma_validation/        # Supplementary Figure S1 (FDMA validation)
│       ├── negative_control/       # Supplementary Figure S2 (negative control)
│       └── additional_climate/     # Additional climate variable figures
└── 04_Manuscripts/
    ├── Manuscript_heatwave_social_isolation_final.qmd  # Quarto source (submission version)
    ├── Are_Heat_Health_Systems_Socially_Blind_main.docx # Final approved manuscript
    ├── references.bib                                  # Reference library
    └── vancouver.csl                                   # Citation style
```

---

## Reproduction / 再現手順

### Prerequisites / 必要環境

- Python ≥ 3.10
- [Quarto](https://quarto.org/) (for manuscript rendering / 論文レンダリング用)

### Installation / インストール

```bash
git clone https://github.com/haruki00430/NDB_XXX_heatwave_heatstroke.git
cd NDB_XXX_heatwave_heatstroke
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### Data Preparation / データ準備

1. Download NDB Open Data No.10 from MHLW and place Excel files under `02_Data/raw/`.  
   NDB オープンデータ第 10 回を厚生労働省からダウンロードし `02_Data/raw/` に配置してください。

2. Run ETL scripts in order to build intermediate datasets:  
   ETL スクリプトを順番に実行して中間データを生成してください：
   ```bash
   python 03_Analysis/etl/01_jma_weather_data_download.py
   python 03_Analysis/etl/02_process_jma_data.py
   python 03_Analysis/etl/03_aggregate_weather_data.py
   python 03_Analysis/etl/04_extract_elderly_solo_rate.py
   ```

### Analysis / 解析実行

Run analysis scripts 01 through 09 in order:  
解析スクリプトを 01 から 09 の順に実行してください：

```bash
python 03_Analysis/analysis/01_integrate_and_analyze.py
python 03_Analysis/analysis/02_population_adjusted_analysis.py
python 03_Analysis/analysis/03_ridge_regression_analysis.py
python 03_Analysis/analysis/04_stepwise_univariate_analysis.py
python 03_Analysis/analysis/05_sensitivity_analysis.py
python 03_Analysis/analysis/06_figures_english.py
python 03_Analysis/analysis/07_additional_climate_variables.py
python 03_Analysis/analysis/08_fdma_heatstroke_validation.py
python 03_Analysis/analysis/09_negative_control_outpatient.py
```

---

## Citation / 引用

If you use this code, please cite the associated manuscript and code repository:  
本コードを使用する場合は、論文とコードリポジトリの両方を引用してください：

**Manuscript**:
> Saito H, Ohira T. Are Heat-Health Systems Socially Blind? Social Isolation and Dehydration-Related Healthcare Utilization Across Japan. *(In submission, 2026)*

**Code repository** (DOI to be updated after Zenodo registration):
> Saito H. Analysis code for "Are Heat-Health Systems Socially Blind?" [Software]. Zenodo. *(DOI: TBD)*

---

## Ethics / 倫理事項

This study used publicly available aggregate data. Individual informed consent was not required, and institutional ethics review was not applicable in accordance with Japanese ethical guidelines for epidemiological research.

本研究は公表集計データを使用しており、個人の同意取得および倫理審査委員会の審査は不要です（「疫学研究に関する倫理指針」に準拠）。

---

## License / ライセンス

Analysis code is released under the [MIT License](LICENSE).  
NDB Open Data is provided by the Ministry of Health, Labour and Welfare of Japan and is not redistributable as part of this repository.

解析コードは MIT ライセンスで公開しています。NDB オープンデータは厚生労働省が提供するものであり、本リポジトリから再配布することはできません。
