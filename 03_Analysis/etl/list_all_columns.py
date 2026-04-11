"""
国勢調査T001141の全カラムをリスト表示
"""

import pandas as pd

file_path = r"C:\Users\user\SharedWorkspace\projects\NDB_Research_Hub\02_Data\raw\Statistics_Bureau\Census_2020\tblT001141H01.txt"

print("=" * 80)
print("T001141 全カラムリスト（北海道）")
print("=" * 80)

# skiprows=0で読み込み（カラムコードがヘッダーになる）
df = pd.read_csv(file_path, encoding='cp932', skiprows=0, low_memory=False)

print(f"\n総カラム数: {len(df.columns)}")
print(f"\nカラムコード → 日本語名 → 北海道合計値:\n")

# T001141で始まるカラムのみ表示
for col in df.columns:
    if 'T001141' in str(col):
        col_name_jp = df[col].iloc[0]  # 日本語名（行1）

        # 数値に変換して合計（行2以降）
        values = pd.to_numeric(df[col].iloc[1:], errors='coerce')
        total = values.sum()

        print(f"{col}: {col_name_jp}")
        print(f"  北海道合計: {int(total):,}")
        print()
