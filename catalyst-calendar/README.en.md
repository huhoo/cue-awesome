# catalyst-calendar

**[中文](README.md) · [English](README.en.md)**

*Full English translation of the Chinese-authoritative [`README.md`](README.md); the Chinese text governs where the two diverge.*

**Line up the *certain dates* behind your holdings as one forward-dated calendar — every date points back to a filed announcement or a statute, and nothing more. No judgments added.**

It answers a plain question: **"In the next three months, what dates matter for each of my holdings?"** Buyback progress milestones, vesting days, ex-dividend dates, inquiry-response deadlines, statutory reporting cutoffs — scattered across announcement feeds, easy to miss by hand. The calendar pulls them from five data domains (`buyback` / `esop` / `disclosure_cn` / `regulatory_cn` / `statute`), adds at most one deep-research pass for lock-up/reduction schedules, and ships `calendar.md` plus a fully traceable source table.

**Input**: a set of issuers (official full names or codes, ≤10) + a horizon window (default: next 90 days)
**Output**: `calendar-<date>-<n>issuers/` — `calendar.md` (forward-dated table + a "watch in the next 30 days" list + source appendix) · `sources.jsonl` · `progress.md` ledger
**Cost**: four pipeline stages + one delivery gate; research ≤1 run (can be zero), always confirmed before it spends

---

## 1. What it is / what it isn't

| You want | Use |
|---|---|
| An event calendar for your holdings (dates with disclosure anchors) | **this skill** |
| A deep earnings review of one issuer | its sibling, `cn-earnings-note` |
| Stock picking, timing, "is this date bullish?" | No — **events are stated, never judged**; bullish/bearish vocabulary is banned outright |
| Rumours like "expected buyback" | No — undisclosed events never enter the table |

## 2. Quick start (three steps)

1. **Install**: put this directory into your agent's skills folder.
2. **Ask**: "我的持仓是美的集团、东方雨虹、宁德时代，给我排未来 90 天的催化剂日历" (triggers work in Chinese or English). It aligns inputs in ≤4 questions (issuer set / window / focus types / output dir, each with a default), then opens a `progress.md` ledger.
3. **Collect**: after `+scope → +events → +derive → +build`, the gate `+check` runs `check_calendar.py` (four checks: statement line / per-row anchor / word list / date format & window) — **no delivery without passing**.

## 3. Built against one specific failure: invented dates

The real risk here is not a wrong analysis — it's a date that never existed. Three hard constraints:

- every date resolves to one of: announcement index / URL / `conv_id`; a bare row FAILs the gate;
- statutory deadlines are derived from the `statute` text fetched live at run time — rules are not hardcoded;
- out-of-window entries must carry an inline "窗口外余档" (out-of-window carry-over) note, or they FAIL; a queried-but-absent item is marked "未检索到" — **an empty calendar is legal; an invented calendar is not**.

## 4. First-time Cue setup (three steps, skippable)

Register at <https://cuecue.cn> (new accounts get 500 at signup and 10 daily — the server-side policy governs) → get `CUE_API_KEY` at <https://cuecue.cn/hub/api-key> into your local credential facility (**never paste it into chat**) → install `cue-data-mcp` / `cue-research` / `cue-omni-reader`. **Not installing raises no error**: the degraded path is you pasting the announcement list (marked as user-supplied); skip the research run and the lock-up/reduction category is marked "not found" — common sense never fills a date. Everything that spends is asked before it burns.

## 5. What's in the package

```
SKILL.md                        master instruction file: iron rules / input contract / pipeline / output / degradation / boundaries (must read)
README.md / README.en.md        this pair (Chinese source of truth / English translation)
CHANGELOG.md                    version history
references/event-taxonomy.md    six event classes + case law on row-splitting, carry-over notes, L3 marking
scripts/check_calendar.py       the four delivery gates (standalone, pure stdlib, --help works)
```

## 6. Current status (the blunt list)

- **v0.1.0, no end-to-end run yet**: docs and the gate script were built in parallel; until a real multi-issuer run over a real window is recorded, timings and coverage are design values, not measurements.
- **Not submitted to any skill market**: publishing (P2) is frozen repo-wide, same gate as the sibling skill; timing is the Owner's call. Repo visibility is governed by the root README and `CHANGELOG.md`.
- Issuer set capped at 10; `margin` (broker margin ratios) deliberately excluded — irrelevant to an event calendar.
- No market-data flow (`equity_market` channel not open); no ratings or target prices — the concepts do not appear.

## 7. Sources & credit

- Base: anthropics/financial-services `catalyst-calendar` (Apache-2.0) — the calendar format and task structure.
- The China-market event taxonomy and statutory-deadline derivation are **re-implemented** here against A-share disclosure rules; the data layer is fully Cue-native, no code from the base. See the repo-root `NOTICE.md`.
