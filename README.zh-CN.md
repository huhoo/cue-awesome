# cue-awesome

**[English](README.md) · [中文](README.zh-CN.md)**

个人自研的 WorkBuddy / Cue 技能集合仓。每个子目录是一个独立 skill，可单独复制使用。

## 先试一次公开资料知识更新

**新材料改变了什么？哪些数字能比较？依据在哪里？** [`cue-omni-ontology`](cue-omni-ontology/README.md) 把公开报告和公告变成带证据的回答、变化简报，以及下次能继续更新的知识包。可以从财报披露、供应商资料或产品更新开始。

```bash
npx skills add huhoo/cue-awesome --skill cue-omni-ontology
```

安装后对 Agent 说：**“使用 cue-omni-ontology，先用自带样例演示：加入新材料后，哪些事实新增、哪些冲突、依据在哪里？”** 自带演示无需 API key，不发起网络请求。真实资料解析需另行配置官方 Cue Omni Reader。

[上手与复用指令](cue-omni-ontology/README.md) · [微软公开披露新解析实测](cue-omni-ontology/assets/public-example/live-preview.md) · [验证范围与边界](cue-omni-ontology/references/verification.md)

## Skills

| 目录 | Name | 版本 | 用途 |
|---|---|---|---|
| [`cue-omni-ontology/`](cue-omni-ontology/) | cue-omni-ontology | [frontmatter](cue-omni-ontology/SKILL.md) | 公开资料知识与变化简报：无需 Key 的演示、原文证据、区分口径的回答，以及保留历史和冲突的持续更新。提供财报、供应商和产品场景指引。公开试验版，已验范围见包内验证记录。 |
| [`cue-lead-pieces/`](cue-lead-pieces/) | cue-lead-pieces | [frontmatter](cue-lead-pieces/SKILL.md) | 财报引文逐字核对：从公司自己的 A 股（巨潮资讯）或美股（SEC EDGAR）公开披露生成线索件（对象 · 为何现在 · 建议动作 · 带来源和页码的原文证据），并把答案里的每句引文对回所注页核对；`verify --fix` 改正注错的页码、把改过字的引文换回原句、删掉原文没有的。数据源公开免费，无需 API key。公开试验版，只在一个宿主、一个模型、24 家公司上实测，数字与局限见包内[验证记录](cue-lead-pieces/references/verification.md)；它只核对引文是否出自原文，不判断信号对错。 |
| [`journal-draft/`](journal-draft/) | journal-draft | [frontmatter](journal-draft/SKILL.md) | 企业期刊 / 内刊 / 客户通讯 / ESG 报告 / 年鉴特刊的「底稿生成器」：把版式体例从 PDF 里量化成可校验参数（版面网格、版心、字号序列、行距、色板、栏目模板），再按这套参数生产新一期内容。含法规动态栏目规范、CTA 溯源机制。 |
| [`long-doc-translation/`](long-doc-translation/) | long-doc-translation | [frontmatter](long-doc-translation/SKILL.md) | 长篇外文（德 / 英 / 法 / 日等）学术专著、古籍、档案、译著的全文高质量中译流水线：解析 → 清洗切片 → 建体例与术语表 → 并行分批翻译 → 多维质检 → 合并交付带目录的阅读版。 |
| [`competitive-brief/`](competitive-brief/) | competitive-brief | [frontmatter](competitive-brief/SKILL.md) | 竞品简报生成器：把散落在网页 / PDF / 录音 / 视频里的竞品素材，变成可溯源、可对比、可更新的决策简报。六阶段管线：素材摄入（omni-reader）→ 需求对齐 → 对比框架 → 取证（cue-research）→ 三件套出稿 → 门禁校订。 |
| [`cn-earnings-note/`](cn-earnings-note/) | cn-earnings-note | [frontmatter](cn-earnings-note/SKILL.md) | A股 / 港股财报深度点评生成器：输入「主体 + 报告期」，产出 8–12 页、**研报结构级（八节骨架）**的 AI 初稿（四期披露差异、分部量价、盈利质量与现金流含金量、附注风险扫描、指引与催化剂、同业对照），逐数可回查，评级与目标价一律标注 `[待人工]`。取证走 Cue 三层通道——结构化披露（Cue 数据 MCP 域）+ 原文解析（omni-reader）+ 横向深研（cue-research）。**P1 端到端实测已完成**（跑次、标的与仍未验证面以本包 README 状态段为准）；港股主体与多主体批量仍按「未验证」对待。基座出处见 [NOTICE.md](NOTICE.md) §金融套件。 |
| [`catalyst-calendar/`](catalyst-calendar/) | catalyst-calendar | [frontmatter](catalyst-calendar/SKILL.md) | 持仓催化剂日历:输入「主体集(≤10)+前瞻窗口(默认 90 天)」,产出日期正排、**逐事件带披露锚**的日历(回购节点/激励归属/解禁减持披露/监管回复期限/分红除权/定期报告法定期限推导)。只陈述事件——未披露不入表、利好利空判词全禁、无锚即删条。机检四道专拦日期幻觉。**对抗审已通过（2026-09-21）；实跑已在账——计数与仍未验证面以本包 README 状态段为准。** 基座出处见 [NOTICE.md](NOTICE.md) §金融套件。 |
| [`tear-sheet/`](tear-sheet/) | tear-sheet | [frontmatter](tear-sheet/SKILL.md) | 公司一页纸(回客件):主体≤5+用途语境 → 五段固定形制、每行带披露锚、页眉含 asof 与通道用量;默认零深研,观点区永远 `[待人工]`。**对抗审已通过（2026-09-21）；实跑已在账——计数与仍未验证面以本包 README 状态段为准。** |
| [`sector-overview/`](sector-overview/) | sector-overview | [frontmatter](sector-overview/SKILL.md) | 行业景气全景(六节):判断词必须与可比序列锚同行,无锚走逐字「不做景气判定」句;政策时间线 statute 三件齐锚。**对抗审已通过（2026-09-21）；实跑已在账——计数与仍未验证面以本包 README 状态段为准。** |
| [`dd-checklist/`](dd-checklist/) | dd-checklist | [frontmatter](dd-checklist/SKILL.md) | 公开信息预尽调清单-cn：唯一主体 + 回溯窗口 → 九类风险逐条带锚摊开，缺什么/查不到什么同表记账；不出投资判断、不出法律意见。**真实主体端到端已在账；复审已闭——已验范围与仍未验证面以本包 README 状态段为准。** 基座出处见 [NOTICE.md](NOTICE.md) §金融套件。 |

