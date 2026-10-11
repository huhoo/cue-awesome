---
name: omni2docx
slug: cue-omni2docx
displayName: "Omni 解析转 Word·HTML·PPT"
summary: "把 Omni 解析结果重建为保真 .docx、展示 HTML、汇报 PPT：源页分页、真标题目录、溯源标注还原，按场景制式排版。"
description: "将 Omni 解析结果重建为保真 Word / 展示 HTML / 汇报 PPT：grounded 页锚点→源页分页、outline→真标题+目录、表格/脚注/溯源标注还原，多源合并带证据溯源附录；--profile 按公文/诉讼/研报制式排版，HTML 可 --pdf 导出打印件。Do NOT use for: 像素级版面复刻、无 omni-reader 的解析层能力（--md 直出除外）；Triggers: Omni 转 Word/HTML/PPT / 保真重建 / 多源证据整合 / 扫描件转 Word; omni to docx / parse to deck"
version: "0.2.1"
license: MIT
metadata:
  requires:
    bins: ["python3"]
tags: [文档转换, Word, HTML, PPT, 解析重建, 公文, 诉讼, 研报]
---

# omni2docx — 双层管线：Omni 解析（Agent 层）× 格式生成（人层）

## 前置条件

| 依赖                                                           | 用途                                     | 缺失时                                                                              |
| ------------------------------------------------------------ | -------------------------------------- | -------------------------------------------------------------------------------- |
| **omni-reader MCP** 已连接（Bridge 就绪）                           | 解析层：parse / read_outline / read_result | 场景②③（grounded 重建/多源合并）不可用，先引导用户安装配置 omni-reader MCP；**场景①（--md 直出）不依赖 omni，仍可用** |
| **Python 3.9+ 且已装 `python-docx`**（`pip install python-docx`） | 渲染层：build_docx.py / validate_docx.py   | 引擎无法运行，先装依赖；调用方式用用户环境通用的 `python`，不假设任何特定安装路径                                    |
| **`python-pptx`**（`pip install python-pptx`；仅 PPTX 输出）  | 汇报渲染：render_pptx.py                    | 仅 PPTX 不可用；docx / HTML 输出不受影响                                                                  |
| **headless 浏览器**（Edge/Chrome/Chromium；仅 `--pdf`）      | HTML → 打印件 PDF                        | 明确提示"未找到浏览器，跳过 PDF"，**不静默失败**；用户装浏览器后再跑 `--pdf` 即可                                          |

- 跨平台：引擎为纯 Python + python-docx，Windows / macOS / Linux 均可运行；示例命令用相对路径与 `python`，不写死文件系统布局。
- 字体说明：预设制式用中文字体名（宋体/黑体/仿宋_GB2312/楷体）。docx 只携带字体名，在非 Windows 环境打开时 Word/WPS 会自动替换为本机字体；公文/法律等制式文档建议在 Windows/WPS 环境打开验收。

## 定位：完整链路，两个环节有效组合

**完整链路 = 多模态解析（给 agent）→ agent 整合分析 → 按需生成文档（给人）。  
生成阶段把解析侧已算出的元数据（grounding / outline / 画面时间点 / 说话人转写）  
再利用回文档——通用转换工具拿不到这些元数据，这是超越普通转换的核心。**

本 skill 是链路的组合器：

```
用户文件（PDF/扫描件/音视频/网页…）
   │  ① Agent 层：Omni parse（grounded）→ markdown + grounding + outline
   ▼     agent 据此推理：摘要 / 对比 / 抽取 / 整合 / 文书起草
Agent 工作产物（markdown，可带 [^n] 引用与〔来源：…〕标注）
   │  ② 人层：同一渲染引擎，两种输入
   ├─ 输入 A 原文重建：解析 markdown + grounding → 页级保真 docx（场景②③）
   └─ 输入 B 产物直出：--md file.md → 专业排版 docx（场景①，免中间 JSON）
   ▼
人可读可编辑的 docx：封面 / 目录 / 真标题 / 表格 / 溯源标注 / 上标引用 + 注释 / 页码标注 / 证据溯源附录
```

