#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""scenario_graph.py —— 把「几枚技能真能前后相接」算成几张可跑的表，不写成文档里的一句话。

读什么：
  1) 仓内每枚包（含 SKILL.md 的目录）frontmatter 里的 `consumes:`／`inputs:`／`produces:`／`legs:` 四枚清单
     （`legs:` 是表三强口径要的那一层，现未引入——缺即按事实点名，不猜、不当 0 结论）；
  2) 一份规范词表（缺省 scripts/artifact-types.yaml）：canonical 工件名全集、inputs 族、alias→canonical、family。
本件不写死任何包名、工件名或域名的清单；包面里出现的名字一律先套 alias 归一，再对照词表——
**表外名字直接退 1 点名**（宁可红，也不让一张凑满的图骗人）。

四张表（枚数一律现算现打：先列条目、再打由同一份列表算出的枚数）：
  一 孤点      —— 跨件入度与出度都为 0 的包。边只由规范工件名相等得出：`inputs:` 不算边，
                   同一枚包自产自消的自环也不算接进链条（自环另在附注里点名，不藏）。
  二 待补入口  —— 两列来源分开报、各带自己枚数，**不相加、不给合计数**：
                   (a) `inputs:` 里的项＝用户/外部必须提供（入参天经地义由人给，不是我们的漏）；
                   (b) `consumes:` 里无任何件 `produces` 的项＝链条内部断口（这才是该补的件）。
                   旧的「断边」定义作为 (b) 活下去，不退役；两读法各留一枚 `--legacy-*` 开关，都不当默认。
  三 覆盖缺口  —— 两口径并列、互不覆盖（结果不同是特性不是缺陷）：
                   弱口径＝域 id 原文出现在包面文（SKILL／SKILL.en／README／README.en）即算引用；
                            文本出现 ≠ 数据腿引用，这一版只答「面上提没提过这个域」。
                   强口径＝某件 frontmatter 显式声明 `legs:` 含该域 id 原文（值＝catalog 的域 id，不是工具名）。
                   域清单由调用方给原料：`--catalog` 读 mcp-catalog 快照（data.domains[]），`--domains` 读逐行 jsonl。
                   原料不在盘时两版都判「不作数」——不列空条目、不记 0、不猜域清单。
  附 指路      —— 包面提到其他包名的次数。指路不是边、不进图，只另开一枚计数与孤点并列
                   （图要能算孤点，指路只能算气氛）。

形制：纯标准库、零网络、只读；条目全部按名排序（输出与枚举顺序无关，可逐字节对拍）；
      只打相对路径，不打绝对路径；任何读不到的东西走一句人话出口、零 Traceback。
      列表项按 YAML 语义收：跨过空行继续收、收到下一个顶格键为止；缩进几格都收（顶格、四格、六格与夹空行都是合法写法，
      把合法写法判成「读不到」＝假红）。缩进不为两格时另出一句「形制不齐」点名，但不拦退码。
      真判「不可判」的只剩一形：该键区域内先有映射行、后又冒类列表行——归属读不出，宁可响亮也不猜（见退码 1）。
退码：0 各表算完（覆盖缺口可以「不作数」，那是原料问题不是本件的失败；形制不齐的点名不拦退码）；
      1 读不到任何包、某枚 SKILL.md 解析不了、包面出现词表外名字、词表读不到或不成形、
        原料（--catalog／--domains）指了路径却读不到或形状不认识、
        某枚键的值归属读不出（不可判；末行并列「不合=0｜不可判=N 把键／M 枚包」，这些键不并入图、不进任何一张表）；
      2 用法错（比如 --catalog 与 --domains 同时给、两枚 --legacy 同时给、路径不是目录）。
      「不可判」的末行只在有话要说时长；三表对账一律两值并列（取到 N 把／跳过 M 把），
      因为一旦有键被跳过，各表枚数就不再是全名册的数——只报一个数会把这件事抹平。
