// Key-light visibility (cast shadows) for the far shading (glsl/far.js farLight): the twilight key comes from the
// bright sky at az 110, ~15 deg up (far.js K); a ridge that rises above that line toward the key shades everything
// behind it - the ranges' big shadowed valleys and the lee faces beyond the crests (the 'stronger 3D effect with
// shadows and light'). Soft (a penumbra of ~7 deg: a patch of sky, not a sun disc).
// Occluders: L1 within +-25 km (31 m), L0 beyond (312 m). Earth curvature included.
// usage: node tools/farkey.mjs   -> data/terrain/L1.key, LF.key (uint8 per vertex, 255 = lit)
import fs from 'node:fs';

const OUT = 'data/terrain';
const meta = JSON.parse(fs.readFileSync(`${OUT}/meta.json`, 'utf8'));
const EARTH_R = meta.EARTH_R;
const rd = (f, T) => new T(fs.readFileSync(`${OUT}/${f}`).buffer.slice(0));
const L0 = meta.LEVELS[0], L1 = meta.LEVELS[1];
const H0 = rd('L0.f32', Float32Array), H1 = rd('L1.f32', Float32Array);
const grid = (lv, H) => ({ H, g: lv.grid, s: lv.size / (lv.grid - 1), h: lv.size / 2 });
const G0 = grid(L0, H0), G1 = grid(L1, H1);
const bil = (G, x, z) => {
  const fx = (x + G.h) / G.s, fz = (z + G.h) / G.s;
  if (fx < 0 || fz < 0 || fx >= G.g - 1 || fz >= G.g - 1) return -1e4;
  const i = Math.floor(fx), j = Math.floor(fz), u = fx - i, w = fz - j, k = j * G.g + i;
  return (G.H[k] * (1 - u) + G.H[k + 1] * u) * (1 - w) + (G.H[k + G.g] * (1 - u) + G.H[k + G.g + 1] * u) * w;
};
const hAt = (x, z) => (Math.abs(x) < G1.h - 1 && Math.abs(z) < G1.h - 1 ? bil(G1, x, z) : bil(G0, x, z));
const K = [0.908, 0.259, 0.330], kh = Math.hypot(K[0], K[2]), dir = [K[0] / kh, K[2] / kh], tanK = K[1] / kh;
const smoothstep = (a, b, x) => { const t = Math.min(1, Math.max(0, (x - a) / (b - a))); return t * t * (3 - 2 * t); };
const keyVis = (x, z, h0, d0) => {
  let maxT = -10, d = d0;
  while (d < 16000) {
    const t = (hAt(x + dir[0] * d, z + dir[1] * d) - h0 - d * d / (2 * EARTH_R)) / d;
    if (t > maxT) maxT = t;
    d = d * 1.06 + 8;
  }
  // angle of the key above the horizon toward it (rad): lit above ~+4 deg, dark below ~-3 deg
  const a = Math.atan(tanK) - Math.atan(maxT);
  return Math.round(255 * smoothstep(-0.05, 0.07, a));
};
const t0 = Date.now();
{
  const N = G1.g * G1.g, out = new Uint8Array(N);
  for (let j = 0; j < G1.g; j++) for (let i = 0; i < G1.g; i++) {
    const k = j * G1.g + i;
    out[k] = keyVis(-G1.h + i * G1.s, -G1.h + j * G1.s, H1[k] + 2, G1.s);
  }
  fs.writeFileSync(`${OUT}/L1.key`, out);
  let lit = 0; for (const v of out) lit += v; console.log(`L1.key ${((Date.now() - t0) / 1000).toFixed(1)} s, mean ${(lit / N / 255).toFixed(2)}`);
}
if (meta.FAR) {
  const XZ = rd('LF.xz', Float32Array), H = rd('LF.f32', Float32Array), N = H.length, out = new Uint8Array(N);
  for (let v = 0; v < N; v++) {
    const x = XZ[v * 2], z = XZ[v * 2 + 1];
    out[v] = keyVis(x, z, H[v] + 2, Math.max(60, Math.hypot(x, z) * 1e-3));
  }
  fs.writeFileSync(`${OUT}/LF.key.tmp`, out);
  fs.renameSync(`${OUT}/LF.key.tmp`, `${OUT}/LF.key`);
  let lit = 0; for (const v of out) lit += v; console.log(`LF.key ${((Date.now() - t0) / 1000).toFixed(1)} s, mean ${(lit / N / 255).toFixed(2)}`);
}
