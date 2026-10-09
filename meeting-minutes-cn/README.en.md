# meeting-minutes-cn

**English companion of `README.md` (Chinese primary; the pair is for reading inside the repository — skill-channel pages do not resolve relative links, so this is deliberately not a clickable switch).**

**A meeting recording goes in, and a minutes card where every sentence can be traced back to the tape comes out: verbatim lines carry [mm:ss] anchors, topic grouping is self-labelled as `此归类非原文所有` (this grouping is not in the original), decisions and action items each carry a verbatim anchor, and everything unclear sits under `[待人工]`.**

No real-time mode, no rewriting, no filling in what was not said - and no names supplied from memory. The demand account is `verify/enterprise-zone-study-2026-10-09.md` in this repository (the vacancy ledger across the enterprise hot list).

**Input**: a recording path (inside a Bridge-authorized directory) or a parseable link; optionally an agenda or whiteboard photo (same parsing route)
**Output**: one filled-in `assets/会议纪要卡.md` card - basic info, anchored verbatim, topic segments, decisions and actions, pending list
**Cost**: the first two parts depend only on what the channel returns; grouping and extraction happen on demand
**Machine gate**: `scripts/check_minutes_card.py`, four lanes (format and boundary declaration / anchors / red lines / counts and declarations), zero network

---

## 1. Open it and work: three steps today

These three are the only "do it now" part. The opening line can be copied verbatim: **"turn this recording into minutes, give me the verbatim lines and the actions first"**.

| Step | Action | How | What happens if you skip it |
|---|---|---|---|
| 1 | **Declare the material shape first** | In the header, record the source, then tick one of single file / clip / whole-file-stopped, and tick the timeline basis (anchors within one clip vs. stitched clips, cross-clip continuity unproven) | Feeding a whole long recording hits the channel gate and you wait for nothing; without the stitching declaration, cross-clip anchors get read as comparable evidence |
| 2 | **Verbatim first, with anchors** | Pair every passage with a [mm:ss]; copy homophones and mishearings **as returned** and hang them in part five | Minutes without anchors are paraphrase with no way back, and "cleaning up" a mishearing is fabricating speech |
| 3 | **Anchor each decision, then run the gate** | Each row = conclusion + owner (only when self-identified on tape) + [mm:ss]; then `python3 scripts/check_minutes_card.py my-card.md` and fix by `E-*` code | "Who owns this" turns into guessing, and the guess travels to readers who cannot verify it |

Topic grouping and decision extraction come **after** these three: the first is note-taking, the second needs the tape behind it.

## 2. The five parts and the four lanes

| Part | Content | What the gate enforces |
|---|---|---|
| 1 Basic info | Meeting, date, duration, speaker count, materials - date from what the tape states or the user gives, otherwise `缺` | Content without basis -> `E-ANCHOR` |
| 2 Anchored verbatim | Source text plus [mm:ss], no summarising in this table | Missing time anchor -> `E-ANCHOR` |
| 3 Topic segments | Each segment carries a start-end anchor pair and ticks "this grouping is not in the original" | Single anchor -> `E-ANCHOR`; unticked self-label -> `E-COVERAGE` |
| 4 Decisions and actions | Conclusion + owner (only if self-identified, else `未自报·待核`) + verbatim anchor | No anchor -> `E-ANCHOR`; bare name -> `E-ANCHOR`; "everyone agreed" without anchor -> `E-BANWORD` |
| 5 Pending list | Homophones, unclear references, cross-clip anchors - all under `[待人工]` | Missing the `[待人工]` roll-up -> `E-COVERAGE` |

The header has its own hard set: **the two self-labels** (`AI 整理纪要`, `决策请对回原话确认`) **plus** a filled source, a ticked material shape and a ticked timeline basis. Any missing is an `E-FORMAT`; ticking "whole file, stopped" while verbatim rows still exist is a contradiction and yields an `E-COVERAGE`.

## 3. Getting started

```bash
# 1. Put it in the skills directory
mkdir -p ~/.workbuddy/skills
cp -r meeting-minutes-cn ~/.workbuddy/skills/

# 2. Copy the card template and fill it following section 1
cp ~/.workbuddy/skills/meeting-minutes-cn/assets/会议纪要卡.md ./my-card.md

# 3. Run the gate (no network)
python3 ~/.workbuddy/skills/meeting-minutes-cn/scripts/check_minutes_card.py ./my-card.md
```

