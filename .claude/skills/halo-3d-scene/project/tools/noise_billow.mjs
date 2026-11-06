// Clouds round 8: tileable 128^3 RGBA8 volume data/noise/billow128.bin for the free-flight cloud relief.
//   R / G: billow fbm (1 - |Perlin|, periods 4/8/16/32 in the tile, gain 0.5): rounded rolls of every size with
//          sharp creases between them - the heaps of a cloud top (Worley fbm reads as equal round lumps: cauliflower)
//   B / A: Perlin fbm (periods 4/8/16/32 and 8/16/32): smooth multi-scale noise for wisps and density variation
// Each channel is normalised to mean 0.5, sd 0.17 (clamped 0..1).
// usage: node tools/noise_billow.mjs
import fs from 'node:fs';
import { mulberry32 } from './noise.mjs';

const N = 128;
function makePerlin(period, seed) {
  const r = mulberry32(seed);
  const G = new Float32Array(period ** 3 * 3);
  for (let i = 0; i < period ** 3; i++) {
    const a = r() * 2 - 1, b = r() * 2 - 1, c = r() * 2 - 1, l = Math.hypot(a, b, c) || 1;
    G[i * 3] = a / l; G[i * 3 + 1] = b / l; G[i * 3 + 2] = c / l;
  }
  const fade = t => t * t * t * (t * (t * 6 - 15) + 10);
  const w = i => ((i % period) + period) % period;
  const g = (ix, iy, iz, x, y, z) => { const k = ((w(iz) * period + w(iy)) * period + w(ix)) * 3; return G[k] * x + G[k + 1] * y + G[k + 2] * z; };
  const l = (a, b, t) => a + (b - a) * t;
  return (x, y, z) => {
    x *= period; y *= period; z *= period;
    const ix = Math.floor(x), iy = Math.floor(y), iz = Math.floor(z);
    const fx = x - ix, fy = y - iy, fz = z - iz, u = fade(fx), v = fade(fy), s = fade(fz);
    return l(l(l(g(ix, iy, iz, fx, fy, fz), g(ix + 1, iy, iz, fx - 1, fy, fz), u), l(g(ix, iy + 1, iz, fx, fy - 1, fz), g(ix + 1, iy + 1, iz, fx - 1, fy - 1, fz), u), v),
      l(l(g(ix, iy, iz + 1, fx, fy, fz - 1), g(ix + 1, iy, iz + 1, fx - 1, fy, fz - 1), u), l(g(ix, iy + 1, iz + 1, fx, fy - 1, fz - 1), g(ix + 1, iy + 1, iz + 1, fx - 1, fy - 1, fz - 1), u), v), s);
  };
}
const fbm = (periods, seed, billow) => {
  const P = periods.map((p, i) => makePerlin(p, seed + i * 13));
  return (x, y, z) => { let s = 0, a = 1; for (const p of P) { const v = p(x, y, z); s += a * (billow ? 1 - Math.abs(v) * 1.6 : v); a *= 0.5; } return s; };
};
const ch = [fbm([4, 8, 16, 32], 301, true), fbm([4, 8, 16, 32], 401, true), fbm([4, 8, 16, 32], 501, false), fbm([8, 16, 32], 601, false)];
const F = ch.map(() => new Float32Array(N ** 3));
for (let z = 0; z < N; z++) {
  for (let y = 0; y < N; y++) for (let x = 0; x < N; x++) {
    const i = (z * N + y) * N + x;
    for (let c = 0; c < 4; c++) F[c][i] = ch[c](x / N, y / N, z / N);
  }
  if (z % 32 === 0) console.log('billow', z);
}
const out = new Uint8Array(N ** 3 * 4);
for (let c = 0; c < 4; c++) {
  let m = 0, v = 0; const A = F[c];
  for (let i = 0; i < A.length; i++) { m += A[i]; v += A[i] * A[i]; }
  m /= A.length; const sd = Math.sqrt(v / A.length - m * m);
  for (let i = 0; i < A.length; i++) out[i * 4 + c] = Math.max(0, Math.min(255, Math.round((0.5 + (A[i] - m) / sd * 0.17) * 255)));
  console.log('billow128', 'rgba'[c], 'raw mean', m.toFixed(4), 'sd', sd.toFixed(4));
}
fs.writeFileSync('data/noise/billow128.bin', out);
