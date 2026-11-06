// Far terrain (round 8): replaces the 312 m L0 level with a ring-centred polar level 'LF' at the DEM's own resolution,
// from L1's square edge (+-25 km) out to ~240 km, and restores L1's outer band (it was blended into L0's 312 m
// heights over 21.5-25 km - right where the Eiger / Schreckhorn / Moench stand).
//   LF layout: rings at s_j (s_0 = 25 km, geometric growth), morphing from L1's square boundary (ring 0 = L1's 6400
//   edge vertices, so the seam is closed) to a circle by ~60 km; bands of 6400 / 3200 / 1600 segments (constant angular
//   resolution ~1e-3 rad = 2-3 px at 1920 px over 50 deg in the first band), stitched by transition strips (no
//   T-junctions). Heights: AWS terrarium z12 (~26 m) within ~60 km, z11 to ~120 km, z10 beyond.
// usage: node tools/fardem.mjs            -> data/terrain/LF.{xz,f32,nrm,attr}, meta.json FAR, L1.f32 (band restored,
//                                            old copy kept as L1.blend.f32), lights_dy.f32 (far lights re-seated)
import fs from 'node:fs';
import path from 'node:path';
import sharp from 'sharp';

const OUT = 'data/terrain', TILES = 'data/dem/tiles';
fs.mkdirSync(TILES, { recursive: true });
const meta = JSON.parse(fs.readFileSync(`${OUT}/meta.json`, 'utf8'));
const { lat0, lon0 } = meta.CENTER;
const EARTH_R = meta.EARTH_R;
const mPerDegLat = 111132.92 - 559.82 * Math.cos(2 * lat0 * Math.PI / 180);
const mPerDegLon = 111412.84 * Math.cos(lat0 * Math.PI / 180);
const smoothstep = (a, b, x) => { const t = Math.min(1, Math.max(0, (x - a) / (b - a))); return t * t * (3 - 2 * t); };

// ---------------------------------------------------------------- terrarium tiles -> sampler per zoom
const tiles = new Map();
async function loadTile(z, x, y) {
  const key = `${z}_${x}_${y}`;
  if (tiles.has(key)) return;
  const f = path.join(TILES, key + '.png');
  if (!fs.existsSync(f)) {
    for (let a = 0; ; a++) {
      try {
        const r = await fetch(`https://s3.amazonaws.com/elevation-tiles-prod/terrarium/${z}/${x}/${y}.png`);
        if (!r.ok) throw new Error('HTTP ' + r.status);
        fs.writeFileSync(f, Buffer.from(await r.arrayBuffer()));
        break;
      } catch (e) { if (a >= 4) throw e; await new Promise(r => setTimeout(r, 1500)); }
    }
  }
  const { data } = await sharp(f).removeAlpha().raw().toBuffer({ resolveWithObject: true });
  const h = new Float32Array(65536);
  for (let i = 0; i < 65536; i++) h[i] = data[i * 3] * 256 + data[i * 3 + 1] + data[i * 3 + 2] / 256 - 32768;
  tiles.set(key, h);
}
const toLL = (x, z) => [lat0 - z / mPerDegLat, lon0 + x / mPerDegLon];
function makeSampler(z, half) {
  const n = 2 ** z;
  const tx = lon => (lon + 180) / 360 * n;
  const ty = lat => { const r = lat * Math.PI / 180; return (1 - Math.log(Math.tan(r) + 1 / Math.cos(r)) / Math.PI) / 2 * n; };
  const [latN] = toLL(0, -half), [latS] = toLL(0, half), [, lonW] = toLL(-half, 0), [, lonE] = toLL(half, 0);
  const x0 = Math.floor(tx(lonW)), x1 = Math.floor(tx(lonE)), y0 = Math.floor(ty(latN)), y1 = Math.floor(ty(latS));
  const jobs = [];
  for (let y = y0; y <= y1; y++) for (let x = x0; x <= x1; x++) jobs.push([x, y]);
  const px = (gx, gy) => {
    const tX = Math.floor(gx / 256), tY = Math.floor(gy / 256);
    const t = tiles.get(`${z}_${tX}_${tY}`);
    return t ? t[(gy - tY * 256) * 256 + (gx - tX * 256)] : 0;
  };
  const cr = t => { t = Math.abs(t); return t < 1 ? 1.5 * t ** 3 - 2.5 * t * t + 1 : t < 2 ? -0.5 * t ** 3 + 2.5 * t * t - 4 * t + 2 : 0; };
  // bicubic (Catmull-Rom), as tools/demlib.mjs fetchGrid (L1 / L2 were resampled this way: identical values)
  const at = (x, zz) => {
    const [la, lo] = toLL(x, zz);
    const gx = tx(lo) * 256 - 0.5, gy = ty(la) * 256 - 0.5;
    const ix = Math.floor(gx), iy = Math.floor(gy), fx = gx - ix, fy = gy - iy;
    let acc = 0;
    for (let m = -1; m <= 2; m++) {
      let row = 0;
      for (let k = -1; k <= 2; k++) row += px(ix + k, iy + m) * cr(k - fx);
      acc += row * cr(m - fy);
    }
    return acc;
  };
  return {
    at, jobs, z,
    async load() {
      console.log(`  z${z}: ${jobs.length} tiles`);
      for (let i = 0; i < jobs.length; i += 24) await Promise.all(jobs.slice(i, i + 24).map(([x, y]) => loadTile(z, x, y)));
    },
  };
}

