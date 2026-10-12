#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_shipment.py — 发布物自跑闸（K-17／CONTRIBUTING「发布物自跑」的可执行形）。

一句话：**仓内跑绿 ≠ 发布物跑绿**。公开面每写一句「自带守护样」「可跑 `--selftest`」「见 `fixtures/…`」，
都是在承诺用户手上的一次执行；打包排除面一旦剔掉样本目录，那句能力在用户侧就失效。
本闸的对象是**发布物**（zip 或已解包目录），不是仓内工作树。纯 stdlib、零网络。

用法：
    python3 scripts/check_shipment.py <发布物：zip 或已解包目录> [--pkg NAME] [--zip 渠道副本.zip]
    python3 scripts/check_shipment.py --selftest      跑 scripts/fixtures/shipment/ 四档守护样＋双跑确定性
    python3 scripts/check_shipment.py --list          列出判定码与本包会走哪几条
    python3 scripts/check_shipment.py <件> --quiet    只报汇总与码表

判定码（详行先打码，再打面／相对路径／规格；末行「码表:」只列本次真正用到的码）：
    S-MISSING   成品面的包内相对指路（fixtures/… scripts/fixtures/… tests/… assets/… references/…）
                在**发布物内**不存在；或成品面有「自带守护样／可跑 --selftest」这类能力句，
                而发布物内没有任何可跑载体。
    S-SELFTEST  发布物内含自测入口的，**在解包件里真跑一次**（subprocess，禁网），非 0 即发红；
                跑不起来（超时／不可解）同样发红并附出口原文首行。
                入口两形都认（缺一形就会把合规包判成假红）：
                  **selftest 形**＝包内 .py 自带 `--selftest`（含成品面写明的命令）→ `python3 X.py --selftest`；
                  **runner 形** ＝包内 `run_*.sh`／`run_*.py`（如 `scripts/fixtures/run_fixtures.sh`、
                                `tests/run_all.py`）→ `.sh` 用 bash 无参直跑、`.py` 用解释器无参直跑。
                详行与读数都注明「入口形=…」，报账面能一眼分诊是哪形没被认。
    S-SIZE      **体积闸量的是发布物 zip 字节**（实发资产形制，不是仓内 `du`，不是解包后目录和）。
                超过闸值（默认 1,048,576 B）即 ERROR 并附现值字节。
                输入是目录而无 zip 可对表时，本条**不判**，只出 WARN 说明对象不是那枚字节。
    S-PARITY    给了 `--zip 渠道副本` 时，对两份字节各跑全套判定；**两跑结论不一致**即 ERROR。
                字节 sha 不同只出 WARN（渠道可能确供另一版），不冒充失败。

出口语义（与同族卫生闸一致：自报错不自掩、退码即语义、双跑同值）：
    有 ERROR → 1；只有 WARN 或零条 → 0；`--selftest` 全绿 → 0，任一档不符 → 1。
    读不动输入件（不是 zip、目录不存在、成品面为空）→ 1 并打 `S-INPUT`（不静默返 0）。

岗单周检与新票探针接法（照抄即可，勿改路径）：
    cd <仓根> && python3 -B scripts/check_shipment.py --selftest                    # 闸本体非恒真
    cd <仓根> && python3 -B scripts/check_shipment.py --repo-scan . --quiet          # 周检第二行：全仓逐包（树构建代理态）
    cd <仓根> && python3 -B scripts/check_shipment.py /path/to/<slug>.zip            # 逐包出门判据（对真发布物字节）
    cd <仓根> && python3 -B scripts/check_shipment.py <本地.zip> --zip <渠道回下载.zip>  # 渠道字节也能跑
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

# K-12：渠道上传口拒收的形制。模拟打包**必须先按这些剔净**再判指路——
# 否则「文件在仓内、指路也在面」的件会判成假绿（M220 的模型错处：assets/*.png 线上必悬空）。
K12_PATTERNS = (".gitignore", "license", ".png", ".jpg", ".jpeg", ".gif")
MAX_BYTES_DEFAULT = 1_048_576          # 渠道 ≈1 MiB 闸；对象＝发布物 zip 字节
SELFTEST_TIMEOUT = 180

CODE_LEGEND = {
    "S-INPUT":    "输入件读不动（非 zip／目录不存在／成品面空）→ 先把发布物取对再谈结论",
    "S-MISSING":  "成品面指路或能力句在发布物内无对应物→补随包样本，或按「裁样本集不删能力句」改指路",
    "S-SELFTEST": "发布物内自测入口真跑非 0 或不可跑→按详行附的出口原文修，别只看仓内",
    "S-SIZE":     "发布物 zip 字节超闸→裁样本集（在包体上限内取舍），不删能力句",
    "S-PARITY":   "本地字节与渠道回下载字节两跑结论不一致→查供体与回包，不假设同源",
}

# 成品面：公开给用户读的那几面（与卫生闸同口径）
SURFACE = re.compile(r"^(SKILL[^/]*\.md|README[^/]*\.md|CONTRACT[^/]*\.md)$")
SURFACE_DIRS = ("assets", "references")   # 票面口径：SKILL*.md／README*.md／assets/**／references/**／CONTRACT.md
# 相对指路：包内目录打头、带扩展名或以 / 结尾的路径 token
# 包内相对指路（首段必须是这几个目录之一）
POINTER = re.compile(r"(?<![\w/.-])((?:scripts/)?(?:fixtures|tests|assets|references|examples|scripts)/"
                     r"[A-Za-z0-9_\-\u4e00-\u9fff./%\u3000-\u303f]*)")
