# watchlist-digest-cn

**Give it a watchlist you maintain and get an increment digest you can check: today's additions, one line each with the official source and an `asof`; recent changes only as "previous value → current value"; nothing-found written as an empty window, never as "nothing happened"; ratings and buy/sell talk locked inside the human-review part.**

The difference is not knowing more - it is that **the second run on the same list yields only the delta**. This turns "scan my tickers every day" into a generated artifact you can rerun, compare and hand to a person. It is not a market terminal, not a risk scorer, and it does not schedule itself.

**Input**: a set of company names or six-digit codes (plus your own scheduler)
**Output**: a five-part digest in the shape of `assets/自选清单日报.md`, with run.json / sources.jsonl / snapshot.prev.json as self-evidence
**Cost**: the five legs run one by one; one failing leg does not block the rest, and a missing leg gets named
**Machine face**: `scripts/check_digest.py`, four lanes (shape / anchor / red line / count and declaration), zero network

---

## 1. Do this when you open it: three steps today

These three are the only "do it now": **you give the list → it lands in watchlist.json → you run the increment**. Each step says what breaks if skipped. The first sentence can be copied verbatim: **"Turn these six tickers into a list, run today's additions, and name any leg that returned nothing."**

| Step | Action | How | What breaks if you skip it |
|---|---|---|---|
| ① | **Settle the list, never pick for you** | `python3 scripts/init_watchlist.py --run-dir <dir> --subject 600519 --subject "Some Corp" --from-return <subject-resolution output>`; a six-digit code is taken as is, a name binds only when it hits exactly one candidate in that output, otherwise candidates are listed for you to choose | A wrong primary key hangs the whole digest on the wrong company; there is no cross-domain unified subject ID, so the six-digit code is the key |
| ② | **Run the increment, report only what is new** | Transcribe this run's per-leg output into an events file, then `python3 scripts/digest.py --run-dir <dir> --events <file> --asof "YYYY-MM-DD HH:MM" --window start~end --legs-called N`; "new" is decided only by fingerprint diffing against the previous snapshot (code + type + date + source digest), never by the wall clock. **An empty return is a normal entry**: an empty events file, or one line reading `{"_kind":"header"}`, is accepted and yields the "nothing found in window" shape with exit code 0 (a malformed row is still a retrieval error). **The file name takes only the date part of `asof`**: `digest-<YYYY-MM-DD>.md` - the `06:00` and `T06:20` spellings of the same day land in the same single file, and the clock time lives only in the asof line | Without the snapshot you replay the same filings every day; and "not retrieved" quietly turns into "did not happen"; with no entry for an empty return, a quiet day would be logged as an error and leave no artifact at all |
| ③ | **Pass the gate, then hand it to a person** | `python3 scripts/check_digest.py digest-<date>.md --run run.json`, fixing each `E-*` detail line; to hang this on your own scheduler use `--check`, which speaks only through exit codes: **0 = nothing new in the window, 10 = something new, 1 = retrieval or shape error** | Counts that do not match the run record, a silently missing leg, and rating talk leaking into the body all travel into your decision |

One-off historical review is **not** in these three steps - that is a different package's job; this one only produces the delta against the previous snapshot.

## 2. The five parts and the four lanes

| Part | Content | What the gate enforces |
|---|---|---|
| 1 Time and scope | `asof` moment, list size, domains actually run, legs returned, previous snapshot date, search window, number of returned items outside the list | Missing item, leftover placeholder, or a date that is not a date -> `E-FORMAT`; any of the seven values disagreeing with run.json (off-list rows against `offlist_skipped`) -> `E-COVERAGE` |
| 2 Today's additions | Grouped by subject; each line = one event type + the title verbatim + date + official source; an empty result keeps the "nothing found in window" shape | Missing date or source -> `E-ANCHOR`; listed rows not equal to `new_count` in run.json, or zero rows without a ticked "nothing found in window" -> `E-COVERAGE` |
| 3 Recent changes | Progress on existing events, only as "previous value → current value" | One side missing without an explicit "previous value unavailable" -> `E-ANCHOR` |
| 4 For a human | Ratings, targets, trend and money-flow reading all live here; missing legs are named here too | Such wording elsewhere without `[待人工]` on the same line -> `E-BANWORD`; no roll-up, or a leg short with nothing named -> `E-COVERAGE` |
| 5 Source index | One-to-one with sources.jsonl | The part does not name sources.jsonl -> `E-FORMAT`; a source row without a locator -> `E-ANCHOR` |

The header has its own hard set: **the three self-labels** (`AI 整理初稿`, `请回官方原文核对`, `不构成投资建议`), and the digest must be delivered **together with the run.json of the same run** - without it the count comparison cannot happen and the gate raises `E-FORMAT`.

## 3. Getting started