// ---------------------------------------------------------------- layout
const S0 = 25000;                  // L1 half size
const L1G = meta.LEVELS[1].grid;   // 1601
const NA = 4 * (L1G - 1);          // 6400 edge vertices of L1
// (band A in two radial densities: the Bernese Alps' main crest stands at 22-45 km)
const BANDS = [
  { seg: NA, q: 0.0016, s1: 45000 },
  { seg: NA, q: 0.0025, s1: 62000 },
  { seg: NA / 2, q: 0.005, s1: 125000 },
  { seg: NA / 4, q: 0.01, s1: 212000 },
];
const MORPH = [S0, 60000];
// point of the square loop (half size 1) at u in [0, 1): corner (1, -1), east edge to (1, 1), south edge, west, north
function sq(u) {
  const f = ((u % 1) + 1) % 1 * 4, side = Math.floor(f), t = f - side;
  const a = -1 + 2 * t;
  return side === 0 ? [1, a] : side === 1 ? [-a, 1] : side === 2 ? [-1, -a] : [a, -1];
}
function ringPoint(u, s) {
  const m = smoothstep(MORPH[0], MORPH[1], s);
  const [qx, qz] = sq(u);
  if (m <= 0) return [qx * s, qz * s];
  // angle: the square point's (unwrapped from the -45 deg corner) -> uniform; radius: square -> equal-area circle
  let phi = Math.atan2(qz, qx);
  const psi = -Math.PI / 4 + 2 * Math.PI * u;
  while (phi < psi - Math.PI) phi += 2 * Math.PI;
  while (phi > psi + Math.PI) phi -= 2 * Math.PI;
  const a = phi + (psi - phi) * m, r = Math.hypot(qx, qz) * s * (1 - m) + 1.1284 * s * m;
  return [Math.cos(a) * r, Math.sin(a) * r];
}
// rings: [{ s, seg, band }]
const rings = [];
{
  let s = S0;
  for (let b = 0; b < BANDS.length; b++) {
    const B = BANDS[b];
    while (s < B.s1) { rings.push({ s, seg: B.seg, band: b }); s *= 1 + B.q; }
  }
}
let N = 0;
for (const r of rings) { r.v0 = N; N += r.seg; }
console.log(`LF: ${rings.length} rings, ${N} vertices, outer s ${rings[rings.length - 1].s.toFixed(0)} m`);