# 带前导段的路径（cue-data-mcp/references/setup.md、~/.workbuddy/skills/<别包>/…）＝跨包或宿主安装位，分形不判
OUTER = re.compile(r"(?<![\w/.-])(?:~|\$HOME)?[A-Za-z0-9_.\-%\u4e00-\u9fff-]+/"
                   r"(?:scripts/)?(?:fixtures|tests|assets|references|examples)/"
                   r"[A-Za-z0-9_\-\u4e00-\u9fff./%\u3000-\u303f]*")
KOWN_FIRST = ("fixtures", "tests", "assets", "references", "examples", "scripts")
def looks_like_file(tok: str) -> bool:
    """末段含「.」即按文件判；否则按目录判（扩展名清单会漏 .sh/.png/.env 这类，不靠清单）。"""
    return "." in tok.rsplit("/", 1)[-1]
# 能力句：出现自测入口字样或「守护样」类承诺
CAPWORD = re.compile(r"--selftest|守护样|自带.{0,6}样本|self.?test", re.I)
# 成品面写下的可跑命令：python3 <路径>.py … --selftest
# 外链不进指针集（M220①：GitHub []() 链接里的 references/setup.md 曾被抽成本包指路）
URLISH = re.compile(r"\[[^\]]*\]\((?:https?|ftp)://[^)]*\)|\b(?:https?|ftp)://[^\s)）]+|\bwww\.[^\s)）]+", re.I)
# 跨技能/安装绝对路径属外调用面，不许截尾当包内指路（M220②）
INSTALLISH = re.compile(r"(?:~|\$HOME)/\S+|\S*/skills/\S+")   # 宿主安装位与别包路径（跨技能调用），不是包内相对指路
# 出生句（运行时产物）豁免：动词与产物位**同句齐备**才免，且同行不得是调用形（M220③⑤）
BIRTH_VERB = re.compile(r"写到|写成|输出到|生成到|落盘到|存到|产出到|落到")
BIRTH_HINT = re.compile(r"输出目录|产物|本次运行|每次运行|填好的|交付物|交付面|交付的四件")
OUTPUT_DECL = re.compile(r"\bOutputs?\s*[:：]|交付物|交付面|输出目录")
INVOKE = re.compile(r"python3?\s|bash\s|\s--|\b--\w")
# 裸脚本调用形（M220⑤假阴：`research_run.py --query …` 没有目录前缀，旧版根本不进指针集）
BARE_INV = re.compile(r"(?:^|[\s`|])([A-Za-z0-9_\-]+\.(?:py|sh))(?=\s+--|\s+-\w)")
RUNNER = re.compile(r"(^|/)run_[a-z0-9_]*\.(sh|py)$", re.I)   # runner 形：run_fixtures.sh／run_all.py／run_tests.sh 一类，无参直跑
CMD = re.compile(r"python3?\s+([^\s`|;]+\.py)([^\n`|;]{0,120}?--selftest[^\n`|;]{0,40})")


class Hit:
    def __init__(self, code, face, ref, detail, sev="ERROR"):
        self.code, self.face, self.ref, self.detail, self.sev = code, face, ref, detail, sev

    def line(self):
        return f"{self.code}｜{self.sev}｜{self.face}｜{self.ref}｜{self.detail}"


def norm_rel(p: str) -> str:
    p = p.strip().strip(".,:;、。（）").lstrip("./")
    p = re.sub(r"/{2,}", "/", p)
    return p.rstrip("/") or p


def surface_files(files):
    out = []
    for rel in files:
        base = rel.rsplit("/", 1)[-1]
        if SURFACE.match(base):
            out.append(rel)
            continue
        parts = rel.split("/")
        if parts[0] in SURFACE_DIRS and base.endswith(".md"):
            out.append(rel)
    return sorted(out)


def read_text(root: Path, rel: str):
    try:
        return (root / rel).read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def extract_pointers(text):
    """→ ([(token, 是否按文件判)], 跨包/宿主路径枚数)。外链、安装位与带前导段的跨包引用都不进包内指针集。"""
    seen = {}
    n_outer = 0
    text = URLISH.sub(" ", text)
    n_outer += len(INSTALLISH.findall(text))
    text = INSTALLISH.sub(" ", text)
    for m in OUTER.finditer(text):        # 形如 cue-data-mcp/references/setup.md：别包路径，不判本包缺失
        tok = m.group(0)
        first = tok.split("/")[0]
        if first in KOWN_FIRST or tok.startswith(("~", "$HOME")):
            continue
        n_outer += 1
        text = text.replace(tok, " ", 1)
    for m in POINTER.finditer(text):
        tok = norm_rel(m.group(0))
        if not tok or tok.startswith("http"):
            continue
        # 只认「看起来是路径」的：末段带点＝文件，或原文以 / 结尾＝目录，或已知目录打头
        raw = m.group(0)
        if looks_like_file(tok) or raw.endswith("/") or tok.split("/")[0] in (
                "fixtures", "tests", "scripts", "assets", "references", "examples"):
            seen[tok] = looks_like_file(tok)
    for m in BARE_INV.finditer(text):        # 裸脚本调用形（无目录前缀）也进指针集
        tok = norm_rel(m.group(1))
        if tok and not tok.startswith(KOWN_FIRST):
            seen[tok] = True
    return sorted(seen.items()), n_outer


