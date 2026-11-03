#!/usr/bin/env python3
"""
"Peek" - an original fan-art reinterpretation of the masked jester of Elation
(Aha, Honkai: Star Rail). A silver-haired jester holds an open book up while
reading and glances over it at the viewer with one eye.

Everything is drawn from code; no game assets are used.

    python3 generate.py      # writes peek.svg next to this file
    node render.js           # renders peek.png (2400x3000)
"""
import math
import os
import random

random.seed(1103)
W, H = 1200, 1500
HERE = os.path.dirname(os.path.abspath(__file__))

defs, out = [], []
add = out.append
adef = defs.append

GOLD, GOLD_D, GOLD_L = "#ebc06a", "#a8732a", "#fff0c2"
CRIMSON, CRIMSON_D = "#c4183f", "#5e0a1f"


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def n(v):
    return f"{v:.1f}"


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
    """Return a filter attribute for a Gaussian blur, defining the filter on first use."""
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
    """Light catching the edge of a shape: shape minus a blurred, shifted copy."""
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


def qellipse(q, cu, cv, ru, rv, steps=72, t0=0.0, t1=2 * math.pi, close=True):
    uv = []
    for i in range(steps + 1):
        t = t0 + (t1 - t0) * i / steps
        uv.append((cu + ru * math.cos(t), cv + rv * math.sin(t)))
    return qpoly(q, uv, close)


def norm(x, y):
    l = math.hypot(x, y)
    return x / l, y / l


# --------------------------------------------------------------------------
# gradients, patterns, filters
# --------------------------------------------------------------------------
rad("gBg", 640, 520, 1000, [(0, "#4f1533"), (0.35, "#2c0b20"), (0.7, "#150611"), (1, "#070209")])
rad("gHalo", 652, 470, 440, [(0, "#ffd9ae", 0.62), (0.3, "#ff9c86", 0.26),
                             (0.65, "#c2285a", 0.08), (1, "#c2285a", 0)])
lin("gCurtain", 0, 0, 230, 0, [(0, "#1e020a"), (0.6, "#5a0c20"), (1, "#7e1531")])
lin("gCurtainShade", 0, 0, 0, 1500, [(0, "#000", 0.55), (0.35, "#000", 0.05), (1, "#000", 0.6)])
lin("gValance", 0, 0, 0, 125, [(0, "#2e040f"), (0.75, "#6b1027"), (1, "#3c0717")])
lin("gGoldF", 0, 0, 1, 1, [(0, GOLD_L), (0.35, "#f1c66b"), (0.7, GOLD_D), (1, "#f5d68a")],
    units="objectBoundingBox")
rad("gBell", 0.35, 0.3, 0.8, [(0, "#fff6d2"), (0.45, "#e9b85a"), (1, "#7a4c14")],
    units="objectBoundingBox")
rad("gGem", 0.35, 0.3, 0.85, [(0, "#ff9cb0"), (0.4, "#e0193f"), (1, "#4d0414")],
    units="objectBoundingBox")

lin("gHairF", 0, 314, 0, 890, [(0, "#fbf8fe"), (0.38, "#e7e0f2"), (0.5, "#d9cde9"),
                               (0.62, "#e4aac2"), (1, "#a8183c")])
lin("gHairB", 0, 300, 0, 1220, [(0, "#efeaf6"), (0.35, "#cdc1df"), (0.6, "#a58bb6"),
                                (0.85, "#7a2347"), (1, "#5a0f2c")])
lin("gHairInner", 0, 640, 0, 1160, [(0, "#d23a5e"), (0.5, "#8e1233"), (1, "#3e0616")])
lin("gHairShade", 640, 0, 846, 0, [(0, "#7d6aa6", 0), (1, "#6f5c9c", 0.5)])
lin("gHairShadeB", 430, 0, 900, 0, [(0, "#000", 0.05), (1, "#2a0f2e", 0.35)])
rad("gHairOcc", 650, 610, 340, [(0, "#2e1a44", 0.55), (0.55, "#3a2252", 0.3), (1, "#3a2252", 0)])

lin("gSkin", 0, 440, 0, 780, [(0, "#fcefea"), (1, "#f5dad3")])
lin("gFaceShade", 600, 0, 792, 0, [(0, "#d38a96", 0), (1, "#c97a8a", 0.42)])
lin("gUplight", 0, 715, 0, 585, [(0, "#ffc06e", 0.6), (1, "#ffc06e", 0)])
lin("gIris", 0, 586, 0, 640, [(0, "#22030c"), (0.28, "#5e0a20"), (0.55, "#b8163a"),
                              (0.8, "#ff5a3c"), (1, "#ffd27c")])
lin("gLid", 0, 590, 0, 614, [(0, "#3a0f22", 0.7), (1, "#3a0f22", 0)])
lin("gEyeWhite", 0, 592, 0, 640, [(0, "#efe1ea"), (1, "#ffffff")])

rad("gMask", -25, -35, 125, [(0, "#ffffff"), (0.55, "#f2edf3"), (1, "#c7bacb")])

lin("gCoat", 0, 850, 0, 1500, [(0, "#2c1f36"), (0.5, "#18101e"), (1, "#0a060c")])
lin("gCoatShade", 300, 0, 1050, 0, [(0, "#fff", 0.05), (1, "#000", 0.3)])
lin("gVest", 0, 1040, 0, 1500, [(0, "#ad1a3d"), (1, "#4e0818")])
lin("gLapel", 0, 1040, 0, 1500, [(0, "#61102a"), (1, "#25040d")])
lin("gJabot", 0, 1070, 0, 1200, [(0, "#ffffff"), (1, "#d9cfe2")])

lin("gBookL", 308, 622, 562, 1072, [(0, "#b52a4c"), (0.45, "#881732"), (1, "#4a0818")])
lin("gBookR", 584, 648, 800, 1092, [(0, "#7a1229"), (0.55, "#4c0819"), (1, "#2a030d")])
lin("gSpine", 548, 0, 598, 0, [(0, "#3e0613"), (0.35, "#8c1a35"), (0.5, "#d84d6f"),
                               (0.62, "#8e1a36"), (1, "#320510")])
lin("gPages", 0, 0, 1, 0, [(0, "#fbefcf"), (0.5, "#ffe6a6"), (1, "#e2b260")],
    units="objectBoundingBox")
lin("gBookSheen", 308, 622, 450, 900, [(0, "#ffd7c9", 0.32), (1, "#ffd7c9", 0)])

lin("gGloveN", 740, 820, 880, 990, [(0, "#ffffff"), (0.6, "#eee8f3"), (1, "#c4b9d2")])
lin("gGloveF", 250, 850, 380, 990, [(0, "#ffffff"), (0.7, "#f4f0f7"), (1, "#d6cde0")])
lin("gSleeveN", 820, 960, 1080, 1500, [(0, "#2e2037"), (1, "#0b070d")])
lin("gSleeveF", 230, 980, 330, 1500, [(0, "#3b2a46"), (1, "#0d080f")])
lin("gCuff", 0, 950, 0, 1065, [(0, "#d42c50"), (1, "#7a0f28")])

rad("gVig", 640, 640, 980, [(0, "#000", 0), (0.55, "#000", 0), (0.85, "#05000a", 0.45),
                            (1, "#05000a", 0.82)])
rad("gKey", 180, 120, 1100, [(0, "#ffd9b0", 0.26), (0.5, "#ffb38a", 0.07), (1, "#ffb38a", 0)])
rad("gRimAmb", 1200, 760, 700, [(0, "#ff3d6e", 0.16), (1, "#ff3d6e", 0)])
lin("gBottom", 0, 1100, 0, 1500, [(0, "#3b0016", 0), (1, "#1a0009", 0.55)])
lin("gBeam", 0, 0, 0, 1500, [(0, "#ffe9cf", 0.9), (1, "#ffe9cf", 0)])

