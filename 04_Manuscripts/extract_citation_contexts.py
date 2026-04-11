#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本文中の引用箇所の文脈を抽出
"""

import re
from pathlib import Path

def extract_citation_contexts(manuscript_path):
    """各引用番号の前後の文脈を抽出"""
    with open(manuscript_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # References セクションより前のみ
    ref_idx = text.find('# References')
    if ref_idx == -1:
        print("ERROR: # References not found")
        return {}

    body_text = text[:ref_idx]

    # 引用パターン: 数字+括弧（文末・文中）
    contexts = {}

    # パターン1: 単独引用 ".XX)" または ", XX)"
    for match in re.finditer(r'([.,]\s*)(\d+)\)', body_text):
        num = int(match.group(2))
        if num < 100:  # 引用番号の範囲
            pos = match.start()
            # 前後100文字を抽出
            start = max(0, pos - 100)
            end = min(len(body_text), match.end() + 100)
            context = body_text[start:end]

            # 統計値パターンを除外
            if re.search(r'\(N\s*=\s*' + str(num), context):
                continue
            if re.search(r'p\s*[<>=]\\s*0\\.\\d*' + str(num), context):
                continue

            if num not in contexts:
                contexts[num] = []
            contexts[num].append({
                'position': pos,
                'context': context.strip(),
                'line': body_text[:pos].count('\n') + 1
            })

    # パターン2: 複数引用 "XX), YY)"
    for match in re.finditer(r'(\d+)\),\s*(\d+)\)', body_text):
        for i in [1, 2]:
            num = int(match.group(i))
            if num < 100:
                pos = match.start()
                start = max(0, pos - 100)
                end = min(len(body_text), match.end() + 100)
                context = body_text[start:end]

                if num not in contexts:
                    contexts[num] = []
                contexts[num].append({
                    'position': pos,
                    'context': context.strip(),
                    'line': body_text[:pos].count('\n') + 1
                })

    return contexts

def main():
    base_dir = Path(__file__).parent
    manuscript_path = base_dir / "Manuscript_heatwave_social_isolation.qmd"
    output_path = base_dir / "citation_contexts.txt"

    print("=" * 80)
    print("Extract Citation Contexts")
    print("=" * 80)

    contexts = extract_citation_contexts(manuscript_path)

    # 出力
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("Citation Contexts\n")
        f.write("=" * 80 + "\n\n")

        for num in sorted(contexts.keys()):
            f.write(f"Citation #{num} (found {len(contexts[num])} times)\n")
            f.write("-" * 80 + "\n")

            for i, ctx in enumerate(contexts[num], 1):
                f.write(f"\nOccurrence {i} (Line {ctx['line']}):\n")
                f.write(f"{ctx['context']}\n")
                f.write("\n")

            f.write("=" * 80 + "\n\n")

    print(f"\nExtracted contexts for {len(contexts)} citation numbers")
    print(f"Output: {output_path}")
    print("\nPlease review the contexts and determine which reference should be cited.")
    print("=" * 80)

if __name__ == "__main__":
    main()
