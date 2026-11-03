# Peek

An original fan-art reinterpretation inspired by Aha, the jester-masked Aeon of Elation in *Honkai: Star Rail*. A silver-haired jester reads a book held up in front of their face, then glances over it at the viewer with one eye.

Everything is drawn in code as a layered SVG. No game assets are used.

| File | What it is |
| --- | --- |
| `peek.png` | Final render, 2400×3000 |
| `peek.svg` | Vector source (scales to any size) |
| `generate.py` | Builds `peek.svg` |
| `render.js` | Renders the SVG to PNG with Playwright/Chromium |

```bash
python3 generate.py && node render.js
```
