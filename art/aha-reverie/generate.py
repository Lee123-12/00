#!/usr/bin/env python3
"""
"Reverie" - a soft, pretty reinterpretation of Aha (Honkai: Star Rail).

A silver-haired girl reads by warm window light in a quiet library. She holds
her book up and glances over it at the viewer with one ruby eye. Roses, pearls
and a small masquerade-mask hairpin replace the loud jester motifs.

Everything is drawn from code; no game assets are used.

    python3 generate.py      # writes reverie.svg next to this file
    node render.js           # renders reverie.png (2400x3000)
"""
import math
import os
import random

random.seed(77)
W, H = 1200, 1500
HERE = os.path.dirname(os.path.abspath(__file__))

defs, out = [], []
add = out.append
adef = defs.append

GOLD, GOLD_D, GOLD_L = "#e9c27a", "#a8762e", "#fff2cc"


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def n(v):
    return f"{v:.1f}"


def norm(x, y):
    l = math.hypot(x, y)
    return x / l, y / l


def poly(points, close=True):
    s = "M " + " L ".join(f"{n(x)} {n(y)}" for x, y in points)
    return s + (" Z" if close else "")


def stops(items):
    res = []
    for it in items:
        a = it[2] if len(it) > 2 else 1
        res.append(f'<stop offset="{it[0]}" stop-color="{it[1]}" stop-opacity="{a}"/>')
    return "".join(res)


def lin(gid, x1, y1, x2, y2, items, units="userSpaceOnUse", extra=""):
    adef(f'<linearGradient id="{gid}" gradientUnits="{units}" x1="{x1}" y1="{y1}" '
         f'x2="{x2}" y2="{y2}" {extra}>{stops(items)}</linearGradient>')


def rad(gid, cx, cy, r, items, units="userSpaceOnUse", fx=None, fy=None):
    fxy = f' fx="{fx}" fy="{fy}"' if fx is not None else ""
    adef(f'<radialGradient id="{gid}" gradientUnits="{units}" cx="{cx}" cy="{cy}" '
         f'r="{r}"{fxy}>{stops(items)}</radialGradient>')


_blurs = set()


def blur(s):
    """Filter attribute for a Gaussian blur, defining the filter on first use."""
    fid = "b" + str(s).replace(".", "_")
    if fid not in _blurs:
        _blurs.add(fid)
        adef(f'<filter id="{fid}" x="-150%" y="-150%" width="400%" height="400%">'
             f'<feGaussianBlur stdDeviation="{s}"/></filter>')
    return f'filter="url(#{fid})"'


def taper(p0, c, p1, w):
    """Thin lens-shaped strand from p0 to p1 bending through c."""
    nx, ny = norm(-(p1[1] - p0[1]), p1[0] - p0[0])
    return (f"M {n(p0[0])} {n(p0[1])} Q {n(c[0] + nx * w)} {n(c[1] + ny * w)} {n(p1[0])} {n(p1[1])} "
            f"Q {n(c[0] - nx * w)} {n(c[1] - ny * w)} {n(p0[0])} {n(p0[1])} Z")


_rim = [0]


def rim(d, dx, dy, color, s=3, op=0.85):
    """Light catching the edge of a shape: the shape minus a blurred, shifted copy."""
    _rim[0] += 1
    mid = f"rim{_rim[0]}"
    adef(f'<mask id="{mid}" maskUnits="userSpaceOnUse" x="-400" y="-400" '
         f'width="{W + 800}" height="{H + 800}">'
         f'<path d="{d}" fill="#fff"/>'
         f'<path d="{d}" fill="#000" transform="translate({dx} {dy})" {blur(s)}/></mask>')
    return f'<path d="{d}" fill="{color}" opacity="{op}" mask="url(#{mid})"/>'


def star4(cx, cy, r, fill="#fff", op=1.0, extra="", k=0.16):
    q = r * k
    d = (f"M {n(cx)} {n(cy - r)} Q {n(cx + q)} {n(cy - q)} {n(cx + r)} {n(cy)} "
         f"Q {n(cx + q)} {n(cy + q)} {n(cx)} {n(cy + r)} "
         f"Q {n(cx - q)} {n(cy + q)} {n(cx - r)} {n(cy)} "
         f"Q {n(cx - q)} {n(cy - q)} {n(cx)} {n(cy - r)} Z")
    return f'<path d="{d}" fill="{fill}" opacity="{op:.2f}" {extra}/>'


def diamond(cx, cy, w, h):
    return poly([(cx, cy - h), (cx + w, cy), (cx, cy + h), (cx - w, cy)])


def qm(q, u, v):
    """Bilinear map of (u, v) in [0,1]^2 onto quad [TL, TR, BR, BL]."""
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = q
    tx, ty = x0 + (x1 - x0) * u, y0 + (y1 - y0) * u
    bx, by = x3 + (x2 - x3) * u, y3 + (y2 - y3) * u
    return tx + (bx - tx) * v, ty + (by - ty) * v


def qpoly(q, uv, close=True):
    return poly([qm(q, u, v) for u, v in uv], close)


def qframe(q, u, v, cw=290.0, ch=435.0):
    """Affine frame at (u, v) of a book cover, in 'cover pixels' (cw x ch per cover)."""
    o = qm(q, u, v)
    eu, ev = qm(q, u + 0.05, v), qm(q, u, v + 0.05)
    a, b = (eu[0] - o[0]) / (0.05 * cw), (eu[1] - o[1]) / (0.05 * cw)
    c, d = (ev[0] - o[0]) / (0.05 * ch), (ev[1] - o[1]) / (0.05 * ch)
    return f"matrix({a:.4f} {b:.4f} {c:.4f} {d:.4f} {o[0]:.2f} {o[1]:.2f})"


def in_ellipse(x, y, cx, cy, rx, ry):
    return ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 < 1


# --------------------------------------------------------------------------
# gradients & filters
# --------------------------------------------------------------------------
lin("gSky", 0, 0, 0, H, [(0, "#1c1236"), (0.45, "#3d1c46"), (0.8, "#2a1027"), (1, "#15070f")])
rad("gWin", 190, 250, 820, [(0, "#fff3dc", 0.9), (0.22, "#ffd0a6", 0.5), (0.55, "#e9789c", 0.14),
                            (1, "#e9789c", 0)])
rad("gHalo", 650, 430, 420, [(0, "#ffe6cc", 0.42), (0.5, "#ffb6c6", 0.14), (1, "#ffb6c6", 0)])
lin("gPane", 0, 70, 0, 780, [(0, "#fffaf0"), (0.6, "#ffe2bf"), (1, "#ffc59a")])
lin("gBeam", 0, 0, 0, H, [(0, "#fff1dc", 1), (1, "#fff1dc", 0)])
lin("gShelfFade", 0, 0, 0, H, [(0, "#120818", 0.55), (0.5, "#120818", 0.25), (1, "#120818", 0.65)])
lin("gSheer", 0, 0, 120, 0, [(0, "#ffffff", 0.35), (1, "#ffffff", 0.0)])

lin("gHairF", 0, 314, 0, 890, [(0, "#fdfbff"), (0.36, "#efe9f7"), (0.5, "#ded3ee"),
                               (0.66, "#f4c7d9"), (1, "#e27ea3")])
lin("gHairB", 0, 300, 0, 1220, [(0, "#f2eef9"), (0.32, "#d5cae8"), (0.58, "#b7a2d2"),
                                (0.82, "#d792b2"), (1, "#b45a84")])
lin("gHairInner", 0, 640, 0, 1160, [(0, "#ffc2d3"), (0.5, "#e07a9f"), (1, "#8e2f5a")])
lin("gHairShade", 640, 0, 846, 0, [(0, "#7d6aa6", 0), (1, "#7562a0", 0.42)])
rad("gHairOcc", 650, 610, 340, [(0, "#3a2552", 0.5), (0.55, "#43295c", 0.25), (1, "#43295c", 0)])

