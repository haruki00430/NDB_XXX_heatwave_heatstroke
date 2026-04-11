"""
e-Stat APIレスポンスのデバッグ
"""

import requests
import json

APP_ID = "8ee5a987b9ec70631de1977bde3afd7ebc11140d"
STAT_TABLE_ID = "0003445081"

url = "https://api.e-stat.go.jp/rest/3.0/app/json/getStatsData"

# まずフィルタなしで少量データを取得
params = {
    "appId": APP_ID,
    "statsDataId": STAT_TABLE_ID,
    "limit": 10  # 最初の10件のみ
}

print("=" * 80)
print("e-Stat APIレスポンスのデバッグ")
print("=" * 80)

try:
    response = requests.get(url, params=params, timeout=60)
    response.raise_for_status()

    data = response.json()

    # 保存
    with open("estat_response_debug.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("Response saved to: estat_response_debug.json")

    # データ構造を表示
    if "GET_STATS_DATA" in data:
        stats_data = data["GET_STATS_DATA"]["STATISTICAL_DATA"]

        # サンプルデータを表示
        if "DATA_INF" in stats_data:
            values = stats_data["DATA_INF"].get("VALUE", [])
            if not isinstance(values, list):
                values = [values]

            print(f"\n取得件数: {len(values)}")
            print("\n最初のデータサンプル:")
            for i, v in enumerate(values[:3], 1):
                print(f"\n[{i}]")
                print(json.dumps(v, indent=2, ensure_ascii=False))

except Exception as e:
    print(f"エラー: {e}")
    import traceback
    traceback.print_exc()
