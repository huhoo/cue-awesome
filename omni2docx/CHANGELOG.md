# CHANGELOG(omni2docx)

### 0.1.0 — 2026-10-10（首发）

- 双层管线：Omni 原生 `parse`（grounded）→ 中间 JSON（markdown+grounding+outline）→ `build_docx.py` 渲染；agent markdown 产物可 `--md` 直出（免中间 JSON，不依赖解析层）。
- 映射能力：grounded 页锚点→源页分页符；官方 outline→真 Heading+可见目录（缺失时从 markdown 保守重建：中文序号 H1/指数型 H2/`###` 标题）；GFM 表格（列一致性护栏）；脚注上标+文末注释节；〔来源〕灰色小字；溯源标注段（【画面】/【说话人N 时间段】/【图说】带底纹）；base64 图像引用剥离字节留说明。
- 多源合并：`sources` 每源一章 + 总目录 + 章间分页 + 文末「证据溯源附录」（页码范围/画面时间点/说话人转写段自动回灌成表）；`analysis` 渲染为首章。
- 排版：`--profile` 五预设（gov 公文 GB/T 9704 / legal / finance / academic / default）+ 内联 JSON/.json 文件任意参数覆盖（字体/字号/行距/缩进/页边距/表样式，行距接受 `28pt`/`1.5倍` 等字符串）；标题黑色+层级字号、零 CJK 伪斜体；`--page-numbers` 页脚 PAGE 域；`--strip-emoji` 剥离装饰符；`--page-marks` 页边界源页码标注。
- 校验：`validate_docx.py` 字符级 CJK 覆盖率（≥99% PASS）+ 锚句命中 + 结构统计，与 `--strip-emoji` 同口径防误报。
- 实测：真实语料矩阵 12 例（xlsx/PDF 研报/债券书/HTML/音频/docx/PPTX/JPG OCR/千页 PDF/截断 PDF/边界×2）× 多制式，覆盖率全部 100%；端到端（原生 parse→渲染→校验）通过。已知限制见 README「能力边界」。
