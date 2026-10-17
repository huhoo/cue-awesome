#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""run_fixtures.py — M243 的构建产物「跟踪态」四档自测（可手跑，也被 check_skills.py --selftest 调）。

    python3 scripts/fixtures/skills/run_fixtures.py            # 跑四档，全绿退 0
    python3 scripts/fixtures/skills/run_fixtures.py -v         # 附每档的原文

形制约束：
- 全程在 `mktemp -d` 里造**一次性 git 仓**，主仓只被读、不被写（本文件不执行任何主仓 git 写）；
- 四档必须含「防恒真」那一档：没有缓存的包不得冒出任何一条——否则前三档逢样必红，等于没判。
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent))          # 仓内 scripts/
import check_skills as cs                            # noqa: E402

PYC = "scripts/__pycache__/_x.cpython-312.pyc"


def _git(repo: Path, *args) -> int:
    return subprocess.run(["git", "-c", "user.email=selftest@local", "-c", "user.name=selftest",
                           "-c", "commit.gpgsign=false", *args],
                          cwd=str(repo), capture_output=True, timeout=120).returncode


def make_pkg(root: Path, name: str, with_cache: bool, tracked: bool) -> Path:
    pkg = root / name
    (pkg / "scripts").mkdir(parents=True)
    (pkg / "SKILL.md").write_text(
        f"---\nname: {name}\nversion: \"1.0.0\"\nsummary: \"自测用最小包形。\"\n"
        f"description: \"自测用最小包形，不含票号与内部路径。\"\nlicense: MIT\n---\n\n# {name}\n\n本包只服务自测。\n",
        encoding="utf-8")
    (pkg / "README.md").write_text(f"# {name}\n\n第一次进入：跑 `python3 scripts/check_skills.py`。\n", encoding="utf-8")
    if with_cache:
        f = pkg / PYC
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(b"\x00fake-bytecode")
        if tracked:
            _git(root, "add", "-f", "--", f.relative_to(root).as_posix())
    return pkg


def build_repo(tmp: Path, with_git: bool = True) -> Path:
    repo = tmp / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / ".gitignore").write_text("# Python\n__pycache__/\n*.py[cod]\n", encoding="utf-8")
    if with_git:
        repo.mkdir(parents=True, exist_ok=True)
        if _git(repo, "init", "-q") != 0:
            raise RuntimeError("一次性仓 git init 失败（自测环境无 git，见档④说明）")
    return repo


def findings(pkg: Path) -> tuple[list[str], list[str]]:
    rep = cs.Report()
    cs.check_skill(pkg, rep)
    keep = lambda ms: [m for m in ms if ("缓存" in m or "artifact" in m)]     # noqa: E731
    return keep(rep.errors), keep(rep.warnings)


