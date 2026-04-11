"""
壊れたCSV構造を修正
"""

import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CSV_PATH = PROJECT_ROOT / "02_Data" / "raw" / "jma_weather" / "jma_daily_temperature_2023_summer.csv"
OUTPUT_PATH = PROJECT_ROOT / "02_Data" / "raw" / "jma_weather" / "jma_daily_temperature_2023_summer_fixed.csv"

print("=" * 80)
print("CSV構造修正スクリプト")
print("=" * 80)

# ヘッダーなしで全データを読み込み
df = pd.read_csv(CSV_PATH, header=None, encoding='utf-8-sig')

print(f"\n[元データ]")
print(f"形状: {df.shape}")
print(f"カラム数: {df.shape[1]}")
print(f"\n最初の3行:")
print(df.head(3))

# 最初の25列のみを抽出（気象データ25列）
df_fixed = df.iloc[:, :25]

# カラム名を設定
df_fixed.columns = [
    '日', '気圧現地', '気圧海面', '降水量合計', '降水量最大1h', '降水量最大10m',
    '気温平均', '気温最高', '気温最低', '湿度平均', '湿度最小',
    '風速平均', '風速最大', '風向最大', '瞬間風速最大', '瞬間風向最大',
    '日照時間', '降雪', '積雪', '天気昼', '天気夜',
    '都道府県', '観測所', '年', '月'
]

print(f"\n[修正後]")
print(f"形状: {df_fixed.shape}")
print(f"\n最初の5行:")
print(df_fixed.head())

# 都道府県の一覧を確認
unique_prefs = df_fixed['都道府県'].dropna().unique()
print(f"\n[都道府県数確認]")
print(f"都道府県数: {len(unique_prefs)}")
print(f"都道府県リスト:")
for pref in sorted(unique_prefs):
    print(f"  - {pref}")

# 保存
df_fixed.to_csv(OUTPUT_PATH, index=False, encoding='utf-8-sig')

print(f"\n[保存完了]")
print(f"出力ファイル: {OUTPUT_PATH}")
print(f"データ行数: {len(df_fixed)}")

# 元のファイルを置き換え
import shutil
shutil.move(str(OUTPUT_PATH), str(CSV_PATH))
print(f"\n[OK] 元ファイルを更新: {CSV_PATH}")

print("\n" + "=" * 80)
print("CSV構造修正完了！")
print("=" * 80)