adef('<pattern id="pDiamond" patternUnits="userSpaceOnUse" width="28" height="40">'
     '<path d="M14 0 L28 20 L14 40 L0 20 Z" fill="none" stroke="#f0c46a" '
     'stroke-width="1.2" stroke-opacity="0.5"/>'
     '<circle cx="14" cy="20" r="1.8" fill="#f0c46a" fill-opacity="0.55"/></pattern>')

adef('<filter id="glow" x="-150%" y="-150%" width="400%" height="400%">'
     '<feGaussianBlur stdDeviation="3" result="b"/>'
     '<feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/>'
     '</feMerge></filter>')
adef('<filter id="glowBig" x="-200%" y="-200%" width="500%" height="500%">'
     '<feGaussianBlur stdDeviation="7" result="b"/>'
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
# reusable props
# --------------------------------------------------------------------------
MASK_OUTLINE = ("M 0 -85 C 55 -85 78 -40 75 5 C 72 55 40 88 0 90 "
                "C -40 88 -72 55 -75 5 C -78 -40 -55 -85 0 -85 Z")
MASK_EYES = ("M -46 -14 Q -28 -42 -10 -14 Q -28 -27 -46 -14 Z "
             "M 10 -14 Q 28 -42 46 -14 Q 28 -27 10 -14 Z")
MASK_GRIN = "M -48 27 Q 0 94 48 27 Q 0 50 -48 27 Z"


def bg_mask(cx, cy, s, rot, op, b):
    return (f'<g transform="translate({cx} {cy}) rotate({rot}) scale({s})" opacity="{op}">'
            f'<g {blur(b)}><path d="{MASK_OUTLINE}" fill="#f4eef6"/>'
            f'<path d="{MASK_EYES}" fill="#2a0c18"/><path d="{MASK_GRIN}" fill="#2a0c18"/>'
            f'<path d="{diamond(30, 12, 6, 11)}" fill="{CRIMSON}"/></g></g>')


def card(cx, cy, w, h, rot, b=0, op=1.0):
    x, y = -w / 2, -h / 2
    ba = blur(b) if b else ""
    fs = w * 0.2
    corner = (f'<text x="{n(x + w * 0.1)}" y="{n(y + h * 0.17)}" font-family="DejaVu Serif" '
              f'font-weight="bold" font-size="{n(fs)}" fill="{CRIMSON}">A</text>'
              f'<path d="{diamond(x + w * 0.165, y + h * 0.25, w * 0.055, h * 0.055)}" '
              f'fill="{CRIMSON}"/>')
    return (f'<g transform="translate({cx} {cy}) rotate({rot})" opacity="{op}"><g {ba}>'
            f'<rect x="{n(x + 4)}" y="{n(y + 7)}" width="{w}" height="{h}" rx="{n(w * 0.09)}" '
            f'fill="#000" opacity="0.35"/>'
            f'<rect x="{n(x)}" y="{n(y)}" width="{w}" height="{h}" rx="{n(w * 0.09)}" '
            f'fill="#f8f2ef" stroke="#d9b56a" stroke-width="{n(max(1.0, w * 0.02))}"/>'
            f'<rect x="{n(x + w * 0.27)}" y="{n(y + h * 0.12)}" width="{n(w * 0.46)}" '
            f'height="{n(h * 0.76)}" rx="{n(w * 0.04)}" fill="none" stroke="{CRIMSON}" '
            f'stroke-width="{n(max(0.8, w * 0.012))}" opacity="0.55"/>'
            f'<path d="{diamond(0, 0, w * 0.16, h * 0.17)}" fill="{CRIMSON}"/>'
            f'{corner}<g transform="rotate(180)">{corner}</g></g></g>')


CONF_COLORS = ["#e3244f", "#f2c063", "#ffffff", "#ff7aa2", "#b8173c", "#ffd98a"]


def confetti(x, y, size, rot, color, op, b=0):
    ba = blur(b) if b else ""
    k = random.random()
    tr = f'transform="translate({n(x)} {n(y)}) rotate({rot:.0f})"'
    if k < 0.5:
        w, h = size * 0.55, size
        return (f'<g {tr} opacity="{op:.2f}"><rect x="{n(-w / 2)}" y="{n(-h / 2)}" '
                f'width="{n(w)}" height="{n(h)}" fill="{color}" {ba}/></g>')
    if k < 0.82:
        return (f'<g {tr} opacity="{op:.2f}"><path d="{diamond(0, 0, size * 0.36, size * 0.6)}" '
                f'fill="{color}" {ba}/></g>')
    return f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(size * 0.28)}" fill="{color}" opacity="{op:.2f}" {ba}/>'


def bell(cx, cy, r):
    return (f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{r}" fill="url(#gBell)" stroke="{GOLD_D}" '
            f'stroke-width="1"/>'
            f'<path d="M {n(cx - r * 0.55)} {n(cy + r * 0.25)} L {n(cx + r * 0.55)} {n(cy + r * 0.25)}" '
            f'stroke="#5a3510" stroke-width="1.4" stroke-linecap="round"/>'
            f'<circle cx="{n(cx)}" cy="{n(cy + r * 0.55)}" r="{n(r * 0.16)}" fill="#5a3510"/>'
            f'<circle cx="{n(cx - r * 0.35)}" cy="{n(cy - r * 0.35)}" r="{n(r * 0.22)}" fill="#fff" '
            f'opacity="0.85"/>')


def in_ellipse(x, y, cx, cy, rx, ry):
    return ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 < 1


# ==========================================================================
# 1. BACKGROUND
# ==========================================================================
add(f'<rect width="{W}" height="{H}" fill="url(#gBg)"/>')

for _ in range(170):
    x, y = random.uniform(0, W), random.uniform(0, H * 0.78)
    r = random.choice([0.6, 0.8, 1.0, 1.2, 1.6])
    add(f'<circle cx="{n(x)}" cy="{n(y)}" r="{r}" fill="#fff" '
        f'opacity="{random.uniform(0.15, 0.75):.2f}"/>')

bok = ["#ff9a7a", "#ffcf8a", "#ff5d7e", "#c98bff", "#ffb3c7"]
for _ in range(30):
    x, y = random.uniform(40, W - 40), random.uniform(40, H - 200)
    add(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(random.uniform(14, 62))}" '
        f'fill="{random.choice(bok)}" opacity="{random.uniform(0.05, 0.14):.2f}" {blur(6)}/>')

# halo / stage ring behind the head
hx, hy = 652, 470
add(f'<circle cx="{hx}" cy="{hy}" r="440" fill="url(#gHalo)"/>')
add(f'<circle cx="{hx}" cy="{hy}" r="345" fill="none" stroke="{GOLD}" stroke-width="1" opacity="0.2"/>')
add(f'<circle cx="{hx}" cy="{hy}" r="318" fill="none" stroke="{GOLD}" stroke-width="3" '
    f'stroke-dasharray="1.5 12" stroke-linecap="round" opacity="0.5"/>')
add(f'<circle cx="{hx}" cy="{hy}" r="300" fill="none" stroke="{GOLD}" stroke-width="2.4" opacity="0.45"/>')
add(f'<circle cx="{hx}" cy="{hy}" r="262" fill="none" stroke="#ffb3a0" stroke-width="1" opacity="0.25"/>')
ticks = []
for i in range(72):
    a = 2 * math.pi * i / 72
    r1 = 276 if i % 6 else 268
    ticks.append(f"M {n(hx + r1 * math.cos(a))} {n(hy + r1 * math.sin(a))} "
                 f"L {n(hx + 286 * math.cos(a))} {n(hy + 286 * math.sin(a))}")
add(f'<path d="{" ".join(ticks)}" stroke="{GOLD}" stroke-width="1.4" opacity="0.32"/>')
for i in range(16):
    a = 2 * math.pi * i / 16 + math.pi / 16
    x, y = hx + 300 * math.cos(a), hy + 300 * math.sin(a)
    add(f'<path d="{diamond(x, y, 5, 8)}" fill="{GOLD if i % 2 else "#ff4d6d"}" opacity="0.75" '
        f'transform="rotate({math.degrees(a) + 90:.1f} {n(x)} {n(y)})"/>')
