# cue-lead-pieces

**读财报的 Agent 贴出的“原文”有三分之一以上对不上；装上它，95% 以上能逐字对回原文和页码，对不上的会被自动标出或改回。**

Agent 思考，Cue 感知。用 **Cue Omni Reader** 把上市公司自己披露的文件（A 股年报、半年报、临时公告来自巨潮资讯；美股 10-K / 10-Q / 8-K 来自 SEC EDGAR）解析成带原 PDF 页码的原文，变成**可追溯的线索件**（对象 · 为何现在 · 建议动作 · 带来源和页码的逐字原文证据），并把 Agent 答案里的每一句引文对回原文页面核对。可选用 **Cue data-MCP** 列公告清单、**cue-research** 补“为何现在”的背景。

**本文件为中文主面；英文版为包内 `README.en.md`（仓库内查阅，渠道页不解析相对链接）。** beta · Python 标准库 · 无使用遥测

![裸 Agent 与 Agent + 本技能对比](assets/demo-verifiable.png)

上图是实测，不是示意：同一个 Agent、同一个问题、同一批公开文件，24 家上市公司。**这组数字是用本地解析通道测的，Omni 解析通道还没有做同样规模的实测**；口径和局限见下文“交付与验证”。

## 它解决什么

| 你遇到的问题 | 这个 skill 交付什么 |
|---|---|
| Agent 贴的“原文”像真的，但翻到那一页找不到 | `verify` 逐句对回所注来源的所注页（±1 页），给出判定和最相近的真实原文 |
| 页码注错、字被改过、表格数字被改写成句子 | `verify --fix` 自动改正页码、换回原句或原表格行，原稿另存 |
| 原文里根本没有的话或数字 | 判为“原文中没有”，`--fix` 直接删掉，并提示哪条信号因此没了证据 |
| 从几百页里找信用恶化信号太慢 | `brief` 一次给出材料目录、线索件和可直接粘贴的逐字证据 |
| 引文页码要和原文一页不差、表格要按表格读 | Cue Omni Reader 的 `grounded` 结果带每段文字的原 PDF 页码，`ingest` 按页落盘，表格保留为表格 |

## Cue 三通道在本件里各做什么

| 通道 | 本件用途 | 未开通时（不报错，降级） |
|---|---|---|
| `cue-omni-reader`（主解析通道） | 解析每份披露；`detail="grounded"` 给出原 PDF 页码，`cue.py ingest` 按页落盘 | `cue.py local` 本地解析兜底（PyMuPDF / pdftotext / EDGAR 分页），材料目录里标 `local` |
| `cue-data-mcp`（可选） | `disclosure_cn` / `disclosure` 域列公告清单和公告索引号，核对补全清单 | `cue.py fetch` 从巨潮资讯 / SEC EDGAR 公开索引列清单（零消耗） |
| `cue-research`（可选，≤1 次） | 给“为何现在”补行业、同业或事件背景，只写进解释，不作引文证据 | 不发起，解释只依据披露原文 |

Omni 解析和 cue-research 会消耗积分：Agent 发起前会先告诉你要解析几份、各是什么，等你同意；只转述服务端返回的计费事实，不估算单价。你也可以只让年报、半年报走 Omni，公告走本地兜底。

## 首次开通 Cue（三步，可跳过）

注册 <https://cuecue.cn>（新账号注册送 500、每日 10，以服务端为准）→ <https://cuecue.cn/hub/api-key> 取 `CUE_API_KEY` 入本地凭据（**别贴进聊天**）→ 装 `cue-omni-reader`：`npx skills add sensedeal/cue-skills --skill cue-omni-reader`（`cue-data-mcp` / `cue-research` 按需，装法见各自 SKILL.md）。

不装也能跑：`cue.py local` 用本地解析把同一批公开文件读进来，核对规则完全一样——上面的实测数字就是这样跑出来的；但页码靠本地抽取，表格可能被拆成散行，看不到 Cue 通道取证的样子。

## 第一次试用

安装后直接对 Agent 说：

> 使用 cue-lead-pieces，看看 Leslie's（LESL）现在最重要的 5 个信用恶化信号，每条附逐字原文和页码，回答前核对引文。

Agent 会先列出文件清单、告诉你要用 Omni 解析几份并等你同意，再解析、出线索件、写答案、核对。

也可以在技能目录直接运行（Python 3.9+）：

