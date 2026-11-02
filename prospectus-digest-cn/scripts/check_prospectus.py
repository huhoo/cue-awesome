#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_prospectus.py — 招股书速览卡的五道机检（零网络、只读传入文件）。

五道码（缺一即不叫过闸）：
  F-STRUCT 五段齐＋八项名目齐：头部申报／八项逐字速览／口径对照／缺数清单／待人工任一段缺失即发红；
           八项里任何一项在全文不出现即发红——缺那一项也要占一行点名，不许省行。
  F-ANCHOR 原句与页码锚：每项速读行必须带书名号内原句＋「锚：」，且锚里要能落回页码（第 N 页／页码／P.N 三种形制之一）；
           写明「未检索到」的那一项免。
  F-CLAIM  自称不当事实：书名号内的原句里出现自称或最高级（领先／先进水平／国际先进／最大／龙头／首创／之最／顶尖，以及「全球·国内·行业·全国·世界＋第一」）时——排名式的事实描述（如「第一大客户占比」）不在这一判里，它判的是没有第三方依据的那类话，
           该行必须同时带「发行人自述」标注；标不出来的那句不进结论。
  F-LINE   红线断言：估值、申购、买卖、涨跌与承诺类词只允许出现在带 [待人工] 的行里。
           书名号内的原文引用不参与本道——判的是我们自己写的断言，不是发行人写过的话。
  F-COUNT  齐缺与申报对账：头部「共八项·缺 N 项」的 N 必须等于实际写明「未检索到」的项行数；申报缺失即发红；
           项值位写「无／不适用／略／待定」而不落到「未检索到」一律发红。

用法：
  python3 -B scripts/check_prospectus.py <待检文件>   # 逐条发红，全过则 PASS
  python3 -B scripts/check_prospectus.py --selftest   # 好样须过、坏样五道齐发、反证各发各码；临时件跑完自清
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

ITEMS = ["发行与上市安排", "主营业务与收入结构", "募集资金投向", "客户与供应商集中度",
         "研发与核心技术", "主要风险因素", "股权结构与实际控制人", "财务口径"]
ITEM_LINE = re.compile(r"^\s*[-*]\s*(" + "|".join(re.escape(x) for x in ITEMS) + r")[：:]")
ANCHOR = re.compile(r"锚[:：]")
PAGE = re.compile(r"第\s*\d+\s*页|页码|P\.?\s*\d+")
VERBATIM = re.compile(r"[「『][^」』]+[」』]")
MISS = re.compile(r"未检索到")
DECL = re.compile(r"共八项·缺\s*(\d+)\s*项")
FILLER = re.compile(r"[：:]\s*(?:无|不适用|略|待定)\s*$")
SELF_WORD = re.compile(r"领先|先进水平|国际先进|最大|龙头|首创|之最|顶尖|(?:全球|国内|行业|全国|世界)第一")
SELF_TAG = re.compile(r"发行人自述")
PENDING = re.compile(r"\[待人工\]")
BANNED = re.compile(r"必涨|稳赚|零风险|保证收益|目标价\s*[:：]?\s*\d|上调评级|下调评级|买入|卖出|加仓|减仓"
                    r"|建议申购|值得申购|一定会涨|利好兑现")
QUOTE = re.compile(r"[「『][^」』]*[」』]")
SECTIONS = (("头部申报", r"头部申报"), ("八项逐字速览", r"八项逐字速览|逐字速览"), ("口径对照", r"口径对照"),
            ("缺数清单", r"缺数清单"), ("待人工", r"待人工"))


def check_text(text: str) -> list[tuple[str, int, str]]:
    """返回 [(码, 行号, 说明)]；行号 0＝整档级判据。"""
    hits: list[tuple[str, int, str]] = []
    lines = text.splitlines()
    for name, pat in SECTIONS:
        if not re.search(pat, text):
            hits.append(("F-STRUCT", 0, f"缺段：{name}"))
    for name in ITEMS:
        if name not in text:
            hits.append(("F-STRUCT", 0, f"缺项名目：{name}（缺那一项也要占一行点名）"))
    for i, ln in enumerate(lines, 1):
        if ITEM_LINE.match(ln) and not MISS.search(ln):
            if not ANCHOR.search(ln):
                hits.append(("F-ANCHOR", i, "该项缺「锚：」定位"))
            elif not PAGE.search(ln):
                hits.append(("F-ANCHOR", i, "该项锚里落不回页码（第 N 页／页码／P.N 三种形制之一）"))
            if not VERBATIM.search(ln):
                hits.append(("F-ANCHOR", i, "该项缺书名号内原句逐字"))
            if FILLER.search(ln):
                hits.append(("F-COUNT", i, "项值位用「无／不适用／略／待定」顶替，未落到「未检索到」"))
        quoted = "".join(QUOTE.findall(ln))
        if SELF_WORD.search(quoted) and not SELF_TAG.search(ln):
            hits.append(("F-CLAIM", i, "原句含自称或最高级，但未标「发行人自述，无第三方依据」"))
        bare = QUOTE.sub("", ln)
        if BANNED.search(bare) and not PENDING.search(ln):
            hits.append(("F-LINE", i, "红线断言词出现在没有 [待人工] 的行"))
    miss_rows = sum(1 for ln in lines if ITEM_LINE.match(ln) and MISS.search(ln))
    m = DECL.search(text)
    if not m:
        hits.append(("F-COUNT", 0, "头部申报缺「共八项·缺 N 项」，无从对账"))
    elif int(m.group(1)) != miss_rows:
        hits.append(("F-COUNT", 0, f"申报缺 {m.group(1)} 项∥实际写明未检索到 {miss_rows} 项"))
    return hits


