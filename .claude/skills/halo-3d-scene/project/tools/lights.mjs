// Village / road light placement from the baked terrain (L2 + L1 + L0 heights and water masks).
// usage: node tools/lights.mjs   -> data/terrain/lights.f32  [x, y, z, intensity, warm + 2 * class] per light
//   warm: 1 = low-pressure sodium orange .. 0 = 3000 K LED; intensity ~0.2..2.2
//   class (src/lights.js core size / brightness ceiling): 0 house / window / farm, 1 town street lamp, hot
//   spot, rural lane, 2 main road / lakefront quay (the brightest continuous lines, refs 2, 4)
// Layers: real towns/villages around Lake Brienz (Brienz on the delta at the near end, Interlaken /
// Unterseen / Boenigen at the far end, Meiringen, Grindelwald, ...) as dense clusters; least-cost routed
// roads (shore roads hugging both shores, valley roads, switchback climbs to the slope villages) lit as
// dotted strings; hamlets, scattered farms on the slopes; a sparse far field on L0.
import fs from 'node:fs';
import { fbm2, smoothstep, mulberry32 } from './noise.mjs';

const OUT = 'data/terrain';
const meta = JSON.parse(fs.readFileSync(`${OUT}/meta.json`, 'utf8'));
const LEVELS = meta.LEVELS, lake = meta.SCENE.lakeLevel;
const { lat0, lon0 } = meta.CENTER;
const mPerDegLat = 111132.92 - 559.82 * Math.cos(2 * lat0 * Math.PI / 180);
const mPerDegLon = 111412.84 * Math.cos(lat0 * Math.PI / 180);
const toXZ = (lat, lon) => [(lon - lon0) * mPerDegLon, (lat0 - lat) * mPerDegLat];

const load = name => {
  const lv = LEVELS.find(l => l.name === name);
  const H = new Float32Array(fs.readFileSync(`${OUT}/${name}.f32`).buffer.slice(0));
  const A = new Uint8Array(fs.readFileSync(`${OUT}/${name}.attr`));
  const g = lv.grid, W = new Uint8Array(g * g);
  for (let k = 0; k < W.length; k++) W[k] = A[k * 4 + 2];
  return { name, lv, H, W, g, step: lv.size / (g - 1), half: lv.size / 2 };
};
// chamfer distance to water (m)
function waterDist(L) {
  const { g, W } = L, D = new Float32Array(g * g).fill(1e9);
  for (let k = 0; k < g * g; k++) if (W[k]) D[k] = 0;
  for (let pass = 0; pass < 2; pass++) {
    const [js, je, jd] = pass ? [g - 1, -1, -1] : [0, g, 1];
    for (let j = js; j !== je; j += jd) for (let i = pass ? g - 1 : 0; pass ? i >= 0 : i < g; i += pass ? -1 : 1) {
      const k = j * g + i; let d = D[k];
      const pj = j - jd, pi = i - (pass ? -1 : 1);
      if (pj >= 0 && pj < g) d = Math.min(d, D[pj * g + i] + 1);
      if (pi >= 0 && pi < g) d = Math.min(d, D[j * g + pi] + 1);
      if (pj >= 0 && pj < g && pi >= 0 && pi < g) d = Math.min(d, D[pj * g + pi] + 1.414);
      D[k] = d;
    }
  }
  for (let k = 0; k < g * g; k++) D[k] *= L.step;
  return D;
}
const L0 = load('L0'), L1 = load('L1'), L2 = load('L2'), L3 = load('L3');
L1.D = waterDist(L1); L2.D = waterDist(L2);
const inside = (L, x, z, m = 1) => Math.abs(x) < L.half - m * L.step && Math.abs(z) < L.half - m * L.step;
const bil = (L, A, x, z) => {
  const fx = (x + L.half) / L.step, fz = (z + L.half) / L.step;
  const i = Math.min(L.g - 2, Math.max(0, Math.floor(fx))), j = Math.min(L.g - 2, Math.max(0, Math.floor(fz)));
  const u = fx - i, v = fz - j, a = j * L.g + i;
  return (A[a] * (1 - u) + A[a + 1] * u) * (1 - v) + (A[a + L.g] * (1 - u) + A[a + L.g + 1] * u) * v;
};
// (round 5: L3, the sculpted 1.6 km near field, included: under the ring it lies up to ~500 m below L2's raw DEM,
// so lamps placed there from L2 heights would float over the gorge floor)
const levelAt = (x, z) => inside(L3, x, z, 8) ? L3 : inside(L2, x, z, 3) ? L2 : inside(L1, x, z, 2) ? L1 : L0;
const hAt = (x, z) => { const L = levelAt(x, z); return bil(L, L.H, x, z); };
const isWater = (x, z) => {
  const L = levelAt(x, z), i = Math.round((x + L.half) / L.step), j = Math.round((z + L.half) / L.step);
  return L.W[j * L.g + i] > 0;
};
const dWater = (x, z) => { const lv = levelAt(x, z), L = lv === L2 || lv === L3 ? L2 : L1; return inside(L, x, z, 2) ? bil(L, L.D, x, z) : 1e9; };
const slopeAt = (x, z, e = 20) => Math.hypot(hAt(x + e, z) - hAt(x - e, z), hAt(x, z + e) - hAt(x, z - e)) / (2 * e);

const rnd = mulberry32(42);
const gauss = () => { let u = 0; for (let k = 0; k < 4; k++) u += rnd(); return (u - 2) * 0.866; };
const lights = [];
// debug: section id per light (env TAGS=path writes them as u8, for projecting sections into the ref views)
const tags = [];
let SEC = 0;
// above ~1450 m only the odd hut / hotel stays lit (refs: the snowy upper slopes are dark)
const ALT_KEEP = h => h < 1450 ? 1 : 0.04 + 0.5 * smoothstep(1800, 1450, h);
// dir: street / road direction (rad, mod pi) for the lit-road segments src/lights.js draws between the lamps
// (32 steps, stored as 8 * (1 + step) on top of warm + 2 * class; 0 = no direction)
const put = (x, z, inten, warm, lift = 4, cls = 0, dir = null) => {
  if (isWater(x, z)) return false;
  const h = hAt(x, z);
  if (rnd() > ALT_KEEP(h)) return false;
  const dc = dir === null ? 0 : 1 + (Math.round(((dir % Math.PI) + Math.PI) % Math.PI / Math.PI * 32) % 32);
  lights.push(x, h + lift + rnd() * 3, z, inten, warm + 2 * cls + 8 * dc);
  tags.push(SEC);
  return true;
};
// wide brightness spread (refs: bright sodium hot spots, street strings, many dim windows); mean ~0.64 as
// before so the shared town-glow map keeps its range
const houseI = () => { const u = rnd(); return u < 0.04 ? 2.4 + 1.6 * rnd() : u < 0.22 ? 0.95 + 0.6 * rnd() : 0.13 + 0.6 * rnd() ** 2; };
const houseWarm = () => rnd() < 0.7 ? 0.55 + 0.45 * rnd() : 0.1 + 0.3 * rnd();

