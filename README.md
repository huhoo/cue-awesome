# cue-awesome

**[English](README.md) · [中文](README.zh-CN.md)**

A personal collection of self-built agent skills for WorkBuddy / Cue. Each subdirectory is a standalone skill — copy the one you need and use it on its own.
The data legs are served through the Cue channel: configure one API key and the open domains in the live catalog are ready to use - no data source to supply here and no data layer to build here. Domains that are not open are not included; the domain list and the tool surface follow the live catalog (`GET https://cuecue.cn/api/mcp-catalog`).

## Try a public-document knowledge workflow

**What changed, which figures are comparable, and where is the evidence?** [`cue-omni-ontology`](cue-omni-ontology/README.en.md) turns public reports and announcements into evidenced answers, a change brief, and a knowledge package you can update with the next release. Start with financial disclosures, supplier information, or product updates.

```bash
npx skills add huhoo/cue-awesome --skill cue-omni-ontology
```

Then ask: **“Use cue-omni-ontology with its bundled demo. Show what the new release adds, where claims conflict, and the source excerpts.”** The bundled demo needs no API key and makes no network calls. Real document parsing uses the separately configured official Cue Omni Reader.

[Quick start and repeat-use prompts](cue-omni-ontology/README.en.md) · [Fresh Microsoft disclosure run](cue-omni-ontology/assets/public-example/live-preview.md) · [Verified scope and limits](cue-omni-ontology/references/verification.md)

## Skills