```sh
export CUE_SEC_UA="你的名字 你的邮箱"
python3 scripts/cue.py fetch /tmp/lesl --us LESL --months 12   # 只列清单，不下载，零消耗
# 主通道：Agent 用 cue-omni-reader 逐份 parse(detail="grounded")，结果存为 /tmp/lesl/omni/<sid>.json，然后：
python3 scripts/cue.py ingest /tmp/lesl --omni-dir /tmp/lesl/omni
# 没开通 Omni 时的兜底：
python3 scripts/cue.py local /tmp/lesl
python3 scripts/cue.py brief /tmp/lesl
```

## 安装

```sh
npx skills add huhoo/cue-awesome --skill cue-lead-pieces
```

该安装方式需要 Node.js/npm；把本目录复制到宿主支持的 skills 位置也可以（Claude Code：`~/.claude/skills/cue-lead-pieces`）。本技能不在仓库 v2026.09.27 发布的 ZIP 里。

## 运行要求

- Python 3.9+（只用标准库）。
- 主解析通道：已安装并配置的官方 `cue-omni-reader`（由 Agent 通过 MCP 调用，本脚本不直接联系 Omni，也不读取 `CUE_API_KEY`）。
- 本地兜底解析 A 股 PDF 需要 PyMuPDF（`pip install pymupdf`）**或** `pdftotext` 命令（poppler）；美股 EDGAR HTML 不需要。
- 文件清单来自巨潮资讯、SEC EDGAR 公开索引，免费。`fetch` 只联网列清单，`local` 联网下载文件；`leads` / `brief` 只在设置了下面的可选模型变量时调用该模型接口；其余只读本地文件。
- SEC EDGAR 要求访问者表明身份：请设置 `CUE_SEC_UA="你的名字 你的邮箱"`（不设置时用占位联系方式，SEC 可能拒绝或限流）。
- 可选：设置 `CUE_LLM_BASE_URL`、`CUE_LLM_API_KEY`、`CUE_LLM_MODEL`（任意 OpenAI 兼容接口），`leads` 会用该模型做跨来源对齐；不设置则用确定性分组。key 放在你自己的凭据设施里，不要贴进聊天或 Issues。

## 命令

| 命令 | 作用 |
|---|---|
| `cue.py fetch DIR --cn 600606` / `--us LESL` | 列出近 12 个月的公开文件和下载地址（不下载、零消耗） |
| `cue.py fetch DIR --list list.json --company X --market CN` | 登记从别处（如 Cue data-MCP）找到的文件 |
| `cue.py ingest DIR --omni-dir DIR/omni` | 读入 Cue Omni Reader 的解析结果（`<sid>.json` 带页码的 grounded 结果，或 `<sid>.md` 纯文本） |
| `cue.py local DIR [来源…]` | 本地解析兜底：下载并按页抽取文本；`fetch … --local` 一步完成 |
| `cue.py brief DIR` | 一次给全：材料目录（含解析通道）+ 线索件 + 可直接粘贴的逐字证据 |
| `cue.py find DIR <关键词…>` | 含关键词的原句，可直接粘贴 |
| `cue.py page DIR <来源> <页码> …` | 读原页，如 `AR2025 54,196-198`，多个来源一次读完 |
| `cue.py verify DIR --json answer.json [--fix]` | 核对每条引文；`--fix` 改正页码、把删改过的引文换回原句、删掉原文没有的引文 |
| `cue.py verify DIR --quote "…" --source S --page N` | 核对单句 |

Agent 的推荐流程写在 `SKILL.md` 里。

## 交付与验证

实测记录见包内 `references/verification.md`，版本记录见 `CHANGELOG.md`。要点：

- 同一个 Agent（Claude Code）、同一个问题（“作为信贷员，这家公司现在最重要的 5 个信用恶化信号是什么？每条都要有逐字原文证据和来源页码。”）、同一批公开文件，24 家上市公司（A 股 12、美股 12，含 4 家健康对照），每家每种做法 1 次。**全部用本地解析通道。**
- 裸 Agent：421 条引文中 61% 能在所注页逐字找到，39% 对不上（按公司重抽样的 95% 区间 33%～46%）。
- 用本技能的流程：443 条引文中 95% 逐字可查（95% 区间 91%～98%）。这一组数是 0.3.0 之前的版本测得的。
- 0.3.0 在之前最慢的 14 家公司上复测：最终答案 279 条引文 100% 逐字可查，`verify --fix` 之前 Agent 原稿为 98%（273/278）；60 分钟超时 1 次，同时段旧版 4 次。
- 原文任何地方都没有的数字：两种做法都是 0。
- 0.4.0 的 Omni 读入只用合成的 grounded 结果做过离线测试，还没有用真实 Omni 解析跑过；在那之前，Omni 通道的页码准确度和上面的比例都不能算作已验证。

