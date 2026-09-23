# dd-checklist

**[中文](README.md) · [English](README.en.md)**

**How far does the public record actually get you?** This checklist answers in two parts: every risk item it can support is laid out with an anchor you can trace back to a live disclosure, and everything it cannot find is recorded by category, with the reason — **no tool in the domain** versus **zero hits inside the window**. It hands you no conclusion; the verdict slots stay `[待人工]` (human-only).

Give it a single subject, an `asof` date, a lookback window and a purpose tier, and you get a fixed seven-column risk table plus a nine-category coverage ledger and a full evidence snapshot directory. The enemy here is not a missed query — it is **an invented risk item that looks plausible**, so the first gate is hard-coded: a live anchor, a live date inside the window, and unambiguous attribution. Miss any one and the row does not enter the table; it enters the ledger.

**Inputs**: `--subject` (exactly one) · `--asof` · `--lookback` (e.g. `36m`, mandatory) · `--purpose` (investment/credit/mna) · `--sources` · `--evidence` — all six are mandatory
**Outputs**: `dd-<code>-<asof>/` — `report.md` · `sources.jsonl` · `evidence/` (with `LEDGER.sha256`) · `references/coverage-map.md` · `progress.md`
**Cost**: five pipeline stages plus one eight-layer gate; deep research is launched only where a gap demands it, with time and consumption reported before it starts — billing is whatever the server returns

---

## 1. What it is / what it is not

| You want | Use |
|---|---|
| Public-record risk items for one subject over one window, each one anchored | **this skill** |
| A pre-meeting glance across several subjects | sibling `tear-sheet` |
| Confirmed dates in a forward window | sibling `catalyst-calendar` |
| Deep earnings review and promise-versus-delivery reconciliation | sibling `cn-earnings-note` |
| An investment verdict, a legal qualification, or a claim that the record is fully covered | not offered — the verdict slots stay empty, and all three phrasings are machine-checked violations |

## 2. Four things that are nailed down

- **Only the last column counts as an anchor.** An announcement number dropped into the fact column does not substitute, and a digit string that merely resembles an event id — an amount, a share count — is not an anchor. An empty row is acceptable; an anchored hallucination is not.
- **"Not found" comes in three kinds.** No tool in the domain (out of reach, needs human or commercial databases); zero hits (queried, nothing disclosed in the window); not attempted (this run did not query it). Turning the first kind into "the company has no litigation" is the red line of this package.
- **Evidence is fail-closed.** A missing or empty `evidence/`, or a hash mismatch, stops delivery — no "ship now, attach proof later". Every anchor in the table must be findable verbatim in a snapshot, and a legally-derived date must find the statutory text itself.
- **No free arithmetic on dates.** A derivation such as "due within N days after the reporting period" only earns a row if the statute was fetched on the spot, with law name, article number and a short quote all present in the evidence. The `statute` domain does not carry ministry-level rules or exchange rules, so this path currently **expects zero anchors**; if nothing comes back, the row is refused and the reason is written to the ledger.

## 3. Quick start (three steps)

1. **Install**: drop this directory into your agent's skills directory.
2. **Ask**: "run a public-record pre-diligence checklist on Beichen, last three years". A missing window or purpose tier gets a question back — it will not guess for you.
3. **Receive**: five stages, then the gate:

   ```bash
   python3 scripts/check_dd.py report.md \
     --subject '北辰股份有限公司（600001.SH）' --asof 2026-09-21 --lookback 36m --purpose investment \
     --sources sources.jsonl --evidence evidence
   ```

   Eight diagnostic layers (`DD-INPUT/DD-TABLE/DD-ROW/DD-REDLINE/DD-COVERAGE/DD-EVIDENCE/DD-STATUTE/DD-OMISSION`). No pass, no delivery. Fixture bank: `bash scripts/fixtures/run_fixtures.sh`.

## 4. First-time Cue setup (three steps, skippable)

Register at <https://cuecue.cn> (new accounts get 500 on signup and 10 daily, per server policy) → take `CUE_API_KEY` from <https://cuecue.cn/hub/api-key> into local credential storage (**never paste it into chat**) → install `cue-data-mcp` (`cue-omni-reader` as needed).
It also runs without the channels: paste the disclosures yourself and the agent organizes them, tagged user-supplied (L2) — but the coverage ledger will say plainly that no domain query happened, and the value of this deliverable lives precisely in that ledger.

