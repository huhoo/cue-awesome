# long-doc-translation

**本文件为中文主面；英文版是同目录下的 `README.en.md`（仓库内查阅用——渠道页不解析相对链接，这里不做可点切换）。**

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
python scripts/init_project.py --help        # 六个脚本里只有这一个支持 --help
python scripts/qa_check.py                  # 其余脚本不带参数即打印用法（缺参数按错误退 1，不是崩）
python scripts/build_reader.py               # 这两个有内置默认路径，路径不存在时**报错退出并给检查提示**
# 实测：目录不存在一律退 1 并提示查路径 / 先跑 init_project，不会「打印 0 个片段再给一排全绿」。
```

完整流程、硬规则与实测参数见 [`SKILL.md`](SKILL.md)；版本历史与当前版本见 [`CHANGELOG.md`](CHANGELOG.md) 与 `SKILL.md` 头部——**本文件不写版本号**（写过一次就永远在说谎）。

三道质检脚本的判定常数（含"按项目改这里"的 CONFIG 区）一条命令原地打出，任意目录整行粘贴可跑：

```bash
grep -n "CONFIG\|^[A-Z_]\{2,\} *=" ~/.workbuddy/skills/long-doc-translation/scripts/qa_check.py ~/.workbuddy/skills/long-doc-translation/scripts/overlap_check.py ~/.workbuddy/skills/long-doc-translation/scripts/dedup_boundary.py
```

闸分两性质：**包内固定闸**（缺目录即报错退出、片段数对账、TOC 层级、页码连续算法）与**项目配置域**（页边码正则、OCR 错字表、体例三节命名、跳过范围、分组模式与各阈值默认值）。README 与 `SKILL.md`、`references/qa-checklist.md` 里的数字都是镜像与常见例，**不作穷尽断言**——以脚本现值为准。
