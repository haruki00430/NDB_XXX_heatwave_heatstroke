"""
e-Stat APIで統計表のメタデータを取得
"""

import requests
import json

# e-Stat APIキー
APP_ID = "8ee5a987b9ec70631de1977bde3afd7ebc11140d"

# 統計表ID（検索結果の1番目）
STAT_TABLE_ID = "0003445102"

# メタデータ取得API
url = "https://api.e-stat.go.jp/rest/3.0/app/json/getMetaInfo"

params = {
    "appId": APP_ID,
    "statsDataId": STAT_TABLE_ID
}

print("=" * 80)
print(f"統計表メタデータ取得: {STAT_TABLE_ID}")
print("=" * 80)

try:
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    data = response.json()

    # メタデータの保存（デバッグ用）
    output_file = f"estat_metadata_{STAT_TABLE_ID}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\nメタデータを保存: {output_file}")

    # 主要な分類項目を表示
    if "GET_META_INFO" in data and "METADATA_INF" in data["GET_META_INFO"]:
        metadata = data["GET_META_INFO"]["METADATA_INF"]

        # CLASS_INFに分類情報がある
        if "CLASS_INF" in metadata:
            class_inf = metadata["CLASS_INF"]

            print("\n主要な分類項目:")
            for i, cls in enumerate(class_inf.get("CLASS_OBJ", []), 1):
                print(f"\n[{i}] {cls.get('@id', 'N/A')} - {cls.get('@name', 'N/A')}")

                # 分類値を表示（最初の10個）
                classes = cls.get("CLASS", [])
                if not isinstance(classes, list):
                    classes = [classes]

                for j, c in enumerate(classes[:10], 1):
                    print(f"    {c.get('@code', 'N/A')}: {c.get('@name', 'N/A')}")

                if len(classes) > 10:
                    print(f"    ... 他 {len(classes) - 10} 件")

    print(f"\n詳細はJSONファイルを参照: {output_file}")

except Exception as e:
    print(f"エラー: {e}")
    import traceback
    traceback.print_exc()
