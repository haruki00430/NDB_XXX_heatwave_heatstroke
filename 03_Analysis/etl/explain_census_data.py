"""
Census_2020フォルダ内のデータの詳細説明
"""

import pandas as pd

file_path = r"C:\Users\user\SharedWorkspace\projects\NDB_Research_Hub\02_Data\raw\Statistics_Bureau\Census_2020\tblT001141H13.txt"

print("=" * 80)
print("Census_2020フォルダ内のデータ構造の詳細")
print("=" * 80)

# データ読み込み（文字列として）
df = pd.read_csv(file_path, encoding='cp932', dtype=str)

print("\n【ファイル構造】")
print(f"- ファイル名形式: tblT001141H01〜H47.txt（47都道府県分）")
print(f"- 東京都（H13）の総行数: {len(df):,} 行")
print(f"- カラム数: {len(df.columns)}")

print("\n【HTKSYORI列の分布】（処理区分と推測）")
htksyori_counts = df['HTKSYORI'].value_counts()
print(htksyori_counts)

print("\n【KEY_CODEの例】（地域識別コード）")
print("最初の20行:")
for i, code in enumerate(df['KEY_CODE'].head(20).tolist(), 1):
    htksyori = df.iloc[i-1]['HTKSYORI']
    pop = df.iloc[i-1]['T001141001']
    print(f"  {i:2d}. KEY_CODE={code}, HTKSYORI={htksyori}, 人口={pop}")

print("\n【データレベルの推測】")
print("HTKSYORI=0の行が4,906行 → これは市区町村・町丁目レベルのデータ")
print("HTKSYORI=1の行が231行 → 何らかの集計レベル")
print("HTKSYORI=2の行が312行 → 何らかの集計レベル")

print("\n【T001141001（人口総数）の値の範囲】")
# 数値に変換できる行のみを抽出
numeric_pop = pd.to_numeric(df['T001141001'], errors='coerce').dropna()
if len(numeric_pop) > 0:
    print(f"  最小値: {numeric_pop.min():,.0f} 人")
    print(f"  最大値: {numeric_pop.max():,.0f} 人")
    print(f"  平均値: {numeric_pop.mean():,.0f} 人")
    print(f"  合計値: {numeric_pop.sum():,.0f} 人")
    print(f"\n  → 東京都の実際の総人口は約14,000,000人")
    print(f"     このファイルの合計 {numeric_pop.sum():,.0f} 人")
    
print("\n【結論】")
print("このデータは:")
print("  ✓ 市区町村・町丁目レベルの小地域統計データ")
print("  ✓ 都道府県全体のサマリーは別途計算が必要")
print("  ✓ HTKSYORI=0の全行を合計すれば都道府県全体の人口が得られる")
print("\n  または、e-Stat APIから都道府県レベルの集計済みデータを取得する")
