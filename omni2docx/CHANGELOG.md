# CHANGELOG(omni2docx)

### 0.1.2 — 2026-10-10（大结果取数路径改正为条件句：按该 part 的存储形制分流＋选 detail 口径）

- 凭据＝双 part artifact 实据的四条读数（①侧车可按游标分块读回，条件是服务端把该 part 判为 artifact，游标绑死 part 与 offset；②`save_result` 只交 content，两种交付形制都交不出侧车；③`result_delivery_effective` 四种组合都不回显于 MCP 回执；④换 detail 只换侧车表示、正文不动）。本轮未复跑任何付费件，字节数与跳数以那份账为准，成品面只写形制不写数。
- 「解析侧能力现状」表：content／grounded 两行由「从内联回执取」改为**按该 part 的 `storage.kind` 现值分流**；`read_result` 行状态由「条件可用」改判为**按 part 分流时可用**，并写明游标绑 part 与 offset、跨 part 借游标或自造前进 offset 一律 `INVALID_RESULT_CURSOR`（`retryable:false`、`billed:false`），且 `result_delivery_effective` 不回显、不得据请求值推交付形制。
- 工作流「使用纪律」块与步骤 1 新增**大件分支**段：`inline` 直取回执、`artifact` 顺游标逐跳到 `next_cursor` 消失并与声明 digest 对拍（实测无损）；**两枚 part 各走各路不混用**，内联侧车要当场整段存住（事后无游标可补取），`save_result` 导出件两种形制都只交正文一枚、Bridge 私有缓存不是公开面本件不依赖。`result_delivery` 项把「小包两枚 part 仍内联返回」改为由该 part 自身字节数判定的表述。
- 选 detail 口径句落地（步骤 1 的 `detail` 项＋已知限制第 1 条）：要页码用 `grounded`、要坐标用 `layout`，**换 detail 不动正文**——同一件在两种表示下 content 的字节与 digest 实测逐字同值，选「页码保真」还是「版面坐标」不必重跑正文核对；同时明写本件映射引擎当前消费页级锚、layout 消费属后续阶段（不把未接上的能力写成已接）。
- `README.md`／`README.en.md` 同步三处：取数纪律段、命令注释行、能力边界两枚 bullet（双语对点，未增裸中文散文句）。
- 代码零动：`build_docx.py`／`validate_docx.py` 与夹具一字未改——本轮改的是取数路径的描述与分流条件，引擎消费什么形制由中间 JSON 决定，与取数分支无关。
- 版本位：0.1.1 → 0.1.2（取数分支与流程表述的改正＝patch，无新增能力；本件唯一版本锁在 `SKILL.md`，改后该面旧字面复算＝0，历史条目里的 0.1.1 不回改）。
- 复验（取脚本自报行）：`check_skills.py --strict` 本包 OK v0.1.2、全仓 17 skill(s), 0 error(s), 0 warning(s)；成品面逐面卫生闸 exit 0；旧句「从 parse 内联回执取」「不必也不靠这个工具」grep＝0 命中，条件句关键词（游标／以实际返回／`storage.kind`）在同段共现；同一 markdown 双跑引擎出口逐字节一致。

### 0.1.1 — 2026-10-10（取数可靠性句改写＋误喂输入的指引化）

- 取数第一性改为**只依赖 `parse` / `get_parse_status` 的内联回执**：content 与 grounding 两枚 part 随回执同进程返回；请求 artifact 形制时小包仍内联返回，一切以实际返回为准。
- `read_outline` / `read_result` 由「可用」改判为**可选续调用、不保证可得**：同一 result_id 上可返回不可重试的 `RESULT_NOT_FOUND`（同时刻落盘类调用仍可成功），无 cursor 时 `read_result` 无法起步。不可得时不重试、不报故障、不猜原因——直接由引擎从干净 markdown 重建章节层级，**outline 缺省是本件常规路径**。原「同会话即天然直接可用」「跨进程属自造假故障」两句撤除（前者把充分条件写成保证，后者把责任写死给调用方，事实都不支持）。
- 能力现状表两行状态列改为可核对形制（可用条件＋不可得时行为），不再裸判「可用」；已知限制第 2 条同改；`README.md` 与 `README.en.md` 各三处同步，与主指令不互相矛盾。
- 路径成立性本轮复跑取到：一份 7 页研报的中间件（键集 detail/grounding/markdown/source，**无 outline 字段**，正文 20,153 字节）喂引擎仍打印 `blocks=117 outline_nodes=62 toc=True segments=7 pagebreaks=6`、退码 0，校验判定 PASS——「outline 缺省仍能重建目录」是实测形制，不是兜底说辞。
- 输入护栏：`--json` 指向不可解析内容（整份 markdown 误喂、或非法字节流）不再抛裸 traceback，退码 1 并给出「整份 markdown 请改用 `--md` 直出；中间 JSON 按步骤 2 从回执组装」的可执行指引。探针三则：误喂 markdown exit=1 且 stderr 含 `--md`、不含 Traceback；形状错守卫句原样不退化；真中间件正例 exit=0。
- 版本位：0.1.0 → 0.1.1（文案与报错形制整改＝patch，无能力增减）。名述面三枚现测：displayName 23／summary 70／description 298（脚本实测，非手数；距 300 上限仅余 2 字，入债务册）。

### 0.1.0 — 2026-10-10（首发）

- 双层管线：Omni 原生 `parse`（grounded）→ 中间 JSON（markdown+grounding+outline）→ `build_docx.py` 渲染；agent markdown 产物可 `--md` 直出（免中间 JSON，不依赖解析层）。
- 映射能力：grounded 页锚点→源页分页符；官方 outline→真 Heading+可见目录（缺失时从 markdown 保守重建：中文序号 H1/指数型 H2/`###` 标题）；GFM 表格（列一致性护栏）；脚注上标+文末注释节；〔来源〕灰色小字；溯源标注段（【画面】/【说话人N 时间段】/【图说】带底纹）；base64 图像引用剥离字节留说明。
- 多源合并：`sources` 每源一章 + 总目录 + 章间分页 + 文末「证据溯源附录」（页码范围/画面时间点/说话人转写段自动回灌成表）；`analysis` 渲染为首章。
- 排版：`--profile` 五预设（gov 公文 GB/T 9704 / legal / finance / academic / default）+ 内联 JSON/.json 文件任意参数覆盖（字体/字号/行距/缩进/页边距/表样式，行距接受 `28pt`/`1.5倍` 等字符串）；标题黑色+层级字号、零 CJK 伪斜体；`--page-numbers` 页脚 PAGE 域；`--strip-emoji` 剥离装饰符；`--page-marks` 页边界源页码标注。
- 校验：`validate_docx.py` 字符级 CJK 覆盖率（≥99% PASS）+ 锚句命中 + 结构统计，与 `--strip-emoji` 同口径防误报。
- 实测：真实语料矩阵 12 例（xlsx/PDF 研报/债券书/HTML/音频/docx/PPTX/JPG OCR/千页 PDF/截断 PDF/边界×2）× 多制式，覆盖率全部 100%；端到端（原生 parse→渲染→校验）通过。已知限制见 README「能力边界」。
