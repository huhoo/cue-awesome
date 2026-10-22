#!/usr/bin/env python3
"""install_line_probe.py｜三形安装式对表尺（M369 交付件）：逐枚现读「面内现值 ∥ ClawHub 真实安装式 ∥ skills.sh 式」。

一条命令重跑：TMPDIR=/tmp python3 -B scripts/install_line_probe.py
  名册＝有 SKILL.md 的目录（由盘上现算，不写死枚数）。三面＝SKILL.md／README.md／README.en.md；包内其它面＝该包其余 *.md（CHANGELOG 除外）。
  三形怎么认（都按被检件的写法取，不按某一枚样例取）：
    A 式＝npx skills add <owner>/<repo> [--skill <名>]——skills.sh 口径认的就是这条（无提交口、按匿名遥测的安装量上榜，
         来路 channel-candidates-2026-10-21.md:48 与 :91 现读）；本尺逐枚校两格形制：repo 是否等于 --expect-repo（默认 huhoo/cue-awesome，
         来路＝origin 现值）、--skill 参数是否等于该枚目录名。任一不符 ⇒ 点名 文件:行号 并计入不合。
    B 式＝mkdir -p ~/.workbuddy/skills ＋ cp -r <目录> ~/.workbuddy/skills/（本地拷贝，不产生可被 ③ 计数的安装动作）。
    C 式＝curl -L -o .../releases/latest/download/....zip ＋ unzip 到技能目录（现读只落在仓根 README.md:69-71／README.zh-CN.md:69，
         不在本名册任何一枚面里——所以它进「名册外一格」自报，不混进逐枚计数）。
  ② ClawHub 真实安装式：只从 --clawhub <文件> 取现值（那份文件是别处取回的缓存返回，本尺自己零网络、一枪不发）。
     没给文件、或给了但文件里没有安装式字段 ⇒ 一律明写「未取到」并带来路那一句；**不许把「未取到」填成 0，也不许猜一条 clawhub install 顶上**——
     盘上现读到 2026-10-22 为止只记到 CLI 本体（npm 包 clawhub／bin clawhub／v0.23.3／node≥22／官方演示为全局安装、npx clawhub 未见文档背书，
     来路 listing-runbook.md §3.1 第 198 行），没有任何一条用户侧安装式串被记过。假装有一条才是假陈述。
  判据：名册齐，且每枚三格各有「现值」或「明写未取到」——cell 的两个出口都产标，所以「空着不写」这形在结构上出不来；
        尺的红由三条真判据升起：①A 式形制点名（repo 不等于 --expect-repo、缺 --skill 参数、或参数不等于目录名）；
        ②①的三项计数（三面现值／只在包内其它面／未取到）相加不等于名册；③③的两项计数相加不等于名册。后两条是尺自查自己别把名册数丢一格。
  退码：0 名册齐、形制全合、且两行末行自检相加等于名册；1 有形制点名，或①三项／③两项任一组相加不等于名册（尺自查）；
        3 取值域故障（--root 取不到、名册为空、--clawhub 指了路径却读不到）。
  反证怎么跑（不必改仓内面）：--root 指一份 TMPDIR 副本，在副本上改一枚的 --skill 参数或摘掉一面的安装串，本尺须分别「点名该行」与「判未取到」。
形制：纯标准库、零网络、只读；逐枚一行、可对拍；不打绝对路径；读不到的东西走一句人话出口、零 Traceback。
"""

import argparse
import re
import sys
from pathlib import Path

FACES = ('SKILL.md', 'README.md', 'README.en.md')
A_RE = re.compile(r'npx skills add\s+([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)(?:\s+--skill\s+([A-Za-z0-9_.-]+))?')
A2_RE = re.compile(r'npx skills add\s+sensedeal/[A-Za-z0-9_.-]+')
B_RE = re.compile(r'(?:cp\s+-r\s+\S+|copy this directory)[^\n]*skills/|mkdir -p ~/\.workbuddy/skills')
C_RE = re.compile(r'curl -L -o|releases/latest/download|unzip -o -d')
NOT_FOUND = '未取到'
# 安装式串里带 @（docs/cli.md:146 的规范式就是 clawhub install @owner/slug）——字符类缺 @ 会把真值读成「没有」，
# 与「同行两式共用一条 search」是同一族：认不到真形＝读成没有。键名也放宽到 install 前缀一族（install_lines／installCommand…）。
CH_CMD_RE = re.compile(r'clawhub\s+install\s+[@A-Za-z0-9_.:/-]+')
CH_KEY_RE = re.compile(r'"install[A-Za-z_]*"\s*:\s*"([^"]+)"')
CLAWHUB_PROVENANCE = ('两条来路分写（2026-10-22 起）：①服务端 listing 现读无安装式字段——verify/m369-artifact/05-clawhub-cache.json 记 '
                      'GET clawhub.ai/api/v1/skills/cue-omni-reader 顶层键 latestVersion／metadata／moderation／owner／skill，skill.stats.installs=0；'
                      '②规范式来自 docs/cli.md:146 节题原句「install @owner/slug」（第 147-151 行：解析最新版→/api/v1/download 取 zip→解到 <workdir>/<dir>/<slug>，'
                      '并写 .clawhub/lock.json 与 <skill>/.clawhub/origin.json）。本尺零网络，②只从 --clawhub 给的缓存读；读不到就明写未取到，不填 0、不猜一条顶上')


