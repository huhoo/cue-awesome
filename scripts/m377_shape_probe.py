#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# m377_shape_probe.py —— M377 探针：一条命令跑完各形 + 不进表格那一格（形数由 SHAPES 现算，不写死）。
# 每形先写下我的预期句子，再跑，再把实读并排打出来；不一致就在本件的末行汇总里点名（不静默放过）。
# 合成靶全落 TMPDIR（含一处真仓只读对拍），真仓与包面一字不动；每例跑完即删靶根并断言已删。

import json
import pathlib
import re
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
VOCAB = str(REPO / "scripts" / "artifact-types.yaml")
TOOL = str(REPO / "scripts" / "scenario_graph.py")
TMP = pathlib.Path("/data/sdc1/work/tmp/awesome-skill/m377")
SHAPE_DIR = TMP / "shapes"
ENV = "CUE_API_KEY"

AAA = "---\nname: aaa\nproduces:\n  - parsed-doc\n---\n\n合成靶面，不属于任何真包。\n"


def face(bbb_body):
    return bbb_body


SHAPES = [
    ("形一 标准（列表项两格）",
     "---\nname: bbb\nconsumes:\n  - parsed-doc\n---\n\n合成靶面。\n",
     "预期：rc=0；读到那一条边（非孤点=2）；不出「形制不齐」也不出「不可判」。"),
    ("形二 更深（列表项四格）",
     "---\nname: bbb\nconsumes:\n    - parsed-doc\n---\n\n合成靶面。\n",
     "预期：rc=0；值按 YAML 语义读得到（非孤点=2）；出一句「形制不齐…4 格」，但不判不可判——合法写法不该判红。"),
    ("形三 更深一级（列表项六格）",
     "---\nname: bbb\nconsumes:\n      - parsed-doc\n---\n\n合成靶面。\n",
     "预期：同形二（缩进报 6 格）。"),
    ("形四 更浅（列表项顶格）",
     "---\nname: bbb\nconsumes:\n- parsed-doc\n---\n\n合成靶面。\n",
     "预期：rc=0；值读得到（非孤点=2）；出「形制不齐…0 格」，不判不可判。"),
    ("形五 键与列表项之间夹一空行（M374 的假红那一形）",
     "---\nname: bbb\nconsumes:\n\n  - parsed-doc\n---\n\n合成靶面。\n",
     "预期：rc=0；非孤点=2；既不判不可判、也不点形制不齐（缩进仍是两格，只是夹了合法空行）。"),
    ("形七 produces 归属存疑＋给一份域原料（验表三也不吃不可判的键）",
     "---\nname: bbb\nproduces:\n  foo: bar\n    - parsed-doc\n---\n\n合成靶面。\n",
     "预期：rc=1；表三那一节自报「本表跳过 N 把键／M 枚包」，且强口径不因该键被读成空清单而冒充「无人引用」。"),
    ("形六 归属存疑（consumes 与 inputs 两把键都先映射行、后冒类列表行）",
     "---\nname: bbb\nconsumes:\n  foo: bar\n    - parsed-doc\ninputs:\n  baz: qux\n    - company-list\n---\n\n合成靶面。\n",
     "预期：rc=1；出一句不可判点名（两把键同列）；末行「不可判=2 把键／1 枚包」；"
     "表一把该枚列成不可判而不是孤点／非孤点；列 (a) 与列 (b) 各自报跳过 1 把（该枚的 inputs 与 consumes 都不进表）。"),
]
MISMATCH = []
# 形数由名册现算：SHAPES 里的每一形 ＋ 形七带域原料那一格（验表三不吃不可判的键）
RUNS = None  # 在 main 里按 len(SHAPES) 现算，避免又一枚写死的常量
# 每形期望的「不可判把键数」：写死在这里，跑出来不一致就是事实与预期打架，由本件点名
EXPECT_KEYS = {"形一": 0, "形二": 0, "形三": 0, "形四": 0, "形五": 0, "形六": 2, "形七": 1}


