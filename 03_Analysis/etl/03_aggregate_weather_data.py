"""
気象データ集計：47都道府県の猛暑日数とWBGT指数を算出

入力:
- jma_daily_temperature_2023_summer.csv（47都道府県×6-9月の日別データ）

出力:
- prefecture_heatwave_summary.csv（47都道府県の猛暑日数・WBGT指数）
"""

import pandas as pd
import numpy as np
from pathlib import Path

# ディレクトリ設定
PROJECT_ROOT = Path(__file__).resolve().parents[2]
INPUT_DIR = PROJECT_ROOT / "02_Data" / "raw" / "jma_weather"
OUTPUT_DIR = PROJECT_ROOT / "02_Data" / "interim"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 80)
print("気象データ集計: 47都道府県の猛暑日数・WBGT指数")
print("=" * 80)

# CSVを読み込み
csv_path = INPUT_DIR / "jma_daily_temperature_2023_summer.csv"

# ヘッダーを4行読み飛ばしてデータのみ取得
df = pd.read_csv(csv_path, skiprows=4, encoding='utf-8-sig')

print(f"\n[データ読み込み]")
print(f"ファイル: {csv_path}")
print(f"形状: {df.shape}")
print(f"\n最初の5行:")
print(df.head())

# カラム名を整理
# 実際のデータ構造: 25列（日〜天気夜 21列 + 都道府県・観測所・年・月 4列）
if len(df.columns) == 25:
    df.columns = [
        '日', '気圧現地', '気圧海面', '降水量合計', '降水量最大1h', '降水量最大10m',
        '気温平均', '気温最高', '気温最低', '湿度平均', '湿度最小',
        '風速平均', '風速最大', '風向最大', '瞬間風速最大', '瞬間風向最大',
        '日照時間', '降雪', '積雪', '天気昼', '天気夜',
        '都道府県', '観測所', '年', '月'
    ]
elif len(df.columns) == 26:
    df.columns = [
        '日', '気圧現地', '気圧海面', '降水量合計', '降水量最大1h', '降水量最大10m',
        '気温平均', '気温最高', '気温最低', '湿度平均', '湿度最小',
        '風速平均', '風速最大', '風向最大', '瞬間風速最大', '瞬間風向最大',
        '日照時間', '降雪', '積雪', '天気昼', '天気夜',
        '都道府県', '観測所', '年', '月', '備考'
    ]
else:
    print(f"\n[警告] 予期しないカラム数: {len(df.columns)}")
    print(f"カラム: {list(df.columns)}")

print(f"\n[カラム名変更後]")
print(df.head())

# 数値型に変換（--などの欠損値をNaNに）
df['気温最高'] = pd.to_numeric(df['気温最高'], errors='coerce')
df['気温平均'] = pd.to_numeric(df['気温平均'], errors='coerce')
df['湿度平均'] = pd.to_numeric(df['湿度平均'], errors='coerce')

# 都道府県カラムの確認
if '都道府県' not in df.columns:
    print("\n[エラー] '都道府県'カラムが見つかりません")
    print(f"利用可能なカラム: {list(df.columns)}")
    raise ValueError("都道府県カラムが見つかりません")


def calc_simple_wet_bulb_temp(dry_temp, humidity):
    """
    簡易湿球温度計算

    Parameters:
    -----------
    dry_temp : float
        乾球温度（℃）
    humidity : float
        相対湿度（%）

    Returns:
    --------
    float
        湿球温度（℃）の近似値
    """
    # 簡易式: Tw ≈ T - (100 - RH)/5
    return dry_temp - (100 - humidity) / 5


# WBGT指数の計算
df['湿球温度推定'] = df.apply(
    lambda row: calc_simple_wet_bulb_temp(row['気温平均'], row['湿度平均'])
    if pd.notna(row['気温平均']) and pd.notna(row['湿度平均']) else np.nan,
    axis=1
)

# WBGT = 0.7 × Tw + 0.3 × T
df['WBGT'] = 0.7 * df['湿球温度推定'] + 0.3 * df['気温平均']

