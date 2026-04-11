"""
e-Stat APIでエアコン普及率に関する統計表を検索
"""

import requests
import json

# e-Stat APIキー
APP_ID = "8ee5a987b9ec70631de1977bde3afd7ebc11140d"

# 統計表検索API
url = "https://api.e-stat.go.jp/rest/3.0/app/json/getStatsList"

# 複数のキーワードで検索
search_keywords = [
    "エアコン 都道府県",
    "エアーコンディショナー 都道府県",
    "冷房 普及率",
    "全国消費実態調査 エアコン"
]

print("=" * 80)
print("エアコン普及率統計表の検索")
print("=" * 80)

all_results = []

for keyword in search_keywords:
    print(f"\n検索キーワード: {keyword}")
    print("-" * 80)

    params = {
        "appId": APP_ID,
        "searchWord": keyword,
        "surveyYears": "2019-2020",  # 2019, 2020年
        "limit": 10
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()

        if "GET_STATS_LIST" in data and "DATALIST_INF" in data["GET_STATS_LIST"]:
            tables = data["GET_STATS_LIST"]["DATALIST_INF"].get("TABLE_INF", [])

            if not isinstance(tables, list):
                tables = [tables]

            print(f"検索結果: {len(tables)} 件")

            for i, table in enumerate(tables, 1):
                table_id = table.get('@id', 'N/A')
                title = table.get('TITLE', {}).get('$', 'N/A')
                stat_name = table.get('STAT_NAME', {}).get('$', 'N/A')
                survey_date = table.get('SURVEY_DATE', 'N/A')

                print(f"\n[{i}] {table_id}")
                print(f"    タイトル: {title}")
                print(f"    統計名: {stat_name}")
                print(f"    調査年月: {survey_date}")

                # ユニークなテーブルIDのみ保存
                if table_id not in [r['id'] for r in all_results]:
                    all_results.append({
                        'id': table_id,
                        'title': title,
                        'stat_name': stat_name,
                        'survey_date': survey_date
                    })
        else:
            print("検索結果なし")

    except Exception as e:
        print(f"エラー: {e}")

print("\n" + "=" * 80)
print("検索結果サマリー（重複除外）")
print("=" * 80)
print(f"ユニーク統計表数: {len(all_results)}\n")

for i, result in enumerate(all_results, 1):
    print(f"[{i}] {result['id']}")
    print(f"    {result['title']}")
    print(f"    統計名: {result['stat_name']}")
    print(f"    調査年月: {result['survey_date']}")
    print()

# 結果を保存
with open("aircon_search_results.json", "w", encoding="utf-8") as f:
    json.dump(all_results, f, indent=2, ensure_ascii=False)

print(f"検索結果を保存: aircon_search_results.json")