组合的粘合点（让人能追溯 agent 的话）：

- `[^n]` 脚注引用 → Word **上标编号**，文末自动生成「注释」节
- `〔来源：视频帧 00:46〕` → **灰色小字**行内标注
- 溯源标注段（【画面】/【说话人】/【图说】/【图片】）保留 Omni 的视觉/转写证据
- **证据溯源附录**（合并模式自动）：各源的源页码范围 / 画面时间点 / 说话人转写段  
  由解析元数据回灌成表格，人按页码/时间点直接对照原件

## 三大使用场景（按用户痛点设计）

| 场景                                 | 痛点                                      | 本 skill 对应能力                                                                                                                                            |
| ---------------------------------- | --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **① Agent 产出 → 可交付文档**             | agent 默认生成 markdown，用户实际要 docx/pptx/pdf | 引擎天然支持**纯 markdown 输入**（无 grounding/outline 自动降级）：中文标题重建 + 真 TOC + 宋体/黑体 + 表格/列表/行内样式。后续接 PPTX/PDF 输出                                                   |
| **② Scanned PDF/不可编辑件 → 可编辑 Word** | 转换后版式对不上，核对/编辑工作量大                      | Omni 解析 scanned PDF → **页级分页保真**（grounded 源页锚点）；`--page-marks` 在每页边界标注「── 源第 N 页 ──」，改稿时直接对照原件；扫描件里的图章/签名/照片由 Omni 转成视觉描述，引擎渲染为带底纹的【图说】标注段              |
| **③ 多源证据整合 → 诉讼文书等**               | 证据来自截图/录音/照片/视频/规章，需保留各自格式与可溯源引用        | **多源合并模式**（`sources` 数组 → 每源一章 + 总目录 + 章间分页）；录音转写 `[说话人0 00:00-01:20]` → **说话人+时间戳标注段**（正文色，可直接引用"某时某人说"）；视频帧 `[画面 HH:MM]` → 带底纹视觉描述段；图像引用剥离 base64 留说明 |

## 输出格式：按用途选（agent 判断，不硬编码映射）

同一份解析结果可渲染为四种交付物，**选哪个取决于文档拿去干什么**——由 agent 结合场景知识判断，必要时向用户确认：

| 交付物     | 用途        | 语义                                                    | 引擎                                      | 依赖                                   |
| ------- | --------- | ----------------------------------------------------- | --------------------------------------- | ------------------------------------ |
| **docx** | 递交 / 编辑 / 归档 | **保真**：grounded 页锚点→分页符、outline→真标题+目录、表格/脚注/溯源标注逐项还原     | `scripts/build_docx.py`                 | python-docx                          |
| **HTML** | **展示**    | **可读可分享**：自包含单文件、目录锚点跳转、源页标注、表格/引用还原、打印样式；`--pdf` 可导打印件 | `scripts/render_html.py`                | 无额外（PDF 需本机 headless 浏览器）           |
| **PPTX** | **汇报**    | **可讲**：标题页/章节页/要点页/表格页；**要点上页、正文细节进演讲者备注**；超页自动续页并告警    | `scripts/render_pptx.py`                | python-pptx                          |
| **PDF**  | 打印 / 定稿   | 走 HTML→headless 浏览器打印，与 HTML 版面一致（不做像素级复刻）             | `render_html.py --pdf`                  | Edge/Chrome/Chromium                 |

**汇报（PPTX）的协作约定**：引擎不替 agent 决定讲什么。agent 按 slide 组织 markdown（`##` 一页、要点用列表、数据用表格），引擎只负责映射与制式；直接喂长文档时引擎按层级切页并对 `≤--split-level` 的标题分页，正文进备注，`--max-slides`（默认 80）兜底截断并提示先提炼。

## 为什么不是又一个 markdown→docx

通用转换（tencent-docx / html-to-docx / pandoc）只拿到 Omni 的**纯 markdown**，  
丢失了 Omni 解析时已算出的结构化信息，且中文排版粗糙：