def build(body):
    if SHAPE_DIR.exists():
        shutil.rmtree(SHAPE_DIR)
    (SHAPE_DIR / "aaa").mkdir(parents=True)
    (SHAPE_DIR / "bbb").mkdir(parents=True)
    (SHAPE_DIR / "aaa" / "SKILL.md").write_text(AAA, encoding="utf-8")
    (SHAPE_DIR / "bbb" / "SKILL.md").write_text(body, encoding="utf-8")
    items = [l for l in body.split("\n") if l.strip().startswith("- ")]
    return items


def run(root):
    p = subprocess.run(["python3", "-B", TOOL, "--repo", str(root), "--vocabulary", VOCAB],
                       capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def line_with(out, *pats):
    for l in out.splitlines():
        if all(x in l for x in pats):
            return l.strip()
    return "(缺行)"


def ok(label, cond, detail):
    if not cond:
        MISMATCH.append(label)
    print("   [" + ("合预期" if cond else "不合预期") + "] " + label + "｜" + detail)


def real_repo_readings():
    p = subprocess.run(["python3", "-B", TOOL, "--vocabulary", VOCAB], cwd=str(REPO),
                       capture_output=True, text=True)
    return p.returncode, p.stdout


def _nums(text):
    """从尺自己的输出里把几枚数抠出来（不写死绝对值——绝对值是上一拍的量，抠出来的才是这一拍的）。"""
    d = {}
    for key, rx in (("非孤点", r"非孤点=(\d+) 枚"), ("全包", r"全包=(\d+) 枚"),
                    ("consumes", r"consumes 总项=(\d+)"), ("指路条", r"枚数=(\d+) 条｜合计出现次数="),
                    ("指路次", r"枚数=\d+ 条｜合计出现次数=(\d+)")):
        m = re.search(rx, text)
        d[key] = int(m.group(1)) if m else None
    seg = re.search(r"==\s*表一[\s\S]*?(?====|表二)", text)
    if seg:
        s = seg.group(0)
        m = re.search(r"枚数=(\d+)（由上列现算）", s)
        d["孤点清单自报"] = int(m.group(1)) if m else None
        d["孤点清单行数"] = len([l for l in s.splitlines() if re.match(r"^\s{2}\S+ ｜", l)])
    else:
        d["孤点清单自报"] = d["孤点清单行数"] = None
    return d


def selfcheck(n, label):
    """只在同一次运行内自洽：清单实数行数＝自报枚数，且 孤点＋非孤点＝全包。跨拍不等不是红（那是世界变了）。"""
    out = []
    if n.get("孤点清单自报") is None or n.get("孤点清单行数") is None:
        out.append("%s：表一段落抠不到自报枚数或清单行数（取值域故障，不算自洽通过）" % label)
    elif n["孤点清单自报"] != n["孤点清单行数"]:
        out.append("%s：表一自报枚数=%s 而清单实数行数=%s（尺自己数错了）" % (label, n["孤点清单自报"], n["孤点清单行数"]))
    if None in (n.get("孤点清单自报"), n.get("非孤点"), n.get("全包")):
        out.append("%s：三枚数有一枚抠不到，无法验「孤点＋非孤点＝全包」" % label)
    elif n["孤点清单自报"] + n["非孤点"] != n["全包"]:
        out.append("%s：孤点 %s＋非孤点 %s ≠ 全包 %s（对账破了）" % (label, n["孤点清单自报"], n["非孤点"], n["全包"]))
    return out


def main():
    global RUNS
    RUNS = len(SHAPES) + 1
    print("%d 形探针（合成靶落 TMPDIR；真仓只读，只在末格对拍）——形数由 SHAPES 现算" % RUNS)
    for label, body, expect in SHAPES:
        items = build(body)
        rc, out, err = run(SHAPE_DIR)
        print("== " + label)
        print("   预期句子：" + expect)
        print("   注入自证：靶面里类列表行现读＝%r" % (items,))
        print("   实读 rc=%d" % rc)
        print("   表一行：" + line_with(out, "枚数=", "非孤点=")[:150])
        loose = line_with(out, "形制不齐")
        unj = line_with(out, "注：") if False else next((x.strip() for x in out.splitlines() if x.strip().startswith("注：") and "值归属存疑" in x), "(无不可判点名)")
        tail = line_with(out, "不合=0｜不可判=")
        print("   点名行：" + (unj if unj != "(缺行)" else "(无不可判点名)")[:150])
        print("   形制行：" + loose[:150])
        print("   末行：" + (tail if tail != "(缺行)" else "(无不可判末行)"))
        wantk = EXPECT_KEYS[label[:2]]
        if rc == 0:
            ok("读到边（非孤点=2 枚）", "非孤点=2 枚" in out, line_with(out, "枚数=", "非孤点=")[:70])
            # 期望值在这一支也得上：不然那五个 0 就是死数，写错也没人发现（lead 逮到的就是这一族）
            ok("期望 0 把不可判 ⇒ 不出汇总末行", wantk == 0 and "不可判=" not in out,
               "EXPECT_KEYS=%d｜末行在场＝%s" % (wantk, "不可判=" in out))
        else:
            ok("不可判末行单位两值并列（把键／枚包）", "不可判=%d 把键／1 枚包" % wantk in out, tail[:90])
        if "形一" in label or "形五" in label:
            ok("不出形制不齐点名", loose == "(缺行)", loose[:60])
        if "形二" in label or "形三" in label or "形四" in label:
            ok("出了形制不齐点名（值仍读得到）", "形制不齐" in loose, loose[:90])
        if "形六" in label:
            ok("表一把该枚列成不可判而不是孤点", "不可判（键：consumes" in out, line_with(out, "不可判（键")[:110])
            la = line_with(out, "列 (a) 枚数=")
            lb = line_with(out, "列 (b) 枚数=")
            ok("列 (a) 那行自报跳过 1 把（needle 按枚数行的形状取，不取表头那句）", "跳过 1 把" in la, la[:130])
            ok("列 (b) 那行自报跳过 1 把", "跳过 1 把" in lb, lb[:130])
            taken = line_with(out, "枚数=", "非孤点=")
            ok("表一也并列取到／跳过（取到 1 枚包／跳过 1 枚包）", "取到 1 枚包／跳过 1 枚包" in taken, taken[:120])
        shutil.rmtree(SHAPE_DIR)
        print("   复原：靶根已删＝%s" % (not SHAPE_DIR.exists()))

    print("== 形七（produces 归属存疑＋一份域原料）：验表三也不吃不可判的键")
    rows = TMP / "domains-rows.jsonl"
    rows.write_text(json.dumps({"id": "macro", "external_status": "live", "legs": ["x"]}) + "\n", encoding="utf-8")
    body7 = [x for x in SHAPES if x[0].startswith("形七")][0][1]
    items7 = build(body7)
    p7 = subprocess.run(["python3", "-B", TOOL, "--repo", str(SHAPE_DIR), "--vocabulary", VOCAB,
                         "--domains", str(rows)], capture_output=True, text=True)
    print("   预期句子：" + [x for x in SHAPES if x[0].startswith("形七")][0][2])
    print("   注入自证：bbb 类列表行现读＝%r" % (items7,))
    print("   实读 rc=%d" % p7.returncode)
    note3 = line_with(p7.stdout, "表三跳过") if "表三跳过" in p7.stdout else line_with(p7.stdout, "本表跳过")
    print("   表三点名行：" + note3[:150])
    ok("表三自报跳过（produces 不可判不进该表）", "本表跳过 1 把键／1 枚包" in note3, note3[:120])
    ok("强口径仍按缺位点名、不读成空清单", "不作数" in p7.stdout or "引用到" in p7.stdout, "见原文")
    shutil.rmtree(SHAPE_DIR)
    rows.unlink()
    print("   复原：靶根已删＝%s｜原料已删＝%s" % (not SHAPE_DIR.exists(), not rows.exists()))

    print("== 末格·真仓两跑（基线由当前 HEAD 现算；比较只在同一次运行内自洽，跨拍差异只两值并列、不当等式锁）")
    rc, out = real_repo_readings()
    head_dir = TMP / "head-snapshot"
    shutil.rmtree(head_dir, ignore_errors=True)   # 每次现解，不吃上一拍的残件
    head_dir.mkdir(parents=True, exist_ok=True)
    hr = None
    ar = subprocess.run(["git", "-C", str(REPO), "archive", "HEAD"], capture_output=True)
    if ar.returncode == 0 and ar.stdout:
        ext = subprocess.run(["tar", "-x", "-C", str(head_dir)], input=ar.stdout, capture_output=True)
        if ext.returncode == 0:
            # git archive 导出的是仓根本身（不带包名前缀），所以 --repo 直指解出来的那层
            h = subprocess.run(["python3", "-B", TOOL, "--repo", str(head_dir), "--vocabulary", VOCAB],
                               cwd=str(REPO), capture_output=True, text=True)
            if h.returncode != 0 or "非孤点=" not in h.stdout:
                print("   HEAD 快照那一跑没给出可读末行（rc=%d，stderr 前 60 字：%s）：这一支算取值域故障，不算通过也不算红" % (
                    h.returncode, h.stderr.strip()[:60]))
                hr = None
            else:
                hr = h.stdout
                print("   HEAD 快照跑：rc=%d｜%s" % (h.returncode, line_with(hr, "非孤点")[:96]))
        else:
            print("   HEAD 快照解不开（tar rc=%d）：跨拍并列这一支明写未跑，不填 0、也不当作通过" % ext.returncode)
    else:
        print("   HEAD 快照取不到（git archive rc=%d）：跨拍并列这一支明写未跑，不填 0、也不当作通过" % ar.returncode)
    for w in ("由上列现算", "全包=", "非孤点=", "consumes 总项=", "合计出现次数="):
        ok("真仓现读里该形状句在场：" + w, w in out, "在场")
    n_now = _nums(out)
    problems = selfcheck(n_now, "工作树")
    if hr is not None:
        n_head = _nums(hr)
        problems += selfcheck(n_head, "HEAD")
        print("   跨拍两值并列（只并列、不锁等式）：非孤点 HEAD=%s ∥ 工作树=%s｜consumes 总项 HEAD=%s ∥ 工作树=%s｜指路 HEAD=%s 条／%s 次 ∥ 工作树=%s 条／%s 次" % (
            n_head.get("非孤点"), n_now.get("非孤点"), n_head.get("consumes"), n_now.get("consumes"),
            n_head.get("指路条"), n_head.get("指路次"), n_now.get("指路条"), n_now.get("指路次")))
    else:
        print("   跨拍两值并列：未跑（HEAD 取不到），这一支不算通过")
    print("   工作树自洽读数：表一自报=%s／清单实数=%s｜非孤点=%s｜全包=%s" % (
        n_now.get("孤点清单自报"), n_now.get("孤点清单行数"), n_now.get("非孤点"), n_now.get("全包")))
    for p in problems:
        ok(p, False, "见上一行自报")
    print()
    print("探针小结：%d 格不合预期%s（跑%d 形＋真仓对拍；形数由名册现算，通与不通都打同一个数）" % (
        len(MISMATCH), "｜" + "；".join(MISMATCH) if MISMATCH else "（全合预期）", RUNS))
    return 1 if MISMATCH else 0


if __name__ == "__main__":
    sys.exit(main())
