// Mid-distance level 'LM' (round 8): the ridges 4-12 km round the ring (Brienzer Grat, Augstmatthorn, the Faulhorn
// group across the lake, Hohgant / Schrattenfluh) at 15.6 m instead of L1's 31 m, with sub-DEM relief: the DEM has
// no detail below ~30 m (terrarium z13 here is an upsample), so from the hero distances its ridges drew straight
// 7-14 px polygon edges against the sky and the farther ranges. Adds: a mild unsharp mask (crests up, notches and
// gullies down) and ridged fall-line relief (spurs / gullies ~35-140 m, amplitude by slope, only above ~1100 m).
// Seams: vertices align with L1 (every 2nd) and with L2's edge polyline; both edge bands blend to L1's bilinear
// surface, which is what L1's and L2's edges already are (no cracks). Attributes: L1's (bilinear), concavity re-baked.
// usage: node tools/farmid.mjs   -> data/terrain/LM.{f32,attr}, meta.json MID, lights_dy.f32 (mid lights re-seated)
import fs from 'node:fs';

const OUT = 'data/terrain';
const meta = JSON.parse(fs.readFileSync(`${OUT}/meta.json`, 'utf8'));
const L1 = meta.LEVELS[1], g1 = L1.grid, s1 = L1.size / (g1 - 1), h1 = L1.size / 2;
const H1 = new Float32Array(fs.readFileSync(`${OUT}/L1.f32`).buffer.slice(0));
const A1 = new Uint8Array(fs.readFileSync(`${OUT}/L1.attr`));
const HALF = 12000, STEP = s1 / 2, IN = meta.LEVELS[2].size / 2;   // +-12 km at 15.625 m; L2 inside +-4 km
const G = Math.round(2 * HALF / STEP) + 1;
const smoothstep = (a, b, x) => { const t = Math.min(1, Math.max(0, (x - a) / (b - a))); return t * t * (3 - 2 * t); };

const l1bil = (A, x, z, stride = 1, c = 0) => {
  const fx = (x + h1) / s1, fz = (z + h1) / s1, i = Math.min(g1 - 2, Math.floor(fx)), j = Math.min(g1 - 2, Math.floor(fz)), u = fx - i, w = fz - j, k = j * g1 + i;
  return (A[k * stride + c] * (1 - u) + A[(k + 1) * stride + c] * u) * (1 - w) + (A[(k + g1) * stride + c] * (1 - u) + A[(k + g1 + 1) * stride + c] * u) * w;
};
const cr = t => { t = Math.abs(t); return t < 1 ? 1.5 * t ** 3 - 2.5 * t * t + 1 : t < 2 ? -0.5 * t ** 3 + 2.5 * t * t - 4 * t + 2 : 0; };
const l1cub = (x, z) => {
  const fx = (x + h1) / s1, fz = (z + h1) / s1, i = Math.floor(fx), j = Math.floor(fz), u = fx - i, w = fz - j;
  let acc = 0;
  for (let m = -1; m <= 2; m++) { let row = 0; for (let k = -1; k <= 2; k++) row += H1[(j + m) * g1 + i + k] * cr(k - u); acc += row * cr(m - w); }
  return acc;
};
// value noise (hash lattice, smooth) in 2D
const hash = (i, j) => { let h = (i * 374761393 + j * 668265263) | 0; h = Math.imul(h ^ (h >>> 13), 1274126177); return ((h ^ (h >>> 16)) >>> 0) / 4294967296; };
const vnoise = (x, y) => {
  const i = Math.floor(x), j = Math.floor(y), u = x - i, v = y - j, su = u * u * (3 - 2 * u), sv = v * v * (3 - 2 * v);
  const a = hash(i, j), b = hash(i + 1, j), c = hash(i, j + 1), d = hash(i + 1, j + 1);
  return a + (b - a) * su + (c - a) * sv + (a - b - c + d) * su * sv;
};

