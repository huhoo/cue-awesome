#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""m395_pin_state.py — 安装式三态读表（只读、零网络、不改既有尺）。

一条命令重跑：python3 -B scripts/m395_pin_state.py
  为什么另开一枚而不改 install_line_probe.py：那把尺判「三面有没有安装式、形制对不对」，
  本尺判「这一行可不可钉、钉在哪、不可钉的原因是什么」——两形判据不同源，不混在一把尺里。
  逐行报、不并成一个数（只报总数＝把某一形整个吞掉，就是「同形静」）。

四形与三态怎么认（按被检行的写法取，不按样例取）：
  A 式＝npx skills add <owner>/<repo> [--skill 名]：文档里这一支只有 owner/repo 与 --skill 两个位，
        未记版本位形 ⇒ 判「不可钉＋原因」；串里真带了 @ref 或 --ref 才判「钉」，并核那枚 ref 在不在盘上（钉到没有的东西＝假钉，发红）。
  第二式＝clawhub install @owner/slug：现读文档只记到 @owner/slug 一级（解析最新版），未记版本位 ⇒ 「不可钉＋原因」，不猜一种没写过的写法。
  B 式＝mkdir -p …/skills ＋ cp -r 本地拷贝 ⇒ 「不适用＋原因」：它不产生渠道计数，也就没有「钉哪一版」这一层。
  C 式＝curl -L -o … releases/<指针>/download/<pkg>.zip（可变指针 latest ⇒ 「未钉」）
        与 releases/download/<tag>/<pkg>.zip（钉死后 tag 换到 download 之后——两种形位置相反，只认其一
        就会把钉好的行整个读没了，这一枚是我自己钉完 tag 后撞出来的，见 03 号证据）；tag 在盘上 ⇒ 「钉」，不在 ⇒ 「假钉」。
  认不到形＝一行里确有安装式字样（releases/、npx skills add、clawhub install、.workbuddy/skills）而本尺一条都没分类上 ⇒ 单列计数、退 1；
        这是尺对自己的「同形静」防线——读不出形要响，不能悄悄当「那一形不存在」。

退码：0 四态相加＝分类数、无假钉、无认不到形；1 有假钉／有认不到形／相加不等（逐条点名）；3 取值域故障（仓根取不到、名册为空、git tag 读不到、一条安装式都没扫到——不读成「零违例」）。
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

A_RE = re.compile(r'npx skills add\s+([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)(@([A-Za-z0-9_.\-]+))?(?:\s+--skill\s+([A-Za-z0-9_.-]+))?(?:\s+--ref\s+([A-Za-z0-9_.\-]+))?')
CH_RE = re.compile(r'clawhub\s+install\s+(@[A-Za-z0-9_.:/-]+)')
B_RE = re.compile(r'(?:cp\s+-r\s+\S+|copy this directory)[^\n]*skills/|mkdir -p ~/\.workbuddy/skills'
                  r'|unzip\s+-o\s+-d\s+\S*skills|git clone [^\n]*\.git[^\n]*skills/')
# GitHub 两种形都得认：可变指针是 releases/latest/download/<pkg>.zip，钉死后是 releases/download/<tag>/<pkg>.zip
# ——指针与 tag 的位置是换的。只认前一形会让钉死后的行整个从表里消失（同形静，尺对自己也成立）。
C_LATEST_RE = re.compile(r'releases/latest/download/(\S+?\.zip)')
C_TAG_RE = re.compile(r'releases/download/([^/\s]+)/(\S+?\.zip)')
TAG_PAGE_RE = re.compile(r'releases/tag/([A-Za-z0-9_.\-]+)')
GUARD_RE = re.compile(r'(?:cp\s+-r|copy this directory|mkdir -p|unzip\s+-o\s+-d|git clone [^\n]*skills/'
                      r'|npx skills add|clawhub install|releases/(?:latest/download|download/|tag/))')
FACES = ('SKILL.md', 'README.md', 'README.en.md')