| 维度      | 纯 markdown 转换（现有）                                     | 本 skill（消费 Omni 解析侧能力）                                                                   |
| ------- | ----------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| 源页边界    | 完全无知，只能吐连续正文                                          | **grounded 页锚点 → Word 分页符**（页级保真）                                                        |
| 标题层级    | LLM 猜 `#` 级别；PDF 正文无 `#` 的章节（"一、美国""1.标普 500 指数"）被当正文 | 从 Omni 干净 markdown 保守重建（中文序号 H1 + 指数型 H2 + 文档自带 `###` 标题）→ 真 Heading + 可见目录              |
| 目录 TOC  | 需重抽/猜                                                 | 文首生成**按层级缩进的可见目录**                                                                       |
| 中文渲染    | 西文字体渲染中文，字体不一致/缺字                                     | 正文宋体、标题黑体（设 `w:eastAsia`），贴近中文研报排版                                                       |
| 阅读顺序    | 单栏 OK，多栏乱                                             | grounded 序列保证顺序                                                                          |
| 表格      | 折叠多栏弱点                                                | GFM 表 → Word 表（列一致性护栏防破碎）；有序/无序列表；行内样式                                                   |
| 多模态视觉理解 | 图像引用/base64 原样塞进文档，画面描述混入正文                           | 视频帧 `[画面 HH:MM]` 与场景描述 → **带底纹的【画面】/【图说】标注段**；`![alt](data:base64…)` 剥离字节、保留说明（【图片：alt】） |
| 保真      | 软换行引入多余空格                                             | `clean_cjk_spaces` 消除中文间多余空格，字符零丢失（实测 100%）                                              |

> 一句话差异化：**通用转换丢结构、排版糙；本 skill 用 Omni 的 grounded 分页 + 章节重建 + 专业中文排版把结构与原貌重建回来。**

## 解析侧能力现状

| 能力                | 状态                 | 本 skill 用法                                                                                                                                                                                                                   |
| ----------------- | ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| content（markdown） | ✅ 可用               | **按该 part 的 `storage.kind` 现值取**：`inline` 直取 `structuredContent.result.parts.content.storage.text`；被判 `artifact` 才顺游标逐跳读回（见步骤 1 大件分支）                                                                                     |
| grounded（页锚点）     | ✅ 可用               | 同上分流：`inline` 取 `parts.grounding.storage.value`（页级锚点），被判 `artifact` 才走游标。`save_result` 实测两种交付形制下都只交正文一枚文件、侧车交不出，所以内联侧车要当场整段存住                                                            |
| `read_result` 工具  | **按 part 分流时可用**     | 起步必须有服务端为该 part 逐跳发出的游标；游标是 base64(JSON)＋签名，**绑死 part 与 offset**——跨 part 借游标、自造前进 offset 一律 `INVALID_RESULT_CURSOR`（`retryable:false`、`billed:false`），没有自主跳转的公开出口。**取数第一性＝回执里各 part 自己的 `storage.kind` 现值**：`inline` 直取（`parts.content.storage.text` 与 `parts.grounding.storage.value`），`artifact` 才用本工具逐跳读回（实测字节级无损）。`result_delivery_effective` 不回显于 MCP 回执，故不得据请求值推交付形制；起步失败时不重试、不报故障，按回执现值继续 |
| `read_outline` 工具 | **不保证可得**         | 可选续调用，**可能不可得**：同一 result_id 上可返回 `RESULT_NOT_FOUND`（含 `retryable:false`），而同一时刻 `save_result`／`get_parse_status` 仍成功。因此 **outline 缺省是本件的常规路径**——引擎从干净 markdown 重建章节层级，不重试、不报故障、不猜原因。可得时（`coverage=complete`）引擎优先采用官方层级；`coverage=none, nodes=[]`＝文档无可识别标题，属正常语义 |
| layout（逐元素 bbox）  | ✅ 可用               | `detail=layout` 实测 COMPLETED，`segments[].layout.items[]` 带 `bbox`/`font`/`size`，`availability=available`。若遇故障不预设结论（瞬时/条件触发/低频均有可能）——先排除调用侧问题，仍失败则降级 `grounded` 并如实报告                                                         |

## 排版能力（--profile）：制式由 agent 按场景知识决定

