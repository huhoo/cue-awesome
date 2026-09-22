#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_calendar.py v4 —— catalyst-calendar 机检(spec §v2-B + §v3-B + §v4-A 七件 + §v4-B 证据层)。

纯 stdlib、零网络、零崩溃(B6:任何输入只输出 FAIL 清单+exit 1,traceback=事故)。
CLI(必传):check_calendar.py <calendar.md> --window YYYY-MM-DD~YYYY-MM-DD --sources <sources.jsonl>
选传:--evidence <run>/evidence(v4-B⑦ 证据层匹配道;不传=跳过并打印提示,旧样兼容)

v4 变更(样号对应 M32 报告 §1):
  ① 前瞻账行(主体+摘要)非日期列全扫 ISO 日期,与日期列不一致即 FAIL(S2)。
  ② 评级扫描无视《》豁免;官方用语后缀强制(光杆「建议增持」不豁免)(S3/S4)。
  ③ 保留区语义:附录禁表格行(只许清单,S5);已发生动态只准过去日(日期<窗口起点,S6b)。
  ④ 摘要 ⊆ 主表日期集合按保留词区定位实现,不依赖字面标题(S10)。
  ⑤ 空/不可解析日期列一律行号化 FAIL,零 traceback(S8)。
  ⑥ 自白词表扩充(或将|有望|估计|按过往节奏|拟+动词)——lint 性质,尽力而为(S7)。
  ⑦ 证据层匹配道:主体/摘要/动态每条锚须在 --evidence 目录原文整词命中(M40-B1:
     锚型左右非 alnum 边界,禁前缀撞号——T1 真号少末位);statute 锚
     法名+条号+要点全串须在证据在场(裸编法名/引已删条文=断链 FAIL);要点含 快报|无条件
     直接拦(S1/S1b)。语义真值到此为止,再深归人审(§v4-B)。

v3 变更(对 M27 十攻击样与 M28 真实冒烟):
  A1 六列表:日期|事件|类型|状态|窗外余档|来源锚;窗外注=第5列以「窗口外余档」开头,窗内行
     第5列必须空,锚列永远末列纯锚。
  A2 节名保留词封闭集 {未来 30 天要盯|已发生动态|附录}:非保留词的 ## 节=主体节(废「主体」
     字面前缀,N3);摘要保留词节必须存在(N8);已发生动态/附录节表行不占前瞻账(窗口/降序/
     计数豁免,N6),但禁词/评级/B11 照扫。
  A3 statute 锚规格:statute:《法名》第N条（要点短引） 三段齐;**主体节/摘要**的 statute 锚须
     sources kind=statute 行以同串承载(N2 反自证);**附注区(已发生动态)锚只验形状不要求行**
     ——§v3-A3 字面「且 sources 对应行」与 N6(附注 statute 行应 PASS)在 B7/N1b 下互斥,
     实现取此判,差异已随 M29 回执申报 lead 裁。
  A4 评级零容忍扫描区=事件/状态/余档/锚列+非表格正文+sources claim;豁免仅类型列、
     《官方标题》区与官方披露用语组合(N4/M4)。
  B6 --window/--sources 必传;解析点全 try 化,主入口 try 兜底。
  B7 反向收紧:sources 行被引用只认「主体节+摘要」表锚列键,附录文本不算(N1b);
     窗口一致性只解析字面「窗口 A~B」。
  B8 类型×锚型全量映射禁 fallback;监管必配函件号(AN 仅辅锚,N9);法定必配 statute。
  B11 幻觉自白词:事件/状态含 惯例|预计|大约|大概率|通常|非承诺 → FAIL(M28 真实样=第11枚)。
