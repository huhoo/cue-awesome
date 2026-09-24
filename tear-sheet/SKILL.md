---
name: tear-sheet
displayName: 公司一页纸
slug: tear-sheet
version: 0.1.1
summary: "见客户前 30 秒一张纸：主体（≤5）+ 用途语境，产出每行带披露锚、时效声明在场的一页纸（屏内 ≤40 行/主体）。五段形制钉死（身份/近四期速览/在场事件/风险/观点区），观点区永远 [待人工]，默认零深研、成本可预期。"
description: "公司一页纸（tear sheet）生成器，套件里最低门槛的回客件——单次默认零深研、data-mcp 直查为主、摘要需要时才动 omni，每一次使用都真实展示 Cue 通道取证。输入「主体（≤5 个，超了拒绝并说明成本理由）+ 用途（会前速览|客户简报 二选一）+ 可选关注点一句话（只升排版，不引入新数据源）」。输出五段固定形制：身份三行（禁简介自造）→ 近四期速览表（营收/归母/扣非/经营现金流，累计+单季双口径带 basis 标签）→ 在场事件 ≤4 条（复用姊妹件 catalyst-calendar v2 入类第一闸：有明确日期的在场披露或可复算 statute 推导）→ 风险 1–3 条（仅直查命中项，无命中写『直查面内未命中≠无敞口』）→ 观点区 [待人工]×3 行（一句不代填）。页眉三声明必在场：生成 asof、数据截止日、本次通道用量。默认 0 次深研（超限即降级标注『深研未发起』）；全流程确认弹窗至多一次，成本可预期是回客件前提。改造自 anthropics/financial-services tear-sheet（Apache-2.0）的 A股化重实现，数据层完全替换为 Cue 通道。Triggers: 给我一页纸看看XX / 见客户前速览XX / 公司名片页 / 客户简报里加一节XX; one-pager on XX / quick company sheet before my meeting / tear sheet for XX. 不用于：需要 Excel/表格交付物（本件只产 md 回客页）、超过 5 个主体的批量（批量日历走 catalyst-calendar）、财报深度点评与兑现度对账（走 cn-earnings-note）、任何评级/目标价/买卖建议（观点区留白归人）。"
tags: [投研, 一页纸, A股, 回客件]
license: MIT
agent_created: true
metadata:
  requires:
    bins: ["python3"]
  optionalSkills: ["cue-data-mcp", "cue-omni-reader"]
---

# tear-sheet — 公司一页纸（AI 初稿）

> 交付的是**每行可锚的一页纸**，不是观点成品；也是套件的回客入口——它替你把「30 秒能确定的事实」先摆上桌。
> 铁律语法继承姊妹件；本件最大风险=**为凑一页而补数据**，全部形制约束围绕「宁缺毋滥」。

## 0. 什么时候用 / 不用

| 你要 | 用什么 |
|---|---|
| 见客户前 30 秒生成的一页速览（屏内读完，每行带锚） | **本 skill** |
| 未来三个月的日期表 | `catalyst-calendar` |
| 深度点评/连续剧对账 | `cn-earnings-note` |
| Excel 交付物、批量 >5 主体、评级/目标价 | 不做（frontmatter「不用于」句） |

## 1. 输入契约（≤3 问）

- **主体集**：官方中文全称或代码，**≤5 个**——超了拒绝并说明成本理由（回客件的定位=快与省，批量走姊妹件）；
- **用途**：`会前速览 | 客户简报` 二选一（只影响详略与排版密度，不改任何纪律）；
- **关注点**（可选，一句话）：如「现金流最近怎么样」→ 该主题在页内升加粗行，**不引入新数据源、不加新段**。

## 2. 一页纸固定形制（五段，顺序钉死=机检④）

