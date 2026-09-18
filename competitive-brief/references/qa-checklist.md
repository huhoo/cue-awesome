# QA 门禁检查清单

## 阻塞项（必须全部通过才能交付）

- [ ] 每条判断性结论有 EvidenceCard（fact / inference 都要）
- [ ] `evidence/index.csv` 覆盖度 ≥ 70%
- [ ] 零 `待验证` 行进入正文
- [ ] 市场信号日期新鲜（>12 个月标 WARN）
- [ ] 所有引用 URL 解析到所宣称的标题/日期
- [ ] fact/inference 标注无遗漏
- [ ] 绝对化用语有来源
- [ ] 三件套齐全（html + pdf + md）
- [ ] `pending.md` 无 ⟨待确认⟩ 残留
- [ ] 数字有来源与口径

## 建议项

- [ ] 举证覆盖率不足 70% 的行有差分析
- [ ] 定价归一化口径差异说明充分
- [ ] 信号条目充足（≥3 条/类别）
- [ ] fact/inference/opinion 比例合理
- [ ] 语义图已用 `gen_diagram.py` 绘制（如需要）
- [ ] 交付清单写进 `review.md` 末尾
