---
name: omni2docx
slug: cue-omni2docx
displayName: "Omni 解析保真转 Word·源页分页带溯源"
summary: "把 Omni 解析结果重建为保真 .docx：源页分页、真标题目录、表格/脚注/溯源标注还原，按场景制式排版；markdown 产物可直出。"
description: "将 Omni Reader 解析结果重建为保真 Word：grounded 页锚点→源页分页符、官方 outline→真标题+目录、GFM 表格/脚注/〔来源〕标注还原，多源合并带证据溯源附录；--profile 按公文/诉讼/研报等制式排版，markdown 可直出。Do NOT use for: 像素级版面复刻、PPTX/PDF 输出、无 omni-reader 的解析层能力（--md 直出除外）；Triggers: Omni 转 Word / 保真重建 / 多源证据整合 / 扫描件转 Word; omni to docx / grounded rebuild / scan to Word"
version: "0.1.0"
license: MIT
metadata:
  requires:
    bins: ["python3"]
tags: [文档转换, Word, 解析重建, 公文, 诉讼, 研报]
---

# omni2docx — 双层管线：Omni 解析（Agent 层）× 格式生成（人层）

## 前置条件

| 依赖                          | 用途                | 缺失时                                        |
| --------------------------- | ----------------- | ------------------------------------------ |
| **omni-reader MCP** 已连接（Bridge 就绪） | 解析层：parse / read_outline / read_result | 场景②③（grounded 重建/多源合并）不可用，先引导用户安装配置 omni-reader MCP；**场景①（--md 直出）不依赖 omni，仍可用** |
| **Python 3.9+ 且已装 `python-docx`**（`pip install python-docx`） | 渲染层：build_docx.py / validate_docx.py | 引擎无法运行，先装依赖；调用方式用用户环境通用的 `python`，不假设任何特定安装路径 |

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
| content（markdown） | ✅ 可用               | **从 `parse` 内联回执取** `structuredContent.result.parts.content.storage.text`                                                                                                                                                    |
| grounded（页锚点）     | ✅ 可用               | 同上 `parts.grounding.storage.value`（kind=`inline`），页级锚点                                                                                                                                                                       |
| `read_result` 工具  | ✅ 可用               | **必须与 parse 同会话**调用（`local_result_cache` 绑定创建它的 bridge 进程，不跨进程、有过期时间）；用 `get_parse_status` 回执里的 `local_result_cache.result_id`                                                                                               |
| `read_outline` 工具 | ✅ 可用               | 同上**同会话**约束。真实研报实测返回 `coverage=complete`；无标题文档返回 `coverage=none, nodes=[]` 属正常语义。节点跳转用法：`read_outline(result_id, node_id)` **铸出 cursor** → `read_result(result_id, cursor)`（不是直接传 `node:xxx`） |
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

> **使用纪律**：Omni 对 agent 原生友好，**一切经 agent 原生 MCP 工具直连**——  
> parse / get_parse_status / read_outline / read_result 全程同一会话即可，**不要为 omni  
> 写额外的 spawn bridge 脚本**：独立进程调 read_* 必然触发同会话约束失败，属自造假故障。

### 步骤 1 — 原生 parse（grounded，内联取数）

调用 `mcp__omni_reader__parse`：

- `source`：本地文件路径（须在 omni 允许的根目录内，即 Bridge 的 allowed roots）或 URL。
- `detail`：`"grounded"`（务必）。
- `result_delivery`：`"artifact"`（内联回执同样返回 bundle；artifact 模式便于将来工具恢复）。  
  轮询 `mcp__omni_reader__get_parse_status` 至 `COMPLETED`。

**取数（从 parse 内联回执，不要调 read_result）**：解析 `parse` 最终回执的  
`structuredContent.result.parts`：

- `parts.content.storage.text` → markdown 正文
- `parts.grounding.storage.value`（kind=`inline`）→ `omni.grounding.v1` bundle

**官方 outline（推荐，同会话调用）**：从 `get_parse_status` 回执取  
`local_result_cache.result_id`，**在同一会话**调 `read_outline(result_id)` →  
`{coverage, nodes:[{id, level, title}]}`。真实研报实测 `coverage=complete`。

