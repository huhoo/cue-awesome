# cn-earnings-note

**[中文](README.md) · [English](README.en.md)**

*Full English translation of the Chinese-authoritative [`README.md`](README.md); the Chinese text governs where the two diverge.*

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

Any stage can be resumed: read the ledger first; questions already answered are never re-asked. Section generation is append-as-you-go (`SKILL.md` §3.5): one section per pass, concatenated into `note.md`.

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
scripts/check_note.py          the four delivery gates (statement & pending-human / traceability / period-basis / word list)
```

## 6. Honest boundaries (the blunt list)

Known **won't-do** or **unverified** — check this before expecting a secret capability:

| Boundary | Status |
|---|---|
| End-to-end field test | **not run yet** (v0.1.0 has no P1 test; until the record is backfilled, timings and channel hit-rates are design values, not measurements) |
| Market / valuation data flow | No — the `equity_market` domain is not open and nothing depends on it; intraday price, market cap and valuation percentiles are never fetched |
| Consensus estimates | no market feed; beat/miss compares only against the company's own pre-announcement / flash report; without one it says "no baseline, no judgement" |
| Excel model / DCF | No (see §1) |
| Non-listed issuers | confirm the material form first; thin material → the ceiling is stated outright |
| Ratings / target prices | always `[待人工]` — refusing to fill them is the feature |
| Insider / non-public information | refused; public sources only |
| Scanned-document parsing | depends on the omni channel; its URL path has an open server-side incident record — while down, degrade to "you paste the text" |
| Compliance word list | built-in minimal blacklist (self-written until ruling D1); **not a compliance opinion** — human review before publishing is still required |

## 7. Sources & credit

- Base: anthropics/financial-services `earnings-analysis` (Apache-2.0) — the methodology and the four-period / beat-miss framing.
- China-market practice reference: 道以研究院 (Daoyi Research Institute) `dao-financial-services` v0.1.9 (MIT) — originator of the CAS conventions, the rating-word whitelist, and the `[待人工]` / prompt-injection defense practices. How to verify (public): package download at <https://hzddyy.com/stdd/api/download/dao>; the series《金融AI_Skill指南》on its WeChat account「小以AI/道以研究院」.
- This package is a **re-implementation, not a port**: the data layer is fully replaced by Cue channels; no code from either project. See the repo-root `NOTICE.md`.
