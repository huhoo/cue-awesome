#!/usr/bin/env bash
# run_fixtures.sh —— catalyst-calendar v4 机检总探针(spec §v2-B+§v3-B+§v4-A/B;工单 M35/M40/2.1)。
# 纪律:退出码直取 "$?",禁管道吞码;--window 全 case 显式(B6 反 wall-clock);
#      S 系列带 runmark 断言「唯一目标」——命中的是 intended gate,且无 Traceback(B6)。
# 账目:M27 十样+B11(M28 真实反哺)+M21 五样+v2 保留样(31)+M32 十样 S 系列
#      (S1 双跑:无形制道可拦=v3 盲区如实;有证据层=断链)+good/partial 证据层对偶
#      +M40 T1 前缀撞号(M37-B1);共 45 断言。
set -u
cd "$(dirname "$0")"
PY="${PYTHON:-python3}"
CHECK="../check_calendar.py"
W="--window 2026-10-01~2026-12-31"
TMP="$(mktemp "${TMPDIR:-/tmp}/cal4_fixture.XXXXXX")"
trap 'rm -f "$TMP" "$TMP.x.jsonl"' EXIT
fail=0

run() { # run <期望exit> <说明> <命令...>
  local want="$1" name="$2"; shift 2
  "$@" >"$TMP" 2>&1
  local got=$?
  if grep -q "Traceback" "$TMP" 2>/dev/null; then
    echo "FAIL $name (traceback=事故 B6)"; sed 's/^/     | /' "$TMP"; fail=1
  elif [ "$got" -eq "$want" ]; then
    echo "ok   $name (exit $got)"
  else
    echo "FAIL $name (want exit $want, got $got)"; sed 's/^/     | /' "$TMP"; fail=1
  fi
}

runmark() { # runmark <期望exit> <目标标记> <说明> <命令...>:exit 对+标记在场,反 Traceback
  local want="$1" mark="$2" name="$3"; shift 3
  "$@" >"$TMP" 2>&1
  local got=$?
  if grep -q "Traceback" "$TMP" 2>/dev/null; then
    echo "FAIL $name (traceback=事故 B6)"; sed 's/^/     | /' "$TMP"; fail=1
  elif [ "$got" -ne "$want" ] || ! grep -q -- "$mark" "$TMP"; then
    echo "FAIL $name (want exit $want + 标记「$mark」,got $got)"; sed 's/^/     | /' "$TMP"; fail=1
  else
    echo "ok   $name (exit $got,命中「$mark」)"
  fi
}

