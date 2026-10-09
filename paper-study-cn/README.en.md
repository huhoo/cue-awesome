# paper-study-cn

**English companion of `README.md` (Chinese primary; the pair is for reading inside the repository — skill-channel pages do not resolve relative links, so this is deliberately not a clickable switch).**

**Turn the paper at hand into a checkable study card: every claim carries a page or section anchor, reproducibility gaps are named one by one, the citation list only holds what the paper itself cites, and academic judgement stays marked `[待人工]`.**

Not a writing service, not a literature mover. This skill does the other half of the job: making the paper actually readable — every point locatable, every citation traceable. The demand account is `verify/enterprise-zone-study-2026-10-09.md` in this repository (the download ledger for comparable enterprise-zone tools).

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

The citation network and the review scaffold come **after** these three: the first depends on a search leg that has not been established (M182 account, section 7), the second needs your own thesis slots.

## 2. The five parts and the four lanes

| Part | Content | What the gate enforces |
|---|---|---|
| 1 Paper card | Title, authors, year, core claim, method, data, conclusion - one anchor per row; absent fields written as `缺` with `不适用` in the anchor cell | Content without anchor -> `E-ANCHOR`; hedged numbers -> `E-BANWORD` |
| 2 Reproducibility list | Dataset availability, whether a code link exists, parameter completeness - **gaps only, never a verdict on reproducibility** | Fewer than three accounted items -> `E-COVERAGE`; "`应该能复现`" style claims -> `E-BANWORD` |
| 3 Citation network | Entries taken only from the paper's own reference list, each with a locator; citation counts declared when not retrieved | Entry without locator -> `E-ANCHOR`; neither entries nor a ticked declaration -> `E-COVERAGE` |
| 4 Review scaffold | Thesis slots belong to the user: given by them, or inferred and then explicitly confirmed; material sentences must be anchored, otherwise leave `空槽（不硬填）` | Unanchored material -> `E-ANCHOR`; unconfirmed inferred slot or unticked origin -> `E-COVERAGE` |
| 5 Pending list | Everything that needs the original text, with academic judgement under `[待人工]` | Missing the `[待人工]` roll-up -> `E-COVERAGE` |

