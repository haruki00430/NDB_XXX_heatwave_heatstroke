"""
NDB医科診療行為データのヘッダー構造詳細確認
"""

import pandas as pd

# ファイルパス
b_file = r"C:\Users\user\.ag-cursor-common\research_workspace\projects\NDB_Research_Hub\02_Data\raw\NDB_OpenData\No.10\01_医科診療行為（算定回数）\01_公費レセプトを含まないデータ\B_医学管理等\診療月別算定回数.xlsx"

print("=" * 80)
print("B_医学管理等 / 診療月別算定回数.xlsx - ヘッダー構造詳細")
print("=" * 80)

# ヘッダーなしで最初の20行を読み込み（シート0を使用）
df = pd.read_excel(b_file, sheet_name=0, header=None, nrows=20)

print(f"\nShape: {df.shape}")
print(f"\n最初の20行:")
print(df.to_string())

# 診療行為コードを含む列を確認
print("\n" + "=" * 80)
print("診療行為コードの確認（列0の値）")
print("=" * 80)
print(df.iloc[:, 0].to_string())
