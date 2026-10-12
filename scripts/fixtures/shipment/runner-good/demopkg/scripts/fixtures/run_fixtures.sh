#!/usr/bin/env bash
set -u
cd "$(dirname "$0")"
fail=0
[ -f ok.md ] || fail=1
echo "assertions: $((1-fail))/1"
[ "$fail" -eq 0 ] && echo "ALL GREEN (assertions: 1/1)" || echo "NOT GREEN"
exit "$fail"
