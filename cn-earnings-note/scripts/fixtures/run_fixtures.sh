#!/usr/bin/env bash
# run_fixtures.sh —— check_note.py 总探针：good→exit 0、四个 bad 各 exit 1、--help→exit 0,全对 exit 0。
set -u
cd "$(dirname "$0")"
PY="${PYTHON:-python3}"
CHECK="../check_note.py"
fail=0

run() { # run <期望exit> <说明> <命令...>
  local want="$1" name="$2"; shift 2
  "$@" >/tmp/check_note_fixture.out 2>&1
  local got=$?
  if [ "$got" -eq "$want" ]; then
    echo "ok   $name (exit $got)"
  else
    echo "FAIL $name (want exit $want, got $got)"
    sed 's/^/     | /' /tmp/check_note_fixture.out
    fail=1
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
run 0 "help (--help)"                "$PY" "$CHECK" --help

exit "$fail"
