"""
47都道府県の気象データを正しいコードで再ダウンロード

修正内容:
- 島根県: prec_no 70 → 68
- 山口県: prec_no 68, block_no 47784 → prec_no 81, block_no 47762
- 愛媛県: block_no 47893 → 47887
- 高知県: block_no 47887 → 47893
- 佐賀県: prec_no 81 → 85
- 大分県: prec_no 85 → 83
- html5lib を使用
"""

import pandas as pd
import requests
from time import sleep
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "02_Data" / "raw" / "jma_weather"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 47都道府県の正しい気象台コード（修正版）
PREFECTURE_STATIONS = {
    '北海道': {'prec_no': 14, 'block_no': 47412, 'station_name': '札幌'},
    '青森県': {'prec_no': 31, 'block_no': 47575, 'station_name': '青森'},
    '岩手県': {'prec_no': 33, 'block_no': 47584, 'station_name': '盛岡'},
    '宮城県': {'prec_no': 34, 'block_no': 47590, 'station_name': '仙台'},
    '秋田県': {'prec_no': 32, 'block_no': 47582, 'station_name': '秋田'},
    '山形県': {'prec_no': 35, 'block_no': 47588, 'station_name': '山形'},
    '福島県': {'prec_no': 36, 'block_no': 47595, 'station_name': '福島'},
    '茨城県': {'prec_no': 40, 'block_no': 47629, 'station_name': '水戸'},
    '栃木県': {'prec_no': 41, 'block_no': 47615, 'station_name': '宇都宮'},
    '群馬県': {'prec_no': 42, 'block_no': 47624, 'station_name': '前橋'},
    '埼玉県': {'prec_no': 43, 'block_no': 47626, 'station_name': 'さいたま'},
    '千葉県': {'prec_no': 45, 'block_no': 47682, 'station_name': '千葉'},
    '東京都': {'prec_no': 44, 'block_no': 47662, 'station_name': '東京'},
    '神奈川県': {'prec_no': 46, 'block_no': 47670, 'station_name': '横浜'},
    '新潟県': {'prec_no': 54, 'block_no': 47604, 'station_name': '新潟'},
    '富山県': {'prec_no': 55, 'block_no': 47607, 'station_name': '富山'},
    '石川県': {'prec_no': 56, 'block_no': 47605, 'station_name': '金沢'},
    '福井県': {'prec_no': 57, 'block_no': 47616, 'station_name': '福井'},
    '山梨県': {'prec_no': 49, 'block_no': 47638, 'station_name': '甲府'},
    '長野県': {'prec_no': 48, 'block_no': 47610, 'station_name': '長野'},
    '岐阜県': {'prec_no': 52, 'block_no': 47632, 'station_name': '岐阜'},
    '静岡県': {'prec_no': 50, 'block_no': 47656, 'station_name': '静岡'},
    '愛知県': {'prec_no': 51, 'block_no': 47636, 'station_name': '名古屋'},
    '三重県': {'prec_no': 53, 'block_no': 47651, 'station_name': '津'},
    '滋賀県': {'prec_no': 60, 'block_no': 47761, 'station_name': '彦根'},
    '京都府': {'prec_no': 61, 'block_no': 47759, 'station_name': '京都'},
    '大阪府': {'prec_no': 62, 'block_no': 47772, 'station_name': '大阪'},
    '兵庫県': {'prec_no': 63, 'block_no': 47770, 'station_name': '神戸'},
    '奈良県': {'prec_no': 64, 'block_no': 47780, 'station_name': '奈良'},
    '和歌山県': {'prec_no': 65, 'block_no': 47777, 'station_name': '和歌山'},
    '鳥取県': {'prec_no': 69, 'block_no': 47746, 'station_name': '鳥取'},
    '島根県': {'prec_no': 68, 'block_no': 47741, 'station_name': '松江'},  # 修正: 70 → 68
    '岡山県': {'prec_no': 66, 'block_no': 47768, 'station_name': '岡山'},
    '広島県': {'prec_no': 67, 'block_no': 47765, 'station_name': '広島'},
    '山口県': {'prec_no': 81, 'block_no': 47762, 'station_name': '下関'},  # 修正: 68, 47784 → 81, 47762
    '徳島県': {'prec_no': 71, 'block_no': 47895, 'station_name': '徳島'},
    '香川県': {'prec_no': 72, 'block_no': 47891, 'station_name': '高松'},
    '愛媛県': {'prec_no': 73, 'block_no': 47887, 'station_name': '松山'},  # 修正: 47893 → 47887
    '高知県': {'prec_no': 74, 'block_no': 47893, 'station_name': '高知'},  # 修正: 47887 → 47893
    '福岡県': {'prec_no': 82, 'block_no': 47807, 'station_name': '福岡'},
    '佐賀県': {'prec_no': 85, 'block_no': 47813, 'station_name': '佐賀'},  # 修正: 81 → 85
    '長崎県': {'prec_no': 84, 'block_no': 47817, 'station_name': '長崎'},
    '熊本県': {'prec_no': 86, 'block_no': 47819, 'station_name': '熊本'},
    '大分県': {'prec_no': 83, 'block_no': 47815, 'station_name': '大分'},  # 修正: 85 → 83
    '宮崎県': {'prec_no': 87, 'block_no': 47830, 'station_name': '宮崎'},
    '鹿児島県': {'prec_no': 88, 'block_no': 47827, 'station_name': '鹿児島'},
    '沖縄県': {'prec_no': 91, 'block_no': 47936, 'station_name': '那覇'},
}


