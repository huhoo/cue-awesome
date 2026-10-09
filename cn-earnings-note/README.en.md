# cn-earnings-note

**English companion of `README.md` (Chinese primary; the pair is for reading inside the repository — skill-channel pages do not resolve relative links, so this is deliberately not a clickable switch).**

*Full English translation of the Chinese-authoritative `README.md` in this directory; the Chinese text governs where the two diverge.*

**Give it an issuer + a reporting period; get back an 8–12-page research-grade deep review of the results as an AI first draft — every number traceable, ratings always `[待人工]` (pending human).**

This is not "analyze this stock for me" — it breaks a statutory filing into an **auditable evidence chain**: four-period deltas across the three statements, segment volume/price, earnings quality, a footnote risk scan, guidance & catalysts, peer comparison, each figure tagged `[L1]/[L2]/[L3]` for confidence, with a closing source index that maps one-to-one to `sources.jsonl`. So what it hands back can enter an internal review workflow, instead of being a pile of opinions.

**Input**: stock code or full company name + reporting period (e.g. `2026H1`); optional materials (results-briefing minutes, PDFs, links) and focus areas
**Output**: `earnings-<code>-<period>/` — `note.md` (eight-section first draft + source index) · `sources.jsonl` · `progress.md` ledger
**Cost**: five pipeline stages + one delivery gate; it runs without the Cue channels (degradation below) — with them, every number stays traceable

---

## 1. What it is / what it isn't

| You want | Use |
|---|---|
| An 8–12-page deep earnings review draft (before internal circulation or publication) | **this skill** |
| A one-page take you finish in thirty seconds | ask `cue-research` directly ("快评XX" — there is a ready-made buddy) |
| Excel three-statement model updates, DCF/LBO | the model-builder line of anthropics/financial-services; explicitly out of scope here |
| Intraday quotes, live valuation percentiles | No — the market-data channel is not open; valuation anchors use disclosure and buyback/incentive text only |
| Charts / visualizations | No — the matplotlib chart step of the original earnings-analysis was **deliberately removed**: this package ships a text-and-table first draft; charts are made downstream |

Two iron rules up front: **the output is an AI first draft** — views, ratings and target prices must come from a human (the `[待人工]` mechanism); **every number is traceable** — no source means "not found", never an invented figure or link.

## 2. Quick start (three steps)

1. **Install**: put this directory into your agent's skills folder (repo-level install: see the root README).
2. **Ask**: "给我出一份 600519 的 2026H1 深度点评" — triggers work in Chinese or English (see the `SKILL.md` frontmatter). It aligns inputs in ≤5 questions (issuer / period / materials / focus / output dir, each with a default), then opens a `progress.md` ledger.
3. **Collect**: the five stages run (`+resolve → +fetch → +parse → +survey → +draft`), then the gate `+check` — **no delivery without passing it**. You get `note.md` + `sources.jsonl` + the ledger; data gaps are marked "未检索到" (not found) in place.

Resume = start from the ledger (read `progress.md` and upstream artifacts first), **re-check the gate's current checks before running** — contracts evolve with field tests, don't resume from stale memory; questions already answered are never re-asked. Section generation is append-as-you-go (`SKILL.md` §3.5): one section per pass, concatenated into `note.md`.

## 3. First-time Cue setup (three steps, skippable)

The evidence backbone is Cue's three channels: structured disclosures (data-mcp) + original-document parsing (omni) + cross-checking deep research (cue-research). **Not installing raises no error** — every step has a degraded path (you supply the material + the agent searches freely); you only lose evidence density and traceability.

1. Register at <https://cuecue.cn> (new accounts get 500 at signup and 10 daily — the server-side policy governs);
2. Get `CUE_API_KEY` at <https://cuecue.cn/hub/api-key> and store it in your local credential facility — **never paste it into chat**; the agent never handles the key;
3. Install the skills: `cue-research` / `cue-omni-reader` / `cue-data-mcp` (install steps in each of their SKILL.md files).