// ---------------------------------------------------------------- settlements (real places)
// [name, lat, lon, radius m, peak lights/km2, altitude band m, snap: 'shore' | 'flat']
const TOWNS = [
  // Lake Brienz, near end: Brienz on the delta, Kienholz, Brienzwiler / Hofstetten / Schwanden behind
  ['Brienz', 46.7545, 8.0385, 1000, 3200, 120, 'shore'],
  ['BrienzW', 46.7505, 8.0250, 500, 2400, 90, 'shore'],
  ['Kienholz', 46.7545, 8.0560, 600, 2400, 80, 'flat'],
  ['Aaredelta', 46.7500, 8.0700, 800, 1300, 60, 'flat'],
  ['Schwanden', 46.7640, 8.0560, 380, 700, 160, 'flat'],
  ['Hofstetten', 46.7600, 8.0780, 420, 650, 160, 'flat'],
  ['Brienzwiler', 46.7475, 8.0993, 380, 1100, 120, 'flat'],
  // north shore
  ['Ebligen', 46.7415, 8.0020, 230, 1200, 70, 'shore'],
  ['Oberried', 46.7370, 7.9580, 380, 1500, 90, 'shore'],
  ['Niederried', 46.7190, 7.9320, 320, 1400, 90, 'shore'],
  ['Ringgenberg', 46.7010, 7.8960, 520, 1700, 110, 'shore'],
  ['Goldswil', 46.6950, 7.8760, 380, 1500, 90, 'flat'],
  // south shore
  ['Giessbach', 46.7330, 8.0200, 320, 1800, 110, 'shore'],
  ['Iseltwald', 46.7110, 7.9645, 520, 3200, 150, 'shore'],
  ['Boenigen', 46.6870, 7.8940, 560, 2200, 70, 'shore'],
  // far end: Interlaken / Unterseen / Matten / Wilderswil on the Boedeli
  ['Interlaken', 46.6860, 7.8632, 1100, 2800, 70, 'flat'],
  ['InterlakenO', 46.6905, 7.8700, 600, 2400, 60, 'flat'],
  ['Unterseen', 46.6855, 7.8480, 700, 2600, 70, 'flat'],
  ['Matten', 46.6780, 7.8690, 600, 2000, 70, 'flat'],
  ['Wilderswil', 46.6640, 7.8700, 520, 1300, 90, 'flat'],
  ['Gsteigwiler', 46.6560, 7.8720, 260, 700, 120, 'flat'],
  ['Neuhaus', 46.6930, 7.8250, 380, 900, 60, 'shore'],
  // Aare valley east (Haslital), Hasliberg terrace
  ['Meiringen', 46.7270, 8.1870, 850, 2400, 90, 'flat'],
  ['Unterbach', 46.7350, 8.1520, 300, 700, 80, 'flat'],
  ['Balm', 46.7200, 8.1600, 300, 600, 90, 'flat'],
  ['Innertkirchen', 46.7060, 8.2290, 480, 900, 90, 'flat'],
  ['Goldern', 46.7440, 8.1980, 330, 700, 160, 'flat'],
  ['Reuti', 46.7390, 8.2250, 330, 650, 160, 'flat'],
  ['Hohfluh', 46.7530, 8.1830, 330, 600, 160, 'flat'],
  ['Wasserwendi', 46.7520, 8.2070, 330, 600, 160, 'flat'],
  // slope / side-valley villages
  ['Axalp', 46.7155, 8.0440, 450, 420, 170, 'flat'],
  ['Habkern', 46.7270, 7.8620, 600, 380, 170, 'flat'],
  ['Beatenberg', 46.6980, 7.7980, 1100, 420, 150, 'flat'],
  ['Saxeten', 46.6370, 7.8290, 250, 400, 120, 'flat'],
  ['Isenfluh', 46.6200, 7.8950, 200, 350, 120, 'flat'],
  // Luetschine valleys
  ['Zweiluetschinen', 46.6310, 7.9000, 260, 900, 90, 'flat'],
  ['Lauterbrunnen', 46.5935, 7.9090, 650, 1400, 120, 'flat'],
  ['Wengen', 46.6055, 7.9220, 480, 1000, 160, 'flat'],
  ['Guendlischwand', 46.6330, 7.9135, 260, 500, 110, 'flat'],
  ['Burglauenen', 46.6370, 7.9760, 300, 450, 120, 'flat'],
  ['Grindelwald', 46.6245, 8.0413, 1400, 700, 230, 'flat'],
  ['Grund', 46.6200, 8.0260, 400, 700, 120, 'flat'],
  // Bruenig / Obwalden behind the ring
  ['Lungern', 46.7858, 8.1597, 650, 1500, 90, 'shore'],
  ['Obsee', 46.7960, 8.1590, 300, 900, 80, 'shore'],
  ['Kaiserstuhl', 46.8150, 8.1700, 250, 600, 90, 'flat'],
  ['Giswil', 46.8350, 8.1810, 750, 1200, 90, 'flat'],
  ['Sachseln', 46.8670, 8.2340, 600, 1600, 90, 'shore'],
  ['Sarnen', 46.8960, 8.2450, 950, 2200, 90, 'flat'],
  ['Alpnach', 46.9400, 8.2720, 700, 1500, 90, 'flat'],
  ['Soerenberg', 46.8220, 8.0360, 600, 500, 150, 'flat'],
  ['Flühli', 46.8840, 8.0150, 450, 600, 120, 'flat'],
  // Lake Thun east end
  ['Leissigen', 46.6540, 7.7750, 450, 1200, 90, 'shore'],
  ['Daerligen', 46.6620, 7.8070, 300, 900, 80, 'shore'],
  ['Merligen', 46.6970, 7.7390, 420, 1100, 80, 'shore'],
  ['Krattigen', 46.6580, 7.7280, 400, 700, 140, 'flat'],
];
// villages placed in DEM space (x, z m): the far (south-east) shore where the hero lines of sight
// (az 200-217) cross it 6-10 km out (seen through the ring void and the cloud gaps; refs 4-7, 11: lit
// villages strung along the far shore), and the near shore west of Brienz (view 2's gorge window)
// Rothornhang: a slope village with its switchback road on the near (north) bank, 900-1200 m, right where
// view 2's gorge window shows the bottom edge of the lake ('fixed': centre not snapped to flatter ground)
// (round 5: the far-shore villages climb their slope - wide altitude bands - instead of lining the water's
// edge; strung along the shore at the same lake level they merged with the quays into one neon line, view 7)
// Planalp: the Rothorn railway's mid station / alp hamlet on the slope under the ring (~1250 m here), the few
// warm lights seen through the ring void and the cloud gaps from straight above (view 8, the film's top-down
// shot); no lit lane down from it (a lamp string winding down the slope right under the ring, view 11)
const TOWNS_XZ = [
  ['Sengg', -4100, 6950, 450, 2900, 200, 'shore'],
  ['Isch', -5300, 7700, 330, 2300, 180, 'shore'],
  ['Fluhberg', -2600, 3500, 350, 1300, 150, 'shore'],
  ['Rothornhang', -1560, 2150, 360, 1700, 180, 'fixed'],
  ['Planalp', -560, 900, 230, 900, 110, 'fixed'],
];
for (const [name, x, z, ...rest] of TOWNS_XZ) TOWNS.push([name, lat0 - z / mPerDegLat, lon0 + x / mPerDegLon, ...rest]);
const towns = {};
for (const [name, lat, lon, r, rho, band, snap] of TOWNS) {
  let [x, z] = toXZ(lat, lon);
  // snap the centre onto buildable ground (flat land; shore towns sit at the water's edge)
  let best = snap === 'fixed' ? { x, z } : null;
  for (let a = 0; a < 1800 && !(a >= 900 && best); a++) {
    const rr = (a < 900 ? 650 : 1800) * Math.sqrt(rnd()), th = rnd() * 6.283;
    const px = x + Math.cos(th) * rr, pz = z + Math.sin(th) * rr;
    if (isWater(px, pz) || !inside(L1, px, pz, 3)) continue;
    const s = slopeAt(px, pz, 30), dw = dWater(px, pz);
    let sc = rr / 650 + s * 4 + (snap === 'shore' ? Math.abs(dw - 120) / 250 : 0);
    if (!best || sc < best.sc) best = { sc, x: px, z: pz };
  }
  if (!best) continue;
  x = best.x; z = best.z;
  // character: share of white-ish LED street lighting (refs: mostly sodium-orange towns, a few paler ones) and
  // an overall brightness, so neighbouring towns do not read as copies of one another
  const led = rnd() < 0.35 ? 0.35 + 0.4 * rnd() : 0.1 * rnd();
  towns[name] = { x, z, h: hAt(x, z), r, rho, band, shore: snap === 'shore', led, bright: 0.7 + 0.6 * rnd() };
  if (process.env.VERBOSE) console.log(name, Math.round(x), Math.round(z), Math.round(towns[name].h));
}
// per-town lights: Gaussian density inside the altitude band, block structure from noise
// ~65% of the lights snap onto local street grids aligned with the slope contour (lines of lamps = streets)
let nTown = 0;
const TOWN_DENSITY = 1.3;
const hashI = (i, j, k) => { const s = Math.sin(i * 127.1 + j * 311.7 + k * 74.7) * 43758.5453; return s - Math.floor(s); };
for (const [name, t] of Object.entries(towns)) {
  const R = t.r * 2.2, cell = 22;
  const gx = hAt(t.x + 60, t.z) - hAt(t.x - 60, t.z), gz = hAt(t.x, t.z + 60) - hAt(t.x, t.z - 60);
  const th = Math.hypot(gx, gz) > 4 ? Math.atan2(gz, gx) : rnd() * Math.PI;
  const sp = [60 + 40 * rnd(), 75 + 50 * rnd()];
  // quarters (jittered Voronoi cells ~450 m): each has its own grid origin, a turned orientation (the
  // old core keeps the contour-aligned one) and spacing; the grid is gently domain-warped so streets bend.
  // (a single ruler-straight lattice read as a comb of parallel lines in the long-lens views)
  const QC = 450;
  const quarter = (x, z) => {
    const ci = Math.floor((x - t.x) / QC), cj = Math.floor((z - t.z) / QC);
    let best = null, bd = 1e18;
    for (let dj = -1; dj <= 1; dj++) for (let di = -1; di <= 1; di++) {
      const i = ci + di, j = cj + dj;
      const sx = t.x + (i + 0.15 + 0.7 * hashI(i, j, t.x)) * QC, sz = t.z + (j + 0.15 + 0.7 * hashI(j, i, t.z)) * QC;
      const d = (sx - x) ** 2 + (sz - z) ** 2;
      if (d < bd) { bd = d; best = { sx, sz, h: hashI(i, j, 7.7 + t.x), h2: hashI(j, i, 3.1 + t.z) }; }
    }
    const core = Math.hypot(best.sx - t.x, best.sz - t.z) < 0.6 * t.r;
    best.th = th + (core ? 0 : (best.h - 0.5) * 1.3);
    best.sp = [sp[0] * (0.75 + 0.5 * best.h2), sp[1] * (0.75 + 0.5 * best.h)];
    // per-quarter brightness and density (refs 4, 7: lit centres and station yards next to dim residential
    // quarters and near-dark fields / parks: clusters with gaps, not an even carpet)
    const hb = hashI(best.sx * 0.013, best.sz * 0.017, 5.3);
    best.qb = core ? 1.15 : 0.45 + 0.9 * hb * hb;
    best.qd = core ? 1 : 0.3 + 0.7 * hashI(best.sz * 0.011, best.sx * 0.019, 2.9);
    return best;
  };
  // ~65% of the lights sit on streets (refs: towns read as networks of lamp strings, dark blocks between)
  const street = (x, z) => {
    if (rnd() > 0.65) return [x, z, 0];
    const q = quarter(x, z), ca = Math.cos(q.th), sa = Math.sin(q.th);
    const wu = 40 * fbm2(x / 380 + 9.1, z / 380 + 2.3, 2), wv = 40 * fbm2(x / 380 - 4.7, z / 380 + 6.2, 2);
    let u = (x - q.sx) * ca + (z - q.sz) * sa + wu, v = -(x - q.sx) * sa + (z - q.sz) * ca + wv;
    const alongV = rnd() < 0.5;
    if (alongV) u = Math.round(u / q.sp[0]) * q.sp[0] + (rnd() - 0.5) * 6; else v = Math.round(v / q.sp[1]) * q.sp[1] + (rnd() - 0.5) * 6;
    u -= wu; v -= wv;
    return [q.sx + u * ca - v * sa, q.sz + u * sa + v * ca, 1, q.th + (alongV ? Math.PI / 2 : 0)];
  };
  SEC = 1;
  for (let z = t.z - R; z < t.z + R; z += cell) for (let x = t.x - R; x < t.x + R; x += cell) {
    const d2 = ((x - t.x) ** 2 + (z - t.z) ** 2) / (t.r * t.r);
    if (d2 > 4.84) continue;
    const jx = x + (rnd() - 0.5) * cell, jz = z + (rnd() - 0.5) * cell;
    if (isWater(jx, jz)) continue;
    const h = hAt(jx, jz), s = slopeAt(jx, jz, 15);
    let w = Math.exp(-d2 * 1.1) * smoothstep(t.band, t.band * 0.45, Math.abs(h - t.h)) * smoothstep(0.75, 0.25, s);
    // blocks / streets / gardens: medium noise opens dark patches, edges dissolve into scattered houses
    const bl = fbm2(jx / 260 + 31, jz / 260 - 7, 3), bl2 = fbm2(jx / 75 - 3, jz / 75 + 11, 2);
    w *= smoothstep(-0.25, 0.2, bl + 0.25 * (1 - d2)) * (0.45 + 0.9 * smoothstep(-0.25, 0.3, bl2));
    const qq = quarter(jx, jz);
    w *= qq.qd;
    let exp = w * t.rho * TOWN_DENSITY * cell * cell * 1e-6;
    while (exp > 0) {
      if (rnd() < Math.min(1, exp)) {
        const [px, pz, onSt, sdir] = street(jx + (rnd() - 0.5) * cell * 0.8, jz + (rnd() - 0.5) * cell * 0.8);
        // street lamps: sodium (or the town's LED share: pale), brighter in the core and the lit quarters;
        // off-street windows / garden lights dim
        const warm = onSt ? (rnd() < t.led ? 0.12 * rnd() : rnd() < 0.75 ? 0.88 + 0.12 * rnd() : houseWarm()) : houseWarm();
        const I = (onSt ? (0.45 + 0.65 * rnd()) * (1.25 - 0.35 * Math.min(d2, 1)) : houseI() * 0.6) * t.bright * qq.qb;
        if (put(px, pz, I, warm, onSt ? 5 : 3, onSt ? 1 : 0, onSt ? sdir : null)) nTown++;
      }
      exp -= 1;
    }
  }
  // sodium hot spots: station yards, squares, sports fields, hotel fronts (tight groups of bright lamps)
  SEC = 2;
  const nHot = Math.round(t.r * t.r * t.rho * 1.6e-9 * (2 + 2 * rnd()));
  for (let k = 0; k < nHot; k++) {
    const a = rnd() * 6.283, rr = t.r * 0.9 * Math.sqrt(rnd());
    const hx = t.x + Math.cos(a) * rr, hz = t.z + Math.sin(a) * rr;
    if (isWater(hx, hz) || Math.abs(hAt(hx, hz) - t.h) > t.band) continue;
    const cnt = 4 + Math.floor(rnd() * 9), sp = 25 + 45 * rnd();
    // (round 5: 1.8-3.2 -> 1.5-2.7: at 6-10 km the groups clipped to cream blobs, hot pixels ~10x the refs')
    for (let m = 0; m < cnt; m++) if (put(hx + gauss() * sp, hz + gauss() * sp, 1.5 + 1.2 * rnd(), 0.92 + 0.08 * rnd(), 8, 1)) nTown++;
  }
  // lakefront promenade / quay: a bright sodium string along the water's edge through the town (refs 2, 4,
  // 7, 8: the shore road is the brightest line of every lake town and throws the long streaks)
  // (round 5: only the town's own waterfront, broken into lit stretches (harbour, promenade, boat station)
  // with dark gaps (gardens, reeds, the railway behind trees), brightness varied along it; the bright main-road
  // class only in the centre. Every shore town's full-length quay joined the shore road into one continuous
  // bright line with a curtain of identical reflections, view 7)
  SEC = 3;
  if (t.shore || dWater(t.x, t.z) < t.r) {
    const Rq = t.r * (t.r > 450 ? 1.2 : 0.8), sq = 10;
    for (let z = t.z - Rq; z < t.z + Rq; z += sq) for (let x = t.x - Rq; x < t.x + Rq; x += sq) {
      const d2 = ((x - t.x) ** 2 + (z - t.z) ** 2) / (Rq * Rq);
      if (d2 > 1) continue;
      const jx = x + (rnd() - 0.5) * sq, jz = z + (rnd() - 0.5) * sq, dw = dWater(jx, jz);
      if (dw < 13 || dw > 22 || Math.abs(hAt(jx, jz) - lake) > 40) continue;
      const gate = fbm2(jx / 160 + 13.7, jz / 160 - 4.1, 2) + 0.35 * (1 - d2) - 0.08;
      if (gate < 0) continue;
      // (pass 2: a narrower band, an even moderate brightness below the hot spots, and no lit-road segment: one
      // crisp dotted row on the drawn waterline (refs 4, 6, 7, 11) instead of dashes; class 2 only so the row
      // survives the screen-space thinning first)
      const I = (0.5 + 0.7 * rnd()) * (1.1 - 0.4 * d2) * t.bright * smoothstep(0, 0.25, gate);
      if (rnd() < 0.4 * (1 - 0.5 * d2) && put(jx, jz, I, rnd() < t.led ? 0.15 * rnd() : 0.9 + 0.1 * rnd(), 6, 2)) nTown++;
    }
  }
}

