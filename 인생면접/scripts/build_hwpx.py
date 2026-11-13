# -*- coding: utf-8 -*-
"""이력서 · 나 소개서 한글(HWPX) 파일 생성.

사용법:  pip install python-hwpx  →  python3 scripts/build_hwpx.py
"""
import copy
import os
import sys

from hwpx import HwpxDocument

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from content import INTRO, RESUME, segments  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MM = 7200 / 25.4  # HWPUNIT per mm
PAGE_W_MM, MARGIN_LR_MM = 210, 18
CONTENT_MM = PAGE_W_MM - 2 * MARGIN_LR_MM

HP = "{http://www.hancom.co.kr/hwpml/2011/paragraph}"
HH = "{http://www.hancom.co.kr/hwpml/2011/head}"

SANS, SERIF = "함초롬돋움", "함초롬바탕"
NAVY, INK, GRAY, BLANK = "#1F3A5F", "#1D232B", "#56657A", "#9AA4B1"
LINE, LINE2 = "#A8B4C3", "#B9C4D2"


def hu(mm):
    return int(round(mm * MM))


class Builder:
    def __init__(self, top_mm=13, bottom_mm=10):
        self.doc = HwpxDocument.new()
        self.doc.page.set_margins(left=hu(MARGIN_LR_MM), right=hu(MARGIN_LR_MM), top=hu(top_mm),
                                  bottom=hu(bottom_mm), header=0, footer=0)
        self.header = self.doc.oxml.headers[0]
        self._first = True
        self._bf_cache = {}
        self._cs_cache = {}
        self._tables = []

    # ------------------------------------------------------------ styles
    def cs(self, size=10, bold=False, color=INK, font=SANS, shade=None, tracking=None):
        key = (size, bold, color, font, shade, tracking)
        if key in self._cs_cache:
            return self._cs_cache[key]
        cid = self.doc.styles.ensure_run(font=font, size=size, bold=bold, color=color,
                                         letter_spacing=tracking)
        if shade:
            props = self.header.element.find(f".//{HH}charProperties")
            src = next(e for e in props.findall(f"{HH}charPr") if e.get("id") == str(cid))
            new = copy.deepcopy(src)
            cid = str(max(int(e.get("id")) for e in props.findall(f"{HH}charPr")) + 1)
            new.set("id", cid)
            new.set("shadeColor", shade)
            props.append(new)
            props.set("itemCnt", str(len(props.findall(f"{HH}charPr"))))
            self.header.mark_dirty()
        self._cs_cache[key] = cid
        return cid

    def bf(self, fill=None, color=LINE, width="0.12 mm", **sides):
        """테두리/배경. sides: top/bottom/left/right = None(없음) 또는 (굵기, 색)."""
        key = (fill, color, width, tuple(sorted(sides.items())))
        if key in self._bf_cache:
            return self._bf_cache[key]
        bid = self.doc.styles.ensure_border_fill(border_color=color, border_width=width, fill_color=fill)
        if sides:
            fills = self.header.element.find(f".//{HH}borderFills")
            src = next(e for e in fills.findall(f"{HH}borderFill") if e.get("id") == str(bid))
            new = copy.deepcopy(src)
            bid = str(max(int(e.get("id")) for e in fills.findall(f"{HH}borderFill")) + 1)
            new.set("id", bid)
            for side, spec in sides.items():
                el = new.find(f"{HH}{side}Border")
                if spec is None:
                    el.set("type", "NONE")
                else:
                    el.set("type", "SOLID")
                    el.set("width", spec[0])
                    el.set("color", spec[1])
            fills.append(new)
            fills.set("itemCnt", str(len(fills.findall(f"{HH}borderFill"))))
            self.header.mark_dirty()
        self._bf_cache[key] = bid
        return bid

    def fmt(self, p, **kw):
        self.doc.styles.apply_paragraph_format(paragraphs=[p], **kw)

    # ------------------------------------------------------------ content
    def para(self, runs, *, align="LEFT", spacing=160, before=0, after=0, indent=None):
        """runs: [(text, charPr id), ...]"""
        if self._first:  # 새 문서의 첫 문단(구역 정의 포함)을 그대로 쓴다
            p = self.doc.paragraphs[0]
            p.text = runs[0][0]
            p.char_pr_id_ref = runs[0][1]
            rest = runs[1:]
            self._first = False
        else:
            p = self.doc.add_paragraph("", include_run=False, inherit_style=False)
            rest = runs
        for text, cid in rest:
            p.add_run(text, char_pr_id_ref=cid)
        kw = dict(alignment=align, line_spacing_percent=spacing, spacing_before_pt=before,
                  spacing_after_pt=after)
        if indent is not None:
            kw["first_line_indent_mm"] = indent
        self.fmt(p, **kw)
        return p

    def rich(self, text, cid, blank_cid):
        return [(seg, blank_cid if blank else cid) for seg, blank in segments(text)]

    def table(self, rows, cols, widths_mm):
        if self._first:
            self.para([("", self.cs(2))], spacing=100)
        t = self.doc.add_table(rows, cols, width=hu(CONTENT_MM), border_fill_id_ref=self.bf(color=LINE))
        t.set_column_widths(widths_mm)
        # 표를 담는 문단: 줄 간격이 표 높이에 더해지지 않도록 100%, 위아래 여백 0
        self.fmt(t.paragraph, line_spacing_percent=100, spacing_before_pt=0, spacing_after_pt=0)
        self._tables.append((t, widths_mm))
        return t

    def _fix_table_geometry(self, t, widths_mm):
        """칸 너비를 mm 값 그대로(최소 너비 보정 없이) 맞추고, 표 크기를 칸 크기 합으로 기록한다."""
        total = hu(CONTENT_MM)
        scale = total / sum(widths_mm)
        cols = [int(round(w * scale)) for w in widths_mm]
        cols[-1] += total - sum(cols)
        rows = t.element.findall(f"{HP}tr")
        row_h = [0] * len(rows)
        cells = []
        for tr in rows:
            for tc in tr.findall(f"{HP}tc"):
                addr, span, size = tc.find(f"{HP}cellAddr"), tc.find(f"{HP}cellSpan"), tc.find(f"{HP}cellSz")
                c, r = int(addr.get("colAddr")), int(addr.get("rowAddr"))
                cs, rs = int(span.get("colSpan")), int(span.get("rowSpan"))
                size.set("width", str(sum(cols[c:c + cs])))
                if rs == 1:
                    row_h[r] = max(row_h[r], int(size.get("height")))
                cells.append((r, rs, size))
        for r, rs, size in cells:
            if rs > 1:
                size.set("height", str(sum(row_h[r:r + rs])))
        sz = t.element.find(f"{HP}sz")
        sz.set("width", str(total))
        sz.set("height", str(sum(row_h)))
        t.mark_dirty()

    def cell(self, t, r, c, paras, *, bf=None, height_mm=None, valign="CENTER", margin_mm=None):
        """paras: [ (runs, dict(align=..., spacing=..., before=..., after=...)), ... ]"""
        cell = t.cell(r, c)
        sub = cell._ensure_sublist()
        for p in list(sub.findall(f"{HP}p")):
            sub.remove(p)
        for runs, opts in paras:
            p = cell.add_paragraph(runs[0][0], char_pr_id_ref=runs[0][1])
            for text, cid in runs[1:]:
                p.add_run(text, char_pr_id_ref=cid)
            kw = dict(alignment=opts.get("align", "CENTER"), line_spacing_percent=opts.get("spacing", 130),
                      spacing_before_pt=opts.get("before", 0), spacing_after_pt=opts.get("after", 0))
            self.fmt(p, **kw)
        sub.set("vertAlign", valign)
        if bf is not None:
            t.set_cell_border_fill(r, c, bf)
        if height_mm is not None:
            cell.set_size(height=hu(height_mm))
        if margin_mm is not None:
            cell.element.set("hasMargin", "1")
            m = cell.element.find(f"{HP}cellMargin")
            for side, v in zip(("left", "right", "top", "bottom"), margin_mm):
                m.set(side, str(hu(v)))
        return cell

    def save(self, path):
        for t, widths in self._tables:
            self._fix_table_geometry(t, widths)
        report = self.doc.validate()
        if report.issues:
            raise SystemExit(f"검증 실패: {report.issues}")
        self.doc.save_to_path(path)
        print("wrote", path)