## 金融研究套件路线图

金融研究类 skill 是对 **anthropics/financial-services**（Apache-2.0）方法论基座的 Cue-native 重写。我方为重实现而非拷贝——数据层完全替换为 Cue 三层通道：**深研（cue-research）· 数据 MCP 域（Cue）· 文档解析（omni-reader）**。出处详见 [NOTICE.md](NOTICE.md)。

> **状态：** 本仓对外发布的金融研究 skill，以上方 Skills 表所列为准。`cn-earnings-note` 已完成 P1 端到端实跑（验收记录见本包 `CHANGELOG.md` 的 Verified 段）。`catalyst-calendar`、`tear-sheet`、`sector-overview` 已于 2026-09-21 通过对抗审终判，且各有一次真实运行在案：催化剂日历——满窗多主体、证据链强制，前瞻稀疏属域面实况，法定期限推导已尝试并当场拒推（该次 statute 通道未取回原文）；公司一页纸——打满主体上限的回客速览、一轮通过；行业景气全景——建材半程，量价逐行带口径与来源锚、两个沥青报价并列不仲裁（设计行为），国内行业量价域仍未开放。**实测计数一律以各包 `README.md` 状态段为唯一权威，本文件不重抄。**版本号以各包 `CHANGELOG.md` 现值为准，不写进本句。路线图其余部分只是已定方向：**未构建、不可用**；上表以外的任何东西都不承诺交付。

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

九件（含 `cue-omni-ontology`）在下方发布页各挂一个 ZIP 资产，任一件都可用同一套三步安装；也可以直接从本仓库复制对应目录。`cue-lead-pieces` 在该发布之后加入，暂无 ZIP，请用下面的技能 CLI 安装或直接复制它的目录。

下方 ZIP 命令说明列出的九个 skill，现有发布页为 <https://github.com/huhoo/cue-awesome/releases/tag/v2026.09.27>。打包版本可能与当前仓库不同，请核对发布页和已安装 skill 的 frontmatter。

```bash
curl -L -o tear-sheet.zip https://github.com/huhoo/cue-awesome/releases/latest/download/tear-sheet.zip
mkdir -p ~/.workbuddy/skills/tear-sheet
unzip -o -d ~/.workbuddy/skills/tear-sheet tear-sheet.zip
```

三行里的 `tear-sheet` 换成你要的那件即可（catalyst-calendar / cn-earnings-note / competitive-brief / cue-omni-ontology / dd-checklist / journal-draft / long-doc-translation / sector-overview / tear-sheet）——每行都是完整命令，不用改引号也不用管转义。
要从当前全部 skill 中选择：`git clone https://github.com/huhoo/cue-awesome.git`，再把需要的子目录拷进 `~/.workbuddy/skills/`。
第三条路是技能 CLI：`npx skills add huhoo/cue-awesome`（列出全部）/ `npx skills add huhoo/cue-awesome --skill journal-draft`（只装一件）。装 `cue-lead-pieces`：`npx skills add huhoo/cue-awesome --skill cue-lead-pieces`。
Windows 目标路径：`C:\Users\<用户名>\.workbuddy\skills\`——三步与文件名同上。
装完 `cd` 进那件目录，跑它自己 README 里给的自查命令：各件自带，本页不复制其内容。

## 语言

文档为双语：`README.md`（英文）/ `README.zh-CN.md`（中文）。本中文版为译文，**以英文 `README.md` 为准**；如有出入以英文为准。Skill 指令文件遵循同一约定——见 [`docs/i18n.md`](docs/i18n.md)。

## 贡献

提交前先看 [`CONTRIBUTING.md`](CONTRIBUTING.md)：commit / PR 规范、新增 skill 清单、禁止提交的内容。全仓门禁每次 push 与 PR 都会跑：

```bash
python scripts/check_skills.py
```

新 skill 提案：用 issue 模板「新 skill 提案」开一个。

## 说明

- 本仓为个人自研集合，与 Cue 官方技能集合 [sensedeal/cue-skills](https://github.com/sensedeal/cue-skills) 无关 —— 后者是官方 monorepo，本仓不是它的子集，也不并入其中。
- `LICENSE.md` / `NOTICE.md` 适用于整个仓库。
- 打包产物（`dist/`、`*.zip`）不入库，发布包见各 skill 的 manifest / CHANGELOG。