for a in (-90, 0, 180, -45, -135):
    x, y = hx + 300 * math.cos(math.radians(a)), hy + 300 * math.sin(math.radians(a))
    s = 22 if a in (-90, 0, 180) else 13
    add(star4(x, y, s, GOLD_L, 0.9, 'filter="url(#glowBig)"'))

# light beams from the upper left
for (x0, x1, x2, x3, op) in [(150, 300, 900, 600, 0.05), (360, 430, 1060, 920, 0.04),
                             (40, 110, 520, 380, 0.035)]:
    add(f'<path d="{poly([(x0, 0), (x1, 0), (x2, H), (x3, H)])}" fill="url(#gBeam)" '
        f'opacity="{op}" {blur(18)} style="mix-blend-mode:screen"/>')

# curtains
CURTAIN = ("M 0 0 L 230 0 C 214 210 168 430 152 620 C 140 760 124 860 96 925 "
           "C 124 1000 150 1160 134 1500 L 0 1500 Z")
adef(f'<clipPath id="cCurtain"><path d="{CURTAIN}"/></clipPath>')
folds = []
for k in range(8):
    xt, xm, xb = 12 + k * 29, 6 + k * 11.5, 8 + k * 17
    d = (f"M {n(xt)} -10 C {n(xt - 4)} 320 {n(xm + 30)} 700 {n(xm)} 925 "
         f"C {n(xm + 4)} 1100 {n(xb)} 1300 {n(xb)} 1510")
    if k % 2:
        folds.append(f'<path d="{d}" fill="none" stroke="#b02a4c" stroke-width="7" '
                     f'opacity="0.38" {blur(4)}/>')
    else:
        folds.append(f'<path d="{d}" fill="none" stroke="#14010a" stroke-width="13" '
                     f'opacity="0.65" {blur(5)}/>')
curtain = (f'<path d="{CURTAIN}" fill="url(#gCurtain)"/>'
           f'<g clip-path="url(#cCurtain)">{"".join(folds)}'
           f'<rect width="240" height="{H}" fill="url(#gCurtainShade)"/></g>'
           f'<path d="M 152 620 C 140 760 124 860 96 925 C 124 1000 150 1160 134 1500" '
           f'fill="none" stroke="#ff5b82" stroke-width="2" opacity="0.35"/>'
           # tie-back rope + tassel
           f'<path d="M -10 905 C 40 890 90 905 112 925 C 90 945 40 950 -10 940" fill="none" '
           f'stroke="{GOLD}" stroke-width="7"/>'
           f'<path d="M -10 905 C 40 890 90 905 112 925 C 90 945 40 950 -10 940" fill="none" '
           f'stroke="{GOLD_D}" stroke-width="7" stroke-dasharray="4 5"/>'
           f'<ellipse cx="108" cy="944" rx="9" ry="12" fill="url(#gGoldF)"/>'
           + "".join(f'<path d="M {n(100 + i * 2.2)} 954 L {n(97 + i * 2.8)} {n(1005 + (i % 3) * 5)}" '
                     f'stroke="{GOLD}" stroke-width="2" opacity="0.9"/>' for i in range(8)))
add(f'<g>{curtain}</g>')
add(f'<g transform="translate({W} 0) scale(-1 1)">{curtain}</g>')

# valance
sc = []
for k in range(8):
    x = W - 150 * k
    sc.append(f"Q {x - 75} 128 {x - 150} 72")
VAL = f"M 0 0 L {W} 0 L {W} 72 " + " ".join(sc) + " Z"
add(f'<path d="{VAL}" fill="url(#gValance)"/>')
vf = []
for k in range(8):
    x0 = 150 * k
    for j in range(5):
        xx = x0 + 25 + j * 25
        vf.append(f'<path d="M {xx} 0 Q {xx + 4} 50 {xx} {n(78 + 22 * math.sin(math.pi * (j + 1) / 6))}" '
                  f'stroke="#16010a" stroke-width="6" fill="none" opacity="0.45" {blur(3)}/>')
add("".join(vf))
edge ="M 0 72 " + " ".join(f"Q {150 * k + 75} 128 {150 * (k + 1)} 72" for k in range(8))
add(f'<path d="{edge}" fill="none" stroke="{GOLD}" stroke-width="3.2"/>')
add(f'<path d="{edge}" fill="none" stroke="{GOLD}" stroke-width="10" '
    f'stroke-dasharray="1.6 4.4" transform="translate(0 7)" opacity="0.85"/>')
for k in range(1, 8):
    x = 150 * k
    add(f'<path d="M {x} 72 L {x} 92" stroke="{GOLD}" stroke-width="2"/>'
        f'<ellipse cx="{x}" cy="98" rx="7" ry="9" fill="url(#gGoldF)"/>'
        + "".join(f'<path d="M {n(x - 6 + i * 2)} 105 L {n(x - 7 + i * 2.3)} {n(135 + (i % 2) * 6)}" '
                  f'stroke="{GOLD}" stroke-width="1.6"/>' for i in range(7)))

# floating background masks & cards
add(bg_mask(285, 300, 0.55, 18, 0.22, 2))
add(bg_mask(930, 250, 0.45, -16, 0.2, 2.5))
add(bg_mask(1010, 640, 0.33, 12, 0.14, 3))
add(bg_mask(205, 860, 0.36, -10, 0.15, 3))
add(card(938, 392, 68, 98, 18, b=1.2, op=0.8))
add(card(222, 610, 76, 108, -14, b=0.8, op=0.85))

# background confetti
for _ in range(85):
    x, y = random.uniform(0, W), random.uniform(80, H)
    add(confetti(x, y, random.uniform(5, 11), random.uniform(0, 180), random.choice(CONF_COLORS),
                 random.uniform(0.25, 0.6), b=random.choice([0, 0.6, 1, 1.5])))
for _ in range(16):
    x, y = random.uniform(160, W - 160), random.uniform(120, 900)
    if in_ellipse(x, y, 650, 560, 250, 300):
        continue
    add(star4(x, y, random.uniform(4, 11), random.choice([GOLD_L, "#fff", "#ffc2d1"]),
              random.uniform(0.5, 0.95), 'filter="url(#glow)"'))


# ==========================================================================
# 2. CHARACTER
# ==========================================================================
HEAD = 'rotate(-7 660 620)'
add('<g transform="translate(0 -30)">')

# ---- back hair ----------------------------------------------------------
BACK = ("M 650 300 C 772 296 862 372 878 486 C 892 590 880 700 902 820 "
        "C 922 930 968 1020 1022 1108 L 968 1094 L 990 1186 L 930 1120 L 912 1200 "
        "L 868 1112 C 840 1060 800 1000 760 980 L 520 980 C 470 1010 440 1060 420 1120 "
        "L 410 1060 L 360 1110 C 400 1010 430 900 432 800 C 434 680 418 570 446 466 "
        "C 476 360 556 304 650 300 Z")
INNER = ("M 788 640 C 826 760 848 880 896 985 C 926 1045 958 1085 990 1112 L 942 1098 "
         "L 952 1156 L 896 1104 L 874 1162 L 836 1084 C 806 990 784 830 760 700 Z")
back_strands = ["M 842 420 C 872 560 858 700 888 840 C 906 940 948 1020 992 1100",
                "M 820 470 C 846 600 840 720 864 860 C 880 960 912 1050 944 1120",
                "M 470 470 C 452 600 456 720 444 840",
                "M 500 430 C 476 560 474 700 462 820"]
