# NOTICE — 来源说明与脱敏声明

## 一、样例已脱敏

本技能随包提供的两个成品样例与一个 `+learn` 中间产物样例，**全部经过实体脱敏**：

| 目录 | 内容 |
|---|---|
| `examples/journal-qiming-regional/` | 成品样例 A：A4 单栏 / 双月刊 / 短条目+长文混合 |
| `examples/journal-hengshi-observation/` | 成品样例 B：非 A4 双栏 / 月刊 / 纯文章型（反向样本） |
| `assets/examples/qiming-regional-sample/` | `+learn` 阶段的中间产物（StyleSpec / semantic / UnitPattern） |

**已替换为虚构合成实体的字段**：机构名与刊物名、自然人姓名、客户与项目名称、
源文件名与站点域名、正文摘录语料（含法规名称的具体编号）。

**保留的是方法学实测值**：版面网格与版心尺寸、字号序列与行距、色板色值、
固定件坐标、页数配比、单元字数分布、slot 定义与句式结构。

**「结构层文字」如实说明**：栏目标题、文章标题与章节小标题（形如「前言：……」
「第一部分：……」）按原样保留。判断依据是它们属于短语与通用结构用语，
既不构成受保护的表达，也不含任何自然人、客户或机构的可识别信息。

**选题领域同样保留**：样例涉及的题材（公开的金融监管与跨境资本市场动态，
含公开法规与公开机构名）按原样保留 —— 这些是公开信息，不涉及第三方非公开内容。
若你介意这层「选题指纹」，最彻底的做法是把 `assets/examples/` 整个替换为自己抽取的样例。

**逐字引用已清除**：样例中原本存在的第三方正文摘录段落，已全部改写为标注「示意语料」
的合成段落；`assets/diagram-templates/` 中承载实质内容的那份图定义也已重写为中性的
角色化示例（只保留布局结构）。

也就是说：样例演示的是**这套流水线怎么工作**，不指向任何一家真实机构或其出版物，
也不复现任何第三方出版物的正文段落。

## 二、样例的用途边界

样例是**教学与起手参考**：

- ✅ 用来理解 StyleSpec / UnitPattern / content.json 三者如何配合
- ✅ 照着结构改造成你自家的刊（机构名、刊物名、栏目、模板本来就要全部换掉）
- ✅ 对照「顺向样本」与「反向样本」理解框架的能力边界

不应当作：

- ❌ 任何真实机构的版式规范来引用
- ❌ 现成可发的稿件（其中的人物、机构、项目均为虚构）

## 三、第三方组件

| 组件 | 性质 | 许可 |
|---|---|---|
| `scripts/*.py` | 本技能原创 | MIT（见 `LICENSE.md`） |
| 中文字体（`gen_diagram.py` 运行时调用系统字体） | **不随包分发**，仅在运行时读取本机已安装字体 | 遵循用户本机字体许可 |
| `pymupdf` / `python-docx` / `pillow` | 可选运行时依赖，**不随包分发** | 各自许可 |

本技能**不内嵌任何第三方字体、图片或数据文件**。

## 四、无网络行为声明

`scripts/` 下的 12 个脚本**不含任何网络请求代码**：无 `requests` / `urllib` / `socket`
调用，无 `subprocess` / `os.system` 执行外部命令，无遥测。数据出站只发生在 agent 侧
主动调用外部工具时（例如检索公开资料），由用户可见地触发。

配图走 agent 内置的多模态能力，**不索取任何 API key、不引入外部图床或模型端点**。

## 五、打包发布

`.gitignore` 只管 git，**不管 zip**。打包前必须显式清缓存：

```bash
cd ~/.workbuddy/skills/journal-draft
find . -name '__pycache__' -type d -prune -exec rm -rf {} +
find . -name '*.pyc' -delete
rm -rf smoke build out out2

# 生成发布包（含隐藏文件以外的全部内容）
cd .. && zip -r journal-draft.zip journal-draft \
  -x '*/__pycache__/*' -x '*.pyc' -x '*/smoke/*'
```

