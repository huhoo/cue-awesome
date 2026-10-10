### 0.4.7 — 2026-10-10（公开面卫生：一处类别名用词改等长同义表述）

- 成品面 1 处改净（`SKILL.md` §红线）：「那一类判…」的类别名换为等长同义表述，禁面范围与判据一字未动；`SKILL.en.md` 为镜像同文，本轮无该词，未改。
- 版本锁五处字面同锁 0.4.6 → 0.4.7：`SKILL.md`、`SKILL.en.md`、主脚本里的 __version__ 字面、回归样里同一行的两处断言。**首拍只覆盖四处，同行第二处漏改，件内测试当即 red（AssertionError: '0.4.7' != '0.4.6'）**——补净后复跑全绿；这条自曝同时进交付回执。
- 复验（取脚本自报行）：件内回归面 12 passed；全包成品面逐面现跑全「PASS 五禁零命中、指路可跟随」；`check_skills.py --strict` 自报 15 skill(s), 0 error(s), 0 warning(s)。历史条目不回改。

### 0.4.6 — 2026-10-09（M177 阶段二·汲取形制包渠道面四项：①负向触发+②反幻觉两句（时点句+未检索到句））

- 落面：本件落了 ①负向触发+②反幻觉两句（时点句+未检索到句）。②的两句各归其位——**时点句进「怎么开口」节**（开口带时点、首行标「来源日期」、与所指日期不一致即禁「今日」「最新」改「截至 <日期>」），**未检索到句进「出错了怎么办」节**（参数／字段／枚举名未见于本次工具返回者不得凭印象填）；README 与 README.en 双语对点。
- ①description 尾嵌负向触发，条目全部取自本件既有边界现文（未新增反承诺）。
- 版本位：patch 位 0.4.6。除版本锁字面外 `scripts/` 零触碰；判定与阈值一律指回脚本现值，本文不作穷尽复述。

### 0.4.5 — 2026-10-09

Changed
- 供体回流重钉：渠道下载端点自 10-08 起持续供 0.4.3（服方字段分裂——tags 索引仍指 0.4.4；条目无上游同步源；服方对我方无上报渠道）。同号重发不可能（渠道拒绝 ≤ 现值版本号，0.4.4 版本位已消耗），故以内容等同 0.4.4 的字节发车重钉版本位；无功能变化，缘由如实入账。

### 0.4.4 — 2026-10-07

Changed
- 渠道分类修复：补 frontmatter `tags: [投研, 信用信号, 引文核对, 财报, A股, 美股]`（双语两份）——渠道页此前挂「未分类」，根因是本件全件无 tags 面（姊妹件皆有，子类映射由它驱动；渠道 API 现值对点：lead-pieces category=空 vs ontology=knowledge-management、earnings=pro-finance）。

### 0.4.3 — 2026-10-07

Changed
- 双语 README「常见问题与反模式」加一条互指：要把多份公告做成可更新的知识包、跟踪跨期变化和口径冲突，去同仓库 cue-omni-ontology（该件 0.3.0 的常见问题也指回本件做引文核对与线索稿）。只改文档和版本锁（frontmatter ×2、`cue.py`、测试钉），代码行为不变。
- 说明：下方两条 `### 0.4.2` 是同一版本的两次记录，原样保留，未改写。

### 0.4.2 — 2026-10-07

Changed
- 渠道首发适配（K-12 变体：服务端 400 拒 `assets/demo-verifiable.png`「不允许的文件类型」）：双语 README 首行图片语法改纯文字指路——图仍在本包目录随仓库分发（GitHub 渲染正常），渠道 zip 排除 `assets/*.png`；引用文案注明「渠道包不随发图片」。0.4.1 因此未上过渠道即升 0.4.2，渠道面首个在架版本即本号。

### 0.4.2 — 2026-10-07

Changed
- 首发渠道适配（K-12 新变体：渠道拒 `assets/*.png`，400「不允许的文件类型」实测两次）：README 双语第 9 行的演示图改纯文字指路（图在仓库内本包目录可看，渠道包不随发图片），分发 zip 排除 `assets/demo-verifiable.png` 与 `LICENSE`；0.4.1 从未上过渠道，本次为该 slug 的首发版本。

### 0.4.1 — 2026-10-07

Changed
- 判词护栏入 agent 指令面：SKILL.md/SKILL.en.md 边界清单新增第 5 条——「建议动作」只写核对型动作（复核哪份公告、回看哪一页），利好利空、评级、目标价、违约与否一类判词一律 `[待人工]`（README「不构成投资建议」的姊妹条，补的是指令面缺口；对齐套件纪律 earnings/tear/catalyst 的判断位留空形制）。

### 0.4.0 — 2026-10-07