**用户要什么文档、用在什么场景、该满足什么制式要求——这些判断交给 agent 的大模型能力  
与领域知识现场决策，本 skill 不预设"什么场景必须怎样"的硬规则。** skill 只负责把  
排版能力完整暴露出来，供 agent 任意组合：

引擎可控参数（`--profile` 接受三种形态：预设名 / 内联 JSON / .json 文件）：

| 参数                                              | 含义                                                       |
| ----------------------------------------------- | -------------------------------------------------------- |
| `body_east` / `body_latin` / `body_size`        | 正文中文字体（设 `w:eastAsia`）/ 西文字体 / 字号 pt                     |
| `heading_east` / `heading_sizes` / `title_size` | 标题中文字体 / H1–H6 字号数组 / 封面字号                               |
| `line_spacing`                                  | 行距：≥12 视为固定磅值，否则为倍数（如 1.5）                               |
| `first_line_indent`                             | 首行缩进字符数（按 body_size 换算 pt）                               |
| `margins_cm`                                    | 页边距 `{top,bottom,left,right}` cm                         |
| `table_style`                                   | Word 表样式名（`Table Grid`=朴素黑框 / `Light Grid Accent 1`=强调色） |

**内置预设只是参考值，不是决策规则**（agent 可直接用、可改、可完全自定义）：  
`gov`（公文 GB/T 9704：仿宋_GB2312 三号/28 磅/缩进 2 字/GB 页边距）、  
`legal`（诉讼：仿宋四号/24 磅）、`finance`（研报：宋体五号）、  
`academic`（论文：宋体小四/1.5 倍）、`default`（通用宋体）。

**排版质量基线（引擎强制，全制式统一）**：标题/封面一律黑色并按层级设字号  
（覆盖 Office 模板默认蓝色与"标题不大于正文"的层级崩塌）；全文零 CJK 伪斜体  
（引用/图说/图片说明用灰色区分，含中文的 `_强调_` 渲染为加粗）。

**对解析信息的利用选择同样交给 agent。** 引擎提供的能力开关：  
`--page-marks`（页边界标源页码）、`--no-toc` / `--no-pagebreak` / `--no-appendix`  
（关目录/分页/溯源附录）、profile 自定义（含溯源标注与表格的取舍空间）。  
agent 按对场景的理解自行决定取舍——例如诉讼证据文书通常需要页码标注与溯源附录、  
公文通常收紧目录与标注篇幅、研报优先表格数据完整——但**这些是场景知识，不是 skill 规则**；  
用户场景特殊（如内部规范有自己的制式）时 agent 应依用户事实构造自定义 profile。

### 与用户的交互原则

需要向用户澄清或确认时由 agent 自行把握分寸，skill 只定两条底线：

- 上下文已能判断的事（场景、制式、取舍）**直接做并说明一句**，不追问；
- 确需提问时**一次问清、给选项带默认**，排版细节（字体字号等）由制式承载，不烦用户。

## 工作流（必须用 Omni 原生工具取数，不自造解析器）

> **使用纪律**：取数按**回执里各 part 自己声明的 `storage.kind`** 分流——`inline` 就直接从
> `parse` / `get_parse_status` 的回执取整段文本，被判 `artifact` 的 part 才用 `read_result`
> 顺服务端为该 part 发的游标逐跳读回（字节级无损已验，见步骤 1 的大件分支）。
> **请求 `result_delivery="artifact"` 不改变实际交付形制**，`result_delivery_effective` 也不回显在
> MCP 回执里，所以分流依据只有回执现值这一条。
> `read_*` 两个续调用按条件走：`read_result` 只在对应 part 有游标时起步；`read_outline` 仍属
> **不保证可得**的可选支路——不可得（`RESULT_NOT_FOUND`／无 cursor 可起步）就走内联回执与引擎重建，
> 不把它当故障处理，也不预设原因。

### 步骤 1 — 原生 parse（grounded，内联取数）

调用 `mcp__omni_reader__parse`：