Everything that spends is **asked before it burns**: a deep-research run takes 3–15 minutes and consumes credits; you confirm each launch. This documentation promises no unit prices.

## 4. Dependencies

- `python3`: only for the gate script `scripts/check_note.py` — pure stdlib, zero network.
- `cue-research` / `cue-omni-reader` / `cue-data-mcp`: declared `optionalSkills` in the frontmatter — **absent, no error**; the per-situation judgement table is in `references/data-channels.md` §5.
- No other runtime dependencies; document parsing runs through the omni channel (local files need its Bridge plus a minimal directory grant — it asks you before installing or widening scope).

## 5. What's in the package

```
SKILL.md                       the master instruction file: iron rules / input contract / five stages / output contract / boundaries (must read)
README.md                      this file's Chinese source of truth
README.en.md                   this file (English translation)
CHANGELOG.md                   version history
references/data-channels.md    Cue three-channel contracts + compliance minimum set + onboarding judgement table
references/report-skeleton.md  the eight-section skeleton, every section with an [执行蓝图] (play-by-play blueprint)
references/expectation-pool.md public-summary-layer expectation pool contract (beat/miss second anchor, source_tier tiers, scaffold anchor line)
references/coverage-ledger.md  coverage-ledger contract (ledger-<period>.json fields / six states / read-before-write / linkage assertions)
references/evidence-format.md    evidence-layer contract (evidence/ naming, sha ledger rows, link-break semantics, spot-check line; shared by three tickets)
scripts/check_note.py          the four delivery gates (statement & pending-human / per-line evidence-level tags on prose numeric lines, plus a 95% aggregate coverage floor / ledger basis fields / word list)
                                 note: which lines count as numeric lines is the union of NUM_UNIT_RE and CN_NUM_UNIT_RE as they currently stand in check_note.py — self-check it from any directory (the command carries the installed path):
                                     grep -n "NUM_UNIT_RE\|CN_NUM_UNIT_RE" ~/.workbuddy/skills/cn-earnings-note/scripts/check_note.py
                                     Installed elsewhere: replace ~/.workbuddy/skills/ with your own skills directory; on Windows: C:\Users\<username>\.workbuddy\skills\cn-earnings-note\scripts\check_note.py
                                     The output is three lines: those two live regex definitions plus the one line in the checker that calls them — the rule source itself, not a per-sentence classifier.
                                     fixtures carry positive and negative guards. The shapes named here are common examples, not an exhaustive claim — intercepted e.g.
                                     三亿元 / 五百万元 / 三千万元 / 20,000千元; not intercepted e.g. 千万元 (no leading numeral), 数亿元, 五万份, 二〇二六年, 230吨.
                                     A list line carrying its own [S<n>] reference is exempt and out of the denominator; a section headed 来源索引 is not checked at all (human review).
                                     The codes actually emitted follow check_note.py as it stands, and the fixtures demonstrate only cases they actually exercise, not an exhaustive list of exemptions.
```

## 6. FAQ and anti-patterns (what you try to do -> this skill refuses, because -> where to go instead)

Nothing new is promised here; reviewed refusal clauses and fixture shapes are simply re-assembled. Word-level
criteria (banned words, estimate words, which lines count as numbers) are whatever `check_note.py` holds now -
locator command in section 5.

| What you try | Does it work, and why not | Where to go instead |
|---|---|---|
| Ask for a rating, a price target, or a promise that the draft will clear publication | **No.** Judgement slots are left as `[待人工]`; filling them is out of bounds | A person writes the conclusion; this skill makes every figure traceable |
| Feed in internal reports, client data or anything non-public | **No.** Public sources only | Write that section once the disclosure is on record; until then it stays "not disclosed" |
| Also produce charts or a DCF model | **Not in scope.** The output is data tables plus a text skeleton; the base's plotting step was deliberately removed (A-share notes are evidence-chain first - a design trade-off, not a gap) | Generate figures elsewhere and pass them in as material; models live outside this format |
| Subject is not a listed company (no periodic filing duty) | **Confirm the material shape first**; with thin material the ceiling is stated rather than papered over | Start once the material is sufficient; otherwise say why it does not apply |
| One period is genuinely missing and you want a plausible number inserted | **No.** Missing values are marked "not disclosed"; estimate-style words are blocked by the gate | Leave the cell and log it. Empty is legal, invented is not |
| Resume from memory because last quarter ran | **No.** Continuation starts by reading the `progress.md` ledger and upstream artifacts; the cross-period ledger must never be rewritten | Read the ledger first; a state mismatch is reported by the gate itself |

