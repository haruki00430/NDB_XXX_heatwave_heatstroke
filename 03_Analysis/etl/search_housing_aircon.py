"""
住宅統計からエアコン関連データを検索
"""

import requests
import json

APP_ID = "8ee5a987b9ec70631de1977bde3afd7ebc11140d"

url = "https://api.e-stat.go.jp/rest/3.0/app/json/getStatsList"

# 住宅統計（年次指定なし）
params = {
    "appId": APP_ID,
    "searchWord": "住宅 エアコン",
    "limit": 30
}

response = requests.get(url, params=params, timeout=30)
data = response.json()

results = []

if "GET_STATS_LIST" in data and "DATALIST_INF" in data["GET_STATS_LIST"]:
    tables = data["GET_STATS_LIST"]["DATALIST_INF"].get("TABLE_INF", [])
    if not isinstance(tables, list):
        tables = [tables]

    print(f"検索結果: {len(tables)} 件\n")

    for i, table in enumerate(tables, 1):
        table_id = table.get("@id", "N/A")
        title = table.get("TITLE", {}).get("$", "N/A")
        stat_name = table.get("STAT_NAME", {}).get("$", "N/A")
        survey_date = table.get("SURVEY_DATE", "N/A")

        results.append({
            "id": table_id,
            "title": title,
            "stat_name": stat_name,
            "survey_date": survey_date
        })

        print(f"[{i}] {table_id}")
        print(f"    タイトル: {title[:100]}...")
        print(f"    統計名: {stat_name[:60]}...")
        print(f"    調査年月: {survey_date}")
        print()

    # 結果を保存
    with open("housing_aircon_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"結果を保存: housing_aircon_results.json")
else:
    print("検索結果なし")
