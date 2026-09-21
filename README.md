# cue-awesome

**[English](README.md) · [中文](README.zh-CN.md)**

A personal collection of self-built agent skills for WorkBuddy / Cue. Each subdirectory is a standalone skill — copy the one you need and use it on its own.

## Skills

| Directory | Name | Version | What it does |
|---|---|---|---|
| [`journal-draft/`](journal-draft/) | journal-draft | 0.15.3 | Draft generator for corporate journals / in-house magazines / client newsletters / investor letters / ESG reports / yearbook specials. It **measures** a publication's layout and editorial conventions out of a sample PDF and turns them into verifiable parameters (grid, type area, type scale, leading, color palette, section templates), then produces the next issue against those parameters. Includes the regulatory-dynamics section spec and CTA source-tracing. |
| [`long-doc-translation/`](long-doc-translation/) | long-doc-translation | 1.3.0 | High-quality full-text Chinese translation pipeline for long foreign-language (German / English / French / Japanese …) scholarly monographs, classics, archives and translated works: parse → clean & slice → build style guide + glossary → parallel batched translation → multi-dimensional QA → merge into a reading edition with a table of contents. |
| [`competitive-brief/`](competitive-brief/) | competitive-brief | 0.3.0 | Competitive-analysis brief generator: turns competitor material scattered across web pages / PDFs / recordings / video into a traceable, comparable, updatable decision brief. Six-stage pipeline: ingest (omni-reader) → brief → comparison map → evidence (cue-research) → three-format delivery → QA gates. |
| [`cn-earnings-note/`](cn-earnings-note/) | cn-earnings-note | 0.3.3 | A-share / HK-share earnings deep-dive note generator: turns a subject + reporting period into an 8–12 page AI draft at **research-report structure level** (an eight-section skeleton: four-period disclosure deltas, segment price/volume, earnings quality & cash-flow, footnote risk scan, guidance & catalysts, peer cross-check), with every figure traceable and ratings / target prices always marked `[待人工]` (human review). Evidence is gathered through the three Cue channels — structured disclosure via Cue data-MCP domains, source parsing via omni-reader, and horizontal deep research via cue-research. **P1 end-to-end testing is complete** (2026-09-18/19: Midea 000333 across two seasons 2026H1+2025AR, and CNBM Yuhong 002271 2026H1; acceptance records in `cn-earnings-note/CHANGELOG.md` Verified); HK-share subjects and multi-subject batching remain untested. Base provenance: see [NOTICE.md](NOTICE.md) §financial-suite. |
| [`catalyst-calendar/`](catalyst-calendar/) | catalyst-calendar | 0.1.0 | Catalyst calendar for a holdings set: subject list (≤10) + forward window (default 90 days) in; a date-sorted calendar out where **every event carries a disclosure anchor** (buyback nodes / equity-incentive vesting / unlock & reduction disclosures / regulatory reply deadlines / dividend dates / statutory filing deadlines by rule derivation). Events are stated, never judged — undisclosed events are excluded, bull/bear wording is banned, anchorless rows are deleted. Four machine checks target date hallucination specifically. **Freshly built: no end-to-end run yet; treat the first real subject as unverified.** Base provenance: see [NOTICE.md](NOTICE.md) §financial-suite. |

## Financial-research suite roadmap

The financial-research skills are a Cue-native rewrite of the methodology base in **anthropics/financial-services** (Apache-2.0); localization practices (CAS terminology, compliance wording, `[待人工]` handling) are first referenced from **道以研究院 dao-financial-services v0.1.9** (MIT). We re-implement rather than copy — the data layer is entirely replaced by the three Cue channels: **deep research (cue-research) · data-MCP domains (Cue) · document parsing (omni-reader)**. Attribution details in [NOTICE.md](NOTICE.md).

> **Status.** Two financial-research skills now exist in this repository: `cn-earnings-note` (v0.3.3, P1 end-to-end verified) and `catalyst-calendar` (v0.1.0, machine checks green, no end-to-end run yet); the rest is direction that has been scoped but **not built and not available**. **Except `cn-earnings-note`, which has completed P1 end-to-end runs (acceptance records in its CHANGELOG Verified); design values remain for all other scoped-but-unbuilt items.** Nothing in this roadmap is promised as shipped beyond what the Skills table above lists.

### Built — the vanguard (2 skills)

- **Earnings deep-dive — [`cn-earnings-note/`](cn-earnings-note/)** (v0.3.3): A-share / HK-share earnings deep-dive notes — the only financial skill delivered so far, P1-verified across 4 runs / 2 subjects. Full one-liner in the Skills table above.
- **Catalyst calendar — [`catalyst-calendar/`](catalyst-calendar/)** (v0.1.0): second vanguard of batch 2; machine checks 8/8 green, end-to-end run not yet done.

### Planned — batch 2 (direction set, not yet built)

Scoped but **not implemented and not available**:

- **Sector overview — 行业景气全景**: industry cycle & landscape briefing.
- **Company one-pager — 公司一页纸**: a fast tear-sheet built from public disclosures.
- **Public-info pre-due-diligence — 公开信息预尽调**: checklist screen from regulatory / statute / IPO-in-review / entity data.

### Deferred (blocked, not built)

- morning-note, idea-generation / screening, comps-analysis — held until the `equity_market` domain goes live (its status is whatever `GET https://cuecue.cn/api/mcp-catalog` reports; a coming-soon domain is never promised).

### Excluded by structure

- Excel-model skills, fund-administration (private internal books), and anything that depends on private data such as accounts or CRM are out of scope — Cue channels are a complement to these, not an internal-ledger or valuation-model engine.

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

## Contributing

Read [`CONTRIBUTING.md`](CONTRIBUTING.md) before opening a PR: commit format, the checklist for adding a skill, and what must never be committed. The gate runs on every push and PR:

```bash
python scripts/check_skills.py
```

New skill proposals: open an issue with the **new skill proposal** template.

## Notes

- This is a **personal** collection. It is not affiliated with the official Cue skills monorepo [sensedeal/cue-skills](https://github.com/sensedeal/cue-skills), is not a subset of it, and is not merged into it.
- `LICENSE.md` / `NOTICE.md` apply to the whole repository.
- Build artifacts (`dist/`, `*.zip`) are not committed; release packages are described in each skill's manifest / CHANGELOG.
