# competitive-brief

**English companion of `README.md` (Chinese primary; the pair is for reading inside the repository — skill-channel pages do not resolve relative links, so this is deliberately not a clickable switch).**

Run a competitive analysis around one decision question, and ship a brief backed by an evidence chain.

```
+brief "Should we enter the compliance-tool market for North American small and mid-size law firms"
  → define the decision, who to compare, and how deep to go
  → omni-reader collects the material, cue-research deep-researches and cross-verifies
  → every claim is labeled fact / inference / opinion
  → delivered: conclusion + traceability + what you still need to confirm yourself
```

## In one sentence

The core is not the process — it's the **evidence table**. Every substantive claim goes into the evidence table before it reaches the brief. If a dimension can't be filled in the table, it doesn't appear in the brief.

## Full spec

[`SKILL.md`](SKILL.md) — evidence table definition, constraints, brief rendering rules.

## Live example

[`examples/competitive-test/`](examples/competitive-test/) — a 5-person team evaluating alternatives to Cursor:
- [Evidence table](examples/competitive-test/evidence-table.md) (23 rows, 87% fact)
- [Brief](examples/competitive-test/brief.md)

Sources verified via omni-reader parsing cursor.com/pricing, claude.com/pricing, and GitHub READMEs.

## Dependencies (recommended)

- `cue-omni-reader`: parse web pages / PDFs / audio / video → extract text into evidence table
- `cue-research`: cross-verify, deep research

Both are free. The skill still runs without them, with reduced capability.

## Domestically reachable evidence paths (when overseas sources do not load)

The live example in this package draws on `cursor.com/pricing`, `claude.com/pricing` and a GitHub README - and those
examples stay exactly as they are, because they are what that run actually used. If your network cannot reach overseas
sites, substitute the three paths this package already supports; **the output shape does not change**:

1. **Hand domestic public pages to `cue-omni-reader`.** Vendor Chinese sites, product documentation sites, app-store
   listing pages, public filings and prospectuses on exchange disclosure platforms, and public industry-media reports.
   Parsed content goes verbatim into the evidence table's claim column, with source URL and parse date recorded.
2. **WeChat public-account articles and overseas pages.** These often sit behind login walls or anti-crawl measures.
   Where reachable, parse online; where not, **export the text yourself** (PDF, HTML or screenshot) and use this
   package's local-parse path - the tool reads files the user explicitly provides; it does not go fetch for you.
3. **Cross-validation** of comparative judgements goes through `cue-research`; when that run is not initiated, mark the
   line "not cross-validated".

What to do when a source is unreachable follows this package's single hard rule: **if the evidence tool fails, you may
not fill its place from your own knowledge.** `cue-omni-reader` error -> note "omni unavailable, this source is not
parse-verified"; `cue-research` error or exhausted quota -> add a line "this judgement is not cross-validated".
Cached knowledge or speculation must never masquerade as a sourced row.

> This section promises no unopened data domain and no promise that a specific site will load. It states how to get
   evidence through channels that already exist, what to mark when you cannot, and why an empty row is not an option.
   Domestic substitutes carry the **same format and the same marking duties** as overseas sources, and neither is belittled.

## FAQ and anti-patterns (what you try -> this skill declines, because -> where to go)

This package is a methodology: it ships **no executable gate**, so anti-patterns are held only by the evidence table
and the coverage statement. Judgements follow `SKILL.md`'s constraints and `references/evidence-standards.md` as they
stand; nothing below re-lists them exhaustively.

