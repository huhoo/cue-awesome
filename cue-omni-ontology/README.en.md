# cue-omni-ontology

**[中文](README.md) · [English](README.en.md)**

**Build and update business knowledge from public documents.** Organize a few sources into evidenced claims; add material without losing history or confusing reporting bases. Version 0.1.1 is a public experimental release.

The Chinese README is canonical for user documentation. `SKILL.md` is the canonical English agent instruction; `SKILL.zh-CN.md` is its Chinese counterpart.

## Three tasks

```text
Use cue-omni-ontology to organize this company's businesses and metrics from these two reports, with evidence.
Add this announcement to the previous package and list new claims, conflicts and proposed definition changes.
Explain which figures are comparable; show separate reporting bases and their sources.
```

Default scope is one subject and 2–5 public sources, primarily digital PDFs and webpages. Confirm the public origin of local files. Official [cue-omni-reader](https://github.com/sensedeal/cue-skills/tree/main/cue-omni-reader) performs parsing; the host model extracts semantics. The Python utility packages, queries and updates extracted data; it is not an extraction model or replacement parser.

## Try an offline example

See the [public-report preview](assets/public-example/preview.md) for reporting-basis and update behavior. It is explicitly labeled as saved-output replay.

[r1.json](assets/demo/r1.json) and [r2.json](assets/demo/r2.json) use fictional training text included in the package. `example.org` addresses are labels, not real disclosure endpoints.

| Input | Expected behavior |
|---|---|
| Old: prior-quarter revenue 100; Alpha product mentioned | Two candidate source assertions |
| New: current revenue 120, adjusted revenue 115, prior-quarter comparative restated to 105 | Separate bases; retain 100/105 as a conflict |
| Alpha absent from new text | Keep the old relationship, no retirement inference |
| Import the same new input again | No duplicate source assertions |

Requires Python 3.10+. From the skill directory, replace all placeholder paths with **new directories in your own workspace**, outside the skill/repository:

```sh
python3 scripts/ontology.py --help
python3 scripts/ontology.py build assets/demo/r1.json --out /path/to/work/v1
python3 scripts/ontology.py update assets/demo/r2.json --base /path/to/work/v1 --out /path/to/work/v2
python3 scripts/ontology.py validate /path/to/work/v2
python3 scripts/ontology.py query /path/to/work/v2 --concept metric:revenue --period 2026Q1
python3 scripts/ontology.py query /path/to/work/v2 --concept metric:revenue --period 2026Q1 --basis IFRS
python3 scripts/ontology.py export-okf /path/to/work/v2 --out /path/to/work/okf-v2
```

For `needs_scope`, inspect returned `scopes` and filter with `--unit`, `--valid-from`, `--valid-to`, or `--fact` using a returned fact ID. A fact ID retains all conflicting assertions in that scope. Validity filters match exact boundaries, not historical point-in-time inference. Report rows include fact IDs, validity and conflict markers.

On Windows use your workspace paths and `python` if appropriate. These paths are placeholders, not literal user directories.

## Install and use real sources

Place this directory in your host's supported skills location, or use the repository's skills CLI route:

```sh
npx skills add huhoo/cue-awesome --skill cue-omni-ontology
```

This command requires Node.js/npm; the Python examples do not. This package does not automatically install Omni dependencies or configure MCP.

Connect official Omni Reader MCP using its [setup guide](https://github.com/sensedeal/cue-skills/blob/main/cue-omni-reader/references/setup.md). Follow host/upstream authorization for installation and file access. Configure the key in your own secret facility, never in chat or Issues. Trial allowances and charges come from the live service.

The agent workflow is public sources → Omni parsing and evidence snapshots → constrained host extraction → offline packaging/validation → semantic review → answers/updates. Calculate locators from actual parsed bytes. Do not guess pages or cite operation handles. Use the natural-language prompts once Omni is connected. Protocol compatibility does not establish tested quality on every host/model.

## Outputs

- `report.md`: reviewable claims, bases, changes and conflicts.
- `knowledge.json`: candidate definitions, entities, assertions and review history.
- `sources.jsonl` / `evidence/`: original URLs, dates, locators and exact parsed snapshots.
- `changes.json` / `run.json`: version changes, integrity checks and versions.
- `extraction-notes.md`: separately written by the agent, covering model, scope, failed sources and semantic checks.
- Optional OKF: draft concept files targeting the 0.2 core subset; no verified external import is claimed.

Existing earnings/DD skills need explicit adaptation and their own checks; automatic compatibility is not established.

## Verification status

See [verification.md](references/verification.md) for actual runs, saved-output replay, synthetic checks and untested scope. Development fixtures are not general accuracy measurements. Hash/range checks do not establish semantic truth.

Offline checks, with no network or charges:

```sh
python3 -B scripts/test_ontology.py
```

## Feedback and enterprise use

After using the result, optionally generate a local draft:

```sh
python3 scripts/ontology.py feedback /path/to/work/v2 --out /path/to/work/feedback.json
```

Nothing is sent. Review it before choosing to report public bugs in [Issues](https://github.com/huhoo/cue-awesome/issues/new). Discuss business details, contacts and private material through a separately agreed private channel. There is no telemetry; downloads are not completed runs. Useful feedback describes your own source task, repeat updates, review/correction effort and target workflow.

## Boundaries and license

v0.1 stores directly reported claims and retains conflicts/history. Keep derived computations in answers with their inputs. Definitions remain candidates; there is no automatic enterprise schema publication. The local review log is not IAM or production approval. Uploading a local file to a cloud parser is not full on-prem deployment.

Code/docs are MIT; see [LICENSE](LICENSE). Synthetic examples refer to no real enterprise. Public sources retain their own usage conditions; public readability is not blanket redistribution permission. The Python utility has no network calls or telemetry; agent-side parsing/model use still relies on the respective services.
