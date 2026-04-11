"""
気象庁データダウンロードのテストスクリプト（東京都のみ）

HTMLの構造を確認し、データ取得が正しく動作するかテスト
"""

import pandas as pd
import requests
from pathlib import Path

# 出力先
OUTPUT_DIR = Path(__file__).resolve().parents[2] / "02_Data" / "raw" / "jma_weather"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 東京都の気象台コード
TOKYO_PREC_NO = 44
TOKYO_BLOCK_NO = 47662

print("=" * 80)
print("気象庁データダウンロードテスト（東京都のみ）")
print("=" * 80)

# テスト1: 日別データ（2023年7月）
print("\n[テスト1] 日別データダウンロード（2023年7月）")
url_daily = "https://www.data.jma.go.jp/obd/stats/etrn/view/daily_s1.php"
params_daily = {
    'prec_no': TOKYO_PREC_NO,
    'block_no': TOKYO_BLOCK_NO,
    'year': 2023,
    'month': 7,
    'day': '',
    'view': ''
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Research Project: NDB Heatwave Analysis)'
}

try:
    response = requests.get(url_daily, params=params_daily, headers=headers, timeout=10)
    response.raise_for_status()

    print(f"[OK] HTTP接続成功 (ステータスコード: {response.status_code})")

    # HTMLテーブルを読み込み
    dfs = pd.read_html(response.content, encoding='utf-8')
    print(f"[OK] HTMLテーブル取得成功（テーブル数: {len(dfs)}）")

    # 各テーブルの構造を表示
    for i, df in enumerate(dfs):
        print(f"\n--- テーブル {i} ---")
        print(f"形状: {df.shape}")
        print(f"カラム: {list(df.columns[:10])}")  # 最初の10カラムのみ表示
        print("\n最初の5行:")
        print(df.head())

        # CSVに保存
        output_path = OUTPUT_DIR / f"test_tokyo_daily_table_{i}.csv"
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"[保存] 保存: {output_path}")

except Exception as e:
    print(f"[ERROR] エラー: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)

# テスト2: 月別データ（2023年年間）
print("\n[テスト2] 月別データダウンロード（2023年）")
url_monthly = "https://www.data.jma.go.jp/obd/stats/etrn/view/monthly_s1.php"
params_monthly = {
    'prec_no': TOKYO_PREC_NO,
    'block_no': TOKYO_BLOCK_NO,
    'year': 2023,
    'month': '',
    'day': '',
    'view': ''
}

try:
    response = requests.get(url_monthly, params=params_monthly, headers=headers, timeout=10)
    response.raise_for_status()

    print(f"[OK] HTTP接続成功 (ステータスコード: {response.status_code})")

    dfs = pd.read_html(response.content, encoding='utf-8')
    print(f"[OK] HTMLテーブル取得成功（テーブル数: {len(dfs)}）")

    for i, df in enumerate(dfs):
        print(f"\n--- テーブル {i} ---")
        print(f"形状: {df.shape}")
        print(f"カラム: {list(df.columns[:10])}")
        print("\n最初の5行:")
        print(df.head())

        output_path = OUTPUT_DIR / f"test_tokyo_monthly_table_{i}.csv"
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"[保存] 保存: {output_path}")

except Exception as e:
    print(f"[ERROR] エラー: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("テスト完了！")
print(f"出力ディレクトリ: {OUTPUT_DIR}")
print("=" * 80)
