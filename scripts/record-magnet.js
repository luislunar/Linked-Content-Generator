// record-magnet.js — open a Notion public URL, scroll down then up over ~5s, save as webm (640x800, 4:5 portrait).
// Playwright video records the whole context lifetime. We pin the scroll motion to the TAIL of the recording
// so ffmpeg's `-sseof -5.5` in overlay-text.sh captures the actual motion (not a static frame).
// Usage: node scripts/record-magnet.js <notion_url> <output_path>

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const WIDTH = 640;
const HEIGHT = 800;
const DOWN_MS = 3000;
const UP_MS = 2000;
const STEPS_DOWN = 30;
const STEPS_UP = 20;

(async () => {
  const [, , notionUrl, outputPath] = process.argv;
  if (!notionUrl || !outputPath) {
    console.error('usage: node record-magnet.js <notion_url> <output_path>');
    process.exit(2);
  }

  const tmpDir = path.join(path.dirname(outputPath), '.recording-tmp');
  fs.mkdirSync(tmpDir, { recursive: true });

  const browser = await chromium.launch();
  const context = await browser.newContext({
    viewport: { width: WIDTH, height: HEIGHT },
    deviceScaleFactor: 2,
    recordVideo: { dir: tmpDir, size: { width: WIDTH, height: HEIGHT } },
  });
  const page = await context.newPage();

  await page.goto(notionUrl, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForSelector('[data-block-id], .notion-page-content, h1', { timeout: 30000 }).catch(() => {});
  await page.waitForTimeout(2500);

  // Notion public pages scroll an INNER <div class="notion-scroller"> — not the window.
  // document.body height is fixed at viewport; the scroller has its own scrollTop/scrollHeight.
  const scrollerSelector = '.notion-scroller.vertical, .notion-scroller';
  await page.waitForSelector(scrollerSelector, { timeout: 5000 }).catch(() => {});

  const setScroll = async (y) =>
    page.evaluate(({ sel, y }) => {
      const el = document.querySelector(sel);
      if (el) el.scrollTop = y;
      else window.scrollTo(0, y);
    }, { sel: scrollerSelector, y });

  const getScrollable = () =>
    page.evaluate((sel) => {
      const el = document.querySelector(sel);
      if (el) return Math.max(0, el.scrollHeight - el.clientHeight);
      return Math.max(0, document.documentElement.scrollHeight - window.innerHeight);
    }, scrollerSelector);

  // Warm lazy-loaded blocks: bounce to bottom and back (gets trimmed by -sseof).
  let scrollable = await getScrollable();
  await setScroll(scrollable);
  await page.waitForTimeout(2000);
  await setScroll(0);
  await page.waitForTimeout(1000);

  scrollable = await getScrollable();

  // Down pass — top → bottom over DOWN_MS.
  for (let i = 1; i <= STEPS_DOWN; i++) {
    await setScroll(Math.round((scrollable * i) / STEPS_DOWN));
    await page.waitForTimeout(DOWN_MS / STEPS_DOWN);
  }
  // Up pass — bottom → top over UP_MS.
  for (let i = 1; i <= STEPS_UP; i++) {
    await setScroll(Math.round(scrollable * (1 - i / STEPS_UP)));
    await page.waitForTimeout(UP_MS / STEPS_UP);
  }
  await page.waitForTimeout(200);

  const video = page.video();
  if (!video) throw new Error('Playwright did not start a video recorder');
  await page.close();
  await video.saveAs(outputPath);
  await context.close();
  await browser.close();
  fs.rmSync(tmpDir, { recursive: true, force: true });
  const size = fs.statSync(outputPath).size;
  if (size < 1000) throw new Error(`output video is suspiciously small (${size} bytes)`);
  console.log(`${outputPath} (${size} bytes)`);
})().catch((err) => {
  console.error(err);
  process.exit(1);
});
