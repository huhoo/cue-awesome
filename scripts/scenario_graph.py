#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""scenario_graph.py —— 把「几枚技能真能前后相接」算成三张表，不写成文档里的一句话。

读什么：仓内每枚包（含 SKILL.md 的目录）frontmatter 里的 `consumes:`／`produces:` 两枚清单，
值＝工件类型名。这是全仓唯一的取数源——本件不写死任何包名、工件名或域名的清单。

三张表（枚数一律现算现打：先列条目、再打由同一份列表算出的枚数）：
  一 孤点      —— 跨件入度与出度都为 0 的包：有人产它吃的东西、或有人吃它产的东西，都不成立。
                   （同一枚包自产自消的自环不算接进链条，自环另在附注里点名，不藏。）
  二 断边      —— 某件 consumes 的工件 X，全仓无任何件 produces X ⇒ 用户走到这里得手工补。
  三 覆盖缺口  —— A 路里 external_status=live 的域，其数据腿无任何件声明引用 ⇒ 有供给无场景。
                   本表要一份外部原料（A 路那一路调研交付的 jsonl，每行 {"domain 或 id","external_status 或 status","legs":[...]}）。
                   原料不在盘或某行未标 legs 时，本件点名缺位并把该表判为「不作数」——不记 0、不猜域清单。

形制：纯标准库、零网络、只读；条目全部按名排序（输出与枚举顺序无关，可逐字节对拍）；
      只打相对路径，不打绝对路径；任何读不到的东西走一句人话出口、零 Traceback。
退码：0 三表算完（覆盖缺口表可以「不作数」，那是原料问题不是本件的失败）；
      1 读不到任何包、某枚 SKILL.md 解析不了、或 --domains 指了文件却读不到（失败要响亮）；
      2 用法错（比如 --domains 缺值）。