- `source`：本地文件路径（须在 omni 允许的根目录内，即 Bridge 的 allowed roots）或 URL。
- `detail`：本件产页级 docx，取 `"grounded"`；要元素级坐标（`bbox`/`font`/`size`）时改取 `"layout"`——
  **换 detail 不动正文**：同一件文档在两种表示下 content part 的字节与 digest 实测逐字同值，改的只是
  侧车表示（侧车是否走 artifact 只看该 part 自身的字节数，与请求值无关）。所以「要页码用 grounded、
  要坐标用 layout」可按需求选，不必因为换了 detail 就重跑正文核对。注意本件映射引擎当前消费的是
  页级锚，取 layout 时坐标字段照存进中间 JSON，版面级重建属后续阶段。
- `result_delivery`：`"artifact"`。**请求 artifact 不改变实际交付形制**：走 inline 还是 artifact 由
  该 part 自身的字节数单独决定（与另一枚 part 无关、与请求值无关），而 `result_delivery_effective`
  不回显在 MCP 回执里——本地记录里有、回执里没有，所以文案与判断都只写实际返回。  
  轮询 `mcp__omni_reader__get_parse_status` 至 `COMPLETED`。

**取数（按回执里该 part 的 `storage.kind` 现值分流）**：解析 `parse` 最终回执的  
`structuredContent.result.parts`：

- `parts.content.storage.text` → markdown 正文
- `parts.grounding.storage.value`（kind=`inline`）→ `omni.grounding.v1` bundle

**大件分支（正文被判 artifact 时）**：`kind=artifact` 的 part 随回执带 `next_cursor`，顺它逐跳
调 `read_result` 读到 `next_cursor` 消失，再把各跳字节按序拼回，与回执声明的 `parts.<part>.digest`
对拍（实测按游标读回是字节级无损的；每跳上限由服务端定，跳长会字符边界让位，不切 UTF-8 字符）。
游标是 base64(JSON)＋签名，**同时绑死 part 与 offset**：跨 part 借游标、自造前进 offset 一律返回
`INVALID_RESULT_CURSOR`（`retryable:false`、`billed:false`），不存在自主跳转的公开出口。
**两枚 part 各走各的路径，不混用**：`inline` 的侧车必须当场从回执整段存住（事后无游标可补取，
`save_result` 也交不出侧车——实测两种交付形制下它都只落正文一枚文件），被判 `artifact` 的侧车才按
游标逐跳读回；Bridge 的私有缓存不是公开面，本件不依赖它。

**可选官方 outline（不保证可得）**：若要从 `get_parse_status` 回执取 `local_result_cache.result_id`
试一次 `read_outline(result_id)` → `{coverage, nodes:[{id, level, title}]}`，
可得即优先采用官方层级，**层级深浅以返货自报的 coverage 值为准**；**不可得是本件常规路径**——直接落盘不带 `outline` 字段，引擎从 markdown 重建目录，不重试、不报故障。

- `coverage=none, nodes=[]` = 文档无可识别标题（正常语义，非故障），此时落盘不写 `outline` 字段、引擎走 markdown 重建。
- 有节点时写入 JSON `outline` 字段，引擎自动优先使用官方层级（引擎兼容 `{coverage,nodes}` 原样传入）。
- ⚠️ **可得性以实际返回为准**：该续调用与缓存条目、进程状态、有效期都相关；同一 result_id 上
  三次调用可能全部返回不可重试的 `RESULT_NOT_FOUND`，此时**盘上的结果文件依然在**（`save_result`
  仍可能成功），所以不得据此判定文档损坏，也不得据此向用户报故障。

### 步骤 2 — 落盘中间 JSON

```json
{
  "markdown": "<步骤1 parts.content.storage.text>",
  "grounding": <步骤1 parts.grounding.storage.value>,
  "outline": <可得时的 {coverage, nodes}；不可得或 coverage=none 时省略该字段>,
  "source": "<源文件描述>",
  "detail": "grounded"
}
```


- `outline` 提供且 coverage=complete 时引擎**优先用官方层级**；缺失或 none 时从 markdown 重建。

### 步骤 3 — 运行渲染引擎（按场景选格式）

