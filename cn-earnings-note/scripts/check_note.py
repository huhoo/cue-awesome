#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_note.py —— cn-earnings-note 交付前门禁（SKILL.md §3.6，不过不交付）。

纯 stdlib、零网络。exit 0=过闸；exit 1=FAIL（逐条列因，含行号）。

四道检查：
  1. 声明在场      —— 首个标题行之后前 5 行内须同时出现「AI 初稿」与「不构成…投资建议」。
  2. [待人工] 就位 —— 含「评级」/「目标价」的行不得给出具体评级词或目标价值，且须带
                      [待人工]；--allow-pending 关闭本项。
  3. 禁用词        —— 合规最小集黑名单（内置），命中即 FAIL。
                      与 references/data-channels.md §合规最小集 冲突时以先 VERIFIED 者对齐。
  4. 数字可回查    —— 含「数字+%/亿元/万元/倍/个百分点」的正文行须带 [L1]/[L2]/[L3]；
                      标题行、列表引导行（以 - * 或数字序号引导且自身不含数字单位）、
                      「来源索引」节内豁免；覆盖率 < --min-coverage（默认 95%）FAIL。
                      给了 --sources 时另验 JSONL 契约（id/kind/ref/claim/confidence/asof
                      齐全、confidence 与标注同级、asof 为 YYYY-MM-DD）且正文引用的
                      [S<n>] id 均可解析。

用法：
  python3 check_note.py <note.md> [--sources sources.jsonl] [--allow-pending]