const N = G * G, base = new Float32Array(N), H = new Float32Array(N);
for (let j = 0; j < G; j++) for (let i = 0; i < G; i++) base[j * G + i] = l1cub(-HALF + i * STEP, -HALF + j * STEP);
// unsharp mask (box blur radius 4 cells = 62 m)
const blur = base.slice();
{
  const r = 4, t = new Float32Array(G);
  for (let pass = 0; pass < 2; pass++) for (let j = 0; j < G; j++) {
    for (let i = 0; i < G; i++) t[i] = pass === 0 ? blur[j * G + i] : blur[i * G + j];
    let s = 0, c = 0;
    for (let i = -r; i < G + r; i++) {
      if (i + r < G) { s += t[i + r]; c++; }
      if (i - r - 1 >= 0) { s -= t[i - r - 1]; c--; }
      if (i >= 0 && i < G) { if (pass === 0) blur[j * G + i] = s / c; else blur[i * G + j] = s / c; }
    }
  }
}
// fall-line ridged relief on 4 fixed directions (per-vertex frames would twist the pattern), blended by alignment
const DIRS = [0, 1, 2, 3].map(k => { const a = k * Math.PI / 4 + 0.3; return [Math.cos(a), Math.sin(a)]; });
// (a 35 m octave aliased into a hatch on the 15.6 m grid)
const OCT = [[160, 1.0], [80, 0.5]];
let dmax = 0;
for (let j = 0; j < G; j++) for (let i = 0; i < G; i++) {
  const k = j * G + i, x = -HALF + i * STEP, z = -HALF + j * STEP;
  // band weight: 0 on both edge bands (L1's bilinear surface there), 1 inside
  const e = Math.max(Math.abs(x), Math.abs(z));
  const w = smoothstep(IN, IN + 800, e) * (1 - smoothstep(HALF - 1000, HALF, e));
  const hb = l1bil(H1, x, z);
  if (w <= 0) { H[k] = hb; continue; }
  const ip = Math.min(G - 1, i + 1), im = Math.max(0, i - 1), jp = Math.min(G - 1, j + 1), jm = Math.max(0, j - 1);
  const gx = (base[j * G + ip] - base[j * G + im]) / ((ip - im) * STEP), gz = (base[jp * G + i] - base[jm * G + i]) / ((jp - jm) * STEP);
  const sl = Math.hypot(gx, gz), gd = sl > 1e-4 ? [gx / sl, gz / sl] : [1, 0];
  let d = 0, ws = 0;
  for (let q = 0; q < 4; q++) {
    const [dx, dz] = DIRS[q], wq = Math.abs(gd[0] * dx + gd[1] * dz) ** 4 + 1e-3;
    let dq = 0;
    for (const [lam, a] of OCT) {
      // across the fall line: lam; along it: 3.5 lam (gullies / spurs run downhill)
      const u = (x * -dz + z * dx) / lam, v = (x * dx + z * dz) / (3.5 * lam) + q * 7.1 + lam * 0.013;
      const n = vnoise(u + 0.6 * vnoise(u * 0.37 + 4.1, v * 1.3), v);
      const r = 1 - Math.abs(2 * n - 1);
      dq += a * (r * r - 0.4);
    }
    d += wq * dq; ws += wq;
  }
  d /= ws;
  // amplitude by slope and by convexity: the crests (silhouettes) get notches and towers every ~100 m along them
  const amp = 3 + 12 * smoothstep(0.25, 1.0, sl) + 10 * smoothstep(0, 15, base[k] - blur[k]);
  const altF = smoothstep(1050, 1600, base[k]);
  const sharp = Math.max(-40, Math.min(40, base[k] - blur[k])) * 0.8;
  const hd = base[k] + altF * (sharp + amp * d * 2.0);
  dmax = Math.max(dmax, Math.abs(hd - base[k]));
  H[k] = hb + (hd - hb) * w;
}
console.log(`LM ${G}x${G} (${N} vertices), step ${STEP} m, max detail ${dmax.toFixed(1)} m`);

