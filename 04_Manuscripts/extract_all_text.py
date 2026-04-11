#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DOCXファイルから全テキストを抽出
"""

from docx import Document
from pathlib import Path
import re

def extract_all_text(docx_path):
    """DOCXファイルから全テキストを抽出"""
    doc = Document(docx_path)

    all_text = []
    for para in doc.paragraphs:
        all_text.append(para.text)

    return '\n'.join(all_text)

def extract_references_section(text):
    """Referencesセクションを抽出"""
    # "References"セクションを探す
    match = re.search(r'References\s*\n(.*)', text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None

def parse_references(ref_text):
    """参考文献をパース"""
    references = []
    lines = ref_text.split('\n')

    current_ref = []
    for line in lines:
        line = line.strip()
        # 番号パターン: "1) Author..."
        if re.match(r'^\d+\)', line):
            # 前の文献を保存
            if current_ref:
                references.append(' '.join(current_ref))
            # 新しい文献を開始
            current_ref = [line]
        elif line and current_ref:
            # 継続行
            current_ref.append(line)

    # 最後の文献を保存
    if current_ref:
        references.append(' '.join(current_ref))

    return references

def main():
    docx_path = Path(__file__).parent / "Manuscript_heatwave_social_isolation.docx"
    output_path = Path(__file__).parent / "references_extracted.txt"

    print("=" * 60)
    print("DOCXから全テキスト抽出")
    print("=" * 60)

    if not docx_path.exists():
        print(f"エラー: {docx_path} が見つかりません")
        return

    # 全テキストを抽出
    print("\n全テキストを抽出中...")
    text = extract_all_text(docx_path)
    print(f"総文字数: {len(text)}")

    # Referencesセクションを抽出
    print("\nReferencesセクションを抽出中...")
    ref_section = extract_references_section(text)

    if ref_section:
        print(f"Referencesセクションのサイズ: {len(ref_section)} 文字")

        # 参考文献をパース
        print("\n参考文献をパース中...")
        references = parse_references(ref_section)
        print(f"抽出された文献数: {len(references)}件")

        # ファイルに保存
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# References\n\n")
            for i, ref in enumerate(references, 1):
                f.write(f"{ref}\n")

        print(f"\n保存先: {output_path}")

        # プレビュー（最初の5件）
        print("\n--- プレビュー（最初の5件）---")
        for i, ref in enumerate(references[:5], 1):
            print(f"\n[{i}]")
            print(ref[:200] + "..." if len(ref) > 200 else ref)

    else:
        print("エラー: Referencesセクションが見つかりませんでした")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
