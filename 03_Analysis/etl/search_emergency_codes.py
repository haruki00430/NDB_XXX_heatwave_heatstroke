"""
救急医療管理加算のコードを検索
"""

import pandas as pd

# ファイルパス
b_file = r"C:\Users\user\.ag-cursor-common\research_workspace\projects\NDB_Research_Hub\02_Data\raw\NDB_OpenData\No.10\01_医科診療行為（算定回数）\01_公費レセプトを含まないデータ\B_医学管理等\診療月別算定回数.xlsx"

print("=" * 80)
print("救急医療管理加算のコード検索")
print("=" * 80)

# データを読み込み（header=2でカラム名を取得、行3をスキップ）
df = pd.read_excel(b_file, sheet_name=0, header=2, skiprows=[3])

# 「救急」を含む行を検索
emergency_mask = df.iloc[:, 3].astype(str).str.contains('救急', na=False)
emergency_df = df[emergency_mask]

print(f"\n「救急」を含む診療行為数: {len(emergency_df)}\n")

if len(emergency_df) > 0:
    # 関連するカラムのみを表示
    display_cols = [
        df.columns[0],  # 分類コード
        df.columns[1],  # 分類名称
        df.columns[2],  # 診療行為コード
        df.columns[3],  # 診療行為名称
        df.columns[4],  # 点数
        df.columns[5],  # 総計
        df.columns[8],  # 6月
        df.columns[9],  # 7月
        df.columns[10], # 8月
        df.columns[11]  # 9月
    ]

    print(emergency_df[display_cols].to_string())
else:
    print("「救急」を含む診療行為が見つかりませんでした")

# 分類コードにB001を含む行も確認
print("\n" + "=" * 80)
print("B001で始まる分類コード")
print("=" * 80)

b001_mask = df.iloc[:, 0].astype(str).str.startswith('B001', na=False)
b001_df = df[b001_mask]

print(f"\nB001で始まる分類数: {len(b001_df)}\n")
if len(b001_df) > 0:
    print(b001_df[display_cols].to_string())
