#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本文中の引用番号を安全に置換（統計値を除外）
"""

from pathlib import Path
import re

def load_mapping(mapping_file):
    """マッピングテーブルを読み込み"""
    mapping = {}
    with open(mapping_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # ヘッダー2行をスキップ
    for line in lines[2:]:
        line = line.strip()
        if not line:
            continue

        # 形式: " 5 →  4 (shift: -1)"
        match = re.match(r'(\d+)\s*→\s*(\d+)', line)
        if match:
            old_num = int(match.group(1))
            new_num = int(match.group(2))
            mapping[old_num] = new_num

    return mapping

def is_statistical_context(text, pos, number):
    """統計値のコンテキストかどうかを判定"""
    # 前後20文字を確認
    start = max(0, pos - 20)
    end = min(len(text), pos + 20)
    context = text[start:end]

    # 除外パターン
    exclude_patterns = [
        r'\(N\s*=\s*' + str(number) + r'\)',  # (N = XX)
        r'p\s*[<>=]\s*0\.\d*' + str(number),  # p = 0.XXX
        r'\d{4}\)',  # 年号 (2020)
        r'[GDB]\d{3}' + str(number),  # 診療行為コード (G004)
        r'4/N\s*=\s*0\.' + str(number),  # Cook's distance threshold
        r'β\s*=\s*\d+\.' + str(number),  # 回帰係数
        r'R²\s*=\s*0\.' + str(number),  # R-squared
        r'\d+\.\d+\)',  # 小数点を含む数値
    ]

    for pattern in exclude_patterns:
        if re.search(pattern, context, re.IGNORECASE):
            return True

    return False

def replace_citations_safe(manuscript_path, mapping_file, output_path):
    """引用番号を安全に置換"""
    # マッピング読み込み
    mapping = load_mapping(mapping_file)

    # 原稿読み込み
    with open(manuscript_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # 行189以降（参考文献セクション）は除外
    lines = text.split('\n')
    body_lines = lines[:188]  # 本文のみ
    ref_lines = lines[188:]   # 参考文献セクション

    body_text = '\n'.join(body_lines)

    # 置換カウンタ
    replacements = {}
    skipped = []

    # プレースホルダー方式で置換（重複を避ける）
    # Step 1: 旧番号をプレースホルダーに置換
    placeholder_map = {}
    for old_num in sorted(mapping.keys()):
        new_num = mapping[old_num]
        placeholder = f"##REF{old_num}##"
        placeholder_map[placeholder] = new_num

        # 引用番号パターン（文中・文末）
        # 前後に文字・数字以外がある場合のみマッチ
        pattern = r'(?<![0-9(])' + str(old_num) + r'\)(?![0-9])'

        replaced_count = 0
        pos = 0
        while True:
            match = re.search(pattern, body_text[pos:])
            if not match:
                break

            abs_pos = pos + match.start()

            # 統計値コンテキストかチェック
            if is_statistical_context(body_text, abs_pos, old_num):
                skipped.append(f"#{old_num} at line ~{body_text[:abs_pos].count(chr(10))+1} (statistical context)")
                pos = abs_pos + len(str(old_num)) + 1
                continue

            # プレースホルダーに置換
            body_text = body_text[:abs_pos] + placeholder + body_text[match.end() + pos:]
            replaced_count += 1
            pos = abs_pos + len(placeholder)

        if replaced_count > 0:
            replacements[old_num] = (new_num, replaced_count)

    # Step 2: プレースホルダーを新番号に置換
    for placeholder, new_num in placeholder_map.items():
        body_text = body_text.replace(placeholder, f"{new_num})")

    # 本文と参考文献を結合
    new_text = body_text + '\n' + '\n'.join(ref_lines)

    # 出力
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(new_text)

    return replacements, skipped

def main():
    base_dir = Path(__file__).parent
    manuscript_path = base_dir / "Manuscript_heatwave_social_isolation.qmd"
    mapping_file = base_dir / "reference_mapping_final.txt"
    output_path = base_dir / "Manuscript_heatwave_social_isolation_fixed.qmd"

    print("=" * 60)
    print("引用番号の置換開始")
    print("=" * 60)

    print(f"\n入力ファイル: {manuscript_path}")
    print(f"マッピング: {mapping_file}")
    print(f"出力ファイル: {output_path}")

    # 置換実行
    replacements, skipped = replace_citations_safe(manuscript_path, mapping_file, output_path)

    # レポート
    print("\n--- 置換結果 ---")
    for old_num, (new_num, count) in sorted(replacements.items()):
        print(f"  #{old_num} → #{new_num} ({count}箇所)")

    if skipped:
        print("\n--- スキップ（統計値コンテキスト）---")
        for skip in skipped[:10]:  # 最初の10件のみ表示
            print(f"  {skip}")
        if len(skipped) > 10:
            print(f"  ... and {len(skipped) - 10} more")

    print("\n" + "=" * 60)
    print("完了！")
    print("=" * 60)
    print(f"\n出力ファイル: {output_path}")
    print("\n次のステップ:")
    print("  1. 出力ファイルを確認")
    print("  2. 統計値 (N = 47) が保護されているか確認")
    print("  3. 問題なければ、元のファイルを置換")
    print(f"     mv {output_path} {manuscript_path}")
    print("=" * 60)

if __name__ == "__main__":
    main()
