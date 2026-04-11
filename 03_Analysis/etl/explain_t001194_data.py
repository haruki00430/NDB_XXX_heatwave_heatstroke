"""
tblT001194データの詳細説明
"""

import pandas as pd

file_path = r"C:\Users\user\SharedWorkspace\projects\NDB_Research_Hub\02_Data\raw\Statistics_Bureau\Census_2020\tblT001194H13.txt"

print("=" * 80)
print("tblT001194データの内容（東京都の例）")
print("=" * 80)

# ヘッダーを確認
with open(file_path, 'r', encoding='cp932') as f:
    # 1行目: カラムコード
    line1 = f.readline().strip()
    # 2行目: カラム名
    line2 = f.readline().strip()

print("\n【カラム名】（2行目から抽出）")
columns = line2.split(',')
for i, col in enumerate(columns[:25], 1):
    print(f"  {i:2d}. {col}")

# データ読み込み
df = pd.read_csv(file_path, encoding='cp932', dtype=str)

print(f"\n【データ構造】")
print(f"  総行数: {len(df):,} 行")
print(f"  カラム数: {len(df.columns)}")

print(f"\n【HTKSYORI列の分布】")
htksyori_counts = df['HTKSYORI'].value_counts()
print(htksyori_counts)

print(f"\n【データの意味】")
print("tblT001194は「住宅データ」:")
print("  - 住宅の種類（持ち家、借家、給与住宅など）")
print("  - 建物の種類（一戸建、長屋建、共同住宅）")
print("  - 共同住宅の階層（1-2階建、3-5階建、6-10階建など）")
print("  - 居住階（何階に住んでいるか）")
print("\ntblT001141は「人口・世帯データ」:")
print("  - 人口（総数、男女別、年齢階級別）")
print("  - 世帯数（1人世帯、2人世帯、高齢単身世帯など）")

print("\n【熱中症研究での利用可能性】")
print("[tblT001194の利用]")
print("  + 共同住宅の階層データ → 高層階の熱環境リスク")
print("  + 持ち家 vs 借家 → エアコン設置率の差")
print("  - ただし、今回の分析では不要（エアコン普及率は既に取得済み）")
print("\n[tblT001141の利用]")
print("  + 総人口データ → 人口10万人あたりの標準化に必須")
