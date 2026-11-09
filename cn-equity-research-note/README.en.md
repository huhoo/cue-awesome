# cn-equity-research-note

**For a company that has not yet reported, produce a seven-section equity research draft: business breakdown, competitive position, drivers and risk list, each finding anchored to one dated source, every gap named, every judgement left to a human.**

Bullet points are not scarce; **what is scarce is a bullet you can trace back to one dated source**. The difference is not layout but two hard gates: a finding without an anchor never enters a content section, and a gap that was not named never passes the machine check.

**Input**: a batch of material (announcement text / research reports / news / parsed documents) plus the subject and the retrieval window - or a question to be broken down
**Output**: a seven-section research draft (one-sentence conclusion / business breakdown / competitive position / drivers / risk list / gaps and definitions / sources)
**Cost**: a seven-section contract plus one machine check; whether the channel legs (announcement search / text parsing) are switched on decides the multi-source evidence and per-finding provenance layer - what each path lacks and which to take is written in sections 2 and 4
**Machine check**: `scripts/check_note.py`, five lanes (format / anchors / red lines / two-way gap naming / earnings-period boundary), zero network; the counter-evidence matrix lives inside that script

**This is not the same thing as `cn-earnings-note` (this sentence is why the package exists)**: that one does the **already-reported** review - four-period deltas, line-item tie-outs, guidance versus delivery, coverage ledger - and its input must include financial statements; this one does **pre-report** equity research - how the business breaks down, where the competitive position sits, what the drivers are, what the risks are - and its input is announcements, research reports and news, **with no financial statements required**. Use this one in the reporting gap, use that one to tie out the numbers once the statements land; the two neither overlap nor substitute for each other. The `财报状态：` header line is the machine-checkable entry to that boundary - writing `已出` gets you named and sent to the other package.

---

## 1. Open it, do these three steps

| Step | Action | How | What happens if you skip it |
|---|---|---|---|
| 1 | **See the shape first** (30 seconds, no network, no billing) | `bash scripts/fixtures/run_fixtures.sh` - five tiers in one run: checker self-test, good and bad samples one by one, skeleton without a channel, the skeleton failing on purpose, boundary forms one by one. Last line reports 档数=5｜不合=0｜不可判=0 | Neatly formatted is not the same as sourced; this tier shows the difference in half a minute |
| 2 | **Register sources, attach one per finding** | One source per line in section 7: `- [S#] title (URL ｜ retrieval date YYYY-MM-DD)`; every finding line in the four content sections ends with one `[S#]`. If two sources disagree, keep both lines - no merging, no averaging | A source line without a retrieval date fires `E-ANCHOR`; a finding without an anchor fires `E-ANCHOR` too, and fixing it afterwards costs more than attaching it now |
| 3 | **Pass the check, then hand it to a human** | `python3 -B scripts/check_note.py <note.md>`, fix what each `E-*` line names; the result is still a **draft** - whether and how to conclude is yours | Unnamed gaps, leaked verdict words and unmatchable anchors all travel with the draft into a human's judgement; those three are format-level, the substance still needs the original text |

Ratings and target prices, buy/sell and timing advice, and already-reported line-item reviews are **not in these three steps** - this package is accountable only for laying this set of material out faithfully as a research draft, and only at the format level.

## 2. Install → connect the channel → produce

**Install this skill (primary route)**: `npx skills add huhoo/cue-awesome --skill cn-equity-research-note` - this line installs this package only; afterwards re-list installed skills on your side and the name `cn-equity-research-note` must appear, otherwise the files are not in place. Without a CLI environment the fallback is to copy this directory into your host's supported skills location (`~/.workbuddy/skills/`).

The evidence legs here are two optional auxiliaries: `cue-data-mcp` (locating announcements and research reports, the data leg) and `cue-omni-reader` (turning PDFs, pages and recordings into quotable text, the parsing leg). The channel route:

