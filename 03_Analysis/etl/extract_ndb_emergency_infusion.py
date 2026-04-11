"""
NDB第10回から救急医療管理加算・輸液の都道府県別算定回数を抽出

データソース:
- B001-2-6: 夜間休日救急搬送医学管理料（診療行為コード: 113013810）
- G004: 点滴注射（500mL以上）（診療行為コード: 130003810）

出力:
- emergency_infusion_prefecture.csv（47都道府県×2指標）
"""

import pandas as pd
from pathlib import Path

# ファイルパス
b_pref_file = r"C:\Users\user\.ag-cursor-common\research_workspace\projects\NDB_Research_Hub\02_Data\raw\NDB_OpenData\No.10\01_医科診療行為（算定回数）\01_公費レセプトを含まないデータ\B_医学管理等\都道府県別算定回数.xlsx"
g_pref_file = r"C:\Users\user\.ag-cursor-common\research_workspace\projects\NDB_Research_Hub\02_Data\raw\NDB_OpenData\No.10\01_医科診療行為（算定回数）\01_公費レセプトを含まないデータ\G_注射\都道府県別算定回数.xlsx"

# 出力先
PROJECT_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_DIR = PROJECT_ROOT / "02_Data" / "interim"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 80)
print("NDB第10回 救急医療管理加算・輸液の都道府県別データ抽出")
print("=" * 80)

# ==============================================================================
# 1. B001-2-6: 夜間休日救急搬送医学管理料
# ==============================================================================
print("\n[1/2] 夜間休日救急搬送医学管理料の抽出")
print("-" * 80)

# データ読み込み（header=2, 行3をスキップ）
df_b = pd.read_excel(b_pref_file, sheet_name='外来', header=2, skiprows=[3])

# 診療行為コード 113013810 を検索
emergency_code = '113013810'
emergency_row = df_b[df_b.iloc[:, 2].astype(str) == emergency_code]

if len(emergency_row) == 0:
    print(f"[!] 診療行為コード {emergency_code} が見つかりませんでした")
    emergency_data = None
else:
    print(f"[OK] 診療行為コード {emergency_code} を発見")
    print(f"  診療行為名: {emergency_row.iloc[0, 3]}")
    print(f"  点数: {emergency_row.iloc[0, 4]}")
    print(f"  総計: {emergency_row.iloc[0, 5]:,} 回")

    # 都道府県別データを抽出（列6-52が都道府県01-47）
    emergency_data = emergency_row.iloc[0, 6:53].values
    print(f"  都道府県数: {len(emergency_data)}")

# ==============================================================================
# 2. G004: 点滴注射（500mL以上）
# ==============================================================================
print("\n[2/2] 点滴注射（500mL以上）の抽出")
print("-" * 80)

# データ読み込み
df_g = pd.read_excel(g_pref_file, sheet_name='外来', header=2, skiprows=[3])

# 診療行為コード 130003810 を検索
infusion_code = '130003810'
infusion_row = df_g[df_g.iloc[:, 2].astype(str) == infusion_code]

if len(infusion_row) == 0:
    print(f"[!] 診療行為コード {infusion_code} が見つかりませんでした")
    infusion_data = None
else:
    print(f"[OK] 診療行為コード {infusion_code} を発見")
    print(f"  診療行為名: {infusion_row.iloc[0, 3]}")
    print(f"  点数: {infusion_row.iloc[0, 4]}")
    print(f"  総計: {infusion_row.iloc[0, 5]:,} 回")

    # 都道府県別データを抽出
    infusion_data = infusion_row.iloc[0, 6:53].values
    print(f"  都道府県数: {len(infusion_data)}")

# ==============================================================================
# 3. データ統合
# ==============================================================================
print("\n" + "=" * 80)
print("データ統合")
print("=" * 80)

