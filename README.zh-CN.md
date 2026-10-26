# cue-awesome

**[English](README.md) · [中文](README.zh-CN.md)**

个人自研的 WorkBuddy / Cue 技能集合仓。每个子目录是一个独立 skill，可单独复制使用。
数据腿由 Cue 通道提供：配置一把 api key，即可接入 catalog 现值所列的开放域，无需自备数据源或自建数据层。不含未开放域；域清单与工具面以 catalog 现值为准（`GET https://cuecue.cn/api/mcp-catalog`）。

## 先试一次公开资料知识更新

**新材料改变了什么？哪些数字能比较？依据在哪里？** [`cue-omni-ontology`](cue-omni-ontology/README.md) 把公开报告和公告变成带证据的回答、变化简报，以及下次能继续更新的知识包。可以从财报披露、供应商资料或产品更新开始。

```bash
npx skills add huhoo/cue-awesome --skill cue-omni-ontology
```

安装后对 Agent 说：**“使用 cue-omni-ontology，先用自带样例演示：加入新材料后，哪些事实新增、哪些冲突、依据在哪里？”** 自带演示无需 API key，不发起网络请求。真实资料解析需另行配置官方 Cue Omni Reader。

[上手与复用指令](cue-omni-ontology/README.md) · [微软公开披露新解析实测](cue-omni-ontology/assets/public-example/live-preview.md) · [验证范围与边界](cue-omni-ontology/references/verification.md)

## Skills

> 「用途」列取自各包 frontmatter 的 `summary`,为**逐字现值**——单一权威字段,原样呈现,本表不另撰写、不改写。

| 目录 | Name | 版本 | 用途 |
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

## 金融研究套件路线图

金融研究类 skill 是对 **anthropics/financial-services**（Apache-2.0）方法论基座的 Cue-native 重写。我方为重实现而非拷贝——数据层完全替换为 Cue 三层通道：**深研（cue-research）· 数据 MCP 域（Cue）· 文档解析（omni-reader）**。出处详见 [NOTICE.md](NOTICE.md)。

> **状态：** 本仓对外发布的 skill 以上方 Skills 表现列为准（现列即权威，不据以承诺任何渠道收录）；本节路线图讲的是其中的金融研究子集。`cn-earnings-note` 已完成 P1 端到端实跑（验收记录见本包 `CHANGELOG.md` 的 Verified 段）。`catalyst-calendar`、`tear-sheet`、`sector-overview` 已于 2026-09-21 通过对抗审终判，且各有一次真实运行在案：催化剂日历——满窗多主体、证据链强制，前瞻稀疏属域面实况，法定期限推导已尝试并当场拒推（该次 statute 通道未取回原文）；公司一页纸——打满主体上限的回客速览、一轮通过；行业景气全景——建材半程，量价逐行带口径与来源锚、两个沥青报价并列不仲裁（设计行为），国内行业量价域仍未开放。**实测计数一律以各包 `README.md` 状态段为唯一权威，本文件不重抄。**版本号以各包 `CHANGELOG.md` 现值为准，不写进本句。路线图其余部分只是已定方向：**未构建、不可用**；上表以外的任何东西都不承诺交付。

### 已建 —— 尖兵（审结，首次真实运行已在账）

- **财报深度点评 —— [`cn-earnings-note/`](cn-earnings-note/)**：A股 / 港股财报深度点评，P1 端到端实跑已过验收（跑次与标的数以本包 `README.md` 状态段为准）；版本以本包 `CHANGELOG.md` 为准。完整一句话见上表 Skills。
- **催化剂日历 —— [`catalyst-calendar/`](catalyst-calendar/)**：满窗实跑在账（证据链强制）——前瞻稀疏属域面实况，空前瞻主体各带一行归因；法定期限推导已尝试并拒推（当场无原文锚即不落行）。计数以本包 `README.md` 状态段为准，此处不重抄。对抗审已闭。版本以本包 `CHANGELOG.md` 为准。
- **公司一页纸 —— [`tear-sheet/`](tear-sheet/)**：打满主体上限的回客速览实跑在账、一轮通过；对抗审已闭；守护样全绿（计数以本包 `README.md` 状态段为准）。回客件五段形制、每行披露锚。
- **行业景气全景 —— [`sector-overview/`](sector-overview/)**：建材半程在账——量价逐行带口径与来源锚、两个沥青报价刻意不仲裁；对抗审已闭，国内行业量价域候工程。唯一权威数与其口径写在本包 `README.md` 状态段。判断词须与可比序列锚同线。
- **公开信息预尽调 —— [`dd-checklist/`](dd-checklist/)**：前两轮判卷先退回 → 按 §v2 逐条修 → 复审通过（过程见 git log 与本包 CHANGELOG）；题库以包内 `scripts/fixtures/` 现跑为准（样数落在评审方对账表，此处不重抄）。**真实主体端到端已在账（六参数全式当时八道全过）；§v2-16② 域集合门入门后按现行门复扫，两份历史件均 FAIL（两域漏记 `DD-OMISSION`，长窗那笔另含 `DD-COVERAGE`），历史件不改（该缺陷内部跟踪中）；**现行门下的真件 PASS 凭据已在盘**（同主体 `mna` 档、12m 窗、六参数全式 exit 0）——已验范围与仍未验证面以本包 `README.md` 状态段为准，此处不重抄。** 版本以本包 `CHANGELOG.md` 为准。

