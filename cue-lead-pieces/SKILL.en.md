---
name: cue-lead-pieces
description: "读上市公司自己的披露文件(A股巨潮资讯/美股SEC EDGAR),产出带来源和页码的信用线索件,并逐句核对答案里的引文是否逐字出自所注页;--fix 改正注错的页码、把改过字的引文换回原句、删掉原文没有的。单一模型与宿主实测24家公司:裸Agent引文39%对不上,用本件流程95%逐字可查。适合:信用恶化信号、财报变化、要求逐字证据。不适合:投资建议、判断信号本身对错。Triggers: credit signals, quote verification, 10-K, 年报, 引文核对。"
license: MIT
version: "0.3.0"
slug: cue-lead-pieces
displayName: 财报引文逐字核对
summary: "从A股/美股公开披露建带页码的信用线索件,逐句核对引文是否逐字出自所注页,对不上的标出或改回;公开免费数据源,无需密钥。"
---

# cue-lead-pieces

*Full English translation of the Chinese-authoritative `SKILL.md`; the Chinese text governs where the two diverge. Agent loading follows `SKILL.md`.*

The agent thinks; Cue perceives. Turns a company's own filings (annual and interim reports and announcements, or 10-K / 10-Q / 8-K) into **traceable lead pieces**: object · why now · suggested action · verbatim source evidence (source + page).
Every quote in a lead piece is cut from the page text by the program, not written by a model; `verify` checks any quote programmatically, and `--fix` puts the quotes in an answer back to the original text.

Script: `scripts/cue.py` next to this file (Python 3.9+ standard library; A-share PDFs need PyMuPDF or the `pdftotext` command). Below, `CUE` is its full path and `DIR` is the company's data directory.

## Fastest flow (5–6 turns)

Every extra model turn means another wait for the model, so **use few turns and finish each one**:

0. If there is no data yet, fetch it (public, free, no key needed):
   - A-share (cninfo): `python3 CUE fetch DIR --cn 600606 [--months 12]`
   - US (SEC EDGAR): `python3 CUE fetch DIR --us LESL [--months 12]` (a CIK also works; set `CUE_SEC_UA="Your Name your@email"` first — SEC asks clients to identify themselves)
1. `python3 CUE brief DIR`
   One call returns the source catalog (source id, type, date, pages), the lead pieces (object, why now, action) and paste-ready verbatim evidence for each lead (JSON lines).
   **No need** to `ls`, `cat sources.json`, Read raw files or the leads JSON first.
2. Only if the lead evidence does not support a claim, **look it up in one command** (one or two rounds at most, not one page per turn):
   - find sentences by keyword: `python3 CUE find DIR "going concern" covenant --max 30` (Chinese works the same way, e.g. `持续经营 担保 逾期`)
   - read pages: `python3 CUE page DIR AR2025 54,196-198 ANN-2026-05-14-1 2` (several sources and pages at once)
3. Write `answer.json` once (evidence copied verbatim from the output above), then run **once**:
   `python3 CUE verify DIR --json answer.json --fix`
   It checks every quote and writes the corrections back to `answer.json`: wrong pages become the real page; edited quotes or table cells rewritten as sentences are replaced by the original sentence or table row; quotes not in the source (including made-up numbers) are dropped. The draft is saved as `answer.before_fix.json`.
   After the fix, report the answer; **do not re-check quote by quote or rewrite and re-verify**. Only if it warns that a signal has no checkable source evidence left, add one source sentence with `find` or drop that signal.

## Other commands

- `python3 CUE leads DIR`: lead pieces only (already inside `brief`; cached in `DIR/leads.json`). Cross-period comparison (risk wording added or dropped between the latest and the previous report of the same kind) and event extraction, then alignment of changes about the same object.
  Deterministic grouping by default, no model call; if `CUE_LLM_BASE_URL` / `CUE_LLM_API_KEY` / `CUE_LLM_MODEL` are set (any OpenAI-compatible endpoint), that model aligns changes across sources.
- `python3 CUE changes DIR`: cross-period comparison and event extraction only.
- Single quote: `python3 CUE verify DIR --quote "..." --source 10-Q_2026-06-30 --page 12`.

## Verdict levels (`verify`; `--fix` does not change them)

`verbatim` (found word for word on the cited page ±1, ignoring whitespace and punctuation), `verbatim_elsewhere` (in the source, but the source/page is wrong), `not_found` (with the nearest real text and its similarity, split into `edited` / `table_restated` / `numbers_differ` / `absent`).
Omitted parts of a quote may be joined with "……"; the pieces must appear in order on the same page.

## Rules

- answer.json shape: `{"signals":[{"rank":1,"title":"...","explanation":"...","evidence":[{"source":"source id","page":12,"quote":"verbatim text"}]}]}`.
- Quotes may only be **copied verbatim** from `brief` / `find` / `page` output — no edits, no joins, no translation; copy source ids and pages as given. Judgement goes in `explanation`; evidence holds source text only.
- Lead pieces are hints; ranking and judgement are yours. Use only the company's public filings; not investment or credit advice.
