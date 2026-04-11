"""
e-Stat APIで「65歳以上単独世帯」に関する統計表を検索
"""

import requests
import json

# e-Stat APIキー
APP_ID = "8ee5a987b9ec70631de1977bde3afd7ebc11140d"

# 統計表検索API
url = "https://api.e-stat.go.jp/rest/3.0/app/json/getStatsList"

params = {
    "appId": APP_ID,
    "searchWord": "65歳以上 単独世帯",  # 検索キーワード
    "surveyYears": "2020",  # 2020年国勢調査
    "limit": 20  # 最大20件
}

print("=" * 80)
print("e-Stat APIで統計表を検索中...")
print("=" * 80)
print(f"検索キーワード: {params['searchWord']}")
print(f"調査年: {params['surveyYears']}\n")

try:
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    data = response.json()

    # 結果の表示
    if "GET_STATS_LIST" in data and "DATALIST_INF" in data["GET_STATS_LIST"]:
        tables = data["GET_STATS_LIST"]["DATALIST_INF"]["TABLE_INF"]

        if not isinstance(tables, list):
            tables = [tables]

        print(f"検索結果: {len(tables)} 件\n")

        for i, table in enumerate(tables, 1):
            print(f"[{i}] {table.get('@id', 'N/A')}")
            print(f"    タイトル: {table.get('TITLE', {}).get('$', 'N/A')}")
            print(f"    統計名: {table.get('STAT_NAME', {}).get('$', 'N/A')}")
            print(f"    調査年月: {table.get('SURVEY_DATE', 'N/A')}")
            print()
    else:
        print("検索結果なし")
        print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")

except Exception as e:
    print(f"エラー: {e}")
    import traceback
    traceback.print_exc()
