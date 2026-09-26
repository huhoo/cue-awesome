# competitive-brief

围绕一个决策问题做竞品分析，出带证据链的简报。

```
+brief "我们要不要进入北美中小律所的合规工具市场"
  → 先定决策、看谁、到什么程度
  → omni-reader 收素材，cue-research 深研交叉验证
  → 每一条 claim 标 fact/inference/opinion
  → 交付：结论 + 追溯 + 自己还需要确认什么
```

## 一句话

核心不是流程，是**证据表（evidence table）**——所有结论性主张在进简报之前，先写进证据表，填不满的维度不写进简报。

## 详细说明

见 [`SKILL.md`](SKILL.md)，包含证据表定义、约束、简报渲染规则。

## 实跑示例

[`examples/competitive-test/`](examples/competitive-test/) — 5人团队从 Cursor 迁移到替代方案的竞品简报：
- [证据表](examples/competitive-test/evidence-table.md)（23 行，87% fact）
- [简报](examples/competitive-test/brief.md)

数据来源经 omni-reader 解析 cursor.com/pricing、claude.com/pricing、GitHub README 验证。

## 依赖（推荐安装）

- `cue-omni-reader`：解析网页/PDF/录音/视频，提取原文填入证据表
- `cue-research`：交叉验证、深度研究

不计费。不装也能跑，但缺能力。

## 版本

版本以本包 `SKILL.md` frontmatter 为唯一权威，历史见 [`CHANGELOG.md`](CHANGELOG.md)。
