#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_brief.py — 校一份「中文多源研究速览」是否合 `SKILL.md` §3 四节契约与 §5 红线。

用法：
    python3 check_brief.py <速览.md>        校一份速览（纯标准库、零网络、不发任何请求）
    python3 check_brief.py --selftest       跑包内夹具：好样必须过，四枚坏样必须各发它该发的那一道
    python3 check_brief.py --help            本说明

出口形制（与套件姊妹件同族）：
    失败 = 一行 "FAIL: <文件>（N 条）"，其下每条详行先打错误码前缀（四枚 E-* 之一），道名后是行号与该道规格；
           末行 "码表:" 只列本次真正用到的码与含义。
    全过 = 一行 "PASS: <文件>（…）"，并印「扫过 N 行」与四道计数——计数说看到多少，不说猜多少。

四道是什么（判定全集在本脚本，本文只指路，不复述细节）：
    道一 形制：头部四件自标逐字在位＋四节齐且按一二三四有序＋一句话结论非空非占位
    道二 锚：每条发现行行末带 [S#]，且该编号在第四节有对应行；第四节每行必须同时带 URL 与 YYYY-MM-DD 检索日
    道三 红线：评级／目标价／买卖与走势类断言一律零命中，要写只能同行挂 [待人工]；改数词（约／左右／大概）不得替数字打底
    道四 未取到与计数：正文写了「未取到／未检索到」的，第三节必须逐条点名它；第四节一行来源都没有＝没有出处

退码：0 全过；1 有发条（详行逐条给码、道名、行号与规格）；2 用法错；3 取值域故障（文件读不到，不读成「零违例」）。
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SECTIONS = ('一句话结论', '逐条发现', '未取到与口径', '来源')
MARKS = ('AI 整理初稿', '请回原文核对', '不构成投资建议', '判断位 [待人工]')
URL_RE = re.compile(r'https?://|www\.[A-Za-z0-9.-]+')
DATE_RE = re.compile(r'\d{4}-\d{2}-\d{2}')
ANCHOR_RE = re.compile(r'\[S(\d+)\]\s*$')
MISS_RE = re.compile(r'未取到|未检索到')
PLACEHOLDER_RE = re.compile(r'^\s*(（[^）]*）)?[—\-–]\s*$|待定|待填|TBD|<[^>]*>$')
BANNED = re.compile(r'买入|卖出|建仓|清仓|加仓|目标价|止盈|止损|必涨|必跌|稳赚|无风险|强烈建议|建议持有|翻倍|跑赢大盘')
HEDGE = re.compile(r'约\s*[\d０-９]|左右|大概|大约')
CODES = {'E-FORMAT': '道一 形制', 'E-ANCHOR': '道二 锚', 'E-BANWORD': '道三 红线', 'E-COVERAGE': '道四 未取到与计数'}


def scan(path: Path):
    issues = []
    seen = set()

    def add(code, lane, line_no, msg):
        key = (code, line_no, msg)
        if key not in seen:
            seen.add(key)
            issues.append((code, lane, line_no, msg))

    lines = path.read_text(encoding='utf-8', errors='replace').split('\n')

    head = '\n'.join(lines[:next((i for i, ln in enumerate(lines) if ln.startswith('## ')), len(lines))])
    for need in MARKS:
        if need not in head:
            add('E-FORMAT', '头部', 1, f"头部自标缺『{need}』（规格：四件逐字齐，写在第一个「## 」之前）")

    idxs = []
    for n, name in enumerate(SECTIONS, 1):
        hit = [i for i, ln in enumerate(lines) if re.match(rf'^##\s*{n}、{re.escape(name)}\s*$', ln)]
        if not hit:
            add('E-FORMAT', '四节', 1, f"缺「## {n}、{name}」段（规格：四节齐且按一二三四有序）")
        else:
            idxs.append((n, hit[0]))
    if len(idxs) > 1 and [n for n, _ in idxs] != sorted(n for n, _ in idxs):
        add('E-FORMAT', '四节', idxs[0][1] + 1, '四节次序与契约不一致（规格：一二三四有序）')
    bounds = {}
    for pos, (n, i0) in enumerate(idxs):
        i1 = idxs[pos + 1][1] if pos + 1 < len(idxs) else len(lines)
        bounds[n] = (i0, i1)

    if 1 in bounds:
        i0, i1 = bounds[1]
        body = [ln for ln in lines[i0 + 1:i1] if ln.strip() and not ln.startswith('#')]
        if not body:
            add('E-FORMAT', '结论', i0 + 1, '一句话结论留空（规格：至少一行实句，不留占位）')
        elif any(PLACEHOLDER_RE.search(ln) for ln in body):
            add('E-FORMAT', '结论', i0 + 1 + body.index(next(ln for ln in body if PLACEHOLDER_RE.search(ln))),
                '一句话结论仍是占位（规格：写成可核的实句；判断走第六位的 [待人工]，不靠占位）')

    anchors_used, rows_without = [], []
    if 2 in bounds:
        i0, i1 = bounds[2]
        for i in range(i0 + 1, i1):
            ln = lines[i]
            if not ln.strip().startswith(('-', '*', '|')):
                continue
            m = ANCHOR_RE.search(ln.strip())
            if not m:
                rows_without.append(i + 1)
                add('E-ANCHOR', '锚', i + 1, '发现行行末没有 [S#] 锚（规格：每条发现一行、行末带一个锚；没有锚就不要写进这一节）')
            else:
                anchors_used.append((int(m.group(1)), i + 1))
        for i in range(i0 + 1, i1):
            if HEDGE.search(lines[i]):
                add('E-BANWORD', '改数', i + 1, f"命中改数词「{HEDGE.search(lines[i]).group(0)}」（规格：数值要么照来源写，要么落第三节写未取到，不用约／左右打底）")

    listed = set()
    if 4 in bounds:
        i0, i1 = bounds[4]
        rows = [ln for ln in lines[i0 + 1:i1] if ln.strip().startswith(('-', '*'))]
        if not rows:
            add('E-COVERAGE', '来源', i0 + 1, '第四节一行来源都没有（规格：速览的价值就在这一节，空节等于没有出处）')
        for k, ln in enumerate(rows, 1):
            m = re.match(r'^[-*]\s*\[S(\d+)\]', ln.strip())
            if not m:
                add('E-ANCHOR', '来源', i0 + 1 + lines[i0 + 1:i1].index(ln) + 1,
                    f'来源第 {k} 行不以 [S#] 开头（规格：编号与正文锚一一对应）')
            else:
                listed.add(int(m.group(1)))
            if not URL_RE.search(ln):
                add('E-ANCHOR', '来源', i0 + 1 + lines[i0 + 1:i1].index(ln) + 1,
                    f'来源 [S{m.group(1) if m else k}] 缺 URL（规格：逐条可回查——域名或链接原样写进同一行）')
            if not DATE_RE.search(ln):
                add('E-ANCHOR', '来源', i0 + 1 + lines[i0 + 1:i1].index(ln) + 1,
                    f'来源 [S{m.group(1) if m else k}] 缺检索日 YYYY-MM-DD（规格：多源速览的时效以检索日为凭）')
    else:
        listed = set()
    for num, ln_no in anchors_used:
        if num not in listed:
            add('E-ANCHOR', '锚', ln_no, f'锚 [S{num}] 在第四节没有对应行（规格：正文用的每个编号都要能回到来源行）')

    for i, ln in enumerate(lines, 1):
        m = BANNED.search(ln)
        if m and '[待人工]' not in ln:
            add('E-BANWORD', '判断词', i, f"命中「{m.group(0)}」（规格：评级／目标价／买卖与走势类断言本件不产出；要写就同行挂 [待人工]，或改中性陈述）")

    if 3 in bounds:
        i0, i1 = bounds[3]
        sec3 = '\n'.join(lines[i0 + 1:i1])
        misses = [ln.strip() for ln in lines if MISS_RE.search(ln) and not ln.strip().startswith('#')]
        for ln in misses:
            if '未取到' not in sec3 and '未检索到' not in sec3:
                add('E-COVERAGE', '未取到', lines.index(ln) + 1, '正文写了未取到／未检索到，但第三节整节没有点名（规格：没列就是没说——缺数要么逐条列要么压根不写这两种话）')
                break
    return issues, lines


def run_one(path: Path, quiet=False):
    issues, lines = scan(path)
    codes = sorted({c for c, _, _, _ in issues})
    if not quiet:
        for code, lane, no, msg in issues:
            print(f"  [{code}] [{lane}] 第 {no} 行：{msg}")
    counts = {}
    for code, _, _, _ in issues:
        counts[code] = counts.get(code, 0) + 1
    if issues:
        print(f'FAIL: {path.name}（{len(issues)} 条）')
        print('       ' + '；'.join(f'{CODES[c]} {n} 条' for c, n in sorted(counts.items())))
        print('       码表: ' + '；'.join(f'{c}={CODES[c]}' for c in codes))
        return 1, len(issues), counts
    print(f'PASS: {path.name}（四节齐、自标在位、每条发现带可回锚、来源行齐 URL 与检索日、判断词零命中、未取到逐条点名）')
    print(f'       扫过 {len(lines)} 行，发条 0 条；判定与阈值全集以本脚本现值为准（--help 看四道说明）')
    return 0, 0, {}


def selftest():
    fx = Path(__file__).resolve().parent / 'fixtures'
    cases = [('good-brief.md', 0, None),
             ('bad-no-anchor.md', 1, 'E-ANCHOR'),
             ('bad-missing-section.md', 1, 'E-FORMAT'),
             ('bad-rating-word.md', 1, 'E-BANWORD'),
             ('bad-unsourced.md', 1, 'E-COVERAGE')]
    bad = 0
    for name, want_rc, want_code in cases:
        p = fx / name
        if not p.is_file():
            print(f'  selftest 取值域故障：夹具不在场 {name}')
            return 3
        import io
        import contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc, n, counts = run_one(p, quiet=True)
        detail = buf.getvalue()
        if rc != want_rc:
            print(f'  不合 {name}：期望退码 {want_rc}，实发 {rc}')
            bad += 1
            continue
        if want_code and want_code not in detail:
            print(f'  不合 {name}：期望发码 {want_code}，实发详行不含它')
            bad += 1
            continue
        if want_code is None and bad == 0 and rc == 0:
            print(f'  ok   {name}（退码 {rc}·发条 {n}）')
        elif want_code:
            print(f'  ok   {name}（退码 {rc}·发条 {n}·实发 {want_code}）')
    print('selftest: ' + ('ALL GREEN（好样 1 枚·坏样四道 4/4）' if bad == 0 else f'{bad} 条不合期望'))
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser(prog='check_brief.py', add_help=False,
                                 description='校一份中文多源研究速览（四道，见 --help 正文）')
    ap.add_argument('target', nargs='?')
    ap.add_argument('--selftest', action='store_true', help='跑包内夹具（好样须过、四枚坏样须各发红）')
    ap.add_argument('--quiet', action='store_true', help='只报末行')
    ap.add_argument('-h', '--help', action='store_true', help='本说明')
    a = ap.parse_args()
    if a.help or (not a.target and not a.selftest):
        print(__doc__)
        return 0 if a.help else 2
    if a.selftest:
        return selftest()
    p = Path(a.target)
    if not p.is_file():
        print(f'取值域故障：读不到速览文件 {p}（不当「零违例」读）')
        return 3
    rc, _, _ = run_one(p, quiet=a.quiet)
    return rc


if __name__ == '__main__':
    sys.exit(main())
