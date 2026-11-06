// Summit / crest pass on L1's outer band (12.3-24.9 km from the ring, 31 m cells: the Eiger .. Schreckhorn group):
// the DEM rounds the summits into ~300 m domes and the crests into smooth arcs (critique of round 8 pass 1: fL's
// main summit a 45-50 px flat top, the front-range crest a chain of smooth arcs; refs: pointed pyramids, spires
// every 10-20 px). Two continuous terms, high ground only (no step anywhere, valleys and the lights untouched):
//  - a positive-only unsharp mask at ~140 m (h - blur, clipped at 0) raises summits and crest lines over their
//    flanks: the domes turn into peaked tops, the aretes into sharper ridges;
//  - a crest serration (value noise ~95 / 150 m) on the convex crests above ~2400 m: notches and spires.
// Tapered to zero at LM's edge (12 km; its seam band blends to L1's surface there) and at L1's edge (25 km: LF's first
// ring is L1's edge vertices), so both seams stay closed.
// usage: node tools/farsummit.mjs [--a 0.6] [--serr 24]   (reads L1.f32, writes L1.sum.f32 and meta.json SUMMIT)
import fs from 'node:fs';
const OUT = 'data/terrain';
const arg = (k, d) => { const i = process.argv.indexOf(k); return i > 0 ? +process.argv[i + 1] : d; };
const A = arg('--a', 0.8), SERR = arg('--serr', 24);
const meta = JSON.parse(fs.readFileSync(`${OUT}/meta.json`, 'utf8'));
const L1 = meta.LEVELS[1], g = L1.grid, step = L1.size / (g - 1), half = L1.size / 2;
const H = new Float32Array(fs.readFileSync(`${OUT}/L1.f32`).buffer.slice(0));
if (H.length !== g * g) throw new Error('L1 size');
// separable box blur (radius r cells), clamped at the edges
function box(a, r) {
  const o = new Float32Array(a.length), t = new Float32Array(a.length);
  for (let j = 0; j < g; j++) {
    let s = 0;
    for (let i = -r; i <= r; i++) s += a[j * g + Math.min(g - 1, Math.max(0, i))];
    for (let i = 0; i < g; i++) {
      t[j * g + i] = s / (2 * r + 1);
      s += a[j * g + Math.min(g - 1, i + r + 1)] - a[j * g + Math.max(0, i - r)];
    }
  }
  for (let i = 0; i < g; i++) {
    let s = 0;
    for (let j = -r; j <= r; j++) s += t[Math.min(g - 1, Math.max(0, j)) * g + i];
    for (let j = 0; j < g; j++) {
      o[j * g + i] = s / (2 * r + 1);
      s += t[Math.min(g - 1, j + r + 1) * g + i] - t[Math.max(0, j - r) * g + i];
    }
  }
  return o;
}
const gauss = (a, r) => box(box(box(a, r), r), r);
const B140 = gauss(H, 4);   // sigma ~4.5 cells ~140 m
const B75 = gauss(H, 2);    // sigma ~2.4 cells ~75 m
// value noise (smooth, world-anchored)
const hash = (i, j) => { let h = Math.imul(i, 374761393) + Math.imul(j, 668265263) | 0; h = Math.imul(h ^ (h >>> 13), 1274126177); return ((h ^ (h >>> 16)) >>> 0) / 4294967296; };
const vn = (x, z) => {
  const i = Math.floor(x), j = Math.floor(z), u = x - i, v = z - j, su = u * u * (3 - 2 * u), sv = v * v * (3 - 2 * v);
  const a = hash(i, j), b = hash(i + 1, j), c = hash(i, j + 1), d = hash(i + 1, j + 1);
  return a + (b - a) * su + (c - a) * sv + (a - b - c + d) * su * sv;
};
const ss = (e0, e1, x) => { const t = Math.min(1, Math.max(0, (x - e0) / (e1 - e0))); return t * t * (3 - 2 * t); };
const O = new Float32Array(H);
let n = 0, maxUp = 0, maxD = 0;
for (let j = 0; j < g; j++) for (let i = 0; i < g; i++) {
  const x = -half + i * step, z = -half + j * step, k = j * g + i, h = H[k];
  const e = Math.max(Math.abs(x), Math.abs(z));
  const w = ss(12300, 13300, e) * (1 - ss(24000, 24900, e)) * ss(2100, 2700, h);
  if (w <= 0) continue;
  // (soft cap: ~30 m on a 50 m dome, ~70 m at most on the steepest pyramids - the real heights stay recognisable)
  const up0 = Math.max(h - B140[k], 0), up = up0 / (1 + up0 / 160);
  const crest = ss(4, 25, h - B75[k]) * ss(2400, 3000, h);
  const serr = SERR * ((vn(x / 95, z / 95) - 0.5) + 0.5 * (vn(x / 150 + 7.3, z / 150 + 3.1) - 0.5));
  const dh = w * (A * up + crest * serr);
  O[k] = h + dh;
  n++; maxUp = Math.max(maxUp, w * A * up); maxD = Math.max(maxD, Math.abs(dh));
}
// seam check: L1's edge and LM's footprint unchanged
let edge = 0, inner = 0;
for (let j = 0; j < g; j++) for (let i = 0; i < g; i++) {
  const k = j * g + i, x = -half + i * step, z = -half + j * step;
  if (i === 0 || j === 0 || i === g - 1 || j === g - 1) edge = Math.max(edge, Math.abs(O[k] - H[k]));
  if (Math.max(Math.abs(x), Math.abs(z)) <= 12100) inner = Math.max(inner, Math.abs(O[k] - H[k]));
}
fs.writeFileSync(`${OUT}/L1.sum.f32`, Buffer.from(O.buffer));
console.log(`L1.sum.f32: ${n} cells changed, max raise ${maxUp.toFixed(1)} m, max |dh| ${maxD.toFixed(1)} m; seam check edge ${edge} inner ${inner}`);

