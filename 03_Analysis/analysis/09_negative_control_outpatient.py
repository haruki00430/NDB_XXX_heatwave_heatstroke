"""
Analysis A-1: Negative control — Outpatient utilization rate (Comment #21 response)

Tests whether elderly solo household rate is associated with GENERAL outpatient
utilization (R5 Patient Survey, per 100,000). A null or weak association would
support that the primary finding (infusion therapy) is not merely reflecting
overall healthcare access, but is more specific to heat-related dehydration.

Generates:
  - negative_control_dataset.csv
  - negative_control_regression_results.txt
  - figS2_negative_control.png  (side-by-side: negative control vs primary outcome)
"""

import csv
import unicodedata
import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path
from scipy import stats as scipy_stats

PROJECT_ROOT    = Path(__file__).resolve().parents[2]
SURVEY_PATH     = PROJECT_ROOT / "02_Data" / "raw" / "patient_survey_r5_t36_pref_age.csv"
DATASET_PATH    = PROJECT_ROOT / "03_Analysis" / "results" / "population_adjusted_dataset.csv"
OUT_DIR         = PROJECT_ROOT / "03_Analysis" / "results" / "negative_control"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ── prefecture name mapping: patient survey (short) → main dataset (full) ──────
# Patient survey omits 県/都/道/府; main dataset uses full names
SURVEY_TO_FULL = {
    '北海道': '北海道', '青森': '青森県', '岩手': '岩手県', '宮城': '宮城県',
    '秋田': '秋田県', '山形': '山形県', '福島': '福島県', '茨城': '茨城県',
    '栃木': '栃木県', '群馬': '群馬県', '埼玉': '埼玉県', '千葉': '千葉県',
    '東京': '東京都', '神奈川': '神奈川県', '新潟': '新潟県', '富山': '富山県',
    '石川': '石川県', '福井': '福井県', '山梨': '山梨県', '長野': '長野県',
    '岐阜': '岐阜県', '静岡': '静岡県', '愛知': '愛知県', '三重': '三重県',
    '滋賀': '滋賀県', '京都': '京都府', '大阪': '大阪府', '兵庫': '兵庫県',
    '奈良': '奈良県', '和歌山': '和歌山県', '鳥取': '鳥取県', '島根': '島根県',
    '岡山': '岡山県', '広島': '広島県', '山口': '山口県', '徳島': '徳島県',
    '香川': '香川県', '愛媛': '愛媛県', '高知': '高知県', '福岡': '福岡県',
    '佐賀': '佐賀県', '長崎': '長崎県', '熊本': '熊本県', '大分': '大分県',
    '宮崎': '宮崎県', '鹿児島': '鹿児島県', '沖縄': '沖縄県',
}

# prefecture English labels (for figure annotation)
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
    '福岡県': 'Fukuoka',    '佐賀県': 'Saga',      '長崎県': 'Nagasaki',
    '熊本県': 'Kumamoto',   '大分県': 'Oita',      '宮崎県': 'Miyazaki',
    '鹿児島県': 'Kagoshima','沖縄県': 'Okinawa',
}


# ── parse patient survey CSV ─────────────────────────────────────────────────
def parse_patient_survey(filepath):
    """
    Extract total outpatient utilization rate (per 100,000) by prefecture.

    File structure (after 6 metadata rows):
      - Prefecture name rows: single element ['北海道']
      - Data rows: 9 elements [sex, age_group, 入院総数, 入院病院, 入院一般, 外来総数, ...]
    We capture row[5] (外来総数) where row[0]='総数' and row[1]='総数'.
    '全国' (national total) is excluded.
    '-' values are treated as NaN.
    """
    results = []
    current_pref = None
    skip_prefectures = {'全国'}

    with open(filepath, encoding='cp932', errors='replace') as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i < 6:
                continue  # skip metadata rows

            # Normalize full-width characters to half-width for robust matching
            row = [unicodedata.normalize('NFKC', cell).strip() for cell in row]

            if len(row) == 1 and row[0]:
                # Prefecture name row
                pref_short = row[0]
                current_pref = None if pref_short in skip_prefectures else pref_short

            elif (len(row) == 9
                  and row[0] == '総数'
                  and row[1] == '総数'
                  and current_pref is not None):
                # Total sex × total age group row → extract 外来総数 (col index 5)
                val_str = row[5]
                val = float(val_str) if val_str not in ('', '-') else float('nan')
                full_name = SURVEY_TO_FULL.get(current_pref)
                if full_name is None:
                    print(f"[WARN] Unknown prefecture in survey: '{current_pref}'")
                    continue
                results.append({'都道府県': full_name, '外来受療率_per100k': val})
                current_pref = None  # reset to avoid duplicate capture

    df = pd.DataFrame(results)
    return df


