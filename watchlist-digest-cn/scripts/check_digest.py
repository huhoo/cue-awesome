#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_digest.py — 校验一份自选清单增量日报是否合 `SKILL.md` §3 五段契约与 §4/§6 红线（零网络）。

用法：
    python3 check_digest.py <digest.md> [--run <run.json>]      校验一份日报（--run 缺省取同目录 run.json）
    python3 check_digest.py --selftest                          跑包内三枚日报样：好样与零新增样须过、坏样四道全发
    python3 check_digest.py --help                              本说明

出口形制（与姊妹件同族）：失败＝一行 "FAIL: <文件>（N 条）" ＋逐条先打 `E-*` 码的详行 ＋末行「码表:」；
全过＝一行 "PASS: <文件>（…）" 并印「扫过行数」「发条数」两类计数。
行数口径：`扫过 N 行` 按 `split('\\n')` 计＝`wc -l` 现值 +1。

四道（判定全集在本脚本；SKILL §5 是验收合同）：
    道一 E-FORMAT   五段齐且有序＋头部三件套＋时点七项就位且落成日期形（asof／窗口缺一不可）
    道二 E-ANCHOR   今日新增每行要日期＋出处锚；近端变更要「前值 → 现值」两侧或明写取不到；来源索引逐条给出处
    道三 E-BANWORD  评级／目标价／走势／买卖建议／行情与资金流承诺／「无风险」类断言落在非「需人工」节且未挂 [待人工]
    道四 E-COVERAGE 日报声明的主体数／实跑域数／返货腿数／新增数／清单外返货数与 run.json 实况对不上；零新增未勾声明或未带窗口；
                    有腿未取到却未点名；待核段缺 [待人工] 汇总

**它是形制闸，不是事实闸**：`exit 0` 只证明形制合式与自证一致，不证明数字为真——事实层由逐条回官方原文承担。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

# 与姊妹件逐字同源的四枚码（第五枚 E-LEDGER 属账本状态机面，本件无账本，故不启用）
E_LEGEND = {
    "E-FORMAT":   "形制/输入/表序不合式→按该行括号内规格改形制后复跑",
    "E-ANCHOR":   "锚/证据链缺失或断链→补合式锚或删除该条,禁虚构",
    "E-BANWORD":  "禁词/评级/幻觉/待人工域命中→改中性陈述或删除,零豁免区",
    "E-COVERAGE": "计数/覆盖/申报对不上→逐类补账或如实标未检索到",
}

SECTIONS = ['时点与范围', '今日新增', '近端变更', '需人工', '来源索引']
CN_NUM = ['一', '二', '三', '四', '五']
HEAD_MARKS = ('AI 整理初稿', '请回官方原文核对', '不构成投资建议')
TIME_KEYS = (('asof 时刻', 'YYYY-MM-DD 或 YYYY-MM-DD HH:MM'),
             ('清单规模', 'N 家，须与 run.json 的 subjects 一致'),
             ('本次实跑域数', '取自返货回显，不外推'),
             ('本次返货腿数', '返货实际覆盖的腿数'),
             ('上次快照日期', 'YYYY-MM-DD 或「无（首次运行）」'),
             ('检索窗口', 'YYYY-MM-DD~YYYY-MM-DD'),
             ('清单外返货（未并入本清单）', 'N 条，与 run.json 的 offlist_skipped 一致；零条也写 0，不删行'))
DATE = re.compile(r'\d{4}-\d{2}-\d{2}')
ASOF = re.compile(r'^\d{4}-\d{2}-\d{2}([ T]\d{2}:\d{2}(:\d{2})?)?$')
URL = re.compile(r'https?://|www\.|\.cn|\.com|\.gov|巨潮|交易所')
BANNED = re.compile(r'风险等级|风险评级|信用评级|违约概率|评分模型|目标价|评级为|建议买入|建议卖出|'
                    r'看涨|看跌|走势|涨停|抄底|资金流向|北向资金|持续监控|自动提醒|每天推给你|'
                    r'无风险|没有风险|没被查过|从未被查')
NEG_WORDS = ('不', '未', '禁', '勿', '拒', '非', '没')
CLAUSE_SPLIT = re.compile(r'[。；;！!？?：:，,、〕）」』]')
NUM = re.compile(r'(\d+)')


def clause_before(line, start):
    idx = 0
    for m in CLAUSE_SPLIT.finditer(line[:start]):
        idx = m.end()
    return line[idx:start]


def guarded(line, m):
    """否定式免责句不算违例：只看命中点所在小句内有无否定词。"""
    return any(n in clause_before(line, m.start()) for n in NEG_WORDS)


