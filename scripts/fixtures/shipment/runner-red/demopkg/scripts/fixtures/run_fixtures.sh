#!/usr/bin/env bash
set -u
cd "$(dirname "$0")"
[ -f 缺的样本.md ] || { echo "NOT GREEN"; exit 1; }
echo "ALL GREEN"
exit 0