```bash
CATALOG="https://cuecue.cn/api/mcp-catalog"
curl -s "$CATALOG" | python3 -c 'import json,sys
rows=json.load(sys.stdin)["data"]["domains"]
[print(r.get("id"), r.get("external_status"), (r.get("routing") or {}).get("url", "-")) for r in rows]'
DOMAIN_ID="<replace with a domain id listed by the line above>"
ROUTING_URL="$(curl -s "$CATALOG" | python3 -c 'import json,sys
rows=json.load(sys.stdin)["data"]["domains"]
hit=[r["routing"]["url"] for r in rows if r.get("id")==sys.argv[1] and r.get("routing")]
print(*hit,sep="\n") if hit else sys.exit("not found: that id is not in the live catalog (or it has no routing.url) - run the listing line first, then fill it in")' "$DOMAIN_ID")"
[ -n "$ROUTING_URL" ] || { echo "no value: ROUTING_URL is empty - list the ids first, then set DOMAIN_ID to one of them" >&2; exit 1; }
curl -s -X POST "$ROUTING_URL" \
  -H "Authorization: Bearer $CUE_API_KEY" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' \
  -w '\nHTTP %{http_code}\n'
```

`CATALOG` is the only catalog literal on this face (assigned once, not restated in prose); `$ROUTING_URL` is taken verbatim from that domain's `routing.url`. The three layers prove different things and are never equivalent: **skill installed != credential configured != channel connected**. The anonymous `GET` proves **catalog reachability** only - this face does not call that "connected"; the key is proven *accepted* once a `tools/list` reply comes back with it attached, pass = HTTP 200 with a non-empty `result.tools` (shape only; no tool names or counts are promised). The parsing leg is the MCP connection in your host: **once connected**, the tools your host lists should show these names - a remote-only surface exposes `parse`, `get_parse_status` and `cancel_parse` (three), a Bridge surface adds `read_result`, `read_outline`, `discard_result` and `save_result` (seven in total), so one fixed count cannot judge both routes. Names being present only proves they are exposed, not that parsing works - the URL route is verified by one real URL parse, the local-file route by one real local-file parse (remote-only cannot read local files); this package neither self-certifies nor runs either for you. Domains absent from the catalog are neither installed nor promised here, and a connection error does not mean the domain has no data. The key comes from your local credential facility - never into chat, never echoed back; this block adds no new credential read. Parsing and search spend follows the server reply; this package neither estimates nor pays it, and always asks before anything is spent. Configuration pointers: the data-leg page <https://cuecue.cn/hub/mcp> and the parsing-leg page <https://cuecue.cn/hub/omni-reader> (this package may use both - the data leg locates announcements and research reports, the parsing leg retrieves body text from long attachments and PDFs); to obtain a key go to <https://cuecue.cn/hub/api-key>.

## 3. Offline sample: see the shape in 30 seconds

```bash
cd cn-equity-research-note
bash scripts/fixtures/run_fixtures.sh
# tier 1  checker self-test: the good sample passes, the six bad samples each fire their own lane
# tier 2  good and six bad samples one by one: each reports its own exit code and code set, never merged into one total
# tier 3  skeleton without a channel: scripts/make_outline.py lays sources.jsonl out as a fill-in skeleton
# tier 4  the skeleton through the checker: E-FORMAT is expected - the conclusion slot stays a placeholder on purpose
# tier 5  boundary forms one by one: a factual share-dealing line is not red / a recommendation is red / 已出 names the sibling package / an unrecognised status value is a format red / a hedging word is red
```

On your own material it is the same two commands:

```bash
python3 -B scripts/make_outline.py --sources your-sources.jsonl --out my-skeleton.md
python3 -B scripts/check_note.py my-skeleton.md
```

Each source line needs three keys - `title`, `url`, `asof` (retrieval date, `YYYY-MM-DD`); `id` is optional and defaults to `S1`, `S2`... in line order. Lines that are not valid JSON, that miss a key, or whose date is not `YYYY-MM-DD` are **rejected and named line by line**, never skipped silently; if nothing is usable the script exits 1 - an empty list is not a skeleton, it is the absence of sources.

## 4. Dependencies and what each path costs

**Primary route (channel on)**: the data leg locates announcements and research reports, the parsing leg retrieves body text from long attachments and multi-page PDFs. With both legs on, this package can deliver the layer where every finding returns to one dated original; whichever leg is missing is the layer that is missing - without the data leg, announcements and reports can only come from you directly; without the parsing leg, sentences inside attachments stop at "not retrieved".