Read `assets/会议纪要卡.md` first (that is the five-part shape), then `SKILL.md` §1/§3 for the boundary and the contract.

### Self-check

```bash
python3 scripts/check_minutes_card.py --help                              # usage; no network
python3 scripts/check_minutes_card.py --selftest                          # good sample must pass, bad sample must fire all four lanes
python3 scripts/check_minutes_card.py scripts/fixtures/good-minutes-card.md   # PASS (scans 51 lines, 0 findings)
python3 scripts/check_minutes_card.py scripts/fixtures/bad-minutes-card.md    # FAIL (20 findings, all four codes)
python3 scripts/check_minutes_card.py assets/会议纪要卡.md                     # FAIL (5 findings - a blank card failing the gate is the design, not a defect)
```

## 4. Boundaries and non-promises

- **One measured boundary: the local bounded clip / split workflow, ≤256 MiB per source.** av-backtest carries the account (three 90-second clips from two meetings completed the parse-to-export chain with 8/8 verbatim re-checks); five public full-length URL attempts were refused and a local full file is stopped by the `constraints.max_bytes` gate (measured 268,435,456 bytes). **Whole-recording ingestion is not established.** When something exceeds the bound, stop and say why - do not force it, do not pretend it was read.
- **Do not assume continuity across clips.** av-backtest's limits state that per-split stitching and timestamp continuity are not established. A card assembled from several clips must tick "cross-clip anchors are pending verification"; the gate accepts that declaration and deliberately does not check cross-clip timelines - a lane over an unproven surface would sell a capability nothing measured.
- ASR homophones enter the minutes **as returned**, marked pending; this package never presents itself as a cleaned transcript. Whatever anchor shapes the channel returns (`[画面 mm:ss]`, `[说话人 mm:ss]`, `(幻灯片标题)`) is what the card records; this file does not freeze that list.
- **No real-time mode** (live transcription is not this package's surface) and **no rewriting** (polishing, "a prettier version" are out).
- **Names are never supplied from memory**: participants appear only when they self-identify on tape; speaker labels follow the channel's own tags.
- **Availability and billing follow the service response**; neither the card nor this file writes a price figure - the gate raises `E-BANWORD` on any price literal.
- **One explicit confirmation before distributing**: before sending decisions or action items to a team, restate target + consequence + timing and wait for a clear reply; bare replies like "ok", "mm" or "sure" are not confirmation. While the step has not happened, completed-form wording ("I've sent it out for you") stays out of the text.
- The two header self-labels are not decoration - they restate why part five exists: decisions must be checked back against the tape.

## 5. When something goes wrong (symptom -> cause -> recovery)

**Whatever is absent from this run's tool output is written as "not found"**: a parameter, field or enum value that does not appear there must not be filled from memory - write `未检索到` (not found) and log it on the pending or coverage list; a blank never stands in for it.

**Error-level findings are blockers**: never describe them as harmless, ignorable, or shippable-as-is - fix them, or declare them explicitly on the deliverable.

The output shape is taken from a live run of `check_minutes_card.py` as it now stands: a failure prints one line `FAIL: <file> (N items)`, then each detail line **starts with an error code (one of four `E-*`)** such as `[E-FORMAT]`, `[E-ANCHOR]`, `[E-BANWORD]`, followed by the lane name, the line number and that lane's spec; the last line `码表:` lists only the codes actually used. A pass prints `PASS: <file> (...)` plus two counts - lines scanned, findings raised.

This package uses **four** codes, byte-identical to the sibling packages' table. The fifth, `E-LEDGER`, belongs to ledger state machines; this skill has no ledger, so it is deliberately not enabled - that is not an omission. The full set and the classification rules live in the script; run this line from any directory to locate them:

    grep -n "^E_LEGEND" ~/.workbuddy/skills/meeting-minutes-cn/scripts/check_minutes_card.py

| Symptom (detail prefix) | Cause | Recovery |
|---|---|---|
| `[E-FORMAT]` header or source lanes | One self-label missing, or the recording source is still a placeholder | Complete the header; give a path inside an authorized directory or a parseable link - with no source, anchors have nowhere to return to |
| `[E-FORMAT]` declaration, timeline or section lanes | Material shape or timeline basis unticked, parts out of order | Tick one of the three; if a whole file was stopped, tick the stop option and state the reason; multi-clip cards tick the pending rule |
| `[E-ANCHOR]` basic, verbatim, segment, decision or owner lanes | Content without a time anchor; a segment with a single point; a bare name as owner | Add [mm:ss]; use start-end pairs; write "speaker N self-identifies [mm:ss]" or "not self-identified, pending" - **delete the row rather than invent an anchor** |
| `[E-BANWORD]` overstep, cleaning, polish, inference or price lanes | Real-time claims; "already cleaned/corrected"; polishing; "everyone agreed" without a quote; any money figure | Drop real-time wording; keep homophones verbatim and mark them pending; stay faithful to the tape; anchor the agreement or delete it; leave billing to the service response |
| `[E-COVERAGE]` contradiction, empty verbatim, grouping label or roll-up lanes | Stopped yet verbatim rows exist; no output and no stop declaration; grouping not self-labelled; pending list without the roll-up | Choose stop or output; declare the stop when nothing came; tick the grouping label on every segment; restore the `[待人工]` roll-up |

## 6. How to ask (three positive examples, one counter-example)

**Ask with the date; the output states the meeting date and recording point**: say which day the meeting was and which segment the audio covers; the deliverable labels its **meeting date and recording point** on the first line, and when it differs from the date you meant, the text never says "today" or "latest" - it reads "as of <date>".

| Positive example | What you get |
|---|---|
| "Turn this recording into minutes - verbatim and actions first, one [mm:ss] per line" | Parts one and two: anchored verbatim plus basic info, actions right after |
| "What was decided and who took it - only what the tape actually says" | The decisions table with a verbatim anchor per row; anything unannounced marked "not self-identified, pending" |
| "This word is unclear in the recording - flag it, don't fix it" | The pending list under `[待人工]`, homophone kept as returned |
| **Counter-example: "make the minutes prettier, complete the half-finished sentences, and tell me what the transcription costs"** | Not done here. Polishing and inference are blocked by the gate, no price figure enters any face, and real-time is not this surface |

## 7. Current state (honest list)

- The documentation face and the machine face are in place (five-part contract, four lanes, two fixtures, self-test green).
- **Status inherited from the P0 skeleton README (lead's wording): not listed, package-level P1 not run.** This package makes no capability claim and gives no accuracy or timing figure.
- **The package-level P1 account (a verbatim re-check over N real meeting recordings) belongs to 2.1's M190** and was not run under this ticket; figures return only with that ticket as their source.
- The one account this package can cite is **av-backtest**: audio works as a bounded local clip/split workflow (≤256 MiB), three 90-second clips from two meetings completed the chain with 8/8 verbatim re-checks, five public full-length URL attempts were refused, a local full file is stopped at 268,435,456 bytes, and cross-clip continuity is not established. That is the **parsing channel's** ledger, not a minutes-quality ledger - the latter waits for M190.
- Channel shapes and billing follow the actual response; this package neither restates a domain list, counts tools, nor prices anything.

## 8. Dependencies

- `python3` (only `scripts/check_minutes_card.py`; standard library, zero network, sends no request)
- The audio parsing channel is an **optional auxiliary**: the card can be filled by hand and still pass the gate; with the channel, [mm:ss] anchors and speaker tags come from its response, whose shape this package does not guess.

## 9. Contents

| File | Purpose |
|---|---|
| `SKILL.md` | Main instructions and the five-part contract (design authority, Chinese primary) |
| `assets/会议纪要卡.md` | The minutes card template you fill |
| `scripts/check_minutes_card.py` | Four-lane gate (format and boundary declaration / anchors / red lines / counts and declarations) |
| `scripts/fixtures/good-minutes-card.md` | Green sample (fictional content, not a real meeting citation) |
| `scripts/fixtures/bad-minutes-card.md` | Red sample (one counter-example per lane) |
| `README.md` | Chinese primary of this file |

Version history lives in `CHANGELOG.md`.
