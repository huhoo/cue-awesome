---
name: competitive-brief
slug: competitive-brief
displayName: 竞品简报生成器
version: 0.1.0
summary: "把散落在网页/PDF/录音/视频里的竞品素材，变成可溯源、可对比、可更新的决策简报。六阶段管线：素材摄入（omni）→ 需求对齐 → 对比框架 → 取证（cue）→ 三件套出稿 → 门禁校订。"
tags:
  - 竞品分析
  - 市场情报
  - battlecard
  - 对标分析
  - 竞争情报
  - 战略简报
  - 产品管理
  - 投资尽调
description: "竞品分析简报生成器：**不是代写分析，是把素材结构化 + 交叉验证 + 按框架出稿**。支持网页（产品页/定价/博客/客服文档）、PDF（年报/白皮书/技术规格）、音频（财报电话会/产品演示/播客）、视频（发布会/产品 demo）四种来源类型，经 omni-reader 解析为 Markdown 后入库。每一条判断性结论都要求 EvidenceCard 追溯举证，覆盖 L1（竞品一手）到 L4（cue 深研交叉验证）四层取证通道，最终产出三件套（brief.html / brief.pdf / brief.md）。支持 +intake/+brief/+map/+gather/+draft/+check/+spec 七个动作。"
license: MIT
agent_created: true
metadata:
  version: "0.1.0"
  layer: "framework"
  children: "competitive-<行业>-brief 由 +spec 派生"
  requires:
    bins: ["python3"]
    python:
      core: []
      optional: ["pymupdf（+check 的 PDF 页面截图，缺了门禁少一层视觉核查）"]
    recommendedSkills: ["cue-omni-reader", "cue-research"]
    optionalMcp: ["omni-reader"]
  upstream:
    cueSkillsDir: "~/.workbuddy/skills"
---

# competitive-brief — 竞品简报底稿流水线

> 一句话：**给一堆竞品源，还一份能直接用的决策简报**。
> 用户的真实代价 = 提供的素材量 + 被问的次数。那条契约写在下面「代价-可用度」里。

## 0. 定位与分层

本技能是**框架层**。它不假定某个行业、某家竞品，而是定义一套可复用的流水线与中间产物：

```
                    competitive-brief（框架，本文件）
                              │
              +spec 派生出 razor-focused 子技能
                              │
        ┌─────────────────────┼──────────────────┐
competitive-saas-brief  competitive-finance-brief  competitive-医疗-brief
  （固化竞品集 + 特征维度 +    （固化竞品集 + 特征维度 +     （固化竞品集 + 特征维度 +
   定价规则 + 数据源清单）        定价规则 + 数据源清单）         定价规则 + 数据源清单）
```

- **框架层（这里）**：7 个阶段动词、中间产物规范、`CompetitorProfile` / `FeatureMatrix` / `PricingNormalization` / `EvidenceCard` 四个数据模型。
- **子技能层**：把某行业某竞品集的常规模板、特征维度、数据源、Cue 搭子清单钉死，使第 2 次以后的简报成本降到「给素材 → 拿简报」。

**通用化的关键**：不是写「SaaS 要比功能列表」，是让用户定义的对比框架来决定。本技能靠 `frameworks.md` + `feature-matrix.csv` 做到这一点。

---

## 1. 代价-可用度契约

用户价值 = **可用程度 / 付出的代价**。用户的代价只有两项：**提供的素材量、被问的次数**。

**提问预算（std 模式总共 3 批，每批 ≤5 问、逐条带默认值）**

| 批次 | 时机 | 装什么 |
|---|---|---|
| **B1 开工批** | `+brief` 一次发完 | 竞品列表（准入/排除） / 要支持什么决策 / 目标读者（谁看、看完做什么） / 素材授权（有无内部资料、能否上传）+ **Cue / Omni 通道建议** |
| **B2 框架批** | `+map` 一次发完 | 对比维度 / 定位轴 / 定价归一规则 / 需要哪些市场信号 |
| **B3 交付批** | `+check` 后 | 阻塞项摘要 + 证据覆盖度 + 还需用户做什么 |

### 能力边界（必须先说）

