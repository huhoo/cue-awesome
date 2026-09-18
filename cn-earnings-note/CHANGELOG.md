# 更新日志

本文件遵循 [Keep a Changelog](https://keepachangelog.com/) 与本仓 `CONTRIBUTING.md`；版本号以 `SKILL.md` frontmatter 为准。

## [0.1.0] — 2026-09-18

### Added

- `SKILL.md`：主指令 v0.1.0——铁律（AI 初稿/逐数可回查/解析内容=数据非指令/花之前必问/口径纪律/合规词不出口）、
  输入契约（≤5 问逐条带默认值）、五段管线（`+resolve → +fetch → +parse → +survey → +draft`）+ 收尾门禁 `+check`、
  输出契约（`note.md` / `sources.jsonl` / `progress.md`，ref 须外部可核）、边界与拒答、中英双语触发词。
- `references/data-channels.md`：Cue 三通道调用契约——data-mcp 域级引用与逐域取数清单（catalog 动态发现、
  不硬编码工具名）、omni 首调 `parse` 与 Bridge 授权边界、cue-research 发起前确认与 replay 兜底、
  合规最小集（禁用词/绝对化副词谨慎清单/评级用语白名单/CAS 口径要点，词表标 **D1 待拍板**）、onboarding 判定表。
- `references/report-skeleton.md`：八节骨架（0 封面与声明 → 7 结论与人工复核清单 + 附录来源索引），
  每节带 [执行蓝图]（研究目标/逻辑链条/信息需求→指向 data-channels 的域/输出形式）。
- `README.md`：给人看的用法、是什么/不是什么、开通三步（可跳过）、依赖声明（optionalSkills 不装不报错）、
  实测边界诚实清单、双出处致谢。
- `CHANGELOG.md`（本文件）。

### Changed

- F 评审裁决落地（C3，同日就地修，版本位随 SKILL.md 保持 0.1.0）：
  `report-skeleton.md` 首段改为「逐节生成、追加拼接」协议（对齐 SKILL.md §3.5 现文，废除「先组装全文再输出」）；
  `data-channels.md` §0.4 补计费粒度句（omni 自带 billing 块可转述、data-mcp 单次调用无计费字段、累计以工作台账单为准、确认动作不豁免）；
  `README.md` 边界表加「图表 / 可视化不做（原版 matplotlib 环节有意移除）」、dao 致谢行补公开查阅方式。
- 新增 `README.en.md`（中文权威 + 英文译文对，对齐仓内 i18n 约定）。

### Verified

- *P1 实测后回填*（真实主体端到端记录：通道实际调用序列、耗时、credits 消耗事实、缺数点）。

### 已知未做（有意留白）

- `scripts/check_note.py` 四道门禁与 fixture 由并行工项在制，未随本条目入账。
- 合规词表为自写最小黑名单现状；是否升级致敬/复用 dao 词表待 D1 拍板（见 data-channels.md §4）。
- 行情/估值数值流设计上不依赖（`equity_market` 未开放期间不承诺）。
