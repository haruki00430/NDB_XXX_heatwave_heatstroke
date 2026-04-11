"""
国勢調査2020年の総人口データを検索
"""

import requests
import json

APP_ID = "8ee5a987b9ec70631de1977bde3afd7ebc11140d"

url = "https://api.e-stat.go.jp/rest/3.0/app/json/getStatsList"

params = {
    "appId": APP_ID,
    "searchWord": "国勢調査 2020 人口",
    "surveyYears": "2020",
    "limit": 20
}

response = requests.get(url, params=params, timeout=60)
data = response.json()

if "GET_STATS_LIST" in data and "DATALIST_INF" in data["GET_STATS_LIST"]:
    tables = data["GET_STATS_LIST"]["DATALIST_INF"].get("TABLE_INF", [])
    
    if not isinstance(tables, list):
        tables = [tables]
    
    print(f"検索結果: {len(tables)} 件\n")
    
    for i, table in enumerate(tables[:10], 1):
        table_id = table.get("@id", "N/A")
        title = table.get("TITLE", {}).get("$", "N/A")
        
        print(f"[{i}] {table_id}")
        print(f"    {title[:100]}...")
        print()
else:
    print("検索結果なし")