def dir_pointers(text):
    """目录级承诺（`fixtures/` 这种以 / 结尾、或「fixtures 目录」字样）→ 至少要有一枚文件在里面。"""
    out = set()
    for m in POINTER.finditer(text):
        raw = m.group(0)
        if raw.endswith("/"):
            out.add(norm_rel(raw))
    return sorted(out)


def load_shipment(target: Path):
    """→ (解包根目录, zip 字节数或 None, zip sha 或 None, 是否临时目录)"""
    if target.is_dir():
        return target, None, None, False
    if target.is_file() and zipfile.is_zipfile(target):
        data = target.read_bytes()
        tmp = Path(tempfile.mkdtemp(prefix="check-shipment-"))
        with zipfile.ZipFile(target) as zf:
            names = [n for n in zf.namelist() if not n.endswith("/")]
            for n in names:
                dest = (tmp / n).resolve()
                if not str(dest).startswith(str(tmp.resolve())):   # zip-slip 防呆
                    raise ValueError(f"越界条目：{n}")
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(zf.read(n))
        return tmp, len(data), hashlib.sha256(data).hexdigest(), True
    raise ValueError("输入既不是目录也不是可读 zip")


def strip_common_root(root: Path):
    """支持两种实发形制：条目在包根（渠道构建）与条目在单一顶层目录下（git archive）。"""
    entries = [p for p in root.iterdir()]
    dirs = [p for p in entries if p.is_dir()]
    files = [p for p in entries if p.is_file()]
    if dirs and not files:
        return dirs[0]
    return root


def rel_files(root: Path):
    out = set()
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != "__pycache__"]
        for fn in filenames:
            out.add(os.path.relpath(os.path.join(dirpath, fn), root).replace(os.sep, "/"))
    return sorted(out)


def run_selftest(root: Path, script_rel: str, extra_args, exe=None):
    """在**解包件里**真跑一次；返回 (退码或 None, 出口首行)。禁网：不给代理，cwd 锁在件内。"""
    env = dict(os.environ)
    for k in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy", "ALL_PROXY", "all_proxy"):
        env.pop(k, None)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    cmd = [exe or sys.executable, script_rel] + list(extra_args)
    try:
        p = subprocess.run(cmd, cwd=str(root), capture_output=True, text=True, timeout=SELFTEST_TIMEOUT, env=env)
    except subprocess.TimeoutExpired:
        return None, f"CLIENT_TIMEOUT_AFTER_{SELFTEST_TIMEOUT}s"
    except Exception as e:
        return None, f"{type(e).__name__}: {str(e)[:120]}"
    out = (p.stdout or "") + "\n" + (p.stderr or "")
    lines = [l.strip() for l in out.splitlines() if l.strip()]
    # runner 的结论行在末尾（ALL GREEN／NOT GREEN／ok …），selftest 亦然：取末行更承重，附首行防上下文丢失
    last = lines[-1] if lines else "(无输出)"
    first = lines[0] if lines else "(无输出)"
    return p.returncode, (last if last != first else first)[:200]


