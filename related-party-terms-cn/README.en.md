# related-party-terms-cn

**Hand it one China A-share related-party transaction announcement or agreement and get back eight verbatim cards: counterparty and related status, subject matter and services, pricing basis and transaction price, deal amount and annual quota, settlement and fund flows, approval procedure and recusal, independent-director mechanism, disclosure and waiver - each item carrying a verbatim quote and a source anchor. Fairness, tunneling and whether the vote passes stay `[待人工]`.**

It reads one transaction's clauses: **which related-party proposals and fund-occupation facts a company produced in a window** live in `dd-checklist` (fixed seven-column risk table), **whether the counterparty of a restructuring is a related party** lives in `ma-restructuring-terms-cn` (one item of that card), **clause highlights of any contract** live in `cn-contract-clauses` (generic shape, no governance fields here), filing lists in `announcement-daily-cn`, event dates in `catalyst-calendar`. The announcement and the agreement are the only authority - **media coverage and second-hand digests must be labelled by level**, and that boundary is why this skill exists.

## 1. Three steps to get going

1. Hand over an announcement, an agreement or a proposal: pasted text, a located disclosure page or a digest all work. For anything it does not state, demand `未检索到` instead of "these quotas are usually set for a year".
2. Read the first two sections: header declaration plus the eight verbatim items - both come out as soon as you have the document, no channel needed.
3. Check the two numeric cells: pricing basis with transaction price, deal amount with annual quota have to sit **inside that item's own quote**, and the gate first **cuts the quote into phrases and classifies mainly on that structure** (each figure looks for its owner inside its own phrase: the nearest substantive noun to its left, once units such as "per kilogram" or "no higher than" are skipped, must belong to that cell's own family to count, and a reference noun - prior-period price, market average, book value, audited figure, cumulative incurred - disqualifies it even when the cell's own noun appears elsewhere in the same phrase; only a figure with no owner in its own phrase inherits the latest own-family noun from the preceding phrases, and it inherits nothing when only reference figures appeared earlier; each cell needs its own landing for **both** elements - a qualifying figure for the numeric one, an arrangement wording for the pricing basis - so "the pricing basis is the market price, the transaction price to be decided" still counts as missing, and the pair is settled jointly only when an **affirmative** copula sits between the two nouns inside one phrase ("the deal amount is the annual quota of 86 million yuan"), while a negated copula ("is not") settles nothing and the appositional shape whose copula follows both nouns ("the deal amount and the annual quota are both 86 million yuan") is not recognised and fires as a known coverage limit for human review; a basis word sharing its sentence with "to be decided" counts as not settled, and so does the co-present shape "quota to be decided but settled quarterly", while a semicolon or full stop between the two is read correctly; ratios and periods take no part in attribution, read off the unit: a candidate ending in %, ％ or 倍 settles nothing, and neither does a money figure whose left edge ends on a ratio word) - "subject to", "to be signed separately", "to be disclosed later" are not figures; "prior-period price of 12.00 yuan", "1.2 times the market average", "book value of 300 million yuan", "410 million yuan already incurred" are reference figures; "the pricing base date is 31 December 2025" is a date; "the deal amount is 10% of the quota" and "the deal amount rose by 12 million yuan year on year" are ratios that settle no amount; when you meet one, send it to the missing-data list. One more rule: the title-mark exemption is for anchored source text only - a verdict of this card's own, wrapped in title marks ("this card concludes: the pricing is fair"), still fires even with an anchor, while quoted announcement wording that carries its anchor stays green.

## 2. Five machine checks (no network)

`scripts/check_rpt_card.py` gates the card: five sections plus item-level presence of the eight names (each name needs its own `- name:` line; a prose mention does not occupy a line) / quote and anchor per item (empty or single-character quotes and empty anchors fire) / red lines in three layers (fixed word family with the evaluative and predictive families folded in, subject word plus judgement tone in one segment, verdict prefix plus effect word) allowed only inside the `[待人工]` or explicit "not accepted" **clause** - neither the marker nor a disclaiming sentence crosses a clause, so "[待人工] whether the pricing is fair stays human; this deal will certainly pass" still fires on the second half; "the pricing is very reasonable" and "the price is basically fair" are judged exactly like "the pricing is reasonable" (intensifiers are no exemption, and the nominal suffixes - fairness, reasonableness, prudence, -degree, argument - name what is being explained rather than asserting, so they stay green, with one shared exclusion list read by both branches), and the modal character inside institutional names ("X 会") and nouns ("会 X") is washed out first, and the title-mark exemption is granted only to anchored source text - a line without `锚：`, or one where this card speaks for itself outside the brackets (conclusion / to sum up / note), keeps those words inside the domain / exactly one completeness declaration reconciled with the `未检索到` count (two contradictory declarations fire) / the two numeric cells judged mainly on a phrase structure, each cell needing its own landing for both elements - a qualifying figure for a numeric element, an arrangement wording for the pricing basis - fields parsed, that item's own quote kept, dates stripped, the domain cut at punctuation and number boundaries, and each candidate classified inside its own phrase only (nearest substantive noun to the left once units are skipped; the right side when the left is empty; an elided figure inherits the latest own-family noun from the preceding phrases but never when the preceding stretch only ever showed reference figures), with amounts, multiples and percentages all going through that one rule while ratios and periods stand aside; an element without its own landing plus no `未检索到` fires - another cell's number, a reference figure and a date cannot settle this cell's account)

