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

# ---- ledger 模式(spec-0.2.0 F1;实现即 M2,缺陷编号见 verify/f1-deskcheck.md)----
LEDGER_STATUSES = {"fulfilled", "unfulfilled", "partial",
                   "carried_forward", "superseded", "unverifiable"}
LEDGER_DIRECTIONS = {"improving", "worsening", "flat"}
LEDGER_RESULTS = {"HIT", "MISS", "NO_TOOL", "EXTRACT_FAILED", "NO_RESPONSE"}
LEDGER_REF_RE = re.compile(r"^[A-Za-z0-9._\-]+:S\d+$")
LEDGER_CARRY_RE = re.compile(r"^(?:[A-Za-z0-9._\-]+:P\d{1,2}|new)$")
LEDGER_HEAD_FIELDS = ("schema", "run", "period")
LEDGER_OF_RE = re.compile(r"^([A-Za-z0-9._\-]+):([\w.\-]+\.json)$")
LEDGER_KNOWN_TOP = {"schema", "run", "period", "ledger_of", "anchors",
                    "risk_scan", "pending", "linkage_checks"}


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


def _walk_value_dicts(node, path):
    """yield (path, dict) for every dict containing a numeric-ish "value" key (D6)."""
    if isinstance(node, dict):
        if "value" in node:
            yield path, node
        for k, v in node.items():
            yield from _walk_value_dicts(v, f"{path}.{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from _walk_value_dicts(v, f"{path}[{i}]")


def _check_ledger_of(led, ledger_path, prev_led, tag, fails):
    """B2(spec-0.2.0 §F1 修 D2):ledger_of 互链的上季文件存在且 period 匹配,机检断言化。"""
    lo = led.get("ledger_of")
    if lo is None:
        return  # 首季建账合法缺省
    m = LEDGER_OF_RE.match(str(lo))
    if not m:
        fails.append(f"[{tag}] ledger_of 格式须为 <run_dir>:<file>.json,实为 {lo!r}")
        return
    run_name, fname = m.group(1), m.group(2)
    here = Path(ledger_path).resolve().parent
    for cand in (here / run_name / fname, Path.cwd() / run_name / fname):
        if cand.is_file():
            try:
                data = json.loads(cand.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as e:
                fails.append(f"[{tag}] ledger_of 命中文件不可读/解析：{cand}（{e}）")
                return
            if data.get("period") == led.get("period"):
                fails.append(f"[{tag}] ledger_of 互链 period 与本季相同（{led.get('period')}）")
            return
    if isinstance(prev_led, dict) and prev_led.get("run") == run_name:
        if prev_led.get("period") == led.get("period"):
            fails.append(f"[{tag}] ledger_of={lo} 经 --prev-ledger 承载,但其 period 与本季相同")
        return
    fails.append(f"[{tag}] ledger_of 断链：{run_name}/{fname} 不可达,且 --prev-ledger 的 run 不匹配")


def check_ledger(path, is_prev=False, prev_led=None):
    fails = []
    tag = "prev-ledger" if is_prev else "ledger"
    try:
        led = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        return [f"[{tag}] 无法读取/解析：{e}"]
    if not isinstance(led, dict):
        return [f"[{tag}] 顶层不是对象"]
    for f in LEDGER_HEAD_FIELDS:  # D2/D9:文件头三件,缺一即断链
        if not str(led.get(f, "")).strip():
            fails.append(f"[{tag}] 头部字段 {f} 缺失或为空")
    _check_ledger_of(led, path, prev_led, tag, fails)  # B2
    unknown = set(led) - LEDGER_KNOWN_TOP
    if unknown:  # 6.1 B1 防呆补位:未识别顶层键提示(不 FAIL,前瞻兼容)
        print(f"[{tag}] ⚠ 未识别顶层键(机检不覆盖,确认拼写): {sorted(unknown)}")
    if "risk_checks" in led:  # 旧名残留=分家复发,直接 FAIL
        fails.append(f"[{tag}] 顶层出现旧名 risk_checks——已统一为 risk_scan(spec-0.2.0)")

    for a in led.get("anchors", []):
        aid = a.get("id", "?")
        status = a.get("status")
        if status not in LEDGER_STATUSES:  # ① D3 六态
            fails.append(f"[{tag}] 锚 {aid} status 非法：{status!r}(六态枚举)")
        if "direction" in a:
            if not a.get("trend"):
                fails.append(f"[{tag}] 锚 {aid} 非趋势锚(trend≠true)不得带 direction(D3)")  # ①
            elif a["direction"] not in LEDGER_DIRECTIONS:
                fails.append(f"[{tag}] 锚 {aid} direction 非法：{a['direction']!r}")
        src = a.get("source")
        if src is not None and not LEDGER_REF_RE.match(str(src)):  # ⑧ D9
            fails.append(f"[{tag}] 锚 {aid} source 引用须为 <run>:S##,实为 {src!r}")
        amended = False
        for ev in a.get("events", []):
            if not ev.get("type") or not ev.get("date"):
                fails.append(f"[{tag}] 锚 {aid} event 缺 type/date(D4)")
            if ev.get("type") == "amendment":
                amended = True
        if amended and status == "fulfilled":  # ② D4
            fails.append(f"[{tag}] 锚 {aid} 有 amendment 事件却判 fulfilled(D4)")

    for key, rc in (led.get("risk_scan") or {}).items():
        result = rc.get("result") if isinstance(rc, dict) else None
        if result not in LEDGER_RESULTS:  # ④ D8 五枚举
            fails.append(f"[{tag}] 风险项 {key} result 非法：{result!r}(HIT/MISS/NO_TOOL/EXTRACT_FAILED/NO_RESPONSE)")
        ev = rc.get("evidence") if isinstance(rc, dict) else None
        if isinstance(ev, str) and ev and not LEDGER_REF_RE.match(ev):  # ⑧
            fails.append(f"[{tag}] 风险项 {key} evidence 引用须为 <run>:S##,实为 {ev!r}")

    for vp, vd in _walk_value_dicts(led, tag):  # ③ D6:一切数值对象带 basis
        b = vd.get("basis")
        if not isinstance(b, dict) or not b:
            fails.append(f"[{tag}] {vp} 带 value 但缺 basis 对象(D6)")

    pend = led.get("pending", [])
    filled = gate_total = 0
    for p in pend:
        pid = p.get("id", "?")
        cf = p.get("carry_from")
        if not LEDGER_CARRY_RE.match(str(cf or "")):  # ⑤ D7
            fails.append(f"[{tag}] pending {pid} carry_from 须为 <run>:P## 或 new,实为 {cf!r}")
        ex = p.get("exempt_from_gate", False)
        if not isinstance(ex, bool):  # ⑥ D11
            fails.append(f"[{tag}] pending {pid} exempt_from_gate 须为布尔(D11)")
            ex = False
        if not ex:
            gate_total += 1
            if p.get("verdict") is not None:
                filled += 1
    print(f"[{tag}] 裁决回填率(除豁免行): {filled}/{gate_total}")  # ⑥:豁免行不入统计

    for i, lc in enumerate(led.get("linkage_checks", []), 1):  # ⑦ D5 核心
        pe, tb = lc.get("prev_period_end"), lc.get("this_period_begin")
        refs = lc.get("both_ref")
        if pe != tb:
            fails.append(
                f"[{tag}] linkage#{i} {lc.get('metric','?')} 跨期衔接不等: "
                f"上季末={pe!r} vs 本季初={tb!r} (refs={refs})")
        if not (isinstance(refs, list) and len(refs) == 2
                and all(LEDGER_REF_RE.match(str(r)) for r in refs)):  # ⑧
            fails.append(f"[{tag}] linkage#{i} both_ref 须为两条 <run>:S##,实为 {refs!r}")
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
    p.add_argument("--ledger", default=None, help="覆盖账本当期 JSON（spec-0.2.0 F1 八项校验，见 references/ledger-schema.md）")
    p.add_argument("--prev-ledger", default=None, help="上一期账本 JSON（同样过结构校验；linkage 断言在当期文件内自含）")
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
    if args.ledger:
        prev_data = None
        if args.prev_ledger:
            try:
                prev_data = json.loads(Path(args.prev_ledger).read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                pass  # 失败由 prev 校验路径自行报
        fails += check_ledger(args.ledger, prev_led=prev_data)
    if args.prev_ledger:
        fails += check_ledger(args.prev_ledger, is_prev=True)

    if fails:
        print(f"FAIL: {args.note}（{len(fails)} 条）")
        for f in fails:
            print(f"  - {f}")
        return 1
    print(f"PASS: {args.note}（数字行 {tagged}/{total} 已标注，四道门禁全过）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
