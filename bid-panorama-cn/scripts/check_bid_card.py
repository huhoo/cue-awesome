#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_bid_card.py — 招投标披露全景卡的机检（零网络、只读本包外传入的文件）。

五道码（缺一即不叫过闸）：
  BP-STRUCT 五段齐：头部申报／八项逐字速读／口径对照／缺数清单／待人工，任一节缺失即发；
            八项名目另须在「逐字速读」段内**行级在场**——每枚名目一行以「- 名目：」起头，只在散文里提到不算占行；
  BP-QUOTE  每项原句与锚：项行的书名号（「」『』«»）内原句不得为空或只剩单字；「锚：」标签在而锚值为空同样发；
  BP-LINE   红线断言：中标概率／必中标／稳赚／零风险／保证收益／利好／建议投标／代客投标／陪标／围标／串通报价／
            利益输送，以及判断式三族——异议…成立／目标价／评级上调下调／收入（营收）增加·上升·提升·减少·下滑，
            只允许出现在带 [待人工] 的行里，否则发（这类结论本件一律不自判）；
  BP-COUNT  齐缺申报恰一枚：头部「共八项·缺 N 项」只准出现一处（两处并存即发），且 N 必须等于速读段里
            「未检索到」的项行数；把「未检索到」写成「无该项／没有此项」一律发；
  BP-AMT    中标金额只认该项原句：「中标候选人及金额」一项，凡未写「未检索到」的，其书名号原句里必须带
            中标／投标报价／成交口径的金额数字（亿元／万元／元）——预算、概算等其它款项的数不顶中标账；
            「详见…」「以合同为准」「另行确定」「金额待定」属空泛语，出现即发，且不因原句夹带其它数字而过闸。

用法：
  python3 -B scripts/check_bid_card.py <待检文件>      # 逐条发红，全过则 PASS
  python3 -B scripts/check_bid_card.py --selftest      # 好样须过、坏样五道齐发、八形钉阈各钉一档、临时件自清
  python3 -B scripts/check_bid_card.py --help
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

ITEMS = ("项目名称与编号", "招标人与代理机构", "开标时间与方式", "评标标准与方法",
         "中标候选人及金额", "中标公示与日期", "合同履约与期限", "异议与质疑渠道")
AMT_ITEM = "中标候选人及金额"
ITEM = re.compile(r"^\s*[-*]\s*(" + "|".join(map(re.escape, ITEMS)) + r")[：:]")
TITLE = re.compile(r"[「『«][^」』»]+[」』»]")
ANCHOR_VAL = re.compile(r"锚[:：]\s*(\S.*)$")
BANNED = re.compile(r"中标概率|必中标|稳赚|零风险|保证收益|利好|建议投标|代客投标|陪标|围标|串通报价|利益输送"
                    r"|异议[^，。；、」』]{0,6}成立|目标价|评级上调|评级下调|(?:收入|营收)[^，。；、」』]{0,8}?(?:增加|上升|提升|减少|下滑)")
PENDING = re.compile(r"\[待人工\]")
DECL = re.compile(r"共\s*(?:八|8)\s*项\s*[·：:|｜、]\s*缺\s*(\d+)\s*项")
EMPTY_LIE = re.compile(r"(?:^|[\s：:])无(?:该项|此项)|没有(?:该项|此项)")
AMT_NUM = re.compile(r"(?:中标|投标报价|投标|成交|报价|合同价?)\D{0,8}?\d[\d,\.]*\s*(?:亿元|万元|元)")
AMT_VAGUE = re.compile(r"详见[^，。]*|以合同为准|另行确定|金额待定|待定")
CORE_STRIP = re.compile(r"[\s\u3000「」『』«»“”（）()《》【】，,。.；;：:、！!？~\-—_·/％%*#]+")
SECTIONS = (("头部申报", r"头部申报"), ("八项逐字速读", r"逐字速读|八项速读"),
            ("口径对照", r"口径对照"), ("缺数清单", r"缺数清单"), ("待人工", r"待人工"))
SPEED_HEAD = re.compile(r"^#{1,4}.*(?:逐字速读|八项速读)")
ANY_HEAD = re.compile(r"^#{1,4}\s")


def core_len(s: str) -> int:
    return len(CORE_STRIP.sub("", s))


