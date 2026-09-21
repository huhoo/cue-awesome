# tear-sheet

**[中文](README.md) · [English](README.en.md)**

*Full English translation of the Chinese-authoritative [`README.md`](README.md); the Chinese text governs where the two diverge.*

**Thirty seconds before a client meeting — enough?** Enough. Hand it an issuer + a use case and you get a one-page sheet where **every line traces to a disclosure anchor** (readable on one screen) — and an opinions column that honestly stays blank.

This is the suite's **lowest-barrier entry piece**: zero deep research by default, built on structured-disclosure lookups, cost kept to single-digit credits and printed in the page header. It does not decide for you; it lays out what is certain within 30 seconds — three identity lines, a four-period snapshot (cumulative + single-quarter, basis-tagged), on-record events (only those with an explicit disclosed date), risk items that actually hit, and three `[待人工]` slots for a human's view.

**Input**: issuer(s) (official name or code, ≤5) + purpose (pre-meeting glance / client brief) + optional one-line focus
**Output**: `tearsheet-<date>-<n>issuers/` — `page.md` (the five-block sheet) · `sources.jsonl` · `progress.md` ledger
**Cost**: three stages + one format gate; 0 research runs by default, at most one billing confirmation across the whole flow

---

## 1. What it is / what it isn't

| You want | Use |
|---|---|
| A 30-second pre-meeting one-pager (every line anchored) | **this skill** |
| A dated calendar of upcoming events for your holdings | sibling `catalyst-calendar` |
| A deep earnings review or quarter-over-quarter ledger | sibling `cn-earnings-note` |
| Spreadsheet deliverables, batches of >5 issuers, ratings / target prices / buy-sell advice | No — the opinions block is literally three blank lines waiting for a human |

## 2. The format *is* the discipline (why it looks like this)

Five blocks in fixed order; three header declarations mandatory (generation asof / data cutoff / this run's channel usage). These are gate checks, not aesthetics:

- **every line anchors**: numbers resolve to announcement indexes / URLs / domain refs, validated column-by-column — digits in other columns cannot impersonate an anchor;
- **events pass a gate first**: on-record events reuse `catalyst-calendar`'s v2 first-gate contract by reference (cited, never copied — no second source of truth); "events" without an explicit disclosed date never reach the page;
- **no fake all-clears**: if the direct lookup hits nothing, the page must carry the fixed line "no hits within the direct-lookup surface ≠ no exposure";
- **better empty than invented**: an unresolvable line is deleted and logged — an empty line is legal, an invented line is not.

## 3. Quick start (three steps)

1. **Install**: put this directory into your agent's skills folder.
2. **Ask**: "见客户前给我一页纸看看东方雨虹" or "客户简报里加一节美的" (Chinese or English triggers). ≤3 questions to align inputs.
3. **Collect**: after three stages, `check_page.py` runs four gates (declarations / column anchors + two-way sources / zero-tolerance word list / format & line budget) — **no delivery without passing**.

## 4. First-time Cue setup (three steps, skippable)

Register at <https://cuecue.cn> (new accounts get 500 at signup and 10 daily — server policy governs) → get `CUE_API_KEY` at <https://cuecue.cn/hub/api-key> into your local credential facility (**never paste it into chat**) → install `cue-data-mcp` (`cue-omni-reader` as needed).
It runs without Cue too (you paste disclosure text; the page marks lines as user-supplied) — but then you don't see what anchored channel lookups actually look like, which is precisely what this piece is meant to show.

## 5. What's in the package

```
SKILL.md          master instruction: input contract / five blocks / cost discipline / pipeline & gate / boundaries (must read)
README.md         this file (Chinese source of truth)
README.en.md      English translation
CHANGELOG.md      version history
scripts/          gate script check_page.py + fixtures (landed; 77 assertions all green)
```

## 6. Current status (the blunt list)

- **v0.1.0, design values**: no end-to-end run has happened yet; the 30-second promise, the single-digit cost, and coverage are all design values until measured records land.
- **Review closed, shipped**: gate M43 (77/77, the question-list-as-contract reconciled 1:1) + adversarial M45 LGTM; public with the repo at 0.1.1. No end-to-end client-meeting run recorded — the 30-second/single-digit-cost wording stays a design-value claim.
- **Not submitted to any skill market**: publishing (P2) remains frozen; timing is the Owner's call. Repo visibility is governed by the root README and `CHANGELOG.md`.
- Issuer cap of 5 (machine-checked); no market-data flow (the `equity_market` channel is not open); **rating vocabulary is zero-tolerance by gate design** — the concept does not exist on this page.

## 7. Sources & credit

- Base: anthropics/financial-services `tear-sheet` (Apache-2.0) — the origin of the one-pager task shape.
- This package is an **A-share re-implementation, not a port**: the data layer is fully Cue-native; the five blocks, dual-basis snapshot, event first-gate, and cost discipline are rebuilt to this suite's contracts. No code from the base. See the repo-root `NOTICE.md`.