## 7. When something goes wrong (symptom -> cause -> recovery)

**Whatever is absent from this run's tool output is written as "not found"**: a parameter, field or enum value that does not appear there must not be filled from memory - write "not found" and log it on the pending or coverage list; a blank never stands in for it.

**Error-level findings are blockers**: never describe them as harmless, ignorable, or shippable-as-is - fix them, or declare them explicitly on the deliverable.

Shapes are taken from **the current output** of `check_note.py`, captured by running it: on failure one line `FAIL: <file> (N items)`; detail lines **start with an error-code prefix (one of the five `E-*` codes), then the original check label** (`[E-BANWORD] [禁用词] (banned)`, `[E-COVERAGE] [数字] (number)`, `[E-FORMAT] [声明] (declaration)`), followed by the line number and that check's spec; the final `code legend:` line lists only the codes used. A clean pass prints `PASS: <file> (numbered lines X/Y tagged, four gates passed)`.

The five codes form a closed, suite-wide identical set (byte-identical with the four siblings): `E-FORMAT` / `E-ANCHOR` / `E-BANWORD` / `E-COVERAGE` / `E-LEDGER`. Handling is not restated here - **it is printed in the `code legend:` line**; which label maps to which code in this package is the classifier inside `check_note.py`, printable from anywhere by swapping these two keys into the grep in section 5:

    grep -n "^E_LEGEND\|^E_RULES" ~/.workbuddy/skills/cn-earnings-note/scripts/check_note.py

| Symptom (detail prefix) | Cause | Recovery |
|---|---|---|
| `[E-BANWORD] ...` on a line | A banned family appeared, or a judgement slot was filled instead of left open | Follow the printed legend: rewrite neutrally or delete, and put the judgement back into `[待人工]`; full word set via section 5 |
| `[E-COVERAGE] [数字] (number) ...` (including the ratio line) | Tagged-number counts disagree with the body, or traceable ratio is under threshold | Re-tag figure by figure: each number either carries a traceable anchor or is explicitly marked undisclosed |
| `[E-ANCHOR] [来源] (source) sources.jsonl line N field ... missing or empty` | The evidence ledger is malformed (missing field, illegal id shape, non-date asof) | Repair that `sources` line per the bracketed spec; delete a claim you cannot evidence rather than invent an anchor |
| `[E-LEDGER] ...` (ledger or cross-link failures) | Cross-period ledger state machine or a broken link (opening balance, amendment, fulfilment) | Rebuild the links per the ledger contract: add the current period's entry, **never rewrite history** |
| `[E-FORMAT] [声明] (declaration) / [脚手架] (scaffold) / [参数] (args)` | First-screen declaration, scaffold section or a required parameter is out of shape | Restore per spec; supply `--ledger` / `--prev-ledger` / `--audit-report` as needed |
| Exact hits are zero and the expectation pool is used silently | Nothing in the domain for the period - a designed fallback, not an error | Pool discipline: pooled content may not be cited into the body; either it carries a disclosure anchor or it is not written |
| Channel missing / parsing failed | Tool absent, or a scan the parser cannot read | Degradation chain: ask for text, switch source, or mark "not obtained" in the ledger, always recording the source level |
| A traceback instead of `FAIL ... (N items)` | An incident: the exit should be a list | Stop: check the criterion definitions through section 5's locator (the checker holds the authoritative set), log the document plus the exact command in `progress.md` and report it |

## 8. How to ask (three positive examples, one counter-example)