def blank(s: str) -> bool:
    s = s.strip()
    return (not s) or set(s) <= {'-', '—'} or '__' in s or s in {'☐', '－', '—'}


def cells(line: str):
    return [c.strip() for c in line.strip().strip('|').split('|')]


def row_items(lines, i0, i1):
    out = []
    for j in range(i0, i1):
        ln = lines[j]
        if not ln.strip().startswith('|'):
            continue
        cs = cells(ln)
        if not cs or set(cs[0]) <= {'-'} or cs[0] in {'#', '项'}:
            continue
        out.append((j, cs))
    return out


def ticks(cell: str):
    return re.findall(r'([☑☐])\s*([^☐☑]+)', cell)


def section_ranges(lines):
    heads = {}
    for i, ln in enumerate(lines):
        m = re.match(r'^##\s+([一二三四五六七八九])、(.+?)\s*$', ln)
        if m:
            heads.setdefault(m.group(2).strip(), i)
    order = sorted(heads.values())
    return {name: (idx, min([o for o in order if o > idx], default=len(lines)))
            for name, idx in heads.items()}


def check(path: Path, run_path: Path | None):
    lines = path.read_text(encoding='utf-8').split('\n')
    finds = []

    def add(code, lane, lineno, detail):
        finds.append(f"[{code}] [{lane}] 第 {lineno} 行：{detail}")

    run = None
    if run_path and run_path.is_file():
        try:
            run = json.loads(run_path.read_text(encoding='utf-8'))
        except json.JSONDecodeError:
            add('E-FORMAT', '实况', 1, f"{run_path.name} 不是合法 JSON（规格：计数比对以 run.json 实况为唯一凭据，坏了就重跑 digest.py）")
    elif run_path:
        add('E-FORMAT', '实况', 1, f"缺 {run_path.name}（规格：日报必须与本次 run.json 同目录成对交付，计数比对无从进行）")

    # ---- 道一 形制 ----
    hi = [i for i, ln in enumerate(lines) if ln.strip() == '## 头部自标']
    if not hi:
        add('E-FORMAT', '头部', 1, "缺「## 头部自标」段（规格：含『AI 整理初稿』『请回官方原文核对』『不构成投资建议』三件套）")
    else:
        i0 = hi[0]
        i1 = min([i for i, ln in enumerate(lines) if i > i0 and ln.startswith('## ')], default=len(lines))
        blob = '\n'.join(lines[i0:i1])
        for need in HEAD_MARKS:
            if need not in blob:
                add('E-FORMAT', '头部', i0 + 1, f"头部自标缺『{need}』（规格：三件套逐字齐）")
    secs = section_ranges(lines)
    for n, name in zip(CN_NUM, SECTIONS):
        if name not in secs:
            add('E-FORMAT', '五段', 1, f"缺「## {n}、{name}」段（规格：五段齐且按一二三四五有序）")
    if all(s in secs for s in SECTIONS):
        idx = [secs[s][0] for s in SECTIONS]
        if idx != sorted(idx):
            add('E-FORMAT', '五段', idx[0] + 1, "五段次序与契约不一致（规格：时点与范围→今日新增→近端变更→需人工→来源索引）")
    if '时点与范围' in secs:
        i0, i1 = secs['时点与范围']
        for key, spec in TIME_KEYS:
            hit = [j for j in range(i0, i1) if key in lines[j] and lines[j].strip().startswith('|')]
            if not hit:
                add('E-FORMAT', '时点', i0 + 1, f"时点段缺「{key}」一行（规格：{spec}）")
                continue
            j = hit[0]
            cs = cells(lines[j])
            val = cs[1] if len(cs) > 1 else ''
            if blank(val):
                add('E-FORMAT', '时点', j + 1, f"「{key}」未填（规格：{spec}）")
            elif key == 'asof 时刻' and not ASOF.match(val):
                add('E-FORMAT', '时点', j + 1, f"「asof 时刻」不是日期形（规格：{spec}）")
            elif key == '检索窗口' and not (val.count('~') == 1 and all(DATE.fullmatch(x.strip()) for x in val.split('~'))):
                add('E-FORMAT', '时点', j + 1, f"「检索窗口」没给起止两个日期（规格：{spec}）")
    if '来源索引' in secs:
        i0, i1 = secs['来源索引']
        if 'sources.jsonl' not in '\n'.join(lines[i0:i1]):
            add('E-FORMAT', '来源', i0 + 1, "来源索引段没点名 sources.jsonl（规格：日报与逐条来源索引件一一对应，缺对应物即无从回查）")

    # ---- 道二 锚 ----
    if '今日新增' in secs:
        i0, i1 = secs['今日新增']
        for j, cs in row_items(lines, i0, i1):
            if len(cs) < 6 or all(blank(c) for c in cs[1:]):
                continue
            if not DATE.search(cs[4]):
                add('E-ANCHOR', '新增日期', j + 1, "该行缺事件日期（规格：照返货逐字填 YYYY-MM-DD）")
            if not URL.search(cs[5]):
                add('E-ANCHOR', '新增出处', j + 1, "该行出处锚不合规（规格：官方链接或公告编号；取不到就删该行，不补猜）")
    if '近端变更' in secs:
        i0, i1 = secs['近端变更']
        for j, cs in row_items(lines, i0, i1):
            if len(cs) < 5 or all(blank(c) for c in cs[1:]):
                continue
            if '不适用' in ' '.join(cs) or '取不到' in ' '.join(cs):
                continue
            if '→' not in cs[3] or any(blank(x) for x in cs[3].split('→')):
                add('E-ANCHOR', '变更两值', j + 1, "前值／现值不成对（规格：要「前值 → 现值」两侧齐；取不到前值就明写取不到，不编造）")
            if not URL.search(cs[4]):
                add('E-ANCHOR', '变更出处', j + 1, "该行依据锚不合规（规格：同上，须能回查）")
    if '来源索引' in secs:
        i0, i1 = secs['来源索引']
        for j, cs in row_items(lines, i0, i1):
            if len(cs) < 3 or all(blank(c) for c in cs[1:]) or '不适用' in ' '.join(cs):
                continue
            if not URL.search(cs[1]):
                add('E-ANCHOR', '来源锚', j + 1, "来源索引行缺出处（规格：与 sources.jsonl 逐条对应的出处链接或公告编号）")

    # ---- 道三 红线 ----
    judge0, judge1 = secs.get('需人工', (-1, -1))
    for j, ln in enumerate(lines):
        if judge0 <= j < judge1:
            continue
        for m in BANNED.finditer(ln):
            if guarded(ln, m) or '[待人工]' in ln:
                continue
            add('E-BANWORD', '评级行情', j + 1, f"命中「{m.group(0)}」——评级／目标价／走势／行情资金流承诺与「无风险」类断言只许挂在第四段（规格：SKILL §4；其余段落要写就同行挂 [待人工]，或改中性陈述）")
            break

    # ---- 道四 计数与申报 ----
    if run:
        want = [('清单规模', run.get('subjects'), '家'),
                ('本次实跑域数', run.get('legs_called'), ''),
                ('本次返货腿数', run.get('legs_returned'), ''),
                ('清单外返货（未并入本清单）', run.get('offlist_skipped'), '条')]
        i0, i1 = secs.get('时点与范围', (0, len(lines)))
        for key, val, unit in want:
            if val is None:
                continue
            hit = [j for j in range(i0, i1) if key in lines[j]]
            if not hit:
                continue
            got = NUM.search(cells(lines[hit[0]])[1] if len(cells(lines[hit[0]])) > 1 else '')
            if not got or int(got.group(1)) != int(val):
                add('E-COVERAGE', '计数比对', hit[0] + 1, f"「{key}」与 run.json 实况（{val}{unit}）对不上（规格：计数一律取本次返货回显，不凭记忆、不外推）")
        i0, i1 = secs['今日新增'] if '今日新增' in secs else (0, len(lines))
        listed = [cs for _, cs in row_items(lines, i0, i1) if len(cs) >= 6 and not all(blank(c) for c in cs[1:])]
        new_count = run.get('new_count')
        if new_count is not None and len(listed) != int(new_count):
            add('E-COVERAGE', '新增数', i0 + 1, f"今日新增列出 {len(listed)} 行，run.json 记 {new_count} 条（规格：两者必须相等，多写少写都是虚报）")
        decl = [ln for ln in lines[i0:i1] if '零新增声明' in ln]
        if new_count == 0:
            picked = [w for ln in decl for mk, w in ticks(ln) if mk == '☑']
            if not any('未检索到' in w for w in picked):
                add('E-COVERAGE', '零新增申报', i0 + 1, "零新增却没勾「窗口内未检索到新增」（规格：没检索到 ≠ 没有发生，必须勾声明并带窗口日期）")
            elif not any(DATE.search(w) for w in picked):
                add('E-COVERAGE', '零新增申报', i0 + 1, "零新增声明没带窗口起止日期（规格：要能核对到检索参数，否则与「没跑」无从区分）")
        elif decl and any('未检索到' in w for ln in decl for mk, w in ticks(ln) if mk == '☑'):
            add('E-COVERAGE', '零新增申报', i0 + 1, "run.json 记有新增却勾了「未检索到新增」（规格：申报与实况互斥，二者必居其一）")
        miss = [ln for ln in lines if '本腿未取到' in ln]
        called, got_legs = run.get('legs_called'), run.get('legs_returned')
        if isinstance(called, int) and isinstance(got_legs, int) and called > got_legs and not miss:
            add('E-COVERAGE', '缺腿点名', 1, f"实跑 {called} 域而返货只覆盖 {got_legs} 腿，日报未点名「本腿未取到」（规格：一腿挂不挡全篇，但必须点名挂第四段待人工）")
    if '需人工' in secs:
        i0, i1 = secs['需人工']
        if '[待人工]' not in '\n'.join(lines[i0:i1]):
            add('E-COVERAGE', '汇总', i0 + 1, "需人工段缺 [待人工] 汇总位（规格：评级／目标价／走势与资金面解读全挂此节）")
    return finds, len(lines)


