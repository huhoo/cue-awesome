# cue-omni-ontology

**Turn public documents into business knowledge you can update and check.**

Give an agent two releases or reports. Receive **evidenced answers, a searchable change brief with source excerpts, and a reusable knowledge package** for the next update. Start with disclosure tracking, public supplier diligence, or product/competitor monitoring.

**English companion of `README.md` (Chinese primary; repo-local reference — channel pages do not resolve relative links).** beta · Python standard-library tools · No usage telemetry

## See the value

[Microsoft public-disclosure example](assets/public-example/live-preview.md): a fresh parse-to-answer run, including extraction, build/update and evidence queries.

| Your question | What the skill provides |
|---|---|
| Why are there two numbers for one metric? | Separate periods, units, bases and qualifiers, with each source. |
| Must I start over after the next report? | Update the existing package while retaining history, added support and conflicts. |
| Where did this conclusion come from? | Search the brief, expand verbatim excerpts and inspect original URLs/locators. |
| Can my next agent task reuse the work? | Structured knowledge and optional draft OKF core-subset export. |

Begin with one subject, 2–5 public sources and a concrete question. A complete enterprise ontology is not a prerequisite.

## First try: no API key

Ask your agent:

> Use cue-omni-ontology with its bundled demo. Show what a new release adds, where claims conflict, and how to inspect the evidence.

Or run one command from the skill directory (Python 3.10+):

```sh
python3 scripts/ontology.py demo --out /path/to/work/cue-demo
```

Replace the placeholder with a **new directory in your workspace**. Open `cue-demo/brief/brief.html`; no server is needed. Search, filter new/conflicting claims and expand excerpts. Hosts without HTML rendering can read adjacent `brief.md` / `brief.json`.

The example is fictional and makes zero API/network calls. Prior revenue 100 and a later comparative 105 remain conflicting; current revenue 120 and adjusted 115 stay separate; an unmentioned Alpha product is not inferred retired.

## Install and use your sources

```sh
npx skills add huhoo/cue-awesome --skill cue-omni-ontology
```

This install route requires Node.js/npm; copying this directory into your host's supported skills location is also possible. Offline tooling only needs Python. Real parsing uses official [cue-omni-reader](https://github.com/sensedeal/cue-skills/tree/main/cue-omni-reader); follow its [setup](https://github.com/sensedeal/cue-skills/blob/main/cue-omni-reader/references/setup.md) to connect MCP and configure credentials. This package does not install or configure Omni automatically. Keep keys in your secret facility, not chat or Issues.

Once connected, provide sources and ask:

```text
Use cue-omni-ontology to answer from these two public reports:
1. What is newly disclosed?
2. Which figures require separate bases before comparison?
3. What remains unsupported?
Give me a brief with expandable evidence and a package I can update next time.
```

Then reuse it:

```text
Add this new announcement to the existing package and produce a change brief.
Preserve old records and highlight conflicts. Missing mentions are not deletions.
```

See [task-recipes.md](references/task-recipes.md) for business tasks. Official Omni parses sources; the host model extracts semantics; offline tooling handles locators, versions, queries and briefs. Protocol compatibility is not certification of every host.

## Reduce mechanical extraction work

Agents can copy exact quotes instead of calculating hashes and UTF-8 offsets manually. See [quote-draft.json](assets/demo/quote-draft.json) and [quote-input.md](references/quote-input.md):

```sh
python3 scripts/ontology.py prepare assets/demo/quote-draft.json --out /path/to/work/prepared
python3 scripts/ontology.py build /path/to/work/prepared/input.json --out /path/to/work/v1
python3 scripts/ontology.py update assets/demo/r2.json --base /path/to/work/v1 --out /path/to/work/v2
python3 scripts/ontology.py brief /path/to/work/v2 --base /path/to/work/v1 --out /path/to/work/brief
python3 scripts/ontology.py query /path/to/work/v2 --concept metric:revenue --period 2026Q1 --with-evidence
```

Repeated quotes require more context or an explicit occurrence; no fuzzy match is used. For `needs_scope`, choose a basis, unit, exact validity boundaries or returned fact ID. `--with-evidence` includes bounded verbatim previews and flags truncation. Matching is not semantic verification: inspect headers, footnotes and qualifications.

## Deliverables and verification

- **Human entry point:** offline `brief.html`, Markdown counterpart, sources, scope distinctions, changes and excerpts.
- **Reusable knowledge:** `knowledge.json`, `sources.jsonl`, `changes.json`, `run.json` and exact source snapshots.
- **Extraction notes:** host-written `extraction-notes.md` records questions, gaps, failed sources and semantic review.
- **Optional interchange:** `export-okf` creates draft concepts targeting the OKF 0.2 core subset; external consumer imports need separate verification.

The [verification record](references/verification.md) distinguishes fresh parsing, saved-output replay, independent synthetic use and remaining limits. The [Microsoft run](references/live-verification.md) produced 21 source claims from two sources and retained all 11 baseline claims after updating. It demonstrates a bounded workflow, not general extraction accuracy or proven customer ROI.

Offline self-check:

```sh
python3 -B scripts/test_ontology.py
```

## Feedback that matters

**Did your own documents answer your question? Would you add the next release? Where did correction still take effort?** These signals are more useful than download counts.

`feedback PACKAGE --out NEW_FILE` creates a local draft. Review it and decide whether to submit a [public issue](https://github.com/huhoo/cue-awesome/issues/new); nothing is uploaded automatically. Share private material, contacts and business context through a separately agreed private channel.

For internal-document monitoring, downstream agents/ERP/CRM, domain schema review or full on-prem deployment, describe the **task, update frequency, current review effort and target workflow**. These are discovery topics, not production capabilities already delivered by this public skill.

## Boundaries and license

Store directly reported claims; disclose inputs for derived calculations and judgments in answers. Definitions remain candidates; local review records do not provide enterprise IAM or operational authorization. Cloud parsing of a local file is not full on-prem deployment.

Briefs include bounded source excerpts; complete packages contain parsed text. Check source conditions and authorization before sharing. Code/docs are [MIT](LICENSE); public access is not blanket permission to redistribute entire reports. The Chinese README is canonical user documentation; English SKILL.md is canonical agent guidance, with synchronized translations.
