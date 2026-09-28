# cue-omni-ontology

**[中文](README.md) · [English](README.en.md)**

**公开资料知识构建与更新**：把几份公开材料整理成带证据的业务知识；加入新材料，保留历史、区分口径和冲突，让后续任务可以复用。

本目录的使用说明以中文为权威；`SKILL.md` 为英文权威指令，`SKILL.zh-CN.md` 是对应中文译文。版本 0.1.1，公开试验版。

## 三个任务

```text
使用 cue-omni-ontology，根据这两期公开报告整理企业的业务和指标，保留原文依据。
把这份新公告加入之前的知识包，列出新增事实、冲突和需要确认的口径变化。
根据知识包说明哪些数字可以同比；有多个口径时分别列出依据。
```

默认一个主体、2–5 份公开来源。优先数字 PDF/网页；公开本地文件须确认来源。解析走官方 [cue-omni-reader](https://github.com/sensedeal/cue-skills/tree/main/cue-omni-reader)，语义抽取由宿主模型完成。下面的 Python 工具负责打包、查询与更新，不是自动抽取模型，也不替代官方解析器。

## 先看一个不调用 API 的例子

先查看[公开财报结果预览](assets/public-example/preview.md)，了解不同口径和跨期更新的实际呈现。该页明确标注为已保存结果回放。

附带 [r1.json](assets/demo/r1.json) / [r2.json](assets/demo/r2.json) 是虚构训练资料，来源文本也随包提供。`example.org` 是说明用地址，不要请求它获取真实披露。

| 输入 | 应出现的结果 |
|---|---|
| 旧版：上季收入 100，披露 Alpha 产品 | 建立两条候选来源断言 |
| 新版：本季收入 120，调整后 115；上季比较数改为 105 | 本季口径分开；上季 100/105 并存为冲突 |
| 新版没有再次提及 Alpha | 旧关系保留，不推断产品下线 |
| 再导入相同新版 | 不重复新增来源断言 |

需要 Python 3.10+。在技能目录下执行，`--out` 请换成**用户工作目录中的全新路径**，不要把运行产物写进技能或仓库：

```sh
python3 scripts/ontology.py --help
python3 scripts/ontology.py build assets/demo/r1.json --out /path/to/work/v1
python3 scripts/ontology.py update assets/demo/r2.json --base /path/to/work/v1 --out /path/to/work/v2
python3 scripts/ontology.py validate /path/to/work/v2
python3 scripts/ontology.py query /path/to/work/v2 --concept metric:revenue --period 2026Q1
python3 scripts/ontology.py query /path/to/work/v2 --concept metric:revenue --period 2026Q1 --basis IFRS
python3 scripts/ontology.py export-okf /path/to/work/v2 --out /path/to/work/okf-v2
```

查询返回 `needs_scope` 时，查看 `scopes`：可按 `--unit`、`--valid-from`、`--valid-to` 精确筛选，或用 `--fact` 选择一个返回的事实 ID。事实 ID 保留该范围内全部冲突。有效期筛选是精确边界匹配，不是历史时点推断。报告逐行显示事实 ID、有效期及冲突标记。

Windows 可用 `python` 并将输出路径替换为自己的工作目录。示例路径是占位符，不能原样当作你的目录。

## 安装和真实运行

将本目录放入宿主客户端支持的 skills 目录，或通过仓库支持的 skills CLI 安装：

```sh
npx skills add huhoo/cue-awesome --skill cue-omni-ontology
```

该命令需要 Node.js/npm。只运行 Python 示例不需要 Node.js。本包不自动安装 Omni 依赖或写入 MCP 配置。

配置官方 Omni Reader MCP，按其 [setup](https://github.com/sensedeal/cue-skills/blob/main/cue-omni-reader/references/setup.md) 完成连接。安装/目录授权依照宿主及上游流程；key 放入自己的凭据设施，勿粘贴到聊天或 Issues。当前试用额度与计费以服务端为准。

真实任务由 Agent 完成：公开材料 → Omni 解析与证据快照 → 按小模型抽取 JSON → 离线打包与验证 → 语义复核 → 回答/更新。文件证据范围需从真实解析字节计算，不能猜页码或用 operation_id 代替来源。

已连接 Omni 的客户端可直接用上面的自然语言任务。不同宿主和模型的质量需要实测；协议兼容不等于每个客户端均已验收。

## 交付

- `report.md`：来源事实、口径、变化与冲突的审阅表。
- `knowledge.json`：候选定义、实体、断言与审阅记录。
- `sources.jsonl` / `evidence/`：原始 URL、时间、定位与解析文本快照。
- `changes.json` / `run.json`：版本变化、检查计数及软件版本。
- `extraction-notes.md`：Agent 另写的模型、范围、失败来源及语义检查说明。
- 可选 OKF：同一版本的概念文件；目标为 0.2 核心子集，保持 draft，不表示外部消费者已导入成功。

报告先给用户看；机器结果供后续任务使用。与财报点评、尽调等现有 skill 的自动适配尚未建立，消费时继续执行各自的检查。

## 验证状态

见 [verification.md](references/verification.md)，其中区分实际运行、保存结果回放、合成边界与尚未测试项。本包不把原型财报开发检查当作通用准确率。哈希与范围检查不证明语义正确。

本地自检（无网络、无计费）：

```sh
python3 -B scripts/test_ontology.py
```

## 反馈与企业场景

有错误、希望用于日常工作，或需要内部材料/本地部署，可以先生成本地反馈草稿：

```sh
python3 scripts/ontology.py feedback /path/to/work/v2 --out /path/to/work/feedback.json
```

脚本不发送数据。检查草稿后，由你决定是否通过 [公开 Issues](https://github.com/huhoo/cue-awesome/issues/new) 提交可公开的问题。商业背景、联系信息和内部材料使用你与维护者另行约定的私有渠道。

没有使用遥测；下载量不代表成功运行。最有价值的反馈是：自己的资料能否完成任务、是否再次更新、查证和纠错是否省时，以及需要接入哪个现有流程。

## 边界与许可

v0.1 存储直接披露的断言，保留冲突和历史；计算结果另在回答中说明。定义都是候选，不自动发布企业 schema。审阅命令是本地记录，不是 IAM 或生产审批。本地文件提交到云端不等于完整本地部署。

代码及说明采用 MIT，见 [LICENSE](LICENSE)。合成样例不指向真实企业；真实公开来源仅按各自使用条件引用，不因公开可读就默认允许整份重分发。代码无网络调用或遥测；Agent 的官方解析调用仍使用相应服务和模型。