# ── load data ────────────────────────────────────────────────────────────────
print("[1/5] Parsing patient survey R5 data...")
df_survey = parse_patient_survey(SURVEY_PATH)
print(f"      Parsed {len(df_survey)} prefectures  "
      f"(mean outpatient rate = {df_survey['外来受療率_per100k'].mean():.0f} per 100,000)")

print("[2/5] Loading main analysis dataset...")
main = pd.read_csv(DATASET_PATH, encoding='utf-8-sig')
df   = main.merge(df_survey, on='都道府県', how='inner')
df['pref_en'] = df['都道府県'].map(PREF_EN).fillna(df['都道府県'])
print(f"      Merged: {len(df)} rows")

# Save merged dataset
save_cols = ['都道府県', '高齢者単独世帯率', '点滴注射_per100k', '外来受療率_per100k',
             '猛暑日数', 'WBGT平均', 'エアコン普及率']
df[save_cols].to_csv(OUT_DIR / "negative_control_dataset.csv",
                     index=False, encoding='utf-8-sig')
print(f"      Saved: negative_control_dataset.csv")


# ── regressions ──────────────────────────────────────────────────────────────
def run_ols(y_series, x_col, df_):
    X = sm.add_constant(df_[[x_col]])
    m = sm.OLS(y_series, X).fit()
    ci = m.conf_int(alpha=0.05)
    r, p_r = scipy_stats.pearsonr(df_[x_col], y_series)
    return m, ci, r, p_r


print("[3/5] Running regressions...")

X_VAR = '高齢者単独世帯率'
Y_NC  = df['外来受療率_per100k']    # negative control
Y_PRI = df['点滴注射_per100k']      # primary outcome

m_nc,  ci_nc,  r_nc,  p_r_nc  = run_ols(Y_NC,  X_VAR, df)
m_pri, ci_pri, r_pri, p_r_pri = run_ols(Y_PRI, X_VAR, df)

# Format p-values
def fmt_p(p):
    if p < 0.001:
        return "p < 0.001"
    return f"p = {p:.3f}"

# Save results
with open(OUT_DIR / "negative_control_regression_results.txt", 'w', encoding='utf-8') as f:
    f.write("=== Negative Control Regression Results ===\n")
    f.write("Outcome: Outpatient utilization rate (per 100,000)  [Patient Survey R5]\n")
    f.write("Predictor: Elderly solo household rate (%)\n\n")

    f.write("--- Model NC: Elderly solo household rate → Outpatient utilization rate ---\n")
    f.write(f"  beta = {m_nc.params[X_VAR]:.2f}\n")
    f.write(f"  95% CI = ({ci_nc.loc[X_VAR, 0]:.2f}, {ci_nc.loc[X_VAR, 1]:.2f})\n")
    f.write(f"  p = {m_nc.pvalues[X_VAR]:.4f}   [{fmt_p(m_nc.pvalues[X_VAR])}]\n")
    f.write(f"  R2 = {m_nc.rsquared:.3f}   Adj.R2 = {m_nc.rsquared_adj:.3f}\n")
    f.write(f"  Pearson r = {r_nc:.3f}   {fmt_p(p_r_nc)}\n\n")

    f.write("--- Model Primary: Elderly solo household rate → Infusion therapy rate ---\n")
    f.write(f"  beta = {m_pri.params[X_VAR]:.2f}\n")
    f.write(f"  95% CI = ({ci_pri.loc[X_VAR, 0]:.2f}, {ci_pri.loc[X_VAR, 1]:.2f})\n")
    f.write(f"  p = {m_pri.pvalues[X_VAR]:.4f}   [{fmt_p(m_pri.pvalues[X_VAR])}]\n")
    f.write(f"  R2 = {m_pri.rsquared:.3f}   Adj.R2 = {m_pri.rsquared_adj:.3f}\n")
    f.write(f"  Pearson r = {r_pri:.3f}   {fmt_p(p_r_pri)}\n")

with open(OUT_DIR / "negative_control_regression_results.txt", 'r', encoding='utf-8') as f:
    print("\n" + f.read())


# ── figure: side-by-side scatter plots ──────────────────────────────────────
print("[4/5] Creating figure...")