lin("gSkin", 0, 440, 0, 780, [(0, "#fff3ee"), (1, "#f9ddd6")])
lin("gFaceShade", 600, 0, 792, 0, [(0, "#e39aa6", 0), (1, "#d98d9c", 0.32)])
lin("gUplight", 0, 715, 0, 585, [(0, "#ffcf8a", 0.55), (1, "#ffcf8a", 0)])
lin("gIris", 0, 584, 0, 642, [(0, "#2a0412"), (0.25, "#6a0c2a"), (0.52, "#c21f4a"),
                              (0.78, "#ff6b8b"), (1, "#ffd6a6")])
lin("gLid", 0, 586, 0, 612, [(0, "#4a1630", 0.65), (1, "#4a1630", 0)])
lin("gEyeWhite", 0, 584, 0, 640, [(0, "#efe3ee"), (1, "#ffffff")])
lin("gLash", 655, 0, 806, 0, [(0, "#2b1322"), (0.6, "#2b1322"), (1, "#7a2a44")])

lin("gJacket", 0, 850, 0, 1500, [(0, "#3d2749"), (0.45, "#1f1328"), (1, "#0f0913")])
lin("gJacketSheen", 300, 0, 1050, 0, [(0, "#ffd9c0", 0.1), (0.5, "#000", 0), (1, "#000", 0.25)])
lin("gBlouse", 0, 1040, 0, 1500, [(0, "#fffdff"), (1, "#d9cfe6")])
lin("gLace", 0, 0, 0, 1, [(0, "#ffffff"), (1, "#e4dbee")], units="objectBoundingBox")
lin("gSatin", 0, 0, 1, 1, [(0, "#ff6b8a"), (0.4, "#d4234d"), (1, "#7d0b2a")], units="objectBoundingBox")
rad("gGem", 0.35, 0.3, 0.85, [(0, "#ffc2cf"), (0.4, "#e0193f"), (1, "#4d0414")], units="objectBoundingBox")
rad("gPearl", 0.35, 0.3, 0.8, [(0, "#ffffff"), (0.55, "#f3ecf5"), (1, "#b9a9c4")], units="objectBoundingBox")
lin("gGoldF", 0, 0, 1, 1, [(0, GOLD_L), (0.35, "#f0c97a"), (0.7, GOLD_D), (1, "#f7dc9a")],
    units="objectBoundingBox")
lin("gLeaf", 0, 0, 1, 1, [(0, "#5f9a72"), (1, "#1f3f2e")], units="objectBoundingBox")

lin("gBookL", 308, 622, 562, 1072, [(0, "#a8254a"), (0.45, "#7c1434"), (1, "#45081c")])
lin("gBookR", 584, 648, 800, 1092, [(0, "#6e1230"), (0.55, "#470a20"), (1, "#28040f")])
lin("gSpine", 548, 0, 598, 0, [(0, "#3e0616"), (0.35, "#8a1b3c"), (0.5, "#d75179"),
                               (0.62, "#8a1b3c"), (1, "#320512")])
lin("gPages", 0, 0, 1, 0, [(0, "#fff3d6"), (0.5, "#ffe8b0"), (1, "#e8bd72")], units="objectBoundingBox")
lin("gBookSheen", 308, 622, 450, 900, [(0, "#ffe0d4", 0.34), (1, "#ffe0d4", 0)])

lin("gSkinN", 740, 820, 880, 990, [(0, "#fff2ec"), (0.55, "#f8dbd3"), (1, "#e5b2ac")])
lin("gSkinF", 250, 850, 380, 990, [(0, "#fff6f2"), (0.7, "#fae2db"), (1, "#eec4bd")])
lin("gSleeveN", 820, 960, 1080, 1500, [(0, "#3a2646"), (1, "#0e0911")])
lin("gSleeveF", 230, 980, 330, 1500, [(0, "#4a3357"), (1, "#110a14")])

rad("gPetalR", 0.5, 0.25, 0.9, [(0, "#ffb3c4"), (0.6, "#e8406a"), (1, "#a8163f")], units="objectBoundingBox")
rad("gPetalP", 0.5, 0.25, 0.9, [(0, "#fff0f4"), (0.6, "#ffb8cb"), (1, "#f0849f")], units="objectBoundingBox")
rad("gPetalW", 0.5, 0.25, 0.9, [(0, "#ffffff"), (0.7, "#fbe6ee"), (1, "#e9c2d2")], units="objectBoundingBox")

rad("gKey", 160, 160, 1250, [(0, "#ffe2c0", 0.3), (0.45, "#ffc2a0", 0.08), (1, "#ffc2a0", 0)])
rad("gHaze", 1100, 1350, 700, [(0, "#ff7aa5", 0.16), (1, "#ff7aa5", 0)])
rad("gVig", 640, 660, 1000, [(0, "#000", 0), (0.6, "#000", 0), (0.88, "#0a0210", 0.35),
                             (1, "#0a0210", 0.65)])

adef('<filter id="glow" x="-150%" y="-150%" width="400%" height="400%">'
     '<feGaussianBlur stdDeviation="2.5" result="b"/>'
     '<feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/>'
     '</feMerge></filter>')
adef('<filter id="glowBig" x="-200%" y="-200%" width="500%" height="500%">'
     '<feGaussianBlur stdDeviation="6" result="b"/>'
     '<feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/>'
     '</feMerge></filter>')
adef('<filter id="fLeather" x="0" y="0" width="100%" height="100%">'
     '<feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="3" seed="8"/>'
     '<feColorMatrix type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -1.6 1.05"/>'
     '</filter>')
adef(f'<filter id="fGrain" filterUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}">'
     '<feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="21" '
     'stitchTiles="stitch"/><feColorMatrix type="saturate" values="0"/></filter>')


# --------------------------------------------------------------------------
# props
# --------------------------------------------------------------------------
_rc = [0]


def rose(cx, cy, r, rot=0, pal=("#4e0414", "#b3123a", "#ff5a7e", "#ffc1cf")):
    _rc[0] += 1
    gid = f"gRose{_rc[0]}"
    dark, mid, light, edge = pal
    rad(gid, 0, 0, r * 1.05, [(0, dark), (0.45, mid), (0.82, light), (1, edge)])
    s = [f'<g transform="translate({n(cx)} {n(cy)}) rotate({rot:.0f})">']
    s.append(f'<circle r="{n(r)}" fill="#2a0010" opacity="0.45" transform="translate({n(r * .1)} {n(r * .14)})" '
             f'{blur(round(max(1.0, r * 0.1), 1))}/>')
    for i in range(6):
        s.append(f'<ellipse cx="0" cy="{n(-r * .45)}" rx="{n(r * .56)}" ry="{n(r * .5)}" '
                 f'transform="rotate({i * 60 + 15})" fill="url(#{gid})" stroke="{dark}" '
                 f'stroke-width="{n(r * .025)}" stroke-opacity="0.6"/>')
    for i in range(5):
        s.append(f'<ellipse cx="0" cy="{n(-r * .28)}" rx="{n(r * .4)}" ry="{n(r * .34)}" '
                 f'transform="rotate({i * 72 + 45})" fill="url(#{gid})" stroke="{dark}" '
                 f'stroke-width="{n(r * .025)}" stroke-opacity="0.5"/>')
    s.append(f'<circle r="{n(r * .42)}" fill="{mid}"/>')
    for rr, a0, sw in [(0.36, 200, 230), (0.27, 30, 220), (0.19, 220, 210), (0.11, 70, 200)]:
        for dr, col, wd, op in [(0, dark, 0.07, 0.75), (0.035, edge, 0.035, 0.9)]:
            R = r * (rr + dr)
            a1, a2 = math.radians(a0), math.radians(a0 + sw)
            s.append(f'<path d="M {n(R * math.cos(a1))} {n(R * math.sin(a1))} A {n(R)} {n(R)} 0 1 1 '
                     f'{n(R * math.cos(a2))} {n(R * math.sin(a2))}" fill="none" stroke="{col}" '
                     f'stroke-width="{n(r * wd)}" stroke-linecap="round" opacity="{op}"/>')
    s.append(f'<circle r="{n(r * .06)}" fill="{dark}"/>')
    s.append(f'<ellipse cx="{n(-r * .4)}" cy="{n(-r * .5)}" rx="{n(r * .22)}" ry="{n(r * .1)}" fill="#fff" '
             f'opacity="0.4" transform="rotate(-35 {n(-r * .4)} {n(-r * .5)})" {blur(round(max(0.6, r * .04), 1))}/>')
    s.append('</g>')
    return "".join(s)