// ---------------------------------------------------------------- main
const t0 = Date.now();
const z12 = makeSampler(12, 62000), z11 = makeSampler(11, 124000), z10 = makeSampler(10, 250000);
for (const smp of [z12, z11, z10]) await smp.load();
console.log(`tiles ${((Date.now() - t0) / 1000).toFixed(1)} s`);
const hAt = (x, z) => {
  const r = Math.hypot(x, z);
  if (r < 56000) return z12.at(x, z);
  if (r < 60000) { const w = (r - 56000) / 4000; return z12.at(x, z) * (1 - w) + z11.at(x, z) * w; }
  if (r < 116000) return z11.at(x, z);
  if (r < 124000) { const w = (r - 116000) / 8000; return z11.at(x, z) * (1 - w) + z10.at(x, z) * w; }
  return z10.at(x, z);
};

// L1: restore the outer band from its raw resample (keep the blended copy once)
const L1raw = new Float32Array(fs.readFileSync(`${OUT}/L1.raw.f32`).buffer.slice(0));
if (!fs.existsSync(`${OUT}/L1.blend.f32`)) fs.copyFileSync(`${OUT}/L1.f32`, `${OUT}/L1.blend.f32`);
const L1old = new Float32Array(fs.readFileSync(`${OUT}/L1.blend.f32`).buffer.slice(0));
// (--noswap: written as L1.new.f32 / meta.new.json, e.g. while a baseline render still has to load the old ones)
const SWAP = !process.argv.includes('--noswap');
fs.writeFileSync(SWAP ? `${OUT}/L1.f32` : `${OUT}/L1.new.f32`, Buffer.from(L1raw.buffer));
const L1step = 2 * S0 / (L1G - 1);
const L1attr = new Uint8Array(fs.readFileSync(`${OUT}/L1.attr`));
// L1 edge vertex index of loop position k (0..NA-1), as sq(): east edge (x = +S0) from z = -S0 first
function l1Edge(k) {
  const side = Math.floor(k / (L1G - 1)), t = k % (L1G - 1), g = L1G - 1;
  const [i, j] = side === 0 ? [g, t] : side === 1 ? [g - t, g] : side === 2 ? [0, g - t] : [t, 0];
  return j * L1G + i;
}

const XZ = new Float32Array(N * 2), H = new Float32Array(N), NRM = new Int8Array(N * 3), ATTR = new Uint8Array(N * 4);
const SP = new Float32Array(N);   // local tangential spacing (m)
for (let ri = 0; ri < rings.length; ri++) {
  const R = rings[ri];
  for (let k = 0; k < R.seg; k++) {
    const v = R.v0 + k, u = k / R.seg;
    let x, z;
    if (ri === 0) { const e = l1Edge(k); x = -S0 + (e % L1G) * L1step; z = -S0 + Math.floor(e / L1G) * L1step; }
    else [x, z] = ringPoint(u, R.s);
    XZ[v * 2] = x; XZ[v * 2 + 1] = z;
    SP[v] = Math.max(L1step, 2 * Math.PI * Math.hypot(x, z) / R.seg);
    H[v] = ri === 0 ? L1raw[l1Edge(k)] : hAt(x, z);
  }
}
console.log(`heights ${((Date.now() - t0) / 1000).toFixed(1)} s`);