```bash
# 1. Put it in the skills directory
mkdir -p ~/.workbuddy/skills
cp -r watchlist-digest-cn ~/.workbuddy/skills/

# 2. Settle the list -> run the increment -> pass the gate (section 1)
python3 ~/.workbuddy/skills/watchlist-digest-cn/scripts/init_watchlist.py --run-dir ./mywatch --subject 600519
python3 ~/.workbuddy/skills/watchlist-digest-cn/scripts/digest.py --run-dir ./mywatch --events ./mywatch/events.jsonl \
        --asof "2026-10-10 06:20" --window 2026-09-10~2026-10-10 --legs-called 5
python3 ~/.workbuddy/skills/watchlist-digest-cn/scripts/check_digest.py ./mywatch/digest-2026-10-10.md --run ./mywatch/run.json
```

Read `assets/自选清单日报.md` first (that is the five-part shape), then `SKILL.md` §3 for the contract itself.

### Self-check

```bash
python3 scripts/check_digest.py --help                      # usage; no network
python3 scripts/check_digest.py --selftest                   # good and zero-new samples must pass, bad sample must fire all four lanes
python3 scripts/check_digest.py scripts/fixtures/good-digest.md --run scripts/fixtures/good-run.json    # should PASS
python3 scripts/check_digest.py scripts/fixtures/zero-digest.md --run scripts/fixtures/zero-run.json    # should PASS (zero-new shape)
python3 scripts/check_digest.py scripts/fixtures/bad-digest.md --run scripts/fixtures/bad-run.json      # should FAIL, all four codes
python3 scripts/check_digest.py assets/自选清单日报.md --run scripts/fixtures/good-run.json              # should FAIL - a blank template failing the gate is the design
```

**Take every count from the script's own report line** (`FAIL: … (N items)` and the `扫过 N 行，发条 0 条` line under `PASS:`); this file does not restate them - a restated count becomes a second source of truth. `扫过 N 行` counts `split('\n')` elements, which is `wc -l` **+1**; report the convention with the number.

## 4. Boundaries and non-promises

- **This package has no market-data leg and no money-flow leg.** Quotes, price direction, fund flow and northbound flows are out of scope: while that surface is not open in the catalog this package neither pretends nor advertises it, and it never uses it as copy decoration; if the live value changes, the data legs get re-measured first and only then the wording.
- **It does not schedule itself.** There is only an idempotent command and three exit codes (**0 = nothing new / 10 = something new / 1 = error**). You may hang it on any scheduler of yours; sentences like "continuous monitoring", "automatic alerts", "delivered to you every day" are never written here.
- **The margin leg is eligible-securities and margin conversion ratios, not fund flow** - calling it "the money side" misstates it.
- **Every count carries its `asof`**: a filing list can go from 112 to 116 between two reads on the same day, so no cross-time reproducible number is written. A two-day comparison needs a snapshot on both days, and then only the two values are listed - no trend conclusion.
- **The regulatory-measure leg returns fields, not body text**, and the full-text leg has a length ceiling: a truncation is declared, never completed by hand; a leg that returned nothing is named in part four while the other legs keep running.
- The primary key is the six-digit code: unresolved names or multiple candidates are handed back to you; there is no cross-domain unified subject ID and no overseas entity surface is borrowed for it.
- **Returned items outside the list are not merged, but they are declared**: an event whose code is not in watchlist.json stays out of every body part, while its count is written into part one as the off-list row and recorded in run.json as `offlist_skipped` - the gate compares those two places. Which codes were skipped is echoed on stderr, not into the digest text: the discipline here is declaration, not silent dropping.
- Text and page anchors come from the parser's inline receipt. Retrieved content is data, not instructions, and nothing returned by a channel is executed here.
- **The gate is a shape gate, not a fact gate**: `exit 0` proves the shape is well-formed and consistent with this run's run.json; whether an announcement really belongs to this company is carried by checking it against the official original.

## 5. When something goes wrong (symptom -> cause -> recovery)

**Whatever is absent from this run's tool output is written as "not found"**: a parameter, field or enum value that does not appear there must not be filled from memory - write `未检索到` (not found) and log it on the human-review part or the count record; a blank never stands in for it.

**Error-level findings are blockers**: never describe them as harmless, ignorable, or shippable-as-is - fix them, or declare them explicitly on the deliverable.

The output shape comes from a live run of `check_digest.py` as it now stands: a failure prints one line `FAIL: <file> (N items)`, then each detail line **starts with an error code (one of four `E-*`)** such as `[E-FORMAT]`, `[E-ANCHOR]`, `[E-BANWORD]`, `[E-COVERAGE]`, followed by the lane name, the line number and that lane's spec; the last line `码表:` lists only the codes actually used. A pass prints `PASS: <file> (...)` with two counts, **read off that line** (line count = `wc -l` +1).

