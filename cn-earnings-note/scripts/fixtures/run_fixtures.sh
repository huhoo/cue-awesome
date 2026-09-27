#!/usr/bin/env bash
# run_fixtures.sh —— check_note.py 总探针：good→exit 0、各 bad exit 1、--help→exit 0,全对 exit 0。
# M135-A:P-27 三道豁免按现行行为固化守护样 6 项入册(20→26 项,零行为变更,check_note.py 一字未动)。
# M135-B:P-25 裁准并码——NUM_UNIT_RE 扩千元/元/亿/百万/万股/亿股/股(元(?!年) 防「元年」);千元守护样翻转(mv→bad-qty-qianyuan,断言 0→1),7 单位正反对+「元年/公元」防误中直证+「吨」集外哨兵代管(26→42 项)。
# 注意(M5 防吞码教训):探针判定一律直取 "$?" 再展示;管道 tail 会把退出码换成 tail 的——
# 任何复现行如需展示退出码,必须 `cmd; echo exit=$?` 形态,勿 `cmd | tail`。
set -u
cd "$(dirname "$0")"
PY="${PYTHON:-python3}"
CHECK="../check_note.py"
TMP="$(mktemp "${TMPDIR:-/tmp}/check_note_fixture.XXXXXX")"  # 唯一名,并发/多 case 不互踩
trap 'rm -f "$TMP"' EXIT
fail=0

run() { # run <期望exit> <说明> <命令...>
  local want="$1" name="$2"; shift 2
  "$@" >"$TMP" 2>&1
  local got=$?
  if [ "$got" -eq "$want" ]; then
    echo "ok   $name (exit $got)"
  else
    echo "FAIL $name (want exit $want, got $got)"
    sed 's/^/     | /' "$TMP"
    fail=1
  fi
}

runout() { # runout <期望exit> <stdout必含子串> <说明> <命令...>:退出码+输出双断言(守护样专用)
  local want="$1" needle="$2" name="$3"; shift 3
  "$@" >"$TMP" 2>&1
  local got=$?
  if [ "$got" -eq "$want" ] && grep -qF -- "$needle" "$TMP"; then
    echo "ok   $name (exit $got + 输出含「$needle」)"
  else
    echo "FAIL $name (want exit $want+「$needle」, got $got)"; sed 's/^/     | /' "$TMP"; fail=1
  fi
}

run 0 "good (with --sources)"        "$PY" "$CHECK" note-good.md --sources sources.jsonl
run 0 "good (without --sources)"     "$PY" "$CHECK" note-good.md
run 1 "bad-nodecl  (缺 AI 初稿声明)"  "$PY" "$CHECK" bad-nodecl.md --sources sources.jsonl
run 1 "bad-norating(给出评级/目标价)" "$PY" "$CHECK" bad-norating.md --sources sources.jsonl
run 1 "bad-norating-enum(枚举句夹带赋值)" "$PY" "$CHECK" bad-norating-enum.md --sources sources.jsonl
run 1 "bad-word    (命中禁用词)"      "$PY" "$CHECK" bad-word.md --sources sources.jsonl
run 1 "bad-numbers(覆盖率不足)"      "$PY" "$CHECK" bad-numbers.md --sources sources.jsonl
run 0 "good + --allow-pending"       "$PY" "$CHECK" note-good.md --allow-pending
run 0 "ledger good (2026H1 vs 2025AR)"  "$PY" "$CHECK" note-good.md --ledger ledger-2026H1.json --prev-ledger ledger-2025AR.json
run 0 "scaffold good    (B 全形状)"      "$PY" "$CHECK" good-scaffold.md --sources sources.jsonl
run 1 "scaffold noborder(B4 缺边框注句)" "$PY" "$CHECK" bad-scaffold-noborder.md --sources sources.jsonl
run 1 "scaffold anchor  (B3 锚行无 S)"   "$PY" "$CHECK" bad-scaffold-anchor.md --sources sources.jsonl
run 1 "scaffold opinion (B2 格夹判断词)" "$PY" "$CHECK" bad-scaffold-opinion.md --sources sources.jsonl
run 1 "bad-linkage  (D5 期初值被改)"     "$PY" "$CHECK" note-good.md --ledger bad-linkage.json --prev-ledger ledger-2025AR.json
run 1 "bad-status    (D3 非法状态枚举)"   "$PY" "$CHECK" note-good.md --ledger bad-status.json --prev-ledger ledger-2025AR.json
run 1 "bad-amendment(D4 变更却fulfilled)" "$PY" "$CHECK" note-good.md --ledger bad-amendment.json --prev-ledger ledger-2025AR.json
run 1 "bad-ledgerof(B2 互链断链)"        "$PY" "$CHECK" note-good.md --ledger bad-ledgerof.json --prev-ledger ledger-2025AR.json

