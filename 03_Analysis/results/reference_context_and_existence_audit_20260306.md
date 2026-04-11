# Reference Audit (2026-03-06)

対象ファイル:
- C:\Users\user\SharedWorkspace\projects\NDB_Research_Hub\projects\NDB_XXX_heatwave_heatstroke\04_Manuscripts\Manuscript_heatwave_social_isolation.qmd

## 1) 実在確認（PubMed API / Google Scholar）

### PubMed API集計
- Matched: 17件（PMID取得）
- Non-journal/report; PubMed not expected: 8件
- No clear PubMed match: 9件

詳細CSV:
- C:\Users\user\SharedWorkspace\projects\NDB_Research_Hub\projects\NDB_XXX_heatwave_heatstroke\03_Analysis\results\reference_validation_summary_20260306.csv

### Google Scholar
- この実行環境ではGoogle ScholarがreCAPTCHAを返し、自動照合は不可。
- Scholar照合ステータスは全件 `Blocked by reCAPTCHA (automated check unavailable)` として記録。

備考:
- PubMed非収載は「実在しない」ことを意味しない（行政資料、書籍、工学系誌など）。

## 2) 文脈妥当性監査（主要な不一致）

1. 重複文献
- Ref 17 と Ref 33 が同一文献（Semenza et al., NEJM 1996）で重複。
- 参照位置: References 208行, 224行

2. Ref 34 の文脈不一致
- Ref 34 は「日本47都道府県の救急搬送と気温の生態学的研究」だが、以下の文脈で引用されており整合しない。
- 139行: デジタル情報アクセス不足
- 147行: 都市ヒートアイランド等の微小スケール曝露
- 153行: 見守りプログラム推奨
- 171行: 微小スケール曝露の限界
- 173行: COVID-19期の救急受診減少

3. Ref 33 の文脈不一致
- Ref 33（Semenza 1996）はChicago熱波死亡研究であり、以下の政策主張の直接根拠としては不適切。
- 149行: 低高齢化地域での社会基盤差
- 157行: 冷房費補助施策の根拠

4. Ref 19 の文脈不一致
- Ref 19（redlining/heat islands）は都市環境格差に関するレビューで、以下の主張には直接対応しない。
- 139行: 高齢単身者のデジタル情報受信困難
- 159行: 低リテラシー向け情報伝達チャネル

5. Ref 29 の文脈不一致
- Ref 29（警察庁の2018熱中症死報告）が、以下の主張に用いられており不一致。
- 147行: 地域の行動適応文化による気候-健康関係の減弱
- 155行: CDC Heat Vulnerability Index の説明

6. Ref 31 の文脈不一致
- Ref 31（2003年イタリア熱波死亡研究）が、以下の主張の直接根拠としては弱い。
- 153行: 日本の行動計画の具体内容
- 167行: 生態学的誤謬の一般論

7. 実在性に追加注意が必要な参照
- Ref 4 はPubMedで一致せず、書誌情報の真偽確認が必要。
- Ref 21, 25 などもPubMed一致なし（誌面・DOIの再確認推奨）。

## 3) 文字化け対応

- qmd本文とReferencesの文字化けを除去済み。
- 確認結果: 代表的な化け文字（窶 / ﾂ / 竕 / 竏 など）0件。