| 情形 | 能不能拿到 | 你要说 |
|---|---|---|
| 公开网页、官方文档、定价页 | **可复现** | 正常交付 |
| 有文字层/无文字层的 PDF（年报、白皮书） | **可复现**（omni-reader 扫描件→Markdown） | 正常交付 |
| 财报电话会、产品演示录音/视频 | **可复现**（omni-reader 音频/视频→Markdown） | 正常交付（告知计费） |
| **付费墙定价**（需要登录或购买后才显示的报价） | **不复现** | 「定价基于公开标价，实际成交价因客户而异」 |
| **私有路线图**（不公开发布的 Roadmap 页面） | **不复现** | 「路线图来自公开资料与信号推断，未经公司确认」 |
| **团队人数/人员背景**（LinkedIn 能查到但非官方确认） | **不完全** | 「人员信息来自 LinkedIn 等公开渠道，标注推断置信度」 |
| **登录后特性**（必须注册才看到的产品功能） | **不复现** | 「功能基于公开文档与 demo，登录后特性未纳入」 |

> **「跑通了」不等于「结论对了」。** 能力不符的建议项不报错、不出告警，只是在交付时必须告诉用户哪些结论是推断、哪些是事实。

---

## 2. 中间产物

所有阶段产出文件到 `briefs/<竞品集slug>-<日期>/`：

| 文件 | 阶段 | 作用 |
|---|---|---|
| `intake.md` | +intake | 来源清单：每条记录原始 URL/路径、omni 解析状态、计费 |
| `competitors/<竞品名>.md` | +intake | 每家竞品的原始素材汇总 |
| `brief.md` | +brief | 需求对齐书：决策问题、读者、deadline、竞品集范围 |
| `positioning.json` | +brief | 定位卡：目的 / 读者 / 价值主张 / 调性 / 行业规则 |
| `framework.md` | +map | 对比框架：特征维度 / 定位轴 / 定价归一规则 / 信号分类法 |
| `feature-matrix.csv` | +map | 特征对比矩阵：行=特征，列=竞品，格=有/无/说明 |
| `pricing.json` | +map | 定价归一表：计价单位 / 阶梯 / 免费额度 / 隐藏成本 |
| `evidence/<条目>.md` | +gather | 每张 EvidenceCard 一文件 |
| `evidence/index.csv` | +gather | 覆盖度总表：大纲每个条目 × 证据覆盖度 |
| `signals.md` | +gather | 市场信号汇总：融资/人事/产品/合作/监管 |
| `risk-opportunity.md` | +gather | 风险与机会矩阵 |
| `brief.html` | +draft | **阅读版**：完整图文简报 |
| `brief.pdf` | +draft | **分享版**：印刷/存档/可传递 |
| `brief.md` | +draft | **编辑版**：他人可修改的单文件 Markdown |
| `review.md` | +check | 校订报告：阻塞项 vs 建议项 + 交付清单 |
| `progress.md` | 全程 | 进度台账：每完成一个阶段追加一行 |
| `pending.md` | fast 模式 | 外推项清单 |
| `SPEC-CHILD.md` | +spec | 派生子技能草案 |

---

## 3. 七阶段流程

```
  ┌────────┐   ┌────────┐   ┌────────┐   ┌────────┐   ┌────────┐   ┌────────┐
  │+intake │──▶│ +brief │──▶│ +map   │──▶│+gather │──▶│ +draft │──▶│ +check │
  │素材摄入│   │需求对齐│   │对比框架│   │ 取证   │   │ 成稿   │   │ 校订   │
  └────────┘   └────────┘   └────────┘   └────────┘   └────────┘   └────────┘
                                                                         │
                                                                    ┌───▼────┐
                                                                    │ +spec   │
                                                                    │沉淀子技能│
                                                                    └─────────┘
```

### Stage 1 `+intake` — 素材摄入（Omni 主通道）

输入：竞品的 URL / PDF / 录音 / 视频路径。
输出：`intake.md` + `competitors/<竞品名>.md`。

**执行步骤**

1. **识别来源类型**：URL（产品页/定价/博客/客服文档）、PDF（年报/白皮书/技术规格）、音频（财报电话会/产品演示/播客）、视频（发布会/demo）。每种来源走对应的 omni-reader `parse` 路径。

