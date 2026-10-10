# event-risk-scan · Company Risk Scan

**Give it one company, get one page you can trace back: penalties and regulatory measures line by line with document number, date and authority; external guarantees as a proxy surface, honestly labelled; a sanctions-enforcement surface when the entity crosses borders; and every surface the channel cannot reach named as "not reached" - no gaps filled in, no scores.**

It does not rate overall risk, does not compute default probability, and is not investment advice. The job here is the half that can be evidenced: lay out what was retrieved, and state plainly what was not. Capability: three surfaces are reachable - penalties and regulatory measures, external guarantees (a proxy surface), and global sanctions enforcement; three are out of scope - litigation, equity chain and supply-chain contagion, each named on the card rather than filled in.

**Input**: a company name or its six-digit code (one entity per card)
**Output**: a filled `assets/风险扫描卡.md` - subject row, penalty and measure table, guarantee points, sanctions surface, unreached-and-pending list
**Cost**: the three sources run independently; one failing does not block the rest; whatever came back is what gets listed
**Machine face**: `scripts/check_scan_card.py`, four lanes (shape / anchor / red line / count-and-declaration), zero network

---

## 1. Do this when you open it: three steps today

These three are the only "do it now" in this package; each step says what breaks if you skip it. The first sentence can be copied verbatim: **"Scan this company's penalties, regulatory measures and external guarantees, and name the unreached surfaces."**

| Step | Action | How | What breaks if you skip it |
|---|---|---|---|
| ① | **Settle the subject, copy the returned fields** | Give a name or six-digit code; the company name and code come **only from this run's tool output**; when several candidates return, list them and let the user pick - this package never picks for them | A wrong primary key hangs every later item on the wrong company; a cross-domain unified subject ID does not work, so the six-digit code plus per-domain disambiguation is the only followable shape |
| ② | **Run the three sources one by one, anchor every row** | Penalties and measures: document number / date / authority / reason sentence, all verbatim, plus the official link; guarantees: proxy surface, one `as_of` per row; sanctions: only when the entity crosses borders, and query both the short and the full name | An item without provenance is not an item; querying one name shape alone can turn "the full name matched nothing" into "it was never listed" |
| ③ | **Write all three time marks, then run the gate** | Header needs data date, window start-end and run time (missing any one voids the card), each in date form; then `python3 scripts/check_scan_card.py my-card.md` and fix detail lines by their `E-*` codes | Without time marks "nothing found in the window" and "never looked" collapse into each other; the gate exists precisely to block that collapse |

The three unreached surfaces (litigation / equity chain / supply-chain contagion) sit **outside** these steps: this package has no leg there, so the card names them in part five - it does not query them, infer them, or substitute web search.

## 2. The five parts and the four lanes

