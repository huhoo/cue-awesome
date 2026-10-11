#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_memo.py — 校验一份投决备忘录草稿是否合 `SKILL.md` §3/§4/§5 契约（纯本地零网络）。

用法：
    python3 check_memo.py <memo.md> [--run <run.json>]     校验一份草稿（--run 缺省取同目录 run.json）
    python3 check_memo.py --selftest                       四档自证（下详）
    python3 check_memo.py --help                           本说明

四档自证（反证矩阵长在脚本里，不另出包外探针件）：
    一档 合规稿须过（发条 0）
    二档 两枚违例样须各自发红、码与道名相符（反方缺一侧／无锚数）
    三档 空模板必须 FAIL（留占位＝违例，不是合规）
    四档 反证矩阵：对合规稿做单点破坏，每枚必须发出预期的码与道名；另附正向不误拦。
         锚点是「合规稿里唯一命中的那行」——锚失配即判该枚不符，所以守护样漂移或某道被拆弱都会先叫。

出口形制（与姊妹件同族）：失败＝一行 "FAIL: <文件>（N 条）" ＋逐条先打 `E-*` 码的详行 ＋末行「码表:」；
全过＝一行 "PASS: <文件>（…）" 并印「扫过行数」「发条数」。行数口径：`扫过 N 行` 按 `split('\n')` 计
＝`wc -l` 现值 +1。

四道（判定全集在本脚本；SKILL §5 那张表是验收合同）：
    道一 E-FORMAT   七节齐且有序＋四件自标与三句边界在位＋快照时点与日期落成 YYYY-MM-DD＋来源索引点名 sources.jsonl
    道二 E-ANCHOR   数值行缺出处锚或缺定位；锚为空或占位；业务行缺可指到的出处；来源行缺出处
    道三 E-COVERAGE 反方缺一侧；缺数清单为空却正文有「未取到」；七类计数与 run.json 对不上；表内合计与分项不 tie
    道四 E-BANWORD  评级／目标价／买卖建议／估值测算／走势与行情承诺／「无风险」类断言落在第六节之外且未挂 `[待人工]`

**它是形制闸，不是事实闸**：`exit 0` 只证明形制合式且与本次 run.json 自证一致，不证明数字为真——
事实层由逐条回官方原文核对承担，交付面必须这样写。
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import tempfile
from decimal import Decimal, InvalidOperation
from pathlib import Path

HERE = Path(__file__).resolve().parent

# 与姊妹件逐字同源的四枚码（第五枚 E-LEDGER 属账本状态机面，本件无账本，故明写不启用）
E_LEGEND = {
    "E-FORMAT":   "形制/输入/表序不合式→按该行括号内规格改形制后复跑",
    "E-ANCHOR":   "锚/证据链缺失或断链→补合式锚或删除该条,禁虚构",
    "E-BANWORD":  "禁词/评级/幻觉/待人工域命中→改中性陈述或删除,零豁免区",
    "E-COVERAGE": "计数/覆盖/申报对不上→逐类补账或如实标未检索到",
}

SECTIONS = ['摘要', '事实与数字', '业务与行业要点', '风险与反方', '缺数与未决', '人工复核清单', '来源索引']
CN = ['一', '二', '三', '四', '五', '六', '七']
HEAD_MARKS = ('AI 整理初稿', '请回官方原文核对', '不构成投资建议', '不构成决议')
BOUNDARY_MARKS = ('不决议只起草', '不评级、不给目标价', '不含估值测算', '适用性声明')
DATE = re.compile(r'\d{4}-\d{2}-\d{2}')
DATE_FULL = re.compile(r'^\d{4}-\d{2}-\d{2}$')
ASOF = re.compile(r'^\d{4}-\d{2}-\d{2}([ T]\d{2}:\d{2}(:\d{2})?)?$')
URL = re.compile(r'https?://|www\.|\.cn|\.com|\.gov|cninfo|巨潮|交易所|证监会|问询|函|公告|编号|document_number')
NA = ('不适用', '未取到', '本次无', '—', '-', '')
BANNED = re.compile(r'风险等级|风险评级|信用评级|主体评级|违约概率|评分模型|给分|目标价|评级为|买入|卖出|'
                    r'看涨|看跌|走势|涨停|抄底|加仓|减仓|稳赚|包赚|无风险|没有风险|没被查过|从未被查|'
                    r'合理估值|估值合理|目标估值|估值为|DCF 测算|测算得出|市盈率给|倍数为|资金流向|北向资金|'
                    r'持续监控|自动发布|自动表决')
