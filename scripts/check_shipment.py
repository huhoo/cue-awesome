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

# ── M263：本闸自建的临时目录必须自带清理，且创建失败要响亮（不得带病判定）──────────
# 病灶实测（lead 01:55 票面＋我本拍复算）：`/fast/tmp` 里 `check-shipment-*` 存量 **4,929 枚／669 MB**，
# 近 90 分钟又长出 53 枚——每跑一次完整判据建 1 枚、每跑一次 `--selftest` 建 24 枚，**全文无一对称清理**。
# 连带伤害比满盘更要命：满盘时 `mkdtemp` 抛异常或被调方变量塌成空串，runner 拿空 TMP 继续跑，
# 把「环境故障」伪装成「包缺陷」（M240 验收当场撞过）。故本闸：①凡自建临时目录一律登记、退出时删；
# ②`--keep-tmp` 显式保留（要留就明说是我在留，并打印路径）；③创建失败当场非 0 退码说一句人话，绝不续跑。
_TMP_MADE: list = []
_KEEP_TMP = False


def mk_tmp(prefix: str) -> Path:
    """建一枚本闸自用的临时目录：登记待清、失败即响亮退出（不返回空串，不留半成品）。"""
    global _TMP_MADE
    try:
        d = Path(tempfile.mkdtemp(prefix=prefix))
    except Exception as exc:                                      # noqa: BLE001
        d = None
    if d is None or str(str(d)).strip() == '' or not d.is_dir():
        print(f'check_shipment: 无法创建临时目录（prefix={prefix}，TMPDIR={tempfile.gettempdir()}）——'
              f'多为磁盘满；本闸**不带病判定**，请腾出空间或设 TMPDIR 后复跑', file=sys.stderr)
        sys.exit(3)
    _TMP_MADE.append(d)
    return d


def keep_tmp_report(dirs: list) -> list[tuple[str, Path]]:
    """把登记册分成两档：`在场`／`已自删`。**只读判定**——不删不建，清理逻辑与退码一律不碰（M291 边界）。
    「站点自己删掉了、路径却还留在登记册」是常态（`build_zip` 的 staging 就是这种形制），所以申报必须
    两个数并列：只报登记册长度而自称「保留」，等于把没留下的东西报成留下了——用户按那个数去找就扑空。
    """
    out: list[tuple[str, Path]] = []
    for d in dirs:
        try:
            alive = d.exists()
        except OSError:                       # 判定本身出错＝算不在场，绝不抬进「在场 M」
            alive = False
        out.append(("在场" if alive else "已自删", d))
    return out


def keep_tmp_lines(dirs: list) -> list[str]:
    """keep-tmp 的申报文本：首行「登记 N 枚／在场 M 枚」双数并列，随后逐枚标 `[在场]`／`[已自删]`。
    拆成纯函数是为了让 `--selftest` 能拿一枚**不存在的路径**喂进登记册（注入型反证），
    而不是只能等人肉跑一次 `--keep-tmp` 去猜它报得对不对。
    """
    rows = keep_tmp_report(dirs)
    n_present = sum(1 for tag, _ in rows if tag == "在场")
    head = (f'--keep-tmp：本闸自建临时目录 **登记 {len(rows)} 枚／在场 {n_present} 枚**'
            f'（另有 {len(rows) - n_present} 枚站点已自删——不计入在场，也不称保留）：')
    return [head] + [f'  [{tag}] {d}' for tag, d in rows]


def _tmp_cleanup() -> None:
    """退出时清掉本闸自建的目录；`--keep-tmp` 改为**登记 N／在场 M 双数自报**＋逐枚标档。"""
    if not _TMP_MADE:
        return
    if _KEEP_TMP:
        for line in keep_tmp_lines(_TMP_MADE):
            print(line)
        return
    import shutil as _sh
    leftovers = []
    for d in _TMP_MADE:
        if not d.exists():
            continue                      # 站点自己已删（如 build_zip 的 staging），不算漏
        _sh.rmtree(d, ignore_errors=True)
        if d.exists():
            leftovers.append(str(d))
    if leftovers:
        print(f'check_shipment: 自建临时目录 **未删净 {len(leftovers)} 枚**（被占用或非空），逐枚列路径：', file=sys.stderr)
        for x in leftovers:
            print(f'  未删净 {x}', file=sys.stderr)
    _TMP_MADE.clear()


import atexit as _atexit
_atexit.register(_tmp_cleanup)
import zipfile
from pathlib import Path

# K-12：渠道上传口拒收的形制。模拟打包**必须先按这些剔净**再判指路——
# 否则「文件在仓内、指路也在面」的件会判成假绿（M220 的模型错处：assets/*.png 线上必悬空）。
K12_PATTERNS = (".gitignore", "license", ".png", ".jpg", ".jpeg", ".gif", ".sha256")   # K-12＋K-23 实测拒收族
MAX_BYTES_DEFAULT = 1_048_576          # 渠道 ≈1 MiB 闸；对象＝发布物 zip 字节
MAX_ENTRIES_DEFAULT = 200              # K-20 渠道第二道**独立**硬限：包内条目 ≤200，且**目录条目照计**
                                       # （2026-10-13 实测：`zip -r -X dd-checklist` 得 1,000 条目＝535 文件＋465 目录，
                                       #  渠道 400「文件数量超出限制(最多 200 个)」；旧版本闸只数文件＝这条盲区由渠道先撞到，记 K-20）
K23_ALLOWED_EXT = ("md", "py", "json", "jsonl", "sh", "txt", "html", "pptx", "docx", "yaml")
                                       # M228：K-23 现值第 20 行早写了「实测补充：`.yaml` 亦可通过
                                       # （cue-lead-pieces 一次受理为证，skillId 270806）→ 已受理集扩为…yaml…」，
                                       # 集是十枚；脚本常量停在九枚＝文档跟上、脚本没跟上（C-54 那族），
                                       # 代价是两枚包各背一条假 WARN（同点 agents/openai.yaml）。
# K-23 扩展名面（lead 10-13 从**已受理**渠道件逐枚反推的实证边界，不再靠试错）：
#   实测可过＝上面这族（十枚，与 K-23 现值同集）；实测拒收＝K12_PATTERNS＋压缩包一族＋`.sha256`（第四拒原文点名
#   `scripts/fixtures/_shared/variants/evidence__LEDGER__….sha256`）＋`pyc/pyo/pyd`。
#   对象口径同体积闸与条数闸：**判发布物 zip 内的条目名**，不判仓内 du。
K23_REJECTED_SUFFIXES = (".pyc", ".pyo", ".pyd")
SELFTEST_TIMEOUT = 180

