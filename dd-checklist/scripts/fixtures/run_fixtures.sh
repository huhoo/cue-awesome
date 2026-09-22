#!/usr/bin/env bash
# run_fixtures.sh — dd-checklist 机检题库跑（题单 R0-I + M63 增题，逐样验 exit 与**诊断码集合精确相等**）
#
#   bash scripts/fixtures/run_fixtures.sh              # 全量
#   bash scripts/fixtures/run_fixtures.sh bad-B14      # 只跑名字含 bad-B14 的样
#
# 每个样目录自带 cmd.txt（一行完整命令，在该目录内执行）与 expect.txt：
#   exit=<期望退出码>  need=<允许的诊断码，可多行>  [must-not=<禁止出现的码>]  [verdict=must-fail]
# 判据（题单 §0.7 / 契约 §v2-6）：**实际 DD-* 码集合必须与声明集合精确相等**，多码=FAIL；
# ctl-* 是 runner 自证样（负控与边界），单列计数、不占合同主集之数（样数只存在于题单矩阵与本 runner 现报，C-19）；崩溃一律不算命中（题单 §0.1）。
set -uo pipefail

FIXROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FILTER="${1:-}"
gb_ok=0
gb_fail=0
gb_total=0
ctl_ok=0
ctl_fail=0
ctl_total=0
failed_cases=()

for dir in "$FIXROOT"/*/; do
  name="$(basename "$dir")"
  case "$name" in
    good-* | bad-*) kind=contract ;;
    ctl-*) kind=ctl ;;
    *) continue ;;
  esac
  if [ -n "$FILTER" ] && ! printf '%s' "$name" | grep -q -- "$FILTER"; then
    continue
  fi
  if [ ! -f "$dir/cmd.txt" ] || [ ! -f "$dir/expect.txt" ]; then
    echo "FAIL $name 缺 cmd.txt / expect.txt"
    failed_cases+=("$name")
    [ "$kind" = contract ] && gb_fail=$((gb_fail + 1)) || ctl_fail=$((ctl_fail + 1))
    continue
  fi
  cmd="$(head -n 1 "$dir/cmd.txt")"
  want_exit="$(sed -n 's/^exit=//p' "$dir/expect.txt" | head -n 1)"
  verdict="$(sed -n 's/^verdict=//p' "$dir/expect.txt" | head -n 1)"
  out="$(cd "$dir" && bash -c "$cmd" 2>&1)"
  got_exit=$?

  allowed="$(sed -n 's/^need=//p' "$dir/expect.txt" | sort -u | tr '\n' ' ' | sed 's/[[:space:]]*$//')"
  actual="$(printf '%s\n' "$out" | sed -n 's/^\(DD-[A-Z]*\): .*/\1/p' | sort -u | tr '\n' ' ' | sed 's/[[:space:]]*$//')"
  forbidden="$(sed -n 's/^must-not=//p' "$dir/expect.txt" | tr ' ' '\n' | sed '/^$/d' | sort -u | tr '\n' ' ' | sed 's/[[:space:]]*$//')"

  exact_ok=1
  if [ "$got_exit" != "$want_exit" ]; then
    exact_ok=0
    why=" exit≠$want_exit"
  else
    why=""
  fi
  if [ "$allowed" != "$actual" ]; then
    exact_ok=0
    why="$why 码集不等(允许[$allowed] 实发[$actual])"
  fi
  for code in $forbidden; do
    case " $actual " in
      *" $code "*) exact_ok=0; why="$why 出现禁码$code" ;;
    esac
  done
  if printf '%s\n' "$out" | grep -qE 'Traceback|SyntaxError'; then
    exact_ok=0
    why="$why 崩溃(不算命中)"
  fi

  if [ "$verdict" = "must-fail" ]; then
    # runner 负控：本样故意多打未声明的码，runner **必须**判它失败——判对了控制样才算过
    if [ "$exact_ok" = 0 ]; then
      printf 'ok   %-38s ctl(负控按预期判失败:%s)\n' "$name" "${why# }"
      ctl_ok=$((ctl_ok + 1))
      ctl_total=$((ctl_total + 1))
    else
      printf 'FAIL %-38s ctl(负控未被拦下=runner 只做包含式检查)\n' "$name"
      ctl_fail=$((ctl_fail + 1))
      failed_cases+=("$name")
    fi
    continue
  fi

  if [ "$exact_ok" = 1 ]; then
    printf 'ok   %-38s exit=%s codes[%s]\n' "$name" "$got_exit" "$actual"
    if [ "$kind" = contract ]; then gb_ok=$((gb_ok + 1)); else ctl_ok=$((ctl_ok + 1)); fi
  else
    printf 'FAIL %-38s exit=%s want=%s |%s\n' "$name" "$got_exit" "$want_exit" "$why"
    printf '%s\n' "$out" | sed 's/^/        /'
    if [ "$kind" = contract ]; then gb_fail=$((gb_fail + 1)); else ctl_fail=$((ctl_fail + 1)); fi
    failed_cases+=("$name")
  fi
  [ "$kind" = contract ] && gb_total=$((gb_total + 1)) || ctl_total=$((ctl_total + 1))
done

echo "----"
printf 'fixtures: %d ok / %d fail / %d total\n' "$gb_ok" "$gb_fail" "$((gb_ok + gb_fail))"
printf 'controls: %d ok / %d fail / %d total\n' "$ctl_ok" "$ctl_fail" "$ctl_total"
if [ "$((gb_fail + ctl_fail))" -gt 0 ]; then
  printf 'failing: %s\n' "${failed_cases[*]}"
  exit 1
fi
exit 0
