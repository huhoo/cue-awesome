#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_ma_card.py — A股并购重组条款卡的机检（零网络、只读传入文件）。

五道码（缺一即不叫过闸）：
  MA-STRUCT 五段齐：头部申报／八项逐字速读／口径对照／缺数清单／待人工，任一节缺失即发；
             八项名目另须在「逐字速读」段内**行级在场**——每枚名目一行以「- 名目：」起头，只在散文里提到不算占行；
  MA-QUOTE  每项原句与锚：项行的书名号（「」『』«»）内原句不得为空或只剩单字；「锚：」标签在而锚值为空同样发；
  MA-LINE   红线断言三道：①定式禁词（是否划算／必能过会／稳赚／零风险／保证收益／利好／建议参与／建议申购／套利／
             内幕信息／绕开审批／规避披露／代客申报／利益输送／估值合理）；②判断式规则——项行拆字段后，红线判据域只取
             本件自己写的话（剥掉书名号内的报告书原句与锚，非 [待人工] 行；免责按**分句**算不跨句，机构名「X 会」与
             「会 X」名词里的「会」先从语气域按形态洗掉），主题词（重组·并购·交易·标的·对价·评估·估值·承诺·补偿·
             锁定·过会·注册·审批·披露·股价·摊薄·稀释·收益·风险·业绩·协同·整合·复牌）与判断语气（应·应予·予以·将·会·
             必·有望·可期·可能·足以·构成·属于·意味着·支持·成立·无效·有效·上调·下调·增加·减少·高于·低于·赚·亏·
             无疑·显然·肯定…）同段出现即发；③自裁效力层：裁定前缀（结论／综上／因此／本件认为／判定／认定…）与
             效力判断（无效／有效／作废／不成立／成立／撤销／违法／违规／属实…）同现即发；
  MA-COUNT  齐缺申报恰一枚：头部「共八项·缺 N 项」只准出现一处（两处并存即发），且 N 必须等于速读段里「未检索到」的
             项行数；把「未检索到」写成「无该项／没有此项」一律发；
  MA-VALUE  三格数字归属（定价方法与交易对价／支付方式与股份发行／业绩承诺与补偿安排）**以短语结构体为主**判：
             ①项行拆字段，判据域只取该项自己的原句；②先剥日期（评估基准日、审计基准日、上市日这类一律从取数域剔除，
             「2025 年 12 月 31 日」不是对价）；③取数域按「标点 ∪ 数字边界」切成短语表，每枚候选（金额·股数·百分比）
             只在它自己那条短语里定档——数左跳过单位与连接词后最近的实义名词是本格族（评估值·交易对价·发行价格·
             发行数量·承诺净利润·补偿金额…）才算本格取到，是外族参照数（账面价值·净资产·审计值·市盈率·股价·均价·
             已实现净利润·同比增长·配套募集资金上限…）且更靠数即剔，**哪怕同一短语别处写了本格名词**；数左什么都不剩时
             看本短语数右；短语两头都没名词＝孤立数才继承前序最近一次的本格名词，前序只出现过外族参照数时不继承；
             ④反向判兜底：剥日期后没有一枚合格候选、又没写「未检索到」即发，空泛语（另行确定·以…为准·届时披露·待定·
             由交易双方协商确定·以经审计的数据为准）只决定发红那句话的措辞。
             **射程就这么多**：判的是「数与其限定名词在同一短语内的相邻关系，加一次跨短语继承」，不声称覆盖所有
             自然语言的归属表达；省略主语究竟指谁属整句语义，机检不解析，这类归属人工回原句核对。数据源也如实说：
             短语内定档吃结构体三列偏移，孤立数继承那一步扫的是剥日期后的原串对应段，不是结构体本身。
             发红句把被剥的日期、落空候选与取数域首段一并点名当证据。

用法：
  python3 -B scripts/check_ma_card.py <待检文件>      # 逐条发红，全过则 PASS
  python3 -B scripts/check_ma_card.py --selftest      # 好样须过、坏样五道齐发、钉阈按整族各钉一档、对照样不误伤、临时件自清
  python3 -B scripts/check_ma_card.py --help
