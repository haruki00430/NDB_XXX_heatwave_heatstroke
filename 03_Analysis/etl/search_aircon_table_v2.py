"""
e-Stat APIでエアコン普及率に関する統計表を検索（年次範囲拡大版）
"""

import requests
import json

# e-Stat APIキー
APP_ID = "8ee5a987b9ec70631de1977bde3afd7ebc11140d"

# 統計表検索API
url = "https://api.e-stat.go.jp/rest/3.0/app/json/getStatsList"

# 複数のキーワードで検索（年次制限なし）
search_keywords = [
    "ルームエアコン",
    "エアコンディショナー",
    "冷房設備",
    "全国消費実態調査",
    "全国家計構造調査",
    "住宅・土地統計調査 冷房"
]

print("=" * 80)
print("エアコン普及率統計表の検索（年次範囲拡大版）")
print("=" * 80)

all_results = []

for keyword in search_keywords:
    print(f"\n検索キーワード: {keyword}")
    print("-" * 80)

    params = {
        "appId": APP_ID,
        "searchWord": keyword,
        "limit": 20  # 20件まで取得
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

            for i, table in enumerate(tables[:5], 1):  # 最初の5件のみ表示
                table_id = table.get('@id', 'N/A')
                title = table.get('TITLE', {}).get('$', 'N/A')
                stat_name = table.get('STAT_NAME', {}).get('$', 'N/A')
                survey_date = table.get('SURVEY_DATE', 'N/A')

                print(f"\n[{i}] {table_id}")
                print(f"    タイトル: {title[:80]}...")
                print(f"    統計名: {stat_name[:60]}...")
                print(f"    調査年月: {survey_date}")

                # ユニークなテーブルIDのみ保存
                if table_id not in [r['id'] for r in all_results]:
                    all_results.append({
                        'id': table_id,
                        'title': title,
                        'stat_name': stat_name,
                        'survey_date': survey_date
                    })

            if len(tables) > 5:
                print(f"\n... 他 {len(tables) - 5} 件")
        else:
            print("検索結果なし")

    except Exception as e:
        print(f"エラー: {e}")

print("\n" + "=" * 80)
print("検索結果サマリー（重複除外）")
print("=" * 80)
print(f"ユニーク統計表数: {len(all_results)}\n")

# 都道府県別データを含む候補を優先表示
priority_results = [r for r in all_results if '都道府県' in r['title'] or '県' in r['title']]

print("【都道府県別データを含む候補】")
for i, result in enumerate(priority_results[:10], 1):
    print(f"[{i}] {result['id']}")
    print(f"    {result['title'][:100]}...")
    print(f"    統計名: {result['stat_name'][:60]}...")
    print(f"    調査年月: {result['survey_date']}")
    print()

# 結果を保存
with open("aircon_search_results_v2.json", "w", encoding="utf-8") as f:
    json.dump(all_results, f, indent=2, ensure_ascii=False)

print(f"検索結果を保存: aircon_search_results_v2.json")
print(f"全結果数: {len(all_results)} 件")
