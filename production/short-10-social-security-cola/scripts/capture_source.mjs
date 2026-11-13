import { chromium } from "playwright";
import fs from "node:fs/promises";

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 1500 }, deviceScaleFactor: 1 });
await page.goto("https://www.ssa.gov/news/en/press/releases/2026-10-14.html", { waitUntil: "domcontentloaded", timeout: 90000 });
await page.waitForTimeout(2500);
await fs.mkdir("compositions/assets", { recursive: true });
const main = page.locator("main").first();
if (await main.count()) {
  await main.screenshot({ path: "compositions/assets/ssa-official-proof.png", animations: "disabled", timeout: 30000 });
} else {
  await page.screenshot({ path: "compositions/assets/ssa-official-proof.png", fullPage: false });
}
await browser.close();
console.log("Captured official SSA source page screenshot.");
