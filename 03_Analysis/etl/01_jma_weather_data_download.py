"""
ETL Script 01: JMA weather data download

Automatically downloads meteorological data from the Japan Meteorological Agency
(JMA) historical data portal for the prefectural capitals of all 47 prefectures.

Retrieved data:
  1. Daily maximum temperature (June–September 2023)
     → Used to calculate heatwave days (days with max temp ≥35°C)
  2. Monthly mean temperature and relative humidity (June–September 2023)
     → Used to calculate WBGT approximation

Data source: https://www.data.jma.go.jp/obd/stats/etrn/index.php

---

ETL スクリプト 01: 気象庁データ自動ダウンロード

気象庁「過去の気象データ検索」から 47 都道府県庁所在地の
気象データを自動取得します。

取得データ:
  1. 日最高気温（2023 年 6–9 月）→ 猛暑日数（35℃以上日数）算出に使用
  2. 月平均気温・月平均湿度（2023 年 6–9 月）→ WBGT 指数算出に使用

データソース: https://www.data.jma.go.jp/obd/stats/etrn/index.php
"""

import pandas as pd
import requests
from time import sleep
import os
from pathlib import Path

# プロジェクトルートディレクトリ
PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "02_Data" / "raw" / "jma_weather"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# 47都道府県庁所在地の気象台コード（prec_no, block_no）
# 出典: 気象庁ウェブサイト（都道府県コードと観測地点コードのマッピング）
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
    '島根県': {'prec_no': 70, 'block_no': 47741, 'station_name': '松江'},
    '岡山県': {'prec_no': 66, 'block_no': 47768, 'station_name': '岡山'},
    '広島県': {'prec_no': 67, 'block_no': 47765, 'station_name': '広島'},
    '山口県': {'prec_no': 68, 'block_no': 47784, 'station_name': '下関'},
    '徳島県': {'prec_no': 71, 'block_no': 47895, 'station_name': '徳島'},
    '香川県': {'prec_no': 72, 'block_no': 47891, 'station_name': '高松'},
    '愛媛県': {'prec_no': 73, 'block_no': 47893, 'station_name': '松山'},
    '高知県': {'prec_no': 74, 'block_no': 47887, 'station_name': '高知'},
    '福岡県': {'prec_no': 82, 'block_no': 47807, 'station_name': '福岡'},
    '佐賀県': {'prec_no': 81, 'block_no': 47813, 'station_name': '佐賀'},
    '長崎県': {'prec_no': 84, 'block_no': 47817, 'station_name': '長崎'},
    '熊本県': {'prec_no': 86, 'block_no': 47819, 'station_name': '熊本'},
    '大分県': {'prec_no': 85, 'block_no': 47815, 'station_name': '大分'},
    '宮崎県': {'prec_no': 87, 'block_no': 47830, 'station_name': '宮崎'},
    '鹿児島県': {'prec_no': 88, 'block_no': 47827, 'station_name': '鹿児島'},
    '沖縄県': {'prec_no': 91, 'block_no': 47936, 'station_name': '那覇'},
}


def download_daily_temperature(prec_no, block_no, year, month):
    """
    気象庁から日別気温データをダウンロード

    Parameters:
    -----------
    prec_no : int
        都道府県コード
    block_no : int
        観測地点コード
    year : int
        年
    month : int
        月

    Returns:
    --------
    pd.DataFrame
        日別気温データ（日付、日最高気温、日平均気温、日最低気温）
    """
    url = f"https://www.data.jma.go.jp/obd/stats/etrn/view/daily_s1.php"
    params = {
        'prec_no': prec_no,
        'block_no': block_no,
        'year': year,
        'month': month,
        'day': '',
        'view': ''
    }

    try:
        # User-Agentを設定（礼儀として）
        headers = {
            'User-Agent': 'Mozilla/5.0 (Research Project: NDB Heatwave Analysis)'
        }
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()

        # HTMLテーブルをpandasで読み込み（2番目のテーブルがデータテーブル）
        dfs = pd.read_html(response.content, encoding='utf-8')

        if len(dfs) < 2:
            print(f"  警告: データテーブルが見つかりません（prec_no={prec_no}, month={month}）")
            return None

        df = dfs[0]  # 最初のテーブルを取得（気象庁のHTMLでは0番目がデータテーブル）

        # カラム名を整理（実際のHTMLに合わせて調整が必要）
        # ここでは仮の処理（実際のデータ構造を確認して調整）
        return df

    except Exception as e:
        print(f"  エラー: {e}")
        return None


