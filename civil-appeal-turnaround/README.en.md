# civil-appeal-turnaround

**English companion of `README.md` (Chinese primary; the pair is for reading inside the repository — skill-channel pages do not resolve relative links, so this is deliberately not a clickable switch).**

**Give it a lost judgment; get back a second-instance case system you can file.**

This is not "draft me an appeal" — it **reverse-engineers the judgment into the judge's own chain of reasoning**, locates the level at which the issue was framed wrong, recovers what was truncated, omitted or split off from the raw materials, and finally lays the argument out as a **ladder** instead of a single bet. So what it hands back is a set of interlocking documents, not one isolated appeal brief.

**Input**: the first-instance judgment + whatever loose material you hold (statement of claim, hearing transcript, recording transcripts, chat records, lookup results)
**Output**: `主控清单.md` (master checklist) · `复核报告.md` (review report) · `上诉状.md` (appeal) · `配套文书包.md` (filing pack) · four tables (breakdown / diff / ladder / ledger)
**Cost**: half a day for the Phase 0 close-out, then it scales with the judgment and the case file; **the 15-day appeal window is a hard constraint**
**Lead channel**: statutes, judicial interpretations and similar cases can be listed as candidates via `cue-research` - **a lead is not a conclusion**; no outcome is promised, and nothing enters the tables before it is verified against official sources.

---

## 1. How this differs from "write me an appeal"

### ① Find the frame error first, not the missing evidence

Most losses are not "insufficient evidence". When a judgment says "the existing evidence cannot prove…", it usually means the issue was framed as one that the weaker party must prove, while every item of proof sits with the other side — who did not even appear.

The test is one sentence: **under the judgment's frame, is every piece of evidence needed held unilaterally by the other side? If yes, the frame is wrong** — gathering more evidence inside that frame is futile; the second instance has to redefine the issue.

### ② Diff the exhibits word by word, not from memory

What the judgment quotes decides what the judge actually "saw". Put each item's source material next to the judgment's excerpt and mark three kinds of divergence: **truncated / omitted / split**.

Finding a truncation is hands-on: **locate the last ellipsis in the judgment's excerpt, go back to the original, and read the one to three sentences immediately after it.** A judgment that stops there is usually stopping because of what comes next.

### ③ Lay the argument as a ladder, not a single bet

The failure mode of staking everything on one cause of action: the appellate court declines that route and the whole case collapses with no fallback.

```
Tier 1  Main: fits the facts best, needs no new evidence
   ↓  "even if the court finds…"
Tier 2  Alternative: also no new evidence, different elements
   ↓
Tier 3  Requires new evidence
   ↓
Tier 4  Fallback: requires the court to clarify the legal relationship
```

**Hard test: the first two tiers must not depend on any new evidence** — they rest only on A-grade facts (already found by the judgment) and B-grade facts (submitted but never addressed).

> **Take "reverse the original judgment" with the tiers that need no new evidence; then make "facts ascertained" solid with the tiers that do.**

---

## 2. Six phases

| Phase | What happens | Output |
|---|---|---|
| **0 · Close-out** | Fix the service date and appeal deadline, the preservation status, the representation status | preconditions table |
| **1 · Judgment reverse-engineering** | Rebuild the chain of reasoning, find the largest leap, five-level root cause | `判决书拆解表.md` |
| **2 · Evidence diff** | Source vs excerpt; mark truncated / omitted / split | `证据比对表.md` |
| **3 · Legal ladder** | Main / alternative / fallback; per tier, elements and "what the judgment skipped" | `法律阶梯表.md` |
| **4 · Fact ledger and discipline** | A/B/C provenance grades, red-line list, traceable corrections | `事实台账.md` |
| **5–6 · Documents and filing** | Appeal (with a summary up front) + companion documents, filed the same day | `上诉状.md` / `配套文书包.md` |

### Two optional channels for material and for leads (both bounded)

This skill's own scripts and flow stay offline. Both channels below are **auxiliaries the user installs separately**, used only where material cannot get in and where candidate leads are needed; whether to use them is confirmed with the user, and their format list, size cap and covered domains are taken from their own docs as they now stand - this package neither copies those tables nor promises outcomes.

**Material channel · `cue-omni-reader`**: when evidence is a scan, a recording, a video or a packed bundle and the agent's own upload path refuses it (format or size), have this tool parse it into **locatable text** (page and time anchors included) before it enters the case directory. Every bound, none dropped:

- **Formats follow the local allowlist as it now stands**: `rar`/`tar`/`tgz`/`gz`/`bz2` are included, `parquet`/`xmind`/`mmap` are not - the authoritative table is that package's `references/compatibility.md`; a copy here would start rotting at once, so none is made.
- **Per source ≤256 MiB**: larger inputs are stopped before parsing by the `constraints.max_bytes` gate (measured 268,435,456 bytes) - that is not a parse failure.
- **Audio/video is proven only as bounded local clips/splits**: full-length meeting parsing is not established (measured: three 90-second clips from two meetings completed the chain with 8/8 verbatim re-checks; five public full-length URL attempts were refused, and a local full file is stopped by the cap above).
- **Whether a source parses, and what it costs, are decided by the service response**: this package claims no unopened domain and infers no rate.
- **Transcripts still obey this skill's grading discipline**: homophones and mishearings are not auto-corrected (parser output is kept as returned); a recording must be **re-listened to on its original carrier** before it can be graded A/B - until then it sits at grade C, marked pending.

