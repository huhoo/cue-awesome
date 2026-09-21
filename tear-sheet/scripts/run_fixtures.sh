#!/usr/bin/env bash
# run_fixtures.sh —— tear-sheet check_page 总探针(工单 M34/2.1;题单=verify/tear-sheet-badspec.md M26+M31 共 22 题)。
# 断言口径(验收协议):每题 3 断言=①exit 1 ②输出含目标道号 [①..④] ③输出含指定诊断关键词;
# good 基线+三个字面改名族(段名同义/去「主体」字面/观点改「观察」)各 PASS=字面形状零依赖。
# 合计 22×3+4 = 70 断言(≥64 题单全覆盖)。纪律:退出码直取禁管道吞码;--sources 每题配对专用自洽 jsonl。
set -u
cd "$(dirname "$0")"
PY="${PYTHON:-python3}"
CHECK="check_page.py"
TMP="$(mktemp "${TMPDIR:-/tmp}/page_fixture.XXXXXX")"
trap 'rm -f "$TMP"' EXIT
pass=0; total=0

a() { # a <期望exit> <期望子串(可空)> <说明> <命令...>
  local want="$1" needle="$2" name="$3"; shift 3
  total=$((total+1))
  "$@" >"$TMP" 2>&1
  local got=$?
  if [ "$got" -ne "$want" ] || { [ -n "$needle" ] && ! grep -qF -- "$needle" "$TMP"; }; then
    echo "FAIL $name (exit=$want→got=$got needle='${needle}')"; sed 's/^/     | /' "$TMP"; fail=1
  else
    pass=$((pass+1))
  fi
}
fail=0

# 题单:ID|目标道号|诊断关键词
QS=(
"TS-B01|①|缺声明字段「通道用量声明」"
"TS-B02|②|来源锚为空/不在白名单"
"TS-B03|②|来源锚为空/不在白名单"
"TS-B04|②|正文孤儿锚"
"TS-B05|②|basis 缺失/不在枚举"
"TS-B06|③|命中禁词「买入」"
"TS-B07|④|风险段出现在事件段之前"
"TS-B08|④|41 行 > 40"
"TS-B09|④|主体数 6 > 5"
"TS-B10|④|估算/非披露明确日期"
"TS-B11|④|在场事件 5 > 4"
"TS-B12|④|存在非"
"TS-B13|④|风险无命中固定句缺失"
"TS-B14|④|主体数 6 > 5"
"TS-B15|④|风险段出现在事件段之前"
"TS-B16|④|存在非"
"TS-B17|④|在场事件 5 > 4"
"TS-B18|②|孤儿记录未被正文引用"
"TS-B19|④|法定锚不可核"
"TS-B20|③|命中禁词"
"TS-B21|③|sources 第"
"TS-B22|④|在场事件 5 > 4"
)
ALL_DAOS="① ② ③ ④"
for entry in "${QS[@]}"; do
  IFS='|' read -r qid dao kw <<< "$entry"
  a 1 "[$dao]"  "$qid exit+道号" "$PY" "$CHECK" "fixtures/$qid.md" --sources "fixtures/$qid.jsonl"
  a 1 "$kw"     "$qid 诊断关键词" "$PY" "$CHECK" "fixtures/$qid.md" --sources "fixtures/$qid.jsonl"
  # 第三断言:唯一目标纯度——其余三道标记不得出现在输出中(跨道冒充=误杀,协议 2)
  "$PY" "$CHECK" "fixtures/$qid.md" --sources "fixtures/$qid.jsonl" >"$TMP.x" 2>&1
  total=$((total+1)); cross=0
  for d in $ALL_DAOS; do
    [ "$d" = "$dao" ] && continue
    grep -qF -- "[$d]" "$TMP.x" && cross=1
  done
  if [ "$cross" -eq 0 ]; then pass=$((pass+1)); else echo "FAIL $qid 跨道并报"; sed 's/^/     | /' "$TMP.x"; fail=1; fi
  rm -f "$TMP.x"
done

# good 基线与字面改名族(协议 6:同义改名/去字面不得关闸)
a 0 "" "good-page"           "$PY" "$CHECK" fixtures/good-page.md            --sources fixtures/good-sources.jsonl
a 0 "" "good-renamed-sections(五段同义改名)" "$PY" "$CHECK" fixtures/good-renamed-sections.md --sources fixtures/good-sources.jsonl
a 0 "" "good-no-subject-word(去「主体」字面)" "$PY" "$CHECK" fixtures/good-no-subject-word.md  --sources fixtures/good-sources.jsonl
a 0 "" "good-view-renamed   (观点→观察)"      "$PY" "$CHECK" fixtures/good-view-renamed.md     --sources fixtures/good-sources.jsonl

echo "----"
echo "assertions: $pass/$total"
[ "$fail" -eq 0 ] && [ "$pass" -eq "$total" ] && { echo "ALL GREEN (≥64 覆盖:$total)"; exit 0; }
echo "NOT GREEN"; exit 1