# 都道府県名リスト（NDBの都道府県コード01-47）
prefecture_names = [
    '北海道', '青森県', '岩手県', '宮城県', '秋田県', '山形県', '福島県',
    '茨城県', '栃木県', '群馬県', '埼玉県', '千葉県', '東京都', '神奈川県',
    '新潟県', '富山県', '石川県', '福井県', '山梨県', '長野県', '岐阜県',
    '静岡県', '愛知県', '三重県', '滋賀県', '京都府', '大阪府', '兵庫県',
    '奈良県', '和歌山県', '鳥取県', '島根県', '岡山県', '広島県', '山口県',
    '徳島県', '香川県', '愛媛県', '高知県', '福岡県', '佐賀県', '長崎県',
    '熊本県', '大分県', '宮崎県', '鹿児島県', '沖縄県'
]

if emergency_data is not None and infusion_data is not None:
    # DataFrame作成
    df_result = pd.DataFrame({
        '都道府県': prefecture_names,
        '夜間休日救急搬送医学管理料_算定回数': emergency_data,
        '点滴注射500mL以上_算定回数': infusion_data
    })

    # マスク値（"-"）をNaNに変換
    df_result['夜間休日救急搬送医学管理料_算定回数'] = pd.to_numeric(
        df_result['夜間休日救急搬送医学管理料_算定回数'],
        errors='coerce'
    )
    df_result['点滴注射500mL以上_算定回数'] = pd.to_numeric(
        df_result['点滴注射500mL以上_算定回数'],
        errors='coerce'
    )

    # 保存
    output_path = OUTPUT_DIR / "emergency_infusion_prefecture.csv"
    df_result.to_csv(output_path, index=False, encoding='utf-8-sig')

    print(f"\n[OK] データ統合完了")
    print(f"  都道府県数: {len(df_result)}")
    print(f"  変数数: {len(df_result.columns) - 1}")  # 都道府県を除く

    # 統計サマリー
    print("\n" + "-" * 80)
    print("統計サマリー")
    print("-" * 80)

    print("\n[夜間休日救急搬送医学管理料_算定回数]")
    print(f"  平均: {df_result['夜間休日救急搬送医学管理料_算定回数'].mean():,.1f} 回")
    print(f"  中央値: {df_result['夜間休日救急搬送医学管理料_算定回数'].median():,.1f} 回")
    print(f"  最大: {df_result['夜間休日救急搬送医学管理料_算定回数'].max():,.0f} 回 ({df_result.loc[df_result['夜間休日救急搬送医学管理料_算定回数'].idxmax(), '都道府県']})")
    print(f"  最小: {df_result['夜間休日救急搬送医学管理料_算定回数'].min():,.0f} 回 ({df_result.loc[df_result['夜間休日救急搬送医学管理料_算定回数'].idxmin(), '都道府県']})")

    print("\n[点滴注射500mL以上_算定回数]")
    print(f"  平均: {df_result['点滴注射500mL以上_算定回数'].mean():,.1f} 回")
    print(f"  中央値: {df_result['点滴注射500mL以上_算定回数'].median():,.1f} 回")
    print(f"  最大: {df_result['点滴注射500mL以上_算定回数'].max():,.0f} 回 ({df_result.loc[df_result['点滴注射500mL以上_算定回数'].idxmax(), '都道府県']})")
    print(f"  最小: {df_result['点滴注射500mL以上_算定回数'].min():,.0f} 回 ({df_result.loc[df_result['点滴注射500mL以上_算定回数'].idxmin(), '都道府県']})")

    # トップ10都道府県
    print("\n" + "-" * 80)
    print("夜間休日救急搬送医学管理料 トップ10都道府県")
    print("-" * 80)
    top10 = df_result.nlargest(10, '夜間休日救急搬送医学管理料_算定回数')
    print(top10[['都道府県', '夜間休日救急搬送医学管理料_算定回数']].to_string(index=False))

    print("\n" + "-" * 80)
    print("点滴注射500mL以上 トップ10都道府県")
    print("-" * 80)
    top10_infusion = df_result.nlargest(10, '点滴注射500mL以上_算定回数')
    print(top10_infusion[['都道府県', '点滴注射500mL以上_算定回数']].to_string(index=False))

    # 保存完了
    print("\n" + "=" * 80)
    print("抽出完了！")
    print("=" * 80)
    print(f"\n出力ファイル: {output_path}")
    print(f"データ件数: {len(df_result)} 都道府県")

else:
    print("\n[!] データ抽出に失敗しました")
