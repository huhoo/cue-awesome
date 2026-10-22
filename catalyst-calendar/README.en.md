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

1. **Install**: `npx skills add huhoo/cue-awesome --skill catalyst-calendar` — that command installs this package; afterwards list your installed skills again and seeing `catalyst-calendar` there is what proves the files landed (nothing more than that). Dropping this directory into your agent's skills folder works the same way.
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

Install the evidence legs separately: `cue-data-mcp` / `cue-research` / `cue-omni-reader` — these three ship in Cue's official skill collection (sensedeal), one command, two forms: the whole set `npx skills add sensedeal/cue-skills` (it lists the skills published there; pick what to install), or one at a time `npx skills add sensedeal/cue-skills --skill cue-data-mcp`, swapping the last name for `cue-research` or `cue-omni-reader` to install just that one. This package itself is installed by the command in the section above (`huhoo/cue-awesome --skill catalyst-calendar`) — do not conflate the two.
Register at <https://cuecue.cn> (new accounts get 500 credits at signup and 10 credits daily — the server-side policy governs) → get `CUE_API_KEY` at <https://cuecue.cn/hub/api-key> into your local credential facility (**never paste it into chat**, and do not echo it in a terminal).
The three layers prove different things and are not interchangeable: **skill installed ≠ credentials configured ≠ channel connected**.
- installed: list your installed skills again and the names above show up — that only proves the files landed, not that data flows.
- credentials configured: the `CUE_API_KEY` exists in your local credential facility; **a key being present is not a key being accepted** — acceptance only becomes judgeable in the next layer.
- connected: connect to the target domain with that key, following the `url` inside the domain's own `routing` (`Authorization: Bearer <$CUE_API_KEY>`, plus `Accept: application/json, text/event-stream` — missing that header gives a 406, which is protocol behaviour, not an authentication failure) **and** `tools/list` returns; tool names and input schemas follow that response's current values, never hardcoded or invented.
An anonymous `GET` of the `CATALOG` defined in the block returning anything proves only that the **catalog is reachable** — this package does not call that "connected"; what it yields is each domain's `external_status` and the live domains' `routing`. A domain missing from that response stays uninstalled and unpromised here. A connection error is not "the domain has no data": report it as-is and retry only what the error marks as retryable. **Not installing raises no error**: the degraded path is you pasting the announcement list (marked as user-supplied); skip the research run and the lock-up/reduction category is marked "not found" — common sense never fills a date. Everything that spends is asked before it burns.

```bash
CATALOG="https://cuecue.cn/api/mcp-catalog"
curl -s "$CATALOG" | python3 -c 'import json,sys
rows=json.load(sys.stdin)["data"]["domains"]
[print(r.get("id"), r.get("external_status"), (r.get("routing") or {}).get("url", "-")) for r in rows]'
DOMAIN_ID="<replace with one of the ids listed by the line above>"
ROUTING_URL="$(curl -s "$CATALOG" | python3 -c 'import json,sys
rows=json.load(sys.stdin)["data"]["domains"]
hit=[r["routing"]["url"] for r in rows if r.get("id")==sys.argv[1] and r.get("routing")]
print(*hit,sep="\n") if hit else sys.exit("Not found: that id is not in the catalog response (or its routing has no url field) - run the line above and pick one of the ids listed")' "$DOMAIN_ID")"
[ -n "$ROUTING_URL" ] || { echo "Fetch failed: ROUTING_URL is empty - run the line above, then set DOMAIN_ID to one of the ids listed" >&2; exit 1; }
curl -s -X POST "$ROUTING_URL" \
  -H "Authorization: Bearer $CUE_API_KEY" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' \
  -w '\nHTTP %{http_code}\n'
```