def read(p):
    try:
        return p.read_text(encoding='utf-8', errors='ignore')
    except OSError:
        return None


def scan(rel, text):
    """一格里放几种形的命中（file:line 列表），不提前返回——摘掉一形还剩一形时，另一形必须被看见。
    同一行可以并现多条 npx 式（现读 cn-earnings-note/references/data-channels.md:174：先 sensedeal、后 huhoo），
    所以逐枚 finditer 取，不用 search 只拿第一条——用 search 会把同一句里的本件安装式读成不存在。
    A 与 A2 分开：A＝装本件那条（owner/repo 由 --expect-repo 校），A2＝装别集那条（sensedeal/cue-skills，取证腿），
    把 A2 当 A 去校目录名会把合法句读成违例。"""
    out = {'A': [], 'A2': [], 'B': [], 'C': [], 'Aocc': []}
    for i, ln in enumerate(text.split('\n'), 1):
        ms = list(A_RE.finditer(ln))
        for k, m in enumerate(ms, 1):
            repo, arg = m.group(1), m.group(2)
            tag = '%s:%d' % (rel, i) + ('' if len(ms) == 1 else '#%d' % k)
            if repo.startswith('sensedeal/'):
                out['A2'].append(tag)
            else:
                out['A'].append(tag)
                out['Aocc'].append((tag, repo, arg))
        if not ms and A2_RE.search(ln):
            out['A2'].append('%s:%d' % (rel, i))
        if B_RE.search(ln):
            out['B'].append('%s:%d' % (rel, i))
        if C_RE.search(ln):
            out['C'].append('%s:%d' % (rel, i))
    return out


def blank():
    return {'A': [], 'A2': [], 'B': [], 'C': [], 'Aocc': []}


def merge(a, b):
    for k in ('A', 'A2', 'B', 'C', 'Aocc'):
        a.setdefault(k, [])
        a[k].extend(b.get(k, []))
    return a


def cell(hits, keys):
    """有值就报 文件:行号（带枚数），没值就明写未取到——两形都有出口，末行的计数才不会是死数。"""
    got = []
    for k in keys:
        got += ['%s[%s]' % (h, k) for h in hits[k]]
    if got:
        return '%d 处：%s' % (len(got), '、'.join(got)), True
    return NOT_FOUND, False


def claw_cell(path_text):
    if path_text is None:
        return NOT_FOUND + '（来路见末行）', False
    vals = CH_CMD_RE.findall(path_text)
    vals += [v for v in CH_KEY_RE.findall(path_text) if v not in vals]
    if vals:
        uniq = sorted(set(vals))
        return '%d 形（%d 处）：%s' % (len(uniq), len(vals), '、'.join(v[:70] for v in uniq[:4])), True
    return '%s（文件在场，但没有安装式字段；来路见末行）' % NOT_FOUND, False


def repo_root_lines(root):
    """名册外那一格：仓根自己的 *.md 里现读着哪些安装形——由盘上现扫，不把行号写死在尺里。"""
    out = {'A': [], 'C': []}
    for p in sorted(root.glob('*.md')):
        for i, ln in enumerate((read(p) or '').split('\n'), 1):
            ms = [m for m in A_RE.finditer(ln) if not m.group(1).startswith('sensedeal/')]
            for k in range(len(ms)):
                out['A'].append('%s:%d' % (p.name, i) + ('' if len(ms) == 1 else '#%d' % (k + 1)))
            if C_RE.search(ln):
                out['C'].append('%s:%d' % (p.name, i))
    return out