add(f'<g transform="{HEAD}">'
    f'<path d="{BACK}" fill="url(#gHairB)"/>'
    f'<path d="{BACK}" fill="url(#gHairShadeB)"/>'
    f'<path d="{BACK}" fill="url(#gHairOcc)"/>'
    f'<path d="{INNER}" fill="url(#gHairInner)"/>'
    + "".join(f'<path d="{s}" fill="none" stroke="#7a6394" stroke-width="2" opacity="0.6"/>'
              for s in back_strands)
    + "".join(f'<path d="{taper(*t)}" fill="#6d5888" opacity="0.45"/>' for t in [
        ((470, 450), (450, 620), (440, 800), 5), ((520, 420), (488, 560), (476, 700), 4),
        ((850, 440), (880, 640), (900, 860), 6), ((830, 520), (850, 760), (900, 980), 5)])
    + f'<path d="{BACK}" fill="none" stroke="#5d4a7a" stroke-width="1.6" opacity="0.55"/>'
    + rim(BACK, -12, 0, "#ff5d86", 4, 0.75)
    + rim(BACK, 10, 8, "#fff3e4", 4, 0.45)
    + '</g>')

# ---- neck & body ----------------------------------------------------------
add('<path d="M 612 735 C 616 790 608 845 596 892 L 724 892 C 712 840 706 790 708 728 Z" '
    'fill="#e9bfb7"/>')

COAT = ("M 640 858 C 720 864 830 885 905 922 C 965 952 995 1010 1010 1100 "
        "C 1022 1200 1036 1350 1046 1500 L 250 1500 C 262 1350 285 1180 305 1090 "
        "C 322 1010 372 958 445 928 C 515 900 585 862 640 858 Z")
adef(f'<clipPath id="cCoat"><path d="{COAT}"/></clipPath>')
add(f'<path d="{COAT}" fill="url(#gCoat)"/>')
add(f'<path d="{COAT}" fill="url(#gCoatShade)"/>')
coat_folds = ["M 860 1000 C 880 1150 900 1300 920 1500", "M 420 1080 C 410 1200 400 1350 395 1500",
              "M 760 1120 C 770 1250 780 1380 790 1500"]
add("".join(f'<path d="{s}" fill="none" stroke="#000" stroke-width="6" opacity="0.35" {blur(3)}/>'
            for s in coat_folds))
# vest + lapels
VEST = "M 548 1040 L 712 1040 C 690 1200 668 1350 652 1500 L 588 1500 C 580 1350 566 1200 548 1040 Z"
add(f'<path d="{VEST}" fill="url(#gVest)"/><path d="{VEST}" fill="url(#pDiamond)"/>')
add('<path d="M 500 1040 L 548 1040 C 566 1200 580 1350 588 1500 L 560 1500 C 548 1350 530 1200 500 1040 Z" '
    'fill="url(#gLapel)"/>')
add('<path d="M 712 1040 L 772 1040 C 734 1200 694 1350 670 1500 L 652 1500 C 668 1350 690 1200 712 1040 Z" '
    'fill="url(#gLapel)"/>')
add(f'<path d="M 548 1040 C 566 1200 580 1350 588 1500 M 712 1040 C 690 1200 668 1350 652 1500" '
    f'fill="none" stroke="{GOLD}" stroke-width="3"/>')
add(f'<path d="M 500 1040 C 530 1200 548 1350 560 1500 M 772 1040 C 734 1200 694 1350 670 1500" '
    f'fill="none" stroke="{GOLD_D}" stroke-width="1.6" opacity="0.8"/>')
for (bx, by) in [(629, 1180), (626, 1270), (623, 1360), (621, 1450)]:
    add(f'<circle cx="{bx}" cy="{by}" r="7.5" fill="url(#gGoldF)" stroke="{GOLD_D}" stroke-width="1"/>'
        f'<circle cx="{bx - 2.5}" cy="{by - 2.5}" r="2" fill="#fff" opacity="0.8"/>')
# watch chain with a tiny mask charm
add(f'<path d="M 628 1272 Q 712 1345 800 1290" fill="none" stroke="{GOLD}" stroke-width="3" '
    f'stroke-dasharray="4 2.5" stroke-linecap="round"/>')
add(f'<path d="M 712 1308 L 712 1322" stroke="{GOLD}" stroke-width="1.6"/>'
    f'<g transform="translate(712 1336) scale(0.15)"><path d="{MASK_OUTLINE}" fill="url(#gGoldF)" '
    f'stroke="{GOLD_D}" stroke-width="8"/><path d="{MASK_EYES}" fill="#3a1a08"/>'
    f'<path d="{MASK_GRIN}" fill="#3a1a08"/></g>')
# jabot + brooch peeking under the book (three ruffled tiers)
for (top, bot, half) in [(1150, 1205, 38), (1110, 1168, 42), (1066, 1128, 40)]:
    xs = [630 - half + i * (2 * half) / 6 for i in range(7)]
    rev = " ".join(f"Q {n((xs[i] + xs[i - 1]) / 2)} {bot + 14 if i % 2 else bot + 4} {n(xs[i - 1])} {bot}"
                   for i in range(6, 0, -1))
    add(f'<path d="M {n(xs[0] + 8)} {top} L {n(xs[-1] - 8)} {top} L {n(xs[-1])} {bot} {rev} Z" '
        f'fill="url(#gJabot)" stroke="#b3a5c4" stroke-width="1.2"/>')
    add(f'<path d="M {n(630 - half * 0.5)} {top + 6} Q {n(630 - half * 0.55)} {(top + bot) / 2} {n(630 - half * 0.6)} {bot + 6} '
        f'M 630 {top + 6} L 630 {bot + 10} M {n(630 + half * 0.5)} {top + 6} Q {n(630 + half * 0.55)} {(top + bot) / 2} '
        f'{n(630 + half * 0.6)} {bot + 6}" fill="none" stroke="#c5b9d3" stroke-width="1.2"/>')
add(f'<path d="{diamond(630, 1104, 13, 17)}" fill="url(#gGoldF)" stroke="{GOLD_D}" stroke-width="1"/>'
    f'<path d="{diamond(630, 1104, 7.5, 10.5)}" fill="url(#gGem)"/>'
    f'<circle cx="627" cy="1099" r="2" fill="#fff" opacity="0.9"/>')
# epaulette with fringe on the near shoulder
fr = []
for i in range(11):
    t = i / 10
    x = 888 + 84 * t
    y = 944 + 34 * t + 10 * math.sin(math.pi * t)
    fr.append(f'<path d="M {n(x)} {n(y)} L {n(x + 2)} {n(y + 28 + (i % 2) * 6)}" stroke="{GOLD}" '
              f'stroke-width="2.6" stroke-linecap="round"/>')
add("".join(fr))
add(f'<ellipse cx="928" cy="944" rx="50" ry="17" transform="rotate(27 928 944)" fill="#2a0712" '
    f'stroke="{GOLD}" stroke-width="3"/>'
    f'<ellipse cx="928" cy="944" rx="38" ry="10" transform="rotate(27 928 944)" fill="url(#gCuff)"/>'
    f'<path d="{diamond(928, 944, 7, 10)}" fill="url(#gGem)" stroke="{GOLD}" stroke-width="1"/>')
add(rim(COAT, -12, 0, "#ff4a78", 4, 0.75))

# ---- head ---------------------------------------------------------------
FACE = ("M 560 440 C 552 510 544 570 550 622 C 554 664 566 702 590 736 C 604 756 618 772 632 777 "
        "C 668 772 716 742 750 702 C 774 672 788 622 788 570 C 788 520 782 476 772 440 Z")
BANGS = ("M 492 500 C 488 400 560 318 655 314 C 752 312 826 380 826 482 "
         "C 826 540 820 600 818 660 C 816 720 830 800 846 884 "
         "C 822 850 800 820 794 790 C 786 740 782 690 784 630 C 786 580 784 548 780 520 "
         "Q 780 552 770 574 Q 758 545 750 522 "
         "Q 738 548 712 566 Q 706 532 700 510 "
         "Q 690 560 664 592 Q 656 550 652 512 "
         "C 644 585 612 660 568 712 C 552 650 540 590 532 540 "
         "C 522 520 505 508 492 500 Z")
