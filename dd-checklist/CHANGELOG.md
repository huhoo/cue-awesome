# 更新日志

本文件遵循 [Keep a Changelog](https://keepachangelog.com/) 与本仓 `CONTRIBUTING.md`；版本号以 `SKILL.md` frontmatter 为准。

## [0.1.0] — 2026-09-22 · 第二轮判卷修复（M73-M77；随 M76 复审 LGTM 同批入仓）

判词=`logs/pr-review-m70.md`（6.1 判 BLOCK，4 blocker，四条均如实标「未自跑=按可达输入推演」）；题单已扩 `DD-X15a–c / X16a–c / X17 / X18` 与 `good-X16-downgrade-accounted`，合同升为 **46 bad + 6 good = 52 样**（控制样另计，现 8 枚）。逐条：

- **B1 · 反向计数从未核 + 流水可被回写**：`check_coverage()` 的比对改为**两侧逐类**（账写「检到 1」而正文零行 = FAIL，配 `ctl-overclaim-row-missing`）；`evidence/calls.jsonl` 每行加 `seq` + `prev_sha256` 逐调用哈希链，checker 验链连续（断链/改序/回写前缀即 FAIL）。**边界写进 SKILL §7.8**：链只证同一次交付内部自洽，**不防整链重写**；能对抗整链伪造的外部锚只有服务端计费/调用回执与人工抽 3 对原文，故内外都不得据链下全称结论。
- **码族更正（承 M74 期间题单 02:43 修订）**：题单 §0.3 现明写 **`DD-OMISSION` 不得折回 `DD-COVERAGE`**——`DD-COVERAGE` 只管账的形制、枚举与账↔正文计数，「原始流水 → 交付」的因果断链是独立一道。我 M73 那版按**当时题面**（X16 写作 `诊断归属：DD-COVERAGE`、`不新造第八个码`）做了并族，现按新合同**恢复八道**：`check_dd.py` 三处流水门（流水在场性 / `M>N` 逐条理由 / 链连续与快照完整）回到 `DD-OMISSION`，X16a–c 与两枚 underreport 控制样的 `need=` 同步，`ctl-overclaim-row-missing`（账↔正文计数）留在 `DD-COVERAGE`；SKILL §6 加分工句、§3/§5/§7 与模板同改。**发现方式值得记**：不是靠眼看，是移出去的对账表脚本按新题单矩阵重跑时报 `ok=43/46` 且 exit 1，三行 ❌ 直接点名 X16a/b/c——脚本自证门禁又一次替人抓了漂移。
- **B2 · statute 同件不同法**：三件（法名/条号/短引）必须在**同一条法条记录**内共现，整份 JSON 当词袋不再算（`bad-X17`）。
- **B3 · 条件锚未按锚定位**：先在 evidence 内按条件锚定位到那条记录，再在**该记录内**核主体双标与在场日期；同文件他主体的记录不借光（`bad-X18`）。
- **B4 · 声明门是跨行词袋**：改为**标题后前 5 行内的同一物理行完整承载五要件**（标点空格归一），缺行/越界/跨行拼凑/笼统弱免责四形各一形 FAIL（`bad-X15a/b/c` + 原 `ctl-declaration-missing`）；SKILL §3 写入权威句式五要件与四形清单，题单 §1.2 基线已同步同款句式。
- 反证位（C-15 三性，改前实测）：`X15c`、`X17`、`X18`、`ctl-overclaim-row-missing` 四形在改门前全部 **exit 0 出门**（词袋/借光/反向计数三类漏口实测成立）；`X15a/X15b` 改前即被 M71 门拦下（如实记，不充作新功）。改后 52 样 + 8 控制样按精确码集全绿。

## [0.1.0] — 2026-09-22 · 第一轮判卷修复（M68，§v2 九条；复审 LGTM 后入仓）

契约升 `spec-dd-checklist-0.1.0.md` **§v2 九条**（lead 按判词落字），本题包按条改门并重建题库：

- **B1 空门** → §v2-2 零条目三条件；正路配对样 `good-zero-entries-evidence-backed`（有证据的零行表合法），坏样 `bad-X08-fake-zero-entries`（未发起伪装零条）拦 `DD-COVERAGE`。
- **B2 statute 散落字符串** → §v2-3 三元绑定（唯一 `kind=statute` 记录 / 三件**同件**逐字 / 主体侧条件锚 + 其证据）；坏样 `bad-X11/X12/X13`，`good-statute-derive` 同步升级为合法三元形状（不再是可被误伤的单件样）。
- **B3 subject 只认全称** → §v2-4 双形制；正路 `good-subject-code-only`（`--subject 600001.SH`）。
- **B4 覆盖率账是红线盲区** → §v2-1 交付面四件全扫；坏样 `bad-X10-redline-in-ledger`（账内注记写「建议回避」）拦 `DD-REDLINE`。
- **M1 降档塞其他类** → §v2-5 已知映射机检；坏样 `bad-X09-refile-to-other` 拦 `DD-TABLE`；「其他」类逐条归类理由入 SKILL §7 人工清单。
- **M2 runner 非精确码集** → §v2-6 runner 改**集合相等** + `ctl-runner-expect-extra-code` 负控自证（多码必判否）。**并更正本包旧申报**：M62 的「31/31 逐码相等」当时 runner 只做包含式检查，该申报**作废**（新表表头同注），正确口径以 M63 后的精确相等为准。
- **M3 B12 旧叙事** → 上方 Verified 段与评审侧 M62 对账表 §五 均改为指向题单勘误，不再写作悬而未决。
- **lead 自查抓出的空门（M71，2026-09-22）**：46 个样**无一个带 AI 初稿声明行**，而 SKILL 曾把它推给人工——同族 cn-earnings-note/catalyst-calendar 都是机检。现：`check_dd.py` 新增机器断言（标题后前 5 行内含「AI 初稿」+「不构成投资建议」类语义，缺=**`DD-INPUT`**）；`gen_fixtures.py` 一次性给全部样补权威句式行（含新增负控样 `ctl-declaration-missing`，现 **4 ctl**），幂等复跑零差异；SKILL §1 铁律 1 / §3 权威句式 / §6 码表 / §7.1 同步为「机检核在场与位置，语义人工抽读」。反证位：补行前对现成品样跑=exit 1 打 `DD-INPUT`，补行后 good 样 exit 0、38 坏样仍各自精确码集。
- **M4 40 字口径** → §v2-7 写入 SKILL §3（去空白后按 Unicode 码点计），并补 39/40/41 × CJK/中英混排边界控制样。

- **M72 精度边界补写（lead 验收补令）**：SKILL §6 加「理由行可归位」正反例（机器面止于词形+条数，归位与否归人工）、§7 加第 7/8 条——`hits=M` 由 `snapshot`+sha 绑定可核，但**整份快照被伪造低命中时流水与伪造件自洽**，属证据整体伪造同族、机器不自证，唯一防线是人工抽 3 对原文；并立对外文案禁令：**不得出现「绝对副词 + 漏报」型全称承诺句**（禁令自身不复述该句式，本件只承诺不齐即拦、归零即须逐条理由）（README 双语已按此写边界句）。- **反沉默漏报（§v2-10，lead 自查抓出的「多查少写」洞，2026-09-22 00:5x）**：新开第八道码 **`DD-OMISSION`**（与 `DD-COVERAGE` 可区分：' 
  前者=账比流水少写，后者=账形制不合法）——每类查询在 `evidence/calls.jsonl` 留一行流水承载**原始命中 M**；`检到 N < M` 须在 `progress.md` 逐条给降级理由行（窗外/归属不判/非本主体）；声称已查却无流水、理由不足、流水指向的快照被删或哈希被改，全部 FAIL。**删 source/evidence 不消除流水**。SKILL §4/§5/§6/§7 与 coverage-map-template 同步；三枚控制样入题库（`ctl-underreport-drop-row`、`ctl-underreport-drop-source` 各钉 `DD-OMISSION`；`ctl-underreport-with-reason` 带理由行 → exit 0，防恒真门）。lead 的三步复现（删行+改零+证据仍在）现值 exit 1 打 `DD-OMISSION`。正式题面候 6.1，落题后并入 exact-set。

- **M77 残值收口（对外一致性）**：包内仍四处写着「七道/七层/seven-layer」且 SKILL frontmatter 的码表漏列第八道 —— 外部使用者从入口就看不见反沉默漏报门。现：README 双语两处、`check_dd.py` 成功回包文案、SKILL frontmatter 码表（八道逐一注明各管什么，含 `DD-OMISSION`=反沉默漏报）全部对齐；`grep -rcE '七道|七层|seven-layer|seven diagnostic'` 四文件改前 4 处、改后 **0**。

### scripts（M69 裁定追加）

- 对账表生成器（反读题单矩阵 + 逐样真跑，题号↔样号双向断言、非精确码集即 exit 1）**不属本包**：它产的是我方逐题对账表，属内部工程件，M74 对外卫生裁定后移出至工作区 `scripts/`；本包只保留 `check_dd.py`、`fixtures/`（含 runner）与 `gen_fixtures.py`（题单为必填参数、无默认路径）。
- `gen_fixtures.py`：题库幂等重铺器（lead 裁定落包，理由=/tmp 曾被子系统清理、题库须可再生）。两条附带条件已实装：①**幂等**——跑一次后 `git status --porcelain dd-checklist/scripts/fixtures` 须为空（包未入库前以 `diff -r` 等价核验，已验零差异）；②**派生纪律写死在文件头**——改样必须先改题单（6.1 的合同），不得反向用脚本产出题单；生成器无判卷权，判卷与评审以仓内成品样为准。stdlib only、零网络、输出不含时间戳/路径/随机量。

## [0.1.0] — 2026-09-22

初始版本（套件第五件；契约=spec-dd-checklist-0.1.0 含 §v2 修订，验收合同=评审方题单（R0-I，不随本包发布）：首建 18 族拆 24 独立坏样 + 加题 7，M63 判卷后加题扩至 14、M70 判卷后再扩至 22（X15–X18），**合同现值=46 坏样 + 6 正路守护样**，逐题 1:1 落样（题号↔样号映射与真码集以评审方对账表为准，包内不留该表副本）；历次修复过程见上方两轮判卷修复段）。

### Added

- `SKILL.md`：输入契约（六参数全必传、一单一主体 ≤1、窗口由 `--asof`+`--lookback` 复算、`--purpose` 封闭三值）；七条铁律（AI 初稿声明/入类第一闸三条同时满足/只陈述不判断/无工具≠不存在/禁日期算术/无锚即删行+证据 fail-closed/花之前必问）；五段管线 `+scope → +facts → +derive → +coverage → +build` + 门禁 `+check`；输出契约（`report.md`/`sources.jsonl`/`evidence/`+`LEDGER.sha256`/`references/coverage-map.md`/`progress.md`）；中英双语触发词与「不用于」句（投资结论、法律定性、完备性宣称、多主体批量、前瞻日历、财报点评）。
- `references/channel-map.md`：九类目 × 域取数意图与锚型、运行时发现流程（不硬编码工具名与数量）、`coming_soon` 域不承诺、**P-10 前置事实**（`statute` 不含部门规章与交易所规则 → 法定推导路径预期零锚）、简称撞号与更名错位两个归属坑、降级与拒产表。
- `references/coverage-map-template.md`：固定五列账形制、「无工具／零条／未发起」三种未检到的区分、机器核什么（与 checker 逐条对应）、`--purpose` 三档的取数面加严口径。
- `README.md`/`README.en.md`：中文权威+英文译文对；文体按仓内反同质化条款自查（无期号连载、无从业者栏目、无效率百分比、无对照式宣言标题）。
- 设计要点：本件最大风险=**风险条目幻觉**，故机检按诊断码分层——`DD-INPUT/DD-TABLE/DD-ROW/DD-REDLINE/DD-COVERAGE/DD-EVIDENCE/DD-STATUTE`，判卷按码对（只 FAIL 不算接住，必须错在该错的那道门上）。

### scripts

- `check_dd.py`：七道门禁，stdlib only；六参数缺失即 `DD-INPUT` 且**不设默认窗口/默认目录**；红线扫**交付面四件**（`report.md`/`sources.jsonl`/`references/coverage-map.md`/`progress.md`，§v2-1；包级 README/SKILL 不属交付面）；**零条目三条件**（§v2-2：调用非空且在域枚举、对应零结果快照标出类目、正文检索域行为账内调用集子集）；**法定推导三元绑定**（§v2-3：唯一 `kind=statute` 记录 + 三件同件逐字 + 主体侧条件锚及其证据）；**subject 双形制**（§v2-4：纯代码+上市地合法，归属由证据内同代码全称完成）；**类目/档位对应机检**（§v2-5：`regulatory_cn` 监管函→合规与处罚、`ipo`→上市与在审状态、`fr_*`→财务与披露质量，命中而降档即 FAIL）；锚型白名单（URL/公告 AN 号/函件号/裁判文书号/`conv_id`/`statute` 原文锚）且**仅最后一列查锚**；红线扫描整份交付物与 `sources.jsonl`（无豁免区）；`evidence` fail-closed（目录空、文件未登记、哈希不符一律 `DD-EVIDENCE`）；归属判定按节作用域取标题主体，evidence 全称与 subject 不一致或简称撞号 → `DD-ROW`；崩溃折算为 FAIL，不以 traceback 代替判定。
- `fixtures/`（**历次快照**：M68 时合同为 38 坏样 + 5 正路守护样、另 3 枚 `ctl-*` 控制样；现值以包内 `scripts/fixtures/` 与评审方对账表为准）：`bad-B01…B24` 对应题单 18 族 24 样、`bad-X01…X14` 对应 6.1 加题 14 样；每样自带 `cmd.txt` 与 `expect.txt`（`exit=` + `need=` 允许码集 + 可选 `must-not=`/`verdict=`），基线段从题单 §1 复制、只改本题声明的差异，**零结果快照按账表内容自动补齐**（同一构造器生成，从源头免掉手抄漂移）。正路 5 样=`good-baseline`/`good-anchors-wide`（六种合法锚型 + 「审议通过」转述）/`good-statute-derive`（statute 三元齐的合法推导）/`good-zero-entries-evidence-backed`（有证据的零行表）/`good-subject-code-only`（纯代码+上市地形制）；`ctl-runner-expect-extra-code` 是 runner 负控（多缺陷样必须被按码判否），`ctl-boundary-40-pass`/`ctl-boundary-41-fail` 是 §v2-7 的 39/40/41 长度边界（CJK 与中英混排各测）。
- `fixtures/run_fixtures.sh`：独立 runner，逐样核 exit + **诊断码集合精确相等**（§v2-6：只查「包含」不算 1:1 判卷，多一个码即 FAIL），崩溃一律判不合格；`ctl-*` 支持 `verdict=must-fail` 反向自证；支持单样过滤（`run_fixtures.sh bad-B14`）。

### Verified

- 门禁自跑（M68 修后）：`bash scripts/fixtures/run_fixtures.sh` → **43 ok / 0 fail**（5 正路 exit 0，38 坏样 exit 1 **且码集与声明精确相等**）+ **controls 3 ok / 0 fail**；`scripts/check_skills.py` 0 error。逐题对账表=评审侧 M63 对账表（脚本反读题单矩阵生成，含真码集与是否精确相等两列，禁手写预期）。
- 稳健性负控：交付物缺失、`sources.jsonl` 非 JSON、`evidence` 目录不存在、`--lookback` 非法单位、LEDGER 登记幽灵文件——五种均 exit 1 且无 traceback。
- **DD-B12 日期方向（已闭合，非悬案）**：契约 spec §3「同一主体节内日期非降序」为唯一口径——由早及晚；题单 R0-I 已按此勘误（`2026-05-10 → 2025-05-10` 为倒序、须 FAIL），样与码（`DD-TABLE`）均按勘误后的题单落。
- *出门条件部分闭合*：对抗审已闭——M76 复审 **LGTM**（判词见评审侧 `logs/pr-review-m70.md`）；仍未闭的是真实单一主体端到端跑（spec §0 第 3 条，候授权实跑）与据此回填的 README 实况（第 4 条）。P2 上架与套件同闸冻结，push 与投放归 Owner。

