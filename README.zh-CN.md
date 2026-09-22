# cue-awesome

**[English](README.md) · [中文](README.zh-CN.md)**

个人自研的 WorkBuddy / Cue 技能集合仓。每个子目录是一个独立 skill，可单独复制使用。

## Skills

| 目录 | Name | 版本 | 用途 |
|---|---|---|---|
| [`journal-draft/`](journal-draft/) | journal-draft | 0.15.3 | 企业期刊 / 内刊 / 客户通讯 / ESG 报告 / 年鉴特刊的「底稿生成器」：把版式体例从 PDF 里量化成可校验参数（版面网格、版心、字号序列、行距、色板、栏目模板），再按这套参数生产新一期内容。含法规动态栏目规范、CTA 溯源机制。 |
| [`long-doc-translation/`](long-doc-translation/) | long-doc-translation | 1.3.0 | 长篇外文（德 / 英 / 法 / 日等）学术专著、古籍、档案、译著的全文高质量中译流水线：解析 → 清洗切片 → 建体例与术语表 → 并行分批翻译 → 多维质检 → 合并交付带目录的阅读版。 |
| [`competitive-brief/`](competitive-brief/) | competitive-brief | 0.3.0 | 竞品简报生成器：把散落在网页 / PDF / 录音 / 视频里的竞品素材，变成可溯源、可对比、可更新的决策简报。六阶段管线：素材摄入（omni-reader）→ 需求对齐 → 对比框架 → 取证（cue-research）→ 三件套出稿 → 门禁校订。 |
| [`cn-earnings-note/`](cn-earnings-note/) | cn-earnings-note | 0.3.3 | A股 / 港股财报深度点评生成器：输入「主体 + 报告期」，产出 8–12 页、**研报结构级（八节骨架）**的 AI 初稿（四期披露差异、分部量价、盈利质量与现金流含金量、附注风险扫描、指引与催化剂、同业对照），逐数可回查，评级与目标价一律标注 `[待人工]`。取证走 Cue 三层通道——结构化披露（Cue 数据 MCP 域）+ 原文解析（omni-reader）+ 横向深研（cue-research）。**P1 端到端实测已完成**（2026-09-18/19：美的 000333 两季连跑 2026H1+2025AR、雨虹 002271 2026H1，验收记录见 `cn-earnings-note/CHANGELOG.md` Verified）；港股主体与多主体批量仍按「未验证」对待。基座出处见 [NOTICE.md](NOTICE.md) §金融套件。 |
| [`catalyst-calendar/`](catalyst-calendar/) | catalyst-calendar | 0.1.0 | 持仓催化剂日历:输入「主体集(≤10)+前瞻窗口(默认 90 天)」,产出日期正排、**逐事件带披露锚**的日历(回购节点/激励归属/解禁减持披露/监管回复期限/分红除权/定期报告法定期限推导)。只陈述事件——未披露不入表、利好利空判词全禁、无锚即删条。机检四道专拦日期幻觉。**新出门件:端到端实跑未做,首个真实主体请按未验证对待。** 基座出处见 [NOTICE.md](NOTICE.md) §金融套件。 |
| [`tear-sheet/`](tear-sheet/) | tear-sheet | 0.1.1 | 公司一页纸(回客件):主体≤5+用途语境 → 五段固定形制、每行带披露锚、页眉含 asof 与通道用量;默认零深研,观点区永远 `[待人工]`。**对抗终审已通过(2026-09-21,M45);端到端未实跑,首个真实主体按「未验证」对待。** |
| [`sector-overview/`](sector-overview/) | sector-overview | 0.1.1 | 行业景气全景(六节):判断词必须与可比序列锚同行,无锚走逐字「不做景气判定」句;政策时间线 statute 三件齐锚。**对抗终审已通过(2026-09-21,M48);端到端未实跑,首个真实主体按「未验证」对待。** |
| [`dd-checklist/`](dd-checklist/) | dd-checklist | 0.1.0 | 公开信息预尽调清单-cn：唯一主体 + 回溯窗口 → 九类风险逐条带锚摊开，缺什么/查不到什么同表记账；不出投资判断、不出法律意见。基座出处见 [NOTICE.md](NOTICE.md) §financial-suite。 |

## 金融研究套件路线图

