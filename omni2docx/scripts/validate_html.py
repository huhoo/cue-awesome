#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""HTML 产物保真 + 结构校验（与 validate_docx.py 同口径）。

用法：
  python validate_html.py --json <中间json或source/markdown字段> --html <产物.html>

判定与 docx 一致：以字符级 CJK 覆盖率（≥99%）为准；emoji 以 --strip-emoji
同口径从源文剥离后再比对，防止剥除误报。结构检查：目录锚点、表格、
源页标注、证据溯源附录的存在性（存在与否均为信息，不参与判定）。
"""
import argparse
import json
import os
import re
import sys
from collections import Counter
from html.parser import HTMLParser

CJK = re.compile(r"[\u4e00-\u9fff]")
EMOJI = re.compile(
    "[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F\u2190-\u21FF\u2B00-\u2BFF]")


class _Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.buf = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("style", "script"):
            self.skip += 1

    def handle_endtag(self, tag):
        if tag in ("style", "script"):
            self.skip = max(self.skip - 1, 0)

    def handle_data(self, data):
        if not self.skip:
            self.buf.append(data)


def text_of_html(path):
    p = _Text()
    p.feed(open(path, encoding="utf-8").read())
    return "".join(p.buf)


def norm_chars(s):
    s = EMOJI.sub("", s or "")
    return [c for c in s if CJK.match(c)]


def source_markdown(data):
    """单源取 markdown；多源取 sources[].markdown 拼接（与渲染口径一致）。"""
    if data.get("sources") or data.get("analysis"):
        parts = []
        ana = data.get("analysis")
        if ana:
            parts.append(ana.get("markdown") if isinstance(ana, dict) else str(ana))
        parts.extend(s.get("markdown") or "" for s in data.get("sources") or [])
        return "\n\n".join(parts)
    return data.get("markdown") or ""


def main():
    ap = argparse.ArgumentParser(description="omni2docx HTML 保真校验器")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--json", help="渲染时输入的中间 JSON")
    g.add_argument("--md", help="若用 --md 直出，则给该 markdown 文件（替代 --json 的源）")
    ap.add_argument("--html", required=True)
    ap.add_argument("--no-toc", action="store_true", help="渲染时未开目录则加此开关")
    args = ap.parse_args()

    if args.md:
        src_md = open(args.md, encoding="utf-8").read()
    else:
        src_md = source_markdown(json.load(open(args.json, encoding="utf-8")))

    html_raw = open(args.html, encoding="utf-8").read()
    html_text = text_of_html(args.html)

    src_cjk = Counter(norm_chars(src_md))
    out_cjk = Counter(norm_chars(html_text))
    if src_cjk:
        hit = sum(min(v, out_cjk.get(k, 0)) for k, v in src_cjk.items())
        coverage = hit / sum(src_cjk.values())
        missing = {k: v for k, v in src_cjk.items() if out_cjk.get(k, 0) < v}
    else:
        coverage, missing = 1.0, {}

    anchors = len(re.findall(r'id="[^"]+"', html_raw))
    toc = 'class="toc"' in html_raw
    pagemarks = html_raw.count('class="pagemark"')
    tables = html_raw.count("<table>")
    appendix = 'class="appendix"' in html_raw
    selfcontained = ("<style>" in html_raw and "http" not in
                     " ".join(re.findall(r'(?:src|href)="(http[^"]+)"', html_raw)))

    print("=" * 64)
    print("Omni2Docx HTML 保真 + 结构校验 :", os.path.basename(args.html))
    print("=" * 64)
    print("[内容保真]")
    print("  源文 CJK 字符种类 :", len(src_cjk))
    print("  HTML 含源文 CJK 覆盖率 : %.2f%%" % (coverage * 100))
    print("  缺失 CJK 字符(种类) :", len(missing), list(missing)[:20])
    print("[结构]")
    print("  锚点(id) 数 :", anchors)
    print("  目录 :", "有" if toc else ("无" if args.no_toc else "无（未加 --no-toc，异常）"))
    print("  源页标注 :", pagemarks)
    print("  表格数 :", tables)
    print("  溯源附录 :", "有" if appendix else "无")
    print("  自包含(无外链) :", "是" if selfcontained else "否")

    ok = coverage >= 0.99
    print("判定 :", "PASS" if ok else "FAIL（CJK 覆盖率 <99%）")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
