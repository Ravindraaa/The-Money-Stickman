import { chromium } from "playwright";
import fs from "node:fs/promises";

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 1100 }, deviceScaleFactor: 1 });
await fs.mkdir("compositions/assets", { recursive: true });

// Capture compact, genuine source-page evidence panels; these are cropped cards, not full-page screenshots.
const sources = [
  { url: "https://apnews.com/article/366d26ae1c60182caa2819bed76ab346", file: "proof-ap-mortgage-rate.png" },
  { url: "https://fortune.com/article/current-mortgage-rates-11-10-2026/", file: "proof-fortune-rate-table.png" },
  { url: "https://www.freddiemac.com/pmms", file: "proof-freddiemac-pmms.png" }
];
for (const source of sources) {
  try {
    await page.goto(source.url, { waitUntil: "domcontentloaded", timeout: 90000 });
    await page.waitForTimeout(1800);
    await page.screenshot({ path: `compositions/assets/${source.file}`, clip: { x: 0, y: 0, width: 1100, height: 560 }, animations: "disabled", timeout: 30000 });
    console.log(`Captured ${source.url}`);
  } catch (error) {
    console.log(`Could not capture ${source.url}: ${error.message}`);
  }
}
await browser.close();
