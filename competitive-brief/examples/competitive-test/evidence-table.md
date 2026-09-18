# Evidence Table: Cursor 替代方案对比

决策问题：5人团队是否从 Cursor 切换到更开放的 coding agent 方案
来源日期：2026-09-18
工具状态：omni-reader 分辨率不限定价页（claude.com/pricing，cursor.com/pricing），已标注；其余条目基于公开文档和已有知识。

| 竞品 | 维度 | 主张 | 级别 | 来源 | 置信度 | 备注 |
|---|---|---|---|---|---|---|
| Cursor | 定价 | Pro $20/月/人，5人$100 | fact | cursor.com/pricing | 高 | 未用 omni 验证（billing 不可用） |
| Claude Code | 定价 | 含在 Max 订阅 $180/月/人 | inference | 公开文档及已有知识 | 中 | 同上 |
| Claude Code | 上下文 | 200K token + 持久内存 | fact | docs.anthropic.com | 高 | |
| Cursor | 上下文 | ~15K token 窗口 | inference | 用户社区及已有知识 | 中 | 未找到官方明确数字 |
| Cursor | 模型开放度 | 仅 Claude + GPT-4o | fact | cursor.com/features | 高 | |
| Claude Code | 模型开放度 | 全系 Claude | fact | docs.anthropic.com | 高 | |
| OpenCode | 定价 | 开源免费 | fact | github repo | 高 | 需自付模型 API 费 |
| OpenCode | 开源 | ✅ | fact | github repo | 高 | |
| Codex CLI | 定价 | 免费 CLI + API 按量 | fact | OpenAI 文档 | 高 | |
| Codex CLI | 成熟度 | 产品迭代节奏不稳定 | opinion | — | 低 | 基于公开观察，无直接来源 |
| Cursor | 插件生态 | 封闭，不支持 MCP | fact | cursor.com/docs | 高 | |
| Claude Code | 插件生态 | 支持 MCP 协议 | fact | docs.anthropic.com | 高 | |
