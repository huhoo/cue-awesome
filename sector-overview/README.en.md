# sector-overview

**English companion of `README.md` (Chinese primary; the pair is for reading inside the repository — skill-channel pages do not resolve relative links, so this is deliberately not a clickable switch).**

*Full English translation of the Chinese-authoritative `README.md` in this directory; the Chinese text governs where the two diverge.*

"This sector is recovering." — on what evidence?

Most sector reports can't answer that: verdicts fly, and nowhere in the text is a comparable series cited. This piece does the opposite: **give it an industry name + a window, get back a six-section brief (≤6 pages) in which every verdict word (rising / falling / recovering / under pressure are common examples — which words count is set by the checker as it now stands, not by this list) carries, in the very same sentence, the series it relies on** (an `S<n>` anchor with basis and as-of date) — and every sentence that can't, honestly reads "no comparable series, no conjuncture judgement". Thin is fine. Unanchored verdicts are not.

**Input**: an industry (Shenwan/CITIC L1 or a colloquial name; ambiguity → candidate list, never a guess) + window (default: last 4 complete quarters) + optional focus
**Output**: `sector-<industry>-<window>/` — `report.md` (portrait & takeaways / volume-price & drivers / supply-demand & capacity / landscape & representatives / policy timeline / review checklist) · `sources.jsonl` · ledger
**Cost**: five stages + four gates; ≤1 deep-research run (cost reported and asked before firing); expectation averages off by default

---

## 1. How the suite splits

| You want | Use |
|---|---|
| A four-quarter evidence brief on one industry (every verdict cite-able on the spot) | **this skill** |
| A deep earnings review of one company | `cn-earnings-note` |
| A 30-second one-pager before a client meeting | `tear-sheet` |
| Dated events for your holdings | `catalyst-calendar` |
| "Which sector should I like" | Nowhere — ratings are zero-tolerance here, **with no exemption zone** |

## 2. Why it's worth it (three hard lines)

- **Verdict-anchor co-location is the lifeblood, and literally gate ②**: which words count as verdict words is not listed here — **the judgement is the union of `JUDGE_PHRASE` and `JUDGE_SINGLE` as they currently stand in `check_sector.py`** (the English words above translate common examples; the machine matches the Chinese strings, examples are not exhaustive — one command prints the live sets, see §5) ⇒ a hit must carry `S<n>` in the same sentence, or the sentence must be the verbatim second-state line (a reworded one still fails while it keeps a verdict word or a second-state hint; a hedge carrying neither is invisible to the machine and sits in the human-review lane) — an unanchored verdict is, by this suite's definition, a hallucination (the sector analogue of the sister ticket's invented dates);
- **No recycled templates**: each run first derives 2–4 analysis dimensions for *this* industry via one deep-research pass (hogs look at inventory, PV looks at production schedules) — the framework is asked anew, never memorized;
- **Association-sourced numbers are all L3** and land in the review checklist; sector-mean expectation data is off by default (high-risk oversell, refused at the source).

## 3. Quick start (three steps)

1. **Install**: put this directory into your agent's skills folder.
2. **Ask**: "光伏行业近况盘一下，重点看排产和价格" (Chinese or English triggers). ≤3 questions to align inputs.
3. **Collect**: after `+scope → +series → +research → +policy → +companies`, `check_sector.py` runs four gates — **no delivery without passing**. The gate script and its guard samples both ship in the package; **the word sets and the guard count are self-checked by running them, not quoted here** (two commands in §5), and the real smoke's shape lessons were back-locked as guard samples.

## 4. First-time Cue setup (three steps, skippable)

Register at <https://cuecue.cn> (new accounts get 500 at signup and 10 daily — server policy governs) → get `CUE_API_KEY` at <https://cuecue.cn/hub/api-key> into your local credential facility (**never paste it into chat**) → install `cue-data-mcp` / `cue-research` (`cue-omni-reader` as needed).
It runs without Cue too (paste association reports; lines marked user-supplied) — but the anchor discipline doesn't relax: only material that can actually anchor a verdict may carry one.

## 5. What's in the package

