# journal-draft

**[中文](README.md) · [English](README.en.md)**

**Give it one back issue; get back a next-issue draft that can go straight into design.**

This is not "write me an article" — it **measures** a publication's layout and editorial conventions out of a PDF and turns them into verifiable parameters, then produces the next issue against those parameters. So what it hands back can go into design directly, instead of a pile of text waiting to be laid out.

**Input**: one back issue as a sample (PDF preferred) + this issue's requirements
**Output**: `draft.html` (mm-precision positioned layout draft) · `draft.pdf` (print-grade, self-drawn) · `draft.docx` / `draft.md` (editable text drafts)
**Cost**: standard mode ≈ **3 batches of questions** (kick-off / outline / delivery — ≤5 questions per batch, each with a default)

---

## 1. How this differs from "just give me an outline"

### ① Layout is **measured**, not described

It extracts the page grid, type area, type scale, leading, color palette, and header/logo coordinates from the sample PDF into `stylespec.json`. The renderer lays out the issue at mm-level absolute positioning — so the PDF is **drawn by PyMuPDF itself**, not printed through a browser (corporate policy can make an entire issue invisible; see `references/pitfalls.md`).

### ② Five gates, built for the "script didn't error, page looks fine" kind of silent failure

| Silent failure | What it looks like | What catches it |
|---|---|---|
| Content clipped | Fewer pages than expected; nothing looks wrong on the page | `overflow` warning from `--stats` (`overflow:hidden` eats the overflow) |
| Not enough content | Layout is perfect, but the issue is only a third as thick as the sample | `scale_baseline` attainment gate — **anything below 60% is a hard FAIL** |
| The three deliverables disagree | HTML updated, docx/md did not | `crosscheck.py` compares text coverage across HTML / MD / PDF item by item |
| The sample is a scan | No type sizes or body text extracted; looks like an empty issue | When the text layer is extremely thin it says "this is probably a scan — OCR it first" instead of returning an empty result |

There is also `check_freshness.py`, a timeliness gate: it locates event dates, issue-number continuity and vague time expressions one by one.

The fourth gate is the **layout quality gate** (`audit_layout.py`, since v0.14.0). The first three cover "is the content right and sufficient"; only this one covers **does it look right and read well** — body type size versus the sample, whether the type hierarchy is fragmented, line-height multiplier, characters per line, whether the font actually applies, leftover Chinese spaces, page density. Measured on an 80-page draft that passed all three gates green: type still one step too small, sizes fragmented into 41 distinct steps, leading 2.16× (sample: 1.85), 73 stray spaces in footers — **not one of those gates reported it**.

The fifth gate is the **editorial positioning gate** (`audit_editorial.py`, since v0.15.0). The first four cover "right content, enough content, good looks"; only this one covers **is it on target** — who this issue is written for, what the reader should do after reading, and what tone it should speak in. Positioning is captured in `positioning.json` (the second machine-readable artifact, a peer of `stylespec.json`); then it judges whether each item's word count falls in the band derived from the tone, coverage of items that deliver "what the reader should do", share of pure-L0 items, sentence length, terminology and taboo words. Measured on a draft that passed all four gates green: all 48 items in a single shape, averaging 409 characters (template declares 180–320, i.e. 28% over), only 4 reader-addressing phrases in the whole issue, only 21% carrying an action suggestion — **again, not one gate reported it**.

### ③ It admits its limits — and **marks them**

The single-column renderer cannot draw two columns; component geometry on non-A4 trim needs manual tuning; chart-heavy pages have no built-in template; bilingual layout has no built-in rendering — none of this is hidden. When you hit one, the `+learn` wrap-up says so out loud, and `examples/` ships a dedicated **negative sample** to calibrate exactly where it breaks.

### ④ Compliance is not an appendix — it is a separate gate

Values are taken across three layers — **reader identity × industry × periodical form** (external clients / employees / investors / public / channel / regulator; law firm / finance / pharma / food / education / tech / manufacturing / real estate / retail) — and for issues that need sign-off it produces a signature list (marketing / legal / HR / company-secretary-IR / PR / compliance).

### ⑤ There is also work it explicitly **will not take**

Boundaries are written down so neither side wastes time. The following are **not "not supported yet" — they are out of scope by design**:

