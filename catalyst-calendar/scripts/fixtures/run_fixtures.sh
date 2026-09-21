#!/usr/bin/env bash
# run_fixtures.sh —— catalyst-calendar 机检独立探针(spec-0.1.0 §4;工单 M20/2.1)。
# 退出码断言纪律:命令直跑后取 "$?",展示用文件重定向——禁 `cmd | tail` 类管道吞码。
set -u
cd "$(dirname "$0")"
PY="${PYTHON:-python3}"
CHECK="../check_calendar.py"
WIN="2026-10-01~2026-12-31"
TMP="$(mktemp "${TMPDIR:-/tmp}/cal_fixture.XXXXXX")"
trap 'rm -f "$TMP" "$TMP.bad-date.md"' EXIT
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

run 0 "good-calendar (四道全过+窗外余档注在场)" "$PY" "$CHECK" good-calendar.md --window "$WIN"
run 1 "bad-naked    (②无锚裸日期行=日期幻觉防线)" "$PY" "$CHECK" bad-naked.md --window "$WIN"
run 1 "bad-word     (③利好|利空…+BANNED 复用)"   "$PY" "$CHECK" bad-word.md --window "$WIN"
run 1 "bad-window   (④窗外日期无「窗口外余档」注)" "$PY" "$CHECK" bad-window.md --window "$WIN"
run 0 "bad-window @ --no-default-window (窗外断言确由窗口参数驱动,不误伤)" "$PY" "$CHECK" bad-window.md --no-default-window
printf '%s\n' '# 日历' '> 本文件为 AI 初稿，不构成投资建议。' '| 日期 | 事件 | 类型 | 状态 | 来源锚 |' '| --- | --- | --- | --- | --- |' '| 2026-13-45 | 不存在的日期 | 回购 | — | AN202609021828930348 |' > "$TMP.bad-date.md"
run 1 "活样:2026-13-45 (④解析失败即 FAIL)"        "$PY" "$CHECK" "$TMP.bad-date.md" --window "$WIN"
run 0 "good+--sources (M19 全式调用,sources 六字段过)" "$PY" "$CHECK" good-calendar.md --window "$WIN" --sources calendar-sources.jsonl
run 1 "bad-sources  (sources 行 ref 空=契约违)"    "$PY" "$CHECK" good-calendar.md --window "$WIN" --sources bad-sources.jsonl
run 0 "--help 可跑(脚本规范 CONTRIBUTING §3)"     "$PY" "$CHECK" --help

exit "$fail"