# 都道府県別に集計
print("\n[都道府県別集計]")
prefecture_summary = []

for pref in df['都道府県'].unique():
    if pd.isna(pref):
        continue

    df_pref = df[df['都道府県'] == pref].copy()

    # 猛暑日数（35℃以上）
    heatwave_days = (df_pref['気温最高'] >= 35.0).sum()

    # 最高気温の統計
    max_temp_max = df_pref['気温最高'].max()
    max_temp_avg = df_pref['気温最高'].mean()

    # WBGT指数の平均
    wbgt_avg = df_pref['WBGT'].mean()

    # WBGT危険日数（31℃以上）
    wbgt_danger_days = (df_pref['WBGT'] >= 31.0).sum()

    # データ日数
    total_days = len(df_pref)

    prefecture_summary.append({
        '都道府県': pref,
        '猛暑日数': heatwave_days,
        '最高気温最大値': max_temp_max,
        '最高気温平均値': max_temp_avg,
        'WBGT平均': wbgt_avg,
        'WBGT危険日数': wbgt_danger_days,
        'データ日数': total_days
    })

    print(f"{pref}: 猛暑日数={heatwave_days}日, 最高気温平均={max_temp_avg:.1f}℃, WBGT平均={wbgt_avg:.1f}℃")

# DataFrame化
df_summary = pd.DataFrame(prefecture_summary)

# 猛暑日数でソート（降順）
df_summary = df_summary.sort_values('猛暑日数', ascending=False).reset_index(drop=True)

print(f"\n[集計完了]")
print(f"都道府県数: {len(df_summary)}")
print(f"\n猛暑日数トップ10:")
print(df_summary[['都道府県', '猛暑日数', '最高気温平均値', 'WBGT平均']].head(10))

# 基本統計
print(f"\n[全国統計]")
print(f"猛暑日数 平均: {df_summary['猛暑日数'].mean():.1f}日")
print(f"猛暑日数 中央値: {df_summary['猛暑日数'].median():.1f}日")
print(f"猛暑日数 最大: {df_summary['猛暑日数'].max()}日 ({df_summary.loc[df_summary['猛暑日数'].idxmax(), '都道府県']})")
print(f"猛暑日数 最小: {df_summary['猛暑日数'].min()}日 ({df_summary.loc[df_summary['猛暑日数'].idxmin(), '都道府県']})")

print(f"\nWBGT平均 全国平均: {df_summary['WBGT平均'].mean():.1f}℃")
print(f"WBGT平均 最大: {df_summary['WBGT平均'].max():.1f}℃ ({df_summary.loc[df_summary['WBGT平均'].idxmax(), '都道府県']})")
print(f"WBGT平均 最小: {df_summary['WBGT平均'].min():.1f}℃ ({df_summary.loc[df_summary['WBGT平均'].idxmin(), '都道府県']})")

# CSVに保存
output_path = OUTPUT_DIR / "prefecture_heatwave_summary.csv"
df_summary.to_csv(output_path, index=False, encoding='utf-8-sig')

print(f"\n[保存完了]")
print(f"出力ファイル: {output_path}")
print(f"データ件数: {len(df_summary)} 都道府県")

# 簡易的なデータ品質チェック
print(f"\n[データ品質チェック]")
if len(df_summary) != 47:
    print(f"[警告] 都道府県数が47ではありません: {len(df_summary)}件")
else:
    print("[OK] 都道府県数: 47件")

# 欠損値チェック
missing_check = df_summary.isna().sum()
if missing_check.sum() > 0:
    print(f"\n[警告] 欠損値あり:")
    print(missing_check[missing_check > 0])
else:
    print("[OK] 欠損値なし")

# 異常値チェック
if (df_summary['猛暑日数'] < 0).any() or (df_summary['猛暑日数'] > 122).any():
    print(f"\n[警告] 猛暑日数に異常値あり（範囲: 0-122日）")
else:
    print("[OK] 猛暑日数の範囲正常（0-122日）")

print("\n" + "=" * 80)
print("集計完了！")
print("=" * 80)