| Won't take | Why | What to do instead |
|---|---|---|
| **Ghostwriting articles / creative copy** | It delivers "a draft with the right layout and right conventions", not "content with fresh points of view". Views, cases and data must come from you | Hand it your existing material to organize into the layout |
| **Replacing legal / compliance review** | It gives checklists and sign-off suggestions, but that is not legal advice | Before publishing, walk [`references/qa-checklist.md`](references/qa-checklist.md) through human review and sign-off |
| **Delivering print-ready finals** | It delivers a **draft**; bleed, color management and printer soft proofs are out of scope | Take the draft into design software for pre-press |
| **Using a scan as the sample** | Style extraction depends on the PDF's **text layer**; scanned images have none | OCR into a text layer first, then run `+learn` |
| **Two-column / multi-column rendering** | The renderer outputs single column only; column flow and text wrap are a different layout logic | For a two-column publication, use it as a source of **conventions and content templates**, and lay out separately |
| **Bilingual / parallel-text rendering** | No built-in bilingual layout | Produce two single-language drafts and merge them manually |
| **Complex data visualization** | The 6 semantic-diagram templates cover relations like parallel / flow / stack / converge / footer — it is not a chart library | Produce charts externally and bring them in through the `+art` image slot |

If you are unsure, just ask — it will state plainly what it can do this time, what it cannot, and who has to fill the gap.

---

## 2. Quick start

```bash
python -m pip install pymupdf        # required: style extraction + PDF output
python -m pip install python-docx    # optional: docx text draft and write-back
python -m pip install pillow         # optional: pre-press image checks
```

Use `python` on Windows; `python3` on macOS / Linux.

**Images need no image API key at all.** Semantic diagrams go through `gen_diagram.py`, drawn as vector graphics in code (zero cost, no watermark, every Chinese character verifiable); only atmospheric images that carry no specific information, such as cover decorations, use the agent's own multimodal image generation.

**Smoke test** (confirm the environment works):

```bash
python scripts/build_draft.py \
  --spec assets/examples/qiming-regional-sample/stylespec.json \
  --content assets/templates/content.example.json \
  --out ./smoke --stats
```

If it prints page count, item count and `unknown=0`, you are through. The sample is only 8 pages, so it will report `[FAIL] 量级严重不足` (it is being compared against a 91-page baseline) — **that FAIL is expected**; what matters is that the gate ran, not its verdict. **The exit code is 1 here too** — that is the gate's verdict, not a script crash; when wiring CI, distinguish those two by status code.

### The Cue channel (deep research / document parsing)

**Not required, but strongly recommended** — without it nothing errors, you just lose one layer of cross-verification and the semantic layer falls back to manual entry. Three steps to enable: register at <https://cuecue.cn> → get `CUE_API_KEY` at <https://cuecue.cn/hub/api-key> → install `cue-research` (Omni parsing additionally needs the local Bridge).

New accounts get **500 credits** on signup plus 10 per day, **and Cue always asks before spending**. At kick-off it asks item by item whether you want to use it; the decision rules are in [`references/cue-onboarding.md`](references/cue-onboarding.md).

---

## 3. Eight verbs — resume from any stage

```
+learn extract style   +brief align requirements   +plan outline    +gather collect evidence
+draft produce draft   +art images                 +check proofread +spec distill sub-skill
```

Saying "make the next issue following this one" automatically walks from `+learn` to `+brief`. A `progress.md` ledger is created at kick-off, one line per completed stage; whoever picks it up after an interruption reads it first, so **questions already answered are not asked again** (spec in [`references/agent-interaction.md`](references/agent-interaction.md)).

---

## 4. Position your publication first (three questions that set every default below)

This framework's **defaults were tuned against a law-firm client newsletter** (A4 single column, sequential issue numbering, external-client readership). If your publication differs and you skip these three questions, you will get a draft that is **"all gates green, all conventions wrong"**.

| Question | What your answer decides | Where copying the default goes wrong |
|---|---|---|
| **Who reads it?** clients / employees / investors / public / channel / regulator | Compliance floor + **the departments that must sign off** | Default is "external clients" → an employee magazine misses HR+legal sign-off and personnel confidentiality items; an IR letter misses selective-disclosure rules |
| **What cadence?** continuous periodical / special issue / annual review / compilation / high-frequency bulletin | How issue numbers are assigned + the timeliness window | Default is "previous issue N-1 + 6-month window" → **yearbooks are numbered by year**, with the window widened to 12 months or exempted item by item; weekly bulletins shrink it to 1 month |
| **What form?** items + long articles / pure articles / chart-heavy / compilation / briefing | How many UnitPatterns to extract + whether the eight templates suffice | Default is "items + long articles" → a pure-article publication needs only one U1; chart-heavy types (annual report / ESG) **have no built-in chart page template** |

