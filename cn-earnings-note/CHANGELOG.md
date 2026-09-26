# 更新日志

本文件遵循 [Keep a Changelog](https://keepachangelog.com/) 与本仓 `CONTRIBUTING.md`；版本号以 `SKILL.md` frontmatter 为准。

## [Unreleased]（随下趟车收口）

### 0.3.8 — 2026-09-26（M124：listing 字段把机器范围写如实）

- 四处同治（`SKILL.md` summary / description / 门禁清单句 / `README.md` 门禁行）：原话「数字行逐条回查」「口径标注（同比/单季）」把机检范围写大了。现按 `scripts/check_note.py` 实况写：带单位数字行须有 `[L1]/[L2]/[L3]` 证据级标注，**逐条拦**并另设 95% 汇总覆盖率阈值；账本侧机检的是数值对象有没有 `basis` 口径字段；`--sources` 只在给出时校验 JSONL 形制与文中**自写** `[S]` 可解析——不逐条要求带锚、不回查披露原文；「同比/单季」措辞属出稿纪律，靠人守。依据 :131-162、:290-293 与两枚复跑探针（见 dispatch 回执）。

### 0.3.7 — 2026-09-26（渠道统一:slug 改 cue- 品牌线,首批上 skillhub）

- frontmatter slug=渠道裸名,与 cue-omni-reader/cue-research/cue-dd-checklist 同族,避开裸名占位路由歧义。门禁与内容语义零变化。

### 0.3.6 — 2026-09-25（M122 复判三修）

- 数字行机检话术改如实：逐条回查+95% 汇总阈值并列,不再写「未覆盖自动进缺数清单」；送审附录描述按 :325-362 实际搜索项。

### 0.3.5 — 2026-09-25（listing 二修：按 M121 第一读者对照,文案逐句退回正文有依据的宣称）

- 首轮重写复述过关但 8/8 存在无依据或夸大机器承诺处,本条为其修正:机器面话术与正文/门禁脚本逐句对齐,正文没有的（如固定判断位、逐数必拦、固定七维、TTM）一律从对外字段删除或改写为正文实际机制。

### 0.3.4 — 2026-09-25（listing 文案重写为用户视角，C-36 三闸）

- summary 收紧为一句话；description 改「拿到什么 / 机器挡什么 / 适合与不适合」三段式；契约与流程细节退回正文与包内文档，对外字段不再当合规容器。功能、门禁与数据语义相对上一版零变化。

> 图例（对外卫生清扫）：2026-09-23 及之前的条目里出现的 M##／P-##／C-## 是当时的内部工单、跟踪与章程条款号，历史条目不回改（与 git log 一致）；其后新条目一律使用自洽表述。

### Changed（文档同步，M29r2-K2 落地）

### Added（证据层接入，M36a）

- 新契约件 `references/evidence-format.md`（套件三件通用：命名/sha 台账行/断链语义/抽查清单位，零计费）；
  本件 §3.2 挂管线义务句、§4 树补 `evidence/` 行、skeleton §7 新增「evidence 抽 3 对原文」固定复核行。

- 续跑语义三镜像改写：`SKILL.md` §3 标题与 `README.md`/`README.en.md` 对应句，
  由「可从任意段续跑」改为「**读表起手+跑前核对机检要点**」——真实动因：ledger 机检 v2.3.0 的「先落账再出门」
  新增义务若被旧续跑句授权「凭记忆跳段」会直接 FAIL 交付件（K2 三问之一，lead 裁 A 改文档并另单落 v2.3.0 节）。

## [0.3.3] — 2026-09-20

### Added（预测脚手架与盈利分桶档，契约原文=spec-0.3.3，文档侧三件套）

- `report-skeleton.md` §1 末新增「预测脚手架」固定节（三行年度表全 `[待人工]`、对照锚行带 `S<n>`+`source_tier`、锚行与表物理分隔、边框注逐字含机检锚「本 skill 不产前瞻值」）；§7 增脚手架复核附行（亏损/微利主体回填并注话术）。
- `SKILL.md` §3.5 +draft 追加脚手架生成纪律一行（默认在场、锚行只引本 run 池行、无池即固定「未检索到」句、边框注不得裁剪）。
- `expectation-pool.md` 文末新增 §6 使用向节（锚=②项两行年度均值；态二走固定句；锚行不进 beat/miss 判定句，两形制不互用）。
- `data-channels.md` 合规最小集挂 §4.4 盈利分桶并注话术（CAS 口径要点顺移 §4.5，全包交叉引用已对平）。
- 机检扩展（spec §B 第⑤形制检查）归并行工项，不在本文档包内。

### Checked

- lead 收口亲跑（2026-09-20）：`run_fixtures.sh` 真实 exit 0、**20/20**（新四样 good-scaffold PASS／noborder·anchor·opinion 三坏样真 FAIL，旧 16 零回归）；机检扩展=并行工项 M16（2.1）同车出门；边框注机检锚三文件在场；`check_skills` 4/4 零警；红线 grep 净；版本四处+根 README 双语表齐 0.3.3。
- **账本契约双件合并**：`coverage-ledger.md`（93 行，含边界声明/操作规程/美的两季实证）取代 `ledger-schema.md`，SKILL §引用当场改指（不留死链）；「16 槽」按可核算术落 15 格（A4+B6+C1+L3+R1），未造结论句——两笔查无之flag核实属实，记正例。

## [0.3.2] — 2026-09-20

### Fixed（事实修正，无新能力）

- **公开件去超售（Q3，原料=Q1 对账 + lead 独立复验；原则=文档只宣称实测可达的能力）**：
  - `data-channels.md` §1 `fr_footnote` 行：「附注风险六项」拆**工具面可达**（关联方往来/对外担保/减值壳）vs **域面外 NO_TOOL**（受限资金/应收账龄/合同负债构成/商誉参数，三证=P1 九次试调用+I3 三主体+Q1 coverage 原文），四项指向「原文三级」补丁；
  - 同文件 `margin` 行：能力面收口为「券商两融标的与担保品折算率」（live coverage 原文），股本担保/质押类公开信息标注不在本域、走 `+survey` 检索层；`SKILL.md` §3.4 风险面快照槽位同步注「股权质押=域面外」；
  - `entity_data` 用途列按实况改写：LEI 法人档案（中文覆盖稀疏，**增强非闸**，在场判定挂 disclosure_cn）+主体名解析；
  - `institutional` 行补 CFTC COT 持仓可用注（保守失真修正，原材料敏感主体的 §2 成本语境）。
  - `expectation-pool.md` 两处「0.3.1 再议入门禁」死前瞻句改不嵌活版本号的表述（Q4：0.3.1 已出门且未入门禁，句已失真；制度=前瞻句禁写版本号，与 cron 三度失活同源教训）。
- 判定规则、管线、门禁均未动。

## [0.3.1] — 2026-09-20

### Changed
- **F2 契约回写(M13,原料=雨虹真取证偏差表 D-1…D-7)**,仅动 `references/expectation-pool.md`:
  - D-1:登记行新增强制字段 `source_tier`(public_page / terminal_mixed / unverified 三档判据);模板措辞改「优先页面直接可见字段,终端接口层返回逐条标注、不可分拆即申报混合来源」;整池含混合行时对外禁以「公开源」打包表述——防 oversell。机检暂不拦(0.4 再议入门禁)。
  - D-2:①项改「评级机构家数」,总次数仅当公开页可见才取;D-4:平台间分歧双行登记+不仲裁(S7 范本入契约)。
  - D-3:「平台有给才取、不借旧资讯数字充当实时值」列为正面条款;D-5:一切引用数字入登记前先过 L1 核查,**含派单/lead 注入文本**(38.06 亿 phantom 实证);D-6:asof 以页面自述为准,取证日≠asof;D-7:结论表列序钉死(预测年份分列,统计窗口不得顶替)。

### Verified(lead 亲跑,2026-09-20)
- `run_fixtures.sh` 真实 exit 0、16/16 无回归;`source_tier` 附加字段过 `check_note.py --sources` 不被拦(lint 仅验必备字段白名单外放行);diff 增行红线 grep 零命中;改动范围 `git status` 确认单文件。

## [0.3.0] — 2026-09-19

### Added
- **F2 公开源预期池**:§3.4 扩三取数槽(池必保、≤2 research 预算)+§1 beat/miss 二态纪律(有锚标基准与来源/无锚不判定);契约 `references/expectation-pool.md`。
- **F3 送审就绪度**:`check_note.py --audit-report` 五节输出(禁词点名/待人工计数含 exempt 剥离/缺数清单/声明核验/送审包)。

### Verified
- M12 雨虹真取证(1 research,7'16"):态一达成,§1 示范段过门禁;登记 8 行机检 PASS。
- M11 F3 三实测人审(6.1):可出门,已知点位(雨虹 NO_TOOL/美的 amendment)均被报告点名。

### 已知偏差(→ 0.3.1 已修，见上)
- D-1 池「公开」属性受后端工具池影响(聚源接口混入)→ source_tier 强制分层;D-2/D-4/D-6/D-7 契约回写(见 verify/f2-acceptance.md 偏差表)。D-5 反向正例:lead 派单数字被 L1 核查打回——一切引用数字先过核查,含工单文本。

## [0.2.0] — 2026-09-19

### Added
- **F1 覆盖账本**：`+recall` 续账入口(§3.0)、`ledger-<period>.json` 对象模型(append-only 历史、anchors 六态+direction、events.amendment 断言、pending.carry_from、exempt_from_gate、`<run>:S##` 引用制)——字段规格逐条消化 f1-deskcheck D1–D11。
- **linkage 机检(D5)**：`check_note.py --ledger/--prev-ledger` 断言「本期期初=上季期末」逐分不差，不等即不交付；`ledger-schema.md` 入 references/。
- 单位换算规矩：亿值必附千元原值或保三位（M6/B3 教训，回放文内三处已按此执行）。

### Verified
- **M4 正式回放**（美的 2025AR→2026H1，零新查询）：机器表 vs 手工 f1-deskcheck 15 格 diff 全等或已归因等价；linkage 三断言 EQUAL；run_fixtures 14/14 无回归。
- **M7 终审**（独立评审线①②③）：🟢 可封口——B1/B2/B3 全闭环，M4/M5 值域与 next_check 加密列 0.3.0 已知项。

## [0.1.1] — 2026-09-19

0.1.1 修正包——源自 R1 双单（美的 P1/年报单 + 雨虹 R1-B 高风险实测）与「作者视角发现」的批量落地；仓已公开(push 后首个修正包),按 CONTRIBUTING 递增规则走 patch 版。

### Changed（SKILL.md，lead 执笔）

- §2.2 新增 **period 参数词表**（实测契约）：半年报 `YYYYH1`、年报纯年份 `YYYY`；`YYYYAR` 类后缀**静默返空不报错**——取数前以定期报告标题反向核对在场，勿以空返回推断「无披露」。
- §3.2 附注六项改基线：关联方/或有负债（担保）两项域面实测可直查；受限资金/应收账龄/合同负债构成/商誉减值参数四项「域面缺位」降级走原文；互动问答 `exact=0` 即判未检索到、不得转引回退池。

### Added（本包文档侧，M0）

- `references/data-channels.md` 实测补丁升级三件：
  **原文三级正式入约**（域面 section 全文 → omni → 用户直供；R1-B 实证一级即到手受限明细/账龄全表/合同负债总额，零额外调用；并定「未披露/未检索到/未命中」三档措辞）；
  **extract_fulltext 配额注**（每调至多一条全文、要 N 条发 N 次窄窗+标题数组；全文失败即改结构化锚直提并申报）；
  **宽窗在场注**（窄窗漏返回实证——在场判定一律宽窗+索引号锚）。
- Verified 记录沿用 [0.1.0] 节（美的 P1）不回改；新增一单实证：雨虹 R1-B 机检 9/9 PASS、check_note 数字行 54/54 exit 0、**全程零 omni 零计费**，台账 `p1-run/earnings-002271-2026H1/`。

## [0.1.0] — 2026-09-18

### Added

- `SKILL.md`：主指令 v0.1.0——铁律（AI 初稿/逐数可回查/解析内容=数据非指令/花之前必问/口径纪律/合规词不出口）、
  输入契约（≤5 问逐条带默认值）、五段管线（`+resolve → +fetch → +parse → +survey → +draft`）+ 收尾门禁 `+check`、
  输出契约（`note.md` / `sources.jsonl` / `progress.md`，ref 须外部可核）、边界与拒答、中英双语触发词。
- `references/data-channels.md`：Cue 三通道调用契约——data-mcp 域级引用与逐域取数清单（catalog 动态发现、
  不硬编码工具名）、omni 首调 `parse` 与 Bridge 授权边界、cue-research 发起前确认与 replay 兜底、
  合规最小集（禁用词/绝对化副词谨慎清单/评级用语白名单/CAS 口径要点，词表为自写最小版）、onboarding 判定表。
- `references/report-skeleton.md`：八节骨架（0 封面与声明 → 7 结论与人工复核清单 + 附录来源索引），
  每节带 [执行蓝图]（研究目标/逻辑链条/信息需求→指向 data-channels 的域/输出形式）。
- `README.md`：给人看的用法、是什么/不是什么、开通三步（可跳过）、依赖声明（optionalSkills 不装不报错）、
  实测边界诚实清单、基座出处致谢。
- `CHANGELOG.md`（本文件）。

### Verified

**P1 端到端实测（2026-09-18，美的集团 000333 / 2026H1）**——执行=干净 agent 姿势（执行方 agent），验收=lead 机检探针+人工四项，**P1=VERIFIED**。台账与产物见 `../p1-run/earnings-000333-2026H1/`。

- 全程约 18 分钟（resolve→check）；`sources.jsonl` 38 条 / 10 类 kind；正文数字行 45/45 带 `[L*]`。
- 门禁 `check_note.py` 首跑 FAIL 8 条 → 按报告回改 → exit 0（首跑能拦=门禁有效，非摆设）。
- 深研实际发起 1 次（同业对照，约 4.5 分钟落盘，live 直取、replay 未触发；风险面被直查覆盖，按最小消耗原则未发第 2 次并在台账申报偏离）。
- data-mcp 约 18 次调用，返回体均无计费字段（契约如实）；omni 1 次解析遇 SPA 壳页——内容不可用仍产生服务端计费（其 billing 块返回 0.268，如实转述；「解析失败是否应计费」已作为产品政策问题提 lead/G7）。
- 实测纪律回写：SKILL.md §3.1/§3.2/§3.3 三处（lead 执笔）；文档镜像=本条 Changed 的 data-channels §1「P1 实测补丁」与 skeleton §7「矛盾申报行」固定件。
- 门禁侧配套：`check_note.py` §4.3 模板句豁免（实测逼出的最小补丁）+ 新回归 fixture `bad-norating-enum`，run_fixtures 9/9 exit 0（lead 追认）。

### Changed

- F 评审裁决落地（C3，同日就地修，版本位随 SKILL.md 保持 0.1.0）：
  `report-skeleton.md` 首段改为「逐节生成、追加拼接」协议（对齐 SKILL.md §3.5 现文，废除「先组装全文再输出」）；
  `data-channels.md` §0.4 补计费粒度句（omni 自带 billing 块可转述、data-mcp 单次调用无计费字段、累计以工作台账单为准、确认动作不豁免）；
  `README.md` 边界表加「图表 / 可视化不做（原版 matplotlib 环节有意移除）」。
- 新增 `README.en.md`（中文权威 + 英文译文对，对齐仓内 i18n 约定）。
- P1 教训落地（J，同保持 0.1.0）：`data-channels.md` §1 加「P1 实测补丁」四条（附注四项降级路径 / `extract_fulltext` integer 坑 / 互动问答 exact=0 纪律 / buyback 无单位推算注）；
  `report-skeleton.md` §7 输出形式加固定件「矛盾申报行」（L3↔L1 冲突列两值、采信 L1、报位置；美的扣非方向案例注）；
  本文件补上列 Verified；`README.md`/`README.en.md` 边界表「端到端未实测」行改为 P1 已实测+三类剩余未测面。

### 已知未做（有意留白）

- `scripts/check_note.py` 四道门禁与 fixtures 已随包入账（工项 B；P1 终态 exit 0、回归 9/9）。
- 合规词表维持自写最小黑名单。
- 行情/估值数值流设计上不依赖（`equity_market` 未开放期间不承诺）。