def check(target: Path, pkg: str, channel_zip: Path | None, max_bytes: int, quiet: bool, repo_dir: Path | None = None):
    hits = []
    notes = []
    try:
        root_raw, nbytes, ndigest, is_tmp = load_shipment(target)
    except Exception as e:
        early = [(str(target.resolve()), "<发布物>"), (str(Path(tempfile.gettempdir()).resolve()), "<临时根>")]
        return [Hit("S-INPUT", "-", mask_paths(str(target), early),
                    f"读不动发布物：{type(e).__name__}: {mask_paths(str(e)[:120], early)}")], notes, {}

    root = strip_common_root(root_raw)
    tmp_root = str(Path(tempfile.gettempdir()).resolve())
    leaks = [(str(root_raw), "<解包根>"), (str(root), "<解包根>"),
             (str(target.resolve()), "<发布物>"), (tmp_root, "<临时根>")]
    files = rel_files(root)
    faces = surface_files(files)
    if not faces:
        hits.append(Hit("S-INPUT", "-", pkg, "发布物内没有可判的成品面（SKILL*.md／README*.md／CONTRACT*.md／assets｜references 下的 .md）"))
    fileset = set(files)

    # ①② 相对指路存在性 ＋ 能力句载体（外调面与出生句单列，供报账分诊）
    cap_lines = []
    births = []
    outer_total = []
    cmds = []
    for rel in faces:
        text = read_text(root, rel)
        birth_lines = [ln for ln in text.splitlines()
                       if not INVOKE.search(ln)
                       and ((BIRTH_VERB.search(ln) and BIRTH_HINT.search(ln)) or OUTPUT_DECL.search(ln))]
        pts, n_outer = extract_pointers(text)
        outer_total.append((rel, n_outer))
        for tok, has_ext in pts:
            if any(tok in ln for ln in birth_lines):
                births.append((rel, tok))
                continue
            if "/" in tok and tok.split("/")[0] not in ("fixtures", "tests", "assets", "references", "examples", "scripts"):
                continue          # 带目录段的只认自家六个目录；裸文件名（调用形）在包内任意路径里找
            base = rel.rsplit("/", 1)[0] if "/" in rel else ""
            cands = ([f"{base}/{tok}"] if base else []) + [tok]
            if has_ext:
                if "/" not in tok:      # 裸调用形：包内**任意路径**下同名件都算跟随
                    found = any(f.rsplit("/", 1)[-1] == tok for f in files)
                else:
                    found = any(c in fileset for c in cands)
                if not found:
                    why = ("成品面以调用形写了这枚脚本（带参数），发布物内没有该件——"
                           "**跨技能调用要在面上写明属别包**，不得让读者以为本件自带"
                           if "/" not in tok else "成品面写了这枚相对路径，发布物内没有该文件")
                    hits.append(Hit("S-MISSING", rel, tok, why))
            else:
                hit = any(f.startswith(c + "/") for f in files for c in cands)   # 判据＝该前缀**目录下**至少一枚真件
                if not hit:
                    hits.append(Hit("S-MISSING", rel, tok,
                                    "成品面写了这枚前缀指路，发布物内**该前缀目录下无一件真件**"
                                    "（判据＝前缀目录下至少一枚真件；不是「存不存在同名目录」那种撞运气形制）"))
        # 目录级承诺（原文以 / 收尾）已由上一条按目录判，这里不重复发红
        for lineno, line in enumerate(text.splitlines(), 1):
            if CAPWORD.search(line):
                cap_lines.append((rel, lineno, line.strip()[:160]))
            for m in CMD.finditer(line):
                cmds.append((rel, lineno, norm_rel(m.group(1))))

    # ③ 自测入口真跑：成品面写明的命令 ∪ 发布物内 .py 自带 --selftest 的脚本
    form = {}
    for _, _, scr in cmds:
        form[norm_rel(scr)] = "selftest（成品面写明）"
    for rel in files:
        base = rel.rsplit("/", 1)[-1]
        if rel.endswith(".py"):
            src = read_text(root, rel)
            if '"--selftest"' in src or "'--selftest'" in src or ("--selftest" in src and "add_argument" in src):
                form.setdefault(rel, "selftest（脚本自带）")
        if RUNNER.search(rel):
            form.setdefault(rel, "runner")
    entries = sorted(form)
    ran = []
    uniq_cmds = entries[:12]
    for scr in uniq_cmds:
        face = next((f for f, _, s in cmds if norm_rel(s) == scr), "（发布物内脚本自报）")
        if scr not in fileset:
            continue  # 缺件已在上面发过 S-MISSING，不在这里重复发红
        kind = form.get(scr, "selftest")
        args = ["--selftest"] if kind.startswith("selftest") else []
        runner = "bash" if scr.endswith(".sh") else sys.executable
        rc, first = run_selftest(root, scr, args, runner)
        ran.append((scr, kind, rc, first))
        if rc is None:
            hits.append(Hit("S-SELFTEST", face, scr, f"入口形={kind}｜解包件内真跑不可完成：{first}"))
        elif rc != 0:
            hits.append(Hit("S-SELFTEST", face, scr, f"入口形={kind}｜解包件内真跑退码 {rc}；出口末读「{first}」"))
    if cap_lines and not ran:
        face, lineno, snippet = cap_lines[0]
        hits.append(Hit("S-MISSING", face, f"{face}:{lineno}",
                        f"成品面有能力句（{snippet}），发布物内没有任何可跑的自测入口"))

    # ④ 体积闸：对象必须是 zip 字节
    if nbytes is None:
        hits.append(Hit("S-SIZE", "-", pkg,
                        "输入是目录：体积闸不判（它量的是发布物 zip 字节，不是仓内 du，也不是解包后目录和）",
                        sev="WARN"))
    elif nbytes > max_bytes:
        hits.append(Hit("S-SIZE", "-", pkg, f"发布物 zip 现值 {nbytes:,} B ＞ 闸 {max_bytes:,} B；sha256 {ndigest[:16]}…"))

    # ⑤ 渠道回下载那份字节也要能跑
    if channel_zip is not None:
        try:
            cdata = channel_zip.read_bytes()
        except Exception as e:
            hits.append(Hit("S-PARITY", "-", str(channel_zip), f"渠道副本读不动：{type(e).__name__}: {str(e)[:100]}"))
            cdata = None
        if cdata is not None:
            cdigest = hashlib.sha256(cdata).hexdigest()
            if nbytes is not None and cdigest != ndigest:
                hits.append(Hit("S-PARITY", "-", pkg,
                                f"两份字节 sha256 不同（本地 {ndigest[:16]}… vs 渠道 {cdigest[:16]}…，"
                                f"{nbytes:,} B vs {len(cdata):,} B）——只报事实不判失败",
                                sev="WARN"))
            sub_hits, _, _ = check(channel_zip, pkg + "（渠道副本）", None, max_bytes, True, repo_dir)
            for h in sub_hits:      # 副本那层的临时根与本层不同，先换成同一占位再比结论
                h.detail = mask_paths(h.detail, leaks)
                h.ref = mask_paths(h.ref, leaks)
            mine = {h.code for h in hits if h.sev == "ERROR"}
            theirs = {h.code for h in sub_hits if h.sev == "ERROR" and h.code != "S-PARITY"}
            if mine != theirs:
                hits.append(Hit("S-PARITY", "-", pkg,
                                f"同一套判定在两枚字节上结论不同：本地 {sorted(mine) or '全绿'} vs 渠道 {sorted(theirs) or '全绿'}"))

    if repo_dir is not None and repo_dir.is_dir():
        repo_files = {os.path.relpath(os.path.join(dp, fn), repo_dir).replace(os.sep, "/")
                      for dp, dn, fns in os.walk(repo_dir) if "__pycache__" not in dp for fn in fns}
        for h in hits:
            if h.code != "S-MISSING" or ":" in h.ref:       # 能力句那条 ref 是「面:行号」，不带路径，不分诊
                continue
            tok = h.ref.rstrip("/")
            inrepo = tok in repo_files or any(f == tok or f.startswith(tok + "/") for f in repo_files)
            h.detail += "（仓内有→属打包排除面，补发随包即可）" if inrepo else "（仓内也无→属指路本身写错）"
    stats = {"faces": len(faces), "cap": len(cap_lines), "ran": ran, "bytes": nbytes, "digest": ndigest, "entries": []}
    n_st = sum(1 for r in ran if r[1].startswith("selftest"))
    n_ru = sum(1 for r in ran if r[1] == "runner")
    for h in hits:                  # 报账面一律去绝对路径：随机临时名进报账＝双跑不可 diff
        h.detail = mask_paths(h.detail, leaks)
        h.ref = mask_paths(h.ref, leaks)
    notes.append(f"豁免分诊：出生句／输出声明行免判 {len(births)} 条；跨包与安装位指路不计本包缺失 "
                 f"{sum(n for _, n in outer_total)} 处（逐面清单在详行区外，不静默放过）")
    notes.append(f"成品面 {len(faces)} 面／能力句 {len(cap_lines)} 行／自测入口 {len(ran)} 枚真跑"
                 f"（入口形：selftest {n_st}｜runner {n_ru}）")
    if ran:
        stats["entries"] = [(r[0], r[1], r[2], r[3]) for r in ran]
    return hits, notes, stats


