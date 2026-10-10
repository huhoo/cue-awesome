#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_public_hygiene.py — 公开面卫生机检闸（CONTRIBUTING §公开面卫生 的可执行形，五禁逐条成码）。

发布包是给用户用的成品，不是施工日志。本闸把「五禁」变成可跑的正则＋指路存在性检查：
成品面命中即 ERROR，CHANGELOG 按留痕原则一律 WARN（历史条目不回改，人裁）。纯 stdlib、零网络。

用法：
    python3 scripts/check_public_hygiene.py              全仓跑（有 ERROR 则 exit 1）
    python3 scripts/check_public_hygiene.py --strict     WARN 也计入失败（提交前自用好）
    python3 scripts/check_public_hygiene.py --quiet      只报汇总与码表
    python3 scripts/check_public_hygiene.py --selftest   跑 scripts/fixtures/hygiene/ 正反守护样
                                                         （违例样必须发红、合规样必须发绿，
                                                          并双跑全仓报告取字节对拍验确定性）
    python3 scripts/check_public_hygiene.py --file PATH  只检单个文件（岗单/新票探针用；
                                                         文件路径决定它被当作哪一类面）
    python3 scripts/check_public_hygiene.py --list       列出被扫的面与各自规则数

五禁与码（详行先打码，再打面/行号/规格；末行「码表:」只列本次真正用到的码）：
    H-TICKET   ① 工单/票号内部流水（M1xx、PR#123 类）
    H-PATH     ② 工作区悬空路径（verify/ logs/ dispatch/ BOARD 等仓外或他目录指路）
    H-POINTER  ②b 包内相对指路目标不存在（assets/… references/… 等——机检可验的那一半）
    H-STATE    ③ 施工状态语（在途/证据票/候账/候 X 裁/随我铃/收卷/交卷/派单…）
    H-DATE     ④ 内部时点戳（「截至 20xx」类过程日期；边界该直接写边界）
    H-ATTRIB   ⑤ 过程归因与账目叙事（需求凭据=/实测由 M1xx/账回/跑回/判词/VERIFIED…）

