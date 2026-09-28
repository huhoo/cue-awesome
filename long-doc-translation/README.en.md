# long-doc-translation

**English companion of `README.md` (Chinese primary; the pair is for reading inside the repository — skill-channel pages do not resolve relative links, so this is deliberately not a clickable switch).**

Turn a several-hundred-page foreign-language monograph into a **deliverable, verifiable, terminologically consistent** Chinese full manuscript.

## In one line

Not "translate a passage" — it is about keeping 100+ translation units consistent in style and wording, so that after merging there are no duplicates, no broken joins, and no untranslated leftovers.

## Pipeline

parse → clean & slice → build style guide + glossary → parallel batched translation → multi-dimensional QA → merge into a reading edition with a table of contents

## Fit

- Scholarly monographs, classics, archives and translated works over 300 pages (German / English / French / Japanese …)
- When you need consistent terminology book-wide, preserved footnotes, and traceable doubtful spots

## Dependencies

- `python3` + `markdown` + `pypinyin` (core scripts run fully offline)
- omni-reader (optional: stage one "parse" converts PDF / images to text)

## Scripts (`scripts/`)

`init_project.py` · `dedup_boundary.py` · `overlap_check.py` · `qa_check.py` · `merge_build.py` · `build_reader.py` · `_common.py`

## Specs (`references/`)

| File | Content |
|---|---|
| `pitfalls.md` | Five pitfalls: detection / fix / prevention, including **silent script failure modes** |
| `qa-checklist.md` | Seven QA criteria + script thresholds + fixes + delivery baseline |
| `reader-build.md` | Engineering decisions and dependency degradation for the enhanced reader HTML |
| `parallel-translation.md` | Chunking rules, three must-haves for sub-agent prompts, acceptance checks |

## Getting started

```bash
python scripts/init_project.py --help        # of the six scripts, only this one accepts --help
python scripts/qa_check.py                  # the others print their usage when run bare (missing args exit 1, not a crash)
python scripts/build_reader.py               # these two carry default paths: a missing directory **errors out with checks to try**
# Measured: a nonexistent directory always exits 1 with guidance — it never prints "0 segments" and a row of green ticks.
```

See [`SKILL.md`](SKILL.md) for the full flow, hard rules and measured parameters; see [`CHANGELOG.md`](CHANGELOG.md) and the `SKILL.md` header for the current version — **this file states no version number** (one written here would be lying forever).

One command prints the constants the three QA scripts actually judge with, including their per-project "change this here" CONFIG blocks, runnable from any directory:

```bash
grep -n "CONFIG\|^[A-Z_]\{2,\} *=" ~/.workbuddy/skills/long-doc-translation/scripts/qa_check.py ~/.workbuddy/skills/long-doc-translation/scripts/overlap_check.py ~/.workbuddy/skills/long-doc-translation/scripts/dedup_boundary.py
```

The gates come in two kinds: **fixed in-package gates** (a missing directory errors out rather than printing zero segments, segment-count reconciliation, TOC depth, page-number continuity) and **project-configured domains** (page-mark regex, the OCR typo table, the three note section names, which files/sections are skipped, grouping patterns and the default thresholds). Every number in this file, in `SKILL.md` and in `references/qa-checklist.md` is a mirror and a common example, **not an exhaustive claim** — the scripts as they now stand govern.