# ====================================================================== 이력서
def build_resume(path):
    b = Builder(top_mm=13, bottom_mm=10)
    r = RESUME
    td, blank = b.cs(9.5), b.cs(9.5, color=BLANK)
    th = b.cs(9.5, bold=True, color=NAVY)

    b.para([(r["title"], b.cs(22, bold=True, color=NAVY))], align="CENTER", spacing=120)
    b.para([("“" + r["tagline"] + "”", b.cs(9.5, color=GRAY))], align="CENTER", after=8)

    navy_top = ("0.5 mm", NAVY)
    navy_bottom = ("0.4 mm", NAVY)
    bf_th = b.bf(fill="#EDF1F6")
    bf_head = b.bf(fill="#DFE6EF", top=navy_top)
    bf_td = b.bf()

    def label(text, align="CENTER"):
        return [([(text, th)], dict(align=align))]

    def value(text, align="CENTER"):
        return [(b.rich(text, td, blank), dict(align=align))]

    # 인적사항 -----------------------------------------------------------
    rows = r["personal"]
    t = b.table(len(rows), 5, [31, 22, 49.5, 22, 49.5])
    t.merge_cells(0, 0, len(rows) - 1, 0)
    t.merge_cells(2, 2, 2, 4)
    t.merge_cells(3, 2, 3, 4)
    for i, row in enumerate(rows):
        edge = dict(top=navy_top) if i == 0 else dict(bottom=navy_bottom) if i == len(rows) - 1 else {}
        b.cell(t, i, 1, label(row[0]), bf=b.bf(fill="#EDF1F6", **edge), height_mm=10)
        b.cell(t, i, 2, value(row[1], "LEFT"), bf=b.bf(**edge), height_mm=10)
        if len(row) == 4:
            b.cell(t, i, 3, label(row[2]), bf=b.bf(fill="#EDF1F6", **edge), height_mm=10)
            b.cell(t, i, 4, value(row[3], "LEFT"), bf=b.bf(**edge), height_mm=10)
    photo = b.cs(9, color=BLANK)
    b.cell(t, 0, 0, [([("사 진", photo)], {}), ([("(3 × 4 cm)", photo)], {})],
           bf=b.bf(fill="#FAFBFC", top=navy_top, bottom=navy_bottom))

    def section_title(text):
        b.para([("■ ", b.cs(9, color=NAVY)), (text, b.cs(11, bold=True, color=NAVY))],
               before=10, after=3)

    # 표 섹션 -------------------------------------------------------------
    for sec in r["sections"]:
        section_title(sec["title"])
        n = len(sec["rows"]) + 1
        t = b.table(n, len(sec["header"]), sec["widths"])
        for c, h in enumerate(sec["header"]):
            b.cell(t, 0, c, label(h), bf=bf_head, height_mm=7.6)
        for i, row in enumerate(sec["rows"], start=1):
            last = i == n - 1
            for c, v in enumerate(row):
                cell_bf = b.bf(bottom=navy_bottom) if last else bf_td
                b.cell(t, i, c, value(v), bf=cell_bf, height_mm=7.6)

    # 나에 대하여 ---------------------------------------------------------
    section_title(r["profile_title"])
    n = len(r["profile"])
    t = b.table(n, 2, [40, CONTENT_MM - 40])
    for i, (k, v) in enumerate(r["profile"]):
        edge = dict(top=navy_top) if i == 0 else dict(bottom=navy_bottom) if i == n - 1 else {}
        h = 7.6 if len(v) < 40 else 11
        b.cell(t, i, 0, label(k), bf=b.bf(fill="#EDF1F6", **edge), height_mm=h)
        b.cell(t, i, 1, value(v, "LEFT"), bf=b.bf(**edge), height_mm=h, margin_mm=(3, 2, 1, 1))

    decl = b.cs(10)
    b.para([(r["declaration"], decl)], align="CENTER", before=14)
    b.para(b.rich(r["date"], decl, b.cs(10, color=BLANK)), align="CENTER", before=6)
    b.para(b.rich(r["signer"], b.cs(10.5), b.cs(10.5, color=BLANK)), align="RIGHT", before=6)
    b.save(path)


