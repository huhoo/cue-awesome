# 贡献规范（cue-awesome）

**[中文](CONTRIBUTING.md) · [English](CONTRIBUTING.en.md)**

这个仓库会被不同的人、不同的 agent 会话往里加 skill，所以规则写死在文件和 CI 里，不靠口头约定。

---

## 0. 三条底线（违反直接打回）

### 公开面卫生(发布前硬门,2026-10-10 立;Owner 点名)

**发布包是给用户用的成品,不是施工日志。** 以下五类过程遥测禁入一切公开面(`SKILL*.md`/`README*.md`/`assets/`/`references/`),CHANGELOG 同守其中①③④⑤:
① **工单/票号**(M1xx、PR# 等内部流水)——外部读者无从解释;
② **工作区悬空路径**——`verify/`、`logs/`、`dispatch/`、`BOARD` 等仓外或他目录指路;包内指路只许相对本包且**文件真实存在**(机检可验);
③ **施工状态语**——「证据票在途」「候账」「候 Owner 裁」「随我铃」;
④ **内部时点戳**——「截至 2026-xx-xx 未立」类过程日期;能力边界直接写边界本身(「本件不做学术库检索」),何时测的不写在墙上;
⑤ **过程归因句**——「需求凭据=XX 榜 311K」「实测由 M18x 跑回」这类出处叙事:该进内部账,不该进成品;成品只写**结论形制**(能做什么、不能做什么、以什么为准——如「音视频:本地小段/切片支持,整场视频不支持,以通道返回为准」)。
判据口径:能力句直述、指路可跟随、归因留内部。违反=发布打回,与红线同级。**历史条目不回改**(留痕原则):本条自生效日起的新条目一律合规;既有 CHANGELOG 条目在其文件下次占版本位时顺手清,不为卫生单独烧位;成品面(SKILL/README/assets/references)则**全量清理,不等下次车**。

**记录性引用不复现词面（五禁的延伸）**：写清理记录、勘正说明或探针键面时，**不得把被禁词面原样抄进任何公开面（含 CHANGELOG）**——要用不可命中的指代（如「上一票票面所列那批对照词」）。违规词表只存在于票面与内部账；成品面与历史条目都只写指代。勘正＝新增条目声明「某条曾复现词面、现改为指代，事实以本条与内部账为准」，**不是把旧条目抹成没发生过**——「历史不回改」防的是失真叙述，不是保护一处红线词面。


**发布物自跑(上架前的最后一道,2026-10-12 立)**:公开面每写一句「自带守护样」「可跑 `--selftest`」「见 `fixtures/…`」,都是在承诺用户手上的一次执行。**仓内跑绿不等于发布物跑绿**——打包排除面一旦剔掉样本目录,成品面那句能力在用户侧就失效。三条判定,对象是**解包后的发布物**:① 成品面里的包内相对指路,必须在发布物内真实存在;② 发布物含自测入口的,必须在解包件里真跑一次且退码 0;③ 排除面与能力宣称冲突时,**裁样本集,不删能力句**(在包体上限内取舍)。仓内校验看不见压缩包里缺了什么,所以这三条要落成发布物层的机器门,不靠谁记得。


**两种输入，两把判据（口径收口,2026-10-12 立）**：同一条指路,在两种输入下由两把门各判各的,**结论可以不同,且都不算矛盾**——

- **仓内那把门**判「成品面的指路在**工作树里**是否存在」＋五禁词面。跨包互引在仓内跟得到,这一把就放行。
- **发布物那把门**判「同一条指路在**解包件里**是否存在」＋自测入口真跑＋体积按 zip 字节。仓内跟得到而发布物里空着的,这一把判红。

两条可跑命令(不是伪码)：

```bash
python3 scripts/check_public_hygiene.py            # 仓内：全仓成品面五禁＋指路跟随（有 ERROR 则退码 1）
python3 scripts/check_shipment.py --repo-scan .    # 发布物侧：按打包配方逐包建 zip→解包→三判（样本被剔掉就判红，这正是要看的）
```

随包态(样本齐发)那一判要从发布侧打包口拿到 zip 之后跑,对象可以是解包目录,也可以是 zip 本体：

```bash
unzip -q <包名>.zip -d <解包目录>
python3 scripts/check_shipment.py <解包目录> --pkg <包名>   # 输入是目录：体积不判，只记一条 WARN
python3 scripts/check_shipment.py <包名>.zip                # 输入是 zip：体积才判，按 zip 字节
```

**禁则：凡报「过了／红了／第几枚绿」,必带输入形制**（仓内工作树 vs 随包态解包件 vs 渠道回下载）。两把门读数不一致时,先对输入再对判据,**不许把一门的绿当成另一门的绿转述**;仓内字节、自产 zip 字节与渠道回下载字节三者**不可互换引用**(排除面与压缩形制都不同)。

**一句边界：渠道拒收格式由构建排除面承担,不得为了「让指路跟随」把被拒格式塞进包内**。正解是把成品面那句话改成文字说明,或改指发布物内确实带着的所在——改排除面去哄门变绿,等于把承诺移到用户看不见的地方。


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
| `description` | ✅ | 用途 + 触发词。**中英两语的可懂入口都要有**——但不必为凑英文触发词堆词（审方裁形 2026-09-28：`Triggers:` 尾块非强制，确有需要才补真实英文关键词，词项须有包内依据、字段不超 C-36 限）。英文入口不足时，允许在 README 实况交代「建议直接点名 skill」 |
| `version` | ✅ | `x.y.z`。**只写顶层 `version:`**——嵌套 `metadata.version:` 即 lint ERROR（扁平解析器会 last-wins 静默覆盖真值，K-11 教训） |
| `license` | 建议 | MIT |
| `slug` / `displayName` / `summary` / `tags` / `metadata` | 可选 | 上架技能市场用；`agent_created: true` 表示由 agent 生成 |

`description` 触发词示例（中英并列）：

```
Triggers: 竞品分析 / 竞品简报 / 这个市场要不要进; competitive analysis / competitor comparison / battlecard
```

### 门面四问（新件与改名件的上架门槛，2026-10-09 立）

1. **名字带不带价值点**：`displayName` 说清「帮你做什么 + 凭什么信」（样：`公告事件速读卡·关键数逐字带出处`）；
2. **简介实不实**：`summary` ≤80、`description` ≤300，**长度必须脚本实测**（wc -m 式，禁手数）；
3. **有没有未实测的数字**：名/简介/描述面禁出现未实测的耗时、命中率、增长率（实测后可入，出处随票）；
4. **打开能不能干活**：README 第一节给「第一次进入」的动词级动作（对标 civil 门牌形制），不堆形容词。

---

## 3. 修改已有 skill

- **版本号必须递增**：修 bug → patch（`0.1.0`→`0.1.1`）；加能力 / 改流程 → minor（`0.1.0`→`0.2.0`）；0.x 阶段的不兼容重构也走 minor。
- **双语版本同步**：`SKILL.md` 与 `SKILL.zh-CN.md` / `README.md` 与 `README.en.md` 的 `version` 必须一致，脚本会查。
- **CHANGELOG**：有 `CHANGELOG.md` 的 skill，最新条目版本要等于 `SKILL.md` 的 `version`（不一致只是 WARN，但请顺手对齐）。头部形制：首条即版本条（`### x.y.z` 起，不留 `Unreleased` 壳），插入用版本条标题做锚、锚失配必须硬失败。
- **脚本**：`scripts/` 下的脚本要 `--help` 可跑；默认零网络请求（除非这个 skill 本身就是网络能力）。
- **双语规则细则**见 [`docs/i18n.zh-CN.md`](docs/i18n.zh-CN.md)：无后缀 = 权威版，`.en` / `.zh-CN` = 译文，改一个就要改另一个。
- **换装 release 资产**：`gh release upload --clobber` 的目标资产名取自上传文件的 basename——文件名必须与仓内登记的资产名逐一对上，错名上传＝静默新增杂项资产而旧件原样在架。换装后必做供体面复核：重新下载该资产、比对 sha256 与本地构建同值；只核「SKILL.md 版本行」拦不住内容回吐旧字节的场景。误挂的杂项资产当场 `DELETE releases/assets/<id>` 清掉再收工。

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

> **模板本身要过门**（4.1 实测回报）：引用「词表只存在于〔两个常用施工语书写形〕与内部账」这类句式会二次命中——**该词表的两个常用书写形都在内**。可用写法：指代写成「该子句转述第三方做法的数据来源要求」，键面归属写成「键面只存续于内部对账记录」。（本文件因规则定义块必须引用被禁模式本身，自扫固定存 5 条，属已知例外，另案呈裁；本枚 commit 同时勘正：前一 commit 文案引用上一枚时写了不存在的哈希前缀「9f0…」，实为 `def3c78`——单号未断言即入文案，同族入账。）