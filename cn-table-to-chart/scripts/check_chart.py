#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_chart.py — 校一份「图规格＋读表要点」是否合 `SKILL.md` §3 四节契约与 §5 三条硬边界。

用法：
    python3 -B scripts/check_chart.py <产物.md> [--table 表原文.md]
    python3 -B scripts/check_chart.py --selftest          跑包内夹具（好样须过、坏样须各发它该发的那一道）
    python3 -B scripts/check_chart.py --help               本说明
    校样件时给上表原文：--table scripts/fixtures/target-table.md

五道（判定全集在本脚本，本文只指路）：
    道一 形制 E-FORMAT  ：头部四件自标逐字在位；四节齐且有序；第一节四件规格（图型／横轴／纵轴／序列）齐且都不是待核位；第二节要点条数落在 3–10 这一带；第四节至少一行来源
    道二 锚   E-ANCHOR  ：每条要点行末尾带 [S#] 且该行有定位（第 N 页 或 文件:行号）；锚在第四节要有对应行；来源行必须同时带定位与解析日——解析日＝日期挂在「解析日」标签下且是日历上存在的一天；机检只核这两件，核不了那天是否真是取回当天
    道三 逐字 E-QUOTE   ：「」里那个数必须逐字在表里（第一节引的也算）；同一行既给页码又给行号时**两个定位各比各的**（只读其一会把假的那枚放过）；没给 --table 时明写不可判、不并入通过
    道四 点名 E-COVERAGE：第三节四类限度（缺格与空值／合并格与跨列表头／单位与口径／表外推与未读到）逐类在位，每类要么给定位要么写「未见到／未取到」，待核不算点名；别处报了未读到而第三节没点名的发红
    道五 断言 E-ADVICE  ：投资建议、评级与目标价、名次排序一律零命中。判的是「作者替读者下了结论」这个动作，两张网并行：①裸断言（建议买入／目标价看至／值得投资／可投／首选／看空…）**单靠词就发条，不要求情态词在场**；②最高级／比较级形态（最高／最强／更优／优于…）与投资结论对象词（估值／基本面／前景／买入…）**同语义段同现**也发条。语义段按段落切——行首不是标题／列表／表格就接到上一段，写完「增速放缓」换行再写「建议减仓」算同一句。引号里的表内原文不算作者表态（先剥引号再判）；要留判断就同一语义段里挂 [待人工]

退码：0 全过（不可判项在输出里明写，不改退码）；1 有发条；2 用法错；3 取值域故障（产物或表原文读不到——不读成「零违例」）。
出口形制：失败＝一行 "FAIL: <文件>（N 条）"，其下每条详行先打错误码前缀；全过＝一行 "PASS: …" 加计数行。
"""

from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import io
import re
import sys
from pathlib import Path

SECTIONS = ('图的规格', '读表要点', '图的限度与未取到', '来源与解析日')
MARKS = ('AI 整理初稿', '请回表核对', '不据图给投资建议', '判断位 [待人工]')
SPEC_KEYS = ('图型', '横轴', '纵轴', '序列')
LIMIT_KINDS = ('缺格与空值', '合并格与跨列表头', '单位与口径', '表外推与未读到')
MIN_ROWS, MAX_ROWS = 3, 10

ANCHOR_RE = re.compile(r'\[S(\d+)\]\s*$')
QUOTE_RE = re.compile(r'[「『](.+?)[」』]', re.S)
PAGE_RE = re.compile(r'第\s*(\d+)\s*页')
LINE_RE = re.compile(r'([A-Za-z0-9_./-]+):(\d+)')
DATE_RE = re.compile(r'\d{4}-\d{2}-\d{2}')
PARSE_DATE_RE = re.compile(r'解析日\s*[:：]?\s*(\d{4}-\d{2}-\d{2})')
PLACE_RE = re.compile(r'\[待人工\]')
TODO_RE = re.compile(r'待填|待核|待补|（下面四件')
UNSEEN_RE = re.compile(r'未见到|未读到|未见对应|未取到')
GAPWORDS_RE = re.compile(r'未读到|未见到|没读到|截断')

ADVICE_RE = re.compile(
    r'建议买入|建议卖出|建议加仓|建议减仓|建议建仓|建议清仓|应买入|应卖出|应回避|'
    r'值得投资|不宜投资|可投|不可投|买入评级|卖出评级|目标价|评级为|予.{0,4}评级|上调评级|下调评级|'
    r'推荐买入|推荐配置|第一梯队|首选标的|跑赢行业|跑输行业|超配|低配|抄底|逃顶|止盈止损|必涨|必跌|看好后市|看空后市')
SUPER_RE = re.compile(r'最[^\n]{0,6}?(?:强|高|好|优|差|低|稳|抗跌)|更[^\n]{0,6}?(?:强|好|优|差)|优于|逊于|胜过|压过|首选|次选')
TARGET_RE = re.compile(r'估值|基本面|成长性|前景|后市|标的|投资|买入|卖出|加仓|减仓|配置|风险回报|回报')

UNIT_START_RE = re.compile(r'^\s*(#|[-*+|>]?\s|\|)')


def norm(t: str) -> str:
    return re.sub(r'\s+', '', t)


def strip_quotes(s: str) -> str:
    return QUOTE_RE.sub('', s)


def units_of(lines):
    """语义段：行首是标题／列表项／表格／引用块才开新段，其余行接到上一段——表态不因换行消失。"""
    out, cur = [], []
    for i, ln in enumerate(lines, 1):
        if not ln.strip():
            if cur:
                out.append(cur)
                cur = []
            continue
        if UNIT_START_RE.match(ln) or not cur:
            if cur:
                out.append(cur)
            cur = [(i, ln)]
        else:
            cur.append((i, ln))
    if cur:
        out.append(cur)
    return out


def page_block(lines, page):
    start = next((i for i, l in enumerate(lines) if PAGE_RE.search(l) and PAGE_RE.search(l).group(1) == str(page)), None)
    if start is None:
        return None
    end = next((i for i in range(start + 1, len(lines)) if PAGE_RE.search(lines[i])), len(lines))
    return '\n'.join(lines[start:end])


def parse_date_state(s: str):
    """返回 (ok, 现读标签, 现读日期)：日期必须在「解析日」标签下且是日历上存在的一天。"""
    ds = PARSE_DATE_RE.findall(s)
    real = []
    for x in ds:
        try:
            dt.date.fromisoformat(x)
            real.append(x)
        except ValueError:
            continue
    if ds and not real:
        return False, '解析日', ds
    if real:
        return True, '解析日', real
    bare = DATE_RE.findall(s)
    if bare:
        labels = re.findall(r'([一-龥]{2,6})\s*[:：]?\s*' + re.escape(bare[0]), s)
        return False, (labels[0] if labels else '无标签'), bare
    return False, '无', []


def scan(path: Path, tbl_lines):
    issues = []
    unverifiable = []
    seen = set()

    def add(code, lane, no, msg):
        key = (code, no, msg)
        if key in seen:
            return
        seen.add(key)
        issues.append((code, lane, no, msg))

    lines = path.read_text(encoding='utf-8', errors='replace').split('\n')
    if not lines or not lines[0].startswith('# '):
        add('E-FORMAT', '标题', 1, '首行不是「# 标题」这一形（规格：产物按标题命名，首行就得是标题）')
    head_end = next((i for i, l in enumerate(lines) if l.startswith('## ')), len(lines))
    head = '\n'.join(lines[:head_end])
    for need in MARKS:
        if need not in head:
            add('E-FORMAT', '头部', 1, '头部自标缺『%s』（规格：四件逐字写在第一个「## 」之前）' % need)

    idxs = []
    for n, name in enumerate(SECTIONS, 1):
        hit = [i for i, l in enumerate(lines) if re.match(r'^##\s*%d、%s' % (n, re.escape(name)), l)]
        if not hit:
            add('E-FORMAT', '四节', 1, '缺「## %d、%s」节（规格：四节齐且按一二三四有序）' % (n, name))
        else:
            idxs.append((n, hit[0]))
    bounds = {}
    for pos in range(len(idxs)):
        n, i0 = idxs[pos]
        i1 = idxs[pos + 1][1] if pos + 1 < len(idxs) else len(lines)
        bounds[n] = (i0, i1)

    def rows_in(n):
        if n not in bounds:
            return []
        i0, i1 = bounds[n]
        return [(i + 1, lines[i].strip()) for i in range(i0 + 1, i1) if lines[i].strip().startswith(('- ', '* '))]

    def verify_row(no, s, where):
        """该行每一段引文与每一个定位都各自比；页码与行号同时给时两个都要成立。"""
        qs = QUOTE_RE.findall(s)
        if not qs:
            return
        if tbl_lines is None:
            unverifiable.append('%s第 %d 行有引文，但未给 --table 表原文（不可判不并入通过）' % (where, no))
            return
        txt = '\n'.join(tbl_lines)
        for q in qs:
            if norm(q) not in norm(txt):
                add('E-QUOTE', '逐字回表', no, '「%s」在表原文里找不到逐字（规格：数要么照抄那一格，要么写进第三节说未读到，不能凭印象补）' % q[:22])
        for pg in sorted(set(PAGE_RE.findall(s))):
            blk = page_block(tbl_lines, int(pg))
            if blk is None:
                add('E-QUOTE', '页码定位', no, '「第 %s 页」在表原文里找不到页标（规格：页码也要回得到，别只写一个看着像的数）' % pg)
            elif not any(norm(q) in norm(blk) for q in qs):
                add('E-QUOTE', '页码定位', no, '第 %s 页里没有那一格数（规格：页码与数要对得上）' % pg)
        for fname, ln_no in LINE_RE.findall(s):
            n = int(ln_no)
            if n < 1 or n > len(tbl_lines):
                add('E-QUOTE', '行号定位', no, '%s:%d 超出表原文行数（现读行数=%d）——行号与页码同时给时两个都要各自成立' % (fname, n, len(tbl_lines)))
            elif not any(norm(q) in norm(tbl_lines[n - 1]) for q in qs):
                add('E-QUOTE', '行号定位', no, '%s:%d 那一行没有这格数（现读：%s）' % (fname, n, tbl_lines[n - 1][:26]))

    # 第一节：规格四件
    if 1 in bounds:
        rows = rows_in(1)
        got = {}
        for no, s in rows:
            for k in SPEC_KEYS:
                m = re.match(r'^[-*]\s*%s\s*[：:]\s*(.*)$' % k, s)
                if m:
                    got[k] = (no, m.group(1).strip())
        for k in SPEC_KEYS:
            if k not in got:
                add('E-FORMAT', '规格四件', bounds[1][0] + 1, '第一节没有「%s」这一件（规格：图型／横轴／纵轴／序列四件都在，缺一件图就画不出来）' % k)
            elif TODO_RE.search(got[k][1]):
                add('E-FORMAT', '规格待核', got[k][0], '「%s」仍是待核位（规格：这一件要人选，待核不算填过——本件不代选图型）' % k)
            else:
                verify_row(got[k][0], got[k][1], '第一节')

    # 第二节：要点条数与锚
    listed = {}
    if 4 in bounds:
        rows = rows_in(4)
        if not rows:
            add('E-COVERAGE', '来源', bounds[4][0] + 1, '第四节一行来源都没有（规格：产物的价值全在能回到哪一格表）')
        for no, ln in rows:
            m = re.match(r'^[-*]\s*\[S(\d+)\]', ln)
            if not m:
                add('E-ANCHOR', '来源', no, '来源行不以 [S#] 开头（规格：编号与锚一一对应）')
            else:
                listed[int(m.group(1))] = no
            ok_label, lab, shown = parse_date_state(ln)
            if not ok_label:
                add('E-ANCHOR', '来源', no, '来源行的日期没挂在「解析日」标签下或不是日历上存在的一天（现读标签=%s，现读日期=%s；规格：形制对不等于它是解析日——「合同签署日」那种标签不算，2026-13-99 也不是真实的一天；机检只核这两件，核不了那天是否真是取回当天）'
                    % (lab, '、'.join(shown) or '无'))
            if not LINE_RE.search(ln) and not PAGE_RE.search(ln) and not re.search(r'https?://|www\.', ln):
                add('E-ANCHOR', '来源', no, '来源行既无 URL 也无 文件:行号／第 N 页（规格：要回到一处表，得有个位置）')

    if 2 in bounds:
        rows = rows_in(2)
        if not MIN_ROWS <= len(rows) <= MAX_ROWS:
            add('E-FORMAT', '条数带', bounds[2][0] + 1, '要点 %d 条，不在 %d–%d 这一带（规格：少于 %d＝这张表没读透，多于 %d＝把整张表抄下来了）'
                % (len(rows), MIN_ROWS, MAX_ROWS, MIN_ROWS, MAX_ROWS))
        for no, s in rows:
            m = ANCHOR_RE.search(s)
            if not m:
                add('E-ANCHOR', '锚', no, '要点行末尾没有 [S#]（规格：每条要点都要回得到一个编号）')
            elif int(m.group(1)) not in listed:
                add('E-ANCHOR', '锚', no, '锚 [S%s] 在第四节没有对应行（规格：用的每个编号都要回得到来源行）' % m.group(1))
            if not LINE_RE.search(s) and not PAGE_RE.search(s):
                add('E-ANCHOR', '定位', no, '要点行没有定位（规格：带 第 N 页 或 文件:行号，读者才翻得到那一格）')
            verify_row(no, s, '要点')

    # 第三节：四类限度点名
    if 3 in bounds:
        rows = rows_in(3)
        by_kind = {}
        for no, s in rows:
            for k in LIMIT_KINDS:
                if k in s or (k.split('与')[0] in strip_quotes(s)):
                    by_kind.setdefault(k, []).append((no, s))
        for k in LIMIT_KINDS:
            got = by_kind.get(k)
            if not got:
                add('E-COVERAGE', '四类点名', bounds[3][0] + 1, '第三节没有「%s」这一类（规格：四类逐类在位——有就给位置，没有就写未见到，不许沉默跳过）' % k)
                continue
            for no, s in got:
                if TODO_RE.search(s):
                    add('E-COVERAGE', '待核不算点名', no, '「%s」这一类仍是待核位（规格：填位置或写未见到，待核不算点名）' % k)
                elif not (LINE_RE.search(s) or PAGE_RE.search(s) or UNSEEN_RE.search(strip_quotes(s))):
                    add('E-COVERAGE', '点名形制', no, '「%s」这一类既没给位置也没写未见到（规格：两类之一，别留半句）' % k)
                verify_row(no, s, '限度')
        for i, ln in enumerate(lines, 1):
            if 3 in bounds and bounds[3][0] < i - 1 < bounds[3][1]:
                continue
            if ln.lstrip().startswith('#') or not GAPWORDS_RE.search(strip_quotes(ln)):
                continue
            if UNSEEN_RE.search(strip_quotes(ln)) and not any(UNSEEN_RE.search(l) for l in lines[bounds[3][0] + 1:bounds[3][1]]):
                add('E-COVERAGE', '缺口点名', i, '这一行报了未读到，而第三节没有任何未见到／未取到条目（规格：没读到的部分一律在第三节点名，不补常识性推断）')

    # 第五节判据：语义段制，裸断言与结构式两网并行
    for unit in units_of(lines):
        text = strip_quotes('\n'.join(l for _, l in unit)).replace('\n', '')
        if PLACE_RE.search(text):
            continue
        m = ADVICE_RE.search(text)
        if m:
            no = next((i for i, l in unit if ADVICE_RE.search(strip_quotes(l))), unit[0][0])
            add('E-ADVICE', '投资断言', no, '作者句子里出现投资／评级／目标价断言「%s」（规格：本件不据图给投资建议、不判评级与目标价；裸断言单靠词就发条，不要求情态词在场；要写就同一语义段里挂 [待人工]）' % m.group(0))
            continue
        s, tg = SUPER_RE.search(text), TARGET_RE.search(text)
        if s and tg:
            no = next((i for i, l in unit if SUPER_RE.search(strip_quotes(l))), unit[0][0])
            add('E-ADVICE', '结论式名次', no, '作者句子里「%s」与「%s」同语义段同现——换了说法的投资结论同样拦（规格：不据图替读者下判断；换行不算躲开，续行并入上一段；要留就挂 [待人工]）'
                % (s.group(0), tg.group(0)))
    return issues, lines, unverifiable


codes_doc = {'E-FORMAT': '道一 形制与规格四件', 'E-ANCHOR': '道二 锚与定位与解析日标签',
             'E-QUOTE': '道三 数逐字回表（页码与行号各比各的）', 'E-COVERAGE': '道四 四类限度点名',
             'E-ADVICE': '道五 投资断言零命中（语义段制）'}

FX = Path(__file__).resolve().parent / 'fixtures'
CASES = [('good-chart.md', 0, None),
         ('bad-spec.md', 1, 'E-FORMAT'),
         ('bad-no-anchor.md', 1, 'E-ANCHOR'),
         ('bad-invented-number.md', 1, 'E-QUOTE'),
         ('bad-missing-limit.md', 1, 'E-COVERAGE'),
         ('bad-advice.md', 1, 'E-ADVICE'),
         ('bad-bare-outcome.md', 1, 'E-ADVICE'),
         ('bad-superlative.md', 1, 'E-ADVICE')]


def run_one(path: Path, source=None, quiet=False):
    tbl_lines = None
    if source:
        p = Path(source)
        if not p.is_file():
            print('取值域故障：表原文读不到 %s（道三不因此算通过，也不算违例）' % source)
            return 3, 0, 0
        tbl_lines = p.read_text(encoding='utf-8', errors='replace').split('\n')
    issues, lines, unverifiable = scan(path, tbl_lines)
    codes = sorted({c for c, _, _, _ in issues})
    counts = {}
    for c, _, _, _ in issues:
        counts[c] = counts.get(c, 0) + 1
    if not quiet:
        for code, lane, no, msg in issues:
            print('  [%s] [%s] 第 %d 行：%s' % (code, lane, no, msg))
        for u in unverifiable:
            print('  [不可判] %s' % u)
    if issues:
        print('FAIL: %s（%d 条）' % (path.name, len(issues)))
        print('       ' + '；'.join('%s %d 条' % (c, n) for c, n in sorted(counts.items())))
        print('       码表: ' + '；'.join('%s=%s' % (c, codes_doc[c]) for c in codes))
        return 1, len(issues), len(unverifiable)
    print('PASS: %s（四节齐、规格四件人选过、要点条数在带内、锚与双定位各自成立、数逐字回表、四类限度都点名、投资与评级断言零命中）' % path.name)
    print('       扫过 %d 行，发条 0 条，不可判 %d 项；判定与阈值全集以本脚本现值为准（--help 看五道说明）'
          % (len(lines), len(unverifiable)))
    return 0, 0, len(unverifiable)


def selftest(source):
    bad = 0
    for name, want_rc, want_code in CASES:
        p = FX / name
        if not p.is_file():
            print('  取值域故障：夹具不在场 %s（不读成「零违例」）' % name)
            return 3
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc, _, _ = run_one(p, source)
        detail = buf.getvalue()
        codes = sorted(set(re.findall(r'E-[A-Z]+', '\n'.join(l for l in detail.splitlines() if l.lstrip().startswith('[E-')))))
        landed = bool(detail.strip()) or rc != 0
        if rc != want_rc:
            print('  不合 %s：期望退码 %d，实发 %d（注入生效=%s）' % (name, want_rc, rc, '是' if landed else '否'))
            bad += 1
            continue
        if want_code and codes != [want_code]:
            print('  不合 %s：期望只发 %s，实发码集=%s（注入生效=%s）' % (name, want_code, '、'.join(codes) or '空', '是' if landed else '否（空注入，读数作废）'))
            bad += 1
            continue
        if want_code is None and codes:
            print('  不合 %s：好样期望全过，实发 %s' % (name, '、'.join(codes)))
            bad += 1
            continue
        print('  ok   %s（退码 %d·期望 %s·实发码 %s·注入生效=%s）' % (
            name, rc, want_code or '全过', '、'.join(codes) or '无', '是' if (rc or codes) else '不适用（好样）'))
    n_good = sum(1 for x in CASES if x[2] is None)
    n_bad = len(CASES) - n_good
    print('selftest: ' + ('ALL GREEN（好样 %d 枚·坏样 %d 枚各只发它该发的那一道 %d/%d·逐枚报注入生效与否）'
                          % (n_good, n_bad, n_bad, n_bad) if bad == 0 else '%d 条不合预期' % bad))
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser(prog='check_chart.py', description=__doc__, add_help=False)
    ap.add_argument('report', nargs='?', help='要校的产物')
    ap.add_argument('--table', help='表原文（本地文件；给了才逐字比数与两个定位）')
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--quiet', action='store_true', help='只报末行与计数')
    ap.add_argument('-h', '--help', action='store_true')
    a = ap.parse_args()
    if a.help or (not a.report and not a.selftest):
        print(__doc__)
        return 0 if a.help else 2
    if a.selftest:
        src = a.table or str(FX / 'target-table.md')
        if not Path(src).is_file():
            print('取值域故障：自测要的表原文不在场 %s（没有原文，道三无从跑）' % src)
            return 3
        return selftest(src)
    p = Path(a.report)
    if not p.is_file():
        print('取值域故障：读不到产物文件 %s（不当「零违例」读）' % p)
        return 3
    rc, _, _ = run_one(p, a.table, quiet=a.quiet)
    return rc


if __name__ == '__main__':
    sys.exit(main())