# --- M135-A(P-27 三道豁免守护样,零行为变更;逐码点名防恒真,C-34) ---
runout 1 "含数字结论但无" "bad-qty-qianyuan  (千元无L→拦:M135-B 翻转 A 半 outunit 正样,mv 更名断言 0→1)" "$PY" "$CHECK" bad-qty-qianyuan.md
runout 1 "含数字结论但无" "bad-inunit-nol  (集外单位对·反:2万元 无L点名)" "$PY" "$CHECK" bad-inunit-nol.md
runout 0 "数字行 0/0" "good-exempt-list    (列表豁免对:引导行自带 [S1]+s1.jsonl)" "$PY" "$CHECK" good-exempt-list.md --sources s1.jsonl
runout 1 "含数字结论但无" "bad-list-nonlist  (同句去「- 」即拦,豁免不随内容走)" "$PY" "$CHECK" bad-exempt-list-nonlist.md
runout 0 "数字行 0/0" "good-exempt-index   (来源索引对:节内无L行豁免 0/0)" "$PY" "$CHECK" good-exempt-index.md
runout 1 "含数字结论但无" "bad-index-moved   (挪进「财务指标」节即拦,豁免随节名不随位置)" "$PY" "$CHECK" bad-exempt-index-moved.md

# --- M135-B(P-25 单位集扩容:7 单位正反 pairs 千元反样在上块 + 防误中直证 + 吨哨兵) ---
runout 0 "数字行 1/1" "good-qty-qianyuan (千元带L→放)"   "$PY" "$CHECK" good-qty-qianyuan.md
runout 1 "含数字结论但无" "bad-qty-yuan    (元无L→拦)"    "$PY" "$CHECK" bad-qty-yuan.md
runout 0 "数字行 1/1" "good-qty-yuan     (元带L→放)"    "$PY" "$CHECK" good-qty-yuan.md
runout 1 "含数字结论但无" "bad-qty-yi      (亿无L→拦)"    "$PY" "$CHECK" bad-qty-yi.md
runout 0 "数字行 1/1" "good-qty-yi       (亿带L→放)"    "$PY" "$CHECK" good-qty-yi.md
runout 1 "含数字结论但无" "bad-qty-baiwan  (百万无L→拦)"  "$PY" "$CHECK" bad-qty-baiwan.md
runout 0 "数字行 1/1" "good-qty-baiwan   (百万带L→放)"  "$PY" "$CHECK" good-qty-baiwan.md
runout 1 "含数字结论但无" "bad-qty-wangu   (万股无L→拦)"  "$PY" "$CHECK" bad-qty-wangu.md
runout 0 "数字行 1/1" "good-qty-wangu    (万股带L→放)"  "$PY" "$CHECK" good-qty-wangu.md
runout 1 "含数字结论但无" "bad-qty-yiguo   (亿股无L→拦)"  "$PY" "$CHECK" bad-qty-yiguo.md
runout 0 "数字行 1/1" "good-qty-yiguo    (亿股带L→放)"  "$PY" "$CHECK" good-qty-yiguo.md
runout 1 "含数字结论但无" "bad-qty-gu      (股无L→拦)"    "$PY" "$CHECK" bad-qty-gu.md
runout 0 "数字行 1/1" "good-qty-gu       (股带L→放)"    "$PY" "$CHECK" good-qty-gu.md
runout 0 "数字行 0/0" "good-misfire-yuanian (「2020元年/公元2026年」防误中直证:误中必 exit 1,不恒真)" "$PY" "$CHECK" good-misfire-yuanian.md
runout 0 "数字行 0/0" "good-outunit-ton  (集外哨兵代管:20,000吨 无L仍0/0)" "$PY" "$CHECK" good-outunit-ton.md

run 0 "help (--help)"                "$PY" "$CHECK" --help



# --- M10/F3:送审就绪度附录两 case(报告内容断言,非仅退出码) ---
AUD="$TMP.audit-good.md"; BADAUD="$TMP.audit-bad.md"
"$PY" "$CHECK" note-good.md --sources sources.jsonl --audit-report "$AUD" >>"$TMP" 2>&1 \
  && grep -q "^## 1\." "$AUD" && grep -q "^## 2\." "$AUD" && grep -q "^## 3\." "$AUD" \
  && grep -q "^## 4\." "$AUD" && grep -q "^## 5\." "$AUD" \
  && grep -q "零命中" "$AUD" && grep -q "✅ 通过" "$AUD" \
  && echo "ok   audit good (五节齐+禁词零命中显式+声明核验)" \
  || { echo "FAIL audit good"; sed 's/^/     | /' "$AUD"; fail=1; }
"$PY" "$CHECK" bad-audit-word.md --audit-report "$BADAUD" >/dev/null 2>&1
got=$?
if [ "$got" -eq 1 ] && grep -q "稳赚" "$BADAUD" && grep -q "第 24 行\|命中词" "$BADAUD"; then
  echo "ok   audit bad  (藏词被报告点名+exit 1)"
else
  echo "FAIL audit bad (exit $got;报告未点名或门禁未抓)"; sed 's/^/     | /' "$BADAUD"; fail=1
fi
rm -f "$AUD" "$BADAUD"

exit "$fail"
