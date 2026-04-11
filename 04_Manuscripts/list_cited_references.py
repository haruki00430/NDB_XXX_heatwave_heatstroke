#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本文中で引用されている34件の参考文献リストを作成
"""

import re
from pathlib import Path

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
    output_path = base_dir / "CITED_REFERENCES_LIST.md"

    # check_citations.pyの結果から、引用されている34件
    cited_nums = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 26, 27, 28, 29, 30, 32, 34, 36, 37, 39]
    uncited_nums = [25, 31, 33, 35, 38, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49]

    print("=" * 80)
    print("Cited References List")
    print("=" * 80)

    # 参考文献リストを抽出
    references = extract_references(manuscript_path)
    print(f"\nExtracted {len(references)} references")
    print(f"Cited: {len(cited_nums)} references")
    print(f"Uncited: {len(uncited_nums)} references")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# 本文中で引用されている34件の参考文献リスト\n\n")
        f.write("## 概要\n\n")
        f.write(f"- **総参考文献数**: 49件\n")
        f.write(f"- **本文中で引用**: 34件\n")
        f.write(f"- **未引用**: 15件\n\n")
        f.write("---\n\n")

        f.write("## 引用されている34件\n\n")
        f.write("各文献について、PubMed / 医中誌 / Google Scholar で実在性を確認してください。\n\n")

        for num in cited_nums:
            ref_text = references.get(num, "ERROR: Reference not found")

            # 著者名を抽出
            author_match = re.match(r'^([A-Z][a-z]+(?:\s+[A-Z]{1,2})?(?:,\s+[A-Z][a-z]+\s+[A-Z]{1,2})?)', ref_text)
            if author_match:
                author = author_match.group(1).strip()
            else:
                # 組織名の場合
                author = ref_text.split('.')[0][:50]

            # 年を抽出
            year_match = re.search(r'\b(19|20)\d{2}\b', ref_text)
            year = year_match.group(0) if year_match else "N/A"

            # タイトルを抽出（簡易版）
            parts = ref_text.split('.')
            if len(parts) > 1:
                title = parts[1].strip() if len(parts) > 1 else ""
            else:
                title = ""

            f.write(f"### [{num}] {author} ({year})\n\n")
            f.write(f"**Full Citation**:\n")
            f.write(f"> {ref_text}\n\n")

            # Google Scholar検索リンク
            search_query = f"{author} {year} {title[:30]}".replace(' ', '+')
            f.write(f"**Google Scholar**: [Search]https://scholar.google.com/scholar?q={search_query})\n\n")

            f.write(f"**Verification Status**: [ ] 未確認\n\n")
            f.write(f"**Existence**: [ ] 実在確認 / [ ] 実在しない / [ ] 不明\n\n")
            f.write(f"**Comments**: \n\n")
            f.write("---\n\n")

        f.write("\n## 未引用の15件（参考）\n\n")
        f.write("これらの文献は本文中で引用されていないため、Vancouver Styleに従って削除する必要があります。\n\n")

        for num in uncited_nums:
            ref_text = references.get(num, "ERROR: Reference not found")
            author_match = re.match(r'^([A-Z][a-z]+(?:\s+[A-Z]{1,2})?)', ref_text)
            author = author_match.group(1).strip() if author_match else ref_text.split('.')[0][:50]
            year_match = re.search(r'\b(19|20)\d{2}\b', ref_text)
            year = year_match.group(0) if year_match else "N/A"

            f.write(f"- **[{num}]** {author} ({year})\n")

        f.write("\n---\n\n")
        f.write("## 次のステップ\n\n")
        f.write("1. 引用されている34件について、実在性を確認\n")
        f.write("2. 実在しない文献を特定\n")
        f.write("3. 未引用の15件を削除\n")
        f.write("4. 引用番号を1-34（または実在文献数）に再番号付け\n")

    print(f"\nCited references list created: {output_path}")
    print("\nNext steps:")
    print("  1. Open CITED_REFERENCES_LIST.md")
    print("  2. Verify each of the 34 cited references")
    print("  3. Mark non-existent references")
    print("  4. Report results for renumbering")
    print("=" * 80)

if __name__ == "__main__":
    main()
