#!/usr/bin/env bash
set -u
cd "$(dirname "$0")"
echo "NOT GREEN"
echo "夹具缺失 $PWD/scripts/fixtures/没这个文件.md"
exit 1