// mesh neighbours: point (x, h, z) of ring j at loop position u (linear along the ring); rings beyond the ends clamp
const P = (j, u, out) => {
  j = Math.min(rings.length - 1, Math.max(0, j));
  const R = rings[j], f = (((u % 1) + 1) % 1) * R.seg, k = Math.floor(f), t = f - k, a = R.v0 + k, b = R.v0 + (k + 1) % R.seg;
  out[0] = XZ[a * 2] + (XZ[b * 2] - XZ[a * 2]) * t; out[2] = XZ[a * 2 + 1] + (XZ[b * 2 + 1] - XZ[a * 2 + 1]) * t;
  out[1] = H[a] + (H[b] - H[a]) * t;
  return out;
};
// ridge sharpening (--sharpen k): an unsharp mask at ~2 vertices (crests up, notches and gullies down) - the
// terrarium / SRTM surface blunts the summits and aretes; faded in over the first 3 km (L1 seam) and off on the
// low valley floors / lakes
{
  const ai = process.argv.indexOf('--sharpen'), K = ai > 0 ? +process.argv[ai + 1] : 0;
  if (K > 0) {
    const H0 = H.slice(), a = [0, 0, 0];
    const P0 = (j, u) => {
      j = Math.min(rings.length - 1, Math.max(0, j));
      const R = rings[j], f = (((u % 1) + 1) % 1) * R.seg, k = Math.floor(f), t = f - k;
      return H0[R.v0 + k] + (H0[R.v0 + (k + 1) % R.seg] - H0[R.v0 + k]) * t;
    };
    for (let ri = 1; ri < rings.length; ri++) {
      const R = rings[ri], w0 = smoothstep(S0, S0 + 3000, R.s);
      for (let k = 0; k < R.seg; k++) {
        const v = R.v0 + k, u = k / R.seg;
        let s = 0;
        for (const d of [1, 2]) s += P0(ri, (k + d) / R.seg) + P0(ri, (k - d) / R.seg) + P0(ri + d, u) + P0(ri - d, u);
        const lap = H0[v] - s / 8;
        H[v] = H0[v] + K * w0 * smoothstep(800, 1400, H0[v]) * Math.max(-60, Math.min(60, lap));
      }
    }
    console.log(`sharpened (k ${K})`);
  }
}
// normals from the mesh (tangent along the ring x tangent across the rings), consistent with the drawn surface
const CV = new Uint8Array(N);
{
  const a = [0, 0, 0], b = [0, 0, 0], c = [0, 0, 0], d = [0, 0, 0];
  for (let ri = 0; ri < rings.length; ri++) {
    const R = rings[ri];
    for (let k = 0; k < R.seg; k++) {
      const v = R.v0 + k, u = k / R.seg;
      P(ri, (k + 1) / R.seg, a); P(ri, (k - 1) / R.seg, b); P(ri + 1, u, c); P(ri > 0 ? ri - 1 : ri, u, d);
      if (ri === 0) { d[0] = XZ[v * 2]; d[1] = H[v]; d[2] = XZ[v * 2 + 1]; }
      const tx = a[0] - b[0], ty = a[1] - b[1], tz = a[2] - b[2], rx = c[0] - d[0], ry = c[1] - d[1], rz = c[2] - d[2];
      // n = r x t (up for a counter-clockwise loop seen from above)
      let nx = ry * tz - rz * ty, ny = rz * tx - rx * tz, nz = rx * ty - ry * tx;
      if (ny < 0) { nx = -nx; ny = -ny; nz = -nz; }
      const l = Math.hypot(nx, ny, nz) || 1;
      NRM[v * 3] = Math.round(nx / l * 127); NRM[v * 3 + 1] = Math.round(ny / l * 127); NRM[v * 3 + 2] = Math.round(nz / l * 127);
      // concavity (as tools/terrain.mjs, 1 and 3 vertices out along and across the rings): + gullies, - ribs
      let cv = 0;
      for (const [Rr, w] of [[1, 0.6], [3, 0.4]]) {
        let s = 0, dsum = 0;
        for (const [jj, uu] of [[ri, (k + Rr) / R.seg], [ri, (k - Rr) / R.seg], [ri + Rr, u], [ri - Rr, u]]) {
          if (jj < 0 || jj >= rings.length) continue;
          P(jj, uu, a);
          s += a[1]; dsum += Math.hypot(a[0] - XZ[v * 2], a[2] - XZ[v * 2 + 1]);
        }
        const cnt = (ri - Rr >= 0 ? 4 : 3) - (ri + Rr >= rings.length ? 1 : 0);
        cv += w * (s / cnt - H[v]) / Math.max(1, dsum / cnt);
      }
      CV[v] = Math.round(Math.min(255, Math.max(1, 128 + cv * 160)));
    }
  }
}
console.log(`normals ${((Date.now() - t0) / 1000).toFixed(1)} s`);