// ---------------------------------------------------------------- roads: least-cost routes on L1
const G = L1.g, ST = L1.step;
const NB = [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1], [2, 1], [2, -1], [-2, 1], [-2, -1], [1, 2], [1, -2], [-1, 2], [-1, -2]];
const slopeG = new Float32Array(G * G);
for (let j = 1; j < G - 1; j++) for (let i = 1; i < G - 1; i++) {
  const k = j * G + i;
  slopeG[k] = Math.hypot(L1.H[k + 1] - L1.H[k - 1], L1.H[k + G] - L1.H[k - G]) / (2 * ST);
}
function route(a, b, shore = false) {
  const ia = Math.round((a.x + L1.half) / ST), ja = Math.round((a.z + L1.half) / ST);
  const ib = Math.round((b.x + L1.half) / ST), jb = Math.round((b.z + L1.half) / ST);
  const m = 90;
  const i0 = Math.max(2, Math.min(ia, ib) - m), i1 = Math.min(G - 3, Math.max(ia, ib) + m);
  const j0 = Math.max(2, Math.min(ja, jb) - m), j1 = Math.min(G - 3, Math.max(ja, jb) + m);
  const w = i1 - i0 + 1, h = j1 - j0 + 1, n = w * h;
  const dist = new Float64Array(n).fill(Infinity), prev = new Int32Array(n).fill(-1);
  const heapK = [], heapV = [];
  const push = (kk, v) => {
    let c = heapK.length; heapK.push(kk); heapV.push(v);
    while (c > 0) { const p = (c - 1) >> 1; if (heapK[p] <= kk) break; heapK[c] = heapK[p]; heapV[c] = heapV[p]; c = p; }
    heapK[c] = kk; heapV[c] = v;
  };
  const pop = () => {
    const v = heapV[0], lk = heapK.pop(), lv = heapV.pop();
    if (heapK.length) {
      let c = 0;
      for (;;) {
        let l = 2 * c + 1; if (l >= heapK.length) break;
        if (l + 1 < heapK.length && heapK[l + 1] < heapK[l]) l++;
        if (heapK[l] >= lk) break;
        heapK[c] = heapK[l]; heapV[c] = heapV[l]; c = l;
      }
      heapK[c] = lk; heapV[c] = lv;
    }
    return v;
  };
  const s0 = (ja - j0) * w + (ia - i0), t0 = (jb - j0) * w + (ib - i0);
  dist[s0] = 0; push(0, s0);
  while (heapK.length) {
    const d0 = heapK[0], u = pop();
    if (d0 > dist[u]) continue;
    if (u === t0) break;
    const ui = u % w, uj = (u / w) | 0, gk = (uj + j0) * G + ui + i0, hu = L1.H[gk];
    for (const [di, dj] of NB) {
      const vi = ui + di, vj = uj + dj;
      if (vi < 0 || vj < 0 || vi >= w || vj >= h) continue;
      const gv = (vj + j0) * G + vi + i0;
      if (L1.W[gv] || L1.W[(uj + j0 + (dj >> 1)) * G + ui + i0 + (di >> 1)]) continue;
      const len = Math.hypot(di, dj) * ST, grade = Math.abs(L1.H[gv] - hu) / len, hv = L1.H[gv];
      const s = slopeG[gv];
      let c = 1 + 3 * (grade / 0.13) ** 4 + (s > 0.65 ? (s - 0.65) * 12 : 0) + Math.max(0, hv - 1250) / 300;
      if (shore) { const dw = L1.D[gv]; c *= dw < 25 ? 1.4 : dw < 160 ? 0.55 : dw < 400 ? 0.8 : 1; }
      const nd = d0 + c * len, v = vj * w + vi;
      if (nd < dist[v]) { dist[v] = nd; prev[v] = u; push(nd, v); }
    }
  }
  const pts = [];
  for (let u = t0; u >= 0; u = prev[u]) pts.push([(u % w + i0) * ST - L1.half, ((u / w | 0) + j0) * ST - L1.half]);
  if (pts.length < 2) return null;
  pts.reverse();
  // Chaikin smoothing (keeps the switchbacks, removes the grid stair-steps)
  let p = pts;
  for (let it = 0; it < 3; it++) {
    const q = [p[0]];
    for (let k = 0; k < p.length - 1; k++) {
      const [x0, z0] = p[k], [x1, z1] = p[k + 1];
      q.push([0.75 * x0 + 0.25 * x1, 0.75 * z0 + 0.25 * z1], [0.25 * x0 + 0.75 * x1, 0.25 * z0 + 0.75 * z1]);
    }
    q.push(p[p.length - 1]);
    p = q;
  }
  return p;
}
// lamps along a polyline: spacing (m), lit-stretch pattern for rural roads, denser inside towns
const nearTown = (x, z) => {
  let best = 0;
  for (const t of Object.values(towns)) {
    const d2 = ((x - t.x) ** 2 + (z - t.z) ** 2) / (t.r * t.r);
    if (d2 < 4) best = Math.max(best, Math.exp(-d2 * 0.8));
  }
  return best;
};
let nRoad = 0;
// main roads (cls 2): tight, irregular spacing (+-40%) and intensity so the lamps merge into a continuous
// winding line brighter than the house lights (refs 2, 4), not a runway of evenly spaced identical beads
// (round 5) Swiss roads are lit through the villages and mostly dark between them: outside the towns a main road
// becomes a faint dotted street-class string with long unlit stretches (dark: share of unlit road), so the shore
// roads no longer join the quays into one continuous neon line along the lake (view 7)
// (round 5, pass 2) Away from the villages (remote: tn < 0.15) a road keeps only short lit pockets of 2-6 dim lamps
// (a junction, a bus stop, a farm gate) between long dark stretches, with no lit-road segments; climbing stretches
// (grade > ~6%: switchbacks, the roads up to the terrace villages) are broken up and dim even inside the towns.
// Long lit stretches of equally spaced equal beads read as a necklace running down the screen (north shore road
// Ebligen - Oberried, views 5, 11) and the Brienz switchbacks as letters drawn in lamps (film top-down shot).
function lampsAlong(p, { spacing = 32, rural = 0.0, sodium = 0.75, inten = 1.0, gap = 0, cls = 2, dark = 0.35 } = {}) {
  let acc = rnd() * spacing, lit = false, stretch = -1, gapLen = acc;   // first lamp: starts a lit stretch sized for where it is
  for (let k = 0; k < p.length - 1; k++) {
    const [x0, z0] = p[k], [x1, z1] = p[k + 1];
    const L = Math.hypot(x1 - x0, z1 - z0);
    let s = 0;
    while (s + acc <= L) {
      s += acc;
      const f = s / L, x = x0 + (x1 - x0) * f, z = z0 + (z1 - z0) * f;
      const tn = nearTown(x, z), remote = tn < 0.15;
      const ex = (x1 - x0) / L * 20, ez = (z1 - z0) / L * 20;
      const climb = smoothstep(0.04, 0.08, Math.abs(hAt(x + ex, z + ez) - hAt(x - ex, z - ez)) / 40);
      // (pass 2: counts the whole gap to the previous lamp; 'acc' here is only its last piece on this polyline
      // segment, so the lit / dark stretches ran ~5x longer than meant)
      stretch -= gapLen;
      if (stretch < 0) {
        lit = !lit || (tn > 0.2 && climb < 0.5);
        stretch = lit ? (remote ? 80 + rnd() * 270 : (150 + rnd() * 900) * (1.4 - dark) * (1 - 0.7 * climb))
                      : (remote ? (250 + rnd() * 650) * (0.6 + dark) : (120 + rnd() * 600) * (0.4 + 3 * dark));
      }
      const inTown = tn > 0.3;
      acc = gapLen = spacing * (inTown ? 0.8 : rural > 0 ? 1 : 1.6) * (0.5 + 1.0 * rnd()) * (1 + 0.8 * climb);
      if ((!lit && (rural > 0 || !inTown || climb > 0.5)) || rnd() < gap) continue;
      // mountain roads are unlit between villages: switchbacks above ~950 m only keep lamps near settlements
      if (tn < 0.25 && rnd() < 0.92 * smoothstep(900, 1250, hAt(x, z))) continue;
      // lamp just off the road centre line (both sides in towns; main roads: close to the centre line, so the
      // lit-road segments join into one line)
      const c2 = rural > 0 || tn < 0.15 || climb > 0.5 ? 1 : cls;
      const nx = -(z1 - z0) / L, nz = (x1 - x0) / L, side = c2 > 1 ? (rnd() - 0.5) * 5 : (rnd() < 0.5 ? -1 : 1) * (4 + 3 * rnd());
      const I = inten * (0.55 + 0.75 * rnd()) * (rnd() < 0.04 ? 0.35 : 1) * (c2 < cls ? 0.75 : 1) * (remote ? 0.6 : 1) * (1 - 0.6 * climb);
      // no lit-road segment on remote or climbing lamps (isolated dots, not dashes)
      const dir = remote || climb > 0.5 ? null : Math.atan2(z1 - z0, x1 - x0);
      if (put(x + nx * side, z + nz * side, I, rnd() < sodium ? 0.9 + 0.1 * rnd() : 0.3 + 0.2 * rnd(), 6, c2, dir)) nRoad++;
    }
    acc -= L - s;
  }
}
const ROADS = [
  // [from, to, shore, opts]
  // north shore road (Brienz - Interlaken)
  ['BrienzW', 'Ebligen', 1], ['Ebligen', 'Oberried', 1], ['Oberried', 'Niederried', 1], ['Niederried', 'Ringgenberg', 1], ['Ringgenberg', 'Goldswil', 1], ['Goldswil', 'InterlakenO', 0],
  ['Brienz', 'BrienzW', 1], ['Brienz', 'Kienholz', 1], ['BrienzW', 'Fluhberg', 1], ['Fluhberg', 'Rothornhang', 0, { spacing: 30 }],
  // south shore (Boenigen - Iseltwald - Isch - Sengg - Giessbach - Kienholz)
  // (the hero views' far shore: the road threads each village as its bright winding main street and runs on as
  // a faint dotted string with dark stretches between them; east of Sengg only a forest lane)
  ['Boenigen', 'Iseltwald', 1], ['Iseltwald', 'Isch', 1, { dark: 0.4, spacing: 30 }], ['Isch', 'Sengg', 1, { dark: 0.45, spacing: 30 }],
  ['Sengg', 'Giessbach', 1, { rural: 1, dark: 0.55, spacing: 40 }], ['Giessbach', 'Kienholz', 1, { rural: 1, dark: 0.5 }], ['Boenigen', 'Matten', 0], ['Boenigen', 'InterlakenO', 0],
  // Boedeli + Lake Thun
  ['InterlakenO', 'Interlaken', 0], ['Interlaken', 'Unterseen', 0], ['Interlaken', 'Matten', 0], ['Matten', 'Wilderswil', 0], ['Unterseen', 'Neuhaus', 0],
  ['Neuhaus', 'Merligen', 1, { rural: 1 }], ['Wilderswil', 'Daerligen', 1, { rural: 1 }], ['Daerligen', 'Leissigen', 1], ['Leissigen', 'Krattigen', 0, { rural: 1, spacing: 45 }],
  // valley roads + switchback climbs
  ['Kienholz', 'Aaredelta', 0], ['Aaredelta', 'Brienzwiler', 0], ['Brienzwiler', 'Unterbach', 0], ['Unterbach', 'Meiringen', 0], ['Balm', 'Meiringen', 0], ['Meiringen', 'Innertkirchen', 0],
  ['Brienz', 'Schwanden', 0, { spacing: 38 }], ['Schwanden', 'Hofstetten', 0, { spacing: 40 }], ['Hofstetten', 'Brienzwiler', 0, { spacing: 40 }],
  ['Kienholz', 'Axalp', 0, { spacing: 42 }],
  ['Meiringen', 'Hohfluh', 0, { spacing: 40 }], ['Hohfluh', 'Wasserwendi', 0], ['Wasserwendi', 'Goldern', 0], ['Goldern', 'Reuti', 0],
  ['Brienzwiler', 'Lungern', 0, { spacing: 40 }], ['Lungern', 'Obsee', 1], ['Obsee', 'Kaiserstuhl', 1], ['Kaiserstuhl', 'Giswil', 0, { rural: 1 }], ['Giswil', 'Sachseln', 1], ['Sachseln', 'Sarnen', 1], ['Sarnen', 'Alpnach', 0],
  ['Giswil', 'Soerenberg', 0, { rural: 1, spacing: 50 }], ['Soerenberg', 'Flühli', 0, { rural: 1, spacing: 50 }],
  ['Interlaken', 'Habkern', 0, { spacing: 42 }], ['Unterseen', 'Beatenberg', 0, { spacing: 42 }],
  ['Wilderswil', 'Gsteigwiler', 0], ['Wilderswil', 'Zweiluetschinen', 0], ['Zweiluetschinen', 'Lauterbrunnen', 0], ['Lauterbrunnen', 'Wengen', 0, { spacing: 45 }],
  ['Zweiluetschinen', 'Guendlischwand', 0], ['Guendlischwand', 'Burglauenen', 0, { rural: 1 }], ['Burglauenen', 'Grund', 0], ['Grund', 'Grindelwald', 0],
  ['Wilderswil', 'Saxeten', 0, { rural: 1, spacing: 48 }], ['Zweiluetschinen', 'Isenfluh', 0, { rural: 1, spacing: 48 }],
];
const t0 = Date.now();
SEC = 4;
for (const [a, b, shore, opts = {}] of ROADS) {
  SEC = 20 + ROADS.findIndex(r => r[0] === a && r[1] === b);
  if (!towns[a] || !towns[b]) { console.log('skip road', a, b); continue; }
  const p = route(towns[a], towns[b], !!shore);
  if (p) lampsAlong(p, { spacing: shore ? 22 : 25, sodium: 0.78, ...opts });
}
console.log('roads routed in', Date.now() - t0, 'ms');

