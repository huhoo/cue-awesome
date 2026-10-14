# demopkg

本样只钉「unittest 形入口必须被真跑」这一条判据。

```bash
python3 -m unittest discover -s scripts -p "test_*.py"   # 两枚入口，逐枚都要真跑
```