// ---------------------------------------------------------------- LF (polar, tools/fardem.mjs), --lf
// The same two terms on the rings beyond ~26 km (ring 0 is L1's edge: untouched; faded in over 26-28.5 km), the blur
// as a plus-shaped Gaussian along / across the rings (the cells are near square: radial step ~ tangential), the
// serration faded where the cells pass ~45 m (beyond ~45 km its 95 m noise would alias). Normals recomputed as
// fardem.mjs does (tangent along the ring x across the rings). Writes LF.sum.f32 / LF.sum.nrm (LF.attr / LF.key
// kept: sky visibility and the cast shadows move little).
let lf = false;
if (process.argv.includes('--lf')) {
  const RS = meta.FAR.rings, NV = meta.FAR.count;
  const XZ = new Float32Array(fs.readFileSync(`${OUT}/LF.xz`).buffer.slice(0));
  const HF = new Float32Array(fs.readFileSync(`${OUT}/LF.f32`).buffer.slice(0));
  if (HF.length !== NV) throw new Error('LF size');
  const V0 = [];
  { let v = 0; for (const s of RS) { V0.push(v); v += s; } }
  const NR = RS.length;
  const P0 = (A, j, u) => {
    j = Math.min(NR - 1, Math.max(0, j));
    const f = (((u % 1) + 1) % 1) * RS[j], k = Math.floor(f), t = f - k, a = V0[j] + k, b = V0[j] + (k + 1) % RS[j];
    return A[a] + (A[b] - A[a]) * t;
  };
  const OF = new Float32Array(HF);
  let nf = 0, mf = 0;
  for (let j = 1; j < NR; j++) {
    const seg = RS[j];
    for (let k = 0; k < seg; k++) {
      const v = V0[j] + k, h = HF[v], x = XZ[v * 2], z = XZ[v * 2 + 1], r = Math.hypot(x, z);
      const w = ss(26000, 28500, r) * (1 - ss(110000, 120000, r)) * ss(2100, 2700, h);
      if (w <= 0) continue;
      const c = 2 * Math.PI * r / seg, u = k / seg;
      // plus-shaped Gaussian blurs (sigma 140 / 75 m)
      const blur = sig => {
        const D = Math.max(1, Math.min(8, Math.round(1.6 * sig / c)));
        let s = h, ws = 1;
        for (let d = 1; d <= D; d++) {
          const wd = Math.exp(-(d * c) * (d * c) / (2 * sig * sig));
          s += wd * (P0(HF, j, (k + d) / seg) + P0(HF, j, (k - d) / seg) + P0(HF, j + d, u) + P0(HF, j - d, u));
          ws += 4 * wd;
        }
        return s / ws;
      };
      const up0 = Math.max(h - blur(140), 0), up = up0 / (1 + up0 / 160);
      const crest = ss(4, 25, h - blur(75)) * ss(2400, 3000, h) * (1 - ss(30, 45, c));
      const serr = SERR * ((vn(x / 95, z / 95) - 0.5) + 0.5 * (vn(x / 150 + 7.3, z / 150 + 3.1) - 0.5));
      OF[v] = h + w * (A * up + crest * serr);
      nf++; mf = Math.max(mf, Math.abs(OF[v] - h));
    }
  }
  // normals of the new surface (as fardem.mjs)
  const NRM = new Int8Array(fs.readFileSync(`${OUT}/LF.nrm`).buffer.slice(0));
  const PX = (j, u, out) => {
    j = Math.min(NR - 1, Math.max(0, j));
    const f = (((u % 1) + 1) % 1) * RS[j], k = Math.floor(f), t = f - k, a = V0[j] + k, b = V0[j] + (k + 1) % RS[j];
    out[0] = XZ[a * 2] + (XZ[b * 2] - XZ[a * 2]) * t; out[2] = XZ[a * 2 + 1] + (XZ[b * 2 + 1] - XZ[a * 2 + 1]) * t;
    out[1] = OF[a] + (OF[b] - OF[a]) * t;
    return out;
  };
  const a = [0, 0, 0], b = [0, 0, 0], cc = [0, 0, 0], d = [0, 0, 0];
  let nn = 0;
  for (let j = 1; j < NR; j++) {
    const seg = RS[j];
    for (let k = 0; k < seg; k++) {
      const v = V0[j] + k;
      // only where the surface (or a neighbour) moved
      const near = Math.abs(OF[v] - HF[v]) > 0.01 || Math.abs(P0(OF, j + 1, k / seg) - P0(HF, j + 1, k / seg)) > 0.01
        || Math.abs(P0(OF, j - 1, k / seg) - P0(HF, j - 1, k / seg)) > 0.01 || Math.abs(OF[V0[j] + (k + 1) % seg] - HF[V0[j] + (k + 1) % seg]) > 0.01
        || Math.abs(OF[V0[j] + (k - 1 + seg) % seg] - HF[V0[j] + (k - 1 + seg) % seg]) > 0.01;
      if (!near) continue;
      const u = k / seg;
      PX(j, (k + 1) / seg, a); PX(j, (k - 1) / seg, b); PX(j + 1, u, cc); PX(j - 1, u, d);
      const tx = a[0] - b[0], ty = a[1] - b[1], tz = a[2] - b[2], rx = cc[0] - d[0], ry = cc[1] - d[1], rz = cc[2] - d[2];
      let nx = ry * tz - rz * ty, ny = rz * tx - rx * tz, nz = rx * ty - ry * tx;
      if (ny < 0) { nx = -nx; ny = -ny; nz = -nz; }
      const l = Math.hypot(nx, ny, nz) || 1;
      NRM[v * 3] = Math.round(nx / l * 127); NRM[v * 3 + 1] = Math.round(ny / l * 127); NRM[v * 3 + 2] = Math.round(nz / l * 127);
      nn++;
    }
  }
  let r0 = 0;
  for (let k = 0; k < RS[0]; k++) r0 = Math.max(r0, Math.abs(OF[k] - HF[k]));
  fs.writeFileSync(`${OUT}/LF.sum.f32`, Buffer.from(OF.buffer));
  fs.writeFileSync(`${OUT}/LF.sum.nrm`, Buffer.from(NRM.buffer));
  lf = true;
  console.log(`LF.sum.f32: ${nf} vertices changed (max |dh| ${mf.toFixed(1)} m), ${nn} normals redone; seam check ring 0 ${r0}`);
}
meta.SUMMIT = { file: 'L1.sum', lf, a: A, serr: SERR, note: 'summit / crest pass on L1\'s outer band (L1.sum.f32) and, if lf, on LF (LF.sum.f32 / LF.sum.nrm) (tools/farsummit.mjs); URL flag &nosum = without' };
fs.writeFileSync(`${OUT}/meta.json`, JSON.stringify(meta, null, 1));