退码：0＝过（或自测全合）；1＝发红／自测不合；2＝用法错。
"""
from __future__ import annotations

import argparse
import atexit
import pathlib
import re
import shutil
import sys
import tempfile

TMP_ROOTS: list[pathlib.Path] = []

ITEMS = ("交易概况与方式", "交易对方与关联关系", "标的资产与权属", "定价方法与交易对价",
         "支付方式与股份发行", "业绩承诺与补偿安排", "锁定期与减持限制", "审批程序与披露义务")

# 三格数字归属：每格一本族（算本格取到）与一外族（参照数，不顶本格账），共用同一台结构体机器
NUM_CELLS = {
    "定价方法与交易对价": {
        "own": re.compile(r"评估值|评估结果|评估净值|交易对价|对价总额|对价|标的估值|估值|增值额|增值率|定价"),
        "foreign": re.compile(r"账面价值|账面净值|账面净资产|净资产|审计(?:后)?(?:的)?(?:净)?资产|评估机构|同行业|市盈率|市净率|可比交易|可比公司|股价|收盘价|开盘价|均价|配套募集资金|募集配套资金|发行数量|承诺净利润"),
    },
    "支付方式与股份发行": {
        "own": re.compile(r"发行价格|发行价|发行数量|发行股数|拟发行|本次发行|新增股份|支付股份|对价股份|现金对价|对价金额"),
        "foreign": re.compile(r"发行前总股本|总股本|股本总额|发行上限|不超过|募集资金|配套资金|收盘价|开盘价|均价|市价|账面|评估值|交易对价|承诺净利润"),
    },
    "业绩承诺与补偿安排": {
        "own": re.compile(r"承诺净利润|承诺[^\n]{0,24}净利润|净利润承诺|业绩承诺|承诺数|承诺金额|应补偿股份|补偿股份数?|补偿金额|应回购股份"),
        "foreign": re.compile(r"已实现净利润|实现净利润|实际净利润|历史净利润|营业收入|净利润率|净资产收益率|同比增长|上年|基准净利润|交易对价|发行价格|评估值"),
    },
}
NUM = re.compile(r"\d[\d,\.]*\s*(?:万元|亿元|亿股|万股|倍|％|%|元|股)")
DATE_SPAN = re.compile(r"\d{4}\s*(?:年|[-/.])\s*\d{1,2}\s*(?:月|[-/.])?\s*\d{1,2}\s*日?"
                       r"|\d{4}\s*年(?:\s*\d{1,2}\s*月)?(?:\s*\d{1,2}\s*日)?"
                       r"|\d{1,2}\s*月\s*\d{1,2}\s*日"
                       r"|\d{4}[-/.]\d{1,2}[-/.]\d{1,2}")
VAGUE = re.compile(r"另行确定|另行约定|另行协商|另定|届时公告|届时披露|届时确定|届时|待定|尚未确定|未确定|未定|"
                   r"由交易双方协商|由双方协商|协商确定|以[^，。；]{0,12}为准|尚需|有待|待[^，。]{0,6}出具|"
                   r"按有关规定执行|按规定执行|详见[^，。]{0,8}公告|视[^，。]{0,8}而定")
UNIT_SKIP = re.compile(r"(?:每股|每份|每一元|人民币|约|为|是|即|按|暂定|最终|合计|总计|分别|不低于|不超过|不高于|"
                       r"高于|低于|占|比例|占比|其中|含|部分|等|的|后|前|则|并|至|以及|万股|亿股|万元|亿元|股|元|万|亿)+"
                       r"\s*$")
COPA = re.compile(r"为|定为|即|按|暂定|是|确定|达|至")
SEG_SPLIT = re.compile(r"[，。；：！？]+|[,;](?!\s*\d)")   # 千分位逗号不断段；顿号算枚举不算归属边界（分年度枚举别把所有者切开）
NOUN_WASH = re.compile(r"[员委事大东议工学协商年例常布明谈论聚汇组独立]会|会[计议场话晤所馆堂员]")
ITEM = re.compile(r"^\s*[-*]\s*(" + "|".join(map(re.escape, ITEMS)) + r")[：:]")
QUOTES = re.compile(r"[「『«]([^」』»]*)[」』»]")
ANCHOR_SPLIT = re.compile(r"锚[:：]")
ANCHOR_VAL = re.compile(r"锚[:：]\s*(\S.*)$")
BANNED = re.compile(r"是否划算|必能过会|一定能过会|稳赚|零风险|保证收益|利好|建议参与|建议申购|建议买入|建议卖出|"
                    r"套利|内幕信息|绕开审批|规避披露|代客申报|代客投票|利益输送|估值合理|估值公允|必然获批")
SUBJECT = re.compile(r"重组|并购|交易|标的|对价|评估|估值|承诺|补偿|锁定|过会|注册|审批|披露|股价|摊薄|稀释|"
                     r"收益|风险|业绩|协同|整合|复牌|停复牌|发行|上市")
TONE = re.compile(r"应当|应予|予以|将|会|必|有望|可期|可能|足以|构成|属于|意味着|支持|成立|推翻|无效|有效|上调|下调|"
                  r"提升|下滑|增加|减少|回升|高于|低于|稳赚|赚|亏|无疑|显然|肯定|应(?!急)")
VERDICT = re.compile(r"结论|综上|因此|可见|据此|本院认为|本件认为|本卡认为|本件判断|判定|认定|断言")
EFFECT = re.compile(r"无效|有效|作废|不成立|成立|撤销|违法|违规|应予支持|予以支持|应支持|支持|必然|属实")
DISCLAIM = re.compile(r"不接|不出|不提供|不作|不判|禁止|未证|无法|不承诺")
PENDING = re.compile(r"\[待人工\]")
DECL = re.compile(r"共\s*(?:八|8)\s*项\s*[·：:|｜、]\s*缺\s*(\d+)\s*项")
EMPTY_LIE = re.compile(r"(?:^|[\s：:])无(?:该项|此项)|没有(?:该项|此项)")
CORE_STRIP = re.compile(r"[\s\u3000「」『』«»“”（）()《》【】，,。.；;：:、！!？~\-—_·/％%*#]+")
SECTIONS = (("头部申报", r"头部申报"), ("八项逐字速读", r"逐字速读|八项速读"),
            ("口径对照", r"口径对照"), ("缺数清单", r"缺数清单"), ("待人工", r"待人工"))
SPEED_HEAD = re.compile(r"^#{1,4}.*(?:逐字速读|八项速读)")
ANY_HEAD = re.compile(r"^#{1,4}\s")


def core_len(s: str) -> int:
    return len(CORE_STRIP.sub("", s))


def parse_item_line(ln: str):
    """项行拆成字段：名目／书名号原句／锚／原句外句体——判定按字段来，不按整行。"""
    m = ITEM.match(ln)
    if not m:
        return None
    name = m.group(1)
    body = ln[m.end():]
    anchor = ""
    ma = ANCHOR_SPLIT.search(body)
    if ma:
        anchor = body[ma.end():].strip()
        body = body[:ma.start()]
    quotes = QUOTES.findall(body)
    spoken = QUOTES.sub(" ", body).strip()
    return {"name": name, "quotes": quotes, "anchor": anchor, "spoken": spoken, "body": body.strip()}


def value_field(item: dict) -> str:
    """数字归属判据域＝该项自己的原句；没有书名号时退化为去掉锚段与名目前缀后的句体。"""
    if item["quotes"]:
        return " ".join(item["quotes"])
    return item["spoken"] or item["body"]


def trim_units(pre: str):
    """数左那一段先跳过单位与连接词（每股·合计·约·为·即·按·不低于·占·比例·元·股…），
    返回剩余左文与途中是否见过谓语词——「每股」是单位不是所有者，「确定为」才是谓语。"""
    rest, copula = pre, False
    while True:
        stripped = UNIT_SKIP.sub("", rest)
        if stripped == rest:
            break
        if COPA.search(rest[len(stripped):]):
            copula = True
        rest = stripped
    return rest, copula


def build_phrases(domain: str, spec: dict) -> list[dict]:
    """显式结构体：把取数域按「SEG_SPLIT 标点 ∪ NUM 数字边界」切成短语表。
    每短语＝〔数左｜本短语收的那枚候选｜数右〕，三列偏移＝内本格名词·内参照数名词·内候选，各自带偏移位；
    候选形制＝金额（元·万元·亿元）∪股数（股·万股·亿股）∪倍数（倍）∪百分比（%·％）。"""
    own, foreign = spec["own"], spec["foreign"]
    nums = list(NUM.finditer(domain))
    phrases: list[dict] = []
    floor = 0
    for k, m in enumerate(nums):
        start = floor
        for punct in SEG_SPLIT.finditer(domain[floor:m.start()]):
            start = max(start, floor + punct.end())
        nxt_punct = len(domain)
        for punct in SEG_SPLIT.finditer(domain[m.end():]):
            nxt_punct = m.end() + punct.start()
            break
        nxt_num = nums[k + 1].start() if k + 1 < len(nums) else len(domain)
        end = min(nxt_punct, nxt_num)
        pre, post = domain[start:m.start()], domain[m.end():end]
        phrases.append({
            "num": m.group(0), "pre": pre, "post": post, "left_at": start,
            "seg": (pre + m.group(0)).strip(),
            "own_pre": [(h.start(), h.group(0)) for h in own.finditer(pre)],
            "for_pre": [(r.start(), r.group(0)) for r in foreign.finditer(pre)],
            "own_post": [(h.start(), h.group(0)) for h in own.finditer(post)],
            "for_post": [(r.start(), r.group(0)) for r in foreign.finditer(post)],
        })
        floor = m.end()
    return phrases


def value_gap(clause: str, spec: dict):
    """三格数字归属的判法（**以短语结构体为主**，射程写在顶条，不自称覆盖所有归属表达）：
    ①剥日期；②build_phrases 切短语表；③每枚候选只在本短语内定档——数左跳过单位后最近的实义名词属本族＝合格、
    属外族且更靠数＝剔（哪怕同一短语别处写了本族名词）；数左什么都不剩时看数右；谓语（确定为·为·即…）领出的数
    也算合格；④短语两头都没有名词＝孤立数（主语省略）才继承**前序最近一次的本族名词**——这一步扫的是剥日期后的
    原串对应段（本短语起点之前的全部文本），不是结构体本身；前序一次本族名词都没出现过时不继承、本数仍归参照；
    ⑤存在一枚合格候选即过，一枚都没有又没写「未检索到」才发。返回（被剥日期，合格段或 None，空泛语，落空候选与理由）。"""
    dates = [d.strip() for d in DATE_SPAN.findall(clause) if d.strip()]
    naked = DATE_SPAN.sub(" ", clause)
    vague = VAGUE.search(naked)
    candidates: list[tuple[str, str]] = []
    own, foreign = spec["own"], spec["foreign"]
    for ph in build_phrases(naked, spec):
        seg = ph["seg"]
        rest, copula = trim_units(ph["pre"])
        mh = mr = None
        for h in own.finditer(rest):
            mh = h
        for r in foreign.finditer(rest):
            if mr is None or r.start() > mr.start():
                mr = r
        if mr and (not mh or mr.start() >= mh.end()):
            candidates.append((seg, "数紧挨着参照数「" + mr.group(0) + "」（在本短语数左），那是账面值·净资产·市盈率·"
                                          "已实现净利润·募集资金一类的参照数，不是本格要的原值"))
            continue
        if mh:
            return dates, seg, vague, candidates
        if copula and not mr:
            return dates, seg, vague, candidates
        r0 = ph["for_post"][0] if ph["for_post"] else None
        h_last = ph["own_post"][-1] if ph["own_post"] else None
        if r0 and (h_last is None or r0[0] < h_last[0]):
            candidates.append((seg, "数紧挨着参照数「" + r0[1] + "」（在本短语数右），不是本格原值"))
            continue
        if ph["own_post"]:
            return dates, seg, vague, candidates
        before = naked[:ph["left_at"]]
        bh = br = None
        for h in own.finditer(before):
            bh = h
        for r in foreign.finditer(before):
            br = r
        if bh:
            return dates, seg, vague, candidates
        if br:
            candidates.append((seg, "本短语两头都没有本格名词，前序也只出现过参照数「" + br.group(0) + "」，孤立数不越界继承"))
            continue
        candidates.append((seg, "数前后与本短语都没有本格名词（评估值·交易对价·发行价格·发行数量·承诺净利润·补偿金额一类的），"
                                "也没有「确定为每股 N 元」这类谓语，前序同样没有所有者可继承"))
    return dates, None, vague, candidates


def judge_field(ln: str) -> str:
    """红线判据域＝本件自己写的话：拆字段后剥掉书名号内的报告书原句与锚段，项名前缀也不进域。"""
    item = parse_item_line(ln)
    body = item["body"] if item else ln
    body = QUOTES.sub(" ", body)
    ma = ANCHOR_SPLIT.search(body)
    if ma:
        body = body[:ma.start()]
    return body.strip()


def speed_zone(lines: list[str]) -> range:
    start = None
    for i, ln in enumerate(lines):
        if SPEED_HEAD.match(ln):
            start = i + 1
            break
    if start is None:
        return range(0, len(lines))
    end = len(lines)
    for j in range(start, len(lines)):
        if ANY_HEAD.match(lines[j]):
            end = j
            break
    return range(start, end)


def check_text(text: str) -> list[tuple[str, int, str]]:
    """返回 [(码, 行号, 说明)]；行号 0＝整档级判据。"""
    hits: list[tuple[str, int, str]] = []
    lines = text.splitlines()
    for name, pat in SECTIONS:
        if not re.search(pat, text):
            hits.append(("MA-STRUCT", 0, f"缺段：{name}"))
    zone = speed_zone(lines)
    seen: dict[str, int] = {}
    for i in zone:
        ln = lines[i]
        item = parse_item_line(ln)
        if not item:
            continue
        name = item["name"]
        seen.setdefault(name, i + 1)
        if "未检索到" in ln:
            continue
        if not item["quotes"]:
            hits.append(("MA-QUOTE", i + 1, f"缺项原句：{name} 那一行没有书名号内的原文"))
        elif any(core_len(q) <= 1 for q in item["quotes"]):
            hits.append(("MA-QUOTE", i + 1, f"原句占位：{name} 那一行的书名号内为空或只剩单字"))
        mv = ANCHOR_VAL.search(ln)
        if not mv or core_len(mv.group(1)) == 0:
            hits.append(("MA-QUOTE", i + 1, f"锚值为空：{name} 那一行的「锚：」后面没有来源定位"))
        if name in NUM_CELLS:
            dates, ok_seg, vague, cands = value_gap(value_field(item), NUM_CELLS[name])
            ev = ""
            if cands:
                ev = "｜有数但不合格的段：" + "∥".join(f"「{s}」＝{why}" for s, why in cands)
            if dates:
                ev += "｜剥掉的日期：" + "∥".join(dates)
            if not cands and ok_seg is None:
                ev += "｜取数域（剥日期后）首段：「" + value_field(item).strip()[:28] + "」"
            if ok_seg is None:
                if vague:
                    hits.append(("MA-VALUE", i + 1, f"{name} 以空泛语顶替原值：原句剥掉日期后没有任何一段给出本格原值，"
                                                   f"只剩「{vague.group(0)}」这类说法{ev}——别格的数、参照数与日期都不顶本格的账，"
                                                   "换同义词换不掉这一判"))
                else:
                    hits.append(("MA-VALUE", i + 1, f"{name} 缺本格原值：原句剥掉日期后没有一段给出属于本格的数量原值"
                                                    f"（金额·股数·百分比），且数与本格名词在同一短语内相邻{ev}——参照数不顶账，"
                                                    "没取到就写「未检索到」"))
    for name in ITEMS:
        if name not in seen:
            hits.append(("MA-STRUCT", 0, f"缺项行：{name} 在逐字速读段里没有以「- 名目：」起头的行"))
    pending_items = sum(1 for i in zone if ITEM.match(lines[i]) and "未检索到" in lines[i])
    decls = DECL.findall(text)
    if len(decls) > 1:
        hits.append(("MA-COUNT", 0, f"齐缺申报出现 {len(decls)} 处：只准一枚，两处并存即口径不唯一"))
    elif len(decls) == 1 and int(decls[0]) != pending_items:
        hits.append(("MA-COUNT", 0, f"齐缺申报与清单不对账：申报缺 {decls[0]} 项∥速读段实有 {pending_items} 行「未检索到」"))
    elif not decls:
        hits.append(("MA-COUNT", 0, "头部缺「共八项·缺 N 项」申报，无从对账"))
    for i, ln in enumerate(lines, 1):
        if PENDING.search(ln):
            continue   # 行首 [待人工] 标记管全行：这些判断的登记位就在这一行里
        dom = judge_field(ln)
        flagged = False
        for seg in SEG_SPLIT.split(dom):
            if DISCLAIM.search(seg):
                continue   # 免责按分句算，不跨句把后半句的真判断一起免掉
            seg = NOUN_WASH.sub("", seg)
            mb = BANNED.search(seg)
            if mb:
                hits.append(("MA-LINE", i, f"红线断言词出现在没有 [待人工] 的行：本件自己写的话里有「{mb.group(0)}」——"
                                            "同一行前半写了免责句也不顶，豁免只到分句为止"))
                flagged = True
                break
            ms, mt = SUBJECT.search(seg), TONE.search(seg)
            if ms and mt:
                hits.append(("MA-LINE", i, f"判断式结论落在非待人工行：本件自己写的话里「{ms.group(0)}」与判断语气"
                                           f"「{mt.group(0)}」同段出现——交易能否过会·估值高低·股价反应这类判断一律留 "
                                           "[待人工]，报告书原句（书名号内）与锚不在此列"))
                flagged = True
                break
        if not flagged:
            mv2, me = VERDICT.search(dom), EFFECT.search(NOUN_WASH.sub("", dom))
            if mv2 and me:
                hits.append(("MA-LINE", i, f"自裁效力判断落在非待人工行：本件自己写的话里裁定前缀「{mv2.group(0)}」"
                                            f"＋效力判断「{me.group(0)}」——本次交易是否有效·程序是否违规这类裁定本件一律不自判，"
                                            "留 [待人工]；报告书原句（书名号内）与锚不在此列"))
        if EMPTY_LIE.search(ln):
            hits.append(("MA-COUNT", i, "把「未检索到」写成「无／没有」"))
    return hits


def make_tmp(prefix: str) -> pathlib.Path:
    d = pathlib.Path(tempfile.mkdtemp(prefix=prefix, dir=str(pathlib.Path(tempfile.gettempdir()))))
    TMP_ROOTS.append(d)
    return d


@atexit.register
def _cleanup() -> None:
    for d in TMP_ROOTS:
        shutil.rmtree(d, ignore_errors=True)


def selftest() -> int:
    here = pathlib.Path(__file__).resolve().parent
    good = here / "fixtures" / "good-ma-card.md"
    bad = here / "fixtures" / "bad-ma-card.md"
    rows = []
    gt = good.read_text(encoding="utf-8")
    gh = check_text(gt)
    rows.append(("好样须过（发条 0）", not gh, f"实发 {len(gh)} 条"))
    bt = bad.read_text(encoding="utf-8")
    bh = check_text(bt)
    codes = {c for c, _, _ in bh}
    rows.append(("坏样五道齐发", {"MA-STRUCT", "MA-QUOTE", "MA-LINE", "MA-COUNT", "MA-VALUE"} <= codes,
                 "实发码 " + "∥".join(sorted(codes))))
    tmp = make_tmp("check-ma-")
    stripped = tmp / "no-anchor.md"
    stripped.write_text(re.sub(r"锚[:：][^\n]*", "锚：", gt), encoding="utf-8")
    sh = check_text(stripped.read_text(encoding="utf-8"))
    rows.append(("反证·剥锚必发 MA-QUOTE", any(c == "MA-QUOTE" for c, _, _ in sh), f"实发 {len(sh)} 条"))
    nproof = 1
    pin = make_tmp("check-ma-pin-")
    ROW_PRICE = "「本次评估采用收益法与市场法，以收益法评估结果为准，标的评估值为 86,000 万元，交易对价确定为 86,000 万元」"
    ROW_PAY = "「本次发行价格为每股 12.60 元，发行数量合计 6,825 万股，现金对价 8,600 万元」"
    ROW_PAX = "「交易对方承诺 2026 年、2027 年、2028 年净利润分别不低于 5,000 万元、6,500 万元、8,000 万元，不足部分以股份补偿」"
    HEAD = "## 二、八项逐字速读"
    tiers = (
        ("钉阈·名目只剩散文必发 MA-STRUCT",
         gt.replace("- 锁定期与减持限制：", "锁定期与减持限制在报告书另有专节，", 1),
         "缺项行：锁定期与减持限制"),
        ("钉阈·整行名目缺席必发 MA-STRUCT",
         gt.replace("- 标的资产与权属：「标的资产为乙公司 100% 股权，权属清晰，不存在质押、查封或冻结」 锚：报告书 第三节 标的资产\n", "", 1),
         "缺项行：标的资产与权属"),
        ("钉阈·书名号内单字必发 MA-QUOTE",
         gt.replace("「标的资产为乙公司 100% 股权，权属清晰，不存在质押、查封或冻结」", "「清」", 1),
         "原句占位"),
        ("钉阈·齐缺申报改数必发 MA-COUNT",
         gt.replace("共八项·缺 1 项", "共八项·缺 0 项", 1),
         "齐缺申报与清单不对账"),
        ("钉阈·把未检索到写成无该项必发 MA-COUNT",
         gt.replace("- 审批程序与披露义务：未检索到（缺数清单已点名）", "- 审批程序与披露义务：无该项", 1),
         "把「未检索到」写成「无／没有」"),
        ("钉阈·评估值被账面值冒充必发 MA-VALUE",
         gt.replace(ROW_PRICE, "「标的账面价值为 32,000 万元，交易对价另行确定」", 1),
         "数紧挨着参照数「账面价值」"),
        ("钉阈·审计净资产冒充对价必发 MA-VALUE",
         gt.replace(ROW_PRICE, "「经审计净资产 41,000 万元，最终对价由双方协商确定」", 1),
         "以空泛语顶替原值"),
        ("钉阈·市盈率倍数不顶对价账必发 MA-VALUE",
         gt.replace(ROW_PRICE, "「标的评估值为账面净资产的 2 倍，最终以协议为准」", 1),
         "数紧挨着参照数「账面净资产」"),
        ("钉阈·发行价被收盘价冒充必发 MA-VALUE",
         gt.replace(ROW_PAY, "「发行价格参照停牌前收盘价 20.35 元，最终由股东大会确定」", 1),
         "数紧挨着参照数「收盘价」"),
        ("钉阈·总股本不顶发行数量账必发 MA-VALUE",
         gt.replace(ROW_PAY, "「发行前总股本为 54,000 万股，本次发行数量另行约定」", 1),
         "数紧挨着参照数「发行前总股本」"),
        ("钉阈·同比增长率不顶承诺数账必发 MA-VALUE",
         gt.replace(ROW_PAX, "「承诺净利润同比增长 30%，具体承诺数以最终协议为准」", 1),
         "数紧挨着参照数「同比增长」"),
        ("钉阈·已实现净利润冒充承诺数必发 MA-VALUE",
         gt.replace(ROW_PAX, "「标的 2024 年已实现净利润 4,200 万元，承诺净利润待定」", 1),
         "数紧挨着参照数「已实现净利润」"),
        ("钉阈·评估基准日不顶对价账必发 MA-VALUE",
         gt.replace(ROW_PRICE, "「评估基准日为 2025 年 12 月 31 日，交易对价届时公告」", 1),
         "以空泛语顶替原值"),
        ("钉阈·本短语自归参照不越界继承必发 MA-VALUE",
         gt.replace(ROW_PRICE, "「交易对价以评估结果为准，其中账面价值 32,000 万元」", 1),
         "（在本短语数左）"),
        ("钉阈·孤立数无前序本格名词不洗绿必发 MA-VALUE",
         gt.replace(ROW_PRICE, "「经审计净资产为 41,000 万元，标的另需支付 8,000 万元」", 1),
         "孤立数不越界继承"),
        ("钉阈·别格数不顶本格账必发 MA-VALUE",
         gt.replace(ROW_PAX, "「标的交易对价为 86,000 万元，承诺净利润待定」", 1),
         "数紧挨着参照数「交易对价」"),
        ("钉阈·红线定式词必发 MA-LINE",
         gt.replace(HEAD, "- 另：本次交易稳赚。\n\n" + HEAD, 1),
         "「稳赚」"),
        ("钉阈·判断式家族（主题＋语气）必发 MA-LINE",
         gt.replace(HEAD, "- 另：本次重组会提升收益。\n\n" + HEAD, 1),
         "与判断语气"),
        ("钉阈·自裁效力族必发 MA-LINE",
         gt.replace(HEAD, "- 结论：本次申请文件有效。\n\n" + HEAD, 1),
         "裁定前缀「结论」"),
        ("钉阈·免责句后半的真判断必发 MA-LINE",
         gt.replace(HEAD, "- 说明：本件不判估值高低；本次交易一定能过会。\n\n" + HEAD, 1),
         "「一定能过会」"),
        ("钉阈·是否划算落在非待人工行必发 MA-LINE",
         gt.replace(HEAD, "- 说明：这笔并购是否划算见下文。\n\n" + HEAD, 1),
         "「是否划算」"),
    )
    ctrls = (
        ("对照·本格原值带括注约束不误伤（MA-VALUE 零发）",
         gt.replace(ROW_PRICE, "「标的评估值为 86,000 万元（不低于账面价值），交易对价确定为 86,000 万元」", 1), "MA-VALUE"),
        ("对照·主语省略的孤立数继承本格名词不误伤（MA-VALUE 零发）",
         gt.replace(ROW_PRICE, "「交易对价参考标的账面价值 32,000 万元，最终确定为 86,000 万元」", 1), "MA-VALUE"),
        ("对照·数右有本格名词不误伤（MA-VALUE 零发）",
         gt.replace(ROW_PAY, "「每股 12.60 元的发行价格」", 1), "MA-VALUE"),
        ("对照·发行价在前参照价在后不误伤（MA-VALUE 零发）",
         gt.replace(ROW_PAY, "「发行价格为每股 12.60 元，参照停牌前均价 20.35 元」", 1), "MA-VALUE"),
        ("对照·承诺数与实现数并列不误伤（MA-VALUE 零发）",
         gt.replace(ROW_PAX, "「标的 2024 年已实现净利润 4,200 万元，交易对方承诺净利润不低于 5,000 万元」", 1), "MA-VALUE"),
        ("对照·分年度承诺三档不误伤（MA-VALUE 零发）",
         gt.replace(ROW_PAX, "「承诺 2026 年、2027 年、2028 年净利润分别不低于 5,000 万元、6,500 万元、8,000 万元」", 1), "MA-VALUE"),
        ("对照·补偿公式带承诺数不误伤（MA-VALUE 零发）",
         gt.replace(ROW_PAX, "「应补偿股份数＝（承诺净利润－实际净利润）÷承诺净利润×发行股份数量，承诺净利润不低于 5,000 万元」", 1), "MA-VALUE"),
        ("对照·机构名里的「会」不误伤（MA-LINE 零发）",
         gt.replace(HEAD, "- 说明：本次交易经董事会审议通过。\n\n" + HEAD, 1), "MA-LINE"),
        ("对照·委员会核实不误伤（MA-LINE 零发）",
         gt.replace(HEAD, "- 说明：独立财务顾问与审计委员会核实了标的权属。\n\n" + HEAD, 1), "MA-LINE"),
        ("对照·会计处理陈述不误伤（MA-LINE 零发）",
         gt.replace(HEAD, "- 说明：合并对价的会计处理按草案列示。\n\n" + HEAD, 1), "MA-LINE"),
        ("对照·报告书原句里的裁定措辞不误伤（MA-LINE 零发）",
         gt.replace("- 审批程序与披露义务：未检索到（缺数清单已点名）",
                    "- 审批程序与披露义务：「本次交易尚需获得股东大会批准，申请文件的效力以监管机构认定为准」 锚：报告书 第八节", 1), "MA-LINE"),
        ("对照·免责分句陈述不误伤（MA-LINE 零发）",
         gt.replace(HEAD, "- 说明：本件不出估值意见，也不接代办。\n\n" + HEAD, 1), "MA-LINE"),
    )

    for n, (name, text, needle) in enumerate(tiers, 1):
        nproof += 1
        f = pin / f"pin-{n}.md"
        f.write_text(text, encoding="utf-8")
        th = check_text(f.read_text(encoding="utf-8"))
        ok = (text != gt) and any(needle in m for _, _, m in th)
        rows.append((name, ok, f"注入{'生效' if text != gt else '作废'}·命中句 {'有' if ok else '无'}"))
    ctrls += (
        ("对照·好样定价行原形不误伤（MA-VALUE 零发）", gt.replace(ROW_PAY, "「本次发行价格为每股 12.60 元」", 1), "MA-VALUE"),
        ("对照·带日期与括注的承诺数不误伤（MA-VALUE 零发）",
         gt.replace(ROW_PAX, "「交易对方承诺 2026 年净利润不低于 5,000 万元（以经审计的扣非前后孰低者为准）」", 1), "MA-VALUE"),
    )
    for n, (name, text, code) in enumerate(ctrls, 1):
        nproof += 1
        c = pin / f"control-{n}.md"
        c.write_text(text, encoding="utf-8")
        th = check_text(c.read_text(encoding="utf-8"))
        fired = [m for cd, _, m in th if cd == code]
        rows.append((name, text != gt and not fired, f"注入{'生效' if text != gt else '作废'}·{code} 实发 {len(fired)} 条"))
    made = [p.name for p in TMP_ROOTS]
    root = pathlib.Path(tempfile.gettempdir())
    for p in TMP_ROOTS:
        shutil.rmtree(p, ignore_errors=True)
    leftover = sorted(q.name for q in root.iterdir() if q.name.startswith("check-ma-")) if root.is_dir() else []
    rows.append(("临时根自清（跑后不增）", not leftover, f"本次建 {len(made)} 枚·跑后残留 {len(leftover)} 枚"))
    bad_rows = [r for r in rows if not r[1]]
    for name, ok, detail in rows:
        print(f"  {'ok  ' if ok else 'FAIL'} {name}｜{detail}")
    print(f"selftest: {'ALL GREEN' if not bad_rows else 'FAIL'}（好样 1 枚·坏样五道·反例 {nproof} 枚·临时根 {len(TMP_ROOTS)} 枚自清）")
    return 0 if not bad_rows else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="A股并购重组条款卡五道机检（零网络）")
    ap.add_argument("target", nargs="?", help="待检的条款卡文件（Markdown）")
    ap.add_argument("--selftest", action="store_true",
                    help="好样须过、坏样五道齐发、钉阈按整族各钉一档、对照样不误伤、临时件自清")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if not args.target:
        ap.error("缺参数：给一个待检文件，或用 --selftest")
    path = pathlib.Path(args.target)
    if not path.is_file():
        print(f"FAIL 读不到文件：{path}")
        return 2
    hits = check_text(path.read_text(encoding="utf-8"))
    if not hits:
        print(f"PASS（扫过 {len(path.read_text(encoding='utf-8').splitlines())} 行，五道全过）")
        return 0
    for code, ln, msg in hits:
        print(f"FAIL [{code}] {path.name}:{ln or '整档'} {msg}")
    print(f"FAIL（扫过 {len(path.read_text(encoding='utf-8').splitlines())} 行，发条 {len(hits)} 条）")
    return 1


if __name__ == "__main__":
    sys.exit(main())