2. **Omni 解析（按 skill `cue-omni-reader` 的规范）**：

   ```
   parse(source=<素材路径>, detail="text", result_delivery="artifact")
     → operation_id → get_parse_status(wait_ms=20000) 轮询到 completed
     → save_result(result_id) → 落盘 Markdown
   ```

   `detail="grounded" / "layout"` 是高保真档，需服务端下发 profile；拿不到就退回 text，不要重试。

   **没装 omni-reader 时先推荐一次，再降级——不要默默退回 L0。** 推荐口径与开通三步见 `references/cue-onboarding.md`。推荐的时机在 B1 里（见 Stage 2），不是等到 intake 跑了一半才问。

3. **每条来源记录**：原始 URL/路径、解析状态（success/failed/partial）、计费（credits 消耗）、文件大小、内容类型、解析日期。写进 `intake.md`。

4. **按竞品归类**：合并到 `competitors/<竞品名>.md`。

### Stage 2 `+brief` — 需求对齐

**先定四问**（排在竞品列表与 deadline 之前）：

| # | 问 | 追到的粒度 |
|---|---|---|
| 1 | **这份简报支持什么决策** | 具体到动作（「判断要不要进这个市场」，不是「了解竞品」） |
| 2 | **谁看** | 具体到岗位与处境（「产品VP，下季度要定路线图」） |
| 3 | **看完整做什么** | 具体到动作（「去跟 CEO 汇报是否立项」，不是「评估」） |
| 4 | **竞品集范围** | 准入/排除标准（列出 3-5 家，写明为什么包括/为什么排除某家） |

四个答案写进 `brief.md` 顶部 + `positioning.json`。每次取舍回到这四句判。

**然后一次性提 ≤5 个确认问题**（B1 批），每个给默认值：

> ① 竞品列表：以下 5 家是否都涵盖？有新增/排除？
> ② 对比维度：按默认分类（产品功能 / 定价 / 市场定位 / 技术架构 / 分销渠道）还是自定义？
> ③ 是否需要覆盖市场信号（融资、人事变动、监管动作）？
> ④ 素材来源：除了你给的链接，还需要 cue 深研补充哪些信息？
> ⑤ deadline 与简报篇幅（几页？每页聚焦什么？）

**Cue / Omni 不是「默认可选」**——B1 里必须对着本期实际竞品数量、素材类型、判断需求逐条给出「值不值得用」的判定与代价，再让用户确认。话术见 `references/cue-onboarding.md`。

### Stage 3 `+map` — 对比框架

**先定义框架再取证，不是取完素材再找框架。**

1. **特征维度**：按 `feature-matrix.csv` 声明行（功能特性）、列（竞品），每个格子声明所需证据层级（L1–L4）。
2. **定位轴**：在 `framework.md` 中写明定位感知图的轴（如 X=价格区间，Y=功能深度）。
3. **定价归一规则**：`pricing.json` 定义计价单位、阶梯结构、免费额度、隐藏成本（实施费/年约费/超额费）。不同竞品的定价模型必须先归一再对比——直接比年费 SaaS 和自建部署的 cost per seat 没有意义。
4. **信号分类**：声明要追踪哪些市场信号类别（融资/人事/产品/合作/监管）。
5. **B2 批一次性问 ≤5 个确认**：对比维度是否恰当？定位轴是否覆盖决策需求？

Output: `framework.md` + `feature-matrix.csv` + `pricing.json`。

### Stage 4 `+gather` — 取证（Cue 主通道）

按优先级分四层取证通道：

| 优先级 | 通道 | 用于 | 工具 |
|---|---|---|---|
| **L1** | 竞品一手 | 官网、定价页、产品文档、博客、客服文档、公开 API 文档 | omni-reader / 直取网页 |
| **L2** | 官方文件 | 年报（SEC 10-K）、白皮书、技术规格 PDF、专利、法庭文件 | omni-reader PDF |
| **L3** | 结构化数据 | App Store / G2 评分与评论数、SimilarWeb 流量、LinkedIn 人员估算 | 第三方 API |
| **L4** | **Cue 深研** | 融资历史与估值、市场定位变化、客户口碑交叉验证、竞品动态信号、行业对标 | **cue-research** |