def leaf(x, y, L, w, rot):
    d = f"M 0 0 Q {n(L * .5)} {n(-w)} {n(L)} 0 Q {n(L * .5)} {n(w)} 0 0 Z"
    return (f'<g transform="translate({n(x)} {n(y)}) rotate({rot:.0f})"><path d="{d}" fill="url(#gLeaf)" '
            f'stroke="#1b3527" stroke-width="0.8"/><path d="M 0 0 Q {n(L * .5)} {n(-w * .15)} {n(L * .9)} 0" '
            f'fill="none" stroke="{GOLD}" stroke-width="0.9" opacity="0.85"/></g>')


def blossom(x, y, r, col="#ffffff"):
    p = "".join(f'<circle cx="{n(x + r * .85 * math.cos(math.radians(a)))}" '
                f'cy="{n(y + r * .85 * math.sin(math.radians(a)))}" r="{n(r * .6)}" fill="{col}"/>'
                for a in range(-90, 270, 72))
    return f'<g opacity="0.95">{p}<circle cx="{n(x)}" cy="{n(y)}" r="{n(r * .38)}" fill="#ffd98a"/></g>'


def pearl(x, y, r):
    return (f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r)}" fill="url(#gPearl)" stroke="#a796b3" '
            f'stroke-width="0.5"/><circle cx="{n(x - r * .35)}" cy="{n(y - r * .35)}" r="{n(r * .25)}" '
            f'fill="#fff"/>')


PETAL = ("M 0 -11 C 3 -13 10 -12 10.5 -3 C 10.5 5 4 11 0 13 C -4 11 -10.5 5 -10.5 -3 "
         "C -10 -12 -3 -13 0 -11 Z")


def petal(x, y, s, rot, squash, grad, op=1.0, b=0):
    ba = f'<g {blur(b)}>' if b else "<g>"
    return (f'<g transform="translate({n(x)} {n(y)}) rotate({rot:.0f}) scale({s:.2f} {s * squash:.2f})" '
            f'opacity="{op:.2f}">{ba}<path d="{PETAL}" fill="url(#{grad})"/>'
            f'<path d="M 0 -6 Q 1 2 0 10" stroke="#fff" stroke-width="0.8" opacity="0.5" fill="none"/></g></g>')


MASQ = ("M -45 -5 C -40 -27 -14 -24 0 -11 C 14 -24 40 -27 45 -5 C 49 9 38 23 20 21 "
        "C 10 20 4 13 0 8 C -4 13 -10 20 -20 21 C -38 23 -49 9 -45 -5 Z")


def masquerade(x, y, s, rot):
    return (f'<g transform="translate({n(x)} {n(y)}) rotate({rot}) scale({s})">'
            f'<path d="{MASQ}" transform="translate(4 6)" fill="#2a1030" opacity="0.4" {blur(4)}/>'
            f'<path d="{MASQ}" fill="url(#gPearl)" stroke="{GOLD}" stroke-width="2.6"/>'
            f'<path d="M -42 -6 C -36 -20 -16 -20 -4 -10 M 42 -6 C 36 -20 16 -20 4 -10" fill="none" '
            f'stroke="{GOLD}" stroke-width="1.4" opacity="0.9"/>'
            f'<path d="M -32 2 Q -20 -9 -8 2 Q -20 8 -32 2 Z M 32 2 Q 20 -9 8 2 Q 20 8 32 2 Z" fill="#cfc3e3" '
            f'stroke="{GOLD_D}" stroke-width="1"/>'
            f'<path d="M -45 -5 C -56 -14 -62 -26 -58 -36 M 45 -5 C 56 -14 62 -26 58 -36" fill="none" '
            f'stroke="{GOLD}" stroke-width="1.4"/>' + pearl(-58, -38, 3) + pearl(58, -38, 3) +
            f'<path d="M -40 10 C -36 22 -26 26 -20 22 M 40 10 C 36 22 26 26 20 22" fill="none" stroke="#fff" '
            f'stroke-width="1" opacity="0.7"/>'
            f'<path d="M -30 12 C -24 16 -14 16 -10 12 M 30 12 C 24 16 14 16 10 12" fill="none" '
            f'stroke="{GOLD}" stroke-width="1.2"/>'
            f'<path d="{diamond(0, -12, 4.5, 6.5)}" fill="url(#gGem)" stroke="{GOLD}" stroke-width="1"/>'
            f'</g>')


def frill(a, b, count, depth, thick):
    """Lace frill along a-b; scallops bulge toward the hand (upward)."""
    ax, ay = a
    bx, by = b
    ux, uy = norm(bx - ax, by - ay)
    nx, ny = uy, -ux
    if ny > 0:
        nx, ny = -nx, -ny
    d = [f"M {n(ax)} {n(ay)}"]
    picots = []
    for i in range(count):
        t0, t1 = i / count, (i + 1) / count
        x1, y1 = ax + (bx - ax) * t1, ay + (by - ay) * t1
        mx, my = ax + (bx - ax) * (t0 + t1) / 2, ay + (by - ay) * (t0 + t1) / 2
        d.append(f"Q {n(mx + nx * depth * 2)} {n(my + ny * depth * 2)} {n(x1)} {n(y1)}")
        picots.append((mx + nx * depth * 1.05, my + ny * depth * 1.05))
        picots.append((mx + nx * depth * 0.45 - ux * 6, my + ny * depth * 0.45 - uy * 6))
    d.append(f"L {n(bx - nx * thick)} {n(by - ny * thick)} L {n(ax - nx * thick)} {n(ay - ny * thick)} Z")
    holes = "".join(f'<circle cx="{n(px - nx * thick * .3)}" cy="{n(py - ny * thick * .3)}" r="1.7" '
                    f'fill="none" stroke="#b9acc9" stroke-width="0.8"/>' for px, py in picots)
    return (f'<path d="{" ".join(d)}" fill="url(#gLace)" stroke="#b3a5c4" stroke-width="1"/>' + holes)


# ==========================================================================
# 1. BACKGROUND (canvas coordinates)
# ==========================================================================
add(f'<rect width="{W}" height="{H}" fill="url(#gSky)"/>')

# out-of-focus bookshelves on the right and lower left
shelf = []
SPINE_COLS = ["#5b1a2e", "#2d2a4a", "#3e2a1e", "#6b4a2a", "#4a1f3d", "#22324a", "#7a2a3a", "#584066"]
for x0, x1, rows in [(880, 1210, range(8)), (-10, 250, range(4, 8))]:
    for k in rows:
        base = 40 + k * 190
        x = x0
        while x < x1:
            w = random.uniform(13, 30)
            hgt = random.uniform(105, 150)
            col = random.choice(SPINE_COLS)
            shelf.append(f'<rect x="{n(x)}" y="{n(base - hgt)}" width="{n(w - 2)}" height="{n(hgt)}" '
                         f'fill="{col}"/>')
            if random.random() < 0.6:
                shelf.append(f'<rect x="{n(x + 2)}" y="{n(base - hgt + 14)}" width="{n(w - 6)}" height="3" '
                             f'fill="{GOLD}" opacity="0.7"/>')
            x += w + random.uniform(0, 3)
        shelf.append(f'<rect x="{x0}" y="{base}" width="{x1 - x0}" height="16" fill="#2a1420"/>')
add(f'<g opacity="0.6" {blur(5)}>{"".join(shelf)}</g>')
add(f'<rect x="860" width="340" height="{H}" fill="url(#gShelfFade)"/>')
add(f'<rect x="0" y="780" width="260" height="{H - 780}" fill="url(#gShelfFade)"/>')

# arched window with warm light (out of focus)
WIN = "M 50 780 L 50 220 A 140 140 0 0 1 330 220 L 330 780 Z"
add(f'<g {blur(7)}><path d="{WIN}" fill="url(#gPane)"/>'
    f'<path d="M 190 80 L 190 780 M 50 360 L 330 360 M 50 560 L 330 560 M 190 220 L 80 130 M 190 220 L 300 130" '
    f'stroke="#3a1e36" stroke-width="12" fill="none"/>'
    f'<path d="{WIN}" fill="none" stroke="#2a1426" stroke-width="22"/></g>')
