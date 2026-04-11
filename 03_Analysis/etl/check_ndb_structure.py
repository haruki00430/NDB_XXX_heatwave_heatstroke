"""
NDB医科診療行為データの構造確認スクリプト
"""

import pandas as pd

# ファイルパス（直接指定）
b_file = r"C:\Users\user\.ag-cursor-common\research_workspace\projects\NDB_Research_Hub\02_Data\raw\NDB_OpenData\No.10\01_医科診療行為（算定回数）\01_公費レセプトを含まないデータ\B_医学管理等\診療月別算定回数.xlsx"
g_file = r"C:\Users\user\.ag-cursor-common\research_workspace\projects\NDB_Research_Hub\02_Data\raw\NDB_OpenData\No.10\01_医科診療行為（算定回数）\01_公費レセプトを含まないデータ\G_注射\診療月別算定回数.xlsx"

print("=" * 80)
print("B_医学管理等 / 診療月別算定回数.xlsx")
print("=" * 80)

# 最初の10行を読み込み（ヘッダー構造を確認）
df_b = pd.read_excel(b_file, nrows=10)
print(f"\nShape: {df_b.shape}")
print(f"\nColumns:\n{df_b.columns.tolist()}")
print(f"\nFirst 10 rows:\n{df_b}")

print("\n" + "=" * 80)
print("G_注射 / 診療月別算定回数.xlsx")
print("=" * 80)

df_g = pd.read_excel(g_file, nrows=10)
print(f"\nShape: {df_g.shape}")
print(f"\nColumns:\n{df_g.columns.tolist()}")
print(f"\nFirst 10 rows:\n{df_g}")

# シート名を確認
print("\n" + "=" * 80)
print("シート名の確認")
print("=" * 80)

b_sheets = pd.ExcelFile(b_file).sheet_names
g_sheets = pd.ExcelFile(g_file).sheet_names

print(f"\nB_医学管理等のシート: {b_sheets}")
print(f"G_注射のシート: {g_sheets}")
