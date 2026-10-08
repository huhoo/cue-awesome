# Verification record — cue-lead-pieces (measured with 0.3.x, 2026-10-07)

**Parsing path: every number in this record was measured with local parsing (PyMuPDF / pdftotext for cninfo PDFs, HTML page breaks for EDGAR) — what 0.4.0 calls the `local` fallback. The 0.4.0 primary path, Cue Omni Reader with `ingest`, has not been measured yet.**

This record lists what was measured, on what, and what it does not show. It is not a general accuracy benchmark. Numbers below are as measured; re-run `python3 scripts/test_skill_regression.py` for the current offline result.

## Setup

- Question (identical for every run, asked in Chinese): "As a credit officer, what are the 5 most important credit-deterioration signals for this company right now? Each must have verbatim source evidence and page."
- Companies: 24 listed companies — 10 A-share in distress, 10 US in distress (some already in Chapter 11), 4 healthy controls (2 A-share, 2 US). Filings from cninfo and SEC EDGAR, last ~12 months; both arms read the same files.
- Arms: A = bare Claude Code; B = the same Claude Code with this skill. One model (thinking off) for every model slot; each run's actual model was checked and runs that could not be checked were voided.
- One run per company per arm for the headline (valid answers: A 19, B 22; 7 voided or missing). 60-minute cap per run; an answer on disk at timeout was scored as is.
- Every quote was scored by the same `cue.py verify`: verbatim (cited page ±1, ignoring whitespace and punctuation), wrong source/page, edited, table restated, not in the source; plus "fabricated numbers" (a number in the quote that appears nowhere in the company's files).

## Results (version before 0.3.0)

| Sample | Arm | Answers | Quotes | Verbatim | Fabricated numbers |
|---|---|---|---|---|---|
| All 24 | A bare | 19 | 421 | 61% | 0 |
| All 24 | B skill | 22 | 443 | 95% | 0 |
| A-share 12 | A / B | 9 / 10 | 194 / 202 | 63% / 94% | 0 / 0 |
| US 12 | A / B | 10 / 12 | 227 / 241 | 59% / 96% | 0 / 0 |
| Healthy 4 | A / B | 2 / 3 | 46 / 45 | 41% / 96% | 0 / 0 |

95% intervals by company bootstrap: A 54%–67% verbatim (so 33%–46% not matching), B 91%–98%. Healthy controls: every claimed signal had source support (A 10/10, B 15/15).

Bare-agent mismatches split as: wrong source/page 7%, edited 16%, table restated 15%, not in the source 2% (shares of all quotes). Five bare-agent quotes (one US company) lost a "$digit" to shell expansion when the agent rewrote its answer file with a shell command; counting those five as matching leaves 38% not matching.

## 0.3.0 speed re-test

The 14 companies whose B runs still timed out after one retry in the run above; same question, filings, host and model; 0.3.0 and the previous version run interleaved at the same time, so endpoint load was shared.

| | 0.3.0 | previous version, same time |
|---|---|---|
| Runs completed / valid answers | 14 / 14 | 14 / 14 |
| 60-minute timeouts | 1 | 4 |
| Median wall time | 42.1 min | 45.4 min |
| Median model turns | 11.5 | 13 |
| Median time to first written answer | 29.1 min | 38.8 min |
| Quotes in final answers | 279 | 265 |
| Final answers verbatim | 100% | 98% |
| Agent draft verbatim before `--fix` | 98% (273/278) | — |
| Fabricated numbers | 0 | 0 |

## Limits

- One host (Claude Code) and one model; no claim for other models or hosts. One run per company per arm.
- The B arm was told to load the skill, which asks for `verify` before answering. The comparison is the same agent with and without this tool and workflow, not model capability.
- Scoring is programmatic: it checks that quotes can be found in the source, not that signals are right. Table checks only test that the numbers are on the same page, not row/column alignment. Fabricated numbers are string matches, so a number that happens to appear elsewhere passes (conservative).
- Sentences swapped in by `--fix` are the nearest original text chosen by the program; no person reviewed whether they still support the original claim.
- The 14-company re-test is the slowest subset, not a sample of all companies.
- Distressed companies were picked from public announcements. Not investment or credit advice.
