# long-doc-translation

**[中文](README.md) · [English](README.en.md)**

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
python scripts/init_project.py --help    # every script supports --help
```

See [`SKILL.md`](SKILL.md) for the full flow, hard rules and measured parameters; see [`CHANGELOG.md`](CHANGELOG.md) for version history. Current version **1.3.0**.
