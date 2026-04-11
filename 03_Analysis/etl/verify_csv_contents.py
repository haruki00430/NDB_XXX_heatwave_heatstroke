"""
CSVファイルの内容を検証
"""

import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CSV_PATH = PROJECT_ROOT / "02_Data" / "raw" / "jma_weather" / "jma_daily_temperature_2023_summer.csv"

print("=" * 80)
print("CSVファイル内容検証")
print("=" * 80)

# CSVを読み込み
df = pd.read_csv(CSV_PATH, encoding='utf-8-sig')

print(f"\n[基本情報]")
print(f"ファイル: {CSV_PATH}")
print(f"形状: {df.shape}")
print(f"カラム数: {len(df.columns)}")

# カラム名を表示
print(f"\n[カラム名]")
for i, col in enumerate(df.columns):
    print(f"  {i}: {col}")

# 都道府県カラムの確認
if '都道府県' in df.columns:
    print(f"\n[都道府県統計]")
    print(f"総行数: {len(df)}")
    print(f"都道府県カラムの欠損値: {df['都道府県'].isna().sum()} 行")
    print(f"都道府県の種類数: {len(df['都道府県'].dropna().unique())}")

    print(f"\n[都道府県リスト]")
    prefs = sorted(df['都道府県'].dropna().unique())
    for pref in prefs:
        count = len(df[df['都道府県'] == pref])
        print(f"  - {pref}: {count} 行")

    # 47都道府県リストと比較
    ALL_PREFECTURES = [
        '北海道', '青森県', '岩手県', '宮城県', '秋田県', '山形県', '福島県',
        '茨城県', '栃木県', '群馬県', '埼玉県', '千葉県', '東京都', '神奈川県',
        '新潟県', '富山県', '石川県', '福井県', '山梨県', '長野県',
        '岐阜県', '静岡県', '愛知県', '三重県',
        '滋賀県', '京都府', '大阪府', '兵庫県', '奈良県', '和歌山県',
        '鳥取県', '島根県', '岡山県', '広島県', '山口県',
        '徳島県', '香川県', '愛媛県', '高知県',
        '福岡県', '佐賀県', '長崎県', '熊本県', '大分県', '宮崎県', '鹿児島県', '沖縄県'
    ]

    current_prefs = set(prefs)
    all_prefs_set = set(ALL_PREFECTURES)
    missing = all_prefs_set - current_prefs

    print(f"\n[欠落している都道府県]")
    if missing:
        print(f"欠落数: {len(missing)}")
        for pref in sorted(missing):
            print(f"  - {pref}")
    else:
        print("なし（47都道府県すべて揃っています）")

else:
    print(f"\n[エラー] '都道府県'カラムが見つかりません")

print("\n" + "=" * 80)