CODE_LEGEND = {
    "S-INPUT":    "输入件读不动（非 zip／目录不存在／成品面空）→ 先把发布物取对再谈结论",
    "S-MISSING":  "成品面指路或能力句在发布物内无对应物→补随包样本，或按「裁样本集不删能力句」改指路",
    "S-SELFTEST": "发布物内自测入口真跑非 0 或不可跑→按详行附的出口原文修，别只看仓内",
    "S-SIZE":     "发布物 zip 字节超闸→裁样本集（在包体上限内取舍），不删能力句",
    "S-COUNT":    "发布物 zip 条目数超渠道硬限（目录条目照计）→把语料并进**允许类型的文本容器**（每样一枚＋runner 铺回临时目录真跑）；"
                  "注意渠道另有扩展名白名单：压缩包与 *.png 同族属拒收面（K-22），**不得缩题、不得把承诺挪到不随包的面**",
    "S-PARITY":   "本地字节与渠道回下载字节两跑结论不一致→查供体与回包，不假设同源",
    "S-TYPE":     "发布物内含渠道实测拒收的扩展名（压缩包／校验值族／字节码）→换允许类型落名，内容不动；"
                  "未实证过的扩展名只出 WARN 不冒充结论（实证可过集见 --list 行）",
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
OUTPUT_DECL = re.compile(r"(?:\bOutputs?|输出|交付物|交付面)\s*(?:\*\*|`|）|\))*\s*[:：]|输出目录|交付的四件")
INVOKE = re.compile(r"python3?\s|bash\s|\s--|\b--\w")
# 裸脚本调用形（M220⑤假阴：`research_run.py --query …` 没有目录前缀，旧版根本不进指针集）
BARE_INV = re.compile(r"(?:^|[\s`|])([A-Za-z0-9_\-]+\.(?:py|sh))(?=\s+--|\s+-\w)")
RUNNER = re.compile(r"(^|/)run_[a-z0-9_]*\.(sh|py)$", re.I)   # runner 形：run_fixtures.sh／run_all.py／run_tests.sh 一类，无参直跑
TESTFILE = re.compile(r"(^|/)test_[A-Za-z0-9_]+\.py$", re.I)   # M220 追加：unittest 形（包内有 test_*.py 即机检面）
MAX_RUNS = 12                                                   # 真跑上限；超出必发「存在未跑」，不得静默截断
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


PLACEHOLDER_TIP = re.compile(r"<[^>`|]+>\s*/?\s*$|^`?<[^>`|]+>")   # 示意图根行：`dd-<主体代码>-<asof>/` 这类占位目录


def schematic_lines(text: str) -> set:
    """「运行产物示意图」行号集（M225 尾巴，lead 把这枚形制判断报给我）：
       围栏代码块内、且**该块根行含 `<占位>` 目录**——那种块画的是用户跑完一次后的交付目录，
       不是包内布局，里面的 `references/x.md` 不是包内指路。
       两条边界钉死：①包内布局图（根行无占位，如 `scripts/fixtures/`）照判，不借豁免扩面；
       ②豁免只作用在**本行**，同一条指路若还出现在别处正文行，仍判（十档i 同形制）。"""
    out, in_fence, block, root_ok = set(), False, [], False
    for i, line in enumerate(text.split("\n"), 1):
        if line.lstrip().startswith("```"):
            if in_fence:
                if root_ok:
                    out.update(block)
                in_fence, block, root_ok = False, [], False
            else:
                in_fence = True
            continue
        if in_fence:
            block.append(i)
            if PLACEHOLDER_TIP.search(line.strip()):
                root_ok = True
    return out


def archive_members(path: Path):
    """K-21 附注：随包档案（tar/tgz/tar/zip）里的**成员名**——语料成档后，面上指的文件可能在档内。
       只读不解（python zipfile/tarfile，K-18 同口径），读不动就返回 None：调用处按「跟随不上」发红，不静默放过。"""
    name = path.name.lower()
    try:
        if name.endswith((".zip",)):
            with zipfile.ZipFile(path) as zf:
                return {n.rstrip("/") for n in zf.namelist()}
        import tarfile
        mode = "r:*" if name.endswith((".tar.gz", ".tgz")) else "r:"
        with tarfile.open(path, mode) as tf:
            return {m.name.rstrip("/") for m in tf.getmembers()}
    except Exception:
        return None


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
    """→ (解包根目录, zip 字节数或 None, zip sha 或 None, 是否临时目录, 条目数或 None, 条目名列表或 None)
       条目数**含目录条目**（渠道 `zip -r` 口径，K-20）；目录输入返回 None（对象口径同体积闸）。"""
    if target.is_dir():
        return target, None, None, False, None, None
    if target.is_file() and zipfile.is_zipfile(target):
        data = target.read_bytes()
        tmp = mk_tmp("check-shipment-")
        with zipfile.ZipFile(target) as zf:
            names_all = zf.namelist()
            n_entries = len(names_all)
            names = [n for n in zf.namelist() if not n.endswith("/")]
            for n in names:
                dest = (tmp / n).resolve()
                if not str(dest).startswith(str(tmp.resolve())):   # zip-slip 防呆
                    raise ValueError(f"越界条目：{n}")
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(zf.read(n))
        return tmp, len(data), hashlib.sha256(data).hexdigest(), True, n_entries, names_all
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


def run_selftest(root: Path, script_rel: str, extra_args, exe=None, argv=None):
    """在**解包件里**真跑一次；返回 (退码或 None, 出口首行)。禁网：不给代理，cwd 锁在件内。
       `argv` 给非直跑形（unittest 用 `-m unittest discover`），不认「文件在=跑过」。"""
    env = dict(os.environ)
    for k in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy", "ALL_PROXY", "all_proxy"):
        env.pop(k, None)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    cmd = list(argv) if argv else [exe or sys.executable, script_rel] + list(extra_args)
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


def check(target: Path, pkg: str, channel_zip: Path | None, max_bytes: int, quiet: bool, repo_dir: Path | None = None,
          max_entries: int = MAX_ENTRIES_DEFAULT, max_runs: int = MAX_RUNS):
    hits = []
    notes = []
    try:
        root_raw, nbytes, ndigest, is_tmp, n_entries, names_all = load_shipment(target)
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
    # K-21 报账可见性：随包档案列出来（成员数供人对账），但**指路一律不拿档案背书**——
    #   档内那份是测试语料，不是「你装好的包里有这件」。实测把档案成员放进解析时，dd 的
    #   `references/coverage-map.md` 两枚真断链当场变绿＝把缺陷藏进档案，正属 K-21 禁手，故只报不判。
    arch_report = []
    for f in files:
        if f.lower().endswith((".tar.gz", ".tgz", ".tar", ".zip")):
            mem = archive_members(root / f)
            arch_report.append((f, (len(mem) if mem is not None else None)))

    # ①② 相对指路存在性 ＋ 能力句载体（外调面与出生句单列，供报账分诊）
    cap_lines = []
    births = []
    birth_by_face = []
    outer_total = []
    schem_total = []
    cmds = []
    for rel in faces:
        text = read_text(root, rel)
        schem = schematic_lines(text)
        pts, birth_hits, outer_hits, schem_hits = {}, 0, 0, 0
        for lno, ln in enumerate(text.splitlines(), 1):
            exempt = (lno in schem) or ((not INVOKE.search(ln)) and (
                (BIRTH_VERB.search(ln) and BIRTH_HINT.search(ln)) or OUTPUT_DECL.search(ln)))
            lp, lo = extract_pointers(ln)
            outer_hits += lo
            for tok, isf in lp:
                if lno in schem:
                    schem_hits += 1
                    continue
                if exempt:
                    birth_hits += 1
                    continue
                pts.setdefault(tok, isf)          # 只在「非豁免行」上留下待判指针
        outer_total.append((rel, outer_hits))
        for tok, has_ext in sorted(pts.items()):
            if "/" in tok and tok.split("/")[0] not in ("fixtures", "tests", "assets", "references", "examples", "scripts"):
                continue          # 带目录段的只认自家六个目录；裸文件名（调用形）在包内任意路径里找
            base = rel.rsplit("/", 1)[0] if "/" in rel else ""
            cands = ([f"{base}/{tok}"] if base else []) + [tok]
            if has_ext:
                if "/" not in tok:      # 裸调用形：包内**任意路径**下同名件都算跟随
                    found = any(f.rsplit("/", 1)[-1] == tok for f in files)
                else:
                    found = any(c in fileset for c in cands)
                    # 路径级承诺**不得由随包档案背书**（档案里那份是测试语料，不是装好的包里有这件）
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
        birth_by_face.append((rel, birth_hits))
        schem_total.append((rel, schem_hits))
        # 目录级承诺（原文以 / 收尾）已由上一条按目录判，这里不重复发红
        for lineno, line in enumerate(text.splitlines(), 1):
            if CAPWORD.search(line):
                cap_lines.append((rel, lineno, line.strip()[:160]))
            for m in CMD.finditer(line):
                cmds.append((rel, lineno, norm_rel(m.group(1))))

    # ③ 自测入口真跑：成品面写明的命令 ∪ 发布物内 .py 自带 --selftest 的脚本 ∪ runner 形 ∪ **unittest 形**
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
        if TESTFILE.search(rel):        # M220 追加：包内有 test_*.py 就是机检面，别只认前两种形
            form.setdefault(rel, "unittest")
    entries = sorted(form)
    ran = []
    uniq_cmds = entries[:max_runs]
    skipped = [e for e in entries if e not in set(uniq_cmds)]
    for scr in uniq_cmds:
        face = next((f for f, _, s in cmds if norm_rel(s) == scr), "（发布物内脚本自报）")
        if scr not in fileset:
            continue  # 缺件已在上面发过 S-MISSING，不在这里重复发红
        kind = form.get(scr, "selftest")
        args = ["--selftest"] if kind.startswith("selftest") else []
        runner = "bash" if scr.endswith(".sh") else sys.executable
        if kind == "unittest":
            d, _, b = scr.rpartition("/")
            argv = [sys.executable, "-m", "unittest", "discover", "-s", d or ".", "-p", b]
            rc, first = run_selftest(root, scr, [], argv=argv)
        else:
            rc, first = run_selftest(root, scr, args, runner)
        ran.append((scr, kind, rc, first))
        if rc is None:
            hits.append(Hit("S-SELFTEST", face, scr, f"入口形={kind}｜解包件内真跑不可完成：{first}"))
        elif rc != 0:
            hits.append(Hit("S-SELFTEST", face, scr, f"入口形={kind}｜解包件内真跑退码 {rc}；出口末读「{first}」"))
    # **存在入口而未跑＝ERROR**（lead 2026-10-14 追加②）：PASS＋0 枚会被下一轮全量回扫读成「跑过且绿」，
    # 比错报更危险。 candidates（盘面实有的机检文件）与 attempted（真跑过的）逐枚对，缺一枚报一枚。
    cand = {e for e in entries if e in fileset}
    missed = sorted(cand - {r[0] for r in ran})
    for m in missed[:8]:
        hits.append(Hit("S-SELFTEST", "（入口清点）", m,
                        f"发布物内存在机检入口（入口形={form.get(m, '？')}）而闸未跑＝**判据空跑**；"
                        f"本轮真跑上限 {max_runs} 枚、候选 {len(cand)} 枚，逐枚清点不得默认「没跑＝跑过」"))
    if len(missed) > 8:
        notes.append(f"入口清点：另有 {len(missed) - 8} 枚存在未跑（详行已截 8 枚）")
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

    # ④b 条数闸（K-20，渠道 2026-10-13 撞出来的第二道**独立**硬限）：对象＝zip 条目数，目录条目照计
    if n_entries is None:
        hits.append(Hit("S-COUNT", "-", pkg,
                        "输入是目录：条数闸不判（它量的是发布物 zip 条目数，**含目录条目**；"
                        "仓内只数文件会少算——实测 dd 随样态 535 文件＋465 目录＝1,000 条目，渠道 400「最多 200 个」）",
                        sev="WARN"))
    elif n_entries > max_entries:
        hits.append(Hit("S-COUNT", "-", pkg,
                        f"发布物 zip 条目现值 {n_entries:,}（含目录条目）＞ 渠道硬限 {max_entries:,}；"
                        f"字节在闸内也不放行——修法＝语料成档（一枚档案＋解包真跑），不缩题、不把承诺挪出随包面"))

    # ④c 类型闸（K-23，第四拒换来的实证边界）：对象＝zip 内**文件条目名**的后缀，目录条目不参与
    if names_all is not None:
        only_files = [n for n in names_all if not n.endswith("/")]
        rej = [n for n in only_files
               if n.lower().endswith(K23_REJECTED_SUFFIXES)
               or any(n.lower().endswith(e) for e in (".tar", ".tar.gz", ".tgz", ".zip", ".gz", ".bz2", ".xz", ".7z", ".rar"))
               or n.lower().rsplit(".", 1)[-1] in ("png", "jpg", "jpeg", "gif", "gitignore", "license")
               or n.lower().endswith(".sha256")]
        unk = [n for n in only_files if n not in rej
               and (("." + n.rsplit(".", 1)[-1].lower()) if "." in n.rsplit("/", 1)[-1] else None) not in
               [("." + e) for e in K23_ALLOWED_EXT]]
        for n in rej[:5]:
            hits.append(Hit("S-TYPE", "-", n,
                            f"渠道实测拒收类型（K-23），发布物内该条目名过不去；共 {len(rej)} 枚，详列在报账行"))
        if len(rej) > 5:
            notes.append(f"拒收类型其余 {len(rej) - 5} 枚：{'、'.join(rej[5:8])}…")
        if unk:
            hits.append(Hit("S-TYPE", "-", "（未实证集）",
                            f"{len(unk)} 枚后缀不在 lead 反推的实证可过集 {list(K23_ALLOWED_EXT)} 内，也未实测被拒"
                            f"（如 {'、'.join(sorted({u.rsplit('.', 1)[-1] for u in unk})[:4])}）——只报不判红",
                            sev="WARN"))

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
            sub_hits, _, _ = check(channel_zip, pkg + "（渠道副本）", None, max_bytes, True, repo_dir, max_entries)
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
    birth_n = sum(b for _, b in birth_by_face)
    schem_n = sum(s for _, s in schem_total)
    n_st = sum(1 for r in ran if r[1].startswith("selftest"))
    n_ru = sum(1 for r in ran if r[1] == "runner")
    for h in hits:                  # 报账面一律去绝对路径：随机临时名进报账＝双跑不可 diff
        h.detail = mask_paths(h.detail, leaks)
        h.ref = mask_paths(h.ref, leaks)
    notes.append(f"豁免分诊：逐行豁免命中 {birth_n} 次；运行产物示意图（占位根行的围栏块）内不计 {schem_n} 处"
                 f"（只免本行，同 token 在正文行照判；包内布局图无占位根，不免）；跨包与安装位指路不计本包缺失 "
                 f"{sum(n for _, n in outer_total)} 处（逐面清单在详行区外，不静默放过）")
    if arch_report:
        unread = [f for f, n in arch_report if n is None]
        notes.append("随包档案：" + "、".join(f"{f}（成员 {n}）" if n is not None else f"{f}（读不动）" for f, n in arch_report)
                     + "；**档案成员不给指路背书**（只列不判，读不动也不静默放过）"
                     + (f"；不可读清单 {unread}" if unread else ""))
    n_ut = sum(1 for r in ran if r[1] == "unittest")
    _forms = f"（入口形：selftest {n_st}｜runner {n_ru}｜unittest {n_ut}）"
    if not ran:
        # lead 票面第 520 行②：「0 枚真跑」不得并类。**仓内有没有入口**决定这句该怎么写——
        #  判据只量发布物字节，但报账不能把「这形态没带样」写成「这包没有机检面」（后者会把该修的假象洗白）。
        if repo_dir is not None and any(
                TESTFILE.search(p.relative_to(repo_dir).as_posix()) or RUNNER.search(p.relative_to(repo_dir).as_posix())
                for p in repo_dir.rglob("*") if p.is_file()):
            _forms = ("（本交付形内无入口载体＝**剔样／配方态**：仓内有 test_*.py／run_*，是没随这枚字节走，"
                      "不是这包没有机检面；缺件面另由 S-MISSING／能力句判）")
        else:
            _forms = ("（**真无机检面**：包内与仓内都无 test_*.py／run_*／`--selftest` 载体；"
                      "「入口存在未识别」不写在这里——那种形制当场发 ERROR）")
    notes.append(f"成品面 {len(faces)} 面／能力句 {len(cap_lines)} 行／自测入口 {len(ran)} 枚真跑{_forms}")
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
    """K-12／K-22 渠道上传口拒收的形制，**含嵌套目录**（basename 命中即剔）。
       模拟打包必须先按它剔净再判指路——否则「文件在仓内、指路也在面」的件会判成假绿。
       压缩包一族是 2026-10-13 实测加进来的：语料封成 tar.gz 后渠道 400
       「不允许的文件类型: scripts/fixtures/corpus.tar.gz」——它与 *.png 同族，条数解了、类型没过。"""
    low = rel.lower()
    base = low.rsplit("/", 1)[-1]
    return (".gitignore" in low or base.startswith("license")
            or any(base.endswith(e) for e in (".png", ".jpg", ".jpeg", ".gif"))
            or any(base.endswith(e) for e in (".tar", ".tar.gz", ".tgz", ".zip", ".gz", ".bz2", ".xz", ".7z", ".rar")))


def build_zip(dst: Path, root: Path, drop=(), include_fixtures=True, apply_k12=True, sink=None):
    """返回 dst（调用点形制不变）；剔件清单写进 sink（list），供报账写明「本次模拟剔了哪些形制」。"""
    import shutil
    staging = mk_tmp("cs-build-")
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
        # 与渠道 `zip -r` 同形制：顶层目录与所有子目录**各占一枚条目**（K-20 条数按全部条目计）。
        # 少写目录条目＝代理件比真发布物小＝条数假绿，这条与 M220 的 K-12 盲区同罪。
        top = zipfile.ZipInfo(root.name + "/")
        top.date_time = (1980, 1, 1, 0, 0, 0)
        top.external_attr = 0o40755 << 16
        zf.writestr(top, "")
        for p in sorted(staging.rglob("*")):
            rel = p.relative_to(staging).as_posix()
            if p.is_dir():
                info = zipfile.ZipInfo(rel + "/")
                info.date_time = (1980, 1, 1, 0, 0, 0)
                info.external_attr = 0o40755 << 16
                zf.writestr(info, "")
            else:
                zf.write(p, rel)
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
    z = build_zip(mk_tmp("cs-z-") / "demopkg.zip", fixture_root("good"))
    r = check(z, "demopkg", None, MAX_BYTES_DEFAULT, True)
    one("一档-合规样必绿", 0, emit(z, "demopkg", r[0], r[1], quiet=True))
    # 一档c（K-18：解包口一律 python zipfile）：中文条目名的包必须绿，且本闸源码不得起 unzip
    import ast as _ast
    _tree = _ast.parse(Path(__file__).read_text(encoding="utf-8"))
    _spawn = ("run", "Popen", "check_output", "check_call", "call", "system", "popen")
    argv_unzip = [c.value for nd in _ast.walk(_tree) if isinstance(nd, _ast.Call)
                  and getattr(nd.func, "attr", "") in _spawn
                  for c in _ast.walk(nd)
                  if isinstance(c, _ast.Constant) and isinstance(c.value, str) and "unzip" in c.value]
    one("一档c-解包口不起 unzip 进程", True, not argv_unzip, f"命中={argv_unzip[:2] or '无'}")
    zh = mk_tmp("cs-zh-") / "demopkg"
    zh.mkdir()
    (zh / "SKILL.md").write_text("# 中文条目名样例\n\n模板见 `assets/交付物模板.md`；说明见 `references/中文说明.md`。\n", encoding="utf-8")
    (zh / "assets").mkdir(); (zh / "references").mkdir()
    (zh / "assets" / "交付物模板.md").write_text("# 模板\n", encoding="utf-8")
    (zh / "references" / "中文说明.md").write_text("说明一句\n", encoding="utf-8")
    zz = build_zip(mk_tmp("cs-z-") / "中文包名.zip", zh)
    rzh = check(zz, "中文包名", None, MAX_BYTES_DEFAULT, True)
    one("一档d-中文条目名必绿（不假红）", 0, 1 if any(h.sev == "ERROR" for h in rzh[0]) else 0,
        "零发条" if not any(h.sev == "ERROR" for h in rzh[0]) else rzh[0][0].line()[:40])

    # 一档b：渠道同一枚字节也要能跑（S-PARITY 不误拦）
    z2 = Path(str(z) + ".copy")
    z2.write_bytes(z.read_bytes())
    r = check(z, "demopkg", z2, MAX_BYTES_DEFAULT, True)
    one("一档b-渠道同字节不误拦", 0, emit(z, "demopkg", r[0], r[1], quiet=True))

    # 二档：缺件样必红（把 fixtures 从包里剔掉，能力句与指路都还在）
    zm = build_zip(mk_tmp("cs-z-") / "demopkg.zip", fixture_root("missing"),
                   include_fixtures=False)
    rm = check(zm, "demopkg", None, MAX_BYTES_DEFAULT, True)
    codes = {h.code for h in rm[0] if h.sev == "ERROR"}
    one("二档-缺件样必红", 1, emit(zm, "demopkg", rm[0], rm[1], quiet=True))
    one("二档b-发红码含 S-MISSING", True, "S-MISSING" in codes, f"实得 {sorted(codes)}")

    # 二档c（反向自证，防恒真）：把同一枚缺件样 SKILL 里那两句指路／能力句删掉，必须转绿——
    #         证明二档的红来自那两行判据，而不是「逢这份样必红」。
    inv = mk_tmp("cs-inv-") / "demopkg"
    shutil.copytree(fixture_root("missing"), inv)
    sk = inv / "SKILL.md"
    sk.write_text("# 示例包 SKILL\n\n只讲能力，不指样本、不承诺自测。\n", encoding="utf-8")
    zi = build_zip(mk_tmp("cs-z-") / "demopkg.zip", inv)
    one("二档c-删掉承诺即转绿（防恒真）", 0, emit(zi, "demopkg", *check(zi, "demopkg", None, MAX_BYTES_DEFAULT, True)[0:2], quiet=True))

    # 三档：自测真跑必红（包里带着会退 1 的入口）
    zr = build_zip(mk_tmp("cs-z-") / "demopkg.zip", fixture_root("red"))
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
    zr_ok = build_zip(mk_tmp("cs-z-") / "demopkg.zip", fixture_root("runner-good"))
    for tag, zz in (("selftest 形", z), ("runner 形", zr_ok)):
        a = subprocess.run([sys.executable, "-B", __file__, str(zz)], capture_output=True, text=True)
        b = subprocess.run([sys.executable, "-B", __file__, str(zz)], capture_output=True, text=True)
        one(f"五档-双跑同值（{tag}）", True, (a.stdout == b.stdout and a.returncode == b.returncode),
            f"退码 {a.returncode}/{b.returncode}")

    # 八档：runner 形三枚（合规必绿／缺件必红／真跑非零必红），加一条「入口形」报账
    rh = check(zr_ok, "demopkg", None, MAX_BYTES_DEFAULT, True)
    one("八档-合规 runner 样必绿", 0, emit(zr_ok, "demopkg", rh[0], rh[1], quiet=True))
    one("八档b-入口形标注为 runner", True, any("runner" in n for n in rh[1]), f"读数={rh[1][-1][:56]}")
    zrm = build_zip(mk_tmp("cs-z-") / "demopkg.zip", fixture_root("runner-missing"))
    rrm = check(zrm, "demopkg", None, MAX_BYTES_DEFAULT, True)
    one("八档c-缺件 runner 样必红", 1, emit(zrm, "demopkg", rrm[0], rrm[1], quiet=True))
    one("八档d-发红码含 S-MISSING", True, "S-MISSING" in {h.code for h in rrm[0] if h.sev == "ERROR"})
    zrr = build_zip(mk_tmp("cs-z-") / "demopkg.zip", fixture_root("runner-red"))
    rrr = check(zrr, "demopkg", None, MAX_BYTES_DEFAULT, True)
    one("八档e-runner 真跑非零必红", 1, emit(zrr, "demopkg", rrr[0], rrr[1], quiet=True))
    one("八档f-发红码含 S-SELFTEST", True, "S-SELFTEST" in {h.code for h in rrr[0] if h.sev == "ERROR"},
        f"详行={next((h.line() for h in rrr[0] if h.code=='S-SELFTEST'), '无')[:64]}")

    # 九档（lead 新逮的形制缺陷：随机临时目录名进报账＝双跑不可 diff）：
    zpl = build_zip(mk_tmp("cs-z-") / "demopkg.zip", fixture_root("runner-pathleak"))
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
        zz = build_zip(mk_tmp("cs-z-") / "demopkg.zip", fixture_root(kind))
        return zz, check(zz, "demopkg", None, MAX_BYTES_DEFAULT, True)

    for kind, label in (("url-green", "外链不进指针集"), ("crosspkg-green", "跨包与安装位不判本包缺件"),
                        ("birth-green", "出生句与输出声明行豁免"), ("prefix-green", "前缀下有真件即算跟随")):
        _, rr = tier(kind)
        errs = [h for h in rr[0] if h.sev == "ERROR"]
        one(f"十档-{label}必绿", 0, 1 if errs else 0, (errs[0].line()[:60] if errs else "零发条"))
    _, rmx = tier("birth-mixed")
    mx = [h for h in rmx[0] if h.code == "S-MISSING" and "coverage-map" in h.ref]
    one("十档i-豁免行不洗白同 token 的非豁免行", 1, 1 if mx else 0,
        (mx[0].line()[:60] if mx else "未发红（＝整文件放行旧病复发）"))

    _, rp2 = tier("prefix-red")
    msgs = [h.detail for h in rp2[0] if h.code == "S-MISSING"]
    one("十档h-前缀下无真件必红", 1, 1 if any("前缀目录下无一件真件" in m for m in msgs) else 0, f"条数={len(msgs)}")

    zr1, rr1 = tier("bareinv-red")
    one("十档e-裸调用缺件必红", 1, 1 if any(h.sev == "ERROR" and h.code == "S-MISSING" for h in rr1[0]) else 0)
    zr2, rr2 = tier("png-red")
    one("十档f-png 被 K-12 剔后指路必红", 1,
        1 if any(h.sev == "ERROR" and h.code == "S-MISSING" and "demo-verifiable.png" in h.ref for h in rr2[0]) else 0)
    sink_probe = []
    zp = build_zip(mk_tmp("cs-z-") / "demopkg.zip", fixture_root("png-red"), sink=sink_probe)
    one("十档g-报账写出剔了哪些形制", True, any(d.startswith("K-12") for d in sink_probe), f"剔={sink_probe[:2]}")

    # 六档b（lead 的两枚实测事实钉成机器判据）：
    #   ①体积闸只认 zip 字节——目录哪怕塞满 2 MiB 也不得发 ERROR（防「拿仓内 du 对渠道闸」那类假前提）
    big = mk_tmp("cs-big-") / "demopkg"
    shutil.copytree(fixture_root("good"), big)
    (big / "assets" / "big.bin").write_bytes(b"\0" * 2_000_000)
    rbig = check(big, "demopkg", None, MAX_BYTES_DEFAULT, True)
    one("六档b-目录2MiB不判体积", 0, emit(big, "demopkg", rbig[0], rbig[1], quiet=True))
    #   ②渠道回下载那份也要能跑，两跑结论不一致必红
    zb = build_zip(mk_tmp("cs-z-") / "demopkg.zip", fixture_root("missing"), include_fixtures=False)
    rp = check(z, "demopkg", zb, MAX_BYTES_DEFAULT, True)
    one("六档c-两枚字节结论不一必红", 1, emit(z, "demopkg", rp[0], rp[1], quiet=True))
    one("六档d-发红码含 S-PARITY", True, "S-PARITY" in {h.code for h in rp[0] if h.sev == "ERROR"})

    # 七档：输入读不动必发 S-INPUT（不自掩）
    bogus = mk_tmp("cs-z-") / "not-a-zip.zip"
    bogus.write_text("这不是 zip", encoding="utf-8")
    rb = check(bogus, "demopkg", None, MAX_BYTES_DEFAULT, True)
    one("七档-读不动不自掩", True, {h.code for h in rb[0]} == {"S-INPUT"}, f"实得 {sorted({h.code for h in rb[0]})}")

    # 十一档（K-20：渠道 2026-10-13 撞出来的**第二道独立硬限**——条目 ≤200，目录条目照计）：
    #   本闸此前只数文件，dd 随样态代理件报 535 条目、渠道报 1,000 并 400 拒收。
    #   这是 M220「模型错了一处」的同罪形（少报方向），故三枚档一起钉：口径、超限必红、合规不误拦。
    ze = build_zip(mk_tmp("cs-z-") / "demopkg.zip", fixture_root("entries-nested"))
    with zipfile.ZipFile(ze) as zf:
        got = len(zf.namelist())
    pred = predict_entries(fixture_root("entries-nested"))
    one("十一档-目录条目必计入（代理件不得比真件小）", True, got == pred == 8, f"zip={got} 预数={pred} 期望=8（4 文件＋4 目录含顶层）")
    rcnt = check(ze, "demopkg", None, MAX_BYTES_DEFAULT, True, None, 3)
    one("十一档b-条目超限必红", 1, emit(ze, "demopkg", rcnt[0], rcnt[1], True))
    one("十一档c-发红码含 S-COUNT", True, "S-COUNT" in {h.code for h in rcnt[0] if h.sev == "ERROR"},
        f"实得 {sorted({h.code for h in rcnt[0] if h.sev == 'ERROR'})}")
    rcnt2 = check(ze, "demopkg", None, MAX_BYTES_DEFAULT, True)          # 同一枚字节，闸值取默认 200
    one("十一档d-合规条数不误拦", 0, emit(ze, "demopkg", rcnt2[0], rcnt2[1], True))
    rdir_cnt = check(fixture_root("entries-nested"), "demopkg", None, MAX_BYTES_DEFAULT, True)
    one("十一档e-目录输入只 WARN 不判条数", True,
        any(h.code == "S-COUNT" and h.sev == "WARN" and "含目录条目" in h.detail for h in rdir_cnt[0]),
        f"详行「{[h.detail[:34] for h in rdir_cnt[0] if h.code == 'S-COUNT']}」")
    one("十一档f-闸值与码表写明 K-20 口径", True,
        MAX_ENTRIES_DEFAULT == 200 and "目录条目照计" in CODE_LEGEND["S-COUNT"], f"现值 {MAX_ENTRIES_DEFAULT}")
    # 十二档（K-21 反洗白）：路径级指路**只有档内那份**时必红——档案是测试语料，不给承诺背书。
    za, ra = tier("arch-dangling")
    one("十二档-指路只在档案内仍必红", 1, emit(za, "demopkg", ra[0], ra[1], True))
    one("十二档b-发红码含 S-MISSING", True,
        any(h.code == "S-MISSING" and h.ref == "references/deep/inside.md" for h in ra[0] if h.sev == "ERROR"),
        f"实得 {[(h.code, h.ref) for h in ra[0]]}")
    # 档案进报账要**不剔类型**才看得见（build_zip 默认按 K-22 把压缩包剔掉，正是渠道真形制）
    zae = build_zip(mk_tmp("cs-z-") / "demopkg.zip",
                    fixture_root("arch-dangling"), apply_k12=False)
    re_ = check(zae, "demopkg", None, MAX_BYTES_DEFAULT, True)
    one("十二档c-档案本身进报账", True, any("corpus.tar.gz" in n and "成员 1" in n for n in re_[1]),
        f"读数={[n[:56] for n in re_[1] if '档案' in n]}")
    sink_arch = []
    zna = build_zip(mk_tmp("cs-z-") / "demopkg.zip", fixture_root("arch-dangling"),
                    sink=sink_arch)
    one("十二档d-压缩包按 K-22 剔出模拟包", True, any(d.startswith("K-12:corpus.tar.gz") for d in sink_arch),
        f"剔={sink_arch[:2]}")
    with zipfile.ZipFile(zna) as zf:
        one("十二档e-剔后包内不留档案", True, not any(n.endswith((".tar.gz", ".zip", ".tgz")) for n in zf.namelist()),
            f"条目={[n for n in zf.namelist()][:3]}")

    # 十三档（运行产物示意图 vs 包内布局图，lead 把这枚形制判断报给我裁）：
    #   豁免只认「围栏块根行含 <占位> 目录」那种交付目录示意图；包内布局图不占这个便宜。
    zg = build_zip(mk_tmp("cs-z-") / "demopkg.zip", fixture_root("tree-output-green"))
    rg = check(zg, "demopkg", None, MAX_BYTES_DEFAULT, True)
    one("十三档-交付目录示意图必绿", 0, emit(zg, "demopkg", rg[0], rg[1], True))
    one("十三档b-豁免计入报账读数", True, any("示意图" in n and "不计 1 处" in n for n in rg[1]),
        f"读数={[n[:44] for n in rg[1] if '示意图' in n]}")
    zr3 = tier("tree-output-red")
    one("十三档c-同 token 在正文行照判（豁免不外溢）", 1, emit(zr3[0], "demopkg", zr3[1][0], zr3[1][1], True))
    one("十三档d-发红恰一条且是那枚路径", True,
        len([h for h in zr3[1][0] if h.sev == "ERROR"]) == 1
        and zr3[1][0][0].ref == "references/coverage-map.md",
        f"实得 {[(h.code, h.ref) for h in zr3[1][0] if h.sev == 'ERROR']}")
    zl = build_zip(mk_tmp("cs-z-") / "demopkg.zip", fixture_root("tree-layout-red"))
    rl = check(zl, "demopkg", None, MAX_BYTES_DEFAULT, True)
    one("十三档e-包内布局图不借豁免", 1, emit(zl, "demopkg", rl[0], rl[1], True))
    one("十三档f-发红码含该缺失件", True,
        any(h.ref == "references/missing.md" for h in rl[0] if h.sev == "ERROR"),
        f"实得 {[(h.code, h.ref) for h in rl[0] if h.sev == 'ERROR']}")

    # 十四档（K-23 扩展名面，lead 用四次 400 换来的实证边界）：
    #   对象＝发布物 zip 内条目名的后缀。实测拒收族发红；未实证过的后缀**只 WARN 不冒充结论**。
    zt = build_zip(mk_tmp("cs-z-") / "demopkg.zip", fixture_root("type-k23"))
    rt = check(zt, "demopkg", None, MAX_BYTES_DEFAULT, True)
    one("十四档-实测拒收后缀必红", 1, emit(zt, "demopkg", rt[0], rt[1], True))
    one("十四档b-发红码含 S-TYPE 且点到那枚件", True,
        any(h.code == "S-TYPE" and h.ref.endswith("LEDGER.sha256") for h in rt[0] if h.sev == "ERROR"),
        f"实得 {[(h.code, h.ref.rsplit('/', 1)[-1]) for h in rt[0] if h.sev == 'ERROR']}")
    # 防恒真：剔掉那枚拒收件（留下同包其余件）必须转绿——红来自那一枚，不是逢样必红
    zt2 = build_zip(mk_tmp("cs-z-") / "demopkg.zip", fixture_root("type-k23"),
                    drop=("LEDGER.sha256",))
    rt2 = check(zt2, "demopkg", None, MAX_BYTES_DEFAULT, True)
    one("十四档c-剔掉拒收件即转绿（防恒真）", 0, emit(zt2, "demopkg", rt2[0], rt2[1], True))
    one("十四档d-未实证后缀只 WARN 不判红", True,
        any(h.code == "S-TYPE" and h.sev == "WARN" and "ini" in h.detail for h in rt2[0])
        and not any(h.sev == "ERROR" for h in rt2[0]),
        f"实得 {[(h.code, h.sev, h.detail[:24]) for h in rt2[0]]}")
    one("十四档e-实证可过集枚数与 K-23 现值同集", True, len(K23_ALLOWED_EXT) == 10 and "yaml" in K23_ALLOWED_EXT,
        f"可过族={list(K23_ALLOWED_EXT)}")

    # 十五档（M220 追加，lead 2026-10-14 渠道回字节逐枚跑出来的**判据空跑**）：
    #   unittest 形入口（包内有 test_*.py）旧版根本不认——cue-lead-pieces／cue-omni-ontology
    #   各自解包件里 discover 退 0 且末行 OK，闸却报「0 枚真跑＋PASS」＝把「没跑」读成「跑过且绿」。
    zug = build_zip(mk_tmp("cs-z-") / "demopkg.zip", fixture_root("unittest-green"))
    rug = check(zug, "demopkg", None, MAX_BYTES_DEFAULT, True)
    one("十五档-unittest 形入口必被真跑且退 0", 0, emit(zug, "demopkg", rug[0], rug[1], True))
    one("十五档b-入口形标注为 unittest", True, any(r[1] == "unittest" for r in rug[2]["ran"]),
        f"读数={[n[:70] for n in rug[1] if '入口形' in n]}")
    zur3 = tier("unittest-red")
    one("十五档c-unittest 真跑非零必红", 1, emit(zur3[0], "demopkg", zur3[1][0], zur3[1][1], True))
    one("十五档d-发红码含 S-SELFTEST 且点到那枚 test", True,
        any(h.code == "S-SELFTEST" and h.ref.endswith("test_fail.py") for h in zur3[1][0] if h.sev == "ERROR"),
        f"实得 {[(h.code, h.ref) for h in zur3[1][0] if h.sev == 'ERROR']}")
    # **存在入口而未跑＝ERROR**（lead 追加②：PASS＋0 枚＝漏跑不报，比错报更危险）
    rug0 = check(zug, "demopkg", None, MAX_BYTES_DEFAULT, True, None, MAX_ENTRIES_DEFAULT, max_runs=1)
    one("十五档e-入口存在而未跑必发 ERROR", 1, emit(zug, "demopkg", rug0[0], rug0[1], True))
    one("十五档f-未跑发码写明判据空跑", True,
        any(h.code == "S-SELFTEST" and "判据空跑" in h.detail for h in rug0[0] if h.sev == "ERROR"),
        f"实得 {[(h.code, h.ref) for h in rug0[0] if h.sev == 'ERROR']}")
    # 十五档g（lead 票面第 520 行②：「0 枚真跑」不得并类）——报账要当场分写出两件事
    # 十六档（M228：`.yaml` 入集后不得顺手把真被拒的放过——集要扩，判据不能软）
    zyy = build_zip(mk_tmp("cs-z-") / "demopkg.zip", fixture_root("yaml-allowed"))
    ryy = check(zyy, "demopkg", None, MAX_BYTES_DEFAULT, True)
    one("十六档-已受理族不再背 WARN", True,
        not any(h.code == "S-TYPE" and h.sev == "WARN" and "yaml" in h.detail for h in ryy[0]),
        f"读数={[h.detail[:52] for h in ryy[0] if h.code == 'S-TYPE']}")
    one("十六档b-同包内真被拒后缀仍必红（入集不放软判据）", True,
        any(h.code == "S-TYPE" and h.sev == "ERROR" and h.ref.endswith("LEDGER.sha256") for h in ryy[0]),
        f"实得={[(h.sev, h.ref.rsplit('/', 1)[-1]) for h in ryy[0] if h.code == 'S-TYPE']}")

    # 十七档（K-25：渠道实供＝平铺无顶层目录；本地建包＝带单一顶层目录。判据不能挑布局）
    d17 = mk_tmp("cs-17-")
    ztop = d17 / "top.zip"
    build_zip(ztop, fixture_root("good"))
    zflat = d17 / "flat.zip"
    with zipfile.ZipFile(ztop) as zin, zipfile.ZipFile(zflat, "w", zipfile.ZIP_DEFLATED) as zout:
        pre = zin.namelist()[0].split("/", 1)[0] + "/"
        for it in zin.infolist():
            n = it.filename
            if n.startswith(pre):
                n = n[len(pre):]
            if not n:
                continue
            it.filename = n
            zout.writestr(it, zin.read(it.filename if False else pre + n if (pre + n) in zin.namelist() else n))
    r17a = check(ztop, "demopkg", None, MAX_BYTES_DEFAULT, True)
    r17b = check(zflat, "demopkg", None, MAX_BYTES_DEFAULT, True)
    one("十七档-两种条目布局结论同值（解包口对布局免疫）", True,
        len([h for h in dedupe(r17a[0]) if h.sev == "ERROR"]) == len([h for h in dedupe(r17b[0]) if h.sev == "ERROR"])
        and bool(r17b[2].get("ran")) == bool(r17a[2].get("ran")),
        f"带顶层={len(r17a[2].get('ran') or [])} 枚真跑／平铺={len(r17b[2].get('ran') or [])} 枚真跑")

    one("十五档g-零入口报账写明「真无机检面」", True,
        any("真无机检面" in n and "入口存在未识别" in n for n in rg[1]) and not any("真无机检面" in n for n in rug[1]),
        f"绿样读数={[n[:60] for n in rug[1] if '自测入口' in n]}｜未跑读数={[n[:40] for n in rg[1] if '自测入口' in n]}")

    # 廿档（M291：`--keep-tmp` 申报改双数——登记 N／在场 M 并列，逐枚标 [在场]／[已自删]）
    # 注入型反证：往登记册喂一枚**不存在**的路径，它必须被报成 [已自删] 且不进「在场 M」；跑不出这枚＝本档红。
    fake = Path(tempfile.gettempdir()) / f"check-shipment-M291INJECT-{os.getpid()}-{len(_TMP_MADE)}"
    real = fixture_root("good")
    kl = keep_tmp_lines([real, fake])
    inj_reported = any(line.endswith(str(fake)) and "[已自删]" in line for line in kl)
    real_reported = any(line.endswith(str(real)) and "[在场]" in line for line in kl)
    head_ok = ("登记 2 枚／在场 1 枚" in kl[0]) and not re.search(r"保留 \d+ 枚", kl[0])
    one("廿档-keep-tmp 申报双数＋反证", True,
        bool(inj_reported and real_reported and head_ok and real.is_dir()),
        f"注入枚＝{fake.name}（exists={fake.exists()}）｜首行＝{kl[0][:76]}｜注入命中＝{int(inj_reported)} 枚")

    SILENT.clear()
    for line in res:
        print(line)
    print(f"selftest: {'ALL GREEN（能红、能绿、可复现、对象口径写明）' if ok else 'FAIL'}")
    return 0 if ok else 1


def predict_entries(root: Path, include_fixtures=True, apply_k12=True) -> int:
    """K-20 前置数：按渠道 `zip -r` 形制**不建 zip 数条目**——顶层目录 1 枚＋所有子目录各 1 枚＋文件各 1 枚。
       用途＝往包里加夹具**之前**先数一次（渠道那条闸看的不是文件数）。与 build_zip 同剔形制口径。"""
    n = 1                                     # 顶层目录条目（zip -r 会把包名本身写进去）
    for p in sorted(root.rglob("*")):
        rel = p.relative_to(root).as_posix()
        if "__pycache__" in p.parts:
            continue
        if not include_fixtures and ("fixtures/" in rel or rel.startswith("tests/") or p.name in ("fixtures", "tests")):
            continue
        if p.is_dir():
            n += 1
        elif p.is_file():
            if apply_k12 and k12_dropped(rel):
                continue
            n += 1
    return n


def repo_scan(repo: Path, max_bytes: int, quiet: bool, max_entries: int = MAX_ENTRIES_DEFAULT) -> int:
    """CI 用：仓内没有现成 zip，就按**渠道老配方**（剔 fixtures/｜tests/）从工作树各建一枚再判。
    对象是「树构建出的 A 态字节」，不是渠道供体——渠道真字节仍须用 `check_shipment.py <zip> --repo <包>` 现验。"""
    bad, good, over = [], 0, []
    for pkg in sorted(d for d in repo.iterdir() if (d / "SKILL.md").is_file()):
        z = mk_tmp("cs-scan-") / f"{pkg.name}.zip"
        dropped = []
        build_zip(z, pkg, include_fixtures=False, sink=dropped)
        hits, notes, _ = check(z, pkg.name, None, max_bytes, True, pkg, max_entries)
        errs = [h for h in dedupe(hits) if h.sev == "ERROR"]
        rc = emit(z, pkg.name, hits, notes, quiet)
        n_size = sum(1 for h in errs if h.code == "S-SIZE")
        n_ptr = sum(1 for h in errs if h.code == "S-MISSING")
        n_run = sum(1 for h in errs if h.code == "S-SELFTEST")
        n_cnt = sum(1 for h in errs if h.code == "S-COUNT")
        eb, ea = predict_entries(pkg, True), predict_entries(pkg, False)
        if eb > max_entries:
            over.append((pkg.name, eb))
        k12 = sorted({d.split(":")[0] for d in dropped})
        if not quiet:
            print(f"    剔形制：{('、'.join(k12) or '无')}（本包剔 {len(dropped)} 件）"
                  f"｜分列：指路 {n_ptr}／真跑 {n_run}／体积 {n_size}／条目 {n_cnt}"
                  f"｜条目现数（K-20 前置，zip -r 形制含目录条目）：随包态 {eb}／剔样态 {ea}／限 {max_entries}")
        if rc:
            bad.append((pkg.name, len(errs), f"指路{n_ptr}·真跑{n_run}·体积{n_size}·条目{n_cnt}"))
        else:
            good += 1
        z.unlink(missing_ok=True)
    print(f"repo-scan：{good} 枚已过，{len(bad)} 枚发红（体积闸与指路红分列，见各包「分列」行）"
          + ("".join(f"（{n}:{c} 条｜{br}）" for n, c, br in bad) if bad else ""))
    if over:
        print("    条数预警（K-20：渠道 ≤%d，**加夹具前先数**）：%s"
              % (max_entries, "、".join(f"{n} 随包态 {e}" for n, e in sorted(over, key=lambda x: -x[1]))))
    return 1 if bad else 0


def main() -> int:
    ap = argparse.ArgumentParser(description="发布物自跑闸（K-17）：指路存在性／自测真跑／体积按 zip 字节")
    ap.add_argument("target", nargs="?", help="发布物：zip 或已解包目录")
    ap.add_argument("--pkg", help="包名（缺省取目标名）")
    ap.add_argument("--zip", dest="channel", help="渠道回下载的那份 zip，对同一套判定再跑一遍")
    ap.add_argument("--max-bytes", type=int, default=MAX_BYTES_DEFAULT, help="体积闸（默认 1,048,576 B）")
    ap.add_argument("--max-entries", type=int, default=MAX_ENTRIES_DEFAULT,
                    help="条数闸（默认 200 条目；渠道按**全部条目计，目录条目照计**——K-20）")
    ap.add_argument("--quiet", action="store_true", help="只报汇总与码表")
    ap.add_argument("--selftest", action="store_true", help="跑四档守护样＋双跑确定性")
    ap.add_argument("--repo-scan", metavar="仓根", nargs="?", const=".", help="CI 用：按渠道老配方从工作树逐包建 zip 再判（报账态起步）")
    ap.add_argument("--repo", help="仓内该包目录（可选）：给每条 S-MISSING 补一句分诊——属打包排除还是指路写错")
    ap.add_argument("--keep-tmp", action="store_true",
                    help="保留本闸自建的临时目录并打印其路径（默认退出时清理；要留就明说）")
    ap.add_argument("--list", action="store_true", help="列判定码")
    args = ap.parse_args()

    global _KEEP_TMP
    _KEEP_TMP = bool(getattr(args, "keep_tmp", False))

    if args.list:
        for c, spec in CODE_LEGEND.items():
            print(f"{c:11} {spec}")
        print(f"\n体积闸现值：{MAX_BYTES_DEFAULT:,} B（对象＝发布物 zip 字节）；自测真跑超时 {SELFTEST_TIMEOUT} s")
        print(f"条数闸现值：{MAX_ENTRIES_DEFAULT:,} 条目（对象＝zip 全部条目，**目录条目照计**；渠道 400 实测口径）")
        print(f"守护样目录：{FIXTURES}")
        return 0
    if args.selftest:
        return selftest(args.quiet)
    if args.repo_scan:
        return repo_scan(Path(args.repo_scan).resolve(), args.max_bytes, args.quiet, args.max_entries)
    if not args.target:
        print("check_shipment: 要给发布物路径（zip 或已解包目录），或用 --selftest / --list / --help", file=sys.stderr)
        return 1
    t = Path(args.target)
    pkg = args.pkg or t.name
    hits, notes, _ = check(t, pkg, Path(args.channel) if args.channel else None, args.max_bytes, args.quiet,
                           Path(args.repo) if args.repo else None, args.max_entries)
    rc = emit(t, pkg, hits, notes, args.quiet)
    sys.stdout.flush()
    return rc


if __name__ == "__main__":
    sys.exit(main())
