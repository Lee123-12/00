// Render peek.svg -> peek.png (2x) with the preinstalled Playwright Chromium.
// Usage: node render.js [scale]
const path = require('path');
const { chromium } = require('playwright');

(async () => {
  const scale = Number(process.argv[2] || 2);
  const browser = await chromium.launch();
  const page = await browser.newPage({
    viewport: { width: 1200, height: 1500 },
    deviceScaleFactor: scale,
  });
  await page.goto('file://' + path.join(__dirname, 'peek.svg'));
  await page.waitForTimeout(300);
  const out = path.join(__dirname, scale === 2 ? 'peek.png' : `peek@${scale}x.png`);
  await page.screenshot({ path: out, fullPage: false });
  await browser.close();
  console.log('wrote', out);
})();