```
SKILL.md                         master instruction: lifeblood rule / input contract / pipeline / output / suite linkage (must read)
README.md / README.en.md         this pair (Chinese source of truth / English translation)
CHANGELOG.md                     version history
references/section-skeleton.md   six sections with an [执行蓝图] each
references/policy-timeline.md    policy-timeline row spec (statute anchor cites `catalyst-calendar/references/event-taxonomy.md`, not copied)
scripts/check_sector.py          four gates (word sets and guard inventory = the script and fixtures as they now stand; run the two lines below)
                                 note: which words count as verdict words, and which words are banned, is never listed in full here — the judgement is the checker as it now stands, self-checkable from any directory (the command carries the installed path):
                                     grep -n -A3 "JUDGE_PHRASE = \|JUDGE_SINGLE = \|BANNED_RE = \|GUESS_RE = " ~/.workbuddy/skills/sector-overview/scripts/check_sector.py
                                     bash ~/.workbuddy/skills/sector-overview/scripts/run_fixtures.sh (guard inventory and pass state, run in this package)
                                     Installed elsewhere: replace ~/.workbuddy/skills/ with your own skills directory; on Windows: C:\Users\<username>\.workbuddy\skills\sector-overview\scripts\check_sector.py
                                     Both lines use POSIX tooling (grep / bash) — on Windows run them in Git Bash or WSL. The first prints those four word-set definitions with context: the rule source itself, not a per-sentence classifier;
                                     the only carve-out the machine makes is the "not investment advice" disclaimer phrase itself (gate ③); a reworded second-state sentence still fails while it keeps a verdict word or a hint token, and one that keeps neither is invisible to the machine. Word examples here are not an exhaustive claim.
```

## 6. FAQ and anti-patterns (what you try to do -> this skill refuses, because -> where to go instead)

Reviewed iron rules and boundary clauses re-assembled. The authoritative word sets (judgement, banned,
speculation families) and anchor shapes are whatever `check_sector.py` holds now - locator command in section 5.

| What you try | Does it work, and why not | Where to go instead |
|---|---|---|
| Say plainly whether the sector is buyable | **No.** That word family has zero exemption - no column exception, no "just verbally" exception | This ships industry heat evidence with comparable-series anchors; the verdict stays human |
| Keep words like recovery / pressure / inflection without an anchor | **No.** Anchor co-location on the same line is the lifeblood - that is literally gate two | Write it only after fetching a comparable series on the spot; otherwise drop to the thin-report state, never substitute stale values |
| Patch a number you cannot fetch on the spot with hedging phrasing | **No.** Missing data is declared, not filled | Data-gap declaration plus a line on the review checklist |
| Apply one fixed industry framework to every sector | **No.** No framework library is carried; dimensions are generated per industry type by the research run (2-4) | Accept dynamic dimensions; a canned framework is a different product |
| Nothing has a series on record, but ship the full six sections anyway | **No.** The legal shape is an empty conclusion | Thin report plus why it is thin; padding is exactly what the gate blocks |
| Also cover one specific name's recent heat | **Out of scope** (subject here is the industry) | `tear-sheet` for a one-pager, `cn-earnings-note` for an earnings note |

## 7. When something goes wrong (symptom -> cause -> recovery)

Shapes are taken from **the current output** of `check_sector.py`, captured by running it: on failure one line `FAIL: <file> (N items)`; detail lines **start with an error-code prefix (one of the five `E-*` codes), then the check label** (`[E-FORMAT] [参数] (args)`, `[E-BANWORD] [3]`, `[E-ANCHOR] [2]`, `[E-FORMAT] [4]` and so on), then the line number and that check's spec; the final `code legend:` line lists only the codes used. A clean pass prints `PASS: <file> (four gates passed: declaration / lifeblood / banned words / format)`.

The five codes are a closed, suite-wide identical set (byte-identical with the four siblings): `E-FORMAT` / `E-ANCHOR` / `E-BANWORD` / `E-COVERAGE` / `E-LEDGER`. Handling is printed in the `code legend:` line, and the label-to-code mapping for this package is the classifier inside the script - one line from anywhere, swapping these two keys into the grep in section 5:

    grep -n "^E_LEGEND\|^E_RULES" ~/.workbuddy/skills/sector-overview/scripts/check_sector.py

