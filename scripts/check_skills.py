#!/usr/bin/env python3
"""Repo lint for cue-awesome — run before you commit, and again in CI.

Also enforces one shape rule over markdown table rows: where a row carries both a
status clause and a provenance clause, status must come first (readers scan row
ends). The rule self-tests on every run, so it cannot pass by matching nothing.

Also enforces the face length caps from CONTRIBUTING 门面四问② (summary <=80,
description <=300). The measured object is the **parsed frontmatter value**, not the
raw quoted YAML line; the difference is exactly two quote characters and judging the
raw line false-reds four real faces. Both caps boundary-check themselves on every run
(exact value must stay green, value+1 must go red), so a `>` written as `>=` cannot
hide behind a green repo.

Stdlib only (PyYAML is used when available, otherwise a minimal fallback
parser handles the flat frontmatter keys we care about).

Usage:
    python scripts/check_skills.py            # errors + warnings
    python scripts/check_skills.py --strict   # warnings become errors
    python scripts/check_skills.py --quiet    # only the summary
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# top-level dirs that are NOT skills
NON_SKILL_DIRS = {".github", "docs", "scripts", "assets", ".git", ".workbuddy"}

# files that must never be committed
SECRET_PATTERNS = (
    ".env",
    ".env.*",
    "*.token",
    "*secret*",
    "*credential*",
    "*.pem",
    "*.key",
    "id_rsa",
    "id_ed25519",
)
ARTIFACT_PATTERNS = ("*.zip", "*.pyc")
ARTIFACT_DIRS = {"__pycache__", "dist", "build", "node_modules", ".venv"}

SEMVER = re.compile(r"^\d+\.\d+\.\d+$")

# ------------------------------------------------------- 门面长度帽（M235）
# CONTRIBUTING.md「门面四问」② 立着帽：`summary` ≤80、`description` ≤300，且明写
# 「长度必须脚本实测（wc -m 式，禁手数）」——纸上有条、脚本不判，就是 C-54 那一族。
# **量的对象（lead 要我自己定形并测一次）＝frontmatter 解析后的值**（去引号、转义还原），
# 不是含引号的 YAML 原始行。实测根据：按原始行判会假红 4 处——cue-lead-pieces 的
# description 解析 300／原始 302（SKILL.md 与 SKILL.en.md 各一处）、cue-omni-ontology 的
# summary 解析 79／原始 81（两处）。帽管的是读者看到的文案长度；引号属 YAML 语法。
CAP_SUMMARY = 80
CAP_DESCRIPTION = 300
CAP_OBJECT = "解析后的值（非含引号原始行）"
CAP_OBS: list[tuple[int, str]] = []      # 脚本自报用：[(长度, 包/面/键)]，不另立文档计数


def length_cap_violations(fm: dict | None) -> list[tuple[str, int, int]]:
    """返回 [(键, 现值长度, 帽)]。键缺失不判（必需性另有判据），帽只判「超长」。"""
    out: list[tuple[str, int, int]] = []
    if not isinstance(fm, dict):
        return out
    for key, cap in (("summary", CAP_SUMMARY), ("description", CAP_DESCRIPTION)):
        val = fm.get(key)
        if val is None:
            continue
        n = len(str(val))
        if n > cap:
            out.append((key, n, cap))
    return out

# --------------------------------------------------------- table row order rule
# Readers scan a table row from the end, so a status clause must come BEFORE the
# provenance clause in the same row; otherwise the last thing they see is a link,
# not the state. Rule is shape-only (marker families), never content judgement.
# Marker families are constants, not a search: reword a README clause and edit the matching family here, or the row silently stops being covered.
STATUS_CLAUSE = ("status section", "状态段")
PROVENANCE_CLAUSE = ("Base provenance:", "基座出处见")
SKIP_DIRS = ARTIFACT_DIRS | {"fixtures"}


def row_clause_positions(line: str) -> tuple[int, int] | None:
    """Return (status_idx, provenance_idx) when a row carries both clauses, else None."""
    if not line.startswith("| ["):
        return None
    hits_s = [line.index(m) for m in STATUS_CLAUSE if m in line]
    hits_p = [line.index(m) for m in PROVENANCE_CLAUSE if m in line]
    if not hits_s or not hits_p:
        return None
    return min(hits_s), min(hits_p)


def check_table_row_order(rep: Report) -> tuple[int, int]:
    """Scan every markdown table row in the repo; status clause must precede provenance."""
    checked = violations = 0
    for path in sorted(ROOT.rglob("*.md")):
        if set(path.relative_to(ROOT).parts[:-1]) & SKIP_DIRS:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        rel = path.relative_to(ROOT)
        for lineno, line in enumerate(text.split("\n"), 1):
            positions = row_clause_positions(line)
            if positions is None:
                continue
            checked += 1
            s, p = positions
            if s > p:
                violations += 1
                rep.error(
                    f"repo: {rel}:{lineno} provenance clause (col {p}) precedes the "
                    f"status clause (col {s}) — status must come first in a table row"
                )
    return checked, violations


def selftest_row_order_rule(rep: Report) -> bool:
    """The rule must fire on a reversed row and stay silent on a correct one.

    Without both directions a green lint proves nothing (a vacuous check is green).
    """
    provenance = "Base provenance: see [NOTICE.md](NOTICE.md) §financial-suite."
    status = "**Run on record — counts in this package's README status section.**"
    good = f"| [`demo/`](demo/) | demo | 0.1.0 | Description. {status} {provenance} |"
    bad = f"| [`demo/`](demo/) | demo | 0.1.0 | Description. {provenance} {status} |"
    both_seen = row_clause_positions(good) is not None and row_clause_positions(bad) is not None
    ok = both_seen and row_clause_positions(good)[0] < row_clause_positions(good)[1] \
        and row_clause_positions(bad)[0] > row_clause_positions(bad)[1]
    if not ok:
        rep.error(
            "repo: row-order self-test failed — the rule did not separate the reversed "
            "sample from the correct one, so a green run would be meaningless"
        )
    return ok



# ---------------------------------------------------------------- frontmatter
def parse_frontmatter(path: Path) -> dict | None:
    text = path.read_text(encoding="utf-8", errors="replace")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
    if not m:
        return None
    raw = m.group(1)
    try:
        import yaml  # type: ignore

        data = yaml.safe_load(raw)
        return data if isinstance(data, dict) else {}
    except Exception:
        pass
    # minimal fallback: `key: value` pairs plus one level of nesting
    # (enough for `metadata: { version: "1.2.0" }`; list items are ignored)
    data: dict = {}
    current: str | None = None
    for line in raw.splitlines():
        if not line.strip():
            continue
        top = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if top:
            current = top.group(1)
            data[current] = top.group(2).strip().strip("\"'")
            continue
        nested = re.match(r"^\s+([A-Za-z_][\w-]*):\s*(.*)$", line)
        if nested and current:
            if not isinstance(data.get(current), dict):
                data[current] = {}
            data[current][nested.group(1)] = nested.group(2).strip().strip("\"'")
    return data


def version_of(fm: dict) -> str | None:
    v = fm.get("version")
    if v is None:
        meta = fm.get("metadata")
        if isinstance(meta, dict):
            v = meta.get("version")
    return str(v) if v is not None else None


# ---------------------------------------------------------------- checks
class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)


def check_skill(skill_dir: Path, rep: Report) -> None:
    name = skill_dir.name
    skill_md = skill_dir / "SKILL.md"

    if not skill_md.is_file():
        rep.error(f"{name}: missing SKILL.md (a skill dir must have one)")
        return

    fm = parse_frontmatter(skill_md)
    if fm is None:
        rep.error(f"{name}: SKILL.md has no YAML frontmatter block")
        return

    # --- required fields ---
    fm_name = fm.get("name")
    if not fm_name:
        rep.error(f"{name}: frontmatter missing `name`")
    elif str(fm_name) != name:
        rep.error(f"{name}: frontmatter `name`={fm_name!r} must equal the directory name")

    if not (fm.get("description") or fm.get("summary")):
        rep.error(f"{name}: frontmatter needs `description` (or `summary`) with trigger words")

    version = version_of(fm)
    if not version:
        rep.error(f"{name}: frontmatter missing `version` (top level or metadata.version)")
    elif not SEMVER.match(version):
        rep.error(f"{name}: version {version!r} is not x.y.z")

    # single-source version rule: a nested `metadata.version` is a second
    # authority that naive line-based consumers (e.g. skillhub CLI) read as
    # the real version -- last-wins silently ships stale numbers.
    try:
        _fm_text = skill_md.read_text(encoding="utf-8").split("---", 2)[1]
    except Exception:
        _fm_text = ""
    import re as _re
    if _re.search(r"^\s{2,}version:", _fm_text, _re.M):
        rep.error(f"{name}: nested metadata.version found in frontmatter -- keep ONE version key at top level "
                  "(flat parsers let the last line silently overwrite the real one)")

    # --- README ---
    if not (skill_dir / "README.md").is_file():
        rep.error(f"{name}: missing README.md")

    # --- bilingual pairs ---
    for stem in ("SKILL", "README"):
        base = skill_dir / f"{stem}.md"
        for suffix in ("zh-CN", "en"):
            twin = skill_dir / f"{stem}.{suffix}.md"
            if twin.is_file():
                if not base.is_file():
                    rep.error(f"{name}: {twin.name} exists but {stem}.md does not")
                if stem == "SKILL":
                    twin_fm = parse_frontmatter(twin)
                    if twin_fm is None:
                        rep.error(f"{name}: {twin.name} has no frontmatter")
                    else:
                        for key in ("name",):
                            if str(twin_fm.get(key)) != str(fm.get(key)):
                                rep.error(
                                    f"{name}: {twin.name} frontmatter `{key}`="
                                    f"{twin_fm.get(key)!r} != SKILL.md {fm.get(key)!r}"
                                )
                        if version_of(twin_fm) != version:
                            rep.error(
                                f"{name}: {twin.name} version {version_of(twin_fm)!r} "
                                f"!= SKILL.md version {version!r}"
                            )

    # --- CHANGELOG alignment ---
    changelog = skill_dir / "CHANGELOG.md"
    if changelog.is_file() and version:
        top = None
        for ln in changelog.read_text(encoding="utf-8", errors="replace").splitlines():
            m = re.match(r"^#{1,3}\s*\[?v?(\d+\.\d+\.\d+)", ln)
            if m:
                top = m.group(1)
                break  # first version heading = newest entry
        if top and top != version:
            rep.warn(f"{name}: CHANGELOG.md newest entry is {top}, but SKILL.md says {version}")

    # --- manifest.yaml ↔ frontmatter version (M171) ---
    # ERROR, not WARN: the manifest is the distribution toolchain's machine-read
    # version; a split from the authoritative frontmatter is credential drift —
    # precedent: long-doc manifest 1.3.0 vs SKILL 1.3.6 (lead hotfixed 680f079).
    # Machine-read surfaces have no legitimate mid-flight state (WARN-grade is
    # for human docs 「顺手对齐」-class only); missing version key = unverifiable
    # distribution claim, same family, also ERROR.
    manifest = skill_dir / "manifest.yaml"
    if manifest.is_file():
        mtext = manifest.read_text(encoding="utf-8", errors="replace")
        mm = re.search(r"^version:\s*[\"']?([0-9][^\"\n]*?)[\"']?\s*$", mtext, re.M)
        if not mm:
            rep.error(f"{name}: manifest.yaml has no top-level `version:` — 分发机读面无从对账,视同漂移")
        elif version and mm.group(1) != version:
            rep.error(f"{name}: manifest.yaml version {mm.group(1)!r} != SKILL.md frontmatter {version!r} "
                      f"— 分发面与权威面漂号(M171;判例 long-doc 1.3.0 vs 1.3.6/680f079),两处必须同号")

    # --- CHANGELOG head shape (M161; CONTRIBUTING §frontmatter-adjacent rule
    # 「首条即版本条」). ERROR, not WARN: a broken head is silent corruption —
    # the newest entry is the release index readers actually land on, and unlike
    # version alignment there is no legitimate mid-flight state for a shell or a
    # bare first line (M150 truncation proved nothing flags it otherwise).
    if changelog.is_file():
        text = changelog.read_text(encoding="utf-8", errors="replace")
        entries = [ln for ln in text.splitlines() if ln.startswith("### ")]
        if not entries:
            rep.error(f"{name}: CHANGELOG.md has no '### x.y.z' entry line — 禁裸标题/无条目")
        elif not re.match(r"^### \d+\.\d+\.\d+", entries[0]):
            rep.error(f"{name}: CHANGELOG.md first entry {entries[0][:40]!r} must be "
                      f"'### x.y.z' — 禁 Unreleased 壳、禁裸标题(首条即版本条)")
        for ln in text.splitlines():
            if re.match(r"^#{2,3}\s*\[?Unreleased", ln):
                rep.error(f"{name}: CHANGELOG.md carries an Unreleased shell heading — "
                          f"随下趟车收口壳禁入文件(首条即版本条)")
                break

    # --- 门面长度帽（M235；CONTRIBUTING 门面四问②）：逐面判 SKILL*.md 的 summary/description ---
    for face in sorted(skill_dir.glob("SKILL*.md")):
        fmx = parse_frontmatter(face)
        if not isinstance(fmx, dict):
            continue
        for key in ("summary", "description"):
            v = fmx.get(key)
            if v is not None:
                CAP_OBS.append((len(str(v)), f"{name}/{face.name}/{key}"))
        for key, n, cap in length_cap_violations(fmx):
            rep.error(f"{name}: {face.name} 的 `{key}` 长 {n} ＞ 帽 {cap}"
                      f"（CONTRIBUTING 门面四问②；量＝{CAP_OBJECT}）")

    # --- forbidden files ---
    if (skill_dir / ".git").exists():
        rep.error(f"{name}: nested .git directory — skills must not carry their own repo")

    for path in skill_dir.rglob("*"):
        rel = path.relative_to(skill_dir)
        parts = set(rel.parts)
        if parts & ARTIFACT_DIRS:
            rep.error(f"{name}: committed build artifact dir {rel}")
            continue
        low = path.name.lower()
        if any(
            low == p.lower() or (p.startswith("*") and low.endswith(p.strip("*").lower()))
            for p in SECRET_PATTERNS
        ):
            rep.error(f"{name}: possible secret file {rel}")
        if any(path.name.lower().endswith(p.strip("*").lstrip(".")) for p in ARTIFACT_PATTERNS if p.startswith("*")):
            rep.error(f"{name}: committed artifact {rel}")


def selftest_length_caps(rep: Report) -> bool:
    """边界双判：恰值必绿、超一枚必红（防 `>` 与 `>=` 写反，防判据空跑）。
       正反两形都走**生产函数** check_skill()，所以「发红且点到包名」这条也是测出来的。
       临时件建在系统 tmp、不落仓：仓里放一枚假 skill 会被别的扫描当真（卫生闸、上架条数字段）。"""
    import shutil
    import tempfile

    ok, forms = True, 0                                      # 自报判过的形数（档数以脚本自报为准，文档不另数）
    saved = list(CAP_OBS)                    # 自报计数不含自测件，避免把 demo 算进全仓现值
    try:
        for key in ("description", "summary"):
            cap = CAP_DESCRIPTION if key == "description" else CAP_SUMMARY
            for delta, want_err in ((0, False), (1, True)):
                tmp = Path(tempfile.mkdtemp(prefix="cs-caps-"))
                try:
                    skill = tmp / "demo"
                    skill.mkdir()
                    fm = {"name": "demo", "version": "1.2.3",
                          "summary": "s" * (cap + delta if key == "summary" else 10),
                          "description": "d" * (cap + delta if key == "description" else 10)}
                    body = "---\n" + "\n".join(f'{k}: "{v}"' for k, v in fm.items()) + "\n---\n\n# demo\n"
                    (skill / "SKILL.md").write_text(body, encoding="utf-8")
                    (skill / "README.md").write_text("# demo\n", encoding="utf-8")
                    sub = Report()
                    check_skill(skill, sub)
                    got = [m for m in sub.errors if "＞ 帽" in m]
                    if want_err and (len(got) != 1 or not got[0].startswith("demo:")):
                        ok = False
                        rep.error(f"repo: 长度帽自测失败——{key}={cap + delta}（帽 {cap}＋1）应发红并点到包名，"
                                  f"实得 {len(got)} 条 {got[:1]}")
                    if not want_err and got:
                        ok = False
                        rep.error(f"repo: 长度帽自测失败——{key}={cap}（恰值）不该红，实发红 {got[:1]}")
                    forms += 1
                finally:
                    shutil.rmtree(tmp, ignore_errors=True)
    finally:
        CAP_OBS[:] = saved
    return ok, forms


def discover_skills() -> list[Path]:
    return sorted(
        d
        for d in ROOT.iterdir()
        if d.is_dir() and d.name not in NON_SKILL_DIRS and not d.name.startswith(".")
    )


def main() -> int:
    ap = argparse.ArgumentParser(description="Lint all skills in cue-awesome")
    ap.add_argument("--strict", action="store_true", help="treat warnings as errors")
    ap.add_argument("--quiet", action="store_true", help="print only the summary")
    args = ap.parse_args()

    rep = Report()
    # repo-level files
    for required in ("README.md", "LICENSE.md", "CONTRIBUTING.md"):
        if not (ROOT / required).is_file():
            rep.warn(f"repo: missing {required}")

    repo_rep = Report()
    selftest_ok = selftest_row_order_rule(repo_rep)
    caps_ok, caps_forms = selftest_length_caps(repo_rep)
    rows_checked, row_violations = check_table_row_order(repo_rep)
    rep.errors.extend(repo_rep.errors)
    rep.warnings.extend(repo_rep.warnings)

    skills = discover_skills()
    if not skills:
        rep.error("repo: no skill directories found")

    per_skill: dict[str, Report] = {}
    for d in skills:
        sub = Report()
        check_skill(d, sub)
        per_skill[d.name] = sub
        rep.errors.extend(sub.errors)
        rep.warnings.extend(sub.warnings)

    if not args.quiet:
        print(f"cue-awesome skill lint — {len(skills)} skill(s)\n")
        for d in skills:
            sub = per_skill[d.name]
            fm = parse_frontmatter(d / "SKILL.md") if (d / "SKILL.md").is_file() else None
            ver = version_of(fm) if isinstance(fm, dict) else None
            status = "FAIL" if sub.errors else ("WARN" if sub.warnings else "OK")
            print(f"  {status:<4} {d.name:<24} v{ver or '?'}")
            for msg in sub.errors + sub.warnings:
                print(f"        {msg}")
        status = "FAIL" if repo_rep.errors else ("WARN" if repo_rep.warnings else "OK")
        print(f"  {status:<4} {'table row order':<24} self-test={'ok' if selftest_ok else 'FAILED'}")
        print(f"        rows with status+provenance: {rows_checked} checked, {row_violations} mis-ordered")
        caps_status = "ok" if caps_ok else "FAILED"
        n_forms = caps_forms
        hi_s = max([n for n, w in CAP_OBS if w.endswith("/summary")] or [0])
        hi_d = max([n for n, w in CAP_OBS if w.endswith("/description")] or [0])
        print(f"  {('FAIL' if not caps_ok else 'OK'):<4} {'face length caps':<24} self-test={caps_status}"
              f"  帽 summary<={CAP_SUMMARY}／description<={CAP_DESCRIPTION}｜量＝{CAP_OBJECT}"
              f"｜自测 {n_forms} 形（两帽各双判：恰值绿／＋1 红）")
        print(f"        自报现值最高：summary={hi_s}／description={hi_d}"
              f"（判过 {len(CAP_OBS)} 个 面×键；计数只在此行，文档不另数）")
        for msg in repo_rep.errors + repo_rep.warnings:
            print(f"        {msg}")

    total_err = len(rep.errors)
    total_warn = len(rep.warnings)
    print(f"\nsummary: {len(skills)} skill(s), {total_err} error(s), {total_warn} warning(s)")

    if total_err:
        return 1
    if args.strict and total_warn:
        print("--strict: warnings promoted to errors")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
