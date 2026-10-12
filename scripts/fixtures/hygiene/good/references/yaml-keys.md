# 合规守护样·YAML 保留键名（反例：这类行曾被 H-PATH 词面误拦）

CI 触发器写作：

```yaml
on:
  push:
    branches: [main]
  pull_request:
  workflow_dispatch:
```

`workflow_dispatch` 是 GitHub Actions 的保留键名，前置是下划线，**不是**工作区路径指路；
真指路一律带目录斜杠形（见同目录族的违例样），词面窄化不得把那一形一起放掉。
