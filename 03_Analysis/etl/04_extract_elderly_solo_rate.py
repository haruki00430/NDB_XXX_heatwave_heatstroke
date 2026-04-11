"""
国勢調査2020年から高齢者単独世帯率を抽出

データソース: C:\\Users\\user\\SharedWorkspace\\projects\\NDB_Research_Hub\\02_Data\\raw\\Statistics_Bureau\\Census_2020\\tblT001141H01-47.txt

必要なカラム:
- T001141038: 一般世帯数
- T001141050: 65歳以上単独世帯数

出力:
- elderly_solo_household_rate.csv (47都道府県)
"""

import pandas as pd
from pathlib import Path

# ディレクトリ設定
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = Path(r"C:\Users\user\SharedWorkspace\projects\NDB_Research_Hub\02_Data\raw\Statistics_Bureau\Census_2020")
OUTPUT_DIR = PROJECT_ROOT / "02_Data" / "interim"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 47都道府県名（H01～H47の順）
PREFECTURES = [
    '北海道', '青森県', '岩手県', '宮城県', '秋田県', '山形県', '福島県',
    '茨城県', '栃木県', '群馬県', '埼玉県', '千葉県', '東京都', '神奈川県',
    '新潟県', '富山県', '石川県', '福井県', '山梨県', '長野県',
    '岐阜県', '静岡県', '愛知県', '三重県',
    '滋賀県', '京都府', '大阪府', '兵庫県', '奈良県', '和歌山県',
    '鳥取県', '島根県', '岡山県', '広島県', '山口県',
    '徳島県', '香川県', '愛媛県', '高知県',
    '福岡県', '佐賀県', '長崎県', '熊本県', '大分県', '宮崎県', '鹿児島県', '沖縄県'
]

print("=" * 80)
print("国勢調査2020年: 高齢者単独世帯率の抽出")
print("=" * 80)

all_data = []

for i, pref in enumerate(PREFECTURES, start=1):
    # ファイル名（H01～H47）
    file_num = str(i).zfill(2)
    file_path = SOURCE_DIR / f"tblT001141H{file_num}.txt"

    print(f"\n処理中: {pref} (H{file_num})")
    print(f"  ファイル: {file_path}")

    try:
        # Shift-JIS (cp932) で読み込み（skiprows=0: 1行目がカラム名）
        # low_memory=Falseで型警告を抑制
        df = pd.read_csv(file_path, encoding='cp932', skiprows=0, low_memory=False)

        # index=0は日本語ヘッダー行なので除外
        # index=1以降が市区町村データ
        df_data = df.iloc[1:].copy()

        # 必要なカラムを数値に変換（"*"はNaNに）
        df_data['T001141038'] = pd.to_numeric(df_data['T001141038'], errors='coerce')
        df_data['T001141050'] = pd.to_numeric(df_data['T001141050'], errors='coerce')

        # 都道府県全体 = 全市区町村の合計
        total_households = df_data['T001141038'].sum()
        elderly_solo_households = df_data['T001141050'].sum()

        # 高齢者単独世帯率（%）
        elderly_solo_rate = (elderly_solo_households / total_households) * 100 if total_households > 0 else 0

        all_data.append({
            '都道府県': pref,
            '総世帯数': int(total_households),
            '65歳以上単独世帯数': int(elderly_solo_households),
            '高齢者単独世帯率': elderly_solo_rate
        })

        print(f"  [OK] 総世帯数={int(total_households):,}, 65歳以上単独世帯={int(elderly_solo_households):,}, 率={elderly_solo_rate:.2f}%")

    except Exception as e:
        print(f"  [エラー] {e}")
        import traceback
        traceback.print_exc()

# DataFrame化
df_result = pd.DataFrame(all_data)

print("\n" + "=" * 80)
print("集計結果")
print("=" * 80)
print(f"都道府県数: {len(df_result)}")
print(f"\n高齢者単独世帯率 トップ10:")
print(df_result.nlargest(10, '高齢者単独世帯率')[['都道府県', '高齢者単独世帯率']])

print(f"\n[統計]")
print(f"  平均: {df_result['高齢者単独世帯率'].mean():.2f}%")
print(f"  中央値: {df_result['高齢者単独世帯率'].median():.2f}%")
print(f"  最大: {df_result['高齢者単独世帯率'].max():.2f}% ({df_result.loc[df_result['高齢者単独世帯率'].idxmax(), '都道府県']})")
print(f"  最小: {df_result['高齢者単独世帯率'].min():.2f}% ({df_result.loc[df_result['高齢者単独世帯率'].idxmin(), '都道府県']})")

# 保存
output_path = OUTPUT_DIR / "elderly_solo_household_rate.csv"
df_result.to_csv(output_path, index=False, encoding='utf-8-sig')

print(f"\n[保存完了]")
print(f"出力ファイル: {output_path}")
print(f"データ件数: {len(df_result)} 都道府県")

print("\n" + "=" * 80)
print("抽出完了！")
print("=" * 80)