```bash
python3 scripts/check_rpt_card.py --help                          # usage
python3 scripts/check_rpt_card.py --selftest                       # good sample passes, bad sample fires all five lanes, one pinned tier per family, control samples stay green, temporary files self-clean (tier count self-reported)
python3 scripts/check_rpt_card.py scripts/fixtures/good-rpt-card.md     # PASS (no findings)
python3 scripts/check_rpt_card.py scripts/fixtures/bad-rpt-card.md      # FAIL (each lane fires with line numbers)
```

## 3. Install and run

```bash
# 1. drop the skill into your skills directory
mkdir -p ~/.workbuddy/skills
cp -r related-party-terms-cn ~/.workbuddy/skills/

# 2. ask the agent for the five-section card defined in SKILL.md, save it as my-related-party-card.md

# 3. run the machine check (no network)
python3 ~/.workbuddy/skills/related-party-terms-cn/scripts/check_rpt_card.py ./my-related-party-card.md
```

Install this skill alone: npx skills add huhoo/cue-awesome --skill related-party-terms-cn (this installs only this package; restart your session on your side for it to take effect).

## 4. First-time Cue setup (three steps, skippable)

This skill has two evidence legs: **source text** (finding the announcements, agreements and proposals on the data leg) and **attachment parsing** (the full agreement, the dedicated independent-director meeting resolution, adviser reviews and supervision opinions usually sit in attachments, on the parsing leg). Both are optional - you can still get a card from a file you paste yourself; the price is that pricing and commitment detail inside attachments stops at `未检索到`, and the announcement-versus-agreement reconciliation cannot be filled in automatically, so it needs a human back at the original text.

1. Register at <https://cuecue.cn>;
2. Get `CUE_API_KEY` at <https://cuecue.cn/hub/api-key> and store it as local credential - **never paste it into chat**; the agent does not handle keys;
3. Install the two skills: `cue-data-mcp` for the source-text leg, `cue-omni-reader` for the parsing leg. One command, two forms:
   - whole set: `npx skills add sensedeal/cue-skills` (it lists the public skills of that collection and prompts which to install);
   - single: `npx skills add sensedeal/cue-skills --skill cue-data-mcp` (swap the trailing name for `cue-omni-reader` to install that one only).

Configuration pointers are pointers only, never re-explained steps: source text on the data leg at <https://cuecue.cn/hub/mcp>; long attachments and PDFs on the parsing leg at <https://cuecue.cn/hub/omni-reader>; the key at <https://cuecue.cn/hub/api-key>.

### Connectivity self-check

```bash
# 1) catalog reachable anonymously: proves the catalog reads, not "connected"
curl -s "https://cuecue.cn/api/mcp-catalog" | head -c 200

# 2) take routing.url and transport for the domain from the response; never hard-code the host
# 3) with the key, send tools/list - proves that endpoint accepted the key, nothing else
curl -s -X POST "$ROUTING_URL" -H "Authorization: Bearer $CUE_API_KEY" \
  -H "Content-Type: application/json" -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | head -c 400
```

Installing a skill is not configuring a credential and is not a connected data leg: that judgement covers only the data-leg path - connecting with the key to the domain's current `routing` and getting a `tools/list` response there proves that key was accepted for that endpoint, nothing more; the parsing leg has its own judgement on its own face.

## 5. Boundaries