1. **身份三行**：全称 / 代码 / 主营一句话（`entity_data`+`disclosure_cn`；**禁简介自造**——主营句取披露原文表述）；
2. **近四期速览表**：营收/归母/扣非/经营现金流 × 四期（**累计+单季双口径**，每值带 basis 标签，继承 `cn-earnings-note/references/data-channels.md` §1 `fr_fact_index` 与口径纪律）；
3. **在场事件 ≤4 条**：入类第一闸与类型封闭枚举**复用姊妹件 `catalyst-calendar` 的 `references/event-taxonomy.md`（v2）——本件只引用不复制**（双事实源禁令）；1%/2% 进度节点等危险项同禁；
4. **风险 1–3 条**：仅 `fr_footnote`/`regulatory_cn` 直查命中项；无命中**必须**写固定句「直查面内未命中≠无敞口」；
5. **观点区**：`[待人工]` **×3 行**空位（行含义由使用者自定，本件不命名、一句不代填）。

**页眉三声明（缺任一 FAIL）**：生成 asof / 数据截止日 / 本次通道用量声明（如「research 0 次·omni 1 次·data-mcp 9 次」）。

## 3. 通道与成本纪律

- `data-mcp` 直查为主（域清单与工具发现规则同 `cn-earnings-note/references/data-channels.md` §1）；
- **默认 0 次 cue-research**——一页纸的成立不以深研为前提；需要深研的诉求出现时，降级标注「深研未发起」并指路姊妹件，**不中途烧**；
- `omni` 仅当需要摘要级原文且域面 section 全文不足时（三级路径同姊妹件）；
- **页眉通道用量声明与 `evidence/` 快照数逐笔对账（缺快照=缺声明，写进台账注因）；全流程 confirm-before-spend 弹窗至多一次**：所有可能计费的调用合并预演、一次问齐——成本可预期=回客件的前提。

## 4. 管线（三段+门禁）

`+scope`（消歧+用途定档）→ `+facts`（五段取数：身份/四期/事件闸内 ≤4/风险直查；**每笔域直查原始返回落 `evidence/`+台账 sha 行，零计费**）→ `+render`（按 §2 形制落 `page.md`，逐节追加同姊妹件纪律）。

收尾门禁（不过不出）：
```bash
python3 scripts/check_page.py <page.md> --sources <sources.jsonl> --subjects <n>
```
四道：①声明行（AI 初稿+asof+通道用量，缺任一 FAIL）②数字行列级锚+正文↔sources 双向（锚型白名单同 check_calendar v2）③禁词=BANNED 全集+`利好|利空|买入|增持|目标价|建议` **零容忍**（本页无评级概念）④形制闸=五段顺序+每主体 ≤40 行+事件条目全过第一闸封闭枚举；主体数 >5 即 FAIL。
（机检脚本与 fixtures 由并行工项在制；出门条件=lint 0 error+fixtures 全绿+红线 grep+独立评审方对抗审判词通过——catalyst 的教训：**绿灯不证防线**，坏样设计先行。）

## 5. 输出契约

```
tearsheet-<日期>-<n>主体/
├── page.md          交付物：页眉三声明+每主体五段（≤40 行/主体）
├── sources.jsonl    行式同姊妹件契约（id/kind/ref/claim/confidence/asof）
├── evidence/        域直查原始快照（契约=`cn-earnings-note/references/evidence-format.md`，只引用不复制；页眉通道用量与之对账）
└── progress.md      台账：取数面+弃行记录+通道用量实况
```

## 6. 边界与拒答

- 「帮我写成能直接发客户的推荐」→ 拒绝：观点区 `[待人工]` 是三行空位，代填=越界；
- 「加上 Excel/做个表格文件」→ 拒绝并指路（本件只产 md 回客页）；
- 主体 >5 → 拒绝并说明成本理由；批量日期场景引导 `catalyst-calendar`；
- 数据取不到 → 该行**删**并记台账弃行，**不以估计值凑页**——空行合法，编行违法。

## 7. 出处

- 基座：anthropics/financial-services `tear-sheet`（Apache-2.0）——一页纸的任务形态来源。
- 本包为**A股化重实现而非搬运**：数据层完全 Cue 通道化，形制（五段/双口径/第一闸/成本纪律）按本套件契约重建，无其代码。出处声明见仓库根 `NOTICE.md`。
