# cue-awesome

**[English](README.md) · [中文](README.zh-CN.md)**

A personal collection of self-built agent skills for WorkBuddy / Cue. Each subdirectory is a standalone skill — copy the one you need and use it on its own.

## Skills

| Directory | Name | Version | What it does |
|---|---|---|---|
| [`journal-draft/`](journal-draft/) | journal-draft | 0.15.3 | Draft generator for corporate journals / in-house magazines / client newsletters / investor letters / ESG reports / yearbook specials. It **measures** a publication's layout and editorial conventions out of a sample PDF and turns them into verifiable parameters (grid, type area, type scale, leading, color palette, section templates), then produces the next issue against those parameters. Includes the regulatory-dynamics section spec and CTA source-tracing. |
| [`long-doc-translation/`](long-doc-translation/) | long-doc-translation | 1.3.0 | High-quality full-text Chinese translation pipeline for long foreign-language (German / English / French / Japanese …) scholarly monographs, classics, archives and translated works: parse → clean & slice → build style guide + glossary → parallel batched translation → multi-dimensional QA → merge into a reading edition with a table of contents. |
| [`competitive-brief/`](competitive-brief/) | competitive-brief | 0.3.0 | Competitive-analysis brief generator: turns competitor material scattered across web pages / PDFs / recordings / video into a traceable, comparable, updatable decision brief. Six-stage pipeline: ingest (omni-reader) → brief → comparison map → evidence (cue-research) → three-format delivery → QA gates. |
| [`cn-earnings-note/`](cn-earnings-note/) | cn-earnings-note | 0.3.3 | A-share / HK-share earnings deep-dive note generator: turns a subject + reporting period into an 8–12 page AI draft at **research-report structure level** (an eight-section skeleton: four-period disclosure deltas, segment price/volume, earnings quality & cash-flow, footnote risk scan, guidance & catalysts, peer cross-check), with every figure traceable and ratings / target prices always marked `[待人工]` (human review). Evidence is gathered through the three Cue channels — structured disclosure via Cue data-MCP domains, source parsing via omni-reader, and horizontal deep research via cue-research. **P1 end-to-end testing is complete** (run counts, subjects and the still-unverified scope are stated in this package's README status section); HK-share subjects and multi-subject batching remain untested. Base provenance: see [NOTICE.md](NOTICE.md) §financial-suite. |
| [`catalyst-calendar/`](catalyst-calendar/) | catalyst-calendar | 0.1.0 | Catalyst calendar for a holdings set: subject list (≤10) + forward window (default 90 days) in; a date-sorted calendar out where **every event carries a disclosure anchor** (buyback nodes / equity-incentive vesting / unlock & reduction disclosures / regulatory reply deadlines / dividend dates / statutory filing deadlines by rule derivation). Events are stated, never judged — undisclosed events are excluded, bull/bear wording is banned, anchorless rows are deleted. Four machine checks target date hallucination specifically. **Adversarial final review passed (2026-09-21); first real runs on record — counts and the still-unverified scope are stated in this package's README status section.** Base provenance: see [NOTICE.md](NOTICE.md) §financial-suite. |
| [`tear-sheet/`](tear-sheet/) | tear-sheet | 0.1.1 | Company tear-sheet (client meeting prep): ≤5 subjects + context → five fixed sections, every line disclosure-anchored, header carries asof + channel usage; zero deep-research by default; opinion slots always `[待人工]`. **Adversarial final review passed (2026-09-21); first real runs on record — counts and the still-unverified scope are stated in this package's README status section.** |
| [`sector-overview/`](sector-overview/) | sector-overview | 0.1.1 | Industry cycle briefing (six sections): every trend judgement must sit in the same line as its comparable-series anchor, else the verbatim "no comparable series, no cycle judgement" applies; policy timeline uses three-part statute anchors. **Adversarial final review passed (2026-09-21); first real runs on record — counts and the still-unverified scope are stated in this package's README status section.** |
| [`dd-checklist/`](dd-checklist/) | dd-checklist | 0.1.0 | A due-diligence screen from public disclosures: nine risk categories, every entry anchor-bound; what could not be checked is stated as such — no investment verdict, no legal opinion. **Real-subject end-to-end run on record; adversarial re-review closed — the verified scope and the remaining unverified tiers are stated in this package's README status section.** Base provenance: see [NOTICE.md](NOTICE.md) §financial-suite. |

## Financial-research suite roadmap

The financial-research skills are a Cue-native rewrite of the methodology base in **anthropics/financial-services** (Apache-2.0). We re-implement rather than copy — the data layer is entirely replaced by the three Cue channels: **deep research (cue-research) · data-MCP domains (Cue) · document parsing (omni-reader)**. Attribution details in [NOTICE.md](NOTICE.md).

> **Status.** The financial-research skills published here are exactly those listed in the Skills table above. `cn-earnings-note` completed its P1 end-to-end runs (acceptance records in its `CHANGELOG.md`, under Verified). `catalyst-calendar`, `tear-sheet` and `sector-overview` passed adversarial final review on 2026-09-21 and each now has one real run on record: catalyst — a full-window multi-subject run with the evidence chain enforced, forward rows sparse by domain reality, and the statutory-deadline derivation attempted then refused (the statute channel returned no source text in that run); tear-sheet — a pre-meeting brief at the contract's subject cap, one pass; sector-overview — building materials, half-journey: volume/price lines each carry their stated scope and source anchor, competing asphalt quotes left un-arbitrated by design, while the industry price/volume domain expansion is still pending (the macro domain carries no domestic industry series). **Measured counts live in each package's own `README.md` status section and are deliberately not repeated here.** Current version numbers live in each package's `CHANGELOG.md`, not in this sentence. Everything else in the roadmap is scoped direction: **not built, not available, and nothing beyond the table above is promised as shipped.**

### Built — the vanguard (reviewed; first real runs on record)

- **Earnings deep-dive — [`cn-earnings-note/`](cn-earnings-note/)**: A-share / HK-share earnings deep-dive notes; P1-verified end to end (run and subject counts in this package's `README.md` status section). Version per this package's `CHANGELOG.md`. Full one-liner in the Skills table above.
- **Catalyst calendar — [`catalyst-calendar/`](catalyst-calendar/)**: full-window run on record with the evidence chain enforced — forward rows sparse by domain reality, each empty section carrying an attribution line, and a statutory-deadline derivation attempted then refused; adversarial review closed. Counts live in this package's `README.md` status section, not here. Version per this package's `CHANGELOG.md`.
- **Tear-sheet — [`tear-sheet/`](tear-sheet/)**: pre-meeting run at the contract's subject cap on record, one pass; adversarial review closed; guard samples all green (counts per this package's `README.md` status section). Client-ready one-pager, five fixed sections, line-level anchors.
- **Sector overview — [`sector-overview/`](sector-overview/)**: building-materials half-journey on record — volume/price lines each carry a stated scope and their source anchor, competing asphalt quotes deliberately left un-arbitrated; adversarial review closed, domestic industry price/volume domain still pending. The single authoritative count and its scope live in this package's `README.md` status section. Trend judgements require same-line comparable-series anchors.
- **DD-checklist — [`dd-checklist/`](dd-checklist/)**: two review rounds returned BLOCK first (M63, M70), fixed question-by-question against §v2, re-review M76 = LGTM; the sample bank is whatever `scripts/fixtures/` runs green today (counts live in the reviewer's mapping table, not repeated here). **Real-subject end-to-end runs on record (all six parameters, gate exits 0); the verified scope and the still-unverified tiers are stated in this package's `README.md` status section and are not repeated here.** Version per this package's `CHANGELOG.md`.

### Planned — batch 2 (direction set, not yet built)

Two items formerly listed here are now built and reviewed — `sector-overview` and `tear-sheet` (see the Built section above). What remains scoped here, none of it available today: **initiating coverage** (first-coverage note; valuation/model steps hand off to a human as `[待人工]`), **thesis tracker** (periodic re-run of a stored thesis against fresh public disclosure), **funding digest** (primary-market raise summary from IPO and disclosure domains). Each depends on data paths that are either already listed as available or explicitly deferred below; none is promised as shipped.

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