REASONS = {
    ('A 式', '不可钉'): 'skills CLI 这一支现读只有 owner/repo 与 --skill 两个位，文档未记版本位形——钉无可钉，不是漏钉',
    ('A 式', '钉'): '串里带版本位（@ref 或 --ref），钉形在场，ref 已对盘上 tag 核过',
    ('第二式', '不可钉'): 'clawhub install 现读只记到 @owner/slug 一级（解析最新版），未记版本位；不猜一种没写过的写法',
    ('第二式', '钉'): '带到了版本一级，核过才算钉',
    ('B 式', '不适用'): '本地拷贝不产生渠道计数，也就没有“钉哪一版”这一层——钉与不钉都不被那条口径数到',
    ('C 式', '未钉'): 'releases/latest 是可变指针：同一条 URL 换一天就是另一个内容，属可钉而未钉',
    ('C 式', '钉'): '指针已是固定 tag',
    ('发布页', '不适用'): '发布页指针不是安装动作；但本尺顺带核它那句“当前发布＝vX”与盘上最新 tag 是否同值，不同值单列「旧版陈述」',
}


def classify(line, tag_list):
    """→ [(形, 态, 细节)]。一行并现多形时全取，不提前返回（只取第一条会把另一形读成不存在）。"""
    out = []
    for m in A_RE.finditer(line):
        ref = m.group(3) or m.group(5)
        out.append(('A 式', '钉' if ref else '不可钉',
                    'repo=%s｜--skill=%s｜ref=%s' % (m.group(1), m.group(4) or '(无)', ref or '(无)')))
    for m in CH_RE.finditer(line):
        tok = m.group(1)
        pinned = tok.count('@') >= 2 or ':' in tok
        out.append(('第二式', '钉' if pinned else '不可钉', tok))
    m = C_LATEST_RE.search(line)
    if m:
        out.append(('C 式', '未钉', '指针=latest（可变）｜tag=-｜zip=%s' % m.group(1)[:44]))
    else:
        m = C_TAG_RE.search(line)
        if m:
            ptr, zipname = m.group(1), m.group(2)
            state = '钉' if ptr in tag_list else '钉在不存在的 ref=%s' % ptr
            out.append(('C 式', state, '指针=%s｜tag=%s｜zip=%s' % (
                '固定' if ptr != 'latest' else 'latest', ptr, zipname[:40])))
        else:
            m = TAG_PAGE_RE.search(line)
            if m:
                out.append(('发布页', '不适用', '那句写的 tag=%s' % m.group(1)))
    if B_RE.search(line) and not out:
        out.append(('B 式', '不适用', '本地拷贝形'))
    return out


