## [Unreleased]

### 0.3.2 — 2026-09-25（listing 二修：按 M121 第一读者对照,文案逐句退回正文有依据的宣称）

- 首轮重写复述过关但 8/8 存在无依据或夸大机器承诺处,本条为其修正:机器面话术与正文/门禁脚本逐句对齐,正文没有的（如固定判断位、逐数必拦、固定七维、TTM）一律从对外字段删除或改写为正文实际机制。

### 0.3.1 — 2026-09-25（listing 文案重写为用户视角，C-36 三闸）

- summary 收紧为一句话；description 改「拿到什么 / 机器挡什么 / 适合与不适合」三段式；契约与流程细节退回正文与包内文档，对外字段不再当合规容器。功能、门禁与数据语义相对上一版零变化。

# Changelog

## 0.3.0 (2026-09-18)

- **实跑验证**：完整跑通「5人团队从 Cursor 迁移」场景，omni-reader 解析 cursor.com/pricing、claude.com/pricing、GitHub README 共 4 个竞品
- **示例更新**：examples/competitive-test/ 证据表（23 行，87% fact）和简报按最新实跑结果更新
- **SKILL.md**：证据表样本行升级为 omni-reader 验证的真实数据

## 0.2.0 (2026-09-17)

- **证据表优先模型**（evidence-table-first）：填不满的维度不写进简报
- 新增 `references/evidence-standards.md`

## 0.1.1 (2026-09-17)

- 精简结构：移除 journal-draft 机械复制文件
- 四层证据模型（fact/inference/opinion + 置信度）

## 0.1.0 (2026-09-17)

- 初版：竞品分析简报流水线
- 七文件结构（journal-draft 风格）