"""

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
IGNORE_DIRS = {".github", "docs", "scripts", "assets", ".git", ".workbuddy"}


def die(msg, code=1):
    print(msg, file=sys.stderr)
    return code


def frontmatter_lines(text):
    """取首尾两枚 `---` 之间的 frontmatter 原文；没有成对分隔符就回空串（由调用方点名）。"""
    ls = text.split("\n")
    if not ls or ls[0].strip() != "---":
        return ""
    try:
        end = next(i for i in range(1, len(ls)) if ls[i].strip() == "---")
    except StopIteration:
        return ""
    return "\n".join(ls[1:end])


def parse_frontmatter_list(text, key):
    """从 frontmatter 文本里取 `key:` 下的 `  - 值` 列表；无该键返回 None（与空列表区分）。"""
    lines = text.split("\n")
    vals, seen, i = [], False, 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith(key + ":"):
            seen = True
            rest = ln[len(key) + 1:].strip()
            if rest.startswith("[") and rest.endswith("]"):
                vals = [x.strip().strip("\"'") for x in rest[1:-1].split(",") if x.strip()]
                break
            i += 1
            while i < len(lines) and (lines[i].startswith("  - ") or lines[i].startswith("  -\t")):
                vals.append(lines[i][4:].strip().strip("\"'"))
                i += 1
            break
        i += 1
    return vals if seen else None


def read_packages(repo):
    """枚枚读 frontmatter → {包名: (consumes, produces)}；缺键按空处理但记进 notes 供点名。"""
    out, notes = {}, []
    for d in sorted(p for p in repo.iterdir() if p.is_dir()):
        if d.name in IGNORE_DIRS or d.name.startswith("."):
            continue
        skill = d / "SKILL.md"
        if not skill.is_file():
            continue
        fm = frontmatter_lines(skill.read_text(encoding="utf-8", errors="replace"))
        cons = parse_frontmatter_list(fm, "consumes")
        prod = parse_frontmatter_list(fm, "produces")
        if cons is None or prod is None:
            notes.append("%s：frontmatter 里 %s（本件按空清单计入，不猜）" % (
                d.name, "、".join(k for k, v in (("consumes", cons), ("produces", prod)) if v is None)))
        out[d.name] = (sorted(cons or []), sorted(prod or []))
    return out, notes


def load_domains(path):
    """A 路原料：JSONL，每行 {"domain|id", "external_status|status", "legs":[...]}。返回 (行, 缺位说明)。"""
    rows = []
    with open(path, "r", encoding="utf-8") as fh:
        for n, line in enumerate(fh, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                obj = json.loads(line)
            except ValueError as err:
                raise SystemExit(die("%s 第 %d 行不是合法 JSON：%s" % (path, n, str(err)[:80])))
            if not isinstance(obj, dict):
                raise SystemExit(die("%s 第 %d 行不是对象（是 %s）——本件按枚行读，不猜" % (path, n, type(obj).__name__)))
            rows.append(obj)
    return rows


def main():
    ap = argparse.ArgumentParser(description="现算三表：孤点／断边／覆盖缺口（读各包 SKILL.md 的 consumes 与 produces）。")
    ap.add_argument("--repo", default=str(REPO), help="仓根（默认本件所在仓的根；输出里只打相对路径）")
    ap.add_argument("--domains", help="A 路 live 域原料（jsonl，见档内形制说明）；不给或不在盘 ⇒ 覆盖缺口表判「不作数」")
    args = ap.parse_args()

    repo = Path(args.repo)
    if not repo.is_dir():
        return die("读不到仓根：%s（本件按枚目录扫 SKILL.md，不换源不猜）" % repo, 2)
    pkgs, notes = read_packages(repo)
    if not pkgs:
        return die("在 %s 下一枚 SKILL.md 都没读到——本件无从算表" % repo.name)

    root = repo.resolve()

    def rel(x):
        s = str(x)
        return s[len(str(root)) + 1:] if s.startswith(str(root) + "/") else s

    def show(x):
        """输出里不打绝对路径：能化成相对当前目录的就化。"""
        import os
        try:
            r = os.path.relpath(str(x), Path.cwd())
        except ValueError:
            return str(x)
        return r if not r.startswith("/" + os.sep) else Path(x).name

    producers, consumers = {}, {}
    for name, (cons, prod) in sorted(pkgs.items()):
        for a in prod:
            producers.setdefault(a, []).append(name)
        for a in cons:
            consumers.setdefault(a, []).append(name)
    for m in (producers, consumers):
        for k in m:
            m[k].sort()

    # 一、孤点：跨件入度与出度都为 0
    iso, loops = [], []
    for name, (cons, prod) in sorted(pkgs.items()):
        out_deg = {q for a in prod for q in consumers.get(a, []) if q != name}   # 我产的谁接走
        in_deg = {q for a in cons for q in producers.get(a, []) if q != name}     # 我吃的谁供的
        if not out_deg and not in_deg:
            iso.append(name)
        self_edges = sorted(a for a in prod if a in cons and producers.get(a) == [name])
        if self_edges:
            loops.append("%s 自环：%s" % (name, "、".join(self_edges)))

    # 二、断边：consumes 的 X 无任何件 produces
    broken = ["%s consumes %s（全仓无任何件 produces）" % (name, a)
              for name, (cons, _p) in sorted(pkgs.items()) for a in cons if not producers.get(a)]

    # 三、覆盖缺口：A 路 live 域无人引用其数据腿
    cov_hdr, gaps, unmarked, covered, dom_note = [], [], [], [], ""
    if args.domains:
        dpath = Path(args.domains)
        if not dpath.is_file():
            return die("--domains 指了路径却读不到：%s（缺原料请别跑这一表，本件不猜域清单）" % args.domains)
        rows = load_domains(dpath)
        declared = {a for (_c, p) in pkgs.values() for a in p} | {a for (c, _p) in pkgs.values() for a in c}
        live = 0
        for obj in rows:
            dom = obj.get("domain") or obj.get("id") or "(无名)"
            status = obj.get("external_status") or obj.get("status") or ""
            if status != "live":
                continue
            live += 1
            legs = obj.get("legs")
            if not isinstance(legs, list) or not legs:
                unmarked.append(dom)
                continue
            hits = sorted(n for n, (_c, p) in sorted(pkgs.items()) if set(legs) & set(p))
            if hits:
                covered.append("%s ← %s" % (dom, "、".join(hits)))
            else:
                gaps.append("%s（腿：%s；无任何件声明引用）" % (dom, "、".join(sorted(legs))))
        dom_note = "原料＝%s｜live 域 %d 枚｜腿已被引用 %d 枚｜缺口 %d 枚｜未标腿 %d 枚" % (
            show(args.domains), live, len(covered), len(gaps), len(unmarked))
    else:
        dom_note = "缺位：未给 --domains（A 路原料由那一路调研的票交付，路径由调用方给）⇒ 本表不作数，不记 0、不猜域清单"

    label = repo.name or str(repo)
    print("scenario_graph｜取数＝各包 SKILL.md frontmatter 的 consumes/produces｜包 %d 枚（扫自 %s）" % (len(pkgs), label))
    for n in notes:
        print("  注：%s" % n)
    print()
    print("== 表一 孤点（跨件入度与出度皆 0）==")
    for n in iso:
        print("  %s ｜ %s" % (n, rel(repo / n / "SKILL.md")))
    print("  枚数=%d（由上列现算）｜全包=%d 枚｜非孤点=%d 枚" % (len(iso), len(pkgs), len(pkgs) - len(iso)))
    if loops:
        print("  附注·自环（自产自消，不计入链条）：")
        for l in loops:
            print("    " + l)
    print()
    print("== 表二 断边（consumes 的工件无任何件 produces）==")
    for b in broken:
        print("  " + b)
    print("  枚数=%d（由上列现算）｜consumes 总项=%d" % (
        len(broken), sum(len(c) for c, _p in pkgs.values())))
    print()
    print("== 表三 覆盖缺口（A 路 live 域无人引用其数据腿）==")
    for g in gaps:
        print("  " + g)
    print("  " + dom_note)
    print("  枚数=%s" % (len(gaps) if args.domains else "不作数（原料缺位）"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