> Per-item differences, reader × compliance matrix, industry prohibitions, common unit library (12 kinds):
> **[`references/journal-types.md`](references/journal-types.md) (read before changing publication type)**

---

## 5. Pick your path by situation (choosing wrong wastes a whole `+learn` round)

| Your situation | Where the sample comes from | Watch out for |
|---|---|---|
| **① Veteran editor of this title** (own publication, back issues exist) | Use **the previous issue** directly | Most common: **reused items are not fact-checked** (people left, phone numbers changed, data expired). The 8 items of the `+brief` "reusable list" must be checked one by one |
| **② Same publication type, different organization** | Use **that organization's own back issue**; if none, go to ④ | **Do not use another company's publication as a production sample** — what you extract is their brand DNA |
| **③ Different publication type, same organization** | Prefer **your own** back issue of that type; otherwise a peer organization's same type | One `stylespec.json` is not enough: **changing publication type means re-running `+learn` and re-deriving**; hand-editing fields always misses something |
| **④ Any publication type at a non-law-firm company** | Your own back issue; if it is a first issue with none, follow the **three ways out** in hard rule 1 of `SKILL.md` | ① Run compliance by the "reader row × industry row" combination, don't copy the finance/legal tone; ② structured data lives in **your ERP/CRM/HR internal systems** — confidential, needs authorization, and must be desensitized |

**Three general onboarding paths**:

| You want | How |
|---|---|
| **To see what a finished result looks like** | Copy `examples/journal-qiming-regional/` into `~/.workbuddy/skills/` and have it produce the next issue. It ships all rendering scripts (12 of them) and does not depend on this directory |
| **To do your own publication** | Take **one issue of your own** as the sample and run `+learn → +brief → +plan → +gather → +draft → +check`, then `+spec` to distill your own skill — **from the second issue on, the cost drops sharply** |
| **To borrow the method only** | Read §3 (seven-stage flow) of `SKILL.md` plus the sample's `unit-patterns.md` to see what a real publication's layout and content templates were distilled into |

**Do not hand-edit `stylespec.json`.** Changing publication type or client means re-running `+learn` and re-deriving; hand-editing dozens of fields always misses something.

---

## 6. Two samples pointing in opposite directions

`examples/` ships a pair of finished skills that are **counter-examples of each other** — reading them side by side shows the framework's edge:

| Sample | Trim and structure | What it tells you |
|---|---|---|
| `journal-qiming-regional` | A4 / 91 pages / **single column** / short items mixed with long articles | **The happy path**: runs through, production-ready (`spec_confidence: pinned`) |
| `journal-hengshi-observation` | 227×276mm / 52 pages / **two columns** / pure articles | **The reverse path**: where the framework fails — the single-column renderer cannot draw two columns, mid-gray body text gets misread as a secondary color, non-A4 trim needs manual geometry tuning (`spec_confidence: weak`, **not production-ready**) |

Plus `assets/examples/qiming-regional-sample/`: the **raw intermediate artifacts** of the `+learn` stage (StyleSpec / semantic / UnitPattern), used to calibrate the split between "machine extraction" and "human refinement".

**The structure is: this skill is the framework (parent package), `examples/` holds finished samples (child packages).** The child packages are neither a runtime dependency nor the **input** for deriving new ones — they are teaching samples.
**To build your own child package, re-run `+learn` on your own publication and derive — do not edit a sample**:

```
Your latest issue PDF ──+learn──▶ stylespec.json ──human fill-in──▶ unit-patterns.md
                                                                          │
                                                  derive_skill.py ────────┘
                                                          ▼
                                        journal-<your-company>-<type>/   ← self-contained, ready to run, publishable on its own
```

A derived child package **carries its own `slug` / `displayName` / `version`** and can be published to a skill marketplace on its own; `scripts/` and the two `assets/` template directories are copied along, so it runs on another machine immediately. Only `references/` is deliberately left in the parent (it evolves with the framework; a copy would be stale at once) —
**day-to-day work in a child package does not need the parent present; you only come back to the parent for underlying issues like changing trim, redesigning, or switching publication type.**