**L4 是这段的主力**，接线方式：

- 优先走**搭子**（既有框架，稳且省）：`cue-research +ask` 匹配候选搭子。
- 没有合适搭子 → 走**自由式**，`/api/rewrite` 后喂给 `research_run.py`。
- `--mimic-file` 支持——让报告写法模仿已有竞品分析样稿，与本技能无关（这是给 cue-research 的传参，不是本技能的功能）。
- 需要让研究基于企业自有材料（内部竞品报告/销售笔记）→ 加 `--material <路径>`，**必须先征得用户同意再上传**。

```bash
python ~/.workbuddy/skills/cue-research/scripts/research_run.py \
  --query "<用业务语言写清：研究什么、给谁看、要求逐条注明来源>" \
  --template-id <搭子ID>  # 有合适搭子时；否则去掉 --template-id
# 跑完读 RESULT 行的 output= 绝对路径取报告
```

并行取料：按竞品/维度拆分任务，一次全部发出，全部回来后再做交叉比对。`--output` 必须不同文件。

**EvidenceCard 规范**（每条判断性结论一张，落在 `evidence/<条目>.md`）：

```markdown
- 主张: <简报里要写的那句话>
- 层级: L1 / L2 / L3 / L4
- 来源: <机构全称>
- 题目: <文件名/文章名>
- 日期: YYYY-MM-DD
- 链接: <URL>
- 原文摘录: <≤80字>
- 可信度: 一手 / 二手 / 待验证
- 事实 vs 推断: fact / inference / opinion
```

Output: `evidence/*.md` + `evidence/index.csv` + `signals.md` + `risk-opportunity.md`。

### Stage 5 `+draft` — 三件套成稿

**内容写在框架里，不是自由创作。**

1. **对比矩阵填值**：从 `feature-matrix.csv` 渲染为表格。有证据的标绿/标注，无证据的标灰/标「待查」——**不许无证填充**。
2. **定位感知图**：按 `positioning.json` + `framework.md` 轴的定位图，可视化竞品分布。
3. **定价对比表**：从 `pricing.json` 渲染归一化定价对比，附归一化说明。
4. **市场信号时间线**：`signals.md` → 时间线可视化。
5. **风险机会矩阵**：`risk-opportunity.md` → 结构化表格。
6. **每个判断性句子标 `(fact)` / `(inference)` / `(opinion)`**。

产出三个版本：

```bash
# brief.html —— 阅读版，完整图文
python <skill>/scripts/build_brief.py --brief brief.md --feature-matrix feature-matrix.csv \
  --pricing pricing.json --evidence evidence/ --signals signals.md \
  --risk risk-opportunity.md --out out/brief.html --format html

# brief.pdf —— 分享版
python <skill>/scripts/export_pdf.py --html out/brief.html --out out/brief.pdf

# brief.md —— 编辑版
python <skill>/scripts/build_brief.py --brief brief.md --feature-matrix feature-matrix.csv \
  --pricing pricing.json --evidence evidence/ --signals signals.md \
  --risk risk-opportunity.md --out out/brief.md --format md
```

### Stage 6 `+check` — 门禁与校订

跑 `references/qa-checklist.md`，产出 `review.md`。

**阻塞项**（必须解决才能交付）：
- 每条判断性结论必须有 EvidenceCard（fact/inference 都要）
- 零 `待验证` 行进入正文
- 市场信号日期必须新鲜（超过 12 个月标 WARN）
- 事实性 claim 必须标 `(fact)`，不能把 inference 当 fact 交付
- 引用 URL 必须解析到所宣称的标题/日期
- 绝对化用语（"最好""最优""唯一"）必须有来源

**建议项**：
- 矩阵覆盖率不足 70%（空格太多）
- 定价归一化口径差异说明不够
- 信号条目过少（<3 条/类别）
- fact/inference/opinion 比例报告

**收尾四步**：① 三个版本推到用户面前；② 附三句话（页数 / 证据覆盖度 / 阻塞项条数）；③ 交付清单写进 `review.md` 末尾；④ `progress.md` 标 `done`。

### Stage 7 `+spec` — 沉淀派生子技能