// ---------------------------------------------------------------- hamlets, farms, valley-floor scatter (L1)
let nRural = 0;
const span = L1.half - 3 * ST;
// hamlets: clusters of 6-30 lights on gentle ground 650-1500 m
const hamlets = [];
SEC = 5;
for (let n = 0, tries = 0; n < 420 && tries < 40000; tries++) {
  const x = (rnd() * 2 - 1) * span, z = (rnd() * 2 - 1) * span;
  const h = hAt(x, z), s = slopeAt(x, z, 30);
  if (isWater(x, z) || s > 0.38 || h < 600 || h > 1550 || nearTown(x, z) > 0.05) continue;
  if (rnd() > smoothstep(1650, 1100, h)) continue;
  n++;
  const cnt = 6 + Math.floor(rnd() ** 2 * 26), rr = 50 + 70 * rnd();
  for (let k = 0; k < cnt; k++) if (put(x + gauss() * rr, z + gauss() * rr, houseI() * 0.9, houseWarm(), 3)) nRural++;
  hamlets.push({ x, z, h });
}
// lit lanes from the lower hamlets to the nearest town / hamlet (refs: winding lamp strings across the
// valley floors and lower slopes); rural lighting (lit / dark stretches), sparse above ~950 m
{
  const t1 = Date.now(), nodes = Object.values(towns).map(t => ({ x: t.x, z: t.z }));
  let nLane = 0;
  SEC = 6;
  for (const hm of hamlets) {
    if (hm.h > 1150 || rnd() < 0.25) { nodes.push(hm); continue; }
    let best = null, bd = 3500;
    for (const o of nodes) { const d = Math.hypot(o.x - hm.x, o.z - hm.z); if (d < bd && d > 150) { bd = d; best = o; } }
    nodes.push(hm);
    if (!best) continue;
    const p = route(hm, best);
    if (p) { const n0 = nRoad; lampsAlong(p, { spacing: 40, rural: 1, sodium: 0.7, inten: 0.8, cls: 1 }); nLane += nRoad - n0; }
  }
  console.log('lanes', nLane, 'lamps in', Date.now() - t1, 'ms');
}
SEC = 7;
// farms: single lights / pairs on slopes up to ~1650 m (Swiss slopes are dotted with them)
for (let n = 0, tries = 0; n < 10000 && tries < 800000; tries++) {
  const x = (rnd() * 2 - 1) * span, z = (rnd() * 2 - 1) * span;
  if (isWater(x, z)) continue;
  const h = hAt(x, z), s = slopeAt(x, z, 25);
  if (s > 0.75 || h > 1650) continue;
  const p = smoothstep(1650, 1050, h) * smoothstep(0.75, 0.35, s) * (0.25 + 0.75 * smoothstep(-0.15, 0.25, fbm2(x / 3000 + 4, z / 3000 - 2, 3)));
  if (rnd() > p) continue;
  n++;
  const c = rnd() < 0.4 ? 2 : 1;
  for (let k = 0; k < c; k++) if (put(x + gauss() * 15, z + gauss() * 15, 0.2 + 0.65 * rnd() ** 2, houseWarm(), 3)) nRural++;
}
SEC = 8;
// valley floors and shore plains: light industry, rail, scattered houses
for (let j = 2; j < G - 2; j++) for (let i = 2; i < G - 2; i++) {
  const k = j * G + i;
  if (L1.W[k]) continue;
  const h = L1.H[k], s = slopeG[k], dw = L1.D[k];
  if (h > 900 || s > 0.2) continue;
  const x = i * ST - L1.half, z = j * ST - L1.half;
  const v = smoothstep(0.2, 0.05, s) * smoothstep(900, 650, h) * (0.4 + 0.6 * Math.exp(-dw / 2500));
  const exp = v * 70e-6 * ST * ST * smoothstep(-0.1, 0.3, fbm2(x / 900 + 7, z / 900 - 3, 3));
  if (rnd() < exp && put(x + (rnd() - 0.5) * ST, z + (rnd() - 0.5) * ST, houseI(), houseWarm(), 4)) nRural++;
}

