# cue-omni-ontology

**把公开资料变成可更新、可查证的业务知识。**

给 Agent 两份报告或公告，拿到三个结果：**有依据的回答、能展开原文的变化简报、下次可继续更新的知识包。** 适合财报跟踪、公开供应商尽调和产品/竞品公告监测。

**本文件为中文主面;英文版为包内 `README.en.md`(仓库内查阅,渠道页不解析相对链接)。**

## 先看实际价值

[微软两期公开披露实测](assets/public-example/live-preview.md)：新解析 → 抽取 → 建立/更新 → 带证据回答，已完整跑通。

| 你遇到的问题 | 这个 skill 交付什么 |
|---|---|
| 同一个指标为什么有两个数字？ | 保留期间、单位、口径及限定条件，列出各自依据。 |
| 新报告发布后，需要从头整理吗？ | 在旧知识包上更新，保留历史，标出新增支持与冲突。 |
| 这个结论从哪来，能核对吗？ | 搜索简报、展开原文摘录，回到真实来源和位置。 |
| 我想接入后续 Agent 工作流 | 复用结构化知识包；可导出 draft OKF 核心子集。 |

用户不需要先设计完整企业本体。默认从一个主体、2–5 份公开来源和一个明确问题开始。

## 第一次试用：无需 API key

安装后直接对 Agent 说：

> 使用 cue-omni-ontology，先用自带样例演示：加入新材料后，哪些事实新增、哪些冲突、依据在哪里？

也可以在技能目录运行一条命令（Python 3.10+）：

```sh
python3 scripts/ontology.py demo --out /path/to/work/cue-demo
```

把示例路径换成自己的**全新工作目录**，然后打开 `cue-demo/brief/brief.html`。不需要启动服务；浏览器可搜索、筛选新增/冲突、展开原文。不能打开 HTML 的客户端可以读取同目录 `brief.md` / `brief.json`。

演示明确使用虚构材料，不联网、不调用解析 API：上季收入 100 后被披露为 105，两个说法并存为冲突；本季 120 与调整后 115 分开；新版未提及的 Alpha 产品保留历史，不推断下线。

## 安装与真实资料

```sh
npx skills add huhoo/cue-awesome --skill cue-omni-ontology
```

该安装方式需要 Node.js/npm；直接复制本目录到宿主支持的 skills 位置也可。离线工具只依赖 Python。真实解析复用官方 [cue-omni-reader](https://github.com/sensedeal/cue-skills/tree/main/cue-omni-reader)，按其 [setup](https://github.com/sensedeal/cue-skills/blob/main/cue-omni-reader/references/setup.md) 连接 MCP 并配置凭据。此包不自动安装或配置 Omni。key 放入自己的凭据设施，不发到聊天或 Issues。

配置好后，给 Agent 真实来源与问题：

```text
使用 cue-omni-ontology，根据这两份公开报告回答：
1. 新一期新增了什么披露？
2. 哪些数字需要区分口径，不能直接比较？
3. 哪些问题缺少依据？
给我能展开原文的简报，并保存下次可更新的知识包。
```

第二次使用：

```text
把这份新公告加入已有知识包，给我变化简报。
保留旧记录，突出需要复核的冲突，不把“未提及”当成删除。
```

更多业务入口见 [task-recipes.md](references/task-recipes.md)。官方解析器负责读取资料，宿主模型负责语义抽取，离线工具负责证据定位、版本、查询和简报。协议兼容不代表每个客户端均已完成验收。

## 让 Agent 少做机械工作

Agent 可以逐字复制原文作为证据，不再手工计算哈希与 UTF-8 偏移。见 [quote-draft.json](assets/demo/quote-draft.json) 和[摘录输入说明](references/quote-input.md)：

```sh
python3 scripts/ontology.py prepare assets/demo/quote-draft.json --out /path/to/work/prepared
python3 scripts/ontology.py build /path/to/work/prepared/input.json --out /path/to/work/v1
python3 scripts/ontology.py update assets/demo/r2.json --base /path/to/work/v1 --out /path/to/work/v2
python3 scripts/ontology.py brief /path/to/work/v2 --base /path/to/work/v1 --out /path/to/work/brief
python3 scripts/ontology.py query /path/to/work/v2 --concept metric:revenue --period 2026Q1 --with-evidence
```

重复摘录会要求增加上下文或明确出现次数，不做模糊匹配。查询返回 `needs_scope` 时，可用口径、单位、有效期或返回的事实 ID 进一步选择。`--with-evidence` 附原文预览，截断时明确标注。匹配成功不证明语义正确，仍需核对表头、脚注及限定条件。

## 交付与验证

- **阅读入口**：离线 `brief.html`、Markdown 对应版，展示来源事实、范围、变化和证据摘录。
- **可复用知识**：`knowledge.json`、`sources.jsonl`、`changes.json`、`run.json`、精确证据快照。
- **抽取说明**：Agent 另写 `extraction-notes.md`，说明问题范围、失败来源及语义复核。
- **可选交换**：`export-okf` 输出 draft 概念文件，目标为 OKF 0.2 核心子集；外部消费者兼容性另行验证。

[验证记录](references/verification.md) 区分真实新解析、旧结果回放、独立合成任务和未验证范围。[微软实测](references/live-verification.md) 涉及两个来源、21 条来源断言，全部 11 条旧断言在更新后保留。它证明这一任务流程可完成，不代表通用准确率或已证实的客户 ROI。

本地自检：

```sh
python3 -B scripts/test_ontology.py
```

## 试用后，最希望听到什么？

**你的资料能否完成任务？你会不会加入第二份新材料再用一次？哪一步仍然需要大量纠错？** 这比下载量更能帮助我们改进产品。

可运行 `feedback PACKAGE --out NEW_FILE` 生成本地反馈草稿，检查后自行选择是否提交[公开问题](https://github.com/huhoo/cue-awesome/issues/new)。没有自动上传。内部材料、联系信息及商业背景通过与维护者另行约定的私有渠道交流。

如果你需要定期跟踪内部资料、接入现有 Agent/ERP/CRM、行业 schema 审阅或完整本地部署，请描述**具体任务、更新频率、当前查证成本和需要接入的流程**。这些是企业场景的讨论入口，不是此公开 skill 已交付的生产能力。

## 边界与许可

只保存直接披露的断言；计算与判断在回答中说明依据。定义保持候选，审阅是本地记录，不提供企业 IAM 或自动行动权限。上传本地文件到云端解析不等于完整本地部署。

简报含有限长度的原文摘录；完整知识包含解析文本，分享前检查授权范围和来源使用条件。代码及说明为 [MIT](LICENSE)；公开可读不等于允许重分发整份报告。中文 README 为权威说明；英文 SKILL.md 为权威 Agent 指令，双语文件同步维护。
