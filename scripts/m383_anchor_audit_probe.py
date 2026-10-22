#!/usr/bin/env python3
"""m383_anchor_audit_probe.py｜出处回查审计尺：落进 facts 的每条出处都必须在同批来源索引里对得上，且反方／缺数两处判定只按可校验形状。

一条命令重跑：TMPDIR=/tmp python3 -B scripts/m383_anchor_audit_probe.py [--intake <path>] [--prefix <改前快照 path>]
  被测件＝ic-memo-cn/scripts/upstream_intake.py（--intake 可换）。给了 --prefix（改动前的快照）就打两头值，没给就只打现值——
  **绝不把「没跑那一支」印成 0**；给了快照而某枚靶在快照上也是绿的，本尺判它「不算靶」（它没量到被修的那件事）。
  索引的取数式**不自己重写**：直接 import 被测那一份 intake 的 ledger_from_jsonl／ledger_from_index——
  同一事实两处真值迟早对不上（这条是她今天刚收进去的族），审计尺自己写一套取数就是第二个真值源。

三枚必红靶（承 6.1 的 M379-1／-2／-3）：
  靶甲 伪造出处夹带：risk-fact-table 的表里多写一行，来源列是一个索引里查无此号的 URL ⇒ 该条必须被跳过并计入回查不到，facts 里不得出现那个串。
  靶乙 反方按形状不按节名：structured-note 的「附注风险扫描」节里放一行非六项科目的数字行（预收款项），另在同一份文档里放一行六项科目但落在别处
       ⇒ 前者不得落 bear、后者必须落 bear（两头都断言，只断一头等于没断）。
  靶丙 缺数账不得吞掉有效事实：一条 bullet 同时含「未取到」字样、数字与可回查锚 ⇒ 必须落成 facts，不得被缺数账吞走。
  再加一条通名不变量：现役三枚夹具各跑一次，facts 里每行的 source 都必须在同批索引里找得到对应 ref。
退码：0 全合；1 有不合（逐条点名）；3 取值域故障（脚本／夹具／快照取不到，或 import 不上被测件——不读成「零违例」）。
形制：纯标准库、零网络、只读；产物只落临时目录、跑完即删；输出只打相对路径。
"""

import argparse
import importlib.util
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
GATE = "https://evil.example/fake-ann-999999"
KINDS = {"tear-sheet-page": "tear-sheet", "structured-note": "note", "risk-fact-table": "risk-table"}


def load_mod(path, name):
    spec = importlib.util.spec_from_file_location(name, str(path))
    if spec is None or spec.loader is None:
        return None
    m = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(m)
    except Exception as exc:  # 取值域故障：读不通就是读不通
        print("3 取值域故障：import 被测件失败 %s（%s）" % (path, exc))
        return None
    return m


def run(intake, kind, artifact, sources, bull, outdir):
    args = [sys.executable, "-B", str(intake), "--kind", kind, "--artifact", str(artifact), "--out-dir", str(outdir)]
    if sources:
        args += ["--sources", str(sources)]
    if bull:
        args += ["--manual-bull", str(bull)]
    r = subprocess.run(args, capture_output=True, text=True, cwd=str(REPO))
    rows, gaps = [], []
    for fn, bag in (("facts.jsonl", rows), ("gaps.jsonl", gaps)):
        fp = Path(outdir) / fn
        if fp.exists():
            bag.extend(json.loads(l) for l in fp.read_text(encoding="utf-8").splitlines() if l.strip())
    return r.returncode, r.stdout + r.stderr, rows, gaps


def refs_of(mod, artifact, src):
    """可回查出处的两个来路分开取：同批来源索引（机器给的那条腿）与 --manual-bull（人工并进来的那几条，出处由人给、不经索引）。
    两类各自数出来报，别让「人工」那一桶把真泄漏盖掉——人工桶里只该出现人工并来那几条。"""
    led = mod.ledger_from_jsonl(str(src)) if src else {}
    led.update(mod.ledger_from_index(Path(artifact).read_text(encoding="utf-8", errors="ignore")))
    idx = {(v.get("ref") or "").strip() for v in led.values()} - {""}
    return idx


