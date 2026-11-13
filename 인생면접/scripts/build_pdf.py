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
    """'{{...}}' 빈칸을 회색 span 으로 바꾼 HTML."""
    out = []
    for seg, blank in segments(text):
        seg = html.escape(seg)
        out.append(f'<span class="blank">{seg}</span>' if blank else seg)
    return "".join(out)


BASE_CSS = """
@page { size: A4; margin: 0; }
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { background: #fff; }
body {
  font-family: "Noto Sans CJK KR", "NanumGothic", sans-serif;
  color: #1d232b; font-size: 9.6pt; line-height: 1.55;
  -webkit-print-color-adjust: exact; print-color-adjust: exact;
}
.page { width: 210mm; padding: 13mm 18mm 0; }
.blank { color: #9aa4b1; }
"""

RESUME_CSS = BASE_CSS + """
.r-title { text-align: center; font-size: 22pt; font-weight: 700; letter-spacing: 6pt;
  color: #1f3a5f; line-height: 1.2; }
.tagline { text-align: center; color: #56657a; font-size: 9.6pt; margin: 1.4mm 0 4.2mm; }
h2.sec { font-size: 10.8pt; font-weight: 700; color: #1f3a5f; margin: 4.6mm 0 1.4mm;
  display: flex; align-items: center; gap: 2mm; }
h2.sec::before { content: ""; width: 2.4mm; height: 2.4mm; background: #1f3a5f; display: inline-block; }
table.grid { width: 100%; border-collapse: collapse; table-layout: fixed;
  border-top: 1.6pt solid #1f3a5f; border-bottom: 1pt solid #1f3a5f; }
table.grid th, table.grid td { border: 0.6pt solid #a8b4c3; padding: 1.2mm 2.2mm; height: 7.6mm;
  vertical-align: middle; word-break: keep-all; }
table.grid tr:first-child th, table.grid tr:first-child td { border-top: none; }
table.grid tr:last-child th, table.grid tr:last-child td { border-bottom: none; }
table.grid th { background: #edf1f6; color: #1f3a5f; font-weight: 600; text-align: center; }
table.grid td { text-align: center; }
table.grid td.left { text-align: left; }
table.grid tr.head th { background: #dfe6ef; }
td.photo { background: #fafbfc; color: #9aa4b1; font-size: 9pt; line-height: 1.5; }
table.profile td { text-align: left; padding-left: 3mm; }
.decl { margin-top: 5mm; text-align: center; }
.decl .date { margin-top: 2.2mm; }
.decl .sign { margin-top: 2mm; text-align: right; padding-right: 4mm; font-size: 10.5pt; }
"""

INTRO_CSS = BASE_CSS + """
body { font-size: 10pt; line-height: 1.72; }
.page { padding: 14mm 18mm 0; }
.i-head { display: flex; justify-content: space-between; align-items: flex-end;
  border-bottom: 1.6pt solid #1f3a5f; padding-bottom: 2.2mm; }
.i-title { font-size: 22pt; font-weight: 700; color: #1f3a5f; letter-spacing: 1pt; line-height: 1.15; }
.i-meta { font-size: 9pt; color: #56657a; text-align: right; line-height: 1.6; }
.i-meta b { color: #1f3a5f; font-weight: 600; margin-right: 1.2mm; }
.i-meta span + span::before { content: "|"; color: #c3ccd7; margin: 0 2.2mm; }
.headline { margin: 4.5mm 0 1mm; background: #f2f5f9; border-left: 1.6mm solid #1f3a5f;
  padding: 3mm 4.5mm; }
.headline .q { font-size: 13pt; font-weight: 700; color: #1f3a5f; line-height: 1.4; }
.headline p { margin-top: 1.2mm; color: #3b4654; font-size: 9.6pt; }
h2 { font-size: 11.6pt; font-weight: 700; color: #1f3a5f; margin-top: 5mm;
  display: flex; align-items: baseline; gap: 2.2mm; }
h2 .no { font-size: 10pt; color: #fff; background: #1f3a5f; border-radius: 1mm;
  padding: 0 1.6mm; line-height: 1.55; }
.sub { color: #56657a; font-size: 9.4pt; margin: 0.4mm 0 1.6mm; padding-left: 0.4mm; }
.essay p { font-family: "Noto Serif CJK KR", "NanumMyeongjo", serif; text-align: justify;
  text-indent: 3.2mm; margin-bottom: 1.3mm; word-break: keep-all; }
.kw { display: grid; grid-template-columns: repeat(3, 1fr); gap: 3mm; margin-top: 1mm; }
.kw .box { border: 0.7pt solid #b9c4d2; border-top: 1.6pt solid #1f3a5f; background: #fafbfd;
  padding: 2.6mm 3.2mm 3mm; }
.kw .word { font-size: 13pt; font-weight: 700; color: #1f3a5f; line-height: 1.3; }
.kw .cap { font-size: 8.8pt; color: #56657a; margin-bottom: 1.4mm; }
.kw .txt { font-family: "Noto Serif CJK KR", "NanumMyeongjo", serif; font-size: 9.5pt;
  line-height: 1.66; word-break: keep-all; }
.closing { margin-top: 2.4mm; text-align: center; color: #1f3a5f; font-weight: 600;
  font-size: 10pt; }
.closing.boxed { border-top: 0.7pt solid #b9c4d2; border-bottom: 0.7pt solid #b9c4d2;
  padding: 2.2mm 0; margin-top: 2.6mm; }
"""


def resume_html():
    r = RESUME
    parts = [f'<h1 class="r-title">{r["title"]}</h1>',
             f'<p class="tagline">“{rich(r["tagline"])}”</p>']

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
    rows = "".join(f'<tr><th>{k}</th><td>{rich(v)}</td></tr>' for k, v in r["profile"])
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
    meta = "".join(f"<span><b>{k}</b>{rich(v)}</span>" for k, v in d["meta"])
    parts = [
        f'<div class="i-head"><div class="i-title">{d["title"]}</div>'
        f'<div class="i-meta">{meta}</div></div>',
        f'<div class="headline"><div class="q">“{d["headline"]}”</div><p>{rich(d["lead"])}</p></div>',
    ]
    for sec in d["sections"]:
        parts.append(f'<h2><span class="no">{sec["no"]}</span>{sec["title"]}</h2>')
        parts.append(f'<div class="sub">{sec["subtitle"]}</div>')
        if "keywords" in sec:
            boxes = "".join(
                f'<div class="box"><div class="word">{k["word"]}</div>'
                f'<div class="cap">{k["caption"]}</div><div class="txt">{k["text"]}</div></div>'
                for k in sec["keywords"]
            )
            parts.append(f'<div class="kw">{boxes}</div>')
            parts.append(f'<div class="closing">{sec["closing"]}</div>')
        else:
            parts.append('<div class="essay">' + "".join(f"<p>{rich(p)}</p>" for p in sec["paragraphs"])
                         + "</div>")
            if sec.get("closing"):
                parts.append(f'<div class="closing boxed">{sec["closing"]}</div>')
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
