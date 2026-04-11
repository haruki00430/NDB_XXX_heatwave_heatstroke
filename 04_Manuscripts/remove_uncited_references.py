#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
未引用の文献を削除し、引用番号を振り直す
"""

import re
from pathlib import Path

def extract_cited_numbers(manuscript_path):
    """本文中で実際に引用されている番号を抽出"""
    with open(manuscript_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # References セクションより前のみ
    ref_idx = text.find('# References')
    if ref_idx == -1:
        return set()

    body_text = text[:ref_idx]

    # 統計値パターンを先に除外
    # p値、R²値、β値、カンマ区切りの数値などを含む箇所をマスク
    masked_text = re.sub(r'p\s*[<>=]\s*0\.\d+\)', '[MASKED]', body_text)  # p = 0.XXX)
    masked_text = re.sub(r'R²\s*=\s*0\.\d+\)', '[MASKED]', masked_text)  # R² = 0.XXX)
    masked_text = re.sub(r'β\s*=\s*[\d,]+\.\d+', '[MASKED]', masked_text)  # β = XX.X
    masked_text = re.sub(r'\(N\s*=\s*\d+\)', '[MASKED]', masked_text)  # (N = XX)
    masked_text = re.sub(r'4/N\s*=\s*0\.\d+', '[MASKED]', masked_text)  # 4/N = 0.XX
    masked_text = re.sub(r'\d{1,3},\d{3}\)', '[MASKED]', masked_text)  # カンマ区切り数値 (12,039)
    masked_text = re.sub(r':\s*\d+–\d+\)', '[MASKED]', masked_text)  # 範囲 (4,533–12,045)

    # 引用番号を抽出（文末・文中のパターン）
    citations = set()
    # パターン1: ". XX)" または ", XX)"
    for match in re.findall(r'[.,]\s+(\d+)\)', masked_text):
        num = int(match)
        if 1 <= num <= 60:  # 引用番号の合理的な範囲
            citations.add(num)

    # パターン2: 複数引用 "XX), YY)"
    for match in re.findall(r'(\d+)\),\s*(\d+)\)', masked_text):
        num1, num2 = int(match[0]), int(match[1])
        if 1 <= num1 <= 60:
            citations.add(num1)
        if 1 <= num2 <= 60:
            citations.add(num2)

    return sorted(citations)

def extract_references(manuscript_path):
    """参考文献リストを抽出"""
    with open(manuscript_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    references = {}
    in_ref_section = False
    current_num = None

    for i, line in enumerate(lines):
        if line.strip() == '# References':
            in_ref_section = True
            continue
        if in_ref_section:
            # 次のセクション（# Tables）で終了
            if line.startswith('# ') and 'References' not in line:
                break

            # 文献番号パターン: "XX) Author..."
            match = re.match(r'^(\d+)\)', line)
            if match:
                current_num = int(match.group(1))
                references[current_num] = line
            elif current_num is not None:
                # 継続行
                references[current_num] += line

    return references

def create_new_references(old_refs, cited_nums):
    """新しい参考文献リストを作成"""
    # 引用されている文献のみを抽出
    cited_refs = {num: old_refs[num] for num in cited_nums if num in old_refs}

    # 旧番号 → 新番号のマッピング
    mapping = {}
    new_refs = {}

    for new_num, old_num in enumerate(sorted(cited_refs.keys()), 1):
        mapping[old_num] = new_num
        # 番号を振り直し
        old_text = cited_refs[old_num]
        new_text = re.sub(r'^\d+\)', f'{new_num})', old_text)
        new_refs[new_num] = new_text

    return new_refs, mapping

def update_citations_in_body(body_text, mapping):
    """本文中の引用番号を更新"""
    # プレースホルダー方式
    placeholder_map = {}

    for old_num in sorted(mapping.keys(), reverse=True):
        new_num = mapping[old_num]
        placeholder = f"##REF{old_num}##"
        placeholder_map[placeholder] = new_num

        # 引用番号パターン
        pattern = r'(?<![0-9(])' + str(old_num) + r'\)(?![0-9])'
        body_text = re.sub(pattern, placeholder, body_text)

    # プレースホルダーを新番号に置換
    for placeholder, new_num in placeholder_map.items():
        body_text = body_text.replace(placeholder, f"{new_num})")

    return body_text

def main():
    base_dir = Path(__file__).parent
    manuscript_path = base_dir / "Manuscript_heatwave_social_isolation.qmd"
    output_path = base_dir / "Manuscript_heatwave_social_isolation_cleaned.qmd"

    print("=" * 80)
    print("未引用文献の削除")
    print("=" * 80)

    # Step 1: 引用されている番号を抽出
    cited_nums = extract_cited_numbers(manuscript_path)
    print(f"\n本文中で引用されている番号（{len(cited_nums)}件）:")
    print(cited_nums)

    # Step 2: 参考文献リストを抽出
    old_refs = extract_references(manuscript_path)
    print(f"\n現在の参考文献リスト: {len(old_refs)}件（1-{max(old_refs.keys())}）")

    # Step 3: 未引用文献を特定
    uncited = sorted(set(old_refs.keys()) - set(cited_nums))
    print(f"\n未引用文献（{len(uncited)}件）:")
    print(uncited)

    # Step 4: 新しい参考文献リストを作成
    new_refs, mapping = create_new_references(old_refs, cited_nums)
    print(f"\n新しい参考文献リスト: {len(new_refs)}件（1-{len(new_refs)}）")

    # Step 5: 原稿を読み込み
    with open(manuscript_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # References セクションの開始位置を特定
    ref_idx = text.find('# References')
    tables_idx = text.find('# Tables and Figures')

    body_text = text[:ref_idx]
    tables_text = text[tables_idx:] if tables_idx != -1 else ""

    # Step 6: 本文中の引用番号を更新
    print("\n引用番号を更新中...")
    body_text_updated = update_citations_in_body(body_text, mapping)

    # Step 7: 新しい参考文献セクションを作成
    ref_section = "# References\n\n"
    for num in sorted(new_refs.keys()):
        ref_section += new_refs[num]

    # Step 8: 結合
    new_text = body_text_updated + ref_section + "\n" + tables_text

    # Step 9: 出力
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(new_text)

    # マッピングを保存
    mapping_path = base_dir / "reference_mapping_cleaned.txt"
    with open(mapping_path, 'w', encoding='utf-8') as f:
        f.write("Old Number -> New Number\n")
        f.write("=" * 30 + "\n")
        for old_num in sorted(mapping.keys()):
            new_num = mapping[old_num]
            f.write(f"{old_num:2d} -> {new_num:2d}\n")

    print("\n" + "=" * 80)
    print("完了！")
    print("=" * 80)
    print(f"  削除された文献: {len(uncited)}件")
    print(f"  最終文献数: {len(new_refs)}件")
    print(f"  出力: {output_path}")
    print(f"  マッピング: {mapping_path}")
    print("=" * 80)

if __name__ == "__main__":
    main()
