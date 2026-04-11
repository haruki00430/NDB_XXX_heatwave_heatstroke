#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
原稿の参考文献セクションを新規リストで置換
"""

from pathlib import Path

def main():
    # ファイルパス
    manuscript_path = Path(__file__).parent / "Manuscript_heatwave_social_isolation.qmd"
    new_ref_path = Path(__file__).parent / "references_final.txt"

    # 新規参考文献リストを読み込み
    with open(new_ref_path, 'r', encoding='utf-8') as f:
        new_references = f.read()

    # 原稿を読み込み
    with open(manuscript_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # References セクションの開始位置を特定（行189）
    ref_start = None
    for i, line in enumerate(lines):
        if line.strip() == "# References":
            ref_start = i
            break

    if ref_start is None:
        print("エラー: # References セクションが見つかりません")
        return

    # 行1-188（本文）+ 新規参考文献リスト
    new_content = ''.join(lines[:ref_start]) + new_references

    # 原稿を上書き
    with open(manuscript_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print("=" * 60)
    print("参考文献セクション置換完了！")
    print("=" * 60)
    print(f"  原稿: {manuscript_path}")
    print(f"  行1-{ref_start}: 本文（保持）")
    print(f"  行{ref_start + 1}以降: 新規参考文献リスト（49件）")
    print("=" * 60)

if __name__ == "__main__":
    main()