def download_monthly_data(prec_no, block_no, year):
    """
    気象庁から月別平均気温・湿度データをダウンロード

    Parameters:
    -----------
    prec_no : int
        都道府県コード
    block_no : int
        観測地点コード
    year : int
        年

    Returns:
    --------
    pd.DataFrame
        月別データ（月、平均気温、平均湿度）
    """
    url = f"https://www.data.jma.go.jp/obd/stats/etrn/view/monthly_s1.php"
    params = {
        'prec_no': prec_no,
        'block_no': block_no,
        'year': year,
        'month': '',
        'day': '',
        'view': ''
    }

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Research Project: NDB Heatwave Analysis)'
        }
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()

        dfs = pd.read_html(response.content, encoding='utf-8')

        if len(dfs) < 1:
            print(f"  警告: 月別データテーブルが見つかりません（prec_no={prec_no}）")
            return None

        df = dfs[0]
        return df

    except Exception as e:
        print(f"  エラー: {e}")
        return None


def main():
    """
    メイン処理：47都道府県の気象データをダウンロード
    """
    print("=" * 80)
    print("気象庁データ自動ダウンロード開始")
    print("=" * 80)

    all_daily_data = []
    all_monthly_data = []

    for pref, info in PREFECTURE_STATIONS.items():
        print(f"\n処理中: {pref} ({info['station_name']})")

        # 日別データ（2023年6-9月）
        for month in [6, 7, 8, 9]:
            print(f"  月別ダウンロード: {month}月...")
            df_daily = download_daily_temperature(
                prec_no=info['prec_no'],
                block_no=info['block_no'],
                year=2023,
                month=month
            )

            if df_daily is not None:
                df_daily['都道府県'] = pref
                df_daily['観測所'] = info['station_name']
                df_daily['年'] = 2023
                df_daily['月'] = month
                all_daily_data.append(df_daily)

            # サーバー負荷軽減のため1秒待機
            sleep(1)

        # 月別データ（2023年年間）
        print(f"  月別平均データダウンロード...")
        df_monthly = download_monthly_data(
            prec_no=info['prec_no'],
            block_no=info['block_no'],
            year=2023
        )

        if df_monthly is not None:
            df_monthly['都道府県'] = pref
            df_monthly['観測所'] = info['station_name']
            df_monthly['年'] = 2023
            all_monthly_data.append(df_monthly)

        sleep(1)

    # データ統合
    if all_daily_data:
        df_all_daily = pd.concat(all_daily_data, ignore_index=True)
        output_path_daily = OUTPUT_DIR / "jma_daily_temperature_2023_summer.csv"
        df_all_daily.to_csv(output_path_daily, index=False, encoding='utf-8-sig')
        print(f"\n[OK] 日別データ保存完了: {output_path_daily}")
        print(f"   データ件数: {len(df_all_daily)} 行")

    if all_monthly_data:
        df_all_monthly = pd.concat(all_monthly_data, ignore_index=True)
        output_path_monthly = OUTPUT_DIR / "jma_monthly_climate_2023.csv"
        df_all_monthly.to_csv(output_path_monthly, index=False, encoding='utf-8-sig')
        print(f"\n[OK] 月別データ保存完了: {output_path_monthly}")
        print(f"   データ件数: {len(df_all_monthly)} 行")

    print("\n" + "=" * 80)
    print("ダウンロード完了！")
    print("=" * 80)


if __name__ == "__main__":
    main()