def run(verbose: bool = False) -> int:
    ok = True
    tmp = Path(tempfile.mkdtemp(prefix="cs-artifact-"))
    try:
        # ---- 档①：真已跟踪的构建产物＝ERROR，且附 git ls-files 命中数
        r1 = build_repo(tmp / "t1")
        p_tracked = make_pkg(r1, "pkg-tracked", with_cache=True, tracked=True)
        make_pkg(r1, "pkg-clean", with_cache=False, tracked=False)
        _git(r1, "add", "-A")
        _git(r1, "commit", "-q", "-m", "fixture")
        e1, w1 = findings(p_tracked)
        has_count = any("命中 1 枚" in m for m in e1)
        good1 = len(e1) == 1 and has_count and not w1
        print(f"档① 真已跟踪＝ERROR：发红 {len(e1)} 条、附命中数＝{'是' if has_count else '否'}、WARN {len(w1)} 条"
              f"＝{'对' if good1 else '错'}")
        if verbose or not good1:
            print("   原文:", (e1 + w1)[:2])
        ok = ok and good1

        # ---- 档②：在盘未跟踪（被 ignore）＝WARN，不得冒 ERROR，句子给清理命令
        r2 = build_repo(tmp / "t2")
        p_untracked = make_pkg(r2, "pkg-untracked", with_cache=True, tracked=False)
        _git(r2, "add", "-A")
        _git(r2, "commit", "-q", "-m", "fixture")
        e2, w2 = findings(p_untracked)
        good2 = (not e2) and len(w2) >= 1 and all(cs.ARTIFACT_CLEAN_CMD in m for m in w2) \
            and all(("未跟踪" in m) for m in w2)
        print(f"档② 未跟踪＝WARN 不冒 ERROR：ERROR {len(e2)} 条、WARN {len(w2)} 条、含清理命令＝"
              f"{'是' if all(cs.ARTIFACT_CLEAN_CMD in m for m in w2) else '否'}＝{'对' if good2 else '错'}")
        if verbose or not good2:
            print("   原文:", (e2 + w2)[:2])
        ok = ok and good2

        # ---- 档③：无 git 环境不得抛 Traceback，且报「跟踪态不可判」
        r3 = build_repo(tmp / "t3", with_git=False)
        p_nogit = make_pkg(r3, "pkg-nogit", with_cache=True, tracked=False)
        try:
            e3, w3 = findings(p_nogit)
            crashed = False
        except Exception as exc:                                   # noqa: BLE001
            e3, w3, crashed = [], [f"Traceback: {type(exc).__name__}: {exc}"], True
        good3 = (not crashed) and (not e3) and len(w3) >= 1 and all("不可判" in m for m in w3)
        print(f"档③ 无 git 不炸：异常＝{'有' if crashed else '无'}、ERROR {len(e3)} 条、"
              f"「不可判」句 {len([m for m in w3 if '不可判' in m])} 条＝{'对' if good3 else '错'}")
        if verbose or not good3:
            print("   原文:", (e3 + w3)[:2])
        ok = ok and good3

        # ---- 档④：防恒真——无缓存的包一条都不该冒
        e4, w4 = findings(p_tracked.parent / "pkg-clean")
        good4 = not e4 and not w4
        print(f"档④ 防恒真（无缓存样）：ERROR {len(e4)} 条／WARN {len(w4)} 条，期望 0/0＝{'对' if good4 else '错（判据逢样必红）'}")
        ok = ok and good4

        # ---- 档⑤／档⑥（M243 追加条，lead 裁：`--strict` 不因在盘未跟踪缓存升败，但既有 WARN 一字不动）
        rep5 = cs.Report()
        cs.check_skill(p_untracked, rep5)
        rc5_strict = cs.decide_exit(rep5, True)
        good5 = rc5_strict == 0 and len(rep5.warnings) == 1 and rep5.no_strengthen == set(rep5.warnings)
        print(f"档⑤ 未跟踪缓存不升败：`--strict` 退码 {rc5_strict}（期望 0）、WARN 仍报 {len(rep5.warnings)} 条、"
              f"标记为不升败 {len(rep5.no_strengthen)} 条＝{'对' if good5 else '错'}")
        if verbose or not good5:
            print("   原文:", rep5.warnings[:1])
        ok = ok and good5

        rep6 = cs.Report()
        p_warn = make_pkg(build_repo(tmp / "t6"), "pkg-stale-changelog", with_cache=False, tracked=False)
        (p_warn / "CHANGELOG.md").write_text("### 0.9.0 — 首条版本条与门面不符（自测用）\n\n- 只服务档⑥。\n",
                                             encoding="utf-8")
        cs.check_skill(p_warn, rep6)
        rc6_loose, rc6_strict2 = cs.decide_exit(rep6, False), cs.decide_exit(rep6, True)
        existing = [w for w in rep6.warnings if w not in rep6.no_strengthen]
        good6 = bool(existing) and rc6_loose == 0 and rc6_strict2 == 1
        print(f"档⑥ 既有 WARN 照旧升败：可升败 WARN {len(existing)} 条、非 strict {rc6_loose}（期望 0）／"
              f"strict {rc6_strict2}（期望 1）＝{'对' if good6 else '错（裁语被做过头了）'}")
        if verbose or not good6:
            print("   原文:", existing[:1])
        ok = ok and good6
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"selftest: {'ALL GREEN（三态分开、防恒真档在场、strict 分档按裁落地）' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="构建产物跟踪态四档自测（一次性仓，主仓只读）")
    ap.add_argument("-v", "--verbose", action="store_true", help="附每档原文")
    sys.exit(run(verbose=ap.parse_args().verbose))
