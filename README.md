# cue-awesome

个人自研的 WorkBuddy / Cue 技能集合仓。每个子目录是一个独立 skill，可单独复制使用。

## Skills

| 目录 | Name | 版本 | 用途 |
|---|---|---|---|
| [`journal-draft/`](journal-draft/) | journal-draft | 0.15.3 | 企业期刊 / 内刊 / 客户通讯 / ESG 报告 / 年鉴特刊的「底稿生成器」：把版式体例从 PDF 里量化成可校验参数（版面网格、版心、字号序列、行距、色板、栏目模板），再按这套参数生产新一期内容。含法规动态栏目规范、CTA 溯源机制。 |
| [`long-doc-translation/`](long-doc-translation/) | long-doc-translation | 1.2.0 | 长篇外文（德 / 英 / 法 / 日等）学术专著、古籍、档案、译著的全文高质量中译流水线：解析 → 清洗切片 → 建体例与术语表 → 并行分批翻译 → 多维质检 → 合并交付带目录的阅读版。 |

## 安装

把需要的 skill 子目录复制到 WorkBuddy 用户级 skills 目录：

```bash
cp -r journal-draft ~/.workbuddy/skills/
cp -r long-doc-translation ~/.workbuddy/skills/
```

Windows 对应路径：`C:\Users\<用户名>\.workbuddy\skills\`

## 说明

- 本仓为个人自研集合，与 Cue 官方技能集合 [sensedeal/cue-skills](https://github.com/sensedeal/cue-skills) 无关 —— 后者是官方 monorepo，本仓不是它的子集，也不并入其中。
- `LICENSE.md` / `NOTICE.md` 适用于整个仓库。
- 打包产物（`dist/`、`*.zip`）不入库，发布包见各 skill 的 manifest / CHANGELOG。