## 5. What is in the package

```
SKILL.md                            main instruction: input contract / first gate / seven-column form / pipeline and gate / human review list (read this)
README.md / README.en.md            this file (Chinese is authoritative) and its English translation
CHANGELOG.md                        version history
references/channel-map.md           nine categories × domain intent, known capability edges, degradation paths
references/coverage-map-template.md ledger template and the three kinds of "not found"
scripts/check_dd.py                 the gate itself (eight diagnostic layers, stdlib only)
scripts/gen_fixtures.py             idempotent re-generator for the whole bank (for re-spawning after new questions; never the other way round)
scripts/fixtures/                   question bank: one sample per contract question, plus positive-path guard samples; the runner grades by exact diagnostic-code set
```

## 6. Current state (honest list)

- **Built**: contract = spec-dd-checklist-0.1.0 including the ten §v2 revisions, acceptance = the reviewer's question list (R0-I) with one sample per question. **The package ships the finished samples and the runner: reproducibility is anchored on `scripts/fixtures/run_fixtures.sh`.** The question list and the per-question mapping table live in the reviewer's workspace and are not part of this package, and no local paths appear here. To re-spawn after new questions: `python3 scripts/gen_fixtures.py --badspec <question-list path>` (no default; samples follow the list, never the other way round, and the script has no grading power).
- **Capability edge (stated plainly)**: `evidence/calls.jsonl` lets the gate machine-catch "the ledger reports fewer than the flow" and "the snapshot the flow points at was deleted or altered", but **a wholesale forged low-hit snapshot is self-consistent with its own flow** — that belongs to the forged-evidence family, which the machine does not disprove; the only defense is the human 3-snapshot verbatim spot check. This package makes no absolute-assurance sentence of that shape (the ban deliberately does not quote the phrasing, so our own literal scans stay clean); what it does commit to is: mismatch blocks delivery, zeroing requires a per-item reason, and under-reporting leaves a machine-side counter-proof.
- **Two BLOCK rounds, then LGTM, and the first real run is on record (M79, 2026-09-22)**: both review rounds returned BLOCK first (M63: 4 blockers; M70: 4 blockers), were fixed question-by-question against §v2, and the M76 re-review is LGTM. **A real single-subject end-to-end run has landed** — 北京东方雨虹防水技术股份有限公司（002271.SZ）with `--asof 2026-09-22 --lookback 12m --purpose investment` (window 2025-09-22~2026-09-22); `check_dd.py` with all six parameters **passed all eight gates at the time and printed the PASS line** (that run did deliver). **Present-tense correction**: re-scanned with the current gate after the §v2-16② domain-set edge landed, this artifact now **exits 1 with two `DD-OMISSION` findings** — for 合规与处罚 and 财务与披露质量 the ledger books one of the two domains the flow actually called. Booked under BACKLOG P-22; the historical artifact is unchanged word for word, and **the PASS credential under the current gate is now on disk** — it is the same-issuer `mna` run described in the next bullet: six parameters, exit 0, PASS line printed. This package still claims no historical artifact passes under today's gate. As measured: **12 anchor-bound rows inside the window** across four categories (equity/control 7, financial & disclosure quality 2, other disclosed material matters 2, related-party & fund occupation 1). **Running through and finding something are two different claims** — all nine categories are booked: three came back with zero hits and two have no public tool (labour & social insurance; listing/review status). `合规与处罚` is booked as zero hits while a coverage difference between the disclosure search face and the full list remains **open under BACKLOG P-19**, so the wording is "zero hits, coverage gap under check", never "no penalties". Statutory-deadline derivation was **refused once on the spot** (no such rule text in the statute domain — the P-10 precondition; the reason line sits in the ledger), and one out-of-window downgrade also has its reason line there. Evidence: **20 raw snapshots + a 15-line call flow (chained `seq`/`prev_sha256`) + the LEDGER**. Consumption as reported: **21 data-MCP calls, zero billing; research 0; omni 0**.
- **§0.3 current-gate credential (same issuer, `mna` tier, run 2026-09-23)**: 北京东方雨虹防水技术股份有限公司（002271.SZ） with `--asof 2026-09-23 --lookback 12m --purpose mna` (window 2025-09-23~2026-09-23); the current gate `check_dd.py` with all six parameters **exits 0 and prints the eight-gate pass line**. Every number below is read off that artifact: **14 anchor-bound rows** inside the window across four categories (equity/control 6, related-party & fund occupation 4, financial & disclosure quality 2, other disclosed material matters 2), row dates 2025-10-15~2026-08-20; the nine-category ledger holds 9 rows = 4 booked as "检到 N" (6/4/2/2, 14 rows in total) + 3 zero-hit + 2 with no public tool (labour & social insurance; listing/review status); `evidence/calls.jsonl` is **9 rows** (seq 1–9 chain continuous, all eight fields present; domain split disclosure_cn 8 + fr_fact_index 1), with the tail seq=9 booking 其他已披露重大事项 / disclosure_cn / hits=2; **12 raw snapshots** by domain — disclosure_cn 9 / fr_fact_index 1 / statute 2 — plus the LEDGER and 14 `sources.jsonl` records. **The multi-domain set form (§v2-16②) now works on a real deliverable**: the 财务与披露质量 row books `disclosure_cn、fr_fact_index`, and ledger cell, flow domain set and per-domain raw snapshots are all three in place; in the same artifact the 合规与处罚 regulatory snapshot is declared in the ledger as a support file rather than pretending to be a category flow row (that trade-off and its consequence stay in `progress.md`, not smoothed over). Statutory derivation: both statute probes returned unrelated rules → **derivation refused on the spot, no row written** (P-10 re-confirmed; the reason line is in the ledger); this run has **no downgrade rows** — the source ledger gives a category count that does not add up against its own nine-category total; the fix belongs to the source artifact, so until that lands this is a paraphrase, not a quotation (four categories with N=M, three zero-hit, two no-tool). Consumption as reported in `progress.md`: **14 direct data-MCP calls** (13 real searches + 1 schema probe inside that count), zero billing; research 0; omni 0. A 12m window does not touch the long-window declaration face — P-19/P-21 remain open and this run claims nothing about long-window coverage.
- **Still unverified**: all runs are the same single issuer — investment (12m), credit (24m) and `mna` (12m, the current-gate PASS credential above); **no second issuer has been run at all**, multi-issuer input is refused by contract, the wider windows for `mna` and `investment` have not been run, and longer windows are bounded by the domain-side search window (P-21 open: declared window vs. reachable evidence cannot yet be machine-cross-checked); marketplace listing (P2) remains frozen. **What the wide-window run evidences (§v2-11 ruling)**: that run predates §v2-11 — it only shows a wide window can complete the seven-step pipeline. Re-scanned with the current gate it FAILS with three findings (a missing age-declaration line → `DD-COVERAGE`, plus the same two-domain under-booking under §v2-16② → `DD-OMISSION`), so it is neither long-window coverage evidence for `disclosure_cn` (that category's known retrieval ceiling is 365 days, i.e. what P-19 tracks) nor a PASS credential. Axes stated explicitly: purpose axis investment / credit / mna, one run each; window axis 12m twice and 24m once, nothing wider; subject axis a single issuer throughout. Outside these three back-filled instances, no other "N items found" number appears anywhere in this README.
- **Marketplace**: the P2 submission is frozen as a whole; timing is the Owner's call, as are push and publication.
- **Known edges**: one subject per run (more than one is refused); no market-data feed; the statutory-derivation path expects zero anchors today; social-insurance detail, full pending-litigation and full administrative-fine data have no public tool — these live only in the coverage ledger, never in an assertion.

## 7. Provenance

- Base: anthropics/financial-services `dd-checklist` and `deal-screening` (Apache-2.0) — origin of the diligence-checklist task shape and the screening tiers.
- This package is an **A-share re-implementation, not a port**: the data layer is fully Cue-native; the nine categories, first gate, coverage ledger and fail-closed evidence rule are rebuilt to this suite's contracts. No code from the base. See the repo-root `NOTICE.md`.