add(f'<rect width="{W}" height="{H}" fill="url(#gWin)" style="mix-blend-mode:screen"/>')
# sheer curtain on the window edge
add(f'<path d="M 0 0 L 120 0 C 100 300 130 600 96 900 C 80 1100 110 1300 90 1500 L 0 1500 Z" '
    f'fill="url(#gSheer)" {blur(3)}/>')
for xx in (22, 48, 74):
    add(f'<path d="M {xx} 0 C {xx - 10} 400 {xx + 12} 800 {xx - 4} 1500" stroke="#fff" stroke-width="5" '
        f'opacity="0.12" fill="none" {blur(3)}/>')

# halo glow behind the head
add(f'<circle cx="650" cy="430" r="420" fill="url(#gHalo)" style="mix-blend-mode:screen"/>')

# light beams from the window
for pts_, op in [([(120, 120), (300, 60), (1100, 1500), (720, 1500)], 0.12),
                 ([(260, 200), (330, 160), (1200, 1150), (1200, 1350)], 0.08),
                 ([(60, 300), (150, 260), (560, 1500), (360, 1500)], 0.07)]:
    add(f'<path d="{poly(pts_)}" fill="url(#gBeam)" opacity="{op}" {blur(20)} style="mix-blend-mode:screen"/>')

# bokeh
for _ in range(46):
    x, y = random.uniform(0, W), random.uniform(0, H - 150)
    warm = x < 520 and y < 900
    col = random.choice(["#ffe1b0", "#ffd0a0", "#fff2d8"] if warm else ["#ffb6cf", "#d7b4ff", "#ffd6e2", "#ffe1b0"])
    r = random.uniform(10, 48)
    add(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r)}" fill="{col}" opacity="{random.uniform(0.07, 0.2):.2f}" '
        f'{blur(random.choice([2, 3, 5]))}/>')
    if random.random() < 0.35:
        add(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r)}" fill="none" stroke="{col}" stroke-width="1.5" '
            f'opacity="0.18" {blur(1)}/>')
# dust motes in the light
for _ in range(90):
    t = random.random()
    x = 120 + t * 900 + random.uniform(-160, 160)
    y = 100 + t * 1300 + random.uniform(-120, 120)
    add(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(random.uniform(0.6, 1.8))}" fill="#fff6e0" '
        f'opacity="{random.uniform(0.2, 0.8):.2f}"/>')
# distant petals
for _ in range(26):
    x, y = random.uniform(0, W), random.uniform(0, H)
    add(petal(x, y, random.uniform(0.5, 0.9), random.uniform(0, 360), random.uniform(0.45, 0.9),
              random.choice(["gPetalP", "gPetalW", "gPetalR"]), random.uniform(0.35, 0.6), b=1.5))


# ==========================================================================
# 2. CHARACTER (drawn in the original 1200x1500 layout, then scaled up)
# ==========================================================================
HEAD = "rotate(-7 660 620)"
add('<g transform="translate(650 620) scale(1.28) translate(-650 -650)">')

# ---- back hair ----------------------------------------------------------
BACK = ("M 650 300 C 772 296 862 372 878 486 C 892 590 880 700 902 820 "
        "C 922 930 968 1020 1022 1108 L 968 1094 L 990 1186 L 930 1120 L 912 1200 "
        "L 868 1112 C 840 1060 800 1000 760 980 L 520 980 C 470 1010 440 1060 420 1120 "
        "L 410 1060 L 360 1110 C 400 1010 430 900 432 800 C 434 680 418 570 446 466 "
        "C 476 360 556 304 650 300 Z")
INNER = ("M 788 640 C 826 760 848 880 896 985 C 926 1045 958 1085 990 1112 L 942 1098 "
         "L 952 1156 L 896 1104 L 874 1162 L 836 1084 C 806 990 784 830 760 700 Z")
bh = [f'<g transform="{HEAD}">', f'<path d="{BACK}" fill="url(#gHairB)"/>',
      f'<path d="{BACK}" fill="url(#gHairOcc)"/>', f'<path d="{INNER}" fill="url(#gHairInner)"/>']
for t in [((470, 450), (450, 620), (440, 800), 5), ((520, 420), (488, 560), (476, 700), 4),
          ((850, 440), (880, 640), (900, 860), 6), ((830, 520), (850, 760), (900, 980), 5),
          ((870, 600), (900, 820), (960, 1060), 4)]:
    bh.append(f'<path d="{taper(*t)}" fill="#7d68a0" opacity="0.4"/>')
for t in [((860, 480), (884, 640), (912, 820), 3), ((456, 520), (444, 640), (446, 760), 2.5)]:
    bh.append(f'<path d="{taper(*t)}" fill="#fff" opacity="0.5"/>')
bh.append(f'<path d="{BACK}" fill="none" stroke="#8a74a8" stroke-width="1.4" opacity="0.45"/>')
bh.append(rim(BACK, -12, 0, "#ffa8c4", 4, 0.7))
bh.append(rim(BACK, 10, 8, "#fff3e2", 4, 0.55))
bh.append('</g>')
add("".join(bh))

# ---- neck & body --------------------------------------------------------
add('<path d="M 612 735 C 616 790 608 845 596 892 L 724 892 C 712 840 706 790 708 728 Z" fill="#f0cdc5"/>')
JACKET = ("M 640 858 C 720 864 830 885 905 922 C 965 952 995 1010 1010 1100 "
          "C 1022 1200 1036 1350 1046 1500 L 250 1500 C 262 1350 285 1180 305 1090 "
          "C 322 1010 372 958 445 928 C 515 900 585 862 640 858 Z")
adef(f'<clipPath id="cJacket"><path d="{JACKET}"/></clipPath>')
add(f'<path d="{JACKET}" fill="url(#gJacket)"/><path d="{JACKET}" fill="url(#gJacketSheen)"/>')
for d_ in ["M 860 1000 C 880 1150 900 1300 920 1500", "M 420 1080 C 410 1200 400 1350 395 1500",
           "M 780 1120 C 790 1250 800 1380 810 1500"]:
    add(f'<path d="{d_}" fill="none" stroke="#000" stroke-width="7" opacity="0.3" {blur(3)}/>')
BLOUSE = "M 528 1040 L 732 1040 C 708 1200 686 1350 670 1500 L 570 1500 C 562 1350 550 1200 528 1040 Z"
add(f'<path d="{BLOUSE}" fill="url(#gBlouse)"/>')
# beaded gold trim + embroidery curls along the jacket opening
for d_ in ["M 528 1040 C 550 1200 562 1350 570 1500", "M 732 1040 C 708 1200 686 1350 670 1500"]:
    add(f'<path d="{d_}" fill="none" stroke="{GOLD}" stroke-width="2.4"/>'
        f'<path d="{d_}" fill="none" stroke="{GOLD_L}" stroke-width="4.5" stroke-dasharray="0.1 10" '
        f'stroke-linecap="round" transform="translate(0 0)"/>')
for y in range(1150, 1500, 46):
    t = (y - 1040) / 460
    xl = 528 + 42 * t - 26
    xr = 732 - 62 * t + 26
    add(f'<path d="M {n(xl)} {y} c -10 -4 -14 -16 -4 -20 c 6 -2 9 4 5 7" fill="none" stroke="{GOLD}" '
        f'stroke-width="1.3" opacity="0.75"/>'
        f'<path d="M {n(xr)} {y} c 10 -4 14 -16 4 -20 c -6 -2 -9 4 -5 7" fill="none" stroke="{GOLD}" '
        f'stroke-width="1.3" opacity="0.75"/>')
