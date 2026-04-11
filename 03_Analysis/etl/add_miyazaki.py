"""
宮崎県のデータをダウンロードして追加
"""

import pandas as pd
import requests
from time import sleep
from pathlib import Path

# プロジェクトルートディレクトリ
PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "02_Data" / "raw" / "jma_weather"

# 宮崎県の気象台コード
MIYAZAKI = {'prec_no': 87, 'block_no': 47830, 'station_name': '宮崎'}


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

        # HTMLテーブルを読み込み
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
print("宮崎県の気象データダウンロード")
print("=" * 80)

all_daily_data = []

print(f"\n処理中: 宮崎県 ({MIYAZAKI['station_name']})")
print(f"  prec_no={MIYAZAKI['prec_no']}, block_no={MIYAZAKI['block_no']}")

# 日別データ（2023年6-9月）
for month in [6, 7, 8, 9]:
    print(f"  月別ダウンロード: {month}月...")
    df_daily = download_daily_temperature(
        prec_no=MIYAZAKI['prec_no'],
        block_no=MIYAZAKI['block_no'],
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
        df_daily['都道府県'] = '宮崎県'
        df_daily['観測所'] = MIYAZAKI['station_name']
        df_daily['年'] = 2023
        df_daily['月'] = month

        all_daily_data.append(df_daily)
        print(f"    [OK] {len(df_daily)} 行取得")
    else:
        print(f"    [ERROR] データ取得失敗")

    sleep(1)

# データ統合
if all_daily_data:
    df_new = pd.concat(all_daily_data, ignore_index=True)

    # 既存データを読み込み
    existing_file = OUTPUT_DIR / "jma_daily_temperature_2023_summer.csv"
    df_existing = pd.read_csv(existing_file, encoding='utf-8-sig')

    # 島根県の重複を削除（最初の122行のみ保持）
    shimane_data = df_existing[df_existing['都道府県'] == '島根県']
    if len(shimane_data) > 122:
        print(f"\n[警告] 島根県が重複しています（{len(shimane_data)}行）")
        print(f"  最初の122行のみ保持します")
        # 島根県以外のデータ
        df_other = df_existing[df_existing['都道府県'] != '島根県'].copy()
        # 島根県の最初の122行
        df_shimane = shimane_data.iloc[:122].copy()
        # 統合
        df_existing = pd.concat([df_other, df_shimane], ignore_index=True)

    # 欠損値行を削除
    df_existing = df_existing.dropna(subset=['都道府県'])

    print(f"\n[統合前]")
    print(f"  既存データ: {len(df_existing)} 行, {len(df_existing['都道府県'].unique())} 都道府県")
    print(f"  新規データ: {len(df_new)} 行")

    # 統合
    df_combined = pd.concat([df_existing, df_new], ignore_index=True)

    print(f"\n[統合後]")
    print(f"  合計: {len(df_combined)} 行, {len(df_combined['都道府県'].unique())} 都道府県")

    # 保存
    df_combined.to_csv(existing_file, index=False, encoding='utf-8-sig')
    print(f"\n[OK] ファイル更新: {existing_file}")

else:
    print("\n[ERROR] データ取得失敗")

print("\n" + "=" * 80)
print("ダウンロード完了！")
print("=" * 80)
