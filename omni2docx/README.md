# omni2docx — Omni 解析保真转 Word

把 Omni Reader 的解析结果重建为**人可读可编辑的 .docx**：不是又一个 markdown→docx，
而是把 Omni 解析时已算出的结构化信息（源页锚点、章节层级、画面/转写元数据）映射回
Word 原生对象——通用转换只吃 markdown，拿不到这些。

## 是什么 / 不是什么

| 是 | 不是 |
|---|---|
| grounded 页锚点 → Word 源页分页符（页级保真） | 像素级版面复刻 |
| 官方 outline → 真 Heading 层级 + 可见目录 | PPTX / PDF 输出（后续阶段） |
| GFM 表格 / 脚注上标+注释节 / 〔来源〕灰标 / 上标引用 | 图像/音频字节嵌入（Omni 不返回字节，保留文本溯源标注） |
| 多源合并 + 自动「证据溯源附录」（页码/时间点/说话人） | 投资建议、内容创作 |

## 三类场景

1. **Agent 产出 → 可交付文档**：agent 的 markdown 工作产物 `--md` 直出，专业中文排版。
2. **Scanned PDF/不可编辑件 → 可编辑 Word**：`--page-marks` 在每页边界标注「源第 N 页」，改稿直接对照原件。
3. **多源证据整合 → 诉讼文书等**：`sources` 数组每源一章 + 总目录 + 证据溯源附录；录音转写段/视频帧标注段可直接引用。

## 上手（三步）

前置：`python3` + `pip install python-docx`；场景②③另需 omni-reader MCP 已连接（场景①不需要）。

```bash
# ① agent markdown 直出（免中间 JSON）
python scripts/build_docx.py --md 产出.md --out 交付.docx --profile gov --page-numbers

# ②③ Omni 解析重建：parse(grounded) 取 markdown+grounding(+同会话 read_outline) 落盘中间 JSON
python scripts/build_docx.py --json 中间.json --out 交付.docx --profile legal --page-marks

# 验收（必做）：字符零丢失 + 结构核对
python scripts/validate_docx.py --json 中间.json --docx 交付.docx
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
- 仅 `.docx` 输出；中文字体名（宋体/仿宋_GB2312/楷体等）在非 Windows 环境由 Word/WPS 自动替换，制式文档建议在 Windows/WPS 打开验收。

## 验收口径

`validate_docx.py` 以**字符级 CJK 覆盖率**（≥99% 判 PASS）+ 锚句命中 + 结构统计（分页/标题/表格数）
对产物做保真校验。真实语料矩阵（xlsx / PDF 研报 / HTML / 音频转写 / docx / PPTX /
JPG OCR / 千页 PDF / 截断 PDF / 边界用例，多制式组合）实测覆盖率全部 100%。

## 文件

| 文件 | 说明 |
|---|---|
| `SKILL.md` | agent 主指令（完整工作流、字段约定、解析侧能力现状） |
| `scripts/build_docx.py` | 渲染引擎（单源/多源合并/markdown 直出） |
| `scripts/validate_docx.py` | 保真+结构校验器 |