| Symptom (detail prefix) | Cause | Recovery |
|---|---|---|
| `[E-FORMAT] [参数] (args) missing --window(...)` | The formal command requires the window (anti wall-clock) | Add `--window YYYY-MM-DD~YYYY-MM-DD`, matching the declared window verbatim |
| `[E-FORMAT] [①] / [④] ...` | The declaration block is missing, or the six-section shape, table columns or row order are off | Restore per the bracketed spec; the shape is fixed, do not add or drop sections |
| `[E-ANCHOR] [②] ...` | The lifeblood rule was not kept: a heat claim with no comparable series anchor on the same line | Attach the series fetched on the spot (domain + value + period), or rewrite the sentence as a declaration or data gap |
| `[E-FORMAT] [④] sources line N field ... missing or empty` (same family: id not S<n>, kind/confidence outside the enum, illegal asof) | The evidence ledger is malformed | Repair that `sources` line per the bracketed spec; research items need `conv_id` plus the saved path |
| `[E-BANWORD] [③] line N ...` | A word from the banned set entered the body (rating, price-target, buy/sell families) | Rewrite neutrally or delete; no exemptions - full word set via section 5's locator |
| `[E-COVERAGE] [④] line N numeric/series row unanchored ... (缺数须申报)` | A row carries numbers with no `[S<n>]` anchor and no declared gap | Add the anchor, or rewrite the row as a declared data gap - never substitute stale values |
| `[E-ANCHOR] [④] 正文孤儿锚:S<n> 在 sources 不存在（④双向账）` / `[E-ANCHOR] [④] 法定锚不可核:statute ...` | An anchor in the body has no ledger entry, or a statutory anchor cannot be verified | Book the `sources` line with its raw snapshot; statutory anchors need name + article number + short quote, all three, or delete the row |
| Evidence directory missing or hash mismatch | Evidence is fail-closed | Restore the raw snapshots and re-book; delete the claim if it cannot be evidenced |
| Association or domain data stopped inside the window | No update for the period - a data shape, not a script error | Declare the gap and hang it on the review checklist; report research cost before spending it |
| A traceback instead of `FAIL ... (N items)` | An incident: the gate is defined zero-crash with every parse point wrapped | Stop and report with the exact command; run section 5's guard samples to tell a bad report from a broken script |

## 8. How to ask (three positive examples, one counter-example)

- **Positive (industry + angle)**: "Review the photovoltaic sector lately, focus on production plans and prices" -
  the shape in section 3; at most three questions fill the contract (industry / window / angle).
- **Positive (ambiguous industry name, disambiguated first)**: "How did the consumer electronics chain do in H1?" -
  "consumer electronics" can mean panels, devices or components, so candidates are listed and you choose; the skill
  never guesses for you, and the window then defaults to the last four complete quarters, echoed back.
- **Positive (multi-angle + explicit window + policy anchor requirement, complex input)**: "Construction machinery,
  window 2025-01-01~2026-06-30, three angles: operating hours, excavator sales, export mix; in the policy section
  keep only anchors fetched on the spot with name + article number + short quote all three present" - anything less
  is not entered, and one line of refusal reasoning goes to `progress.md`.
- **Counter-example (adjacent need, not this skill)**: "one-pager on CATL recently" - `tear-sheet`; "deep-dive note
  for 2026 Q2" - `cn-earnings-note`; "lay out anchored public risk facts for these names" - `dd-checklist`.

## 9. Current status (the blunt list)

- **Building-materials half-course run landed (2026-09-21)**: 1 research run (~13 min) + 7 direct lookups + 0 omni; portrait/volume-price/supply-demand moved from all-second-state to line-by-line sourcing (research-second-hand rows all carry L3 and sit in the review checklist). **Single authoritative count for the whole repo, scope fixed: the volume-price & drivers section holds 6 table rows, each carrying both a scope column and its source anchor — that number is this section's row count only, not the report-wide sourced-row count and not the L3-tier count.** Competing asphalt quotes from two sources stay un-arbitrated by design; continuous weekly series remain unavailable (five "not found" rows on record): **a half-course anchor pass ≠ a claimable price/volume series capability**; dimension quality stays a design value;
- **capability state**: public with the repo (current version per this package's `CHANGELOG.md` and frontmatter); **a full end-to-end delivery run has not landed** (the half-course run and the smoke are both ≠ full delivery) — until it does, section coverage, runtime and dimension quality stay design values and are not claimed as verified;
- **Not submitted to any skill market** (P2 frozen repo-wide; timing is the Owner's call);
- no charts (tables carry as-of dates); no market-data flow, no expectation means; companies appear only as anchored aggregates, never as commentary.

## 10. Sources & credit

- Base: anthropics/financial-services `sector-overview` (Apache-2.0) — origin of the six-section task shape.
- This package is an **A-share re-implementation, not a port**: the verdict-anchor rule, dynamic dimensions, and policy-anchor format are this suite's own discipline. No code from the base. See the repo-root `NOTICE.md`.