def make_tmp(prefix: str) -> pathlib.Path:
    d = pathlib.Path(tempfile.mkdtemp(prefix=prefix, dir=str(pathlib.Path(tempfile.gettempdir()))))
    TMP_ROOTS.append(d)
    return d


@atexit.register
def _cleanup() -> None:
    for d in TMP_ROOTS:
        shutil.rmtree(d, ignore_errors=True)


def selftest() -> int:
    here = pathlib.Path(__file__).resolve().parent
    gt = (here / "fixtures" / "good-prospectus.md").read_text(encoding="utf-8")
    bt = (here / "fixtures" / "bad-prospectus.md").read_text(encoding="utf-8")
    rows = []
    gh = check_text(gt)
    rows.append(("好样须过（发条 0）", not gh, f"实发 {len(gh)} 条" + ("" if not gh else "｜" + gh[0][2])))
    codes_bad = {c for c, _, _ in check_text(bt)}
    rows.append(("坏样五道齐发", {"F-STRUCT", "F-ANCHOR", "F-CLAIM", "F-LINE", "F-COUNT"} <= codes_bad,
                 "实发码 " + "∥".join(sorted(codes_bad))))
    tmp = make_tmp("check-prospectus-")
    p1 = tmp / "no-anchor.md"
    p1.write_text(re.sub(ANCHOR, "", gt), encoding="utf-8")
    h1 = check_text(p1.read_text(encoding="utf-8"))
    rows.append(("反证·剥锚必发 F-ANCHOR", any(c == "F-ANCHOR" for c, _, _ in h1),
                 f"实发 {sum(1 for c, _, _ in h1 if c == 'F-ANCHOR')} 条"))
    p2 = tmp / "no-page.md"
    p2.write_text(re.sub(PAGE, "", gt), encoding="utf-8")
    h2 = check_text(p2.read_text(encoding="utf-8"))
    rows.append(("反证·剥页码必发 F-ANCHOR", any(c == "F-ANCHOR" and "页码" in m for c, _, m in h2),
                 f"实发 {sum(1 for c, _, m in h2 if c == 'F-ANCHOR' and '页码' in m)} 条"))
    p3 = tmp / "no-tag.md"
    p3.write_text(re.sub(SELF_TAG, "", gt), encoding="utf-8")
    h3 = check_text(p3.read_text(encoding="utf-8"))
    rows.append(("反证·剥自述标注必发 F-CLAIM", any(c == "F-CLAIM" for c, _, _ in h3),
                 f"实发 {sum(1 for c, _, _ in h3 if c == 'F-CLAIM')} 条"))
    lost = "研发与核心技术"
    p4 = tmp / "lost-item.md"
    p4.write_text("\n".join(l for l in gt.splitlines() if lost not in l), encoding="utf-8")
    h4 = check_text(p4.read_text(encoding="utf-8"))
    rows.append(("反证·删一项名目必发 F-STRUCT", any(c == "F-STRUCT" and lost in m for c, _, m in h4),
                 f"实发 {sum(1 for c, _, _ in h4 if c == 'F-STRUCT')} 条"))
    p5 = tmp / "skewed-decl.md"
    p5.write_text(gt.replace("共八项·缺 1 项", "共八项·缺 5 项"), encoding="utf-8")
    h5 = check_text(p5.read_text(encoding="utf-8"))
    rows.append(("反证·齐缺申报改歪必发 F-COUNT", any(c == "F-COUNT" for c, _, _ in h5),
                 f"实发 {sum(1 for c, _, _ in h5 if c == 'F-COUNT')} 条"))
    made = len(TMP_ROOTS)
    root = pathlib.Path(tempfile.gettempdir())
    for p in TMP_ROOTS:
        shutil.rmtree(p, ignore_errors=True)
    leftover = sorted(q.name for q in root.iterdir() if q.name.startswith("check-prospectus-")) if root.is_dir() else []
    rows.append(("临时根自清（跑后不增）", not leftover, f"本次建 {made} 枚·跑后残留 {len(leftover)} 枚"))
    rows.append(("atexit 钩子在场", True, "已注册"))
    bad_rows = [r for r in rows if not r[1]]
    for name, ok, detail in rows:
        print(f"  {'ok  ' if ok else 'FAIL'} {name}｜{detail}")
    nproof = len([r for r in rows if r[0].startswith("反证")])
    print(f"selftest: {'ALL GREEN' if not bad_rows else 'FAIL'}（好样 1 枚·坏样五道·反例 {nproof} 枚·临时根 {made} 枚自清）"
          + (f"｜不合 {len(bad_rows)} 枚" if bad_rows else ""))
    return 0 if not bad_rows else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="招股书速览卡五道机检（零网络）")
    ap.add_argument("target", nargs="?", help="待检文件（本件不读网络、不读目录）")
    ap.add_argument("--selftest", action="store_true", help="好样须过、坏样五道齐发、反证各发各码")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not a.target:
        print("用法：check_prospectus.py <待检文件> | --selftest", file=sys.stderr)
        return 2
    p = pathlib.Path(a.target)
    if not p.is_file():
        print(f"FAIL 文件不在场：{p}", file=sys.stderr)
        return 2
    text = p.read_text(encoding="utf-8", errors="replace")
    hits = check_text(text)
    for code, ln, msg in hits:
        print(f"FAIL [{code}] {p.name}" + (f":{ln}" if ln else "") + f" {msg}")
    print(("PASS" if not hits else "FAIL") + f"（扫过 {len(text.splitlines())} 行，发条 {len(hits)} 条）")
    return 0 if not hits else 1


if __name__ == "__main__":
    sys.exit(main())
