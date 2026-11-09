#!/usr/bin/env bash
# 离线样例 runner：30 秒内在临时目录里走完「机检自测 → 好样坏样逐枚单跑 → 边界形逐枚单跑」三档。
# 用法：bash scripts/fixtures/run_fixtures.sh     （零网络、零计费、纯标准库；产物只落 ${TMPDIR:-/tmp}，跑完即删）
# 退码：0 三档全合期望；1 有不合（逐档点名并附那次真实退码与真实码集）；3 取值域故障（脚本或夹具取不到，不读成「零违例」）。
# 三档各自的期望都挂在两条分支上都被读的断言里（通与不通都读同一个数），不是只在失败分支里写死的死数。
set -u
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
FIX="$ROOT/scripts/fixtures"
WORK="$(mktemp -d "${TMPDIR:-/tmp}/cn-equity-research-note.XXXXXX")"
if [ -z "$WORK" ] || [ ! -d "$WORK" ]; then echo "3 取值域故障：临时目录没建成（TMPDIR=$TMPDIR 是否存在、可写？），不带空路径往下跑"; exit 3; fi
trap 'rm -rf "$WORK"' EXIT

bad=0
unk=0
for f in "$ROOT/scripts/check_note.py" "$FIX/good-note.md" "$FIX/bad-no-anchor.md" \
         "$FIX/bad-missing-section.md" "$FIX/bad-rating-word.md" "$FIX/bad-gap-unlisted.md" \
         "$FIX/bad-earnings-period.md" "$FIX/bad-empty-section.md"; do
  if [ ! -f "$f" ]; then echo "3 取值域故障：取不到 $f（不读成「夹具全过」）"; exit 3; fi
done

echo "档① 机检自测（好样须过、六枚坏样须各发它该发的那一道、钉阈三形与反证四档）"
out=$(cd "$ROOT" && python3 -B scripts/check_note.py --selftest 2>&1); rc=$?
echo "$(printf '%s\n' "$out" | tail -1)"; echo "  实发退码=$rc｜期望=0"
if [ "$rc" -ne 0 ]; then echo "  → 不合"; bad=$((bad + 1)); else echo "  → 合"; fi

echo "档② 好样与六枚坏样逐枚单跑（不并成一个总数：每枚报它自己的退码与码集）"
run_one() {
  local name="$1" want_rc="$2" want_code="$3"
  local o r codes
  o=$(cd "$ROOT" && python3 -B scripts/check_note.py "$FIX/$name" 2>&1); r=$?
  codes=$(printf '%s\n' "$o" | grep -o 'E-[A-Z]*' | sort -u | tr '\n' ' ')
  echo "  $name｜实发退码=$r｜期望=$want_rc｜实发码集=${codes:-（无）}"
  if [ "$r" -ne "$want_rc" ]; then
    echo "    → 不合：退码不符"; bad=$((bad + 1)); return
  fi
  if [ -n "$want_code" ] && ! printf '%s\n' "$codes" | grep -q "$want_code"; then
    echo "    → 不合：期望发码 $want_code 不在实发码集里"; bad=$((bad + 1)); return
  fi
  echo "    → 合"
}
run_one good-note.md 0 ""
run_one bad-no-anchor.md 1 E-ANCHOR
run_one bad-missing-section.md 1 E-FORMAT
run_one bad-rating-word.md 1 E-BANWORD
run_one bad-gap-unlisted.md 1 E-COVERAGE
run_one bad-earnings-period.md 1 E-SCOPE
run_one bad-empty-section.md 1 E-FORMAT

echo "档③ 零通道骨架（材料清单 → 待填骨架；本件不代填结论、不发请求）"
out=$(cd "$ROOT" && python3 -B scripts/make_outline.py --sources scripts/fixtures/sources.jsonl --out "$WORK/outline.md" 2>&1); rc=$?
echo "$(printf '%s\n' "$out" | head -1)"; echo "  实发退码=$rc｜期望=0｜骨架行数=$(wc -l < "$WORK/outline.md" 2>/dev/null || echo 取不到)"
if [ "$rc" -ne 0 ]; then
  if [ "$rc" -eq 3 ]; then echo "  → 不可判：骨架生成走到取值域出口（见上一行原文）"; unk=$((unk + 1));
  else echo "  → 不合：期望退码 0，实发 $rc"; bad=$((bad + 1)); fi
else
  echo "  → 合（骨架落成，结论位仍留占位）"
fi