```
# Word：保真重建（递交/编辑/归档）
python <skill_dir>/scripts/build_docx.py --json <中间json> --out <输出.docx>
python <skill_dir>/scripts/build_docx.py --md <agent产出.md> --out <输出.docx>

# HTML：展示（浏览器打开 / 分享 / 可打印）
python <skill_dir>/scripts/render_html.py --json <中间json> --out <输出.html> --profile gov
python <skill_dir>/scripts/render_html.py --md <agent产出.md> --out <输出.html> --pdf   # 同时导出 PDF

# PPT：汇报（deck，要点上页、细节进备注）
python <skill_dir>/scripts/render_pptx.py --md <slide提纲.md> --out <输出.pptx> --profile finance
python <skill_dir>/scripts/render_pptx.py --json <中间json> --out <输出.pptx> --max-slides 30
```

- 自动：封面标题提取（"标题：xxx"）→ 中文字体 → markdown 章节重建 → 真标题 +  
  文首目录 → grounded 源页分页符 → 表格/列表/引用/行内样式 → 脚注上标 + 文末注释 +  
  〔来源〕灰标 → 溯源标注段。
- `--no-pagebreak` 忽略分页；`--no-toc` 忽略章节重建（仅纯 markdown + 表格/列表）；  
  `--page-marks` 分页处标注「源第 N 页」（核对原件）；`--profile` 套制式——预设名  
  （gov/legal/finance/academic/default）或自定义 JSON（内联或 .json 文件，参数见上节表）。

### 步骤 4 — 验收（产品级，必做）

对产出做保真 + 结构校验，确认**字符零丢失（覆盖率≥99%）**且分页/标题/表格数量  
符合预期，再 `present_files` 交付。三种格式各有对应验收器（`--json`/`--md` 与渲染  
时输入保持一致）：

```
python <skill_dir>/validate_docx.py --json <中间json> --docx <输出.docx>
python <skill_dir>/validate_html.py --json <中间json> --html <输出.html>   # 或 --md <源md>
python <skill_dir>/validate_pptx.py --json <中间json> --pptx <输出.pptx>   # 备注/正文/表格合并计入覆盖口径
```

### 步骤 5 — 交付

`present_files` 打开/交付 `.docx` / `.html` / `.pptx`（`.html` 可在内置预览直接看）。

## 映射引擎字段约定（build_docx.py）

| 输入字段                | 必填 | 说明                                                                                                                                             |
| ------------------- | -- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| `markdown`          | 是  | GFM / 纯文本 markdown（UTF-8）                                                                                                                      |
| `grounding`         | 否  | `omni.grounding.v1` bundle                                                                                                                     |
| `outline`           | 否  | `{coverage, nodes:[{level,title}]}`（兼容 nodes 直接为数组或包在 `{outline:...}`）；提供则优先于重建                                                                |
| `source` / `detail` | 否  | 仅写入 docx 属性 / 日志                                                                                                                               |
| `title` + `sources` | 否  | **多源合并模式**：`sources: [{markdown, grounding?, outline?, source}, ...]`，每源一章（H1=source 名，章间分页），总目录前置（章内层级自动 +1），`title` 为文档封面标题                  |
| `analysis`          | 否  | **agent 整合分析产物** `{markdown, source?}`：渲染为合并文档**首章**（[^n] 引用/〔来源〕标注照常），排在各证据源之前                                                                |
| （合并模式自动）            | —  | 文末自动生&#x6210;**「证据溯源附录」**：把各源 grounding 页锚点（源第 N–M 页）、画面时间点（首/末时间戳）、说话人转写段（数量/说话人/起始时间）、outline 章节数回灌成表格，并自动推断源类型；`--no-appendix` 关闭，附录条目纳入总目录 |

内部逻辑：

- **封面标题**：行首 `标题：xxx` 提取为 Word `Title` 样式（研报/文章常见），并从正文去除以免重复。
- **中文字体**：正文 `宋体`、标题/封面 `黑体`，均设 `w:eastAsia`，避免西文字体渲染中文导致缺字/不一致。
- **章节重建（无 outline 时）**：从 markdown 保守识别三类高置信结构 —— 行首中文序号 `一、二、…`  
  → H1；`N.XX指数` → H2（以"指数"识别，排除含 ETF/基金代码的推荐列表项）；文档自带  
  `###` 标题 → 对应 H1–H6。**有 outline 字段时跳过重建、用官方层级。**