NEG_WORDS = ('不', '未', '禁', '勿', '拒', '非', '没')
CLAUSE_SPLIT = re.compile(r'[。；;！!？?：:，,、〕）」』]')
NUM = re.compile(r'(\d+)')
SUMMARY_COUNTS = re.compile(r'事实与数字 (\d+) 条、业务要点 (\d+) 条、看多 (\d+) 条、看空 (\d+) 条；缺数与未决 (\d+) 条')
SIDE_COUNTS = re.compile(r'两方条数：看多 (\d+) 条、看空 (\d+) 条')


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
    return (not s) or set(s) <= {'-', '—'} or '__' in s or s in {'☐', '－'}


def cells(line: str):
    return [c.strip() for c in line.strip().strip('|').split('|')]


def section_ranges(lines):
    heads = {}
    for i, ln in enumerate(lines):
        m = re.match(r'^##\s+([一二三四五六七八九])、(.+?)\s*$', ln)
        if m:
            heads.setdefault(m.group(2).strip(), i)
    order = sorted(heads.values())
    return {name: (idx, min([o for o in order if o > idx], default=len(lines)))
            for name, idx in heads.items()}


def table(lines, i0, i1):
    """返回 [(行号, 单元格列表)]，跳过分隔行与列名行。"""
    out = []
    for j in range(i0, i1):
        ln = lines[j]
        if not ln.strip().startswith('|'):
            continue
        cs = cells(ln)
        if not cs or set(cs[0]) <= {'-'} or cs[0] == '#':
            continue
        out.append((j, cs))
    return out


def header_map(lines, i0, i1):
    for j in range(i0, i1):
        ln = lines[j]
        if ln.strip().startswith('|') and cells(ln)[0] == '#':
            return {name: k for k, name in enumerate(cells(ln))}
    return {}


def col(hmap, names, default=None):
    for n in names:
        if n in hmap:
            return hmap[n]
    return default