# lace jabot tiers (bottom tier first)
for top, bot, half in [(1286, 1346, 40), (1244, 1304, 45), (1202, 1262, 48), (1160, 1220, 50)]:
    xs = [630 - half + i * (2 * half) / 7 for i in range(8)]
    rev = " ".join(f"Q {n((xs[i] + xs[i - 1]) / 2)} {bot + 13} {n(xs[i - 1])} {bot}" for i in range(7, 0, -1))
    add(f'<path d="M {n(xs[0] + 10)} {top} L {n(xs[-1] - 10)} {top} L {n(xs[-1])} {bot} {rev} Z" '
        f'fill="url(#gLace)" stroke="#b6a8c7" stroke-width="1.1"/>')
    add("".join(f'<circle cx="{n((xs[i] + xs[i + 1]) / 2)}" cy="{bot + 4}" r="2" fill="none" '
                f'stroke="#bcb0cc" stroke-width="0.8"/>' for i in range(7)))
    add(f'<path d="M {n(630 - half * .5)} {top + 6} Q {n(630 - half * .56)} {(top + bot) / 2} {n(630 - half * .62)} {bot + 6} '
        f'M 630 {top + 6} L 630 {bot + 10} M {n(630 + half * .5)} {top + 6} Q {n(630 + half * .56)} {(top + bot) / 2} '
        f'{n(630 + half * .62)} {bot + 6}" fill="none" stroke="#cbc0d8" stroke-width="1.1"/>')
# satin ribbon bow with a ruby brooch
add('<path d="M 622 1168 L 596 1262 L 609 1256 L 616 1268 L 634 1170 Z" fill="url(#gSatin)"/>'
    '<path d="M 638 1168 L 666 1258 L 652 1253 L 645 1266 L 626 1170 Z" fill="url(#gSatin)"/>'
    '<path d="M 630 1160 C 600 1126 566 1136 572 1164 C 577 1190 612 1186 630 1160 Z" fill="url(#gSatin)" '
    'stroke="#7d0b2a" stroke-width="1"/>'
    '<path d="M 630 1160 C 660 1126 694 1136 688 1164 C 683 1190 648 1186 630 1160 Z" fill="url(#gSatin)" '
    'stroke="#7d0b2a" stroke-width="1"/>'
    '<path d="M 584 1150 C 596 1142 612 1148 622 1158 M 676 1150 C 664 1142 648 1148 638 1158" fill="none" '
    'stroke="#ffb0c2" stroke-width="2" opacity="0.8"/>')
add(f'<ellipse cx="630" cy="1162" rx="12" ry="14" fill="url(#gGoldF)" stroke="{GOLD_D}" stroke-width="1"/>'
    f'<ellipse cx="630" cy="1162" rx="8" ry="10" fill="url(#gGem)"/>'
    f'<circle cx="627" cy="1157" r="2.2" fill="#fff" opacity="0.9"/>'
    + "".join(pearl(630 + 15 * math.cos(math.radians(a)), 1162 + 17 * math.sin(math.radians(a)), 2.6)
              for a in range(0, 360, 45)))
# puffed shoulder on the near side
PUFF = "M 846 900 C 880 868 952 878 992 930 C 1012 960 1014 1000 1002 1032 C 970 1002 930 986 880 976 C 860 960 848 930 846 900 Z"
add(f'<path d="{PUFF}" fill="url(#gJacket)" stroke="#120a16" stroke-width="1"/>')
add("".join(f'<path d="M {n(870 + i * 22)} {n(905 + i * 4)} Q {n(890 + i * 22)} {n(945 + i * 6)} '
            f'{n(884 + i * 24)} {n(982 + i * 8)}" stroke="#5c4470" stroke-width="2" fill="none" opacity="0.6"/>'
            for i in range(5)))
add(f'<path d="M 880 976 C 930 986 970 1002 1002 1032" fill="none" stroke="{GOLD}" stroke-width="3"/>'
    + "".join(pearl(884 + i * 15, 977 + i * 4.2 + (i * i) * 0.25, 2.8) for i in range(8)))
add(rim(JACKET, -12, 0, "#ff86ab", 4, 0.6))
add(rim(PUFF, -8, 0, "#ff9cbc", 3, 0.6))

# ---- head ---------------------------------------------------------------
FACE = ("M 560 440 C 552 510 544 570 550 622 C 554 664 566 702 590 736 C 604 756 618 772 632 777 "
        "C 668 772 716 742 750 702 C 774 672 788 622 788 570 C 788 520 782 476 772 440 Z")
BANGS = ("M 492 500 C 488 400 560 318 655 314 C 752 312 826 380 826 482 "
         "C 826 540 820 600 818 660 C 816 720 830 800 846 884 "
         "C 822 850 800 820 794 790 C 786 740 782 690 784 630 C 786 580 784 548 780 520 "
         "Q 780 552 770 574 Q 758 545 750 522 "
         "Q 738 548 712 566 Q 706 532 700 510 "
         "Q 690 560 664 592 Q 656 550 652 512 "
         "C 640 580 606 640 560 690 C 548 640 540 590 532 540 "
         "C 522 520 505 508 492 500 Z")
EYE = ("M 660 618 C 674 596 702 584 732 584 C 754 584 769 592 778 606 "
       "C 772 620 762 630 748 635 C 726 642 694 638 660 618 Z")
adef(f'<clipPath id="cFace"><path d="{FACE}"/></clipPath>')
adef(f'<clipPath id="cEye"><path d="{EYE}"/></clipPath>')
adef(f'<clipPath id="cBangs"><path d="{BANGS}"/></clipPath>')
adef('<clipPath id="cRimR"><rect x="772" y="250" width="200" height="700"/></clipPath>')

h = [f'<g transform="{HEAD}">']
h.append(f'<path d="{FACE}" fill="url(#gSkin)" stroke="#d99aa0" stroke-width="1.3" stroke-opacity="0.55"/>')
h.append(f'<g clip-path="url(#cFace)">'
         f'<rect x="540" y="430" width="260" height="360" fill="url(#gFaceShade)"/>'
         f'<path d="{BANGS}" transform="translate(4 14)" fill="#e6a9b2" opacity="0.5" {blur(5)}/>'
         f'<ellipse cx="740" cy="664" rx="40" ry="16" fill="#ff8fa8" opacity="0.5" {blur(7)}/>'
         f'<ellipse cx="616" cy="672" rx="22" ry="10" fill="#ff8fa8" opacity="0.35" {blur(6)}/>'
         f'<path d="M 726 660 L 732 650 M 738 662 L 744 652 M 750 663 L 755 654" stroke="#ff9fb3" '
         f'stroke-width="1.4" stroke-linecap="round" opacity="0.6"/>'
         f'<ellipse cx="760" cy="648" rx="6" ry="3" fill="#fff" opacity="0.6" {blur(1)}/>'
         f'<ellipse cx="722" cy="652" rx="40" ry="9" fill="#ffadc0" opacity="0.3" {blur(5)}/>'
         f'<path d="M 636 612 Q 628 640 614 658" fill="none" stroke="#e3a5ad" stroke-width="4" '
         f'opacity="0.4" {blur(2)}/>'
         f'<rect x="540" y="560" width="260" height="230" fill="url(#gUplight)" '
         f'style="mix-blend-mode:screen"/></g>')
# nose
h.append(f'<path d="M 604 668 L 612 662" fill="none" stroke="#d99aa2" stroke-width="1.5" '
         f'stroke-linecap="round" opacity="0.85"/><ellipse cx="612" cy="671" rx="7" ry="3" fill="#e7a9b0" '
         f'opacity="0.45" {blur(1.5)}/><ellipse cx="609" cy="653" rx="2.4" ry="1.5" fill="#fff" opacity="0.7"/>')
# eye
h.append(f'<path d="{EYE}" fill="url(#gEyeWhite)"/>')
e = ['<g clip-path="url(#cEye)">', '<ellipse cx="737" cy="613" rx="23" ry="29" fill="url(#gIris)"/>']
for i in range(18):
    a = 2 * math.pi * i / 18
    e.append(f'<path d="M {n(737 + 9 * math.cos(a))} {n(613 + 12 * math.sin(a))} '
             f'L {n(737 + 21 * math.cos(a))} {n(613 + 27 * math.sin(a))}" stroke="#ffa3b6" '
             f'stroke-width="0.9" opacity="0.32"/>')
