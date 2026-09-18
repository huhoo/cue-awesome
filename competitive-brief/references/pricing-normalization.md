# 定价归一化规则

## 为什么要归一化

不同竞品的定价模型差异很大（按 seat、按 usage、按 tier、自建部署），直接比数字没有意义。归一化是把各家的定价翻译成同一套计量单位后再对比。

## 归一化步骤

1. **确定基准单位**：人均月费（per-seat/month），这是最普遍的 SaaS 计价单位。
2. **转换各竞品定价到基准单位**：
   - 年付套餐 → 折算到月均（年付÷12）
   - Usage-based → 取典型用量（官网常见案例的用量数据做估算）
   - 自建部署 → 拆成三年 TCO（许可+实施+维护）后折算 per-seat/month
3. **标注归一化假设**：每一步折算都写清楚假设条件。

## 常见陷阱

| 陷阱 | 例子 | 处理 |
|---|---|---|
| 只看标价不看折扣 | 多数 SaaS 年付打折 15-20%，标价是月付价 | 按年付折算，标注「基于公开年付标价」 |
| 免费额度计入平均 | 某竞品前 10 用户免费，算均摊时把免费部分算进收入 | 分档：free / paid starter / paid scale |
| 隐藏成本遗漏 | 实施费 / 年约违约金 / 超额费 / API 调用费 | 从用户评价与二手来源补充，标注 `inference` |
| 计价单位不同 | 按 developer 价 vs 按 workspace 价 vs 按 org 价 | 定义 `per-developer` 为基准，其他按典型团队规模折算 |

## 定价表格式

输出到 `pricing.json`：

```json
{
  "base_unit": "per-seat/month",
  "currency": "USD",
  "source_date": "2026-09-18",
  "competitors": [
    {
      "name": "CompetitorA",
      "tiers": [
        {"name": "Free", "price": 0, "seats": "up to 3", "note": ""},
        {"name": "Pro", "price": 12, "seats": "per seat", "note": "年付$120/seat/年"},
        {"name": "Enterprise", "price": null, "seats": "custom", "note": "需联系销售"}
      ],
      "hidden_costs": [],
      "normalization_note": "Pro tier 按年付÷12折算"
    }
  ]
}
```
