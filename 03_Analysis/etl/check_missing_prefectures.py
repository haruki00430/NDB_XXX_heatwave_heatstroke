"""
欠落している都道府県を特定
"""

import pandas as pd
from pathlib import Path

# 47都道府県の完全リスト
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

# 現在のデータを読み込み
PROJECT_ROOT = Path(__file__).resolve().parents[2]
csv_path = PROJECT_ROOT / "02_Data" / "interim" / "prefecture_heatwave_summary.csv"

df = pd.read_csv(csv_path, encoding='utf-8-sig')

current_prefs = set(df['都道府県'].tolist())
all_prefs_set = set(ALL_PREFECTURES)

# 欠落している都道府県
missing = all_prefs_set - current_prefs

print(f"全都道府県数: {len(ALL_PREFECTURES)}")
print(f"現在のデータ: {len(current_prefs)} 都道府県")
print(f"欠落: {len(missing)} 都道府県\n")

if missing:
    print("欠落している都道府県:")
    for pref in sorted(missing):
        print(f"  - {pref}")
else:
    print("欠落なし（47都道府県すべて揃っています）")
