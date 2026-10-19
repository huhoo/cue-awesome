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
    H-STALE    ③b 施工进度标签（P0 骨架／细化候×开单／仍待完善…）——**只判成品面**（历史条目不回改，见 CONTRIBUTING 留痕原则）
    H-DATE     ④ 内部时点戳（「截至 20xx」类过程日期；边界该直接写边界）
    H-ATTRIB   ⑤ 过程归因与账目叙事（需求凭据=/实测由 M1xx/账回/跑回/判词/VERIFIED…）
    H-GIFT-UNIT ⑥ §5-1 对外额度句**两个数字各自带单位**（触发串＝送 500／500…每日 10／500…signup·daily·per day；
               `500` 与 `10` 之后窗口内各须有「积分／credits」，**缺任一即发条**，命中文字＝那枚裸数字）
               ——**WARN 族**（不是五禁本体，报文里打「口径⑥」不打「五禁⑥」）：判据串显式列出，宽式子串重复禁用；
               射程限 README／SKILL 门面句与包内 references，assets／examples 模板与样例面不判；CHANGELOG 不判（逐码不入门）

面与分级（判据口径：能力句直述、指路可跟随、归因留内部）：
    成品面  SKILL*.md / README*.md（含仓根集合仓说明）/ assets/** / references/**  → 五禁全适用（含 ③b 子项），命中=ERROR
    CHANGELOG  CHANGELOG*.md                                                       → 守①③④⑤（②③b⑥不在此面），命中=WARN
    逐码降级  WARN_CODES＝{H-GIFT-UNIT}：这支即便命中成品面也记 **WARN** 不记 ERROR——它判的是「等他票补齐」的
              过渡态（M288 落字前应红、落字后归零），拿 ERROR 去卡会把整仓门钉死在别人名下的在途字上。
              计数因此**逐条走**（一枚面可同时出两档），表头显该面最重的一档。
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
    ("H-PATH", "②", re.compile(r"\bverify/|\blogs/|\bdispatch/|\bBOARD\b|(?<![\w_])dispatch(?![\w_])"),
     "仓外或他目录指路不得出现在成品面（verify/、logs/、dispatch/、BOARD）；指路只许相对本包"),
    ("H-STATE", "③", re.compile(r"在途|证据票|候账|候\s*(?:Owner|M\d|[1-6]\.1)|随我铃|收卷|交卷|派单|(?<!作)工单|候裁|候批|待你|等你一句"),
     "施工状态语禁入成品面（读者无从解释「在途/候账/随我铃」是什么意思）"),
    # ③b：施工进度标签——与 ③ 同族但词面不同（「P0 骨架」说的是包的状态，不是「在途」这类流程遥测）。
    # **只判成品面**：历史 CHANGELOG 条目里「由 P0 骨架重写为九节」是当时的 factual record，按留痕原则不判，
    # 故本码**不进 CHANGELOG_CODES**（那是整面豁免之外的逐码豁免，与留痕原则同一层）。
    ("H-STALE", "③b", re.compile(r"P[0-9]\s*骨架|骨架\s*·\s*设计权威|(?:仍是|尚是|还是|暂为|尚在)\s*(?:纯)?骨架"
                                  r"|(?:细化|完善|扩写|补全)\s*候\s*[^，。；、）)]{0,12}(?:开单|派单|开票)"
                                  r"|候\s*[^，。；、）)]{0,10}\s*(?:细化|完善|补全|开单)"
                                  r"|待(?:细化|补全|扩写|完善)|占位待(?:补|填)|TODO\s*[:：]|FIXME"),
     "③ 的子项：成品面不写施工进度标签（「P0 骨架」「细化候×开单」「仍待完善」「TODO:」类）——它写的是包的状态，不是能力；只判成品面"),
    ("H-DATE", "④", re.compile(r"截至\s*20\d{2}(?:[-/.年]\d{1,2}(?:[-/.日]\d{1,2})?)?|20\d{2}-\d{2}-\d{2}\s*(?:未立|未证|实测)"),
     "过程日期不写在墙上：能力边界直接写边界（「本件不做 X」），何时测的不进成品面"),
    ("H-ATTRIB", "⑤", re.compile(r"需求凭据|实测由|账回|跑回|判词|VERIFIED|派\s*[1-6]\.1|归\s*[1-6]\.1|据\s*[1-6]\.1|哨兵单枪|catalog-diff"),
     "过程归因与账目叙事禁入成品面（出处叙事进内部账；成品只写结论形制：能做什么/不能做什么/以什么为准）"),
    # ⑥：对外额度句缺单位。唯一许可句是 §5-1「注册送 500 积分、每日 10 积分，以服务端为准」——
    # 这条红线由闸守，不由 lead 的眼睛守（M289）。判据串**显式列出**，不用宽式：
    # 宽式「任意 ≥10 字子串同行重复」实测跑出 95 枚假红，猜串读出过一枚假缺（同日两枚教训）。
    # **M298 新 canon＝两个数字都要各自带单位**（Owner 令④「要单位」；旧写法是「行内任意处出现积分／credits
    # 即整行放行」，那一支全行负向前瞻比令宽——`500 积分、每日再 +10` 这种 10 裸着的并列形从此发条）。
    # 现形制：`500` 之后窗口（10 字内）须含单位、`10` 之后窗口须含单位，**缺一即发条**，命中文字就是那枚裸数字。
    # 已知抓不到、也不许为它改成跨行匹配：`500 积分、\n每日再 +10 积分` 这类**跨行句形**——尺按行匹配，
    # 此形由 4.1 的逐面判据守护（M298 票面③；改成跨行会牵动其它码的射程）。
    # 与 H-STALE 同族形制：**不进 CHANGELOG_CODES**；射程再限门面句与 references（见 GIFT_SCOPE_SKIP，
    # assets／examples 不在尺内＝**不得拿「全仓零命中」替这两个面签字**）。
    ("H-GIFT-UNIT", "⑥", re.compile(
        r"^(?=.*(?:送\s*500|500[^\n]{0,40}?每日[^\n]{0,8}?(?:再\s*)?\+?10|500[^\n]{0,90}?(?:signup|daily|per day)))"
        r".*?(?P<hit>(?<![\d.,])500(?![\d])(?![^\n]{0,10}?(?:积分|(?i:credits)))"
        r"|(?<![\d.,])10(?![\d])(?![^\n]{0,10}?(?:积分|(?i:credits))))"),
     "对外额度句**两个数字都要带单位**（§5-1 许可句形：注册送 500 积分、每日 10 积分，以服务端为准）——任一枚裸着就是承诺，不是事实"),
)

SKIP_OUTPUT_POINTERS: list[tuple[str, int, str]] = []
EXEMPT_DISCARDED: list[tuple[str, str]] = []   # 因窄化被弃用的测试面同名件命中（报账用，不静默吞）

CHANGELOG_CODES = {"H-TICKET", "H-STATE", "H-DATE", "H-ATTRIB"}  # CHANGELOG 面**逐码**判这四支（①③④⑤）；
#   ②（H-PATH／H-POINTER）与 ③b（H-STALE）、⑥（H-GIFT-UNIT）不在此面判——**逐码不入门**是豁免的唯一形制，
#   没有「整面豁免」这种口子（M258 裁定，M289 沿用）。
WARN_CODES = {"H-GIFT-UNIT"}    # ⑥即便命中成品面也记 WARN：它判的是「等他票补齐」的过渡态，
#   用 ERROR 会把整仓门卡死在别人名下的在途字上；归零与否看 WARN 计数走向，不看门是否红。
GIFT_SCOPE_SKIP = ("assets", "examples")   # ⑥射程：README／SKILL 门面句＋包内 references；模板面与样例面不判
LEGEND = {c: spec for c, _, _, spec in RULES}
LEGEND["H-POINTER"] = "包内相对指路目标不存在——要么补文件，要么删指路；不许留断链"


def hit_of(m) -> str:
    """命中文字：尺子带命名组 `hit` 就报那一小段（⑥的行首否证要吃掉前缀，不能把整行当命中），
    其余码没有这组，逐字节照旧报整段匹配。"""
    g = m.groupdict().get("hit")
    return g if g else m.group(0)


def ban_label(code: str) -> str:
    """报文里的族名前缀：①〜⑤（含 ②b／③b 子项）是五禁本体；⑥是 §5-1 口径校验，不冒充「五禁⑥」。"""
    return "口径" if code == "H-GIFT-UNIT" else "五禁"


def severity(face: str | None, code: str) -> str:
    """面与码两头定级：成品面=ERROR、CHANGELOG=WARN；WARN_CODES 里的码不分面一律 WARN。
    一枚文件可以同时出两种级别，所以计数按**逐条**走，表头只显示该面最重的一档。"""
    if code in WARN_CODES:
        return "WARN"
    return "ERROR" if face == "product" else "WARN"

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


def gift_scope_ok(path: Path) -> bool:
    """⑥射程（M289 票面）：门面句 README／SKILL 与包内 references 判；assets／examples 不判。
    仓外路径按成品面从严判那条路照旧给判——射程收的是包内模板与样例面，不是「仓外免检」。"""
    try:
        parts = path.resolve().relative_to(ROOT).parts
    except ValueError:
        return True
    return not any(seg in GIFT_SCOPE_SKIP for seg in parts[1:-1])


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


TESTISH_SEGMENTS = {"fixtures", "tests", "samples", "examples"}   # M242：测试与样例面的同名件是**语料**，不给指路背书


def _basename_elsewhere(pkg: Path, rel: str, own: Path, text_path: Path):
    """同名件在包内**非测试面**别处存在 → 多半是运行时产出路径或范例副本，不当断链。
       M242 窄化：命中路径（相对包根）任一段属 fixtures／tests／samples／examples 时**不算豁免**——
       否则任何包把同名件丢进测试语料就能盖住真断链（dd 散件时代 29 枚 `coverage-map.md` 正是这形，
       当时把面上两枚真断链洗白成 0 条；lead 10-17 重测确认现值上这条已不再被求值，故窄化零代价）。
       返回 True／False，并把「因测试面而被弃用的命中数」记进 EXEMPT_DISCARDED（报账可查，不静默）。"""
    name = Path(rel).name
    if not name or name.count(".") < 1:
        return False
    for cand in pkg.rglob(name):
        if cand == text_path:
            continue
        try:
            parts = {x.lower() for x in cand.relative_to(pkg).parts[:-1]}
        except ValueError:
            parts = {x.lower() for x in cand.parts}
        if parts & TESTISH_SEGMENTS:
            EXEMPT_DISCARDED.append((rel, cand.relative_to(pkg).as_posix()))
            continue
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
            born = bool(OUTPUT_VERB.search(line))
            if born or _basename_elsewhere(pkg, t, own, as_file or own / t.name):
                SKIP_OUTPUT_POINTERS.append((lineno, t, "出生动词" if born else "非测试面同名件"))
                continue
            out.append((lineno, t, "本包根与本文件目录两侧都找不到目标"))
    return out


def check_pointers(path: Path, text: str) -> list[tuple[int, str, str]]:
    return _pointers(text, _pkg_root(path), path.parent, path)


# ---------------------------------------------------------------- 单文件检查
def check_file(path: Path) -> list[tuple[str, int, str]]:
    """返回 [(码, 行号, 详句)] 三元组——**severity 不在这里出**，由调用方按面与码定（`severity(face, code)`）。
    （M271：本函数标注曾写四元组、实返三元组，按标注解包必 `ValueError`——是标注骗人，不是接口少了一项。）"""
    face = classify(path)
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.split("\n")
    finds: list[tuple[str, int, str]] = []

    if face == "product":
        for lineno, ptr, why in check_pointers(path, text):
            finds.append(("H-POINTER", lineno, f"包内指路 `{ptr}` {why}（规格：{LEGEND['H-POINTER']}）"))

    for code, ban, pat, spec in RULES:
        if face == "changelog" and code not in CHANGELOG_CODES:
            continue
        if code == "H-GIFT-UNIT" and not gift_scope_ok(path):
            continue
        for lineno, line in enumerate(lines, 1):
            for m in pat.finditer(line):
                finds.append((code, lineno, f"{ban_label(code)}{ban}命中「{hit_of(m)}」（规格：{spec}）"))
                break  # 每行每码只报一次，报告不被同一行刷屏
    return sorted(finds, key=lambda x: (x[1], x[0]))


# ---------------------------------------------------------------- 全仓跑
def run_repo(strict: bool, quiet: bool) -> tuple[int, int, int]:
    SKIP_OUTPUT_POINTERS.clear()
    EXEMPT_DISCARDED.clear()
    faces = iter_faces()
    errors = warnings = 0
    used_codes: set[str] = set()
    per_file: list[tuple[Path, str, list]] = []

    for f in faces:
        face = classify(f)
        finds = check_file(f)
        if not finds:
            continue
        sevs = {severity(face, code) for code, _, _ in finds}
        sev = "ERROR" if "ERROR" in sevs else "WARN"   # 表头显最重一档；计数逐条走（一枚面可两档同出）
        per_file.append((f, sev, finds))
        for code, _, _ in finds:
            used_codes.add(code)
            if severity(face, code) == "ERROR":
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

    _born = sum(1 for x in SKIP_OUTPUT_POINTERS if x[2] == "出生动词")
    _twin = sum(1 for x in SKIP_OUTPUT_POINTERS if x[2] == "非测试面同名件")
    print(f"指路附账：判为运行时产出路径而跳过 {len(SKIP_OUTPUT_POINTERS)} 条（出生动词 {_born}／非测试面同名件 {_twin}）"
          f"；因窄化被弃用的测试面同名件命中 {len(EXEMPT_DISCARDED)} 次（这类不再算豁免）")
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
                    finds.append((code, lineno, f.name, f"{ban}命中「{hit_of(m)}」"))
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
    EXEMPT_DISCARDED.clear()
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

    # 档②′ M220⑦：正反样成对——YAML 键名行必须零发条，真悬空 dispatch/ 路径必须发红
    yk = good / "references" / "yaml-keys.md"
    dg = bad / "assets" / "dangling-dispatch.md"
    if not (yk.is_file() and dg.is_file()):
        print("   缺 M220⑦ 形态对样（yaml-keys.md / dangling-dispatch.md）→ 词面误拦无回归防线")
        ok = False
    else:
        d_hit = [x for x in bad_f if x[0] == "H-PATH" and "dispatch/" in x[3]]
        y_hit = [x for x in _fixture_findings(good) if x[2].endswith("yaml-keys.md")]
        print(f"档②′ 词面鉴别力：真悬空 dispatch/ 发红 {len(d_hit)} 条＝{'对' if d_hit else '错（被窄化放掉了）'}；"
              f"YAML 键名样发条 {len(y_hit)} 条＝{'对' if not y_hit else '错（workflow_dispatch 又被误拦）'}")
        if not d_hit or y_hit:
            ok = False

    # 档④／档⑤（M242：把「同名件在包内别处存在」这半条豁免窄化到不认测试与样例面）
    dt = bad / "assets" / "dangling-twin.md"
    dtf = [x for x in bad_f if x[2].endswith("dangling-twin.md") and x[0] == "H-POINTER"]
    old_would_exempt = any(c.name == "unit-twin.md" and c != dt for c in bad.rglob("unit-twin.md"))
    discarded = [d for d in EXEMPT_DISCARDED if d[1].startswith(("scripts/fixtures/", "fixtures/", "tests/", "samples/", "examples/"))]
    ok4 = len(dtf) == 1 and old_would_exempt and bool(discarded)
    print(f"档④ 反例必红（洗白路径已拆）：改前口径会豁免＝{'是' if old_would_exempt else '否'}"
          f"｜改后该面发红 {len(dtf)} 条（期望 1）｜被弃用的测试面命中 {len(discarded)} 次"
          f"＝{'对' if ok4 else '错（要么没拆死，要么拆过了头）'}")
    if not ok4:
        ok = False

    tw = good / "references" / "twin-exempt.md"
    twf = [x for x in _fixture_findings(good) if x[2].endswith("twin-exempt.md")]
    still_exempt = _basename_elsewhere(good, "references/台账甲.md", good / "references", tw)
    ok5 = not twf and still_exempt
    print(f"档⑤ 正例仍绿（不许过窄）：同名件在非测试面（assets/）时豁免＝{'仍成立' if still_exempt else '被误删'}"
          f"｜该面发条 {len(twf)} 条（期望 0）＝{'对' if ok5 else '错（正当豁免被动了，会造成假红）'}")
    if not ok5:
        ok = False

    # 档⑥（M258：③b 施工进度标签——成品面必红、CHANGELOG 面不判，两向同取自测夹具）
    # 点名用**内容锚**（夹具里带「P0 骨架」的那一行），不押「行号＝末行」：夹具日后加行就会假红/假绿。
    st_bad = [x for x in bad_f if x[0] == "H-STALE" and x[2].endswith("SKILL.md")]
    st_cl = [x for x in bad_f if x[0] == "H-STALE" and x[2].endswith("CHANGELOG.md")]
    st_lines = (bad / "SKILL.md").read_text(encoding="utf-8", errors="replace").splitlines()
    st_at = [i for i, ln in enumerate(st_lines, 1) if "P0 骨架" in ln]
    st_named = next((x for x in st_bad if x[1] in st_at), None)
    ok6 = bool(st_bad) and not st_cl and bool(st_at) and st_named is not None
    print(f"档⑥ ③b 施工进度标签：成品面发红 {len(st_bad)} 条（期望 ≥1）｜点名到带「P0 骨架」的行（第 {'/'.join(map(str, st_at)) or '—'} 行）＝{'是' if st_named else '否'}"
          f"｜CHANGELOG 面发条 {len(st_cl)} 条（期望 0，留痕原则）＝{'对' if ok6 else '错'}")
    if not ok6:
        ok = False

    # 档⑦（M289 立尺、M298 收 canon：⑥ 两个数字各自带单位——成品面必红、并列裸 10 也必红、
    #        CHANGELOG 面不判、正例只留「两数都带单位」那形、射程与逐码降级都验）
    gu_bad = [x for x in bad_f if x[0] == "H-GIFT-UNIT" and x[2].endswith("SKILL.md")]
    gu_cl = [x for x in bad_f if x[0] == "H-GIFT-UNIT" and x[2].endswith("CHANGELOG.md")]
    gu_good = [x for x in _fixture_findings(good) if x[0] == "H-GIFT-UNIT"]
    gu_lines = (bad / "SKILL.md").read_text(encoding="utf-8", errors="replace").splitlines()
    ln_both = [i for i, x in enumerate(gu_lines, 1) if "送 500、每日 10" in x]           # 两数全裸那行（内容锚）
    ln_par = [i for i, x in enumerate(gu_lines, 1) if "500 积分、每日再 +10" in x]         # 并列裸 10 那行（内容锚）
    gu_anchor = [x for x in gu_bad if x[1] in ln_both and "命中「500」" in x[3]]
    gu_parallel = [x for x in gu_bad if x[1] in ln_par and "命中「10」" in x[3]]
    scope_ok = (gift_scope_ok(ROOT / "demo" / "README.md") and gift_scope_ok(ROOT / "demo" / "references" / "r.md")
                and not gift_scope_ok(ROOT / "demo" / "assets" / "t.md")
                and not gift_scope_ok(ROOT / "demo" / "examples" / "e" / "SKILL.md"))
    sev_ok = (severity("product", "H-GIFT-UNIT") == "WARN" and severity("product", "H-STATE") == "ERROR"
              and severity("changelog", "H-STATE") == "WARN" and "H-GIFT-UNIT" not in CHANGELOG_CODES)
    ok7 = bool(gu_bad) and not gu_cl and not gu_good and bool(gu_anchor) and bool(gu_parallel) and scope_ok and sev_ok
    print(f"档⑦ ⑥ 额度句两数各自带单位：成品面发红 {len(gu_bad)} 条（期望 ≥2）"
          f"｜两数全裸那行（第 {'/'.join(map(str, ln_both)) or '—'} 行）点到「500」＝{'是' if gu_anchor else '否'}"
          f"｜并列裸 10 那行（第 {'/'.join(map(str, ln_par)) or '—'} 行）点到「10」＝{'是' if gu_parallel else '否（M298 的 canon 没落进尺里）'}"
          f"｜CHANGELOG 面 {len(gu_cl)} 条（期望 0，逐码不入门）｜合规样 {len(gu_good)} 条发条（期望 0：中文两数带单位／英文两数带 credits）"
          f"｜射程 assets·examples 不判＝{'对' if scope_ok else '错'}（**这两个面零命中不等于它们合规，别拿全仓零命中替它们签字**）"
          f"｜逐码分级 WARN 族＝{'对' if sev_ok else '错'}｜本档={'对' if ok7 else '错'}")
    if not ok7:
        ok = False

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
    text = path.read_text(encoding="utf-8", errors="replace")
    finds: list[tuple[str, int, str]] = []
    for code, ban, pat, spec in RULES:
        if face == "changelog" and code not in CHANGELOG_CODES:
            continue
        if code == "H-GIFT-UNIT" and not gift_scope_ok(path):
            continue
        for lineno, line in enumerate(text.split("\n"), 1):
            m = pat.search(line)
            if m:
                finds.append((code, lineno, f"{ban_label(code)}{ban}命中「{hit_of(m)}」（规格：{spec}）"))
    if face == "product":
        base = _pkg_root(path)
        for lineno, ptr, why in _pointers(text, base, path.parent, path):
            finds.append(("H-POINTER", lineno, f"包内指路 `{ptr}` {why}（规格：{LEGEND['H-POINTER']}）"))
    finds.sort(key=lambda x: (x[1], x[0]))
    codes = {c for c, _, _ in finds}
    sevs = {severity(face, c) for c, _, _ in finds}
    sev = "ERROR" if "ERROR" in sevs else "WARN"      # 逐码分级后，表头显最重一档
    n_warn_only = sum(1 for c, _, _ in finds if severity(face, c) == "WARN")
    if finds:
        print(f"{sev}: {path.name}（{len(finds)} 条）{note}")
        for code, lineno, detail in finds:
            own = severity(face, code)
            print(f"  - [{code}{'／' + own if own != sev else ''}] 第 {lineno} 行：{detail}")
        if n_warn_only:
            print(f"  其中按码记 WARN（`WARN_CODES`＝{sorted(WARN_CODES)}）：{n_warn_only} 条——不抬升成 ERROR，也不静默吞")
    else:
        print(f"PASS: {path.name} 五禁零命中、指路可跟随 {note}")
    print("  码表: " + "; ".join(f"{c}→{LEGEND[c]}" for c in sorted(codes)))
    if not finds:
        return 0
    return 1 if ("ERROR" in sevs or strict) else 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description="公开面卫生机检闸（五禁＋指路存在性，纯 stdlib 零网络）。",
        epilog="出口：ERROR=成品面违禁（发布打回，与红线同级）；WARN 有两条通路——①CHANGELOG 面命中（留痕原则，人裁）；"
               "②成品面命中、但该码在 WARN_CODES 里逐码降级（M289 起，如 ⑥ 额度句缺单位——过渡态不钉门）。"
               "判定与词表全集以本脚本现值为准（--help 看禁项全集，不止五禁）。")
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