EYE = ("M 662 617 C 678 601 704 592 732 592 C 752 592 766 598 775 608 "
       "C 770 620 760 628 748 632 C 728 640 696 636 662 617 Z")
adef(f'<clipPath id="cFace"><path d="{FACE}"/></clipPath>')
adef(f'<clipPath id="cEye"><path d="{EYE}"/></clipPath>')
adef(f'<clipPath id="cBangs"><path d="{BANGS}"/></clipPath>')

h = [f'<g transform="{HEAD}">']
h.append(f'<path d="{FACE}" fill="url(#gSkin)" stroke="#c98a90" stroke-width="1.4" '
         f'stroke-opacity="0.6"/>')
h.append(f'<g clip-path="url(#cFace)">'
         f'<rect x="540" y="430" width="260" height="360" fill="url(#gFaceShade)"/>'
         f'<path d="{BANGS}" transform="translate(4 14)" fill="#d48d9a" opacity="0.55" {blur(5)}/>'
         f'<ellipse cx="742" cy="660" rx="36" ry="14" fill="#ff7d93" opacity="0.5" {blur(6)}/>'
         f'<ellipse cx="612" cy="664" rx="22" ry="10" fill="#ff7d93" opacity="0.3" {blur(6)}/>'
         f'<path d="M 728 652 L 734 642 M 740 654 L 746 644 M 752 655 L 757 646" stroke="#ff8fa3" '
         f'stroke-width="1.5" stroke-linecap="round" opacity="0.7"/>'
         f'<ellipse cx="758" cy="642" rx="6" ry="3" fill="#fff" opacity="0.55" {blur(1)}/>'
         f'<path d="M 640 600 Q 628 628 618 650" fill="none" stroke="#d99aa3" stroke-width="5" '
         f'opacity="0.45" {blur(3)}/>'
         f'<rect x="540" y="560" width="260" height="230" fill="url(#gUplight)" '
         f'style="mix-blend-mode:screen"/></g>')
# eye
h.append(f'<path d="{EYE}" fill="url(#gEyeWhite)"/>')
iris = [f'<g clip-path="url(#cEye)">']
iris.append('<ellipse cx="736" cy="612" rx="21" ry="27" fill="url(#gIris)"/>')
for i in range(14):
    a = 2 * math.pi * i / 14
    iris.append(f'<path d="M {n(736 + 8 * math.cos(a))} {n(612 + 11 * math.sin(a))} '
                f'L {n(736 + 19 * math.cos(a))} {n(612 + 25 * math.sin(a))}" stroke="#ff9a7a" '
                f'stroke-width="1" opacity="0.35"/>')
iris.append(f'<ellipse cx="736" cy="627" rx="14" ry="8" fill="#ff8a5a" opacity="0.55" {blur(2)}/>')
iris.append('<ellipse cx="736" cy="612" rx="21" ry="27" fill="none" stroke="#2a0510" stroke-width="2.2"/>')
iris.append(f'<path d="{diamond(736, 611, 6.5, 13)}" fill="#16020a"/>')
iris.append('<rect x="650" y="586" width="140" height="30" fill="url(#gLid)"/>')
iris.append('<ellipse cx="726" cy="602" rx="7" ry="5.2" fill="#fff" transform="rotate(-20 726 602)"/>')
iris.append('<circle cx="746" cy="623" r="2.6" fill="#fff" opacity="0.9"/>')
iris.append(star4(749, 603, 5, "#fff", 0.95))
iris.append('</g>')
h.extend(iris)
h.append(f'<circle cx="736" cy="614" r="26" fill="#ff4d6d" opacity="0.14" {blur(8)} '
         f'style="mix-blend-mode:screen"/>')
h.append('<path d="M 672 587 C 696 573 730 571 760 579" fill="none" stroke="#c99aa6" '
         'stroke-width="1.6" opacity="0.85"/>')
h.append('<path d="M 658 618 C 670 595 702 580 732 580 C 752 580 768 586 781 595 L 795 584 '
         'C 793 597 787 605 779 611 C 768 599 752 592 732 592 C 704 592 679 602 663 620 Z" fill="#24101c"/>')
h.append('<path d="M 774 600 L 797 603 L 778 608 Z M 768 594 L 784 580 L 776 597 Z" fill="#24101c"/>')
h.append('<path d="M 664 617 Q 656 620 650 628" fill="none" stroke="#24101c" stroke-width="1.8" '
         'stroke-linecap="round"/>')
h.append('<path d="M 678 630 C 700 641 732 641 754 627 L 763 621" fill="none" stroke="#8a4a58" '
         'stroke-width="2" stroke-linecap="round"/>')
h.append('<path d="M 666 562 C 690 546 728 540 764 550 C 730 547 694 553 668 567 Z" fill="#a493b8"/>')
# bangs
h.append(f'<path d="{BANGS}" fill="url(#gHairF)"/>')
h.append(f'<g clip-path="url(#cBangs)">'
         f'<rect x="620" y="300" width="240" height="600" fill="url(#gHairShade)"/>'
         f'<path d="M 646 520 Q 636 590 604 652 Q 618 590 628 526 Z" fill="#b9a9d2" opacity="0.6"/>'
         f'<path d="M 520 470 Q 532 520 548 560" fill="none" stroke="#a796c4" stroke-width="7" '
         f'opacity="0.5" {blur(3)}/></g>')
strands = ["M 655 330 C 640 420 620 520 590 660", "M 670 330 C 672 420 668 500 664 580",
           "M 700 335 C 712 420 714 500 712 556", "M 735 345 C 752 420 764 500 770 566",
           "M 792 380 C 816 470 812 600 822 760", "M 620 330 C 590 400 560 470 545 560",
           "M 580 345 C 540 400 515 450 505 500", "M 805 420 C 820 520 808 640 832 860"]
h.append(f'<g clip-path="url(#cBangs)">' + "".join(
    f'<path d="{taper(*t)}" fill="#9a88bf" opacity="0.55"/>' for t in [
        ((700, 330), (735, 430), (750, 522), 6), ((672, 330), (690, 430), (700, 508), 6),
        ((650, 330), (652, 430), (652, 510), 5), ((632, 340), (618, 500), (586, 668), 8),
        ((610, 340), (575, 450), (548, 560), 6), ((760, 360), (800, 450), (792, 560), 5),
        ((802, 470), (812, 640), (836, 860), 6), ((585, 360), (535, 420), (512, 492), 5)])
    + "".join(f'<path d="{taper(*t)}" fill="#ffffff" opacity="0.55"/>' for t in [
        ((690, 345), (712, 430), (722, 520), 3), ((640, 350), (630, 470), (606, 600), 4),
        ((782, 420), (798, 560), (808, 700), 3)])
    + '</g>')
h.append(f'<path d="{BANGS}" fill="none" stroke="#6f5f92" stroke-width="1.6" opacity="0.6"/>')
# ahoge
h.append('<path d="M 660 318 C 668 280 700 258 728 268 C 706 272 686 288 672 318 Z" fill="url(#gHairF)"/>')
# angel-ring glints
h.append(f'<path d="M 588 402 Q 660 360 760 405" fill="none" stroke="#fff" stroke-width="12" '
         f'opacity="0.2" {blur(4)}/>')
for i in range(10):
    a = math.radians(252 + i * 6.3)
    px, py = 655 + 215 * math.cos(a), 600 + 215 * math.sin(a)
    dx, dy = norm(px - 655, py - 314)
    L = random.uniform(18, 32)
    w = random.uniform(2.2, 3.6)
    h.append(f'<path d="{poly([(px - dx * L / 2, py - dy * L / 2), (px - dy * w, py + dx * w), (px + dx * L / 2, py + dy * L / 2), (px + dy * w, py - dx * w)])}" '
             f'fill="#fff" opacity="0.85"/>')
