// Automatic grade calibration: matches the Lab distributions (percentiles of L, a, b, chroma) of our renders
// to the references, which is insensitive to the (unavoidable) composition differences. Each view is rendered
// once, its HDR frame is snapshotted, and only tone + grade are re-run while a coordinate descent searches
// exposure / white balance / saturation / contrast / lift / warm highlights / shoulder.
// usage: node tools/gradetune.mjs [views=1,...,11] [tag]   (env PORT, Q)  -> prints params, writes out/shots/<tag>_vN.png
import sharp from 'sharp';
import fs from 'node:fs';
import { launch, compare } from './shot.mjs';

const args = process.argv.slice(2);
const views = (args[0] || '1,2,3,4,5,6,7,8,9,10,11').split(',').map(Number);
const tag = args[1] || 'grade';
const GW = 418, GH = 235;

// Lab histogram percentiles of an RGBA/RGB byte buffer (runs in node and in the page)
function labStats(px, ch) {
  const lin = c => { c /= 255; return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4; };
  const g3 = t => t > 0.008856 ? Math.cbrt(t) : 7.787 * t + 16 / 116;
  const N = 240, hL = new Float64Array(N), hA = new Float64Array(N), hB = new Float64Array(N), hC = new Float64Array(N);
  const n = px.length / ch;
  for (let i = 0; i < n; i++) {
    const R = lin(px[i * ch]), G = lin(px[i * ch + 1]), B = lin(px[i * ch + 2]);
    const X = g3((R * 0.4124 + G * 0.3576 + B * 0.1805) / 0.95047), Y = g3(R * 0.2126 + G * 0.7152 + B * 0.0722), Z = g3((R * 0.0193 + G * 0.1192 + B * 0.9505) / 1.08883);
    const L = 116 * Y - 16, a = 500 * (X - Y), b = 200 * (Y - Z);
    const bin = (v, lo, hi) => Math.max(0, Math.min(N - 1, Math.floor((v - lo) / (hi - lo) * N)));
    hL[bin(L, 0, 100)]++; hA[bin(a, -60, 60)]++; hB[bin(b, -60, 60)]++; hC[bin(Math.hypot(a, b), 0, 80)]++;
  }
  const pct = (h, lo, hi, qs) => {
    const out = []; let acc = 0, k = 0;
    for (let i = 0; i < N && k < qs.length; i++) { acc += h[i]; while (k < qs.length && acc >= qs[k] * n) { out.push(lo + (i + 0.5) / N * (hi - lo)); k++; } }
    while (out.length < qs.length) out.push(hi);
    return out;
  };
  return {
    L: pct(hL, 0, 100, [0.05, 0.25, 0.5, 0.75, 0.95, 0.99]),
    a: pct(hA, -60, 60, [0.1, 0.5, 0.9]),
    b: pct(hB, -60, 60, [0.1, 0.5, 0.9]),
    C: pct(hC, 0, 80, [0.25, 0.5, 0.9]),
  };
}
const W8 = { L: 1, a: 1.5, b: 1.5, C: 1 };
function loss(s, r) {
  let e = 0;
  for (const k of ['L', 'a', 'b', 'C']) s[k].forEach((v, i) => { e += W8[k] * (v - r[k][i]) ** 2; });
  return e;
}

// env MASK=<tag>: compare only the 3D part of the frame (matte weight out/shots/<tag>_vN_w.png below 0.5), since the
// matte background is the reference itself and is composited after the grade
const masks = {};
if (process.env.MASK) for (const v of views) {
  const m = await sharp(`out/shots/${process.env.MASK}_v${v}_w.png`).greyscale().resize(GW, GH, { fit: 'fill' }).raw().toBuffer();
  masks[v] = Array.from(m, x => (x < 128 ? 1 : 0));
}
const pick = (px, ch, m) => {
  if (!m) return px;
  const out = []; for (let i = 0; i < m.length; i++) if (m[i]) for (let c = 0; c < ch; c++) out.push(px[i * ch + c]);
  return out;
};
const refs = {};
for (const v of views) {
  const { data } = await sharp(`ref/${v}.webp`).removeAlpha().resize(GW, GH, { fit: 'fill' }).raw().toBuffer({ resolveWithObject: true });
  refs[v] = labStats(pick(data, 3, masks[v]), 3);
}