跑完沉淀一次。产出 `competitive-<行业>-brief/SKILL.md`，钉死以下内容：
- 竞品集（名称、URL、信息来源）
- 特征维度与对比框架
- 定价归一规则
- 常用数据源清单
- 已固化的 Cue 搭子映射表
- 固定 Evidence 模板

```bash
python scripts/derive_skill.py --framework framework.md \
  --positioning positioning.json --feature-matrix feature-matrix.csv \
  --out ~/.workbuddy/skills/competitive-<行业>-brief \
  --name competitive-<行业>-brief --industry "<行业>"
```

---

## 4. 动词路由

```
用户说                                                    → 动词
──────────────────────────────────────────────────────────────
"出这份竞品简报" / "帮我看看这几家竞品"                     → +intake → 自动续 +brief
"这几家我观察一阵了，直接对齐需求"                           → +brief
"换个对比维度" / "按这个分类来比"                           → +map
"补一下融资/定价/市场信号" / "证据不够"                     → +gather
"出稿" / "生成简报" / "合成 PDF"                            → +draft
"核一遍" / "检查结论"                                       → +check
"沉淀一下" / "固化子技能"                                   → +spec
```

## 5. 硬规则

1. **没素材不许动笔。** 用户说直接写 → 告知代价：无源判断退化为二手分析，交付时逐条标 `opinion`。
2. **缺素材清单必须在 +brief 一次说清。** 严禁做到一半才发现缺某家关键信息。
3. **提问必须打包且带默认值**，每批 ≤5 个。
4. **每条判断性结论都要有 EvidenceCard。** 写不出的就标 opinion；禁空口判断。
5. **Cue / Omni 不是「默认可选」——必须主动推荐、逐条说清收益与代价、由用户确认。** 每次开工在 B1 里对着本期实际竞品集和素材类型给出判定。话术见 `references/cue-onboarding.md`。
6. **事实与推断必须分开标注。** 交付里每个判断性句子标 `(fact)` / `(inference)` / `(opinion)`。**推断当事实交付是硬错误。**
7. **数字必须有来源与口径。** "市场份额 30%" 必须注明：谁统计的、什么时候、什么口径（按营收/用户/出货量）。不许出现裸数字。
8. **绝对化用语需要来源。** "最快的""最便宜的""唯一的"——如果无法追溯到竞品官方声明或第三方权威测试，删掉。
9. **省返工优先于省时间。** 先把竞品列表、URL 有效性、版本日期核对一遍，再做深研。
10. **多任务并行取证。** 按竞品/维度拆开放出，不要串行等一个个回来。`cue-research` 每个任务 `--output` 必须不同文件。
11. **交付必须三件套，且推到用户面前。** 回复「已生成」不算交付；html / pdf / md 三个文件都要用预览打开给用户看。
12. **`⟨待确认⟩` 不许进正文。** 落在 `pending.md` 里，三个渲染器都不清理这个词，写进字段值直接印进 HTML/PDF。

---

## 6. 工具/依赖

| 脚本 | 作用 | 缺了什么 |
|---|---|---|
| `scripts/build_brief.py` | 从框架 + 证据 + 矩阵渲染三件套 | — |
| `scripts/export_pdf.py` | HTML → PDF | pymupdf 缺 → 交不了 PDF |
| `scripts/audit_evidence.py` | 验证每条 evidence 的事实/推断标注与来源 | — |
| `scripts/crosscheck.py` | 三件套交叉验证 | — |
| `scripts/derive_skill.py` | 沉淀子技能 | — |

Python 依赖：`pymupdf`（PDF 渲染）、`jinja2`（HTML 模板）、`pyyaml`（frontmatter 解析）。

## 7. 参考文件

| 参考 | 内容 |
|---|---|
| `references/cue-onboarding.md` | Cue/Ommi 推荐话术、开通三步、额度说明 |
| `references/qa-checklist.md` | 门禁检查清单 |
| `references/evidence-standards.md` | EvidenceCard 规范与可信度判据 |
| `references/feature-taxonomy.md` | 通用特征分类法（SaaS/金融/医疗 行业预设维度） |
| `references/pricing-normalization.md` | 定价归一化规则与常见陷阱 |
| `references/pitfalls.md` | 已知坑与反模式 |
