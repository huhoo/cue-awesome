# Verification record — 2026-09-28, v0.2.0

This record distinguishes executed code, synthetic host tasks and saved parser output. It is not a general extraction accuracy report.

| Surface | Executed result | Limits |
|---|---|---|
| Offline boundary suite | 46 tests pass (`python3 -B scripts/test_ontology.py`) | Synthetic fixtures; no live parser, no LLM accuracy or enterprise IAM claim |
| Independent host use | A separate agent followed SKILL.md using newly supplied fictional Cedar Instruments releases; built/updated two versions and answered business questions | Supplied parsed synthetic text; no live Omni invocation and no claim of cold client onboarding |
| Independent query outcomes | Unscoped Q1 `needs_scope`; statutory/adjusted Q1 each `found`; restated Q4 `conflict`; alleged Beacon discontinuation `not_found` | One task, not a statistical generalization benchmark; machine assertions were not marked human-reviewed |
| Public-source replay | Existing grounded Omni output for two Tencent 2026 quarterly releases successfully repackaged and updated | Saved earlier output and seeded rule-extracted claims; not a fresh model extraction or fresh parser run |
| Replay counts | 2 sources, 1 entity, 18 metric definitions, 96 source assertions, 83 fact scopes; second batch adds 36 facts and 13 supporting assertions | Definitions here group metric labels; bases/qualifiers live on facts, so counts differ from the earlier prototype's 23 combined metric/basis concepts |
| OKF exporter | Public replay produced 18 concept files plus navigation | Core Markdown/YAML subset only; no external consumer import verified |

The independent host task and public replay below were originally executed with v0.1.0; the v0.1.1 audit adds eight offline regressions. Version 0.1.1 fixes numeric-spelling conflicts, scope selection, boolean qualifier matching, structured errors for malformed assertions and unsafe Markdown rendering; it exposes conflict IDs/validity in reports. Schema remains 0.1.0.

Scrubbed machine summaries: [forward-results.json](forward-results.json), [replay-results.json](replay-results.json). Public source metadata and hashes: [sources.json](../assets/public-example/sources.json). Full reports/parsed sources are not redistributed with this skill.

The earlier parser run used official Omni Reader Bridge 1.8.4 and native page anchors. The new package preserves the exact stored text hashes. The original v0.1 release added **zero** live parse calls. Version 0.2.0 has a separately recorded fresh run and its returned billing facts; no general speed or cost claim is inferred.

Not established: arbitrary document-family extraction accuracy; fresh installation and end-to-end execution in multiple third-party clients; automated compatibility with other cue-awesome skills; external OKF consumers; full enterprise-local deployment; operational authorization and writeback; customer time savings or willingness to pay.

Version 0.2.0 adds a [fresh source-to-answer run](live-verification.md) on two Microsoft public releases: 21 selected claims, all 11 baseline claims preserved. The installed development environment completed official parsing, host extraction, preparation, updates, evidence queries and a generated brief. Fresh installation in multiple third-party clients and user time-savings remain untested. Preserve independent sources for evaluation rather than tuning against all release examples.

HTML browser checks: the local browser binary was unavailable, and the configured cloud browser rejected local-file navigation under its URL policy. Real-browser interaction and mobile layout are therefore not certified in this environment. HTML generation, safe data embedding, excerpt limits and package workflows have automated coverage; the Markdown output remains a usable fallback.

Independent 0.2 forward use: a fresh agent received two previously unused fictional Vela Components releases and used quote preparation → build → update → validate → evidence queries → brief. It produced 9 assertions / 8 fact scopes, retained all 4 baseline assertions, separated September standard/pilot prices, preserved one June delivery-estimate conflict and left product certification unknown. No command blockers occurred. Human-readable relation names and Markdown/JSON briefs were inspected; browser rendering was not. The observed workflow still requires host judgment for disclosure dates, explicit corrections and absent certification evidence.