- **outline 消费**（当提供）：`nodes[].title` 与 markdown 段落做规范化前缀匹配（兼容段落开头的  
  "一、"/"1." 等章节序号），命中即提升为对应 `level` 的 Heading；标题只取匹配前缀，余下作正文  
  （避免把整段长描述提升为标题）。
- **保真拼接**：段落按软换行拼接后用 `clean_cjk_spaces` 删除紧贴 CJK 字符的多余空格  
  （"核心 资产"→"核心资产"），保留英文词间空格。
- **grounded 消费**：`segments[].content_range_utf8` 为 UTF-8 **字节**偏移，引擎内部做  
  字节→字符换算；相邻段落源页变化时插入 `w:br w:type="page"`（首页不插）。
- **表格护栏**：列数不一致的"假表"（Omni 偶发锯齿布局表）降级为段落渲染，避免破碎表格；  
  列数一致的真实表格（如财务表）正常还原为 Word 表（表头加粗）。
- **多模态溯源标注**：Omni 解析视频/图片/音频/网页时不返回图像/音频字节，但产出  
  **文本形式的溯源标注**。引擎以高置信前缀识别并渲染为与正文明显区分的标注段：
  - `[画面 00:48] 场景: …` / `场景：` / `这张图片` / `图：` → **【画面】/【图说】**（灰斜体 + 底纹，Omni"看见的"）
  - `[说话人0 00:00-01:20] …` / `[00:48] …` → **【说话人N 时间段】**（标签加粗蓝 + 正文色，**可直接引用**——录音/视频证据场景）
  - `![alt](data:image;base64,…)` 剥离字节仅保留说明（【图片：alt】），纯装饰图丢弃
- **优雅降级**：无 outline → 无 TOC/标题提升（仍分页）；无 grounding → 无分页；纯 markdown（场景①）全部能力自动降级为基础渲染 + 中文标题重建。
- **引用渲染（agent→人粘合）**：`[^n]` 脚注引用 → 上标编号（深蓝），`[^n]: 定义` 行剥出，  
  文末自动渲染「注释」节；`〔…〕` → 灰色小字（约定放"来源：…"）。注释节随所在  
  文档/章节收尾，合并模式下每章各自收尾。

## 验收口径（真实数据实测通过）

两份**真实** Omni grounded parse 文档，经 `validate_docx.py` 校验：