金融研究类 skill 是对 **anthropics/financial-services**（Apache-2.0）方法论基座的 Cue-native 重写；本土化实践（CAS 术语、合规词表、`[待人工]` 处理）首采 **道以研究院 dao-financial-services v0.1.9**（MIT）为参考。我方为重实现而非拷贝——数据层完全替换为 Cue 三层通道：**深研（cue-research）· 数据 MCP 域（Cue）· 文档解析（omni-reader）**。出处详见 [NOTICE.md](NOTICE.md)。

> **状态：** 本仓对外发布的金融研究 skill，以上方 Skills 表所列为准。`cn-earnings-note` 已完成 P1 端到端实跑（验收记录见本包 `CHANGELOG.md` 的 Verified 段）。`catalyst-calendar`、`tear-sheet`、`sector-overview` 已于 2026-09-21 通过对抗审终判，且各有一次真实运行在案：催化剂日历——10 主体 × 90 天满窗、证据链强制，窗内可锚前瞻 1 行、9 个主体节空前瞻各带一行归因，法定期限推导已尝试并当场拒推（该次 statute 通道未取回原文）；公司一页纸——5 主体回客速览、一轮通过；行业景气全景——建材半程，六条量价锚各带口径、两个沥青报价并列不仲裁（设计行为），国内行业量价域仍未开放。版本号以各包 `CHANGELOG.md` 现值为准，不写进本句。路线图其余部分只是已定方向：**未构建、不可用**；上表以外的任何东西都不承诺交付。

### 已建 —— 尖兵（审结，首次真实运行已在账）

- **财报深度点评 —— [`cn-earnings-note/`](cn-earnings-note/)**：A股 / 港股财报深度点评，P1 实测四跑两标的已过验收；版本以本包 `CHANGELOG.md` 为准。完整一句话见上表 Skills。
- **催化剂日历 —— [`catalyst-calendar/`](catalyst-calendar/)**：满窗实跑在账（10 主体 × 90 天，证据链强制）——可锚前瞻 1 行 + 9 节空前瞻各带归因行；法定期限推导已尝试并拒推（当场无原文锚即不落行）。对抗审已闭。版本以本包 `CHANGELOG.md` 为准。
- **公司一页纸 —— [`tear-sheet/`](tear-sheet/)**：5 主体回客速览实跑在账、一轮通过；对抗审已闭；守护样全绿（数量以 `CHANGELOG.md` 为准）。回客件五段形制、每行披露锚。
- **行业景气全景 —— [`sector-overview/`](sector-overview/)**：建材半程在账——六条量价锚带口径、两个沥青报价刻意不仲裁；对抗审已闭，国内行业量价域候工程。判断词须与可比序列锚同线。
- **公开信息预尽调 —— [`dd-checklist/`](dd-checklist/)**：两轮判卷先 BLOCK（M63、M70）→ 按 §v2 逐条修 → M76 复审 LGTM；题库以包内 `scripts/fixtures/` 现跑为准（样数落在评审方对账表，此处不重抄）。**真实主体端到端尚未跑——首个真实标的一律按未验证对待。** 版本以本包 `CHANGELOG.md` 为准。

### 规划中 —— 批 2（方向已定、未建）

本节原有两项现已建成并通过对抗审——`sector-overview`、`tear-sheet`（见上方「已建」段）；此节留下的是三个方向，今天都不可用：**首次覆盖**（initiating coverage，估值/建模环节一律 `[待人工]` 交人）、**论点跟迹**（thesis tracker，把已存的看法对新披露周期性复跑）、**融资摘要**（funding digest，取 IPO 与披露域的融资动态）。三者依赖的数据面要么已在上文列为可用、要么在下方明确暂缓；**本节不作任何交付承诺**。

### 暂缓（受阻、未建）

- 晨报、选股 / 创意生成、可比公司分析——等 `equity_market` 域开放后再做（live 状态以 `GET https://cuecue.cn/api/mcp-catalog` 为准，coming_soon 期间不承诺）。

### 结构性排除

- 需要 Excel 引擎的模型类、fund-admin 内账类、以及依赖私有数据（账户 / CRM 等）的 skill 不在范围内——Cue 通道是互补方，不是内部账簿或估值模型引擎。

## 安装

用 skills CLI：

```bash
npx skills add huhoo/cue-awesome                            # 列出全部 skill
npx skills add huhoo/cue-awesome --skill journal-draft      # 只装一个
```

或把需要的 skill 子目录复制到 WorkBuddy 用户级 skills 目录：

```bash
cp -r journal-draft ~/.workbuddy/skills/
cp -r competitive-brief ~/.workbuddy/skills/
```

Windows 对应路径：`C:\Users\<用户名>\.workbuddy\skills\`

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
