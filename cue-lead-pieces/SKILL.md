---
name: cue-lead-pieces
description: "读上市公司自己的披露文件(A股巨潮资讯/美股SEC EDGAR),产出带来源和页码的信用线索件,并逐句核对答案里的引文是否逐字出自所注页;--fix 改正注错的页码、把改过字的引文换回原句、删掉原文没有的。单一模型与宿主实测24家公司:裸Agent引文39%对不上,用本件流程95%逐字可查。适合:信用恶化信号、财报变化、要求逐字证据。不适合:投资建议、判断信号本身对错。Triggers: credit signals, quote verification, 10-K, 年报, 引文核对。"
license: MIT
version: "0.3.1"
slug: cue-lead-pieces
displayName: 财报引文逐字核对
summary: "从A股/美股公开披露建带页码的信用线索件,逐句核对引文是否逐字出自所注页,对不上的标出或改回;公开免费数据源,无需密钥。"
---

# cue-lead-pieces

**中文主入口（本文件）；英文对应版为包内 `SKILL.en.md`，仓库内查阅。渠道页不解析相对链接，故不给可点切换。**

Agent 思考，Cue 感知。把一家公司自己披露的文件（年报、中报/季报、临时公告，或 10-K/10-Q/8-K）变成**可追溯的线索件**：对象 · 为何现在 · 建议动作 · 逐字原文证据（来源 + 页码）。
线索件里的每一句引文都是程序从页面文本里截下来的，不是模型写的；`verify` 能对任何引文做程序化核对，`--fix` 能把答案里的引文自动改回原文。

脚本：本文件同目录下的 `scripts/cue.py`（Python 3.9+ 标准库；A 股 PDF 需要 PyMuPDF 或 `pdftotext` 命令）。下文 `CUE` 指它的完整路径，`DIR` 指这家公司的数据目录。

## 最快流程（5～6 轮完成）

每多一轮模型调用就要多等一次模型响应，所以**少轮次、每轮把事做完**：

0. 没有数据时先抓取（公开来源，免费，无需任何密钥）：
   - A 股（巨潮资讯）：`python3 CUE fetch DIR --cn 600606 [--months 12]`
   - 美股（SEC EDGAR）：`python3 CUE fetch DIR --us LESL [--months 12]`（也可给 CIK；建议先设 `CUE_SEC_UA="你的名字 你的邮箱"`，SEC 要求访问者表明身份）
1. `python3 CUE brief DIR`
   一次拿到：材料目录（来源编号、类型、日期、页数）、线索件（对象、为何现在、建议动作）、每条线索可直接粘贴的逐字证据（JSON 行）。
   **不需要**先 `ls`、`cat sources.json`、用 Read 读原文件或线索件 JSON。
2. 只有线索件的证据不够支撑某条判断时，**在同一条命令里一次补查完**（最多一到两轮，不要一页一轮地读）：
   - 按关键词找原句：`python3 CUE find DIR 持续经营 担保 逾期 --max 30`（英文同理，如 `"going concern" covenant`）
   - 读原页：`python3 CUE page DIR AR2025 54,196-198 ANN-2026-05-14-1 2`（多个来源、多个页码一次读完）
3. 一次写好 `answer.json`（证据只从上面的输出里原样复制），然后**只运行一次**：
   `python3 CUE verify DIR --json answer.json --fix`
   它逐条核对并把修正写回 `answer.json`：页码注错的改成原文实际页码；改过字或把表格改写成句子的，换成原文原句或原表格行；原文中不存在的（含编造的数字）删掉。原稿另存为 `answer.before_fix.json`。
   修正后直接复述答案；**不要再逐句复核、不要反复改写重核**。只有出现“这条信号已没有可核对的原文证据”的警告时，才用 `find` 补一句原文或删掉那条信号。

## 其他命令

- `python3 CUE leads DIR`：只看线索件（`brief` 已包含它，结果缓存在 `DIR/leads.json`）。先做跨期比对（最新 vs 上一期同类报告里新增/删除的风险表述）和事项抽取，再把同一对象的变化对齐。
  默认用确定性分组，不调用任何模型；如果设置了 `CUE_LLM_BASE_URL` / `CUE_LLM_API_KEY` / `CUE_LLM_MODEL`（任意 OpenAI 兼容接口），会用该模型做跨来源对齐。
- `python3 CUE changes DIR`：只做跨期比对和事项抽取。
- 单句核对：`python3 CUE verify DIR --quote "..." --source 10-Q_2026-06-30 --page 12`。

## 核对等级（`verify` 的判定，`--fix` 不改变它们）

`verbatim`（所注页 ±1 逐字找到，忽略空白和标点）、`verbatim_elsewhere`（原文有但来源/页码注错）、`not_found`（附最相近的真实原文和相似度，并分为 `edited` 删改过的原文 / `table_restated` 表格数字被改写成句子 / `numbers_differ` 数字在原文件中不存在 / `absent` 原文中没有这句话）。
引文中间省略的部分可用“……”连接，各段须按顺序出现在同一页。

## 规则

- answer.json 格式：`{"signals":[{"rank":1,"title":"...","explanation":"...","evidence":[{"source":"来源编号","page":12,"quote":"逐字原文"}]}]}`。
- 引文只能从 `brief` / `find` / `page` 的输出里**原样复制**，不改字、不拼接、不翻译；来源编号和页码照抄。判断写在 explanation 里，证据只放原文。
- 线索件只是提示，排序和判断由你决定。只依据公司公开披露的文件；不构成投资或信贷建议。
