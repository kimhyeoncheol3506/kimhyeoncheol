// Photographic sky bake (round 8): a CC0 HDRI (Poly Haven, data/sky/src/*.hdr) -> data/sky/sky.png + sky.json.
// The HDRI is turned so its sun sits at the scene's glow azimuth (config SUN_AZ + AZ_OFF), lowered by DELTA deg at
// the horizon (tapering to 0 at the zenith: the setting sun and its disk drop below the scene horizon), and graded by
// a per-direction gain: target(e, t) / clear(e_h, t), where target is the reference-calibrated analytic twilight sky
// (port of common.js skyClear at dip 0) and clear is the HDRI's own clear-sky radiance at the same elevation /
// azimuth-from-sun, measured on its cloud-free side. The clear sky then lands on the refs' colours while every cloud
// keeps its photographic ratio to the sky behind it (through an asymmetric curve, GD / GB, see below); then a
// horizon haze toward fogColor, a band restore in the glow sector and two-scale clarity.
// Output: equirect, u = compass azimuth / 360 (north 0, east 0.25), rows from +90 deg down to EL_BOT, log2-encoded
// 8-bit RGB with triangular dither (decode: c = exp2(lmin + v * lrange), linear radiance before uSkyExposure).
// usage: node tools/skybake.mjs [src.hdr] ; env W (out width, 8192), DELTA (3.5), AZ_OFF (-5), GD / GB / CHROMA,
// CH_HI / GB_HI, LM_A / LM_B, HAZE / HAZE_E / HAZE_K, BAND, CLARITY / CL_SIG / CLARITY2 / CL_SIG2, STREAKS (0: off),
// OUT (data/sky), PREVIEW=1; second HDRI: SRC2 (none: off), MIRROR2, AZ_OFF2, DELTA2, T2A..T2D, EL2A / EL2B,
// DISP_T / DISP_E, GD2 / GB2, W2, W2Z / E2A / E2B (overhead), BLUE2. The defaults reproduce the shipped data/sky
// (round 8 pass 2: belfast_sunset_puresky + cedar_bridge_sunset_1 right of the glow, the refs' bluer grade, streaks).
// Takes ~1-2 min and ~5 GB with both sources (node --max-old-space-size=14000).
import fs from 'node:fs';
import sharp from 'sharp';
import { readHDR, sampleEq } from './skyhdr.mjs';

const SRC = process.argv[2] || 'data/sky/src/belfast_sunset_puresky_8k.hdr';
const OW = +(process.env.W || 8192);
const EL_BOT = -10;                                   // deg
const OH = Math.round((90 - EL_BOT) * OW / 360);
const DELTA = +(process.env.DELTA ?? 3.5);
const AZ_OFF = +(process.env.AZ_OFF ?? -5);         // the HDRI's sun 5 deg left of the scene glow: the mass's lit tongue ends at the glow
const SUN_AZ = 214;
const D2R = Math.PI / 180;
// horizon haze toward common.js fogColor (its cool / warm airlight, linear): strength, e-folding height (deg), gain
const HAZE = +(process.env.HAZE ?? 0.85), HAZE_E = +(process.env.HAZE_E ?? 4.5), HAZE_K = +(process.env.HAZE_K ?? 1.12);
const BAND = +(process.env.BAND ?? 0.6);            // band restore under the masses in the glow sector
const GD = +(process.env.GD ?? 0.75), GB = +(process.env.GB ?? 1.25), CHROMA = +(process.env.CHROMA ?? 1.0);
// pass 2: above the band the photo's sunset-lit undersides (its sun is 2 deg up, ours 4 deg down) must not stay the
// hottest thing in the frame: the chroma exponent falls from CHROMA (el < 2.5 deg) to CH_HI (> 7 deg) and the
// bright-cloud exponent from GB (< 2 deg) to GB_HI (> 5 deg); the refs keep the masses slate with a thin lit rim
const CH_HI = +(process.env.CH_HI ?? 0.45), GB_HI = +(process.env.GB_HI ?? 0.5);
// overhead (above ~30-50 deg, ref 9: billows with salmon-lit undersides against deep indigo gaps): the curve's
// contrast comes back (GD_UP / GB_UP) and in the glow half the parts brighter than the clear sky take a salmon
// tint (UPW; the sun 4 deg below the horizon still lights the high cloud from beneath)
const GD_UP = +(process.env.GD_UP ?? 1.0), GB_UP = +(process.env.GB_UP ?? 1.1), UPW = +(process.env.UPW ?? 1.0);
const SALMON = [1.7, 1.02, 0.78].map(Math.log);
// pass 2: the photo's own low cloud bank (a dark grey stripe 2-8 deg up all round its horizon) gives way to the
// target gradient away from the glow, below LM_B deg (fully below LM_A)
const LM_A = +(process.env.LM_A ?? 3), LM_B = +(process.env.LM_B ?? 9);
// (keep in sync with common.js fogColor; pass 2: the warm end peach-grey instead of pink-lilac)
const FOG_COOL = [0.353, 0.384, 0.533].map(v => Math.pow(v, 2.2)), FOG_WARM = [0.500, 0.390, 0.440].map(v => Math.pow(v, 2.2));

const sm = (a, b, x) => { const t = Math.min(Math.max((x - a) / (b - a), 0), 1); return t * t * (3 - 2 * t); };
const mix = (a, b, t) => [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t];

