"""
国勢調査ファイルの実データ行を確認
"""

import pandas as pd

file_path = r"C:\Users\user\SharedWorkspace\projects\NDB_Research_Hub\02_Data\raw\Statistics_Bureau\Census_2020\tblT001141H01.txt"

print("=" * 80)
print("北海道（H01）のデータ行を確認")
print("=" * 80)

# skiprows=0 で読み込み
df = pd.read_csv(file_path, encoding='cp932', skiprows=0)

print(f"\n形状: {df.shape}")
print(f"行数: {len(df)}")

# 最初の10行を表示
print(f"\n最初の10行:")
for i in range(min(10, len(df))):
    key_code = df['KEY_CODE'].iloc[i]
    total_households = df['T001141038'].iloc[i]
    elderly_solo = df['T001141050'].iloc[i]
    print(f"行{i}: KEY_CODE={key_code}, 総世帯数={total_households}, 65歳以上単独={elderly_solo}")

# KEY_CODEの値をチェック
print(f"\n\nKEY_CODEの一意な値（最初の20個）:")
unique_keys = df['KEY_CODE'].unique()[:20]
for key in unique_keys:
    print(f"  {key}")

# 都道府県全体のデータを探す（KEY_CODEが都道府県コードのみの行）
print(f"\n\n都道府県全体データの候補:")
for i in range(len(df)):
    key_code = str(df['KEY_CODE'].iloc[i])
    # 都道府県全体は特定のコード（01 for 北海道）
    if len(key_code) == 8 and key_code.endswith('0000'):
        total_households = df['T001141038'].iloc[i]
        elderly_solo = df['T001141050'].iloc[i]
        print(f"  行{i}: KEY_CODE={key_code}, 総世帯数={total_households}, 65歳以上単独={elderly_solo}")