plt.rcParams.update({
    'font.family':         'DejaVu Sans',
    'axes.unicode_minus':  False,
    'axes.spines.top':     False,
    'axes.spines.right':   False,
})

fig, axes = plt.subplots(1, 2, figsize=(16, 7))
fig.subplots_adjust(wspace=0.35)


def plot_panel(ax, x_data, y_data, model, ci_df_model, r_val, p_val,
               xlabel, ylabel, title, color, label_series):
    ax.scatter(x_data, y_data, s=80, alpha=0.65,
               color=color, edgecolors='#333', linewidth=0.5)

    x_line = np.linspace(x_data.min(), x_data.max(), 100)
    X_line  = sm.add_constant(pd.DataFrame({x_data.name: x_line}))
    y_pred  = model.predict(X_line)
    ci_pred = model.get_prediction(X_line).summary_frame(alpha=0.05)

    ax.plot(x_line, y_pred, '-', color='#c0392b', linewidth=2, label='Regression line')
    ax.fill_between(x_line, ci_pred['mean_ci_lower'], ci_pred['mean_ci_upper'],
                    alpha=0.18, color='#c0392b', label='95% CI')

    for _, row in label_series.iterrows():
        ax.annotate(row['pref_en'],
                    xy=(row[x_data.name], row[y_data.name]),
                    xytext=(5, 3), textcoords='offset points',
                    fontsize=8, alpha=0.85)

    p_str  = fmt_p(p_val)
    beta_v = model.params[x_data.name]
    r2_v   = model.rsquared
    ax.set_title(f"{title}\n"
                 f"β = {beta_v:.2f},  {p_str},  r = {r_val:.3f},  R² = {r2_v:.3f}  (N = 47)",
                 fontsize=10.5, fontweight='bold', pad=10)
    ax.set_xlabel(xlabel, fontsize=11)
    ax.set_ylabel(ylabel, fontsize=11)
    ax.legend(fontsize=9)
    ax.grid(alpha=0.2)


# Determine top/bottom 5 for each panel
top5_nc  = df.nlargest(3,  '外来受療率_per100k')
bot5_nc  = df.nsmallest(3, '外来受療率_per100k')
label_nc = pd.concat([top5_nc, bot5_nc])

top5_pri  = df.nlargest(3,  '点滴注射_per100k')
bot5_pri  = df.nsmallest(3, '点滴注射_per100k')
label_pri = pd.concat([top5_pri, bot5_pri])

plot_panel(
    ax=axes[0],
    x_data=df[X_VAR], y_data=df['外来受療率_per100k'],
    model=m_nc, ci_df_model=ci_nc, r_val=r_nc, p_val=m_nc.pvalues[X_VAR],
    xlabel="Elderly solo household rate (%)",
    ylabel="General outpatient utilization rate (per 100,000)",
    title="Negative Control\nElderly Solo Household Rate → Outpatient Utilization",
    color='#7f8c8d',
    label_series=label_nc,
)

plot_panel(
    ax=axes[1],
    x_data=df[X_VAR], y_data=df['点滴注射_per100k'],
    model=m_pri, ci_df_model=ci_pri, r_val=r_pri, p_val=m_pri.pvalues[X_VAR],
    xlabel="Elderly solo household rate (%)",
    ylabel="Infusion therapy rate (per 100,000)",
    title="Primary Outcome\nElderly Solo Household Rate → Infusion Therapy",
    color='steelblue',
    label_series=label_pri,
)

fig.suptitle(
    "Supplementary Figure S2. Negative Control Analysis: General Outpatient Utilization\n"
    "vs. Dehydration-Related Infusion Therapy Across 47 Japanese Prefectures",
    fontsize=12, fontweight='bold', y=1.01,
)

fig.savefig(OUT_DIR / "figS2_negative_control.png",
            dpi=300, bbox_inches='tight')
print("[OK] Figure saved: figS2_negative_control.png")
plt.close(fig)

print("[5/5] Done.")
print(f"\n=== Summary ===")
print(f"Negative control  (outpatient): beta={m_nc.params[X_VAR]:.2f}, "
      f"{fmt_p(m_nc.pvalues[X_VAR])}, R2={m_nc.rsquared:.3f}")
print(f"Primary outcome   (infusion):   beta={m_pri.params[X_VAR]:.2f}, "
      f"{fmt_p(m_pri.pvalues[X_VAR])}, R2={m_pri.rsquared:.3f}")