// ---------------------------------------------------------------- far field (L0 outside L1): sparse valley towns
let nFar = 0;
SEC = 9;
{
  const L = L0, g = L.g, step = L.step, D = waterDist(L0);
  for (let j = 1; j < g - 1; j++) for (let i = 1; i < g - 1; i++) {
    const k = j * g + i;
    if (L.W[k]) continue;
    const x = -L.half + i * step, z = -L.half + j * step;
    if (Math.abs(x) < L1.half && Math.abs(z) < L1.half) continue;
    const h = L.H[k];
    const slope = Math.hypot(L.H[k + 1] - L.H[k - 1], L.H[k + g] - L.H[k - g]) / (2 * step);
    if (slope > 0.3) continue;
    let s = Math.exp(-D[k] / 1500) + 0.35 * smoothstep(0.12, 0.0, slope) * smoothstep(900, 300, h);
    s *= smoothstep(0.3, 0.08, slope) * smoothstep(1300, 350, h);
    const cl = fbm2(x / 2600 + 11, z / 2600 - 5, 4), cl2 = fbm2(x / 700 - 3, z / 700 + 8, 3);
    s *= smoothstep(-0.1, 0.4, cl) * (0.5 + 0.9 * smoothstep(-0.2, 0.4, cl2));
    let exp = s * 0.00042 * step * step * 0.11;
    while (exp > 0) {
      if (rnd() < Math.min(1, exp)) { lights.push(x + (rnd() - 0.5) * step, h + 4 + rnd() * 6, z + (rnd() - 0.5) * step, 0.4 + 1.6 * rnd() ** 3, rnd() < 0.78 ? 1 : 0.4); tags.push(SEC); nFar++; }
      exp -= 1;
    }
  }
}

