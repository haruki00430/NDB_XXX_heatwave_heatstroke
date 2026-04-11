"""
気象庁データ処理：猛暑日数とWBGT指数の算出

入力:
- test_tokyo_daily_table_0.csv（日別気温データ）

出力:
- 猛暑日数（35℃以上日数）
- WBGT指数（暑さ指数）
"""

import pandas as pd
from pathlib import Path

# ディレクトリ設定
PROJECT_ROOT = Path(__file__).resolve().parents[2]
INPUT_DIR = PROJECT_ROOT / "02_Data" / "raw" / "jma_weather"
OUTPUT_DIR = PROJECT_ROOT / "02_Data" / "interim"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 80)
print("気象庁データ処理: 猛暑日数・WBGT指数の算出")
print("=" * 80)

# CSVを読み込み（マルチインデックスヘッダーをスキップして単純化）
csv_path = INPUT_DIR / "test_tokyo_daily_table_0.csv"

# ヘッダーを4行読み飛ばしてデータのみ取得
df = pd.read_csv(csv_path, skiprows=4, encoding='utf-8-sig')

print(f"\n[データ読み込み]")
print(f"ファイル: {csv_path}")
print(f"形状: {df.shape}")
print(f"\nカラム: {list(df.columns)}")
print(f"\n最初の5行:")
print(df.head())

# カラム名を整理
# 実際のデータから推測：カラム0=日, カラム6=平均気温, カラム7=最高気温, カラム8=最低気温
df.columns = [
    '日', '気圧現地', '気圧海面', '降水量合計', '降水量最大1h', '降水量最大10m',
    '気温平均', '気温最高', '気温最低', '湿度平均', '湿度最小',
    '風速平均', '風速最大', '風向最大', '瞬間風速最大', '瞬間風向最大',
    '日照時間', '降雪', '積雪', '天気昼', '天気夜'
]

print(f"\n[カラム名変更後]")
print(df.head())

# 数値型に変換（--などの欠損値をNaNに）
df['気温最高'] = pd.to_numeric(df['気温最高'], errors='coerce')
df['気温平均'] = pd.to_numeric(df['気温平均'], errors='coerce')
df['湿度平均'] = pd.to_numeric(df['湿度平均'], errors='coerce')

# 猛暑日数（35℃以上の日数）を集計
heatwave_days = (df['気温最高'] >= 35.0).sum()
max_temperature = df['気温最高'].max()
mean_temperature = df['気温最高'].mean()

print(f"\n[猛暑日数（35℃以上）]")
print(f"東京都 2023年7月: {heatwave_days} 日")
print(f"最高気温の最大値: {max_temperature:.1f}℃")
print(f"最高気温の平均値: {mean_temperature:.1f}℃")

# WBGT指数の簡易計算（屋外）
# WBGT ≈ 0.7 × 湿球温度 + 0.3 × 乾球温度
# 湿球温度は湿度から推定（簡易式）
# Tw ≈ T × arctan(0.151977 × sqrt(RH% + 8.313659)) + arctan(T + RH%) - arctan(RH% - 1.676331) + 0.00391838 × (RH%)^(3/2) × arctan(0.023101 × RH%) - 4.686035
# ここでは簡易版として: Tw ≈ T × (RH/100)^0.5 を使用

import numpy as np

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
    # 簡易式: Tw ≈ T - (100 - RH)/5 （湿度100%でTw=T、湿度0%でTw=T-20）
    return dry_temp - (100 - humidity) / 5

df['湿球温度推定'] = df.apply(
    lambda row: calc_simple_wet_bulb_temp(row['気温平均'], row['湿度平均'])
    if pd.notna(row['気温平均']) and pd.notna(row['湿度平均']) else np.nan,
    axis=1
)

# WBGT = 0.7 × Tw + 0.3 × T
df['WBGT'] = 0.7 * df['湿球温度推定'] + 0.3 * df['気温平均']

mean_wbgt = df['WBGT'].mean()

print(f"\n[WBGT指数（暑さ指数）]")
print(f"東京都 2023年7月平均: {mean_wbgt:.1f}℃")
print(f"\nWBGT基準:")
print(f"  31℃以上: 危険（運動は原則中止）")
print(f"  28-31℃: 厳重警戒（激しい運動は中止）")
print(f"  25-28℃: 警戒（積極的に休憩）")
print(f"  25℃未満: 注意（こまめに水分補給）")

# 危険日数（WBGT>=31℃）を集計
dangerous_days = (df['WBGT'] >= 31.0).sum()
print(f"\n危険日数（WBGT>=31℃）: {dangerous_days} 日")

# 結果を保存
result_df = df[['日', '気温平均', '気温最高', '気温最低', '湿度平均', 'WBGT']].copy()
result_df['都道府県'] = '東京都'
result_df['年'] = 2023
result_df['月'] = 7

output_path = OUTPUT_DIR / "tokyo_heatwave_july2023.csv"
result_df.to_csv(output_path, index=False, encoding='utf-8-sig')

print(f"\n[保存] 処理済みデータ: {output_path}")

print("\n" + "=" * 80)
print("処理完了！")
print("=" * 80)