def dec(v):
    s = str(v).replace(',', '').strip()
    m = re.search(r'-?\d+(\.\d+)?', s)
    if not m:
        return None
    try:
        return Decimal(m.group(0))
    except InvalidOperation:
        return None


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
            add('E-FORMAT', '实况', 1, f"{run_path.name} 不是合法 JSON（规格：计数比对以 run.json 实况为唯一凭据，坏了就重跑 build_memo.py）")
    elif run_path:
        add('E-FORMAT', '实况', 1, f"缺 {run_path.name}（规格：草稿必须与本次 run.json 同目录成对交付，计数比对无从进行）")

    # ---- 道一 形制 ----
    hi = [i for i, ln in enumerate(lines) if ln.strip() == '## 头部自标']
    if not hi:
        add('E-FORMAT', '头部', 1, "缺「## 头部自标」段（规格：四件自标＋三句边界，见 SKILL §0／§4）")
    else:
        i0 = hi[0]
        i1 = min([i for i, ln in enumerate(lines) if i > i0 and ln.startswith('## ')], default=len(lines))
        blob = '\n'.join(lines[i0:i1])
        for need in HEAD_MARKS:
            if need not in blob:
                add('E-FORMAT', '头部', i0 + 1, f"头部自标缺『{need}』（规格：四件逐字齐）")
        for need in BOUNDARY_MARKS:
            if need not in blob:
                add('E-FORMAT', '边界', i0 + 1, f"能力边界句缺『{need}』（规格：不决议只起草／不评级不目标价／不含估值测算只做适用性声明，三句原样在位）")
    secs = section_ranges(lines)
    for n, name in zip(CN, SECTIONS):
        if name not in secs:
            add('E-FORMAT', '七节', 1, f"缺「## {n}、{name}」段（规格：七节齐且按一二三四五六七有序，段名与 SKILL §3 逐字一致）")
    if all(s in secs for s in SECTIONS):
        idx = [secs[s][0] for s in SECTIONS]
        if idx != sorted(idx):
            add('E-FORMAT', '七节', idx[0] + 1, "七节次序与契约不一致（规格：摘要→事实与数字→业务与行业要点→风险与反方→缺数与未决→人工复核清单→来源索引）")
    if '摘要' in secs:
        i0, i1 = secs['摘要']
        m = re.search(r'快照时点\s+(\S+)', '\n'.join(lines[i0:i1]))
        if not m:
            add('E-FORMAT', '时点', i0 + 1, "摘要段没给快照时点（规格：首行写「快照时点 YYYY-MM-DD[ HH:MM]」，一切计数带 asof）")
        elif not ASOF.match(m.group(1)):
            add('E-FORMAT', '时点', i0 + 1, f"快照时点「{m.group(1)}」不是日期形（规格：YYYY-MM-DD 或 YYYY-MM-DD HH:MM）")
    for sec in ('事实与数字', '风险与反方'):
        if sec not in secs:
            continue
        i0, i1 = secs[sec]
        hm = header_map(lines, i0, i1)
        di = col(hm, ['日期'])
        if di is None:
            continue
        for j, cs in table(lines, i0, i1):
            if len(cs) <= di or all(blank(c) for c in cs[1:]):
                continue
            val = cs[di]
            if val in NA:
                continue
            if not DATE_FULL.match(val):
                add('E-FORMAT', '日期', j + 1, f"日期列「{val[:24]}」不是 YYYY-MM-DD（规格：日期只用返货给的日期位，带补齐时刻的形制只取到日）")
    if '来源索引' in secs:
        i0, i1 = secs['来源索引']
        if 'sources.jsonl' not in '\n'.join(lines[i0:i1]):
            add('E-FORMAT', '来源', i0 + 1, "来源索引段没点名 sources.jsonl（规格：草稿与逐条来源索引件一一对应，缺对应物即无从回查）")

    # ---- 道二 锚 ----
    for sec in ('事实与数字', '风险与反方'):
        if sec not in secs:
            continue
        i0, i1 = secs[sec]
        hm = header_map(lines, i0, i1)
        si = col(hm, ['出处锚', '出处'])
        li = col(hm, ['定位'])
        if si is None:
            continue
        for j, cs in table(lines, i0, i1):
            joined = ' '.join(cs)
            if all(blank(c) for c in cs[1:]) or '本次无' in joined or '未取到' in joined or '不适用' in joined:
                continue
            if '合计' in cs:  # 合计行由道四按同口径分项复算，不在此道要求外部锚
                continue
            if len(cs) <= si or not URL.search(cs[si]):
                add('E-ANCHOR', '数值锚', j + 1, "该行缺合规出处锚（规格：官方链接或公告／问询编号；锚取不到就删该行并落第五节，不补猜）")
            if li is not None and len(cs) > li and blank(cs[li]):
                add('E-ANCHOR', '数值定位', j + 1, "该行定位格留空（规格：页码或字符区间，返货给什么写什么；没有就删该行）")
    if '业务与行业要点' in secs:
        i0, i1 = secs['业务与行业要点']
        hm = header_map(lines, i0, i1)
        si = col(hm, ['出处锚', '出处'])
        if si is not None:
            for j, cs in table(lines, i0, i1):
                if all(blank(c) for c in cs[1:]) or '本次无' in ' '.join(cs) or '不适用' in ' '.join(cs):
                    continue
                if len(cs) <= si or not URL.search(cs[si]):
                    add('E-ANCHOR', '业务锚', j + 1, "该行缺可指到的出处（规格：只写返货或材料里能指到的陈述；行业语境无腿就写「本件无行业数据腿」）")
    if '来源索引' in secs:
        i0, i1 = secs['来源索引']
        hm = header_map(lines, i0, i1)
        si = col(hm, ['出处'])
        if si is not None:
            for j, cs in table(lines, i0, i1):
                if all(blank(c) for c in cs[1:]) or '本次无' in ' '.join(cs) or '不适用' in ' '.join(cs):
                    continue
                if len(cs) <= si or not (URL.search(cs[si]) or '用户材料' in cs[si]):
                    add('E-ANCHOR', '来源锚', j + 1, "来源索引行缺出处（规格：与 sources.jsonl 逐条对应；材料行要写明「用户材料：标题（路径）」）")

    # ---- 道三 红线 ----
    judge0, judge1 = secs.get('人工复核清单', (-1, -1))
    for j, ln in enumerate(lines):
        if judge0 <= j < judge1:
            continue
        for m in BANNED.finditer(ln):
            if guarded(ln, m) or '[待人工]' in ln:
                continue
            add('E-BANWORD', '判断词', j + 1, f"命中「{m.group(0)}」——评级／目标价／买卖建议／估值测算／走势与行情承诺与「无风险」类断言只许挂在第六节（规格：SKILL §4；要写就同行挂 [待人工]，或改中性陈述）")
            break

    # ---- 道四 计数、反方、合计 ----
    if run:
        listed = {}
        if '事实与数字' in secs:
            i0, i1 = secs['事实与数字']
            hm = header_map(lines, i0, i1)
            gi, ti = col(hm, ['组']), col(hm, ['事实／指标'])
            listed['fact_rows'] = len([cs for _, cs in table(lines, i0, i1)
                                       if ti is not None and len(cs) > ti and cs[ti] != '合计'
                                       and '不合计' not in ' '.join(cs)])
        if '业务与行业要点' in secs:
            i0, i1 = secs['业务与行业要点']
            listed['business_rows'] = len([cs for _, cs in table(lines, i0, i1) if '本次无' not in ' '.join(cs)])
        if '风险与反方' in secs:
            i0, i1 = secs['风险与反方']
            side, b_rows, k_rows = None, [], []
            for ln in lines[i0:i1]:
                if '看多依据' in ln:
                    side = 'b'
                elif '看空依据' in ln:
                    side = 'k'
                elif ln.strip().startswith('|'):
                    cs = cells(ln)
                    if not cs or set(cs[0]) <= {'-'} or cs[0] == '#' or all(blank(c) for c in cs[1:]):
                        continue
                    (b_rows if side == 'b' else k_rows).append(cs)
            listed['bull_rows'], listed['bear_rows'] = len(b_rows), len(k_rows)
        if '缺数与未决' in secs:
            i0, i1 = secs['缺数与未决']
            listed['gap_rows'] = len([cs for _, cs in table(lines, i0, i1) if '本次无缺数' not in ' '.join(cs)])
        if '来源索引' in secs:
            i0, i1 = secs['来源索引']
            listed['source_rows'] = len([cs for _, cs in table(lines, i0, i1) if '本次无' not in ' '.join(cs)])

        for key, label in (('fact_rows', '事实与数字条数'), ('business_rows', '业务要点条数'),
                           ('bull_rows', '看多条数'), ('bear_rows', '看空条数'),
                           ('gap_rows', '缺数与未决条数'), ('source_rows', '来源枚数')):
            val = run.get(key)
            if val is None:
                continue
            got = listed.get(key)
            if got is None:
                continue
            if int(val) != got:
                add('E-COVERAGE', '计数比对', secs.get('摘要', (0, 0))[0] + 1,
                    f"{label}：正文列出 {got}，run.json 记 {val}（规格：计数一律取本次运行账，不凭记忆、不外推；两处不符必有一处虚报）")
        sline = re.search(SUMMARY_COUNTS.pattern, '\n'.join(lines[secs['摘要'][0]:secs['摘要'][1]])) if '摘要' in secs else None
        if sline:
            for got_v, key in zip(sline.groups(), ('fact_rows', 'business_rows', 'bull_rows', 'bear_rows', 'gap_rows')):
                if run.get(key) is not None and int(got_v) != int(run[key]):
                    add('E-COVERAGE', '摘要条数句', secs['摘要'][0] + 1,
                        f"摘要写「{key}={got_v}」而 run.json 记 {run[key]}（规格：摘要里的条数取自本次运行账回显，禁凭记忆）")
        dline = re.search(SIDE_COUNTS.pattern, '\n'.join(lines[secs['风险与反方'][0]:secs['风险与反方'][1]])) if '风险与反方' in secs else None
        if dline:
            for got_v, key in zip(dline.groups(), ('bull_rows', 'bear_rows')):
                if run.get(key) is not None and int(got_v) != int(run[key]):
                    add('E-COVERAGE', '两方条数句', secs['风险与反方'][0] + 1,
                        f"两方条数句写 {key}={got_v} 而 run.json 记 {run[key]}（规格：不等就照实写不等，但数要来自本次账）")
        bull, bear = run.get('bull_rows'), run.get('bear_rows')
        if isinstance(bull, int) and isinstance(bear, int):
            if bull == 0 or bear == 0:
                add('E-COVERAGE', '反方缺一侧', secs.get('风险与反方', (1, 1))[0] + 1,
                    f"本次看多 {bull} 条／看空 {bear} 条——两侧缺一侧即不成文（规格：SKILL §0「bull 与 bear 各至少一条」，本件不得出一半再补）")
            elif listed.get('bull_rows') == 0 or listed.get('bear_rows') == 0:
                add('E-COVERAGE', '反方缺一侧', secs.get('风险与反方', (1, 1))[0] + 1,
                    "账上有两侧、正文却少一侧（规格：两栏都要成表，缺一侧＝不成文）")
        gap_txt = '\n'.join(lines[secs['缺数与未决'][0]:secs['缺数与未决'][1]]) if '缺数与未决' in secs else ''
        gap_table = table(lines, *secs['缺数与未决']) if '缺数与未决' in secs else []
        gap_named = [cs for _, cs in gap_table if '本次无缺数' not in ' '.join(cs)]
        if '未取到' in '\n'.join(lines) and (not gap_named or '本次无缺数与未决申报' in gap_txt):
            add('E-COVERAGE', '缺数互证', secs.get('缺数与未决', (1, 1))[0] + 1,
                "正文出现「未取到」而缺数清单没逐条列它（规格：取不到的行必须落第五节点名，不能只在正文里说一句）")
        if '事实与数字' in secs:
            i0, i1 = secs['事实与数字']
            hm = header_map(lines, i0, i1)
            gi, ti, vi = col(hm, ['组']), col(hm, ['事实／指标']), col(hm, ['数值'])
            si = col(hm, ['出处锚'])
            all_rows = table(lines, i0, i1)
            for j, cs in all_rows:
                if ti is None or len(cs) <= ti or cs[ti] != '合计':
                    continue
                gname = cs[gi] if gi is not None and len(cs) > gi else ''
                total = dec(cs[vi]) if vi is not None and len(cs) > vi else None
                parts = NUM.search(cs[si]) if si is not None and len(cs) > si else None
                rows = [c2 for _, c2 in all_rows if gi is not None and len(c2) > gi and c2[gi] == gname and c2[ti] != '合计']
                vals = [dec(c2[vi]) for c2 in rows] if vi is not None else []
                if total is None or any(v is None for v in vals):
                    continue
                if sum(vals) != total:
                    add('E-COVERAGE', '合计 tie', j + 1,
                        f"「{gname}」合计写 {total}，本组分项相加＝{sum(vals)}（规格：合计只由本次同口径分项逐条相加，不引外部数、不取平均；不 tie 即虚报）")
                if parts and int(parts.group(1)) != len(rows):
                    add('E-COVERAGE', '合计 tie', j + 1,
                        f"「{gname}」合计声明 {parts.group(1)} 枚分项，本组实有 {len(rows)} 行（规格：声明的分项数要与表内同组行数一致）")
                tmeta = (run.get('totals') or {}).get(gname)
                if tmeta is not None and dec(tmeta) != total:
                    add('E-COVERAGE', '计数比对', j + 1,
                        f"「{gname}」合计与 run.json 记值（{tmeta}）不符（规格：账与稿同源，两处不一致必有一处错）")
            for gname, why in (run.get('mixed_groups') or {}).items():
                if not any(gname in ' '.join(cs) and '不合计' in ' '.join(cs) for _, cs in all_rows):
                    add('E-COVERAGE', '口径不齐点名', i0 + 1,
                        f"账上记「{gname}」口径不齐（{why}）却未在表内点名（规格：不齐就不合计并写明不合计，不悄悄合）")

    if '人工复核清单' in secs:
        i0, i1 = secs['人工复核清单']
        if '[待人工]' not in '\n'.join(lines[i0:i1]):
            add('E-COVERAGE', '汇总', i0 + 1, "人工复核清单缺 [待人工] 挂位（规格：评级／目标价／估值倍数／走势与资金面全部只在此节留位）")
    return finds, len(lines)


