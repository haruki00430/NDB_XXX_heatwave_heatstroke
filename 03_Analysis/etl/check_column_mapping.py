"""
T001141のカラム対応を確認
"""

import pandas as pd

file_path = r"C:\Users\user\SharedWorkspace\projects\NDB_Research_Hub\02_Data\raw\Statistics_Bureau\Census_2020\tblT001141H01.txt"

# skiprows=0で読み込み
df = pd.read_csv(file_path, encoding='cp932', skiprows=0, low_memory=False)

print("=" * 80)
print("カラム対応確認")
print("=" * 80)

# 1行目：カラムコード
# 2行目（index=0）：日本語カラム名
print("\nカラムコード → 日本語名:")
for i, (col_code, col_name_jp) in enumerate(zip(df.columns, df.iloc[0])):
    if 'T001141' in str(col_code):
        print(f"  {col_code}: {col_name_jp}")

# 特に注目すべきカラム
target_cols = ['T001141037', 'T001141038', 'T001141039', 'T001141049', 'T001141050']
print(f"\n\n注目カラムの詳細:")
for col in target_cols:
    if col in df.columns:
        col_name = df[col].iloc[0]
        # 北海道全体（全行の合計）
        total_value = pd.to_numeric(df[col].iloc[1:], errors='coerce').sum()
        print(f"{col}: {col_name}")
        print(f"  北海道合計: {int(total_value):,}")
        print()
