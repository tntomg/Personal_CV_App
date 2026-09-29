import { createServer } from 'node:http';
import { readFile, stat } from 'node:fs/promises';
import { extname, join, normalize, resolve } from 'node:path';
import { chromium } from 'playwright-core';

const dist = resolve('dist');
const types = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css',
  '.js': 'text/javascript',
  '.webp': 'image/webp',
  '.svg': 'image/svg+xml',
  '.woff2': 'font/woff2'
};

const server = createServer(async (req, res) => {
  try {
    let pathname = decodeURIComponent(new URL(req.url, 'http://x').pathname);
    if (pathname === '/favicon.ico') pathname = '/favicon.svg';
    let file = normalize(join(dist, pathname));
    if (!file.startsWith(dist)) throw new Error('outside dist');
    if ((await stat(file).catch(() => null))?.isDirectory()) file = join(file, 'index.html');
    const body = await readFile(file);
    res.writeHead(200, { 'content-type': types[extname(file)] || 'application/octet-stream' });
    res.end(body);
  } catch {
    console.log('SERVER 404:', req.url);
    res.writeHead(404);
    res.end();
  }
});

await new Promise((ok) => server.listen(0, '127.0.0.1', ok));
const origin = `http://127.0.0.1:${server.address().port}`;
const browser = await chromium.launch({ channel: 'msedge', headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
const problems = [];

page.on('pageerror', (e) => problems.push(`PageError: ${e.message}`));
page.on('console', (m) => {
  if (m.type() === 'error') problems.push(`ConsoleError: ${m.text()}`);
});
page.on('response', (res) => {
  if (res.status() === 404) console.log('404 URL:', res.url());
});

try {
  // 1. Verify main page
  console.log('Testing /ru/ main page...');
  await page.goto(`${origin}/ru/`, { waitUntil: 'load' });

  // Verify no Kern app mentioned in apps
  const appsSection = await page.locator('#apps').innerText();
  if (appsSection.includes('Керн и горные выработки') || appsSection.includes('03\nКерн') || appsSection.includes('Описание выработок')) {
    problems.push('Kern application still mentioned in #apps section');
  }

  // Verify presentation buttons on main page
  const fieldPresBtn = page.locator('a[href="/ru/presentations/field/"]');
  if (await fieldPresBtn.count() === 0) problems.push('Field presentation link missing on main page');

  const classPresBtn = page.locator('a[href="/ru/presentations/classifier/"]');
  if (await classPresBtn.count() === 0) problems.push('Classifier presentation link missing on main page');

  // 2. Test Field Presentation Mini-App
  console.log('Testing /ru/presentations/field/ ...');
  await page.goto(`${origin}/ru/presentations/field/`, { waitUntil: 'load' });

  let counter = await page.locator('#counter').innerText();
  if (counter.trim() !== '01 / 12') problems.push(`Initial counter expected "01 / 12", got "${counter}"`);

  // Click next slide
  await page.locator('#next').click();
  await page.waitForTimeout(300);
  counter = await page.locator('#counter').innerText();
  if (counter.trim() !== '02 / 12') problems.push(`After next, counter expected "02 / 12", got "${counter}"`);

  // Check language switcher
  const btnEn = page.locator('#btn-lang-en');
  await btnEn.click();
  await page.waitForTimeout(300);
  const activeDeckEn = await page.locator('#deck-en').evaluate(el => el.classList.contains('active-deck'));
  if (!activeDeckEn) problems.push('English deck was not activated on toggle click');

  const btnRu = page.locator('#btn-lang-ru');
  await btnRu.click();
  await page.waitForTimeout(300);
  const activeDeckRu = await page.locator('#deck-ru').evaluate(el => el.classList.contains('active-deck'));
  if (!activeDeckRu) problems.push('Russian deck was not reactivated on toggle click');

  // Test keyboard navigation
  await page.keyboard.press('ArrowRight');
  await page.waitForTimeout(300);
  counter = await page.locator('#counter').innerText();
  if (counter.trim() !== '03 / 12') problems.push(`After ArrowRight, counter expected "03 / 12", got "${counter}"`);

  // 3. Test Classifier Presentation Mini-App
  console.log('Testing /ru/presentations/classifier/ ...');
  await page.goto(`${origin}/ru/presentations/classifier/`, { waitUntil: 'load' });

  counter = await page.locator('#counter').innerText();
  if (counter.trim() !== '01 / 10') problems.push(`Classifier initial counter expected "01 / 10", got "${counter}"`);

  // Slide 2 has carousel with 4 states
  await page.locator('#next').click();
  await page.waitForTimeout(400);
  counter = await page.locator('#counter').innerText();
  if (counter.trim() !== '02 / 10') problems.push(`Classifier slide 2 counter expected "02 / 10", got "${counter}"`);

  const carouselItemCount = await page.locator('.slide.active .carousel-item').count();
  if (carouselItemCount !== 4) problems.push(`Expected 4 carousel items on slide 2, found ${carouselItemCount}`);

  // Test carousel next button
  const carouselBtnNext = page.locator('.slide.active .carousel-btn.next');
  if (await carouselBtnNext.count() > 0) {
    await carouselBtnNext.click();
    await page.waitForTimeout(300);
  }

  // 4. Test case detail pages
  console.log('Testing /ru/apps/rocksurv-field/ ...');
  await page.goto(`${origin}/ru/apps/rocksurv-field/`, { waitUntil: 'load' });
  const caseFieldPres = page.locator('a[href="/ru/presentations/field/"]');
  if (await caseFieldPres.count() === 0) problems.push('Presentation link missing on /ru/apps/rocksurv-field/');

  console.log('Testing /ru/apps/classifier/ ...');
  await page.goto(`${origin}/ru/apps/classifier/`, { waitUntil: 'load' });
  const caseClassPres = page.locator('a[href="/ru/presentations/classifier/"]');
  if (await caseClassPres.count() === 0) problems.push('Presentation link missing on /ru/apps/classifier/');

  if (problems.length > 0) {
    console.error('FAILURES:\n' + problems.join('\n'));
  } else {
    console.log('ALL PRESENTATION MINI-APP TESTS PASSED SUCCESSFULLY!');
  }
} catch (err) {
  console.error(`Test threw: ${err.message}\n${err.stack}`);
  problems.push(err.message);
} finally {
  server.close();
  await Promise.race([browser.close(), new Promise((ok) => setTimeout(ok, 2000))]);
  process.exit(problems.length ? 1 : 0);
}