adef('<clipPath id="cRimR"><rect x="772" y="250" width="200" height="700"/></clipPath>')
h.append(f'<g clip-path="url(#cRimR)">{rim(BANGS, -10, 2, "#ff7b9c", 3, 0.8)}</g>')
h.append(rim(BANGS, 8, 7, "#fff6ea", 4, 0.5))
# mask worn on the side of the head + ribbon tails with bells
h.append('<path d="M 470 492 C 458 520 444 552 437 578 L 450 582 C 458 554 470 524 482 496 Z" fill="#b5153a"/>')
h.append('<path d="M 480 496 C 478 528 472 558 470 584 L 483 586 C 487 556 491 528 494 500 Z" fill="#8e1030"/>')
h.append(bell(443, 584, 8) + bell(476, 590, 7))
h.append('<path d="M 474 490 C 452 468 438 494 460 502 Z M 474 490 C 496 474 504 500 482 504 Z" '
         'fill="#d02448" stroke="#7a0c26" stroke-width="1"/>')
m = ['<g transform="translate(505 420) rotate(-28)">']
m.append(f'<path d="{MASK_OUTLINE}" transform="translate(9 11)" fill="#2b1330" opacity="0.45" {blur(6)}/>')
m.append(f'<path d="{MASK_OUTLINE}" fill="url(#gMask)" stroke="#c9973f" stroke-width="3"/>')
m.append(f'<path d="{MASK_OUTLINE}" transform="scale(0.91)" fill="none" stroke="{GOLD}" '
         f'stroke-width="1.2" opacity="0.8"/>')
m.append(f'<path d="{MASK_EYES}" fill="#1a0a12"/>')
m.append(f'<path d="{MASK_GRIN}" fill="#1d0710"/>')
m.append('<path d="M -28 44 Q 0 68 28 44 Q 0 55 -28 44 Z" fill="#a3142f" opacity="0.9"/>')
m.append(f'<path d="{diamond(-30, 12, 6, 11)}" fill="{CRIMSON}"/>')
m.append(star4(30, 10, 8, GOLD, 1))
m.append('<ellipse cx="-42" cy="8" rx="12" ry="6" fill="#ff8fa3" opacity="0.35"/>'
         '<ellipse cx="42" cy="8" rx="12" ry="6" fill="#ff8fa3" opacity="0.35"/>')
m.append(f'<path d="M -6 -58 C -20 -72 -38 -62 -30 -48 M 6 -58 C 20 -72 38 -62 30 -48" fill="none" '
         f'stroke="{GOLD}" stroke-width="2.2" stroke-linecap="round"/>')
m.append(f'<path d="{diamond(0, -58, 6, 9)}" fill="url(#gGem)" stroke="{GOLD}" stroke-width="1.2"/>')
m.append('<path d="M 54 -60 L 42 -47 L 48 -39 L 36 -27 L 40 -20" fill="none" stroke="#5a4a5e" '
         'stroke-width="1.2"/>')
m.append(f'<ellipse cx="-28" cy="-50" rx="18" ry="9" fill="#fff" opacity="0.75" '
         f'transform="rotate(-30 -28 -50)" {blur(2)}/>')
m.append('</g>')
h.extend(m)
h.append('</g>')
add("".join(h))

# ---- book ---------------------------------------------------------------
LQ = [(308, 622), (548, 642), (562, 1072), (320, 1030)]
RQ = [(584, 648), (805, 690), (800, 1092), (598, 1078)]
SPINE = "M 548 642 Q 566 630 584 648 L 598 1078 Q 580 1090 562 1072 Z"
BOOK_ALL = poly([(308, 622), (548, 642), (566, 632), (584, 648), (805, 690), (800, 1092),
                 (598, 1078), (580, 1088), (562, 1072), (320, 1030)])

# glow spilling from the pages onto the face (behind the covers)
add(f'<g style="mix-blend-mode:screen">'
    f'<ellipse cx="556" cy="652" rx="290" ry="44" fill="#ffc46a" opacity="0.55" '
    f'transform="rotate(8 556 652)" {blur(22)}/>'
    f'<ellipse cx="560" cy="650" rx="170" ry="18" fill="#fff0c4" opacity="0.7" '
    f'transform="rotate(8 560 650)" {blur(8)}/></g>')
# cast shadow on the coat
add(f'<g clip-path="url(#cCoat)"><path d="{BOOK_ALL}" transform="translate(22 30)" fill="#000" '
    f'opacity="0.6" {blur(14)}/></g>')

# sleeves (forearms rising to the hands)
SLEEVE_N = ("M 818 990 L 890 958 C 938 1046 1002 1196 1050 1336 C 1066 1390 1076 1450 1082 1500 "
            "L 932 1500 C 922 1420 898 1300 868 1200 C 848 1120 834 1050 818 990 Z")
SLEEVE_F = "M 236 984 L 308 1000 C 314 1100 322 1280 338 1500 L 186 1500 C 196 1360 214 1160 236 984 Z"
add(f'<path d="{SLEEVE_N}" fill="url(#gSleeveN)"/>' + rim(SLEEVE_N, -10, 0, "#ff4a78", 4, 0.7))
add(f'<path d="{SLEEVE_F}" fill="url(#gSleeveF)"/>' + rim(SLEEVE_F, 9, 4, "#ffd9c0", 4, 0.35))
for cq in ([(818, 990), (890, 958), (916, 1015), (834, 1050)],
           [(236, 984), (308, 1000), (312, 1062), (228, 1048)]):
    add(f'<path d="{poly(cq)}" fill="url(#gCuff)"/>')
    add(f'<path d="M {n(cq[0][0])} {n(cq[0][1])} L {n(cq[1][0])} {n(cq[1][1])} '
        f'M {n(cq[3][0])} {n(cq[3][1])} L {n(cq[2][0])} {n(cq[2][1])}" stroke="{GOLD}" stroke-width="3"/>')
    for i in range(4):
        u = (i + 0.5) / 4
        x, y = qm(cq, u, 0.5)
        add(f'<path d="{diamond(x, y, 6, 10)}" fill="{GOLD if i % 2 else "#1a0a12"}" opacity="0.9"/>')

# the book itself
add(f'<path d="{poly(LQ)}" fill="url(#gBookL)" stroke="#5e0a1f" stroke-width="3" stroke-linejoin="round"/>')
add(f'<path d="{poly(RQ)}" fill="url(#gBookR)" stroke="#3a0512" stroke-width="3" stroke-linejoin="round"/>')
for q in (LQ, RQ):
    adef_id = f"cP{len(defs)}"
    adef(f'<clipPath id="{adef_id}"><path d="{poly(q)}"/></clipPath>')
    add(f'<g clip-path="url(#{adef_id})"><rect x="290" y="600" width="540" height="520" '
        f'filter="url(#fLeather)" opacity="0.22"/></g>')
add(f'<path d="{poly(LQ)}" fill="url(#gBookSheen)"/>')
add(f'<path d="{SPINE}" fill="url(#gSpine)" stroke="#2a030c" stroke-width="1.5"/>')
# page edges peeking above the covers
add(f'<path d="{poly([(310, 614), (548, 635), (548, 642), (308, 622)])}" fill="url(#gPages)"/>')
add(f'<path d="{poly([(584, 641), (806, 683), (805, 690), (584, 648)])}" fill="url(#gPages)"/>')
add('<path d="M 312 617 L 548 638 M 586 644 L 805 686" stroke="#c99a4e" stroke-width="0.8" opacity="0.8"/>')