const { browser, page } = await launch(1672, 941, process.env.Q || '');
await page.evaluate(`window.labStats = ${labStats.toString()}; window.__pick = ${pick.toString()}`);
// the page reads its pixels back bottom row first: flip the masks to match
const flip = m => { const o = []; for (let y = GH - 1; y >= 0; y--) for (let x = 0; x < GW; x++) o.push(m[y * GW + x]); return o; };
await page.evaluate(m => { window.__masks = m; }, Object.fromEntries(Object.entries(masks).map(([v, m]) => [v, flip(m)])));
await page.evaluate(vs => {
  window.__snaps = {};
  for (const v of vs) { window.APP.setView(v); window.APP.render(10); window.APP.render(10); window.__snaps[v] = window.APP.snapHdr(); }
}, views);
const base = await page.evaluate(() => {
  const p = window.APP.post.params;
  return { exposure: p.exposure, wbR: p.wb.x, wbB: p.wb.z, saturation: p.saturation, contrast: p.contrast,
    liftR: p.lift.x, liftG: p.lift.y, liftB: p.lift.z, warmHi: p.warmHi, shoulder: p.shoulder, grain: p.grain };
});
const toPost = q => ({ exposure: q.exposure, wb: { x: q.wbR, y: 1, z: q.wbB }, saturation: q.saturation, contrast: q.contrast,
  lift: { x: q.liftR, y: q.liftG, z: q.liftB }, warmHi: q.warmHi, shoulder: q.shoulder });

async function evalAll(q) {
  const st = await page.evaluate((pp, vs, gw, gh) => {
    const out = {};
    for (const v of vs) out[v] = window.labStats(window.__pick(window.APP.regrade({ ...pp, grain: 0 }, window.__snaps[v], gw, gh), 4, window.__masks[v]), 4);
    return out;
  }, toPost(q), views, GW, GH);
  let e = 0; const per = {};
  for (const v of views) { per[v] = loss(st[v], refs[v]); e += per[v]; }
  return { e: e / views.length, per, st };
}

const RANGE = { exposure: [0.4, 2.5], wbR: [0.6, 1.5], wbB: [0.6, 1.6], saturation: [0.7, 1.7], contrast: [0.8, 1.4],
  liftR: [-0.05, 0.08], liftG: [-0.05, 0.08], liftB: [-0.05, 0.1], warmHi: [0, 0.15], shoulder: [0.2, 0.8] };
const STEP = { exposure: 0.15, wbR: 0.08, wbB: 0.08, saturation: 0.1, contrast: 0.05, liftR: 0.01, liftG: 0.01, liftB: 0.01, warmHi: 0.02, shoulder: 0.05 };
let cur = { ...base }, best = await evalAll(cur);
const start = best;
console.log('start loss', best.e.toFixed(1), JSON.stringify(cur));
for (let pass = 0; pass < 7; pass++) {
  let improved = false;
  for (const k of Object.keys(STEP)) {
    for (const dir of [1, -1]) {
      const q = { ...cur };
      q[k] = k === 'exposure' ? cur[k] * Math.exp(dir * STEP[k]) : cur[k] + dir * STEP[k];
      q[k] = Math.min(RANGE[k][1], Math.max(RANGE[k][0], q[k]));
      const r = await evalAll(q);
      if (r.e < best.e - 1e-3) { best = r; cur = q; improved = true; break; }
    }
  }
  console.log(`pass ${pass} loss ${best.e.toFixed(1)}`);
  if (!improved) for (const k in STEP) STEP[k] *= 0.5;
}
const fmt = s => `L50 ${s.L[2].toFixed(0)} L95 ${s.L[4].toFixed(0)} a50 ${s.a[1].toFixed(1)} b50 ${s.b[1].toFixed(1)} C50 ${s.C[1].toFixed(1)}`;
for (const v of views) console.log(`v${v}  ref ${fmt(refs[v])} | start ${fmt(start.st[v])} | tuned ${fmt(best.st[v])}  loss ${start.per[v].toFixed(0)} -> ${best.per[v].toFixed(0)}`);
console.log('BEST', JSON.stringify(Object.fromEntries(Object.entries(cur).map(([k, v]) => [k, +v.toFixed(4)]))));

// full-size captures with the tuned grade (grain restored)
let sum = 0;
for (const v of views) {
  const url = await page.evaluate((pp, v) => {
    Object.assign(window.APP.post.params, pp);
    window.APP.post.finish(window.__snaps[v], 10, null);
    return window.APP.capture();
  }, toPost(cur), v);
  const file = `out/shots/${tag}_v${v}.png`;
  fs.writeFileSync(file, Buffer.from(url.split(',')[1], 'base64'));
  const r = await compare(`ref/${v}.webp`, file, `out/shots/cmp_${tag}_v${v}.png`);
  sum += r.dE; console.log(`view ${v}: dE=${r.dE}`);
}
console.log('mean dE', (sum / views.length).toFixed(2));
await browser.close();
