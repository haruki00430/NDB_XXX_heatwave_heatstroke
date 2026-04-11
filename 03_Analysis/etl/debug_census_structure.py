"""
国勢調査データの構造デバッグ
"""

import pandas as pd

# 東京都のファイルを詳しく調査
file_path = r"C:\Users\user\SharedWorkspace\projects\NDB_Research_Hub\02_Data\raw\Statistics_Bureau\Census_2020\tblT001141H13.txt"

print("=" * 80)
print("国勢調査データ構造の詳細確認（東京都）")
print("=" * 80)

# データ型を指定せずに読み込み（文字列として）
df = pd.read_csv(file_path, encoding='cp932', dtype=str)

print(f"\n総行数: {len(df)}")
print(f"\nカラム数: {len(df.columns)}")

# HTKSYORIの値を確認
print(f"\nHTKSYORI列のユニーク値:")
print(df['HTKSYORI'].value_counts())

# HTKSYORI=0の行を確認
htksyori_0 = df[df['HTKSYORI'] == '0']
print(f"\nHTKSYORI=0の行数: {len(htksyori_0)}")

if len(htksyori_0) > 0:
    print(f"\nHTKSYORI=0の最初の5行:")
    print(htksyori_0.head()[['KEY_CODE', 'HTKSYORI', 'HTKSAKI', 'GASSAN', 'T001141001', 'T001141002', 'T001141003']])

# T001141001カラムの値を確認
print(f"\nT001141001（人口総数）の先頭10行:")
print(df['T001141001'].head(10).tolist())

# T001141001の文字列長を確認
df['pop_len'] = df['T001141001'].astype(str).str.len()
print(f"\nT001141001の最大文字列長: {df['pop_len'].max()}")
print(f"T001141001の最小文字列長: {df['pop_len'].min()}")
