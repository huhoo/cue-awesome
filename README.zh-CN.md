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
| [`tear-sheet/`](tear-sheet/) | tear-sheet | 0.1.0 | 公司一页纸(回客件):主体≤5+用途语境 → 五段固定形制、每行带披露锚、页眉含 asof 与通道用量;默认零深研,观点区永远 `[待人工]`。**在验:对抗终审未过、端到端未实跑。** |
| [`sector-overview/`](sector-overview/) | sector-overview | 0.1.0 | 行业景气全景(六节):判断词必须与可比序列锚同行,无锚走逐字「不做景气判定」句;政策时间线 statute 三件齐锚。**在验:文档+机检规格就绪,终审与实跑未做。** |

## 金融研究套件路线图

金融研究类 skill 是对 **anthropics/financial-services**（Apache-2.0）方法论基座的 Cue-native 重写；本土化实践（CAS 术语、合规词表、`[待人工]` 处理）首采 **道以研究院 dao-financial-services v0.1.9**（MIT）为参考。我方为重实现而非拷贝——数据层完全替换为 Cue 三层通道：**深研（cue-research）· 数据 MCP 域（Cue）· 文档解析（omni-reader）**。出处详见 [NOTICE.md](NOTICE.md)。

> **状态：** 以下**只有尖兵 `cn-earnings-note` 在本仓中真实存在**；其余均为已定方向、**尚未构建、不可用**。**除 `cn-earnings-note` 已完成 P1 端到端实测（验收记录见其 CHANGELOG Verified）外，其余规划项的任何性能数字均为设计值。** 除上表 Skills 所列成品外，本路线图不承诺任何已交付内容。

### 已建 —— 尖兵（4 件,其中 3 件在验）

- **财报深度点评 —— [`cn-earnings-note/`](cn-earnings-note/)**（v0.3.3）：A股 / 港股财报深度点评，P1 实测四跑两标的已过验收。完整一句话见上表 Skills。
- **催化剂日历 —— [`catalyst-calendar/`](catalyst-calendar/)**（v0.1.0）：第二批尖兵，机检四道 8/8 全绿；端到端实跑未做，首个真实主体按「未验证」对待。
- **公司一页纸 —— [`tear-sheet/`](tear-sheet/)**（v0.1.0，在验）：回客件,五段形制每行带锚。
- **行业景气全景 —— [`sector-overview/`](sector-overview/)**（v0.1.0，在验）：判断词-锚同行,无锚即不判定。

### 规划中 —— 批 2（方向已定、未建）

以下三项为已圈定方向，**未实现、不可用**：

- **行业景气全景**：行业景气与格局简报。
- **公司一页纸**：从公开披露快速生成的单页速览。
- **公开信息预尽调**：监管 / 法规 / 在审 IPO / 主体数据的清单式筛查。

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