| 文档                   | 字符覆盖率    | 分页符       | 标题/目录                             | 表格                                   |
| -------------------- | -------- | --------- | --------------------------------- | ------------------------------------ |
| ETF 文章（etf_real.pdf） | **100%** | 7 段→**6** | 6×H1(国家)+8×H2(指数) + 13 条目录 + 封面标题 | 0（基金池在文末被截断）                         |
| 券商研报（燕京啤酒 000729）    | **100%** | 4 段→**3** | 4×H3(###标题) + 目录                  | **5**（含"会计年度"5 列财务表，单元格数值与源一一对应，已抽检） |
| 金融短视频（mp4，多模态）       | **100%** | —         | **48 个【画面】标注段**全部带底纹，与正文区分        | —                                    |

| 网页（含 base64 图像引用） | **100%** | — | 2 处图像引用 → 【图片：alt】说明，base64 字节零残留（docx 136KB→40KB） | — |  
| 会议录音（m4a，场景③） | **100%** | — | **7/7 说话人转写段**带【说话人N 时间段】标签（加粗蓝，正文色可引用） | — |  
| 三源合并（视频+录音+研报，场景③） | **100%** | 章2 + 章3**5** | Title + 总目录 + 3 章 H1 + 章内 H4×4（层级与目录一致） | 5（研报章内完整保留） |  
| Agent 产物直出（--md，场景①） | **99.4%**（"标题"2 字被提为封面所致） | — | 封面 Title + 2×H1 + 3×H2 + 目录；**上标引用 1/2/3（正文+表格）+ 文末注释 3 条 + 〔来源〕灰标 4 处** | 1 |  
| **完整链路**（分析+视频+录音+研报，四源合一） | **100%** | 章间分页 + 研报章 3 | Title + 总目录（5 条 H1 含附录）+ 首章=agent 分析（上标引用+注释） | 6（研报 5 + **溯源附录表**） |

完整链路的**证据溯源附录**实测（元数据自动回灌，非手填）：

| 证据源                 | 类型（自动推断）    | 可溯源位置                                             |
| ------------------- | ----------- | ------------------------------------------------- |
| agent 整合分析          | 网页/文本       | 纯文本（无结构化锚点）                                       |
| 金融短视频               | 视频/图片（画面描述） | 48 个画面时间点（首 00:00 … 末 01:18）；1 段转写（说话人 0，00:00 起） |
| 录音 web.m4a          | 音视频（说话人转写）  | 7 段转写（说话人 0、1，00:00-01:20 起）                      |
| research_report.pdf | PDF/文档（页锚点） | 第 1–4 页                                           |

- 字节偏移换算：中文 6239 字符 = 14861 UTF-8 字节，映射无截断。
- 标题提升覆盖"段落型"与"有序列表型"小节；修复了"小节被并入父段落"导致吞掉子标题的缺陷。
- 真实财务表（会计年度/资产负债表/评级标准）列数一致，正确还原；真实研报 GFM 表格语法已确认（`| --- | --- |` 分隔）。

## 已知限制

1. 保真级别为**页级**（grounded）。元素级（bbox）数据可经 `detail=layout` 产出（实测  
   `layout.items[].bbox/font/size`），引擎消费 layout 的升级为后续阶段。**换 detail 不动正文**：
   同一件在 grounded 与 layout 下 content part 的字节与 digest 实测逐字同值，所以按需求在
   「页码保真」与「版面坐标」之间选，不必重跑正文核对。
2. `read_result` 是**按 part 分流的一环**：被判 `artifact` 的 part 顺服务端发的游标逐跳读回（实测
   字节级无损），`inline` 的 part 不需要它、也没有游标可起步。`read_outline` 仍是**不保证可得**的
   可选续调用（受缓存条目、进程状态与有效期共同影响；同一 result_id 上可返回不可重试的
   `RESULT_NOT_FOUND`）。**本件不依赖 outline 工作**：章节层级缺省由引擎从 markdown 重建——一条
   已实测的常规路径，不是降级异常；outline 可得时引擎优先采用官方层级。侧车一律不取
   `save_result` 的导出件：实测两种交付形制下它都只交正文一枚文件。
3. 段落跨源页边界时归入其起始字节所在页（MVP 简化）。
4. **图像/音频不嵌入，但溯源标注保留**：Omni 多模态解析不返回图像/音频字节，docx 亦不含  
   多媒体；但 Omni 产出的**文本溯源标注**（视频帧 `[画面 HH:MM]`、说话人转写  
   `[说话人N MM:SS-MM:SS]`、场景描述）由引擎识别并渲染为区分明显的标注段；  
   `![…](data:base64…)` 引用剥离字节、保留 alt 说明。
5. 复杂 markdown（嵌套表、脚注、数学公式）按文本降级；表格为**版式保真**非像素级还原。
6. **PPTX 是汇报 deck，不是版面复刻**：按标题层级切页、要点上页、正文进备注；不做"每源页一页"  
   的机械平铺，也不做像素级还原。表格按列数自动降字号，超长标题自动降字号。
7. **PDF 走 HTML 打印**（headless 浏览器），版面与 HTML 一致；本机无浏览器时明确提示跳过。  
   不做原生 PDF 排版（reportlab 路线），避免字体嵌入/分页/脚注的重复实现。
8. PDF 抽取/OCR 的**逐字母空格**（"T h e y"）不可还原词边界，不强修（强拼会产出  
   "demonstrateprecisionan" 这类错误串）；CJK 字间空格由 `clean_cjk_spaces` 正常消除。
