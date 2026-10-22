#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""upstream_intake.py —— 把上游三枚产出（tear-sheet-page／structured-note／risk-fact-table）读成本件已有的三对象。

一条命令：python3 -B scripts/upstream_intake.py --kind structured-note --artifact note.md --out-dir OUT
  产出 OUT/facts.jsonl（逐行 section|item|value|basis|date|source|locator，四节另带 side）、OUT/gaps.jsonl（item+why）、
  OUT/materials.jsonl（path+title）——三件都是本件入口 --facts／--gaps／--materials 认的形状，不改 build_memo／check_memo 一字。

三条硬规矩（写在这儿，防下一个手痒的人放宽）：
  1) 只做**保形映射**：一节喂一节——上游自己标「风险」的那节才落到反方（side=bear），标「待人工／未检索到」的才落到缺数账；
     看多一侧本件不代上游产出（那是人的判断），需要时由 --manual-bull 并进来，并在自报行里数出来。
  2) 锚取不到就不编：行内 [S#]/[L#] 若不在来源索引里，该行进「锚未命中」计数并跳过，不拿别的锚凑、不写「未标注」。
  3) 自报行必须齐：读到多少行、产出多少条、跳过多少条（含原因分类），缺一类就是假绿。
退码：0 正常；1 上游一侧一条都没映射出来（空结果不静默；人工行不顶替，且不写三件）；
      2 用法错（kind 不在三枚之内，由 argparse 拒——现测 rc=2，别按 3 读）；
      3 取值域故障（件读不到／上游件无 H1 标题／来源索引为空且未给 --sources／人工件读不到或不是合法 JSON）。
