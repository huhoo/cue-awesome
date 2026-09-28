# Changelog

本文件遵循 keep-a-changelog;版本权威=各 SKILL.md frontmatter 现值。

### 0.2.2 — 2026-09-28（lead·主从倒正,Owner 二点）

- SKILL 主文件由英文改为**中文主**(原 SKILL.md→SKILL.en.md,原 SKILL.zh-CN.md→SKILL.md):skillhub 是中文社区,九件主面语言至此全部一致。
- 四处「中文·English」切换行改为**纯文字指路**——渠道页不解析相对链接,可点切换在此环境是死 UI,不装能点。
- 两文口径同步句改「以代码与夹具现值为准」,与 C-46 一致。

### 0.2.2（机器面·M158）— 2026-09-28 版本戳同号化+一致性锁（M156 判词第 6 项）

- 审方仓外 demo 实测:0.2.2 流程产出的 run.json.skill_version 仍刻脚本常量 0.2.0——凭据分裂,且违本文件顶章「版本权威=各 SKILL.md frontmatter 现值」自书规矩。**案①同号化**:VERSION 对齐 frontmatter 现值 0.2.2(理据:让 run.json 自证为真,优于一行改字段+改名注的「双轨并见」;后者前提是文案面把区别写可见,改动预算越界)。SCHEMA_VERSION(0.1.0)保持独立轨不动——协议版本与 skill 版本分离本属设计意图(:148/:347 皆协议面),此单只修「冒充 skill 版本的字段」。
- 新增一致性锁 `VersionConsistency.test_script_version_equals_skill_frontmatter`:现读 SKILL.md frontmatter 断言相等,今后任何一侧版本动作不同步即 FAIL(反证在案:VERSION 人为改 9.9.9 → 锁报 `'9.9.9' != '0.2.2'`)。测试 47→**48 项实测 OK**;lint 9 skill 0 error 0 warning;本包 SKILL/README 零触碰,文案面 M157 各写各面互不抄。

### 0.2.1 — 2026-09-28（lead·渠道一致性修正,Owner 点名）

- 渠道 listing description 由英文主改为**中文主**(≤300、三段:拿到什么/机器挡什么/适合与不适合),英文触发词移至尾部保留,零丢失。
- 两份 README 头部「v0.2.0 公开试验版」活版本+状态尾句删除(指针化纪律,对齐族规)。
- 新建本 CHANGELOG(族规补齐:此前为九件中唯一缺 CHANGELOG 的包)。
- 语言切换行经查与姊妹件同制(链接目标四件俱在),保留不动。

### 0.2.0 — 2026-09-28（Owner:v0.2 evidence briefs 与零密钥 demo）

- 上游历史(仓内 PR#1-4):v0.1.1 audited public knowledge workflow → v0.2 evidence briefs;Windows 首跑兼容三修(.gitattributes LF、symlink 测试平台跳过、claim_kind 默认 reported),47 项测试。

### 0.1.1 — 2026-09-27（Owner:audited public knowledge workflow 首发）

- 初始上架前审计版,细节以 git log(PR#1)为准。
