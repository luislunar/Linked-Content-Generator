const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const c = await b.newContext({ viewport: { width: 640, height: 800 } });
  const p = await c.newPage();
  await p.goto(process.argv[2], { waitUntil: 'domcontentloaded', timeout: 60000 });
  await p.waitForSelector('[data-block-id], .notion-page-content, h1').catch(()=>{});
  await p.waitForTimeout(3000);
  const info = await p.evaluate(() => {
    const scrollers = [];
    document.querySelectorAll('*').forEach(el => {
      const s = getComputedStyle(el);
      if ((s.overflowY === 'auto' || s.overflowY === 'scroll') && el.scrollHeight > el.clientHeight + 10) {
        scrollers.push({ tag: el.tagName, cls: el.className?.toString().slice(0,80), sh: el.scrollHeight, ch: el.clientHeight });
      }
    });
    return {
      docHeight: document.documentElement.scrollHeight,
      bodyHeight: document.body.scrollHeight,
      winInner: window.innerHeight,
      scrollers: scrollers.slice(0, 10),
    };
  });
  console.log(JSON.stringify(info, null, 2));
  await b.close();
})();
