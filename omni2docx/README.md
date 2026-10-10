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

# ②③ Omni 解析重建：parse(grounded) 从内联回执取 markdown+grounding（outline 可选）→ 落盘中间 JSON
python scripts/build_docx.py --json 中间.json --out 交付.docx --profile legal --page-marks

# 验收（必做）：字符零丢失 + 结构核对
python scripts/validate_docx.py --json 中间.json --docx 交付.docx
```

Omni 取数纪律：第一性只依赖 parse / get_parse_status 的**内联回执**——小包两枚 part 随回执返回，
即使请求了 artifact 形制也以实际返回为准。read_* 两个续调用是**可选支路**：可得就用，不可得
（`RESULT_NOT_FOUND`、或没有 cursor 可起步）就走内联件与引擎从 markdown 重建目录，不重试、不报故障。

## 场景制式（--profile）

排版参数由文档的使用场景决定，agent 按场景知识决策；预设只是参考值：
`gov`（公文 GB/T 9704：仿宋三号/28 磅/GB 页边距）、`legal`（诉讼：仿宋四号）、
`finance`（研报：宋体五号）、`academic`（论文：小四 1.5 倍）、`default`。
任意参数可覆盖：`--profile` 接受内联 JSON / .json 文件（字体/字号/行距/缩进/页边距/表样式等）。

质量基线：标题一律黑色并按层级设字号、全文零 CJK 伪斜体（中文强调→加粗）、
`--page-numbers` 页脚 PAGE 域、`--strip-emoji` 剥离装饰符。

## 能力边界（诚实清单）

- 保真级别为**页级**（grounded）；元素级 bbox 数据可经 `detail=layout` 产出，引擎消费为后续阶段。
- `read_result` / `read_outline` 是**可选续调用，不保证可得**（同一 result_id 上可能返回不可重试的 `RESULT_NOT_FOUND`；无 cursor 时 `read_result` 也无法起步）。本件不依赖它们工作：取数走内联回执，目录缺省由引擎从 markdown 重建——这是常规路径，不是降级异常。
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
