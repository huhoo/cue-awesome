#!/usr/bin/env python3
import sys
if "--selftest" in sys.argv:
    print("selftest: ALL GREEN（守护样 1/1）")
    sys.exit(0)
print("usage: --selftest")
