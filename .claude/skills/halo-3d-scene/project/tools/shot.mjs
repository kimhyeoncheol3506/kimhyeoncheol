// Render reference-matched views headlessly and build side-by-side comparisons + color metric.
// usage: node tools/shot.mjs [views=1,2,...] [tag] [--w 1672 --h 941] [--keep-open]
import puppeteer from 'puppeteer-core';
import sharp from 'sharp';
import fs from 'node:fs';
import { acquireGpu, gpuRest } from './gpulock.mjs';

const args = process.argv.slice(2);
const views = (args[0] && !args[0].startsWith('--') ? args[0] : '2,3,4,7,8,9').split(',').map(Number);
const tag = args[1] && !args[1].startsWith('--') ? args[1] : 'cur';
const W = 1672, H = 941;
fs.mkdirSync('out/shots', { recursive: true });

export async function launch(w = W, h = H, extra = '') {
  // one headless renderer at a time on this machine (tools/gpulock.mjs); released when the browser closes
  const release = await acquireGpu(process.argv.slice(1, 3).join(' '));
  const browser = await puppeteer.launch({
    executablePath: process.env.CHROME || 'C:/Program Files/Google/Chrome/Application/chrome.exe',
    headless: 'new',
    protocolTimeout: 600000,
    args: [...(process.platform === 'win32' ? ['--use-angle=d3d11'] : (process.env.SOFT_GL ? ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--no-sandbox'] : [])), '--ignore-gpu-blocklist', '--enable-gpu-rasterization', '--disable-gpu-watchdog',
      '--disable-renderer-backgrounding', '--disable-background-timer-throttling', `--window-size=${w},${h}`],
  });
  const close = browser.close.bind(browser);
  browser.close = async () => { try { await close(); } finally { release(); } };
  browser.on('disconnected', release);
  const page = await browser.newPage();
  page.on('console', m => { const t = m.text(); if (!/Download the React DevTools/.test(t)) console.log('[page]', t.slice(0, 400)); });
  page.on('pageerror', e => console.log('[pageerror]', e.message.slice(0, 2000)));
  await page.setViewport({ width: w, height: h });
  const port = process.env.PORT || 5173;
  await page.goto(`http://localhost:${port}/?capture&w=${w}&h=${h}${extra}`, { waitUntil: 'load', timeout: 120000 });
  await page.waitForFunction('window.APP && window.APP.ready', { timeout: 120000 });
  await page.evaluate('window.APP.ready');
  const gpu = await page.evaluate(() => {
    const gl = window.APP.renderer.getContext(); const e = gl.getExtension('WEBGL_debug_renderer_info');
    return e ? gl.getParameter(e.UNMASKED_RENDERER_WEBGL) : 'unknown';
  });
  console.log('GPU:', gpu);
  return { browser, page };
}

function toLab([r, g, b]) {
  const f = c => { c /= 255; return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4; };
  const R = f(r), G = f(g), B = f(b);
  let X = (R * 0.4124 + G * 0.3576 + B * 0.1805) / 0.95047, Y = R * 0.2126 + G * 0.7152 + B * 0.0722, Z = (R * 0.0193 + G * 0.1192 + B * 0.9505) / 1.08883;
  const g3 = t => t > 0.008856 ? Math.cbrt(t) : 7.787 * t + 16 / 116;
  X = g3(X); Y = g3(Y); Z = g3(Z);
  return [116 * Y - 16, 500 * (X - Y), 200 * (Y - Z)];
}
export async function compare(refPath, renderPath, outPath) {
  const gw = 32, gh = 18;
  const a = await sharp(refPath).removeAlpha().resize(gw, gh, { fit: 'fill' }).raw().toBuffer();
  const b = await sharp(renderPath).removeAlpha().resize(gw, gh, { fit: 'fill' }).raw().toBuffer();
  let dE = 0, dL = 0;
  for (let i = 0; i < gw * gh; i++) {
    const la = toLab([a[i * 3], a[i * 3 + 1], a[i * 3 + 2]]), lb = toLab([b[i * 3], b[i * 3 + 1], b[i * 3 + 2]]);
    dE += Math.hypot(la[0] - lb[0], la[1] - lb[1], la[2] - lb[2]); dL += lb[0] - la[0];
  }
  dE /= gw * gh; dL /= gw * gh;
  // side by side (ref | render) at half size
  const hw = 836, hh = 470;
  const ra = await sharp(refPath).resize(hw, hh).png().toBuffer();
  const rb = await sharp(renderPath).resize(hw, hh).png().toBuffer();
  await sharp({ create: { width: hw * 2 + 6, height: hh, channels: 3, background: '#000' } })
    .composite([{ input: ra, left: 0, top: 0 }, { input: rb, left: hw + 6, top: 0 }]).png().toFile(outPath);
  return { dE: +dE.toFixed(2), dL: +dL.toFixed(2) };
}

if (process.argv[1].endsWith('shot.mjs')) {
  const { browser, page } = await launch(W, H, process.env.Q || ''); // Q='&noclouds' etc.
  const results = {};
  for (const v of views) {
    const t0 = Date.now();
    // env K>1: accumulate K jittered sub-frames (clean clouds / AA, like film frames)
    await page.evaluate((n, K) => {
      window.APP.setView(n); window.APP.render(10);
      if (K > 1 && window.APP.renderStill) window.APP.renderStill(10, K); else window.APP.render(10);
    }, v, +(process.env.K || 1));
    const url = await page.evaluate(() => window.APP.capture());
    await gpuRest(Date.now() - t0);
    const file = `out/shots/${tag}_v${v}.png`;
    fs.writeFileSync(file, Buffer.from(url.split(',')[1], 'base64'));
    const ref = `ref/${v}.webp`;   // the reference images are not in the public repo: no comparison without them
    const r = fs.existsSync(ref) ? await compare(ref, file, `out/shots/cmp_${tag}_v${v}.png`) : { dE: NaN, dL: NaN };
    results[v] = r;
    console.log(`view ${v}: ${Date.now() - t0} ms  dE=${r.dE} dL=${r.dL}`);
  }
  const avg = Object.values(results).reduce((s, r) => s + r.dE, 0) / views.length;
  console.log('mean dE', avg.toFixed(2));
  fs.writeFileSync(`out/shots/${tag}_metrics.json`, JSON.stringify(results, null, 1));
  await browser.close();
}
