// Tileable 3D cloud noise volumes + 2D weather map.
// shape128.bin : 128^3 RGBA8  R = Perlin-Worley, G/B/A = Worley fbm at 2x/4x/8x frequency
// detail32.bin : 32^3  RGBA8  R/G/B = Worley at 1x/2x/4x frequency
// weather512.bin: 512^2 RGBA8 R = coverage, G = height variation, B = density variation
import fs from 'node:fs';
import { mulberry32 } from './noise.mjs';

fs.mkdirSync('data/noise', { recursive: true });
const rnd = mulberry32(99);

function makeWorley(cells, seed) {
  const r = mulberry32(seed);
  const pts = new Float32Array(cells * cells * cells * 3);
  for (let i = 0; i < pts.length; i++) pts[i] = r();
  return (x, y, z) => { // x,y,z in [0,1) tile space
    const fx = x * cells, fy = y * cells, fz = z * cells;
    const ix = Math.floor(fx), iy = Math.floor(fy), iz = Math.floor(fz);
    let md = 1e9;
    for (let dz = -1; dz <= 1; dz++) for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) {
      const cx = ix + dx, cy = iy + dy, cz = iz + dz;
      const wx = ((cx % cells) + cells) % cells, wy = ((cy % cells) + cells) % cells, wz = ((cz % cells) + cells) % cells;
      const k = ((wz * cells + wy) * cells + wx) * 3;
      const px = cx + pts[k] - fx, py = cy + pts[k + 1] - fy, pz = cz + pts[k + 2] - fz;
      const d = px * px + py * py + pz * pz;
      if (d < md) md = d;
    }
    return 1 - Math.min(1, Math.sqrt(md));
  };
}
// tileable gradient noise
function makePerlin(period, seed) {
  const r = mulberry32(seed);
  const G = new Float32Array(period * period * period * 3);
  for (let i = 0; i < period ** 3; i++) {
    let a = r() * 2 - 1, b = r() * 2 - 1, c = r() * 2 - 1; const l = Math.hypot(a, b, c) || 1;
    G[i * 3] = a / l; G[i * 3 + 1] = b / l; G[i * 3 + 2] = c / l;
  }
  const fade = t => t * t * t * (t * (t * 6 - 15) + 10);
  const g = (ix, iy, iz, x, y, z) => {
    const k = ((((iz % period) + period) % period * period + (((iy % period) + period) % period)) * period + (((ix % period) + period) % period)) * 3;
    return G[k] * x + G[k + 1] * y + G[k + 2] * z;
  };
  return (x, y, z) => {
    x *= period; y *= period; z *= period;
    const ix = Math.floor(x), iy = Math.floor(y), iz = Math.floor(z);
    const fx = x - ix, fy = y - iy, fz = z - iz, u = fade(fx), v = fade(fy), w = fade(fz);
    const l = (a, b, t) => a + (b - a) * t;
    return l(l(l(g(ix, iy, iz, fx, fy, fz), g(ix + 1, iy, iz, fx - 1, fy, fz), u), l(g(ix, iy + 1, iz, fx, fy - 1, fz), g(ix + 1, iy + 1, iz, fx - 1, fy - 1, fz), u), v),
      l(l(g(ix, iy, iz + 1, fx, fy, fz - 1), g(ix + 1, iy, iz + 1, fx - 1, fy, fz - 1), u), l(g(ix, iy + 1, iz + 1, fx, fy - 1, fz - 1), g(ix + 1, iy + 1, iz + 1, fx - 1, fy - 1, fz - 1), u), v), w);
  };
}
const remap = (v, a, b, c, d) => c + (v - a) / (b - a) * (d - c);
const clamp01 = v => Math.min(1, Math.max(0, v));

// ---- shape volume
{
  const N = 128, out = new Uint8Array(N * N * N * 4);
  const p1 = makePerlin(4, 1), p2 = makePerlin(8, 2), p3 = makePerlin(16, 3);
  const w1 = makeWorley(4, 11), w2 = makeWorley(8, 12), w3 = makeWorley(16, 13), w4 = makeWorley(32, 14);
  for (let z = 0; z < N; z++) {
    for (let y = 0; y < N; y++) for (let x = 0; x < N; x++) {
      const u = x / N, v = y / N, w = z / N;
      const perlin = clamp01((p1(u, v, w) * 0.6 + p2(u, v, w) * 0.28 + p3(u, v, w) * 0.12) * 0.9 + 0.5);
      const wf1 = w1(u, v, w) * 0.625 + w2(u, v, w) * 0.25 + w3(u, v, w) * 0.125;
      const pw = clamp01(remap(perlin, wf1 - 1, 1, 0, 1));
      const wf2 = w2(u, v, w) * 0.625 + w3(u, v, w) * 0.25 + w4(u, v, w) * 0.125;
      const wf3 = w3(u, v, w) * 0.75 + w4(u, v, w) * 0.25;
      const wf4 = w4(u, v, w);
      const k = ((z * N + y) * N + x) * 4;
      out[k] = pw * 255; out[k + 1] = wf2 * 255; out[k + 2] = wf3 * 255; out[k + 3] = wf4 * 255;
    }
    if (z % 32 === 0) console.log('shape', z);
  }
  fs.writeFileSync('data/noise/shape128.bin', out);
}
// ---- detail volume
{
  const N = 32, out = new Uint8Array(N * N * N * 4);
  const w1 = makeWorley(4, 21), w2 = makeWorley(8, 22), w3 = makeWorley(16, 23);
  for (let z = 0; z < N; z++) for (let y = 0; y < N; y++) for (let x = 0; x < N; x++) {
    const u = x / N, v = y / N, w = z / N;
    const k = ((z * N + y) * N + x) * 4;
    out[k] = w1(u, v, w) * 255; out[k + 1] = w2(u, v, w) * 255; out[k + 2] = w3(u, v, w) * 255; out[k + 3] = 255;
  }
  fs.writeFileSync('data/noise/detail32.bin', out);
}
// ---- weather map (tileable 2D fbm via 3D perlin on a torus-free trick: use z=0 slice of tileable perlin)
{
  const N = 512, out = new Uint8Array(N * N * 4);
  const a = makePerlin(4, 31), b = makePerlin(8, 32), c = makePerlin(16, 33), d = makePerlin(32, 34), e = makePerlin(6, 35);
  const wA = makeWorley(6, 41), wB = makeWorley(12, 42);
  for (let y = 0; y < N; y++) for (let x = 0; x < N; x++) {
    const u = x / N, v = y / N;
    const f = a(u, v, 0.3) * 0.5 + b(u, v, 0.3) * 0.25 + c(u, v, 0.3) * 0.15 + d(u, v, 0.3) * 0.1;
    const cell = wA(u, v, 0.5) * 0.6 + wB(u, v, 0.5) * 0.4;
    const cov = clamp01(0.5 + f * 1.25 + (cell - 0.5) * 0.45);
    const k = (y * N + x) * 4;
    out[k] = cov * 255;
    out[k + 1] = clamp01(0.5 + e(u, v, 0.7) * 1.2) * 255;
    out[k + 2] = clamp01(0.5 + c(u, v, 0.9) * 1.4) * 255;
    out[k + 3] = 255;
  }
  fs.writeFileSync('data/noise/weather512.bin', out);
}
console.log('done');
