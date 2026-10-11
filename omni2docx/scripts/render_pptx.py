#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""omni2docx — PPTX 汇报渲染器（汇报场景：把文档/提纲变成可讲的 deck）

约定（C 路线）：内容取舍交给 agent——agent 按 slide 组织好 markdown，
引擎只负责把结构映射为 deck（标题页/章节页/要点页/表格页）与制式排版。
不做像素级版面复刻；不做"每源页一页"的机械平铺（那是展示/归档，不是汇报）。
"""
import argparse
import base64
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from build_docx import (  # noqa: E402
    DOC_PROFILES, build_outline_map, clean_cjk_spaces, derive_outline_from_markdown,
    extract_footnotes, extract_title, match_outline_level, parse_blocks, strip_emoji,
)

from pptx import Presentation  # noqa: E402
from pptx.util import Inches, Pt  # noqa: E402
from pptx.oxml.ns import qn  # noqa: E402

# deck 制式：汇报场景字号显著大于文档场景；字体沿用场景预设的东亚字体
PPT_PROFILES = {
    "default": {"title_east": "微软雅黑", "body_east": "微软雅黑",
                "title_size": 28, "body_size": 18, "section_size": 32},
    "gov": {"title_east": "黑体", "body_east": "仿宋_GB2312",
            "title_size": 28, "body_size": 20, "section_size": 32},
    "legal": {"title_east": "黑体", "body_east": "仿宋_GB2312",
              "title_size": 26, "body_size": 18, "section_size": 30},
    "finance": {"title_east": "黑体", "body_east": "等线",
                "title_size": 26, "body_size": 16, "section_size": 30},
    "academic": {"title_east": "黑体", "body_east": "宋体",
                 "title_size": 26, "body_size": 18, "section_size": 30},
}

LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]+\)")
IMG_RE = re.compile(r"!\[([^\]]*)\]\(([^)]*)\)")


def plain(text):
    """markdown 行内 → PPT 纯文本（去标记、保留可读内容）。"""
    t = text or ""
    t = IMG_RE.sub(lambda m: m.group(1) or "图像", t)
    t = LINK_RE.sub(r"\1", t)
    t = re.sub(r"\*\*(.+?)\*\*(?!\*)", r"\1", t)
    t = re.sub(r"__(.+?)__(?!_)", r"\1", t)
    t = re.sub(r"`(.+?)`", r"\1", t)
    t = re.sub(r"\*([^\s*][^*\n]*)\*", r"\1", t)
    t = re.sub(r"_([^\s_][^_\n]*)_", r"\1", t)
    t = re.sub(r"\[\^([^\]]+)\]", r"[\1]", t)
    return clean_cjk_spaces(t).strip()  # 清 OCR 残留的 CJK 字间空格（拉丁逐字母空格不可还原，不强修）


def set_east(run, east, latin=None):
    rPr = run._r.get_or_add_rPr()
    for tag in ("a:latin", "a:ea", "a:cs"):
        el = rPr.find(qn(tag))
        if el is not None:
            rPr.remove(el)
    from pptx.oxml import parse_xml
    from pptx.oxml.ns import nsdecls
    latin_el = parse_xml('<a:latin %s typeface="%s"/>' % (nsdecls("a"), latin or east))
    ea_el = parse_xml('<a:ea %s typeface="%s"/>' % (nsdecls("a"), east))
    cs_el = parse_xml('<a:cs %s typeface="%s"/>' % (nsdecls("a"), east))
    rPr.append(latin_el)
    rPr.append(ea_el)
    rPr.append(cs_el)


def add_line(tf, text, size, east, bold=False, color=None, level=0, space_after=6):
    p = tf.add_paragraph() if tf.paragraphs[0].runs or tf.paragraphs[0].text else tf.paragraphs[0]
    p.text = text
    p.level = level
    p.space_after = Pt(space_after)
    for r in p.runs:
        r.font.size = Pt(size)
        r.font.bold = bold
        if color:
            from pptx.dml.color import RGBColor
            r.font.color.rgb = RGBColor(*color)
        set_east(r, east)
    return p


class Deck:
    def __init__(self, cfg, ratio="16:9"):
        self.prs = Presentation()
        if ratio == "16:9":
            self.prs.slide_width, self.prs.slide_height = Inches(13.333), Inches(7.5)
        elif ratio == "4:3":
            self.prs.slide_width, self.prs.slide_height = Inches(10), Inches(7.5)
        self.cfg = cfg
        self.W = float(self.prs.slide_width)
        self.H = float(self.prs.slide_height)
        self.blank = self.prs.slide_layouts[6]

    def slide(self):
        return self.prs.slides.add_slide(self.blank)

    @property
    def n_slides(self):
        return len(self.prs.slides._sldIdLst)

    def title_slide(self, title, subtitle=None):
        s = self.slide()
        tf = s.shapes.add_textbox(Inches(0.8), Inches(2.6), self.W - Inches(1.6), Inches(2.0)).text_frame
        tf.word_wrap = True
        add_line(tf, title, self.cfg.get("section_size", 32) + 4,
                 self.cfg.get("title_east", "微软雅黑"), bold=True)
        if subtitle:
            tf2 = s.shapes.add_textbox(Inches(0.8), Inches(4.7), self.W - Inches(1.6), Inches(1.2)).text_frame
            tf2.word_wrap = True
            add_line(tf2, subtitle, self.cfg.get("body_size", 18),
                     self.cfg.get("body_east", "微软雅黑"), color=(0x66, 0x66, 0x66))
        return s

    def section_slide(self, title):
        s = self.slide()
        tf = s.shapes.add_textbox(Inches(0.8), Inches(3.0), self.W - Inches(1.6), Inches(1.6)).text_frame
        tf.word_wrap = True
        add_line(tf, title, self.cfg.get("section_size", 32),
                 self.cfg.get("title_east", "微软雅黑"), bold=True)
        return s

    def content_slide(self, title, items, tables=None, images=None, notes=None):
        """items: [("bullet"|"text"|"note", 文本)]；tables: [(header, rows)]。"""
        tables = tables or []
        images = images or []
        s = self.slide()
        tb = s.shapes.add_textbox(Inches(0.6), Inches(0.45), self.W - Inches(1.2), Inches(1.4))
        tf = tb.text_frame
        tf.word_wrap = True
        base = self.cfg.get("title_size", 28)
        # 标题过长自动降字号（避免溢出标题区）
        tsize = base - 6 if len(title) > 70 else base - 3 if len(title) > 40 else base
        add_line(tf, title, tsize, self.cfg.get("title_east", "微软雅黑"), bold=True, space_after=2)
        top = Inches(1.85) if len(title) > 40 else Inches(1.55)
        avail_h = self.H - top - Inches(0.5)
        left_w = (self.W - Inches(1.2)) * (0.55 if images else 1.0)
        if items:
            body = s.shapes.add_textbox(Inches(0.6), top, left_w, avail_h)
            btf = body.text_frame
            btf.word_wrap = True
            for kind, text in items:
                if kind == "bullet":
                    add_line(btf, "• " + text, self.cfg.get("body_size", 18),
                             self.cfg.get("body_east", "微软雅黑"))
                elif kind == "note":
                    add_line(btf, text, max(self.cfg.get("body_size", 18) - 4, 10),
                             self.cfg.get("body_east", "微软雅黑"), color=(0x77, 0x77, 0x77))
                else:
                    add_line(btf, text, self.cfg.get("body_size", 18),
                             self.cfg.get("body_east", "微软雅黑"))
        cur_top = top
        for header, rows in tables:
            n_rows, n_cols = len(rows) + 1, max(len(header), max((len(r) for r in rows), default=1))
            tbl_h = min(Inches(0.35) * n_rows + Inches(0.2), avail_h)
            gt = s.shapes.add_table(n_rows, n_cols, Inches(0.6), cur_top, left_w, tbl_h)
            tbl = gt.table
            fsize = Pt(14 if n_cols <= 3 else 12 if n_cols <= 5 else 10)
            for j, c in enumerate(header):
                cell = tbl.cell(0, j)
                cell.text = plain(c)[:60]
                for p in cell.text_frame.paragraphs:
                    for r in p.runs:
                        r.font.size = fsize
                        r.font.bold = True
                        set_east(r, self.cfg.get("title_east", "微软雅黑"))
            for i, row in enumerate(rows, start=1):
                for j, c in enumerate(row[:n_cols]):
                    cell = tbl.cell(i, j)
                    cell.text = plain(c)[:80]
                    for p in cell.text_frame.paragraphs:
                        for r in p.runs:
                            r.font.size = fsize
                            set_east(r, self.cfg.get("body_east", "微软雅黑"))
            cur_top = cur_top + tbl_h + Inches(0.15)
        for img_bytes, alt in images:
            try:
                s.shapes.add_picture(io.BytesIO(img_bytes),
                                     Inches(0.6) + left_w + Inches(0.2), top,
                                     width=(self.W - left_w - Inches(1.0)))
            except Exception:
                pass
        if notes:
            s.notes_slide.notes_text_frame.text = notes
        return s

    def save(self, path):
        os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
        self.prs.save(path)


def chunk(items, max_bullets, max_chars):
    """要点过多/过长时切分为多页，避免溢出不可读。"""
    page, pages, chars = [], [], 0
    for it in items:
        page.append(it)
        chars += len(it[1])
        if len(page) >= max_bullets or chars >= max_chars:
            pages.append(page)
            page, chars = [], 0
    if page:
        pages.append(page)
    return pages or [[]]


def build(md, cfg, title=None, section_level=1, split_level=2, max_bullets=7,
          max_chars=900, ratio="16:9", strip=False, embed_images=True, prose="notes",
          max_slides=80):
    """prose：正文段落去向——notes（默认，进演讲者备注）/ body（上正文区）/ skip（丢弃）。

    汇报语义：要点、表格、图像上页；正文细节进备注页，避免长文档被逐段平铺成上百页。
    """
    if strip:
        md = strip_emoji(md)
    md, foot = extract_footnotes(md)
    t_title, md = extract_title(md)
    doc_title = title or t_title
    blocks = parse_blocks(md)
    deck = Deck(cfg, ratio)

    if doc_title:
        deck.title_slide(doc_title, "Omni 解析重建 · 汇报版")

    cur_title = None
    cur_items, cur_tables, cur_images, cur_notes = [], [], [], []
    pending_notes = []
    capped = [False]

    def room():
        """页数上限（避免长文档被机械平铺成上百页）；0 = 不限。"""
        if max_slides and deck.n_slides >= max_slides:
            capped[0] = True
            return False
        return True

    def flush():
        nonlocal cur_items, cur_tables, cur_images, cur_notes, pending_notes
        notes = "\n".join(x for x in (pending_notes + cur_notes) if x).strip() or None
        if not (cur_items or cur_tables or cur_images):
            # 无要点可上页：正文留作备注，顺延到下一页，避免产出空页
            if cur_title and cur_title != "要点":
                # 空节标题（标题下只有图片/分隔线）不得被下一标题覆盖丢失
                pending_notes = pending_notes + [cur_title] + cur_notes
            else:
                pending_notes = pending_notes + cur_notes
            cur_notes = []
            return
        t = cur_title or "要点"
        pages = chunk(cur_items, max_bullets, max_chars) if cur_items else [[]]
        for pi, pg in enumerate(pages):
            if not room():
                return
            deck.content_slide(t if pi == 0 else "%s（续 %d）" % (t, pi + 1),
                               pg, cur_tables if pi == 0 else [],
                               cur_images if pi == 0 else [],
                               notes=(notes if pi == 0 else None))
        cur_items, cur_tables, cur_images, cur_notes = [], [], [], []
        pending_notes = []

    for kind, payload, _ in blocks:
        if kind == "heading":
            lvl, text = int(payload[0]), plain(payload[1])
            if lvl <= section_level:
                flush()
                cur_title = None
                if room():
                    deck.section_slide(text)
                continue
            if lvl <= split_level:
                flush()
                cur_title = text
                continue
            cur_items.append(("bullet", text))
            continue
        if kind in ("ul", "ol"):
            for it in payload:
                cur_items.append(("bullet", plain(it)))
            continue
        if kind == "table":
            header, rows = payload
            cur_tables.append((header, rows))
            continue
        if kind == "quote":
            cur_items.append(("note", "“%s”" % plain(payload)))
            continue
        if kind == "visual":
            cur_items.append(("note", "%s %s" % (payload[0], plain(payload[1]))))
            continue
        if kind == "hr":
            continue
        text = plain(payload)
        m = IMG_RE.search(text)
        if m and embed_images and m.group(2).startswith("data:image"):
            try:
                raw = base64.b64decode(m.group(2).split(",", 1)[1])
                cur_images.append((raw, m.group(1)))
                text = IMG_RE.sub("", text).strip()
            except Exception:
                pass
        if not text:
            continue
        if prose == "body":
            cur_items.append(("text", text))
        elif prose == "notes":
            cur_notes.append(text)
    flush()
    # 兜底一：文档无标题层级（扫描件/纯正文）时，正文全落备注会产出空 deck——
    # 此时按要点页平铺，保证有可讲的内容页（agent 若要更精炼，自行提炼提纲）。
    leftover = [x for x in (pending_notes + cur_notes) if x]
    if leftover and deck.n_slides <= (1 if doc_title else 0):
        pages = chunk([("bullet", t) for t in leftover], max_bullets, max_chars)
        for pi, pg in enumerate(pages):
            if not room():
                break
            deck.content_slide("要点" if pi == 0 else "要点（续 %d）" % (pi + 1), pg)
        leftover = []
    # 兜底二：deck 正常时，尾部纯正文（如免责声明节）残留的备注不得静默丢弃——
    # 追加到最后一张幻灯片的演讲者备注，保证正文零丢失。
    if leftover and deck.prs.slides:
        try:
            last = deck.prs.slides[-1]
            tf = last.notes_slide.notes_text_frame
            tf.text = (tf.text or "") + ("\n" if tf.text else "") + "\n".join(leftover)
        except Exception:
            pass
    if capped[0]:
        sys.stderr.write("警告：达到 --max-slides=%d 上限，已截断；"
                         "建议 agent 先提炼提纲再渲染 deck。\n" % max_slides)
    if foot:
        # 脚注落到最后一页备注，保证可追溯
        try:
            last = deck.prs.slides[-1]
            tf = last.notes_slide.notes_text_frame
            tf.text = (tf.text or "") + "\n注释：" + "；".join(
                "%s %s" % (k, plain(v)) for k, v in foot)
        except Exception:
            pass
    return deck


def main():
    ap = argparse.ArgumentParser(description="文档/提纲 → 汇报用 PPTX deck")
    ap.add_argument("--json", help="中间 JSON（markdown+grounding+outline）")
    ap.add_argument("--md", help="markdown 文件（agent 按 slide 组织好的提纲）")
    ap.add_argument("--out", required=True, help="输出 .pptx")
    ap.add_argument("--profile", default="default",
                    help="deck 制式：default/gov/legal/finance/academic，或内联 JSON / .json 文件")
    ap.add_argument("--title", help="deck 标题")
    ap.add_argument("--section-level", type=int, default=1,
                    help="≤该层级的标题生成章节页（默认 1）")
    ap.add_argument("--split-level", type=int, default=2,
                    help="≤该层级的标题另起内容页（默认 2）")
    ap.add_argument("--max-bullets", type=int, default=7, help="每页最多要点数（超出续页）")
    ap.add_argument("--max-chars", type=int, default=900, help="每页正文字符上限（超出续页）")
    ap.add_argument("--prose", default="notes", choices=["notes", "body", "skip"],
                    help="正文段落去向：notes=演讲者备注（默认，汇报语义）/ body=上正文区 / skip=丢弃")
    ap.add_argument("--ratio", default="16:9", choices=["16:9", "4:3"])
    ap.add_argument("--strip-emoji", action="store_true")
    ap.add_argument("--no-images", action="store_true", help="不嵌入 data:image 图像")
    ap.add_argument("--max-slides", type=int, default=80,
                    help="deck 页数上限（默认 80；超出即截断并告警，提示先提炼提纲）。0=不限")
    args = ap.parse_args()
    if not args.json and not args.md:
        ap.error("--json 或 --md 必须提供一个")

    p = args.profile.strip()
    if p.startswith("{"):
        cfg = dict(PPT_PROFILES["default"]); cfg.update(json.loads(p))
    elif p.endswith(".json"):
        cfg = dict(PPT_PROFILES["default"])
        cfg.update(json.load(open(p, encoding="utf-8")))
    else:
        if p in PPT_PROFILES:
            cfg = PPT_PROFILES[p]
        elif p in DOC_PROFILES:
            d = DOC_PROFILES[p]
            cfg = {"title_east": d.get("heading_east", "微软雅黑"),
                   "body_east": d.get("body_east", "微软雅黑"),
                   "title_size": 28, "body_size": 18, "section_size": 32}
        else:
            ap.error("--profile 未知预设 %r（可选：%s，或 JSON 自定义）"
                     % (p, "/".join(sorted(PPT_PROFILES))))

    if args.md:
        data = {"markdown": open(args.md, encoding="utf-8").read(), "source": args.md}
    else:
        data = json.load(open(args.json, encoding="utf-8"))

    if data.get("sources") or data.get("analysis"):
        sources = list(data.get("sources") or [])
        analysis = data.get("analysis")
        if analysis:
            ana = dict(analysis) if isinstance(analysis, dict) else {"markdown": str(analysis)}
            ana.setdefault("source", "整合分析")
            sources.insert(0, ana)
    else:
        sources = [data]

    # 多源合并：各源拼为一个 H1 章节（→ 章节页），单 deck 顺序渲染
    if len(sources) > 1:
        merged = []
        for i, s in enumerate(sources):
            name = (s.get("source") or "来源 %d" % (i + 1)).strip()
            merged.append("# %s\n\n%s" % (name, s.get("markdown") or ""))
        data_md = "\n\n".join(merged)
        deck = build(data_md, cfg, title=args.title,
                     section_level=args.section_level, split_level=args.split_level,
                     max_bullets=args.max_bullets, max_chars=args.max_chars,
                     ratio=args.ratio, strip=args.strip_emoji,
                     embed_images=not args.no_images)
    else:
        deck = build(sources[0].get("markdown") or "", cfg, title=args.title,
                     section_level=args.section_level, split_level=args.split_level,
                     max_bullets=args.max_bullets, max_chars=args.max_chars,
                     ratio=args.ratio, strip=args.strip_emoji,
                     embed_images=not args.no_images)
    deck.save(args.out)
    from pptx import Presentation as P
    n = len(P(args.out).slides)
    print("PPTX 已生成：%s（%d 页，%d 字节）"
          % (os.path.abspath(args.out), n, os.path.getsize(args.out)))


if __name__ == "__main__":
    main()
