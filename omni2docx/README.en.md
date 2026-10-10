# omni2docx — Rebuild Omni parse results as fidelity Word

Rebuilds Omni Reader parse results into **human-readable, editable .docx**. Not
another markdown→docx converter: it maps the structured information Omni already
computed during parsing (page anchors, heading levels, frame/transcript metadata)
back into native Word objects — generic converters only see the markdown and lose
all of it.

## What it is / what it is not

| It is | It is not |
|---|---|
| grounded page anchors → native Word page breaks (page-level fidelity) | pixel-perfect layout cloning |
| official outline → real Heading levels + visible TOC | PPTX / PDF output (later stage) |
| GFM tables / superscript footnotes + notes section / gray source tags | embedding image/audio bytes (Omni returns no bytes; text provenance tags are kept) |
| multi-source merge + auto "provenance appendix" (pages / timestamps / speakers) | investment advice, content creation |

## Three scenarios

1. **Agent output → deliverable document**: `--md` direct conversion of agent markdown, with professional CJK typography.
2. **Scanned PDF / non-editable files → editable Word**: `--page-marks` stamps "source page N" at every page boundary for proofreading against the original.
3. **Multi-source evidence merge → litigation documents etc.**: a `sources` array becomes one chapter per source + master TOC + provenance appendix; transcript/frame tags are directly quotable.

## Getting started (three steps)

Prerequisites: `python3` + `pip install python-docx`; scenarios ②③ additionally
require a connected omni-reader MCP (scenario ① does not).

```bash
# ① agent markdown direct output (no intermediate JSON)
python scripts/build_docx.py --md output.md --out deliverable.docx --profile gov --page-numbers

# ②③ Omni parse rebuild: parse(grounded) → markdown+grounding (+ same-session read_outline) → intermediate JSON
python scripts/build_docx.py --json intermediate.json --out deliverable.docx --profile legal --page-marks

# Acceptance (mandatory): zero character loss + structure checks
python scripts/validate_docx.py --json intermediate.json --docx deliverable.docx
```

Omni discipline: use the agent-native MCP tools throughout (parse /
get_parse_status / read_outline / read_result) **within the same session** — do
not write spawn scripts around omni (cross-process read_* calls fail by design).

## Scenario profiles (--profile)

Typography is decided by the document's use scenario; presets are reference
values only: `gov` (GB/T 9704 official documents), `legal` (litigation),
`finance` (research reports), `academic` (papers), `default`. Any parameter can
be overridden via `--profile` with inline JSON or a .json file (fonts, sizes,
line spacing, indents, margins, table style).

Quality baseline: headings always black with per-level sizes, zero CJK fake
italics (CJK emphasis → bold), `--page-numbers` adds a footer PAGE field,
`--strip-emoji` removes decorative symbols.

## Capability boundaries (honest list)

- Fidelity is **page-level** (grounded); element-level bbox data is available via
  `detail=layout`, engine consumption is a later stage.
- `read_result` / `read_outline` are bound to a **same-session constraint**
  (`local_result_cache` lives with the bridge process); fine inside an agent-native session.
- Paragraphs spanning page boundaries belong to the page where they start.
- Complex markdown (nested tables, math) degrades to text; tables are layout-faithful, not pixel-faithful.
- `.docx` output only; CJK font names (SimSun, FangSong_GB2312, KaiTi…) are
  substituted automatically by Word/WPS on non-Windows systems — acceptance for
  format-regulated documents should happen on Windows/WPS.

## Acceptance

`validate_docx.py` checks character-level CJK coverage (PASS at ≥99%) plus anchor
phrases and structure counts (page breaks / headings / tables). A real-corpus
matrix (xlsx / PDF reports / HTML / audio transcripts / docx / PPTX / JPG OCR /
1000-page PDF / truncated PDF / edge cases, across profiles) measured 100%
coverage on every case.

## Files

| File | Purpose |
|---|---|
| `SKILL.md` | agent-facing instructions (full workflow, field contract, parse-side capability notes) |
| `scripts/build_docx.py` | rendering engine (single source / multi-source merge / markdown direct) |
| `scripts/validate_docx.py` | fidelity + structure validator |
