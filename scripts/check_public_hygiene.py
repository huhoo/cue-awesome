#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_public_hygiene.py — 公开面卫生机检闸（CONTRIBUTING §公开面卫生 的可执行形，五禁逐条成码）。

发布包是给用户用的成品，不是施工日志。本闸把「五禁」变成可跑的正则＋指路存在性检查：
成品面命中即 ERROR，CHANGELOG 按留痕原则一律 WARN（历史条目不回改，人裁）。纯 stdlib、零网络。

用法：
    python3 scripts/check_public_hygiene.py              全仓跑（有 ERROR 则 exit 1）
    python3 scripts/check_public_hygiene.py --strict     WARN 也计入失败（提交前自用好）
    python3 scripts/check_public_hygiene.py --quiet      只报汇总与码表
    python3 scripts/check_public_hygiene.py --selftest   跑 scripts/fixtures/hygiene/ 正反守护样
                                                         （违例样必须发红、合规样必须发绿，
                                                          并双跑全仓报告取字节对拍验确定性）
    python3 scripts/check_public_hygiene.py --file PATH  只检单个文件（岗单/新票探针用；
                                                         文件路径决定它被当作哪一类面）
    python3 scripts/check_public_hygiene.py --list       列出被扫的面与各自规则数

五禁与码（详行先打码，再打面/行号/规格；末行「码表:」只列本次真正用到的码）：
    H-TICKET   ① 工单/票号内部流水（M1xx、PR#123 类）
    H-PATH     ② 工作区悬空路径（verify/ logs/ dispatch/ BOARD 等仓外或他目录指路）
    H-POINTER  ②b 包内相对指路目标不存在（assets/… references/… 等——机检可验的那一半）
    H-STATE    ③ 施工状态语（在途/证据票/候账/候 X 裁/随我铃/收卷/交卷/派单…）
    H-STALE    ③b 施工进度标签（P0 骨架／细化候×开单／仍待完善…）——**只判成品面**（历史条目不回改，见 CONTRIBUTING 留痕原则）
    H-DATE     ④ 内部时点戳（「截至 20xx」类过程日期；边界该直接写边界）
    H-ATTRIB   ⑤ 过程归因与账目叙事（需求凭据=/实测由 M1xx/账回/跑回/判词/VERIFIED…）
    H-GIFT-UNIT ⑥ §5-1 对外额度句**两个数字各自带单位**（触发串＝送 500／500…每日 10／500…signup·daily·per day；
               `500` 与 `10` 之后窗口内各须有「积分／credits」，**缺任一即发条**，命中文字＝那枚裸数字）
               ——**WARN 族**（不是五禁本体，报文里打「口径⑥」不打「五禁⑥」）：判据串显式列出，宽式子串重复禁用；
               射程限 README／SKILL 门面句与包内 references，assets／examples 模板与样例面不判；CHANGELOG 不判（逐码不入门）
    H-TOOL-PROMISE ⑦ §5-3 对外面文**不承诺固定工具清单、不叫用户按名直调**（工具名与入参 schema 一律以 catalog
               那份返回现值为准）。触发＝承诺语（A 集 17 枚：固定可用工具清单／工具清单如下／直接按名调用／内置工具／
               无需 catalog／fixed list／no catalog…）与**清单或工具名**（B 集 2 枚：动作前缀的 snake_case 名／「以下 N 枚」枚举形）
               **同线同现**才发条；C 集 12 枚限定语（以现值为准／以 catalog 为准／示例／不预先承诺…）同线则不报。
               **B 集是形状假设（M317c 补行）**：只认**以动作前缀开头**的 snake_case——①动作词不在段首
               （`alpha_get_quote`）、②名词式（`alpha_api`／`conv_id`）、③camelCase、④纯中文工具名，这四形
               **一律不匹配＝该报的不报**；这是为不在正当技术句上造假阳而做的**有意收窄，不是缺陷**，
               真名出现凭靶再扩、不预先宽。
               枚数一律现算自报（len），不手打。**WARN 族**（M317 先落在 WARN，抬不抬 ERROR 候现网走向）；
               射程与 CHANGELOG 逐码不入门与 ⑥ 同（共用 SCOPE_GATED）

