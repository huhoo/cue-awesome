#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""omni2docx — PPTX 汇报渲染器（汇报场景：把文档/提纲变成可讲的 deck）

设计（参照 kimi pptx skill 的设计哲学，离线可复现、零外部资源）：
- 主题色系统：每个 profile 一套克制的三色体系（primary / accent / 中性灰），全程统一。
- 分页型版式：封面（hero）→ 目录（TOC）→ 章节分隔（带序号）→ 内容（标题栏+色条+要点）
  → 结束页。不再把正文逐段平铺成上百页（那是展示，不是汇报）。
- 栅格平衡：统一页边距、顶部标题栏、底部页脚（页码+来源），内容垂直居中防头重脚轻。
- 装饰克制：色条、分隔线、序号、彩色项目符号——均为无文本形状，不触发几何重叠审计。
- 表格美化：表头主题色底+白字、斑马纹、细边框。

约定（C 路线）：内容取舍交给 agent——agent 按 slide 组织好 markdown，引擎只负责把结构
映射为 deck 与制式排版。不做像素级版面复刻。
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
from pptx.util import Inches, Pt, Emu  # noqa: E402
from pptx.oxml.ns import qn  # noqa: E402
from pptx.dml.color import RGBColor  # noqa: E402

# deck 字体/字号制式：汇报场景字号显著大于文档场景
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

# 主题色系统：克制三色（primary + accent + 中性灰），背景以白/极浅灰为主，符合学术/商务规范
THEMES = {
    "default":  {"primary": "#2563EB", "ink": "#1E293B", "accent": "#0EA5E9",
                 "panel": "#F1F5F9", "text": "#1F2937", "muted": "#64748B",
                 "zebra": "#F8FAFC"},
    "academic": {"primary": "#1E3A8A", "ink": "#0F172A", "accent": "#B45309",
                 "panel": "#F8FAFC", "text": "#1E293B", "muted": "#475569",
                 "zebra": "#F4F7FB"},
    "gov":      {"primary": "#B91C1C", "ink": "#7F1D1D", "accent": "#C8A24B",
                 "panel": "#FEF2F2", "text": "#1F2937", "muted": "#6B7280",
                 "zebra": "#FCF5F5"},
    "legal":    {"primary": "#9A2D2D", "ink": "#5B1616", "accent": "#B8862B",
                 "panel": "#FBF4F4", "text": "#1F2937", "muted": "#6B7280",
                 "zebra": "#FAF3F3"},
    "finance":  {"primary": "#0F766E", "ink": "#134E4A", "accent": "#B45309",
                 "panel": "#F0FDFA", "text": "#1F2937", "muted": "#64748B",
                 "zebra": "#F3FBF9"},
}


def rgb(hexstr):
    h = hexstr.lstrip("#")
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


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
    return clean_cjk_spaces(t).strip()  # 清 OCR 残留的 CJK 字间空格（拉丁逐字母空格不可还原，不强修)


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


def add_line(tf, text, size, east, bold=False, color=None, level=0, space_after=6,
             align=None, marker=None):
    """加一行。marker=(color_hex, glyph) 时渲染彩色项目符号前置 run。"""
    p = tf.paragraphs[0] if (not tf.paragraphs[0].runs and not tf.paragraphs[0].text) else tf.add_paragraph()
    p.level = level
    p.space_after = Pt(space_after)
    if align is not None:
        p.alignment = align
    if marker:
        rm = p.add_run()
        rm.text = marker[1] + " "
        rm.font.size = Pt(size)
        rm.font.bold = True
        rm.font.color.rgb = rgb(marker[0])
        set_east(rm, east)
    r = p.add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.bold = bold
    if color:
        r.font.color.rgb = rgb(color)
    set_east(r, east)
    return p


def fill_solid(shape, hexstr):
    shape.fill.solid()
    shape.fill.fore_color.rgb = rgb(hexstr)
    shape.line.fill.background()


def no_line(shape):
    shape.line.fill.background()


