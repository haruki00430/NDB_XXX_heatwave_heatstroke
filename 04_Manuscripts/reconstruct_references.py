#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
参考文献リストの再構築スクリプト

破損した参考文献リストから、重複を除去し、削除対象を除外して、
1-48の連番で再構築します。
"""

import re
from pathlib import Path

# 削除対象の文献（著者名で識別）
DELETE_AUTHORS = [
    "Sasaki H",      # 旧#4（行194） - 経済負担の論文、元の#4は削除対象
    "Tominaga Y",    # 旧#24 - CFD論文
]

def parse_reference_section(file_path):
    """参考文献セクションをパースする"""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 参考文献セクションの開始・終了を特定
    ref_start = None
    for i, line in enumerate(lines):
        if line.strip() == "# References":
            ref_start = i
            break

    if ref_start is None:
        raise ValueError("# References セクションが見つかりません")

    # 参考文献を抽出（空行で区切られる）
    references = {}  # {番号: 文献内容}
    current_num = None
    current_ref = []

    for line in lines[ref_start + 2:]:  # "# References"と空行の後から
        # 番号パターン: "1) Author..."
        match = re.match(r'^(\d+)\)\s+(.+)$', line)
        if match:
            # 前の文献を保存
            if current_num is not None and current_ref:
                ref_text = ''.join(current_ref)
                # 重複の場合、最初の出現のみ保持
                if current_num not in references:
                    references[current_num] = ref_text

            # 新しい文献を開始
            current_num = int(match.group(1))
            current_ref = [line]
        elif current_num is not None:
            # 継続行
            current_ref.append(line)

    # 最後の文献を保存
    if current_num is not None and current_ref:
        ref_text = ''.join(current_ref)
        if current_num not in references:
            references[current_num] = ref_text

    return references, ref_start, lines

def filter_references(references):
    """削除対象を除外"""
    filtered = {}
    deleted = []

    for num, ref in references.items():
        # 削除対象かチェック
        is_delete = False
        for author in DELETE_AUTHORS:
            if author in ref:
                deleted.append((num, author, ref[:100]))
                is_delete = True
                break

        if not is_delete:
            filtered[num] = ref

    return filtered, deleted

def renumber_references(references):
    """1-48に再番号付け"""
    # 元の番号順にソート
    sorted_refs = sorted(references.items(), key=lambda x: x[0])

    # 新番号を割り当て
    new_references = []
    for new_num, (old_num, ref) in enumerate(sorted_refs, start=1):
        # 番号を置換（最初の番号のみ）
        ref_modified = re.sub(r'^\d+\)', f'{new_num})', ref, count=1)
        new_references.append({
            'new_num': new_num,
            'old_num': old_num,
            'content': ref_modified
        })

    return new_references

def create_mapping_table(new_references):
    """旧番号→新番号のマッピングテーブル"""
    mapping = {}
    for ref in new_references:
        mapping[ref['old_num']] = ref['new_num']
    return mapping

def main():
    # ファイルパス
    manuscript_path = Path(__file__).parent / "Manuscript_heatwave_social_isolation.qmd"

    print("=" * 60)
    print("参考文献リスト再構築スクリプト")
    print("=" * 60)

    # Step 1: パース
    print("\nStep 1: 参考文献セクションをパース中...")
    references, ref_start, lines = parse_reference_section(manuscript_path)
    print(f"  - 抽出された文献数: {len(references)}件")
    print(f"  - 参考文献セクション開始行: {ref_start + 1}")

    # Step 2: 削除対象を除外
    print("\nStep 2: 削除対象を除外中...")
    filtered_refs, deleted = filter_references(references)
    print(f"  - 削除された文献数: {len(deleted)}件")
    for num, author, preview in deleted:
        print(f"    - #{num}: {author} - {preview}...")
    print(f"  - 残り文献数: {len(filtered_refs)}件")

    # Step 3: 再番号付け
    print("\nStep 3: 1-48に再番号付け中...")
    new_references = renumber_references(filtered_refs)
    print(f"  - 新規番号: 1-{len(new_references)}")

    # Step 4: マッピングテーブル作成
    print("\nStep 4: マッピングテーブル作成中...")
    mapping = create_mapping_table(new_references)
    print(f"  - マッピング数: {len(mapping)}件")

    # マッピングテーブルを保存
    mapping_path = Path(__file__).parent / "reference_mapping.txt"
    with open(mapping_path, 'w', encoding='utf-8') as f:
        f.write("旧番号 → 新番号\n")
        f.write("=" * 30 + "\n")
        for old_num in sorted(mapping.keys()):
            new_num = mapping[old_num]
            shift = new_num - old_num
            f.write(f"{old_num:2d} → {new_num:2d} (shift: {shift:+d})\n")

    print(f"  - マッピングテーブル保存: {mapping_path}")

    # Step 5: 新規参考文献リスト作成
    print("\nStep 5: 新規参考文献リスト作成中...")
    new_ref_section = "# References\n\n"
    for ref in new_references:
        new_ref_section += ref['content']

    # ファイル保存
    new_ref_path = Path(__file__).parent / "references_reconstructed.txt"
    with open(new_ref_path, 'w', encoding='utf-8') as f:
        f.write(new_ref_section)

    print(f"  - 新規参考文献リスト保存: {new_ref_path}")

    # 統計情報
    print("\n" + "=" * 60)
    print("完了！")
    print("=" * 60)
    print(f"  元の文献数（重複含む）: {len(references)}件")
    print(f"  削除対象: {len(deleted)}件")
    print(f"  最終文献数: {len(new_references)}件")
    print(f"\n次のステップ:")
    print(f"  1. {new_ref_path} の内容を確認")
    print(f"  2. 原稿の参考文献セクション（行{ref_start + 1}以降）を置換")
    print(f"  3. {mapping_path} を参照して、本文中の引用番号を置換")
    print("=" * 60)

if __name__ == "__main__":
    main()
