# long-doc-translation

**[中文](README.md) · [English](README.en.md)**

把一部几百页的外文专著，译成**可交付、可核查、术语统一**的中文全稿。

## 一句话

不是「翻译一段文字」，而是让 100+ 个翻译单元在体例与用词上保持一致，合并后不出现重复、断裂、未译残留。

## 流水线

解析 → 清洗切片 → 建体例与术语表 → 并行分批翻译 → 多维质检 → 合并交付带目录的阅读版

## 适用

- 300 页以上的学术专著、古籍、档案、译著（德 / 英 / 法 / 日等）
- 需要术语全书统一、脚注保留、存疑可追溯

## 依赖

- `python3` + `markdown` + `pypinyin`（核心脚本完全离线运行）
- omni-reader（可选：阶段一「解析」把 PDF / 图片转成文本）

## 脚本（`scripts/`）

`init_project.py` · `dedup_boundary.py` · `overlap_check.py` · `qa_check.py` · `merge_build.py` · `build_reader.py` · `_common.py`

## 规范（`references/`）

| 文件 | 内容 |
|---|---|
| `pitfalls.md` | 五大陷阱：发现 / 修复 / 预防，含**脚本静默失效模式** |
| `qa-checklist.md` | 七项质检标准 + 脚本阈值 + 修复动作 + 交付基线 |
| `reader-build.md` | 增强阅读版 HTML 的工程决策与依赖降级 |
| `parallel-translation.md` | 并行翻译分片原则、子代理提示词三要素、验收 |

## 上手

```bash
python scripts/init_project.py --help    # 每个脚本都支持 --help
```

完整流程、硬规则与实测参数见 [`SKILL.md`](SKILL.md)；版本历史见 [`CHANGELOG.md`](CHANGELOG.md)。当前版本 **1.3.0**。
