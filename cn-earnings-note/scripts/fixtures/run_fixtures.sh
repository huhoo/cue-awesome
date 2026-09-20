#!/usr/bin/env bash
# run_fixtures.sh —— check_note.py 总探针：good→exit 0、各 bad exit 1、--help→exit 0,全对 exit 0。
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

run 0 "good (with --sources)"        "$PY" "$CHECK" note-good.md --sources sources.jsonl
run 0 "good (without --sources)"     "$PY" "$CHECK" note-good.md
run 1 "bad-nodecl  (缺 AI 初稿声明)"  "$PY" "$CHECK" bad-nodecl.md --sources sources.jsonl
run 1 "bad-norating(给出评级/目标价)" "$PY" "$CHECK" bad-norating.md --sources sources.jsonl
run 1 "bad-norating-enum(枚举句夹带赋值)" "$PY" "$CHECK" bad-norating-enum.md --sources sources.jsonl
run 1 "bad-word    (命中禁用词)"      "$PY" "$CHECK" bad-word.md --sources sources.jsonl
run 1 "bad-numbers(覆盖率不足)"      "$PY" "$CHECK" bad-numbers.md --sources sources.jsonl
run 0 "good + --allow-pending"       "$PY" "$CHECK" note-good.md --allow-pending
run 0 "ledger good (2026H1 vs 2025AR)"  "$PY" "$CHECK" note-good.md --ledger ledger-2026H1.json --prev-ledger ledger-2025AR.json
run 1 "bad-linkage  (D5 期初值被改)"     "$PY" "$CHECK" note-good.md --ledger bad-linkage.json --prev-ledger ledger-2025AR.json
run 1 "bad-status    (D3 非法状态枚举)"   "$PY" "$CHECK" note-good.md --ledger bad-status.json --prev-ledger ledger-2025AR.json
run 1 "bad-amendment(D4 变更却fulfilled)" "$PY" "$CHECK" note-good.md --ledger bad-amendment.json --prev-ledger ledger-2025AR.json
run 1 "bad-ledgerof(B2 互链断链)"        "$PY" "$CHECK" note-good.md --ledger bad-ledgerof.json --prev-ledger ledger-2025AR.json
run 0 "help (--help)"                "$PY" "$CHECK" --help

exit "$fail"
