# CHANGELOG(omni2docx)

### 0.2.1 — 2026-10-11（验收闭环：HTML/PPTX 验收器 + 两处保真修复）

- 新增 `scripts/validate_html.py`：HTML 产物验收器，与 `validate_docx.py` 同口径（字符级 CJK 覆盖率 ≥99% 判 PASS，emoji 以 `--strip-emoji` 同口径从源文剥离防误报），附加目录/锚点/源页标注/溯源附录/自包含（无外链）结构检查；`--json`/`--md` 二选一，与渲染输入保持一致。
- 新增 `scripts/validate_pptx.py`：PPTX 产物验收器，**幻灯片正文 + 表格单元格 + 演讲者备注合并计入覆盖口径**（汇报版式"要点上页、正文进备注"）；附加空页/页数/表格/图像/截断检查。
- 修复 `render_pptx.py` 尾部正文静默丢失：deck 正常时，最后一段纯正文节（如免责声明）残留在 `pending_notes` 被丢弃——实测 61k 字法务研报覆盖率仅 66.86%；现追加到最后一张幻灯片备注，同源复测 99.17%（剩余 0.83% 为源文档逐页重复的页眉页脚 chrome 行，非正文）。
- 修复 `render_pptx.py` 空节标题丢失：标题下只有图片/分隔线的节（如"## 6. 图像与分隔"），标题只存 `cur_title`，被下一标题覆盖丢失；现空节标题保入备注流。
- 回归升级：`run_matrix_multi.py` 改为直接调用随包验收器（回归同时覆盖验收器本身），并新增专项用例——多源合并（3 源 + analysis）、`--md` 直出、空 markdown、纯表格，共 34 例全 PASS；docx 12 例矩阵回归无回归。
- 版本位：0.2.0 → 0.2.1（新增验收器 = minor 伴随修复，docx/HTML/PPTX 渲染口径不变）。

### 0.2.0 — 2026-10-11（多格式：展示 HTML + 汇报 PPT + 打印 PDF）

- 新增 `scripts/render_html.py`（展示）：把同一份解析结果渲染为**自包含单文件 HTML**——目录锚点跳转、源页标注（grounded）、GFM 表格/引用（楷体）/脚注尾注/溯源标注段还原，内联 CSS 按 `--profile` 制式（字体/字号/行距/首行缩进/页边距），打印样式 `@page A4`；`--pdf` 调用本机 headless 浏览器（Edge/Chrome/Chromium）导出打印件，缺浏览器时明确提示跳过、不静默失败。
- 新增 `scripts/render_pptx.py`（汇报）：标题页 / 章节页 / 要点页 / 表格页；**要点上页、正文细节进演讲者备注**（汇报语义，避免长文档被逐段平铺成上百页）；要点超 `--max-bullets`/`--max-chars` 自动续页；表格按列数降字号、超长标题自动降字号；支持 `data:image` 图像嵌入；无标题层级的文档有兜底分页；`--max-slides`（默认 80）截断并告警，提示先提炼提纲。
- 架构取舍：不重构为 block IR，采用**轻量契约**（markdown + grounding + outline + profile，各渲染器自消费），docx 引擎零改动、旧产出不受影响。
- 实测：真实语料 13 例 ×（HTML 覆盖率 + PPTX 页数/可打开）全 PASS，HTML CJK 覆盖率 100%；docx 侧 12 例矩阵回归无回归；HTML→PDF 打印件中文抽取 100%。

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