# ==================================================================== 나 소개서
def build_intro(path):
    b = Builder(top_mm=14, bottom_mm=10)
    d = INTRO
    body = b.cs(10, font=SERIF)
    navy_line = ("0.5 mm", NAVY)

    # 머리 (제목 | 이름·소속·작성일) ------------------------------------------
    t = b.table(1, 2, [52, CONTENT_MM - 52])
    head_bf = b.bf(top=None, left=None, right=None, bottom=navy_line)
    b.cell(t, 0, 0, [([(d["title"], b.cs(22, bold=True, color=NAVY))], dict(align="LEFT", spacing=110))],
           bf=head_bf, valign="BOTTOM", margin_mm=(0, 0, 0, 1.5))
    lab, val, blank = b.cs(9, bold=True, color=NAVY), b.cs(9, color=GRAY), b.cs(9, color=BLANK)
    sep = b.cs(9, color="#C3CCD7")
    runs = []
    for i, (k, v) in enumerate(d["meta"]):
        if i:
            runs.append(("   |   ", sep))
        runs.append((k + " ", lab))
        runs += b.rich(v, val, blank)
    b.cell(t, 0, 1, [(runs, dict(align="RIGHT"))], bf=head_bf, valign="BOTTOM", margin_mm=(0, 0, 0, 1.5))

    # 헤드라인 박스 --------------------------------------------------------
    b.para([("", b.cs(6))], spacing=100)
    t = b.table(1, 1, [CONTENT_MM])
    box_bf = b.bf(fill="#F2F5F9", top=None, right=None, bottom=None, left=("1.5 mm", NAVY))
    b.cell(t, 0, 0, [
        ([("“" + d["headline"] + "”", b.cs(13, bold=True, color=NAVY))], dict(align="LEFT", spacing=140)),
        (b.rich(d["lead"], b.cs(9.5, color="#3B4654"), blank), dict(align="LEFT", spacing=160, before=2)),
    ], bf=box_bf, margin_mm=(4.5, 4, 2.6, 2.6))

    for sec in d["sections"]:
        b.para([(f" {sec['no']} ", b.cs(10.5, bold=True, color="#FFFFFF", shade=NAVY)),
                ("  " + sec["title"], b.cs(11.5, bold=True, color=NAVY))], before=12, after=1)
        b.para([(sec["subtitle"], b.cs(9.5, color=GRAY))], after=3)
        if "keywords" in sec:
            gap = 3
            w = (CONTENT_MM - 2 * gap) / 3
            t = b.table(1, 5, [w, gap, w, gap, w])
            box = b.bf(fill="#FAFBFD", color=LINE2, top=navy_line)
            none = b.bf(top=None, bottom=None, left=None, right=None)
            for i, k in enumerate(sec["keywords"]):
                b.cell(t, 0, i * 2, [
                    ([(k["word"], b.cs(13, bold=True, color=NAVY))], dict(align="LEFT", spacing=130)),
                    ([(k["caption"], b.cs(9, color=GRAY))], dict(align="LEFT", after=3)),
                    ([(k["text"], b.cs(9.5, font=SERIF))], dict(align="LEFT", spacing=165)),
                ], bf=box, valign="TOP", margin_mm=(3.2, 3.2, 2.6, 3), height_mm=63)
                if i < 2:
                    b.cell(t, 0, i * 2 + 1, [([("", b.cs(6))], {})], bf=none)
            b.para([(sec["closing"], b.cs(9.5, bold=True, color=NAVY, tracking=-3))],
                   align="CENTER", before=6)
        else:
            for text in sec["paragraphs"]:
                b.para(b.rich(text, body, blank), align="JUSTIFY", spacing=170, after=2.5, indent=3.2)
            if sec.get("closing"):
                b.para([("", b.cs(4))], spacing=100)
                t = b.table(1, 1, [CONTENT_MM])
                closing = b.cs(10, bold=True, color=NAVY)
                lines = [ln.strip() + ("." if not ln.strip().endswith(".") else "")
                         for ln in sec["closing"].split(". ")]
                b.cell(t, 0, 0, [([(ln, closing)], dict(spacing=150)) for ln in lines],
                       bf=b.bf(color=LINE2, left=None, right=None), margin_mm=(1, 1, 2, 2))
    b.save(path)


if __name__ == "__main__":
    build_resume(os.path.join(ROOT, "이력서.hwpx"))
    build_intro(os.path.join(ROOT, "나_소개서.hwpx"))