Where the value comes from: `$ROUTING_URL` is fetched by the two lines above from the anonymous catalog response - the verbatim `url` field inside that domain's `routing` object, never a hardcoded domain or path; `CATALOG` in the block is the only catalog-entry literal on this face (assigned once, not restated in prose); `$CUE_API_KEY` comes from the local credential facility set up in the layer above, never enters chat, is not echoed in a terminal, and this block adds no new credential-reading step.
Pass = HTTP 200 with a non-empty `result.tools` in the body (recognised by shape only, e.g. `{"result":{"tools":[…]}}`; this face lists no tool names and promises no counts).
One-command form (no need to edit the line inside the block): `cd catalyst-calendar && python3 -B scripts/cue_connectivity_check.py --domain <your domain id> --post`. This shipped script sends nothing by default - without --post it only fetches the url inside that domain routing and shows it to you. To see which ids exist, run the same script with `--list` first (it lists domains and urls, no POST). This script sets up no second criterion, 4 means connectivity is not proven yet (rerun with --post), 5 means it connected but the live values did not satisfy it, 1 means nothing could be fetched, nothing could be sent, or the HTTP layer itself reported an error (4xx and 5xx included), 6 means the destination failed the two credential-egress gates - nothing was sent and not one credential byte was attached, 7 means the catalog entry itself was not https. On the default catalog entry this script only checks runtime-endpoint connectivity - it publishes nothing to any channel and creates no acceptance record. **A swapped source is not exempt from the check**: whether that url came from the default catalog, from --catalog-url or from the --catalog-file snapshot, the request carrying the key must first pass the same two gates - the scheme must be https, and the host must match an authorized suffix (the default one is derived from the catalog entry in this script header, not a list invented here; pass --allow-host to authorize another). If it does not pass, the script refuses and prints the reason together with that host, and it neither reads the key nor builds the request. The cost is stated in the same breath: the old "whatever the swapped source hands over gets dialled" behaviour is closed off, and what you get in exchange is credentials that never leave toward an unauthorised destination - if your legitimate endpoint sits outside the suffix, exit 6 is the script asking you to confirm it with --allow-host, not a claim that endpoint should not exist.
One precision note about the live reply: this endpoint may answer in SSE form (an event line followed by a data line), and the result.tools to look for lives inside that data payload - the verdict is unchanged, the body is just wrapped one layer deeper.

## 5. What's in the package

```
SKILL.md                        master instruction file: iron rules / input contract / pipeline / output / degradation / boundaries (must read)
README.md / README.en.md        this pair (Chinese source of truth / English translation)
CHANGELOG.md                    version history
references/event-taxonomy.md    event taxonomy (the closed type set is the checker as it now stands; the table is a human-readable mirror) + case law on row-splitting, carry-over notes, confidence-tier L3 marking
scripts/check_calendar.py       the full gate set (pure stdlib, --help works; word sets and guard inventory = the script and fixtures as they now stand, run the two lines below)
                                 note: which words count as rating words, banned words or self-confession words, and which event types are in the closed set, is never listed in full here — the judgement is the checker as it now stands, self-checkable from any directory (the command carries the installed path):
                                     grep -n -A3 "BANNED_RE = \|RATING_RE = \|HALLUCINATION_RE = \|OFFICIAL_USAGE_RE = \|EVENT_TYPES = \|TYPE_ANCHORS = \|SIX_RE = " ~/.workbuddy/skills/catalyst-calendar/scripts/check_calendar.py
                                     bash ~/.workbuddy/skills/catalyst-calendar/scripts/fixtures/run_fixtures.sh (guard inventory and pass state, run in this package)
                                     Installed elsewhere: replace ~/.workbuddy/skills/ with your own skills directory; on Windows: C:\Users\<username>\.workbuddy\skills\catalyst-calendar\scripts\check_calendar.py
                                     Both lines use POSIX tooling (grep / bash) — on Windows run them in Git Bash or WSL. The first prints those seven judgement definitions with context: the rule source itself, not a per-sentence classifier;
                                     the only two exemptions are the type column (never scanned) and official-disclosure word shapes (a bare "increase/decrease of holdings" is not exempted). Word and type examples here are not an exhaustive claim.
```

## 6. FAQ and anti-patterns (what you try to do -> this skill refuses, because -> where to go instead)

This section only re-assembles refusal clauses and fixture shapes that were already reviewed; it adds no new
promise. Banned-word families are named by category here, never listed in full - the authoritative set is
whatever `check_calendar.py` contains right now (locator command in section 5).

