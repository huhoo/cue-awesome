#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""omni2docx — HTML 展示渲染器（展示场景：浏览器直接打开/分享，自包含单文件）

设计：复用 build_docx 的块解析（parse_blocks）与内联正则（INLINE_RE），
把同一份 Omni 解析结果渲染为 HTML；docx 引擎不做任何改动。
展示场景关注：可读排版、目录锚点跳转、源页标注、表格/脚注/引用还原、可打印（@page）。
"""
import argparse
import html
import json
import os
import re
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from build_docx import (  # noqa: E402
    DOC_PROFILES, INLINE_RE, EMOJI_RE,
    build_outline_map, build_segment_index, classify_visual, clean_cjk_spaces,
    derive_outline_from_markdown, extract_footnotes, extract_title,
    match_outline_level, page_for_byte, parse_blocks, split_row, strip_emoji,
)


def esc(t):
    return html.escape(t or "", quote=False)


def slug(text, used):
    s = re.sub(r"[^\w\u4e00-\u9fff]+", "-", (text or "").strip()).strip("-")[:40] or "s"
    base, i = s, 2
    while s in used:
        s = "%s-%d" % (base, i)
        i += 1
    used.add(s)
    return s


def inline(text, footnotes=None):
    """markdown 行内 → HTML（递归，支持粗体内嵌代码/链接/斜体）。"""
    out, pos = [], 0
    for m in INLINE_RE.finditer(text or ""):
        if m.start() > pos:
            out.append(esc(text[pos:m.start()]))
        tok = m.group(0)
        if tok.startswith("!["):
            mm = re.match(r"!\[([^\]]*)\]\(([^)]*)\)", tok)
            alt, src = (mm.group(1), mm.group(2)) if mm else ("", "")
            if src.startswith(("data:image", "http://", "https://")):
                out.append('<figure class="img"><img src="%s" alt="%s">'
                           '<figcaption>%s</figcaption></figure>'
                           % (html.escape(src, quote=True), esc(alt), esc(alt or "图像")))
            else:
                out.append('<span class="img-note">［图像：%s］</span>' % esc(alt or "图像"))
        elif tok.startswith("[^"):
            key = tok[2:-1]
            n = len(footnotes) + 1 if footnotes is not None else 1
            idx = n
            if footnotes is not None and key not in footnotes:
                footnotes[key] = len(footnotes) + 1
                idx = footnotes[key]
            out.append('<sup class="fn"><a href="#fn-%s" id="fnref-%s">[%s]</a></sup>'
                       % (esc(key), esc(key), idx))
        elif tok.startswith("〔"):
            out.append('<span class="srcnote">%s</span>' % esc(tok))
        elif tok.startswith("**") or tok.startswith("__"):
            out.append("<strong>%s</strong>" % inline(tok[2:-2], footnotes))
        elif tok.startswith("`"):
            out.append("<code>%s</code>" % esc(tok[1:-1]))
        elif tok.startswith("["):
            mm = re.match(r"\[([^\]]+)\]\(([^)]+)\)", tok)
            if mm:
                out.append('<a href="%s" target="_blank" rel="noopener">%s</a>'
                           % (html.escape(mm.group(2), quote=True), inline(mm.group(1), footnotes)))
            else:
                out.append(esc(tok))
        else:
            inner = tok[1:-1]
            # CJK 伪斜体：中文不用 <em>（渲染为机械倾斜），改用 <span class="cjk-em">
            if re.search(r"[\u4e00-\u9fff]", inner):
                out.append('<span class="cjk-em">%s</span>' % inline(inner, footnotes))
            else:
                out.append("<em>%s</em>" % inline(inner, footnotes))
        pos = m.end()
    if pos < len(text or ""):
        out.append(esc(text[pos:]))
    return "".join(out)


def spacing_css(ls):
    """行距容错：数值（≥12 视为磅值，否则倍数）/ 字符串（28pt、28磅、1.5倍、1.5x）。"""
    if ls is None:
        return "1.75"
    if isinstance(ls, (int, float)):
        return ("%gpt" % float(ls)) if float(ls) >= 12 else ("%g" % float(ls))
    s = str(ls).strip().lower()
    m = re.search(r"([0-9.]+)\s*(pt|磅|倍|x|em)?", s)
    if not m:
        return "1.75"
    val = float(m.group(1))
    unit = m.group(2)
    if unit in ("pt", "磅"):
        return "%gpt" % val
    if unit in ("倍", "x", "em"):
        return "%g" % val
    return ("%gpt" % val) if val >= 12 else ("%g" % val)


def css_for(pcfg, page_marks):
    east = pcfg.get("body_east", "宋体")
    latin = pcfg.get("body_latin")
    heast = pcfg.get("heading_east", "黑体")
    body = float(pcfg.get("body_size") or 10.5)
    hs = pcfg.get("heading_sizes") or [16, 14, 13, 12, 12, 12]
    title = float(pcfg.get("title_size") or 20)
    lh = spacing_css(pcfg.get("line_spacing"))
    ind = float(pcfg.get("first_line_indent") or 0)
    mg = pcfg.get("margins_cm") or {}
    mgc = "@page{size:A4;margin:%s}" % " ".join(
        "%gcm" % float(mg.get(k, 2.54)) for k in ("top", "right", "bottom", "left")
    ) if mg else "@page{size:A4;margin:2.54cm}"
    family = ('"%s",%s,"Microsoft YaHei","PingFang SC",sans-serif'
              % (east, ('"%s",' % latin) if latin else ""))
    hfamily = '"%s","Microsoft YaHei","PingFang SC",sans-serif' % heast
    return """
