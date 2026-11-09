#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_note.py — 校一份「未出财报期的个股研究初稿」是否合 `SKILL.md` §3 七节契约与 §5 红线。

用法：
    python3 check_note.py <研究稿.md>        校一份研究稿（纯标准库、零网络、不发任何请求）
    python3 check_note.py --selftest         跑包内夹具：好样必须过，六枚坏样必须各发它该发的那一道
    python3 check_note.py --help             本说明

出口形制（与套件姊妹件同族）：
    失败 = 一行 "FAIL: <文件>（N 条）"，其下每条详行先打错误码前缀（五枚 E-* 之一），道名后是行号与该道规格；
           末行 "码表:" 只列本次真正用到的码与含义。
    全过 = 一行 "PASS: <文件>（…）"，并印「扫过 N 行」与五道计数——计数说看到多少，不说猜多少。

五道是什么（判定全集在本脚本，本文只指路，不复述细节）：
    道一 形制：头部四件自标逐字在位＋「财报状态：」行在场且值为未出＋七节齐且按一至七有序
                ＋一句话结论非空非占位＋四个内容节（业务拆解／竞争位／驱动因子／风险清单）各至少一行
    道二 锚：内容节每条发现行行末带 [S#]，且该编号在第七节有对应行；第七节每行必须同时带 URL 与 YYYY-MM-DD 检索日
    道三 红线：评级／目标价／买卖与走势类断言一律零命中，要写只能同行挂 [待人工]；改数词（约／左右／大概）不得替数字打底
    道四 未取到与计数：正文写了「未取到／未检索到」的，第六节必须逐条点名它；第六节列了而正文没有这条表述的同样发
    道五 边界：财报状态写「已出」＝这一期该走 cn-earnings-note 的逐数点评，本件的四节框架不适用

退码：0 全过；1 有发条（详行逐条给码、道名、行号与规格）；2 用法错；3 取值域故障（文件读不到，不读成「零违例」）。
"""

from __future__ import annotations

import argparse
import atexit
import re
import shutil
import sys
import tempfile
from pathlib import Path

TMP_ROOTS = []


@atexit.register
def _cleanup_tmp() -> None:
    for d in TMP_ROOTS:
        shutil.rmtree(d, ignore_errors=True)


def _probe_copy(text: str) -> Path:
    d = Path(tempfile.mkdtemp(prefix='check-equity-note-', dir=tempfile.gettempdir()))
    TMP_ROOTS.append(d)
    f = d / 'probe.md'
    f.write_text(text, encoding='utf-8')
    return f


SECTIONS = ('一句话结论', '业务拆解', '竞争位', '驱动因子', '风险清单', '未取到与口径', '来源')
CONTENT_IDX = (2, 3, 4, 5)          # 四个内容节：各至少一行，空节＝不是一份研究稿
MARKS = ('AI 整理初稿', '请回原文核对', '不构成投资建议', '判断位 [待人工]')
URL_RE = re.compile(r'https?://|www\.[A-Za-z0-9.-]+')
DATE_RE = re.compile(r'\d{4}-\d{2}-\d{2}')
ANCHOR_RE = re.compile(r'\[S(\d+)\]\s*$')
PLACEHOLDER_RE = re.compile(r'^\s*(（[^）]*）)?[—\-–]\s*$|待定|待填|TBD|<[^>]*>$')
STATUS_RE = re.compile(r'^财报状态[：:]\s*(.+?)\s*$')
# 红线词族：只收「推荐动作」与「涨跌承诺」的确形。增持／减持**不收**——股东增减持公告是事实陈述，
# 收进来会把「控股股东计划减持不超过 2%」这类正当登记判红；要禁的是「建议增持」这种推荐语。
BANNED = re.compile(r'买入|卖出|建仓|清仓|加仓|目标价|止盈|止损|必涨|必跌|稳赚|无风险'
                    r'|强烈建议|建议持有|建议买入|建议增持|建议减持|翻倍|跑赢大盘'
                    r'|严重低估|严重高估|值得买入|可以买入')
HEDGE = re.compile(r'约\s*[\d０-９]|左右|大概|大约')
CODES = {'E-FORMAT': '道一 形制', 'E-ANCHOR': '道二 锚', 'E-BANWORD': '道三 红线',
         'E-COVERAGE': '道四 未取到与计数', 'E-SCOPE': '道五 边界'}


def scan(path: Path):
    issues = []
    seen = set()

    def add(code, lane, line_no, msg):
        key = (code, line_no, msg)
        if key not in seen:
            seen.add(key)
            issues.append((code, lane, line_no, msg))

    lines = path.read_text(encoding='utf-8', errors='replace').split('\n')
    first_h2 = next((i for i, ln in enumerate(lines) if ln.startswith('## ')), len(lines))
    head = '\n'.join(lines[:first_h2])

    # ---- 道一 头部自标 ----
    for need in MARKS:
        if need not in head:
            add('E-FORMAT', '头部', 1, f"头部自标缺『{need}』（规格：四件逐字齐，写在第一个「## 」之前）")

    # ---- 道一／道五 财报状态 ----
    st = None
    for i in range(first_h2):
        m = STATUS_RE.match(lines[i].strip())
        if m:
            st = (i, m.group(1))
            break
    if st is None:
        add('E-FORMAT', '财报状态', 1,
            '头部缺「财报状态：」行（规格：本件只做未出财报期，这一格是它与财报点评的分界，必须自报）')
    else:
        i, v = st
        if '已出' in v:
            add('E-SCOPE', '边界', i + 1,
                f'财报状态写的是「{v}」——已出财报期的逐数点评走 cn-earnings-note（四期差异／科目勾稽／覆盖账本），'
                '本件的业务拆解四节框架不适用；要么改走那一件，要么把研究窗口挪到财报空窗期')
        elif '未出' not in v:
            add('E-FORMAT', '财报状态', i + 1,
                f'财报状态「{v}」认不出（规格：以「未出」起头并注明最近一期，如「未出（最近一期：2025 年报）」）')

    # ---- 道一 七节齐且有序 ----
    idxs = []
    for n, name in enumerate(SECTIONS, 1):
        hit = [i for i, ln in enumerate(lines) if re.match(rf'^##\s*{n}、{re.escape(name)}\s*$', ln)]
        if not hit:
            add('E-FORMAT', '七节', 1, f"缺「## {n}、{name}」段（规格：七节齐且按一至七有序）")
        else:
            idxs.append((n, hit[0]))
    if len(idxs) > 1 and [n for n, _ in idxs] != sorted(n for n, _ in idxs):
        add('E-FORMAT', '七节', idxs[0][1] + 1, '七节次序与契约不一致（规格：一至七有序）')
    bounds = {}
    for pos, (n, i0) in enumerate(idxs):
        i1 = idxs[pos + 1][1] if pos + 1 < len(idxs) else len(lines)
        bounds[n] = (i0, i1)

    # ---- 道一 结论非空非占位 ----
    if 1 in bounds:
        i0, i1 = bounds[1]
        body = [ln for ln in lines[i0 + 1:i1] if ln.strip() and not ln.startswith('#')]
        if not body:
            add('E-FORMAT', '结论', i0 + 1, '一句话结论留空（规格：至少一行实句，不留占位）')
        else:
            bad = next((ln for ln in body if PLACEHOLDER_RE.search(ln)), None)
            if bad is not None:
                add('E-FORMAT', '结论', i0 + 1 + body.index(bad),
                    '一句话结论仍是占位（规格：写成可核的实句；判断走 [待人工]，不靠占位）')

    # ---- 道一 四个内容节各至少一行 ----
    for n in CONTENT_IDX:
        if n not in bounds:
            continue
        i0, i1 = bounds[n]
        rows = [ln for ln in lines[i0 + 1:i1] if ln.strip() and not ln.startswith('#')]
        if not rows:
            add('E-FORMAT', '内容节', i0 + 1,
                f'「{SECTIONS[n - 1]}」整节为空（规格：四个内容节各至少一行——没有风险清单的研究稿不是研究稿）')

    # ---- 道二 锚 ----
    anchors_used, listed = [], set()
    for n in CONTENT_IDX:
        if n not in bounds:
            continue
        i0, i1 = bounds[n]
        for i in range(i0 + 1, i1):
            ln = lines[i]
            if not ln.strip().startswith(('-', '*', '|')):
                continue
            m = ANCHOR_RE.search(ln.strip())
            if not m:
                add('E-ANCHOR', '锚', i + 1,
                    '发现行行末没有 [S#] 锚（规格：每条发现一行、行末带一个锚；没有锚就不要写进内容节）')
            else:
                anchors_used.append((int(m.group(1)), i + 1))
            if HEDGE.search(ln):
                add('E-BANWORD', '改数', i + 1,
                    f"命中改数词「{HEDGE.search(ln).group(0)}」（规格：数值要么照来源写，要么落第六节写未取到，不用约／左右打底）")

    if 7 in bounds:
        i0, i1 = bounds[7]
        rows = [ln for ln in lines[i0 + 1:i1] if ln.strip().startswith(('-', '*'))]
        if not rows:
            add('E-COVERAGE', '来源', i0 + 1, '第七节一行来源都没有（规格：逐条挂源的价值就在这一节，空节等于没有出处）')
        for k, ln in enumerate(rows, 1):
            no = i0 + 1 + lines[i0 + 1:i1].index(ln) + 1
            m = re.match(r'^[-*]\s*\[S(\d+)\]', ln.strip())
            if not m:
                add('E-ANCHOR', '来源', no, f'来源第 {k} 行不以 [S#] 开头（规格：编号与正文锚一一对应）')
            else:
                listed.add(int(m.group(1)))
            if not URL_RE.search(ln):
                add('E-ANCHOR', '来源', no,
                    f'来源 [S{m.group(1) if m else k}] 缺 URL（规格：逐条可回查——域名或链接原样写进同一行）')
            if not DATE_RE.search(ln):
                add('E-ANCHOR', '来源', no,
                    f'来源 [S{m.group(1) if m else k}] 缺检索日 YYYY-MM-DD（规格：个股研究的时效以检索日为凭）')
    for num, ln_no in anchors_used:
        if num not in listed:
            add('E-ANCHOR', '锚', ln_no, f'锚 [S{num}] 在第七节没有对应行（规格：正文用的每个编号都要能回到来源行）')

    # ---- 道三 红线 ----
    for i, ln in enumerate(lines, 1):
        m = BANNED.search(ln)
        if m and '[待人工]' not in ln:
            add('E-BANWORD', '判断词', i,
                f"命中「{m.group(0)}」（规格：评级／目标价／买卖与走势类断言本件不产出；要写就同行挂 [待人工]，或改中性陈述）")

    # ---- 道四 未取到两向点名 ----
    MISS_WORD = re.compile(r"未取到|未检索到|没取到|没检索到")
    STOP_TOK = {"它", "这", "该", "其", "本节", "来源", "渠道", "本条", "该项", "本次"}
    # 名目「同指」判：先剥括号注与标点，再按核心名词短语判——字面全等算同指；一方含另一方且短的一方 ≥4 字算同指；
    # 否则取汉字集合的 Jaccard ≥ SAME_REF_MIN 算同指。阈值写在这里、由自测的三形钉死，不按文体特例放宽。
    SAME_REF_MIN = 0.6
    PUNCT_STRIP = re.compile(r"[^一-龥A-Za-z0-9]")

    def core(tok):
        return PUNCT_STRIP.sub("", re.sub(r"[（(][^）)]*[）)]", "", tok))

    def same_ref(a, b):
        ca, cb = core(a), core(b)
        if not ca or not cb:
            return False
        if ca == cb:
            return True
        if (ca in cb or cb in ca) and min(len(ca), len(cb)) >= 4:
            return True
        sa, sb = set(ca), set(cb)
        return len(sa & sb) / len(sa | sb) >= SAME_REF_MIN

    def refs(tok, pool):
        return any(same_ref(tok, other) for other in pool)

    def miss_tokens(seg_lines):
        out = []
        for off, ln in seg_lines:
            if ln.strip().startswith("#") or not MISS_WORD.search(ln):
                continue
            # 后置形只认「未取到：X」与「未取到X」两种——**逗号不算分隔符**：
            # 「分品类收入未取到，本期无定期报告」里逗号后面是原因从句，不是名目；
            # 把逗号当分隔符会把整句原因抓成名目，于是好样被判「第六节多列一项」。
            for m in re.finditer(r"(?:未取到|未检索到|没取到|没检索到)[：:\s]*([^\s，。；、：:｜\[\]（）()「」【】\n]{3,24})", ln):
                tok = m.group(1)
                if tok not in STOP_TOK:
                    out.append((tok, off))
            for m in re.finditer(r"([^\s，。；、：:｜\[\]（）()「」【】\n]{3,24}?)(?:未取到|未检索到|没取到|没检索到)", ln):
                tok = m.group(1)
                if tok not in STOP_TOK:
                    out.append((tok, off))
        return out

    body_seg = [(i, lines[i]) for n, (a, b) in bounds.items() if n != 6 for i in range(a + 1, b)]
    sec6_seg = [(i, lines[i]) for i in range(bounds[6][0] + 1, bounds[6][1])] if 6 in bounds else []
    body_toks = [tok for tok, _ in miss_tokens(body_seg)]
    sec6_toks = [tok for tok, _ in miss_tokens(sec6_seg)]
    for tok, no in miss_tokens(body_seg):
        if not refs(tok, sec6_toks):
            add("E-COVERAGE", "未取到点名", no + 1,
                f"第六节的点名缺一项：正文写了「{tok}」未取到，第六节没有同指的名目"
                "（规格：没列就是没说——逐条点名按名目同指对，不认整节出现过一个「未取到」）")
    for tok, no in miss_tokens(sec6_seg):
        if not refs(tok, body_toks):
            add("E-COVERAGE", "未取到点名", no + 1,
                f"第六节多列一项：「{tok}」在第六节点名为未取到，正文没有同指的这条表述"
                "（规格：反向同判——多列与少列都不许）")
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
    print('PASS: ' + path.name + '（七节齐、自标在位、财报状态为未出、每条发现带可回锚、'
          '来源行齐 URL 与检索日、判断词零命中、未取到逐条点名）')
    print(f'       扫过 {len(lines)} 行，发条 0 条；判定与阈值全集以本脚本现值为准（--help 看五道说明）')
    return 0, 0, {}


def selftest():
    fx = Path(__file__).resolve().parent / 'fixtures'
    cases = [('good-note.md', 0, None),
             ('bad-no-anchor.md', 1, 'E-ANCHOR'),
             ('bad-missing-section.md', 1, 'E-FORMAT'),
             ('bad-rating-word.md', 1, 'E-BANWORD'),
             ('bad-gap-unlisted.md', 1, 'E-COVERAGE'),
             ('bad-earnings-period.md', 1, 'E-SCOPE'),
             ('bad-empty-section.md', 1, 'E-FORMAT')]
    bad = 0
    gt = (fx / 'good-note.md').read_text(encoding='utf-8')
    body_gap_line = '- 分品类收入未取到，本期无定期报告 [S1]'
    sec6_line = '- 未取到：分品类收入（本期无定期报告，只有 2025 年报口径）'
    assert gt.count(body_gap_line) == 1 and gt.count(sec6_line) == 1, '夹具形制变了，反证档要跟着改'
    probes = []
    # 阈值三形钉死：字面全等与同指异词都算点到，真无关才算多列
    p0a = gt.replace(sec6_line, '- 未取到：分品类收入（本期无定期报告）')
    probes.append(('钉阈·字面全等（两侧都写「分品类收入」）不得报多列', p0a, '第六节多列一项', False))
    p0b = gt.replace(sec6_line, '- 未取到：分品类收入数据（本期无定期报告）')
    probes.append(('钉阈·同指异词（正文「分品类收入」∥第六节「分品类收入数据」）不得报多列', p0b, '第六节多列一项', False))
    p0c = gt.replace(sec6_line, '- 未取到：质押股份比例')
    probes.append(('钉阈·真无关（第六节只列「质押股份比例」）必须报多列', p0c, '第六节多列一项', True))
    p1 = gt.replace(body_gap_line, body_gap_line + '\n- 境外子公司担保余额未取到 [S2]')
    probes.append(('反证·正文多写一条未取到而第六节不列｜独有句「第六节的点名缺一项」', p1, '第六节的点名缺一项', True))
    p2 = gt.replace(sec6_line, sec6_line + '；质押股份比例未取到')
    probes.append(('反证·第六节多列一条而正文无｜独有句「第六节多列一项」', p2, '第六节多列一项', True))
    p3 = gt.replace('\n' + body_gap_line, '').replace(
        sec6_line, '- 口径：产能数字为公司公告口径的名义产能，非实际产量')
    probes.append(('反证·两处都无这一项时本支不发｜独有句反向断言', p3, '第六节的点名缺一项', False))
    probes.append(('反证·两处都有时本支不发（好样原样）', gt, '第六节多列一项', False))
    for name, txt, needle, want in probes:
        assert txt != gt or not want, '注入自证：反证档必须真改过文本（除好样档）'
        pf = _probe_copy(txt)
        iss_p, _ls_p = scan(pf)
        detail_p = "\n".join(f'[{c}] 第 {no} 行：{msg}' for c, lane, no, msg in iss_p)
        rc_p = 1 if iss_p else 0
        hit = needle in detail_p
        okp = (hit if want else not hit)
        print(f"  {'ok  ' if okp else 'FAIL'} {name}｜实发{'含' if hit else '不含'}独有句、退码 {rc_p}")
        if not okp:
            bad += 1
    root = Path(tempfile.gettempdir())
    for d in TMP_ROOTS:
        shutil.rmtree(d, ignore_errors=True)
    leftover = sorted(q.name for q in root.iterdir() if q.name.startswith('check-equity-note-')) if root.is_dir() else []
    print(f"  {'ok  ' if not leftover else 'FAIL'} 临时根自清（跑后不增）｜本次建 {len(TMP_ROOTS)} 枚·跑后残留 {len(leftover)} 枚")
    if leftover:
        bad += 1
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
        if want_code is None and rc == 0:
            print(f'  ok   {name}（退码 {rc}·发条 {n}）')
        elif want_code:
            print(f'  ok   {name}（退码 {rc}·发条 {n}·实发 {want_code}）')
    print('selftest: ' + ('ALL GREEN（好样 1 枚·坏样六道 6/6）' if bad == 0 else f'{bad} 条不合期望'))
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser(prog='check_note.py', add_help=False,
                                 description='校一份未出财报期的个股研究初稿（五道，见 --help 正文）')
    ap.add_argument('target', nargs='?')
    ap.add_argument('--selftest', action='store_true', help='跑包内夹具（好样须过、六枚坏样须各发红）')
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
        print(f'取值域故障：读不到研究稿文件 {p}（不当「零违例」读）')
        return 3
    rc, _, _ = run_one(p, quiet=a.quiet)
    return rc


if __name__ == '__main__':
    sys.exit(main())
