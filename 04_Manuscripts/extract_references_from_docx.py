#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DOCXファイルから参考文献を抽出するスクリプト
"""

from docx import Document
from pathlib import Path
import re

def extract_references_from_docx(docx_path):
    """DOCXファイルから参考文献セクションを抽出"""
    doc = Document(docx_path)

    references = []
    in_references = False
    current_ref = []

    for para in doc.paragraphs:
        text = para.text.strip()

        # "References"セクションの開始を検出
        if text == "References" or text.startswith("# References"):
            in_references = True
            continue

        if in_references:
            # 番号パターン: "1) Author..."
            if re.match(r'^\d+\)', text):
                # 前の文献を保存
                if current_ref:
                    references.append('\n'.join(current_ref))
                # 新しい文献を開始
                current_ref = [text]
            elif text and current_ref:
                # 継続行
                current_ref.append(text)
            elif not text and not current_ref:
                # 空行（文献間）
                continue

    # 最後の文献を保存
    if current_ref:
        references.append('\n'.join(current_ref))

    return references

def main():
    docx_path = Path(__file__).parent / "Manuscript_heatwave_social_isolation.docx"

    print("=" * 60)
    print("DOCXから参考文献抽出")
    print("=" * 60)

    if not docx_path.exists():
        print(f"エラー: {docx_path} が見つかりません")
        return

    print(f"\nファイル: {docx_path}")

    # 参考文献を抽出
    print("\n参考文献を抽出中...")
    references = extract_references_from_docx(docx_path)

    print(f"抽出された文献数: {len(references)}件")

    # ファイルに保存
    output_path = Path(__file__).parent / "references_from_docx.txt"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# References\n\n")
        for ref in references:
            f.write(f"{ref}\n")

    print(f"\n保存先: {output_path}")

    # プレビュー（最初の3件）
    print("\n--- プレビュー（最初の3件）---")
    for i, ref in enumerate(references[:3], 1):
        print(f"\n[{i}]")
        print(ref[:150] + "..." if len(ref) > 150 else ref)

    print("\n" + "=" * 60)
    print("完了！")
    print("=" * 60)

if __name__ == "__main__":
    main()