def download_daily_temperature(prec_no, block_no, year, month):
    """気象庁から日別気温データをダウンロード"""
    url = "https://www.data.jma.go.jp/obd/stats/etrn/view/daily_s1.php"
    params = {
        'prec_no': prec_no,
        'block_no': block_no,
        'year': year,
        'month': month,
        'day': '',
        'view': ''
    }

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Research Project: NDB Heatwave Analysis)'
        }
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()

        # html5libを明示的に使用
        dfs = pd.read_html(response.content, encoding='utf-8', flavor='html5lib')

        if len(dfs) < 1:
            print(f"  [警告] データテーブルが見つかりません")
            return None

        df = dfs[0]
        return df

    except Exception as e:
        print(f"  [エラー] {e}")
        return None


print("=" * 80)
print("47都道府県 気象データ再ダウンロード（正しいコード）")
print("=" * 80)

all_daily_data = []
success_count = 0
fail_count = 0
failed_prefs = []

for pref, info in PREFECTURE_STATIONS.items():
    print(f"\n処理中: {pref} ({info['station_name']})")
    print(f"  prec_no={info['prec_no']}, block_no={info['block_no']}")

    pref_success = True

    # 2023年6-9月の日別データ
    for month in [6, 7, 8, 9]:
        print(f"  {month}月...", end="")
        df_daily = download_daily_temperature(
            prec_no=info['prec_no'],
            block_no=info['block_no'],
            year=2023,
            month=month
        )

        if df_daily is not None:
            # カラム名を設定
            df_daily.columns = [
                '日', '気圧現地', '気圧海面', '降水量合計', '降水量最大1h', '降水量最大10m',
                '気温平均', '気温最高', '気温最低', '湿度平均', '湿度最小',
                '風速平均', '風速最大', '風向最大', '瞬間風速最大', '瞬間風向最大',
                '日照時間', '降雪', '積雪', '天気昼', '天気夜'
            ]

            # メタデータを追加
            df_daily['都道府県'] = pref
            df_daily['観測所'] = info['station_name']
            df_daily['年'] = 2023
            df_daily['月'] = month

            all_daily_data.append(df_daily)
            print(f" [OK] {len(df_daily)}行")
        else:
            print(f" [ERROR]")
            pref_success = False

        sleep(1)

    if pref_success:
        success_count += 1
    else:
        fail_count += 1
        failed_prefs.append(pref)

# データ統合
print("\n" + "=" * 80)
print("ダウンロード結果")
print("=" * 80)
print(f"成功: {success_count} 都道府県")
print(f"失敗: {fail_count} 都道府県")

if failed_prefs:
    print(f"\n失敗した都道府県:")
    for pref in failed_prefs:
        print(f"  - {pref}")

if all_daily_data:
    df_all = pd.concat(all_daily_data, ignore_index=True)

    print(f"\n[データ統合]")
    print(f"総行数: {len(df_all)}")
    print(f"都道府県数: {len(df_all['都道府県'].unique())}")

    # 都道府県ごとの行数を確認
    print(f"\n[都道府県別行数]")
    for pref in sorted(df_all['都道府県'].unique()):
        count = len(df_all[df_all['都道府県'] == pref])
        print(f"  {pref}: {count}行")

    # 保存
    output_path = OUTPUT_DIR / "jma_daily_temperature_2023_summer.csv"
    df_all.to_csv(output_path, index=False, encoding='utf-8-sig')

    print(f"\n[保存完了]")
    print(f"出力ファイル: {output_path}")

else:
    print("\n[ERROR] データ取得失敗")

print("\n" + "=" * 80)
print("再ダウンロード完了！")
print("=" * 80)
