"""
輸液のコードを検索
"""

import pandas as pd

# ファイルパス
g_file = r"C:\Users\user\.ag-cursor-common\research_workspace\projects\NDB_Research_Hub\02_Data\raw\NDB_OpenData\No.10\01_医科診療行為（算定回数）\01_公費レセプトを含まないデータ\G_注射\診療月別算定回数.xlsx"

print("=" * 80)
print("輸液のコード検索")
print("=" * 80)

# データを読み込み（header=2でカラム名を取得、行3をスキップ）
df = pd.read_excel(g_file, sheet_name=0, header=2, skiprows=[3])

# 表示カラムを事前に定義
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

# 「輸液」または「点滴」を含む行を検索
infusion_mask = df.iloc[:, 3].astype(str).str.contains('輸液|点滴', na=False, regex=True)
infusion_df = df[infusion_mask]

print(f"\n「輸液」を含む診療行為数: {len(infusion_df)}\n")

if len(infusion_df) > 0:
    # 関連するカラムのみを表示（最初の20件）
    print(infusion_df[display_cols].head(20).to_string())

    if len(infusion_df) > 20:
        print(f"\n... 他 {len(infusion_df) - 20} 件")
else:
    print("「輸液」を含む診療行為が見つかりませんでした")

# G002で始まる分類コードも確認
print("\n" + "=" * 80)
print("G002で始まる分類コード")
print("=" * 80)

g002_mask = df.iloc[:, 0].astype(str).str.startswith('G002', na=False)
g002_df = df[g002_mask]

print(f"\nG002で始まる分類数: {len(g002_df)}\n")
if len(g002_df) > 0:
    print(g002_df[display_cols].head(20).to_string())