面与分级（判据口径：能力句直述、指路可跟随、归因留内部）：
    成品面  SKILL*.md / README*.md（含仓根集合仓说明）/ assets/** / references/**  → 五禁全适用（含 ③b 子项），命中=ERROR
    CHANGELOG  CHANGELOG*.md                                                       → 守①③④⑤（②③b⑥⑦不在此面），命中=WARN
    逐码降级  WARN_CODES＝{H-GIFT-UNIT, H-TOOL-PROMISE}：这两支即便命中成品面也记 **WARN** 不记 ERROR——它们判的是「等他票补齐」的
              过渡态（M288 落字前应红、落字后归零），拿 ERROR 去卡会把整仓门钉死在别人名下的在途字上。
              计数因此**逐条走**（一枚面可同时出两档），表头显该面最重的一档。
    不检面  CONTRIBUTING*（贡献者文档，内部指路是它的职责）/ docs/ / scripts/ / NOTICE / LICENSE / .github
    「lead」一类英文产品词**不入词表**（cue-lead-pieces 的 lead pieces 是正式术语，入表即假阳）。

岗单周检与新票探针接法（照抄即可，勿改路径）：
    cd <仓根> && python3 -B scripts/check_public_hygiene.py --quiet; echo exit=$?          # 周检：整仓一道门
    cd <仓根> && python3 -B scripts/check_public_hygiene.py --selftest                      # 周检：闸本体非恒真
    cd <仓根> && python3 -B scripts/check_public_hygiene.py --file <包>/SKILL.md --strict    # 新票：只检本票改动的面
"""

from __future__ import annotations

import argparse
import hashlib
import os
import io
import re
import sys
import contextlib
from pathlib import Path

try:                                     # M423：description 必须结构化解析（票面硬约束③）
    import yaml
except ImportError:                      # noqa: BLE001
    yaml = None                          # 缺库⇒该尺响亮不可判，不静默通过

ROOT = Path(__file__).resolve().parent.parent
FIXDIR = ROOT / "scripts" / "fixtures" / "hygiene"

NON_SKILL_DIRS = {".github", "docs", "scripts", "assets", ".git", ".workbuddy", ".attic"}
SKIP_DIR_NAMES = {"__pycache__", "dist", "build", "node_modules", ".venv", "fixtures"}

# ---------------------------------------------------------------- 五禁规则表
# 每条：(码, 五禁项, 编译后正则, 人读规格)
# 词表只收「过程遥测」的确形：宁可窄而准，宽则由人另开票加词。

# M317（§5-3「live 状态以 catalog 为准、不硬编码工具名」这条红线此前**无机检**——来源＝6.1 的 M313-C3，lead 独立复现）：
#   新码 H-TOOL-PROMISE ⑦，三集分工，枚数一律现算自报（len(...)）：
#   A 承诺语＝命中文字（报出来的就是那一小段承诺）；B 清单/工具名＝同现条件（没有清单就没有「固定清单」这回事）；
#   C 限定语＝同线豁免（§5-3 允许的写法正是「以现值为准」那一族）。三集各逐枚给理由，见账 §2。
PROMISE_A_ITEMS = (
    r"固定可用工具清单", r"可用工具清单", r"工具清单(?:如下|固定为|为以下|是下面)", r"清单(?:如下|固定为)",
    r"以下[一二三四五六七八九十\d]+枚(?:工具|能力)", r"直接按名调用", r"按名调用(?:即可)?", r"直接调用即可",
    r"内置工具", r"自带工具", r"随包工具", r"无需(?:读取|查)?\s*catalog", r"不必(?:读取|查)?\s*catalog",
    r"no catalog", r"fixed(?: tool)? list", r"call (?:them|it) by name", r"hardcoded tool",
)
PROMISE_B_ITEMS = (
    r"(?<![A-Za-z0-9_])(?i:(?:get|list|search|fetch|query|read|write|run|call)_[a-z0-9]+(?:_[a-z0-9]+)*)(?![A-Za-z0-9_])",
    r"(?:以下|如下)\s*[一二三四五六七八九十\d]+\s*枚",
)
PROMISE_C_ITEMS = (
    r"以[^，。；\n]{0,12}现值为准", r"以\s*catalog\s*为准", r"以\s*discovery\s*为准",
    r"不作对外表述", r"不预先承诺", r"不作为承诺", r"示例", r"举例", r"可能变动", r"会变", r"非固定", r"不固定",
)
PROMISE_A = "(?i:" + "|".join(PROMISE_A_ITEMS) + ")"
PROMISE_B = "(?:" + "|".join(PROMISE_B_ITEMS) + ")"
PROMISE_C = "(?i:" + "|".join(PROMISE_C_ITEMS) + ")"

RULES = (
    ("H-TICKET", "①", re.compile(r"(?<![A-Za-z0-9])M\d{2,4}(?![A-Za-z0-9])|(?<![A-Za-z])PR\s*#?\d{2,}"),
     "成品面与 CHANGELOG 不写内部流水号（工单/票号/PR 号）；要引能力来源就写能力本身"),
    ("H-PATH", "②", re.compile(r"\bverify/|\blogs/|\bdispatch/|\bBOARD\b|(?<![\w_])dispatch(?![\w_])"),
     "仓外或他目录指路不得出现在成品面（verify/、logs/、dispatch/、BOARD）；指路只许相对本包"),
    ("H-STATE", "③", re.compile(r"在途|证据票|候账|候\s*(?:Owner|M\d|[1-6]\.1)|随我铃|收卷|交卷|派单|(?<!作)工单|候裁|候批|待你|等你一句"),
     "施工状态语禁入成品面（读者无从解释「在途/候账/随我铃」是什么意思）"),
    # ③b：施工进度标签——与 ③ 同族但词面不同（「P0 骨架」说的是包的状态，不是「在途」这类流程遥测）。
    # **只判成品面**：历史 CHANGELOG 条目里「由 P0 骨架重写为九节」是当时的 factual record，按留痕原则不判，
    # 故本码**不进 CHANGELOG_CODES**（那是整面豁免之外的逐码豁免，与留痕原则同一层）。
    ("H-STALE", "③b", re.compile(r"P[0-9]\s*骨架|骨架\s*·\s*设计权威|(?:仍是|尚是|还是|暂为|尚在)\s*(?:纯)?骨架"
                                  r"|(?:细化|完善|扩写|补全)\s*候\s*[^，。；、）)]{0,12}(?:开单|派单|开票)"
                                  r"|候\s*[^，。；、）)]{0,10}\s*(?:细化|完善|补全|开单)"
                                  r"|待(?:细化|补全|扩写|完善)|占位待(?:补|填)|TODO\s*[:：]|FIXME"),
     "③ 的子项：成品面不写施工进度标签（「P0 骨架」「细化候×开单」「仍待完善」「TODO:」类）——它写的是包的状态，不是能力；只判成品面"),
    ("H-DATE", "④", re.compile(r"截至\s*20\d{2}(?:[-/.年]\d{1,2}(?:[-/.日]\d{1,2})?)?|20\d{2}-\d{2}-\d{2}\s*(?:未立|未证|实测)"),
     "过程日期不写在墙上：能力边界直接写边界（「本件不做 X」），何时测的不进成品面"),
    ("H-ATTRIB", "⑤", re.compile(r"需求凭据|实测由|账回|跑回|判词|VERIFIED|派\s*[1-6]\.1|归\s*[1-6]\.1|据\s*[1-6]\.1|哨兵单枪|catalog-diff"),
     "过程归因与账目叙事禁入成品面（出处叙事进内部账；成品只写结论形制：能做什么/不能做什么/以什么为准）"),
    # ⑥：对外额度句缺单位。唯一许可句是 §5-1「注册送 500 积分、每日 10 积分，以服务端为准」——
    # 这条红线由闸守，不由 lead 的眼睛守（M289）。判据串**显式列出**，不用宽式：
    # 宽式「任意 ≥10 字子串同行重复」实测跑出 95 枚假红，猜串读出过一枚假缺（同日两枚教训）。
    # **M298 新 canon＝两个数字都要各自带单位**（Owner 令④「要单位」；旧写法是「行内任意处出现积分／credits
    # 即整行放行」，那一支全行负向前瞻比令宽——`500 积分、每日再 +10` 这种 10 裸着的并列形从此发条）。
    # 现形制：`500` 之后窗口（10 字内）须含单位、`10` 之后窗口须含单位，**缺一即发条**，命中文字就是那枚裸数字。
    # 已知抓不到、也不许为它改成跨行匹配：`500 积分、\n每日再 +10 积分` 这类**跨行句形**——尺按行匹配，
    # 此形由 4.1 的逐面判据守护（M298 票面③；改成跨行会牵动其它码的射程）。
    # 与 H-STALE 同族形制：**不进 CHANGELOG_CODES**；射程再限门面句与 references（见 GIFT_SCOPE_SKIP，
    # assets／examples 不在尺内＝**不得拿「全仓零命中」替这两个面签字**）。
    # M306（lead 21:14:56 逮到的两枚单因致盲）：①词表补「每天」与「每日」并列；②`送` 与 500 之间容许
    #   markdown 强调符——但**只容空白与 * _ ~ 这六类字符、上限 8 枚**，不是把 `[^\n]{0,n}` 放宽成整行放行
    #   （那正是今日 §10「要变红靠靶不靠扩射程」的反面）。判定窗（数字后 10 字内须含单位）与语义一字未动。
    # M308（lead 21:44:45 自造靶 T5 逮到的**放宽后新造假阳族**）：**第二支加「额度语境」前置要求**——频率相邻支
    #   须先出现额度族词才构成触发，族词全集九枚：注册／signup／sign-up／赠送／即送／充值／额度／积分／credits。
    #   M308-R1（lead 22:04:22 用靶 Z5「本件运送 500 份扫描件…」把我那句假定打回）：**第一支同样受语境约束**——
    #     裸「送」不再独立构成触发，须族词在其前 40 字内出现；这不是加词、是收门（九枚族词照 M308 定案不动）。
    #     我原先写的「第一支本身已含额度语义」是假定不是测数：运送／发送／派送／递送／输送 全都含裸「送」。
    #   M315（lead 22:45:28 用四枚英文靶把上一行那句假定打回）：**第三支同样受额度语境约束**——那句
    #     「第三支本身已要求英文额度词语」是没验过的假定：`daily`／`per day` 是**频率词**不是额度词，
    #     所以「The batch processes 500 pages daily and emits 10 summaries.」这类纯产量句照旧发红（＝假阳，
    #     与中文侧 Z5「运送 500 份扫描件」同一种病穿了英文衣裳）。改法与中文侧同形制、不自创第二套：
    #     拆成三枝——①`500…signup` 形自带开户义，不需额外语境；②频率形须**前置**英文额度词（40 字内）；
    #     ③频率形须**后置**英文额度词（40 字内）。后置这一枝不是冗余：英文里「Get 500 … per day, new
    #     accounts only」这类语序真实存在，只收前置会把已抓得住的开户句一起静掉＝覆盖缩。
    #     英文语境集十二枚（逐枚理由在 M315 账 §2）：signup／sign up／sign-up／new account／regist(er|ers|
    #     ered|ering|ration)／credit／bonus／free／grant／allowance／quota／top up／recharge。
    #     两处刻意不收并写明理由：`points`（评分面里到处是 points，收进来等于给非额度句开门）、
    #     `registry`（技术名词，故 regist 只接 er/ers/ered/ering/ration 五种后缀）；`trial`／`allocation`
    #     同因不收（「The trial processed 500 samples daily」正是 E1 那一型）。
    #     判定窗（数字后 10 字内须含单位）／命中组／WARN_CODES／GIFT_SCOPE_SKIP／CHANGELOG_CODES／
    #     severity() 照旧一字未动——本枝只加前置条件，不放宽任何窗口。
    #   残留限度如实记（中英同一条）：语境词是**必要非充分**——「赠送 500 份样本、每天出 10 条」这类量词歧义句、
    #   以及「Register the handler; the batch processes 500 pages daily」这类同线歧义句仍会触发；凭新靶再收，不放行整行。
    ("H-GIFT-UNIT", "⑥", re.compile(
        r"^(?=.*(?:(?:注册|signup|sign-up|赠送|即送|充值|额度|积分|credits)[^\n]{0,40}?送[\s*_~]{0,8}500"
        r"|(?:注册|signup|sign-up|赠送|即送|充值|额度|积分|credits)[^\n]{0,40}?500[^\n]{0,40}?(?:每日|每天)[^\n]{0,8}?(?:再\s*)?\+?10"
        r"|500[^\n]{0,90}?(?i:signup|sign[ -]up)"
        r"|(?i:signup|sign[ -]up|new account|regist(?:er|ers|ered|ering|ration)|credit|bonus|free|grant|allowance|quota|top[ -]?up|recharge)"
        r"[^\n]{0,40}?500[^\n]{0,90}?(?:daily|per day)"
        r"|500[^\n]{0,90}?(?:daily|per day)[^\n]{0,40}?"
        r"(?i:signup|sign[ -]up|new account|regist(?:er|ers|ered|ering|ration)|credit|bonus|free|grant|allowance|quota|top[ -]?up|recharge)))"
        r".*?(?P<hit>(?<![\d.,])500(?![\d])(?![^\n]{0,10}?(?:积分|(?i:credits)))"
        r"|(?<![\d.,])10(?![\d])(?![^\n]{0,10}?(?:积分|(?i:credits))))"),

     "对外额度句**两个数字都要带单位**（§5-1 许可句形：注册送 500 积分、每日 10 积分，以服务端为准）——任一枚裸着就是承诺，不是事实"),
    # ⑦（M317）：§5-3「工具名与入参 schema 一律以 catalog 那份返回现值为准、不硬编码工具名」这条红线此前无机检。
    #   触发＝A 承诺语 与 B 清单/工具名 **同线同现**；C 限定语同线则不报（那一族正是 §5-3 许可的写法）。
    #   与 ⑥ 同形制：不进 CHANGELOG_CODES（历史条目不回改，留痕原则同一层）；射程共用 GIFT_SCOPE_SKIP（assets／examples
    #   是模板与样例面，那里出现示例工具名不是对外承诺）；先 WARN 级，别一上来抬 ERROR。
    #   已知抓不到、也不许为它改成跨行匹配：「工具清单固定为以下三枚」把名字排在后一行时，本尺按行判、这一行仍发条
    #   （因为它自带「以下三枚」枚举形），但**纯靠下一行列名的那一形**抓不到——与 ⑥ 的跨行句形同一限度，归 4.1 逐面判据。
    #   B 集是**形状假设**（M317c 精度补行，lead 2026-10-20 验收注记＋我这一拍的单一变量扫描）：只认
    #     **以动作前缀开头**的 snake_case（get_/list_/search_/fetch_/query_/read_/write_/run_/call_ 打头）。四形**不匹配**＝该报的不报：
    #     ①动作词不在段首（`alpha_get_quote`——lookbehind 把中段咬住的那种挡住了）；②名词式 snake_case
    #     （`alpha_api`、`conv_id` 这类无前缀名）；③camelCase（`getLiveEquityQuote`）；④纯中文工具名（`实时行情`）。
    #     lead 验收时首组靶正是拿②试的，四枚全静、差点判成「B 集漏逮」；按单一变量重造（同一句承诺、只换名字形状）
    #     实测：`get_quote_alpha` 红／`alpha_get_quote` 静／`alpha_api` 静／`getLiveQuote` 静／`实时行情` 静／
    #     `get_quote_alpha、alpha_api` 红（一枚合形即报，一枚不合法名不掩住另一枚）。
    #     **这枚静是我为「不在 conv_id 那种正当技术句上造假阳」而做的有意收窄，不是缺陷**；真名出现凭靶再扩，不预先宽。
    #   同一条限度随之升成 §10（lead 落款）：报「漏逮」之前先做**形状敏感度扫描**（只改一个变量看它会不会红），
    #     并先读被检件自己的限度自述。
    ("H-TOOL-PROMISE", "⑦", re.compile(
        r"^(?=.*?(?P<hit>" + PROMISE_A + r"))"
        r"(?=.*?" + PROMISE_B + r")"
        r"(?![^\n]*(?:" + PROMISE_C + r"))"),
     "§5-3：对外面文不承诺固定工具清单、不叫用户按名直调——工具名与入参 schema 一律以 catalog 那份返回现值为准"),
)

SKIP_OUTPUT_POINTERS: list[tuple[str, int, str]] = []
EXEMPT_DISCARDED: list[tuple[str, str]] = []   # 因窄化被弃用的测试面同名件命中（报账用，不静默吞）

CHANGELOG_CODES = {"H-TICKET", "H-STATE", "H-DATE", "H-ATTRIB"}  # CHANGELOG 面**逐码**判这四支（①③④⑤）；
#   ②（H-PATH／H-POINTER）与 ③b（H-STALE）、⑥（H-GIFT-UNIT）、⑦（H-TOOL-PROMISE）不在此面判——
#   **逐码不入门**是豁免的唯一形制，没有「整面豁免」这种口子（M258 裁定，M289 沿用，M317 再加一支）。
WARN_CODES = {"H-GIFT-UNIT", "H-TOOL-PROMISE"}    # ⑥⑦即便命中成品面也记 WARN：它判的是「等他票补齐」的过渡态，
#   用 ERROR 会把整仓门卡死在别人名下的在途字上；归零与否看 WARN 计数走向，不看门是否红。
GIFT_SCOPE_SKIP = ("assets", "examples")   # ⑥⑦共用的射程：README／SKILL 门面句＋包内 references；模板面与样例面不判
SCOPE_GATED = {"H-GIFT-UNIT", "H-TOOL-PROMISE"}   # 走上面那条射程的两支码（M317 起不再只有 ⑥）
LEGEND = {c: spec for c, _, _, spec in RULES}
LEGEND["H-POINTER"] = "包内相对指路目标不存在——要么补文件，要么删指路；不许留断链"

# M423（BOARD M416 裁定③）：**卡面前 160 字符不得出现安装动作串**——安装式的正式来路是仓根与渠道安装字段。
# 形制（M289 同族）：串集合**写死**、逐枚报命中字符位；取数走**结构化**（PyYAML 解析 frontmatter 再切前 160，
# 不按行正则扫 SKILL.md）；分层＝**只判活面 SKILL.md 的 description**——历史 CHANGELOG 条目与票面自引用不判。
INSTALL_FACE_CODE = "H-INSTALL-FACE"
INSTALL_FACE_LIMIT = 160
INSTALL_FACE_PATTERNS = ("npx skills add", "curl -L -o", "git clone")
INSTALL_FACE_SPEC = (f"description 中**起始于**前 {INSTALL_FACE_LIMIT} 字符的安装动作串不得出现"
                     f"（起点<{INSTALL_FACE_LIMIT}，**尾部可跨界**；写死集合：{'／'.join(INSTALL_FACE_PATTERNS)}）；"
                     f"安装式的正式来路＝仓根与渠道安装字段；散文引路「装：」**不享豁免**——只判命令串本身，"
                     f"命令串起于窗口内照样红（靶：prose 样与活体 sector-overview）")
LEGEND[INSTALL_FACE_CODE] = INSTALL_FACE_SPEC


def hit_of(m) -> str:
    """命中文字：尺子带命名组 `hit` 就报那一小段（⑥的行首否证要吃掉前缀，不能把整行当命中），
    其余码没有这组，逐字节照旧报整段匹配。"""
    g = m.groupdict().get("hit")
    return g if g else m.group(0)


def ban_label(code: str) -> str:
    """报文里的族名前缀：①〜⑤（含 ②b／③b 子项）是五禁本体；⑥是 §5-1 口径校验，不冒充「五禁⑥」。"""
    return "口径" if code in ("H-GIFT-UNIT", "H-TOOL-PROMISE") else "五禁"


def severity(face: str | None, code: str) -> str:
    """面与码两头定级：成品面=ERROR、CHANGELOG=WARN；WARN_CODES 里的码不分面一律 WARN。
    一枚文件可以同时出两种级别，所以计数按**逐条**走，表头只显示该面最重的一档。"""
    if code in WARN_CODES:
        return "WARN"
    return "ERROR" if face == "product" else "WARN"

# 指路提取：markdown 链接目标 + 反引号内的相对路径形
MD_LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
BACKTICK_PATH = re.compile(r"`((?:assets|references|scripts|docs)/[^`\s]+)`")
PLACEHOLDER = re.compile(r"[<>*{}××…_|\s]|\d{3,}")
# 运行时产出路径的两种信号：行内有出生动词，或同名的东西在包里别处存在（模板/范例副本）。
OUTPUT_VERB = re.compile(r"写\s*`|交付物|产出|生成|落盘|输出|模板\s*=|写入")


# ---------------------------------------------------------------- 面分类
def classify(path: Path) -> str | None:
    """返回 'product'（成品面）|'changelog'|None（不检/仓外）。入参可为仓外路径：判 None 交调用方从严。"""
    try:
        parts = path.resolve().relative_to(ROOT).parts
    except ValueError:
        return None
    if any(p in SKIP_DIR_NAMES for p in parts[:-1]):
        return None
    name = path.name
    if len(parts) == 1:  # 仓根文件
        if name.startswith("README"):
            return "product"
        return None
    if name.startswith("CONTRIBUTING") or name in {"NOTICE.md", "LICENSE.md"}:
        return None
    if name.startswith("CHANGELOG"):
        return "changelog"
    if name.startswith("SKILL") or name.startswith("README"):
        return "product"
    if "assets" in parts or "references" in parts:
        return "product"
    return None


def gift_scope_ok(path: Path) -> bool:
    """⑥射程（M289 票面）：门面句 README／SKILL 与包内 references 判；assets／examples 不判。
    仓外路径按成品面从严判那条路照旧给判——射程收的是包内模板与样例面，不是「仓外免检」。"""
    try:
        parts = path.resolve().relative_to(ROOT).parts
    except ValueError:
        return True
    return not any(seg in GIFT_SCOPE_SKIP for seg in parts[1:-1])


def iter_faces() -> list[Path]:
    out = []
    for path in sorted(ROOT.rglob("*.md")):
        if classify(path) is not None:
            out.append(path)
    return out


# ---------------------------------------------------------------- ②b 指路存在性
def _pkg_root(path: Path) -> Path:
    """本包根目录：仓根文件→仓根；否则顶层 skill 目录。仓外路径→该文件所在目录。"""
    try:
        rel = path.resolve().relative_to(ROOT)
    except ValueError:
        return path.parent
    return ROOT if len(rel.parts) == 1 else ROOT / rel.parts[0]


def _resolves(pkg: Path, own: Path, rel: str) -> bool:
    """指路可跟随 = 相对本包根 或 相对本文件目录 任一命中（`../` 原样交给路径解析，不手剥）；
    无扩展名时按前缀唯一匹配（`references/01` 这类简写能对上 01-xxx.md 就不算断链）。"""
    cands = []
    for base in (own, pkg):
        target = (base / rel).resolve()
        cands.append(target)
        if not rel.endswith("/") and target.suffix == "":
            cands.extend(sorted(target.parent.glob(target.name + "*")))
    for c in cands:
        if rel.endswith("/") or c.suffix == "":
            if c.is_dir():
                return True
        elif c.is_file():
            return True
    return False


TESTISH_SEGMENTS = {"fixtures", "tests", "samples", "examples"}   # M242：测试与样例面的同名件是**语料**，不给指路背书


def _basename_elsewhere(pkg: Path, rel: str, own: Path, text_path: Path):
    """同名件在包内**非测试面**别处存在 → 多半是运行时产出路径或范例副本，不当断链。
       M242 窄化：命中路径（相对包根）任一段属 fixtures／tests／samples／examples 时**不算豁免**——
       否则任何包把同名件丢进测试语料就能盖住真断链（dd 散件时代 29 枚 `coverage-map.md` 正是这形，
       当时把面上两枚真断链洗白成 0 条；lead 10-17 重测确认现值上这条已不再被求值，故窄化零代价）。
       返回 True／False，并把「因测试面而被弃用的命中数」记进 EXEMPT_DISCARDED（报账可查，不静默）。"""
    name = Path(rel).name
    if not name or name.count(".") < 1:
        return False
    for cand in pkg.rglob(name):
        if cand == text_path:
            continue
        try:
            parts = {x.lower() for x in cand.relative_to(pkg).parts[:-1]}
        except ValueError:
            parts = {x.lower() for x in cand.parts}
        if parts & TESTISH_SEGMENTS:
            EXEMPT_DISCARDED.append((rel, cand.relative_to(pkg).as_posix()))
            continue
        return True
    return False


def _pointers(text: str, pkg: Path, own: Path, as_file: Path | None = None) -> list[tuple[int, str, str]]:
    """返回 (行号, 指路串, 原因)。只判本包目录内的指路；他目录由 H-PATH 管。
    判为运行时产出路径的记进 skipped（报告尾行公开计数，不静默吞）。"""
    out = []
    for lineno, line in enumerate(text.split("\n"), 1):
        cands = {m.group(1) for m in MD_LINK.finditer(line)} | {m.group(1) for m in BACKTICK_PATH.finditer(line)}
        for cand in sorted(cands):
            t = cand.strip("<>\"'()（）,，。;；")
            if not t or t.startswith(("#", "http", "mailto:", "/")):
                continue
            if not re.match(r"^(?:\.\./)*(?:assets|references|scripts|docs)/", t):
                continue
            if PLACEHOLDER.search(t):
                continue  # 模板占位与通配不算指路（assets/××.md 类）
            if _resolves(pkg, own, t):
                continue
            born = bool(OUTPUT_VERB.search(line))
            if born or _basename_elsewhere(pkg, t, own, as_file or own / t.name):
                SKIP_OUTPUT_POINTERS.append((lineno, t, "出生动词" if born else "非测试面同名件"))
                continue
            out.append((lineno, t, "本包根与本文件目录两侧都找不到目标"))
    return out


def check_pointers(path: Path, text: str) -> list[tuple[int, str, str]]:
    return _pointers(text, _pkg_root(path), path.parent, path)


# ---------------------------------------------------------------- 单文件检查
def check_install_face(path: Path, text: str) -> list[tuple[str, int, str]]:
    """M423：卡面前 160 安装式尺。**只判活面 SKILL.md 的 description**（PyYAML 结构化后切前 160），
       历史 CHANGELOG 条目与票面自引用不判；串集合写死、命中报字符位；缺库/解析失败⇒响亮不可判。"""
    if path.name != "SKILL.md":
        return []
    if yaml is None:
        return [(INSTALL_FACE_CODE, 1, "PyYAML 不在场——本尺不可判（不静默通过）")]
    m = re.match(r"\A---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|\Z)", text, re.S)
    if not m:
        return []
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except Exception as exc:                                      # noqa: BLE001
        return [(INSTALL_FACE_CODE, 1, f"frontmatter 解析失败：{exc}——本尺不可判（不猜）")]
    desc = fm.get("description") if isinstance(fm, dict) else None
    if not isinstance(desc, str) or not desc:
        return []
    out = []
    low = desc.casefold()
    for pat in INSTALL_FACE_PATTERNS:
        i = low.find(pat.casefold())
        if 0 <= i < INSTALL_FACE_LIMIT:          # M428：按**起点**判——起点在窗口内、尾部跨界也算（店卡会截半截）
            tail = '（尾部跨界）' if i + len(pat) > INSTALL_FACE_LIMIT else ''
            out.append((INSTALL_FACE_CODE, 1,
                        f"description 起于前 {INSTALL_FACE_LIMIT} 字符内的安装动作串「{pat}」@字符位 {i}{tail}"
                        f"（规格：{INSTALL_FACE_SPEC}；分层：只判活面 SKILL.md，历史条目与票面自引用不判）"))
    return out


def check_file(path: Path) -> list[tuple[str, int, str]]:
    """返回 [(码, 行号, 详句)] 三元组——**severity 不在这里出**，由调用方按面与码定（`severity(face, code)`）。
    （M271：本函数标注曾写四元组、实返三元组，按标注解包必 `ValueError`——是标注骗人，不是接口少了一项。）"""
    face = classify(path)
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.split("\n")
    finds: list[tuple[str, int, str]] = []

    if face == "product":
        for lineno, ptr, why in check_pointers(path, text):
            finds.append(("H-POINTER", lineno, f"包内指路 `{ptr}` {why}（规格：{LEGEND['H-POINTER']}）"))
        finds.extend(check_install_face(path, text))

    for code, ban, pat, spec in RULES:
        if face == "changelog" and code not in CHANGELOG_CODES:
            continue
        if code in SCOPE_GATED and not gift_scope_ok(path):
            continue
        for lineno, line in enumerate(lines, 1):
            for m in pat.finditer(line):
                finds.append((code, lineno, f"{ban_label(code)}{ban}命中「{hit_of(m)}」（规格：{spec}）"))
                break  # 每行每码只报一次，报告不被同一行刷屏
    return sorted(finds, key=lambda x: (x[1], x[0]))


# ---------------------------------------------------------------- 全仓跑
def run_repo(strict: bool, quiet: bool) -> tuple[int, int, int]:
    SKIP_OUTPUT_POINTERS.clear()
    EXEMPT_DISCARDED.clear()
    faces = iter_faces()
    errors = warnings = 0
    used_codes: set[str] = set()
    per_file: list[tuple[Path, str, list]] = []

    for f in faces:
        face = classify(f)
        finds = check_file(f)
        if not finds:
            continue
        sevs = {severity(face, code) for code, _, _ in finds}
        sev = "ERROR" if "ERROR" in sevs else "WARN"   # 表头显最重一档；计数逐条走（一枚面可两档同出）
        per_file.append((f, sev, finds))
        for code, _, _ in finds:
            used_codes.add(code)
            if severity(face, code) == "ERROR":
                errors += 1
            else:
                warnings += 1

    if not quiet:
        print(f"公开面卫生机检 — 被扫面 {len(faces)} 个（{sum(1 for p in per_file)} 个有发现）\n")
        rel = ROOT
        for f, sev, finds in per_file:
            print(f"  {sev:<5} {f.relative_to(rel)}（{len(finds)} 条）")
            for code, lineno, detail in finds:
                print(f"        [{code}] 第 {lineno} 行：{detail}")
        print()
        print("  码表: " + "; ".join(f"{c}→{LEGEND[c]}" for c in sorted(used_codes)))

    _born = sum(1 for x in SKIP_OUTPUT_POINTERS if x[2] == "出生动词")
    _twin = sum(1 for x in SKIP_OUTPUT_POINTERS if x[2] == "非测试面同名件")
    print(f"指路附账：判为运行时产出路径而跳过 {len(SKIP_OUTPUT_POINTERS)} 条（出生动词 {_born}／非测试面同名件 {_twin}）"
          f"；因窄化被弃用的测试面同名件命中 {len(EXEMPT_DISCARDED)} 次（这类不再算豁免）")
    print(f"\nsummary: 面 {len(faces)}，ERROR {errors}，WARN {warnings}"
          + ("（--strict：WARN 计入失败）" if strict and warnings else ""))
    if errors:
        return 1
    if strict and warnings:
        return 1
    return 0


# ---------------------------------------------------------------- 守护样自测
def _fixture_findings(dirpath: Path) -> list[tuple[str, int, str, str]]:
    """守护样内 check_pointers 需要 pkg 基准，这里按目录直扫（复刻面判定，不依赖 ROOT 分类）。"""
    finds: list[tuple[str, int, str, str]] = []
    for f in sorted(dirpath.rglob("*.md")):
        text = f.read_text(encoding="utf-8", errors="replace")
        is_changelog = f.name.startswith("CHANGELOG")
        for lineno, line in enumerate(text.split("\n"), 1):
            for code, ban, pat, spec in RULES:
                if is_changelog and code not in CHANGELOG_CODES:
                    continue
                m = pat.search(line)
                if m:
                    finds.append((code, lineno, f.name, f"{ban}命中「{hit_of(m)}」"))
        if not is_changelog:
            for lineno, ptr, why in _pointers(text, dirpath, f.parent, f):
                finds.append(("H-POINTER", lineno, f.name, f"`{ptr}` {why}"))
    return finds


def _pointers_in(pkg: Path, f: Path, text: str) -> list[tuple[int, str, str]]:
    out = []
    for lineno, line in enumerate(text.split("\n"), 1):
        cands = {m.group(1) for m in MD_LINK.finditer(line)} | {m.group(1) for m in BACKTICK_PATH.finditer(line)}
        for cand in sorted(cands):
            t = cand.strip("<>\"'()（）,，。;；")
            if not t or t.startswith(("#", "http", "mailto:", "/")):
                continue
            if not re.match(r"^(?:\.\./)?(?:assets|references|scripts|docs)/", t):
                continue
            if PLACEHOLDER.search(t):
                continue
            rel = t[3:] if t.startswith("../") else t
            target = pkg / rel
            if rel.endswith("/") or target.suffix == "":
                if not target.is_dir():
                    out.append((lineno, t, "目录不存在"))
            elif not target.is_file():
                out.append((lineno, t, "目标文件不存在"))
    return out


def selftest() -> int:
    """三档自跑（C-53）：① 违例样必须每禁发红；② 合规样必须零发条；③ 全仓报告双跑字节一致。

    缺任一方向，绿灯就是假绿（恒真检查必然全过）。
    """
    ok = True
    bad = FIXDIR / "bad"
    good = FIXDIR / "good"
    if not bad.is_dir() or not good.is_dir():
        print(f"SELFTEST FAIL: 守护样目录缺失（{bad} / {good}）")
        return 1

    SKIP_OUTPUT_POINTERS.clear()
    EXEMPT_DISCARDED.clear()
    bad_f = _fixture_findings(bad)
    bad_codes = {c for c, _, _, _ in bad_f}
    want = {c for c, _, _, _ in RULES} | {"H-POINTER"}
    print(f"档① 违例样：应发红，实发 {len(bad_f)} 条，覆盖禁项 {len(bad_codes & want)}/{len(want)}")
    for c in sorted(want - bad_codes):
        print(f"   未发红 → {c}（守护样没种下这一禁，或词表漏了它）")
        ok = False

    # 档①b 分级面正确：bad/CHANGELOG.md 必须发红 ①③④⑤ 之一，且绝不判 ②（charter 只列 ①③④⑤）
    cl = [x for x in bad_f if x[2] == "CHANGELOG.md"]
    cl_codes = {c for c, _, _, _ in cl}
    if not (cl_codes & CHANGELOG_CODES):
        print("   CHANGELOG 面未发红 → 分级失效（历史条目留痕通道没接住票号）")
        ok = False
    if cl_codes & {"H-PATH", "H-POINTER"}:
        print(f"   CHANGELOG 面误判 ②：{sorted(cl_codes & {'H-PATH', 'H-POINTER'})}（章程 CHANGELOG 只守 ①③④⑤）")
        ok = False
    print(f"档①b CHANGELOG 面：发红 {len(cl)} 条，码 {sorted(cl_codes)}，②不判={'对' if not (cl_codes & {'H-PATH','H-POINTER'}) else '错'}")

    # 档②′ M220⑦：正反样成对——YAML 键名行必须零发条，真悬空 dispatch/ 路径必须发红
    yk = good / "references" / "yaml-keys.md"
    dg = bad / "assets" / "dangling-dispatch.md"
    if not (yk.is_file() and dg.is_file()):
        print("   缺 M220⑦ 形态对样（yaml-keys.md / dangling-dispatch.md）→ 词面误拦无回归防线")
        ok = False
    else:
        d_hit = [x for x in bad_f if x[0] == "H-PATH" and "dispatch/" in x[3]]
        y_hit = [x for x in _fixture_findings(good) if x[2].endswith("yaml-keys.md")]
        print(f"档②′ 词面鉴别力：真悬空 dispatch/ 发红 {len(d_hit)} 条＝{'对' if d_hit else '错（被窄化放掉了）'}；"
              f"YAML 键名样发条 {len(y_hit)} 条＝{'对' if not y_hit else '错（workflow_dispatch 又被误拦）'}")
        if not d_hit or y_hit:
            ok = False

    # 档④／档⑤（M242：把「同名件在包内别处存在」这半条豁免窄化到不认测试与样例面）
    dt = bad / "assets" / "dangling-twin.md"
    dtf = [x for x in bad_f if x[2].endswith("dangling-twin.md") and x[0] == "H-POINTER"]
    old_would_exempt = any(c.name == "unit-twin.md" and c != dt for c in bad.rglob("unit-twin.md"))
    discarded = [d for d in EXEMPT_DISCARDED if d[1].startswith(("scripts/fixtures/", "fixtures/", "tests/", "samples/", "examples/"))]
    ok4 = len(dtf) == 1 and old_would_exempt and bool(discarded)
    print(f"档④ 反例必红（洗白路径已拆）：改前口径会豁免＝{'是' if old_would_exempt else '否'}"
          f"｜改后该面发红 {len(dtf)} 条（期望 1）｜被弃用的测试面命中 {len(discarded)} 次"
          f"＝{'对' if ok4 else '错（要么没拆死，要么拆过了头）'}")
    if not ok4:
        ok = False

    tw = good / "references" / "twin-exempt.md"
    twf = [x for x in _fixture_findings(good) if x[2].endswith("twin-exempt.md")]
    still_exempt = _basename_elsewhere(good, "references/台账甲.md", good / "references", tw)
    ok5 = not twf and still_exempt
    print(f"档⑤ 正例仍绿（不许过窄）：同名件在非测试面（assets/）时豁免＝{'仍成立' if still_exempt else '被误删'}"
          f"｜该面发条 {len(twf)} 条（期望 0）＝{'对' if ok5 else '错（正当豁免被动了，会造成假红）'}")
    if not ok5:
        ok = False

    # 档⑥（M258：③b 施工进度标签——成品面必红、CHANGELOG 面不判，两向同取自测夹具）
    # 点名用**内容锚**（夹具里带「P0 骨架」的那一行），不押「行号＝末行」：夹具日后加行就会假红/假绿。
    st_bad = [x for x in bad_f if x[0] == "H-STALE" and x[2].endswith("SKILL.md")]
    st_cl = [x for x in bad_f if x[0] == "H-STALE" and x[2].endswith("CHANGELOG.md")]
    st_lines = (bad / "SKILL.md").read_text(encoding="utf-8", errors="replace").splitlines()
    st_at = [i for i, ln in enumerate(st_lines, 1) if "P0 骨架" in ln]
    st_named = next((x for x in st_bad if x[1] in st_at), None)
    ok6 = bool(st_bad) and not st_cl and bool(st_at) and st_named is not None
    print(f"档⑥ ③b 施工进度标签：成品面发红 {len(st_bad)} 条（期望 ≥1）｜点名到带「P0 骨架」的行（第 {'/'.join(map(str, st_at)) or '—'} 行）＝{'是' if st_named else '否'}"
          f"｜CHANGELOG 面发条 {len(st_cl)} 条（期望 0，留痕原则）＝{'对' if ok6 else '错'}")
    if not ok6:
        ok = False

    # 档⑦（M289 立尺、M298 收 canon：⑥ 两个数字各自带单位——成品面必红、并列裸 10 也必红、
    #        CHANGELOG 面不判、正例只留「两数都带单位」那形、射程与逐码降级都验）
    gu_bad = [x for x in bad_f if x[0] == "H-GIFT-UNIT" and x[2].endswith("SKILL.md")]
    gu_cl = [x for x in bad_f if x[0] == "H-GIFT-UNIT" and x[2].endswith("CHANGELOG.md")]
    gu_good = [x for x in _fixture_findings(good) if x[0] == "H-GIFT-UNIT"]
    gu_lines = (bad / "SKILL.md").read_text(encoding="utf-8", errors="replace").splitlines()
    ln_both = [i for i, x in enumerate(gu_lines, 1) if "送 500、每日 10" in x]           # 两数全裸那行（内容锚）
    ln_par = [i for i, x in enumerate(gu_lines, 1) if "500 积分、每日再 +10" in x]         # 并列裸 10 那行（内容锚）
    gu_anchor = [x for x in gu_bad if x[1] in ln_both and "命中「500」" in x[3]]
    gu_parallel = [x for x in gu_bad if x[1] in ln_par and "命中「10」" in x[3]]
    scope_ok = (gift_scope_ok(ROOT / "demo" / "README.md") and gift_scope_ok(ROOT / "demo" / "references" / "r.md")
                and not gift_scope_ok(ROOT / "demo" / "assets" / "t.md")
                and not gift_scope_ok(ROOT / "demo" / "examples" / "e" / "SKILL.md"))
    sev_ok = (severity("product", "H-GIFT-UNIT") == "WARN" and severity("product", "H-STATE") == "ERROR"
              and severity("changelog", "H-STATE") == "WARN" and "H-GIFT-UNIT" not in CHANGELOG_CODES)
    ok7 = bool(gu_bad) and not gu_cl and not gu_good and bool(gu_anchor) and bool(gu_parallel) and scope_ok and sev_ok
    print(f"档⑦ ⑥ 额度句两数各自带单位：成品面发红 {len(gu_bad)} 条（期望 ≥2）"
          f"｜两数全裸那行（第 {'/'.join(map(str, ln_both)) or '—'} 行）点到「500」＝{'是' if gu_anchor else '否'}"
          f"｜并列裸 10 那行（第 {'/'.join(map(str, ln_par)) or '—'} 行）点到「10」＝{'是' if gu_parallel else '否（M298 的 canon 没落进尺里）'}"
          f"｜CHANGELOG 面 {len(gu_cl)} 条（期望 0，逐码不入门）｜合规样 {len(gu_good)} 条发条（期望 0：中文两数带单位／英文两数带 credits）"
          f"｜射程 assets·examples 不判＝{'对' if scope_ok else '错'}（**这两个面零命中不等于它们合规，别拿全仓零命中替它们签字**）"
          f"｜逐码分级 WARN 族＝{'对' if sev_ok else '错'}｜本档={'对' if ok7 else '错'}")
    if not ok7:
        ok = False

    # 档⑧（M306 两枚单因 → M308／M308-R1 语境门 → M312 常驻两向）：**双态断言＋枚数一律现算自报**（禁手打计数）。
    #   红组五枚（含 M312 新加「两数皆裸哨兵」）、零组八枚（含 M312 新加 派送／递送／输送三行），
    #   锚点全部按**正文子串**匹配——标签一律不许自含九枚族词（M308 那枚「靶面自污」学到的规矩，落样前逐行自查过）。
    #   一旦离谱，打印句直接点名是哪几枚锚点、在哪一行离的谱（M312 判据③的两种回退都靠这句自证）。
    RED_ANCHORS = [("合形·送＋粗＋每天裸10", "每天再 **+10**，以服务端为准", "10"),
                   ("无送·每天形", "每天再 **+10** 的名额", "500"),
                   ("注册·每天裸10", "注册 500 积分，此后每天再 **+10**", "10"),
                   ("注册送两数皆裸", "注册送 500、每天 10", "500"),
                   ("哨兵·即送两数皆裸", "新账号即送 500，每天再 +10。", "500"),
                   ("英文裸数红样甲·频率词在后", "New accounts get 500 and 10 daily", "500"),
                   ("英文裸数红样乙·短语在数前", "you get 500 plus 10 per day", "500")]
    ZERO_ANCHORS = [("正例·加粗带单位", "每天再 **+10 积分**"), ("正例·无加粗带单位", "每天再 +10 积分"),
                    ("频率相邻哨兵", "都要备份 **500** 份日志"), ("量词靶·跑批页数", "跑批 500 页扫描件"),
                    ("裸送靶·运送", "运送 500 份扫描件"), ("线路量词·派送", "站点派送 500 单"),
                    ("线路量词·递送", "仓库递送 500 箱"), ("线路量词·输送", "管线输送 500 吨"),
                    ("英文产量零样·证英文语境门收窄", "processes 500 pages daily"),
                    ("英文带单位正例·必然零（单位紧贴数）", "500 credits plus 10 credits")]
    gu8_lines = (bad / "SKILL.md").read_text(encoding="utf-8", errors="replace").splitlines()
    good8_lines = (good / "SKILL.md").read_text(encoding="utf-8", errors="replace").splitlines()
    red_rows, red_missing = [], []
    for label, frag, want in RED_ANCHORS:
        ls = [x for x, v in enumerate(gu8_lines, 1) if frag in v]
        got = [x for x in gu_bad if x[1] in ls and f"命中「{want}」" in x[3]]
        red_rows.append((label, ls, want, bool(got)))
        if not ls or not got:
            red_missing.append(f"{label}@行{'/'.join(map(str, ls)) or '锚缺'}（期望点「{want}」）")
    zero_rows, zero_off = [], []
    for label, frag in ZERO_ANCHORS:
        ls = [x for x, v in enumerate(good8_lines, 1) if frag in v]
        got = [x for x in gu_good if x[1] in ls]
        zero_rows.append((label, ls, bool(got)))
        if not ls:
            zero_off.append(f"{label}（锚点缺失）")
        elif got:
            n = got[0][3]
            seg = n[n.find("命中"):n.find("命中") + 11]
            zero_off.append(f"{label}@第{'/'.join(map(str, ls))} 行发条「{seg}」")
    red_detail = [(l, ('/'.join(map(str, n)) or '—'), w, '红' if h else '未中') for l, n, w, h in red_rows]
    zero_detail = [(l, ('/'.join(map(str, n)) or '—'), ('发条' if h else '静')) for l, n, h in zero_rows]
    # M315 加的一条硬线（lead 22:45）：**打印面与现算枚数同拍比对，不等即 selftest 红**——
    #   防的是「同形重叠把两枚算成一枚」或有人给明细串加 `[:N]` 截断，那时面上仍写「红组 N 枚」而清单已短。
    n_red_rendered = str(red_detail).count("('")
    n_zero_rendered = str(zero_detail).count("('")
    count_off = []
    if n_red_rendered != len(RED_ANCHORS):
        count_off.append(f"红组明细串 {n_red_rendered} 条 ≠ 现算 {len(RED_ANCHORS)} 枚")
    if n_zero_rendered != len(ZERO_ANCHORS):
        count_off.append(f"零组明细串 {n_zero_rendered} 条 ≠ 现算 {len(ZERO_ANCHORS)} 枚")
    ok8 = not red_missing and not zero_off and not count_off
    print(f"档⑧ 语境门双态（枚数现算）：红组 {len(RED_ANCHORS)} 枚／该面发红 {len(gu_bad)} 条／逐枚点名到位＝{'是' if not red_missing else '否'}"
          f"｜零组 {len(ZERO_ANCHORS)} 枚／越界发条 {len([z for z in zero_off if '发条' in z])} 枚（期望 0）"
          f"｜明细条数与现算枚数同拍＝{'是' if not count_off else '否'}（红 {n_red_rendered}/{len(RED_ANCHORS)}／零 {n_zero_rendered}/{len(ZERO_ANCHORS)}）"
          f"｜红组明细＝{red_detail}"
          f"｜零组明细＝{zero_detail}"
          + ("" if ok8 else f"｜**离谱者**：红组缺＝{red_missing or '无'}｜零组越界＝{zero_off or '无'}｜条数对拍＝{count_off or '无'}"))
    if not ok8:
        ok = False

    # 档⑨（M317 新码 H-TOOL-PROMISE ⑦）：形制照档⑧——**锚点按正文子串、枚数与明细条数一律现算**，
    #   红组逐枚点名「命中文字就是那一小段承诺」，零组里既有「证 C 集豁免在场」的可翻转靶，
    #   也有「必然零（无 A）、不证判别」的对照靶——两类并列标注性质，不混成一个「零组全绿」。
    TP_BAD = [("注入形·命中在清单承诺语", "固定可用工具清单：get_live_equity_quote", "固定可用工具清单"),
              ("直调口吻·命中在内置工具", "本包内置工具 get_xxx", "内置工具"),
              ("枚举形·命中在 catalog 否定", "工具清单固定为以下三枚", "无需读取 catalog"),
              ("中英混排·命中在 fixed list", "（fixed list）：get_live_equity_quote", "fixed list")]
    TP_ZERO = [("限定语同线·证 C 集豁免在场", "工具清单如下（示例", "可翻转：摘掉 C 豁免它必红"),
               ("现值口径句·无承诺语", "以那份返回现值为准", "必然零（A 不命中）——不证判别"),
               ("不承诺句·无承诺语", "工具清单以现值为准、不预先承诺", "必然零（A 不命中）"),
               ("技术名词句·无承诺语", "registry 列 500 entries", "必然零（A 不命中）"),
               ("只给清单不给承诺·证同现", "安装步骤如下三枚", "可翻转：只给 B 不给 A 必须零（A∧B 不是任一）")]
    tp_bad = [x for x in bad_f if x[0] == "H-TOOL-PROMISE" and x[2].endswith("SKILL.md")]
    tp_good = [x for x in _fixture_findings(good) if x[0] == "H-TOOL-PROMISE"]
    tp_red_rows, tp_red_missing = [], []
    for label, frag, want in TP_BAD:
        ls = [i for i, v in enumerate(gu8_lines, 1) if frag in v]
        got = [x for x in tp_bad if x[1] in ls and f"命中「{want}」" in x[3]]
        tp_red_rows.append((label, ls, want, bool(got)))
        if not ls or not got:
            tp_red_missing.append(f"{label}@行{'/'.join(map(str, ls)) or '锚缺'}（期望命中「{want}」）")
    tp_zero_rows, tp_zero_off = [], []
    for label, frag, nature in TP_ZERO:
        ls = [i for i, v in enumerate(good8_lines, 1) if frag in v]
        got = [x for x in tp_good if x[1] in ls]
        tp_zero_rows.append((label, ls, nature, bool(got)))
        if not ls:
            tp_zero_off.append(f"{label}（锚点缺失）")
        elif got:
            d = got[0][3]
            seg = d[d.find("命中"):d.find("命中") + 22]
            tp_zero_off.append(f"{label}@第{'/'.join(map(str, ls))} 行发条「{seg}」")
    tp_red_detail = [(l, ('/'.join(map(str, n)) or '—'), w, '红' if h else '未中') for l, n, w, h in tp_red_rows]
    tp_zero_detail = [(l, ('/'.join(map(str, n)) or '—'), ('发条' if h else '静')) for l, n, _, h in tp_zero_rows]
    n_tp_red = str(tp_red_detail).count("('")
    n_tp_zero = str(tp_zero_detail).count("('")
    tp_count_off = []
    if n_tp_red != len(TP_BAD):
        tp_count_off.append(f"红组明细串 {n_tp_red} 条 ≠ 现算 {len(TP_BAD)} 枚")
    if n_tp_zero != len(TP_ZERO):
        tp_count_off.append(f"零组明细串 {n_tp_zero} 条 ≠ 现算 {len(TP_ZERO)} 枚")
    tp_sev_ok = (severity("product", "H-TOOL-PROMISE") == "WARN"
                 and "H-TOOL-PROMISE" not in CHANGELOG_CODES
                 and "H-TOOL-PROMISE" in WARN_CODES and "H-TOOL-PROMISE" in SCOPE_GATED
                 and "H-TOOL-PROMISE" in LEGEND)
    ok9 = not tp_red_missing and not tp_zero_off and not tp_count_off and tp_sev_ok
    print(f"档⑨ §5-3 工具清单承诺双态（枚数现算）：红组 {len(TP_BAD)} 枚／该面发红 {len(tp_bad)} 条／逐枚点名到位＝{'是' if not tp_red_missing else '否'}"
          f"｜零组 {len(TP_ZERO)} 枚／越界发条 {len(tp_zero_off)} 枚（期望 0）"
          f"｜明细条数与现算枚数同拍＝{'是' if not tp_count_off else '否'}（红 {n_tp_red}/{len(TP_BAD)}／零 {n_tp_zero}/{len(TP_ZERO)}）"
          f"｜语集枚数 A {len(PROMISE_A_ITEMS)}／B {len(PROMISE_B_ITEMS)}／C {len(PROMISE_C_ITEMS)}（现算，非手打）"
          f"｜分级与射程＝{'是' if tp_sev_ok else '否'}（WARN_CODES 现算 {len(WARN_CODES)} 枚；CHANGELOG 不入门＝{'H-TOOL-PROMISE' not in CHANGELOG_CODES}）"
          f"｜红组明细＝{tp_red_detail}｜零组明细＝{tp_zero_detail}｜零组性质＝{[nature for _, _, nature in TP_ZERO]}"
          + ("" if ok9 else f"｜**离谱者**：红组缺＝{tp_red_missing or '无'}｜零组越界＝{tp_zero_off or '无'}｜条数对拍＝{tp_count_off or '无'}｜分级射程＝{'过' if tp_sev_ok else '不过'}"))
    if not ok9:
        ok = False

    good_f = _fixture_findings(good)
    print(f"档② 合规样：应零发条，实发 {len(good_f)} 条")
    for c, lineno, fname, d in good_f:
        print(f"   意外发条 → {fname}:{lineno} [{c}] {d}")
        ok = False

    buf_a, buf_b = io.StringIO(), io.StringIO()
    for buf in (buf_a, buf_b):
        with contextlib.redirect_stdout(buf):
            run_repo(False, True)
    ha = hashlib.sha256(buf_a.getvalue().encode()).hexdigest()[:16]
    hb = hashlib.sha256(buf_b.getvalue().encode()).hexdigest()[:16]
    print(f"档③ 全仓双跑确定性：报告 sha256 前 16 位 {ha} vs {hb} → {'一致' if ha == hb else '不一致'}")
    if ha != hb:
        ok = False

    # 档⑩（M428：卡面前 160 安装式——**按起点判、尾部可跨界**；四形矩阵＋缺席／散文两枚正控）
    inst = FIXDIR / "install-face"
    forms = ("at000", "at159", "at161", "absent", "prose")
    if not all((inst / f / "SKILL.md").is_file() for f in forms):
        print("   缺 M428 卡面安装式守护样（install-face/at000·at159·at161·absent·prose）→ 本档无法自证")
        ok = False
    else:
        def _hit(f):
            p = inst / f / "SKILL.md"
            return check_install_face(p, p.read_text(encoding="utf-8"))
        h0, h159, h161, ha_, hp = (_hit(f) for f in forms)

        def _pos(h):
            return [re.search(r"@字符位 (\d+)", d).group(1) for _, _, d in h if re.search(r"@字符位 (\d+)", d)]
        ok9 = (len(h0) == 1 and _pos(h0) == ["0"] and len(h159) == 1 and _pos(h159) == ["159"]
               and not h161 and not ha_ and len(hp) == 1 and _pos(hp) == ["2"])
        print(f"档⑩ 卡面前160安装式（按起点判、尾部可跨界）：起0红 {len(h0)}@{_pos(h0)}"
              f"｜起159红 {len(h159)}@{_pos(h159)}｜起161红 {len(h161)}（期望 0）"
              f"｜缺席正控 {len(ha_)}（期望 0）｜散文「装：」＋命令 {len(hp)}@{_pos(hp)}（期望红@2，不享豁免）"
              f"｜本档={'对' if ok9 else '错'}")
        if not ok9:
            ok = False

    print(f"selftest: {'ALL GREEN（闸能红、能绿、可复现）' if ok else 'FAIL'}")
    return 0 if ok else 1


# ---------------------------------------------------------------- 单文件探针
def check_one(path: Path, strict: bool) -> int:
    if not path.is_file():
        print(f"[出错] 文件不存在：{path}")
        return 1
    path = path.resolve()
    face = classify(path)
    if face is None:
        # 仓外或不在检面（run 目录里的待发文稿）：按成品面从严判，不给假绿
        inside = str(path).startswith(str(ROOT) + "/")
        face = "product"
        note = "（仓内但非公开面，按成品面从严判）" if inside else "（仓外路径，按成品面从严判）"
    else:
        note = f"（面分类：{face}）"
    text = path.read_text(encoding="utf-8", errors="replace")
    finds: list[tuple[str, int, str]] = []
    for code, ban, pat, spec in RULES:
        if face == "changelog" and code not in CHANGELOG_CODES:
            continue
        if code in SCOPE_GATED and not gift_scope_ok(path):
            continue
        for lineno, line in enumerate(text.split("\n"), 1):
            m = pat.search(line)
            if m:
                finds.append((code, lineno, f"{ban_label(code)}{ban}命中「{hit_of(m)}」（规格：{spec}）"))
    if face == "product":
        base = _pkg_root(path)
        for lineno, ptr, why in _pointers(text, base, path.parent, path):
            finds.append(("H-POINTER", lineno, f"包内指路 `{ptr}` {why}（规格：{LEGEND['H-POINTER']}）"))
        finds.extend(check_install_face(path, text))
    finds.sort(key=lambda x: (x[1], x[0]))
    codes = {c for c, _, _ in finds}
    sevs = {severity(face, c) for c, _, _ in finds}
    sev = "ERROR" if "ERROR" in sevs else "WARN"      # 逐码分级后，表头显最重一档
    n_warn_only = sum(1 for c, _, _ in finds if severity(face, c) == "WARN")
    if finds:
        print(f"{sev}: {path.name}（{len(finds)} 条）{note}")
        for code, lineno, detail in finds:
            own = severity(face, code)
            print(f"  - [{code}{'／' + own if own != sev else ''}] 第 {lineno} 行：{detail}")
        if n_warn_only:
            print(f"  其中按码记 WARN（`WARN_CODES`＝{sorted(WARN_CODES)}）：{n_warn_only} 条——不抬升成 ERROR，也不静默吞")
    else:
        print(f"PASS: {path.name} 五禁零命中、指路可跟随 {note}")
    print("  码表: " + "; ".join(f"{c}→{LEGEND[c]}" for c in sorted(codes)))
    if not finds:
        return 0
    return 1 if ("ERROR" in sevs or strict) else 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description="公开面卫生机检闸（五禁＋指路存在性，纯 stdlib 零网络）。",
        epilog="出口：ERROR=成品面违禁（发布打回，与红线同级）；WARN 有两条通路——①CHANGELOG 面命中（留痕原则，人裁）；"
               "②成品面命中、但该码在 WARN_CODES 里逐码降级（M289 起，如 ⑥ 额度句缺单位——过渡态不钉门）。"
               "判定与词表全集以本脚本现值为准（--help 看禁项全集，不止五禁）。")
    ap.add_argument("--strict", action="store_true", help="WARN 也计失败")
    ap.add_argument("--quiet", action="store_true", help="只报汇总")
    ap.add_argument("--selftest", action="store_true", help="跑 scripts/fixtures/hygiene/ 正反守护样＋双跑确定性")
    ap.add_argument("--file", metavar="PATH", help="只检一个文件（岗单周检/新票探针）")
    ap.add_argument("--list", action="store_true", help="列出被扫的面")
    a = ap.parse_args()

    if a.selftest:
        return selftest()
    if a.file:
        return check_one(Path(a.file), a.strict)
    if a.list:
        faces = iter_faces()
        for f in faces:
            print(f"{classify(f):<9} {f.relative_to(ROOT)}")
        print(f"\n共 {len(faces)} 面，规则 {len(RULES)} 禁 + H-POINTER")
        return 0
    return run_repo(a.strict, a.quiet)


if __name__ == "__main__":
    try:
        code = main()
        sys.stdout.flush()
    except BrokenPipeError:
        code = 1  # 探针常被 `| head` 截：按管道语义收，不把 Traceback 当结论
    try:
        sys.stdout.close()  # 显式关，避开解释器退出时的隐式 flush 报错
    except BrokenPipeError:
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
    sys.exit(code)
