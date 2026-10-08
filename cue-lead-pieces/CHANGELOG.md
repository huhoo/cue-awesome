### 0.3.1 — 2026-10-07

Fixed
- `fetch` with an unknown A-share code, US ticker or CIK used to exit with a Python traceback ending in `StopIteration`. It now prints one line on stderr and exits with code 2, e.g. `cue.py: error: unknown US ticker 'ZZZZQX': not in the SEC EDGAR ticker list (use the ticker, e.g. LESL, or the numeric CIK)`. HTTP 4xx responses (except 429) are no longer retried.
- Regression test `test_unknown_code_one_line_error` covers all three cases offline.

### 0.3.0 — 2026-10-07 (first release in this repository)

Changed
- Fewer, fuller agent turns: `brief` returns the source catalog, lead pieces and paste-ready verbatim evidence in one call; `find` returns paste-ready sentences for several terms; `page` reads several sources and page ranges in one call (compacted, capped at 12 pages).
- `verify --json answer.json --fix` repairs the answer in place: wrong page → real page; edited quote (similarity ≥ 0.5) → the original sentence; table cells rewritten as a sentence → the original table rows (tries page p, p+1, then both); not in the source or numbers that differ → dropped. The draft is saved as `answer.before_fix.json`, and a warning is printed when a signal is left without evidence. Verdict levels are unchanged.
- Model alignment in `leads` is optional and provider-neutral (`CUE_LLM_BASE_URL` / `CUE_LLM_API_KEY` / `CUE_LLM_MODEL`, any OpenAI-compatible endpoint); without them a deterministic grouping is used. SEC contact via `CUE_SEC_UA`.
- Added the offline regression test `scripts/test_skill_regression.py` (frontmatter, verdict levels, `--fix`, `page` / `brief`).

Verified (measured; one host, one model; details in `references/verification.md`)
- 24 listed companies (12 A-share, 12 US, including 4 healthy controls), one run per company per arm, same question and filings. Bare agent: 61% of 421 quotes verbatim on the cited page, 39% not (95% interval 33%–46%). With the skill: 95% of 443 (91%–98%). Measured with the version before 0.3.0.
- 0.3.0 on the 14 previously slowest companies, run interleaved with the old version: final answers 100% of 279 quotes verbatim (agent draft before `--fix` 98%, 273/278); 60-minute timeouts 1 vs 4; median wall time 42.1 vs 45.4 minutes.
- Numbers that appear nowhere in the source: 0 in every arm above. Healthy controls: every claimed signal had source support (10/10 bare, 15/15 with the skill).
- Caveats: verbatim means found on the cited page ±1 ignoring whitespace and punctuation; it does not judge whether a signal is right. Sentences swapped in by `--fix` were not reviewed by a person. Five bare-agent quotes lost a "$digit" to shell expansion while the agent rewrote its answer file; counting them as matching still leaves 38% not matching. One model and one host only; results may differ elsewhere.
- Known issue: for a few companies the `brief` output exceeds the host's single-output limit and is saved to a file, costing the agent one more turn.
