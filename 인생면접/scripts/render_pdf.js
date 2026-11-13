// HTML → PDF (Chromium). 사용법: node render_pdf.js in1.html out1.pdf [in2.html out2.pdf ...]
const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const pairs = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage();
  for (let i = 0; i < pairs.length; i += 2) {
    await page.goto('file://' + path.resolve(pairs[i]));
    await page.evaluate(() => document.fonts.ready);
    await page.pdf({ path: pairs[i + 1], format: 'A4', printBackground: true, preferCSSPageSize: true });
    console.log('wrote', pairs[i + 1]);
  }
  await browser.close();
})();