// ---- target: common.js skyClear with uFarDip 0, uSkyView identity, uHorizonDip 0.025 (dy = sin(elevation),
// t = azimuth from the glow in rad). Keep in sync with skyClear's knots (the refs' measured clear-sky colours).
export function targetClear(dy, t) {
  const e = dy + 0.025;
  const u = e - 0.055;
  const h = u < 0.03 ? u / 0.72 : 0.041667 + (u - 0.03) * 0.9;
  // (round 8: skyClear's band base was a 0.3 deg step, hidden behind the far skyline in the stills; a free camera
  // sees it as a hard line wherever the skyline dips, so the base ramps in over ~1.3 deg from a deep orange)
  let s = [0.80, 0.25, 0.085];
  s = mix(s, [0.90, 0.29, 0.095], sm(-0.03, 0.0035, h));
  s = mix(s, [0.88, 0.35, 0.115], sm(0.0035, 0.0105, h));
  s = mix(s, [0.96, 0.47, 0.16], sm(0.0105, 0.019, h));
  s = mix(s, [0.98, 0.54, 0.19], sm(0.019, 0.026, h));
  s = mix(s, [0.95, 0.47, 0.19], sm(0.026, 0.033, h));
  s = mix(s, [0.90, 0.40, 0.20], sm(0.033, 0.040, h));
  s = mix(s, [0.76, 0.34, 0.22], sm(0.040, 0.049, h));
  s = mix(s, [0.45, 0.24, 0.24], sm(0.049, 0.056, h));
  s = mix(s, [0.30, 0.205, 0.27], sm(0.056, 0.063, h));
  s = mix(s, [0.23, 0.185, 0.285], sm(0.063, 0.075, h));
  s = mix(s, [0.18, 0.175, 0.31], sm(0.075, 0.092, h));
  s = mix(s, [0.15, 0.165, 0.315], sm(0.092, 0.108, h));
  s = mix(s, [0.105, 0.145, 0.31], sm(0.108, 0.122, h));
  // (pass 2: the shoulders either side of the band peach-grey then blue-grey instead of mauve-lilac)
  let m = [0.22, 0.12, 0.16];
  m = mix(m, [0.30, 0.17, 0.18], sm(-0.004, 0.0035, h));
  m = mix(m, [0.24, 0.17, 0.20], sm(0.0035, 0.030, h));
  m = mix(m, [0.165, 0.152, 0.24], sm(0.030, 0.055, h));
  m = mix(m, [0.12, 0.142, 0.27], sm(0.055, 0.080, h));
  m = mix(m, [0.09, 0.135, 0.30], sm(0.080, 0.115, h));
  // (pass 2: away from the glow grey-lavender instead of pink at 2-4 deg, and the upper sky a deep blue with less
  // red: the refs' clear sky above ~8 deg is #355184 / #3e557e / #45598b, a* 3-7, b* -26..-32; the bake output
  // of pass 1 measured #615679 there. These knots now differ from common.js skyClearA, the pre-load fallback)
  let a = [0.070, 0.076, 0.150];
  a = mix(a, [0.088, 0.086, 0.16], sm(0.0, 0.0296, e));
  a = mix(a, [0.112, 0.105, 0.19], sm(0.0296, 0.0667, e));
  a = mix(a, [0.075, 0.100, 0.245], sm(0.0667, 0.126, e));
  let col = mix(a, m, Math.exp(-t * t / 0.36));
  col = mix(col, s, Math.exp(-t * t / 0.075));
  col = mix(col, mix([0.066, 0.112, 0.285], [0.078, 0.130, 0.31], sm(1.6, 0.6, t)), sm(0.17, 0.20, e));
  col = mix(col, [0.058, 0.110, 0.29], sm(0.20, 0.33, e));
  col = mix(col, [0.046, 0.090, 0.255], sm(0.33, 1.2, e));
  // (pass 2: skyClearA's mauve lift at 11-20 deg toward the glow dropped)
  const v2 = Math.exp(-t * t / 0.9) * sm(0.27, 0.62, e) * (1 - 0.5 * sm(1.1, 1.45, e));
  col = [col[0] * (1 - 0.42 * v2), col[1] * (1 - 0.54 * v2), col[2] * (1 - 0.44 * v2)];
  const f = 1 - 0.45 * sm(0.0, -0.15, e);
  return [col[0] * f, col[1] * f, col[2] * f];
}

