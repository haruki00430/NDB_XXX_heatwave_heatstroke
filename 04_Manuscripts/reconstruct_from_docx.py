#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DOCXから抽出した54件の文献から、削除対象を除外して48件に再構築
"""

from docx import Document
from pathlib import Path
import re

# 削除対象の文献（段落番号で指定）
DELETE_PARAGRAPHS = {
    92,   # #4: Fujibe F.
    109,  # #21: Abatzoglou
    112,  # #24: Tominaga
    113,  # #25: Takagi
    124,  # #36: Oka K.
}

# 削除対象の著者名（確認用）
DELETE_AUTHORS = {
    "Fujibe F",
    "Abatzoglou JT",
    "Tominaga Y",
    "Takagi H",
    "Oka K",
}

def extract_references_from_docx(docx_path):
    """DOCXファイルから参考文献を抽出（段落89-142）"""
    doc = Document(docx_path)

    references = []
    ref_start = 89  # 段落89から開始
    ref_end = 142   # 段落142まで（54件）

    for i, para in enumerate(doc.paragraphs, 1):
        if ref_start <= i <= ref_end:
            text = para.text.strip()
            if text:
                references.append({
                    'paragraph_num': i,
                    'original_num': i - ref_start + 1,  # 元の文献番号（1-54）
                    'text': text
                })

    return references

def filter_references(references):
    """削除対象を除外"""
    filtered = []
    deleted = []
    log_lines = []

    for ref in references:
        para_num = ref['paragraph_num']
        text = ref['text']

        # 削除対象かチェック
        if para_num in DELETE_PARAGRAPHS:
            # 著者名で確認
            is_delete = False
            for author in DELETE_AUTHORS:
                if author in text:
                    deleted.append(ref)
                    is_delete = True
                    log_lines.append(f"  Deleted: #{ref['original_num']} (paragraph {para_num}): {author}")
                    break

            if not is_delete:
                log_lines.append(f"  Warning: paragraph {para_num} is marked for deletion but author name not matched")
                # それでも削除
                deleted.append(ref)
        else:
            filtered.append(ref)

    # ログを出力
    for line in log_lines:
        print(line)

    return filtered, deleted

def renumber_references(references):
    """1-48（または49）に再番号付け"""
    new_references = []

    for new_num, ref in enumerate(references, 1):
        new_ref = {
            'new_num': new_num,
            'old_num': ref['original_num'],
            'paragraph_num': ref['paragraph_num'],
            'text': f"{new_num}) {ref['text']}"
        }
        new_references.append(new_ref)

    return new_references

def create_mapping_table(new_references):
    """旧番号→新番号のマッピングテーブル"""
    mapping = {}
    for ref in new_references:
        mapping[ref['old_num']] = ref['new_num']
    return mapping

def main():
    docx_path = Path(__file__).parent / "Manuscript_heatwave_social_isolation.docx"

    print("=" * 60)
    print("DOCX から参考文献を再構築")
    print("=" * 60)

    # Step 1: DOCXから抽出
    print("\nStep 1: DOCXから参考文献を抽出中...")
    references = extract_references_from_docx(docx_path)
    print(f"  抽出された文献数: {len(references)}件（段落89-142）")

    # Step 2: 削除対象を除外
    print("\nStep 2: 削除対象を除外中...")
    filtered_refs, deleted = filter_references(references)
    print(f"  削除された文献数: {len(deleted)}件")
    print(f"  残り文献数: {len(filtered_refs)}件")

    # Step 3: 再番号付け
    print("\nStep 3: 1-{len(filtered_refs)}に再番号付け中...")
    new_references = renumber_references(filtered_refs)
    print(f"  新規番号: 1-{len(new_references)}")

    # Step 4: マッピングテーブル作成
    print("\nStep 4: マッピングテーブル作成中...")
    mapping = create_mapping_table(new_references)

    # マッピングテーブルを保存
    mapping_path = Path(__file__).parent / "reference_mapping_final.txt"
    with open(mapping_path, 'w', encoding='utf-8') as f:
        f.write("旧番号 → 新番号\n")
        f.write("=" * 30 + "\n")
        for old_num in sorted(mapping.keys()):
            new_num = mapping[old_num]
            shift = new_num - old_num
            f.write(f"{old_num:2d} → {new_num:2d} (shift: {shift:+d})\n")

    print(f"  マッピングテーブル保存: {mapping_path}")

    # Step 5: 新規参考文献リスト作成
    print("\nStep 5: 新規参考文献リスト作成中...")
    new_ref_section = "# References\n\n"
    for ref in new_references:
        new_ref_section += f"{ref['text']}\n"

    # ファイル保存
    new_ref_path = Path(__file__).parent / "references_final.txt"
    with open(new_ref_path, 'w', encoding='utf-8') as f:
        f.write(new_ref_section)

    print(f"  新規参考文献リスト保存: {new_ref_path}")

    # プレビュー（最初の5件）
    print("\n--- プレビュー（最初の5件）---")
    for ref in new_references[:5]:
        print(f"  [{ref['new_num']}] (元#{ref['old_num']})")
        print(f"    {ref['text'][:120]}...")

    # 統計情報
    print("\n" + "=" * 60)
    print("完了！")
    print("=" * 60)
    print(f"  元の文献数: {len(references)}件")
    print(f"  削除対象: {len(deleted)}件")
    print(f"  最終文献数: {len(new_references)}件")
    print(f"\n次のステップ:")
    print(f"  1. {new_ref_path} の内容を確認")
    print(f"  2. 原稿の参考文献セクション（行189以降）を置換")
    print(f"  3. {mapping_path} を参照して、本文中の引用番号を置換")
    print("=" * 60)

if __name__ == "__main__":
    main()
