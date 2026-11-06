// Offline film render: deterministic timeline frames -> PNG sequence (resumable).
// usage: node tools/render.mjs --out out/frames --w 1920 --h 1080 --fps 30 --K 4 [--start 0 --end N] [--every 1] [--jpg]
import fs from 'node:fs';
import { launch } from './shot.mjs';
import { gpuRest } from './gpulock.mjs';

const arg = (k, d) => { const i = process.argv.indexOf('--' + k); return i > 0 ? process.argv[i + 1] : d; };
const flag = k => process.argv.includes('--' + k);
const out = arg('out', 'out/frames'), W = +arg('w', 1920), H = +arg('h', 1080), fps = +arg('fps', 30), K = +arg('K', 4);
const every = +arg('every', 1), jpg = flag('jpg'), shutter = +arg('shutter', 0.5);
fs.mkdirSync(out, { recursive: true });

const { browser, page } = await launch(W, H, process.env.Q || '');   // env Q: URL flags, e.g. '&noclouds'
const total = await page.evaluate(() => window.APP.TOTAL);
const nFrames = Math.round(total * fps);
const start = +arg('start', 0), end = Math.min(nFrames, +arg('end', nFrames));
console.log(`timeline ${total.toFixed(2)} s -> ${nFrames} frames; rendering ${start}..${end - 1} every ${every}, K=${K}`);
const t0 = Date.now();
let done = 0;
// --coarse N: render every N-th frame first (an early preview of every shot), then fill in the rest
// --times 2,15.5,40: only the frames at these film times (s), e.g. test frames of chosen shots
let list = [];
for (let f = start; f < end; f += every) list.push(f);
if (arg('times', null)) list = arg('times').split(',').map(t => Math.min(nFrames - 1, Math.round(+t * fps)));
const coarse = +arg('coarse', 0);
if (coarse) list.sort((a, b) => ((a % coarse !== 0) - (b % coarse !== 0)) || a - b);
for (const f of list) {
  const file = `${out}/f_${String(f).padStart(5, '0')}.${jpg ? 'jpg' : 'png'}`;
  if (fs.existsSync(file) && !flag('force')) continue;
  const tf = Date.now();
  const shot = await page.evaluate((t, o) => window.APP.renderFrame(t, o), f / fps, { K, shutter, fps });
  const url = await page.evaluate(j => window.APP.renderer.domElement.toDataURL(j ? 'image/jpeg' : 'image/png', 0.92), jpg);
  fs.writeFileSync(file, Buffer.from(url.split(',')[1], 'base64'));
  const ms = Date.now() - tf;
  await gpuRest(ms);
  done++;
  if (flag('times')) console.log(`f ${f} t ${(f / fps).toFixed(2)} [${shot}] ${ms} ms`);
  else if (done % 10 === 0 || f === start) {
    const el = (Date.now() - t0) / 1000, per = el / done, left = ((end - f) / every) * per;
    console.log(`frame ${f} [${shot}]  ${per.toFixed(2)} s/frame  eta ${(left / 60).toFixed(1)} min`);
  }
}
console.log('done', ((Date.now() - t0) / 1000).toFixed(0), 's');
await browser.close();