def mask_paths(text: str, leaks) -> str:
    """把报账文本里的绝对路径换成稳定占位符。
       随机临时目录名一旦进报账，双跑就不可 diff（S-SELFTEST 的出口原文会带 $PWD）——
       这里只改可复现性，不改判据：路径照原样保留尾部，根位换成 <解包根>／<发布物>。"""
    out = text or ""
    for real, alias in sorted(leaks, key=lambda x: -len(x[0])):
        if real:
            out = out.replace(real, alias)
    return out


def dedupe(hits):
    seen, out = set(), []
    for h in hits:
        k = (h.code, h.sev, h.face, h.ref)   # 同面同指路只发一条，详因取首条
        if k in seen:
            continue
        seen.add(k)
        out.append(h)
    return sorted(out, key=lambda h: (h.sev != "ERROR", h.code, h.face, h.ref))


SILENT = []          # selftest 期间吞掉汇总行，只留逐档读数


def emit(target, pkg, hits, notes, quiet):
    hits = dedupe(hits)
    errs = [h for h in hits if h.sev == "ERROR"]
    warns = [h for h in hits if h.sev != "ERROR"]
    if not SILENT:
        if errs:
            print(f"FAIL: {pkg}（{len(errs)} 条 ERROR／{len(warns)} 条 WARN）")
        else:
            print(f"PASS: {pkg}（发布物内成品面指路齐、自测入口真跑退码 0、体积在闸内）"
                  + (f"；WARN {len(warns)} 条" if warns else ""))
    if not quiet:
        for h in hits:
            print(f"    {h.line()}")
    for n in notes:
        if not quiet:
            print(f"    读数：{n}")
    used = sorted({h.code for h in hits})
    if used and not SILENT:
        print("    码表: " + "　".join(f"{c}={CODE_LEGEND[c]}" for c in used))
    return 1 if errs else 0


# ---------------- 守护样与 --selftest（四档＋双跑确定性） ----------------

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "shipment"


def k12_dropped(rel: str) -> bool:
    """K-12 渠道上传口拒收的形制，**含嵌套目录**（basename 命中即剔）。
       模拟打包必须先按它剔净再判指路——否则「文件在仓内、指路也在面」的件会判成假绿。"""
    low = rel.lower()
    base = low.rsplit("/", 1)[-1]
    return (".gitignore" in low or base.startswith("license")
            or any(base.endswith(e) for e in (".png", ".jpg", ".jpeg", ".gif")))


def build_zip(dst: Path, root: Path, drop=(), include_fixtures=True, apply_k12=True, sink=None):
    """返回 dst（调用点形制不变）；剔件清单写进 sink（list），供报账写明「本次模拟剔了哪些形制」。"""
    import shutil
    staging = Path(tempfile.mkdtemp(prefix="cs-build-"))
    dropped = []
    for rel in sorted(p for p in root.rglob("*") if p.is_file() and "__pycache__" not in p.parts):
        r = rel.relative_to(root).as_posix()
        if not include_fixtures and ("fixtures/" in r or r.startswith("tests/")):
            dropped.append(f"样本面:{r}")
            continue
        if apply_k12 and k12_dropped(r):
            dropped.append(f"K-12:{r}")
            continue
        if any(r.endswith(d) or d in r for d in drop):
            dropped.append(f"自选:{r}")
            continue
        out = staging / r
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(rel, out)
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(staging.rglob("*")):
            if p.is_file():
                zf.write(p, p.relative_to(staging).as_posix())
    shutil.rmtree(staging, ignore_errors=True)
    if sink is not None:
        sink.extend(dropped)
    return dst