# ---- 好样(5):含 N4/N5/N6 误杀治理形状 ----
run 0 "good-calendar    (六列全形+N4预披露+N5余档列+statute承载+监管函件)" "$PY" "$CHECK" good-calendar.md $W --sources calendar-sources.jsonl
run 0 "good-statute     (N2 对偶正样:形制合规 statute)" "$PY" "$CHECK" good-statute.md $W --sources statute-sources.jsonl
run 0 "good-meeting     (说明会/股东大会新类)" "$PY" "$CHECK" good-meeting.md $W --sources meeting-sources.jsonl
run 0 "good-letter      (函件号必配样)" "$PY" "$CHECK" good-letter.md $W --sources letter-sources.jsonl
run 0 "good-boundary-10 (10 主体=过,N3 前界)" "$PY" "$CHECK" good-boundary-10.md $W --sources boundary-sources.jsonl
# ---- M27 攻击样(7) ----
run 1 "bad-n2-statute   (N2 编造法条锚)" "$PY" "$CHECK" bad-n2-statute.md $W --sources calendar-sources.jsonl
run 1 "bad-n3-companies (N3 公司名 11 节)" "$PY" "$CHECK" bad-n3-companies.md $W --sources n3-sources.jsonl
run 1 "bad-n1b-appendix (N1b 附录独引死账)" "$PY" "$CHECK" bad-n1b-appendix.md $W --sources n1b-sources.jsonl
run 1 "bad-n7-desc      (N7 公司节降序)" "$PY" "$CHECK" bad-n7-desc.md $W --sources calendar-sources.jsonl
run 1 "bad-n8-renamed   (N8 摘要改名逃逸)" "$PY" "$CHECK" bad-n8-renamed.md $W --sources calendar-sources.jsonl
run 1 "bad-n9-anonly    (N9 监管缺函件号)" "$PY" "$CHECK" bad-n9-anonly.md $W --sources calendar-sources.jsonl
run 1 "bad-n16-crash    (N16 非法日期=FAIL 清单非 traceback)" "$PY" "$CHECK" bad-n16-crash.md $W --sources calendar-sources.jsonl
# ---- B11(M28 真实冒烟反哺)----
run 1 "bad-hallucination(B11 惯例/非承诺自白)" "$PY" "$CHECK" bad-hallucination.md $W --sources calendar-sources.jsonl
# ---- M21 五样 ----
run 1 "bad-anchor-fake  (M21-1 事件数字冒充锚)" "$PY" "$CHECK" bad-anchor-fake.md $W --sources calendar-sources.jsonl
run 1 "bad-type-wrong   (M21-2 说明会填分红)" "$PY" "$CHECK" bad-type-wrong.md $W --sources calendar-sources.jsonl
run 1 "bad-stat-noanchor(M21-3 法定挂 AN)" "$PY" "$CHECK" bad-stat-noanchor.md $W --sources calendar-sources.jsonl
run 1 "bad-noheader     (M21-4 孤儿管道行)" "$PY" "$CHECK" bad-noheader.md $W --sources calendar-sources.jsonl
run 1 "bad-rating       (M21-5 评级句入表)" "$PY" "$CHECK" bad-rating.md $W --sources calendar-sources.jsonl
# ---- v2 保留样 + 窗外余档误用 + claim 扫描 ----
run 1 "bad-naked        (锚列空)" "$PY" "$CHECK" bad-naked.md $W --sources calendar-sources.jsonl
run 1 "bad-word         (利好禁词)" "$PY" "$CHECK" bad-word.md $W --sources calendar-sources.jsonl
run 1 "bad-window       (窗外余档列未注)" "$PY" "$CHECK" bad-window.md $W --sources calendar-sources.jsonl
run 1 "bad-outside-misuse(窗内误注余档 A1)" "$PY" "$CHECK" bad-outside-misuse.md $W --sources calendar-sources.jsonl
run 1 "bad-order        (R1/R2 换序)" "$PY" "$CHECK" bad-order.md $W --sources calendar-sources.jsonl
run 1 "bad-summary      (摘要超起点+30)" "$PY" "$CHECK" bad-summary.md $W --sources calendar-sources.jsonl
run 1 "bad-bidirection  (正文锚断链)" "$PY" "$CHECK" bad-bidirection.md $W --sources calendar-sources.jsonl
run 1 "bad-claim-rating (A4 sources claim 扫描区)" "$PY" "$CHECK" good-calendar.md $W --sources bad-claim-sources.jsonl
run 1 "bad-legacy-5col  (B13 冒烟真件:五列旧形+自白词双重死)" "$PY" "$CHECK" bad-legacy-5col.md --window 2026-09-21~2026-12-20 --sources legacy-sources.jsonl
run 1 "bad-sources      (行契约全家坏)" "$PY" "$CHECK" good-calendar.md $W --sources bad-sources.jsonl
# ---- v4-B⑦ 证据层对偶(2):全匹配=过,断链=拦 ----
run 0 "good-evidence    (全部锚∈evidence-good 原文匹配)" "$PY" "$CHECK" good-calendar.md $W --sources calendar-sources.jsonl --evidence evidence-good
runmark 1 "无原文匹配" "evidence-partial(只statute)断链被拦" "$PY" "$CHECK" good-calendar.md $W --sources calendar-sources.jsonl --evidence evidence-partial
# ---- M32 十攻击样 S 系列(§v4-A 七件收编) ----
run 0 "bad-s1 无证据层  (三件齐伪满:形制道拦不住,如实账——v4-C 语义层职责)" "$PY" "$CHECK" bad-s1-fake-statute.md $W --sources bad-s1-sources.jsonl
runmark 1 "不在 evidence 当场取回清单" "bad-s1-fake-statute(S1 裸编法名:证据层断链)" "$PY" "$CHECK" bad-s1-fake-statute.md $W --sources bad-s1-sources.jsonl --evidence evidence-good
runmark 1 "被禁推导" "bad-s1b-statute-deleted(S1b 真法名+已删/快报无条件)" "$PY" "$CHECK" bad-s1b-statute-deleted.md $W --sources bad-s1b-sources.jsonl
runmark 1 "藏日期" "bad-s2-event-date      (S2 事件列另藏 2030-01-01,v4-A①)" "$PY" "$CHECK" bad-s2-event-date.md $W --sources calendar-sources.jsonl
runmark 1 "「买入」" "bad-s3-booktitle-rating(S3《》套评级不豁免,v4-A②)" "$PY" "$CHECK" bad-s3-booktitle-rating.md $W --sources calendar-sources.jsonl
runmark 1 "「增持」" "bad-s4-naked-add       (S4 光杆建议增持后缀强制,v4-A②)" "$PY" "$CHECK" bad-s4-naked-add.md $W --sources calendar-sources.jsonl
runmark 1 "附录内出现表格行" "bad-s5-appendix-table  (S5 附录停机坪关闭,v4-A③)" "$PY" "$CHECK" bad-s5-appendix-table.md $W --sources calendar-sources.jsonl
runmark 1 "动态区只准过去日" "bad-s6b-future-dongtai (S6b 已发生动态未来日,v4-A③)" "$PY" "$CHECK" bad-s6b-future-dongtai.md $W --sources calendar-sources.jsonl
runmark 1 "自白词" "bad-s7-rhythm          (S7 按过往节奏/或将,v4-A⑥ 扩充)" "$PY" "$CHECK" bad-s7-rhythm.md $W --sources calendar-sources.jsonl
runmark 1 "日期列为空或不可解析" "bad-s8-empty-date        (S8 空日期=行号化 FAIL 非 TypeError,v4-A⑤)" "$PY" "$CHECK" bad-s8-empty-date.md $W --sources calendar-sources.jsonl
runmark 1 "不在主表日期集合" "bad-s10-summary-subset (S10 摘要⊄主表,v4-A④ 保留词定位)" "$PY" "$CHECK" bad-s10-summary-subset.md $W --sources calendar-sources.jsonl
# ---- M37-B1/T1(M40 手术刀):前缀撞号须整词边界拦 ----
runmark 1 "无原文匹配" "bad-t1-an-prefix     (T1 真 AN 少末位撞子串,整词边界断链)" "$PY" "$CHECK" bad-t1-an-prefix.md $W --sources bad-t1-sources.jsonl --evidence evidence-good
# ---- B6 缺参与 help ----
run 1 "no-window  (缺 --window)" "$PY" "$CHECK" good-calendar.md --sources calendar-sources.jsonl
run 1 "no-sources (缺 --sources)" "$PY" "$CHECK" good-calendar.md $W
run 0 "--help     (CONTRIBUTING §3)" "$PY" "$CHECK" --help

exit "$fail"
