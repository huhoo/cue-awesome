# Changelog

本文件遵循 keep-a-changelog;版本权威=各 SKILL.md frontmatter 现值。

### 0.2.4 — 2026-10-04（docs·M168 第二批三件套 + 专项「国内可达取证路径」：FAQ 与反模式 / 出错了怎么办 / 触发示例，中英双脸同步；新增节接在 §交付与验证 之后、§试用反馈 之前）

- 缘起：渠道质量测评本件 antiPatternFaq=3.8（全档最低项之一：该禁的散在 update-policy 与 knowledge-contract，无反模式专节）、errorHandling=4.3（技术性强、无面向使用者的修正引导）、trigger=4.8（调用面散在段落里）、**trust.domestic=4.3**（示例与文档链接指向境外站点，网络受限时取证面变窄；另指出「脚本输出与错误提示为英文」——本段只补路径与说明，**不改脚本出口语言**，那属机器面，另票）。
- 「出错了怎么办」按 `ontology.py` **现跑实际出口**写：成功一行 JSON `{"status":"valid", "counts":{...}, "semantic_verification":"not_established_by_scripts"}` 退 0；失败 `{"status":"invalid","error":"…"}` 退 2（stderr），实测两类真实原因 `knowledge integrity mismatch` 与 `source hash mismatch: <来源 ID>`；契约类消息（invalid ID / duplicate ID / duplicate JSON key / invalid value for）取自脚本源码字面。**不新造错误码**，也不把「脚本不证语义」这句省掉——出口里那句 `not_established_by_scripts` 就是本件的精度边界。
- 专项口径：**demo 无需 API key、不联网**为既有事实；真实取证补三条现成路径（用户给文件优先 / 境外取不到就导出成文件而不是绕 / 检索补来源只在授权研究范围内），并保留两条既有铁律：URL 形状不能证明公开可访问、取不到就标「未取得」不推断不静默覆盖。不承诺未开放数据域、不承诺特定站点可达。
- 版本位：README 与 README.en 在渠道包字节面内，占 patch 位 0.2.3 → 0.2.4（SKILL.md 与 SKILL.en.md 的 frontmatter `version` 同步，双语一致性由机检查）；脚本、references、assets 零触碰。
### 0.2.3（文案面·五处窄修）— 2026-09-28 机检范围两分 / 触发尾块补旧形 / 权威向归位 / 计数指针化

- 机检范围收窄为如实：listing 与摘要此前把「打包、更新、查询、导出」与「完整性」并列写成由工具机检——工具只**机检输入包完整性**，其余四件事是工具**执行**的动作，导出路径对消费端返回未验证，外部 OKF 兼容性本件不验证。四词并列句改两分句，中英两份 frontmatter 同文同改。**同时删掉摘要与描述里写死的自测条数**：同一个数在包内出现多处且彼此不一致，改为一句话指现跑命令（活计数只留能被跑出来的那一处）。
- 英文触发尾块补回一个旧字段里存在、迁移时掉出来的英文形状（供应商/产品变化类）；**本包早前一条 CHANGELOG 曾把那次迁移写成"英文触发词零丢失"，那句不实**——当时中文语义确实仍在，但英文检索面少了一形；按「解释性句子只写类别名」的规矩，此处不复述那六个字的原话，只定性：**该声明当时的判定口径把"语义在"当成了"检索词在"，是两件事**。
- 权威向归位：两处称英文译件为权威 Agent 指令，是主从倒正之前的旧句，现改为「Agent 指令以中文主文件为准、英文件为同步译文」；另把我上一轮写的一句过头话（把夹具与代码并列为权威）改回边界内的形状：**判定=脚本现值，夹具只是已跑用例的例证、不保证穷尽**。
- 公开验证记录里那条测试计数改指针形：记录只说"当日全过"，数与结果以现跑命令为准。
- 根 README 两处（同批）：本件那一行的活版本号换成与其余八件同法的 frontmatter 指针；「本件不在旧 ZIP 里」那句按发布页现值改为现状句（发布页实有本件资产），不再与同段九件指路自相矛盾。**「版本权威=frontmatter」这条声明从本条起才是真的**：根行、文档、渠道字段三处都不再各存一份数。
- summary / description 均在字数闸内（75／297）。**本条与同日那条机器面条目同占 0.2.3 一个版本位**（工具版本戳同号化属机器面，两事各写一条、不互抄），贴本条时机器面已在盘，文案面未再动 scripts。
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