"""

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
IGNORE_DIRS = {".github", "docs", "scripts", "assets", ".git", ".workbuddy"}
FACE_GLOBS = ("SKILL.md", "SKILL.en.md", "README.md", "README.en.md")
FM_KEYS = ("consumes", "inputs", "produces", "legs")


def die(msg, code=1):
    print(msg, file=sys.stderr)
    return code


def strip_comment(line):
    """去掉行尾 ` #…` 注释（本词表不用值内 #，注释一律前面有空白）。"""
    out = []
    for i, ch in enumerate(line):
        if ch == "#" and (i == 0 or line[i - 1] in " \t"):
            break
        out.append(ch)
    return "".join(out).rstrip()


def load_vocabulary(path):
    """读词表（受限 YAML 子集：顶层键 + 缩进列表 + 缩进 `k: v`）；缺任一族即失败，不猜。"""
    text = path.read_text(encoding="utf-8", errors="replace")
    top, fam = None, None
    vocab = {"aliases": {}, "families": {}, "inputs": [], "canonical": []}
    for raw in text.split("\n"):
        ln = strip_comment(raw)
        if not ln.strip():
            continue
        if not ln.startswith((" ", "\t")):
            fam = None
            top = ln.split(":")[0].strip()
            if top not in vocab:
                print("  注：词表 %s 出现不认识的顶层键：%s（本件只读 aliases/families/inputs/canonical）" % (
                    path.name, top), file=sys.stderr)
            continue
        body = ln.strip()
        if top == "aliases" and ":" in body:
            k, v = body.split(":", 1)
            vocab["aliases"][k.strip().strip("\"'")] = v.strip().strip("\"'")
        elif top in ("inputs", "canonical") and body.startswith("- "):
            vocab[top].append(body[2:].strip().strip("\"'"))
        elif top == "families":
            if body.startswith("- "):
                if fam is None:
                    print("  注：词表 families 里有一枚列表项不在任何族下：%s（已忽略）" % body, file=sys.stderr)
                else:
                    vocab["families"][fam].append(body[2:].strip().strip("\"'"))
            elif body.endswith(":"):
                fam = body[:-1].strip()
                vocab["families"].setdefault(fam, [])
    for k in ("aliases", "families", "inputs", "canonical"):
        if not vocab[k]:
            raise SystemExit(die("词表 %s 里没有 %s 这一族（本件不猜词表，缺即失败）" % (path, k)))
    return {k: (dict(v) if isinstance(v, dict) else sorted(set(v))) if k != "families"
            else {f: sorted(set(m)) for f, m in v.items()} for k, v in vocab.items()}


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
    """取 `key:` 下的列表值。返回 (清单或 None, 归属存疑的类列表行枚数, 区内实际见过的缩进集合)。

    四态分清（M377 按 6.1 的 M374-1 改的这一支）：
      无该键＝(None, 0, set())——由调用方按「缺键」点名；
      键在场、列表项按 YAML 语义读得到＝(值, 0, 缩进集)——**值收集跨过空行继续收，收到下一个顶格键为止**；
        缩进是几格都收（顶格与更深都是合法写法，把合法写法判成「读不到」＝假红），只是缩进不为两格时另出一句形制不齐的点名；
      区内出现归属存疑的类列表行（先见到映射行、之后才冒出的类列表行）＝(值, 枚数>0, 缩进集)——
        这种键整体按不可判处理：不并入图、不进任何一张表、也不读成空清单；
      键后紧跟别的顶格键＝正常空清单（值, 0, set()）。
    不收的是「放错层的列表算成真边」那一形——所以归属存疑时宁可响亮不可判，也不猜。
    """
    lines = text.split("\n")
    vals, seen, i = [], False, 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith(key + ":") and (len(ln) == len(key) + 1 or ln[len(key) + 1] in (" ", "\t")):
            seen = True
            rest = ln[len(key) + 1:].strip()
            if rest.startswith("[") and rest.endswith("]"):
                vals = [x.strip().strip("\"'") for x in rest[1:-1].split(",") if x.strip()]
                return sorted(vals), 0, set()
            i += 1
            odd, indents, after_map = 0, set(), False
            while i < len(lines):
                s = lines[i]
                if not s.strip():
                    i += 1
                    continue
                body = s.strip()
                ind = len(s) - len(s.lstrip(" \t"))
                is_item = body == "-" or body.startswith("- ") or body.startswith("-\t")
                if ind == 0 and not is_item:
                    break                                   # 下一个顶格键＝本键区域结束
                if is_item:
                    if after_map:
                        odd += 1                            # 归属存疑：映射行之后的类列表行
                    else:
                        vals.append(body[1:].strip().strip("\"'"))
                        indents.add(ind)
                else:
                    after_map = True
                i += 1
            return (sorted(vals) if vals else []), odd, indents
        i += 1
    if not seen:
        return None, 0, set()
    return sorted(vals), 0, set()