面与分级（判据口径：能力句直述、指路可跟随、归因留内部）：
    成品面  SKILL*.md / README*.md（含仓根集合仓说明）/ assets/** / references/**  → 五禁全适用，命中=ERROR
    CHANGELOG  CHANGELOG*.md                                                       → 守①③④⑤（②不在此面），命中=WARN
    不检面  CONTRIBUTING*（贡献者文档，内部指路是它的职责）/ docs/ / scripts/ / NOTICE / LICENSE / .github
    「lead」一类英文产品词**不入词表**（cue-lead-pieces 的 lead pieces 是正式术语，入表即假阳）。

岗单周检与新票探针接法（照抄即可，勿改路径）：
    cd <仓根> && python3 -B scripts/check_public_hygiene.py --quiet; echo exit=$?          # 周检：整仓一道门
    cd <仓根> && python3 -B scripts/check_public_hygiene.py --selftest                      # 周检：闸本体非恒真
    cd <仓根> && python3 -B scripts/check_public_hygiene.py --file <包>/SKILL.md --strict    # 新票：只检本票改动的面
"""

from __future__ import annotations

import argparse
import hashlib
import os
import io
import re
import sys
import contextlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIXDIR = ROOT / "scripts" / "fixtures" / "hygiene"

NON_SKILL_DIRS = {".github", "docs", "scripts", "assets", ".git", ".workbuddy", ".attic"}
SKIP_DIR_NAMES = {"__pycache__", "dist", "build", "node_modules", ".venv", "fixtures"}

# ---------------------------------------------------------------- 五禁规则表
# 每条：(码, 五禁项, 编译后正则, 人读规格)
# 词表只收「过程遥测」的确形：宁可窄而准，宽则由人另开票加词。
RULES = (
    ("H-TICKET", "①", re.compile(r"(?<![A-Za-z0-9])M\d{2,4}(?![A-Za-z0-9])|(?<![A-Za-z])PR\s*#?\d{2,}"),
     "成品面与 CHANGELOG 不写内部流水号（工单/票号/PR 号）；要引能力来源就写能力本身"),
    ("H-PATH", "②", re.compile(r"\bverify/|\blogs/|\bdispatch/|\bBOARD\b|dispatch\b"),
     "仓外或他目录指路不得出现在成品面（verify/、logs/、dispatch/、BOARD）；指路只许相对本包"),
    ("H-STATE", "③", re.compile(r"在途|证据票|候账|候\s*(?:Owner|M\d|[1-6]\.1)|随我铃|收卷|交卷|派单|(?<!作)工单|候裁|候批|待你|等你一句"),
     "施工状态语禁入成品面（读者无从解释「在途/候账/随我铃」是什么意思）"),
    ("H-DATE", "④", re.compile(r"截至\s*20\d{2}(?:[-/.年]\d{1,2}(?:[-/.日]\d{1,2})?)?|20\d{2}-\d{2}-\d{2}\s*(?:未立|未证|实测)"),
     "过程日期不写在墙上：能力边界直接写边界（「本件不做 X」），何时测的不进成品面"),
    ("H-ATTRIB", "⑤", re.compile(r"需求凭据|实测由|账回|跑回|判词|VERIFIED|派\s*[1-6]\.1|归\s*[1-6]\.1|据\s*[1-6]\.1|哨兵单枪|catalog-diff"),
     "过程归因与账目叙事禁入成品面（出处叙事进内部账；成品只写结论形制：能做什么/不能做什么/以什么为准）"),
)

SKIP_OUTPUT_POINTERS: list[tuple[str, int, str]] = []

CHANGELOG_CODES = {"H-TICKET", "H-STATE", "H-DATE", "H-ATTRIB"}  # ② 不在 CHANGELOG 面判（charter 只列 ①③④⑤）
LEGEND = {c: spec for c, _, _, spec in RULES}
LEGEND["H-POINTER"] = "包内相对指路目标不存在——要么补文件，要么删指路；不许留断链"

# 指路提取：markdown 链接目标 + 反引号内的相对路径形
MD_LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
BACKTICK_PATH = re.compile(r"`((?:assets|references|scripts|docs)/[^`\s]+)`")
PLACEHOLDER = re.compile(r"[<>*{}××…_|\s]|\d{3,}")
# 运行时产出路径的两种信号：行内有出生动词，或同名的东西在包里别处存在（模板/范例副本）。
OUTPUT_VERB = re.compile(r"写\s*`|交付物|产出|生成|落盘|输出|模板\s*=|写入")


# ---------------------------------------------------------------- 面分类
def classify(path: Path) -> str | None:
    """返回 'product'（成品面）|'changelog'|None（不检/仓外）。入参可为仓外路径：判 None 交调用方从严。"""
    try:
        parts = path.resolve().relative_to(ROOT).parts
    except ValueError:
        return None
    if any(p in SKIP_DIR_NAMES for p in parts[:-1]):
        return None
    name = path.name
    if len(parts) == 1:  # 仓根文件
        if name.startswith("README"):
            return "product"
        return None
    if name.startswith("CONTRIBUTING") or name in {"NOTICE.md", "LICENSE.md"}:
        return None
    if name.startswith("CHANGELOG"):
        return "changelog"
    if name.startswith("SKILL") or name.startswith("README"):
        return "product"
    if "assets" in parts or "references" in parts:
        return "product"
    return None


def iter_faces() -> list[Path]:
    out = []
    for path in sorted(ROOT.rglob("*.md")):
        if classify(path) is not None:
            out.append(path)
    return out


# ---------------------------------------------------------------- ②b 指路存在性
def _pkg_root(path: Path) -> Path:
    """本包根目录：仓根文件→仓根；否则顶层 skill 目录。仓外路径→该文件所在目录。"""
    try:
        rel = path.resolve().relative_to(ROOT)
    except ValueError:
        return path.parent
    return ROOT if len(rel.parts) == 1 else ROOT / rel.parts[0]


def _resolves(pkg: Path, own: Path, rel: str) -> bool:
    """指路可跟随 = 相对本包根 或 相对本文件目录 任一命中（`../` 原样交给路径解析，不手剥）；
    无扩展名时按前缀唯一匹配（`references/01` 这类简写能对上 01-xxx.md 就不算断链）。"""
    cands = []
    for base in (own, pkg):
        target = (base / rel).resolve()
        cands.append(target)
        if not rel.endswith("/") and target.suffix == "":
            cands.extend(sorted(target.parent.glob(target.name + "*")))
    for c in cands:
        if rel.endswith("/") or c.suffix == "":
            if c.is_dir():
                return True
        elif c.is_file():
            return True
    return False


def _basename_elsewhere(pkg: Path, rel: str, own: Path, text_path: Path) -> bool:
    """同名件在包内别处存在 → 多半是运行时产出路径或范例副本，不当断链。"""
    name = Path(rel).name
    if not name or name.count(".") < 1:
        return False
    for cand in pkg.rglob(name):
        if cand != text_path:
            return True
    return False


def _pointers(text: str, pkg: Path, own: Path, as_file: Path | None = None) -> list[tuple[int, str, str]]:
    """返回 (行号, 指路串, 原因)。只判本包目录内的指路；他目录由 H-PATH 管。
    判为运行时产出路径的记进 skipped（报告尾行公开计数，不静默吞）。"""
    out = []
    for lineno, line in enumerate(text.split("\n"), 1):
        cands = {m.group(1) for m in MD_LINK.finditer(line)} | {m.group(1) for m in BACKTICK_PATH.finditer(line)}
        for cand in sorted(cands):
            t = cand.strip("<>\"'()（）,，。;；")
            if not t or t.startswith(("#", "http", "mailto:", "/")):
                continue
            if not re.match(r"^(?:\.\./)*(?:assets|references|scripts|docs)/", t):
                continue
            if PLACEHOLDER.search(t):
                continue  # 模板占位与通配不算指路（assets/××.md 类）
            if _resolves(pkg, own, t):
                continue
            if OUTPUT_VERB.search(line) or _basename_elsewhere(pkg, t, own, as_file or own / t.name):
                SKIP_OUTPUT_POINTERS.append((lineno, t, ""))
                continue
            out.append((lineno, t, "本包根与本文件目录两侧都找不到目标"))
    return out


def check_pointers(path: Path, text: str) -> list[tuple[int, str, str]]:
    return _pointers(text, _pkg_root(path), path.parent, path)


# ---------------------------------------------------------------- 单文件检查
def check_file(path: Path) -> list[tuple[str, int, str, str]]:
    """返回 [(码, 行号, 严重级 note, 详句)]；severity 由调用方按面定。"""
    face = classify(path)
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.split("\n")
    finds: list[tuple[str, int, str, str]] = []

    if face == "product":
        for lineno, ptr, why in check_pointers(path, text):
            finds.append(("H-POINTER", lineno, f"包内指路 `{ptr}` {why}（规格：{LEGEND['H-POINTER']}）"))

    for code, ban, pat, spec in RULES:
        if face == "changelog" and code not in CHANGELOG_CODES:
            continue
        for lineno, line in enumerate(lines, 1):
            for m in pat.finditer(line):
                finds.append((code, lineno, f"五禁{ban}命中「{m.group(0)}」（规格：{spec}）"))
                break  # 每行每码只报一次，报告不被同一行刷屏
    return sorted(finds, key=lambda x: (x[1], x[0]))


# ---------------------------------------------------------------- 全仓跑
def run_repo(strict: bool, quiet: bool) -> tuple[int, int, int]:
    SKIP_OUTPUT_POINTERS.clear()
    faces = iter_faces()
    errors = warnings = 0
    used_codes: set[str] = set()
    per_file: list[tuple[Path, str, list]] = []

    for f in faces:
        face = classify(f)
        sev = "ERROR" if face == "product" else "WARN"
        finds = check_file(f)
        if finds:
            per_file.append((f, sev, finds))
        for code, _, _ in finds:
            used_codes.add(code)
            if sev == "ERROR":
                errors += 1
            else:
                warnings += 1

    if not quiet:
        print(f"公开面卫生机检 — 被扫面 {len(faces)} 个（{sum(1 for p in per_file)} 个有发现）\n")
        rel = ROOT
        for f, sev, finds in per_file:
            print(f"  {sev:<5} {f.relative_to(rel)}（{len(finds)} 条）")
            for code, lineno, detail in finds:
                print(f"        [{code}] 第 {lineno} 行：{detail}")
        print()
        print("  码表: " + "; ".join(f"{c}→{LEGEND[c]}" for c in sorted(used_codes)))

    print(f"指路附账：判为运行时产出路径而跳过 {len(SKIP_OUTPUT_POINTERS)} 条（信号=行内有出生动词，或同名件在包内别处存在）")
    print(f"\nsummary: 面 {len(faces)}，ERROR {errors}，WARN {warnings}"
          + ("（--strict：WARN 计入失败）" if strict and warnings else ""))
    if errors:
        return 1
    if strict and warnings:
        return 1
    return 0


# ---------------------------------------------------------------- 守护样自测
def _fixture_findings(dirpath: Path) -> list[tuple[str, int, str, str]]:
    """守护样内 check_pointers 需要 pkg 基准，这里按目录直扫（复刻面判定，不依赖 ROOT 分类）。"""
    finds: list[tuple[str, int, str, str]] = []
    for f in sorted(dirpath.rglob("*.md")):
        text = f.read_text(encoding="utf-8", errors="replace")
        is_changelog = f.name.startswith("CHANGELOG")
        for lineno, line in enumerate(text.split("\n"), 1):
            for code, ban, pat, spec in RULES:
                if is_changelog and code not in CHANGELOG_CODES:
                    continue
                m = pat.search(line)
                if m:
                    finds.append((code, lineno, f.name, f"{ban}命中「{m.group(0)}」"))
        if not is_changelog:
            for lineno, ptr, why in _pointers(text, dirpath, f.parent, f):
                finds.append(("H-POINTER", lineno, f.name, f"`{ptr}` {why}"))
    return finds


def _pointers_in(pkg: Path, f: Path, text: str) -> list[tuple[int, str, str]]:
    out = []
    for lineno, line in enumerate(text.split("\n"), 1):
        cands = {m.group(1) for m in MD_LINK.finditer(line)} | {m.group(1) for m in BACKTICK_PATH.finditer(line)}
        for cand in sorted(cands):
            t = cand.strip("<>\"'()（）,，。;；")
            if not t or t.startswith(("#", "http", "mailto:", "/")):
                continue
            if not re.match(r"^(?:\.\./)?(?:assets|references|scripts|docs)/", t):
                continue
            if PLACEHOLDER.search(t):
                continue
            rel = t[3:] if t.startswith("../") else t
            target = pkg / rel
            if rel.endswith("/") or target.suffix == "":
                if not target.is_dir():
                    out.append((lineno, t, "目录不存在"))
            elif not target.is_file():
                out.append((lineno, t, "目标文件不存在"))
    return out


def selftest() -> int:
    """三档自跑（C-53）：① 违例样必须每禁发红；② 合规样必须零发条；③ 全仓报告双跑字节一致。

    缺任一方向，绿灯就是假绿（恒真检查必然全过）。
    """
    ok = True
    bad = FIXDIR / "bad"
    good = FIXDIR / "good"
    if not bad.is_dir() or not good.is_dir():
        print(f"SELFTEST FAIL: 守护样目录缺失（{bad} / {good}）")
        return 1

    SKIP_OUTPUT_POINTERS.clear()
    bad_f = _fixture_findings(bad)
    bad_codes = {c for c, _, _, _ in bad_f}
    want = {c for c, _, _, _ in RULES} | {"H-POINTER"}
    print(f"档① 违例样：应发红，实发 {len(bad_f)} 条，覆盖禁项 {len(bad_codes & want)}/{len(want)}")
    for c in sorted(want - bad_codes):
        print(f"   未发红 → {c}（守护样没种下这一禁，或词表漏了它）")
        ok = False

    # 档①b 分级面正确：bad/CHANGELOG.md 必须发红 ①③④⑤ 之一，且绝不判 ②（charter 只列 ①③④⑤）
    cl = [x for x in bad_f if x[2] == "CHANGELOG.md"]
    cl_codes = {c for c, _, _, _ in cl}
    if not (cl_codes & CHANGELOG_CODES):
        print("   CHANGELOG 面未发红 → 分级失效（历史条目留痕通道没接住票号）")
        ok = False
    if cl_codes & {"H-PATH", "H-POINTER"}:
        print(f"   CHANGELOG 面误判 ②：{sorted(cl_codes & {'H-PATH', 'H-POINTER'})}（章程 CHANGELOG 只守 ①③④⑤）")
        ok = False
    print(f"档①b CHANGELOG 面：发红 {len(cl)} 条，码 {sorted(cl_codes)}，②不判={'对' if not (cl_codes & {'H-PATH','H-POINTER'}) else '错'}")

    good_f = _fixture_findings(good)
    print(f"档② 合规样：应零发条，实发 {len(good_f)} 条")
    for c, lineno, fname, d in good_f:
        print(f"   意外发条 → {fname}:{lineno} [{c}] {d}")
        ok = False

    buf_a, buf_b = io.StringIO(), io.StringIO()
    for buf in (buf_a, buf_b):
        with contextlib.redirect_stdout(buf):
            run_repo(False, True)
    ha = hashlib.sha256(buf_a.getvalue().encode()).hexdigest()[:16]
    hb = hashlib.sha256(buf_b.getvalue().encode()).hexdigest()[:16]
    print(f"档③ 全仓双跑确定性：报告 sha256 前 16 位 {ha} vs {hb} → {'一致' if ha == hb else '不一致'}")
    if ha != hb:
        ok = False

    print(f"selftest: {'ALL GREEN（闸能红、能绿、可复现）' if ok else 'FAIL'}")
    return 0 if ok else 1


# ---------------------------------------------------------------- 单文件探针
def check_one(path: Path, strict: bool) -> int:
    if not path.is_file():
        print(f"[出错] 文件不存在：{path}")
        return 1
    path = path.resolve()
    face = classify(path)
    if face is None:
        # 仓外或不在检面（run 目录里的待发文稿）：按成品面从严判，不给假绿
        inside = str(path).startswith(str(ROOT) + "/")
        face = "product"
        note = "（仓内但非公开面，按成品面从严判）" if inside else "（仓外路径，按成品面从严判）"
    else:
        note = f"（面分类：{face}）"
    sev = "ERROR" if face == "product" else "WARN"
    text = path.read_text(encoding="utf-8", errors="replace")
    finds: list[tuple[str, int, str]] = []
    for code, ban, pat, spec in RULES:
        if face == "changelog" and code not in CHANGELOG_CODES:
            continue
        for lineno, line in enumerate(text.split("\n"), 1):
            m = pat.search(line)
            if m:
                finds.append((code, lineno, f"五禁{ban}命中「{m.group(0)}」（规格：{spec}）"))
    if face == "product":
        base = _pkg_root(path)
        for lineno, ptr, why in _pointers(text, base, path.parent, path):
            finds.append(("H-POINTER", lineno, f"包内指路 `{ptr}` {why}（规格：{LEGEND['H-POINTER']}）"))
    finds.sort(key=lambda x: (x[1], x[0]))
    codes = {c for c, _, _ in finds}
    if finds:
        print(f"{sev}: {path.name}（{len(finds)} 条）{note}")
        for code, lineno, detail in finds:
            print(f"  - [{code}] 第 {lineno} 行：{detail}")
    else:
        print(f"PASS: {path.name} 五禁零命中、指路可跟随 {note}")
    print("  码表: " + "; ".join(f"{c}→{LEGEND[c]}" for c in sorted(codes)))
    if not finds:
        return 0
    return 1 if (sev == "ERROR" or strict) else 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description="公开面卫生机检闸（五禁＋指路存在性，纯 stdlib 零网络）。",
        epilog="出口：ERROR=成品面违禁（发布打回，与红线同级）；WARN=CHANGELOG 命中（留痕原则，人裁）。"
               "判定与词表全集以本脚本现值为准（--help 看五禁）。")
    ap.add_argument("--strict", action="store_true", help="WARN 也计失败")
    ap.add_argument("--quiet", action="store_true", help="只报汇总")
    ap.add_argument("--selftest", action="store_true", help="跑 scripts/fixtures/hygiene/ 正反守护样＋双跑确定性")
    ap.add_argument("--file", metavar="PATH", help="只检一个文件（岗单周检/新票探针）")
    ap.add_argument("--list", action="store_true", help="列出被扫的面")
    a = ap.parse_args()

    if a.selftest:
        return selftest()
    if a.file:
        return check_one(Path(a.file), a.strict)
    if a.list:
        faces = iter_faces()
        for f in faces:
            print(f"{classify(f):<9} {f.relative_to(ROOT)}")
        print(f"\n共 {len(faces)} 面，规则 {len(RULES)} 禁 + H-POINTER")
        return 0
    return run_repo(a.strict, a.quiet)


if __name__ == "__main__":
    try:
        code = main()
        sys.stdout.flush()
    except BrokenPipeError:
        code = 1  # 探针常被 `| head` 截：按管道语义收，不把 Traceback 当结论
    try:
        sys.stdout.close()  # 显式关，避开解释器退出时的隐式 flush 报错
    except BrokenPipeError:
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
    sys.exit(code)