| Directory | Name | Version | What it does |
|---|---|---|---|
| [`cue-omni-ontology/`](cue-omni-ontology/) | cue-omni-ontology | [frontmatter](cue-omni-ontology/SKILL.md) | 从公开资料建可追溯业务知识包：逐字证据锚、口径、跨期变化与变化简报；可选数字包校验数字逐字出处；音视频限本地小段/切片。工具不判断真伪、不预警，须人工核证据。 |
| [`cue-lead-pieces/`](cue-lead-pieces/) | cue-lead-pieces | [frontmatter](cue-lead-pieces/SKILL.md) | 用 Cue Omni Reader 解析公司披露，建带页码的信用线索件，逐句核对引文是否逐字出自所注页±1，对不上的标出或改回。 |
| [`journal-draft/`](journal-draft/) | journal-draft | [frontmatter](journal-draft/SKILL.md) | 企业内刊、客户通讯、投资人信的成稿底稿：提纲→成稿→引证逐条回源→版面与编辑定位多道门禁，流程留痕可自证。 |
| [`long-doc-translation/`](long-doc-translation/) | long-doc-translation | [frontmatter](long-doc-translation/SKILL.md) | 外文长篇（专著/古籍/档案/译著参考）全文中译流水线：主稿+阅读版+逐段备查+术语总表，拿不准的进存疑清单不硬翻。 |
| [`competitive-brief/`](competitive-brief/) | competitive-brief | [frontmatter](competitive-brief/SKILL.md) | 竞对对比简报：先证据表后简报，每格带来源、日期与 fact/inference/opinion 级别；一页内结论先行给建议，缺口如实列明。 |
| [`cn-earnings-note/`](cn-earnings-note/) | cn-earnings-note | [frontmatter](cn-earnings-note/SKILL.md) | A股/港股财报深度点评初稿：四期差异、科目勾稽、预告对照；数字行按包内规则逐条要证据级标注，评级判断位 [待人工]。 |
| [`catalyst-calendar/`](catalyst-calendar/) | catalyst-calendar | [frontmatter](catalyst-calendar/SKILL.md) | 未来三个月有哪些确定日子要盯：业绩披露、解禁、股东大会——入表只认已披露含明确日期或法定可推导两种，不猜不判涨跌。 |
| [`tear-sheet/`](tear-sheet/) | tear-sheet | [frontmatter](tear-sheet/SKILL.md) | 公司一页纸：五段形制机检钉死顺序——近四期双口径、事件≤4、风险1-3 只写直查命中，观点区三行 [待人工] 留白。 |
| [`sector-overview/`](sector-overview/) | sector-overview | [frontmatter](sector-overview/SKILL.md) | 行业景气全景（A股口径）：六节固定形制，分析维度按行业动态生成 2–4 个——每个判断词当场答得出「凭什么：哪条序列、哪个口径、截至哪天」。 |
| [`dd-checklist/`](dd-checklist/) | dd-checklist | [frontmatter](dd-checklist/SKILL.md) | 给一家 A 股公司拉一份公开信息风险清单：查得到的逐条带披露锚，查不到的逐类写明原因；不给投资结论，不出法律意见。 |
| [`civil-appeal-turnaround/`](civil-appeal-turnaround/) | civil-appeal-turnaround | [frontmatter](civil-appeal-turnaround/SKILL.md) | 一审败诉后建二审作战体系：判决逆向、证据逐字比对、请求权阶梯、台账与文书包。不是法律意见，条号递交前核对。 |
| [`cn-contract-clauses/`](cn-contract-clauses/) | cn-contract-clauses | [frontmatter](cn-contract-clauses/SKILL.md) | 一份合同拆成逐条要点与需盯条款清单：每条挂 [S#] 与页码行号，七类逐类点名，不出法律意见、不判效力。 |
| [`cn-link-to-note/`](cn-link-to-note/) | cn-link-to-note | [frontmatter](cn-link-to-note/SKILL.md) | 一条链接进来、一条带出处的笔记出去：要点逐条挂 [S#]，原话逐字比回那一页那一行，缺口点名，判断留人工。 |
| [`cn-research-brief/`](cn-research-brief/) | cn-research-brief | [frontmatter](cn-research-brief/SKILL.md) | 把多份中文来源整理成一份逐条挂源的速览：每条发现带一条可回查来源与检索日，缺的点名，判断留人工。 |
| [`cn-resume-jd-fit/`](cn-resume-jd-fit/) | cn-resume-jd-fit | [frontmatter](cn-resume-jd-fit/SKILL.md) | 一份简历对一枚 JD 的双向核对：要求逐条挂到简历原话，缺口分两栏点名，不排先后、不下录用结论。 |
| [`event-brief-cn/`](event-brief-cn/) | event-brief-cn | [frontmatter](event-brief-cn/SKILL.md) | 把一份A股临时公告变成五段可核对速读卡：逐字关键数带出处、影响链候选、同类对照、待核清单；评级目标价一律[待人工]。 |
| [`event-risk-scan/`](event-risk-scan/) | event-risk-scan | [frontmatter](event-risk-scan/SKILL.md) | 对一家公司跑处罚/监管措施/对外担保三源扫描卡：逐条带出处与日期，未达面明写未达；不评整体风险、不算违约概率。 |
| [`ic-memo-cn/`](ic-memo-cn/) | ic-memo-cn | [frontmatter](ic-memo-cn/SKILL.md) | 给一家公司起草投决备忘录：七个结构节，每条数字带官方出处与定位，缺数点名不填空；bull 与 bear 并陈，不评级不表决。 |
| [`meeting-minutes-cn/`](meeting-minutes-cn/) | meeting-minutes-cn | [frontmatter](meeting-minutes-cn/SKILL.md) | 把会议录音变成带时间锚的分段纪要：逐字句挂 mm:ss，话题归段自标，决策与待办逐条回查原话；边界内工作，不承诺实时。 |
| [`omni2docx/`](omni2docx/) | omni2docx | [frontmatter](omni2docx/SKILL.md) | 把 Omni 解析结果重建为保真 .docx、展示 HTML、汇报 PPT：源页分页、真标题目录、溯源标注还原，按场景制式排版。 |
| [`paper-study-cn/`](paper-study-cn/) | paper-study-cn | [frontmatter](paper-study-cn/SKILL.md) | 把一篇论文变成可核对的研读卡：论点-方法-数据-结论逐句挂页锚，复现清单，引用网络，综述骨架与待核清单；不代写、不编引文。 |
| [`skill-review-cn/`](skill-review-cn/) | skill-review-cn | [frontmatter](skill-review-cn/SKILL.md) | 装之前先给一枚 skill 体检：五面逐条挂原文与检索日，缺的点名，装不装留人工。 |
| [`watchlist-digest-cn/`](watchlist-digest-cn/) | watchlist-digest-cn | [frontmatter](watchlist-digest-cn/SKILL.md) | 对你维护的自选清单跑每日增量：回购/股权激励/两融标的与折算率/公告/监管措施五腿，逐条带出处与 asof；无新增也明写，不评风险不预测。 |

## Financial-research suite roadmap

The financial-research skills are a Cue-native rewrite of the methodology base in **anthropics/financial-services** (Apache-2.0). We re-implement rather than copy — the data layer is entirely replaced by the three Cue channels: **deep research (cue-research) · data-MCP domains (Cue) · document parsing (omni-reader)**. Attribution details in [NOTICE.md](NOTICE.md).

> **Status.** The skills this repository publishes are exactly those listed in the Skills table above — the current listing is the authority, and it makes no claim about any channel's index; this roadmap covers the financial-research subset among them. `cn-earnings-note` completed its P1 end-to-end runs (acceptance records in its `CHANGELOG.md`, under Verified). `catalyst-calendar`, `tear-sheet` and `sector-overview` passed adversarial final review on 2026-09-21 and each now has one real run on record: catalyst — a full-window multi-subject run with the evidence chain enforced, forward rows sparse by domain reality, and the statutory-deadline derivation attempted then refused (the statute channel returned no source text in that run); tear-sheet — a pre-meeting brief at the contract's subject cap, one pass; sector-overview — building materials, half-journey: volume/price lines each carry their stated scope and source anchor, competing asphalt quotes left un-arbitrated by design, while the industry price/volume domain expansion is still pending (the macro domain carries no domestic industry series). **Measured counts live in each package's own `README.md` status section and are deliberately not repeated here.** Current version numbers live in each package's `CHANGELOG.md`, not in this sentence. Everything else in the roadmap is scoped direction: **not built, not available, and nothing beyond the table above is promised as shipped.**

### Built — the vanguard (reviewed; first real runs on record)

- **Earnings deep-dive — [`cn-earnings-note/`](cn-earnings-note/)**: A-share / HK-share earnings deep-dive notes; P1-verified end to end (run and subject counts in this package's `README.md` status section). Version per this package's `CHANGELOG.md`. Full one-liner in the Skills table above.
- **Catalyst calendar — [`catalyst-calendar/`](catalyst-calendar/)**: full-window run on record with the evidence chain enforced — forward rows sparse by domain reality, each empty section carrying an attribution line, and a statutory-deadline derivation attempted then refused; adversarial review closed. Counts live in this package's `README.md` status section, not here. Version per this package's `CHANGELOG.md`.
- **Tear-sheet — [`tear-sheet/`](tear-sheet/)**: pre-meeting run at the contract's subject cap on record, one pass; adversarial review closed; guard samples all green (counts per this package's `README.md` status section). Client-ready one-pager, five fixed sections, line-level anchors.
- **Sector overview — [`sector-overview/`](sector-overview/)**: building-materials half-journey on record — volume/price lines each carry a stated scope and their source anchor, competing asphalt quotes deliberately left un-arbitrated; adversarial review closed, domestic industry price/volume domain still pending. The single authoritative count and its scope live in this package's `README.md` status section. Trend judgements require same-line comparable-series anchors.
- **DD-checklist — [`dd-checklist/`](dd-checklist/)**: two review rounds came back blocked first, were fixed question-by-question against §v2, and the follow-up review passed (full trail in git log and this package's CHANGELOG); the sample bank is whatever `scripts/fixtures/` runs green today (counts live in the reviewer's mapping table, not repeated here). **Real-subject end-to-end runs on record (all six parameters, eight gates passed at the time); §v2-16② re-scan with the current gate fails both historical artifacts (under-booked domains, `DD-OMISSION`; the wide-window run also `DD-COVERAGE`) — the artifacts are kept unchanged (that defect is tracked internally), and the PASS credential under the current gate is now on disk — a same-issuer `mna` run at a 12m window, six parameters, exit 0; the verified scope and the still-unverified tiers are stated in this package's `README.md` status section and are not repeated here.** Version per this package's `CHANGELOG.md`.

### Planned — batch 2 (direction set, not yet built)

Two items formerly listed here are now built and reviewed — `sector-overview` and `tear-sheet` (see the Built section above). What remains scoped here, none of it available yet: **initiating coverage** (first-coverage note; valuation/model steps hand off to a human as `[待人工]`), **thesis tracker** (periodic re-run of a stored thesis against fresh public disclosure), **funding digest** (primary-market raise summary from IPO and disclosure domains). Each depends on data paths that are either already listed as available or explicitly deferred below; none is promised as shipped.

### Deferred (blocked, not built)

- morning-note, idea-generation / screening, comps-analysis — held until the required data domains are live; the current live set is whatever the server-side catalog returns (`GET https://cuecue.cn/api/mcp-catalog`), and nothing here is a promise.

### Excluded by structure

- Excel-model skills, fund-administration (private internal books), and anything that depends on private data such as accounts or CRM are out of scope — Cue channels are a complement to these, not an internal-ledger or valuation-model engine.

## Install

All eleven skills, `cue-omni-ontology` and `cue-lead-pieces` included, ship as one ZIP asset each on the release page below — install any of them with the same three steps; copying a skill's directory out of this repository is the other way in.

The release list is <https://github.com/huhoo/cue-awesome/releases>; this sentence deliberately pins no version number, because a number written here goes stale the moment the next release is cut. Check the release page and the installed skill's frontmatter.

```bash
curl -L -o tear-sheet.zip https://github.com/huhoo/cue-awesome/releases/download/v2026.10.23/tear-sheet.zip
mkdir -p ~/.workbuddy/skills/tear-sheet
unzip -o -d ~/.workbuddy/skills/tear-sheet tear-sheet.zip
```

Replace `tear-sheet` in those three lines with the skill you want (catalyst-calendar / civil-appeal-turnaround / cn-earnings-note / competitive-brief / cue-lead-pieces / cue-omni-ontology / dd-checklist / journal-draft / long-doc-translation / sector-overview / tear-sheet) — each line is complete as it stands, nothing to escape or quote.
To choose from all current skills: `git clone https://github.com/huhoo/cue-awesome.git`, then copy the skill folders you need into `~/.workbuddy/skills/`.
Third route, the skills CLI: `npx skills add huhoo/cue-awesome` (lists all) / `npx skills add huhoo/cue-awesome --skill journal-draft` (one).
Fourth route, the ClawHub CLI (the store-side form, documented as `install @owner/slug`): `clawhub install @huhoo/cue-journal-draft`. The slug there is `cue-` plus the directory name, which is not the string the skills CLI takes - the two forms are not interchangeable in that argument slot.
On Windows the destination is `C:\Users\<username>\.workbuddy\skills\` — same three steps, same file names.
After installing, `cd` into the skill folder and run the self-check commands its own README prints; each skill ships them, this page deliberately does not copy them.

## Language

Docs are bilingual: `README.md` (English) / `README.zh-CN.md` (Chinese). Skill instruction files follow the same convention — see [`docs/i18n.md`](docs/i18n.md).

## Contributing

Read [`CONTRIBUTING.md`](CONTRIBUTING.md) before opening a PR: commit format, the checklist for adding a skill, and what must never be committed. The gate runs on every push and PR:

```bash
python scripts/check_skills.py                                # structure, frontmatter, changelog shape
python scripts/check_public_hygiene.py --selftest             # public-surface hygiene gate proves its own guard samples
python scripts/check_public_hygiene.py                        # five-ban scan of every published surface
```

The hygiene gate's counts are a **working-tree snapshot, not a stable quantity**: they move with every edit in the tree, so cite them with a timestamp or not at all. Its finding lines carry stable codes instead (`H-TICKET`, `H-PATH`, `H-POINTER`, `H-STATE`, `H-DATE`, `H-ATTRIB`).

New skill proposals: open an issue with the **new skill proposal** template.

## Notes

- This is a **personal** collection. It is not affiliated with the official Cue skills monorepo [sensedeal/cue-skills](https://github.com/sensedeal/cue-skills), is not a subset of it, and is not merged into it.
- `LICENSE.md` / `NOTICE.md` apply to the whole repository.
- Build artifacts (`dist/`, `*.zip`) are not committed; release packages are described in each skill's manifest / CHANGELOG.