// attributes: L1's sky / glow visibility and water (bilinear), concavity re-baked from the detailed surface
const ATTR = new Uint8Array(N * 4);
const at = (i, j) => H[Math.min(G - 1, Math.max(0, j)) * G + Math.min(G - 1, Math.max(0, i))];
for (let j = 0; j < G; j++) for (let i = 0; i < G; i++) {
  const k = j * G + i, x = -HALF + i * STEP, z = -HALF + j * STEP, h = H[k];
  let cv = 0;
  for (const [R, w] of [[2, 0.6], [6, 0.4]]) {
    const d = Math.round(R * 0.7071);
    const avg = (at(i + R, j) + at(i - R, j) + at(i, j + R) + at(i, j - R) + at(i + d, j + d) + at(i - d, j + d) + at(i + d, j - d) + at(i - d, j - d)) / 8;
    cv += w * (avg - h) / (R * STEP);
  }
  const e = Math.max(Math.abs(x), Math.abs(z)), w = smoothstep(IN, IN + 800, e) * (1 - smoothstep(HALF - 1000, HALF, e));
  const cv1 = l1bil(A1, x, z, 4, 3);
  ATTR[k * 4] = Math.round(l1bil(A1, x, z, 4, 0));
  ATTR[k * 4 + 1] = Math.round(l1bil(A1, x, z, 4, 1));
  ATTR[k * 4 + 2] = l1bil(A1, x, z, 4, 2) > 127 ? 255 : 0;
  ATTR[k * 4 + 3] = Math.round(cv1 + (Math.min(255, Math.max(1, 128 + cv * 160)) - cv1) * w);
}
fs.writeFileSync(`${OUT}/LM.f32`, Buffer.from(H.buffer));
fs.writeFileSync(`${OUT}/LM.attr`, Buffer.from(ATTR.buffer));

// lights inside LM (placed on L1's surface by tools/lights.mjs): add the detail's height change to lights_dy.f32
{
  const lights = new Float32Array(fs.readFileSync(`${OUT}/lights.f32`).buffer.slice(0));
  const f = `${OUT}/lights_dy.f32`;
  const dy = fs.existsSync(f) ? new Float32Array(fs.readFileSync(f).buffer.slice(0)) : new Float32Array(lights.length / 5);
  const base0 = fs.existsSync(`${OUT}/lights_dy.far.f32`) ? new Float32Array(fs.readFileSync(`${OUT}/lights_dy.far.f32`).buffer.slice(0)) : dy.slice();
  fs.writeFileSync(`${OUT}/lights_dy.far.f32`, Buffer.from(base0.buffer));   // (far part, so re-runs do not accumulate)
  let n = 0, mx = 0;
  for (let i = 0; i < dy.length; i++) {
    dy[i] = base0[i];
    const x = lights[i * 5], z = lights[i * 5 + 2];
    if (Math.max(Math.abs(x), Math.abs(z)) >= HALF || Math.max(Math.abs(x), Math.abs(z)) <= IN) continue;
    const fx = (x + HALF) / STEP, fz = (z + HALF) / STEP, ii = Math.min(G - 2, Math.floor(fx)), jj = Math.min(G - 2, Math.floor(fz)), u = fx - ii, w = fz - jj, k = jj * G + ii;
    const hm = (H[k] * (1 - u) + H[k + 1] * u) * (1 - w) + (H[k + G] * (1 - u) + H[k + G + 1] * u) * w;
    const d = hm - l1bil(H1, x, z);
    if (Math.abs(d) > 0.05) { dy[i] += d; n++; mx = Math.max(mx, Math.abs(d)); }
  }
  fs.writeFileSync(f, Buffer.from(dy.buffer));
  console.log(`mid lights re-seated: ${n}, max |dy| ${mx.toFixed(1)} m`);
}
meta.MID = { name: 'LM', x0: -HALF, z0: -HALF, nx: G, nz: G, step: STEP, note: 'mid level 4-12 km (tools/farmid.mjs): L1 + sub-DEM relief' };
fs.writeFileSync(`${OUT}/meta.json`, JSON.stringify(meta, null, 1));
console.log('done');