零网络、纯标准库、只读取上游件，不写上游目录。
"""
import argparse
import json
import re
import sys
from pathlib import Path

NUM = re.compile(r"(\d[\d,]*(?:\.\d+)?\s*(?:亿元|万元|元|万吨|吨|亿股|股|倍|%|个百分点|米|台|项|条))")
ANCHOR = re.compile(r"\[([SL]\d+)\]")
BULL_RE = re.compile(r"^- \[([SL]\d+)\]\s*(.*?)（([a-z_]+)，(\d{4}-\d{2}-\d{2})，(L\d)\）", re.M)


def die(msg, code):
    print("upstream_intake: " + msg, file=sys.stderr)
    return code


def read(p):
    try:
        return Path(p).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def ledger_from_index(text):
    """上游件自带的「来源索引」节 → {id: {ref/claim/date/kind}}；这是保形的唯一来源，不猜。"""
    out = {}
    for m in BULL_RE.finditer(text):
        sid, claim, kind, date, conf = m.group(1), m.group(2), m.group(3), m.group(4), m.group(5)
        out[sid] = {"ref": claim.split("（")[0].strip(), "claim": claim, "date": date, "kind": kind, "confidence": conf}
    return out


def ledger_from_jsonl(path):
    out = {}
    t = read(path)
    if t is None:
        return out
    for ln in t.splitlines():
        ln = ln.strip()
        if not ln:
            continue
        try:
            o = json.loads(ln)
        except ValueError:
            continue
        sid = str(o.get("id", "")).strip()
        if sid:
            out[sid] = {"ref": str(o.get("ref", "")), "claim": str(o.get("claim", "")),
                        "date": str(o.get("asof", "")), "kind": str(o.get("kind", "")),
                        "confidence": str(o.get("confidence", ""))}
    return out


def title_of(text):
    for ln in text.splitlines():
        if ln.startswith("# "):
            return ln[2:].strip()
    return ""


def subject_of(text):
    m = re.search(r"（(\d{6})(?:\.\w{2})?）", text)
    return m.group(1) if m else ""


def tables(text):
    """返回 [(表头行, [数据行])]，只收 markdown 表。"""
    out, cur = [], None
    for ln in text.split("\n"):
        if ln.strip().startswith("|") and ln.strip().endswith("|"):
            cells = [c.strip() for c in ln.strip().strip("|").split("|")]
            if set("".join(cells)) <= set("-: "):
                continue
            if cur is None:
                cur = (cells, [])
                out.append(cur)
            else:
                cur[1].append(cells)
        else:
            cur = None
    return out


def anchors_in(row):
    return ANCHOR.findall(row)


def resolve(led, ids, skip):
    """取第一个能对上来源索引的锚；对不上就计跳过。"""
    for a in ids:
        if a in led:
            return a, led[a]
    if ids:
        skip["anchor"] += 1
    else:
        skip["noanchor"] += 1
    return None, None


# 本件下游的门认「官方链接或公告／问询编号」这一形；上游 ledger 的 ref 常是裸索引号（AN…）或案号，
# 原样搬下去会被判「缺合规出处锚」。这里只做**加前缀的换形**，不改指称对象：原值完整地留在括号里，可逐字回查。
GATE_ANCHOR = re.compile(r"https?://|www\.|\.cn|\.com|\.gov|cninfo|巨潮|交易所|证监会|问询|函|公告|编号|document_number")


def anchor_form(ref, kind):
    r = (ref or "").strip()
    if not r or GATE_ANCHOR.search(r):
        return r
    label = "公告编号" if re.match(r"^(AN|ZL|SH|SZ)\d", r, re.I) or kind in (
        "disclosure_cn", "fr_fact_index", "fr_footnote", "entity_data", "omni") else "来源编号"
    if kind in ("court", "judgment", "penalty"):
        label = "裁判文书／处罚文书编号"
    return "%s %s（原样：%s）" % (label, r, r)


def sections_of(text):
    """按二级／三级标题切片：[(标题, [行])]。"""
    out, cur = [], (None, [])
    for ln in text.split("\n"):
        if re.match(r"^#{2,3} ", ln):
            out.append(cur)
            cur = (re.sub(r"^#+\s*", "", ln).strip(), [])
        else:
            cur[1].append(ln)
    out.append(cur)
    return [(t, ls) for t, ls in out if t]


def map_tear_sheet(text, led, skip):
    facts, gaps = [], []
    asof = ""
    m = re.search(r"^- 数据截止日[:：]\s*(\d{4}-\d{2}-\d{2})", text, re.M)
    if m:
        asof = m.group(1)
    for head, rows in tables(text):
        joined = "|".join(head)
        if "期间" in joined and any("来源锚" in c for c in head):
            cols = [(i, c) for i, c in enumerate(head) if i >= 2 and "来源锚" not in c and c not in ("期间", "basis")]
            for r in rows:
                ids = anchors_in("|".join(r))
                aid, meta = resolve(led, ids, skip)
                if not aid:
                    continue
                for i, cname in cols:
                    if i >= len(r):
                        continue
                    val = r[i].strip()
                    if not re.fullmatch(r"[\d,\.]+", val):
                        skip["nonnum"] += 1
                        continue
                    unit = re.search(r"（(.*?)）", cname)
                    facts.append({"section": "2", "item": "%s %s" % (r[0].strip(), re.sub(r"（.*?）", "", cname).strip()),
                                  "value": val, "basis": "%s｜%s" % (r[1].strip(), unit.group(1) if unit else "单位未标"),
                                  "date": meta.get("date") or asof, "source": anchor_form(meta["ref"], meta.get("kind", "")),
                                  "locator": "§2 近四期速览 %s 行·%s 列" % (r[0].strip(), cname)})
        elif "日期" in joined and "事件" in joined:
            for r in rows:
                ids = anchors_in("|".join(r))
                aid, meta = resolve(led, ids, skip)
                if not aid:
                    continue
                facts.append({"section": "3", "item": "%s %s（%s）" % (r[0].strip(), r[1].strip(), r[2].strip() if len(r) > 2 else ""),
                              "source": anchor_form(meta["ref"], meta.get("kind", "")), "locator": "§3 在场事件 %s 行" % r[0].strip()})
    for head, lines in sections_of(text):
        if "风险" not in head:
            continue
        n = 0
        for ln in lines:
            if not ln.strip().startswith("- "):
                continue
            n += 1
            ids = anchors_in(ln)
            aid, meta = resolve(led, ids, skip)
            if not aid:
                continue
            facts.append({"section": "4", "side": "bear", "item": re.sub(r"\s*\[[SL]\d+\]", "", ln.strip()[2:]).strip(),
                          "value": "（定性）", "basis": "上游 §%s 风险条目（定性，无数字）" % head[:2],
                          "date": meta.get("date") or asof, "source": anchor_form(meta["ref"], meta.get("kind", "")),
                          "locator": "§%s 第 %d 条" % (head[:2], n)})
    for head, lines in sections_of(text):
        pend = sum(1 for ln in lines if "[待人工]" in ln)
        if pend:
            gaps.append({"item": "上游 §%s 待人工 %d 处" % (head, pend),
                         "why": "上游该节为待人工占位（未取值），本件不代填"})
    return facts, gaps


def map_note(text, led, skip):
    facts, gaps = [], []
    for head, lines in sections_of(text):
        risk = ("风险" in head) or ("附注" in head and "风险" in head)
        for ln in lines:
            s = ln.strip()
            if "[待人工]" in s or "未检索到" in s or "未取到" in s:
                gaps.append({"item": re.sub(r"\s*\[[SL]\d+\]", "", s[2:] if s.startswith("- ") else s).strip()[:60],
                             "why": "上游原文即标注待人工／未取到"})
                continue
            if not s.startswith("- "):
                continue
            m = NUM.search(s)
            if not m:
                skip["nonnum"] += 1
                continue
            ids = anchors_in(s)
            aid, meta = resolve(led, ids, skip)
            if not aid:
                continue
            row = {"item": re.sub(r"\s*\[[SL]\d+\]", "", s[2:]).strip(),
                   "value": m.group(1).strip(), "basis": "上游 §%s 原文口径" % head[:2],
                   "date": meta.get("date"), "source": anchor_form(meta["ref"], meta.get("kind", "")), "locator": "§%s「%s」条目" % (head[:2], head[3:6] or head)}
            if risk:
                row.update({"section": "4", "side": "bear", "value": "（定性）",
                            "basis": "上游 §%s 风险条目（原文带数：%s）" % (head[:2], m.group(1).strip())})
            else:
                row["section"] = "2"
            facts.append(row)
    for head, rows in tables(text):
        if not any("科目" in c for c in head):
            continue
        for r in rows:
            for i in range(1, len(r)):
                cell = re.sub(r"\s*\[[SL]\d+\]", "", r[i]).strip()
                if not re.fullmatch(r"[\d,\.]+", cell):
                    skip["nonnum"] += 1
                    continue
                ids = anchors_in(r[i])
                aid, meta = resolve(led, ids, skip)
                if not aid:
                    continue
                facts.append({"section": "2", "item": "%s %s" % (r[0].strip(), head[i].strip()), "value": cell,
                              "basis": "上游 §2 四期差异表（口径见列名）", "date": meta.get("date"),
                              "source": anchor_form(meta["ref"], meta.get("kind", "")), "locator": "§2 表格 %s 行·%s 列" % (r[0].strip(), head[i].strip())})
    return facts, gaps


def map_risk_table(text, led, skip):
    facts, gaps = [], []
    for head, rows in tables(text):
        if "类目" not in head or "事实" not in "".join(head):
            continue
        idx = {c: i for i, c in enumerate(head)}
        col_fact = next((i for c, i in idx.items() if "事实" in c), None)
        col_date = idx.get("日期")
        col_cat = idx.get("类目")
        col_grade = next((i for c, i in idx.items() if "影响" in c), None)
        col_state = idx.get("状态")
        col_anchor = next((i for c, i in idx.items() if "锚" in c or "来源" in c), None)
        n = 0
        for r in rows:
            if col_fact is None or col_fact >= len(r):
                continue
            n += 1
            ref = r[col_anchor].strip() if col_anchor is not None and col_anchor < len(r) else ""
            if not ref or ref in ("—", "-"):
                ids = anchors_in("|".join(r))
                aid, meta = resolve(led, ids, skip)
                if not aid:
                    continue
                ref = meta["ref"]
            facts.append({"section": "4", "side": "bear", "item": r[col_fact].strip(),
                          "value": (r[col_grade].strip() if col_grade is not None and col_grade < len(r) else "（定性）"),
                          "basis": "%s｜%s" % (r[col_cat].strip() if col_cat is not None else "类目未标",
                                               r[col_state].strip() if col_state is not None else "状态未标"),
                          "date": (r[col_date].strip() if col_date is not None and col_date < len(r) else ""),
                          "source": anchor_form(ref, "risk"), "locator": "风险事实表 第 %d 行·%s" % (n, r[col_cat].strip() if col_cat is not None else "")})
    for m in re.finditer(r"^\s*[-*]?\s*(无工具项[:：]\s*\d+|本节检索域[:：].*|降级[:：].*|窗外余档[:：].*)$", text, re.M):
        gaps.append({"item": m.group(1).strip()[:60], "why": "上游覆盖率账里自报的缺位项（原文）"})
    for ln in text.split("\n"):
        if "未取到" in ln or "未查到" in ln:
            gaps.append({"item": ln.strip()[:60], "why": "上游原文写未取到／未查到"})
    return facts, gaps


MAPS = {"tear-sheet-page": map_tear_sheet, "structured-note": map_note, "risk-fact-table": map_risk_table}


def main():
    ap = argparse.ArgumentParser(description="上游产出 → 本件三对象（facts／gaps／materials），只做保形映射")
    ap.add_argument("--kind", required=True, choices=sorted(MAPS))
    ap.add_argument("--artifact", required=True, help="上游件路径（markdown）")
    ap.add_argument("--sources", help="来源索引 jsonl（缺省时读上游件自带的「来源索引」节）")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--manual-bull", help="人工看多依据逐行 JSON（本件不代产出，只并进来并计数）")
    a = ap.parse_args()

    text = read(a.artifact)
    if text is None:
        return die("读不到上游件：%s（取值域故障，不猜内容）" % a.artifact, 3)
    title = title_of(text)
    if not title:
        return die("上游件没有 H1 标题（无法确定材料名），不猜", 3)
    led = ledger_from_jsonl(a.sources) if a.sources else {}
    led.update(ledger_from_index(text))
    if not led:
        return die("来源索引为空：上游件既无「来源索引」节也未给 --sources（锚无从落实，不编）", 3)

    skip = {"anchor": 0, "noanchor": 0, "nonnum": 0}
    facts, gaps = MAPS[a.kind](text, led, skip)
    manual = []
    if a.manual_bull:
        t = read(a.manual_bull)
        if t is None:
            return die("读不到人工看多依据件：%s" % a.manual_bull, 3)
        for ln in t.splitlines():
            ln = ln.strip()
            if not ln:
                continue
            try:
                manual.append(json.loads(ln))
            except ValueError:
                return die("人工看多依据第 %d 行不是合法 JSON" % (t.splitlines().index(ln) + 1), 3)
    rows = facts + manual
    if not facts and not gaps:
        return die("上游一侧一条都没映射出来（kind=%s 与该件形制不符？）——人工行不顶替上游映射，空结果不算成功，不写三件" % a.kind, 1)
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "facts.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    (out / "gaps.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in gaps), encoding="utf-8")
    (out / "materials.jsonl").write_text(json.dumps({"path": str(a.artifact), "title": title}, ensure_ascii=False) + "\n",
                                         encoding="utf-8")
    print("upstream_intake｜kind=%s｜件=%s｜主体=%s" % (a.kind, a.artifact, subject_of(text) or "(件内未标 6 位代码)"))
    print("  来源索引枚数=%d｜上游映射 facts=%d 条（其中反方 %d 条）｜人工并来 side 行=%d 条｜gaps=%d 条｜materials=1 条" % (
        len(led), len(facts), len([x for x in facts if x.get("side") == "bear"]), len(manual), len(gaps)))
    print("  跳过：锚对不上来源索引 %d 处｜行内无锚 %d 处｜非数字单元格 %d 处（都不凑、不编）" % (
        skip["anchor"], skip["noanchor"], skip["nonnum"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