def read_packages(repo):
    """枚枚读 frontmatter → ({包名: {四把键}}, 缺键点名, 不可判 {包: [键]}, 形制不齐点名)。

    缺键＝按空清单计入并点名（不猜）；不可判＝既不并入图、也不进任何一张表；
    缩进非两格但语义读得到的＝值照收，另出一句形制不齐（这一类不拦退码——合法写法不该判红）。
    """
    out, notes, unj, loose = {}, [], {}, []
    for d in sorted(p for p in repo.iterdir() if p.is_dir()):
        if d.name in IGNORE_DIRS or d.name.startswith("."):
            continue
        skill = d / "SKILL.md"
        if not skill.is_file():
            continue
        fm = frontmatter_lines(skill.read_text(encoding="utf-8", errors="replace"))
        got, bad_here = {}, []
        for k in FM_KEYS:
            got[k], odd, indents = parse_frontmatter_list(fm, k)
            if odd:
                bad_here.append(k)
            elif indents and indents != {2}:
                loose.append("%s：%s 的列表项缩进是 %s 格（合法写法，值已按语义读入；与全仓两格形制不齐）" % (
                    d.name, k, "、".join(str(x) for x in sorted(indents))))
        miss = [k for k in FM_KEYS if got[k] is None]
        if miss:
            notes.append("%s：frontmatter 里没有 %s（本件按空清单计入，不猜）" % (d.name, "、".join(miss)))
        if bad_here:
            unj[d.name] = sorted(bad_here)
            out.setdefault(d.name, {})
        out[d.name] = {k: ([] if k in bad_here else (got[k] or [])) for k in FM_KEYS}
    return out, notes, unj, sorted(loose)


def normalize(pkgs, vocab):
    """套 alias 归一并对照词表：表外名字／同物挂两处的都退 1 点名（`legs:` 装域 id，不比词表）。"""
    canon, ins, alias = set(vocab["canonical"]), set(vocab["inputs"]), vocab["aliases"]
    fixed, notes, bad = {}, [], []
    for name, decl in sorted(pkgs.items()):
        row = {}
        for where, allowed, label in (("consumes", canon, "canonical"), ("inputs", ins, "inputs 族"),
                                      ("produces", canon, "canonical")):
            vals = []
            for v in decl[where]:
                if v in alias:
                    notes.append("%s 的 %s：%s 按词表归一为 %s" % (name, where, v, alias[v]))
                    v = alias[v]
                if v not in allowed:
                    bad.append("%s 的 %s 写了词表外的名字：%s（该族的允许值＝%s；改名请改词表，别散在包里重谈）" % (
                        name, where, v, label))
                vals.append(v)
            row[where] = sorted(set(vals))
        row["legs"] = sorted(set(decl["legs"]))
        both = sorted(set(row["consumes"]) & set(row["inputs"]))
        if both:
            bad.append("%s 的同一枚名字同时出现在 consumes 与 inputs：%s（边与入参只准挂一处）" % (name, "、".join(both)))
        fixed[name] = row
    return fixed, sorted(set(notes)), sorted(bad)


