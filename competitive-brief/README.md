# competitive-brief — 竞品简报生成器

**把散落在网页/PDF/录音/视频里的竞品素材，变成可溯源、可对比、可更新的决策简报。**

## 一句话

不是代写分析，是把素材结构化 + 交叉验证 + 按框架出稿。

## 快速开始

```bash
# 安装
npx skills add huhoo/cue-awesome --skill competitive-brief

# 启动
+intake "竞品A官网 竞品B定价页 竞品C年报.pdf"
```

## 流程

```
素材 → omni-reader -> +intake -> +brief -> +map -> +gather(cue) -> +draft -> +check
```

## 三件套交付

- `brief.html` — 阅读版
- `brief.pdf` — 分享版
- `brief.md` — 编辑版

## 依赖

- **推荐安装**：`cue-omni-reader`（素材摄入）、`cue-research`（深研取证）
- **Python**：pymupdf、jinja2、pyyaml

## License

MIT
