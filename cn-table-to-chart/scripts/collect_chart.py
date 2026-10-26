#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""collect_chart.py — 离线采集器：读一份含表的正文，把表里的数逐字搬成四节骨架（不代选图型、不代判要点）。

用法：
    python3 -B scripts/collect_chart.py --source 那份表.md [--out 图与要点.md] [--asof YYYY-MM-DD] [--max-rows 10]
    python3 -B scripts/collect_chart.py --help

它做什么：
    只读盘上那份文件（解析通道取回的正文或已有文件），认出 markdown 表格行与其中的数值格，
    把每一行的**首个行首标签＋该行数值**逐字搬进第二节，自带两枚定位（最近前驱页标 ＋ 文件:行号）；
    第一节留四件规格待核位；第三节按四类限度各留一个待核位；第四节登记来源与解析日。
它不做什么：
    不代选图型（选哪种图取决于你想看清的关系，机器按列形状猜会把「能画」说成「该这么画」）、
    不代写读表要点（要点要读语义）、不算同比/环比/占比/平均——要算就交给宿主或电子表格，本件只核在场与一致、
    不出投资建议、不判评级与目标价、不发请求、不执行表里提到的任何程序。

骨架按设计发红：第一节四件规格是待核位，机检在道一 E-FORMAT 发条——那是「还没人选图型」的记号，不是待补的疏漏。
退码：0 骨架落成；1 表里认不出任何数值行（没有可搬的对象，不出骨架）；3 取值域故障（文件读不到、--asof 形制不对）。
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path

ROW_RE = re.compile(r'^\s*\|(.+)\|\s*$')
NUM_RE = re.compile(r'(?<![\d.])[-+]?\d[\d.,]*\s*(?:%|亿元|万元|元|个百分点|天|倍|人|台|吨)?(?![\d])')
PAGE_RE = re.compile(r'第\s*(\d+)\s*页')
SPEC_KEYS = ('图型', '横轴', '纵轴', '序列')
LIMIT_KINDS = ('缺格与空值', '合并格与跨列表头', '单位与口径', '表外推与未读到')


def nearest_page(lines, idx):
    page = None
    for i in range(0, idx):
        m = PAGE_RE.search(lines[i])
        if m:
            page = m.group(1)
    return page


def cells(line):
    m = ROW_RE.match(line)
    if not m:
        return []
    return [c.strip() for c in m.group(1).split('|')]


def main():
    ap = argparse.ArgumentParser(prog='collect_chart.py', description=__doc__, add_help=False)
    ap.add_argument('--source', required=True, help='含表的正文（解析件或本地文件）')
    ap.add_argument('--out', help='骨架落盘位置；不给就走标准输出')
    ap.add_argument('--asof', help='解析日 YYYY-MM-DD（缺省＝本次运行的当天）')
    ap.add_argument('--max-rows', type=int, default=10, help='第二节最多搬几行（默认 10，与机检条数带上限同值）')
    ap.add_argument('-h', '--help', action='store_true')
    a = ap.parse_args()
    if a.help:
        print(__doc__)
        return 0
    src = Path(a.source)
    if not src.is_file():
        print('取值域故障：%s 读不到（本件不抓链接——先把含表的正文取回本地，再跑这一支）' % src)
        return 3
    lines = src.read_text(encoding='utf-8', errors='replace').split('\n')
    if not any(l.strip() for l in lines):
        print('没有可用文本：%s 是空的——空原文不出骨架（那是没有出处，不是待填）' % src)
        return 1
    if a.asof:
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', a.asof):
            print('取值域故障：--asof 要写成 YYYY-MM-DD，现读=%r（来源行的解析日用它）' % a.asof)
            return 3
        try:
            dt.date.fromisoformat(a.asof)
        except ValueError:
            print('取值域故障：--asof 成形但不是日历上存在的一天，现读=%r（机检只核形制与在场，写错了照样进不来）' % a.asof)
            return 3
        asof = a.asof
    else:
        asof = dt.date.today().isoformat()

    def is_sep(l):
        cs = cells(l)
        return len(cs) >= 2 and all(set(c) <= set('-: ') and c for c in cs)

    rows, headers = [], []
    for i, ln in enumerate(lines, 1):
        cs = cells(ln)
        if len(cs) < 2 or is_sep(ln):
            continue
        nxt = lines[i] if i < len(lines) else ''
        if is_sep(nxt):
            # markdown 语义：分隔行的上一行就是列头——列头不是数据，不当要点搬进第二节
            if not headers:
                headers = cs
            continue
        nums = [c for c in cs[1:] if NUM_RE.search(c)]
        if not nums:
            continue
        pg = nearest_page(lines, i - 1)
        rows.append((i, cs[0], nums, pg))
    if not rows:
        print('认不出数值行：%s 里没有「标签＋至少一个数值格」的表格行——不出骨架（那是要另定形状，不是待填）' % src)
        return 1
    moved = rows[:a.max_rows]
    title = next((l[2:].strip() for l in lines if l.startswith('# ')), src.stem)

    out = ['# %s·图规格与读表要点（骨架）' % title, '',
           '本页由 AI 整理，是 **AI 整理初稿**：每个数都请回表核对。它不据图给投资建议、不判评级与目标价，判断位 [待人工]。',
           '被核对文件：%s｜解析日：%s｜读取方式：本地只读（本件不抓链接、不执行表里提到的任何程序、不代做算术）' % (src, asof),
           '没读到的部分一律写进第三节，不补常识性推断。', '',
           '## 1、图的规格', '',
           '（下面四件是待核位——图型要按你想看清的关系选，本件不代选）']
    out += ['- %s：（待核——这一件要人选）' % k for k in SPEC_KEYS]
    out += ['', '## 2、读表要点', '']
    for no, label, nums, pg in moved:
        loc = '〔第 %s 页〕，' % pg if pg else ''
        shown = '、'.join('「%s」' % n for n in nums[:3])
        out.append('- %s：%s%s%s:%d [S1]' % (label, shown, loc, src, no))
    out += ['', '## 3、图的限度与未取到', '']
    for k in LIMIT_KINDS:
        out.append('- %s：（待核——填表内位置与一句逐字引文，没有这一类就在此写未见到）' % k)
    out += ['', '- 口径：图的数值一律取自上表逐字格；要算同比、占比、环比、平均，请到宿主或电子表格算，本件不代人算也不代验算得对不对。',
            '判断位：这张图要不要用、给谁看、支撑什么结论，一律 [待人工]。', '',
            '## 4、来源与解析日', '',
            '- [S1] %s（%s:1 ｜解析日 %s）' % (title, src, asof), '',
            '表行现读=%d 行｜第二节搬入=%d 行（上限 --max-rows=%d，超出部分本件不代选）｜列头=%s'
            % (len(rows), len(moved), a.max_rows, '、'.join(headers[:4]) or '未认到')]
    body = '\n'.join(out) + '\n'

    if a.out:
        p = Path(a.out)
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(body, encoding='utf-8')
        except OSError as e:
            print('取值域故障：写不到 %s（%s）' % (p, e.strerror or '原因未取到'))
            return 3
        print('骨架落成：%s｜表行=%d｜搬入要点=%d 行｜规格待核位=%d 件（机检按设计在 E-FORMAT 发红）'
              % (p, len(rows), len(moved), len(SPEC_KEYS)))
    else:
        sys.stdout.write(body)
        print('\n---- 以上为骨架全文；未落盘（没给 --out）。表行=%d' % len(rows))
    return 0


if __name__ == '__main__':
    sys.exit(main())
