---
name: catalyst-calendar
displayName: 持仓催化剂日历
slug: catalyst-calendar
version: 0.1.0
summary: "输入主体集（≤10）+ 前瞻窗口（默认 90 天），产出一张日期正排、逐事件带披露锚的催化剂日历：回购节点/激励归属/解禁减持披露/监管回复期限/分红除权/定期报告法定期限。只陈述事件，不判利好利空。"
description: "持仓催化剂日历生成器。回答的真实问题是「未来三个月，这些持仓各自有什么确定的日子要盯？」。产出 calendar.md：主体节=日期正排表（日期|事件|类型|状态|来源锚）+ 未来 30 天要盯摘要 + 附录来源。事件只收「已有披露在场」或「法定期限规则推导（挂 statute 原文锚）」两类——未披露推测事件一律不入表；无锚即删条。取证走 Cue 通道：buyback/esop/disclosure_cn/regulatory_cn/statute 域直查 + cue-research ≤1 次（解禁/减持原表，可零）+ omni 仅公告原文需要时；margin 域不入列（其能力面=券商两融折算率，与事件日历无关）。改造自 anthropics/financial-services catalyst-calendar（Apache-2.0）的 A股化重实现，数据层完全替换为 Cue 通道。Triggers: 催化剂日历 / 事件日历 / 我的持仓未来三个月有什么日子 / 解禁和分红日程表 / 回购进度节点盘点; catalyst calendar / upcoming disclosures / earnings dates tracker / what dates should I watch for my holdings. 不用于：选股或择时建议（本件不判利好利空，事件只陈述）、标的池发现（主体集由用户给）、预测未披露事件（只收在场披露+法定推导）、财报深度点评（用姊妹件 cn-earnings-note）。"
tags: [投研, 事件日历, A股, 催化剂]
license: MIT
agent_created: true
metadata:
  requires:
    bins: ["python3"]
  optionalSkills: ["cue-data-mcp", "cue-research", "cue-omni-reader"]
---

# catalyst-calendar — 持仓催化剂日历（AI 初稿）

> 交付的是**带披露锚的日程表**，不是交易信号。日历上每一个日期都必须能回指一条在场公告或一条法条。
> 铁律与通道契约语法继承姊妹件 `cn-earnings-note`；本件最大风险=**日期幻觉**，全部设计围绕它。

## 0. 什么时候用 / 不用

| 你要 | 用什么 |
|---|---|
| 「未来三个月这些持仓各有什么确定的日子」的日历 | **本 skill** |
| 某只票的深度点评/兑现度对账 | `cn-earnings-note`（覆盖账本在其契约内） |
| 选股、择时、利好利空判断 | 不做——判词类表述全禁（铁律 3） |
| 传闻/预期类「事件」 | 不做——未披露不入表（铁律 2） |

## 1. 铁律

1. **输出是 AI 初稿**：标题后前 5 行内含 AI 声明行（机检①）；不构成投资建议，本件无评级概念、不出现「评级」一词的判词用法。
2. **只收两类条目**：已有披露在场（公告索引号/URL 锚）；法定期限推导（`statute` 原文锚+规则，如年报 4 月底）。**未披露的推测事件一律不入表**——「市场传闻将回购」不是条目。
3. **只陈述，不判断**：禁预判涨跌、禁「利好/利空/暴涨/会涨/抄底/逃顶」判词与姊妹件禁用词表（机检③词表=`cn-earnings-note` 禁用词全集+本件六词）。事件的中性陈述例：「回购方案到期日」「问询回复截止日」。
4. **无锚即删条**：数字与日期回指不了 `sources` 的条目，直接从日历删除并在台账记弃条原因；**日期一律 `YYYY-MM-DD` 全格式**（机检④），窗口外但确有必要的条目同行注「窗口外余档」。
5. **花之前必问**：cue-research ≤1 次（解禁/减持原表）与一切计费动作同姊妹件纪律——发起前报告耗时与消耗，只转述服务端计费事实。

## 2. 输入契约（≤4 问，逐条带默认值）

- **主体集**：官方中文全称或代码，≤10 个（逐个过消歧，姿势同 `cn-earnings-note/references/data-channels.md` §1）
- **窗口**：`YYYY-MM-DD~YYYY-MM-DD`，缺省=今起 90 天
- **关注类**（可选）：如「只看回购与分红」——缩窄 §3 取数面，不扩
- **输出目录**：默认 `./calendar-<日期>-<n>主体/`

## 3. 管线（四段+门禁，可续跑；开工建 `progress.md` 台账）

- `+scope`：主体集消歧+窗口落表；逐主体 `disclosure_cn` 拉窗口内公告清单存锚。
- `+events`：分类学（`references/event-taxonomy.md`）逐类取数——`buyback`/`esop`/`disclosure_cn`/`regulatory_cn` 域直查（工具级发现规则同 data-channels §1，入参 schema 现发现）；解禁/减持原表按缺口决定是否发起 research ≤1（L3 标注规则见分类学）。omni 仅在公告原文必须解析时调用（域面 section 全文优先，三级路径同姊妹件）。**`margin` 域不入列**——能力面=两融折算率，与事件日历无关（Q1 对账定案）。
- `+derive`：法定期限类（定期报告与快报的法定截止）按规则推导，**每条挂 `statute` 当场取回的法条原文锚**；规则文本不写死在日历里，推导依据入 sources。
- `+build`：按主体节组装 `calendar.md`（日期正排表：日期|事件|类型|状态|来源锚）+「未来 30 天要盯」摘要段（**只列，不评**）+ 附录来源索引（全锚可解析）。
- `+check`（不过不交付）：
  ```bash
  python3 scripts/check_calendar.py <calendar.md> --sources <sources.jsonl>
  ```
  四道：①声明行 ②表格数据行逐行含锚（公告索引号/URL/`conv_id` 三式其一，裸行 FAIL）③禁词表 ④日期格式与窗口（窗外无注 FAIL）。FAIL 回改复跑。

## 4. 输出契约

```
calendar-<日期>-<n>主体/
├── calendar.md      交付物：声明行+主体节（正排表）+30 天要盯段+附录来源
├── sources.jsonl    行式同姊妹件契约（id/kind/ref/claim/confidence/asof；research 件带 conv_id）
└── progress.md      台账：各段进度+弃条记录+research 实况
```

## 5. 通道依赖与降级

首次开通 Cue 三步同姊妹件（注册→api-key→装 skill；不装不报错）。降级路径：data-mcp 不可得→用户贴公告清单（标 L2 直供）；research 不发起→解禁/减持类整类标「未检索到」，**不以常识补日**。全降级仍可用，代价是日历覆盖度。

## 6. 边界与拒答

- 「帮我挑什么时候卖」→ 拒绝：日历陈述日子，不产出择时判断。
- 「把传闻/预期的事件加进表」→ 拒绝并引铁律 2。
- 主体集 >10 个 → 提示拆分（保取数质量与每主体锚完整）。

## 7. 出处

- 基座：anthropics/financial-services `catalyst-calendar`（Apache-2.0）——日历形态与事件分类的任务结构来源。
- 本包为**A股化重实现而非搬运**：数据层完全替换为 Cue 通道，事件分类学与法定推导按 A股披露制度重建，无其代码。出处声明见仓库根 `NOTICE.md`。