// coarse grid (250 m, +-250 km) for the horizon bake
const CG = 2001, CS = 250, CH = 250000;
const C = new Float32Array(CG * CG);
for (let j = 0; j < CG; j++) for (let i = 0; i < CG; i++) C[j * CG + i] = hAt(-CH + i * CS, -CH + j * CS);
const cAt = (x, z) => {
  let fx = (x + CH) / CS, fz = (z + CH) / CS;
  if (fx < 0 || fz < 0 || fx >= CG - 1 || fz >= CG - 1) return 0;
  const i = Math.floor(fx), j = Math.floor(fz), u = fx - i, w = fz - j, k = j * CG + i;
  return (C[k] * (1 - u) + C[k + 1] * u) * (1 - w) + (C[k + CG] * (1 - u) + C[k + CG + 1] * u) * w;
};
console.log(`coarse grid ${((Date.now() - t0) / 1000).toFixed(1)} s`);

// attributes: sky visibility (8-direction horizon), glow visibility (horizon toward the sun azimuth), water, concavity
const sunAz = meta.SCENE.sunAz * Math.PI / 180, sunDir = [Math.sin(sunAz), -Math.cos(sunAz)];
const NDIR = 8, dirs = [...Array(NDIR)].map((_, d) => { const a = (d + 0.5) / NDIR * Math.PI * 2; return [Math.cos(a), Math.sin(a)]; });
const lakeY = meta.SCENE.lakeLevel;
for (let ri = 0; ri < rings.length; ri++) {
  const R = rings[ri];
  for (let k = 0; k < R.seg; k++) {
    const v = R.v0 + k, x = XZ[v * 2], z = XZ[v * 2 + 1], h = H[v] + 1.5, sp = SP[v];
    const nx = NRM[v * 3] / 127, ny = NRM[v * 3 + 1] / 127, nz = NRM[v * 3 + 2] / 127;
    const sx = -nx / ny, sz = -nz / ny;
    const horizon = d0 => {
      let maxT = -10, d = Math.max(sp, 120);
      while (d < 25000) {
        const t = (cAt(x + d0[0] * d, z + d0[1] * d) - h - d * d / (2 * EARTH_R)) / d;
        if (t > maxT) maxT = t;
        d *= 1.15; d += 40;
      }
      return Math.atan(maxT);
    };
    let vis = 0;
    for (const d0 of dirs) {
      const aP = Math.atan(sx * d0[0] + sz * d0[1]);
      const aH = Math.max(aP, horizon(d0));
      vis += (1 - Math.sin(aH)) / Math.max(1e-3, 1 - Math.sin(aP));
    }
    vis /= NDIR;
    const glow = 1 - smoothstep(0.0, 0.16, horizon(sunDir));
    // water: flat ground near the lake level (Lake Thun 558 m; the shader shades it as water within 25 m of 564)
    let water = 0;
    if (Math.abs(H[v] - lakeY) < 22) {
      let mn = 1e9, mx = -1e9;
      for (const [a, b] of [[0, 0], [1, 0], [-1, 0], [0, 1], [0, -1]]) { const hh = hAt(x + a * sp, z + b * sp); mn = Math.min(mn, hh); mx = Math.max(mx, hh); }
      if (mx - mn < 1.0) water = 255;
    }
    let sv = 255 * Math.min(1, Math.max(0, vis)), gv = 255 * glow, cvv = CV[v];
    // first ~2.5 km: fade into L1's edge values (its own horizon bake) so the seam shows no brightness step
    const wE = smoothstep(S0, S0 + 2500, R.s);
    if (R.band === 0 && wE < 1) {
      const e = l1Edge(k) * 4;
      sv = L1attr[e] + (sv - L1attr[e]) * wE; gv = L1attr[e + 1] + (gv - L1attr[e + 1]) * wE;
      cvv = L1attr[e + 3] + (cvv - L1attr[e + 3]) * wE;
      if (ri === 0) water = L1attr[e + 2];
    }
    ATTR[v * 4] = Math.round(sv); ATTR[v * 4 + 1] = Math.round(gv); ATTR[v * 4 + 2] = water; ATTR[v * 4 + 3] = Math.round(cvv);
  }
  if (ri % 100 === 0) console.log(`  attr ring ${ri}/${rings.length} ${((Date.now() - t0) / 1000).toFixed(1)} s`);
}

