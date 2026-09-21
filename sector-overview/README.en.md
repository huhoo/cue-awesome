# sector-overview

**[中文](README.md) · [English](README.en.md)**

*Full English translation of the Chinese-authoritative [`README.md`](README.md); the Chinese text governs where the two diverge.*

"This sector is recovering." — on what evidence?

Most sector reports can't answer that: verdicts fly, and nowhere in the text is a comparable series cited. This piece does the opposite: **give it an industry name + a window, get back a six-section brief (≤6 pages) in which every word like rising / falling / recovering / under pressure carries, in the very same sentence, the series it relies on** (an `S<n>` anchor with basis and as-of date) — and every sentence that can't, honestly reads "no comparable series, no conjuncture judgement". Thin is fine. Unanchored verdicts are not.

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

- **Verdict-anchor co-location is the lifeblood, and literally gate ②**: verdict words (rising / falling / recovering / under pressure / weakening / inflection / high boom / trough) appearing in the body ⇒ the same sentence must carry `S<n>`, or the verbatim second-state sentence applies — an unanchored "inflection" is, by this suite's definition, a hallucination (the sector analogue of catalyst's invented dates);
- **No recycled templates**: each run first derives 2–4 analysis dimensions for *this* industry via one deep-research pass (hogs look at inventory, PV looks at production schedules) — the framework is asked anew, never memorized;
- **Association-sourced numbers are all L3** and land in the review checklist; sector-mean expectation data is off by default (high-risk oversell, refused at the source).

## 3. Quick start (three steps)

1. **Install**: put this directory into your agent's skills folder.
2. **Ask**: "光伏行业近况盘一下，重点看排产和价格" (Chinese or English triggers). ≤3 questions to align inputs.
3. **Collect**: after `+scope → +series → +research → +policy → +companies`, `check_sector.py` runs four gates — **no delivery without passing**. The gate script has landed (49/49); the adversarial review ran the new loop (M46 questions authored by the reviewer, M48 LGTM), and the real smoke's shape lessons were back-locked as guard samples by M49.

## 4. First-time Cue setup (three steps, skippable)

Register at <https://cuecue.cn> (new accounts get 500 at signup and 10 daily — server policy governs) → get `CUE_API_KEY` at <https://cuecue.cn/hub/api-key> into your local credential facility (**never paste it into chat**) → install `cue-data-mcp` / `cue-research` (`cue-omni-reader` as needed).
It runs without Cue too (paste association reports; lines marked user-supplied) — but the anchor discipline doesn't relax: only material that can actually anchor a verdict may carry one.

## 5. What's in the package

```
SKILL.md                         master instruction: lifeblood rule / input contract / pipeline / output / suite linkage (must read)
README.md / README.en.md         this pair (Chinese source of truth / English translation)
CHANGELOG.md                     version history
references/section-skeleton.md   six sections with an [执行蓝图] each
references/policy-timeline.md    policy-timeline row spec (statute anchor cites catalyst's v3-A3, not copied)
scripts/check_sector.py          four gates (landed; 49/49 green)
```

## 6. Current status (the blunt list)

- **v0.1.0, design values**: no end-to-end run yet — coverage, timings, and dimension quality are design values until measured;
- **review closed, shipped**: M48 adversarial LGTM and the M49 smoke rework are closed; 0.1.1 is public with the repo. A full end-to-end delivery run has not landed (smoke ≠ delivery) — until it does, treat coverage as design values;
- **Not submitted to any skill market** (P2 frozen repo-wide; timing is the Owner's call);
- no charts (tables carry as-of dates); no market-data flow, no expectation means; companies appear only as anchored aggregates, never as commentary.

## 7. Sources & credit

- Base: anthropics/financial-services `sector-overview` (Apache-2.0) — origin of the six-section task shape.
- This package is an **A-share re-implementation, not a port**: the verdict-anchor rule, dynamic dimensions, and policy-anchor format are this suite's own discipline. No code from the base. See the repo-root `NOTICE.md`.