// ---- sources: the main HDRI (everything) and an optional second one (SRC2) whose clouds take over above
// E2A .. E2B deg (an upper cloud layer: ref 9's sunset-lit field overhead). Each gets its own sun and clear profile.
const t0 = Date.now();
// blueOnly: the clear profile from the bluest quarter of each bin (a mostly cloudy daytime photo: its median is
// cloud, its blue gaps are the clear sky)
function loadSource(path, side, runMax, sunOverride, blueOnly) {
  const img = readHDR(path);
  const { w: SW, h: SH, data } = img;
  console.log(`read ${path} ${SW}x${SH} in ${Date.now() - t0} ms`);
  const L = i => 0.2126 * data[i] + 0.7152 * data[i + 1] + 0.0722 * data[i + 2];
  // sun: brightest pixel 0 .. 12 deg up
  let mx = 0, sx = 0, sy = 0;
  for (let y = Math.round(78 / 180 * SH); y < SH / 2; y++) for (let x = 0; x < SW; x++) { const l = L((y * SW + x) * 3); if (l > mx) { mx = l; sx = x; sy = y; } }
  const sunU = sunOverride ? +sunOverride : (sx + 0.5) / SW, sunEl = 90 - (sy + 0.5) / SH * 180;   // (override: a lamp can outshine the sun)
  console.log(`sun u=${sunU.toFixed(4)} el=${sunEl.toFixed(2)} L=${mx.toFixed(1)}`);
  // clear-sky profile on the clear side (side 1: clockwise of the sun, t > 0), per HDRI elevation / t bin, per
  // channel median, then smoothed
  const prof = new Float32Array(NE * NT * 3);
  const vals = Array.from({ length: NE * NT }, () => [[], [], []]);
  for (let y = 0; y < SH; y++) {
    const el = 90 - (y + 0.5) / SH * 180;
    if (el < E0 - EB) continue;
    const ei = Math.min(NE - 1, Math.max(0, Math.round((el - E0) / EB)));
    const step = Math.max(1, Math.round(1 / Math.max(Math.cos(el * D2R), 0.02) / 2));   // thin out near the zenith
    for (let x = 0; x < SW; x += step) {
      let tdeg = (((x + 0.5) / SW - sunU) * 360) * side;
      tdeg = ((tdeg % 360) + 360) % 360;
      if (tdeg > 102) continue;
      const ti = Math.min(NT - 1, Math.round(tdeg / TB));
      const i = (y * SW + x) * 3, b = vals[ei * NT + ti];
      b[0].push(data[i]); b[1].push(data[i + 1]); b[2].push(data[i + 2]);
    }
  }
  if (blueOnly) for (let k = 0; k < NE * NT; k++) {
    const [R, G, B] = vals[k], n = R.length;
    if (!n) continue;
    const bl = R.map((r, i) => B[i] / Math.max(r + G[i] + B[i], 1e-6));
    const thr = [...bl].sort((p, q) => p - q)[Math.floor(n * 0.75)];
    const keep = [[], [], []];
    for (let i = 0; i < n; i++) if (bl[i] >= thr) { keep[0].push(R[i]); keep[1].push(G[i]); keep[2].push(B[i]); }
    vals[k] = keep;
  }
  for (let k = 0; k < NE * NT; k++) for (let c = 0; c < 3; c++) {
    const a = vals[k][c];
    if (!a.length) { prof[k * 3 + c] = NaN; continue; }
    a.sort((p, q) => p - q);
    prof[k * 3 + c] = a[Math.floor(a.length * 0.5)];
  }
  // fill gaps (none expected) from the elevation neighbour
  for (let k = 0; k < NE * NT; k++) for (let c = 0; c < 3; c++) if (!(prof[k * 3 + c] >= 0)) prof[k * 3 + c] = prof[(k - NT) * 3 + c] || 1;
  // the clear sky only brightens toward the sun: a running maximum from 100 deg in to the sun (by luminance), so
  // the dark cloud tongue that crosses the sun's azimuth on its clear side keeps its darkness instead of being
  // normalised into sky
  if (runMax) for (let ei = 0; ei < NE; ei++) for (let ti = NT - 2; ti >= 0; ti--) {
    const a = (ei * NT + ti) * 3, b = (ei * NT + ti + 1) * 3;
    const la = 0.2126 * prof[a] + 0.7152 * prof[a + 1] + 0.0722 * prof[a + 2], lb = 0.2126 * prof[b] + 0.7152 * prof[b + 1] + 0.0722 * prof[b + 2];
    if (la < lb) for (let c = 0; c < 3; c++) prof[a + c] *= lb / Math.max(la, 1e-6);   // (brightness only: keep the hue)
  }
  // smooth in log space: t sigma 1 bin near the sun .. 3 bins; elevation sigma 0.5 deg low .. 4 deg high
  const lp = prof.map(v => Math.log(Math.max(v, 1e-4)));
  const sp = new Float32Array(lp.length);
  for (let ei = 0; ei < NE; ei++) for (let ti = 0; ti < NT; ti++) {
    const el = E0 + ei * EB;
    const se = (0.5 + 3.5 * sm(3, 40, el)) / EB, st = 0.7 + 2.3 * sm(0, 6, ti) * sm(4, 15, el + 6);
    for (let c = 0; c < 3; c++) {
      let s = 0, wsum = 0;
      for (let de = -Math.ceil(2.5 * se); de <= Math.ceil(2.5 * se); de++) {
        const ej = ei + de; if (ej < 0 || ej >= NE) continue;
        for (let dt = -Math.ceil(2.5 * st); dt <= Math.ceil(2.5 * st); dt++) {
          const tj = Math.abs(ti + dt); if (tj >= NT) continue;
          const wgt = Math.exp(-0.5 * (de * de / (se * se) + dt * dt / (st * st)));
          s += wgt * lp[(ej * NT + tj) * 3 + c]; wsum += wgt;
        }
      }
      sp[(ei * NT + ti) * 3 + c] = s / wsum;
    }
  }
  // clear(e_h deg, t deg) -> rgb (bilinear in the table)
  function clearAt(el, tdeg, out) {
    const fe = Math.min(Math.max((el - E0) / EB, 0), NE - 1.001), ft = Math.min(Math.max(tdeg / TB, 0), NT - 1.001);
    const e0 = Math.floor(fe), t0 = Math.floor(ft), a = fe - e0, b = ft - t0;
    for (let c = 0; c < 3; c++) {
      const v = (sp[(e0 * NT + t0) * 3 + c] * (1 - b) + sp[(e0 * NT + t0 + 1) * 3 + c] * b) * (1 - a)
              + (sp[((e0 + 1) * NT + t0) * 3 + c] * (1 - b) + sp[((e0 + 1) * NT + t0 + 1) * 3 + c] * b) * a;
      out[c] = Math.exp(v);
    }
    return out;
  }
  for (const el of [0, 2, 4, 8, 15, 30, 60, 85]) {
    const r = [];
    for (const td of [0, 20, 50, 100]) { const o = clearAt(el, td, [0, 0, 0]); r.push(o.map(v => v.toFixed(2)).join(',')); }
    console.log(`clear el ${el}: ${r.join(' | ')}`);
  }
  return { img, sunU, sunEl, clearAt };
}
const EB = 0.5, E0 = -4, NE = Math.round((90 - E0) / EB) + 1;      // elevation bins (deg)
const TB = 4, NT = 26;                                              // t bins 0 .. 100 deg
const S1 = loadSource(SRC, +(process.env.CLEAR_SIDE || 1), true);
const { img, sunU, sunEl, clearAt } = S1;
// pass 2: the second source fills the half of the sphere the first leaves empty (pass 1: ~135 deg of flat gradient
// right of the glow) and the back: CC0 Poly Haven cedar_bridge_sunset_1 (heavy billowing masses with clear blue gaps,
// regraded through its own clear profile from its bluest pixels). Its weight: 0 in the glow sector, ramping in
// from T2A to T2B deg right of the glow and out again from T2C to T2D (behind), optionally W2Z overhead
// above E2A .. E2B deg, never below EL2A .. EL2B deg (its ground and buildings). SRC2=none: the first source alone.
const SRC2 = (process.env.SRC2 ?? 'data/sky/src_cedar/cedar_bridge_sunset_1_8k.hdr') === 'none' ? '' : (process.env.SRC2 ?? 'data/sky/src_cedar/cedar_bridge_sunset_1_8k.hdr');
const E2A = +(process.env.E2A ?? 40), E2B = +(process.env.E2B ?? 62), W2 = +(process.env.W2 ?? 1), W2Z = +(process.env.W2Z ?? 0);
const T2A = +(process.env.T2A ?? 18), T2B = +(process.env.T2B ?? 55), T2C = +(process.env.T2C ?? 125), T2D = +(process.env.T2D ?? 160);
const EL2A = +(process.env.EL2A ?? 6.5), EL2B = +(process.env.EL2B ?? 10);
// the masses' edge stays soft (a crisp mask edge over the photo's evenly dark mass reads as a cardboard cut-out);
// RIM lightens and warms it on the glow side (the refs' lit edges toward the glow)
const RIM = +(process.env.RIM ?? 0.3);
// the hand-over edges are displaced by a world-direction value noise (~20 deg features): +-DISP_T deg in azimuth,
// +-DISP_E deg in elevation, so the second photo's masses end in ragged edges rather than straight lines
const DISP_T = +(process.env.DISP_T ?? 18), DISP_E = +(process.env.DISP_E ?? 2.5);
const GD2 = +(process.env.GD2 ?? 0.6), GB2 = +(process.env.GB2 ?? 0.35);   // its dark-mass / bright-top exponents
const S2 = SRC2 ? loadSource(SRC2, +(process.env.CLEAR_SIDE2 || 1), false, process.env.SUNU2, +(process.env.BLUE2 ?? 1)) : null;
const AZ_OFF2 = +(process.env.AZ_OFF2 ?? -45), DELTA2 = +(process.env.DELTA2 ?? 0);
// mirrored (MIRROR2 1): its big dark mass, left of its sun in the photo, comes to lie right of the glow with its
// sun-lit flank facing the glow
const MIRROR2 = +(process.env.MIRROR2 ?? 1);
// value noise of the world direction (3 octaves, ~20 deg base features), tabulated on a 0.25 deg grid over the
// output's (u, v) and looked up bilinearly; two independent channels
const NNX = 1440, NNY = Math.round((90 - EL_BOT) * 4) + 1, NZT = new Float32Array(NNX * NNY * 2);
{
  const h3 = (x, y, z) => { const v = Math.sin(x * 127.1 + y * 311.7 + z * 74.7) * 43758.5453; return v - Math.floor(v); };
  const vn3 = (x, y, z) => {
    const ix = Math.floor(x), iy = Math.floor(y), iz = Math.floor(z);
    let fx = x - ix, fy = y - iy, fz = z - iz; fx = fx * fx * (3 - 2 * fx); fy = fy * fy * (3 - 2 * fy); fz = fz * fz * (3 - 2 * fz);
    const l = (a, b, t) => a + (b - a) * t;
    return l(l(l(h3(ix, iy, iz), h3(ix + 1, iy, iz), fx), l(h3(ix, iy + 1, iz), h3(ix + 1, iy + 1, iz), fx), fy),
             l(l(h3(ix, iy, iz + 1), h3(ix + 1, iy, iz + 1), fx), l(h3(ix, iy + 1, iz + 1), h3(ix + 1, iy + 1, iz + 1), fx), fy), fz);
  };
  for (let j = 0; j < NNY; j++) for (let i = 0; i < NNX; i++) {
    const az = i / NNX * 2 * Math.PI, el = (90 - j / (NNY - 1) * (90 - EL_BOT)) * D2R;
    const dx = Math.cos(el) * Math.sin(az), dy = Math.sin(el), dz = -Math.cos(el) * Math.cos(az);
    for (let k = 0; k < 2; k++) {
      const s0 = 3.0, o = k * 17.3;
      const n = 0.45 * vn3(dx * s0 + o, dy * s0, dz * s0) + 0.27 * vn3(dx * s0 * 2.1, dy * s0 * 2.1 + o, dz * s0 * 2.1)
              + 0.17 * vn3(dx * s0 * 4.3, dy * s0 * 4.3, dz * s0 * 4.3 + o) + 0.11 * vn3(dx * s0 * 9.1 + o, dy * s0 * 9.1 + o, dz * s0 * 9.1);
      NZT[(j * NNX + i) * 2 + k] = n;
    }
  }
}
function noiseAt(u, v, k) {
  const fx = u * NNX, fy = Math.min(v * (NNY - 1), NNY - 1.001), x0 = Math.floor(fx), y0 = Math.floor(fy), a = fx - x0, b = fy - y0;
  const xa = ((x0 % NNX) + NNX) % NNX, xb = (xa + 1) % NNX;
  return (NZT[(y0 * NNX + xa) * 2 + k] * (1 - a) + NZT[(y0 * NNX + xb) * 2 + k] * a) * (1 - b)
       + (NZT[((y0 + 1) * NNX + xa) * 2 + k] * (1 - a) + NZT[((y0 + 1) * NNX + xb) * 2 + k] * a) * b;
}
// ---- output
const out = new Float32Array(OW * OH * 3);
const s = [0, 0, 0], cl = [0, 0, 0];
const azSun = (SUN_AZ + AZ_OFF) * D2R;              // where the HDRI's sun goes
const NTT = 721, NCT = 401;                         // per-row tables: target over t 0..180 deg, clear over 0..100 deg
const tgT = new Float32Array(NTT * 3), clT = new Float32Array(NCT * 3), clT2 = new Float32Array(NCT * 3);
const s2 = [0, 0, 0], azSun2 = (SUN_AZ + AZ_OFF2) * D2R;
for (let y = 0; y < OH; y++) {
  const el = 90 - (y + 0.5) / OH * (90 - EL_BOT);
  const elh = el + DELTA * (1 - el / 90);                       // HDRI elevation
  const vh = (90 - elh) / 180;
  const dy = Math.sin(el * D2R);
  for (let k = 0; k < NTT; k++) { const tg = targetClear(dy, k * 0.25 * D2R); tgT[k * 3] = tg[0]; tgT[k * 3 + 1] = tg[1]; tgT[k * 3 + 2] = tg[2]; }
  for (let k = 0; k < NCT; k++) { clearAt(elh, k * 0.25, cl); clT[k * 3] = cl[0]; clT[k * 3 + 1] = cl[1]; clT[k * 3 + 2] = cl[2]; }
  // toward the zenith the azimuth from the glow loses its meaning: both tables converge on their 90 deg value
  // (otherwise the gain fans out radially around the pole: a dark spike at the zenith)
  const wz = sm(70, 88, el);
  if (wz > 0) {
    for (let k = 0; k < NTT; k++) for (let c = 0; c < 3; c++) tgT[k * 3 + c] += (tgT[360 * 3 + c] - tgT[k * 3 + c]) * wz;
    for (let k = 0; k < NCT; k++) for (let c = 0; c < 3; c++) clT[k * 3 + c] += (clT[360 * 3 + c] - clT[k * 3 + c]) * wz;
  }
  // second source for this row (its azimuth sector weight per pixel below)
  const w2 = S2 ? W2 * sm(EL2A, EL2B, el + DISP_E) : 0, w2z = W2Z * sm(E2A, E2B, el);   // (row upper bound)
  const elh2 = el + DELTA2 * (1 - el / 90), vh2 = (90 - elh2) / 180;
  const ch = CHROMA + (CH_HI - CHROMA) * sm(2.5, 7, el), wup = sm(30, 50, el);
  const gbr = GB + (GB_HI - GB) * sm(2, 5, el) + (GB_UP - GB_HI) * wup, gdr = GD + (GD_UP - GD) * wup;
  if (w2 > 0) {
    for (let k = 0; k < NCT; k++) { S2.clearAt(elh2, k * 0.25, cl); clT2[k * 3] = cl[0]; clT2[k * 3 + 1] = cl[1]; clT2[k * 3 + 2] = cl[2]; }
    if (wz > 0) for (let k = 0; k < NCT; k++) for (let c = 0; c < 3; c++) clT2[k * 3 + c] += (clT2[360 * 3 + c] - clT2[k * 3 + c]) * wz;
  }
  for (let x = 0; x < OW; x++) {
    const az = (x + 0.5) / OW * 2 * Math.PI;
    let tdeg = (az - azSun) / D2R;                              // clockwise from the HDRI's sun
    tdeg = ((tdeg + 540) % 360) - 180;
    const uh = sunU + tdeg / 360;
    sampleEq(img, ((uh % 1) + 1) % 1, vh, s);
    // clear sky of the HDRI at this |t|; target in the scene frame: t from the scene's glow (SUN_AZ, without AZ_OFF)
    const fc = Math.min(Math.abs(tdeg), 100) * 4, c0 = Math.min(Math.floor(fc), NCT - 2), bc = fc - c0;
    let tg = (az / D2R - SUN_AZ); tg = Math.abs(((tg + 540) % 360) - 180) * 4;
    const g0 = Math.min(Math.floor(tg), NTT - 2), bg = tg - g0;
    const o = (y * OW + x) * 3;
    // horizon haze: the HDRI's low cloud bank (dark grey all round its horizon) gives way to the scene's airlight
    // (fogColor, the colour the far ranges fade into) over the lowest ~2-3 deg, except in the glow sector where
    // the band runs down to the skyline
    const tr = tg / 4 * D2R;
    let wh = HAZE * Math.exp(-Math.pow(Math.max(el, 0) / HAZE_E, 1.5)) * (1 - Math.exp(-tr * tr / 0.10));
    // below the horizon (only reflections and the odd gap past the far terrain see it): all haze by -1.5 deg (the
    // HDRI's mirrored ground with its smeared sun reflection is never shown)
    if (el < 0) wh = 1 - (1 - wh) * sm(-1.5, 0, el);
    // band: in the glow sector the hot band runs on under the masses down to the skyline (refs 7, 4, 11)
    const wb = BAND * Math.exp(-tr * tr / 0.35) * sm(-0.6, 0.2, el) * (1 - sm(0.8, 2.6, el));
    const fw = 0.3 * Math.exp(-tr * tr / 0.09) + 0.1 * Math.exp(-tr * tr / 0.6);
    // cloud / clear ratio: luminance ratio rl through an asymmetric curve (masses darker than the sky are
    // compressed toward it, GD < 1: the refs' slate masses sit only ~0.7x below the clear sky in linear; lit rims
    // brighter than it are expanded, GB > 1), the per-channel chroma ratio r_c / rl kept (^CHROMA)
    const r = [0, 0, 0], tv = [0, 0, 0];
    for (let c = 0; c < 3; c++) {
      const clv = clT[c0 * 3 + c] * (1 - bc) + clT[(c0 + 1) * 3 + c] * bc;
      tv[c] = tgT[g0 * 3 + c] * (1 - bg) + tgT[(g0 + 1) * 3 + c] * bg;
      r[c] = Math.max(s[c], 1e-5) / clv;
    }
    // per-source log multiplier on the target: luminance ratio through the asymmetric curve, chroma ratio ^ch
    const rl = Math.max(0.2126 * r[0] + 0.7152 * r[1] + 0.0722 * r[2], 1e-5);
    const fl = rl < 1 ? Math.pow(rl, gdr) : Math.pow(rl, gbr);
    const lm = [0, 0, 0];
    for (let c = 0; c < 3; c++) lm[c] = Math.log(fl) + ch * Math.log(r[c] / rl);
    // second source: sector weight (signed scene azimuth from the glow, deg; + = clockwise / right), then a mask
    // biased toward whichever source is cloudier (so in the hand-over both cloud fields keep their opacity instead
    // of ghosting through each other)
    const ts = ((az / D2R - SUN_AZ + 540) % 360) - 180;
    let w2p = 0;
    if (w2 > 0) {
      const nA = noiseAt(x / OW, y / OH, 0), nB = noiseAt(x / OW, y / OH, 1), tsd = ts + DISP_T * Math.max(-1, Math.min(1, (nA - 0.5) * 5));
      // (ts_d stays below T2A for ts <= 0 and above T2D at ts = 180: no seam at the branch cut, which sits at -90)
      const wa = Math.max(ts > -90 ? sm(T2A, T2B, tsd) * (1 - sm(T2C, T2D, tsd)) : 0, w2z);
      w2p = W2 * sm(EL2A, EL2B, el + DISP_E * Math.max(-1, Math.min(1, (nB - 0.5) * 5))) * wa;   // (the fbm's std is ~0.09: x5)
    }
    if (w2p > 0.002) {
      let t2 = (az - azSun2) / D2R; t2 = ((t2 + 540) % 360) - 180;
      const u2 = S2.sunU + (MIRROR2 ? -t2 : t2) / 360;
      sampleEq(S2.img, ((u2 % 1) + 1) % 1, vh2, s2);
      const f2 = Math.min(Math.abs(t2), 100) * 4, k2 = Math.min(Math.floor(f2), NCT - 2), b2 = f2 - k2;
      const r2 = [0, 0, 0];
      for (let c = 0; c < 3; c++) r2[c] = Math.max(s2[c], 1e-5) / (clT2[k2 * 3 + c] * (1 - b2) + clT2[(k2 + 1) * 3 + c] * b2);
      const rl2 = Math.max(0.2126 * r2[0] + 0.7152 * r2[1] + 0.0722 * r2[2], 1e-5);
      const fl2 = rl2 < 1 ? Math.pow(rl2, GD2) : Math.pow(rl2, GB2);
      const c1 = Math.min(Math.abs(Math.log(fl)) / 0.5, 1), c2 = Math.min(Math.abs(Math.log(fl2)) / 0.5, 1);
      const wm = sm(0, 1, w2p + 0.4 * (c2 - c1) * 4 * w2p * (1 - w2p));
      for (let c = 0; c < 3; c++) lm[c] += (Math.log(fl2) + ch * Math.log(r2[c] / rl2) - lm[c]) * wm;
      // lit fringe where the second photo's mass meets the open sky, on the glow side only
      const rim = RIM * 4 * wm * (1 - wm) * c2 * (1 - sm(60, 110, ts));
      if (rim > 0.002) for (let c = 0; c < 3; c++) lm[c] += rim * [0.55, 0.42, 0.32][c];
    }
    // overhead salmon: lit (brighter than clear) parts in the glow half
    const wsal = UPW * sm(25, 45, el) * Math.exp(-0.5 * ts * ts / (85 * 85));
    if (wsal > 0.002) {
      const q = Math.min(Math.max((0.2126 * lm[0] + 0.7152 * lm[1] + 0.0722 * lm[2]) / Math.log(1.35), 0), 1) * wsal;
      for (let c = 0; c < 3; c++) lm[c] += q * SALMON[c];
    }
    // away from the glow the photos' low cloud banks give way to the target gradient (no dark stripe 2-8 deg up)
    const wl = (1 - sm(LM_A, LM_B, el)) * (1 - Math.exp(-tr * tr / 0.25));
    for (let c = 0; c < 3; c++) {
      const tgv = tv[c];
      let v = tgv * Math.exp(lm[c] * (1 - wl));
      v += (tgv - v) * wb;
      const fog = (FOG_COOL[c] + (FOG_WARM[c] - FOG_COOL[c]) * fw) * HAZE_K * (el < 0 ? 1 - 0.3 * sm(0, -6, el) : 1);
      out[o + c] = v + (fog - v) * wh;
    }
  }
}
console.log(`graded in ${Date.now() - t0} ms`);
// pass 2: a few thin long dark streaks across the band (refs 7, 4, 11, 2: backlit stratus lines 0.3-1 deg thick at
// 1-6 deg), [from, to (deg right of the glow), el at from, el at to, thickness (deg), opacity, seed]. Width,
// opacity and a slight waviness vary along each streak (1-D value noise); the ends taper. Colour: dark slate
// picking up a little of the band behind (forward-scattered glow).
const STREAKS = (process.env.STREAKS ?? '1') === '0' ? [] : [
  [-40, 20, 2.4, 2.9, 0.45, 0.65, 1], [-14, 50, 4.8, 4.0, 0.80, 0.50, 2],
  [-70, -8, 1.5, 1.3, 0.30, 0.50, 3], [12, 66, 6.4, 5.6, 1.10, 0.40, 4]];
{
  const hash1 = n => { const v = Math.sin(n * 127.1 + 311.7) * 43758.5453; return v - Math.floor(v); };
  const vn = x => { const i = Math.floor(x), f = x - i, u = f * f * (3 - 2 * f); return hash1(i) * (1 - u) + hash1(i + 1) * u; };
  const fbm1 = x => 0.5 * vn(x) + 0.3 * vn(x * 2.13 + 5.1) + 0.2 * vn(x * 4.37 + 11.3);
  for (const [a0, a1, e0, e1, th, op, sd] of STREAKS) {
    const x0 = Math.floor((SUN_AZ + a0 - 1) / 360 * OW), x1 = Math.ceil((SUN_AZ + a1 + 1) / 360 * OW);
    const emax = Math.max(e0, e1) + 4 * th + 0.5, emin = Math.min(e0, e1) - 4 * th - 0.5;
    const y0 = Math.max(0, Math.floor((90 - emax) / (90 - EL_BOT) * OH)), y1 = Math.min(OH - 1, Math.ceil((90 - emin) / (90 - EL_BOT) * OH));
    for (let xx = x0; xx <= x1; xx++) {
      const x = ((xx % OW) + OW) % OW, ts = (xx + 0.5) / OW * 360 - SUN_AZ, sp = (ts - a0) / (a1 - a0);
      const env = sm(0, 0.16, sp) * (1 - sm(0.8, 1, sp));
      if (env <= 0) continue;
      const ec = e0 + (e1 - e0) * sp + 0.35 * (fbm1(ts / 7 + sd * 13) - 0.5);
      const thk = th * (0.35 + 1.2 * fbm1(ts / 3.5 + sd * 7)) * (0.4 + 0.6 * env);
      const opv = op * env * (0.55 + 0.45 * fbm1(ts / 2.2 + sd * 3));
      for (let y = y0; y <= y1; y++) {
        const el = 90 - (y + 0.5) / OH * (90 - EL_BOT), q = (el - ec) / (0.5 * thk);
        const a = opv * Math.exp(-0.5 * q * q);
        if (a < 0.002) continue;
        const o = (y * OW + x) * 3;
        const col = [0.050 + 0.12 * out[o], 0.054 + 0.12 * out[o + 1], 0.100 + 0.12 * out[o + 2]];
        for (let c = 0; c < 3; c++) out[o + c] += (col[c] - out[o + c]) * a;
      }
    }
  }
}
// pass 2: the pole. The rows converge on one point; any azimuthal structure left there is a radial pinch (pass 1:
// a dark dot at the zenith). Above 84 deg each row fades to its own azimuthal mean, all of it by 89.5 deg
// (run after the clarity passes)
const poleFill = () => { for (let y = 0; y < OH; y++) {
  const el = 90 - (y + 0.5) / OH * (90 - EL_BOT), wp = sm(84, 89.5, el);
  if (wp <= 0) break;
  const m = [0, 0, 0];
  for (let x = 0; x < OW; x++) for (let c = 0; c < 3; c++) m[c] += Math.log(Math.max(out[(y * OW + x) * 3 + c], 1e-6));
  for (let x = 0; x < OW; x++) for (let c = 0; c < 3; c++) { const o = (y * OW + x) * 3 + c; out[o] = Math.exp(Math.log(Math.max(out[o], 1e-6)) * (1 - wp) + m[c] / OW * wp); }
} };
// clarity: log-luminance unsharp masks (angularly isotropic: wider in u toward the zenith) at two scales, ~CL_SIG px
// (0.3 deg: the billows' lobes and lit rims) and CL_SIG2 px (~1.3 deg: lighter tops vs dark cores inside a mass),
// so the masses read with internal structure at film resolution (the photo's overhead field is soft)
// (pass 2: the fine pass off and the coarse one lighter: they left brushed striations and halos on the lit edges)
const CLARITY = +(process.env.CLARITY ?? 0), CL_SIG = +(process.env.CL_SIG ?? 7);
const CLARITY2 = +(process.env.CLARITY2 ?? 0.2), CL_SIG2 = +(process.env.CL_SIG2 ?? 30);
function clarity(amt, sig, elw) {
  const N = OW * OH, lg = new Float32Array(N), tmp = new Float32Array(N);
  for (let i = 0; i < N; i++) lg[i] = Math.log(Math.max(0.2126 * out[i * 3] + 0.7152 * out[i * 3 + 1] + 0.0722 * out[i * 3 + 2], 1e-6));
  // horizontal (wrapping), sigma / cos(el)
  for (let y = 0; y < OH; y++) {
    const el = 90 - (y + 0.5) / OH * (90 - EL_BOT);
    const sg = Math.min(sig / Math.max(Math.cos(el * D2R), 0.02), 1200), R = Math.ceil(2.5 * sg);
    const k = new Float32Array(2 * R + 1);
    for (let i = -R; i <= R; i++) k[i + R] = Math.exp(-0.5 * i * i / (sg * sg));
    const step = Math.max(1, Math.floor(sg / 6));            // sparse taps for the wide kernels
    const row = y * OW;
    for (let x = 0; x < OW; x++) {
      let s = 0, w = 0;
      for (let i = -R; i <= R; i += step) { const xx = (x + i + OW) % OW; s += k[i + R] * lg[row + xx]; w += k[i + R]; }
      tmp[row + x] = s / w;
    }
  }
  // vertical (clamped)
  const R = Math.ceil(2.5 * sig), k = new Float32Array(2 * R + 1), step = Math.max(1, Math.floor(sig / 6));
  for (let i = -R; i <= R; i++) k[i + R] = Math.exp(-0.5 * i * i / (sig * sig));
  for (let y = 0; y < OH; y++) for (let x = 0; x < OW; x++) {
    let s = 0, w = 0;
    for (let i = -R; i <= R; i += step) { const yy = Math.min(OH - 1, Math.max(0, y + i)); s += k[i + R] * tmp[yy * OW + x]; w += k[i + R]; }
    const dl = Math.max(-0.8, Math.min(0.8, lg[y * OW + x] - s / w));
    const g = Math.exp(amt * (elw ? elw(90 - (y + 0.5) / OH * (90 - EL_BOT)) : 1) * dl), o = (y * OW + x) * 3;
    out[o] *= g; out[o + 1] *= g; out[o + 2] *= g;
  }
  console.log(`clarity ${amt} @ ${sig} px in ${Date.now() - t0} ms`);
}
if (CLARITY2 > 0) clarity(CLARITY2, CL_SIG2);
// pass 2: overhead only, a wide pass (~5 deg) so the soft overhead field reads as billows 10-25 deg across
const CLARITY3 = +(process.env.CLARITY3 ?? 0.5), CL_SIG3 = +(process.env.CL_SIG3 ?? 110) * OW / 8192;
if (CLARITY3 > 0) clarity(CLARITY3, CL_SIG3, e => sm(28, 50, e));
if (CLARITY > 0) clarity(CLARITY, CL_SIG);
poleFill();
// horizon colour (el 0.3 .. 2 deg, mean) per 20 deg of azimuth from the glow vs common.js fogColor
{
  const r0 = Math.round((90 - 2) / (90 - EL_BOT) * OH), r1 = Math.round((90 - 0.3) / (90 - EL_BOT) * OH);
  const cool = FOG_COOL, warm = FOG_WARM;
  const rows = [];
  for (let tdeg = 0; tdeg <= 180; tdeg += 20) {
    const m = [0, 0, 0]; let n = 0;
    for (const sg of [1, -1]) {
      const az = (SUN_AZ + sg * tdeg + 720) % 360;
      const x0 = Math.round((az - 5) / 360 * OW), x1 = Math.round((az + 5) / 360 * OW);
      for (let y = r0; y < r1; y++) for (let x = x0; x < x1; x++) { const o = (y * OW + ((x % OW) + OW) % OW) * 3; m[0] += out[o]; m[1] += out[o + 1]; m[2] += out[o + 2]; n++; }
    }
    const t = tdeg * D2R, w = 0.3 * Math.exp(-t * t / 0.09) + 0.1 * Math.exp(-t * t / 0.6);
    const fc = mix(cool, warm, w);
    rows.push(`t ${tdeg}: sky ${m.map(v => (v / n).toFixed(3)).join(',')}  fog ${fc.map(v => v.toFixed(3)).join(',')}`);
  }
  console.log('horizon 0.3-2 deg:\n' + rows.join('\n'));
}
// ---- log encode (a NaN anywhere would silently encode as black: count and zero them)
{ let nn = 0; for (let i = 0; i < out.length; i++) if (!(out[i] >= 0)) { out[i] = 1e-6; nn++; } if (nn) console.warn('WARNING: ' + nn + ' non-finite values'); }
let lo = Infinity, hi = -Infinity;
const ls = [];
for (let i = 0; i < out.length; i += 97) ls.push(out[i]);
ls.sort((a, b) => a - b);
lo = Math.log2(Math.max(ls[Math.floor(ls.length * 0.0005)] * 0.8, 1e-4));
hi = Math.log2(ls[ls.length - 1] * 1.05);
const rng = hi - lo;
console.log(`log2 range ${lo.toFixed(3)} .. ${hi.toFixed(3)} (${rng.toFixed(2)} stops, ${(100 * (Math.pow(2, rng / 255) - 1)).toFixed(2)} % per code)`);
const px = Buffer.alloc(OW * OH * 3);
let seed = 12345;
const rnd = () => { seed = (seed * 1664525 + 1013904223) >>> 0; return seed / 4294967296; };
for (let i = 0; i < out.length; i++) {
  const v = (Math.log2(Math.max(out[i], 1e-6)) - lo) / rng * 255 + (rnd() - rnd());
  px[i] = Math.min(255, Math.max(0, Math.round(v)));
}
const OUT = process.env.OUT || 'data/sky';
fs.mkdirSync(OUT, { recursive: true });
await sharp(px, { raw: { width: OW, height: OH, channels: 3 } }).png({ compressionLevel: 7 }).toFile(OUT + '/sky.png');
const meta = { src: SRC.replace(/^.*[\\/]/, ''), license: SRC2 ? 'CC0 (Poly Haven: Greg Zaal / Jarod Guest; Dario Barresi)' : 'CC0 (Poly Haven, Greg Zaal / Jarod Guest)', w: OW, h: OH, elTop: 90, elBot: EL_BOT,
  lmin: +lo.toFixed(5), lrange: +rng.toFixed(5), sunAz: SUN_AZ + AZ_OFF, delta: DELTA, gd: GD, gb: GB, chroma: CHROMA, chHi: CH_HI, gbHi: GB_HI, lowMask: [LM_A, LM_B], haze: [HAZE, HAZE_E, HAZE_K], band: BAND, clarity: [CLARITY2, CL_SIG2, CLARITY, CL_SIG, CLARITY3, +(process.env.CL_SIG3 ?? 110)], up: [GD_UP, GB_UP, UPW], src2: SRC2 ? SRC2.replace(/^.*[\\/]/, '') : null, src2Sector: SRC2 ? { azOff: AZ_OFF2, mirror: MIRROR2, disp: [DISP_T, DISP_E], rim: RIM, t2: [T2A, T2B, T2C, T2D], el2: [EL2A, EL2B], zen: [W2Z, E2A, E2B], gd2: GD2, gb2: GB2 } : null, streaks: STREAKS.length, sunU: +sunU.toFixed(5), sunEl: +sunEl.toFixed(3) };