e.append('<ellipse cx="737" cy="616" rx="15" ry="19" fill="none" stroke="#ff9fb4" stroke-width="1" opacity="0.4"/>')
e.append(f'<ellipse cx="737" cy="631" rx="15" ry="8" fill="#ffb5a0" opacity="0.6" {blur(2)}/>')
e.append('<ellipse cx="737" cy="613" rx="23" ry="29" fill="none" stroke="#3a0718" stroke-width="2"/>')
e.append('<ellipse cx="738" cy="610" rx="7.5" ry="12" fill="#1e0310" opacity="0.92"/>')
e.append('<rect x="650" y="582" width="140" height="32" fill="url(#gLid)"/>')
e.append('<ellipse cx="727" cy="601" rx="7.5" ry="6" fill="#fff" transform="rotate(-20 727 601)"/>')
e.append('<circle cx="748" cy="626" r="3" fill="#fff" opacity="0.95"/>')
e.append('<circle cx="733" cy="629" r="1.6" fill="#fff" opacity="0.85"/>')
e.append(star4(751, 600, 5.5, "#fff", 0.95))
e.append('<path d="M 722 634 Q 737 641 752 633" fill="none" stroke="#fff" stroke-width="1.2" opacity="0.55"/>')
e.append('</g>')
h.extend(e)
h.append(f'<circle cx="737" cy="615" r="28" fill="#ff6d8f" opacity="0.13" {blur(8)} style="mix-blend-mode:screen"/>')
h.append('<path d="M 670 584 C 696 566 734 564 766 574" fill="none" stroke="#d4a3ad" stroke-width="1.5" opacity="0.8"/>')
h.append('<path d="M 655 620 C 668 593 700 574 732 574 C 754 574 772 582 786 594 L 800 585 '
         'C 798 598 791 607 782 613 C 772 598 755 586 732 586 C 704 586 678 600 661 622 Z" fill="url(#gLash)"/>')
for t in [((776, 600), (791, 598), (807, 597), 2.2), ((772, 593), (784, 583), (795, 572), 2),
          ((781, 607), (793, 611), (804, 616), 1.8), ((664, 616), (657, 620), (650, 628), 1.3),
          ((690, 590), (686, 584), (684, 577), 1.2)]:
    h.append(f'<path d="{taper(*t)}" fill="#2b1322"/>')
h.append('<path d="M 678 629 C 700 640 732 642 752 633" fill="none" stroke="#b0646f" stroke-width="1.8" '
         'stroke-linecap="round"/>')
for t in [((744, 637), (747, 642), (749, 647), 1), ((753, 633), (758, 635), (763, 638), 1)]:
    h.append(f'<path d="{taper(*t)}" fill="#8a4a58"/>')
h.append('<path d="M 668 556 C 692 541 730 536 764 546 C 730 543 694 549 670 561 Z" fill="#b8a7c9"/>')
# bangs
h.append(f'<path d="{BANGS}" fill="url(#gHairF)"/>')
h.append(f'<g clip-path="url(#cBangs)"><rect x="620" y="300" width="240" height="600" fill="url(#gHairShade)"/>'
         + "".join(f'<path d="{taper(*t)}" fill="#a594c6" opacity="0.5"/>' for t in [
             ((700, 330), (735, 430), (750, 522), 6), ((672, 330), (690, 430), (700, 508), 6),
             ((650, 330), (652, 430), (652, 510), 5), ((632, 340), (614, 500), (580, 650), 8),
             ((610, 340), (575, 450), (548, 560), 6), ((760, 360), (800, 450), (792, 560), 5),
             ((802, 470), (812, 640), (836, 860), 6), ((585, 360), (535, 420), (512, 492), 5)])
         + "".join(f'<path d="{taper(*t)}" fill="#ffffff" opacity="0.6"/>' for t in [
             ((690, 345), (712, 430), (722, 520), 3), ((640, 350), (626, 470), (600, 590), 4),
             ((782, 420), (798, 560), (808, 700), 3), ((560, 380), (534, 440), (520, 500), 2.5)])
         + '</g>')
h.append(f'<path d="{BANGS}" fill="none" stroke="#8070a3" stroke-width="1.4" opacity="0.5"/>')
h.append('<path d="M 660 318 C 668 280 700 258 728 268 C 706 272 686 288 672 318 Z" fill="url(#gHairF)"/>')
for d_ in ["M 846 470 C 874 510 880 560 868 610", "M 452 520 C 428 560 424 610 438 650",
           "M 880 600 C 906 660 900 720 912 780", "M 826 760 C 852 800 860 850 850 900"]:
    h.append(f'<path d="{d_}" fill="none" stroke="#f6f0fb" stroke-width="1.2" opacity="0.8"/>')
h.append(f'<path d="M 588 402 Q 660 360 760 405" fill="none" stroke="#fff" stroke-width="12" '
         f'opacity="0.22" {blur(4)}/>')
for i in range(10):
    a = math.radians(252 + i * 6.3)
    px, py = 655 + 215 * math.cos(a), 600 + 215 * math.sin(a)
    dx, dy = norm(px - 655, py - 314)
    L, w = random.uniform(18, 32), random.uniform(2, 3.4)
    h.append(f'<path d="{poly([(px - dx * L / 2, py - dy * L / 2), (px - dy * w, py + dx * w), (px + dx * L / 2, py + dy * L / 2), (px + dy * w, py - dx * w)])}" '
             f'fill="#fff" opacity="0.85"/>')
h.append(f'<g clip-path="url(#cRimR)">{rim(BANGS, -10, 2, "#ffb3c9", 3, 0.8)}</g>')
h.append(rim(BANGS, 8, 7, "#fff6ea", 4, 0.6))
# earring
h.append(f'<path d="M 790 688 L 791 708" stroke="{GOLD}" stroke-width="1.2"/>'
         f'<path d="{diamond(790, 686, 4, 5)}" fill="url(#gGem)" stroke="{GOLD}" stroke-width="0.8"/>'
         + pearl(791, 716, 6.5))
# hair ornament: masquerade pin, roses, leaves, blossoms, ribbon + pearls
h.append(masquerade(560, 392, 0.82, -38))
h.append('<path d="M 470 492 C 458 530 446 570 440 612 L 452 615 C 459 574 470 534 482 496 Z" fill="url(#gSatin)"/>')
h.append('<path d="M 480 496 C 478 536 474 576 472 620 L 485 621 C 489 578 492 538 494 500 Z" fill="url(#gSatin)" opacity="0.85"/>')
h.append(pearl(446, 620, 5) + pearl(478, 627, 4.5))
h.append('<path d="M 476 490 C 448 464 430 498 458 506 Z M 476 490 C 504 470 514 504 486 508 Z" '
         'fill="url(#gSatin)" stroke="#7d0b2a" stroke-width="1"/>')
for i in range(7):
    h.append(pearl(518 - i * 2.2, 470 + i * 11.5, 3.6 - i * 0.12))
h.append(f'<path d="M 503 550 L 503 556" stroke="{GOLD}" stroke-width="1"/>'
         f'<ellipse cx="503" cy="563" rx="5" ry="7" fill="url(#gPearl)" stroke="#a796b3" stroke-width="0.5"/>')
for (x, y, L, w, r_) in [(480, 440, 34, 9, 200), (540, 455, 30, 8, 20), (500, 395, 28, 7, -70),
                         (460, 470, 26, 7, 150), (548, 418, 26, 7, -20)]:
    h.append(leaf(x, y, L, w, r_))
h.append(rose(473, 470, 22, -30))
h.append(rose(512, 430, 33, 10))
h.append(rose(546, 456, 14, 40, ("#6e1a34", "#e0577d", "#ff9db6", "#ffe0e8")))
for (x, y, r_) in [(488, 404, 5), (538, 432, 4.5), (462, 446, 4.5), (500, 474, 4), (532, 400, 4),
                   (456, 494, 3.5), (556, 478, 3.5)]:
    h.append(blossom(x, y, r_))
h.append('</g>')
add("".join(h))

# ---- book (lowered 40px so the face reads better) -------------------------
LQ = [(308, 622), (548, 642), (562, 1072), (320, 1030)]
RQ = [(584, 648), (805, 690), (800, 1092), (598, 1078)]
SPINE = "M 548 642 Q 566 630 584 648 L 598 1078 Q 580 1090 562 1072 Z"
BOOK_ALL = poly([(308, 622), (548, 642), (566, 632), (584, 648), (805, 690), (800, 1092),
                 (598, 1078), (580, 1088), (562, 1072), (320, 1030)])