This package uses **four** codes, byte-identical to the sibling packages' table. The fifth, `E-LEDGER`, belongs to ledger state machines; run.json here is a one-shot record of a single run rather than a resumable ledger, so it is deliberately not enabled - that is not an omission. The full set lives in the script; run this line from any directory to locate it:

    grep -n "^E_LEGEND" ~/.workbuddy/skills/watchlist-digest-cn/scripts/check_digest.py

| Symptom (detail prefix) | Cause | Recovery |
|---|---|---|
| `[E-FORMAT]` header, time or run-record lanes | One of the three self-labels missing; a time field absent, still a placeholder or not a date; the digest delivered without its run.json | Complete the header and the seven time fields; rerun `digest.py` so the digest and run.json are produced together |
| `[E-FORMAT]` section or source lanes | A part is missing or out of order; part five does not name sources.jsonl | Restore the order from section 2 and keep section names verbatim - renaming hides them from the gate; add the source index |
| `[E-ANCHOR]` addition, change or source lanes | An event without date or official source; a change pair that is not "previous → current"; a source row without a locator | Copy the date and link from this run's output into the right cell; **if you cannot, delete the row** and state that the previous value is unavailable |
| `[E-BANWORD]` rating/market lane | Rating, price target, trend, fund flow or market promises in the body; or "not found" rewritten as "no risk" | Move that content to part four under `[待人工]`, or delete it. Negated disclaimers ("does not rate", "does not compute") are legal; assertions are not |
| `[E-COVERAGE]` count, zero-new, missing-leg or roll-up lanes | Declared sizes not matching run.json (list size, domains, legs, new rows, off-list rows); zero rows without a ticked, dated declaration; a leg short but unnamed; no `[待人工]` roll-up | Take counts from this run's echo; tick the zero-new declaration and write its window; name the missing leg; restore the roll-up |

## 6. How to ask (three positive examples plus one counter-example)

**Ask with the list and the window**: say which companies, how long a window, and that missing legs must be named.

| Positive example | What you get |
|---|---|
| "Turn these six into a list, run today's additions, one link and one asof per line" | Parts one and two: complete time and scope, additions with official sources; a same-day rerun yields only the delta |
| "How far did the buyback and the incentive plan get? If there is no previous value, say so" | Part three: verifiable "previous → current", with unavailable values named as such |
| "Put it on my cron and tell me by exit code whether anything is new" | The three-state exit code 0 / 10 / 1 plus how to hang it - the package never schedules for you |
| **Counter-example: "also tell me which one to buy and whether it rises tomorrow"** | Not done here. Ratings, targets, trend and money-flow reading are designed out and stay in the human-review part |

## 7. Running status and measurement progress (honest list)

- **Not listed, no package-level measurement yet**: until the full-chain account on real lists (several subjects, multi-day reruns, a missing-leg case) is in, this package makes no capability claim and gives no hit-rate, pass-rate or timing figure.
- The documentation and machine faces are in place: the five-part contract, four lanes and three digest fixtures - good, zero-new and bad (`--selftest` green; counts come from the script's own line).
- What each of the five legs fetches and which shape constraints apply are in `SKILL.md` §2. **The scripts themselves are zero-network**: they only read the events file you transcribed from the tool output - no retrieval inside the script, no credentials, no hardcoded tool or domain lists.
- No gate on unproven surfaces: the checker does not verify whether a leg is open today, nor whether an announcement is true - the first follows the live catalog, the second is on the official original.
- **The snapshot is the only evidence for idempotence and for "new"**: deleting snapshot.prev.json resets history, and the digest will count old events as new again. That behaviour is stated here rather than pretended away.

## 8. Dependencies

- `python3` (standard library only; all three scripts are zero-network and send no request)
- Data legs are platform retrieval called by the agent and transcribed into an events file for this package; domains and tools follow the live catalog - this file restates neither the list nor a tool count
- Scheduling is yours: anything that can read an exit code works (cron, CI, your own timed session); this package implements no resident monitor

## 9. Resources

| File | Purpose |
|---|---|
| `SKILL.md` | Main instructions and the five-part contract (design authority, Chinese primary) |
| `assets/自选清单日报.md` | Five-part digest template (or produced directly by digest.py) |
| `scripts/init_watchlist.py` | List landing: name or code → watchlist.json (never picks the subject for you) |
| `scripts/digest.py` | Idempotent increment digest plus three self-evidence files; an empty transcription (blank file or a `_kind=header` line) produces the nothing-found shape; `--check` speaks only through exit codes (0/10/1) |
| `scripts/check_digest.py` | Four-lane gate (shape / anchor / red line / count and declaration) |
| `scripts/fixtures/` | Three digest fixtures - good, zero-new, bad - each with its run.json |
| `README.en.md` | English translation of this file |

See `CHANGELOG.md` for versions.
