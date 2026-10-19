# 示例包 SKILL（发布物自跑闸的「成对注入」守护样）

自带守护样：`python3 scripts/gate_paired.py --selftest`，被检件在 `scripts/fixtures/witness.md`。
指路：`references/spec.md`、`assets/模板.md`。

本样与 `good/` 的唯一区别：**入口真的读被检件**。这正是 M276 那条链需要的形状——合规态退 0；只把被检件弄坏（考官与本闸一字不动），入口必须退非 0，仓级闸必须随之由 PASS 转 `S-SELFTEST`。