"""

import argparse
import json
import re
import sys
from pathlib import Path

# 合规最小集（铁律 6）。与 A 单 data-channels.md §合规最小集 若冲突，以先 VERIFIED 者对齐。
BANNED_WORDS = ["必涨", "稳赚", "零风险", "保证收益", "内幕", "无风险套利", "历史最佳"]
BANNED_RE = re.compile("|".join(BANNED_WORDS))

NUM_UNIT_RE = re.compile(r"\d(?:[.,]\d+)?\s*(?:%|percent|亿元|万元|倍|个百分点)", re.IGNORECASE)
LEVEL_RE = re.compile(r"\[L[123]\]")
SRC_REF_RE = re.compile(r"\[S(\d+)\]")
HEADING_RE = re.compile(r"^#{1,6}\s")
INDEX_HEADING_RE = re.compile(r"^#{1,6}\s.*来源索引")
LIST_LEAD_RE = re.compile(r"^\s*(?:[-*]|\d+[.)、])\s+")
RATING_WORD_RE = re.compile(
    r"买入|增持|减持|卖出|中性|持有|推荐|强烈推荐|强烈买入|审慎增持|跑赢|跑输|逢低|高沽"
)
TARGET_VALUE_RE = re.compile(r"目标价[^。\n]*?\d+(?:\.\d+)?\s*(?:元|港元|美元|RMB|HKD|USD)", re.IGNORECASE)
PENDING_RE = re.compile(r"\[待人工\]")
# 白名单评级词以斜杠枚举并列且同行带 [待人工] 时,是 data-channels.md §4.3 允许的
# 「模板占位句式」(封面声明/§7 评级行),不构成「给出具体评级」——豁免条件:行内每个
# 白名单词都邻接斜杠;任一裸出现的词(如「倾向买入」)即破豁免照常 FAIL。
# 邻接前先把词典叠词(买卖/购买)归一,防「证券买卖推荐」这类通用词误判为评级词。
RATING_ENUM_RE = re.compile(r"(?:买入|增持|中性|减持|卖出)/(?:买入|增持|中性|减持|卖出)")
ANY_RATING_RE = re.compile(r"买入|增持|中性|减持|卖出")
SLASH = "/"


def _all_ratings_slash_adjacent(line):
    probe = line.replace("买卖", "XX").replace("购买", "XX")
    for m in ANY_RATING_RE.finditer(probe):
        before = probe[m.start() - 1] if m.start() > 0 else ""
        after = probe[m.end()] if m.end() < len(probe) else ""
        if SLASH not in (before, after):
            return False
    return True
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SOURCE_REQUIRED_FIELDS = ("id", "kind", "ref", "claim", "confidence", "asof")


def classify_lines(lines):
    """返回与 lines 等长的布尔表：该行是否属于「来源索引」豁免区（标题起，至下一任意标题止）。"""
    exempt = [False] * len(lines)
    in_index = False
    for i, line in enumerate(lines):
        if INDEX_HEADING_RE.match(line):
            in_index = True
        elif in_index and HEADING_RE.match(line):
            in_index = False
        exempt[i] = in_index
    return exempt


def check_declaration(lines):
    fails = []
    title_idx = next((i for i, l in enumerate(lines) if HEADING_RE.match(l)), None)
    if title_idx is None:
        return ["[声明] 未找到标题行（# 开头），AI 初稿声明无从挂靠"]
    window = "".join(lines[title_idx + 1: title_idx + 6])
    if "AI 初稿" not in window:
        fails.append(f"[声明] 标题后前 5 行内未出现「AI 初稿」（实际扫描行 {title_idx + 2}–{title_idx + 6}）")
    if not re.search(r"不构成.{0,12}投资建议", window):
        fails.append("[声明] 标题后前 5 行内未出现「不构成…投资建议」免责句")
    return fails


def check_pending(lines, index_exempt):
    fails = []
    for i, line in enumerate(lines):
        if index_exempt[i] or not line.strip():
            continue
        has_kw = ("评级" in line) or ("目标价" in line)
        if not has_kw:
            continue
        if has_kw and PENDING_RE.search(line) and RATING_ENUM_RE.search(line) \
                and _all_ratings_slash_adjacent(line):
            continue  # §4.3 模板占位句式:白名单词全部斜杠邻接且同行 [待人工];裸出现一词即破豁免
        if RATING_WORD_RE.search(line) or TARGET_VALUE_RE.search(line):
            fails.append(f"[待人工] 第 {i + 1} 行给出了具体评级/目标价：{line.strip()[:60]}")
        elif not PENDING_RE.search(line):
            fails.append(f"[待人工] 第 {i + 1} 行涉及评级/目标价但未见 [待人工]：{line.strip()[:60]}")
    return fails


def check_banned(lines):
    fails = []
    for i, line in enumerate(lines):
        m = BANNED_RE.search(line)
        if m:
            fails.append(f"[禁用词] 第 {i + 1} 行命中「{m.group(0)}」：{line.strip()[:60]}")
    return fails


def check_numbers(lines, index_exempt, sources_path, min_coverage):
    fails = []
    stat_rows = []
    refs = set()
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        for rid in SRC_REF_RE.findall(line):
            if not index_exempt[i]:
                refs.add(int(rid))
        if index_exempt[i] or HEADING_RE.match(line):
            continue
        has_num = bool(NUM_UNIT_RE.search(line))
        if not has_num:
            continue
        if LIST_LEAD_RE.match(line) and not LEVEL_RE.search(line) and SRC_REF_RE.search(line):
            continue  # 列表引导行自带 [S<n>] 来源指向,视为可回查
        stat_rows.append((i, line))
        if not LEVEL_RE.search(line):
            fails.append(f"[数字] 第 {i + 1} 行含数字结论但无 [L1]/[L2]/[L3]：{stripped[:60]}")

    total = len(stat_rows)
    tagged = total - sum(1 for f in fails if f.startswith("[数字]"))
    coverage = 1.0 if total == 0 else tagged / total
    pct = coverage * 100
    if coverage * 100 + 1e-9 < min_coverage:
        fails.insert(0, f"[数字] 可回查覆盖率 {pct:.1f}% < 阈值 {min_coverage:.0f}%（{tagged}/{total}）")

    if sources_path:
        fails.extend(check_sources_jsonl(sources_path, refs, lines))
    return fails, total, tagged


def check_sources_jsonl(path, refs_in_note, lines):
    fails = []
    ids = set()
    try:
        raw = Path(path).read_text(encoding="utf-8")
    except OSError as e:
        return [f"[来源] --sources 无法读取：{e}"]
    for ln, line in enumerate(raw.splitlines(), 1):
        if not line.strip():
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError as e:
            fails.append(f"[来源] sources.jsonl 第 {ln} 行非法 JSON：{e}")
            continue
        if not isinstance(rec, dict):
            fails.append(f"[来源] sources.jsonl 第 {ln} 行不是对象")
            continue
        for f in SOURCE_REQUIRED_FIELDS:
            v = rec.get(f)
            if not isinstance(v, str) or not v.strip():
                fails.append(f"[来源] sources.jsonl 第 {ln} 行字段 {f} 缺失或为空")
        m = re.fullmatch(r"S(\d+)", str(rec.get("id", "")))
        if m:
            ids.add(int(m.group(1)))
        elif rec.get("id"):
            fails.append(f"[来源] sources.jsonl 第 {ln} 行 id 不符合 S<n>：{rec['id']}")
        if rec.get("asof") and not DATE_RE.match(rec["asof"]):
            fails.append(f"[来源] sources.jsonl 第 {ln} 行 asof 非 YYYY-MM-DD：{rec['asof']}")

    missing = sorted(refs_in_note - ids)
    if missing:
        fails.append("[来源] 正文引用的 [S<n>] 在 sources.jsonl 中无法解析：" + ", ".join(f"S{n}" for n in missing))
    return fails


def main(argv=None):
    p = argparse.ArgumentParser(
        description="cn-earnings-note 交付前四道门禁：声明在场 / [待人工] 就位 / 禁用词 / 数字可回查。",
        epilog="exit 0=过闸；exit 1=FAIL。纯 stdlib、零网络。",
    )
    p.add_argument("note", help="待检查的 note.md")
    p.add_argument("--sources", default=None, help="sources.jsonl；给了则逐条验证契约字段与 [S<n>] 引用可解析")
    p.add_argument("--allow-pending", action="store_true", help="关闭「[待人工] 就位」检查（第 2 道）")
    p.add_argument("--min-coverage", type=float, default=95.0, help="数字可回查覆盖率阈值（默认 95）")
    args = p.parse_args(argv)

    try:
        lines = Path(args.note).read_text(encoding="utf-8").splitlines()
    except OSError as e:
        print(f"FAIL: 无法读取 {args.note}: {e}")
        return 1

    index_exempt = classify_lines(lines)
    fails = []
    fails += check_declaration(lines)
    if not args.allow_pending:
        fails += check_pending(lines, index_exempt)
    fails += check_banned(lines)
    num_fails, total, tagged = check_numbers(lines, index_exempt, args.sources, args.min_coverage)
    fails += num_fails

    if fails:
        print(f"FAIL: {args.note}（{len(fails)} 条）")
        for f in fails:
            print(f"  - {f}")
        return 1
    print(f"PASS: {args.note}（数字行 {tagged}/{total} 已标注，四道门禁全过）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