def main():
    ap = argparse.ArgumentParser(description='三形安装式对表尺（零网络、只读）')
    ap.add_argument('--root', default='/data/sdc1/work/gtm/cue-awesome', help='被检仓根（反证可指 TMPDIR 副本）')
    ap.add_argument('--expect-repo', default='huhoo/cue-awesome', help='A 式应当装的 owner/repo（来路＝origin 现值）')
    ap.add_argument('--clawhub', help='别处取回的 ClawHub 返回缓存（本尺不发请求；不给＝②一律未取到）')
    ap.add_argument('--quiet', action='store_true', help='只报末行与名册外一格')
    a = ap.parse_args()

    root = Path(a.root)
    if not root.is_dir():
        print('3 --root 取不到目录：%s（取值域故障，不读成「0 枚安装式」）' % a.root)
        return 3
    pkgs = sorted(p.name for p in root.iterdir() if (p / 'SKILL.md').is_file())
    if not pkgs:
        print('3 名册为空：%s 下没有含 SKILL.md 的目录（取值域故障，不读成「0 枚」）' % root)
        return 3

    claw_text = None
    if a.clawhub:
        cp = Path(a.clawhub)
        if not cp.exists():
            print('3 --clawhub 指了路径却读不到：%s（取值域故障，②不因此算「没有安装式」）' % a.clawhub)
            return 3
        claw_text = read(cp)

    bad = []
    arch = {'三面': 0, '包内其它面': 0}
    counts = {'三面现值': 0, '只在包内其它面': 0, '①未取到': 0, '②未取到': 0, '③现值': 0, '③未取到': 0, '形制点名': 0}
    for d in pkgs:
        three, other = blank(), blank()
        for f in FACES:
            p = root / d / f
            t = read(p) if p.exists() else None
            if t is None:
                continue
            merge(three, scan(f, t))
        for p in sorted((root / d).rglob('*.md')):
            if p.name == 'CHANGELOG.md' or p.name in FACES:
                continue
            rel = str(p.relative_to(root / d))
            merge(other, scan(rel, read(p) or ''))

        c1, has1 = cell(three, ('A', 'B', 'C'))
        arch['三面'] += len(three['A'])
        arch['包内其它面'] += len(other['A'])
        o_hits = other['A'] + other['B'] + other['C']
        if has1:
            counts['三面现值'] += 1
            c1 = '%s／包内其它面另有：%s' % (c1, cell(other, ('A', 'B', 'C'))[0]) if o_hits else c1
        elif o_hits:
            counts['只在包内其它面'] += 1
            c1 = '%s／包内其它面：%s' % (c1, cell(other, ('A', 'B', 'C'))[0])
        else:
            counts['①未取到'] += 1

        c2, has2 = claw_cell(claw_text)
        if not has2:
            counts['②未取到'] += 1

        t3, h3 = cell(three, ('A',))
        to, ho = cell(other, ('A',))
        if h3 and ho:
            c3, has3 = '%s／另：包内其它面 %s' % (t3, to), True
        elif h3:
            c3, has3 = t3, True
        elif ho:
            c3, has3 = '三面无 A 式／包内其它面 %s' % to, True
        else:
            c3, has3 = '%s（三面与包内其它面都没有那条 npx 式）' % NOT_FOUND, False
        counts['③现值' if has3 else '③未取到'] += 1

        for hit, repo, arg in three['Aocc'] + other['Aocc']:
            if repo != a.expect_repo:
                bad.append('%s｜A 式 repo 现读=%s｜期望=%s（%s）' % (d, repo, a.expect_repo, hit))
            if arg is None:
                bad.append('%s｜A 式没有 --skill 参数，装的是整套还是本枚无从判（%s）' % (d, hit))
            elif arg != d:
                bad.append('%s｜--skill 参数现读=%s｜期望=目录名 %s（%s）' % (d, arg, d, hit))
        if not a.quiet:
            print('%-24s ①%s' % (d, c1))
            print('%-24s ②%s' % ('', c2))
            print('%-24s ③%s' % ('', c3))

    print('----')
    rl = repo_root_lines(root)
    print('名册=%d 枚（由盘上现算）｜①三面现值=%d（其中另有包内其它面的枚数见逐枚行）／只在包内其它面=%d／未取到=%d｜'
          '②未取到=%d｜③有 A 式（三面或包内）=%d／未取到=%d' % (
              len(pkgs), counts['三面现值'], counts['只在包内其它面'], counts['①未取到'],
              counts['②未取到'], counts['③现值'], counts['③未取到']))
    print('A 式三档现数（由逐枚现算，报数必带档名）：主档＝三面 %d 处｜另档①＝包内（除 CHANGELOG、除三面）%d 处｜另档②＝再加仓根 *.md %d 处＝%d 处' % (
        arch['三面'], arch['包内其它面'], len(rl['A']), arch['三面'] + arch['包内其它面'] + len(rl['A'])))

    print('名册外一格（仓根自己的 *.md 现扫，不写死行号）：A 式 %d 处＝%s｜C 式（release-zip）%d 处＝%s——'
          '这些不在逐枚名册的 ①②③ 计数里，别把它们读成某枚面的现值。' % (
              len(rl['A']), '、'.join(rl['A']) if rl['A'] else '无',
              len(rl['C']), '、'.join(rl['C']) if rl['C'] else '无'))
    print('②来路：%s' % CLAWHUB_PROVENANCE)
    print('③口径：skills.sh 无人工提交口（现读 /submit＝404），按匿名遥测的安装量上榜——来路 channel-candidates-2026-10-21.md:48、:91；'
          '能被它计数的只有 A 式，B 式（本地拷贝）与 C 式（release-zip）都不产生该渠道口径的安装动作。')
    for b in bad:
        print('点名 %s' % b)
    print('形制点名=%d 处（由上面逐行现数）｜不合=%d' % (len(bad), len(bad)))
    if bad:
        return 1
    if counts['三面现值'] + counts['只在包内其它面'] + counts['①未取到'] != len(pkgs):
        print('末行自检：①的三项计数相加不等于名册——这把尺自己错了，别当读数用')
        return 1
    if counts['③现值'] + counts['③未取到'] != len(pkgs):
        print('末行自检：③的两项计数相加不等于名册——这把尺自己错了，别当读数用')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
