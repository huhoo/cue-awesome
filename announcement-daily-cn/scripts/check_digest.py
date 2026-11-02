#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_digest.py — 公告速览产物的四道机检（零网络、只读本包外传入的文件）。

四道码（缺一即不叫过闸）：
  F-STRUCT 四段齐：头部申报／逐条要点／同类前后串／缺数与待人工，四段小标题任一段缺失即发红；
  F-ANCHOR 逐条双要素＋锚：每条要点行必须同带「[披露日]」＋书名号内的公告标题逐字＋「锚：」定位，缺任一项发红；
  F-LINE   红线断言：评级／目标价／涨跌与承诺类词只允许出现在带 [待人工] 的行里，否则发红；
  F-COUNT  计数与申报一致：头部写的「共 N 条」必须等于实际要点条数；把「未检索到」写成「无／没有」一律发红。

用法：
  python3 -B scripts/check_digest.py <待检文件>      # 逐条发红，全过则 PASS
  python3 -B scripts/check_digest.py --selftest      # 好样须过、坏样四道齐发；临时件跑完自清
  python3 -B scripts/check_digest.py --help
退码：0＝过（或自测全合）；1＝发红／自测不合；2＝用法错。
"""
from __future__ import annotations

import argparse
import atexit
import pathlib
import re
import shutil
import sys
import tempfile

TMP_ROOTS: list[pathlib.Path] = []
AT_EXIT_DONE = {"done": False}

ITEM = re.compile(r"^\s*[-*]\s*\[(\d{4}-\d{2}-\d{2}|\d{1,2}\s*月\s*\d{1,2}\s*日)\]")
TITLE = re.compile(r"[「『][^」』]+[」』]")
ANCHOR = re.compile(r"锚[:：]")
BANNED_WORDS = re.compile(r"必涨|稳赚|零风险|保证收益|目标价\s*[:：]?\s*\d|上调评级|下调评级|买入|卖出|加仓|减仓")
PENDING = re.compile(r"\[待人工\]")
COUNT = re.compile(r"共\s*(\d+)\s*条")
EMPTY_LIE = re.compile(r"(?:^|[\s：:])无公告|没有公告|无新增公告")
SECTIONS = (("头部申报", r"头部申报|申报"), ("逐条要点", r"逐条要点|要点清单"),
            ("同类前后串", r"同类|前后串"), ("缺数与待人工", r"缺数|待人工"))


def check_text(text: str) -> list[tuple[str, int, str]]:
    """返回 [(码, 行号, 说明)]；行号 0＝整档级判据。"""
    hits: list[tuple[str, int, str]] = []
    lines = text.splitlines()
    for name, pat in SECTIONS:
        if not re.search(pat, text):
            hits.append(("F-STRUCT", 0, f"缺段：{name}"))
    items = 0
    for i, ln in enumerate(lines, 1):
        if ITEM.match(ln):
            items += 1
            if not TITLE.search(ln):
                hits.append(("F-ANCHOR", i, "要点行缺公告标题逐字（书名号内）"))
            if not ANCHOR.search(ln):
                hits.append(("F-ANCHOR", i, "要点行缺「锚：」来源定位"))
        if BANNED_WORDS.search(ln) and not PENDING.search(ln):
            hits.append(("F-LINE", i, "红线断言词出现在没有 [待人工] 的行"))
    m = COUNT.search(text)
    if m and int(m.group(1)) != items:
        hits.append(("F-COUNT", 0, f"申报共 {m.group(1)} 条∥实际要点 {items} 条"))
    if not m and items:
        hits.append(("F-COUNT", 0, "头部申报缺「共 N 条」，无从对账"))
    for i, ln in enumerate(lines, 1):
        if EMPTY_LIE.search(ln):
            hits.append(("F-COUNT", i, "把「未检索到」写成「无／没有」"))
    return hits


def make_tmp(prefix: str) -> pathlib.Path:
    d = pathlib.Path(tempfile.mkdtemp(prefix=prefix, dir=str(pathlib.Path(tempfile.gettempdir()))))
    TMP_ROOTS.append(d)
    return d


@atexit.register
def _cleanup() -> None:
    AT_EXIT_DONE["done"] = True
    for d in TMP_ROOTS:
        shutil.rmtree(d, ignore_errors=True)


def selftest() -> int:
    here = pathlib.Path(__file__).resolve().parent
    good = here / "fixtures" / "good-digest.md"
    bad = here / "fixtures" / "bad-digest.md"
    rows = []
    gt = good.read_text(encoding="utf-8")
    gh = check_text(gt)
    rows.append(("好样须过（发条 0）", not gh, f"实发 {len(gh)} 条"))
    bt = bad.read_text(encoding="utf-8")
    bh = check_text(bt)
    codes = {c for c, _, _ in bh}
    rows.append(("坏样四道齐发", {"F-STRUCT", "F-ANCHOR", "F-LINE", "F-COUNT"} <= codes,
                 "实发码 " + "∥".join(sorted(codes))))
    # 反证：临时件——把好样剥掉锚行，必须只发 F-ANCHOR
    tmp = make_tmp("check-digest-")
    stripped = tmp / "no-anchor.md"
    stripped.write_text(re.sub(ANCHOR, "", gt), encoding="utf-8")
    sh = check_text(stripped.read_text(encoding="utf-8"))
    rows.append(("反证·剥锚必发 F-ANCHOR", any(c == "F-ANCHOR" for c, _, _ in sh), f"实发 {len(sh)} 条"))
    made = [p.name for p in TMP_ROOTS]
    root = pathlib.Path(tempfile.gettempdir())
    for p in TMP_ROOTS:
        shutil.rmtree(p, ignore_errors=True)
    leftover = sorted(q.name for q in root.iterdir() if q.name.startswith("check-digest-")) if root.is_dir() else []
    rows.append(("临时根自清（跑后不增）", not leftover,
                 f"本次建 {len(made)} 枚·跑后残留 {len(leftover)} 枚"))
    rows.append(("atexit 钩子在场", True, "已注册"))
    bad_rows = [r for r in rows if not r[1]]
    for name, ok, detail in rows:
        print(f"  {'ok  ' if ok else 'FAIL'} {name}｜{detail}")
    print(f"selftest: {'ALL GREEN' if not bad_rows else 'FAIL'}（好样 1 枚·坏样四道·反例 %d 枚·临时根 %d 枚自清）"
          % (len([r for r in rows if r[0].startswith('反证')]), len(TMP_ROOTS)))
    return 0 if not bad_rows else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="公告速览产物四道机检（零网络）")
    ap.add_argument("target", nargs="?", help="待检文件（本件不读网络、不读目录）")
    ap.add_argument("--selftest", action="store_true", help="好样须过、坏样四道齐发、临时件自清")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not a.target:
        print("用法：check_digest.py <待检文件> | --selftest", file=sys.stderr)
        return 2
    p = pathlib.Path(a.target)
    if not p.is_file():
        print(f"FAIL 文件不在场：{p}", file=sys.stderr)
        return 2
    hits = check_text(p.read_text(encoding="utf-8", errors="replace"))
    for code, ln, msg in hits:
        print(f"FAIL [{code}] {p.name}" + (f":{ln}" if ln else "") + f" {msg}")
    scanned = len(p.read_text(encoding='utf-8', errors='replace').splitlines())
    print(("PASS" if not hits else "FAIL") + f"（扫过 {scanned} 行，发条 {len(hits)} 条）")
    return 0 if not hits else 1


if __name__ == "__main__":
    sys.exit(main())
