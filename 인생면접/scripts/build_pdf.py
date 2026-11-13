# -*- coding: utf-8 -*-
"""이력서 · 나 소개서 PDF 생성 (HTML → Chromium PDF).

사용법:  python3 scripts/build_pdf.py
"""
import html
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from content import INTRO, RESUME, segments  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "scripts", "build")


def rich(text):
    """'{{빈칸}}' 은 회색 span, '**굵게**' 는 b 로 바꾼 HTML."""
    out = []
    for seg, kind in segments(text):
        seg = html.escape(seg)
        out.append(f'<span class="blank">{seg}</span>' if kind == "blank"
                   else f"<b>{seg}</b>" if kind == "bold" else seg)
    return "".join(out)


BASE_CSS = """
@page { size: A4; margin: 0; }
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { background: #fff; }
body {
  font-family: "Noto Sans CJK KR", "NanumGothic", sans-serif;
  color: #1a1a1a; font-size: 9.6pt; line-height: 1.55;
  -webkit-print-color-adjust: exact; print-color-adjust: exact;
}
.page { width: 210mm; padding: 13mm 18mm 0; }
.blank { color: #9a9a9a; }
"""

RESUME_CSS = BASE_CSS + """
.r-title { text-align: center; font-size: 22pt; font-weight: 700; letter-spacing: 6pt; line-height: 1.2; }
.tagline { text-align: center; color: #666; font-size: 9.4pt; margin: 1.4mm 0 4.2mm; }
h2.sec { font-size: 10.8pt; font-weight: 700; margin: 4.6mm 0 1.4mm; }
h2.sec::before { content: "■"; font-size: 8.5pt; margin-right: 1.6mm; position: relative; top: -1pt; }
table.grid { width: 100%; border-collapse: collapse; table-layout: fixed;
  border-top: 1.4pt solid #1a1a1a; border-bottom: 1pt solid #1a1a1a; }
table.grid th, table.grid td { border: 0.6pt solid #8c8c8c; padding: 1.2mm 2.2mm; height: 7.6mm;
  vertical-align: middle; word-break: keep-all; }
table.grid tr:first-child th, table.grid tr:first-child td { border-top: none; }
table.grid tr:last-child th, table.grid tr:last-child td { border-bottom: none; }
table.grid th { background: #efefef; font-weight: 600; text-align: center; }
table.grid td { text-align: center; }
table.grid td.left { text-align: left; }
table.grid tr.head th { background: #e3e3e3; }
td.photo { background: #fafafa; color: #9a9a9a; font-size: 9pt; line-height: 1.5; }
table.profile td { text-align: left; padding: 1.6mm 3mm; line-height: 1.5; }
table.profile td b { font-weight: 700; margin-right: 1mm; }
table.profile td div + div { margin-top: 0.4mm; }
.decl { margin-top: 5mm; text-align: center; }
.decl .date { margin-top: 2.2mm; }
.decl .sign { margin-top: 2mm; text-align: right; padding-right: 4mm; font-size: 10.5pt; }
"""

INTRO_CSS = BASE_CSS + """
body { font-size: 10.2pt; line-height: 1.75; }
.page { padding: 15mm 18mm 0; }
.i-head { display: flex; justify-content: space-between; align-items: flex-end;
  border-bottom: 1.2pt solid #1a1a1a; padding-bottom: 2mm; }
.i-title { font-size: 20pt; font-weight: 700; line-height: 1.15; }
.i-meta { font-size: 9pt; color: #333; }
.i-meta span + span { margin-left: 4.5mm; }
p.body { font-family: "Noto Serif CJK KR", "NanumMyeongjo", serif; text-align: justify;
  text-indent: 3.2mm; margin-bottom: 1.3mm; word-break: keep-all; }
p.lead { margin-top: 4.5mm; }
h2 { font-size: 11.8pt; font-weight: 700; margin: 6mm 0 1.8mm; }
table.kw { width: 100%; border-collapse: collapse; table-layout: fixed; margin: 1.6mm 0 2.4mm; }
table.kw th, table.kw td { border: 0.6pt solid #8c8c8c; }
table.kw th { background: #efefef; font-size: 10.5pt; font-weight: 700; padding: 1.2mm 0; }
table.kw td { vertical-align: top; padding: 2.4mm 3mm 2.6mm;
  font-family: "Noto Serif CJK KR", "NanumMyeongjo", serif; font-size: 9.8pt;
  line-height: 1.68; word-break: keep-all; }
"""


