// Clouds round 5: tileable 128^3 RGBA8 volume data/noise/curl128.bin for the fine cloud relief.
//   R/G/B: curl of a 3-octave Perlin vector potential (divergence-free swirls for the curl-warped tendrils),
//          normalised to ~N(0,1) * 0.17 + 0.5
//   A    : billow Worley fbm (cells 8/16/32, seed independent of shape128) - a decorrelated relief octave
// Also prints the stats (mean/sd) of shape128 G and of curl128 A (used to normalise them in clouds.js).
// usage: node tools/noise_curl.mjs
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
function makeWorley(cells, seed) {
  const r = mulberry32(seed);
  const pts = new Float32Array(cells ** 3 * 3);
  for (let i = 0; i < pts.length; i++) pts[i] = r();
  return (x, y, z) => {
    const fx = x * cells, fy = y * cells, fz = z * cells;
    const ix = Math.floor(fx), iy = Math.floor(fy), iz = Math.floor(fz);
    let md = 1e9;
    for (let dz = -1; dz <= 1; dz++) for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) {
      const cx = ix + dx, cy = iy + dy, cz = iz + dz;
      const k = (((((cz % cells) + cells) % cells) * cells + (((cy % cells) + cells) % cells)) * cells + (((cx % cells) + cells) % cells)) * 3;
      const px = cx + pts[k] - fx, py = cy + pts[k + 1] - fy, pz = cz + pts[k + 2] - fz;
      md = Math.min(md, px * px + py * py + pz * pz);
    }
    return 1 - Math.min(1, Math.sqrt(md));
  };
}

// vector potential: 3 independent Perlin fbms (periods 4/8/16 in the tile)
const pot = [0, 1, 2].map(c => { const a = makePerlin(4, 71 + c * 7), b = makePerlin(8, 72 + c * 7), d = makePerlin(16, 73 + c * 7); return (x, y, z) => a(x, y, z) + 0.5 * b(x, y, z) + 0.25 * d(x, y, z); });
const P = [0, 1, 2].map(() => new Float32Array(N ** 3));
for (let z = 0; z < N; z++) for (let y = 0; y < N; y++) for (let x = 0; x < N; x++) {
  const i = (z * N + y) * N + x;
  for (let c = 0; c < 3; c++) P[c][i] = pot[c](x / N, y / N, z / N);
}
const at = (A, x, y, z) => A[((((z + N) % N) * N + ((y + N) % N)) * N) + ((x + N) % N)];
const curl = [new Float32Array(N ** 3), new Float32Array(N ** 3), new Float32Array(N ** 3)];
let ss = 0;
for (let z = 0; z < N; z++) for (let y = 0; y < N; y++) for (let x = 0; x < N; x++) {
  const i = (z * N + y) * N + x;
  const d = (A, ax) => (ax === 0 ? at(A, x + 1, y, z) - at(A, x - 1, y, z) : ax === 1 ? at(A, x, y + 1, z) - at(A, x, y - 1, z) : at(A, x, y, z + 1) - at(A, x, y, z - 1)) * 0.5;
  curl[0][i] = d(P[2], 1) - d(P[1], 2);
  curl[1][i] = d(P[0], 2) - d(P[2], 0);
  curl[2][i] = d(P[1], 0) - d(P[0], 1);
  ss += curl[0][i] ** 2 + curl[1][i] ** 2 + curl[2][i] ** 2;
}
const sd = Math.sqrt(ss / (3 * N ** 3));
const w1 = makeWorley(8, 91), w2 = makeWorley(16, 92), w3 = makeWorley(32, 93);
const out = new Uint8Array(N ** 3 * 4);
let wm = 0, wv = 0;
for (let z = 0; z < N; z++) {
  for (let y = 0; y < N; y++) for (let x = 0; x < N; x++) {
    const i = (z * N + y) * N + x, k = i * 4;
    for (let c = 0; c < 3; c++) out[k + c] = Math.max(0, Math.min(255, Math.round((0.5 + curl[c][i] / sd * 0.17) * 255)));
    const u = x / N, v = y / N, w = z / N;
    const wf = w1(u, v, w) * 0.55 + w2(u, v, w) * 0.3 + w3(u, v, w) * 0.15;
    out[k + 3] = Math.round(wf * 255); wm += wf; wv += wf * wf;
  }
  if (z % 32 === 0) console.log('curl', z);
}
wm /= N ** 3; console.log('curl128.a mean', wm.toFixed(4), 'sd', Math.sqrt(wv / N ** 3 - wm * wm).toFixed(4));
fs.writeFileSync('data/noise/curl128.bin', out);
// stats of shape128 channels (normalisation constants)
const sh = fs.readFileSync('data/noise/shape128.bin');
for (let c = 0; c < 4; c++) {
  let m = 0, v = 0; const n = sh.length / 4;
  for (let i = 0; i < n; i++) { const a = sh[i * 4 + c] / 255; m += a; v += a * a; }
  m /= n; console.log('shape128', 'rgba'[c], 'mean', m.toFixed(4), 'sd', Math.sqrt(v / n - m * m).toFixed(4));
}
