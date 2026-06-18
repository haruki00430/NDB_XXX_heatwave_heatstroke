# 次ステップ工程書・チェックリスト
## Are Heat-Health Systems Socially Blind? — 残作業
**作成日**: 2026-06-17

---

## 優先度別タスク一覧

### 🔴 優先度A（投稿前に必須）

---

#### A-1｜患者調査R5 negative control解析（コメント#21対応）

**目的**: 高齢者単独世帯率と「一般外来受療率」の関連が弱い・非有意であることを示し、点滴療法との関連が一般的医療受診行動の反映ではないことを確認する。

**データ**: 取得済み
- `02_Data/raw/patient_survey_r5_t36_pref_age.csv`（Shift-JIS、2,070行）
- 外来受療率（総数）：各都道府県の「総数,総数,…」行の第6列目（入院総数・病院・一般診療所・**外来総数**・病院・一般診療所・歯科の順）

**実施手順**:
1. CSVを解析し、都道府県別の外来受療率（総数、per 100,000）を抽出
2. 主解析データセット（`population_adjusted_dataset.csv`）とマージ
3. 回帰①：高齢者単独世帯率 → 外来受療率（負の対照）
4. 回帰②：比較用として高齢者単独世帯率 → 点滴療法率（既存結果の再掲）
5. 2つの散布図を並べた比較図を作成（figS2相当）
6. 結果をResults・Limitationsに追記

**期待する結果（仮説）**:
- 外来受療率への回帰：非有意（またはβが点滴より大幅に小さい）→ 点滴療法の関連は一般受診行動ではなく脱水特異的である根拠となる
- もし有意であれば：Limitationsにその旨を正直に記載する

**スクリプト作成先**: `03_Analysis/analysis/09_negative_control_outpatient.py`

**出力先**: `03_Analysis/results/negative_control/`

**論文への反映**:
- Results に新セクション「7. Negative Control: Outpatient Utilization Rate」を追加（または既存Results 6に統合）
- Limitations の「General outpatient utilization was not examined...」文を実際の結果に基づいて書き換える
- 比較図をSupplementary Figure S2として追加

- [ ] CSVの構造確認・パーサー実装
- [ ] 都道府県名の統一（患者調査名 ↔ 主解析データ）
- [ ] 回帰実施・結果確認
- [ ] 比較図作成（300dpi PNG）
- [ ] QMD修正（Results・Limitations）
- [ ] DOCX再レンダリング

---

#### A-2｜G004文献追加（コメント#13対応）

**対象文**:
> "We extracted claims for infusion procedures involving ≥500 mL volume (procedure code: G004), commonly used for rehydration in moderate-to-severe dehydration from heat illness or other acute conditions."

**推奨参照**: 既存Reference 11（Bouchama & Knochel, 2002, NEJM）

- 引用後の文末: `...other acute conditions.11)`

**代替案**: 日本救急医学会「熱中症診療ガイドライン2015」（書誌情報が確認できれば参考文献として追加し、別番号を付番する）

- [ ] 引用する文献を決定（Bouchama ref.11 or 新規文献）
- [ ] QMDの当該文末に参照番号を追記
- [ ] 新規文献の場合：Referencesリストに追加・番号整合確認
- [ ] DOCX再レンダリング

---

#### A-3｜Limitations B1文の追加確認

**背景**: 対応案（RP版）のLimitations第7パラ末尾に存在するが、現MS版に未反映の一文。

**該当文**:
> "The present findings should be interpreted as evidence for surveillance prioritization rather than causal evidence of heat-related illness."

**現在の第7パラ末尾（MS版）**:
> "...the extreme lower range observed in this study (26.6% in one prefecture) likely reflects historical underuse in cold-climate prefectures that may have changed in recent years."

**判断**: 研究の解釈的枠組みを明示する重要な一文。Conclusions削除（M9）と整合する形でLimitationsに残すことが推奨される。

- [ ] 追加するか否かをユーザーが最終判断
- [ ] 追加する場合：第7パラ末尾に1文を追記
- [ ] DOCX再レンダリング

---

### 🟡 優先度B（投稿準備として推奨）

---

#### B-1｜後付セクションの確認（RP版にあってMS版にないもの）

RP版（対応案ファイル）には以下のセクションが含まれているが、現在のMS版QMDには存在しない。投稿時に必要かどうか確認・追加が必要。