def report(path, finds, n):
    if finds:
        print(f"FAIL: {path.name}（{len(finds)} 条）")
        for f in finds:
            print('  - ' + f)
        codes = sorted({re.match(r'\[(E-[A-Z]+)\]', f).group(1) for f in finds})
        print('  码表: ' + '; '.join(f'{c}→{E_LEGEND[c]}' for c in codes))
        return 1
    print("PASS: " + path.name + "（五段齐、时点七项落成日期形、每行有锚、评级与行情承诺零命中、五类计数与 run.json 对上）")
    print(f"       扫过 {n} 行，发条 0 条；判定与阈值全集以本脚本现值为准（--help 看四道说明）")
    return 0


def selftest():
    gd = HERE / 'fixtures' / 'good-digest.md'
    gr = HERE / 'fixtures' / 'good-run.json'
    zd = HERE / 'fixtures' / 'zero-digest.md'
    zr = HERE / 'fixtures' / 'zero-run.json'
    bd = HERE / 'fixtures' / 'bad-digest.md'
    br = HERE / 'fixtures' / 'bad-run.json'
    for f in (gd, gr, zd, zr, bd, br):
        if not f.is_file():
            print(f"SELFTEST FAIL: 守护样缺失 {f}")
            return 1
    gf, gnl = check(gd, gr)
    zf, znl = check(zd, zr)
    bf, bnl = check(bd, br)
    got = {re.match(r'\[(E-[A-Z]+)\]', x).group(1) for x in bf}
    want = set(E_LEGEND)
    ok = True
    print(f"selftest 好样：{gd.name} 扫过 {gnl} 行，发条 {len(gf)} 条（规格 0）")
    for x in gf:
        print('   意外发条 → ' + x)
        ok = False
    print(f"selftest 零新增样：{zd.name} 扫过 {znl} 行，发条 {len(zf)} 条（规格 0，形制＝第二段勾「未检索到新增」带窗口）")
    for x in zf:
        print('   意外发条 → ' + x)
        ok = False
    zrun = json.loads(zr.read_text(encoding='utf-8'))
    zdecl = [ln for ln in zd.read_text(encoding='utf-8').split('\n') if '零新增声明' in ln]
    zticked = [w for ln in zdecl for mk, w in ticks(ln) if mk == '☑']
    if zrun.get('new_count') != 0 or not any('未检索到' in w and DATE.search(w) for w in zticked):
        print('   零新增样自身不合式 → new_count=%s，勾选项=%s' % (zrun.get('new_count'), zticked))
        ok = False
    print(f"selftest 坏样：{bd.name} 扫过 {bnl} 行，发条 {len(bf)} 条（规格 ≥1 且四道全发）")
    missing = sorted(want - got)
    if missing:
        print('   未发出的码 → ' + ', '.join(missing))
        ok = False
    print(f"selftest: {'ALL GREEN' if ok else 'FAIL'}（好样 0/{len(gf)} · 零新增样 0/{len(zf)} · 坏样四道 {len(got)}/{len(want)}）")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description='校验一份增量日报是否合五段契约与红线（零网络）。',
                                 epilog='出口：FAIL 一行计数＋逐条 E-* 详行＋码表；PASS 一行＋两类计数。判定全集在本脚本现值。')
    ap.add_argument('digest', nargs='?', help='待校验的日报（markdown）')
    ap.add_argument('--run', help='同次运行的 run.json（缺省取日报同目录）')
    ap.add_argument('--selftest', action='store_true', help='跑包内两件守护样（好样须过、坏样四道全发）')
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if not args.digest:
        ap.error('缺参数：给一份日报，或用 --selftest')
    p = Path(args.digest)
    if not p.is_file():
        print(f"[出错] 文件不存在：{p}")
        return 1
    rp = Path(args.run) if args.run else p.parent / 'run.json'
    finds, n = check(p, rp)
    return report(p, finds, n)


if __name__ == '__main__':
    sys.exit(main())