def main():
    ap = argparse.ArgumentParser(description='安装式三态读表（只读、零网络）')
    ap.add_argument('--root', default=str(Path(__file__).resolve().parent.parent))
    ap.add_argument('--quiet', action='store_true', help='只报末行与钉目标')
    a = ap.parse_args()
    root = Path(a.root)
    if not root.is_dir():
        print('3 取值域故障：--root 取不到 %s（不读成「零安装式」）' % root)
        return 3
    pkgs = sorted(p.name for p in root.iterdir() if (p / 'SKILL.md').is_file())
    if not pkgs:
        print('3 取值域故障：%s 下名册为空（由盘上现算）' % root)
        return 3
    t = subprocess.run(['git', '-C', str(root), 'tag', '--sort=-creatordate'],
                       capture_output=True, text=True)
    if t.returncode != 0:
        print('3 取值域故障：git tag 读不到（rc=%d｜%s）——「钉在哪一枚」无从判，不填「无」' % (
            t.returncode, t.stderr.strip()[:80]))
        return 3
    tag_list = [x for x in t.stdout.split() if x]
    newest = tag_list[0] if tag_list else ''
    newest_files = ''
    if newest:
        lt = subprocess.run(['git', '-C', str(root), 'ls-tree', '-r', '--name-only', newest],
                            capture_output=True, text=True)
        newest_files = lt.stdout if lt.returncode == 0 else ''

    counts = {'钉': 0, '未钉': 0, '不可钉': 0, '不适用': 0, '假钉': 0, '认不到形': 0}
    rows, fake, unrecognized, stale = [], [], [], []
    targets = [(pkg, f) for pkg in pkgs for f in FACES] + \
              [('(仓根)', p.name) for p in sorted(root.glob('*.md'))]
    for pkg, face in targets:
        base = (root / pkg / face) if pkg != '(仓根)' else (root / face)
        if not base.is_file():
            continue
        try:
            text = base.read_text(encoding='utf-8', errors='ignore')
        except OSError:
            continue
        for i, line in enumerate(text.split('\n'), 1):
            found = classify(line, tag_list)
            if not found and GUARD_RE.search(line):
                counts['认不到形'] += 1
                unrecognized.append('%s/%s:%d｜%s' % (pkg, face, i, line.strip()[:110]))
                continue
            for form, state, detail in found:
                if form == '发布页':
                    tg = re.search(r'tag=([A-Za-z0-9_.\-]+)', detail)
                    if tg and newest and tg.group(1) != newest:
                        stale.append('%s/%s:%d｜那句写 %s｜盘上最新 tag＝%s' % (
                            pkg, face, i, tg.group(1), newest))
                if state.startswith('钉在不存在的'):
                    counts['假钉'] += 1
                    fake.append('%s/%s:%d｜%s｜%s' % (pkg, face, i, form, state))
                    continue
                counts[state] += 1
                rows.append((pkg, face, i, form, state, detail))
                if state == '钉' and form == 'C 式':
                    tg = re.search(r'tag=([^｜]+)', detail)
                    if not tg or tg.group(1) not in tag_list:
                        counts['假钉'] += 1
                        fake.append('%s/%s:%d｜C 式｜tag 不在 git tag 现值里（假钉）' % (pkg, face, i))
    if not rows and not unrecognized:
        print('3 取值域故障：名册=%d 枚逐面扫完一条安装式都没读到——不当「全部已钉」读' % len(pkgs))
        return 3
    if not rows:
        print('尺自查：名册=%d 枚里一条也没分类上，但有 %d 行确有安装式字样而本尺认不出形——按 1 报不按 3' % (
            len(pkgs), len(unrecognized)))
        for u in unrecognized:
            print('认不到形 %s' % u)
        return 1

    cur = None
    for pkg, face, i, form, state, detail in rows:
        if not a.quiet:
            if (pkg, face) != cur:
                cur = (pkg, face)
                print('== %s/%s' % (pkg, face))
            print('   :%-4d %-7s %-4s %-58s %s' % (i, form, state, detail, REASONS.get((form, state), '')))
    print('----')
    print('钉目标现读：tag 枚数=%d｜最新一枚=%s｜该 tag 内含 SKILL.md 的包=%d／名册=%d 枚（缺的那些钉上去就是旧内容）' % (
        len(tag_list), newest or '(盘上无 tag)',
        sum(1 for p in pkgs if ('%s/SKILL.md' % p) in newest_files.split('\n')), len(pkgs)))
    missing = [p for p in pkgs if ('%s/SKILL.md' % p) not in newest_files.split('\n')]
    if missing:
        print('   该 tag 里没有的包=%s' % '、'.join(missing))
    classified = counts['钉'] + counts['未钉'] + counts['不可钉'] + counts['不适用']
    scanned = classified + counts['假钉'] + counts['认不到形']
    print('逐行数=%d（分类 %d＋假钉 %d＋认不到形 %d）｜钉=%d｜未钉=%d｜不可钉=%d｜不适用=%d｜四态相加=%d（应＝分类数 %d）' % (
        scanned, classified, counts['假钉'], counts['认不到形'],
        counts['钉'], counts['未钉'], counts['不可钉'], counts['不适用'], classified, classified))
    for f in fake:
        print('假钉 %s' % f)
    for u in unrecognized:
        print('认不到形 %s' % u)
    for sline in stale:
        print('旧版陈述 %s' % sline)
    if stale:
        print('   （这一格只报不拦：那是发布页那句散文，改它要她落字，本尺不替面文做主）')
    if fake:
        return 1
    if counts['认不到形']:
        print('尺自查：有安装式在场而本尺认不出形制＝不可判，不当「该形不存在」读——请补认形正则并复跑')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
