#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本文中の引用番号を厳密にチェック
"""

import re
from pathlib import Path

def extract_citations(manuscript_path):
    """本文中の引用番号を抽出"""
    with open(manuscript_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # References セクションより前のみ（本文）
    ref_idx = text.find('# References')
    if ref_idx == -1:
        print("ERROR: # References not found")
        return set()

    body_text = text[:ref_idx]

    # 引用パターン: 数字+括弧（文末・文中）
    # ただし、統計値・年号を除外
    citations = set()

    # パターン1: 文末の引用 ".XX)" または ", XX)"
    pattern1 = r'[.,]\s*(\d+)\)'
    matches1 = re.findall(pattern1, body_text)

    # パターン2: 複数引用 "XX), YY)"
    pattern2 = r'(\d+)\),\s*(\d+)\)'
    matches2 = re.findall(pattern2, body_text)

    # 全マッチを収集
    for match in matches1:
        num = int(match)
        # 統計値・年号を除外（2000以上は年号）
        if num < 100:
            citations.add(num)

    for match in matches2:
        num1, num2 = int(match[0]), int(match[1])
        if num1 < 100:
            citations.add(num1)
        if num2 < 100:
            citations.add(num2)

    # 統計値を手動で除外
    exclude_patterns = [
        r'\(N\s*=\s*(\d+)\)',  # (N = XX)
        r'p\s*[<>=]\s*0\.(\d+)',  # p = 0.0XX
        r'R²\s*=\s*0\.(\d+)',  # R² = 0.XXX
        r'β\s*=\s*(\d+)\.',  # β = XX.X
    ]

    for pattern in exclude_patterns:
        for match in re.findall(pattern, body_text):
            try:
                num = int(match)
                if num in citations and num < 100:
                    citations.discard(num)
            except:
                pass

    return sorted(citations)

def extract_references(manuscript_path):
    """参考文献リストの番号を抽出"""
    with open(manuscript_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    references = set()
    in_ref_section = False

    for line in lines:
        if line.strip() == '# References':
            in_ref_section = True
            continue
        if in_ref_section:
            # 次のセクション（# Tables）に到達したら終了
            if line.startswith('# ') and 'References' not in line:
                break
            # 文献番号パターン: "XX) Author..."
            match = re.match(r'^(\d+)\)', line)
            if match:
                references.add(int(match.group(1)))

    return sorted(references)

def find_citation_locations(manuscript_path, citation_num):
    """特定の引用番号の出現箇所を検索"""
    with open(manuscript_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    locations = []
    for i, line in enumerate(lines, 1):
        # References セクションより前のみ
        if line.strip() == '# References':
            break

        # 引用パターン
        if re.search(r'[.,\s]' + str(citation_num) + r'\)', line):
            # 統計値でないことを確認
            if not re.search(r'\(N\s*=\s*' + str(citation_num), line):
                locations.append((i, line.strip()[:100]))

    return locations

def main():
    base_dir = Path(__file__).parent
    manuscript_path = base_dir / "Manuscript_heatwave_social_isolation.qmd"

    print("=" * 80)
    print("引用番号の厳密チェック")
    print("=" * 80)

    # 本文中の引用番号を抽出
    citations = extract_citations(manuscript_path)
    print(f"\n本文中の引用番号（{len(citations)}件）:")
    print(citations)

    # 参考文献リストの番号を抽出
    references = extract_references(manuscript_path)
    print(f"\n参考文献リストの番号（{len(references)}件）:")
    print(f"  範囲: {min(references)} - {max(references)}")
    print(f"  欠番: {sorted(set(range(1, max(references) + 1)) - set(references))}")

    # 未引用の文献を特定
    uncited = sorted(set(references) - set(citations))
    print(f"\n未引用の文献（{len(uncited)}件）:")
    print(uncited)

    # 詳細レポート
    print("\n" + "=" * 80)
    print("詳細レポート")
    print("=" * 80)

    if uncited:
        print("\n[WARNING] The following references are NOT cited in the manuscript body:")
        for num in uncited:
            print(f"  #{num}")

    # Citations that are not in the reference list
    missing_refs = sorted(set(citations) - set(references))
    if missing_refs:
        print("\n[ERROR] The following citation numbers do NOT exist in the reference list:")
        for num in missing_refs:
            locs = find_citation_locations(manuscript_path, num)
            print(f"  #{num} (found {len(locs)} times in body):")
            for line_num, text in locs[:3]:  # Show first 3 locations
                print(f"    Line {line_num}: {text}")

    # 統計
    print("\n" + "=" * 80)
    print("統計")
    print("=" * 80)
    print(f"  本文中の引用: {len(citations)}件")
    print(f"  参考文献リスト: {len(references)}件")
    print(f"  未引用: {len(uncited)}件")
    print(f"  参照エラー: {len(missing_refs)}件")

    if len(uncited) > 0:
        print("\nRecommended Action:")
        print("  According to Vancouver Style, uncited references should be removed from the reference list.")

    print("=" * 80)

if __name__ == "__main__":
    main()
