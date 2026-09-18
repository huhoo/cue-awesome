# cue-awesome

**[English](README.md) · [中文](README.zh-CN.md)**

A personal collection of self-built agent skills for WorkBuddy / Cue. Each subdirectory is a standalone skill — copy the one you need and use it on its own.

## Skills

| Directory | Name | Version | What it does |
|---|---|---|---|
| [`journal-draft/`](journal-draft/) | journal-draft | 0.15.3 | Draft generator for corporate journals / in-house magazines / client newsletters / investor letters / ESG reports / yearbook specials. It **measures** a publication's layout and editorial conventions out of a sample PDF and turns them into verifiable parameters (grid, type area, type scale, leading, color palette, section templates), then produces the next issue against those parameters. Includes the regulatory-dynamics section spec and CTA source-tracing. |
| [`long-doc-translation/`](long-doc-translation/) | long-doc-translation | 1.2.0 | High-quality full-text Chinese translation pipeline for long foreign-language (German / English / French / Japanese …) scholarly monographs, classics, archives and translated works: parse → clean & slice → build style guide + glossary → parallel batched translation → multi-dimensional QA → merge into a reading edition with a table of contents. |
| [`competitive-brief/`](competitive-brief/) | competitive-brief | 0.1.0 | Competitive-analysis brief generator: turns competitor material scattered across web pages / PDFs / recordings / video into a traceable, comparable, updatable decision brief. Six-stage pipeline: ingest (omni-reader) → brief → comparison map → evidence (cue-research) → three-format delivery → QA gates. |

## Install

With the skills CLI:

```bash
npx skills add huhoo/cue-awesome                            # lists all skills
npx skills add huhoo/cue-awesome --skill journal-draft      # add one skill
```

Or copy the directory you want into the WorkBuddy user-level skills directory:

```bash
cp -r journal-draft ~/.workbuddy/skills/
cp -r competitive-brief ~/.workbuddy/skills/
```

On Windows: `C:\Users\<username>\.workbuddy\skills\`

## Language

Docs are bilingual: `README.md` (English) / `README.zh-CN.md` (Chinese). Skill instruction files follow the same convention — see [`docs/i18n.md`](docs/i18n.md).

## Notes

- This is a **personal** collection. It is not affiliated with the official Cue skills monorepo [sensedeal/cue-skills](https://github.com/sensedeal/cue-skills), is not a subset of it, and is not merged into it.
- `LICENSE.md` / `NOTICE.md` apply to the whole repository.
- Build artifacts (`dist/`, `*.zip`) are not committed; release packages are described in each skill's manifest / CHANGELOG.