add(f'<g clip-path="url(#cJacket)"><path d="{BOOK_ALL}" transform="translate(22 70)" fill="#000" '
    f'opacity="0.55" {blur(14)}/></g>')
add('<g transform="translate(0 40)">')
add(f'<g style="mix-blend-mode:screen">'
    f'<ellipse cx="556" cy="652" rx="290" ry="46" fill="#ffcf85" opacity="0.6" '
    f'transform="rotate(8 556 652)" {blur(24)}/>'
    f'<ellipse cx="560" cy="650" rx="170" ry="18" fill="#fff3d0" opacity="0.75" '
    f'transform="rotate(8 560 650)" {blur(8)}/></g>')

SLEEVE_N = ("M 818 990 L 890 958 C 938 1046 1002 1196 1050 1336 C 1066 1390 1076 1450 1082 1500 "
            "L 932 1500 C 922 1420 898 1300 868 1200 C 848 1120 834 1050 818 990 Z")
SLEEVE_F = "M 236 984 L 308 1000 C 314 1100 322 1280 338 1500 L 186 1500 C 196 1360 214 1160 236 984 Z"
add(f'<path d="{SLEEVE_N}" fill="url(#gSleeveN)"/>' + rim(SLEEVE_N, -10, 0, "#ff86ab", 4, 0.6))
add(f'<path d="{SLEEVE_F}" fill="url(#gSleeveF)"/>' + rim(SLEEVE_F, 9, 4, "#ffe2cc", 4, 0.4))
for (a, b) in [((826, 1010), (902, 978)), ((232, 1004), (310, 1020))]:
    add(f'<path d="M {a[0]} {a[1]} L {b[0]} {b[1]}" stroke="{GOLD}" stroke-width="3"/>'
        + "".join(pearl(a[0] + (b[0] - a[0]) * (i + .5) / 7, a[1] + (b[1] - a[1]) * (i + .5) / 7 + 6, 2.6)
                  for i in range(7)))

add(f'<path d="{poly(LQ)}" fill="url(#gBookL)" stroke="#55091f" stroke-width="3" stroke-linejoin="round"/>')
add(f'<path d="{poly(RQ)}" fill="url(#gBookR)" stroke="#34041a" stroke-width="3" stroke-linejoin="round"/>')
for i, q in enumerate((LQ, RQ)):
    adef(f'<clipPath id="cPanel{i}"><path d="{poly(q)}"/></clipPath>')
    add(f'<g clip-path="url(#cPanel{i})"><rect x="290" y="600" width="540" height="520" '
        f'filter="url(#fLeather)" opacity="0.2"/></g>')
add(f'<path d="{poly(LQ)}" fill="url(#gBookSheen)"/>')
add(f'<path d="{SPINE}" fill="url(#gSpine)" stroke="#2a030c" stroke-width="1.5"/>')
add(f'<path d="{poly([(310, 614), (548, 635), (548, 642), (308, 622)])}" fill="url(#gPages)"/>')
add(f'<path d="{poly([(584, 641), (806, 683), (805, 690), (584, 648)])}" fill="url(#gPages)"/>')


def corners(q):
    s = []
    s.append(f'<path d="{qpoly(q, [(0.06, 0.035), (0.94, 0.035), (0.94, 0.965), (0.06, 0.965)])}" '
             f'fill="none" stroke="{GOLD}" stroke-width="2"/>')
    s.append(f'<path d="{qpoly(q, [(0.09, 0.055), (0.91, 0.055), (0.91, 0.945), (0.09, 0.945)])}" '
             f'fill="none" stroke="{GOLD}" stroke-width="0.9" opacity="0.8"/>')
    curl = ("M 0 0 C 22 -1 38 8 38 26 C 38 38 26 42 20 34 C 15 27 22 20 28 24 "
            "M 0 0 C -1 22 8 38 26 38 C 38 38 42 26 34 20 C 27 15 20 22 24 28")
    for (u, v, sx, sy) in [(0.09, 0.055, 1, 1), (0.91, 0.055, -1, 1), (0.91, 0.945, -1, -1), (0.09, 0.945, 1, -1)]:
        s.append(f'<g transform="{qframe(q, u, v)}"><g transform="scale({sx} {sy})">'
                 f'<path d="{curl}" fill="none" stroke="{GOLD}" stroke-width="1.6" stroke-linecap="round"/>'
                 f'<circle cx="7" cy="7" r="3" fill="{GOLD}"/></g></g>')
    return "".join(s)


add(corners(LQ) + corners(RQ))
# right cover: rose medallion
med = [f'<g transform="{qframe(RQ, 0.47, 0.43)}">']
med.append(''.join(f'<circle cx="{n(72 * math.cos(math.radians(a)))}" cy="{n(90 * math.sin(math.radians(a)))}" '
                   f'r="2.2" fill="{GOLD}"/>' for a in range(0, 360, 15)))
med.append(f'<ellipse rx="62" ry="80" fill="#3a0716" stroke="{GOLD}" stroke-width="3"/>')
med.append(f'<ellipse rx="54" ry="71" fill="none" stroke="{GOLD}" stroke-width="1.1" opacity="0.8"/>')
for side in (-1, 1):
    med.append(f'<g transform="scale({side} 1)">'
               + "".join(f'<path d="M {n(10 + i * 7)} {n(52 - i * 13)} q 8 -2 12 -10 q -9 0 -12 10 Z" '
                         f'fill="{GOLD}" opacity="0.9"/>' for i in range(5))
               + f'<path d="M 8 58 Q 36 30 40 -8" fill="none" stroke="{GOLD}" stroke-width="1.4"/></g>')
med.append(rose(0, -6, 26, 0))
med.append(star4(0, -104, 10, GOLD_L, 1))
med.append(f'<path d="M -46 100 L 46 100 L 38 108 L 46 116 L -46 116 L -38 108 Z" fill="none" '
           f'stroke="{GOLD}" stroke-width="1.5"/>')
med.append('</g>')
add("".join(med))
# left cover: crescent moon and stars
moon = [f'<g transform="{qframe(LQ, 0.5, 0.44)}">']
moon.append(f'<circle r="64" fill="none" stroke="{GOLD}" stroke-width="1.2" opacity="0.7"/>')
adef('<mask id="mMoon" maskUnits="userSpaceOnUse" x="-80" y="-80" width="160" height="160">'
     '<circle r="46" fill="#fff"/><circle cx="20" cy="-10" r="40" fill="#000"/></mask>')
moon.append(f'<g mask="url(#mMoon)"><circle r="46" fill="url(#gGoldF)"/>'
            f'<circle r="45" fill="none" stroke="{GOLD_D}" stroke-width="1.2"/></g>')
for (x, y, r_) in [(26, -14, 10), (40, 18, 6), (14, 30, 4), (-60, -50, 5), (58, -54, 4)]:
    moon.append(star4(x, y, r_, GOLD_L, 1))
moon.append(f'<path d="M -70 110 L 70 110 M -40 122 L 40 122" stroke="{GOLD}" stroke-width="1.2" opacity="0.8"/>')
moon.append('</g>')
add("".join(moon))
sb = []
for v in (0.08, 0.13, 0.87, 0.92):
    lx, ly, rx_, ry_ = 548 + 14 * v, 642 + 430 * v, 584 + 14 * v, 648 + 430 * v
    sb.append(f'<path d="M {n(lx)} {n(ly)} Q {n((lx + rx_) / 2)} {n((ly + ry_) / 2 + 7)} {n(rx_)} {n(ry_)}" '
              f'fill="none" stroke="{GOLD}" stroke-width="3"/>')
for v in (0.32, 0.5, 0.68):
    sb.append(star4(566 + 14 * v, 645 + 430 * v, 8 if v == 0.5 else 5, GOLD, 1))
add("".join(sb))
add(f'<path d="M 560 660 L 573 1060" stroke="#ffadc2" stroke-width="4" opacity="0.35" {blur(2)}/>')
add('<path d="M 308 622 L 548 642 M 308 622 L 320 1030" stroke="#e66a8c" stroke-width="2" opacity="0.5" fill="none"/>')
add(f'<path d="M 805 690 L 800 1092" stroke="#ff8fae" stroke-width="5" opacity="0.45" {blur(3)}/>'
    f'<path d="M 805 690 L 800 1092" stroke="#ffb3c6" stroke-width="1.4" opacity="0.8"/>')
