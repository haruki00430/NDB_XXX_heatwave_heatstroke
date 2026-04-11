#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
引用箇所と参考文献を照合し、PubMed APIで実在性を確認
"""

import re
import time
import requests
from pathlib import Path
from typing import Dict, List, Tuple, Optional

def extract_citation_contexts(manuscript_path: Path) -> Dict[int, List[str]]:
    """本文中の引用箇所の文脈を抽出"""
    with open(manuscript_path, 'r', encoding='utf-8') as f:
        text = f.read()

    ref_idx = text.find('# References')
    if ref_idx == -1:
        return {}

    body_text = text[:ref_idx]
    contexts = {}

    # 引用パターン: ". XX)" または ", XX)"
    for match in re.finditer(r'([^.]{100}[.,]\s*)(\d+)\)([^.]{100})', body_text):
        num = int(match.group(2))
        if num < 100 and num > 0:
            context = match.group(1) + match.group(2) + ')' + match.group(3)

            # 統計値を除外
            if re.search(r'\(N\s*=\s*' + str(num), context):
                continue
            if re.search(r'p\s*[<>=]\s*0\.\d', context):
                continue
            if re.search(r'\d{1,3},\d{3}', context):
                continue

            if num not in contexts:
                contexts[num] = []
            contexts[num].append(context.strip())

    return contexts

def extract_references(manuscript_path: Path) -> Dict[int, Dict[str, str]]:
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
                    references[current_num] = parse_reference(current_text)

                current_num = int(match.group(1))
                current_text = match.group(2).strip()
            elif current_num is not None and line.strip():
                current_text += ' ' + line.strip()

    # 最後の文献を保存
    if current_num is not None:
        references[current_num] = parse_reference(current_text)

    return references

def parse_reference(text: str) -> Dict[str, str]:
    """参考文献テキストから著者・タイトル・雑誌・年を抽出"""
    ref = {
        'full_text': text,
        'first_author': '',
        'title': '',
        'journal': '',
        'year': ''
    }

    # 年（4桁の数字）
    year_match = re.search(r'\b(19|20)\d{2}\b', text)
    if year_match:
        ref['year'] = year_match.group(0)

    # Vancouver styleの構造: Author. Title. Journal. Year;volume(issue):pages.
    # または: Organization. Title. Location: Publisher; Year.

    # パターン1: 著者名 et al. タイトル. 雑誌名.
    author_match = re.match(r'^([A-Z][a-z]+\s+[A-Z]{1,2}(?:,\s+[A-Z][a-z]+\s+[A-Z]{1,2})*)', text)
    if author_match:
        ref['first_author'] = author_match.group(1).split(',')[0].strip()

        # 著者名の後からタイトルを抽出
        after_author = text[author_match.end():].strip()

        # タイトルは最初のピリオドまで（ただし、et al. は除く）
        title_match = re.match(r'^(?:,\s*et al\.\s*)?([^.]+)\.', after_author)
        if title_match:
            ref['title'] = title_match.group(1).strip()

            # タイトルの後から雑誌名を抽出
            after_title = after_author[title_match.end():].strip()
            journal_match = re.match(r'^([A-Z][^.]+)\.', after_title)
            if journal_match:
                ref['journal'] = journal_match.group(1).strip()

    # パターン2: Organization name (for government/international sources)
    elif re.match(r'^[A-Z][A-Za-z\s,]+\(', text):
        # 組織名が括弧の前まで
        org_match = re.match(r'^([^.(]+)', text)
        if org_match:
            ref['first_author'] = org_match.group(1).strip()

        # タイトルは最初のピリオドまで
        title_match = re.search(r'\.\s*([^.]+)\.', text)
        if title_match:
            ref['title'] = title_match.group(1).strip()

    return ref

def search_pubmed(title: str, author: Optional[str] = None, year: Optional[str] = None) -> Tuple[bool, Optional[str]]:
    """PubMed APIで文献を検索"""
    if not title or len(title) < 10:
        return False, "Title too short"

    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"

    # クエリ構築（タイトルの最初の100文字を使用、引用符なし）
    # 引用符なしにすることで部分一致を許可
    title_clean = title[:100].replace('"', '').replace('[', '').replace(']', '')
    query_parts = [f'{title_clean}[Title]']

    if author:
        # 著者名の姓のみを使用
        author_last = author.split()[0] if author.split() else author
        query_parts.append(f'{author_last}[Author]')

    if year:
        query_parts.append(f'{year}[Publication Date]')

    query = ' AND '.join(query_parts)

    params = {
        'db': 'pubmed',
        'term': query,
        'retmode': 'json',
        'retmax': 5
    }

    try:
        response = requests.get(base_url, params=params, timeout=10)
        time.sleep(0.4)  # Rate limiting (max 3 requests/sec)

        if response.status_code == 200:
            data = response.json()
            count = int(data['esearchresult']['count'])
            if count > 0:
                pmid = data['esearchresult']['idlist'][0] if data['esearchresult']['idlist'] else None
                return True, pmid
            else:
                return False, "Not found in PubMed"
        else:
            return False, f"HTTP {response.status_code}"
    except Exception as e:
        return False, str(e)

def analyze_context_topic(context: str) -> List[str]:
    """文脈からトピックを抽出"""
    topics = []

    keywords = {
        'climate': ['climate change', 'global warming', 'greenhouse gas', 'emission', 'IPCC'],
        'heat': ['heat wave', 'heat stroke', 'heat-related', 'heatstroke', 'heat illness', 'hot weather', 'high temperature', 'WBGT', 'ambient temperature'],
        'social_isolation': ['social isolation', 'living alone', 'solitary', 'loneliness', 'elderly living alone'],
        'vulnerability': ['vulnerable', 'susceptibility', 'risk factor', 'high-risk'],
        'aging': ['elderly', 'older', 'aging', 'aged', 'geriatric'],
        'mortality': ['mortality', 'death', 'fatal', 'died'],
        'epidemiology': ['ecological study', 'regression', 'correlation', 'association', 'statistic'],
        'policy': ['government', 'ministry', 'policy', 'prevention', 'measure'],
        'urban': ['urban', 'city', 'metropolitan', 'heat island']
    }

    context_lower = context.lower()
    for topic, kws in keywords.items():
        for kw in kws:
            if kw.lower() in context_lower:
                topics.append(topic)
                break

    return list(set(topics))

def match_reference_to_context(context_topics: List[str], reference: Dict[str, str]) -> float:
    """文脈のトピックと参考文献の関連性をスコアリング"""
    score = 0.0
    ref_text = reference['full_text'].lower()
    ref_title = reference['title'].lower()

    topic_keywords = {
        'climate': ['climate', 'ipcc', 'warming'],
        'heat': ['heat', 'temperature', 'thermal'],
        'social_isolation': ['social', 'isolation', 'alone', 'loneliness'],
        'vulnerability': ['vulnerability', 'susceptible', 'risk'],
        'aging': ['elderly', 'older', 'aging', 'aged'],
        'mortality': ['mortality', 'death', 'fatal'],
        'epidemiology': ['ecological', 'epidemiol', 'regression', 'statistic'],
        'policy': ['government', 'ministry', 'policy', 'prevention'],
        'urban': ['urban', 'city', 'heat island']
    }

    for topic in context_topics:
        if topic in topic_keywords:
            for kw in topic_keywords[topic]:
                if kw in ref_title:
                    score += 2.0  # タイトルに含まれる場合は高スコア
                elif kw in ref_text:
                    score += 0.5

    return score

def main():
    base_dir = Path(__file__).parent
    manuscript_path = base_dir / "Manuscript_heatwave_social_isolation.qmd"
    output_path = base_dir / "reference_verification_results.txt"

    print("=" * 80)
    print("Reference Verification and Matching")
    print("=" * 80)

    # Step 1: 引用箇所の文脈を抽出
    print("\nStep 1: Extracting citation contexts...")
    contexts = extract_citation_contexts(manuscript_path)
    print(f"  Found {len(contexts)} citation numbers")

    # Step 2: 参考文献リストを抽出
    print("\nStep 2: Extracting references...")
    references = extract_references(manuscript_path)
    print(f"  Found {len(references)} references")

    # Step 3: 各引用箇所のトピックを分析
    print("\nStep 3: Analyzing context topics...")
    citation_topics = {}
    for num, ctx_list in contexts.items():
        topics = []
        for ctx in ctx_list:
            topics.extend(analyze_context_topic(ctx))
        citation_topics[num] = list(set(topics))

    # Step 4: PubMed APIで参考文献を検証
    print("\nStep 4: Verifying references in PubMed...")
    print("  (This may take 1-2 minutes...)")

    verification_results = {}
    for num, ref in references.items():
        print(f"  Checking #{num}: {ref['first_author']} ({ref['year']})...", end='')

        # 政府機関・国際機関はスキップ
        if any(org in ref['full_text'] for org in ['Ministry', 'Agency', 'IPCC', 'CDC', 'WHO']):
            verification_results[num] = {'verified': True, 'source': 'Government/International', 'pmid': None}
            print(" [Government/International - OK]")
            continue

        # 書籍はスキップ
        if 'Press' in ref['full_text'] or 'Publishers' in ref['full_text']:
            verification_results[num] = {'verified': True, 'source': 'Book', 'pmid': None}
            print(" [Book - OK]")
            continue

        # PubMed検索
        found, pmid = search_pubmed(ref['title'], ref['first_author'], ref['year'])
        verification_results[num] = {
            'verified': found,
            'source': 'PubMed' if found else 'Not found',
            'pmid': pmid
        }

        if found:
            print(f" [PubMed PMID:{pmid} - OK]")
        else:
            print(f" [NOT FOUND in PubMed - {pmid}]")

    # Step 5: 引用箇所と参考文献をマッチング
    print("\nStep 5: Matching citations to references...")
    matches = {}
    for cite_num in sorted(citation_topics.keys()):
        topics = citation_topics[cite_num]
        best_match = None
        best_score = 0.0

        for ref_num, ref in references.items():
            score = match_reference_to_context(topics, ref)
            if score > best_score:
                best_score = score
                best_match = ref_num

        matches[cite_num] = {
            'current_ref': cite_num,
            'suggested_ref': best_match,
            'score': best_score,
            'topics': topics,
            'contexts': contexts[cite_num]
        }

    # Step 6: 結果を出力
    print("\nStep 6: Writing results...")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("Reference Verification and Matching Results\n")
        f.write("=" * 80 + "\n\n")

        # セクション1: PubMed検証結果
        f.write("## Section 1: PubMed Verification Results\n")
        f.write("-" * 80 + "\n\n")

        not_found = []
        for num in sorted(references.keys()):
            ref = references[num]
            result = verification_results[num]

            f.write(f"#{num}: {ref['first_author']} ({ref['year']})\n")
            f.write(f"  Title: {ref['title'][:80]}...\n")
            f.write(f"  Verification: {result['source']}")
            if result['pmid']:
                f.write(f" (PMID: {result['pmid']})")
            f.write("\n")

            if not result['verified'] and result['source'] == 'Not found':
                not_found.append(num)

            f.write("\n")

        # セクション2: PubMedで見つからなかった文献
        f.write("\n## Section 2: References NOT Found in PubMed\n")
        f.write("-" * 80 + "\n\n")

        if not_found:
            f.write(f"Total: {len(not_found)} references\n\n")
            for num in not_found:
                ref = references[num]
                f.write(f"#{num}: {ref['first_author']} ({ref['year']})\n")
                f.write(f"  {ref['full_text'][:150]}...\n\n")
        else:
            f.write("All references verified!\n\n")

        # セクション3: 引用箇所と参考文献のマッチング
        f.write("\n## Section 3: Citation-Reference Matching\n")
        f.write("-" * 80 + "\n\n")

        for cite_num in sorted(matches.keys()):
            match = matches[cite_num]
            f.write(f"Citation #{cite_num}\n")
            f.write(f"  Topics: {', '.join(match['topics'])}\n")
            f.write(f"  Current reference: #{match['current_ref']}\n")
            f.write(f"  Suggested match: #{match['suggested_ref']} (score: {match['score']:.1f})\n")
            f.write(f"  Context (first occurrence):\n")
            f.write(f"    {match['contexts'][0][:150]}...\n")

            # 現在の参考文献と提案された参考文献が異なる場合は警告
            if match['current_ref'] != match['suggested_ref']:
                f.write(f"  ⚠️ WARNING: Mismatch detected!\n")
                f.write(f"    Current: {references[match['current_ref']]['first_author']} ({references[match['current_ref']]['year']})\n")
                if match['suggested_ref'] is not None:
                    f.write(f"    Suggested: {references[match['suggested_ref']]['first_author']} ({references[match['suggested_ref']]['year']})\n")
                else:
                    f.write(f"    Suggested: None (no match found)\n")

            f.write("\n")

    print("\n" + "=" * 80)
    print("Verification Complete!")
    print("=" * 80)
    print(f"\nResults written to: {output_path}")
    print(f"\nSummary:")
    print(f"  Total references: {len(references)}")
    print(f"  Verified in PubMed: {sum(1 for r in verification_results.values() if r['verified'])}")
    print(f"  NOT found: {len(not_found)}")
    print(f"\nPlease review the results and:")
    print(f"  1. Check references NOT found in PubMed (may need manual verification)")
    print(f"  2. Review citation-reference mismatches")
    print(f"  3. Confirm which references should be kept")
    print("=" * 80)

if __name__ == "__main__":
    main()
