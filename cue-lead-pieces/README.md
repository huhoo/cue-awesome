# cue-lead-pieces

**读财报的 Agent 贴出的“原文”有三分之一以上对不上；装上它，95% 以上能逐字对回原文和页码，对不上的会被自动标出或改回。**

把上市公司自己披露的文件（A 股年报、中报、临时公告来自巨潮资讯；美股 10-K / 10-Q / 8-K 来自 SEC EDGAR）变成**可追溯的线索件**（对象 · 为何现在 · 建议动作 · 带来源和页码的逐字原文证据），并把 Agent 答案里的每一句引文对回原文页面核对。Agent 思考，Cue 感知。

**本文件为中文主面；英文版为包内 `README.en.md`（仓库内查阅，渠道页不解析相对链接）。** beta · Python 标准库 · 无使用遥测 · 数据源公开免费，无需 API key

![裸 Agent 与 Agent + 本技能对比](assets/demo-verifiable.png)

上图是实测，不是示意：同一个 Agent、同一个问题、同一批公开文件，24 家上市公司。数字的口径和局限见下文“交付与验证”。

## 它解决什么

| 你遇到的问题 | 这个 skill 交付什么 |
|---|---|
| Agent 贴的“原文”像真的，但翻到那一页找不到 | `verify` 逐句对回所注来源的所注页（±1 页），给出判定和最相近的真实原文 |
| 页码注错、字被改过、表格数字被改写成句子 | `verify --fix` 自动改正页码、换回原句或原表格行，原稿另存 |
| 原文里根本没有的话或数字 | 判为“原文中没有”，`--fix` 直接删掉，并提示哪条信号因此没了证据 |
| 从几百页里找信用恶化信号太慢 | `brief` 一次给出材料目录、线索件和可直接粘贴的逐字证据 |

## 第一次试用

安装后直接对 Agent 说：

> 使用 cue-lead-pieces，看看 Leslie's（LESL）现在最重要的 5 个信用恶化信号，每条附逐字原文和页码，回答前核对引文。

也可以在技能目录直接运行（Python 3.9+；会联网下载这家公司的公开文件）：

```sh
export CUE_SEC_UA="你的名字 你的邮箱"
python3 scripts/cue.py fetch /tmp/lesl --us LESL --months 12
python3 scripts/cue.py brief /tmp/lesl
```

## 安装

```sh
npx skills add huhoo/cue-awesome --skill cue-lead-pieces
```

该安装方式需要 Node.js/npm；把本目录复制到宿主支持的 skills 位置也可以（Claude Code：`~/.claude/skills/cue-lead-pieces`）。本技能不在仓库 v2026.09.27 发布的 ZIP 里。

## 运行要求

- Python 3.9+（只用标准库）。
- A 股 PDF 需要 PyMuPDF（`pip install pymupdf`）**或** `pdftotext` 命令（poppler）。美股 EDGAR HTML 不需要。
- 数据来源：巨潮资讯、SEC EDGAR，公开免费，不需要任何 API key 或付费服务。`fetch` 联网下载；`leads` / `brief` 只在设置了下面的可选模型变量时调用该模型接口；其余只读本地已下载的文件。
- SEC EDGAR 要求访问者表明身份：请设置 `CUE_SEC_UA="你的名字 你的邮箱"`（不设置时用占位联系方式，SEC 可能拒绝或限流）。
- 可选：设置 `CUE_LLM_BASE_URL`、`CUE_LLM_API_KEY`、`CUE_LLM_MODEL`（任意 OpenAI 兼容接口），`leads` 会用该模型做跨来源对齐；不设置则用确定性分组，不调用任何模型。key 放在你自己的凭据设施里，不要贴进聊天或 Issues。

## 命令

| 命令 | 作用 |
|---|---|
| `cue.py fetch DIR --cn 600606` / `--us LESL` | 下载近 12 个月的公开文件，按页抽取文本 |
| `cue.py brief DIR` | 一次给全：材料目录 + 线索件 + 可直接粘贴的逐字证据 |
| `cue.py find DIR <关键词…>` | 含关键词的原句，可直接粘贴 |
| `cue.py page DIR <来源> <页码> …` | 读原页，如 `AR2025 54,196-198`，多个来源一次读完 |
| `cue.py verify DIR --json answer.json [--fix]` | 核对每条引文；`--fix` 改正页码、把删改过的引文换回原句、删掉原文没有的引文 |
| `cue.py verify DIR --quote "…" --source S --page N` | 核对单句 |

