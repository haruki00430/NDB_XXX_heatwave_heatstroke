"""
e-Stat APIから都道府県別「65歳以上単独世帯数」をダウンロード（修正版）

統計表ID: 0003445181
フィルタ条件:
- cat01=0: 総数
- cat02=0: 世帯主の男女（総数）
- cat03=R2: 世帯主の年齢（65歳以上）
- cat04=1: 世帯人員が1人
"""

import requests
import pandas as pd
from pathlib import Path
import time

# 設定
APP_ID = "8ee5a987b9ec70631de1977bde3afd7ebc11140d"
STAT_TABLE_ID = "0003445181"

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "02_Data" / "interim"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# データ取得API
url = "https://api.e-stat.go.jp/rest/3.0/app/json/getStatsData"

# 都道府県コードマッピング
PREF_CODES = {
    "01000": "北海道", "02000": "青森県", "03000": "岩手県", "04000": "宮城県",
    "05000": "秋田県", "06000": "山形県", "07000": "福島県", "08000": "茨城県",
    "09000": "栃木県", "10000": "群馬県", "11000": "埼玉県", "12000": "千葉県",
    "13000": "東京都", "14000": "神奈川県", "15000": "新潟県", "16000": "富山県",
    "17000": "石川県", "18000": "福井県", "19000": "山梨県", "20000": "長野県",
    "21000": "岐阜県", "22000": "静岡県", "23000": "愛知県", "24000": "三重県",
    "25000": "滋賀県", "26000": "京都府", "27000": "大阪府", "28000": "兵庫県",
    "29000": "奈良県", "30000": "和歌山県", "31000": "鳥取県", "32000": "島根県",
    "33000": "岡山県", "34000": "広島県", "35000": "山口県", "36000": "徳島県",
    "37000": "香川県", "38000": "愛媛県", "39000": "高知県", "40000": "福岡県",
    "41000": "佐賀県", "42000": "長崎県", "43000": "熊本県", "44000": "大分県",
    "45000": "宮崎県", "46000": "鹿児島県", "47000": "沖縄県"
}

print("=" * 80)
print("e-Stat APIから65歳以上単独世帯数をダウンロード（修正版）")
print("=" * 80)
print(f"統計表ID: {STAT_TABLE_ID}")
print(f"フィルタ: 世帯主65歳以上 × 世帯人員1人\n")

# 全都道府県のデータを収集
results = []

for pref_code, pref_name in PREF_CODES.items():
    print(f"取得中: {pref_name} ({pref_code})...", end="\r")

    params = {
        "appId": APP_ID,
        "statsDataId": STAT_TABLE_ID,
        "cdCat01": "0",   # 総数
        "cdCat02": "0",   # 世帯主の男女（総数）
        "cdCat03": "R2",  # 世帯主の年齢（65歳以上）
        "cdCat04": "1",   # 世帯人員が1人
        "cdArea": pref_code,  # 都道府県コード
        "metaGetFlg": "N"
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()

        # データ抽出
        if "GET_STATS_DATA" in data and "STATISTICAL_DATA" in data["GET_STATS_DATA"]:
            stats_data = data["GET_STATS_DATA"]["STATISTICAL_DATA"]
            data_inf = stats_data.get("DATA_INF", {})
            values = data_inf.get("VALUE", [])

            if not isinstance(values, list):
                values = [values]

            if len(values) > 0:
                value = values[0].get("$", "0")
                try:
                    elderly_solo_households = int(value)
                except:
                    elderly_solo_households = 0

                results.append({
                    "都道府県": pref_name,
                    "65歳以上単独世帯数": elderly_solo_households
                })

                print(f"  [OK] {pref_name}: {elderly_solo_households:,}")
            else:
                print(f"  [データなし] {pref_name}")

        # API rate limit対策（1秒待機）
        time.sleep(1)

    except Exception as e:
        print(f"  [エラー] {pref_name}: {e}")

print("\n" + "=" * 80)
print("一般世帯総数を取得中...")
print("=" * 80)

# 既存のT001141から総世帯数を抽出
all_household_data = []
PREFECTURES = [
    '北海道', '青森県', '岩手県', '宮城県', '秋田県', '山形県', '福島県',
    '茨城県', '栃木県', '群馬県', '埼玉県', '千葉県', '東京都', '神奈川県',
    '新潟県', '富山県', '石川県', '福井県', '山梨県', '長野県',
    '岐阜県', '静岡県', '愛知県', '三重県',
    '滋賀県', '京都府', '大阪府', '兵庫県', '奈良県', '和歌山県',
    '鳥取県', '島根県', '岡山県', '広島県', '山口県',
    '徳島県', '香川県', '愛媛県', '高知県',
    '福岡県', '佐賀県', '長崎県', '熊本県', '大分県', '宮崎県', '鹿児島県', '沖縄県'
]

SOURCE_DIR = Path(r"C:\Users\user\SharedWorkspace\projects\NDB_Research_Hub\02_Data\raw\Statistics_Bureau\Census_2020")

for i, pref in enumerate(PREFECTURES, start=1):
    file_num = str(i).zfill(2)
    file_path = SOURCE_DIR / f"tblT001141H{file_num}.txt"

    df_census = pd.read_csv(file_path, encoding='cp932', skiprows=0, low_memory=False)
    df_data = df_census.iloc[1:].copy()

    # T001141035: 一般世帯数（総世帯数）
    df_data['T001141035'] = pd.to_numeric(df_data['T001141035'], errors='coerce')
    total_households = df_data['T001141035'].sum()

    all_household_data.append({
        '都道府県': pref,
        '総世帯数': int(total_households)
    })

    print(f"  {pref}: {int(total_households):,}")

# DataFrame化
df_result = pd.DataFrame(results)
df_households = pd.DataFrame(all_household_data)

# マージ
df_final = pd.merge(df_result, df_households, on='都道府県', how='inner')

# 高齢者単独世帯率を計算
df_final['高齢者単独世帯率'] = (df_final['65歳以上単独世帯数'] / df_final['総世帯数']) * 100

# 保存
output_path = OUTPUT_DIR / "elderly_solo_household_rate.csv"
df_final.to_csv(output_path, index=False, encoding='utf-8-sig')

print("\n" + "=" * 80)
print("集計結果")
print("=" * 80)
print(f"都道府県数: {len(df_final)}")
print(f"\n高齢者単独世帯率 トップ10:")
print(df_final.nlargest(10, '高齢者単独世帯率')[['都道府県', '高齢者単独世帯率']])

print(f"\n[統計]")
print(f"  平均: {df_final['高齢者単独世帯率'].mean():.2f}%")
print(f"  中央値: {df_final['高齢者単独世帯率'].median():.2f}%")
print(f"  最大: {df_final['高齢者単独世帯率'].max():.2f}% ({df_final.loc[df_final['高齢者単独世帯率'].idxmax(), '都道府県']})")
print(f"  最小: {df_final['高齢者単独世帯率'].min():.2f}% ({df_final.loc[df_final['高齢者単独世帯率'].idxmin(), '都道府県']})")

print(f"\n[保存完了]")
print(f"出力ファイル: {output_path}")
print(f"データ件数: {len(df_final)} 都道府県")

print("\n" + "=" * 80)
print("抽出完了！")
print("=" * 80)