// ---------------------------------------------------------------- slope groups above the shore villages
// (round 5) The shore villages the hero lines of sight cross 4-10 km out sit on a narrow strip under steep slopes;
// squeezed onto it they read through the long lenses as one bright ribbon along the water's edge (view 7). Like
// the real ones (Iseltwald's hamlets, the Giessbach hotel terrace, the Oberried / Niederried farm groups) they
// climb the slope: groups of houses along a short contour lane 50-560 m above the lake, each with its own size
// and brightness, a few joined to the village by a dim lane. Through the long lenses the village becomes a 2D
// field of lit pockets with dark forest between (refs 7, 11, 4: towns spread up a hillside, streets winding up)
const TERRACES = { Giessbach: 5, Sengg: 6, Isch: 5, Iseltwald: 6, Oberried: 4, Niederried: 4, Ebligen: 3, Fluhberg: 3, Ringgenberg: 3, Boenigen: 3, Brienz: 4 };
let nTerr = 0;
for (const [name, cnt] of Object.entries(TERRACES)) {
  const t = towns[name];
  if (!t) continue;
  const picked = [];
  for (let tries = 0; tries < 5000 && picked.length < cnt; tries++) {
    const rr = t.r * 0.8 + 1300 * Math.sqrt(rnd()), th = rnd() * 6.283;
    const x = t.x + Math.cos(th) * rr, z = t.z + Math.sin(th) * rr;
    if (!inside(L1, x, z, 3) || isWater(x, z)) continue;
    const h = hAt(x, z), s = slopeAt(x, z, 25);
    if (h < lake + 45 || h > lake + 560 || s > 0.9 || rnd() > smoothstep(0.9, 0.35, s)) continue;
    if (picked.some(p => Math.hypot(p.x - x, p.z - z) < 280)) continue;
    picked.push({ x, z, h });
  }
  for (const p of picked) {
    SEC = 10;
    // contour direction (the lane runs across the slope), the group's own size and brightness
    const gx = hAt(p.x + 30, p.z) - hAt(p.x - 30, p.z), gz = hAt(p.x, p.z + 30) - hAt(p.x, p.z - 30), gl = Math.hypot(gx, gz);
    const ux = gl > 1 ? -gz / gl : 1, uz = gl > 1 ? gx / gl : 0;
    const n = 6 + Math.floor(rnd() ** 1.5 * 36), len = 50 + 4 * n + 80 * rnd(), wd = 18 + 30 * rnd(), br = (0.5 + 0.8 * rnd()) * t.bright;
    const led = rnd() < t.led;
    for (let k = 0; k < n; k++) {
      const a = (rnd() - 0.5) * len * (0.6 + 0.4 * rnd()), onSt = rnd() < 0.35, b = onSt ? (rnd() - 0.5) * 6 : gauss() * wd;
      const px = p.x + ux * a - uz * b, pz = p.z + uz * a + ux * b;
      if (Math.abs(hAt(px, pz) - p.h) > 60) continue;
      const I = onSt ? (0.4 + 0.5 * rnd()) * br : houseI() * 0.7 * br;
      if (put(px, pz, I, onSt ? (led ? 0.1 * rnd() : 0.88 + 0.12 * rnd()) : houseWarm(), onSt ? 5 : 3, onSt ? 1 : 0, onSt ? Math.atan2(uz, ux) : null)) nTerr++;
    }
    // inn / chapel / hotel front: one or two brighter lamps in about half the groups
    if (rnd() < 0.5) for (let k = 0, m = 1 + Math.floor(rnd() * 3); k < m; k++)
      if (put(p.x + gauss() * 15, p.z + gauss() * 15, (1.4 + 1.0 * rnd()) * br, 0.92 + 0.08 * rnd(), 6, 1)) nTerr++;
    // a dim lane down to the village for about a third of them (rural: long dark stretches; more read as a
    // tangle of lit worms over the dark slope)
    if (rnd() < 0.33) {
      const r = route(p, t);
      SEC = 11;
      if (r) { const n0 = nRoad; lampsAlong(r, { spacing: 45, rural: 1, sodium: 0.75, inten: 0.5, cls: 1, dark: 0.65 }); nTerr += nRoad - n0; nRoad = n0; }
    }
  }
}
console.log('slope groups', nTerr);

