# catalyst-calendar

**English companion of `README.md` (Chinese primary; the pair is for reading inside the repository — skill-channel pages do not resolve relative links, so this is deliberately not a clickable switch).**

*Full English translation of the Chinese-authoritative `README.md` in this directory; the Chinese text governs where the two diverge.*

**Line up the *certain dates* behind your holdings as one forward-dated calendar — every date points back to a filed announcement or a statute, and nothing more. No judgments added.**

It answers a plain question: **"In the next three months, what dates matter for each of my holdings?"** Buyback deadlines (only when the announcement states a full date), vesting days, shareholder-meeting and briefing dates, ex-dividend dates, inquiry-response deadlines, ST effectivity or trading-resumption days, statutory reporting cutoffs — scattered across announcement feeds, easy to miss by hand. The calendar pulls them from five data domains (`buyback` / `esop` / `disclosure_cn` / `regulatory_cn` / `statute`), adds at most one deep-research pass for lock-up/reduction schedules, and ships `calendar.md` plus a fully traceable source table.

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
3. **Collect**: after `+scope → +events → +derive → +build`, `+check` runs the full gate set of `check_calendar.py` — every judgement is the script as it now stands (two self-check commands in §5); invocation flags per the formal command in `SKILL.md` §3 — **no delivery without passing**.

## 3. Built against one specific failure: invented dates

The real risk here is not a wrong analysis — it's a date that never existed. The first gate in `references/event-taxonomy.md` §1 enforces it:

- an entry enters only if either (a) a filed disclosure is on record **and states an explicit date**, or (b) a statutory derivation whose **applicability conditions are decidable inside the cited statute anchor** — anything else never reaches the table;
- **no date arithmetic, period**: "announcement date + 360 days" style derivations never produce a row — the start date, calendar versus trading days, inclusive endpoints and amendment overrides are all undefined, so a derived date cannot be checked against anything; a deadline enters only when the announcement itself writes the full date;
- every date resolves to an announcement index / formal document number / URL / `conv_id`+path / a `statute:` spec string, checked row by row against the type×anchor-kind mapping as it now stands in the script (the kind list is not reproduced here); bare numerals of six-plus digits are themselves one accepted anchor kind (index and issuer-code shapes), so "a number on the page" is not "an anchored line" — what you verify is whether that column leads back to a disclosure; statutory rules come from the `statute` text fetched live at run time, never hardcoded;
- out-of-window entries live in the dedicated 5th column "窗外余档" of the six-column format (the anchor column stays last and pure — notes never crowd out anchors); an empty carry-over column on an out-of-window row FAILs; a queried-but-absent item is marked "未检索到" — **an empty calendar is legal; an invented calendar is not**.

Progress-style disclosures with no pre-known date (1%/2% buyback milestones) go to a trailing "已发生动态" (already-occurred updates) notes section — they never masquerade as upcoming events.

## 4. First-time Cue setup (three steps, skippable)

Register at <https://cuecue.cn> (new accounts get 500 at signup and 10 daily — the server-side policy governs) → get `CUE_API_KEY` at <https://cuecue.cn/hub/api-key> into your local credential facility (**never paste it into chat**) → install `cue-data-mcp` / `cue-research` / `cue-omni-reader`. **Not installing raises no error**: the degraded path is you pasting the announcement list (marked as user-supplied); skip the research run and the lock-up/reduction category is marked "not found" — common sense never fills a date. Everything that spends is asked before it burns.

## 5. What's in the package

```
SKILL.md                        master instruction file: iron rules / input contract / pipeline / output / degradation / boundaries (must read)
README.md / README.en.md        this pair (Chinese source of truth / English translation)
CHANGELOG.md                    version history
references/event-taxonomy.md    event taxonomy (the closed type set is the checker as it now stands; the table is a human-readable mirror) + case law on row-splitting, carry-over notes, L3 marking
scripts/check_calendar.py       the full gate set (pure stdlib, --help works; word sets and guard inventory = the script and fixtures as they now stand, run the two lines below)
                                 note: which words count as rating words, banned words or self-confession words, and which event types are in the closed set, is never listed in full here — the judgement is the checker as it now stands, self-checkable from any directory (the command carries the installed path):
                                     grep -n -A3 "BANNED_RE = \|RATING_RE = \|HALLUCINATION_RE = \|OFFICIAL_USAGE_RE = \|EVENT_TYPES = \|TYPE_ANCHORS = \|SIX_RE = " ~/.workbuddy/skills/catalyst-calendar/scripts/check_calendar.py
                                     bash ~/.workbuddy/skills/catalyst-calendar/scripts/fixtures/run_fixtures.sh (guard inventory and pass state, run in this package)
                                     Installed elsewhere: replace ~/.workbuddy/skills/ with your own skills directory; on Windows: C:\Users\<username>\.workbuddy\skills\catalyst-calendar\scripts\check_calendar.py
                                     Both lines use POSIX tooling (grep / bash) — on Windows run them in Git Bash or WSL. The first prints those seven judgement definitions with context: the rule source itself, not a per-sentence classifier;
                                     the only two exemptions are the type column (never scanned) and official-disclosure word shapes (a bare "increase/decrease of holdings" is not exempted). Word and type examples here are not an exhaustive claim.
```

## 6. Current status (the blunt list)

- **Public with the repo**; **the full multi-issuer end-to-end delivery run has landed (back-filled 2026-09-21)**: 10 issuers × 90-day window with the evidence chain enforced end to end, the full-form check_calendar exit 0; full-window reality: 1 anchorable upcoming row inside 10 issuers × 90 days (an extraordinary shareholders' meeting whose notice states the date), the other 9 issuers carry an empty forward section **with an attribution line**; the statutory Q3-report deadline 2026-10-31 is derivable in principle but the statute channel returned no source text in this run, so nothing was entered (no anchor, no entry) — skipping the `+derive` step on the first pass was a pipeline gap, now back-filled and turned into a required disclosure line.
- **Release surface**: repo visibility is governed by the root README and `CHANGELOG.md`; whether this package reaches any skill marketplace is not decided by the package documents themselves.
- Issuer set capped at 10 (machine-checked); `margin` (broker margin ratios) deliberately excluded — irrelevant to an event calendar.
- No market-data flow (`equity_market` channel not open); **rating vocabulary is zero-tolerance by gate design** — ratings do not apply here, there is no blank left to fill.

## 7. Sources & credit

- Base: anthropics/financial-services `catalyst-calendar` (Apache-2.0) — the calendar format and task structure.
- The China-market event taxonomy and statutory-deadline derivation are **re-implemented** here against A-share disclosure rules; the data layer is fully Cue-native, no code from the base. See the repo-root `NOTICE.md`.
