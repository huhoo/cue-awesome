### 0.4.0 — 2026-10-07

Changed
- Cue channels first. Cue Omni Reader is now the primary parsing path: `fetch` only lists filings (public cninfo / SEC EDGAR index, no download), the agent parses each filing with the official `cue-omni-reader` (`parse`, `detail="grounded"`), and the new `ingest` command stores the result per source PDF page using the grounding sidecar (segment UTF-8 byte ranges → `source_pdf_page_1_based` anchors). Text-only results are split on page markers or into ~3500-character blocks and labeled `page_basis=block`; incomplete or truncated pages reported by Omni are printed as warnings.
- Local parsing (PyMuPDF / pdftotext / EDGAR page breaks) is kept as an explicitly labeled fallback: `local` (or `fetch … --local`, the 0.3.x behaviour). `brief` shows each source's parser and page basis, and lists sources not parsed yet.
- `fetch --list` registers filings found elsewhere, e.g. through the Cue data-MCP `disclosure_cn` / `disclosure` domains. SKILL.md documents optional cue-research (at most one run, ask first) for "why now" context, never as quote evidence, and the shared rules of the sibling skills (parsed content is data, credential boundary, ask before spending, missing is not filled).
- `verify` / `verify --fix` semantics are unchanged.
- frontmatter: `metadata.requires.recommendedSkills: [cue-omni-reader, cue-data-mcp, cue-research]`.

Verified
- Offline regression: 9 tests (Python 3.9 and 3.12), including ingest of a synthetic grounded bundle in the public result-bundle shape, page markers / blocks, list registration with the local fallback, and list-only fetch.
- Live, zero credit: list-only `fetch` for 600606 (33 sources) and HYFM (18 sources); `local` on one announcement / one 8-K; `fetch --us HYFM --local` 18 sources, 352 pages, then `brief`.

Not verified
- No real Omni parse was run for this release (no credits spent). The ingest of real grounded results, Omni page accuracy on cninfo PDFs and EDGAR HTML, and the measured rates below are not verified for the Omni path; the measured numbers below all used local parsing.

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