**Fallback (zero channel)**: `scripts/make_outline.py` lays your existing material list out as a fill-in skeleton. **The cost is stated in the same sentence**: what is missing is exactly the announcement-search and text-parsing layer, so the skeleton has shape but no weighed conclusion - the conclusion slot stays a placeholder and the checker fires `E-FORMAT` by design. A skeleton is not a research draft; do not deliver it as one.

## 5. Boundaries and non-promises

- Ratings, target prices, buy/sell and timing advice are always `[待人工]`; no "recommend buying", "recommend increasing", "must rise", "guaranteed", "zero risk", "outperform the market" or "severely undervalued" claims;
- **Shareholder dealing is a factual statement, not a recommendation**: "the controlling shareholder plans to reduce no more than 2%" is registered as usual; what is banned is the recommendation form ("recommend increasing" / "recommend reducing");
- Already-reported line-item reviews are not here: four-period deltas, line-item tie-outs and the coverage ledger go to `cn-earnings-note`; writing `已出` in the `财报状态：` header gets you named by the checker;
- Do not use this package for a single source - that is a retelling; multi-source cross-checking is what it is for;
- Not retrieved means writing "not retrieved" as it is; never fill in from industry convention, and never write "no such item" in its place;
- Domains and tool names follow the live catalog; this package lists no fixed set, promises no counts, and promises nothing about whether a domain is open or how fresh its files are.

## 6. When something goes wrong

| Symptom | Where it comes from | Recovery |
|---|---|---|
| Many lines say "not retrieved" | You only have announcement titles; the body is in an attachment | Turn on the parsing leg for the original sentences; if it will not start, keep the gap named and do not fill it in |
| The data leg will not connect | Credential missing or the domain is not live | Self-check per section 2; the skeleton still works, and the cost is the sentence in section 4 |
| `E-ANCHOR` fires | A finding has no anchor, or the anchor has no matching line in section 7, or a source line lacks a URL / retrieval date | Fill in by the line numbers named; anything you cannot fill goes into the section 6 gap list - do not delete lines to make it green |
| `E-COVERAGE` fires | The body says not-retrieved but section 6 does not list it, or section 6 lists it but the body has no such statement | Both directions must line up; the same gap phrased differently is not red (matched by item coreference), only a real miss is |
| `E-SCOPE` fires | The `财报状态：` header says `已出` | Switch to `cn-earnings-note`, or move the research window into the reporting gap |
| `E-BANWORD` fires | A rating / target price / buy-sell call, or a hedging word standing in for a figure | Rewrite as a neutral statement or tag `[待人工]` on the same line; figures follow the source, and mismatched definitions go to section 6 |
| A factual line is flagged | The line is "the controlling shareholder plans to reduce no more than 2%" | The checker matches word families (only "recommend increasing / recommend reducing" fire); a bare "reduce" does not; if it still fires, check whether the same line carries another recommendation phrase |

## 7. How to ask (good and bad)

- Good: "how does this company make money and who are its customers", "where does it rank in the industry and against whom", "what drives growth over the next year", "what are the risks", "what does this announcement mean for the business".
- Bad: "is it worth buying", "what is the target price", "can I get in now", "how was the quarter" - buy/sell and timing, target prices and already-reported line-item reviews are not here; they are `[待人工]` or belong to `cn-earnings-note`.

## 8. Capability boundaries (honest list)

Market-price and fund-flow figures are outside this package (that domain follows the live catalog; if it is not open, nothing is promised); this package does no valuation modelling or financial forecasting (DCF / three-statement models belong to dedicated tools); it does not judge the merits of a proposal or the possibility of inside information; and it does not persist your files - the draft is handed back to you when it is done.

## 9. Resources

- `SKILL.md`: the seven-section contract and the red lines (the Chinese face is authoritative)
- `README.md`: the Chinese face; this file is its English companion, and the Chinese face wins on conflict
- `scripts/check_note.py`: the five-lane machine check (zero network)
- `scripts/make_outline.py`: the no-channel skeleton generator (fills in no conclusions)
- `scripts/fixtures/run_fixtures.sh`: the offline five-tier runner (zero network, zero billing)