echo "档④ 骨架过机检——期望红，且红在结论占位那一行"
if [ -f "$WORK/outline.md" ]; then
  out=$(cd "$ROOT" && python3 -B scripts/check_note.py "$WORK/outline.md" 2>&1); rc=$?
  hit=$(printf '%s\n' "$out" | grep -c '结论仍是占位')
  echo "  实发退码=$rc｜期望=1｜「结论仍是占位」命中=$hit｜末行=$(printf '%s\n' "$out" | head -1)"
  if [ "$rc" -eq 1 ] && [ "$hit" -ge 1 ]; then echo "  → 合（骨架不该被当成研究稿交付，红在这行是设计）";
  else echo "  → 不合：期望的红不再在场（退码 $rc／命中 $hit）——这一形变了就复读 make_outline 的结论位与 check_note 的占位判据，别沿用本断言"; bad=$((bad + 1)); fi
else
  echo "  → 不可判：档③没出骨架，这一档无从跑"; unk=$((unk + 1))
fi

echo "档⑤ 边界形逐枚单跑（这一档钉的是本包的实际射程，不是好样坏样的复读）"
# 边界形由好样就地改写生成，落临时目录；每形只断言它自己那一支的独有句在不在。
edge() {
  local label="$1" py="$2" needle="$3" want="$4"
  local f="$WORK/edge.md"
  python3 - "$FIX/good-note.md" "$f" <<PY
import sys
gt = open(sys.argv[1], encoding='utf-8').read()
$py
open(sys.argv[2], 'w', encoding='utf-8').write(t)
PY
  if [ ! -s "$f" ]; then echo "  $label｜→ 不可判：边界形没生成"; unk=$((unk + 1)); return; fi
  local o r hit
  o=$(cd "$ROOT" && python3 -B scripts/check_note.py "$f" 2>&1); r=$?
  hit=$(printf '%s\n' "$o" | grep -c "$needle")
  echo "  $label｜实发退码=$r｜「$needle」命中=$hit｜期望命中=$want"
  if [ "$want" = "1" ] && [ "$hit" -lt 1 ]; then echo "    → 不合：该发的没发"; bad=$((bad + 1)); return; fi
  if [ "$want" = "0" ] && [ "$hit" -ge 1 ]; then echo "    → 不合：不该发的发了"; bad=$((bad + 1)); return; fi
  echo "    → 合"
}
# 边界①：股东增减持是事实陈述，不是推荐语——「控股股东计划减持不超过 2%」不得判红
edge "边界① 增减持事实陈述不误红" \
  "t = gt.replace('- 供应集中：前五名供应商合计采购占比 47%，编码器与 IGBT 均无自供能力 [S1]', '- 供应集中：前五名供应商合计采购占比 47%，编码器与 IGBT 均无自供能力 [S1]\n- 控股股东计划减持不超过 2% 股份 [S2]')" \
  "E-BANWORD" 0
# 边界②：推荐语「建议增持」必须判红（与边界①成对，证明收窄没把该抓的也放掉）
edge "边界② 推荐语「建议增持」必红" \
  "t = gt.replace('- 供应集中：前五名供应商合计采购占比 47%，编码器与 IGBT 均无自供能力 [S1]', '- 供应集中：前五名供应商合计采购占比 47%，编码器与 IGBT 均无自供能力 [S1]\n- 建议增持 [S2]')" \
  "E-BANWORD" 1
# 边界③：财报状态写「已出」时，道五必须点名走姊妹件（不是只报形制错）
edge "边界③ 财报状态已出→道五点名" \
  "t = gt.replace('财报状态：未出（最近一期：2025 年报；本稿研究窗口为 2026 中报披露前）', '财报状态：已出（2026 中报已披露）')" \
  "cn-earnings-note" 1
# 边界④：财报状态写了个认不出的值（既非未出也非已出）→ 形制发红，不静默放行
edge "边界④ 财报状态值认不出→形制红" \
  "t = gt.replace('财报状态：未出（最近一期：2025 年报；本稿研究窗口为 2026 中报披露前）', '财报状态：待定')" \
  "认不出" 1
# 边界⑤：改数词「约 2.3 亿元」替数字打底 → 道三发红
edge "边界⑤ 改数词「约」替数字打底必红" \
  "t = gt.replace('标的 2025 年营业收入为 2.3 亿元 [S3]', '标的 2025 年营业收入约 2.3 亿元 [S3]')" \
  "改数" 1

echo "----"
echo "档数=5（由上面逐档现报）｜不合=$bad｜不可判=$unk"
if [ "$unk" -gt 0 ]; then echo "有档取值域故障，整趟按 3 读，不并入「不合」。"; exit 3; fi
if [ "$bad" -gt 0 ]; then exit 1; fi
exit 0