它证明的是“引文能不能在原文里逐字找到”，不代表信号判断正确，也不代表其他模型或宿主上会有同样的数字。

自检（离线，不联网）：

```sh
python3 scripts/test_skill_regression.py
python3 scripts/cue.py --help
```

## 常见问题与反模式（你想这么用 → 本件不接，因为 → 替代去向）

- 想让它判断“这家公司会不会违约” → 不接，它只保证引文出自原文，不判断信号对错 → 由你或你的信用模型判断，本件只给可核对的证据。
- 想核对研报、新闻或第三方数据库里的说法 → 不接，它只读公司自己的披露文件 → 先找到对应的公司公告或 10-K 原文再核对。
- 想覆盖港股、债券募集说明书或非上市公司 → 目前不接，`fetch` 只会列巨潮资讯和 SEC EDGAR 的清单 → 可以用 Omni 解析其他公开文件后 `ingest --sid … --kind … --date … --title …` 登记读入，但这条路没有实测过。
- 想把 `--fix` 的结果直接当终稿 → 不建议，换上的原句是程序选出的最相近原文，没有人工复核它是否仍支撑原来的说法 → 关键结论请人工看一眼原页（`page` 命令）。

## 出错了怎么办（症状 → 原因 → 恢复动作）

- Omni 返回 `OMNI_NOT_ENTITLED` / 403、额度不足，或你不同意花费 → 账号未开通或未批准消耗 → 按官方 cue-omni-reader 的提示处理；不想花就运行 `cue.py local DIR` 走本地兜底，回答里会标明。
- Omni 返回 `UNSUPPORTED_DETAIL` / `DETAIL_CAPABILITIES_UNAVAILABLE` → 这份文件拿不到带页码的 grounded 结果 → 用默认文本结果存成 `<sid>.md` 再 `ingest`，页码会标成文本块号；要原页码就对这份走 `cue.py local`。
- `ingest` 输出 `warning: incomplete page [...]` 或 `truncated` → Omni 这次有页面没解析完 → 这些页的引文核对不到；对这份重新解析前先问用户（可能再次计费），或对这份走 `cue.py local`。
- `fetch` 报网络错误或 SEC 返回 403 → 网络不通或没有表明身份 → 检查网络，设置 `CUE_SEC_UA` 后重试。
- A 股 `local` 报找不到 `pdftotext` → 没装 PyMuPDF 也没装 poppler → `pip install pymupdf` 或安装 poppler。
- `fetch` 只输出一行 `cue.py: error: unknown A-share code '999999': not in the cninfo stock list ...`（美股为 `unknown US ticker '...'` 或 `unknown CIK '...'`），退出码 2 → 股票代码查不到（代码不对或该市场不支持） → A 股用 6 位代码，美股用 ticker 或 CIK。
- `brief` 输出太长被宿主存成文件 → 个别公司材料多 → 让 Agent 读那个文件即可，或用 `--top` 减少线索件条数。
- `verify --fix` 提示某条信号已没有可核对的原文证据 → 那条信号的引文都不在原文里 → 用 `find` 补一句原文，或删掉那条信号。

## 怎么开口（触发示例：三条正例 + 一条反例）

- 正例：“用 cue-lead-pieces 看看 600606 最近一年的披露里有哪些信用恶化信号，带原文页码；年报用 Omni 解析，公告本地解析就行。”
- 正例：“这份答案里的引文帮我逐句核对一下是不是原文。”（附 answer.json 和数据目录）
- 正例：“Check the latest 10-Q of QVCG for going-concern and covenant language, with page numbers.”
- 反例：“帮我预测这只股票下个月涨不涨。”（不在本件范围内）

## 边界与许可

只依据公司公开披露的文件；不构成投资或信贷建议。线索件和核对结果含有限长度的原文摘录，分享前请确认来源的使用条件。代码及说明为 MIT（见包内 LICENSE）。中文 README 为权威说明；Agent 指令以 `SKILL.md`（中文主）为准，`SKILL.en.md` 是其同步译文。
