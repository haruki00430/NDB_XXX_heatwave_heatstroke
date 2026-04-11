"""
国勢調査2020年から都道府県別人口データを抽出

データソース:
- Statistics_Bureau/Census_2020/tblT001141H01~H47.txt
- T001141001: 人口（総数）
"""

import pandas as pd
from pathlib import Path

# パス設定
CENSUS_DIR = Path(r"C:\Users\user\SharedWorkspace\projects\NDB_Research_Hub\02_Data\raw\Statistics_Bureau\Census_2020")
OUTPUT_DIR = Path(__file__).resolve().parents[2] / "02_Data" / "interim"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 80)
print("国勢調査2020年 都道府県別人口データ抽出")
print("=" * 80)

# 都道府県名リスト（H01=北海道〜H47=沖縄県）
prefecture_names = [
    '北海道', '青森県', '岩手県', '宮城県', '秋田県', '山形県', '福島県',
    '茨城県', '栃木県', '群馬県', '埼玉県', '千葉県', '東京都', '神奈川県',
    '新潟県', '富山県', '石川県', '福井県', '山梨県', '長野県', '岐阜県',
    '静岡県', '愛知県', '三重県', '滋賀県', '京都府', '大阪府', '兵庫県',
    '奈良県', '和歌山県', '鳥取県', '島根県', '岡山県', '広島県', '山口県',
    '徳島県', '香川県', '愛媛県', '高知県', '福岡県', '佐賀県', '長崎県',
    '熊本県', '大分県', '宮崎県', '鹿児島県', '沖縄県'
]

results = []

for pref_num, pref_name in enumerate(prefecture_names, 1):
    # ファイルパス（H01〜H47）
    file_path = CENSUS_DIR / f"tblT001141H{pref_num:02d}.txt"

    if not file_path.exists():
        print(f"[!] ファイルが見つかりません: {file_path}")
        continue

    print(f"処理中: {pref_name} ({pref_num:02d}/47)...", end="\r")

    try:
        # データ読み込み（CP932エンコーディング、全て文字列として読み込み）
        df = pd.read_csv(file_path, encoding='cp932', dtype=str)

        # 都道府県全体の集計行を抽出（HTKSYORI='0'の行）
        # HTKSYORIカラムが'0'の行を抽出
        pref_data = df[df['HTKSYORI'] == '0']

        if len(pref_data) == 0:
            print(f"[!] {pref_name}: 都道府県集計行が見つかりません")
            continue

        # T001141001カラムを数値に変換してから合計
        # errors='coerce'で変換できない値はNaNになる
        numeric_pop = pd.to_numeric(pref_data['T001141001'], errors='coerce')
        total_population = numeric_pop.sum()

        results.append({
            '都道府県': pref_name,
            '総人口': int(total_population)
        })

        print(f"  [OK] {pref_name}: 総人口 {total_population:,} 人")

    except Exception as e:
        print(f"  [エラー] {pref_name}: {e}")

# DataFrame作成
df_result = pd.DataFrame(results)

# 保存
output_path = OUTPUT_DIR / "prefecture_population_2020.csv"
df_result.to_csv(output_path, index=False, encoding='utf-8-sig')

print("\n" + "=" * 80)
print("集計結果")
print("=" * 80)
print(f"都道府県数: {len(df_result)}")
print(f"\n統計:")
print(f"  総人口合計: {df_result['総人口'].sum():,} 人")
print(f"  平均: {df_result['総人口'].mean():,.0f} 人")
print(f"  中央値: {df_result['総人口'].median():,.0f} 人")
print(f"  最大: {df_result['総人口'].max():,} 人 ({df_result.loc[df_result['総人口'].idxmax(), '都道府県']})")
print(f"  最小: {df_result['総人口'].min():,} 人 ({df_result.loc[df_result['総人口'].idxmin(), '都道府県']})")

print(f"\nトップ10都道府県:")
top10 = df_result.nlargest(10, '総人口')
print(top10.to_string(index=False))

print("\n" + "=" * 80)
print("抽出完了！")
print("=" * 80)
print(f"\n出力ファイル: {output_path}")
print(f"データ件数: {len(df_result)} 都道府県")