def domain_rows(args, show):
    """域原料：--catalog 读 mcp-catalog 快照、--domains 读逐行 jsonl。返回 (行, 来源说明)；读不到或形状不认识即退 1。"""
    if args.catalog:
        path = Path(args.catalog)
        if not path.is_file():
            raise SystemExit(die("--catalog 指了路径却读不到：%s（缺原料请别跑表三，本件不猜域清单）" % args.catalog))
        try:
            doc = json.loads(path.read_text(encoding="utf-8", errors="replace"))
        except ValueError as err:
            raise SystemExit(die("目录快照不是合法 JSON：%s（%s）" % (show(args.catalog), str(err)[:80])))
        rows = (doc.get("data") or {}).get("domains") if isinstance(doc, dict) else None
        if not isinstance(rows, list):
            raise SystemExit(die("目录快照里没有 data.domains 数组（顶层键＝%s）——本件按这一形读，换形请直说" % (
                ", ".join(sorted(doc)) if isinstance(doc, dict) else type(doc).__name__)))
        out = [r for r in rows if isinstance(r, dict)]
        return out, "目录快照＝%s（取 data.domains，枚数=%d）" % (show(args.catalog), len(out))
    path = Path(args.domains)
    if not path.is_file():
        raise SystemExit(die("--domains 指了路径却读不到：%s（缺原料请别跑表三，本件不猜域清单）" % args.domains))
    out, n = [], 0
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            n += 1
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            try:
                obj = json.loads(s)
            except ValueError as err:
                raise SystemExit(die("%s 第 %d 行不是合法 JSON：%s" % (show(args.domains), n, str(err)[:80])))
            if not isinstance(obj, dict):
                raise SystemExit(die("%s 第 %d 行不是对象（是 %s）——本件按枚行读，不猜" % (
                    show(args.domains), n, type(obj).__name__)))
            out.append(obj)
    return out, "逐行原料＝%s（行数=%d）" % (show(args.domains), len(out))


