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
  '.woff2': 'font/woff2',
  '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  '.pdf': 'application/pdf',
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

try {
  console.log('1. Testing /en/ main page...');
  await page.goto(`${origin}/en/`, { waitUntil: 'load' });

  // Title and header check
  const title = await page.title();
  if (!title.includes('Alexey Pakhalko')) problems.push(`Wrong EN page title: ${title}`);

  const headerText = await page.locator('.site-header').innerText();
  if (!headerText.includes('Profile') || !headerText.includes('Experience') || !headerText.includes('Apps')) {
    problems.push('EN navigation links missing in header');
  }

  // Language switcher in header
  const activeLang = await page.locator('.lang-switch .is-active').innerText();
  if (activeLang.trim() !== 'EN') problems.push(`Expected active lang to be EN, got ${activeLang}`);
  const ruLink = page.locator('.lang-switch a[hreflang="ru"]');
  if (await ruLink.count() === 0) problems.push('RU link missing in lang switcher');
  const ruHref = await ruLink.getAttribute('href');
  if (ruHref !== '/ru/') problems.push(`RU link href expected /ru/, got ${ruHref}`);

  // CV download
  const cvLink = page.locator('a[download][href*="CV-EN"]');
  if (await cvLink.count() === 0) problems.push('EN CV download link missing');

  // Carousel check
  const g = page.locator('#stage-gmas [data-gallery]');
  await g.scrollIntoViewIfNeeded();
  const initialStatus = await g.locator('[data-status]').innerText();
  if (!initialStatus.includes('of')) problems.push(`Carousel status should use "of", got: "${initialStatus}"`);
  await g.locator('[data-next]').click();
  await page.waitForTimeout(500);
  const nextStatus = await g.locator('[data-status]').innerText();
  if (!nextStatus.startsWith('2 of')) problems.push(`Carousel status after next should be "2 of ...", got: "${nextStatus}"`);

  // Lightbox check
  await g.locator('.gallery-slide.is-current a[data-zoom]').click();
  await page.waitForTimeout(600);
  const lbStatus = await page.locator('[data-lb-count]').innerText();
  if (!lbStatus.includes('of')) problems.push(`Lightbox counter should use "of", got: "${lbStatus}"`);
  await page.locator('[data-lb-close]').click();
  await page.waitForTimeout(400);

  // App presentation links on /en/
  const fieldPresLink = page.locator('a[href="/en/presentations/field/"]');
  if (await fieldPresLink.count() === 0) problems.push('Field presentation link to /en/ missing on /en/ page');
  const classifierPresLink = page.locator('a[href="/en/presentations/classifier/"]');
  if (await classifierPresLink.count() === 0) problems.push('Classifier presentation link to /en/ missing on /en/ page');

  // 2. Testing /en/apps/rocksurv-field/
  console.log('2. Testing /en/apps/rocksurv-field/ ...');
  await page.goto(`${origin}/en/apps/rocksurv-field/`, { waitUntil: 'load' });
  const appTitle = await page.locator('h1').innerText();
  if (!appTitle.includes('Rocksurv Field')) problems.push(`App page h1 expected Rocksurv Field, got: ${appTitle}`);
  const appRuLink = await page.locator('.lang-switch a[hreflang="ru"]').getAttribute('href');
  if (appRuLink !== '/ru/apps/rocksurv-field/') problems.push(`App page RU switch href expected /ru/apps/rocksurv-field/, got ${appRuLink}`);
  const breadcrumb = await page.locator('.crumbs').innerText();
  if (!breadcrumb.includes('Home') || !breadcrumb.includes('Apps')) problems.push(`Breadcrumb not localized: ${breadcrumb}`);

  // 3. Testing /en/apps/classifier/
  console.log('3. Testing /en/apps/classifier/ ...');
  await page.goto(`${origin}/en/apps/classifier/`, { waitUntil: 'load' });
  const classTitle = await page.locator('h1').innerText();
  if (!classTitle.includes('Rocksurv Classifier')) problems.push(`App page h1 expected Rocksurv Classifier, got: ${classTitle}`);
  const classRuLink = await page.locator('.lang-switch a[hreflang="ru"]').getAttribute('href');
  if (classRuLink !== '/ru/apps/classifier/') problems.push(`Classifier RU switch expected /ru/apps/classifier/, got ${classRuLink}`);

  // 4. Testing /en/presentations/field/
  console.log('4. Testing /en/presentations/field/ ...');
  await page.goto(`${origin}/en/presentations/field/`, { waitUntil: 'load' });
  const activeDeck = await page.locator('.active-deck').getAttribute('id');
  if (activeDeck !== 'deck-en') problems.push(`Field presentation expected deck-en active, got: ${activeDeck}`);
  const backText = await page.locator('#back-link').innerText();
  if (!backText.includes('Back to CV')) problems.push(`Field presentation back button expected "Back to CV", got: "${backText}"`);

  // 5. Testing /en/presentations/classifier/
  console.log('5. Testing /en/presentations/classifier/ ...');
  await page.goto(`${origin}/en/presentations/classifier/`, { waitUntil: 'load' });
  const classBackText = await page.locator('#back-link').innerText();
  if (!classBackText.includes('Back to CV')) problems.push(`Classifier presentation back button expected "Back to CV", got: "${classBackText}"`);

  // 6. Testing root / redirect
  console.log('6. Testing root / entry point...');
  await page.goto(`${origin}/`, { waitUntil: 'load' });
  // By default in headless, navigator.language might be en-US -> should redirect to /en/
  await page.waitForTimeout(500);
  const finalUrl = page.url();
  console.log(`Root redirected to: ${finalUrl}`);
  if (!finalUrl.includes('/en/') && !finalUrl.includes('/ru/')) {
    problems.push(`Root / did not redirect to /en/ or /ru/, stayed at: ${finalUrl}`);
  }

} catch (err) {
  problems.push(`Test execution error: ${err.message}`);
}

if (problems.length > 0) {
  console.error('FAILURES:');
  problems.forEach(p => console.error(' - ' + p));
} else {
  console.log('ALL EN EDITION AND BILINGUAL ROUTING TESTS PASSED PERFECTLY!');
}

try { server.close(); } catch {}
// Headless Edge on Windows sometimes never acknowledges close; do not hang on it.
await Promise.race([browser.close(), new Promise((ok) => setTimeout(ok, 2000))]);
process.exit(problems.length ? 1 : 0);