Agent 的推荐流程（5～6 轮完成）写在 `SKILL.md` 里。

## 交付与验证

实测记录见包内 `references/verification.md`，版本记录见 `CHANGELOG.md`。要点：

- 同一个 Agent（Claude Code）、同一个问题（“作为信贷员，这家公司现在最重要的 5 个信用恶化信号是什么？每条都要有逐字原文证据和来源页码。”）、同一批公开文件，24 家上市公司（A 股 12、美股 12，含 4 家健康对照），每家每种做法 1 次。
- 裸 Agent：421 条引文中 61% 能在所注页逐字找到，39% 对不上（按公司重抽样的 95% 区间 33%～46%）。
- 用本技能的流程：443 条引文中 95% 逐字可查（95% 区间 91%～98%）。这一组数是 0.3.0 之前的版本测得的。
- 0.3.0 在之前最慢的 14 家公司上复测：最终答案 279 条引文 100% 逐字可查，`verify --fix` 之前 Agent 原稿为 98%（273/278）；60 分钟超时 1 次，同时段旧版 4 次。
- 原文任何地方都没有的数字：两种做法都是 0。

它证明的是“引文能不能在原文里逐字找到”，不代表信号判断正确，也不代表其他模型或宿主上会有同样的数字。

自检（离线，不联网）：

```sh
python3 scripts/test_skill_regression.py
python3 scripts/cue.py --help
```

## 常见问题与反模式（你想这么用 → 本件不接，因为 → 替代去向）

- 想让它判断“这家公司会不会违约” → 不接，它只保证引文出自原文，不判断信号对错 → 由你或你的信用模型判断，本件只给可核对的证据。
- 想核对研报、新闻或第三方数据库里的说法 → 不接，它只读公司自己的披露文件 → 先找到对应的公司公告或 10-K 原文再核对。
- 想覆盖港股、债券募集说明书或非上市公司 → 目前不接，`fetch` 只支持巨潮资讯和 SEC EDGAR → 可以自己把 PDF 放进数据目录的格式里，但这条路没有实测过。
- 想把 `--fix` 的结果直接当终稿 → 不建议，换上的原句是程序选出的最相近原文，没有人工复核它是否仍支撑原来的说法 → 关键结论请人工看一眼原页（`page` 命令）。

## 出错了怎么办（症状 → 原因 → 恢复动作）

- `fetch` 报网络错误或 SEC 返回 403 → 网络不通或没有表明身份 → 检查网络，设置 `CUE_SEC_UA` 后重试。
- A 股 `fetch` 报找不到 `pdftotext` → 没装 PyMuPDF 也没装 poppler → `pip install pymupdf` 或安装 poppler。
- `fetch` 以 Python 回溯退出、最后一行是 `StopIteration` → 股票代码查不到（代码不对或该市场不支持） → A 股用 6 位代码，美股用 ticker 或 CIK。
- `brief` 输出太长被宿主存成文件 → 个别公司材料多 → 让 Agent 读那个文件即可，或用 `--top` 减少线索件条数。
- `verify --fix` 提示某条信号已没有可核对的原文证据 → 那条信号的引文都不在原文里 → 用 `find` 补一句原文，或删掉那条信号。

## 怎么开口（触发示例：三条正例 + 一条反例）

- 正例：“用 cue-lead-pieces 看看 600606 最近一年的披露里有哪些信用恶化信号，带原文页码。”
- 正例：“这份答案里的引文帮我逐句核对一下是不是原文。”（附 answer.json 和数据目录）
- 正例：“Check the latest 10-Q of QVCG for going-concern and covenant language, with page numbers.”
- 反例：“帮我预测这只股票下个月涨不涨。”（不在本件范围内）

## 边界与许可

只依据公司公开披露的文件；不构成投资或信贷建议。线索件和核对结果含有限长度的原文摘录，分享前请确认来源的使用条件。代码及说明为 MIT（见包内 LICENSE）。中文 README 为权威说明；Agent 指令以 `SKILL.md`（中文主）为准，`SKILL.en.md` 是其同步译文。
