#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gate_paired.py — M276「成对注入」守护样的包内自测入口。

它与同包 `scripts/fixtures/witness.md`（**被检件**）之间是真读真判的关系：
  · 被检件在场且含必查标记 → 退 0（ALL GREEN）
  · 被检件缺那行标记      → 退 1（＝对必查项静默放行／产物少一枚这一类坏输出）
  · 被检件根本不在场      → 退 2（打包剔件、路径写错一类）

**本文件在三态里一字不动**——仓级闸 `check_shipment.py` 亦然。变的只有被检件：
注入落在被检件侧，才叫「包内自测真的看见了坏输出」；改考官不算。
"""
import pathlib
import sys

MARK = "必查项：已核"


def main(argv) -> int:
    if "--selftest" not in argv:
        print("usage: --selftest")
        return 0
    wit = pathlib.Path(__file__).resolve().parent / "fixtures" / "witness.md"
    if not wit.is_file():
        print(f"selftest: FAIL（被检件不在场：{wit.name}）")
        return 2
    text = wit.read_text(encoding="utf-8", errors="replace")
    if MARK not in text:
        print(f"selftest: FAIL（被检件缺必查标记「{MARK}」＝静默放行或产物少一枚）")
        return 1
    print(f"selftest: ALL GREEN（被检件 {wit.name} 含「{MARK}」）")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