def fixture_root(kind: str) -> Path:
    """守护样落盘在 scripts/fixtures/shipment/<kind>/demopkg，可手工复跑：
       good＝指路齐＋自测入口退 0；missing＝SKILL 仍指 scripts/fixtures/ 但该目录不在；red＝入口真跑退 1。"""
    root = FIXTURES / kind / "demopkg"
    if not root.is_dir():
        raise SystemExit(f"守护样缺失：{root}（闸本体的自证凭据不在盘上，不发结论）")
    return root


def selftest(quiet=False) -> int:
    import shutil
    ok = True
    res = []
    SILENT.append(1)

    def one(name, want, got, detail=""):
        nonlocal ok
        good = (want == got)
        ok = ok and good
        res.append(f"   {name:26} 期望 {str(want):>10} 实得 {str(got):>10} {detail}")

    # 一档：合规样必绿
    z = build_zip(Path(tempfile.mkdtemp(prefix="cs-z-")) / "demopkg.zip", fixture_root("good"))
    r = check(z, "demopkg", None, MAX_BYTES_DEFAULT, True)
    one("一档-合规样必绿", 0, emit(z, "demopkg", r[0], r[1], quiet=True))
    # 一档b：渠道同一枚字节也要能跑（S-PARITY 不误拦）
    z2 = Path(str(z) + ".copy")
    z2.write_bytes(z.read_bytes())
    r = check(z, "demopkg", z2, MAX_BYTES_DEFAULT, True)
    one("一档b-渠道同字节不误拦", 0, emit(z, "demopkg", r[0], r[1], quiet=True))

    # 二档：缺件样必红（把 fixtures 从包里剔掉，能力句与指路都还在）
    zm = build_zip(Path(tempfile.mkdtemp(prefix="cs-z-")) / "demopkg.zip", fixture_root("missing"),
                   include_fixtures=False)
    rm = check(zm, "demopkg", None, MAX_BYTES_DEFAULT, True)
    codes = {h.code for h in rm[0] if h.sev == "ERROR"}
    one("二档-缺件样必红", 1, emit(zm, "demopkg", rm[0], rm[1], quiet=True))
    one("二档b-发红码含 S-MISSING", True, "S-MISSING" in codes, f"实得 {sorted(codes)}")

    # 二档c（反向自证，防恒真）：把同一枚缺件样 SKILL 里那两句指路／能力句删掉，必须转绿——
    #         证明二档的红来自那两行判据，而不是「逢这份样必红」。
    inv = Path(tempfile.mkdtemp(prefix="cs-inv-")) / "demopkg"
    shutil.copytree(fixture_root("missing"), inv)
    sk = inv / "SKILL.md"
    sk.write_text("# 示例包 SKILL\n\n只讲能力，不指样本、不承诺自测。\n", encoding="utf-8")
    zi = build_zip(Path(tempfile.mkdtemp(prefix="cs-z-")) / "demopkg.zip", inv)
    one("二档c-删掉承诺即转绿（防恒真）", 0, emit(zi, "demopkg", *check(zi, "demopkg", None, MAX_BYTES_DEFAULT, True)[0:2], quiet=True))

    # 三档：自测真跑必红（包里带着会退 1 的入口）
    zr = build_zip(Path(tempfile.mkdtemp(prefix="cs-z-")) / "demopkg.zip", fixture_root("red"))
    rr = check(zr, "demopkg", None, MAX_BYTES_DEFAULT, True)
    rcodes = {h.code for h in rr[0] if h.sev == "ERROR"}
    one("三档-真跑非零必红", 1, emit(zr, "demopkg", rr[0], rr[1], quiet=True))
    one("三档b-发红码含 S-SELFTEST", True, "S-SELFTEST" in rcodes, f"实得 {sorted(rcodes)}")

    # 四档：体积闸按 zip 字节判（闸值压到 10 B 必红；换成目录则不判）
    one("四档-超字节必红", 1, emit(z, "demopkg", *check(z, "demopkg", None, 10, True)[0:2], quiet=True))
    droot = fixture_root("good")
    rd = check(droot, "demopkg", None, MAX_BYTES_DEFAULT, True)
    one("四档b-目录输入只 WARN 不判体积", 0, emit(droot, "demopkg", rd[0], rd[1], quiet=True))

    # 五档（双跑确定性）：**两形各一枚**字节两跑报告逐字节同
    zr_ok = build_zip(Path(tempfile.mkdtemp(prefix="cs-z-")) / "demopkg.zip", fixture_root("runner-good"))
    for tag, zz in (("selftest 形", z), ("runner 形", zr_ok)):
        a = subprocess.run([sys.executable, "-B", __file__, str(zz)], capture_output=True, text=True)
        b = subprocess.run([sys.executable, "-B", __file__, str(zz)], capture_output=True, text=True)
        one(f"五档-双跑同值（{tag}）", True, (a.stdout == b.stdout and a.returncode == b.returncode),
            f"退码 {a.returncode}/{b.returncode}")

    # 八档：runner 形三枚（合规必绿／缺件必红／真跑非零必红），加一条「入口形」报账
    rh = check(zr_ok, "demopkg", None, MAX_BYTES_DEFAULT, True)
    one("八档-合规 runner 样必绿", 0, emit(zr_ok, "demopkg", rh[0], rh[1], quiet=True))
    one("八档b-入口形标注为 runner", True, any("runner" in n for n in rh[1]), f"读数={rh[1][-1][:56]}")
    zrm = build_zip(Path(tempfile.mkdtemp(prefix="cs-z-")) / "demopkg.zip", fixture_root("runner-missing"))
    rrm = check(zrm, "demopkg", None, MAX_BYTES_DEFAULT, True)
    one("八档c-缺件 runner 样必红", 1, emit(zrm, "demopkg", rrm[0], rrm[1], quiet=True))
    one("八档d-发红码含 S-MISSING", True, "S-MISSING" in {h.code for h in rrm[0] if h.sev == "ERROR"})
    zrr = build_zip(Path(tempfile.mkdtemp(prefix="cs-z-")) / "demopkg.zip", fixture_root("runner-red"))
    rrr = check(zrr, "demopkg", None, MAX_BYTES_DEFAULT, True)
    one("八档e-runner 真跑非零必红", 1, emit(zrr, "demopkg", rrr[0], rrr[1], quiet=True))
    one("八档f-发红码含 S-SELFTEST", True, "S-SELFTEST" in {h.code for h in rrr[0] if h.sev == "ERROR"},
        f"详行={next((h.line() for h in rrr[0] if h.code=='S-SELFTEST'), '无')[:64]}")

    # 九档（lead 新逮的形制缺陷：随机临时目录名进报账＝双跑不可 diff）：
    zpl = build_zip(Path(tempfile.mkdtemp(prefix="cs-z-")) / "demopkg.zip", fixture_root("runner-pathleak"))
    rpl = check(zpl, "demopkg", None, MAX_BYTES_DEFAULT, True)
    one("九档-路径泄漏样真跑必红", 1, emit(zpl, "demopkg", rpl[0], rpl[1], quiet=True))
    one("九档b-发红码含 S-SELFTEST", True, "S-SELFTEST" in {h.code for h in rpl[0] if h.sev == "ERROR"})
    dl = " ".join(h.detail for h in rpl[0] if h.code == "S-SELFTEST")
    one("九档c-详行去绝对路径", True, ("<解包根>" in dl) and (str(Path(tempfile.gettempdir()).resolve()) not in dl),
        f"详行={dl[:70]}")
    pa = subprocess.run([sys.executable, "-B", __file__, str(zpl)], capture_output=True, text=True)
    pb = subprocess.run([sys.executable, "-B", __file__, str(zpl)], capture_output=True, text=True)
    one("九档d-非报账态双跑同值", True, (pa.stdout == pb.stdout and pa.returncode == pb.returncode),
        f"退码 {pa.returncode}/{pb.returncode}")

    # 十档（M220：四类假红必绿、两类必红、K-12 剔形制必写进报账）
    def tier(kind):
        zz = build_zip(Path(tempfile.mkdtemp(prefix="cs-z-")) / "demopkg.zip", fixture_root(kind))
        return zz, check(zz, "demopkg", None, MAX_BYTES_DEFAULT, True)

    for kind, label in (("url-green", "外链不进指针集"), ("crosspkg-green", "跨包与安装位不判本包缺件"),
                        ("birth-green", "出生句与输出声明行豁免"), ("prefix-green", "前缀下有真件即算跟随")):
        _, rr = tier(kind)
        errs = [h for h in rr[0] if h.sev == "ERROR"]
        one(f"十档-{label}必绿", 0, 1 if errs else 0, (errs[0].line()[:60] if errs else "零发条"))
    _, rp2 = tier("prefix-red")
    msgs = [h.detail for h in rp2[0] if h.code == "S-MISSING"]
    one("十档h-前缀下无真件必红", 1, 1 if any("前缀目录下无一件真件" in m for m in msgs) else 0, f"条数={len(msgs)}")

    zr1, rr1 = tier("bareinv-red")
    one("十档e-裸调用缺件必红", 1, 1 if any(h.sev == "ERROR" and h.code == "S-MISSING" for h in rr1[0]) else 0)
    zr2, rr2 = tier("png-red")
    one("十档f-png 被 K-12 剔后指路必红", 1,
        1 if any(h.sev == "ERROR" and h.code == "S-MISSING" and "demo-verifiable.png" in h.ref for h in rr2[0]) else 0)
    sink_probe = []
    zp = build_zip(Path(tempfile.mkdtemp(prefix="cs-z-")) / "demopkg.zip", fixture_root("png-red"), sink=sink_probe)
    one("十档g-报账写出剔了哪些形制", True, any(d.startswith("K-12") for d in sink_probe), f"剔={sink_probe[:2]}")

    # 六档b（lead 的两枚实测事实钉成机器判据）：
    #   ①体积闸只认 zip 字节——目录哪怕塞满 2 MiB 也不得发 ERROR（防「拿仓内 du 对渠道闸」那类假前提）
    big = Path(tempfile.mkdtemp(prefix="cs-big-")) / "demopkg"
    shutil.copytree(fixture_root("good"), big)
    (big / "assets" / "big.bin").write_bytes(b"\0" * 2_000_000)
    rbig = check(big, "demopkg", None, MAX_BYTES_DEFAULT, True)
    one("六档b-目录2MiB不判体积", 0, emit(big, "demopkg", rbig[0], rbig[1], quiet=True))
    #   ②渠道回下载那份也要能跑，两跑结论不一致必红
    zb = build_zip(Path(tempfile.mkdtemp(prefix="cs-z-")) / "demopkg.zip", fixture_root("missing"), include_fixtures=False)
    rp = check(z, "demopkg", zb, MAX_BYTES_DEFAULT, True)
    one("六档c-两枚字节结论不一必红", 1, emit(z, "demopkg", rp[0], rp[1], quiet=True))
    one("六档d-发红码含 S-PARITY", True, "S-PARITY" in {h.code for h in rp[0] if h.sev == "ERROR"})

    # 七档：输入读不动必发 S-INPUT（不自掩）
    bogus = Path(tempfile.mkdtemp(prefix="cs-z-")) / "not-a-zip.zip"
    bogus.write_text("这不是 zip", encoding="utf-8")
    rb = check(bogus, "demopkg", None, MAX_BYTES_DEFAULT, True)
    one("七档-读不动不自掩", True, {h.code for h in rb[0]} == {"S-INPUT"}, f"实得 {sorted({h.code for h in rb[0]})}")

    SILENT.clear()
    for line in res:
        print(line)
    print(f"selftest: {'ALL GREEN（能红、能绿、可复现、对象口径写明）' if ok else 'FAIL'}")
    return 0 if ok else 1