def _set_cell_border(cell):
    """给单元格加四边细灰边框（python-pptx Cell 无 border_size，走 XML）。"""
    from pptx.oxml.ns import nsdecls
    from pptx.oxml import parse_xml
    tcPr = cell._tc.get_or_add_tcPr()
    for tag in ("a:lnL", "a:lnR", "a:lnT", "a:lnB"):
        el = tcPr.find(qn(tag))
        if el is not None:
            tcPr.remove(el)
    node = parse_xml(
        '<a:tcPr %s>'
        '<a:lnL w="6350" cap="flat"><a:solidFill><a:srgbClr val="BFBFBF"/></a:solidFill></a:lnL>'
        '<a:lnR w="6350" cap="flat"><a:solidFill><a:srgbClr val="BFBFBF"/></a:solidFill></a:lnR>'
        '<a:lnT w="6350" cap="flat"><a:solidFill><a:srgbClr val="BFBFBF"/></a:solidFill></a:lnT>'
        '<a:lnB w="6350" cap="flat"><a:solidFill><a:srgbClr val="BFBFBF"/></a:solidFill></a:lnB>'
        '</a:tcPr>' % nsdecls("a"))
    for child in list(node):
        tcPr.append(child)


class Deck:
    """带主题与分页型版式的 deck 构造器。"""

    def __init__(self, cfg, theme, ratio="16:9"):
        self.prs = Presentation()
        if ratio == "16:9":
            self.prs.slide_width, self.prs.slide_height = Inches(13.333), Inches(7.5)
        elif ratio == "4:3":
            self.prs.slide_width, self.prs.slide_height = Inches(10), Inches(7.5)
        else:  # 自定义尺寸（英寸元组字符串 "13.333,7.5"）
            try:
                w, h = (float(x) for x in str(ratio).split(","))
                self.prs.slide_width, self.prs.slide_height = Inches(w), Inches(h)
            except Exception:
                self.prs.slide_width, self.prs.slide_height = Inches(13.333), Inches(7.5)
        self.cfg = cfg
        self.theme = theme
        self.W = float(self.prs.slide_width)
        self.H = float(self.prs.slide_height)
        self.blank = self.prs.slide_layouts[6]
        self.M = Inches(0.6)            # 统一页边距
        self.mw = self.W - 2 * self.M   # 内容宽度
        self.page_no = 0

    def slide(self, bg=None):
        s = self.prs.slides.add_slide(self.blank)
        if bg:
            s.background.fill.solid()
            s.background.fill.fore_color.rgb = rgb(bg)
        else:
            s.background.fill.solid()
            s.background.fill.fore_color.rgb = rgb("#FFFFFF")
        return s

    @property
    def n_slides(self):
        return len(self.prs.slides._sldIdLst)

    # ---------- 通用装饰 ----------
    def _footer(self, s, source):
        """底部页脚：左来源、右页码；下方细线。所有文本 >=11pt，避免过小字号审计。"""
        y = self.H - Inches(0.46)
        no_line(s.shapes.add_shape(1, self.M, y, self.mw, Pt(1.2)))  # 分隔细线（rect）
        # 来源（左）
        tf = s.shapes.add_textbox(self.M, self.H - Inches(0.42), self.mw * 0.7, Inches(0.32)).text_frame
        tf.word_wrap = True
        add_line(tf, ("来源：" + source) if source else "Omni 解析重建 · 汇报版", 11,
                 self.cfg.get("body_east", "微软雅黑"), color=self.theme["muted"])
        # 页码（右）
        self.page_no += 1
        tf2 = s.shapes.add_textbox(self.W - self.M - Inches(1.2), self.H - Inches(0.42),
                                   Inches(1.2), Inches(0.32)).text_frame
        tf2.word_wrap = False
        add_line(tf2, "%02d" % self.page_no, 11, self.cfg.get("body_east", "微软雅黑"),
                 color=self.theme["muted"], align=3)  # 3=right

    def _accent_bar(self, s, x, y, w, h, color=None):
        shp = s.shapes.add_shape(1, x, y, w, h)  # 1=rectangle
        fill_solid(shp, color or self.theme["primary"])
        return shp

    # ---------- 分页型 ----------
    def cover_slide(self, title, subtitle, source):
        s = self.slide(bg=self.theme["panel"])
        # 左侧主色竖条（无文本装饰）
        self._accent_bar(s, 0, 0, Inches(0.22), self.H, self.theme["primary"])
        # 顶部细线
        self._accent_bar(s, Inches(1.0), Inches(2.45), Inches(3.4), Pt(3), self.theme["accent"])
        tf = s.shapes.add_textbox(Inches(1.0), Inches(2.7), self.W - Inches(1.4), Inches(2.0)).text_frame
        tf.word_wrap = True
        add_line(tf, title, self.cfg.get("section_size", 32) + 12,
                 self.cfg.get("title_east", "微软雅黑"), bold=True,
                 color=self.theme["ink"], space_after=10)
        if subtitle:
            tf2 = s.shapes.add_textbox(Inches(1.0), Inches(4.7), self.W - Inches(1.4), Inches(1.2)).text_frame
            tf2.word_wrap = True
            add_line(tf2, subtitle, self.cfg.get("body_size", 18),
                     self.cfg.get("body_east", "微软雅黑"), color=self.theme["muted"])
        self._footer(s, source)
        return s

    def toc_slide(self, title, entries, source):
        s = self.slide()
        self._title_bar(s, "目录")
        # 条目：序号 + 标题，左色条装饰
        top = Inches(1.95)
        row_h = min(Inches(0.62), (self.H - top - Inches(0.7)) / max(len(entries), 1))
        for i, e in enumerate(entries):
            ey = top + row_h * i
            self._accent_bar(s, self.M, ey + Inches(0.06), Inches(0.1), row_h - Inches(0.12), self.theme["accent"])
            tf = s.shapes.add_textbox(self.M + Inches(0.32), ey, self.mw - Inches(0.32), row_h).text_frame
            tf.word_wrap = True
            add_line(tf, "%02d  %s" % (i + 1, e), self.cfg.get("body_size", 18),
                     self.cfg.get("body_east", "微软雅黑"), color=self.theme["text"])
        self._footer(s, source)
        return s

    def section_slide(self, title, idx):
        s = self.slide(bg=self.theme["panel"])
        self._accent_bar(s, 0, 0, self.W, Inches(0.16), self.theme["primary"])
        # 大号序号（无文本装饰，单独 textbox）
        nf = s.shapes.add_textbox(Inches(0.8), Inches(2.4), Inches(2.6), Inches(2.4)).text_frame
        nf.word_wrap = False
        add_line(nf, "%02d" % (idx or 1), 90, self.cfg.get("title_east", "微软雅黑"),
                 bold=True, color=self.theme["accent"])
        tf = s.shapes.add_textbox(Inches(3.4), Inches(3.0), self.W - Inches(4.0), Inches(1.8)).text_frame
        tf.word_wrap = True
        add_line(tf, title, self.cfg.get("section_size", 32),
                 self.cfg.get("title_east", "微软雅黑"), bold=True, color=self.theme["ink"])
        self._footer(s, None)
        return s

    def _title_bar(self, s, title):
        tf = s.shapes.add_textbox(self.M, Inches(0.5), self.mw, Inches(0.95)).text_frame
        tf.word_wrap = True
        # 标题过长自动降字号（避免溢出标题区）
        t = len(title)
        ts = (self.cfg.get("title_size", 28) - 6 if t > 70 else
              self.cfg.get("title_size", 28) - 3 if t > 40 else self.cfg.get("title_size", 28))
        add_line(tf, title, ts, self.cfg.get("title_east", "微软雅黑"), bold=True,
                 color=self.theme["ink"], space_after=2)
        self._accent_bar(s, self.M, Inches(1.5), Inches(2.6), Pt(4), self.theme["accent"])

    def content_slide(self, title, items, tables=None, images=None, notes=None, source=None):
        """items: [("bullet"|"text"|"note", 文本)]；tables: [(header, rows)]。"""
        tables = tables or []
        images = images or []
        s = self.slide()
        self._title_bar(s, title)

        top = Inches(1.85)
        avail_h = self.H - top - Inches(0.7)
        left_w = self.mw * (0.55 if images else 1.0)
        # 内容区左侧装饰竖条（无文本）
        self._accent_bar(s, self.M, top, Pt(4), avail_h, self.theme["accent"])

        if items:
            body = s.shapes.add_textbox(self.M + Inches(0.28), top, left_w - Inches(0.28), avail_h)
            btf = body.text_frame
            btf.word_wrap = True
            for kind, text in items:
                if kind == "note":
                    add_line(btf, text, max(self.cfg.get("body_size", 18) - 3, 11),
                             self.cfg.get("body_east", "微软雅黑"), color=self.theme["muted"],
                             space_after=8)
                elif kind == "bullet":
                    add_line(btf, text, self.cfg.get("body_size", 18),
                             self.cfg.get("body_east", "微软雅黑"),
                             marker=(self.theme["primary"], "▪"), space_after=10)
                else:
                    add_line(btf, text, self.cfg.get("body_size", 18),
                             self.cfg.get("body_east", "微软雅黑"), space_after=8)

        cur_top = top
        for header, rows in tables:
            n_rows, n_cols = len(rows) + 1, max(len(header), max((len(r) for r in rows), default=1))
            tbl_h = min(Inches(0.34) * n_rows + Inches(0.2), avail_h - Inches(0.1))
            gt = s.shapes.add_table(n_rows, n_cols, self.M + Inches(0.28), cur_top,
                                    left_w - Inches(0.28), tbl_h)
            tbl = gt.table
            fsize = Pt(14 if n_cols <= 3 else 12 if n_cols <= 5 else 10)
            # 表头：主题色底 + 白字
            for j, c in enumerate(header):
                cell = tbl.cell(0, j)
                cell.text = plain(c)[:60]
                cell.fill.solid(); cell.fill.fore_color.rgb = rgb(self.theme["primary"])
                cell.vertical_anchor = 3
                for p in cell.text_frame.paragraphs:
                    p.alignment = 1
                    for r in p.runs:
                        r.font.size = fsize; r.font.bold = True
                        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                        set_east(r, self.cfg.get("title_east", "微软雅黑"))
            for i, row in enumerate(rows, start=1):
                zebra = self.theme["zebra"] if i % 2 == 0 else "#FFFFFF"
                for j, c in enumerate(row[:n_cols]):
                    cell = tbl.cell(i, j)
                    cell.text = plain(c)[:80]
                    cell.fill.solid(); cell.fill.fore_color.rgb = rgb(zebra)
                    cell.vertical_anchor = 3
                    for p in cell.text_frame.paragraphs:
                        p.alignment = 1  # 左对齐（PP_PARAGRAPH_ALIGNMENT.LEFT=1）
                        for r in p.runs:
                            r.font.size = fsize
                            r.font.color.rgb = rgb(self.theme["text"])
                            set_east(r, self.cfg.get("body_east", "微软雅黑"))
            # 细边框（XML 设置，python-pptx Cell 无 border_size 属性）
            for r_idx in range(n_rows):
                for c_idx in range(n_cols):
                    _set_cell_border(tbl.cell(r_idx, c_idx))
            cur_top = cur_top + tbl_h + Inches(0.15)

        for img_bytes, alt in images:
            try:
                s.shapes.add_picture(io.BytesIO(img_bytes),
                                     self.M + left_w + Inches(0.2), top,
                                     width=(self.W - left_w - self.M - Inches(0.4)))
            except Exception:
                pass

        if notes:
            s.notes_slide.notes_text_frame.text = notes
        self._footer(s, source)
        return s

    def closing_slide(self, source):
        s = self.slide(bg=self.theme["panel"])
        self._accent_bar(s, 0, 0, self.W, Inches(0.16), self.theme["primary"])
        tf = s.shapes.add_textbox(Inches(1.0), Inches(2.9), self.W - Inches(2.0), Inches(1.6)).text_frame
        tf.word_wrap = True
        add_line(tf, "谢谢", self.cfg.get("section_size", 32) + 16,
                 self.cfg.get("title_east", "微软雅黑"), bold=True,
                 color=self.theme["ink"], align=2)
        self._footer(s, source)
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