// ---------------------------------------------------------------- the gorge floor under the ring
// (round 5) From straight above (view 8, the film's top-down shot) the void looks down the slot onto the gorge
// floor ~800 m below the deck (L3, 1.4 km flat floor ~250-450 m out, the Planalp gully beyond it). Refs 8 / the
// top-down shot: warm lights in the cloud gaps through the ring. An alp / railway-station group on the flat
// floor - a few short lit lanes (a small grid read from above), windows, a brighter station front - and the
// Planalp huts down the gully; nothing on the slopes the hero views see.
let nGorge = 0;
SEC = 12;
{
  // (pass 2) three tight groups along one curving lane (ref 8: clusters of round dots strung on a road, dark
  // ground between them); no street directions, so no lit-road segments: drawn on these lone lamps seen from
  // ~1 km they made '+' spikes, and the old four-lane grid read as a star field from above
  const C = [-130, 380], th = 2.094;   // floor centre, lane direction (along the slot, az 210)
  const ux = Math.cos(th), uz = Math.sin(th);
  const lane = a => 22 * Math.sin(a / 55 + 0.6);   // lateral offset of the lane (m) at a (m along)
  const at = (a, b) => [C[0] + ux * a - uz * (lane(a) + b), C[1] + uz * a + ux * (lane(a) + b)];
  // [centre along (m), radius (m), lamps, brightness]: station / inn group, chalet group, barns
  for (const [ca, rr, cnt, br] of [[-60, 26, 34, 1.0], [35, 20, 24, 0.85], [105, 16, 12, 0.7]]) {
    for (let k = 0; k < cnt; k++) {
      const a = ca + gauss() * rr, onLane = rnd() < 0.45, b = onLane ? (rnd() < 0.5 ? -1 : 1) * (4 + 3 * rnd()) : gauss() * rr * 0.7;
      const [px, pz] = at(a, b);
      if (slopeAt(px, pz, 8) > 0.5) continue;
      const I = (onLane ? 0.8 + 0.6 * rnd() : houseI() * 1.1) * br;
      if (put(px, pz, I, onLane && rnd() < 0.2 ? 0.1 * rnd() : onLane ? 0.88 + 0.12 * rnd() : houseWarm(), onLane ? 4 : 3, onLane ? 1 : 0)) nGorge++;
    }
  }
  // a few lamps on the lane between the groups, irregular, the station front
  for (let a = -30; a < 85; a += 18 + 30 * rnd()) {
    const [px, pz] = at(a, (rnd() - 0.5) * 6);
    if (slopeAt(px, pz, 8) < 0.5 && put(px, pz, 0.5 + 0.4 * rnd(), 0.9 + 0.1 * rnd(), 4, 1)) nGorge++;
  }
  for (let k = 0; k < 5; k++) { const [px, pz] = at(-60 + gauss() * 8, gauss() * 6); if (put(px, pz, 2.0 + rnd(), 0.95, 6, 1)) nGorge++; }
  SEC = 13;
  // Planalp huts down the gully (~1230-1300 m)
  for (let k = 0; k < 16; k++) if (put(-530 + gauss() * 22, 880 + gauss() * 30, houseI() * 0.8, houseWarm(), 3)) nGorge++;
}
console.log('gorge floor', nGorge);

// stored intensity also drives terrain.js / clouds.js town-glow map (sum per 98 m cell, blurred): scale it so
// the much denser towns keep that map in its tuned range (peak ~0.5); src/lights.js uGain = 1 / I_SCALE
const I_SCALE = 0.3;
let iSum = 0;
for (let i = 3; i < lights.length; i += 5) { lights[i] *= I_SCALE; iSum += lights[i]; }
const arr = new Float32Array(lights);
fs.writeFileSync(`${OUT}/lights.f32`, Buffer.from(arr.buffer));
if (process.env.TAGS) fs.writeFileSync(process.env.TAGS, Buffer.from(Uint8Array.from(tags)));
console.log('lights', arr.length / 5, { town: nTown, road: nRoad, rural: nRural, far: nFar, intensitySum: Math.round(iSum) });