def repo_scan(repo: Path, max_bytes: int, quiet: bool) -> int:
    """CI 用：仓内没有现成 zip，就按**渠道老配方**（剔 fixtures/｜tests/）从工作树各建一枚再判。
    对象是「树构建出的 A 态字节」，不是渠道供体——渠道真字节仍须用 `check_shipment.py <zip> --repo <包>` 现验。"""
    bad, good = [], 0
    for pkg in sorted(d for d in repo.iterdir() if (d / "SKILL.md").is_file()):
        z = Path(tempfile.mkdtemp(prefix="cs-scan-")) / f"{pkg.name}.zip"
        dropped = []
        build_zip(z, pkg, include_fixtures=False, sink=dropped)
        hits, notes, _ = check(z, pkg.name, None, max_bytes, True, pkg)
        errs = [h for h in dedupe(hits) if h.sev == "ERROR"]
        rc = emit(z, pkg.name, hits, notes, quiet)
        n_size = sum(1 for h in errs if h.code == "S-SIZE")
        n_ptr = sum(1 for h in errs if h.code == "S-MISSING")
        n_run = sum(1 for h in errs if h.code == "S-SELFTEST")
        k12 = sorted({d.split(":")[0] for d in dropped})
        if not quiet:
            print(f"    剔形制：{('、'.join(k12) or '无')}（本包剔 {len(dropped)} 件）"
                  f"｜分列：指路 {n_ptr}／真跑 {n_run}／体积 {n_size}")
        if rc:
            bad.append((pkg.name, len(errs), f"指路{n_ptr}·真跑{n_run}·体积{n_size}"))
        else:
            good += 1
        z.unlink(missing_ok=True)
    print(f"repo-scan：{good} 枚已过，{len(bad)} 枚发红（体积闸与指路红分列，见各包「分列」行）"
          + ("".join(f"（{n}:{c} 条｜{br}）" for n, c, br in bad) if bad else ""))
    return 1 if bad else 0


