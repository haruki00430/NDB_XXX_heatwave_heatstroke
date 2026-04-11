"""
都道府県別算定回数データの構造確認
"""

import pandas as pd

# ファイルパス
b_pref_file = r"C:\Users\user\.ag-cursor-common\research_workspace\projects\NDB_Research_Hub\02_Data\raw\NDB_OpenData\No.10\01_医科診療行為（算定回数）\01_公費レセプトを含まないデータ\B_医学管理等\都道府県別算定回数.xlsx"
g_pref_file = r"C:\Users\user\.ag-cursor-common\research_workspace\projects\NDB_Research_Hub\02_Data\raw\NDB_OpenData\No.10\01_医科診療行為（算定回数）\01_公費レセプトを含まないデータ\G_注射\都道府県別算定回数.xlsx"

print("=" * 80)
print("B_医学管理等 / 都道府県別算定回数.xlsx - 構造確認")
print("=" * 80)

# シート名を確認
b_sheets = pd.ExcelFile(b_pref_file).sheet_names
print(f"シート名: {b_sheets}")

# 最初のシートのヘッダー構造を確認
df_b = pd.read_excel(b_pref_file, sheet_name=0, header=None, nrows=20)
print(f"\nShape: {df_b.shape}")
print(f"\n最初の20行（列0-10のみ）:")
print(df_b.iloc[:, :11].to_string())

print("\n" + "=" * 80)
print("G_注射 / 都道府県別算定回数.xlsx - 構造確認")
print("=" * 80)

g_sheets = pd.ExcelFile(g_pref_file).sheet_names
print(f"シート名: {g_sheets}")

df_g = pd.read_excel(g_pref_file, sheet_name=0, header=None, nrows=20)
print(f"\nShape: {df_g.shape}")
print(f"\n最初の20行（列0-10のみ）:")
print(df_g.iloc[:, :11].to_string())
