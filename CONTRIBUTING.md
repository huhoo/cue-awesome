# 贡献规范（cue-awesome）

**[中文](CONTRIBUTING.md) · [English](CONTRIBUTING.en.md)**

这个仓库会被不同的人、不同的 agent 会话往里加 skill，所以规则写死在文件和 CI 里，不靠口头约定。

---

## 0. 三条底线（违反直接打回）

1. **不提交密钥与个人信息**：token、API key、`.env`、私钥、内部域名、内网地址、未脱敏的客户/自然人信息。
2. **不提交产物**：`dist/`、`build/`、`*.zip`、`__pycache__/`、`*.pyc`。
3. **不编造来源**：凡是事实陈述与外部链接，必须带可核实来源；查不到就留空，不许编 URL。

另外：**不要 `git add .`**。提交前 `git status` 逐条看一遍，本地产物就是这么混进去的。

---

## 1. 仓库结构

```
cue-awesome/
├── README.md / README.zh-CN.md      集合仓说明（英文权威）
├── CONTRIBUTING.md / .en.md         本文件
├── LICENSE.md  NOTICE.md
├── docs/                            仓库级文档（i18n 规范等）
├── scripts/check_skills.py          全仓校验脚本
├── .github/                         PR / issue 模板 + CI
└── <skill-name>/                    一个 skill 一个目录
```

**判定规则：顶层目录里含 `SKILL.md` 的，就是一个 skill。** 加新 skill = 加一个顶层目录，不需要改任何注册表。`docs/`、`scripts/`、`.github/` 不算 skill。

---

## 2. 新增一个 skill

目录名 = frontmatter 里的 `name`（小写、连字符，如 `competitive-brief`）。

### 必备文件

| 文件 | 说明 |
|---|---|
| `SKILL.md` | 主指令，必须有 YAML frontmatter |
| `README.md` | 给人看：用途、边界、上手、依赖 |

可选：`scripts/`、`references/`、`assets/`、`examples/`、`CHANGELOG.md`、`manifest.yaml`、`README.en.md`。

### frontmatter 字段

| 字段 | 必填 | 说明 |
|---|---|---|
| `name` | ✅ | **必须等于目录名**，校验脚本会查 |
| `description` | ✅ | 用途 + 触发词。**中英双语触发词都要写** —— 只有中文触发词，英文用户永远触发不到 |
| `version` | ✅ | `x.y.z`。顶层 `version:` 或 `metadata.version:` 二选一，**不要两处都写且不一致** |
| `license` | 建议 | MIT |
| `slug` / `displayName` / `summary` / `tags` / `metadata` | 可选 | 上架技能市场用；`agent_created: true` 表示由 agent 生成 |

`description` 触发词示例（中英并列）：

```
Triggers: 竞品分析 / 竞品简报 / 这个市场要不要进; competitive analysis / competitor comparison / battlecard
```

---

## 3. 修改已有 skill

- **版本号必须递增**：修 bug → patch（`0.1.0`→`0.1.1`）；加能力 / 改流程 → minor（`0.1.0`→`0.2.0`）；0.x 阶段的不兼容重构也走 minor。
- **双语版本同步**：`SKILL.md` 与 `SKILL.zh-CN.md` / `README.md` 与 `README.en.md` 的 `version` 必须一致，脚本会查。
- **CHANGELOG**：有 `CHANGELOG.md` 的 skill，最新条目版本要等于 `SKILL.md` 的 `version`（不一致只是 WARN，但请顺手对齐）。
- **脚本**：`scripts/` 下的脚本要 `--help` 可跑；默认零网络请求（除非这个 skill 本身就是网络能力）。
- **双语规则细则**见 [`docs/i18n.zh-CN.md`](docs/i18n.zh-CN.md)：无后缀 = 权威版，`.en` / `.zh-CN` = 译文，改一个就要改另一个。

---

## 4. Commit 规范

用 Conventional Commits，scope 写 skill 目录名：

```
<type>(<skill 名>): <简述>

正文：写「为什么」，不写「改了什么」（diff 里能看到）
```

| type | 用于 |
|---|---|
| `feat` | 新 skill、新能力 |
| `fix` | 修 bug |
| `docs` | 文档、README、规范 |
| `i18n` | 双语文件 |
| `refactor` | 重构，不改行为 |
| `test` / `chore` | 测试、杂项 |

示例：

```
feat(competitive-brief): 证据链加来源可信度分级
fix(journal-draft): 修跨目录调用时图源解析失败
i18n(journal-draft): 补 README 英文版
docs(repo): 新增贡献规范与 skill 校验脚本
refactor(repo): 顶层内容移入子目录，改为集合仓结构
```

规则：**一个 commit 只做一件事**；同时改两个 skill 就拆两个 commit。仓库级改动用 `repo` 或省略 scope。

---

## 5. PR 规范

**分支命名**：`skill/<name>` · `fix/<name>-<要点>` · `docs/<主题>` · `i18n/<name>`

**PR 标题**：同 commit 标题格式（`type(scope): 简述`）。

**必须做到**：

- 跑过 `python scripts/check_skills.py`，**0 error**（CI 也会跑，红了不合入）
- 新 skill：一句话用途、触发词、依赖、怎么验证
- 改 skill：版本号已递增 + CHANGELOG 条目
- 双语文件已同步
- 无密钥、无本地绝对路径、无打包产物
- **一个 PR 只动一个 skill**；仓库级改动单独开 PR

**合并方式**：squash merge，PR 标题即最终 commit 标题；main 保持线性（用 rebase，不留 merge commit）。

---

## 6. 自动门禁

```bash
python scripts/check_skills.py            # 全仓校验
python scripts/check_skills.py --strict   # warning 也算失败
```

检查项：目录名 == `name` · `version` 存在且为 x.y.z · `description`/`summary` 非空 · README 存在 · 双语对完整且 frontmatter 一致 · CHANGELOG 版本对齐 · 无嵌套 `.git` · 无密钥文件 · 无打包产物。

CI：`.github/workflows/skill-lint.yml`，每次 push / PR 自动跑（error 才 fail，warning 只提示）。

---

## 7. 目录里不收什么

- 只有想法没有 `SKILL.md` 的目录（先开 issue 提案）
- 密钥、token、个人数据、内部域名
- 编造的来源链接、未脱敏的客户与自然人信息（脱敏做法参考 `journal-draft/NOTICE.md`）
- 别人家 skill 的直接拷贝（改写的请注明来源与许可）
