#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手動検証用の参考文献リストを作成
"""

import re
from pathlib import Path

def extract_references(manuscript_path):
    """参考文献リストを抽出"""
    with open(manuscript_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    references = []
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
                    references.append({'num': current_num, 'text': current_text})

                current_num = int(match.group(1))
                current_text = match.group(2).strip()
            elif current_num is not None and line.strip():
                current_text += ' ' + line.strip()

    # 最後の文献を保存
    if current_num is not None:
        references.append({'num': current_num, 'text': current_text})

    return references

def main():
    base_dir = Path(__file__).parent
    manuscript_path = base_dir / "Manuscript_heatwave_social_isolation.qmd"
    output_path = base_dir / "MANUAL_VERIFICATION_LIST.md"

    print("=" * 80)
    print("Creating Manual Verification List")
    print("=" * 80)

    references = extract_references(manuscript_path)
    print(f"\nExtracted {len(references)} references")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# 参考文献の手動検証リスト\n\n")
        f.write("## 検証方法\n\n")
        f.write("各文献について、以下の手順で実在性を確認してください：\n\n")
        f.write("1. **PubMed** (https://pubmed.ncbi.nlm.nih.gov/) で検索\n")
        f.write("   - タイトルの一部 + 著者名で検索\n")
        f.write("   - 見つからない場合は次へ\n\n")
        f.write("2. **医中誌Web** (https://login.jamas.or.jp/) で検索\n")
        f.write("   - 日本語文献の場合\n\n")
        f.write("3. **Google Scholar** (https://scholar.google.com/) で検索\n")
        f.write("   - タイトルの一部 + 著者名で検索\n\n")
        f.write("4. **確認結果**\n")
        f.write("   - ✅ 実在確認 → チェックボックスにチェック\n")
        f.write("   - ❌ 実在しない → チェックボックスを空欄にし、コメント欄に「実在しない」と記入\n")
        f.write("   - ⚠️ 不明 → コメント欄に「要確認」と記入\n\n")
        f.write("---\n\n")
        f.write("## 参考文献リスト（49件）\n\n")

        for ref in references:
            num = ref['num']
            text = ref['text']

            # 著者名を抽出（最初の著者のみ）
            author_match = re.match(r'^([A-Z][a-z]+\s+[A-Z]{1,2}(?:,\s+[A-Z][a-z]+\s+[A-Z]{1,2})?)', text)
            if author_match:
                author = author_match.group(1).strip()
            else:
                author = text.split('.')[0][:30]  # 最初の30文字

            # 年を抽出
            year_match = re.search(r'\b(19|20)\d{2}\b', text)
            year = year_match.group(0) if year_match else "N/A"

            # タイトルを抽出（簡易版）
            parts = text.split('.')
            if len(parts) > 1:
                title = parts[1].strip()[:80]  # 最初の80文字
            else:
                title = text[:80]

            # チェックボックス付きで出力
            f.write(f"### [{num}] - [ ] {author} ({year})\n\n")
            f.write(f"**Full Citation**:\n")
            f.write(f"> {text}\n\n")
            f.write(f"**Search Keywords**: `{author} {year}`\n\n")
            f.write(f"**Verification Status**: _未確認_\n\n")
            f.write(f"**Comments**: \n\n")
            f.write("---\n\n")

    print(f"\nManual verification list created: {output_path}")
    print("\nNext steps:")
    print("  1. Open MANUAL_VERIFICATION_LIST.md")
    print("  2. For each reference, verify existence in PubMed/医中誌/Google Scholar")
    print("  3. Check the box [ ] → [x] if verified")
    print("  4. Add comments for non-existent or questionable references")
    print("  5. Share the results with Claude for next steps")
    print("=" * 80)

if __name__ == "__main__":
    main()
