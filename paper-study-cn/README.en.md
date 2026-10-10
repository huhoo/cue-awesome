# paper-study-cn

**English companion of `README.md` (Chinese primary; the pair is for reading inside the repository — skill-channel pages do not resolve relative links, so this is deliberately not a clickable switch).**

**Turn the paper at hand into a checkable study card: every claim carries a page or section anchor, reproducibility gaps are named one by one, the citation list only holds what the paper itself cites, and academic judgement stays marked `[待人工]`.**

Not a writing service, not a literature mover. This skill does the other half of the job: making the paper actually readable - every point locatable, every citation traceable. Paper input comes two ways only: the file you provide and a publicly reachable link.

**Input**: a public PDF URL / a local file path / pasted text - one card per paper
**Output**: one filled-in `assets/论文研读卡.md` card - paper card, reproducibility list, citation network, review scaffold, pending list
**Cost**: the first two parts depend only on the file actually read this time; the citation network and scaffold material are fetched on demand
**Machine gate**: `scripts/check_study_card.py`, four lanes (format / anchors / red lines / counts and declarations), zero network

---

## 1. Open it and work: three steps today

These three are the only "do it now" part. The first sentence can be copied verbatim: **"read this paper, give me the paper card and the reproducibility list first"**.

| Step | Action | How | What happens if you skip it |
|---|---|---|---|
| 1 | **Hand over the source, copy the edition** | Give the PDF path or link; take title, authors and volume/issue **from inside the paper**, and write `缺` (absent) when the text does not say | Nobody can tell which version was read, and every later anchor may belong to a different preprint or final edition |
| 2 | **Anchor every row of the paper card** | Add a page or section locator to claim, method, data and conclusion (P3, page 8, section 4, references); delete any row whose locator you cannot supply | Points cannot be traced back to sentences, citation checking turns into impression, and that is exactly how invention enters |
| 3 | **Run the gate before quoting** | `python3 scripts/check_study_card.py my-card.md`, then fix each detail line by its `E-*` code | Hedged figures, unanchored citations and unconfirmed inferred slots travel into your manuscript, and no one can check them for you |

The citation network and the review scaffold come **after** these three: the first is bounded by this package's search surface (section 7), the second needs your own thesis slots.

## 2. The five parts and the four lanes

| Part | Content | What the gate enforces |
|---|---|---|
| 1 Paper card | Title, authors, year, core claim, method, data, conclusion - one anchor per row; absent fields written as `缺` with `不适用` in the anchor cell | Content without anchor -> `E-ANCHOR`; an anchor number beyond the page set on the card (e.g. `P99` when the set says 共 13 页) -> `E-ANCHOR`; hedged numbers -> `E-BANWORD` |
| 2 Reproducibility list | Dataset availability, whether a code link exists, parameter completeness - **gaps only, never a verdict on reproducibility** | Fewer than three accounted items -> `E-COVERAGE`; "`应该能复现`" style claims -> `E-BANWORD` |
| 3 Citation network | Entries taken only from the paper's own reference list, each with a locator; citation counts declared when not retrieved | Entry without locator -> `E-ANCHOR`; neither entries nor a ticked declaration -> `E-COVERAGE` |
| 4 Review scaffold | Thesis slots belong to the user: given by them, or inferred and then explicitly confirmed; material sentences must be anchored, otherwise leave `空槽（不硬填）` | Unanchored material -> `E-ANCHOR`; unconfirmed inferred slot or unticked origin -> `E-COVERAGE` |
| 5 Pending list | Everything that needs the original text, with academic judgement under `[待人工]` | Missing the `[待人工]` roll-up -> `E-COVERAGE` |

The header has its own hard set: **the three self-labels** (`AI 研读整理`, `观点请回原文核对`, `不构成学术评价`) **plus** the file this read is based on, the paper edition (or `缺`), and the **channel page set** - whatever the parse echoed, written as `共 N 页`; when it is not available write `未取` and declare `页集比对跳过` on the same line. Any of them missing or still a placeholder is an `E-FORMAT`. When the page set is recorded, the gate compares every page anchor against it - **an anchor beyond the set fires `E-ANCHOR`**; a missing set without that declaration fires `E-COVERAGE`.

## 3. Getting started

```bash
# 1. Put it in the skills directory
mkdir -p ~/.workbuddy/skills
cp -r paper-study-cn ~/.workbuddy/skills/

# 2. Copy the card template and fill it following section 1
cp ~/.workbuddy/skills/paper-study-cn/assets/论文研读卡.md ./my-card.md

# 3. Run the gate (no network)
python3 ~/.workbuddy/skills/paper-study-cn/scripts/check_study_card.py ./my-card.md
```

Read `assets/论文研读卡.md` first (that is the five-part shape), then `SKILL.md` §3 for the contract itself.

### Self-check