fs.writeFileSync(OUT + '/sky.json', JSON.stringify(meta, null, 1));
console.log(`wrote ${OUT}/sky.png`, JSON.stringify(meta), `${Date.now() - t0} ms`);

// ---- preview: simple tone (post.js-like exposure 1, filmic-ish), equirect elevation -4 .. 60 at 2048 wide
if (process.env.PREVIEW) {
  const PW = 2048, e0 = 60, e1 = -4, PH = Math.round((e0 - e1) / 360 * PW);
  const pv = Buffer.alloc(PW * PH * 3);
  for (let j = 0; j < PH; j++) {
    const el = e0 - (j + 0.5) / PH * (e0 - e1), yy = Math.min(OH - 1, Math.round((90 - el) / (90 - EL_BOT) * OH - 0.5));
    for (let i = 0; i < PW; i++) {
      const xx = Math.floor((i + 0.5) / PW * OW), o = (yy * OW + xx) * 3;
      for (let c = 0; c < 3; c++) { const v = out[o + c] * 1.0; const tm = v * (1 + v / 4) / (1 + v); pv[(j * PW + i) * 3 + c] = Math.round(255 * Math.pow(Math.min(tm, 1), 1 / 2.2)); }
    }
  }
  await sharp(pv, { raw: { width: PW, height: PH, channels: 3 } }).jpeg({ quality: 88 }).toFile('out/shots/sky_bake_preview.jpg');
}
