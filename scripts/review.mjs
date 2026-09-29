// Visual review: screenshots of key views on desktop and mobile into review/, plus basic runtime checks.
// Usage: npm run build, then node scripts/review.mjs (serves dist/ itself; APP_URL overrides).
import { mkdirSync } from 'node:fs';
import { readFile, stat } from 'node:fs/promises';
import { createServer } from 'node:http';
import { extname, join, normalize, resolve } from 'node:path';
import { chromium } from 'playwright-core';

const dist = resolve('dist');
const types = { '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'text/javascript', '.webp': 'image/webp', '.svg': 'image/svg+xml', '.woff2': 'font/woff2' };
const server = createServer(async (req, res) => {
  try {
    let file = normalize(join(dist, decodeURIComponent(new URL(req.url, 'http://x').pathname)));
    if (!file.startsWith(dist)) throw new Error('outside dist');
    if ((await stat(file).catch(() => null))?.isDirectory()) file = join(file, 'index.html');
    const body = await readFile(file);
    res.writeHead(200, { 'content-type': types[extname(file)] || 'application/octet-stream' });
    res.end(body);
  } catch {
    res.writeHead(404);
    res.end();
  }
});
await new Promise((ok) => server.listen(0, '127.0.0.1', ok));
const origin = process.env.APP_URL || `http://127.0.0.1:${server.address().port}`;
const out = 'review';
mkdirSync(out, { recursive: true });
const browser = await chromium.launch({ channel: 'msedge', headless: true });
const problems = [];

async function page(width, height, reduced = true) {
  const p = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: 1, reducedMotion: reduced ? 'reduce' : 'no-preference' });
  p.on('pageerror', (e) => problems.push(`${width}: ${e.message}`));
  p.on('console', (m) => { if (m.type() === 'error') problems.push(`${width}: ${m.text()}`); });
  return p;
}
const shot = (p, name, locator) => (locator ? p.locator(locator).first().screenshot({ path: `${out}/${name}.png` }) : p.screenshot({ path: `${out}/${name}.png` }));

for (const [label, w, h] of [['desktop', 1440, 900], ['mobile', 390, 844]]) {
  const p = await page(w, h);
  await p.goto(`${origin}/ru/`, { waitUntil: 'load' });
  await shot(p, `${label}-1-hero`);
  const overflow = await p.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  if (overflow > 0) problems.push(`${label}: horizontal overflow ${overflow}px`);
  for (const [name, sel] of [['2-profile', '.profile'], ['3-stage', '#stage-gmas'], ['4-stage-monche', '#stage-monchegorsk'], ['5-apps', '#app-rocksurv-field'], ['6-classifier', '#app-classifier'], ['7-achievements', '#achievements']]) {
    await p.locator(sel).scrollIntoViewIfNeeded();
    await p.waitForTimeout(500);
    await shot(p, `${label}-${name}`, sel);
  }
  // Carousel: next button, status text, thumbnails.
  const g = p.locator('#stage-gmas [data-gallery]');
  await g.scrollIntoViewIfNeeded();
  const totalPhotos = await g.locator('.gallery-slide').count();
  await g.locator('[data-next]').click();
  await p.waitForTimeout(700);
  const status = await g.locator('[data-status]').innerText();
  if (!new RegExp(`^2 из ${totalPhotos}`).test(status.trim())) problems.push(`${label}: carousel status after next = "${status}"`);
  // Lightbox.
  await g.locator('.gallery-slide.is-current a[data-zoom]').click();
  await p.waitForTimeout(900);
  if (!(await p.locator('dialog[data-lightbox]').evaluate((d) => d.open))) problems.push(`${label}: lightbox did not open`);
  await shot(p, `${label}-8-lightbox`);
  await p.keyboard.press('ArrowRight');
  await p.waitForTimeout(700);
  const lb = await p.locator('[data-lb-count]').innerText();
  if (!new RegExp(`^3 из ${totalPhotos}`).test(lb.trim())) problems.push(`${label}: lightbox count after ArrowRight = "${lb}"`);
  await p.keyboard.press('Escape');
  await p.waitForTimeout(700);
  if (await p.locator('dialog[data-lightbox]').evaluate((d) => d.open)) problems.push(`${label}: lightbox did not close`);
  const synced = await g.locator('[data-status]').innerText();
  if (!new RegExp(`^3 из ${totalPhotos}`).test(synced.trim())) problems.push(`${label}: carousel not synced after lightbox = "${synced}"`);
  // Every gallery frame keeps its photo's proportions: nothing cropped, nothing letterboxed.
  const skewed = await p.locator('.gallery-media').evaluateAll((nodes) =>
    nodes
      .filter((a) => {
        const box = a.getBoundingClientRect();
        const photo = Number(a.dataset.width) / Number(a.dataset.height);
        return Math.abs(box.width / box.height - photo) / photo > 0.015;
      })
      .map((a) => a.getAttribute('href')),
  );
  if (skewed.length) problems.push(`${label}: frames not in photo proportions: ${skewed.join(', ')}`);
  await p.close();

  const c = await page(w, h);
  await c.goto(`${origin}/ru/apps/classifier/`, { waitUntil: 'load' });
  await shot(c, `${label}-9-case`);
  await c.close();
}