| セクション | 内容 | 状況 |
|-----------|------|------|
| Acknowledgments | NDBオープンデータ提供への謝辞 | RP版にあり、MS版にない |
| Conflicts of Interest | 「著者らは利益相反なし」 | RP版にあり、MS版にない |
| Data Availability | NDBデータの公開情報 | RP版にあり、MS版にない |
| Author Contributions | Haruki Saito の貢献区分 | RP版にあり、MS版にない |
| Funding | 「None declared.」 | RP版にあり、MS版にない |
| AI Disclosure | Claude・GPT等の使用開示 | RP版にあり、MS版にない |

- [ ] 各セクションを投稿規定（Journal of Epidemiology 等）に照らして確認
- [ ] 必要なセクションをQMDに追加
- [ ] AI Disclosure は投稿先の方針に合わせて文言調整

---

#### B-2｜査読コメント回答文の完成

現在のセッションで5件のドラフトを作成済み。最終化に向けて以下を確認。

| コメント | 回答ドラフト | 追記要否 |
|---------|-------------|---------|
| #1 投稿先 | 完成 | 投稿先確定後に誌名を確定 |
| #13 アウトカム特異性 | 完成 | A-2（G004文献）対応後に文献番号を記入 |
| #16 熱曝露指標 | 完成 | 解析B結果は反映済み |
| #21 単変量解析・受療率 | ドラフト | **A-1（患者調査解析）の実施後に大幅更新が必要** |
| #38 強い表現 | 完成 | 修正前後の文章対比あり |

- [ ] A-1完了後、コメント#21の回答文を実際の解析結果に基づいて更新
- [ ] A-2完了後、コメント#13の回答文に文献番号を追記
- [ ] 投稿先確定後、コメント#1の回答文に誌名を記入
- [ ] 全5件を1つのResponse letterドキュメントにまとめる

---

#### B-3｜タイトルの最終確認（manuscript-revision skill Step 5）

現在のタイトル：
> "Are Heat-Health Systems Socially Blind? Social Isolation and Dehydration-Related Healthcare Utilization Across Japan"

追加解析後に以下を確認：
- 「patients survey negative control」追加後もタイトルとの整合性があるか
- サブタイトルに「ecological study」等の研究デザイン明示を加えるか（Journal of Epidemiology 等は推奨）

- [ ] 最終Results・Conclusionsを再読してタイトルとの整合を確認
- [ ] 必要に応じてサブタイトルに「: A Nationwide Ecological Study」等を追加検討

---

### 🟢 優先度C（最終仕上げ）

---

#### C-1｜最終DOCX レンダリング

A-1〜A-3・B-1 の修正がすべて完了した段階で実施。

```bash
quarto render 04_Manuscripts/Manuscript_heatwave_social_isolation_final.qmd --to docx
```

- [ ] 全修正完了を確認
- [ ] `quarto render` 実行
- [ ] 図の解像度・表の書式を目視確認
- [ ] ページ数・文字数を投稿規定と照合

---

#### C-2｜投稿前セキュリティチェックリスト

manuscript-revision skill および security_and_reproducibility.md に基づく確認。

- [ ] NDB実データがファイルに含まれていないか
- [ ] `02_Data/raw/` を変更していないか
- [ ] `.gitignore` に設定フォルダが含まれているか
- [ ] 全解析スクリプトが `03_Analysis/analysis/` に保存されているか
- [ ] 参考文献が初登場順に番号付けされているか
- [ ] Abstractに引用番号がないか
- [ ] 図の解像度が 300 dpi 以上か

---

## 作業フロー（推奨順序）

```
A-2（G004文献追加）           ← 短時間で完了
    ↓
A-1（患者調査R5解析）          ← メイン作業（データ解析＋論文反映）
    ↓
A-3（Limitations B1文確認）   ← ユーザー判断後に即時実施
    ↓
B-1（後付セクション追加）      ← 投稿規定確認後
    ↓
B-2（回答文最終化）            ← A-1完了後に#21回答を更新
    ↓
C-1（DOCX最終レンダリング）   ← 全修正完了後
    ↓
C-2（投稿前チェック）          ← 投稿直前
```

---

*本工程書は 2026-06-17 時点の状況に基づく。作業の進捗に応じて適宜更新すること。*