%s
:root{--f:%s;--hf:%s;--body:%gpt;--lh:%s}
*{box-sizing:border-box}
body{margin:0 auto;max-width:52rem;padding:2.5rem 1.5rem;font-family:var(--f);
 font-size:var(--body);line-height:var(--lh);color:#1a1a1a;background:#fff}
h1,h2,h3,h4,h5,h6{font-family:var(--hf);color:#000;font-weight:600;
 line-height:1.4;margin:1.4em 0 .6em}
h1{%gpt}h2{%gpt}h3{%gpt}h4{%gpt}h5{%gpt}h6{%gpt}
.doc-title{font-size:%gpt;text-align:center;margin:0 0 1.2em}
p{margin:.5em 0;text-align:justify%s}
ul,ol{margin:.5em 0 .5em 1.6em;padding:0}
li{margin:.25em 0}
table{border-collapse:collapse;width:100%%;margin:1em 0;font-size:.95em}
th,td{border:1px solid #b9b9b9;padding:.35em .6em;text-align:left;vertical-align:top}
th{background:#f2f2f2;font-family:var(--hf)}
blockquote{margin:1em 0;padding:.6em 1em;border-left:3px solid #c8c8c8;
 background:#fafafa;font-family:%s;color:#333}
code{font-family:Consolas,Monaco,monospace;background:#f4f4f4;padding:.1em .3em;
 border-radius:3px;font-size:.9em}
.srcnote{color:#8a8a8a;font-size:.85em}
.cjk-em{font-weight:600}
.fn a{text-decoration:none;color:#185FA5}
.visual{background:#f5f5f0;border-left:3px solid #d0d0c0;padding:.5em .9em;
 margin:.8em 0;color:#555;font-size:.92em}
.img-note{color:#8a8a8a;font-size:.85em}
figure.img{margin:1em 0}figure.img img{max-width:100%%}
figure.img figcaption{color:#777;font-size:.85em;text-align:center;margin-top:.3em}
nav.toc{background:#fafafa;border:1px solid #e3e3e3;border-radius:8px;
 padding:1em 1.2em;margin:0 0 2em}
nav.toc summary{cursor:pointer;font-family:var(--hf);font-weight:600}
nav.toc ol{margin:.6em 0 0 1.2em;padding:0;line-height:1.9}
nav.toc a{color:#185FA5;text-decoration:none}
nav.toc a:hover{text-decoration:underline}
.pagemark{display:block;color:#b0b0b0;font-size:.78em;margin:1.1em 0 .2em;
 border-top:1px dashed #e0e0e0;padding-top:.3em}
.meta{color:#777;font-size:.85em;text-align:center;margin:.2em 0 1.6em}
hr{border:0;border-top:1px solid #e0e0e0;margin:1.6em 0}
section.endnotes{margin-top:2.5em;border-top:1px solid #e0e0e0;padding-top:1em;
 font-size:.9em;color:#444}
section.endnotes ol{margin-left:1.4em}
section.appendix{margin-top:2.5em}
@media print{nav.toc{display:none}body{padding:0;max-width:none}
 a{color:#000;text-decoration:none}}
""" % (
        mgc, family, hfamily, body, lh,
        float(hs[0] if len(hs) > 0 else 16), float(hs[1] if len(hs) > 1 else 14),
        float(hs[2] if len(hs) > 2 else 13), float(hs[3] if len(hs) > 3 else 12),
        float(hs[4] if len(hs) > 4 else 12), float(hs[5] if len(hs) > 5 else 12),
        title,
        (";text-indent:%gem" % ind) if ind else "",
        '"%s",serif' % pcfg.get("quote_east", "楷体"),
    )


def block_html(kind, payload, used_ids, footnotes, outline_map, level_offset=0):
    """返回 (html, toc_entry or None)。"""
    if kind == "heading":
        lvl, text = payload
        mr = match_outline_level(text, outline_map)
        if mr:
            lvl = mr[0]
        lvl = min(max(int(lvl) + level_offset, 1), 6)
        sid = slug(text, used_ids)
        return ('<h%d id="%s">%s</h%d>' % (lvl, sid, inline(text, footnotes), lvl),
                (lvl, text, sid))
    if kind == "para":
        return ("<p>%s</p>" % inline(payload, footnotes), None)
    if kind == "quote":
        return ("<blockquote>%s</blockquote>" % inline(payload, footnotes), None)
    if kind in ("ul", "ol"):
        tag = "ol" if kind == "ol" else "ul"
        items = "".join("<li>%s</li>" % inline(x, footnotes) for x in payload)
        return ("<%s>%s</%s>" % (tag, items, tag), None)
    if kind == "table":
        header, rows = payload
        th = "".join("<th>%s</th>" % inline(c, footnotes) for c in header)
        trs = "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % inline(c, footnotes) for c in r)
                      for r in rows)
        return ("<table><thead><tr>%s</tr></thead><tbody>%s</tbody></table>" % (th, trs), None)
    if kind == "hr":
        return ("<hr>", None)
    if kind == "visual":
        if isinstance(payload, (tuple, list)):
            label, text = payload[0], payload[1]
        else:
            label, text = "标注", str(payload)
        return ('<div class="visual"><strong>%s</strong>：%s</div>'
                % (esc(label), inline(text, footnotes)), None)
    return ("<p>%s</p>" % inline(str(payload), footnotes), None)


def render_source(md, outline, grounding, pcfg, used, page_marks=False, level_offset=0,
                  toc=True):
    md, foot = extract_footnotes(md)
    om = build_outline_map(outline) if outline else derive_outline_from_markdown(md)
    seg = build_segment_index(grounding) if grounding else []
    blocks = parse_blocks(md)
    body, toc_items = [], []
    footnotes = {}
    last_page = None
    for kind, payload, bstart in blocks:
        if seg:
            p = page_for_byte(seg, bstart)
            if p is not None and p != last_page:
                last_page = p
                cls = "pagemark"
                body.append('<span class="%s" data-page="%s">源第 %s 页</span>'
                            % (cls, esc(str(p)), esc(str(p))))
        h, toc_entry = block_html(kind, payload, used, footnotes, om, level_offset)
        body.append(h)
        if toc_entry:
            toc_items.append(toc_entry)
    return body, toc_items, footnotes, foot


def toc_html(items):
    if not items:
        return ""
    li = []
    for lvl, text, sid in items:
        li.append('<li style="margin-left:%dem"><a href="#%s">%s</a></li>'
                  % (max(lvl - 1, 0) * 1.2, sid, esc(text)))
    return ('<nav class="toc"><details open><summary>目录</summary><ol>%s</ol></details></nav>'
            % "".join(li))


def endnotes_html(foot):
    if not foot:
        return ""
    items = []
    for key, text in foot:
        items.append('<li id="fn-%s">%s</li>' % (esc(key), inline(text)))
    return '<section class="endnotes"><h2>注释</h2><ol>%s</ol></section>' % "".join(items)


def find_browser():
    cands = []
    if sys.platform.startswith("win"):
        for p in (r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                  r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
                  r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                  r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"):
            cands.append(p)
    elif sys.platform == "darwin":
        cands += ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                  "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"]
    else:
        cands += ["google-chrome", "chromium", "chromium-browser", "microsoft-edge"]
    for c in cands:
        if os.path.exists(c):
            return c
    for c in cands:
        from shutil import which
        if which(c):
            return which(c)
    return None


def html_to_pdf(html_path, pdf_path):
    browser = find_browser()
    if not browser:
        return False, "未找到 headless 浏览器（Edge/Chrome/Chromium），跳过 PDF"
    url = "file:///" + os.path.abspath(html_path).replace("\\", "/")
    try:
        subprocess.run([browser, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                        "--print-to-pdf=%s" % os.path.abspath(pdf_path), url],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
    except Exception as e:
        return False, "浏览器调用失败：%s" % e
    for _ in range(40):
        if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0:
            time.sleep(0.3)
            return True, os.path.abspath(pdf_path)
        time.sleep(0.25)
    return False, "浏览器未产出 PDF（超时）"


def main():
    ap = argparse.ArgumentParser(description="Omni 解析结果 → 展示用 HTML（自包含单文件）")
    ap.add_argument("--json", help="中间 JSON（markdown+grounding+outline）")
    ap.add_argument("--md", help="直接输入 markdown 文件（agent 产物/提纲）")
    ap.add_argument("--out", required=True, help="输出 .html")
    ap.add_argument("--profile", default="default",
                    help="场景制式：预设名（gov/legal/finance/academic/default）或内联 JSON / .json 文件")
    ap.add_argument("--no-toc", action="store_true", help="不生成目录")
    ap.add_argument("--page-marks", action="store_true", help="标注源页码（需 grounding）")
    ap.add_argument("--strip-emoji", action="store_true", help="剥离 emoji/装饰符号")
    ap.add_argument("--pdf", action="store_true", help="同时用 headless 浏览器导出 PDF（打印保真）")
    ap.add_argument("--title", help="覆盖文档标题")
    args = ap.parse_args()
    if not args.json and not args.md:
        ap.error("--json 或 --md 必须提供一个")

    if args.profile.strip().startswith("{"):
        pcfg = json.loads(args.profile)
    elif args.profile.strip().endswith(".json"):
        with open(args.profile.strip(), encoding="utf-8") as f:
            pcfg = json.load(f)
    else:
        if args.profile not in DOC_PROFILES:
            ap.error("--profile 未知预设 %r" % args.profile)
        pcfg = DOC_PROFILES[args.profile]

    if args.md:
        with open(args.md, encoding="utf-8") as f:
            data = {"markdown": f.read(), "source": args.md}
    else:
        with open(args.json, encoding="utf-8") as f:
            data = json.load(f)

    want_strip = args.strip_emoji or bool(pcfg.get("strip_emoji"))

    def prep(md):
        if want_strip:
            md = strip_emoji(md)
        return md

    used = set()
    doc_title = args.title or data.get("title")
    parts_head, parts_body, all_toc = [], [], []

    if data.get("sources") or data.get("analysis"):
        sources = list(data.get("sources") or [])
        analysis = data.get("analysis")
        if analysis:
            ana = dict(analysis) if isinstance(analysis, dict) else {"markdown": str(analysis)}
            ana.setdefault("source", "整合分析")
            sources.insert(0, ana)
        for i, s in enumerate(sources):
            md = prep(s.get("markdown") or "")
            t_title, md = extract_title(md)
            chapter = (s.get("source") or "来源 %d" % (i + 1)).strip()
            body, toc_items, footnotes, foot = render_source(
                md, s.get("outline"), s.get("grounding"), pcfg, used,
                args.page_marks, level_offset=1)
            all_toc.append((1, chapter, slug(chapter, used)))
            all_toc.extend(toc_items)
            parts_body.append('<article><h1 id="%s">%s</h1>%s%s</article>'
                              % (all_toc[-len(toc_items) - 1][2] if toc_items else slug(chapter, used),
                                 esc(chapter), "".join(body), endnotes_html(foot)))
        if data.get("sources"):
            rows = "".join(
                "<tr><td>%s</td><td>%s</td></tr>"
                % (esc((s.get("source") or "来源 %d" % (i + 1)).strip()),
                   esc(str(s.get("detail") or "")))
                for i, s in enumerate(data.get("sources") or []))
            parts_body.append('<section class="appendix"><h2>证据溯源附录</h2>'
                              '<table><thead><tr><th>来源</th><th>解析级别</th></tr>'
                              '</thead><tbody>%s</tbody></table></section>' % rows)
    else:
        md = prep(data.get("markdown") or "")
        t_title, md = extract_title(md)
        if not doc_title and t_title:
            doc_title = t_title
        body, toc_items, footnotes, foot = render_source(
            md, data.get("outline"), data.get("grounding"), pcfg, used, args.page_marks)
        parts_body.append("".join(body))
        parts_body.append(endnotes_html(foot))
        all_toc.extend(toc_items)

    if doc_title:
        parts_head.append('<h1 class="doc-title">%s</h1>' % esc(doc_title))
    if data.get("source") and not (data.get("sources") or data.get("analysis")):
        parts_head.append('<p class="meta">来源：%s</p>' % esc(str(data["source"])))
    if not args.no_toc:
        parts_head.append(toc_html(all_toc))

    doc = ("<!DOCTYPE html>\n<html lang=\"zh-CN\"><head><meta charset=\"utf-8\">"
           "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
           "<title>%s</title><style>%s</style></head><body>%s%s</body></html>\n"
           % (esc(doc_title or "Omni 文档"), css_for(pcfg, args.page_marks),
              "".join(parts_head), "".join(parts_body)))

    out = os.path.abspath(args.out)
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(doc)
    print("HTML 已生成：%s（%d 字节）" % (out, os.path.getsize(out)))

    if args.pdf:
        pdf_path = os.path.splitext(out)[0] + ".pdf"
        ok, msg = html_to_pdf(out, pdf_path)
        print("PDF：%s" % (msg if ok else "跳过 —— " + msg))


if __name__ == "__main__":
    main()