def main() -> int:
    ap = argparse.ArgumentParser(description="发布物自跑闸（K-17）：指路存在性／自测真跑／体积按 zip 字节")
    ap.add_argument("target", nargs="?", help="发布物：zip 或已解包目录")
    ap.add_argument("--pkg", help="包名（缺省取目标名）")
    ap.add_argument("--zip", dest="channel", help="渠道回下载的那份 zip，对同一套判定再跑一遍")
    ap.add_argument("--max-bytes", type=int, default=MAX_BYTES_DEFAULT, help="体积闸（默认 1,048,576 B）")
    ap.add_argument("--quiet", action="store_true", help="只报汇总与码表")
    ap.add_argument("--selftest", action="store_true", help="跑四档守护样＋双跑确定性")
    ap.add_argument("--repo-scan", metavar="仓根", nargs="?", const=".", help="CI 用：按渠道老配方从工作树逐包建 zip 再判（报账态起步）")
    ap.add_argument("--repo", help="仓内该包目录（可选）：给每条 S-MISSING 补一句分诊——属打包排除还是指路写错")
    ap.add_argument("--list", action="store_true", help="列判定码")
    args = ap.parse_args()

    if args.list:
        for c, spec in CODE_LEGEND.items():
            print(f"{c:11} {spec}")
        print(f"\n体积闸现值：{MAX_BYTES_DEFAULT:,} B（对象＝发布物 zip 字节）；自测真跑超时 {SELFTEST_TIMEOUT} s")
        print(f"守护样目录：{FIXTURES}")
        return 0
    if args.selftest:
        return selftest(args.quiet)
    if args.repo_scan:
        return repo_scan(Path(args.repo_scan).resolve(), args.max_bytes, args.quiet)
    if not args.target:
        print("check_shipment: 要给发布物路径（zip 或已解包目录），或用 --selftest / --list / --help", file=sys.stderr)
        return 1
    t = Path(args.target)
    pkg = args.pkg or t.name
    hits, notes, _ = check(t, pkg, Path(args.channel) if args.channel else None, args.max_bytes, args.quiet,
                           Path(args.repo) if args.repo else None)
    rc = emit(t, pkg, hits, notes, args.quiet)
    sys.stdout.flush()
    return rc


if __name__ == "__main__":
    sys.exit(main())