// (written as .tmp and renamed together at the end: a renderer loading meanwhile never sees a mixed set)
fs.writeFileSync(`${OUT}/LF.xz.tmp`, Buffer.from(XZ.buffer));
fs.writeFileSync(`${OUT}/LF.f32.tmp`, Buffer.from(H.buffer));
fs.writeFileSync(`${OUT}/LF.nrm.tmp`, Buffer.from(NRM.buffer));
fs.writeFileSync(`${OUT}/LF.attr.tmp`, Buffer.from(ATTR.buffer));

// far village lights (tools/lights.mjs placed them on L0's 312 m / L1's blended heights): re-seat on the new surface
{
  const L0 = meta.LEVELS[0], L0H = new Float32Array(fs.readFileSync(`${OUT}/L0.f32`).buffer.slice(0));
  const bil = (A, g, size, x, z) => {
    const st = size / (g - 1), fx = Math.min(g - 1.001, Math.max(0, (x + size / 2) / st)), fz = Math.min(g - 1.001, Math.max(0, (z + size / 2) / st));
    const i = Math.floor(fx), j = Math.floor(fz), u = fx - i, w = fz - j, k = j * g + i;
    return (A[k] * (1 - u) + A[k + 1] * u) * (1 - w) + (A[k + g] * (1 - u) + A[k + g + 1] * u) * w;
  };
  const lights = new Float32Array(fs.readFileSync(`${OUT}/lights.f32`).buffer.slice(0));
  const dy = new Float32Array(lights.length / 5);
  let n = 0, mx = 0;
  for (let i = 0; i < dy.length; i++) {
    const x = lights[i * 5], z = lights[i * 5 + 2];
    if (Math.max(Math.abs(x), Math.abs(z)) < 0.86 * S0) continue;   // L2 / L1 interior: unchanged
    const inL1 = Math.max(Math.abs(x), Math.abs(z)) < S0;
    const hOld = inL1 ? bil(L1old, L1G, 2 * S0, x, z) : bil(L0H, L0.grid, L0.size, x, z);
    const hNew = inL1 ? bil(L1raw, L1G, 2 * S0, x, z) : hAt(x, z);
    dy[i] = hNew - hOld; n++; mx = Math.max(mx, Math.abs(dy[i]));
  }
  fs.writeFileSync(`${OUT}/lights_dy.f32`, Buffer.from(dy.buffer));
  console.log(`lights re-seated: ${n}, max |dy| ${mx.toFixed(0)} m`);
}

meta.FAR = { name: 'LF', count: N, rings: rings.map(r => r.seg), note: 'polar far level (tools/fardem.mjs): LF.xz (x,z f32), LF.f32, LF.nrm (i8x3), LF.attr; replaces L0' };
for (const f of ['xz', 'f32', 'nrm', 'attr']) fs.renameSync(`${OUT}/LF.${f}.tmp`, `${OUT}/LF.${f}`);
fs.writeFileSync(SWAP ? `${OUT}/meta.json` : `${OUT}/meta.new.json`, JSON.stringify(meta, null, 1));
console.log(`done ${((Date.now() - t0) / 1000).toFixed(1)} s`);