- `coverage=none, nodes=[]` = 文档无可识别标题（正常语义，非故障），此时落盘不写 `outline` 字段、引擎走 markdown 重建。
- 有节点时写入 JSON `outline` 字段，引擎自动优先使用官方层级（引擎兼容 `{coverage,nodes}` 原样传入）。
- ⚠️ **同会话约束**：`local_result_cache` 绑定创建它的 bridge 进程，跨进程/进程重启后 `RESULT_NOT_FOUND`。agent 原生 MCP 会话内 parse + read_outline 天然同进程，直接可用。

### 步骤 2 — 落盘中间 JSON

```json
{
  "markdown": "<步骤1 parts.content.storage.text>",
  "grounding": <步骤1 parts.grounding.storage.value>,
  "outline": <同会话 read_outline 返回的 {coverage, nodes}；coverage=none 时省略>,
  "source": "<源文件描述>",
  "detail": "grounded"
}
```

- `outline` 提供且 coverage=complete 时引擎**优先用官方层级**；缺失或 none 时从 markdown 重建。

### 步骤 3 — 运行映射引擎

```
python <skill_dir>/scripts/build_docx.py --json <中间json> --out <输出.docx>

# agent 工作产物直出（场景①）：免中间 JSON
python <skill_dir>/scripts/build_docx.py --md <agent产出.md> --out <输出.docx>
```


- 自动：封面标题提取（"标题：xxx"）→ 中文字体 → markdown 章节重建 → 真标题 +  
  文首目录 → grounded 源页分页符 → 表格/列表/引用/行内样式 → 脚注上标 + 文末注释 +  
  〔来源〕灰标 → 溯源标注段。
- `--no-pagebreak` 忽略分页；`--no-toc` 忽略章节重建（仅纯 markdown + 表格/列表）；  
  `--page-marks` 分页处标注「源第 N 页」（核对原件）；`--profile` 套制式——预设名  
  （gov/legal/finance/academic/default）或自定义 JSON（内联或 .json 文件，参数见上节表）。

### 步骤 4 — 验收（产品级，必做）

用 `validate_docx.py` 对产出做保真 + 结构校验，确认**字符零丢失（覆盖率≥99%）**&#x4E14;  
分页/标题/表格数量符合预期，再 `present_files` 交付：

```
python <skill_dir>/scripts/validate_docx.py --json <中间json> --docx <输出.docx>
```

### 步骤 5 — 交付

`present_files` 打开/交付 `.docx`。

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
| ETF 文章（PDF 源） | **100%** | 7 段→**6** | 6×H1(国家)+8×H2(指数) + 13 条目录 + 封面标题 | 0（基金池在文末被截断）                         |
| 券商研报（PDF 源）    | **100%** | 4 段→**3** | 4×H3(###标题) + 目录                  | **5**（含"会计年度"5 列财务表，单元格数值与源一一对应，已抽检） |
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
| 券商研报（PDF 源） | PDF/文档（页锚点） | 第 1–4 页                                           |

- 字节偏移换算：中文 6239 字符 = 14861 UTF-8 字节，映射无截断。
- 标题提升覆盖"段落型"与"有序列表型"小节；修复了"小节被并入父段落"导致吞掉子标题的缺陷。
- 真实财务表（会计年度/资产负债表/评级标准）列数一致，正确还原；真实研报 GFM 表格语法已确认（`| --- | --- |` 分隔）。

## 已知限制

1. 保真级别为**页级**（grounded）。元素级（bbox）数据可经 `detail=layout` 产出（实测  
   `layout.items[].bbox/font/size`），引擎消费 layout 的升级为后续阶段。
2. `read_result` / `read_outline` **可用**，但受**同会话约束**（`local_result_cache` 绑定  
   bridge 进程，跨进程 `RESULT_NOT_FOUND`）；agent 原生会话内使用无碍。outline 缺失时  
   引擎从 markdown 重建兜底，提供时优先官方层级。
3. 段落跨源页边界时归入其起始字节所在页（MVP 简化）。
4. **图像/音频不嵌入，但溯源标注保留**：Omni 多模态解析不返回图像/音频字节，docx 亦不含  
   多媒体；但 Omni 产出的**文本溯源标注**（视频帧 `[画面 HH:MM]`、说话人转写  
   `[说话人N MM:SS-MM:SS]`、场景描述）由引擎识别并渲染为区分明显的标注段；  
   `![…](data:base64…)` 引用剥离字节、保留 alt 说明。
5. 复杂 markdown（嵌套表、脚注、数学公式）按文本降级；表格为**版式保真**非像素级还原。
6. 仅 `.docx` 输出；PPTX / PDF（坐标保真）为后续阶段。