def manual_srcs(path):
    out = set()
    if not path or not Path(path).exists():
        return out
    for ln in Path(path).read_text(encoding="utf-8").splitlines():
        ln = ln.strip()
        if not ln:
            continue
        try:
            o = json.loads(ln)
        except ValueError:
            continue
        if o.get("source"):
            out.add(str(o["source"]).strip())
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--intake", default=str(REPO / "ic-memo-cn/scripts/upstream_intake.py"))
    ap.add_argument("--prefix", help="改动前的 intake 快照；给了就打两头值，并检查每枚靶在快照上确实发红")
    a = ap.parse_args()
    intake = Path(a.intake)
    if not intake.is_file():
        print("3 取值域故障：取不到被测 intake %s（不读成「零违例」）" % intake)
        return 3
    pre = Path(a.prefix) if a.prefix else None
    if pre and not pre.is_file():
        print("3 取值域故障：--prefix 指了路径却读不到 %s（两头值不因此算「修前＝0」）" % pre)
        return 3
    fx = REPO / "ic-memo-cn/scripts/fixtures/upstream"
    for p in (fx / "tear-sheet-page.md", fx / "tear-sheet-sources.jsonl", fx / "earnings-note.md",
              fx / "risk-report.md", fx / "risk-sources.jsonl", fx / "manual-bull-tear-sheet.jsonl",
              fx / "manual-bull-note.jsonl", fx / "manual-bull-risk-table.jsonl"):
        if not p.exists():
            print("3 取值域故障：取不到夹具 %s（不读成「零违例」）" % p.name)
            return 3
    mod_now = load_mod(intake, "intake_now")
    if mod_now is None:
        return 3
    mod_pre = load_mod(pre, "intake_pre") if pre else None
    if pre and mod_pre is None:
        return 3

    work = Path(tempfile.mkdtemp(prefix="m383-audit-"))
    bad, notes = [], []

    # —— 不变量：三枚现役夹具的每条 facts 出处都要在同批索引里 ——
    for kind, art, src in (("tear-sheet-page", fx / "tear-sheet-page.md", fx / "tear-sheet-sources.jsonl"),
                           ("structured-note", fx / "earnings-note.md", None),
                           ("risk-fact-table", fx / "risk-report.md", fx / "risk-sources.jsonl")):
        bull = fx / ("manual-bull-%s.jsonl" % KINDS[kind])
        rc, out, rows, gaps = run(intake, kind, art, src, bull, work / ("inv-" + kind))
        refs, msrc = refs_of(mod_now, art, src), manual_srcs(bull)
        stray, via_manual = [], 0
        for r in rows:
            s = r.get("source", "")
            if any(x in s for x in refs):
                continue
            if any(s and s == m for m in msrc):
                via_manual += 1
                continue
            stray.append(r)
        notes.append("%s：facts=%d 条｜索引对上 %d 条｜人工并来那几条=%d 条｜两处都对不上=%d 条｜intake rc=%d" % (
            kind, len(rows), len(rows) - len(stray) - via_manual, via_manual, len(stray), rc))
        for r in stray[:3]:
            bad.append("不变量 %s：facts 里的出处在索引与人工件里都找不到：%s（行：%s）" % (kind, r.get("source", "")[:56], r.get("item", "")[:36]))

    # —— 靶甲：把伪造一行插进 dd 表格的最后一行之后（表内，不是表外；表外的行本来就不会被读）——
    base = (fx / "risk-report.md").read_text(encoding="utf-8").split("\n")
    last = max(i for i, l in enumerate(base) if l.startswith("| 2026-"))
    base.insert(last + 1, "| 2026-06-01 | 合规与处罚 | 伪造一行测试靶，来源列写着索引里查无此号的 URL | 重大 | 已披露 | — | %s |" % GATE)
    forged = work / "risk-forged.md"
    forged.write_text("\n".join(base), encoding="utf-8")

    def shot_a(path, mod):
        rc, out, rows, gaps = run(path, "risk-fact-table", forged, fx / "risk-sources.jsonl",
                                  fx / "manual-bull-risk-table.jsonl", work / ("a-" + str(abs(hash(str(path))))))
        leak = [r for r in rows if GATE in r.get("source", "")]
        m = re.search(r"回查不到索引 (\d+) 处", out)
        return ("泄漏 %d 条｜自报回查不到=%s｜表内行被收 facts=%d 条" % (len(leak), m.group(1) if m else "未自报", len(rows)), len(leak) == 0)

    # —— 靶乙：非六项科目落在「附注风险扫描」节里不得成 bear；六项科目落在别处必须成 bear ——
    t = (fx / "earnings-note.md").read_text(encoding="utf-8")
    t = t.replace("- 受限货币资金 1.2 亿元 [L1] [S5]",
                  "- 受限货币资金 1.2 亿元 [L1] [S5]\n- 预收款项 0.9 亿元 [L1] [S5]")
    t = t.replace("- 管理层全年收入指引为同比增长 10% 以上 [L2] [S4]",
                  "- 合同负债余额 2.2 亿元，指引口径未拆 [L2] [S4]\n- 管理层全年收入指引为同比增长 10% 以上 [L2] [S4]")
    note2 = work / "note-shape.md"
    note2.write_text(t, encoding="utf-8")

    def shot_b(path, mod):
        rc, out, rows, gaps = run(path, "structured-note", note2, None,
                                  fx / "manual-bull-note.jsonl", work / ("b-" + str(abs(hash(str(path))))))
        adv = [r for r in rows if "预收款项" in r.get("item", "") and r.get("side") == "bear"]
        good = [r for r in rows if "合同负债" in r.get("item", "") and r.get("side") == "bear"]
        bear = sorted({r.get("item", "")[:6] for r in rows if r.get("side") == "bear"})
        return ("bear=%s｜风险节里的非六项科目成 bear＝%s｜六项科目在别处成 bear＝%s" % (bear, bool(adv), bool(good)), (not adv) and bool(good))

    # —— 靶丙：一条同时含未取到字样／数字／可回查锚的 bullet 必须落 facts ——
    t3 = (fx / "earnings-note.md").read_text(encoding="utf-8").replace(
        "- 管理层全年收入指引为同比增长 10% 以上 [L2] [S4]",
        "- 管理层称该业务未取到第三方风险评级前不并表，本期收入 4.5 亿元 [L2] [S4]\n"
        "- 管理层全年收入指引为同比增长 10% 以上 [L2] [S4]")
    note3 = work / "note-quote.md"
    note3.write_text(t3, encoding="utf-8")

    def shot_c(path, mod):
        rc, out, rows, gaps = run(path, "structured-note", note3, None,
                                  fx / "manual-bull-note.jsonl", work / ("c-" + str(abs(hash(str(path))))))
        kept = [r for r in rows if "4.5" in r.get("value", "")]
        swallowed = [g for g in gaps if "未取到第三方风险评级" in g.get("item", "")]
        return ("有效事实落成 facts=%d 条｜被缺数账吞走=%d 条" % (len(kept), len(swallowed)), bool(kept) and not swallowed)

    def both(fn, mod_now, mod_pre):
        nd, nok = fn(intake, mod_now)
        if pre is None:
            return nd, nok, None, None
        pd_, pok = fn(pre, mod_pre)
        return nd, nok, pd_, pok

    a_now, a_ok, a_pre, a_pre_ok = both(shot_a, mod_now, mod_pre)
    b_now, b_ok, b_pre, b_pre_ok = both(shot_b, mod_now, mod_pre)
    c_now, c_ok, c_pre, c_pre_ok = both(shot_c, mod_now, mod_pre)
    for label, nd, nok, pd_, pok in (("靶甲 伪造出处", a_now, a_ok, a_pre, a_pre_ok),
                                     ("靶乙 反方形状", b_now, b_ok, b_pre, b_pre_ok),
                                     ("靶丙 缺数吞事实", c_now, c_ok, c_pre, c_pre_ok)):
        if not nok:
            bad.append("%s 修后仍不合：%s" % (label, nd))
        if pre is not None and pok:
            bad.append("%s 在改前快照上也是绿的 ⇒ 它没量到被修的那件事，不算靶（%s）" % (label, pd_))

    import shutil
    print("== 三枚靶的两头值（同一支断言分别打在 现件 与 --prefix 快照 上）")
    for label, nd, nok, pd_, pok in (("靶甲 伪造出处", a_now, a_ok, a_pre, a_pre_ok),
                                     ("靶乙 反方形状", b_now, b_ok, b_pre, b_pre_ok),
                                     ("靶丙 缺数吞事实", c_now, c_ok, c_pre, c_pre_ok)):
        print("  %s｜修后：%s → %s" % (label, nd, "合" if nok else "不合"))
        pre_txt = pd_ if pd_ is not None else "未跑（没给 --prefix 快照，不填 0）"
        pre_res = "-" if pok is None else ("仍绿（不是靶）" if pok else "红（这一支确实量到了）")
        print("           修前：%s → %s" % (pre_txt, pre_res))
    print("== 不变量（现役三枚夹具逐枚）")
    for x in notes:
        print("  " + x)
    for b in bad:
        print("FAIL " + b)
    print("----")
    print("靶=3 枚｜不变量=3 条（逐枚现算）｜不合=%d｜两头值：%s" % (len(bad), "两把都跑" if pre else "只有现件（未给 --prefix）"))
    shutil.rmtree(work, ignore_errors=True)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
