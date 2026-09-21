# 更新日志

本文件遵循 [Keep a Changelog](https://keepachangelog.com/) 与本仓 `CONTRIBUTING.md`；版本号以 `SKILL.md` frontmatter 为准。

## [0.1.1] — 2026-09-21

### Added/Fixed
- M47 check_sector 四道机检+48 断言对账;对抗审 LGTM(判词模板同 §v4-C);README 状态位改「审结待实跑」。

## [0.1.0] — 2026-09-21

初始版本（套件管线第三格·行业镜像；契约=spec-sector-overview-0.1.0，铁律语法与通道契约承姊妹件）。

### Added

- `SKILL.md`：命门纪律「判断词-锚同行」入铁律 2（`升|降|回暖|承压|走弱|拐点|高景气|低谷` ⇒ 同句 `S<n>` 或态二逐字句「无可比序列，不做景气判定」）；评级零容忍**无豁免区**（比姊妹件更严的行业层表述）；维度动态生成（research ≤1 先出 2–4 个本行业维度，不背框架库）；三 basis 标签制/缺数禁补/预期均值默认不取；输入 ≤3 问、五段管线+四道机检、双语触发词与套件分流「不用于」句。
- `references/section-skeleton.md`：六节+每节 [执行蓝图]（研究目标/逻辑链条/信息需求→域/输出形式），节名为本件自定（画像是结论先行制，非任何既有栏目改名）。
- `references/policy-timeline.md`：时间线行规格——生效日行首键、发布≠生效分列、要点短引 ≤40 字禁转述加成判断、归因句另挂锚；statute 三件齐锚规格**引用** catalyst spec §v3-A3 不复制（双事实源禁令）。
- `README.md`/`README.en.md`：中文权威+英文译文对；开场用引语反驳式（与姊妹件三开场的句式差异见 §5-7 自查表）。
- `CHANGELOG.md`（本文件）。

### Verified

- **出门条件未闭（设计值声明）**：端到端真实跑未发生（六节覆盖度/耗时/维度质量为设计值）；机检 `check_sector.py` 与 fixtures 归并行工项在制；坏样规格单按新制度**先由对抗审出**（写手不自造好人心证），出门=三审制（fixtures 含对方攻击样全绿真 exit + 6.1 LGTM「构造不出下一枚」）；P2 上架与套件同闸冻结，push 单独候 Owner。