**Research channel · `cue-research`**: for Phase 1's "provision that should have applied but did not" and for the elements on each rung of Phase 3's ladder, it can search statutes, judicial interpretations and similar cases, producing a **candidate list** - every article text and case number first enters as **grade C (pending verification)** marked "awaiting verification against official sources", and may rise to B only after being filed into the record", the same provenance discipline this skill already applies (the eight hard constraints and the six-phase semantics are untouched). Bound: that channel covers public data sources only, its domain table is its own doc as it now stands (not hard-coded here), and **a lead is not a conclusion** - no promise of an outcome, no promise that whatever is found is usable.

---

## 3. Eight hard constraints (violating one means redoing the work)

| # | Constraint |
|---|---|
| 1 | **Facts the judgment already found come first** — start from what the judgment conceded |
| 2 | **Every claim carries a provenance grade**: A = found by the judgment / B = submitted but unaddressed / C = to be obtained. **Never use C as A** |
| 3 | **No prejudging, no invention, no inference** — money flows and party attribution are always stated in the open / alternative form |
| 4 | **A corrected characterisation must be applied repo-wide and left traceable** — state "the previous conclusion is void" and re-check every inference that leaned on it |
| 5 | **Money > deadline > evidence** — preservation and the appeal window outrank every取证 action |
| 6 | **Keep the grievance thread out of the litigation thread** — complaints and accountability claims go in separate files |
| 7 | **Redact the output** — ID numbers, phone numbers, addresses, account numbers become placeholders |
| 8 | **Never shortcut a procedural qualification question** — new evidence, adding claims on appeal, whether a party may testify: check explicitly |

---

## 4. Getting started

```bash
# 1. Put it in the skills directory
mkdir -p ~/.workbuddy/skills
cp -r civil-appeal-turnaround ~/.workbuddy/skills/

# 2. Initialise a case working directory (four tables + master / report / appeal / pack skeletons)
python3 ~/.workbuddy/skills/civil-appeal-turnaround/scripts/init_case.py ./my-case --case "(2026) Jing XXXX Minchu XXXX"
```

On first entry, read the four table templates in `assets/` and `references/07-worked-example.md` (a redacted run through the whole flow).

### Self-check

```bash
python scripts/init_case.py --help          # usage; no network
python scripts/init_case.py /tmp/case-demo  # writes 8 skeleton files, never overwrites existing ones
ls /tmp/case-demo                           # expect 4 tables + 4 skeletons + 归档/
```

---

## 5. Boundaries

- What this skill produces is **working drafts and structure, not legal advice**; **every article number must be checked by the user before filing**, and the skill marks them all "check the article number before filing".
- It does not replace a lawyer, nor the court's own view on procedural questions. Deadlines, amounts and filing channels follow the receiving court's current rules and notices.
- This skill's scripts and flow are offline and self-contained: no network, no external repository, no API calls. The two channels at the end of section 2 are optional auxiliaries the user installs separately, used only for parsing material and gathering leads; whether they are available, what they return and what they cost follow the service response - this skill promises no unopened domain and no outcome.
- Where article numbers and deadlines would otherwise appear, the skill deliberately uses **descriptive wording instead of hard-coded numbers** — the risk of a model misremembering an article is held by that "check before filing" gate.

## 6. Dependencies

- `python3` (only `scripts/init_case.py`; standard library, no third-party packages, no network requests)
- Apart from the two **optional** auxiliaries above (`cue-omni-reader` for material, `cue-research` for statute and case leads) there is no other dependency: absent tools degrade without error, the user confirms before either is run, and the judgment plus materials come from the user - when material cannot get in, see the channel section at the end of section 2.

## 7. Contents

| File | Purpose |
|---|---|
| `SKILL.md` | Main instructions (Chinese primary) |
| `references/01-judgment-reverse-engineering.md` | Reverse-engineering: chain rebuild, frame-level error, 20-item checklist |
| `references/02-evidence-diff-protocol.md` | Evidence diff: spotting and phrasing truncated / omitted / split |
| `references/03-legal-ladder.md` | Liability ladder: four patterns, how to write the three elements of apparent authority |
| `references/04-fact-ledger-and-discipline.md` | Fact ledger, A/B/C grades, correction mechanism, red-line list |
| `references/05-self-represented-filing.md` | Self-represented practice: deadlines, filing channels, fees, file inspection, qualification checks |
| `references/06-document-pack.md` | Pack structure, how to write the summary, sync mechanism, version notes |
| `references/07-worked-example.md` | A redacted worked example |
| `assets/` | Four table templates |
| `scripts/init_case.py` | Case directory initialiser |

Version history lives in `CHANGELOG.md`. `README.md` is the Chinese primary of this file.