| What you try | Declined? Why | Where instead |
|---|---|---|
| Ship a "roughly right" brief first, decide the decision question later | **No.** Constraint one: decide before filling. A brief whose "what changes once I know this" cannot be stated is not made | Narrow the decision question first, then who to compare and how deep |
| Keep a dimension where only 1/3 of competitors have data | **No.** Constraint two: unfilled dimensions do not go into the comparison table | Move it to the not-covered list and say so in the coverage statement |
| Treat "my guess" as a kind of source | **No.** Constraint three: rows with unreliable sources are not written; speculation is not a source | Mark it `inference` with the basis named, or drop the row |
| Fill the claim from memory because the parse tool failed | **No** - this is the package's one hard rule. Readers of an unmarked brief assume every line has a source | Note "not parse-verified / not cross-validated", leave the cell empty and count it in coverage |
| A full-looking brief equals complete work | **No.** Completeness is answered by the coverage statement: rows filled, how many fact / inference / opinion, which dimensions uncovered | Attach coverage at delivery (constraint four); say plainly what is missing |
| Take a vendor blog's own performance claims as fact | **No.** Claims are graded fact / inference / opinion, and vendor self-description is a claim needing verification | Cross-validate, then downgrade or relabel; unverified stays labelled |

## When something goes wrong (symptom -> cause -> recovery)

**Whatever is absent from this run's tool output is written as "not found"**: a parameter, field or enum value that does not appear there must not be filled from memory - write "not found" and log it on the pending or coverage list; a blank never stands in for it.
This package has no scripts, therefore **there are no error codes to report**. The rows below cover process stalls and
follow only the constraints already written in `SKILL.md` (no new vocabulary, no promise of tool capability):

| Symptom | Cause | Recovery |
|---|---|---|
| `cue-omni-reader` fails / page will not load | Site unreachable, login wall, or an image-only page that cannot be parsed | Mark the row "omni unavailable, this source is not parse-verified"; ask the user to export it and use the local-parse path, or switch to a domestic public source. **Do not substitute your own fill** |
| `cue-research` errors or quota is exhausted | Dependency unavailable, or spend not approved | Add "this judgement is not cross-validated"; report the cost before launching research and let the user decide |
| A dimension has only scattered rows filled | Material coverage is thin - a sourcing problem, not a rendering one | Move it out of the comparison table into the not-covered list; add material instead of padding rows |
| A conclusion paragraph has no traceable basis | A claim entered the brief before it entered the evidence table | Go back to the table, add the row labelled `fact` / `inference` / `opinion`; delete sentences you cannot ground |
| The decision question is too big to fill against | The question does not sit at the level where it changes an action | Narrow it (who decides, under what condition the answer flips, how deep) and refill |
| The coverage statement cannot be written | Rows and labels were never reconciled | Before delivery count: total rows, fact / inference / opinion each, and the uncovered dimension list. If you cannot count it, it is not done |

## How to ask (three positive examples, one counter-example)

**Ask with a point in time; the output states its source date**: give the reporting period, reference date or look-back window in the request; the deliverable labels its **source date** on the first line, and when that differs from the date you asked about, the text never says "today" or "latest" - it reads "as of <date>".
- **Positive (a single decision question)**: "Should we enter the compliance-tools market for small and mid US law
  firms - take a competitive look" - decision and competitor set first, then the evidence table; this is the shape at
  the top of this README.
- **Positive (complex: competitor set + dimensions + supplied material + domestic sources)**: "Competitors are `A`, `B`,
  `C`. Compare pricing and billing basis, deployment model, and data-compliance commitments. Material is downloaded to
  `~/cb/src/` as PDFs - if the overseas sites do not load, start from these files. Numbers from vendor blogs are claims
  to verify, never the fact column." - files go through the local-parse path with source and parse date recorded;
  unverified items become `inference` or stay empty.
- **Positive (a brief that must survive scrutiny)**: "This goes to an investment committee - every conclusion must click
  back to a source, and where a competitor beats us say so plainly." - exactly the shape of conclusion + traceability +
  what still needs confirming; uncovered dimensions go to the not-covered list instead of empty rows.
- **Counter-example (adjacent need, not this skill)**: "make me a one-pager on this company" - `tear-sheet`;
  "lay out anchor-bound public risk facts for this listed issuer and account for what cannot be checked" -
  `dd-checklist`; "turn these two announcements into an updatable knowledge package that separates new facts, conflicts
  and caliber differences" - `cue-omni-ontology`. This package does the evidence chain around one decision question.

## Version

The `SKILL.md` frontmatter `version` is the single source of truth; see [`CHANGELOG.md`](CHANGELOG.md) for history.
