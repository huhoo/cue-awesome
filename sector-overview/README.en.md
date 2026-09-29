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

## 6. Current status (the blunt list)

- **Building-materials half-course run landed (2026-09-21)**: 1 research run (~13 min) + 7 direct lookups + 0 omni; portrait/volume-price/supply-demand moved from all-second-state to line-by-line sourcing (research-second-hand rows all carry L3 and sit in the review checklist). **Single authoritative count for the whole repo, scope fixed: the volume-price & drivers section holds 6 table rows, each carrying both a scope column and its source anchor — that number is this section's row count only, not the report-wide sourced-row count and not the L3-tier count.** Competing asphalt quotes from two sources stay un-arbitrated by design; continuous weekly series remain unavailable (five "not found" rows on record): **a half-course anchor pass ≠ a claimable price/volume series capability**; dimension quality stays a design value;
- **capability state**: public with the repo (current version per this package's `CHANGELOG.md` and frontmatter); **a full end-to-end delivery run has not landed** (the half-course run and the smoke are both ≠ full delivery) — until it does, section coverage, runtime and dimension quality stay design values and are not claimed as verified;
- **Not submitted to any skill market** (P2 frozen repo-wide; timing is the Owner's call);
- no charts (tables carry as-of dates); no market-data flow, no expectation means; companies appear only as anchored aggregates, never as commentary.

## 7. Sources & credit

- Base: anthropics/financial-services `sector-overview` (Apache-2.0) — origin of the six-section task shape.
- This package is an **A-share re-implementation, not a port**: the verdict-anchor rule, dynamic dimensions, and policy-anchor format are this suite's own discipline. No code from the base. See the repo-root `NOTICE.md`.