| What you try | Does it work, and why not | Where to go instead |
|---|---|---|
| Derive a deadline by adding the plan's duration to the announcement date | **No.** All date arithmetic was revoked: start day, calendar vs trading days, inclusive bounds, and which version supersedes which were never defined (v1 allowed it, adversarial review took it back) | A row exists only when the announcement itself states the full date; otherwise there is no row and `progress.md` carries one line of reasoning |
| Mark which rows are good news and which are bad | **No.** Events are stated, not judged; that word family has no exemption (the only column never scanned is the type column) | Leave the judgement to a person; every cell this skill ships stays date + anchor |
| Put rumoured or expected events into the calendar | **No.** The first gate needs a filed disclosure **and** an explicit date | Add the row once the disclosure lands; progress notes with no pre-known date go to the trailing already-occurred section, never as forward rows |
| Run a whole portfolio at once (dozens of issuers) | **No.** Issuer set is capped at 10 (machine-checked); beyond that per-issuer anchors degrade | Split into batches of at most 10, each with its own ledger |
| Ask which date is a good moment to act | **No.** Timing is not a calendar output | Use `tear-sheet` for a pre-meeting page, `dd-checklist` for an anchor-bound risk ledger |
| Extrapolate the next meeting or filing date from past rhythm | **No.** Invented dates are the hallucination family this gate targets | A row appears only when a notice carrying the actual date is on record |

## 7. When something goes wrong (symptom -> cause -> recovery)

**Whatever is absent from this run's tool output is written as "not found"**: a parameter, field or enum value that does not appear there must not be filled from memory - write "not found" and log it on the pending or coverage list; a blank never stands in for it.

**Error-level findings are blockers**: never describe them as harmless, ignorable, or shippable-as-is - fix them, or declare them explicitly on the deliverable.

Shapes below are taken from **the current output** of `check_calendar.py`, captured by running it: a failure is one line `FAIL: <file> (N items)`; each detail line **starts with an error-code prefix (one of the five `E-*` codes), then the original check label** (`[E-FORMAT] [参数] (args)`, `[E-BANWORD] [禁词] (banned)`, `[E-ANCHOR] [双向] (bidirectional)` and so on), followed by the line number and that check's spec; the final `code legend:` line lists only the codes actually used, with their handling. A clean pass prints `PASS: <file> (... all gates passed, table rows N, --window ...)`.

The five codes are a **closed, suite-wide identical** set (this package and its four siblings share the table verbatim): `E-FORMAT` (format/input/row-order), `E-ANCHOR` (missing or broken anchor chain), `E-BANWORD` (banned / rating / hallucination / human-slot hit), `E-COVERAGE` (counts, coverage, declarations disagree), `E-LEDGER` (ledger state machine or cross-link broken). This page does not restate each code's handling - **the handling is printed in the `code legend:` line itself**; the full set and its classification live in the script as it now stands (paste one line from anywhere, swapping `E_LEGEND` into the grep in section 5):

    grep -n "^E_LEGEND" ~/.workbuddy/skills/catalyst-calendar/scripts/check_calendar.py