```bash
python3 scripts/check_study_card.py --help                            # usage; no network
python3 scripts/check_study_card.py --selftest                        # good sample must pass, bad sample must fire all four lanes
python3 scripts/check_study_card.py scripts/fixtures/good-study-card.md   # should PASS
python3 scripts/check_study_card.py scripts/fixtures/bad-study-card.md    # should FAIL, all four codes
python3 scripts/check_study_card.py assets/论文研读卡.md                   # should FAIL - a blank card failing the gate is the design, not a defect
```

**Take every count from the script's own report line** (`FAIL: … (N items)` and the `扫过 N 行，发条 0 条` line under `PASS:`); this file does not restate them - a restated count becomes a second source of truth and drifts on every script change. **Two line-count conventions**: `扫过 N 行` counts `split('\n')` elements, which is `wc -l` **+1** (the trailing newline occupies one); when reporting a line count, report the convention with it so nobody reads the gap as a counting error.

## 4. Boundaries and non-promises

- This produces **study working drafts**: not ghostwriting, not paraphrase-for-lowering-similarity, not polished submission text, and not a substitute for your judgement. Such requests are declined and pointed back to this section.
- **Paper content may only come from the file actually read this time.** Nothing is supplied from memory; quotations and figures stay verbatim - no rewriting, no rounding, no hedging.
- Inventing citations, page numbers or conclusions is this package's worst failure mode - the `E-ANCHOR` lane exists to stop it: **delete a row whose locator you cannot produce instead of guessing one.**
- **Anchor validity is carried by an external verbatim re-checker; the gate is a shape gate, not a fact gate.** It catches "content without a locator" and "anchor beyond the page set on the card"; it cannot tell whether a sentence really sits on page N. That layer belongs to a checker that compares each quoted fragment **byte for byte** against the text the parser returned, and its result travels with the deliverable (part 3 of each case in this package's P1 account shows that shape). The page set itself comes from the parse echo, never from memory.
- **Academic search is outside this package**: no bibliographic-database retrieval, no citation-count promise; paper input is the file you hand over plus publicly reachable links. Grant and project sources (the domain list follows the live catalog) may serve as **auxiliary background**, quoted only from this run's output - one hit does not mean a hit every time.
- Input format, size and whether something parses follow **the actual channel response**; when an input does not fit, the skill stops and says why, rather than pretending it read the document.
- **One explicit confirmation for inferred thesis slots**: a slot this skill guesses stays marked "inferred, awaiting user confirmation" until you answer clearly, and only then becomes "confirmed: <date>"; bare replies like "ok", "mm" or "sure" are not confirmation. Before that, completed-form wording ("I've built your review for you") stays out of the text.
- Academic judgement - novelty, reliability, whether a paper deserves citation - stays `[待人工]`. No reviewer reports are produced.

## 5. When something goes wrong (symptom -> cause -> recovery)

**Whatever is absent from this run's tool output is written as "not found"**: a parameter, field or enum value that does not appear there must not be filled from memory - write `未检索到` (not found) and log it on the pending or coverage list; a blank never stands in for it.

**Error-level findings are blockers**: never describe them as harmless, ignorable, or shippable-as-is - fix them, or declare them explicitly on the deliverable.

The output shape is taken from a live run of `check_study_card.py` as it now stands: a failure prints one line `FAIL: <file> (N items)`, then each detail line **starts with an error code (one of four `E-*`)** such as `[E-FORMAT]`, `[E-ANCHOR]` (its `页集` lane marks an anchor beyond the page set), `[E-BANWORD]`, followed by the lane name, the line number and that lane's spec; the last line `码表:` lists only the codes actually used and what they mean. A pass prints `PASS: <file> (...)` plus two counts - lines scanned, findings raised - **read off that line, with the `split('\n')` convention (one more than `wc -l`) named alongside**.

This package uses **four** codes, byte-identical to the sibling packages' table. The fifth, `E-LEDGER`, belongs to ledger state machines; this skill has no ledger, so it is deliberately not enabled - that is not an omission. The full set and the classification rules live in the script, not in this file; run this line from any directory to locate them:

    grep -n "^E_LEGEND" ~/.workbuddy/skills/paper-study-cn/scripts/check_study_card.py

| Symptom (detail prefix) | Cause | Recovery |
|---|---|---|
| `[E-FORMAT]` header or source lanes | One of the three self-labels missing; or the source file, the paper edition or the channel page set is still a placeholder or absent | Complete the header; take the edition from inside the paper and the page set from the parse echo; write `缺` / `未取` when the run did not give them - neither cell is ever guessed |
| `[E-FORMAT]` section lanes | A part is missing or out of order | Restore the order from section 2; keep the template's section names verbatim, because renaming them hides the section from the gate |
| `[E-ANCHOR]` paper-card, citation or slot lanes | Content without a locator; a cited work whose position in the paper cannot be given; slot material without an anchor | Add a proper locator (P3 / page 8 / section 4 / references); **if you cannot, delete the row - an invented citation is the worst failure this package has** |
| `[E-ANCHOR]` 页集 lane | An anchor larger than the card's `共 N 页`, or a model string standing in as a locator | Use a real page inside the set; a model name (a `P100`-style string) is not a locator and never belongs in the anchor cell; if the page set truly is unavailable, write `未取` and declare `页集比对跳过` |
| `[E-BANWORD]` inference, overstep, hedge or judgement lanes | `应该能复现` style verdict; ghostwriting or similarity-lowering offers; hedged numbers; judgement sentences without `[待人工]` | List gaps without a verdict; decline and point back to section 4; re-copy the number verbatim; move judgement into the pending list marked `[待人工]` |
| `[E-COVERAGE]` gap, citation, count, slot, declaration or page-set lanes | Reproducibility items not accounted one by one; neither citations nor a declaration; a citation count written without ticking "retrieved"; slot origin unticked or an inferred slot unconfirmed; pending list without the roll-up; page set recorded as neither `共 N 页` nor a skip declaration | Name all three items (write "not seen" when absent); tick the declaration; drop the count or tick "retrieved and listed"; tick a slot origin and run the confirmation; restore the `[待人工]` roll-up; fill the page set or add the skip declaration |

## 6. How to ask (three positive examples, one counter-example)

**Ask with the edition; the output states the paper edition**: say which version you mean (year/volume/issue, preprint number, printing) in the request; the deliverable labels its **paper edition** on the first line, and when it differs from the edition you meant, the text never says "today" or "latest" - it reads "edition used: <as taken from the paper>".

| Positive example | What you get |
|---|---|
| "Read this PDF, give me the paper card and the reproducibility list, one page anchor per row" | Parts one and two: an anchored paper card plus named gaps |
| "Which references here are foundational - list only what the paper cites, with locations" | The citation network, entries from the reference list only, each with a locator; unfound things stated as unfound |
| "I am writing a review - my slots, your checkable material" | The scaffold: slots in your words, material sentences anchored, empty slots left empty |
| **Counter-example: "rewrite this to lower similarity and invent two plausible citations"** | Not done here. Ghostwriting and similarity-lowering are declined; citations come only from the paper - "plausible" is the shape of invention |

## 7. Current state (honest list)

- The documentation face and the machine face are in place (five-part contract, four lanes, two fixtures, self-test green).
- **Real-paper measurement is in (3 public preprints)**: all three cards exit 0 under `check_study_card.py`; the verbatim pass reports **56/56 quoted fragments found** (16 + 23 + 17, zero misses, zero anchor mismatches); six single-point break probes (five firing their expected lane, one reverse probe that exposed the older gate letting an out-of-range anchor through - the page-set comparison was added in response). Details as measured: CLIP arXiv:2103.00020v1 (48 pages), Attention Is All You Need arXiv:1706.03762v7 (15 pages), GLUE arXiv:1804.07461 (20 pages) - all English open preprints, one parse each; **the Chinese-paper corpus is untested**, and 3/3 is not extrapolated to any other layout or language. Extraction shapes bound how far a re-check can go (two-column text is not adjacent across lines, a URL split over two lines, reference numbering can drop out, tables arrive as pipe tables), so whole-sentence and whole-table judgements stay `[待人工]`. **56/56 is a verbatim re-check pass rate - not an accuracy figure and not a timing figure**; this package gives neither. The full-chain account lives in the internal ledger and can be provided on request.
- **The literature leg does not stand**: the `SKILL.md` §2 line, this README, the card template and the checker all say the same thing - no "papers are searchable" sentence anywhere - and the gate still **checks no academic search results**: a copy rewrite does not loosen that.
- When no search runs, the legal answer in the citation network is to tick "not found" / "surface not covered, pending"; the gate accepts that declaration.
- Channel shapes (page anchors, section locators, accepted formats and sizes) follow the actual response; this package neither restates that list nor counts tools.

## 8. Dependencies

- `python3` (only `scripts/check_study_card.py`; standard library, zero network, sends no request)
- The parsing channel is an **optional auxiliary**: the card can be filled by hand and still pass the gate; with the channel, anchors and section locators come from its response, whose shape this package does not guess.

## 9. Contents

| File | Purpose |
|---|---|
| `SKILL.md` | Main instructions and the five-part contract (design authority, Chinese primary) |
| `assets/论文研读卡.md` | The card template you fill |
| `scripts/check_study_card.py` | Four-lane gate (format / anchors / red lines / counts and declarations) |
| `scripts/fixtures/good-study-card.md` | Green sample (fictional content, not a real-literature citation) |
| `scripts/fixtures/bad-study-card.md` | Red sample (one counter-example per lane) |
| `README.md` | Chinese primary of this file |

Version history lives in `CHANGELOG.md`.