// Full-screen viewer: landscape and portrait photos are whole on screen and fill the free stage.
for (const [w, h] of [[1440, 900], [1366, 657], [390, 844], [844, 390]]) {
  const v = await page(w, h);
  await v.goto(`${origin}/ru/`, { waitUntil: 'load' });
  const photoIndices = await v.evaluate(() => {
    const links = Array.from(document.querySelectorAll('#stage-gmas a[data-zoom]'));
    const landscapeIdx = links.findIndex((a) => Number(a.dataset.width) >= Number(a.dataset.height));
    const portraitIdx = links.findIndex((a) => Number(a.dataset.width) < Number(a.dataset.height));
    return [landscapeIdx >= 0 ? landscapeIdx : 0, portraitIdx >= 0 ? portraitIdx : 0];
  });
  for (const index of photoIndices) {
    await v.evaluate((i) => document.querySelectorAll('#stage-gmas a[data-zoom]')[i].click(), index);
    await v.waitForTimeout(700);
    const fit = await v.evaluate(() => {
      const img = document.querySelector('[data-lb-stage] img');
      const stageEl = document.querySelector('[data-lb-stage]');
      const stage = stageEl.getBoundingClientRect();
      const cs = getComputedStyle(stageEl);
      const width = stage.width - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight);
      const height = stage.height - parseFloat(cs.paddingTop) - parseFloat(cs.paddingBottom);
      const r = img.getBoundingClientRect();
      return {
        inside: r.top >= stage.top - 1 && r.bottom <= Math.min(stage.bottom, innerHeight) + 1 && r.left >= stage.left - 1 && r.right <= stage.right + 1,
        fills: Math.abs(r.width - width) < 2 || Math.abs(r.height - height) < 2,
        shown: `${Math.round(r.width)}x${Math.round(r.height)}`,
      };
    });
    if (!fit.inside || !fit.fills) problems.push(`${w}x${h}: lightbox photo ${index} not whole or not filling: ${JSON.stringify(fit)}`);
    await v.keyboard.press('Escape');
    await v.waitForTimeout(400);
  }
  await v.close();
}

// Motion on: first frame of the hero load sequence must not leave content hidden after it ends.
const m = await page(1440, 900, false);
await m.goto(`${origin}/ru/`, { waitUntil: 'load' });
await m.waitForTimeout(2200);
await shot(m, 'motion-hero');
await m.locator('#apps').scrollIntoViewIfNeeded();
await m.waitForTimeout(1200);
const scene = await m.locator('[data-header]').getAttribute('data-scene');
if (scene !== 'night') problems.push(`header scene over apps = ${scene}`);
await shot(m, 'motion-apps');
await m.close();

console.log(problems.length ? `PROBLEMS:\n${problems.join('\n')}` : 'All review checks passed');
server.close();
// Headless Edge on Windows sometimes never acknowledges close; report first and do not hang on it.
await Promise.race([browser.close(), new Promise((ok) => setTimeout(ok, 5000))]);
process.exit(problems.length ? 1 : 0);