**发布前自检**（不通过就别发）：

| 检查 | 命令 | 期望 |
|---|---|---|
| 无密钥 | `grep -riE 'api[_-]?key\|secret\|password\|token' . \| grep -v '(CUE_API_KEY\|不加 key\|no key\|无 key)'` | 无实质命中 |
| 无缓存 | `find . -name '__pycache__' -o -name '*.pyc'` | 空 |
| 无绝对路径 | `grep -rn 'C:\\\\Users\|/Users/[a-z]' .` | 无（字体回落白名单除外） |
| **随包 HTML 无绝对路径** | `grep -c 'file:///\|[A-Za-z]:/' assets/demo/demo.html` | `0`（见下方说明） |
| **无真实实体残留** | 用 `skill-release-audit` 的 `sanitize_entities.py --verify` | 0 命中 |
| 脚本可跑 | `for s in scripts/*.py; do python "$s" --help >/dev/null \|\| echo "FAIL $s"; done` | 12/12 通过 |
| 脚本三份一致 | 对比 `scripts/` 与 `examples/*/scripts/` 的 md5 | 全部相同 |
| 文档无断链 | 逐条相对链接检查 | 0 断链 |
| 关键门禁实测 | 跑一次 README 的冒烟命令 | 打印 `OK pages=... unknown=0`（`exit 1` 属预期） |

> **关于「随包 HTML 无绝对路径」**：`build_draft.py` 的 `img_src()` 在图片文件存在时
> 会输出 `file:///` + **绝对路径**，所以每次重新渲染 `assets/demo/demo.html` 之后，
> 都必须再做一次「绝对路径 → 相对路径」替换（把 `file:///<本机路径>/assets/demo/` 换成空串），
> 否则既会在别人机器上打不开图，也会把本机路径带进发布包。
> 本机自用的稿子不受影响；要分发时才需要处理。

---

# 第二部分 · 金融研究套件的基座出处

以上第一节（一～五）针对 `journal-draft` 的样例脱敏与打包声明。本节单独说明**金融研究套件**（首批为 `cn-earnings-note`，后续含行业景气全景 / 催化剂日历 / 公司一页纸 / 公开信息预尽调）的方法与术语出处。

## 一、方法论基座：anthropics/financial-services（Apache-2.0）

本套件的**任务切分、报告骨架与交付流程**改写自 `anthropics/financial-services` 技能集合（earnings-analysis 等），采用 **Apache-2.0** 授权。此处为「改写」而非「拷贝」：仅借鉴其方法论结构，不搬运其代码、文本或数据。

## 二、本土化实践参考：道以研究院 dao-financial-services v0.1.9（MIT）

A股化过程中的 **CAS 术语、合规词表、`[待人工]`（评级 / 目标价一律人工复核）等本土化实践**，本土化实践参考为道以研究院的 `dao-financial-services` 功能包（**v0.1.9**，**MIT**）。该功能包无公开代码仓，但可经官方端点公开下载查阅：<https://hzddyy.com/stdd/api/download/dao>（返回 `application/zip`，文件名 `Dao-financial-services-0.1.9.zip`，版本号与本文引用自证一致）。我方在 MIT 允许范围内做的是**不同交付物的重实现**（报告型 vs 其数字型），术语与合规commons 致敬在此声明。

## 三、重实现，非拷贝

- **数据层完全替换为 Cue 通道**：结构化披露走 Cue 数据 MCP 域、原文走 omni-reader 解析、横向对照走 cue-research 深研；不沿用基座或参考方的任何数据接口。
- 交付物形态、门禁与触发词均为本仓独立设计。

## 四、合规词表（D1）决策待定

当前 `cn-earnings-note` 采用**内置最小黑名单**。是否升级为「致敬 / 复用 dao 词表」或自写全量词表，属 **D1 拍板项**，P1 真实主体实测已完成（2026-09-18/19），拍板仍未决——定夺后由 lead 记录进 runbook。在此之前，本套件不对具体合规词表范围作对外承诺。