def cover_deco(q, emblem):
    s = []
    s.append(f'<path d="{qpoly(q, [(0.06, 0.035), (0.94, 0.035), (0.94, 0.965), (0.06, 0.965)])}" '
             f'fill="none" stroke="{GOLD}" stroke-width="2.2"/>')
    s.append(f'<path d="{qpoly(q, [(0.1, 0.06), (0.9, 0.06), (0.9, 0.94), (0.1, 0.94)])}" '
             f'fill="none" stroke="{GOLD}" stroke-width="1.1" opacity="0.85"/>')
    for (cu, cv, su, sv) in [(0.1, 0.06, 1, 1), (0.9, 0.06, -1, 1), (0.9, 0.94, -1, -1), (0.1, 0.94, 1, -1)]:
        s.append(f'<path d="{qpoly(q, [(cu, cv - 0.022), (cu + 0.035, cv), (cu, cv + 0.022), (cu - 0.035, cv)])}" '
                 f'fill="{GOLD}"/>')
        arc = [(cu + su * 0.09 * math.cos(t), cv + sv * 0.06 * math.sin(t))
               for t in [k * math.pi / 2 / 12 for k in range(13)]]
        s.append(f'<path d="{qpoly(q, arc, close=False)}" fill="none" stroke="{GOLD}" stroke-width="1.5"/>')
    if emblem:
        cu, cv, ru, rv = 0.45, 0.42, 0.2, 0.133
        rays = []
        for i in range(16):
            a = 2 * math.pi * i / 16
            r2 = 1.2 if i % 2 == 0 else 1.1
            p1 = qm(q, cu + ru * 1.04 * math.cos(a), cv + rv * 1.04 * math.sin(a))
            p2 = qm(q, cu + ru * r2 * math.cos(a), cv + rv * r2 * math.sin(a))
            rays.append(f"M {n(p1[0])} {n(p1[1])} L {n(p2[0])} {n(p2[1])}")
        s.append(f'<path d="{" ".join(rays)}" stroke="{GOLD}" stroke-width="1.8" stroke-linecap="round"/>')
        s.append(f'<path d="{qellipse(q, cu, cv, ru, rv)}" fill="#3a0612" stroke="{GOLD}" stroke-width="2.6"/>')
        s.append(f'<path d="{qellipse(q, cu, cv, ru * 0.86, rv * 0.86)}" fill="none" stroke="{GOLD}" '
                 f'stroke-width="1" opacity="0.8"/>')
        fr_, fv = ru * 0.62, rv * 0.62

        def fm(x, y):
            return (cu + x * fr_, cv + y * fv)
        eyes = []
        for ex in (-0.42, 0.42):
            eyes.append(qpoly(q, [fm(ex + 0.22 * math.cos(t), -0.14 - 0.22 * math.sin(t))
                                  for t in [k * math.pi / 14 for k in range(15)]], close=False))
        s.append(f'<path d="{" ".join(eyes)}" fill="none" stroke="{GOLD_L}" stroke-width="2.4" '
                 f'stroke-linecap="round"/>')
        grin = ([fm(0.58 * math.cos(t), 0.2 + 0.4 * math.sin(t)) for t in [k * math.pi / 20 for k in range(21)]]
                + [fm(-0.58 * math.cos(t), 0.2 + 0.1 * math.sin(t)) for t in [k * math.pi / 20 for k in range(21)]])
        s.append(f'<path d="{qpoly(q, grin)}" fill="{CRIMSON}" stroke="{GOLD_L}" stroke-width="2"/>')
        dc = fm(0, -0.66)
        s.append(f'<path d="{qpoly(q, [(dc[0], dc[1] - 0.025), (dc[0] + 0.03, dc[1]), (dc[0], dc[1] + 0.025), (dc[0] - 0.03, dc[1])])}" '
                 f'fill="{GOLD_L}"/>')
        for u in (0.33, 0.45, 0.57):
            x, y = qm(q, u, 0.78)
            s.append(star4(x, y, 6 if u == 0.45 else 4, GOLD, 0.95))
        a, b = qm(q, 0.22, 0.74), qm(q, 0.68, 0.74)
        s.append(f'<path d="M {n(a[0])} {n(a[1])} L {n(b[0])} {n(b[1])}" stroke="{GOLD}" stroke-width="1" opacity="0.7"/>')
    else:
        cu, cv = 0.5, 0.45
        s.append(f'<path d="{qpoly(q, [(cu, cv - 0.1), (cu + 0.16, cv), (cu, cv + 0.1), (cu - 0.16, cv)])}" '
                 f'fill="none" stroke="{GOLD}" stroke-width="2"/>')
        s.append(f'<path d="{qpoly(q, [(cu, cv - 0.056), (cu + 0.09, cv), (cu, cv + 0.056), (cu - 0.09, cv)])}" '
                 f'fill="url(#gGem)" stroke="{GOLD}" stroke-width="1.4"/>')
        for (du, dv) in [(0, -0.125), (0.2, 0), (0, 0.125), (-0.2, 0)]:
            x, y = qm(q, cu + du, cv + dv)
            s.append(f'<circle cx="{n(x)}" cy="{n(y)}" r="2.6" fill="{GOLD}"/>')
        for v in (0.27, 0.63):
            a, b, c = qm(q, 0.25, v), qm(q, 0.75, v), qm(q, 0.5, v)
            s.append(f'<path d="M {n(a[0])} {n(a[1])} L {n(b[0])} {n(b[1])}" stroke="{GOLD}" stroke-width="1.2"/>')
            s.append(f'<path d="{diamond(c[0], c[1], 5, 7)}" fill="{GOLD}"/>')
    return "".join(s)


add(cover_deco(LQ, False))
add(cover_deco(RQ, True))
# spine bands and ornaments
sb = []
for v in (0.08, 0.13, 0.87, 0.92):
    lx, ly = 548 + 14 * v, 642 + 430 * v
    rx_, ry_ = 584 + 14 * v, 648 + 430 * v
    sb.append(f'<path d="M {n(lx)} {n(ly)} Q {n((lx + rx_) / 2)} {n((ly + ry_) / 2 + 7)} {n(rx_)} {n(ry_)}" '
              f'fill="none" stroke="{GOLD}" stroke-width="3.2"/>')
for v, kind in ((0.3, "s"), (0.5, "d"), (0.7, "s")):
    cx, cy = 566 + 14 * v, 645 + 430 * v
    sb.append(star4(cx, cy, 7, GOLD, 1) if kind == "s"
              else f'<path d="{diamond(cx, cy, 7, 12)}" fill="url(#gGem)" stroke="{GOLD}" stroke-width="1.2"/>')
add("".join(sb))
add(f'<path d="M 560 660 L 573 1060" stroke="#ff9db2" stroke-width="4" opacity="0.35" {blur(2)}/>')
add('<path d="M 308 622 L 548 642 M 308 622 L 320 1030" stroke="#e05a78" stroke-width="2" '
    'opacity="0.55" fill="none"/>')
add(f'<path d="M 805 690 L 800 1092" stroke="#ff6d8c" stroke-width="5" opacity="0.5" {blur(3)}/>'
    f'<path d="M 805 690 L 800 1092" stroke="#ff9ab0" stroke-width="1.6" opacity="0.8"/>')
# golden light on the page edges
add(f'<path d="M 312 616 L 548 637 M 586 642 L 805 684" stroke="#ffe3a0" stroke-width="5" '
    f'opacity="0.55" {blur(3)} style="mix-blend-mode:screen"/>')