**Ask with a point in time; the output states its data date**: give the reporting period, reference date or look-back window in the request; the deliverable labels its **data date** on the first line, and when that differs from the date you asked about, the text never says "today" or "latest" - it reads "as of <date>".
- **Positive (code + period)**: "Give me the 2026 H1 deep-dive note for 600519" - the shape in section 2; five
  questions fill the contract and work starts.
- **Positive (complex: user-supplied material + focus + output dir)**: "Subject is Oriental Yuhong (002271.SZ),
  period 2026 Q2. Material is downloaded: the half-year report text and one earnings flash release under
  `~/mat/2026H1/`; treat the two documents against the caliber discipline (mixed calibers fail the gate outright). Focus this run on
  segment price/volume and cash-flow quality, keep other sections at defaults, output to `~/notes/2026Q2/`" - supplied
  material is booked at its source level, focus changes fetch priority but never the output format.
- **Positive (English)**: "Write the 2026 H1 deep-dive note for 600519." The frontmatter trigger phrase face is
  currently Chinese-shaped, so English users should name the skill (`cn-earnings-note`) explicitly.
- **Counter-example (adjacent need, not this skill)**: "Can I buy it, and what is it worth" - no verdict and no price
  here; use `dd-checklist` for anchor-bound facts plus a ledger of what could not be checked, `tear-sheet` for a
  pre-meeting one-pager.

## 9. Honest boundaries (the blunt list)

Known **won't-do** or **unverified** — check this before expecting a secret capability:

| Boundary | Status |
|---|---|
| End-to-end field test | **five runs across three issuers verified**: Midea 000333 (2026H1 + 2025AR) + Oriental Yuhong 002271 (2026H1) + Gudi Technology 002694 (*ST high-risk first case), machine gates + manual acceptance passed; record in `CHANGELOG.md` Verified. **Still untested**: HK-listed issuers, multi-issuer batches — treat a first run of these two as unverified |
| High-risk issuers (ST/*ST) | **first case run (2026-09-21)**: Gudi — research 2/2 full slots + omni 1 (shell-page billed 0.268 per server receipt, product discarded) + 11 direct lookups; pre-announcement range, going-concern uncertainty and fund-occupancy items all handled strictly by "no anchor, no judgement" |
| Forecast scaffold (0.3.3) | **first flight = gate layer proven**: three `[待人工]` year rows + border note + anchor row passed; two rounds of gate rejects (12+2) were the line working — not an endorsement of judgement quality |
| Market / valuation data flow | No — the `equity_market` domain is not open and nothing depends on it; intraday price, market cap and valuation percentiles are never fetched |
| Consensus estimates | paid terminals are neither fetched nor promised; since 0.3.0 beat/miss has a second anchor — the public-summary-layer expectation pool (`references/expectation-pool.md`: institution counts / consensus means / target-price range, with `source_tier` self-declaration, cross-platform divergence left un-arbitrated); judgement priority = company pre-announcement / flash report > pool mean > verbatim "no company baseline and no public pool mean — no beat/miss judgement" |
| Excel model / DCF | No (see §1) |
| Non-listed issuers | confirm the material form first; thin material → the ceiling is stated outright |
| Ratings / target prices | always `[待人工]` — refusing to fill them is the feature |
| Insider / non-public information | refused; public sources only |
| Scanned-document parsing | depends on the omni channel; the earlier server-side outage on its URL path is fixed (failed-parse-no-charge re-verified; the "completed-but-shell page still billed" edge case is fixed and re-verified (a failed parse returned billed:false; billing is whatever the server receipt says) — while the channel is down, degrade to "you paste the text" |
| Compliance word list | built-in minimal blacklist (self-written); **not a compliance opinion** — human review before publishing is still required |

## 10. Sources & credit

- Base: anthropics/financial-services `earnings-analysis` (Apache-2.0) — the methodology and the four-period / beat-miss framing.
- This package is a **re-implementation, not a port**: the data layer is fully replaced by Cue channels; no code from the base. See the repo-root `NOTICE.md`.