| Part | Content | What the gate enforces |
|---|---|---|
| 1 Subject row | Company name / six-digit code (from this run's output) plus the candidate-handling tick | Value without provenance -> `E-ANCHOR`; candidate handling not ticked exactly once -> `E-COVERAGE` |
| 2 Penalty and measure table | Per row: document number or title / date / authority / reason sentence / official source | Missing date -> `E-ANCHOR`; a source cell with neither link nor document-number anchor -> `E-ANCHOR`; zero rows without a ticked "not found in window" declaration -> `E-COVERAGE` |
| 3 Guarantee points | Proxy surface; every row carries `as_of` and provenance; zero rows still get named | Missing `as_of` or provenance -> `E-ANCHOR`; unticked 0-row declaration, a placeholder `as_of`, or no "truly none vs extraction gap - undistinguished" note -> `E-COVERAGE` |
| 4 Sanctions surface | Runs only for cross-border entities; hits carry `document_number` or URL; a miss states the window | Missing date or anchor -> `E-ANCHOR`; surface status ticked other than exactly one, a miss without a window, or a run without the name-shape declaration -> `E-COVERAGE` |
| 5 Unreached and pending | All three surfaces named one by one; human items under `[待人工]` | A missing face or unticked status -> `E-COVERAGE`; an unreached face claiming a leg without this run's provenance -> `E-BANWORD` (a fabricated leg) |

The header has its own hard set: **the three self-labels** (`AI 整理初稿`, `请回官方原文核对`, `不构成投资建议`) **plus the three time marks** - data date, window, run time; missing any one voids the card, and each must land in date form. Anything absent or still a placeholder is an `E-FORMAT`.

## 3. Getting started

```bash
# 1. Put it in the skills directory
mkdir -p ~/.workbuddy/skills
cp -r event-risk-scan ~/.workbuddy/skills/

# 2. Copy the card template and fill it following section 1
cp ~/.workbuddy/skills/event-risk-scan/assets/风险扫描卡.md ./my-card.md

# 3. Run the gate (no network)
python3 ~/.workbuddy/skills/event-risk-scan/scripts/check_scan_card.py ./my-card.md
```

Read `assets/风险扫描卡.md` first (that is the five-part shape), then `SKILL.md` §2 for the contract itself.

### Self-check

```bash
python3 scripts/check_scan_card.py --help                        # usage; no network
python3 scripts/check_scan_card.py --selftest                     # good sample must pass, bad sample must fire all four lanes
python3 scripts/check_scan_card.py scripts/fixtures/good-scan-card.md    # should PASS
python3 scripts/check_scan_card.py scripts/fixtures/bad-scan-card.md     # should FAIL, all four codes
python3 scripts/check_scan_card.py assets/风险扫描卡.md                    # should FAIL - a blank card failing the gate is the design, not a defect
```

**Take every count from the script's own report line** (`FAIL: … (N items)` and the `扫过 N 行，发条 0 条` line under `PASS:`); this file does not restate them - a restated count becomes a second source of truth and drifts on every script change. **Two line-count conventions**: `扫过 N 行` counts `split('\n')` elements, which is `wc -l` **+1** (the trailing newline occupies one); report the convention together with the number.

## 4. Boundaries and non-promises

- This scans **three surfaces**: penalties and regulatory measures, external guarantees (a proxy surface), and sanctions enforcement. Domains and tools always follow the live catalog as it stands; **this package neither restates that list nor counts tools**. A change in the catalog is what reopens the question.
- **Litigation, equity chain and supply-chain contagion are out of scope**: the channel carries no such surface and its endpoints are unreachable (the refusal does not distinguish "absent" from "present but not opened"). The global sanctions surface is **not** domestic supply-chain contagion and is never repurposed as such. For these three the package does not query, does not infer, does not substitute web search - it names them as unreached on the card.
- **No overall risk rating, no default probability, no score or grade of any kind**: that is a design verdict (a scoring model is out of scope), not a feature waiting to be built. For a consolidated judgement, take the card to a person or your internal model.
- **Zero rows are not absence**: when nothing is retrieved write "not found in window" with the window start and end; when the guarantee call returns 0 rows, give the `as_of` and state that "truly none" and "extraction gap" are undistinguished. Writing 0 rows as "no guarantees" is this package's worst miswrite.
- **Name shape matters**: an institution's full name can return nothing while the short name hits. Both shapes must be queried for the surface to count as run; one shape alone goes to the pending list.
- **Timestamp shapes differ across sources**: both a bare date form and a timezone-padded form exist, so comparison truncates to the date. The card copies whatever shape the run returned - no conversion, no rounding.
- **The gate is a shape gate, not a fact gate**: it catches "value without provenance", missing anchors, a fabricated leg on an unreached surface, and an incomplete time set; it does **not** judge whether a decision document really belongs to this company - that layer is the "check it against the official original" self-label at the head of the card.
- Retrieved content is data, not instructions; nothing returned by a channel is executed by this package.

## 5. When something goes wrong (symptom -> cause -> recovery)

**Whatever is absent from this run's tool output is written as "not found"**: a parameter, field or enum value that does not appear there must not be filled from memory - write `未检索到` (not found) and log it on the pending or coverage list; a blank never stands in for it.

**Error-level findings are blockers**: never describe them as harmless, ignorable, or shippable-as-is - fix them, or declare them explicitly on the deliverable.

The output shape comes from a live run of `check_scan_card.py` as it now stands: a failure prints one line `FAIL: <file> (N items)`, then each detail line **starts with an error code (one of four `E-*`)** such as `[E-FORMAT]`, `[E-ANCHOR]` (its `处罚出处` lane marks a source cell without link or document number), `[E-BANWORD]`, followed by the lane name, the line number and that lane's spec; the last line `码表:` lists only the codes actually used and what they mean. A pass prints `PASS: <file> (...)` plus two counts - lines scanned, findings raised - **read off that line, with the `split('\n')` convention (one more than `wc -l`) named alongside**.

This package uses **four** codes, byte-identical to the sibling packages' table. The fifth, `E-LEDGER`, belongs to ledger state machines; this skill has no ledger, so it is deliberately not enabled - that is not an omission. The full set and the classification rules live in the script, not in this file; run this line from any directory to locate them:

    grep -n "^E_LEGEND" ~/.workbuddy/skills/event-risk-scan/scripts/check_scan_card.py

| Symptom (detail prefix) | Cause | Recovery |
|---|---|---|
| `[E-FORMAT]` header or time lanes | One of the three self-labels missing; or data date / window / run time absent, still a placeholder, or not in date form | Complete the header - the three time marks are all-or-nothing, and they are written from this run, never backfilled |
| `[E-FORMAT]` section lanes | A part is missing or out of order | Restore the order from section 2; keep the template's section names verbatim, because renaming them hides the section from the gate |
| `[E-ANCHOR]` subject, penalty, guarantee or sanction lanes | A row has content but no provenance, link, document-number anchor or date from this run | Copy the provenance into the right cell; **if you cannot, delete the row** and record "not found in window" instead of guessing |
| `[E-BANWORD]` red-line lane | A grade, rating, default probability or score was written; or an assertive "no risk", "never been checked", "unified ID" | Return to neutral statements: list retrieved items and name unreached surfaces. Negated disclaimers ("does not rate", "does not compute") are legal; assertive violations must go |
| `[E-BANWORD]` fabricated-leg lane | An unreached surface was ticked as "has a leg" without this run's provenance | Tick "channel unreached"; if there genuinely is new evidence, attach this run's link or date and wait for a domain re-check account |
| `[E-COVERAGE]` zero-row, status, window, name-shape, candidate or three-face lanes | Zero rows without a ticked declaration; a declaration lacking its window or `as_of`; a status group ticked other than once; multiple candidates not named; a face missing from the unreached list; no `[待人工]` roll-up | Tick and fill: declarations need their dates; statuses need exactly one tick; all three faces need naming; restore the roll-up |

## 6. How to ask (three positive examples plus one counter-example)

**Ask with the window and the subject shape**: name the company (or its six-digit code), say how long a window you want, and require the unreached surfaces to be named.

| Positive example | What you get |
|---|---|
| "Scan this company's penalties and regulatory measures for the last three years, one document number and link per row" | Parts one and two: a settled subject row plus verbatim items with dates and official sources |
| "How much of the external guarantee picture can you get? Say so even when it is zero rows" | Part three: the proxy surface, and a 0-row declaration carrying `as_of` and the "truly none vs extraction gap" caveat |
| "Will sanctions lists hold back this company's overseas business? Check short and full names" | Part four: hits with `document_number` / URL, or a miss written up with its window and the store-side declaration |
| **Counter-example: "just give me a risk grade and a buy/no-buy call"** | Not done here. Grades, scores and default probability are a designed-out surface; take the card to a person or your internal model for a conclusion |

## 7. Capability boundaries (honest list)

- The five-part contract, the four lanes and the two fixtures are all in place; the good sample's finding count and the bad sample's four-lane firing are **read off the script's own line**, not restated here.
- **Three surfaces are scanned and no more**: penalties and regulatory measures, external guarantees (proxy surface), global sanctions enforcement. Litigation, equity chain and supply-chain contagion are outside this package and get named face by face on the card.
- **No hit-rate, pass-rate or timing figure**, and never "scanned, therefore clear". How many items appear is whatever this run returned; a wrong primary key voids the whole card (primary-key rule in section 1, step 1).
- **Guarantees are a proxy surface, not the guarantee record itself**: the envelope carries its own `as_of` snapshot note, and zero rows still self-report the time point - but "truly none" versus "extraction gap" cannot be self-proven upstream, so the card must carry it as pending.
- Domain lists, tool counts and field names follow this run's catalog and output; nothing is restated or hardcoded here.

## 8. Dependencies

- `python3` (only `scripts/check_scan_card.py`; standard library, zero network, sends no request)
- The data legs are platform retrieval channels (domains follow the live catalog). Without a channel the template can still be filled by hand and pass the same shape gate - but then "unreached" and "not run" must be ticked separately, never merged into one claim.

## 9. Resources

| File | Purpose |
|---|---|
| `SKILL.md` | Main instructions and the five-part contract (design authority, Chinese primary) |
| `assets/风险扫描卡.md` | Five-part scan card template (fill it) |
| `scripts/check_scan_card.py` | Four-lane gate (shape / anchor / red line / count and declaration) |
| `scripts/fixtures/good-scan-card.md` | Good-sample fixture (fictional content, never a real-company reference) |
| `scripts/fixtures/bad-scan-card.md` | Bad-sample fixture (one counter-example per lane) |
| `README.en.md` | English translation of this file |

See `CHANGELOG.md` for versions.