# ---- hands --------------------------------------------------------------
def hand(back_d, bases, direction, lens, grad, light_side):
    dx, dy = norm(*direction)
    px, py = -dy, dx                     # perpendicular
    if py < 0:
        px, py = -px, -py                # make it point "down"
    s = [f'<path d="{back_d}" fill="url(#{grad})" stroke="#8d7fa3" stroke-width="1.5"/>']
    segs = []
    for (bx, by), L in zip(bases, lens):
        tx, ty = bx + dx * L, by + dy * L
        mx, my = (bx + tx) / 2 + px * 4, (by + ty) / 2 + py * 4
        segs.append((bx, by, mx, my, tx, ty))
    sh = "".join(f'<path d="M {n(b[0])} {n(b[1])} Q {n(b[2])} {n(b[3])} {n(b[4])} {n(b[5])}" '
                 f'stroke="#12000a" stroke-width="22" stroke-linecap="round" fill="none"/>' for b in segs)
    s.insert(0, f'<g transform="translate(7 9)" opacity="0.5" {blur(5)}>{sh}</g>')
    for b in reversed(segs):
        path = f"M {n(b[0])} {n(b[1])} Q {n(b[2])} {n(b[3])} {n(b[4])} {n(b[5])}"
        s.append(f'<path d="{path}" stroke="#8d7fa3" stroke-width="24.5" stroke-linecap="round" fill="none"/>')
        s.append(f'<path d="{path}" stroke="url(#{grad})" stroke-width="21" stroke-linecap="round" fill="none"/>')
        # highlight along the lit side
        hx_, hy_ = -px * light_side * 5, -py * light_side * 5
        s.append(f'<path d="M {n(b[0] + hx_)} {n(b[1] + hy_)} Q {n(b[2] + hx_)} {n(b[3] + hy_)} '
                 f'{n(b[4] + hx_ + dx * -6)} {n(b[5] + hy_ + dy * -6)}" stroke="#fff" stroke-width="3" '
                 f'stroke-linecap="round" fill="none" opacity="0.9"/>')
        # knuckle crease
        cx, cy = b[0] + (b[4] - b[0]) * 0.52, b[1] + (b[5] - b[1]) * 0.52
        s.append(f'<path d="M {n(cx - px * 7)} {n(cy - py * 7)} Q {n(cx + dx * 3)} {n(cy + dy * 3)} '
                 f'{n(cx + px * 7)} {n(cy + py * 7)}" stroke="#b5a8c6" stroke-width="1.4" fill="none"/>')
    return "".join(s)


NEAR_BACK = ("M 798 838 C 820 828 848 842 856 872 C 862 905 868 940 878 968 L 832 990 "
             "C 830 962 830 942 826 928 C 818 905 806 870 798 838 Z")
FAR_BACK = ("M 322 862 C 300 856 276 868 268 896 C 260 926 254 956 246 985 L 298 998 "
            "C 300 975 300 958 302 946 C 308 920 316 890 322 862 Z")
add(hand(NEAR_BACK, [(808, 845), (815, 872), (822, 898), (829, 922)], (-0.93, -0.36),
         [60, 68, 62, 50], "gGloveN", 1))
add('<path d="M 818 868 C 830 900 840 930 846 962 M 826 900 C 836 925 844 945 852 968" fill="none" '
    'stroke="#cfc4dc" stroke-width="1.2" stroke-dasharray="3 3"/>')
add(hand(FAR_BACK, [(318, 870), (312, 895), (306, 920), (300, 944)], (0.95, -0.3),
         [60, 68, 62, 48], "gGloveF", 1))
add('<path d="M 300 880 C 290 910 282 940 276 975 M 306 906 C 298 930 292 955 288 985" fill="none" '
    'stroke="#d8cfe2" stroke-width="1.2" stroke-dasharray="3 3"/>')


def frill(a, b, count, depth, thick):
    ax, ay = a
    bx, by = b
    ux, uy = norm(bx - ax, by - ay)
    nx, ny = uy, -ux                   # points "up" toward the hand
    if ny > 0:
        nx, ny = -nx, -ny
    pts_ = [f"M {n(ax)} {n(ay)}"]
    for i in range(count):
        t0, t1 = i / count, (i + 1) / count
        x1, y1 = ax + (bx - ax) * t1, ay + (by - ay) * t1
        mx, my = ax + (bx - ax) * (t0 + t1) / 2, ay + (by - ay) * (t0 + t1) / 2
        pts_.append(f"Q {n(mx + nx * depth * 2)} {n(my + ny * depth * 2)} {n(x1)} {n(y1)}")
    pts_.append(f"L {n(bx - nx * thick)} {n(by - ny * thick)} L {n(ax - nx * thick)} {n(ay - ny * thick)} Z")
    d = " ".join(pts_)
    lines = []
    for i in range(1, count):
        t = i / count
        x, y = ax + (bx - ax) * t, ay + (by - ay) * t
        lines.append(f"M {n(x)} {n(y)} L {n(x - nx * thick * 0.8)} {n(y - ny * thick * 0.8)}")
    return (f'<path d="{d}" fill="#fbf8fd" stroke="#a99bbb" stroke-width="1.2"/>'
            f'<path d="{" ".join(lines)}" stroke="#c5b9d3" stroke-width="1.2"/>')


add(frill((812, 993), (894, 958), 6, 7, 16))
add(frill((236, 984), (306, 1002), 5, 7, 16))

# ---- particles rising from the book ------------------------------------
SUITS = ["♦", "♠", "♥", "♣", "✦"]
for _ in range(42):
    x = random.uniform(330, 800)
    y = random.uniform(360, 628) if random.random() < 0.7 else random.uniform(150, 360)
    if in_ellipse(x, y, 712, 598, 105, 70) or in_ellipse(x, y, 480, 450, 90, 110):
        continue
    if in_ellipse(x, y, 655, 470, 215, 190):          # keep the head itself clean
        continue
    hgt = (640 - y) / 480
    op = max(0.25, 0.95 - hgt * 0.7)
    r = max(2.5, 9 - hgt * 6) * random.uniform(0.6, 1.2)
    k = random.random()
    if k < 0.55:
        add(star4(x, y, r, random.choice([GOLD_L, "#fff", "#ffd27c"]), op, 'filter="url(#glow)"'))
    elif k < 0.8:
        add(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r * 0.3)}" fill="#ffe6a8" opacity="{op:.2f}" '
            f'filter="url(#glow)"/>')
    else:
        add(f'<text x="{n(x)}" y="{n(y)}" font-family="DejaVu Sans" font-size="{n(r * 2.4)}" '
            f'fill="{random.choice([GOLD, "#ff6d8a"])}" opacity="{op:.2f}" text-anchor="middle" '
            f'filter="url(#glow)" transform="rotate({random.uniform(-25, 25):.0f} {n(x)} {n(y)})">'
            f'{random.choice(SUITS)}</text>')
# "kira" glint beside the glancing eye
add(star4(793, 553, 17, "#fff", 0.95, 'filter="url(#glowBig)"', k=0.1))
add(star4(814, 532, 7, GOLD_L, 0.9, 'filter="url(#glow)"'))

add('</g>')  # end character


# ==========================================================================
# 3. FOREGROUND + GRADING
# ==========================================================================
for _ in range(60):
    x, y = random.uniform(0, W), random.uniform(60, H)
    if in_ellipse(x, y, 660, 520, 240, 270):
        continue
    edge = x < 260 or x > 960 or y > 1260
    if edge and random.random() < 0.45:
        add(confetti(x, y, random.uniform(16, 28), random.uniform(0, 180), random.choice(CONF_COLORS),
                     random.uniform(0.55, 0.85), b=random.choice([3, 4, 5])))
    else:
        add(confetti(x, y, random.uniform(7, 13), random.uniform(0, 180), random.choice(CONF_COLORS),
                     random.uniform(0.6, 0.95)))
add(card(118, 1340, 150, 214, -24, b=5, op=0.92))
add(card(1100, 1200, 118, 168, 22, b=4, op=0.88))

add(f'<rect width="{W}" height="{H}" fill="url(#gKey)" style="mix-blend-mode:screen"/>')
add(f'<rect width="{W}" height="{H}" fill="url(#gRimAmb)" style="mix-blend-mode:screen"/>')
add(f'<rect width="{W}" height="{H}" fill="url(#gBottom)"/>')
add(f'<rect width="{W}" height="{H}" fill="url(#gVig)"/>')
add(f'<rect width="{W}" height="{H}" filter="url(#fGrain)" opacity="0.07" style="mix-blend-mode:overlay"/>')

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
       f'<title>Peek - a masked jester of Elation glancing over a book</title>'
       f'<defs>{"".join(defs)}</defs>{"".join(out)}</svg>')
with open(os.path.join(HERE, "peek.svg"), "w", encoding="utf-8") as fh:
    fh.write(svg)
print(f"wrote peek.svg ({len(svg) / 1024:.0f} KB)")