def speed_zone(lines: list[str]) -> range:
    start = None
    for i, ln in enumerate(lines):
        if SPEED_HEAD.match(ln):
            start = i + 1
            break
    if start is None:
        return range(0, len(lines))
    end = len(lines)
    for j in range(start, len(lines)):
        if ANY_HEAD.match(lines[j]):
            end = j
            break
    return range(start, end)


def check_text(text: str) -> list[tuple[str, int, str]]:
    """返回 [(码, 行号, 说明)]；行号 0＝整档级判据。"""
    hits: list[tuple[str, int, str]] = []
    lines = text.splitlines()
    for name, pat in SECTIONS:
        if not re.search(pat, text):
            hits.append(("BP-STRUCT", 0, f"缺段：{name}"))
    zone = speed_zone(lines)
    seen = {}
    for i in zone:
        ln = lines[i]
        m = ITEM.match(ln)
        if not m:
            continue
        name = m.group(1)
        seen.setdefault(name, i + 1)
        if "未检索到" not in ln:
            if not TITLE.search(ln):
                hits.append(("BP-QUOTE", i + 1, f"缺项原句：{name} 那一行没有书名号内的原文"))
            elif any(core_len(q) <= 1 for q in re.findall(r"[「『«]([^」』»]*)[」』»]", ln)):
                hits.append(("BP-QUOTE", i + 1, f"原句占位：{name} 那一行的书名号内为空或只剩单字"))
            mv = ANCHOR_VAL.search(ln)
            if not mv or core_len(mv.group(1)) == 0:
                hits.append(("BP-QUOTE", i + 1, f"锚值为空：{name} 那一行的「锚：」后面没有来源定位"))
            if name == AMT_ITEM:
                segs = re.findall(r"[「『«]([^」』»]*)[」』»]", ln)
                clause = " ".join(segs) if segs else re.sub(r"^\s*[-*]\s*[^：:]+[：:]\s*", "", re.split(r"锚[:：]", ln, 1)[0])
                if AMT_VAGUE.search(clause):
                    hits.append(("BP-AMT", i + 1, f"中标金额以空泛语顶替：{name} 原句出现「详见…／以合同为准／另行确定／金额待定」——同句另有其它款项的数字也不顶中标账，空泛语不带数豁免"))
                elif not AMT_NUM.search(clause):
                    hits.append(("BP-AMT", i + 1, f"中标金额无数字原值：{name} 原句里没有中标／投标报价口径的金额数字（预算、概算等其它款项金额不顶账）"))
    for name in ITEMS:
        if name not in seen:
            hits.append(("BP-STRUCT", 0, f"缺项行：{name} 在逐字速读段里没有以「- 名目：」起头的行"))
    pending_items = sum(1 for i in zone if ITEM.match(lines[i]) and "未检索到" in lines[i])
    decls = DECL.findall(text)
    if len(decls) > 1:
        hits.append(("BP-COUNT", 0, f"齐缺申报出现 {len(decls)} 处：只准一枚，两处并存即口径不唯一"))
    elif len(decls) == 1 and int(decls[0]) != pending_items:
        hits.append(("BP-COUNT", 0, f"齐缺申报与清单不对账：申报缺 {decls[0]} 项∥速读段实有 {pending_items} 行「未检索到」"))
    elif not decls:
        hits.append(("BP-COUNT", 0, "头部缺「共八项·缺 N 项」申报，无从对账"))
    for i, ln in enumerate(lines, 1):
        if BANNED.search(ln) and not PENDING.search(ln):
            hits.append(("BP-LINE", i, "红线断言词出现在没有 [待人工] 的行"))
        if EMPTY_LIE.search(ln):
            hits.append(("BP-COUNT", i, "把「未检索到」写成「无／没有」"))
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
    good = here / "fixtures" / "good-bid-card.md"
    bad = here / "fixtures" / "bad-bid-card.md"
    rows = []
    gt = good.read_text(encoding="utf-8")
    gh = check_text(gt)
    rows.append(("好样须过（发条 0）", not gh, f"实发 {len(gh)} 条"))
    bt = bad.read_text(encoding="utf-8")
    bh = check_text(bt)
    codes = {c for c, _, _ in bh}
    rows.append(("坏样五道齐发", {"BP-STRUCT", "BP-QUOTE", "BP-LINE", "BP-COUNT", "BP-AMT"} <= codes,
                 "实发码 " + "∥".join(sorted(codes))))
    tmp = make_tmp("check-bid-")
    stripped = tmp / "no-anchor.md"
    stripped.write_text(re.sub(r"锚[:：][^\n]*", "锚：", gt), encoding="utf-8")
    sh = check_text(stripped.read_text(encoding="utf-8"))
    rows.append(("反证·剥锚必发 BP-QUOTE", any(c == "BP-QUOTE" for c, _, _ in sh), f"实发 {len(sh)} 条"))
    nproof = 1
    pin = make_tmp("check-bid-pin-")
    tiers = (
        ("钉阈·名目只剩散文必发 BP-STRUCT",
         gt.replace("- 异议与质疑渠道：", "异议与质疑渠道在公告另有说明，", 1),
         "缺项行：异议与质疑渠道"),
        ("钉阈·书名号内单字必发 BP-QUOTE",
         gt.replace("「市政道路改造工程（招标编号：ZB-2026-0312）」", "「项」", 1),
         "原句占位"),
        ("钉阈·齐缺申报改数必发 BP-COUNT",
         gt.replace("共八项·缺 1 项", "共八项·缺 0 项", 1),
         "齐缺申报与清单不对账"),
        ("钉阈·中标金额写成详见公告必发 BP-AMT",
         gt.replace("「第一中标候选人某建设集团，投标报价 8,600 万元」", "「中标金额详见公告」", 1),
         "中标金额以空泛语顶替"),
        ("钉阈·预算金额洗中标额（带空泛语）必发 BP-AMT",
         gt.replace("「第一中标候选人某建设集团，投标报价 8,600 万元」",
                    "「项目预算 2 亿元，中标金额以合同为准」", 1),
         "中标金额以空泛语顶替"),
        ("钉阈·预算金额洗中标额（不带空泛语）必发 BP-AMT",
         gt.replace("「第一中标候选人某建设集团，投标报价 8,600 万元」",
                    "「项目预算 2 亿元，最终数额在合同阶段明确」", 1),
         "中标金额无数字原值"),
        ("钉阈·红线词落在非待人工行必发 BP-LINE",
         gt.replace("｜附件腿：未发起", "｜附件腿：未发起｜中标概率高", 1),
         "红线断言词出现在没有 [待人工] 的行"),
        ("钉阈·判断式结论行必发 BP-LINE",
         gt.replace("## 二、八项逐字速读",
                    "- 结论：异议必然成立，目标价上调，项目收入将增加。\n\n## 二、八项逐字速读", 1),
         "红线断言词出现在没有 [待人工] 的行"),
    )
    for n, (name, text, needle) in enumerate(tiers, 1):
        nproof += 1
        p = pin / f"pin-{n}.md"
        p.write_text(text, encoding="utf-8")
        ph = check_text(p.read_text(encoding="utf-8"))
        fired = [m for c, _, m in ph if needle in m]
        injected = text != gt
        rows.append((name, injected and bool(fired),
                     f"注入{'生效' if injected else '作废'}·实发 {len(ph)} 条·命中句 "
                     + ("∥".join(fired) if fired else "无")))
    made = [p.name for p in TMP_ROOTS]
    root = pathlib.Path(tempfile.gettempdir())
    for p in TMP_ROOTS:
        shutil.rmtree(p, ignore_errors=True)
    leftover = sorted(q.name for q in root.iterdir() if q.name.startswith("check-bid-")) if root.is_dir() else []
    rows.append(("临时根自清（跑后不增）", not leftover,
                 f"本次建 {len(made)} 枚·跑后残留 {len(leftover)} 枚"))
    bad_rows = [r for r in rows if not r[1]]
    for name, ok, detail in rows:
        print(f"  {'ok  ' if ok else 'FAIL'} {name}｜{detail}")
    print(f"selftest: {'ALL GREEN' if not bad_rows else 'FAIL'}（好样 1 枚·坏样五道·反例 {nproof} 枚·临时根 {len(TMP_ROOTS)} 枚自清）")
    return 0 if not bad_rows else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="招投标披露全景卡五道机检（零网络）")
    ap.add_argument("target", nargs="?", help="待检文件（本件不读网络、不读目录）")
    ap.add_argument("--selftest", action="store_true", help="好样须过、坏样五道齐发、八形钉阈各钉一档、临时件自清")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not a.target:
        print("用法：check_bid_card.py <待检文件> | --selftest", file=sys.stderr)
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