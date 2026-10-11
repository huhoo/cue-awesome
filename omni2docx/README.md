# omni2docx — Omni 解析结果转 Word / HTML / PPT

把 Omni Reader 的解析结果重建为**人可读可交付的文档**：不是又一个 markdown→docx，
而是把 Omni 解析时已算出的结构化信息（源页锚点、章节层级、画面/转写元数据）映射回
原生对象——通用转换只吃 markdown，拿不到这些。

同一份解析结果可输出四种交付物，按用途选：**docx 保真**（递交/编辑/归档）、
**HTML 展示**（可读可分享、可打印）、**PPTX 汇报**（deck，要点上页、细节进备注）、
**PDF 打印**（HTML 走浏览器打印）。

## 是什么 / 不是什么

| 是 | 不是 |
|---|---|
| grounded 页锚点 → Word 源页分页符（页级保真） | 像素级版面复刻 |
| 官方 outline → 真 Heading 层级 + 可见目录 | PPT 的版面复刻（PPTX 是汇报 deck，按层级切页） |
| GFM 表格 / 脚注上标+注释节 / 〔来源〕灰标 / 上标引用 | 图像/音频字节嵌入（Omni 不返回字节，保留文本溯源标注） |
| 多源合并 + 自动「证据溯源附录」（页码/时间点/说话人） | 投资建议、内容创作 |

## 三类场景

1. **Agent 产出 → 可交付文档**：agent 的 markdown 工作产物 `--md` 直出，专业中文排版。
2. **Scanned PDF/不可编辑件 → 可编辑 Word**：`--page-marks` 在每页边界标注「源第 N 页」，改稿直接对照原件。
3. **多源证据整合 → 诉讼文书等**：`sources` 数组每源一章 + 总目录 + 证据溯源附录；录音转写段/视频帧标注段可直接引用。

## 上手（三步）

前置：`python3` + `pip install python-docx`；场景②③另需 omni-reader MCP 已连接（场景①不需要）。
PPTX 输出另需 `pip install python-pptx`；`--pdf` 另需本机装有 Edge/Chrome/Chromium（缺则明确提示跳过）。

```bash
# ① agent markdown 直出（免中间 JSON）
python scripts/build_docx.py --md 产出.md --out 交付.docx --profile gov --page-numbers

# ②③ Omni 解析重建：parse(grounded) 取 markdown+grounding(+同会话 read_outline) 落盘中间 JSON
python scripts/build_docx.py --json 中间.json --out 交付.docx --profile legal --page-marks

# 验收（必做）：字符零丢失 + 结构核对
python scripts/validate_docx.py --json 中间.json --docx 交付.docx

# 展示：自包含 HTML（可加 --pdf 同时导出打印件）
python scripts/render_html.py --json 中间.json --out 展示.html --profile gov --page-marks --pdf

# 汇报：deck（要点上页、正文进备注）；长文档建议 agent 先提炼提纲
python scripts/render_pptx.py --md slide提纲.md --out 汇报.pptx --profile finance --max-slides 30

# HTML / PPTX 同口径验收（备注/正文/表格合并计入覆盖口径）
python scripts/validate_html.py --json 中间.json --html 展示.html
python scripts/validate_pptx.py --json 中间.json --pptx 汇报.pptx
```

Omni 取数纪律：全程用 agent 原生 MCP 工具（parse / get_parse_status / read_outline /
read_result）且**同会话**调用——不要为 omni 写 spawn 脚本（跨进程调 read_* 必然失败）。

## 场景制式（--profile）

排版参数由文档的使用场景决定，agent 按场景知识决策；预设只是参考值：
`gov`（公文 GB/T 9704：仿宋三号/28 磅/GB 页边距）、`legal`（诉讼：仿宋四号）、
`finance`（研报：宋体五号）、`academic`（论文：小四 1.5 倍）、`default`。
任意参数可覆盖：`--profile` 接受内联 JSON / .json 文件（字体/字号/行距/缩进/页边距/表样式等）。

质量基线：标题一律黑色并按层级设字号、全文零 CJK 伪斜体（中文强调→加粗）、
`--page-numbers` 页脚 PAGE 域、`--strip-emoji` 剥离装饰符。

## 能力边界（诚实清单）

- 保真级别为**页级**（grounded）；元素级 bbox 数据可经 `detail=layout` 产出，引擎消费为后续阶段。
- `read_result` / `read_outline` 受**同会话约束**（`local_result_cache` 绑定 bridge 进程）；agent 原生会话内使用无碍。
- 段落跨源页边界时归入其起始字节所在页。
- 复杂 markdown（嵌套表、数学公式）按文本降级；表格为版式保真非像素级还原。
- 中文字体名（宋体/仿宋_GB2312/楷体等）在非 Windows 环境由 Word/WPS 自动替换，制式文档建议在 Windows/WPS 打开验收。
- PPTX 为汇报 deck：按标题层级切页、正文进演讲者备注、`--max-slides`（默认 80）截断并告警；不做每源页一页的机械平铺。
- PDF 经 HTML + headless 浏览器打印导出，版面与 HTML 一致；不做原生 PDF 排版。
- PDF 抽取的逐字母空格（"T h e y"）不可还原词边界，不强修；CJK 字间空格正常消除。

## 验收口径

三种格式各有验收器，同以**字符级 CJK 覆盖率**（≥99% 判 PASS）为准：
`validate_docx.py`（+ 锚句命中 + 结构统计：分页/标题/表格数）、
`validate_html.py`（+ 目录/锚点/源页标注/自包含检查）、
`validate_pptx.py`（幻灯片正文+表格+演讲者备注合并计入覆盖口径，+ 空页/截断检查）。
真实语料矩阵（xlsx / PDF 研报 / HTML / 音频转写 / docx / PPTX /
JPG OCR / 千页 PDF / 截断 PDF / 边界用例，多制式组合）实测覆盖率全部 100%。

## 文件

| 文件 | 说明 |
|---|---|
| `SKILL.md` | agent 主指令（完整工作流、字段约定、解析侧能力现状） |
| `scripts/build_docx.py` | Word 渲染引擎（单源/多源合并/markdown 直出） |
| `scripts/validate_docx.py` | 保真+结构校验器（docx） |
| `scripts/render_html.py` | HTML 展示渲染器（自包含单文件，可 `--pdf`） |
| `scripts/render_pptx.py` | PPTX 汇报渲染器（deck，要点上页/细节进备注） |
| `scripts/validate_html.py` | HTML 验收器（覆盖率 + 目录/锚点/自包含） |
| `scripts/validate_pptx.py` | PPTX 验收器（覆盖率含备注 + 空页/截断） |
