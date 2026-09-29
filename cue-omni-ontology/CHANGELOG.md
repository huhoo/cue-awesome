# Changelog

本文件遵循 keep-a-changelog;版本权威=各 SKILL.md frontmatter 现值。

### 0.2.3（机器面·M158+追加）— 2026-09-28 版本戳同号化+双份 frontmatter 一致性锁（M156 第 6 项,M158 追加条闭 EN 面漂移盲区）

- 审方仓外 demo 实测:0.2.2 流程产出的 run.json.skill_version 仍刻脚本常量 0.2.0——凭据分裂,且违本文件顶章「版本权威=各 SKILL.md frontmatter 现值」自书规矩。**案①同号化**:VERSION 与两份 frontmatter 同号(裁单「0.2.3 版本位同批:VERSION+两份 frontmatter 一起走」,三处现值均 0.2.3)。SCHEMA_VERSION(0.1.0)保持独立轨不动——协议版本与 skill 版本分离本属设计意图(:148/:347 皆协议面),此单只修「冒充 skill 版本的字段」。案②(双轨并见+文案注明)不取:字段名就叫 skill_version,让它自证为真优于加解释,且「写可见」的前提工作在文案面、越「只常量+锁」预算。
- **追加条(4.1 发现,lead 转)**:锁初版只读 SKILL.md——本包 SKILL.en.md 同带 version 字段,两文漂移测不到。**判形=双读不撤字段**:渠道加载器可能各读自面 frontmatter,撤 EN 版位=给未验证的读方制造风险;等式收为「脚本==SKILL.md==SKILL.en.md 三点同号」,任何一处独走即 FAIL,零破坏面。锁测试 `VersionConsistency.test_script_version_equals_both_skill_frontmatter`(subTest 两份逐面);反证两笔实测:**脚本漂 9.9.9→恰 2 failures(两面各逮一次,subTest 归属正确)**;**仅 EN 独漂 0.2.9→恰该面 1 failure、中面不告**(旧单读锁对此哑巴——追加条所要闭的正是这个盲区),EN 面测后原样恢复、复跑全绿。
- 测试 47→**48 项实测 OK**(锁 +1);lint 9 skill 0 error 0 warning。改动面:ontology.py 常量一行、两份 SKILL frontmatter 各一行(裁单授权)、test_ontology.py 锁+import re、本机器条;文案面 M157 各写各面互不抄。

### 0.2.2 — 2026-09-28（lead·主从倒正,Owner 二点）

- SKILL 主文件由英文改为**中文主**(原 SKILL.md→SKILL.en.md,原 SKILL.zh-CN.md→SKILL.md):skillhub 是中文社区,九件主面语言至此全部一致。
- 四处「中文·English」切换行改为**纯文字指路**——渠道页不解析相对链接,可点切换在此环境是死 UI,不装能点。
- 两文口径同步句改「以代码与夹具现值为准」,与 C-46 一致。

### 0.2.1 — 2026-09-28（lead·渠道一致性修正,Owner 点名）

- 渠道 listing description 由英文主改为**中文主**(≤300、三段:拿到什么/机器挡什么/适合与不适合),英文触发词移至尾部保留,零丢失。
- 两份 README 头部「v0.2.0 公开试验版」活版本+状态尾句删除(指针化纪律,对齐族规)。
- 新建本 CHANGELOG(族规补齐:此前为九件中唯一缺 CHANGELOG 的包)。
- 语言切换行经查与姊妹件同制(链接目标四件俱在),保留不动。

### 0.2.0 — 2026-09-28（Owner:v0.2 evidence briefs 与零密钥 demo）

- 上游历史(仓内 PR#1-4):v0.1.1 audited public knowledge workflow → v0.2 evidence briefs;Windows 首跑兼容三修(.gitattributes LF、symlink 测试平台跳过、claim_kind 默认 reported),47 项测试。

### 0.1.1 — 2026-09-27（Owner:audited public knowledge workflow 首发）

- 初始上架前审计版,细节以 git log(PR#1)为准。