The header has its own hard set: **the three self-labels** (`AI 研读整理`, `观点请回原文核对`, `不构成学术评价`) **plus** the file this read is based on and the paper edition (or `缺`). Any of them missing is an `E-FORMAT`.

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
python3 scripts/check_study_card.py scripts/fixtures/good-study-card.md   # PASS (scans 56 lines, 0 findings)
python3 scripts/check_study_card.py scripts/fixtures/bad-study-card.md    # FAIL (15 findings, all four codes)
python3 scripts/check_study_card.py assets/论文研读卡.md                   # FAIL (6 findings - a blank card failing the gate is the design, not a defect)
```

## 4. Boundaries and non-promises

- This produces **study working drafts**: not ghostwriting, not paraphrase-for-lowering-similarity, not polished submission text, and not a substitute for your judgement. Such requests are declined and pointed back to this section.
- **Paper content may only come from the file actually read this time.** Nothing is supplied from memory; quotations and figures stay verbatim - no rewriting, no rounding, no hedging.
- Inventing citations, page numbers or conclusions is this package's worst failure mode - the `E-ANCHOR` lane exists to stop it: **delete a row whose locator you cannot produce instead of guessing one.**
- The **academic search augmentation leg is not established as of 2026-10-09**: M182 measured the literature leg at 4/4 HTTP 429 with zero data, so it does not stand, and **the throttling is unattributed** (shared pool, local quota and upstream limiting against the channel are all unexcluded - only the fact is recorded). This package therefore writes no "papers are searchable" sentence and never promises citation counts. Grant and project sources (NIH, NSF and the like; the domain list follows the live catalog) each returned one live positive and are **auxiliary background only** - existence proven, stability not. Re-entry: a sentinel single-shot probe for the 429->200 flip plus a catalog diff, then rerun that account to fill in fields, date shapes, PDF anchors and the Chinese-corpus face.
- Input format, size and whether something parses follow **the actual channel response**; when an input does not fit, the skill stops and says why, rather than pretending it read the document.
- **One explicit confirmation for inferred thesis slots**: a slot this skill guesses stays marked "inferred, awaiting user confirmation" until you answer clearly, and only then becomes "confirmed: <date>"; bare replies like "ok", "mm" or "sure" are not confirmation. Before that, completed-form wording ("I've built your review for you") stays out of the text.
- Academic judgement - novelty, reliability, whether a paper deserves citation - stays `[待人工]`. No reviewer reports are produced.

## 5. When something goes wrong (symptom -> cause -> recovery)

**Whatever is absent from this run's tool output is written as "not found"**: a parameter, field or enum value that does not appear there must not be filled from memory - write `未检索到` (not found) and log it on the pending or coverage list; a blank never stands in for it.

**Error-level findings are blockers**: never describe them as harmless, ignorable, or shippable-as-is - fix them, or declare them explicitly on the deliverable.

The output shape is taken from a live run of `check_study_card.py` as it now stands: a failure prints one line `FAIL: <file> (N items)`, then each detail line **starts with an error code (one of four `E-*`)** such as `[E-FORMAT]`, `[E-ANCHOR]`, `[E-BANWORD]`, followed by the lane name, the line number and that lane's spec; the last line `码表:` lists only the codes actually used and what they mean. A pass prints `PASS: <file> (...)` plus two counts - lines scanned, findings raised.

This package uses **four** codes, byte-identical to the sibling packages' table. The fifth, `E-LEDGER`, belongs to ledger state machines; this skill has no ledger, so it is deliberately not enabled - that is not an omission. The full set and the classification rules live in the script, not in this file; run this line from any directory to locate them:

    grep -n "^E_LEGEND" ~/.workbuddy/skills/paper-study-cn/scripts/check_study_card.py

| Symptom (detail prefix) | Cause | Recovery |
|---|---|---|
| `[E-FORMAT]` header or source lanes | One of the three self-labels missing, the source file still a placeholder, or the edition has neither year/volume/issue nor `缺` | Complete the header; take the edition from inside the paper; write `缺` when the text does not state it - this cell is never guessed |
| `[E-FORMAT]` section lanes | A part is missing or out of order | Restore the order from section 2; keep the template's section names verbatim, because renaming them hides the section from the gate |
| `[E-ANCHOR]` paper-card, citation or slot lanes | Content without a locator; a cited work whose position in the paper cannot be given; slot material without an anchor | Add a proper locator (P3 / page 8 / section 4 / references); **if you cannot, delete the row - an invented citation is the worst failure this package has** |
| `[E-BANWORD]` inference, overstep, hedge or judgement lanes | `应该能复现` style verdict; ghostwriting or similarity-lowering offers; hedged numbers; judgement sentences without `[待人工]` | List gaps without a verdict; decline and point back to section 4; re-copy the number verbatim; move judgement into the pending list marked `[待人工]` |
| `[E-COVERAGE]` gap, citation, count, slot or declaration lanes | Reproducibility items not accounted one by one; neither citations nor a declaration; a citation count written without ticking "retrieved"; slot origin unticked or an inferred slot unconfirmed; pending list without the roll-up | Name all three items (write "not seen" when absent); tick the declaration; drop the count or tick "retrieved and listed"; tick a slot origin and run the confirmation; restore the `[待人工]` roll-up |

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
- **Not listed, not measured**: until the P1 verbatim re-check account exists (N real papers, every sentence on the card traced back), this package makes no capability claim and gives no accuracy or timing figure - that line is inherited verbatim from the P0 skeleton README (lead's own wording) and is lifted with the account, not before.
- **The augmentation verdict was rewritten against the M182 account (0.2.1 / M192)**: the literature leg **does not stand**, so the SKILL §2 line now reads "not established as of 2026-10-09 + unattributed throttling + NIH/NSF as auxiliary sources only + the sentinel hook on record" (the superseded wording lives in this repository's git history). All four faces - this README, the card template and the checker - are synced, none writes a "papers are searchable" sentence, and the gate still **checks no academic search results**: a copy rewrite does not loosen that.
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