> ⚠️ **The two finished samples and the one intermediate sample are all desensitized**: institution names, publication names, natural-person names, client and project names, and source file names are **fictional synthetic entities**; what is preserved is the measured layout parameters and template structure. See [`NOTICE.md`](NOTICE.md).

---

## 7. The six easiest traps

| # | Trap | One-line fix |
|---|---|---|
| 1 | **Pagination overflow is silent** | `.page{overflow:hidden}` eats the overflow. Fewer pages than expected means it got clipped — check `overflow` in `--stats` |
| 2 | **"It ran" ≠ "the layout is right"** | Measured case: zero script errors, all attainment rates correct, yet a whole column was offset by half a page and articles were set single-column. After changing trim, always **measure the actual column width** |
| 3 | **Semantic diagrams must not go to text-to-image** | The information lives in label text and topology; diffusion models cannot do it. Measured: 5 of 6 images carried zero information, one had a caption saying "division of labor" while the picture showed "convergence" |
| 4 | **The editable-draft round trip needs a no-op test** | Export docx and write it straight back; it must be byte-identical to the original `content.json`. One no-op run found 5 silent losses |
| 5 | **It promises three questions and asks eight** | That is a flow problem, not a patience problem → move questions earlier and pack them into 3 batches. But **packing ≠ defaulting them off** — the Cue channel must be asked out loud |
| 6 | **Gate re-checks must carry `--spec`** | Since v0.13.1 it no longer passes silently: no `scale_baseline` in the spec means a hard `[FAIL]` + `exit 1`, forcing you to add it or pass `--no-baseline-gate` explicitly |

> The full **12 traps** (including the image `avoid` list not catching sensitive subjects, empty image slots disguising themselves as path errors in docx, skipping positioning when changing publication type producing "all gates green, all conventions wrong"…): **[`references/pitfalls.md`](references/pitfalls.md)**

---

## 8. What is in the package

```
SKILL.md                     main flow and hard rules (read first)
README.md                    this file in Chinese (features, limits, onboarding)
README.en.md                 English version
CHANGELOG.md                 version history and breaking changes
NOTICE.md                    source statement and desensitization notice
LICENSE.md                   MIT (keeps the .md extension: marketplaces reject extension-less files)

references/
  journal-types.md           publication typology: reader × cadence × form × industry × common unit library  ← read before switching type
  pitfalls.md                12 measured traps (including CLI traps)
  cue-onboarding.md          Cue / Omni channel: per-item decision table + suggested scripts + first-time setup
  content-schema.md          content.json field spec (eight page templates / units / blocks / self-checks)
  content-sourcing.md        sourcing matrix L1–L5 (company-owned sources / official texts / structured data / deep research)
  stylespec-schema.md        StyleSpec field definitions
  style-extraction.md        style extraction method and traps
  qa-checklist.md            pre-publication checklist (common floor + industry plugin entry points)
  editable-output.md         editable drafts and the write-back loop
  imagery.md                 images: four decision classes / prompt structure / pre-press checks
  omni-channel.md            document parsing channels and fallbacks
  cue-playbook-map.md        topic → Cue capability mapping
  cue-buddy-map.md           how to solidify a smooth run into a Cue buddy
  instantiation.md           derivation flow
  agent-interaction.md       question batching and delivery action spec
  regulatory-dynamics-spec.md  spec for the regulatory-dynamics section

scripts/                     12 scripts, all support --help, zero network requests
assets/templates/            starter templates: issue-brief / outline / unit-pattern / evidence-card /
                             imagery / progress / content.example / buddy draft
assets/demo/                 **layout drafts you can open directly** (13-page sample + content source + two semantic diagrams)
assets/diagram-templates/    6 semantic diagram definitions (columns / flow / rows / stack / converge / footer)
assets/examples/             intermediate artifacts from +learn
examples/                    two finished sample skills, installable or adaptable as-is
```

**Dependencies**: `pymupdf` (required) · `python-docx` / `pillow` (optional) · everything else is stdlib only.
`build_draft.py --pdf` is a legacy path (depends on `playwright`) — **do not use it**; PDFs are always self-drawn by `export_pdf.py`.

Version is in the `SKILL.md` frontmatter.