"""

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

HEADER_COLS = ["日期", "事件", "类型", "状态", "窗外余档", "来源锚"]
RESERVED = ("未来 30 天要盯", "已发生动态", "附录")
SUMMARY_HEAD = "未来 30 天要盯"
DONGTAI_HEAD = "已发生动态"
OUTSIDE_PREFIX = "窗口外余档"
BANNED_RE = re.compile(
    r"必涨|稳赚|零风险|保证收益|内幕|无风险套利|历史最佳|利好|利空|暴涨|会涨|抄底|逃顶")
RATING_RE = re.compile(r"买入|增持|减持|持有|推荐|目标价")
OFFICIAL_USAGE_RE = re.compile(
    r"(?:减持|增持)(?:计划|预披露|进展|实施|结果|完成|期限|变动|股份)"
    r"|持有(?:公司股份|股份|以上|5%)|买入返售")  # v4-B②:后缀强制,光杆「增持/减持」不豁免(S4)
HALLUCINATION_RE = re.compile(
    r"惯例|预计|大约|大概率|通常|非承诺|或将|有望|估计|按过往节奏"
    r"|拟(?:披露|增持|减持|回购|发行|实施|审议|变更|修订)")  # v4-B⑥ lint 性质,尽力而为;「预案」类名词不杀
HEADING_RE = re.compile(r"^(#{1,6})\s*(.*)$")
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
LOOSE_DATE_RE = re.compile(r"\d{4}\s*[/年.-]\s*\d{1,2}\s*[/月.-]\s*\d{1,2}\s*日?")
QUOTE_TITLE_RE = re.compile(r"《[^《》]*》")
TITLE_HEAD = re.compile(r"窗口\s*(\d{4}-\d{2}-\d{2})\s*[~至]\s*(\d{4}-\d{2}-\d{2})")
BAN_NOTE_RE = re.compile(r"不得|禁止|不适用|勿|不构成")
AN_RE = re.compile(r"^AN\d{8,}$")
SIX_RE = re.compile(r"^\d{6,}$")
URL_RE = re.compile(r"^https?://\S+$")
LETTER_SEG_RE = re.compile(r"^\S*〔\d{4}〕\d+号$")
STATUTE_SPEC_RE = re.compile(
    r"^statute[:：]《[^《》]+》第[0-9一二三四五六七八九十百零]+条（[^（）]{2,}）$")
CONV_RE = re.compile(r"conv_id=\S+")
CONV_PATH_RE = re.compile(r"(\.md|\.log|reports/)")
SEP_ROW_RE = re.compile(r"^[|\s:\-]+$")

EVENT_TYPES = {"回购", "激励", "解禁减持", "监管", "分红", "法定",
               "股东大会", "说明会", "风险警示", "停复牌"}
TYPE_ANCHORS = {  # B8 全量映射,无 fallback 放行
    "回购": {"AN", "six", "url", "conv"},
    "激励": {"AN", "six", "url", "conv"},
    "解禁减持": {"AN", "six", "url", "conv"},
    "监管": {"letter", "AN", "six", "url", "conv"},
    "分红": {"AN", "six", "url", "conv"},
    "法定": {"statute"},
    "股东大会": {"AN", "six", "url", "conv"},
    "说明会": {"AN", "six", "url", "conv"},
    "风险警示": {"AN", "six", "url", "conv"},
    "停复牌": {"AN", "six", "url", "conv"},
}
TYPE_MUST = {"法定": "statute", "监管": "letter"}
TYPE_HINTS = {  # B2 语义归错(v2 保留,M21-2 样依赖):事件含他类提示且不含本类提示 → FAIL
    "回购": ["回购"], "激励": ["激励", "持股计划", "归属", "行权"],
    "解禁减持": ["解禁"], "监管": ["问询", "监管", "警示函", "整改", "通报批评"],
    "分红": ["中期分红", "派发", "派息", "除权", "除息", "利润分配", "分红方案", "分红议案"],
    "法定": ["法定", "定期报告", "季报", "半年报", "年报"],
    "股东大会": ["股东会"], "说明会": ["说明会", "业绩会", "路演"],
    "风险警示": ["ST", "风险警示", "退市警示"], "停复牌": ["停牌", "复牌"],
}
KIND_ENUM = {"buyback", "esop", "disclosure_cn", "regulatory_cn", "statute",
             "research", "disclosure", "institutional", "user", "omni", "pool"}


def parse_date(s):
    try:
        return dt.date.fromisoformat(s)
    except (ValueError, TypeError):
        return None


def rating_offending(s):
    for w in ("解禁减持", "解禁/减持", "解除限售减持"):  # B5 名词豁免:分类学词组非判词
        s = s.replace(w, "□")
    cleaned = OFFICIAL_USAGE_RE.sub("□", s)
    m = RATING_RE.search(cleaned)
    return m.group(0) if m else None


def evidence_hit(text, probe):
    """M40-B1:证据层按锚型整词边界匹配——探针左右须非 alnum,禁前缀撞号。
    T1 样(真公告号 AN…44258 少末位 AN…4425)在子串 in 下假阳性放行;AN/函件号/
    six/conv/url/statute 整段同界(CJK 相邻字符本非 alnum,天然安全)。"""
    return re.search(r"(?<![0-9A-Za-z])" + re.escape(probe) + r"(?![0-9A-Za-z])", text) is not None


def anchor_forms(cell):
    forms = set()
    for seg in re.split(r"\s*\+\s*", (cell or "").strip()):
        s = seg.strip().rstrip("。;；")
        if not s or s in {"—", "-", "–"}:
            continue
        if AN_RE.match(s):
            forms.add("AN")
        elif SIX_RE.match(s):
            forms.add("six")
        elif s.lower().startswith("statute:"):
            forms.add("statute")
        elif URL_RE.match(s):
            forms.add("url")
        elif "conv_id=" in s:
            forms.add("conv")
        elif LETTER_SEG_RE.match(s):
            forms.add("letter")
        else:
            forms.add(f"unrecognized:{s[:18]}")
    return forms


def anchor_keys(cell):
    keys = []
    for seg in re.split(r"\s*\+\s*", (cell or "").strip()):
        s = seg.strip().rstrip("。;；")
        if not s or s in {"—", "-", "–"}:
            continue
        if AN_RE.match(s) or SIX_RE.match(s) or s.lower().startswith("statute:"):
            keys.append(s)
            continue
        keys.extend(u.rstrip(".,;") for u in re.findall(r"https?://\S+", s))
        keys.extend(c.rstrip(".,;") for c in re.findall(r"conv_id=\S+", s))
        keys.extend(re.findall(r"\S*〔\d{4}〕\d+号", s))
    return keys


def split_sections(lines):
    sections = []
    cur, cur_lv, start = "(前言)", 0, 0
    for i, l in enumerate(lines):
        m = HEADING_RE.match(l)
        if m:
            sections.append((cur, cur_lv, start, i))
            cur, cur_lv, start = m.group(2).strip(), len(m.group(1)), i
    sections.append((cur, cur_lv, start, len(lines)))
    return sections


def section_kind(title):
    for r in RESERVED:
        if title.startswith(r):
            return "reserved:" + r
    return "subject"


def parse_tables(lines):
    rows, fails = [], []
    i, n = 0, len(lines)
    while i < n:
        s = lines[i].strip()
        if not s.startswith("|"):
            i += 1
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if cells[:5] == ["日期", "事件", "类型", "状态", "来源锚"] and cells[:6] != HEADER_COLS:
            fails.append(f"[表] 第 {i + 1} 行五列旧形(v3 六列强制 B13):{s[:60]}")
            i += 1
            continue
        if cells[:6] == HEADER_COLS:
            if i + 1 >= n or "|" not in lines[i + 1] or not SEP_ROW_RE.match(lines[i + 1].strip()):
                fails.append(f"[表] 第 {i + 1} 行六列表头后缺分隔行(B1 双验)")
                i += 1
                continue
            i += 2
            while i < n and lines[i].strip().startswith("|"):
                r = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if len(r) != 6:
                    fails.append(f"[表] 第 {i + 1} 行列数 {len(r)}≠6(v3 六列形制 A1)")
                else:
                    rows.append({"lineno": i + 1, "date": r[0], "event": r[1], "type": r[2],
                                 "status": r[3], "outside": r[4], "anchor": r[5]})
                i += 1
            continue
        if SEP_ROW_RE.match(s):
            fails.append(f"[表] 第 {i + 1} 行分隔行无表头在前(B1):{s[:50]}")
            i += 1
            continue
        fails.append(f"[表] 第 {i + 1} 行孤儿管道行,无合法表头(B1):{s[:60]}")
        i += 1
    return rows, fails


def load_sources(path):
    recs, fails = [], []
    try:
        raw = Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        return recs, [f"[sources] 无法读取:{e}"]
    seen = set()
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
        recs.append((ln, rec))
        rid = rec.get("id")
        rid = rid if isinstance(rid, str) else ""
        if not re.fullmatch(r"S\d+", rid):
            fails.append(f"[sources] 第 {ln} 行 id 非 S<n>:{rid!r}")
        if rid in seen:
            fails.append(f"[sources] id 重复:{rid}")
        seen.add(rid)
        for f in ("id", "kind", "ref", "claim", "confidence", "asof"):
            v = rec.get(f)
            if not isinstance(v, str) or not v.strip():
                fails.append(f"[sources] 第 {ln} 行字段 {f} 缺失或为空")
        kind = rec.get("kind")
        if isinstance(kind, str) and kind and kind not in KIND_ENUM:
            fails.append(f"[sources] 第 {ln} 行 kind 非枚举:{kind!r}")
        conf = rec.get("confidence")
        if isinstance(conf, str) and conf and conf not in {"L1", "L2", "L3"}:
            fails.append(f"[sources] 第 {ln} 行 confidence 非枚举:{conf!r}")
        a = rec.get("asof")
        if isinstance(a, str) and a and (not re.fullmatch(r"\d{4}-\d{2}-\d{2}", a) or parse_date(a) is None):
            fails.append(f"[sources] 第 {ln} 行 asof 非法日期:{a!r}")
        if kind == "research":
            ref = rec.get("ref") if isinstance(rec.get("ref"), str) else ""
            if not (CONV_RE.search(ref) and CONV_PATH_RE.search(ref)):
                fails.append(f"[sources] 第 {ln} 行 research 件缺 conv_id+落盘路径")
        if kind == "statute" and not STATUTE_SPEC_RE.match(str(rec.get("ref", "")).strip()):
            fails.append(f"[sources] 第 {ln} 行 statute ref 不符《法名》第N条（要点）规格(A3)")
        if isinstance(rec.get("claim"), str):
            bad = rating_offending(QUOTE_TITLE_RE.sub("", rec["claim"]))
            if bad:
                fails.append(f"[评级] sources 第 {ln} 行 claim 含评级词「{bad}」(A4 扫描区)")
    return recs, fails


def run(args):
    fails = []
    if not args.window:
        fails.append("[参数] 缺 --window(B6 必传,反 wall-clock)")
    if not args.sources:
        fails.append("[参数] 缺 --sources(B7 必传)")
    if fails:
        return fails, None
    m = re.match(r"^(\d{4}-\d{2}-\d{2})[~至](\d{4}-\d{2}-\d{2})$", args.window.strip())
    lo = parse_date(m.group(1)) if m else None
    hi = parse_date(m.group(2)) if m else None
    if not m or not lo or not hi:
        return [f"[参数] --window 形制或日期非法:{args.window!r}"], None
    if lo > hi:
        return ["[参数] --window 起点晚于终点"], None
    try:
        lines = Path(args.calendar).read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError) as e:
        return [f"无法读取 {args.calendar}:{e}"], None

    recs, sf = load_sources(args.sources)
    fails += sf
    evidence_text = None
    if args.evidence:
        epaths = [p for p in Path(args.evidence).resolve().iterdir() if p.is_file()] if Path(args.evidence).is_dir() else []
        if not epaths:
            fails.append(f"[证据] --evidence 目录无文件:{args.evidence}")
        else:
            evidence_text = "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in epaths)
    elif not fails:
        print("[证据] 未提供 --evidence,证据层匹配道跳过(v4-B⑦;题单旧样兼容)")

    title = next((i for i, l in enumerate(lines) if HEADING_RE.match(l)), None)
    if title is None:
        fails.append("[声明] 未找到标题行")
    else:
        w5 = "".join(lines[title + 1: title + 6])
        if "AI 初稿" not in w5:
            fails.append("[声明] 标题后前 5 行缺「AI 初稿」")
        if not re.search(r"不构成.{0,12}投资建议", w5):
            fails.append("[声明] 标题后前 5 行缺「不构成…投资建议」")
    h2 = next((i for i, l in enumerate(lines) if l.startswith("## ")), len(lines))
    tw = TITLE_HEAD.search("\n".join(lines[:min(h2, 8)]))  # B7:只认字面「窗口 A~B」
    if tw and (tw.group(1) != lo.isoformat() or tw.group(2) != hi.isoformat()):
        fails.append(f"[窗口] 标题声明 {tw.group(1)}~{tw.group(2)} 与 --window 不一致")

    sections = split_sections(lines)
    kinds = [(t, s0, s1, section_kind(t)) for t, lv, s0, s1 in sections if lv in (0, 2)]
    # 主体节=二级且非保留词;一级标题与三级以下不入节计数
    n_subject = sum(1 for t, s0, s1, k in kinds if k == "subject" and t != "(前言)" and s1 > s0 + 1)
    if n_subject > 10:
        fails.append(f"[主体] 主体节 {n_subject} 个 > 10(A2 保留词判定,N3)")
    if not any(k == f"reserved:{SUMMARY_HEAD}" for _, _, _, k in kinds):
        fails.append("[节名] 缺保留词节「未来 30 天要盯」(A2,N8:改名即不是摘要)")

    rows, tf = parse_tables(lines)
    fails += tf

    def locate(r):
        ln = r["lineno"] - 1
        for t, s0, s1, k in kinds:
            if s0 <= ln < s1:
                return t, k
        return "?", "?"

    forward_keys = set()
    subj_dates = {}
    for r in rows:
        sec_t, sec_k = locate(r)
        d = parse_date(r["date"]) if re.fullmatch(r"\d{4}-\d{2}-\d{2}", r["date"]) else None
        if sec_k == "subject":
            if d is None:
                fails.append(f"[日期] 第 {r['lineno']} 行日期列为空或不可解析:{r['date'][:20]!r}(v4-B⑤ 行号化,零 traceback)")
            else:
                if not (lo <= d <= hi) and not r["outside"].startswith(OUTSIDE_PREFIX):
                    fails.append(f"[日期] 第 {r['lineno']} 行 {r['date']} 窗外且第5列未注「{OUTSIDE_PREFIX}(…)」(A1)")
                if lo <= d <= hi and r["outside"]:
                    fails.append(f"[日期] 第 {r['lineno']} 行窗内但第5列非空(余档列专用 A1)")
                subj_dates.setdefault(sec_t, []).append(d)
        elif sec_k == f"reserved:{DONGTAI_HEAD}":  # v4-B③/S6b:动态区只准过去日
            if d is None:
                fails.append(f"[日期] 第 {r['lineno']} 行动态区日期列为空或不可解析:{r['date'][:20]!r}(v4-B⑤ 行号化)")
            elif d >= lo:
                fails.append(f"[日期] 第 {r['lineno']} 行动态区 {r['date']} 不早于窗口起点 {lo}(动态区只准过去日,v4-B③/S6b)")
        if sec_k == f"reserved:{SUMMARY_HEAD}":
            if d is None:
                fails.append(f"[日期] 第 {r['lineno']} 行摘要日期列为空或不可解析:{r['date'][:20]!r}(v4-B⑤ 行号化)")
            elif d > lo + dt.timedelta(days=30):
                fails.append(f"[摘要] 第 {r['lineno']} 行 {r['date']} 超起点+30 天(B8)")

        typ = r["type"]
        if sec_k == "subject" and typ not in EVENT_TYPES:
            fails.append(f"[类型] 第 {r['lineno']} 行类型 {typ!r} 不在封闭枚举(B4)")
        elif sec_k == "subject" and typ in TYPE_HINTS:
            ev = r["event"]
            hints = TYPE_HINTS[typ]
            if not any(h in ev for h in hints):
                other = next((o for o, hs in TYPE_HINTS.items()
                              if o != typ and any(h in ev for h in hs)), None)
                if other:
                    fails.append(f"[类型] 第 {r['lineno']} 行事件语义像「{other}」却填「{typ}」(B2 归错)")
        forms = anchor_forms(r["anchor"])
        if sec_k in ("subject", f"reserved:{SUMMARY_HEAD}") and not forms:
            fails.append(f"[锚] 第 {r['lineno']} 行来源锚列为空——无锚即删条(B2)")
        allowed = TYPE_ANCHORS.get(typ)
        if typ in TYPE_MUST and forms and TYPE_MUST[typ] not in forms:
            fails.append(f"[锚] 第 {r['lineno']} 行类型「{typ}」必配 {TYPE_MUST[typ]}(B8 强制,N9)")
        for f in sorted(forms):
            if f.startswith("unrecognized:"):
                fails.append(f"[锚] 第 {r['lineno']} 行锚段不属白名单:{f[13:]!r}(B2)")
            elif allowed is None or f not in allowed:
                fails.append(f"[锚] 第 {r['lineno']} 行类型「{typ}」不接受锚型 {f!r}(B8 禁 fallback)")

        if "statute" in forms:  # A3
            for seg in re.split(r"\s*\+\s*", r["anchor"].strip()):
                s = seg.strip().rstrip("。;；")
                if not s.lower().startswith("statute:"):
                    continue
                if not STATUTE_SPEC_RE.match(s):
                    fails.append(f"[锚] 第 {r['lineno']} 行 statute 锚不符《法名》第N条（要点）规格(A3/N2)")
                elif re.search(r"无条件|快报", s):
                    fails.append(f"[锚] 第 {r['lineno']} 行 statute 要点含被禁推导(快报/无条件——v2-A 撤权项,v4-B⑦/S1b)")
                elif sec_k in ("subject", f"reserved:{SUMMARY_HEAD}") and not any(
                        rec.get("kind") == "statute" and s == str(rec.get("ref", "")).strip()
                        for _, rec in recs):
                    fails.append(f"[锚] 第 {r['lineno']} 行 statute 锚无 sources kind=statute 同串承载(A3/N2)")
                if evidence_text is not None:  # v4-B⑦:法名+条号须在当场取回证据原文中匹配
                    core = re.sub(r"^statute[:：]", "", s)
                    if core and not evidence_hit(evidence_text, core):
                        fails.append(f"[证据] 第 {r['lineno']} 行 statute 锚不在 evidence 当场取回清单(断链;法名伪满/条文已删皆拦,v4-B⑦/S1)")
        if evidence_text is not None and sec_k in (
                "subject", f"reserved:{SUMMARY_HEAD}", f"reserved:{DONGTAI_HEAD}"):
            for key in anchor_keys(r["anchor"]):  # 全部锚型须证据原文匹配(v4-B:每条锚)
                probe = key
                if probe.startswith("conv_id="):
                    probe = probe.split(" ")[0]
                if probe.startswith("statute:") or probe.startswith("statute："):
                    continue  # statute 由上段 core 专检,不重复报(证据里存的是条文原文非锚前缀)
                if probe and not evidence_hit(evidence_text, probe):
                    fails.append(f"[证据] 第 {r['lineno']} 行锚 {probe[:36]!r} 在 evidence/ 无原文匹配(v4-B⑦断链)")

        if sec_k in ("subject", f"reserved:{SUMMARY_HEAD}"):
            for key in anchor_keys(r["anchor"]):
                hits = [ln for ln, rec in recs if isinstance(rec.get("ref"), str) and key in rec["ref"]]
                if not hits:
                    fails.append(f"[双向] 第 {r['lineno']} 行锚 {key[:36]!r} 在 sources 无对应(B3)")
                elif len(hits) > 1:
                    fails.append(f"[双向] 第 {r['lineno']} 行锚 {key[:36]!r} 对应多行 {hits}(歧义)")
                forward_keys.add(key)

        mh = HALLUCINATION_RE.search(r["event"] + "|" + r["status"])
        if mh:
            fails.append(f"[幻觉] 第 {r['lineno']} 行含自白词「{mh.group(0)}」——锚证事件在、不证日期(B11);改道已发生动态或不产")
        if typ not in EVENT_TYPES:
            pass  # 类型列是 A4 唯一豁免区(封闭枚举中性词)
        for col in ("event", "status", "outside", "anchor"):
            mb = BANNED_RE.search(QUOTE_TITLE_RE.sub("", r[col]))
            if mb:
                fails.append(f"[禁词] 第 {r['lineno']} 行「{col}」列命中「{mb.group(0)}」")
            bad = rating_offending(r[col])          # v4-B② 评级扫原文,《》不豁免
            if bad:
                fails.append(f"[评级] 第 {r['lineno']} 行「{col}」列含评级/目标价词「{bad}」(A4 无豁免区在列)")
            if sec_k in ("subject", f"reserved:{SUMMARY_HEAD}"):  # v4-B①/S2 前瞻账行非日期列藏日期
                for dd in DATE_RE.findall(re.sub(r"https?://\S+", "", r[col])):
                    # M51 冒烟修:URL 段先剥——路径日期(cninfo /finalpage/2026-09-08/)是取数路径非事件日期,不构成藏日期
                    if dd != r["date"]:
                        fails.append(f"[日期] 第 {r['lineno']} 行「{col}」列藏日期 {dd},与日期列 {r['date']!r} 不一致(v4-B①/S2)")


    for t_, _lv_, s0_, s1_ in sections:
        if t_.startswith("附录"):
            for i_ in range(s0_ + 1, s1_):
                if lines[i_].strip().startswith("|"):
                    fails.append(f"[保留区] 第 {i_ + 1} 行附录内出现表格行——附录只许清单,前瞻停机坪关闭(v4-B③/S5)")
                    break
    # v4-B④/S10:摘要 ⊆ 主表日期集合(按保留词定位,不认标题字面)
    main_date_set = {d.isoformat() for ds_ in subj_dates.values() for d in ds_}
    for t_, _lv_, s0_, s1_ in sections:
        if t_.startswith(SUMMARY_HEAD):
            for i_ in range(s0_ + 1, s1_):
                for dd in DATE_RE.findall(re.sub(r"https?://\S+", "", lines[i_])):  # M51:URL 路径日期不入户账比对
                    if lines[i_].strip().startswith("|") and dd not in main_date_set:
                        fails.append(f"[摘要] 第 {i_ + 1} 行 {dd} 不在主表日期集合(v4-B④/S10)")
    for t, ds in subj_dates.items():
        for i in range(len(ds) - 1):
            if ds[i] > ds[i + 1]:
                fails.append(f"[序] 节「{t[:24]}」日期降序(B8/N7)")
                break

    for ln, rec in recs:  # B7 反向:只认主体/摘要表锚列键
        ref = rec.get("ref") if isinstance(rec.get("ref"), str) else ""
        keys = anchor_keys(ref) or re.findall(r"AN\d{8,}|(?<!\d)\d{6,}(?!\d)|conv_id=\S+|https?://\S+", ref)
        if not any(k in forward_keys for k in keys):
            fails.append(f"[双向] sources 第 {ln} 行 id={rec.get('id')} 未被主体节/摘要锚列引用(附录不算,B7/N1b)")

    table_idx = {r["lineno"] - 1 for r in rows}
    for i, l in enumerate(lines):
        if i in table_idx or not l.strip() or l.strip().startswith("#") or l.strip().startswith("|"):
            continue
        stripped = QUOTE_TITLE_RE.sub("", l)
        mb = BANNED_RE.search(stripped)
        if mb:
            fails.append(f"[禁词] 第 {i + 1} 行命中「{mb.group(0)}」")
        bad = rating_offending(l)  # v4-B② 非表格区评级扫原文
        if bad and not BAN_NOTE_RE.search(stripped):
            fails.append(f"[评级] 第 {i + 1} 行含评级词「{bad}」(A4;禁令说明句除外)")
        ml = LOOSE_DATE_RE.search(DATE_RE.sub("", l))
        if ml:
            fails.append(f"[日期] 第 {i + 1} 行非标准日期写法:{ml.group(0)!r}(全篇 YYYY-MM-DD)")
    return fails, len(rows)


def main(argv=None):
    p = argparse.ArgumentParser(description="catalyst-calendar v4 机检(§v2-B+§v3-B+§v4-A/B)。--window/--sources 必传,--evidence 选传。")
    p.add_argument("calendar", help="calendar.md")
    p.add_argument("--window", default=None, help="YYYY-MM-DD~YYYY-MM-DD(必传,B6)")
    p.add_argument("--sources", default=None, help="sources.jsonl(必传,B7)")
    p.add_argument("--evidence", default=None, help="run 的 evidence/ 目录(v4-B⑦;不传=证据层跳过并打印提示)")
    args = p.parse_args(argv)
    fails, nrows = run(args)
    if fails:
        print(f"FAIL: {args.calendar}（{len(fails)} 条）")
        for f in fails:
            print(f"  - {f}")
        return 1
    print(f"PASS: {args.calendar}（§v2-B+§v3-B 全过,表行 {nrows},--window {args.window}）")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as e:  # B6:崩溃=事故,兜底成 FAIL
        print(f"FAIL: 内部异常兜底(请报 bug):{type(e).__name__}: {e}")
        sys.exit(1)
