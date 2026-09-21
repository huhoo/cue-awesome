#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_calendar.py —— catalyst-calendar 交付前机检(spec-0.1.0 §4 最小四道,自成一包)。

纯 stdlib、零网络。exit 0=过闸;exit 1=FAIL(逐条列因,含行号)。
CLI: check_calendar.py <calendar.md> [--window YYYY-MM-DD~YYYY-MM-DD] [--no-default-window]
     窗口缺省=今起 90 天;CI 复现请显式 --window,或 --no-default-window 只查日期格式。
四道:
  ①声明行:首个标题后前 5 行内须含「AI 初稿」+「不构成…投资建议」(与姊妹件同死文字标准)。
  ②锚三式:表格数据行必含 公告索引号(AN+10位/12开头9位)/URL/`conv_id=` 其一——
    最大风险=日期幻觉,无锚裸日期行一律 FAIL(表头与分隔行豁免)。
  ③禁词:cn-earnings-note BANNED 七词 + 利好|利空|暴涨|会涨|抄底|逃顶。
  ④日期:全格式 YYYY-MM-DD 且在窗口内;窗外条目须同行注「窗口外余档」;解析失败即 FAIL。
"""

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

SOURCE_REQUIRED_FIELDS = ("id", "kind", "ref", "claim", "confidence", "asof")

BANNED_RE = re.compile(
    r"必涨|稳赚|零风险|保证收益|内幕|无风险套利|历史最佳|利好|利空|暴涨|会涨|抄底|逃顶")
HEADING_RE = re.compile(r"^#{1,6}\s")
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
LOOSE_DATE_RE = re.compile(r"(?<![\d-])\d{3,4}[-/年.]\d{1,2}([-/月.]\d{1,2}日?)?(?![\d-])")
ANCHOR_RES = (
    re.compile(r"AN\d{10}|(?<!\d)12\d{7}(?!\d)"),
    re.compile(r"https?://"),
    re.compile(r"conv_id="),
)
OUTSIDE_NOTE = "窗口外余档"


def check_declaration(lines):
    fails = []
    title = next((i for i, l in enumerate(lines) if HEADING_RE.match(l)), None)
    if title is None:
        return ["[声明] 未找到标题行"]
    window = "".join(lines[title + 1: title + 6])
    if "AI 初稿" not in window:
        fails.append("[声明] 标题后前 5 行缺「AI 初稿」")
    if not re.search(r"不构成.{0,12}投资建议", window):
        fails.append("[声明] 标题后前 5 行缺「不构成…投资建议」")
    return fails


def is_table_row(s):
    return s.strip().startswith("|")


def check_rows(lines, lo, hi):
    """②锚三式+④日期窗口。返回 fails。"""
    fails = []
    prev_is_table = False
    for i, raw in enumerate(lines):
        line = raw.strip()
        if not line:
            prev_is_table = False  # 空行=表结束,下一张表的首行重新按表头豁免
            continue
        if line.startswith("```"):
            continue  # 代码围栏行进/出本身非数据行,不查
        row = is_table_row(line)
        header_ctx = row and prev_is_table
        if row and not header_ctx:
            prev_is_table = row
            continue  # 表头行豁免
        if row:  # 分隔行(仅 - : | 空格)豁免
            if not re.sub(r"[|:\-\s]", "", line):
                prev_is_table = row
                continue
            if not any(p.search(line) for p in ANCHOR_RES):
                fails.append(f"[锚] 第 {i + 1} 行表格数据行无任何来源锚(日期幻觉防线):{line[:60]}")
        prev_is_table = row
        for d in DATE_RE.findall(line):
            try:
                day = dt.date.fromisoformat(d)
            except ValueError:
                fails.append(f"[日期] 第 {i + 1} 行日期不可解析:{d}")
                continue
            if (lo or hi) and OUTSIDE_NOTE not in line:
                if lo and day < lo:
                    fails.append(f"[日期] 第 {i + 1} 行 {d} 早于窗口起点且未注「{OUTSIDE_NOTE}」")
                elif hi and day > hi:
                    fails.append(f"[日期] 第 {i + 1} 行 {d} 晚于窗口终点且未注「{OUTSIDE_NOTE}」")
        m = LOOSE_DATE_RE.search(re.sub(r"\d{4}-\d{2}-\d{2}", "", line))
        if m:
            fails.append(f"[日期] 第 {i + 1} 行非标准日期写法:{m.group(0)!r}(全篇须 YYYY-MM-DD)")
    return fails


def check_banned(lines):
    return [f"[禁词] 第 {i + 1} 行命中「{BANNED_RE.search(l).group(0)}」:{l.strip()[:60]}"
            for i, l in enumerate(lines) if BANNED_RE.search(l)]


def check_sources(path):
    """sources.jsonl 六字段契约(与姊妹件同源;日历正文用直锚不用 S 引用,故不做双向解析)。"""
    fails = []
    try:
        raw = Path(path).read_text(encoding="utf-8")
    except OSError as e:
        return [f"[sources] 无法读取:{e}"]
    for ln, line in enumerate(raw.splitlines(), 1):
        if not line.strip():
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError as e:
            fails.append(f"[sources] 第 {ln} 行非法 JSON:{e}")
            continue
        if not isinstance(rec, dict):
            fails.append(f"[sources] 第 {ln} 行不是对象")
            continue
        for f in SOURCE_REQUIRED_FIELDS:
            v = rec.get(f)
            if not isinstance(v, str) or not v.strip():
                fails.append(f"[sources] 第 {ln} 行字段 {f} 缺失或为空")
    return fails


def main(argv=None):
    p = argparse.ArgumentParser(description="catalyst-calendar 四道机检(声明/锚三式/禁词/日期窗口)。")
    p.add_argument("calendar", help="calendar.md")
    p.add_argument("--sources", default=None, help="sources.jsonl(六字段契约核验;§3 输出契约「全锚可解析」)")
    p.add_argument("--window", default=None, help="窗口 YYYY-MM-DD~YYYY-MM-DD;缺省=今起90天")
    p.add_argument("--no-default-window", action="store_true", help="不套默认窗口,仅查日期格式")
    args = p.parse_args(argv)
    try:
        lines = Path(args.calendar).read_text(encoding="utf-8").splitlines()
    except OSError as e:
        print(f"FAIL: 无法读取 {args.calendar}: {e}")
        return 1

    lo = hi = None
    if args.window:
        try:
            a, b = args.window.split("~")
            lo, hi = dt.date.fromisoformat(a.strip()), dt.date.fromisoformat(b.strip())
        except ValueError:
            print(f"FAIL: --window 形制应为 YYYY-MM-DD~YYYY-MM-DD,实为 {args.window!r}")
            return 1
    elif not args.no_default_window:
        today = dt.date.today()
        lo, hi = today, today + dt.timedelta(days=90)

    fails = check_declaration(lines)
    fails += check_rows(lines, lo, hi)
    fails += check_banned(lines)
    if args.sources:
        fails += check_sources(args.sources)
    if fails:
        print(f"FAIL: {args.calendar}（{len(fails)} 条）")
        for f in fails:
            print(f"  - {f}")
        return 1
    print(f"PASS: {args.calendar}（声明/锚三式/禁词/日期四道全过"
          + (f"，窗口 {lo}~{hi}）" if hi else "，窗口未启用）"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