add(f'<path d="M 312 616 L 548 637 M 586 642 L 805 684" stroke="#ffe7b0" stroke-width="5" '
    f'opacity="0.6" {blur(3)} style="mix-blend-mode:screen"/>')


# ---- hands ----------------------------------------------------------------
def finger(bx, by, dx, dy, L, wb, wt):
    px, py = -dy, dx
    tx, ty = bx + dx * L, by + dy * L
    k = wt * 1.35
    p1, p2 = (bx + px * wb, by + py * wb), (tx + px * wt, ty + py * wt)
    p3, p4 = (tx - px * wt, ty - py * wt), (bx - px * wb, by - py * wb)
    return (f"M {n(p1[0])} {n(p1[1])} L {n(p2[0])} {n(p2[1])} "
            f"C {n(p2[0] + dx * k)} {n(p2[1] + dy * k)} {n(p3[0] + dx * k)} {n(p3[1] + dy * k)} "
            f"{n(p3[0])} {n(p3[1])} L {n(p4[0])} {n(p4[1])} Z")


def hand(back_d, bases, direction, lens, grad):
    dx, dy = norm(*direction)
    px, py = -dy, dx
    fingers = [(bx, by, L) for (bx, by), L in zip(bases, lens)]
    sh = "".join(f'<path d="{finger(bx, by, dx, dy, L, 10.5, 8)}"/>' for bx, by, L in fingers)
    s = [f'<g transform="translate(6 9)" fill="#1a0010" opacity="0.45" {blur(5)}>{sh}</g>',
         f'<path d="{back_d}" fill="url(#{grad})" stroke="#cf9298" stroke-width="1.1"/>']
    for bx, by, L in reversed(fingers):
        s.append(f'<path d="{finger(bx, by, dx, dy, L, 10.5, 8)}" fill="url(#{grad})" stroke="#cf9298" '
                 f'stroke-width="1.1"/>')
        tx, ty = bx + dx * L, by + dy * L
        nb, nt = (tx - dx * 11, ty - dy * 11), (tx + dx * 3.5, ty + dy * 3.5)
        s.append(f'<path d="{finger(nb[0], nb[1], dx, dy, 14.5, 5.2, 5)}" fill="#fbd3da" stroke="#eaa9b4" '
                 f'stroke-width="0.7"/>')
        s.append(f'<path d="M {n(nb[0] + px * 2 + dx * 3)} {n(nb[1] + py * 2 + dy * 3)} L '
                 f'{n(nt[0] + px * 2 - dx * 3)} {n(nt[1] + py * 2 - dy * 3)}" stroke="#fff" stroke-width="1.2" '
                 f'opacity="0.85" stroke-linecap="round"/>')
        for frac, half in ((0.42, 5.5), (0.68, 4.5)):
            cx, cy = bx + dx * L * frac, by + dy * L * frac
            s.append(f'<path d="M {n(cx - px * half)} {n(cy - py * half)} Q {n(cx + dx * 2.5)} {n(cy + dy * 2.5)} '
                     f'{n(cx + px * half)} {n(cy + py * half)}" stroke="#dba3a6" stroke-width="1" fill="none" '
                     f'opacity="0.8"/>')
        s.append(f'<path d="M {n(bx - px * 4)} {n(by - py * 4)} L {n(tx - px * 3 - dx * 8)} {n(ty - py * 3 - dy * 8)}" '
                 f'stroke="#fff" stroke-width="2" opacity="0.55" stroke-linecap="round"/>')
    return "".join(s)


add(hand("M 798 836 C 820 826 848 840 856 870 C 862 903 868 938 878 966 L 832 988 "
         "C 830 960 830 940 826 924 C 818 900 806 866 798 836 Z",
         [(808, 846), (814, 868), (820, 890), (826, 912)], (-0.93, -0.36), [62, 68, 63, 52], "gSkinN"))
add(hand("M 322 862 C 300 856 276 868 268 896 C 260 926 254 956 246 985 L 298 998 "
         "C 300 975 300 958 302 946 C 308 920 316 890 322 862 Z",
         [(318, 870), (312, 892), (306, 914), (300, 936)], (0.95, -0.3), [60, 66, 61, 50], "gSkinF"))
add(frill((808, 994), (898, 956), 7, 8, 22))
add(frill((230, 982), (310, 1004), 6, 8, 22))

# ---- light, sparkles and petals drifting up from the pages ----------------
for _ in range(46):
    x = random.uniform(330, 800)
    y = random.uniform(380, 640) if random.random() < 0.7 else random.uniform(200, 380)
    if in_ellipse(x, y, 712, 560, 115, 80) or in_ellipse(x, y, 655, 430, 215, 190):
        continue
    hgt = (650 - y) / 450
    op = max(0.25, 0.95 - hgt * 0.7)
    r = max(2.5, 8 - hgt * 5) * random.uniform(0.6, 1.2)
    k = random.random()
    if k < 0.45:
        add(star4(x, y, r, random.choice([GOLD_L, "#fff", "#ffe0b0"]), op, 'filter="url(#glow)"'))
    elif k < 0.75:
        add(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r * .3)}" fill="#fff0c8" opacity="{op:.2f}" filter="url(#glow)"/>')
    else:
        add(petal(x, y, r / 9, random.uniform(0, 360), random.uniform(0.5, 0.9),
                  random.choice(["gPetalR", "gPetalP"]), op))
add('</g>')  # book group

# glint beside the glancing eye
add(star4(793, 553, 14, "#fff", 0.9, 'filter="url(#glowBig)"', k=0.1))
add(star4(812, 534, 6, GOLD_L, 0.85, 'filter="url(#glow)"'))
add('</g>')  # character


# ==========================================================================
# 3. FOREGROUND + GRADING (canvas coordinates)
# ==========================================================================
for _ in range(34):
    x, y = random.uniform(0, W), random.uniform(0, H)
    if in_ellipse(x, y, 700, 520, 260, 300):
        continue
    near = random.random() < 0.35
    add(petal(x, y, random.uniform(1.4, 2.4) if near else random.uniform(0.8, 1.3), random.uniform(0, 360),
              random.uniform(0.45, 0.95), random.choice(["gPetalR", "gPetalP", "gPetalW"]),
              random.uniform(0.75, 0.95), b=random.choice([2, 3]) if near else 0))
# blurred roses in the near foreground
add(f'<g {blur(5)} opacity="0.95">' + leaf(30, 1380, 90, 26, -40) + leaf(120, 1470, 80, 22, -10)
    + rose(70, 1440, 105, 20) + rose(215, 1500, 70, -30, ("#6e1a34", "#e0577d", "#ff9db6", "#ffe0e8")) + '</g>')
add(f'<g {blur(4)} opacity="0.9">' + leaf(1170, 1360, 80, 22, 200) + rose(1150, 1420, 88, -15) + '</g>')
for _ in range(14):
    x, y = random.uniform(40, W - 40), random.uniform(60, H - 60)
    if in_ellipse(x, y, 700, 520, 280, 320):
        continue
    add(star4(x, y, random.uniform(3, 8), random.choice([GOLD_L, "#fff", "#ffd1dc"]),
              random.uniform(0.5, 0.9), 'filter="url(#glow)"'))

add(f'<rect width="{W}" height="{H}" fill="url(#gKey)" style="mix-blend-mode:screen"/>')
add(f'<rect width="{W}" height="{H}" fill="url(#gHaze)" style="mix-blend-mode:screen"/>')
add(f'<rect width="{W}" height="{H}" fill="url(#gVig)"/>')
add(f'<rect width="{W}" height="{H}" filter="url(#fGrain)" opacity="0.05" style="mix-blend-mode:overlay"/>')

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
       f'<title>Reverie - a glance over the book</title>'
       f'<defs>{"".join(defs)}</defs>{"".join(out)}</svg>')
with open(os.path.join(HERE, "reverie.svg"), "w", encoding="utf-8") as fh:
    fh.write(svg)
print(f"wrote reverie.svg ({len(svg) / 1024:.0f} KB)")