Changed
- Cue channels first. Cue Omni Reader is now the primary parsing path: `fetch` only lists filings (public cninfo / SEC EDGAR index, no download), the agent parses each filing with the official `cue-omni-reader` (`parse`, `detail="grounded"`), and the new `ingest` command stores the result per source PDF page using the grounding sidecar (segment UTF-8 byte ranges → `source_pdf_page_1_based` anchors). Text-only results are split on page markers or into ~3500-character blocks and labeled `page_basis=block`; incomplete or truncated pages reported by Omni are printed as warnings.
- Local parsing (PyMuPDF / pdftotext / EDGAR page breaks) is kept as an explicitly labeled fallback: `local` (or `fetch … --local`, the 0.3.x behaviour). `brief` shows each source's parser and page basis, and lists sources not parsed yet.
- `fetch --list` registers filings found elsewhere, e.g. through the Cue data-MCP `disclosure_cn` / `disclosure` domains. SKILL.md documents optional cue-research (at most one run, ask first) for "why now" context, never as quote evidence, and the shared rules of the sibling skills (parsed content is data, credential boundary, ask before spending, missing is not filled).
- `verify` / `verify --fix` semantics are unchanged.
- frontmatter: `metadata.requires.recommendedSkills: [cue-omni-reader, cue-data-mcp, cue-research]`.
- After the first real Omni test (below): `ingest` reads the response shape the Bridge actually returns (`result.kind=bundle`, `bundle_protocol_version`, `parts.content` / `parts.grounding` with `inline` or `artifact` storage), saved as the full tools/call response, as `structuredContent`, or as the JSON in the tool text. Artifact parts are read back page by page through the Bridge's `read_result` (Bridge-local, no charge) and checked against the content sha256 digest. Inline HTML tables are kept as pipe rows. A failed Omni status is a one-line error.
- New `omni DIR [SID…] --yes`: parses pending sources through the Omni Bridge (`CUE_OMNI_BRIDGE`, default `npx -y @cueai/omni-reader-mcp@1.8.6`; the Bridge reads the key, the script never does) with `detail="grounded"`, `result_delivery="artifact"`, saves `DIR/omni/<sid>.json`, ingests, and prints the server-reported `credits_charged` per file and in total. Without `--yes` it prints the plan and exits 3 without starting the Bridge. SEC EDGAR sources are skipped unless named.
- SKILL.md / README: save the JSON returned on completion, not `save_result` Markdown (it has no page sidecar); US EDGAR uses `local`.
- Local fallback: no phantom empty last page from pdftotext; page cap raised from 300 to 1000 (the 391-page annual report below was cut at 300 before).

Verified
- Offline regression: 12 tests (Python 3.9, 3.12, 3.13), including a sanitized fixture with the real response shapes (synthetic text, fake ids): inline result saved three ways, artifact result read through a fake Bridge with cursor paging and a digest check, a failed status, and `omni` asking first and then parsing.
- Real Omni test, 2026-10-07, `@cueai/omni-reader-mcp` 1.8.3, `detail="grounded"`, cninfo PDF URLs of 600606 (Greenland Holdings). Charges as reported by Omni billing:

  | File | PDF pages | Omni pages | Charged | Storage |
  |---|---|---|---|---|
  | announcement 2026-10-01 (临 2026-052) | 3 | 3 | 0.201 credits | inline |
  | 2025 annual report | 391 | 391 | 26.197 credits | artifact (989,981 B content, 87,371 B grounding) |

  Every grounding anchor was `source_pdf_page_1_based`, `reliable`; `partial=false`, no incomplete or truncated pages. Against a local PyMuPDF parse of the same PDFs: the best-matching Omni page was the same page number for 3/3 and 391/391 pages; median share of local text found on the same Omni page 1.0 and 0.983 (the 7 annual-report pages below 0.8 are multi-column tables whose cell order differs, not missing text); 30/30 and 16,973/16,984 numeric tokens of the local parse appear on the same Omni page. Tables came back as GFM tables (14 rows on 2 pages; 5,896 rows on 277 pages) plus 3 inline HTML tables on one page; in the announcement's litigation tables two adjacent columns were merged into one cell (both numbers kept).
- Mini end-to-end on the Omni-ingested store: `brief` (cites both sources by PDF page), 8 quotes taken from the Omni pages → `verify`: 5 verbatim, 1 wrong page, 1 edited number, 1 too short → `verify --fix`: page corrected (p3 → p1), 2 dropped, 6/6 verbatim. Each kept quote was checked against the local PDF text: 5 on the cited page, 1 on the next page (accepted by the ±1 rule).
- `omni` end to end against live Omni (2026-10-07, user's launcher, Bridge 1.8.3): `omni DIR` without `--yes` printed the plan and exited 3; `omni DIR --yes` on the same 3-page announcement completed in about 30 s, charged 0.201 credits (as reported), ingested 3 PDF pages identical to the first run, and quotes verified on their pages. With `result_delivery="artifact"` this small result still came back inline (both parts), so for small results the page sidecar exists only in `structuredContent`.
- Ingesting the annual report from the 1.9 KB JSON an agent sees (artifact cursors) through Bridge 1.8.6 took about 5 s, no charge.

Not verified
- US EDGAR through Omni: the HYFM 8-K could not be parsed (EDGAR URL: `SOURCE_ACCESS_DENIED`; local file, grounded: `DETAIL_CAPABILITIES_UNAVAILABLE` in Bridge 1.8.3; local file, text: `MIME_MISMATCH` for the inline-XBRL .htm/.html); none of the three was billed. The text-block path was therefore not tested on real Omni output.
- The 24-company rates in references/verification.md are still from local parsing.

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