def resume_html():
    r = RESUME
    parts = [f'<h1 class="r-title">{r["title"]}</h1>',
             f'<p class="tagline">{rich(r["tagline"])}</p>']

    # 인적사항
    rows = []
    for i, row in enumerate(r["personal"]):
        cells = []
        if i == 0:
            cells.append(f'<td class="photo" rowspan="{len(r["personal"])}">사 진<br>(3 × 4 cm)</td>')
        if len(row) == 4:
            cells += [f"<th>{row[0]}</th>", f'<td class="left">{rich(row[1])}</td>',
                      f"<th>{row[2]}</th>", f'<td class="left">{rich(row[3])}</td>']
        else:
            cells += [f"<th>{row[0]}</th>", f'<td class="left" colspan="3">{rich(row[1])}</td>']
        rows.append("<tr>" + "".join(cells) + "</tr>")
    parts.append(
        '<table class="grid personal" style="height:40mm"><colgroup>'
        '<col style="width:31mm"><col style="width:22mm"><col><col style="width:22mm"><col>'
        "</colgroup>" + "".join(rows) + "</table>"
    )

    for sec in r["sections"]:
        total = sum(sec["widths"])
        cols = "".join(f'<col style="width:{w / total * 100:.2f}%">' for w in sec["widths"])
        head = '<tr class="head">' + "".join(f"<th>{h}</th>" for h in sec["header"]) + "</tr>"
        body = ""
        for row in sec["rows"]:
            body += "<tr>" + "".join(f"<td>{rich(c)}</td>" for c in row) + "</tr>"
        parts.append(f'<h2 class="sec">{html.escape(sec["title"])}</h2>')
        parts.append(f'<table class="grid"><colgroup>{cols}</colgroup>{head}{body}</table>')

    parts.append(f'<h2 class="sec">{r["profile_title"]}</h2>')
    rows = "".join(
        f'<tr><th>{k}</th><td>' + "".join(f"<div>{rich(line)}</div>" for line in v) + "</td></tr>"
        for k, v in r["profile"]
    )
    parts.append('<table class="grid profile"><colgroup><col style="width:40mm"><col>'
                 f"</colgroup>{rows}</table>")

    parts.append(
        f'<div class="decl"><div>{r["declaration"]}</div>'
        f'<div class="date">{rich(r["date"])}</div>'
        f'<div class="sign">{rich(r["signer"])}</div></div>'
    )
    return page("이력서", RESUME_CSS, "".join(parts))


def intro_html():
    d = INTRO
    meta = "".join(f"<span>{k}: {rich(v)}</span>" for k, v in d["meta"])
    parts = [
        f'<div class="i-head"><div class="i-title">{d["title"]}</div>'
        f'<div class="i-meta">{meta}</div></div>',
        f'<p class="body lead">{rich(d["lead"])}</p>',
    ]
    for sec in d["sections"]:
        parts.append(f'<h2>{sec["no"]}. {sec["title"]}</h2>')
        if "keywords" in sec:
            head = "".join(f'<th>{k["word"]}</th>' for k in sec["keywords"])
            body = "".join(f'<td>{rich(k["text"])}</td>' for k in sec["keywords"])
            parts.append(f'<table class="kw"><tr>{head}</tr><tr>{body}</tr></table>')
            parts.append(f'<p class="body">{rich(sec["after"])}</p>')
        else:
            parts += [f'<p class="body">{rich(p)}</p>' for p in sec["paragraphs"]]
    return page("나 소개서", INTRO_CSS, "".join(parts))


def page(title, css, body):
    return (f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>{title}</title>'
            f"<style>{css}</style></head><body><div class=\"page\">{body}</div></body></html>")


def main():
    os.makedirs(BUILD, exist_ok=True)
    jobs = [("이력서", resume_html()), ("나_소개서", intro_html())]
    args = []
    for name, doc in jobs:
        src = os.path.join(BUILD, f"{name}.html")
        with open(src, "w", encoding="utf-8") as f:
            f.write(doc)
        args += [src, os.path.join(ROOT, f"{name}.pdf")]
    subprocess.run(["node", os.path.join(ROOT, "scripts", "render_pdf.js"), *args], check=True)


if __name__ == "__main__":
    main()