| Symptom (detail prefix) | Cause | Recovery |
|---|---|---|
| `[E-FORMAT] [表] (table) / [日期] (date) / [序] (order)` | Header, column slots, date shape or row order against the contract | Fix per the spec in the brackets and re-run; delete a row you cannot fix instead of filling it |
| `[E-FORMAT] [参数] (args) missing --window(...)` | The formal command requires the window (anti wall-clock) | Add `--window YYYY-MM-DD~YYYY-MM-DD`, matching the declared title window verbatim (a mismatch emits its own window detail) |
| `[E-ANCHOR] [双向] (bidirectional) row N anchor '...' has no entry in sources` | The anchor was never booked, or booked without a matching raw snapshot / hash | Add the `sources.jsonl` line and store the raw response under `evidence/` (hash-verifiable), or delete the row. Never invent an anchor to close a chain |
| `[E-BANWORD] [禁词] (banned) / [评级] (rating) / [幻觉] (inference) ...` | A judgement, rating or inference family appeared in the deliverable | Follow the printed legend: rewrite neutrally or delete. The type column is the only one never scanned; full word set via section 5 |
| `[E-COVERAGE] [摘要] (summary) ...` | Summary or counts disagree with the main table (including a missing reserved-area declaration) | Complete the ledger category by category, or mark "not found" honestly - do not delete rows to make counts match |
| A channel is not installed / a category returns nothing | Channel missing, or that category has no public tool | Take the degradation path: the user pastes the announcement list (marked user-supplied, still snapshotted into `evidence/` with its source level); without the research run that category reads "not found" - common sense never fills a date. The price is coverage |
| A traceback instead of `FAIL ... (N items)` | An incident: this gate is defined as pure stdlib, no network, no crash, every parse point wrapped | Stop: log the document and the exact command in `progress.md` and report it; run the guard samples from section 5 first to tell a bad document from a broken script. Do not silence the gate |

## 8. How to ask (three positive examples, one counter-example)

**Ask with a point in time; the output states its data date**: give the reporting period, reference date or look-back window in the request; the deliverable labels its **data date** on the first line, and when that differs from the date you asked about, the text never says "today" or "latest" - it reads "as of <date>".
Section 2 carries the simplest phrasing. These three are other shapes it handles, and the counter-example is an
adjacent request that genuinely belongs to a sibling skill.

- **Positive (many issuers + chosen categories + output dir)**: "Ten holdings: Midea, Oriental Yuhong, CATL, BYD,
  China Merchants Bank, Yangtze Power, ZTE, Poly Developments, Haier, Sungrow. Only unlocks and regulatory reply
  deadlines in the next 60 days, skip the other categories, write to `~/work/cal/`" - categories can be narrowed and
  the window can differ from the default; anything missing falls back to the documented default and is echoed back.
- **Positive (single issuer, spoken window)**: "Which confirmed dates does Midea have next month?" - the window is
  expanded to explicit start and end dates and echoed, so the ledger shows what was actually used.
- **Positive (English)**: "List the confirmed dates in the next 90 days for my holdings: Midea, Oriental Yuhong."
  The frontmatter trigger phrase face is currently Chinese-shaped, so English users are better off naming the skill
  (`catalyst-calendar`) explicitly rather than relying on a fuzzy match.
- **Counter-example (adjacent need, not this skill)**: "Lay out the risk items of these names and also account for
  whatever cannot be checked" - that is `dd-checklist`; "give me a one-pager before the client meeting" - that is
  `tear-sheet`. This skill only arranges dates that are already certain.

## 9. Current status (the blunt list)

- **Public with the repo**; **the full multi-issuer end-to-end delivery run has landed (back-filled 2026-09-21)**: 10 issuers × 90-day window with the evidence chain enforced end to end, the full-form check_calendar exit 0; full-window reality: 1 anchorable upcoming row inside 10 issuers × 90 days (an extraordinary shareholders' meeting whose notice states the date), the other 9 issuers carry an empty forward section **with an attribution line**; the statutory Q3-report deadline 2026-10-31 is derivable in principle but the statute channel returned no source text in this run, so nothing was entered (no anchor, no entry) — skipping the `+derive` step on the first pass was a pipeline gap, now back-filled and turned into a required disclosure line.
- **Release surface**: repo visibility is governed by the root README and `CHANGELOG.md`; whether this package reaches any skill marketplace is not decided by the package documents themselves.
- Issuer set capped at 10 (machine-checked); `margin` (broker margin ratios) deliberately excluded — irrelevant to an event calendar.
- No market-data flow (`equity_market` channel not open); **rating vocabulary is zero-tolerance by gate design** — ratings do not apply here, there is no blank left to fill.

## 10. Sources & credit

- Base: anthropics/financial-services `catalyst-calendar` (Apache-2.0) — the calendar format and task structure.
- The China-market event taxonomy and statutory-deadline derivation are **re-implemented** here against A-share disclosure rules; the data layer is fully Cue-native, no code from the base. See the repo-root `NOTICE.md`.
