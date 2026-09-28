# Verification record — 2026-09-28, v0.1.1

This record distinguishes executed code, synthetic host tasks and saved parser output. It is not a general extraction accuracy report.

| Surface | Executed result | Limits |
|---|---|---|
| Offline boundary suite | 36 tests pass (`python3 -B scripts/test_ontology.py`) | Synthetic fixtures; no live parser, no LLM accuracy or enterprise IAM claim |
| Independent host use | A separate agent followed SKILL.md using newly supplied fictional Cedar Instruments releases; built/updated two versions and answered business questions | Supplied parsed synthetic text; no live Omni invocation and no claim of cold client onboarding |
| Independent query outcomes | Unscoped Q1 `needs_scope`; statutory/adjusted Q1 each `found`; restated Q4 `conflict`; alleged Beacon discontinuation `not_found` | One task, not a statistical generalization benchmark; machine assertions were not marked human-reviewed |
| Public-source replay | Existing grounded Omni output for two Tencent 2026 quarterly releases successfully repackaged and updated | Saved earlier output and seeded rule-extracted claims; not a fresh model extraction or fresh parser run |
| Replay counts | 2 sources, 1 entity, 18 metric definitions, 96 source assertions, 83 fact scopes; second batch adds 36 facts and 13 supporting assertions | Definitions here group metric labels; bases/qualifiers live on facts, so counts differ from the earlier prototype's 23 combined metric/basis concepts |
| OKF exporter | Public replay produced 18 concept files plus navigation | Core Markdown/YAML subset only; no external consumer import verified |

The independent host task and public replay below were originally executed with v0.1.0; the v0.1.1 audit adds eight offline regressions. Version 0.1.1 fixes numeric-spelling conflicts, scope selection, boolean qualifier matching, structured errors for malformed assertions and unsafe Markdown rendering; it exposes conflict IDs/validity in reports. Schema remains 0.1.0.

Scrubbed machine summaries: [forward-results.json](forward-results.json), [replay-results.json](replay-results.json). Public source metadata and hashes: [sources.json](../assets/public-example/sources.json). Full reports/parsed sources are not redistributed with this skill.

The earlier parser run used official Omni Reader Bridge 1.8.4 and native page anchors. The new package preserves the exact stored text hashes. This release added **zero** live parse calls and makes no new billing or speed claim.

Not established: arbitrary document-family extraction accuracy; fresh end-to-end execution from public URL to final package in multiple installed clients; automated compatibility with other cue-awesome skills; external OKF consumers; full enterprise-local deployment; operational authorization and writeback; customer time savings or willingness to pay.

Before broad promotion, run a fresh source-to-answer task in the intended primary client with user-configured credentials and record installation, parse, host extraction, package checks, correction effort and returned billing facts. Preserve independent sources for evaluation rather than tuning against all release examples.
