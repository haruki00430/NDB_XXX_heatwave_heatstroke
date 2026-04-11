"""
e-Stat APIから都道府県別エアコン普及率をダウンロード

データソース: 2014年全国消費実態調査
統計表ID: 0003108733
フィルタ条件:
- tab=002: 普及率（％）
- cat02=07001: 二人以上の世帯
- cat03=00330: ルームエアコン
- area=01000-47000: 47都道府県
"""

import requests
import pandas as pd
from pathlib import Path
import time

# 設定
APP_ID = "8ee5a987b9ec70631de1977bde3afd7ebc11140d"
STAT_TABLE_ID = "0003108733"

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
print("e-Stat APIから都道府県別エアコン普及率をダウンロード")
print("=" * 80)
print(f"統計表ID: {STAT_TABLE_ID}")
print(f"データソース: 2014年全国消費実態調査")
print(f"対象: 二人以上の世帯、ルームエアコン普及率\n")

# 全都道府県のデータを収集
results = []

for pref_code, pref_name in PREF_CODES.items():
    print(f"取得中: {pref_name} ({pref_code})...", end="\r")

    params = {
        "appId": APP_ID,
        "statsDataId": STAT_TABLE_ID,
        "cdTab": "002",      # 普及率
        "cdCat02": "07001",  # 二人以上の世帯
        "cdCat03": "00330",  # ルームエアコン
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
                    aircon_prevalence = float(value)
                except:
                    aircon_prevalence = 0.0

                results.append({
                    "都道府県": pref_name,
                    "エアコン普及率": aircon_prevalence
                })

                print(f"  [OK] {pref_name}: {aircon_prevalence:.1f}%")
            else:
                print(f"  [データなし] {pref_name}")

        # API rate limit対策（1秒待機）
        time.sleep(1)

    except Exception as e:
        print(f"  [エラー] {pref_name}: {e}")

# DataFrame化
df_result = pd.DataFrame(results)

# 保存
output_path = OUTPUT_DIR / "aircon_prevalence_2014.csv"
df_result.to_csv(output_path, index=False, encoding='utf-8-sig')

print("\n" + "=" * 80)
print("集計結果")
print("=" * 80)
print(f"都道府県数: {len(df_result)}")
print(f"\nエアコン普及率 トップ10:")
print(df_result.nlargest(10, 'エアコン普及率')[['都道府県', 'エアコン普及率']])

print(f"\n[統計]")
print(f"  平均: {df_result['エアコン普及率'].mean():.2f}%")
print(f"  中央値: {df_result['エアコン普及率'].median():.2f}%")
print(f"  最大: {df_result['エアコン普及率'].max():.2f}% ({df_result.loc[df_result['エアコン普及率'].idxmax(), '都道府県']})")
print(f"  最小: {df_result['エアコン普及率'].min():.2f}% ({df_result.loc[df_result['エアコン普及率'].idxmin(), '都道府県']})")

print(f"\n[保存完了]")
print(f"出力ファイル: {output_path}")
print(f"データ件数: {len(df_result)} 都道府県")

print("\n" + "=" * 80)
print("抽出完了！")
print("=" * 80)
