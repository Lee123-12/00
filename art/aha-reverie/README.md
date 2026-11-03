# Reverie

A soft, pretty reinterpretation of Aha (*Honkai: Star Rail*). A silver-haired girl reads by warm window light in a quiet library, holds her book up, and glances over it at the viewer with one ruby eye. Roses, pearls and a small masquerade-mask hairpin stand in for the loud jester motifs.

Everything is drawn in code as a layered SVG. No game assets are used.

| File | What it is |
| --- | --- |
| `reverie.png` | Final render, 2400×3000 |
| `reverie.svg` | Vector source (scales to any size) |
| `generate.py` | Builds `reverie.svg` |
| `render.js` | Renders the SVG to PNG with Playwright/Chromium |

```bash
python3 generate.py && node render.js
```