def report(path, finds, n):
    if finds:
        print(f"FAIL: {path.name}（{len(finds)} 条）")
        for f in finds:
            print('  - ' + f)
        codes = sorted({re.match(r'\[(E-[A-Z]+)\]', f).group(1) for f in finds})
        print('  码表: ' + '; '.join(f'{c}→{E_LEGEND[c]}' for c in codes))
        return 1
    print("PASS: " + path.name + "（七节齐、自标与边界在位、每行有锚、判断词零命中、七类计数与 run.json 对上、合计 tie）")
    print(f"       扫过 {n} 行，发条 0 条；判定与阈值全集以本脚本现值为准（--help 看四道说明）")
    return 0


def _lane(finding):
    m = re.match(r'\[(E-[A-Z]+)\] \[([^\]]+)\]', finding)
    return (m.group(1), m.group(2)) if m else ('?', '?')


def probe_matrix(md, run, tmp: Path):
    """第四档：单点破坏每枚必须发出预期的码与道名；正向不误拦必须零发条。

    锚点从合规稿现场取（要求唯一命中）；锚失配＝该枚判 FAIL 并说明命中几处——
    守护样漂移或某道判定被拆弱都会先叫，不让破坏样静默"通过"（防恒真）。"""
    out = []

    def one(name, expect, md2, run2, anchor_n=1):
        exp = expect if isinstance(expect, str) else '%s／%s' % expect
        if anchor_n != 1:
            out.append((name, exp, '锚失配（合规稿里命中 %d 处）' % anchor_n, False, []))
            return
        d = tmp / name
        d.mkdir(parents=True, exist_ok=True)
        f = d / 'memo.md'
        f.write_text(md2, encoding='utf-8')
        rp = d / 'run.json'
        rp.write_text(json.dumps(run2, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
        finds, _n = check(f, rp)
        lanes = [_lane(x) for x in finds]
        if expect == '零发条':
            got = '零发条' if not lanes else '误拦：%s／%s（共 %d 条）' % (lanes[0][0], lanes[0][1], len(lanes))
            out.append((name, exp, got, not lanes, finds))
        else:
            hit = next((i for i, l in enumerate(lanes, 1) if l == expect), 0)
            got = ('%s／%s（第 %d／共 %d 条）' % (expect[0], expect[1], hit, len(lanes)) if hit else
                   ('未命中：零发条' if not lanes else '未命中：首条 %s／%s（共 %d 条）' % (lanes[0][0], lanes[0][1], len(lanes))))
            out.append((name, exp, got, bool(hit), finds))

    def replace_once(text, old, new, tag):
        n = text.count(old)
        if n != 1:
            return text, n
        return text.replace(old, new, 1), 1

    lines = md.split('\n')

    def row(prefix):
        hits = [ln for ln in lines if ln.startswith(prefix)]
        return hits[0] if len(hits) == 1 else None, len(hits)

    head_line, n_head = row('- 本件状态：')
    bound_line, n_bound = row('- 能力边界：')
    fact_row, n_fact = row('| 1 | 营业收入 | 营业收入 |')
    total_row = None
    total_idx = 0
    n_total = 0
    vcol_idx = None
    for ln in lines:
        if ln.startswith('| # | 组 |'):
            vcol_idx = cells(ln).index('数值')
        if ln.startswith('| ') and '合计' in cells(ln)[:4]:
            total_row, n_total = ln, n_total + 1
    total_idx = vcol_idx if vcol_idx is not None else 0
    bull_row, n_bull = row('| 1 | 收入连续两期')
    bear_row, n_bear = row('| 1 | 受限资金占比')
    src_line, n_src = row('与同目录 sources.jsonl')
    biz_row, n_biz = row('| 1 | 主营构成')
    sec7 = [i for i, ln in enumerate(lines) if ln.startswith('## 七、来源索引')]

    def set_col(rowstr, idx, val):
        cs = cells(rowstr)
        if idx >= len(cs):
            return rowstr
        cs[idx] = val
        return '| ' + ' | '.join(cs) + ' |'

    t, n = replace_once(md, '，快照时点 ', '，本稿时点另记 ', 'PB1')
    one('PB1-摘要没给时点', ('E-FORMAT', '时点'), t, run, n)
    t, n = replace_once(md, head_line, '- 本件状态：**AI 整理初稿**。', 'PB2')
    one('PB2-自标缺件', ('E-FORMAT', '头部'), t, run, n)
    t, n = replace_once(md, bound_line, '- 能力边界：本节奏另定。', 'PB3')
    one('PB3-边界句缺失', ('E-FORMAT', '边界'), t, run, n)
    t, n = replace_once(md, fact_row, set_col(fact_row, 6, '____'), 'PB4')
    one('PB4-日期留占位', ('E-FORMAT', '日期'), t, run, n * (1 if n_fact == 1 else 0))
    t, n = replace_once(md, fact_row, set_col(fact_row, 7, '—'), 'PB5')
    one('PB5-出处锚删空', ('E-ANCHOR', '数值锚'), t, run, n)
    t, n = replace_once(md, bull_row, set_col(bull_row, 6, ''), 'PB6')
    one('PB6-定位删空', ('E-ANCHOR', '数值定位'), t, run, n)
    t, n = replace_once(md, biz_row, set_col(biz_row, 2, '—'), 'PB7')
    one('PB7-业务行缺出处', ('E-ANCHOR', '业务锚'), t, run, n)
    t, n = replace_once(md, bull_row + '\n', '', 'PB8')
    one('PB8-看多删一行', ('E-COVERAGE', '计数比对'), t, run, n)
    bear_all = []
    grab = False
    for ln in lines:
        if ln.strip() == '**看空依据**':
            grab = True
            continue
        if grab and ln.startswith('**'):
            break
        if grab and ln.startswith('|'):
            cs = cells(ln)
            if cs and cs[0] != '#' and not set(cs[0]) <= {'-'} and not all(blank(c) for c in cs[1:]):
                bear_all.append(ln)
    t9 = md
    for ln in bear_all:
        t9 = t9.replace(ln + '\n', '', 1)
    one('PB9-反方缺一侧', ('E-COVERAGE', '反方缺一侧'), t9, run, 1 if bear_all else 0)
    t, n = replace_once(md, total_row, set_col(total_row, total_idx, '2400.0'), 'PB10')
    one('PB10-合计不 tie', ('E-COVERAGE', '合计 tie'), t, run, n)
    t, n = replace_once(md, src_line, '与同目录的清单文件对应；下表逐条给出处与快照时点。', 'PB11')
    one('PB11-来源段不点来源件', ('E-FORMAT', '来源'), t, run, n)
    gap_lines = [ln for ln in lines if (ln.startswith('| 1 | 或有负债') or ln.startswith('| 2 | 分季度毛利率'))]
    if len(gap_lines) == 2:
        t, n = replace_once(md, gap_lines[0] + '\n' + gap_lines[1],
                            '| 1 | 本次无缺数与未决申报 | 不适用（正文无「未取到」行） | — |', 'PB12a')
        t, n2 = replace_once(t, biz_row, biz_row + '\n\n> 分季度毛利率：本次未取到（窗口内无同口径披露）。', 'PB12b')
        one('PB12-正文未取到清单没列', ('E-COVERAGE', '缺数互证'), t, run, 1 if (n == 1 and n2 == 1) else 0)
    else:
        out.append(('PB12-正文未取到清单没列', 'E-COVERAGE／缺数互证',
                    f'锚失配（缺数样行命中 {len(gap_lines)} 处）', False, []))
    t, n = replace_once(md, '\n同一事实多源时并列两源', '\n> 机构给予买入评级，目标价 30 元。\n\n同一事实多源时并列两源', 'PB13')
    one('PB13-判断词入正文', ('E-BANWORD', '判断词'), t, run, n)
    if len(sec7) == 1:
        t = md[:sec7[0]]
        one('PB14-缺第七节', ('E-FORMAT', '七节'), t, run, 1)
    else:
        out.append(('PB14-缺第七节', 'E-FORMAT／七节', f'锚失配（第七节标题命中 {len(sec7)} 处）', False, []))

    # 正向不误拦：否定式免责句／两侧条数不等（同步改正文行＋两处条数句＋账）
    pos1, n1 = replace_once(md, biz_row, biz_row + '\n\n本稿不评级、不给目标价、不做估值测算，也不代用户表决。', 'POS1')
    one('POS1-否定式免责句合法', '零发条', pos1, run, n1)
    if n_bear == 1:
        pos2, na = replace_once(md, bear_row + '\n', '', 'POS2a')
        pos2, nb = replace_once(pos2, '两方条数：看多 2 条、看空 2 条', '两方条数：看多 2 条、看空 1 条', 'POS2b')
        pos2, nc = replace_once(pos2, '看多 2 条、看空 2 条；缺数与未决', '看多 2 条、看空 1 条；缺数与未决', 'POS2c')
        r2 = dict(run)
        r2['bear_rows'] = int(run.get('bear_rows', 2)) - 1
        one('POS2-两侧不等仍合法', '零发条', pos2, r2, 1 if {na, nb, nc} == {1} else 0)
    else:
        out.append(('POS2-两侧不等仍合法', '零发条', f'锚失配（看空首行命中 {n_bear} 处）', False, []))
    return out


def selftest():
    gd = HERE / 'fixtures' / 'good-memo.md'
    gr = HERE / 'fixtures' / 'good-run.json'
    wd = HERE / 'fixtures' / 'weak-side-memo.md'
    wr = HERE / 'fixtures' / 'weak-side-run.json'
    nd = HERE / 'fixtures' / 'no-anchor-memo.md'
    nr = HERE / 'fixtures' / 'no-anchor-run.json'
    tpl = HERE.parent / 'assets' / '投决备忘录.md'
    for f in (gd, gr, wd, wr, nd, nr, tpl):
        if not f.is_file():
            print(f"SELFTEST FAIL: 守护样缺失 {f}")
            return 1
    gf, gnl = check(gd, gr)
    wf, wnl = check(wd, wr)
    nf, nnl = check(nd, nr)
    tf, tnl = check(tpl, gr)
    ok = True
    print(f"selftest 一档合规稿：{gd.name} 扫过 {gnl} 行，发条 {len(gf)} 条（规格 0）")
    for x in gf:
        print('   意外发条 → ' + x)
        ok = False

    def expect(name, finds, code, lane, path, nl):
        nonlocal ok
        lanes = [_lane(x) for x in finds]
        hit = next((i for i, l in enumerate(lanes, 1) if l == (code, lane)), 0)
        got = '%s／%s（第 %d／共 %d 条）' % (code, lane, hit, len(lanes)) if hit else \
              ('未命中：零发条' if not lanes else '未命中：首条 %s／%s（共 %d 条）' % (lanes[0][0], lanes[0][1], len(lanes)))
        print('selftest %s：%s 扫过 %d 行，发条 %d 条｜期望 %s／%s｜实得 %s｜%s' % (
            name, path.name, nl, len(finds), code, lane, got, '符合' if hit else '不符'))
        if not hit:
            ok = False

    expect('二档反方缺一侧', wf, 'E-COVERAGE', '反方缺一侧', wd, wnl)
    expect('二档无锚数', nf, 'E-ANCHOR', '数值锚', nd, nnl)
    codes = {_lane(x)[0] for x in tf}
    print(f"selftest 三档空模板：{tpl.name} 扫过 {tnl} 行，发条 {len(tf)} 条（规格 ≥1，留占位＝违例）｜实发码 {'、'.join(sorted(codes)) or '无'}")
    if not tf:
        print('   意外：空模板过了闸（缺陷——占位必须判违例）')
        ok = False
    tmp = Path(tempfile.mkdtemp(prefix='check-memo-selftest-'))
    try:
        res = probe_matrix(gd.read_text(encoding='utf-8'), json.loads(gr.read_text(encoding='utf-8')), tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    bad = [x for x in res if not x[3]]
    print(f"selftest 四档反证矩阵：{len(res)} 枚，未达预期 {len(bad)} 枚")
    for name, exp, gotv, passed, finds in res:
        print('   %-24s 期望 %-26s 实得 %-34s %s' % (name, exp, gotv, '符合' if passed else '不符'))
        if not passed and finds:
            for x in finds[:2]:
                print('      实发详行 → ' + x[:120])
    if bad:
        ok = False
    print(f"selftest: {'ALL GREEN' if ok else 'FAIL'}（一档 0/{len(gf)} · 二档 2/2 · 三档 {'发条' if tf else '未发条!'} · 四档 {len(res) - len(bad)}/{len(res)}）")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description='校验一份投决备忘录草稿是否合七节契约与红线（纯本地零网络）。',
                                 epilog='出口：FAIL 一行计数＋逐条 E-* 详行＋码表；PASS 一行＋两类计数。判定全集在本脚本现值。')
    ap.add_argument('memo', nargs='?', help='待校验的草稿（markdown）')
    ap.add_argument('--run', help='同次运行的 run.json（缺省取草稿同目录）')
    ap.add_argument('--selftest', action='store_true', help='四档自证：合规稿须过、两枚违例样须发红、空模板必须 FAIL、反证矩阵逐枚自报')
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if not args.memo:
        ap.error('缺参数：给一份草稿，或用 --selftest')
    p = Path(args.memo)
    if not p.is_file():
        print(f"[出错] 文件不存在：{p}")
        return 1
    rp = Path(args.run) if args.run else p.parent / 'run.json'
    finds, n = check(p, rp)
    return report(p, finds, n)


if __name__ == '__main__':
    sys.exit(main())