def main():
    ap = argparse.ArgumentParser(
        description="现算：孤点／待补入口（两列分开）／覆盖缺口（两口径并列）＋指路计数。"
                    "取数＝各包 SKILL.md frontmatter 的 consumes/inputs/produces/legs + 一份规范词表。")
    ap.add_argument("--repo", default=str(REPO), help="仓根（默认本件所在仓的根；输出里只打相对路径）")
    ap.add_argument("--vocabulary", default=str(HERE / "artifact-types.yaml"),
                    help="规范词表（默认 scripts/artifact-types.yaml；表外名字一律退 1）")
    ap.add_argument("--catalog", help="表三原料甲：mcp-catalog 快照（取 data.domains 的 id 与 external_status）")
    ap.add_argument("--domains", help="表三原料乙：逐行 jsonl（每行 {domain|id, external_status|status, legs?}）")
    ap.add_argument("--legacy-inputs-only", action="store_true", help="旧读法甲：表二只报 (a) 那一列（inputs）")
    ap.add_argument("--legacy-broken-only", action="store_true",
                    help="旧读法乙＝旧「断边」定义（consumes 里无任何件 produces），表二只报那一列")
    args = ap.parse_args()

    if args.legacy_inputs_only and args.legacy_broken_only:
        return die("--legacy-inputs-only 与 --legacy-broken-only 是两读法，只准挑一枚（缺省两枚都不带＝默认走两列分开）", 2)
    if args.catalog and args.domains:
        return die("--catalog 与 --domains 是两份域原料，只准挑一枚（本件不合并两份清单，免得谁覆盖谁说不清）", 2)

    repo = Path(args.repo)
    if not repo.is_dir():
        return die("读不到仓根：%s（本件按枚目录扫 SKILL.md，不换源不猜）" % repo, 2)
    vpath = Path(args.vocabulary)
    if not vpath.is_file():
        return die("读不到规范词表：%s（边与入参的口径全靠它，缺表不猜名）" % args.vocabulary)
    vocab = load_vocabulary(vpath)

    pkgs, notes, unj, loose = read_packages(repo)
    if not pkgs:
        return die("在 %s 下一枚 SKILL.md 都没读到——本件无从算表" % repo.name)
    pkgs, norm_notes, bad = normalize(pkgs, vocab)
    if bad:
        for b in bad:
            print("  表外：%s" % b, file=sys.stderr)
        return die("词表校验未过：%d 处包面名字对不上表（改名请改 %s，再跑本件）" % (len(bad), vpath.name))

    # 不可判的键不进任何一张表：受影响那格显式写「不可判」，各表自报行并列「取到 N 把／跳过 M 把」
    unj_keys_total = sorted((p, k) for p, ks in unj.items() for k in ks)
    unj_pkgs = sorted(unj)

    def skipped(keys):
        """该表涉及的键位里，有几把不可判、落在几枚包上。"""
        pairs = [(p, k) for p, ks in sorted(unj.items()) for k in ks if k in keys]
        return len(pairs), len({p for p, _k in pairs})

    def unj_note(keys):
        n, p = skipped(keys)
        if not n:
            return ""
        who = "、".join("%s/%s" % (x, y) for x, y in sorted((a, b) for a, bs in unj.items() for b in bs if b in keys))
        return "本表跳过 %d 把键／%d 枚包（不可判：%s）" % (n, p, who)

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

    def fam_of(a):
        for f, members in sorted(vocab["families"].items()):
            if a in members:
                return f
        return "(无族)"

    producers, consumers = {}, {}
    for name, row in sorted(pkgs.items()):
        for a in row["produces"]:
            producers.setdefault(a, []).append(name)
        for a in row["consumes"]:
            consumers.setdefault(a, []).append(name)
    for m in (producers, consumers):
        for k in m:
            m[k].sort()

    # 一、孤点：跨件入度与出度都为 0（inputs 不算边、自环不算边；不可判的包不进本表，另列一行）
    iso, loops, unj_rows = [], [], []
    for name, row in sorted(pkgs.items()):
        if name in unj:
            unj_rows.append("%s ｜ 不可判（键：%s；本表不判它孤不孤）" % (name, "、".join(unj[name])))
            continue
        out_deg = {q for a in row["produces"] for q in consumers.get(a, []) if q != name}
        in_deg = {q for a in row["consumes"] for q in producers.get(a, []) if q != name}
        if not out_deg and not in_deg:
            iso.append(name)
        self_edges = sorted(a for a in row["produces"] if a in row["consumes"] and producers.get(a) == [name])
        if self_edges:
            loops.append("%s 自环：%s" % (name, "、".join(self_edges)))
    taken_pkgs = len(pkgs) - len(unj_rows)

    # 二、待补入口：(a) inputs 列 ∥ (b) 断口列 —— 分开报、不相加；不可判的键不进列
    inputs_rows, inputs_unj = {}, []
    for name, row in sorted(pkgs.items()):
        if "inputs" in unj.get(name, []):
            inputs_unj.append("%s/inputs" % name)
            continue
        for a in row["inputs"]:
            inputs_rows.setdefault(a, []).append(name)
    for users in inputs_rows.values():
        users.sort()
    broken_rows, broken_unj = [], []
    for name, row in sorted(pkgs.items()):
        if "consumes" in unj.get(name, []):
            broken_unj.append("%s/consumes" % name)
            continue
        for a in row["consumes"]:
            if not producers.get(a):
                broken_rows.append("%s consumes %s（全仓无任何件 produces）" % (name, a))

    # 三、覆盖缺口：弱口径（域 id 出现在包面文）∥ 强口径（件面显式 legs: 含该域 id）
    face_text = {}
    for name in sorted(pkgs):
        blob = []
        for g in FACE_GLOBS:
            f = repo / name / g
            if f.is_file():
                blob.append(f.read_text(encoding="utf-8", errors="replace"))
        face_text[name] = "\n".join(blob)
    legs_decl = {a for name, row in sorted(pkgs.items()) for a in row["legs"]}

    label = repo.name or str(repo)
    print("scenario_graph｜取数＝各包 SKILL.md frontmatter 的 consumes/inputs/produces/legs｜"
          "词表＝%s（canonical %d 枚／inputs 族 %d 枚／alias %d 枚／family %d 枚）｜包 %d 枚（扫自 %s）" % (
              rel(vpath), len(vocab["canonical"]), len(vocab["inputs"]), len(vocab["aliases"]),
              len(vocab["families"]), len(pkgs), label))
    unj_notes = ["%s：%s 的值归属存疑（该键区域内先有映射行、后又冒类列表行；本件按不可判处理：不并入图、不进任何表、不读成空清单）"
                 % (p, "、".join(ks)) for p, ks in sorted(unj.items())]
    for n in notes + unj_notes + loose + norm_notes:
        print("  注：%s" % n)
    print()
    print("== 表一 孤点（跨件入度与出度皆 0；inputs 不算边、自环不算边）==")
    for n in unj_rows:
        print("  " + n)
    for n in iso:
        print("  %s ｜ %s" % (n, rel(repo / n / "SKILL.md")))
    print("  枚数=%d（由上列现算）｜全包=%d 枚｜取到 %d 枚包／跳过 %d 枚包（不可判 %d 把键）｜非孤点=%d 枚" % (
        len(iso), len(pkgs), taken_pkgs, len(unj_rows), len(unj_keys_total), taken_pkgs - len(iso)))
    if loops:
        print("  附注·自环（自产自消，不计入链条）：")
        for l in loops:
            print("    " + l)
    print()
    if args.legacy_inputs_only:
        print("== 表二 待补入口（旧读法甲：只报 inputs 那一列）==")
    elif args.legacy_broken_only:
        print("== 表二 断边（旧读法乙：consumes 的工件无任何件 produces）==")
    else:
        print("== 表二 待补入口（两列来源分开报，各带自己枚数，不给合计数）==")
    if not (args.legacy_broken_only or args.legacy_inputs_only):
        print("  列 (a) inputs＝用户/外部必须提供（入参天经地义由人给，不算我们的漏）")
    if not args.legacy_broken_only:
        for a, users in sorted(inputs_rows.items()):
            extra = "（族：%s）" % fam_of(a) if fam_of(a) != "(无族)" else ""
            print("    %-22s %d 件消：%s｜%d 件产%s" % (a, len(users), "、".join(users), len(producers.get(a, [])), extra))
        print("  列 (a) 枚数=%d 项／%d 条包–项配对｜取到 %d 把键／跳过 %d 把（不可判：%s）" % (
            len(inputs_rows), sum(len(v) for v in inputs_rows.values()),
            len(pkgs) - len(inputs_unj), len(inputs_unj), "、".join(inputs_unj) or "无")
            if inputs_unj else "  列 (a) 枚数=%d 项／%d 条包–项配对（均由上列现算）｜取到 %d 把键／跳过 0 把" % (
            len(inputs_rows), sum(len(v) for v in inputs_rows.values()), len(pkgs)))
    if not args.legacy_inputs_only:
        if not args.legacy_broken_only:
            print("  列 (b) 断口＝consumes 里无任何件 produces 的项（这才是该补的件）")
        for b in broken_rows:
            print("    " + b)
        cons_total = sum(len(row["consumes"]) for name, row in sorted(pkgs.items()) if "consumes" not in unj.get(name, []))
        print("  %s枚数=%d（由上列现算）｜consumes 总项=%d｜取到 %d 把键／跳过 %d 把（不可判：%s）" % (
            "" if args.legacy_broken_only else "列 (b) ", len(broken_rows), cons_total,
            len(pkgs) - len(broken_unj), len(broken_unj), "、".join(broken_unj) or "无"))
    if not (args.legacy_broken_only or args.legacy_inputs_only):
        print("  本表按裁定不给合计数：(a) 与 (b) 是两类东西，加成一枚就抹掉了这个差别。")
    print()
    print("== 表三 覆盖缺口（live 域无人引用其数据腿；两口径并列、互不覆盖）==")
    if not (args.catalog or args.domains):
        print("  缺位：未给 --catalog 也未给 --domains（域清单由调用方给原料；A 路那一路交付的 jsonl 走 --domains）")
        print("  ⇒ 两版都不作数：这一表不列空条目、不打 0（打了就等于假装查过）")
    else:
        rows, src = domain_rows(args, show)
        parsed = [(str(r.get("domain") or r.get("id") or "(无名)"),
                   str(r.get("external_status") or r.get("status") or ""), r) for r in rows]
        live_rows = [x for x in parsed if x[1] == "live"]
        live = sorted({dom for dom, _st, _r in live_rows})
        nonlive = len(parsed) - len(live_rows)
        unmarked = sorted({dom for dom, _st, r in live_rows if not isinstance(r.get("legs"), list)})
        weak_cov, weak_gap = [], []
        for dom in live:
            hits = sorted(n for n, blob in sorted(face_text.items()) if dom in blob)
            if hits:
                weak_cov.append("%s ← 面文出现于 %s" % (dom, "、".join(hits)))
            else:
                weak_gap.append("%s（包面文里这枚 id 原文 0 处）" % dom)
        print("  弱口径＝域 id 原文出现在包面文（SKILL／SKILL.en／README／README.en）即算引用｜文本出现 ≠ 数据腿引用")
        for x in weak_cov:
            print("    引用到：" + x)
        for x in weak_gap:
            print("    缺口：" + x)
        print("    弱口径 枚数：live=%d｜引用到=%d｜缺口=%d" % (len(live), len(weak_cov), len(weak_gap)))
        print("  强口径＝某件 frontmatter 显式声明 legs: 含该域 id 原文（值＝catalog 的域 id，不是工具名）")
        n_sk, p_sk = skipped({"legs", "produces"})
        if n_sk:
            print("    本表跳过 %d 把键／%d 枚包（不可判：legs 或 produces 读不出归属的那些；两版读数只覆盖取到的键）" % (n_sk, p_sk))
        print("    现读：全仓声明 legs: 的件数=%d｜legs 值枚数=%d" % (
            sum(1 for row in pkgs.values() if row["legs"]), len(legs_decl)))
        strong_cov, strong_gap = [], []
        for dom in live:
            hits = sorted(n for n, row in sorted(pkgs.items()) if dom in row["legs"])
            if hits:
                strong_cov.append("%s ← %s" % (dom, "、".join(hits)))
            else:
                strong_gap.append(dom)
        for x in strong_cov:
            print("    引用到：" + x)
        if any(row["legs"] for row in pkgs.values()):
            for x in strong_gap:
                print("    缺口：" + x)
            print("    强口径 枚数：live=%d｜引用到=%d｜缺口=%d" % (len(live), len(strong_cov), len(strong_gap)))
        else:
            print("    ⇒ 强口径不作数：这一层按裁定「等 A 路原料在盘再引入显式 legs:」，件面现未引入；"
                  "未引入不等于无引用，故 live=%d 枚只报缺位、不记 0 结论" % len(live))
        if unmarked:
            print("    原料完整度：%d 枚 live 行未标 legs（本件的强口径读物面声明，与原料标不标腿是两件事）" % len(unmarked))
        print("    " + src + "｜非 live 行=%d 枚（不进本表）" % nonlive)
    print()
    print("== 附 指路（包面提到其他包名；不算边、不进图，与孤点并列读即可）==")
    ref_rows = []
    for name in sorted(pkgs):
        for other in sorted(pkgs):
            if other == name:
                continue
            c = face_text[name].count(other)
            if c:
                ref_rows.append((name, other, c))
    for name, other, c in ref_rows:
        print("  %s 面上提到 %s：现读 %d 次" % (name, other, c))
    print("  枚数=%d 条｜合计出现次数=%d（均由上列现算）｜这一列只算气氛，别拿它当图上的边" % (
        len(ref_rows), sum(c for _n, _o, c in ref_rows)))
    if unj_keys_total:
        # 这一行只在有话说时长：干净一趟的 stdout 不该被汇总行长胖；但一旦出现，单位必须两值并列（把键／枚包）
        print()
        print("  不合=0｜不可判=%d 把键／%d 枚包（不可判＝该键的值归属读不出，不并入图、不进任何表；"
              "退码非 0——认不出＝响亮不可签）" % (len(unj_keys_total), len(unj_pkgs)))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