- Pricing fairness, tunneling suspicion, harm to minority holders, whether the vote passes, earnings and share-price impact - all `[待人工]`; no "join in", "vote against", "abstain", "sure profit", "zero risk", "guaranteed return", "positive for the price", "will certainly pass";
- No legal-effect calls: whether the transaction is valid, whether the procedure violates rules, whether the recusal was sufficient, whether the waiver stands - human and regulatory territory; writing such a self-verdict fires the gate;
- No rule-application answers: whether the independent directors should have used a dedicated meeting or a prior approval, whether shareholder approval is required - the skill registers whichever form the filing states and never answers which rule applies;
- Figures verbatim and cell-scoped: "subject to", "to be signed separately", "to be disclosed later", prior-period price, market average, book value, audited figure and cumulative incurred are not the cell's own figure - if it was not retrieved, write `未检索到`; each cell needs a landing for **both** elements, a figure for the numeric one and an arrangement wording for the pricing basis, so one figure does not settle the pair;
- The attribution rule has a stated reach: adjacency inside one phrase plus one cross-phrase inheritance and one co-reference check; it does not claim to cover every natural-language assignment of a figure. The appositional co-reference shape and the "amount undecided, method decided" co-present sentence are declared coverage limits that fire under the strict reading - read those against the announcement; when the document genuinely does not state a figure, `未检索到` is a lawful answer;
- `未检索到` means writing exactly that - no filling from what comparable deals do, and no "this item does not exist" substitute;
- Domains and tool names follow live catalog values: no fixed list, no promised counts, no promise that the domain is open or that the filing is current.

## 6. Troubleshooting

| Symptom | Why | Recovery |
|---|---|---|
| Several items read `未检索到` | The file is a resolution summary, or the pricing and quota detail lives in the agreement attachment | Start the attachment-parsing leg to recover quotes; if it cannot run, keep the named gaps instead of filling them |
| The data leg will not connect | Missing credential or the domain is not live | Use the self-check in section 4; the first two sections still produce, at the cost written there |
| The gate fires | Missing anchor or quote, an element without its own landing in the two numeric cells, a count mismatch, a judgement sentence | Fix by the named line numbers; anything unrecoverable goes to the missing-data list, never by deleting lines |
| A judgement line fires in error | The line says "shareholders' meeting", "board", "audit committee" or quotes the announcement | Keep quotes inside the title marks and keep the anchor; the gate washes institutional-name tokens before judging tone, so ordinary registration sentences stay green |
| A self-verdict inside title marks still fires | The line is this card's own conclusion ("this card concludes: the pricing is fair") with no source text behind it | Reword it as a `[待人工]` reservation, or quote the announcement and keep its anchor - the exemption belongs to anchored source text only |
| The cell's own figure was called a reference figure | The sentence puts market average or book value next to the figure and the cell's noun further left | Keep the announcement's own sentence for that cell, or if the document really omits it, write `未检索到` |
| A same-value sentence fires | It was written appositionally ("the deal amount and the annual quota are both 86 million yuan"), which the gate declares out of coverage | Read that sentence against the announcement; rewriting it as "the deal amount is the annual quota of 86 million yuan" is recognised |
| Announcement and agreement disagree | Terms are routinely adjusted between them | Put both quotes side by side in the comparison section with their own anchors; do not choose between them |

## 7. How to ask (good and bad prompts)

- Good: "what is the pricing basis and the price for this related-party deal", "how much is planned with this related party this year and how much quota is left", "how many related directors recused and is shareholder approval needed", "did the independent directors hold a dedicated meeting or give a prior approval", "what are the payment terms, is there non-operating fund occupation", "can this stay inside the approved quota without a separate vote".
- Bad: "is this price fair", "is value being tunneled", "does it harm minority holders", "will the proposal pass", "where does the stock go" - fairness, tunneling, harm, outcome prediction and market reaction are outside this skill and stay `[待人工]`.

## 8. Capability limits (honest list)

Market and fund-flow figures are outside this skill (domains follow live catalog values; unopened means unpromised); no fairness computations or comparability analysis - comparable prices, valuations and earnings forecasts belong to valuers, advisers and the filing itself; no judgement on deal motive, tunneling suspicion or insider-information likelihood; no rule-application answers about which approval route was required; and nothing of yours is stored persistently - the card is handed back when it is done.

## 9. Resources

- `SKILL.md`: the five-section card and red lines (Chinese face is authoritative)
- `SKILL.en.md`: the matching English face; conflicts resolve to the Chinese face
- `references/rpt-terms.md`: the eight items' fields, the four kinds of stand-in wording in the two numeric cells, what the governance cell reads, and the split against sibling skills
- `scripts/check_rpt_card.py`: five machine checks (no network)
