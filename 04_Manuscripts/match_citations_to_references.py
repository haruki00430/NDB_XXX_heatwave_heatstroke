#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
引用箇所の文脈と参考文献を照合
"""

import re
from pathlib import Path

def extract_citation_contexts(manuscript_path):
    """本文中の引用箇所の文脈を抽出"""
    with open(manuscript_path, 'r', encoding='utf-8') as f:
        text = f.read()

    ref_idx = text.find('# References')
    if ref_idx == -1:
        return {}

    body_text = text[:ref_idx]

    # 統計値を除外
    masked_text = re.sub(r'p\s*[<>=]\s*0\.\d+\)', '[MASKED]', body_text)
    masked_text = re.sub(r'R²\s*=\s*0\.\d+\)', '[MASKED]', masked_text)
    masked_text = re.sub(r'\(N\s*=\s*\d+\)', '[MASKED]', masked_text)
    masked_text = re.sub(r'\d{1,3},\d{3}\)', '[MASKED]', masked_text)

    contexts = {}

    # 引用パターン: ". XX)" または ", XX)"
    for match in re.finditer(r'([^.]{150}[.,]\s*)(\d+)\)([^.]{150})', masked_text):
        num = int(match.group(2))
        if num < 100 and num > 0:
            context = match.group(1) + match.group(2) + ')' + match.group(3)

            if num not in contexts:
                contexts[num] = context.strip()

    return contexts

def extract_references(manuscript_path):
    """参考文献リストを抽出"""
    with open(manuscript_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    references = {}
    in_ref_section = False
    current_num = None
    current_text = ""

    for line in lines:
        if line.strip() == '# References':
            in_ref_section = True
            continue
        if in_ref_section:
            if line.startswith('# ') and 'References' not in line:
                break

            match = re.match(r'^(\d+)\)\s*(.+)', line)
            if match:
                # 前の文献を保存
                if current_num is not None:
                    references[current_num] = current_text

                current_num = int(match.group(1))
                current_text = match.group(2).strip()
            elif current_num is not None and line.strip():
                current_text += ' ' + line.strip()

    # 最後の文献を保存
    if current_num is not None:
        references[current_num] = current_text

    return references

def main():
    base_dir = Path(__file__).parent
    manuscript_path = base_dir / "Manuscript_heatwave_social_isolation.qmd"
    output_path = base_dir / "CITATION_REFERENCE_MATCHING.md"

    print("=" * 80)
    print("Citation-Reference Matching")
    print("=" * 80)

    # 引用箇所の文脈を抽出
    contexts = extract_citation_contexts(manuscript_path)
    print(f"\nExtracted contexts for {len(contexts)} citation numbers")

    # 参考文献リストを抽出
    references = extract_references(manuscript_path)
    print(f"Extracted {len(references)} references")

    # 照合表を作成
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# 引用箇所と参考文献の照合表\n\n")
        f.write("## 本文中で引用されている34件\n\n")
        f.write("各引用番号について、文脈と参考文献が一致しているか確認してください。\n\n")
        f.write("---\n\n")

        # 引用されている番号のみ
        cited_nums = sorted(contexts.keys())

        for num in cited_nums:
            context = contexts[num]
            ref_text = references.get(num, "ERROR: Reference not found")

            # 著者名を抽出
            author_match = re.match(r'^([A-Z][a-z]+(?:\s+[A-Z]{1,2})?(?:,\s+[A-Z][a-z]+\s+[A-Z]{1,2})?)', ref_text)
            if author_match:
                author = author_match.group(1).strip()
            else:
                author = ref_text.split('.')[0][:40]

            # 年を抽出
            year_match = re.search(r'\b(19|20)\d{2}\b', ref_text)
            year = year_match.group(0) if year_match else "N/A"

            f.write(f"## Citation #{num}\n\n")
            f.write(f"### Context (文脈)\n")
            f.write(f"```\n{context}\n```\n\n")
            f.write(f"### Current Reference (現在の参考文献)\n")
            f.write(f"**[{num}] {author} ({year})**\n\n")
            f.write(f"> {ref_text[:200]}{'...' if len(ref_text) > 200 else ''}\n\n")
            f.write(f"### Verification Question (検証質問)\n")
            f.write(f"- [ ] 文脈と参考文献の内容は一致していますか？\n")
            f.write(f"- [ ] この参考文献は実在しますか？（PubMed/医中誌/Google Scholarで確認）\n\n")
            f.write(f"### Comments (コメント)\n")
            f.write(f"\n\n")
            f.write("---\n\n")

    print(f"\nMatching table created: {output_path}")
    print("\nNext steps:")
    print("  1. Open CITATION_REFERENCE_MATCHING.md")
    print("  2. For each citation, verify:")
    print("     - Does the context match the reference content?")
    print("     - Does the reference exist? (check PubMed/Google Scholar)")
    print("  3. Mark citations with issues for correction")
    print("=" * 80)

if __name__ == "__main__":
    main()