def build(md, cfg, theme, title=None, section_level=1, split_level=2, max_bullets=6,
          max_chars=760, ratio="16:9", strip=False, embed_images=True, prose="notes",
          max_slides=80, source=""):
    """prose：正文段落去向——notes（默认，进演讲者备注）/ body（上正文区）/ skip（丢弃）。

    汇报语义：要点、表格、图像上页；正文细节进备注页，避免长文档被逐段平铺成上百页。
    """
    if strip:
        md = strip_emoji(md)
    md, foot = extract_footnotes(md)
    t_title, md = extract_title(md)
    doc_title = title or t_title
    blocks = parse_blocks(md)
    deck = Deck(cfg, theme, ratio)

    if doc_title:
        deck.cover_slide(doc_title, "Omni 解析重建 · 汇报版", source)

    cur_title = None
    cur_items, cur_tables, cur_images, cur_notes = [], [], [], []
    pending_notes = []
    capped = [False]
    sec_idx = [0]

    def room():
        if max_slides and deck.n_slides >= max_slides:
            capped[0] = True
            return False
        return True

    def flush():
        nonlocal cur_items, cur_tables, cur_images, cur_notes, pending_notes
        notes = "\n".join(x for x in (pending_notes + cur_notes) if x).strip() or None
        if not (cur_items or cur_tables or cur_images):
            if cur_title and cur_title != "要点":
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
                               notes=(notes if pi == 0 else None), source=source)
        cur_items, cur_tables, cur_images, cur_notes = [], [], [], []
        pending_notes = []

    for kind, payload, _ in blocks:
        if kind == "heading":
            lvl, text = int(payload[0]), plain(payload[1])
            if lvl <= section_level:
                flush()
                cur_title = None
                sec_idx[0] += 1
                if room():
                    deck.section_slide(text, sec_idx[0])
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
    # 此时按要点页平铺，保证有可讲的内容页。
    leftover = [x for x in (pending_notes + cur_notes) if x]
    if leftover and deck.n_slides <= (1 if doc_title else 0):
        pages = chunk([("bullet", t) for t in leftover], max_bullets, max_chars)
        for pi, pg in enumerate(pages):
            if not room():
                break
            deck.content_slide("要点" if pi == 0 else "要点（续 %d）" % (pi + 1), pg, source=source)
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
    if foot:
        try:
            last = deck.prs.slides[-1]
            tf = last.notes_slide.notes_text_frame
            tf.text = (tf.text or "") + "\n注释：" + "；".join(
                "%s %s" % (k, plain(v)) for k, v in foot)
        except Exception:
            pass
    # 结束页
    if room():
        deck.closing_slide(source)
    if capped[0]:
        sys.stderr.write("警告：达到 --max-slides=%d 上限，已截断；"
                         "建议 agent 先提炼提纲再渲染 deck。\n" % max_slides)
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
    ap.add_argument("--max-bullets", type=int, default=6, help="每页最多要点数（超出续页）")
    ap.add_argument("--max-chars", type=int, default=760, help="每页正文字符上限（超出续页）")
    ap.add_argument("--prose", default="notes", choices=["notes", "body", "skip"],
                    help="正文段落去向：notes=演讲者备注（默认，汇报语义）/ body=上正文区 / skip=丢弃")
    ap.add_argument("--ratio", default="16:9", help="16:9 / 4:3 / 自定义 'w,h'（英寸）")
    ap.add_argument("--strip-emoji", action="store_true")
    ap.add_argument("--no-images", action="store_true", help="不嵌入 data:image 图像")
    ap.add_argument("--max-slides", type=int, default=80,
                    help="deck 页数上限（默认 80；超出即截断并告警）。0=不限")
    ap.add_argument("--source-label", default="", help="页脚来源署名（默认空）")
    args = ap.parse_args()
    if not args.json and not args.md:
        ap.error("--json 或 --md 必须提供一个")

    p = args.profile.strip()
    if p.startswith("{"):
        cfg = dict(PPT_PROFILES["default"]); cfg.update(json.loads(p))
        theme = dict(THEMES["default"])
    elif p.endswith(".json"):
        cfg = dict(PPT_PROFILES["default"])
        cfg.update(json.load(open(p, encoding="utf-8")))
        theme = dict(THEMES["default"])
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
        theme = THEMES.get(p, THEMES["default"])

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

    src_label = args.source_label or (sources[0].get("source") if len(sources) == 1 else "")

    # 多源合并：各源拼为一个 H1 章节（→ 章节页），单 deck 顺序渲染
    if len(sources) > 1:
        merged = []
        for i, s in enumerate(sources):
            name = (s.get("source") or "来源 %d" % (i + 1)).strip()
            merged.append("# %s\n\n%s" % (name, s.get("markdown") or ""))
        data_md = "\n\n".join(merged)
        deck = build(data_md, cfg, theme, title=args.title,
                     section_level=args.section_level, split_level=args.split_level,
                     max_bullets=args.max_bullets, max_chars=args.max_chars,
                     ratio=args.ratio, strip=args.strip_emoji,
                     embed_images=not args.no_images, source=src_label)
    else:
        deck = build(sources[0].get("markdown") or "", cfg, theme, title=args.title,
                     section_level=args.section_level, split_level=args.split_level,
                     max_bullets=args.max_bullets, max_chars=args.max_chars,
                     ratio=args.ratio, strip=args.strip_emoji,
                     embed_images=not args.no_images, source=src_label)
    deck.save(args.out)
    from pptx import Presentation as P
    n = len(P(args.out).slides)
    print("PPTX 已生成：%s（%d 页，%d 字节）"
          % (os.path.abspath(args.out), n, os.path.getsize(args.out)))


if __name__ == "__main__":
    main()