### 规划中 —— 批 2（方向已定、未建）

本节原有两项现已建成并通过对抗审——`sector-overview`、`tear-sheet`（见上方「已建」段）；此节留下的是三个方向，均尚无可用件：**首次覆盖**（initiating coverage，估值/建模环节一律 `[待人工]` 交人）、**论点跟迹**（thesis tracker，把已存的看法对新披露周期性复跑）、**融资摘要**（funding digest，取 IPO 与披露域的融资动态）。三者依赖的数据面要么已在上文列为可用、要么在下方明确暂缓；**本节不作任何交付承诺**。

### 暂缓（受阻、未建）

- 晨报、选股 / 创意生成、可比公司分析——等所需数据域在服务端目录上线后再做；开放节奏不在本文承诺，实况以 `GET https://cuecue.cn/api/mcp-catalog` 返回为准。

### 结构性排除

- 需要 Excel 引擎的模型类、fund-admin 内账类、以及依赖私有数据（账户 / CRM 等）的 skill 不在范围内——Cue 通道是互补方，不是内部账簿或估值模型引擎。

## 安装

十一件（含 `cue-omni-ontology`、`cue-lead-pieces`）在下方发布页各挂一个 ZIP 资产，任一件都可用同一套三步安装；也可以直接从本仓库复制对应目录。

发布列表见 <https://github.com/huhoo/cue-awesome/releases>。这一句有意不写具体版本号——号写在这里，下一次发布一出它就过期；请核对发布页和已安装 skill 的 frontmatter。

```bash
curl -L -o tear-sheet.zip https://github.com/huhoo/cue-awesome/releases/download/v2026.10.23/tear-sheet.zip
mkdir -p ~/.workbuddy/skills/tear-sheet
unzip -o -d ~/.workbuddy/skills/tear-sheet tear-sheet.zip
```

三行里的 `tear-sheet` 换成你要的那件即可（catalyst-calendar / civil-appeal-turnaround / cn-earnings-note / competitive-brief / cue-lead-pieces / cue-omni-ontology / dd-checklist / journal-draft / long-doc-translation / sector-overview / tear-sheet）——每行都是完整命令，不用改引号也不用管转义。
要从当前全部 skill 中选择：`git clone https://github.com/huhoo/cue-awesome.git`，再把需要的子目录拷进 `~/.workbuddy/skills/`。
第三条路是技能 CLI：`npx skills add huhoo/cue-awesome`（列出全部）/ `npx skills add huhoo/cue-awesome --skill journal-draft`（只装一件）。
第四条路是 ClawHub 的 CLI（商店侧形制，文档写的是 `install @owner/slug`）：`clawhub install @huhoo/cue-journal-draft`。那里的 slug 是 `cue-` 加目录名，与技能 CLI 那一式取的不是同一个串——同一个参数位两种取值，别当可互换。
Windows 目标路径：`C:\Users\<用户名>\.workbuddy\skills\`——三步与文件名同上。
装完 `cd` 进那件目录，跑它自己 README 里给的自查命令：各件自带，本页不复制其内容。

## 语言

文档为双语：`README.md`（英文）/ `README.zh-CN.md`（中文）。本中文版为译文，**以英文 `README.md` 为准**；如有出入以英文为准。Skill 指令文件遵循同一约定——见 [`docs/i18n.md`](docs/i18n.md)。

## 贡献

提交前先看 [`CONTRIBUTING.md`](CONTRIBUTING.md)：commit / PR 规范、新增 skill 清单、禁止提交的内容。全仓门禁每次 push 与 PR 都会跑：

```bash
python scripts/check_skills.py                                # 结构、frontmatter、CHANGELOG 形制
python scripts/check_public_hygiene.py --selftest             # 公开面卫生闸先自证守护样能红能绿
python scripts/check_public_hygiene.py                        # 五禁扫描全部公开面
```

卫生闸的计数是**工作树现值快照，不是稳定量**：树里动一笔它就动，要引就带时间戳，否则不引。它的详行带稳定码（`H-TICKET`、`H-PATH`、`H-POINTER`、`H-STATE`、`H-DATE`、`H-ATTRIB`），按码追责即可。

新 skill 提案：用 issue 模板「新 skill 提案」开一个。

## 说明

- 本仓为个人自研集合，与 Cue 官方技能集合 [sensedeal/cue-skills](https://github.com/sensedeal/cue-skills) 无关 —— 后者是官方 monorepo，本仓不是它的子集，也不并入其中。
- `LICENSE.md` / `NOTICE.md` 适用于整个仓库。
- 打包产物（`dist/`、`*.zip`）不入库，发布包见各 skill 的 manifest / CHANGELOG。
