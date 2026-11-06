// Terrain build: real DEM (Lake Brienz / Bernese Alps) in 3 nested levels + sculpted near-field rock towers (L3,
// 1.56 m) + a fine near level (L4, 0.39 m) around the ring, baked sky-visibility / horizon-glow AO, concavity,
// water mask and outcrop masks.
// usage: node tools/terrain.mjs [--refetch] [--only-l2] [--only-l3] [--only-l4 [--quick]]
//   --only-l2: L2 (valley carve) + L3 + L4 heights and bakes, L0 / L1 attributes kept; --only-l3: re-sculpt and re-bake L3 + L4 only (~2 min); --only-l4: L4 only (~1 min); --quick: no L4 horizon bake
import { Worker, isMainThread, workerData, parentPort } from 'node:worker_threads';
import fs from 'node:fs';
import os from 'node:os';
import sharp from 'sharp';
import { fetchGrid } from './demlib.mjs';
import { perlin2, perlin3, fbm2, fbm3, ridged3, smoothstep, smin, smax, mulberry32 } from './noise.mjs';

export const CENTER = { lat0: 46.7871, lon0: 8.0466 };   // Brienzer Rothorn
export const LEVELS = [
  { name: 'L0', size: 320000, grid: 1025, zoom: 9 },
  { name: 'L1', size: 50000, grid: 1601, zoom: 12 },
  { name: 'L2', size: 8000, grid: 1281, zoom: 13 },
  { name: 'L3', size: 1600, grid: 1025 },
];
// L4: fine near level at L3 step / 4 (0.39 m) on a world rectangle snapped to L3's vertex lines ([i0, i1] x
// [j0, j1] are L3 vertex indices), so its border vertices lie on L3's edges. It holds every ray of the 11
// reference views that lands where a 1.56 m L3 facet would span > 6 px at 1672 px (world x -145..181,
// z -190..125), plus ~40 m for the film and the seam band (L4 fades into L3's surface over `band` metres).
export const FINE = (() => {
  const L3 = LEVELS[3], s3 = L3.size / (L3.grid - 1), ratio = 4;
  const i0 = 393, i1 = 653, j0 = 364, j1 = 618;
  return { name: 'L4', ratio, i0, i1, j0, j1, step: s3 / ratio, x0: -L3.size / 2 + i0 * s3, z0: -L3.size / 2 + j0 * s3,
    nx: (i1 - i0) * ratio + 1, nz: (j1 - j0) * ratio + 1, band: 18 };
})();
export const EARTH_R = 6371000;
// ring + scene constants shared with the app (keep in sync with src/config.js)
export const SCENE = {
  deckY: 2180,           // ring roof-deck altitude (m)
  ringRo: 55,            // ring outer radius
  sunAz: 214,            // azimuth of sunset (deg from north, clockwise)
  heroAz: 210,           // azimuth the hero camera looks along (through the gorge)
  lakeLevel: 564,
};
const OUT = 'data/terrain';
// bake worker threads: at most half the logical cores (the laptop also renders / runs other agents)
const NW = Math.max(2, Math.min(8, os.cpus().length >> 1));

// ---------------------------------------------------------------- sampling helpers
// grid layout of a level: origin, vertex counts and step (square DEM levels and the rectangular L4 alike)
export function spec(lv) {
  if (lv.nx) return lv;
  const step = lv.size / (lv.grid - 1);
  return { name: lv.name, x0: -lv.size / 2, z0: -lv.size / 2, nx: lv.grid, nz: lv.grid, step };
}
function makeSampler(lv, H) {
  const { x0, z0, nx, nz, step } = spec(lv), x1 = x0 + (nx - 1) * step, z1 = z0 + (nz - 1) * step;
  return {
    step,
    inside: (x, z, m = 0) => x >= x0 + m && x <= x1 - m && z >= z0 + m && z <= z1 - m,
    at(x, z) {
      let fx = (x - x0) / step, fz = (z - z0) / step;
      fx = Math.min(nx - 1.001, Math.max(0, fx)); fz = Math.min(nz - 1.001, Math.max(0, fz));
      const i = Math.floor(fx), j = Math.floor(fz), u = fx - i, v = fz - j, k = j * nx + i;
      return (H[k] * (1 - u) + H[k + 1] * u) * (1 - v) + (H[k + nx] * (1 - u) + H[k + nx + 1] * u) * v;
    },
    // the GPU's triangulation of the cell (index order a c b / b c d: diagonal from (i+1, j) to (i, j+1))
    tri(x, z) {
      let fx = (x - x0) / step, fz = (z - z0) / step;
      fx = Math.min(nx - 1.001, Math.max(0, fx)); fz = Math.min(nz - 1.001, Math.max(0, fz));
      const i = Math.floor(fx), j = Math.floor(fz), u = fx - i, v = fz - j, k = j * nx + i;
      if (u + v <= 1) return H[k] + (H[k + 1] - H[k]) * u + (H[k + nx] - H[k]) * v;
      return H[k + nx + 1] + (H[k + nx] - H[k + nx + 1]) * (1 - u) + (H[k + 1] - H[k + nx + 1]) * (1 - v);
    },
  };
}

// ---------------------------------------------------------------- near-field sculpt
// Local frame: x east, z south, y altitude. Ring centred at (0, deckY, 0), bridges along +/-z.
// South tower (+z) is the taller one (left when looking west).
// pyramid/horn peak: faces = [[azimuthDeg (0 = +x east, 90 = +z south), slope], ...]
function horn(x, z, cx, cz, H, faces) {
  let d = -1e9;
  for (const [a, s] of faces) {
    const r = a * Math.PI / 180;
    d = Math.max(d, ((x - cx) * Math.cos(r) + (z - cz) * Math.sin(r)) * s);
  }
  return H - d;
}
// Outflow valley (round 6): under the ring the gorge falls into a deep valley that runs along the hero view down to
// Lake Brienz (refs 7, 4, 5, 6, 11: past the strut feet the eye goes down to ridges, forested slopes and the lake).
// (The round-5 'outflow ravine' was a straight flat-floored canal with planar 45 deg walls: from the hero cameras
// it read as one flat dark plain.) A stream bed meanders down a concave long profile from ~deck -900 under the
// ring to the lake shore ~3.7 km out; V sides at ~37-45 deg carry interlocking spurs - ridges running down to the
// stream, angled downstream, alternating sides - with V gullies between them, so the view down-valley shows
// overlapping ridge crests, not a plane. t = along the hero view from the ring (m), lat = sculpt z (left +).
// Shared by L2's carve and by the slot floor of the near-field sculpt (shapeHeight), so the two meet in the blend.
// Long profile: gentle for the first 2 km (~1280 -> 1160 m: below the hero views' lower frame edge, so the view
// passes over it to the ridges and the lake), then steeper; from ~2.3 km on the real slopes down to Brienz lie below
// the valley surface and take over (min), so its ridges show in front of the lake.
export const VALLEY = { z0: SCENE.deckY - 900 };
export function valleyH(t, lat) {
  const lake = SCENE.lakeLevel, tc = Math.max(0, t);
  const zc = Math.max(lake - 6, VALLEY.z0 - 0.06 * tc - 0.32 * Math.max(0, tc - 2000));
  // stream: meanders +-110 m, drifting a little left (toward Brienz)
  const lc = (0.08 * tc + 110 * Math.sin(tc / 480 - 0.4) + 50 * perlin2(tc / 900 + 3.3, 0.7)) * smoothstep(120, 700, tc);
  const d = Math.abs(lat - lc), side = lat > lc ? 1 : 0;
  // V: a ~20 m bed, sides ~37 deg steepening outward
  let v = zc + Math.max(0, d - 10) * 0.75 + 0.00025 * d * d;
  // spurs ~650 m apart, offset by half a period between the sides; crests ~80-170 m above the mean side
  const ph = (tc + 0.6 * d) / 650 + 0.5 * side + 0.35 * fbm2(tc / 900 + side * 4.1, d / 700 + 1.3, 3);
  const tri = 1 - Math.abs(2 * (ph - Math.floor(ph)) - 1);
  const amp = (95 + 110 * fbm2(tc / 700 - 2.1, d / 500 + side * 7.7, 2)) * smoothstep(15, 230, d) * smoothstep(-150, 250, tc);
  v += amp * (1.5 * Math.pow(tri, 1.7) - 0.45);
  // secondary ribs and gullies on the sides (~120-200 m), rock ribs where steep
  v += smoothstep(20, 120, d) * (28 * fbm2(tc / 160 + 0.6 * d / 160, d / 260 + side * 3.3, 3) + 12 * fbm2(tc / 55, d / 55, 2));
  return v;
}
// L2 carve: the valley replaces the DEM where it lies below it (its sides meet the real slopes at the rim); the DEM's
// own relief finer than ~150 m (hp: the raw grid minus its box blur) is kept on the valley sides at 1.3x
export function carveValley(A, g, step, half) {
  const Ar = SCENE.heroAz * Math.PI / 180, dx = Math.sin(Ar), dz = -Math.cos(Ar);
  const B = A.slice(), tmp = new Float32Array(g * g), r = 12;
  for (let pass = 0; pass < 2; pass++) {
    for (let j = 0; j < g; j++) for (let i = 0; i < g; i++) {   // box blur along i then j (2 passes ~ tent)
      let s = 0, n = 0;
      for (let a = -r; a <= r; a++) { const ii = Math.min(g - 1, Math.max(0, i + a)); s += B[j * g + ii]; n++; }
      tmp[j * g + i] = s / n;
    }
    for (let j = 0; j < g; j++) for (let i = 0; i < g; i++) {
      let s = 0, n = 0;
      for (let b = -r; b <= r; b++) { const jj = Math.min(g - 1, Math.max(0, j + b)); s += tmp[jj * g + i]; n++; }
      B[j * g + i] = s / n;
    }
  }
  for (let j = 0; j < g; j++) for (let i = 0; i < g; i++) {
    const wx = -half + i * step, wz = -half + j * step, k = j * g + i;
    const t = wx * dx + wz * dz, lat = wx * dz - wz * dx;
    const w = smoothstep(-200, 100, t) * smoothstep(4400, 3700, t) * smoothstep(2600, 1900, Math.abs(lat));
    if (w <= 0) continue;
    const h = A[k], v = valleyH(t, lat) + 1.3 * (h - B[k]) * smoothstep(10, 60, Math.abs(lat));
    A[k] = Math.min(h, h + (v - h) * w);
  }
}

// integer hash -> [0,1)
function hash2(x, z, s = 0) {
  let h = Math.imul(x | 0, 374761393) + Math.imul(z | 0, 668265263) + Math.imul(s, 1442695041) | 0;
  h = Math.imul(h ^ (h >>> 13), 1274126177); h ^= h >>> 16;
  return (h >>> 0) / 4294967296;
}
// 2D Voronoi: writes F1, F2 (cell units), the nearest cell's random ids and its seed point into CELL
const CELL = { f1: 0, f2: 0, id: 0, id2: 0, px: 0, pz: 0 };
function cell2(x, z, seed) {
  const ix = Math.floor(x), iz = Math.floor(z);
  let f1 = 9, f2 = 9, id = 0, id2 = 0, bx = 0, bz = 0;
  for (let b = -1; b <= 1; b++) for (let a = -1; a <= 1; a++) {
    const cx = ix + a, cz = iz + b;
    const px = cx + 0.1 + 0.8 * hash2(cx, cz, seed), pz = cz + 0.1 + 0.8 * hash2(cx, cz, seed + 7);
    const d = (px - x) * (px - x) + (pz - z) * (pz - z);
    if (d < f1) { f2 = f1; f1 = d; id = hash2(cx, cz, seed + 13); id2 = hash2(cx, cz, seed + 29); bx = px; bz = pz; } else if (d < f2) f2 = d;
  }
  CELL.f1 = Math.sqrt(f1); CELL.f2 = Math.sqrt(f2); CELL.id = id; CELL.id2 = id2; CELL.px = bx; CELL.pz = bz;
}
// irregular 1D partition: cell index and bounds of t on a lattice of spacing L with jittered (+-30%) boundaries
const PART = { k: 0, a: 0, b: 0 };
function part1(t, L, seed) {
  const bnd = k => L * (k + 0.6 * (hash2(k, 7, seed) - 0.5));
  let k = Math.floor(t / L);
  if (t < bnd(k)) k--; else if (t >= bnd(k + 1)) k++;
  PART.k = k; PART.a = bnd(k); PART.b = bnd(k + 1);
}
// rectangular brick cells in the sculpt frame (rows along z, bricks along x, each row offset and with its own
// brick length 0.45-1.2 x size): bounds -> RECT {x0, x1, z0, z1, id, id2}
const RECT = { x0: 0, x1: 0, z0: 0, z1: 0, id: 0, id2: 0 };
function rect(x, z, size, seed) {
  part1(z, size, seed);
  const r = PART.k, z0 = PART.a, z1 = PART.b, len = size * (0.45 + 0.75 * hash2(r, 3, seed + 1)), off = len * 3.7 * hash2(r, 5, seed + 2);
  part1(x + off, len, seed + 11 + (r & 1023) * 3);
  RECT.x0 = PART.a - off; RECT.x1 = PART.b - off; RECT.z0 = z0; RECT.z1 = z1;
  RECT.id = hash2(PART.k, r, seed + 13); RECT.id2 = hash2(PART.k, r, seed + 29);
}
// stepped dolomite outcrop: a random subset of cells (size m) stands proud of the snow slope as a block whose
// top is tilted at only `tilt` x the slope (snow-capped benches) and whose downhill side is a cliff (relief grows
// downhill, merges into the slope uphill); crenellated by sub-blocks. (gx, gz) = gradient of the smooth form.
// Returns relief in metres (>= 0).
// (round 5: the cells are bricks aligned with the sculpt axes - the gorge flanks' contours run along x or z, so
// the downhill risers run along the contour as short cliff bands (stepped where it runs diagonally) and the sides
// follow the fall line; the former Voronoi cells stood their downhill corner up as a prow, which L4's crisp
// 0.39 m grid turned into a field of shark fins)
function stepRect(x, z, gx, gz, size, seed, frac, hb, hmax, tilt) {
  // (pass 2: seen from above (view 8) the axis-aligned brick lattice read as city blocks: Voronoi tiles of ~2.7 sizes
  // each turn the lattice by their own +-30 deg about their seed point and shift it by their own offset; blocks are
  // cut along the tile borders, so the outlines are irregular polygons with no shared orientation. The gradient
  // turns with the frame (block heights stay referred to the true fall line).)
  const TS = 2.7 * size, o1 = 0.37 * seed, o2 = -0.53 * seed;
  cell2(x / TS + o1, z / TS + o2, seed + 601);
  const tE = 0.5 * (CELL.f2 - CELL.f1) * TS, ang = 1.05 * (CELL.id - 0.5), ca = Math.cos(ang), sa = Math.sin(ang);
  const qx = (CELL.px - o1) * TS, qz = (CELL.pz - o2) * TS, sh = 7.3 * size * CELL.id2;
  const rx = qx + sh + ca * (x - qx) - sa * (z - qz), rz = qz - 0.61 * sh + sa * (x - qx) + ca * (z - qz);
  const rgx = ca * gx - sa * gz, rgz = sa * gx + ca * gz;
  gx = rgx; gz = rgz;
  // (the brick grid warped, +-0.25 x size over ~1.7 sizes: risers wander and bend)
  x = rx + 0.25 * size * perlin2(rz / (1.7 * size) + 0.3 * seed, rx / (1.7 * size));
  z = rz + 0.25 * size * perlin2(rx / (1.7 * size) - 0.7 * seed, rz / (1.7 * size) + 5.1);
  // rows across the fall line, the narrower bricks along the contour: ribs / pillars down the slope (ref 7's
  // studded flanks), not terraces (wide bricks along the contour read as stairs)
  const swap = Math.abs(gx) > Math.abs(gz);
  rect(swap ? z : x, swap ? x : z, size, seed);
  if (swap) { const a = RECT.x0, b = RECT.x1; RECT.x0 = RECT.z0; RECT.x1 = RECT.z1; RECT.z0 = a; RECT.z1 = b; }
  const on = smoothstep(1 - frac, 1 - frac + 0.06, RECT.id);
  if (on <= 0) return 0;
  const { x0, x1, z0, z1 } = RECT, id2 = RECT.id2;
  // (edges ~0.2-0.5 m wide: crisp risers, two L4 cells)
  const e = Math.min(x - x0, x1 - x, z - z0, z1 - z, tE), edge = smoothstep(0.1, 0.55, e);
  // the block top passes through the smooth form a third of the way up from the centre (seed) ...
  const cx = 0.5 * (x0 + x1), cz = 0.5 * (z0 + z1), gl = Math.hypot(gx, gz) + 1e-6;
  const ux = -gx / gl * 0.17 * (x1 - x0), uz = -gz / gl * 0.17 * (z1 - z0);
  const dc = gx * (cx + ux - x) + gz * (cz + uz - z);
  const hr = hb * (0.55 + 0.9 * id2);
  // ... crenellated by sub-bricks (0.75-1.25 x) and broken by a +-0.4 m irregular top
  rect(x + 13.1, z - 7.7, size * 0.4, seed + 101);
  const sub = 0.75 + 0.5 * RECT.id * smoothstep(0.05, 0.3, Math.min(x - RECT.x0, RECT.x1 - x, z - RECT.z0, RECT.z1 - z));
  return on * edge * Math.min(hmax, Math.max(0, hr * sub + (1 - tilt) * dc + 0.4 * perlin2(x / 2.3 + seed, z / 2.3)));
}
// dolomite joint columns: per-cell protrusion with recessed joints (F2-F1 grooves), in [-1, 1]
function columns(x, z, size, seed) {
  cell2(x / size, z / size, seed);
  const joint = smoothstep(0.0, 0.22, CELL.f2 - CELL.f1);
  return (0.35 + 0.65 * (CELL.id * 2 - 1)) * joint - (1 - joint) * 0.9;
}
// blocky outcrops poking through snow: a random subset of cells is raised with steep sides
function outcrops(x, z, size, seed, frac) {
  cell2(x / size, z / size, seed);
  const on = smoothstep(1 - frac, 1 - frac + 0.12, CELL.id);
  if (on <= 0) return 0;
  const edge = smoothstep(0.03, 0.3, CELL.f2 - CELL.f1);
  return on * edge * (1 - 0.35 * CELL.f1) * (0.6 + 0.8 * hash2(Math.floor(x / size * 3), Math.floor(z / size * 3), seed + 3));
}

// smooth large-scale form in the sculpt frame (peaks, ribs, gorge) - no small detail
export function shapeHeight(x, z) {
  const Yd = SCENE.deckY;
  const r = Math.hypot(x, z);
  // domain warp for organic outlines (weaker near the ring so the gorge stays clean)
  const warpA = 9 + 22 * smoothstep(60, 260, r);
  const wx = x + warpA * fbm2(x / 190 + 3.1, z / 190, 3) * 2 - warpA * 0.5;
  const wz = z + warpA * fbm2(x / 190, z / 190 - 7.7, 3) * 2 - warpA * 0.5;

  // buttress ribs (sharp crests) and couloirs (rounded snow troughs) radiating from a summit;
  // relief grows with distance from the top. Two octaves of irregular azimuthal ridging.
  const ribs = (cx, cz, k, seed) => {
    const dx = wx - cx, dz = wz - cz, rho = Math.hypot(dx, dz);
    const phi = Math.atan2(dz, dx);
    const warp = 1.8 * fbm2(rho / 90 + seed, phi * 1.3 + seed * 2, 3);
    const s1 = Math.abs(Math.sin(phi * k * 0.5 + warp + seed));
    const s2 = Math.abs(Math.sin(phi * k * 1.15 + warp * 1.7 + seed * 3.1 + rho / 70));
    const rib = Math.pow(1 - s1, 1.5) - 0.32 + 0.35 * (Math.pow(1 - s2, 2.0) - 0.25);
    // (kept moderate: big ribs make every flank steeper than the ~55 deg snow limit)
    return rib * Math.min(11, rho * 0.09) * smoothstep(6, 36, rho);
  };
  // south (taller, left in hero view) and north pinnacles: each a broad crest of 3-4 towers joined
  // by notches (small smax radius), not a single cone.
  // faces: [azimuth (0 = +x east toward the hero camera, 90 = +z south), slope]
  // gorge-facing faces steep (60-65 deg), outer / camera-facing flanks 40-47 deg so they hold snow
  // The pinnacles' gorge-side flanks are the tall towers that frame the hero views: summits pulled in
  // toward the gorge so their flanks stand ~40-75 m above the deck at |z| 85-110 beside / behind the
  // bridge ends (the carve below cuts them into near-vertical gorge faces the bridges anchor into);
  // they step down toward the cameras and toward the lake.
  // (camera-facing (+x) faces steep: seen head-on in the top corners of the hero views)
  // (apexes trimmed in pass 2: ref 2 shows the summits only ~0.16 frame above the deck; the hero views'
  // top corners only need the gorge faces at |z| 85-95 to reach ~deck +30)
  // (round 6, view 2: each pinnacle is one pyramid - the main summit (south, north; broader caps) with the flank tower
  // behind the bridge end (southF / northF) - the other horns lowered 12-40 m into shoulders on its ridges: five summits
  // at similar heights made the broad spiky crowns. southF / northF 6 m higher instead of their 3-10 m crest blocks: lower, they left sky in the top
  // corners of views 4, 7 and 11, which view 2's lower summits would need)
  // (round 7: view 2's summits measured against ref 2 - the south pinnacle peaks ~deck +31 just behind the bridge end
  // (southF, the one summit; south / southB / southSub / southC lowered into its shoulders and ridges), the north one
  // ~deck -2 (north / northF; ref 2 puts it at ~deck -15, but the hero views' top-right corners need its gorge face
  // up to ~deck +27: the refs disagree by ~40 m, this splits it). Small spires (blunt caps) and 5 broad ribs instead of
  // 8-9: snowfields between a few arêtes, not a crown of needles)
  // (round 7 pass 2: no spires - their exponential caps plus the crest towers made view 2's 5-6 tip crowns; each horn is
  // a plain pyramid of planar faces (one apex), its base raised by about the spire it lost so the summits stay put)
  const south = horn(wx, wz, -16, 104, Yd + 14, [[270, 1.5], [-60, 1.7], [0, 1.9], [40, 1.6], [90, 1.15], [140, 1.1], [180, 0.75], [220, 1.1]]) + ribs(-16, 104, 5, 1.3);
  const southB = horn(wx, wz, -58, 116, Yd - 15, [[270, 1.4], [0, 1.3], [60, 1.0], [120, 1.2], [180, 1.1], [230, 1.3]]) + ribs(-58, 116, 7, 5.2);
  // (carries the tall wall above the approach path, ref 10)
  const southC = horn(wx, wz, 36, 112, Yd + 19, [[270, 3.0], [-40, 2.2], [0, 1.7], [60, 1.3], [120, 1.6], [180, 1.5]]);
  const southSub = horn(wx, wz, -78, 156, Yd - 11, [[270, 1.8], [0, 1.1], [90, 1.15], [180, 1.5], [225, 1.4], [320, 1.7]]) + ribs(-78, 156, 7, 4.1);
  const north = horn(wx, wz, 2, -100, Yd - 6, [[90, 1.5], [60, 1.7], [0, 1.9], [-40, 1.6], [-90, 1.05], [-140, 1.1], [180, 0.8]]) + ribs(2, -100, 5, 2.7);
  const northB = horn(wx, wz, -42, -112, Yd - 15, [[90, 1.4], [0, 1.3], [-60, 1.0], [-120, 1.2], [180, 1.1], [140, 1.3]]) + ribs(-42, -112, 7, 3.3);
  const northC = horn(wx, wz, 36, -100, Yd - 16, [[90, 1.6], [40, 1.7], [0, 1.8], [-60, 1.2], [-120, 1.6], [180, 1.6]]);
  const northSub = horn(wx, wz, 70, -150, Yd - 38, [[90, 1.6], [0, 1.05], [-90, 1.15], [180, 1.5], [-30, 1.2]]) + ribs(70, -150, 7, 6.3);
  // flank towers behind the bridge ends (cut by the carve into the faces framing the hero views)
  const southF = horn(wx, wz, -36, 90, Yd + 31, [[270, 2.2], [0, 1.9], [60, 1.2], [120, 1.1], [180, 1.3], [230, 1.8]]);
  const northF = horn(wx, wz, -32, -88, Yd - 1, [[90, 2.2], [0, 1.9], [-60, 1.2], [-120, 1.1], [180, 1.3], [130, 1.8]]);
  const sPk = smax(smax(smax(smax(south, southB, 6), southC, 5), southSub, 12), southF, 6);
  const nPk = smax(smax(smax(smax(north, northB, 6), northC, 5), northSub, 12), northF, 6);
  let peaks = smax(sPk, nPk, 10);
  // broad snowy shoulders the pinnacles stand on (N-S ridge, descending away from the notch)
  const massif = Yd - 95 - 0.92 * Math.abs(wx - 0.08 * wz) - 0.3 * Math.max(0, Math.abs(wz) - 140) + ribs(0, 0, 13, 9.1) * 0.6;
  peaks = smax(peaks, massif, 30);
  // foreground shoulders: each pinnacle sends a ridge along the gorge toward the cameras, stepping down
  // (the gorge carve cuts its inner side into the V walls and shelves of the hero views' lower corners)
  // (pass 2: crest higher and the gorge side a broad ~35 deg slope, so the flanks beside the slot stay at /
  // above the lip near the struts and the hero views' lower corners are rock-studded slopes, not a low shelf)
  for (const sg of [1, -1]) {
    const zc = 78 + 0.35 * Math.max(0, wx - 30);
    const hc = Yd + 12 - 0.6 * Math.max(0, wx - 30) - 1.0 * Math.max(0, -20 - wx) + ribs(40, sg * 70, 11, 7.7 + sg) * 0.5;
    const dz = sg * wz - zc;
    peaks = smax(peaks, hc - (dz < 0 ? -0.7 * dz : 1.1 * dz), 10);
  }

  // gorge carve (cross-section in |z|): a near-vertical slot (half-width S, lip at Yd+Lb) under the ring
  // and along the gorge, so the void looks straight down into the cloud sea; from the lip, snowy rock-
  // studded slopes / benches (the strut footings) rise to the foot of the towers (Yd+Lz at |z| = F), then
  // the towers' near-vertical gorge faces. The cleft deepens toward the camera and toward the lake.
  const ax = Math.abs(x);
  const ringZ = smoothstep(75, 30, ax);
  const zs = z + 2.5 * Math.sin(x / 37);
  const az = Math.abs(zs), side = zs >= 0 ? 0 : 1;
  const st = x / 58 + side * 0.41 + 0.18 * perlin2(x / 45, side * 3.3 + 0.5);
  const tri = 1 - Math.abs(2 * (st - Math.floor(st)) - 1);
  // spurs / ribs stepping into the gorge away from the ring (near rib / farther ribs in the hero views)
  const spur = (1 - ringZ) * (8 + 7 * (perlin2(x / 90 + 7, side * 5.1) + 0.5)) * Math.pow(tri, 2.2);
  const front = Math.max(0, x - 40), back = Math.max(0, -x - 50);
  // vertical chimneys (recessed joints) and buttresses of different depth along the sheer faces
  cell2(x / 9.5, side * 13.7 + 0.5, 223);
  const chim = 2.6 * (1 - smoothstep(0.0, 0.22, CELL.f2 - CELL.f1)) - 2.2 * CELL.id;
  const behind = Math.max(0, -x - 22);   // beyond the ring (lake side): the gorge opens out
  // behind the pavilions the towers step in toward the gorge (to |z| ~78), so they stand in the top corners of
  // every hero view right beside / behind the ring's ends; further toward the lake they recede again
  let F = 86 + 3 * perlin2(x / 31 + 1.7, side * 2.9) - 8 * smoothstep(-6, -24, x) + 0.4 * Math.max(0, -x - 70)
    + 0.35 * Math.max(0, x - 15) - 0.5 * spur + chim;
  if (side === 0 && x > 0) F = Math.max(F, pathEdge(x) + 1.5);      // the approach path runs along the tower foot
  const Lz = -8 - 0.55 * Math.max(0, x - 25) - 0.7 * back;
  // in front of the ring (fr -> 1) the slot's lip runs steadily down and in toward the cameras (half-width
  // 55 -> 14 m, lip deck -30 -> ~-60), and from the lip the flank rises outward (a ~56 deg rock wall for
  // ~15 m, then a ~29 deg rock-studded bench up to the shoulders / towers) - never a shelf below the lip, so
  // the hero views see the slot's inner edges converge downward in a V (ref 7) instead of two free-standing
  // pillars; the V never closes, so the hero views look down the slot into the cloud sea.
  // The lip wanders +-5 m (bays / buttresses every ~20 m), so the void's rim is never a straight edge.
  const fr = smoothstep(8, 60, x), xf = Math.max(0, x - 8);
  // (round 6: under the ring the void's walls stand ~1.3 R out - 72 m at the bridges (ref 8), ~65 m at the strut feet
  // (61 m: their shoes sit on short buttresses, sculptClamp), bays between; toward the cameras it narrows 0.6 m per m
  // (the near flanks' V in the hero views); beyond the pavilions (x < -60) it opens out toward the lake 2 m per m and
  // its walls lean back into the valley's sides, the towers receding with it (view 10 looks down into the valley))
  // (round 7 pass 2: in front of the strut feet the void narrows ~1.15 m per m into the hero views' V - two spurs
  // falling from the feet toward the cameras, the left one closer in (refs 4, 7, 11: the notch at the frame bottom
  // ~460 px wide, its centre right of the frame centre); the round-6 0.6 m per m left two free-standing pillars)
  const vN = smoothstep(14, 40, x);
  // (just in front of the feet the spur's edge comes in a further ~6 m and stands ~6 m higher (Lb below): the foot sits
  // on the spur's head, which hides the sheer void walls under the ring that showed as a dark pillar below each foot)
  const S = Math.max(12, 72 - 0.6 * Math.max(0, x) - 0.55 * Math.max(0, x - 14) - 6.5 * Math.exp(-(((x + 10.77) / 10) ** 2))
    - 6 * smoothstep(10, 16, x) * smoothstep(30, 20, x)) + (side ? 4 : -3) * vN
    + 5 * perlin2(x / 23 + 4.1, side * 6.7 + 0.3) * (1 - 0.5 * vN) + 2.0 * Math.max(0, -x - 60)
    - spur * (1 - 0.7 * fr) + chim;
  F = Math.max(F, S + 8 * smoothstep(-40, -70, x));
  const Lb = -30 - 0.33 * xf - 0.9 * back + 4 * perlin2(x / 17 + 2.3, side * 2.3 + 5.1) + 6 * Math.exp(-(((x - 15) / 9) ** 2));
  const kB = Math.max(0.35, (Lz - Lb) / Math.max(8, F - S));
  const dS = az - S;
  const gB = Yd + Lb + dS * kB * (1 - fr) + fr * Math.min(1.5 * dS, 22.5 + 0.55 * (dS - 15));
  // tower gorge face (~76 deg mean) dominated by vertical structure (round 5: the stacked 10-15 m risers read as
  // evenly spaced white stripes): pillars ~5-12 m wide, each standing out or set back by its own 0-4 m and leaning
  // at its own 70-80 deg, split by narrow chimneys, and every ~25 m a deep gully; a pillar carries at most two
  // short ledges at its own random heights and widths, so no ledge line runs across the face
  cell2(x / 8.5 + 0.37 * side, side * 7.3 + 0.5, 211);
  const pId = CELL.id, pId2 = CELL.id2, pJ = CELL.f2 - CELL.f1;
  cell2(x / 26 + 0.61 * side, side * 3.9 + 0.5, 217);
  const gully = (1 - smoothstep(0.0, 0.11, CELL.f2 - CELL.f1)) * smoothstep(0.25, 0.4, CELL.id);
  // (round 7: the pillar offsets, chimneys and gullies fade out where the face runs up into a summit (pkF): their
  // 10-30 m notches cut the pinnacles' crests into the needle crowns of view 2; ref 2's summits are single pyramids
  // whose gorge faces end in one sharp arête)
  const pkF = smoothstep(Yd - 30, Yd + 5, peaks), pkK = 1 - 0.8 * pkF;
  let Fp = F + pkK * (-4.2 * (pId - 0.45) + 2.4 * (1 - smoothstep(0.0, 0.16, pJ)) + 7.5 * gully);
  // (along the approach path the foot stays 1-2.5 m behind the rock edge: a recess there bared the path clamp's
  // smooth 2.2:1 ramp as the view-10 wall)
  if (side === 0 && x > 0) Fp = Math.min(Math.max(Fp, pathEdge(x) + 1.0), Math.max(F, pathEdge(x) + 2.5));
  const kT = 2.8 + 2.9 * pId2 * pkK;
  let uT = (az - Fp) * kT;
  for (let l = 0; l < 2; l++) {
    const r1 = (pId * 7.31 + pId2 * 2.17 + l * 0.37) % 1, r2 = (pId2 * 5.17 + pId * 1.31 + l * 0.71) % 1;
    if ((pId * 3.71 + pId2 * 1.93 + l * 0.5) % 1 < 0.42) continue;
    const hL = 8 + 64 * r1 + 2.5 * perlin2(x / 6.5 + l * 3.1, side * 2.7), wL = (0.7 + 2.6 * r2) * kT;
    uT -= Math.min(wL, Math.max(0, uT - hL));
  }
  const gT = Yd + Lz + uT;
  const upper = smax(gB, gT, 4);
  // slot walls: sheer, from the lip down into the cloud sea
  const lip = Yd + Lb;
  // (in front of the void, x > ~30, the slot's walls lean into a ~65 deg V below the lip: the near walls
  // converge downward in the hero views and hide the sheer walls under the ring below the lip)
  // (the V spans the top ~38 m below the lip, then a sheer ~16 m wide cleft: the gorge never closes)
  // (round 6: beyond the pavilions the walls lean back (~58 deg by x -200) all the way down: the gorge opens into
  // the valley's V sides instead of a sheer cleft)
  // (round 7 pass 2: the lean starts right at the strut feet (x 8-18, was 14-34) and is ~60 deg: the sheer walls under
  // the narrowing spurs were seen as two vertical pillars below the feet; now each spur's face falls toward the axis)
  const kS = 30.0 - 28.3 * smoothstep(3, 15, x) - 28.4 * smoothstep(-60, -200, x), dSl = az - S;
  const Dv = Math.min(18 + 22 * smoothstep(14, 40, x), Math.max(4, S - 8)) + 600 * smoothstep(-60, -200, x);
  let gS = lip + Math.max(dSl * kS, -Dv * kS + (dSl + Dv) * 30.0);
  // (round 6: the sheer walls are tiered dolomite - the round-5 buttress pillars (15 m cells, flat tops) read as
  // organ pipes in view 10, ref 10 has faces of ledges and blocks.) The wall is split along the gorge into columns
  // 4-15 m wide (joints / chimneys between them, 1 in 5 set back 2-6 m); each column is a staircase of risers
  // 6-28 m tall at its own heights, stepping 0.7-4 m toward the void at every ledge (snow lines that never run
  // across the face, blocks standing out where a step is wide); sheer from ~180 m under the lip. Where the walls lean (the V
  // in front, the valley sides behind) the plain lean takes over.
  const fT = smoothstep(12, 26, kS);
  if (fT > 0 && dSl < 8) {
    part1(x + 23.7 * side, 10, 781 + side);
    let ck = PART.k * 7 + side * 50021;
    if (hash2(PART.k, 2, 783 + side) < 0.3) { part1(x + 1.9, 4.5, 787 + side); ck += PART.k * 131; }
    const sd = 789 + side;
    let a = S + (hash2(ck, 1, sd) < 0.2 ? 2 + 4 * hash2(ck, 2, sd) : 0) - 1.2 * hash2(ck, 3, sd), Lp = lip, hS = 0;
    for (let k = 0; ; k++) {
      if (lip - Lp > 180 || k > 24) { hS = Lp + (az - a) * 30; break; }
      const Hb = (k === 0 ? 2 : 6) + 22 * hash2(ck, 10 + k, sd), w = 0.7 + 3.3 * hash2(ck, 40 + k, sd) ** 2;
      if (az >= a - w) { hS = Math.max(Lp - Hb, Lp + (az - a) * 30); break; }
      a -= w; Lp -= Hb;
    }
    gS += (hS - gS) * fT;
  }
  let prof = smin(upper, gS, 3);
  // (round 6: the void has no floor of its own any more: under the ring it falls ~900 m into the head of the outflow
  // valley (valleyH, the same surface as L2's carve), which runs down to the lake)
  prof = Math.max(prof, valleyH(-x, z));
  // the film's underside shot needs a bay in the near flank below its track (see underCap)
  prof = Math.min(prof, underCap(x, z) - 2);
  return smin(peaks, prof, 8);
}

// film 'underside' shot (timeline.js): the camera tracks from ring (0.50, -0.42, 0.78) to (0.86, -0.40, 0.70) (x R)
// = sculpt (42.9, -27.5) deck -23.1 -> (38.5, -47.3) deck -22.0, over the near flank beside the slot's lip.
// underCap = highest rock that keeps >= 15 m (3D) to that track: a bay in the flank under it, ~16.5 m deep under
// the track, its sides rising steeply from ~17 m out
const UNDER = [[42.9, -27.5, -23.1], [38.5, -47.3, -22.0]];
export function underCap(x, z) {
  const [a, b] = UNDER, ex = b[0] - a[0], ez = b[1] - a[1];
  const t = Math.min(1, Math.max(0, ((x - a[0]) * ex + (z - a[1]) * ez) / (ex * ex + ez * ez)));
  const d = Math.hypot(x - a[0] - t * ex, z - a[1] - t * ez);
  if (d >= 26) return 1e9;
  return SCENE.deckY + a[2] + t * (b[2] - a[2]) - 16.5 * Math.sqrt(Math.max(0, 1 - (d / 26) ** 2)) + 1.2 * Math.max(0, d - 17) ** 2;
}

// rotate world (x east, z south) into the sculpt frame: +x toward the hero camera
// (opposite the view direction), +z = left of the view (the taller pinnacle).
// Ring frame (views.js, metres): sculpt x = ring z, sculpt z = -ring x.
export function toSculpt(wxIn, wzIn) {
  const A = SCENE.heroAz * Math.PI / 180, dx = Math.sin(A), dz = -Math.cos(A);
  return [-(wxIn * dx + wzIn * dz), wxIn * dz - wzIn * dx];
}

// strut footings (sculpt frame): ring frame (+-61.06, -25, +-10.77) -> sculpt (+-10.77, -+61.06)
const FOOT_Y = -25, FOOT_Z = 61.06, FOOT_X = 10.77;
// cliff approach path (structure.js buildPath): runs at deck-5.4 along the south pinnacle's gorge
// wall from the -X pavilion's front door (sculpt x 6) to the view-10 camera (sculpt (57, 97.5)).
// pathEdge(x) = sculpt z of the rock edge the path follows (the path sits 1.7 m gorge-side of it)
const pathEdge = x => 79.6 + 21.5 * smoothstep(8, 57, x) + 0.25 * Math.max(0, x - 57);

// clear volumes and guaranteed rock: ring, bridges, pavilions, approach path ledge, strut footings.
// wallF(s): L4's fine rock relief at slope s, carved into the walkway wall (the cap defines that face)
export function sculptClamp(x, z, h, wallF = null) {
  const Yd = SCENE.deckY;
  const r = Math.hypot(x, z), bz = Math.abs(z);
  // the underside shot's camera keeps >= 15 m to the rock (the smooth form already carries the bay)
  h = Math.min(h, underCap(x, z));
  // keep clear volume for the ring (soffit at Yd-9.3)
  // (>= 4.7 m under the soffit edge, rising steeply outside r 57 so the gentler walls get no moat)
  if (r < SCENE.ringRo + 12) h = Math.min(h, Yd - 14 - Math.max(0, 52 - r) * 1.5 + Math.max(0, r - 57) * 2.5);
  // approach path ledge on the south pinnacle: the gorge side drops away below the path (2.5:1 for
  // 4 m, then ~2:1 down to the gorge; gentler near the strut footings), the rock side rises as a
  // ~76 deg wall from path level (cap) over at least a 2.2:1 rock ramp (floor), so the walkway hugs
  // the cliff and the view-10 camera (4 m above the path's outer rail) is never inside rock
  if (z > 0 && x > 0 && x < 90) {
    const inR = smoothstep(2, 9, x) * smoothstep(84, 70, x);
    if (inR > 0) {
      const d = pathEdge(x) - z;                       // > 0: gorge side of the rock edge
      const k2 = 0.4 + 1.6 * smoothstep(12, 24, x);
      // blocky relief on the cut faces (buttresses / recesses of 1-2 m), none right at the path
      // (only on the cliff band next to the path; the slope further below is the plain snow wall)
      const rel = 2.8 * (fbm3(x / 6, z / 6, d * 0.25, 3) - 0.5) * smoothstep(0.5, 3, Math.abs(d)) * smoothstep(16, 8, d);
      // rock side: stacked blocks (pass 2, view 10) - ~6 m risers with ~0.8 m snow ledges, the ledge
      // height shifting from block to block (~3.4 m wide); same 4:1 mean as the plain wall
      let wall = 4.0 * -d;
      if (d < 0) {
        cell2(x / 3.4, -d / 2.2, 331);
        const q = -d / 1.6 + 0.45 * CELL.id, n = Math.floor(q);
        wall = Math.min(wall + 0.3, 6.4 * (n + smoothstep(0.45, 0.9, q - n)) - 2.88 * CELL.id);
        // (L4: fractured columns / blocks on the wall face, none at the path's edge)
        // (outward relief only from ~3 m into the rock, ~12 m above the path: the walkway film camera keeps its
        // 2.5 m to the wall; recesses from 0.3 m)
        // (pass 2: no step-backs here and recesses <= 4 m (2.5 m on the ramp below): structure.js finds the path's line
        // at runtime from the rock edge at the path's level, and deeper recesses pulled the walkway into the rock)
        if (wallF) { const f = wallF(4.0, Yd - 6.3 + wall, 0, false); wall += f > 0 ? f * smoothstep(3.0, 6.0, -d) : Math.max(f, -4) * smoothstep(0.3, 2.0, -d); }
      }
      // (below the 10 m drop under the walkway the cut is a ~45 deg snow slope, not a rock band:
      // it was the dark wall in the left corner of the hero views)
      // (pass 2: the ~45 deg drop ends 16 m out and a ~27 deg bench runs on to the slot's lip - a 1:1 slope
      // all the way down undercut the lip and left the slot wall under the ring a free-standing pillar in
      // the hero views)
      // (round 7 pass 2: from 16 m out the cap falls only 0.2 m per m: the 0.5 bench all the way to the axis cut the left
      // spur of the hero views' V ~15 m below its lip, and the left foot's spur head)
      let cap = rel + (d >= 0 ? Yd - 6.3 - 2.5 * Math.min(d, 4) - Math.min(k2, 1.0) * Math.max(0, Math.min(d, 16) - 4) - 0.2 * Math.max(0, d - 16) : Yd - 6.3 + wall);
      // (L4, round 5: the cut slope below the path was one plain snow plane in the hero views' lower left; ref 7
      // has a rock-studded slope there: stepped outcrops 1-7 m proud (downhill risers, snow-capped tops) and knobs,
      // with fractured faces, from ~6 m below the path's edge)
      if (wallF && d > 4) {
        const kc = d < 16 ? Math.min(k2, 1.0) : 0.5, pe = 21.5 * (smoothstep(7.5, 56.5, x) - smoothstep(8.5, 57.5, x)) + 0.25 * (x > 57 ? 1 : 0);
        // (ref 7 / 4: about half of that slope is rock - towers and steps 2-9 m, snow between)
        const gcx = -kc * pe, gcz = kc, on = smoothstep(5, 9, d);
        // (pass 2: the 13 / 6.5 m flat-topped slabs read as terraces of bricks; ref 7's slope is dense upright fins
        // 2-6 m tall every 3-8 m: smaller blocks (8 / 4.2 / 2.4 m), more of them and taller (about half of the slope
        // is risers: the rock share), tops sloping at ~0.45-0.55 x the slope)
        let o = Math.max(stepRect(x + 2.3, z - 1.1, gcx, gcz, 8, 761, 0.5, 4.5, 9.0, 0.45),
          stepRect(x - 3.9, z + 4.4, gcx, gcz, 4.2, 767, 0.62, 2.8, 6.0, 0.45))
          + stepRect(x + 7.1, z - 5.3, gcx, gcz, 2.4, 773, 0.55, 1.4, 3.0, 0.55);
        o += fineKnobs(x, z, gcx, gcz, Math.max(0.5, kc));
        // fractured faces on the steps (the face frame: columns along x, as the slope's contour)
        if (o > 0.2) o += smoothstep(0.2, 1.5, o) * 0.35 * faceFam(x, z, cap + o, 1.6, 0);
        cap += on * o;
      }
      h = Math.min(h, cap + 300 * (1 - inR));
      const floor = Yd - 5.6 + 2.2 * Math.max(0, -d) - 300 * (1 - inR) - 120 * smoothstep(7, 12, -d)
        + (wallF && d < 0 ? Math.max(-2.5, Math.min(0, wallF(2.2, Yd - 5.6 + 2.2 * -d, 0, false))) * smoothstep(0.3, 2.0, -d) : 0);
      if (d < 0 && d > -12) h = Math.max(h, floor);
    }
  }
  // strut footings: a rock buttress whose top carries the strut shoe (shoe base at FOOT_Y - 1.4),
  // ramping up into the wall behind (fades 12-18 m in) and falling away steeply toward the gorge
  for (const sx of [-1, 1]) for (const sz of [-1, 1]) {
    const v = Math.abs(x - sx * FOOT_X), u = sz * z - FOOT_Z;   // u > 0: into the wall
    if (v > 30 || Math.abs(u) > 30) continue;
    // (gorge side: drops into the sheer slot wall ~3 m beyond the shoe, so the void stays deep)
    // (pass 2: the pad's 1.8:1 ridge into the wall with 1.6:1 planar sides stood as a smooth 20 m tetrahedral fin
    // beside every strut foot in the hero views; ref 7's struts land at the foot of a fractured cliff. Now a buttress
    // block: the shoe ledge, behind it a ~74 deg step 14 m high, then a 0.6:1 top running into the wall; sides
    // ~74 deg; all its faces fractured in L4 (none within ~2 m of the shoe))
    // (round 6: the void's walls stand ~11 m behind the feet, so each buttress is a rib on the wall face: its sides
    // break away 2 m out and plunge near-vertically, so the gap between the two feet under a bridge stays open)
    // (round 7 pass 2: on the camera side of the front feet the buttress no longer plunges sheer (30-40 m per m: the
    // free-standing pillars below the feet in the hero views) but falls ~1.6:1 toward the camera and the axis, into
    // the V spurs of refs 4, 7, 11; on the ring side and under the back feet it stays sheer, the void wide)
    const kF = sx > 0 ? smoothstep(FOOT_X + 1, FOOT_X + 6, x) : 0;
    const top = Yd + FOOT_Y - 0.9 + (u > 2.5 ? Math.min(3.5 * (u - 2.5), 14 + 0.6 * (u - 6.5)) : 0), vv = Math.max(0, v - 4.5);
    let pad = Math.min(top - 3.5 * Math.min(vv, 2) - (30 - 28.4 * kF) * Math.max(0, vv - 2), u < -3 ? top - (40 - 38.4 * kF) * (-u - 3.0) : 1e9) - 200 * smoothstep(12, 18, u);
    if (wallF) {
      const away = smoothstep(1.5, 4, Math.max(v - 4.5, u - 2.5, -u - 3));
      const fS = smoothstep(0, 2, v - 4.5), fB = smoothstep(0.5, 2, u - 2.5) * (1 - fS);
      pad += away * (fS * wallF(3.5, pad, 1) + fB * wallF(3.5, pad, 0));
    }
    // bench cut into the (gentler) wall so the shoe sits on the rock, not buried in it (behind the shoe it may rise
    // as steeply as the buttress: the strut leans out over the gorge)
    let bench = Yd + FOOT_Y - 0.9 + 3.5 * Math.max(0, u - 2.5) + 1.8 * (Math.max(0, v - 4.5) + Math.max(0, -u - 3));
    // (L4: fractured rock on the bench cut, none within ~4 m of the shoe)
    if (wallF) bench += wallF(1.8, bench) * smoothstep(4, 9, Math.max(u - 2.5, v - 4.5, -u - 3));
    h = smax(Math.min(h, bench), pad, 1.2);
  }
  // bridges / pavilions
  if (Math.abs(x) < 9 && bz < 73.5) h = Math.min(h, Yd - 12.5);
  if (Math.abs(x) < 7.5 && bz >= 73 && bz < 84) h = Math.min(h, Yd - 10.2);   // pavilion shelf
  return h;
}

// near-field sculpt split into the smooth large form (h) and the detail layer (det); main() band-
// limits det on the L3 grid before combining, so steep faces never get one-cell shards.
export function sculptParts(wxIn, wzIn) {
  const [x, z] = toSculpt(wxIn, wzIn);
  const Yd = SCENE.deckY;
  const r = Math.hypot(x, z);
  const wBlend = smoothstep(760, 420, r);
  if (wBlend <= 0) return null;

  const h0 = shapeHeight(x, z);
  // gradient of the smooth form (drives the stepped outcrops)
  const e = 2.0;
  const gx = (shapeHeight(x + e, z) - shapeHeight(x - e, z)) / (2 * e), gz = (shapeHeight(x, z + e) - shapeHeight(x, z - e)) / (2 * e);
  const sl = Math.hypot(gx, gz);
  const nearRing = smoothstep(50, 80, r);          // (footings / path / ring are re-clamped after the detail)
  const amp = 0.35 + 0.65 * nearRing;
  // ridge / crest measure of the smooth form (Laplacian over 9 m): towers stand on ribs and crests
  const q = 9;
  const lap = (shapeHeight(x + q, z) + shapeHeight(x - q, z) + shapeHeight(x, z + q) + shapeHeight(x, z - q)) / 4 - h0;
  const ridge = smoothstep(0.5, 3.5, -lap);

  // gentle lumps so the snow surface is never a perfect plane (isotropic, no stretched fluting)
  const lump = (4.5 * (fbm3(x / 55, h0 / 55, z / 55, 3) - 0.5) + 1.6 * (fbm3(x / 17, h0 / 17, z / 17, 2) - 0.5)) * amp;
  let det = lump;
  // stepped outcrops (3 scales): dark blocks 2-8 m proud of the snow, snow-capped benches on top;
  // more and taller on ribs, fewer in couloirs; on steep faces they make buttresses and ledges
  const sF = 1 + 0.6 * ridge, steepCut = 1 - 0.45 * smoothstep(1.6, 2.6, sl);
  // (pass 2: dense small outcrops on the 25-55 deg mid slopes - the hero views' lower corners are
  // rock-studded slopes in the refs, ~40% rock, not open snowfields)
  const midS = smoothstep(0.32, 0.6, sl) * smoothstep(1.9, 1.3, sl) * smoothstep(40, 70, r);
  // (round 5: on the outer flanks - view 2's pinnacle bases, 150-300 m out - the 19 m blocks read as cow-print
  // blotches; there the rock breaks up into the smaller scales, ref 2's fine speckle of outcrops)
  const outer = smoothstep(140, 220, r);
  // (round 7: the pinnacles' upper flanks below the summits - ref 2's big snowfields between the arêtes - carry half
  // the large / medium outcrops; the gorge faces (steep) and the hero views' lower corners (low) keep theirs)
  const snowF = 1 - 0.5 * smoothstep(Yd - 90, Yd - 40, h0) * smoothstep(1.5, 1.1, sl) * smoothstep(80, 110, r);
  det += amp * steepCut * (
    stepRect(x, z, gx, gz, 19, 51, 0.22 * sF * (1 - 0.7 * outer) * snowF, 3.2, 10.0, 0.30) +
    stepRect(x + 5.1, z + 2.3, gx, gz, 9.5, 61, (0.22 * sF + 0.22 * midS - 0.08 * outer) * snowF, 2.0 + 1.5 * midS, 6.0, 0.30) +
    stepRect(x - 3.7, z + 8.9, gx, gz, 5.2, 67, 0.18 * sF + 0.25 * midS + 0.12 * outer, 1.1 + 1.2 * midS, 4.0, 0.35));
  // towers on ribs and on the pinnacle crests: taller, narrower blocks with notches between them
  // (round 6: on the summits only along the arêtes (ridge), not over every crest cell: the field of 3-10 m blocks on
  // the whole summit area was the 'hedgehog' crown of view 2; the faces between the arêtes stay plain snowfields;
  // on the summits a quarter of the cells, 0-7 m, so a summit is a rocky point, not a cluster of needles)
  const crest = smoothstep(Yd - 40, Yd + 5, h0) * smoothstep(0.3, 0.75, ridge);
  const tw = Math.max(ridge * smoothstep(1.0, 0.0, Math.abs(sl - 1.2)), crest) * nearRing;
  if (tw > 0) {
    cell2(x / 11, z / 11, 83);
    const notch = 1 - smoothstep(0.0, 0.2, CELL.f2 - CELL.f1);
    const tall = smoothstep(0.35 + 0.2 * crest, 0.45 + 0.2 * crest, CELL.id) * (3 + 7 * CELL.id2 - 3 * crest) * smoothstep(0.03, 0.2, CELL.f2 - CELL.f1) * (1 - 0.5 * CELL.f1)
      * (1 - 0.6 * smoothstep(Yd - 70, Yd - 20, h0));
    // (round 7 pass 2: none within ~30 m of the two summits - one apex per peak in view 2, ref 2)
    const sumK = smoothstep(14, 32, Math.min(Math.hypot(x + 35, z - 97), Math.hypot(x + 21, z + 82)));
    det += tw * sumK * (tall - 4 * notch * crest);
  }
  return { x, z, w: wBlend, h: h0, det, lump, ridge: Math.max(ridge, crest * smoothstep(0.2, 1.5, -lap)), cv: lap };
}

// 3D Voronoi (cell units): F1, F2, the nearest cell's random ids and its seed offset from the sample -> CELL3
const CELL3 = { f1: 0, f2: 0, id: 0, id2: 0, ox: 0, oy: 0, oz: 0 };
function cell3(x, y, z, seed) {
  const ix = Math.floor(x), iy = Math.floor(y), iz = Math.floor(z);
  let f1 = 9, f2 = 9, id = 0, id2 = 0, ox = 0, oy = 0, oz = 0;
  for (let c = -1; c <= 1; c++) for (let b = -1; b <= 1; b++) for (let a = -1; a <= 1; a++) {
    const cx = ix + a, cy = iy + b, cz = iz + c, hk = cx + 1031 * cy;
    const dx = cx + 0.1 + 0.8 * hash2(hk, cz, seed) - x, dy = cy + 0.1 + 0.8 * hash2(hk, cz, seed + 3) - y, dz = cz + 0.1 + 0.8 * hash2(hk, cz, seed + 7) - z;
    const d = dx * dx + dy * dy + dz * dz;
    if (d < f1) { f2 = f1; f1 = d; id = hash2(hk, cz, seed + 13); id2 = hash2(hk, cz, seed + 29); ox = dx; oy = dy; oz = dz; } else if (d < f2) f2 = d;
  }
  CELL3.f1 = Math.sqrt(f1); CELL3.f2 = Math.sqrt(f2); CELL3.id = id; CELL3.id2 = id2; CELL3.ox = ox; CELL3.oy = oy; CELL3.oz = oz;
}

// ---------------------------------------------------------------- L4 fine relief (0.39 m grid)
// Rock: fractured dolomite as a displacement along the normal turned into height (x sqrt(1 + s^2), s = local
// slope), from 3D Voronoi blocks on the surface (x, y, z): ~3.5 m wide, ~2x taller than wide (columnar on the
// faces), each one a planar slab of its own tilt and standing-out (angular facets, lit / shadowed sides), open
// joints between them; ~1.5 m sub-blocks; deep cracks on some joints. y = surface height (m).
// Grooves are kept >= ~0.6 m wide (1.5 cells): finer cracks belong to the material.
export function fineRock(x, z, s, y = 0) {
  const sC = Math.min(4.5, s), nk = Math.sqrt(1 + sC * sC);
  // (plan-cell columns stretched up the faces by the slope read as a bed of nails: blocks live in 3D now)
  cell3(x / 3.5, y / 7.0, z / 3.5, 401);
  const j1 = smoothstep(0.0, 0.16, CELL3.f2 - CELL3.f1);
  // slab: stands out 0-0.7 m, its face tilted by up to ~+-0.35 m across the block (seed offset . random axis)
  const tilt = 0.5 * (CELL3.ox * (CELL3.id2 - 0.5) + CELL3.oz * (CELL3.id - 0.5) + 0.6 * CELL3.oy * (CELL3.id2 - CELL3.id));
  let n = (0.75 * CELL3.id - 0.15 + tilt) * j1 - 0.4 * (1 - j1);
  // sub-blocks ~1.5 m
  cell3(x / 1.5 + 3.3, y / 2.6, z / 1.5 - 8.1, 409);
  const j2 = smoothstep(0.0, 0.35, CELL3.f2 - CELL3.f1);
  n += (0.3 * CELL3.id - 0.1) * j2 - 0.1 * (1 - j2);
  // deep cracks / narrow chimneys on some ~10 m joints (~0.7 m wide, ~1.2 m deep), mostly vertical
  cell3(x / 10 + 0.3, y / 30, z / 10 - 0.6, 419);
  n -= 1.2 * (1 - smoothstep(0.0, 0.07, CELL3.f2 - CELL3.f1)) * smoothstep(0.3, 0.45, CELL3.id2);
  return n * nk;
}
// Steep faces (L4): fractured dolomite built in the face's own frame - columns along the contour (u, ~1.5-7 m wide),
// each split into blocks at its own random bedding heights (5-20 m apart, tilted / wavy per column); every column and
// block stands out or is set back by its own horizontal offset, turned into height by the slope (h = y + offset * s).
// A block's top clips its face (min) and the surface is the highest block face there (max): a ledge where a block
// stands out of the one above, a plain riser where it is set back, never a notch. (Plan-space displacement x slope
// made a bed of needles on the faces: every plan cell boundary across the fall line became a spike and a pit.)
// Column edges are vertical planes (u = const) carrying cracks / chimneys; fine fluting runs down the face.
// fam 0: columns along x (faces looking +-z: the gorge faces, the walkway wall), 1: along z. y = surface height.
// soft: without the 1-2 cell grooves (column-edge cracks, slab joints) - for the clamps' second pass (fine3), which is
// not band-limited: its crisp cracks x the slope were the white knife-blade shards on the walkway wall
export function faceFam(x, z, y, s, fam, soft = false, steps = true) {
  const u = fam ? z : x, w = fam ? -x : z, CW = 4.2, Yd = SCENE.deckY;
  // (rows of columns change every ~70 m across the contour: rare enough to never cut one face)
  cell2(u / CW + 0.31 * fam, w / 70 + 5.3 * fam, 503 + 6 * fam);
  const cId = CELL.id, cId2 = CELL.id2, uc = CELL.px * CW, key = Math.floor(cId * 1e6);
  const eM = 0.5 * (CELL.f2 - CELL.f1) * CW;            // ~ metres to the column's edge
  const sC = Math.min(4.5, s);
  // column offset +-0.7 m; ~1 in 5 columns set far back (recesses / chimneys between the pillars); each column leans
  // by its own +-1.4 deg (+-1.5 m at most), so neighbours are never parallel flutes ...
  let dc = 1.4 * (cId - 0.5) - (cId2 < 0.2 ? 1.0 + 6 * cId2 : 0)
    + (steps ? Math.max(-1.5, Math.min(1.5, 0.05 * (((cId * 9.17) % 1) - 0.5) * (y - Yd + 40))) : 0);
  // ... on pillars of random width (pass 2: the fixed ~11 m pillars read as organ pipes): an irregular partition
  // at ~9 m (3.6-14 m wide), a third of the pillars split again at ~3.6 m; each stands out / is set back by +-1.8 m,
  // 1 in 4 a deep 4 m recess, and has 1-2 step-backs of 1.5-5 m at its own heights (abrupt steps in the
  // silhouettes and short ledges, refs 7 / 4 / 2)
  const pSeed = 541 + fam + 17 * Math.floor(w / 90 + 0.37);
  part1(u, 9, pSeed);
  let pk = PART.k * 31;
  if (hash2(PART.k, 3, pSeed) < 0.33) { part1(u + 1.3, 3.6, pSeed + 5); pk += PART.k; }
  const pId = hash2(pk, 5, pSeed), pId2 = hash2(pk, 7, pSeed);
  dc += 3.6 * (pId - 0.5) - (pId2 < 0.25 ? 2.5 : 0);
  const r1 = hash2(pk, 11, pSeed), r2 = hash2(pk, 13, pSeed), r3 = hash2(pk, 17, pSeed);
  const yS1 = Yd - 130 + 175 * r1, sb1 = steps && r2 < 0.75 ? 1.5 + 2.5 * r3 : 0;
  const yS2 = yS1 + 9 + 30 * r2, sb2 = steps && r3 < 0.45 ? 1.0 + 1.5 * r1 : 0;
  // ... and split into slabs ~1.6 m wide standing out / back by +-0.3 m (the close-ups' fractured face)
  cell2(u / 1.6 + 2.9 + fam, w / 40 + 0.7, 551 + fam);
  dc += 0.6 * (CELL.id - 0.5) - (soft ? 0 : 0.35 * (1 - smoothstep(0.0, 0.18, CELL.f2 - CELL.f1)));
  // bedding: spacing 3.5-14.5 m, phase and +-10 deg tilt per column, +-0.7 m waviness per bed
  const T = 3.5 + 11 * ((cId * 7.13) % 1), tl = 0.36 * (((cId * 3.71) % 1) - 0.5), base = cId2 * T + tl * (u - uc);
  const bed = n => base + n * T + 1.4 * perlin2(u / 5.5 + n * 0.71, (key % 97) + n * 1.37 + 0.5);
  const n0 = Math.floor((y - base) / T), nr = Math.ceil((Math.abs(dc) + sb1 + sb2 + 0.5) * sC / T) + 1;
  let h = -1e9, lo = 1e9;
  for (let n = n0 - nr; n <= n0 + nr; n++) {
    const b0 = bed(n);
    // (blocks whose bed lies above a step-back height are set back: a ledge where the pillar steps in)
    const hb = y + (dc + 0.9 * (hash2(key, n, 521) - 0.5) - (b0 > yS1 ? sb1 : 0) - (b0 > yS2 ? sb2 : 0)) * sC;
    lo = Math.min(lo, hb);
    if (hb >= b0) h = Math.max(h, Math.min(bed(n + 1), hb));
  }
  if (h < -1e8) h = lo;
  // cracks on the column edges (0.35-0.95 m wide, 0.4-2 m deep) and fluting down the face
  const cw = 0.35 + 0.6 * cId2, crack = soft ? 0 : (1 - smoothstep(cw * 0.4, cw, eM)) * (0.4 + 1.6 * ((cId * 5.3) % 1));
  const rough = 0.22 * perlin2(u / 2.1 + 3.3 * fam, y / 3.4) + 0.1 * perlin2(u / 0.9 + 1.7, y / 7);
  return h - y + (rough - crack) * sC;
}
// both families, fw = weight of family 0 (from the face's orientation)
function faceRock(x, z, y, s, fw) {
  let r = 0;
  if (fw > 0.01) r += fw * faceFam(x, z, y, s, 0);
  if (fw < 0.99) r += (1 - fw) * faceFam(x, z, y, s, 1);
  return r;
}
// stepped knobs on the mid slopes (ref 7's studded flanks): small blocks whose tops tilt at ~0.35-0.4 x the
// slope (snow caps) and whose downhill sides are 0.5-3 m risers (dark rock); (gx, gz) = local gradient
function fineKnobs(x, z, gx, gz, s) {
  const dens = smoothstep(0.35, 0.8, s) * smoothstep(3.6, 2.2, s);
  if (dens <= 0) return 0;
  return dens * (stepRect(x, z, gx, gz, 4.4, 441, 0.4, 0.9, 3.0, 0.5) + stepRect(x + 1.7, z - 2.9, gx, gz, 2.3, 447, 0.45, 0.5, 1.8, 0.55));
}
// wind-packed snow on the gentle ground: long smooth drifts across the wind (from ~WSW), gentle undulation;
// 0.1-0.4 m, nothing at the grid scale (no quilting)
function fineSnow(x, z) {
  const u = x * 0.88 + z * 0.47, v = -x * 0.47 + z * 0.88;
  return 0.55 * fbm2(u / 17 + 1.3, v / 6.5 - 2.1, 3) + 0.16 * perlin2(u / 5.5 + 3.1, v / 2.4) + 0.06 * perlin2(x / 1.9, z / 1.9 + 7.7);
}
// all of L4's relief at sculpt (x, z), surface height y: s / (gx, gz) local slope / gradient of the sculpt surface
// at ~2 m, o its block relief above the snow lumps (m), ridge crest measure, cv concavity of the smooth form
// (> 0 hollows). Returns [total, snow-surface part] in metres of height.
// The fractured rock covers only bare ground - faces > ~50-60 deg, the sculpt's outcrop blocks and the knobs -
// so the snow between them stays smooth (a rough field everywhere bared every 45 deg slope in dark speckle)
// fw: weight of the faces' column family 0 (contour along x), from the smooth form's orientation
// (round 5 pass 3: steep ground (> ~45-60 deg) takes faceRock, gentler bare ground the 3D blocks at <= ~60 deg's
// height scale - the 3D blocks x the full slope were the needle field on every face)
// sB: slope over ~4 m (face relief gate and scale; the fine 3D blocks' height scale too)
export function fineRelief(x, z, y, gx, gz, s, o, ridge, cv, fw = 0.5, sB = s) {
  const knobs = fineKnobs(x, z, gx, gz, s);
  const rw = Math.min(1, Math.max(smoothstep(1.15, 1.75, s), smoothstep(0.8, 2.5, o)) + smoothstep(0.3, 1.0, knobs));
  const snow = (1 - rw) * fineSnow(x, z);
  let rel = snow + knobs;
  // (bare rock steeper than ~30 deg takes the face-frame relief (its offsets scale with the slope); the 3D blocks,
  // whose cell boundaries across the fall line stand up as spikes on any slope, only on the gentler block tops)
  if (rw > 0.001) {
    const wF = smoothstep(0.55, 1.2, sB);
    rel += rw * ((wF < 1 ? (1 - wF) * fineRock(x, z, Math.min(sB, 0.8), y) : 0) + (wF > 0 ? wF * faceRock(x, z, y, sB, fw) : 0));
  }
  // jagged crests: on ridges and tower tops ~3.6 m blocks stand up to ~3 m proud, notches between them
  if (ridge > 0.05 && rw > 0.05) {
    cell2(x / 3.6 - 2.2, z / 3.6 + 4.4, 457);
    const e = CELL.f2 - CELL.f1;
    rel += ridge * rw * (3.0 * CELL.id * CELL.id * smoothstep(0.04, 0.22, e) - 1.1 * (1 - smoothstep(0.0, 0.16, e)));
  }
  // scree / rubble aprons at the foot of the faces (hollows on moderate slopes): stones 0.4-1.3 m under the snow
  const apron = smoothstep(0.4, 2.2, cv) * smoothstep(0.25, 0.55, s) * smoothstep(1.3, 0.85, s);
  if (apron > 0) {
    cell2(x / 1.15 + 9.1, z / 1.15 - 3.3, 463);
    rel += apron * 0.5 * (0.3 + 0.7 * CELL.id) * Math.max(0, 1 - 1.4 * CELL.f1 * CELL.f1);
  }
  return [rel, snow];
}

export function sculptHeight(wxIn, wzIn, base) {
  const p = sculptParts(wxIn, wzIn);
  if (!p) return base;
  return base + (sculptClamp(p.x, p.z, p.h + p.det) - base) * p.w;
}

// separable binomial [1 2 1] / 4 blur of an nx x nz grid, in place (edges clamped)
function binomial3(A, nx, nz) {
  const t = new Float32Array(Math.max(nx, nz));
  for (let j = 0; j < nz; j++) {
    const o = j * nx;
    for (let i = 0; i < nx; i++) t[i] = A[o + i];
    for (let i = 0; i < nx; i++) A[o + i] = 0.25 * (t[Math.max(0, i - 1)] + 2 * t[i] + t[Math.min(nx - 1, i + 1)]);
  }
  for (let i = 0; i < nx; i++) {
    for (let j = 0; j < nz; j++) t[j] = A[j * nx + i];
    for (let j = 0; j < nz; j++) A[j * nx + i] = 0.25 * (t[Math.max(0, j - 1)] + 2 * t[j] + t[Math.min(nz - 1, j + 1)]);
  }
}

// remove one-vertex spikes / pits left after the clamps (a vertex may exceed its 8 neighbours'
// range by at most tol); genuine cliff steps are untouched since they have neighbours on both levels
function despike(A, g, mask, tol) {
  const src = A.slice();
  let n = 0;
  for (let j = 1; j < g - 1; j++) for (let i = 1; i < g - 1; i++) {
    const k = j * g + i;
    if (!mask[k]) continue;
    let mx = -1e9, mn = 1e9;
    for (let b = -1; b <= 1; b++) for (let a = -1; a <= 1; a++) {
      if (!a && !b) continue;
      const v = src[k + b * g + a]; if (v > mx) mx = v; if (v < mn) mn = v;
    }
    const h = src[k];
    if (h > mx + tol) { A[k] = mx + tol; n++; } else if (h < mn - tol) { A[k] = mn - tol; n++; }
  }
  return n;
}

// ---------------------------------------------------------------- main
async function main() {
  fs.mkdirSync(OUT, { recursive: true });
  const refetch = process.argv.includes('--refetch');
  const H = {};
  for (const lv of LEVELS.slice(0, 3)) {
    const raw = `${OUT}/${lv.name}.raw.f32`;
    if (!refetch && fs.existsSync(raw)) H[lv.name] = new Float32Array(fs.readFileSync(raw).buffer.slice(0));
    else {
      console.log('fetch', lv.name);
      H[lv.name] = await fetchGrid({ ...CENTER, size: lv.size, zoom: lv.zoom, grid: lv.grid });
      fs.writeFileSync(raw, Buffer.from(H[lv.name].buffer));
    }
  }
  // carve the outflow valley into L2 (stays inside L2's extent, away from its blended border)
  {
    const lv = LEVELS[2];
    carveValley(H.L2, lv.grid, lv.size / (lv.grid - 1), lv.size / 2);
  }
  // blend each inner level's border toward the outer level so seams match
  for (let li = 1; li < 3; li++) {
    const lv = LEVELS[li], outer = makeSampler(LEVELS[li - 1], H[LEVELS[li - 1].name]);
    const g = lv.grid, step = lv.size / (g - 1), half = lv.size / 2, A = H[lv.name];
    for (let j = 0; j < g; j++) for (let i = 0; i < g; i++) {
      const x = -half + i * step, z = -half + j * step;
      const e = Math.max(Math.abs(x), Math.abs(z)) / half;
      const w = smoothstep(0.86, 1.0, e);
      if (w > 0) A[j * g + i] = A[j * g + i] * (1 - w) + outer.at(x, z) * w;
    }
  }
  // --only-l4: keep the baked L3 (heights, outcrop mask, attributes) and re-sculpt / re-bake L4 only;
  // --quick (with --only-l4): no horizon bake for L4 (sky / glow visibility taken from L3) - geometry previews
  const onlyL4 = process.argv.includes('--only-l4'), quick = onlyL4 && process.argv.includes('--quick');
  if (onlyL4) {
    H.L3 = new Float32Array(fs.readFileSync(`${OUT}/L3.f32`).buffer.slice(0));
    H.RK3 = new Uint8Array(fs.readFileSync(`${OUT}/L3.rock`));
  }
  // L3 sculpt (the sculpt function runs in worker threads, rows split between them)
  if (!onlyL4) {
    const lv = LEVELS[3], s2 = makeSampler(LEVELS[2], H.L2);
    const g = lv.grid, step = lv.size / (g - 1), half = lv.size / 2, A = new Float32Array(g * g);
    const t0 = Date.now();
    const sab = () => new SharedArrayBuffer(g * g * 4);
    const bufs = { S: sab(), Dt: sab(), Wb: sab(), PX: sab(), PZ: sab(), Lm: sab() };
    const nW = NW, rowsPer = Math.ceil(g / nW);
    await Promise.all([...Array(nW)].map((_, w) => new Promise((res, rej) => {
      const wk = new Worker(new URL(import.meta.url), { workerData: { mode: 'sculpt', bufs, j0: w * rowsPer, j1: Math.min(g, (w + 1) * rowsPer) } });
      wk.on('message', res); wk.on('error', rej);
    })));
    const S = new Float32Array(bufs.S), Dt = new Float32Array(bufs.Dt), Wb = new Float32Array(bufs.Wb);
    const PX = new Float32Array(bufs.PX), PZ = new Float32Array(bufs.PZ), Lm = new Float32Array(bufs.Lm), B = new Float32Array(g * g);
    for (let j = 0; j < g; j++) for (let i = 0; i < g; i++) B[j * g + i] = s2.at(-half + i * step, -half + j * step);
    console.log(`L3 sculpt ${((Date.now() - t0) / 1000).toFixed(1)}s`);
    // band-limit the detail (half-strength binomial 3x3): block edges stay crisp (one cell wide) without
    // one-cell shards on the steep faces
    const Db = Dt.slice();
    for (let j = 1; j < g - 1; j++) for (let i = 1; i < g - 1; i++) {
      const k = j * g + i;
      if (!Wb[k]) continue;
      Db[k] = 0.5 * Dt[k] + 0.5 * (4 * Dt[k] + 2 * (Dt[k - 1] + Dt[k + 1] + Dt[k - g] + Dt[k + g]) + Dt[k - g - 1] + Dt[k - g + 1] + Dt[k + g - 1] + Dt[k + g + 1]) / 16;
    }
    const mask = new Uint8Array(g * g);
    for (let k = 0; k < g * g; k++) {
      if (Wb[k] > 0) { A[k] = B[k] + (sculptClamp(PX[k], PZ[k], S[k] + Db[k]) - B[k]) * Wb[k]; mask[k] = 1; }
      else A[k] = B[k];
    }
    let nd = 0;
    for (let it = 0; it < 2; it++) nd += despike(A, g, mask, 0.6);
    console.log('L3 despiked vertices', nd);
    H.L3 = A;
    // outcrop mask for the land shader (L3.rock, 1 byte/vertex): 0 = not sculpted (shader falls back
    // to a procedural outcrop field), 1..255 = baked block / tower relief above the snow surface (the
    // smooth form plus the gentle snow lumps, which must not read as rock), 0..6 m
    const RK = new Uint8Array(g * g);
    for (let k = 0; k < g * g; k++) {
      if (Wb[k] < 0.5) continue;
      const smooth = B[k] + (sculptClamp(PX[k], PZ[k], S[k] + Lm[k]) - B[k]) * Wb[k];
      RK[k] = 1 + Math.round(254 * Math.min(1, Math.max(0, (A[k] - smooth) / 6)));
    }
    fs.writeFileSync(`${OUT}/L3.rock`, Buffer.from(RK.buffer));
    H.RK3 = RK;
  }
  // L4 fine near level (0.39 m): the sculpt evaluated at full resolution (blocks crisp, not band-limited) plus
  // fineRelief (fractured columns / blocks, knobs, crest spires, rubble, snow drifts) and the clamps; its outer
  // `band` metres fade into L3's triangulated surface, so the border vertices (on L3's edges) match L3 exactly
  {
    const F = FINE, nx = F.nx, nz = F.nz, N = nx * nz, t0 = Date.now();
    const sab = () => new SharedArrayBuffer(N * 4);
    const bufs = { S: sab(), Dt: sab(), Lm: sab(), PX: sab(), PZ: sab(), Rg: sab(), Cv: sab(), GX: sab(), GZ: sab(), FW: sab(), SB: sab(), A: sab(), Sm: sab() };
    await runRows(nz, 'fine1', bufs);
    const S = new Float32Array(bufs.S), Dt = new Float32Array(bufs.Dt), GX = new Float32Array(bufs.GX), GZ = new Float32Array(bufs.GZ);
    const FW = new Float32Array(bufs.FW);
    // local gradient of the sculpt surface (smooth form + blocks) over +-3 cells (~2.3 m), turned into the
    // sculpt frame (toSculpt is a rotation: the gradient maps like the coordinates); FW = face family weight from
    // the smooth form's gradient over +-10 cells (~3.9 m): 1 where the contour runs along x
    const Ar = SCENE.heroAz * Math.PI / 180, dx = Math.sin(Ar), dz = -Math.cos(Ar);
    const hs = (i, j) => S[Math.min(nz - 1, Math.max(0, j)) * nx + Math.min(nx - 1, Math.max(0, i))];
    // where the smooth form is steeper than ~50-63 deg the sculpt's plan-space blocks (stepped outcrops, towers;
    // Dt minus the snow lumps) fade out: sampled crisply at 0.39 m they stood as needles on every face - the
    // face-frame relief (faceRock) builds those faces instead
    const Lm = new Float32Array(bufs.Lm);
    for (let j = 0; j < nz; j++) for (let i = 0; i < nx; i++) {
      const sw = hs(i + 10, j) - hs(i - 10, j), sv = hs(i, j + 10) - hs(i, j - 10), k = j * nx + i;
      const ax = Math.abs(-dx * sw - dz * sv), az = Math.abs(dz * sw - dx * sv);
      FW[k] = smoothstep(0.38, 0.62, az / (ax + az + 1e-6));
      const wD = smoothstep(1.2, 2.0, Math.hypot(sw, sv) / (20 * F.step));
      Dt[k] = Lm[k] + (Dt[k] - Lm[k]) * (1 - wD);
    }
    // SB: slope of the same surface over +-10 cells (~3.9 m): decides / scales the face relief, whose metre-scale
    // horizontal offsets only fit faces taller than a few metres (on the 1-3 m risers of the outcrop blocks the
    // +-1.2 m slope said "face" and the offsets x slope stood up as 10 m needles)
    const SB = new Float32Array(bufs.SB);
    const hb = (i, j) => { const k = Math.min(nz - 1, Math.max(0, j)) * nx + Math.min(nx - 1, Math.max(0, i)); return S[k] + Dt[k]; };
    for (let j = 0; j < nz; j++) for (let i = 0; i < nx; i++) {
      const gw = (hb(i + 3, j) - hb(i - 3, j)) / (6 * F.step), gv = (hb(i, j + 3) - hb(i, j - 3)) / (6 * F.step);
      GX[j * nx + i] = -dx * gw - dz * gv; GZ[j * nx + i] = dz * gw - dx * gv;
      SB[j * nx + i] = Math.hypot(hb(i + 10, j) - hb(i - 10, j), hb(i, j + 10) - hb(i, j - 10)) / (20 * F.step);
    }
    await runRows(nz, 'fine2', bufs);
    const A = new Float32Array(bufs.A), Sm = new Float32Array(bufs.Sm);
    // band-limit (two binomial 3x3 passes, sigma ~1 cell) and clamp again: the faces' steps run along the sculpt
    // axes, 30 deg off the grid, and a sharp metre-scale step across the grid's diagonals is a sawtooth of thin
    // tall triangles (read as a field of needles); ~1 m wide steep ramps keep the blocks' edges crisp at 1080p
    for (let it = 0; it < 2; it++) binomial3(A, nx, nz);
    await runRows(nz, 'fine3', bufs);
    console.log(`L4 sculpt ${((Date.now() - t0) / 1000).toFixed(1)}s (${nx} x ${nz} = ${(N / 1e6).toFixed(2)}M vertices)`);
    // seam band: fade into L3's surface / outcrop mask toward the border
    const s3 = makeSampler(LEVELS[3], H.L3), g3 = LEVELS[3].grid, st3 = LEVELS[3].size / (g3 - 1);
    const RK = new Uint8Array(N);
    for (let j = 0; j < nz; j++) for (let i = 0; i < nx; i++) {
      const k = j * nx + i, x = F.x0 + i * F.step, z = F.z0 + j * F.step;
      const w = smoothstep(0, F.band, Math.min(i, nx - 1 - i, j, nz - 1 - j) * F.step);
      const b = s3.tri(x, z);
      A[k] = b + (A[k] - b) * w;
      let rk = Math.min(1, Math.max(0, (A[k] - Sm[k]) / 6));
      if (w < 1) {
        const fi = (x + LEVELS[3].size / 2) / st3, fj = (z + LEVELS[3].size / 2) / st3;
        const r3 = Math.max(0, H.RK3[Math.round(fj) * g3 + Math.round(fi)] - 1) / 254;
        rk = r3 + (rk - r3) * w;
      }
      RK[k] = 1 + Math.round(254 * rk);
    }
    H.L4 = A;
    fs.writeFileSync(`${OUT}/L4.rock`, Buffer.from(RK.buffer));
  }
  // write heights
  for (const lv of onlyL4 ? [FINE] : [...LEVELS, FINE]) fs.writeFileSync(`${OUT}/${lv.name}.f32`, Buffer.from(H[lv.name].buffer));

  // water masks (flat lake surfaces). The 5x5 window is clamped at the grid edge: skipping the two outer
  // rows left a straight 2-cell strip of 'land' (and shore lights) across Lake Brienz at the L2 / L1 seam
  const water = {};
  for (const lv of LEVELS) {
    const g = lv.grid, A = H[lv.name], W = new Uint8Array(g * g);
    for (let j = 0; j < g; j++) for (let i = 0; i < g; i++) {
      const h0 = A[j * g + i];
      if (h0 > 1200 || h0 < 1) continue;
      let mn = h0, mx = h0;
      for (let b = -2; b <= 2; b++) for (let a = -2; a <= 2; a++) {
        const v = A[Math.min(g - 1, Math.max(0, j + b)) * g + Math.min(g - 1, Math.max(0, i + a))];
        if (v < mn) mn = v; if (v > mx) mx = v;
      }
      if (mx - mn < 0.6) W[j * g + i] = 255;
    }
    water[lv.name] = W;
  }
  water.L4 = new Uint8Array(FINE.nx * FINE.nz);   // (all far above the lake)

  // AO bake with workers
  const shared = {};
  for (const lv of [...LEVELS, FINE]) {
    const sab = new SharedArrayBuffer(H[lv.name].byteLength);
    new Float32Array(sab).set(H[lv.name]);
    shared[lv.name] = sab;
  }
  const nW = NW;
  const onlyL3 = process.argv.includes('--only-l3'), onlyL2 = process.argv.includes('--only-l2');
  const packs = {};
  if (onlyL3) packs.L2 = new Uint8Array(fs.readFileSync(`${OUT}/L2.attr`));
  if (onlyL2) packs.L1 = new Uint8Array(fs.readFileSync(`${OUT}/L1.attr`));
  if (onlyL4) packs.L3 = new Uint8Array(fs.readFileSync(`${OUT}/L3.attr`));
  for (const lv of (onlyL4 ? [FINE] : onlyL3 ? [LEVELS[3], FINE] : onlyL2 ? [LEVELS[2], LEVELS[3], FINE] : [...LEVELS, FINE])) {
    const t0 = Date.now();
    const { nx, nz } = spec(lv), N = nx * nz;
    const outSab = new SharedArrayBuffer(N * 2);
    const rowsPer = Math.ceil(nz / nW);
    if (!quick) await Promise.all([...Array(nW)].map((_, w) => new Promise((res, rej) => {
      const wk = new Worker(new URL(import.meta.url), { workerData: { shared, level: lv.name, j0: w * rowsPer, j1: Math.min(nz, (w + 1) * rowsPer), outSab } });
      wk.on('message', res); wk.on('error', rej);
    })));
    else {   // (quick: L3's visibility, bilinear)
      const o = new Uint8Array(outSab), s3 = LEVELS[3].size / (LEVELS[3].grid - 1), g3 = LEVELS[3].grid, P3 = packs.L3;
      for (let j = 0; j < nz; j++) for (let i = 0; i < nx; i++) {
        const fx = (FINE.x0 + i * FINE.step + 800) / s3, fz = (FINE.z0 + j * FINE.step + 800) / s3;
        const oi = Math.floor(fx), oj = Math.floor(fz), u = fx - oi, v = fz - oj, k0 = oj * g3 + oi;
        for (const c of [0, 1]) o[(j * nx + i) * 2 + c] = Math.round((P3[k0 * 4 + c] * (1 - u) + P3[(k0 + 1) * 4 + c] * u) * (1 - v) + (P3[(k0 + g3) * 4 + c] * (1 - u) + P3[(k0 + g3 + 1) * 4 + c] * u) * v);
      }
    }
    const ao = new Uint8Array(outSab);
    // pack RGBA: sky vis, glow vis, water, concavity (1..255, 128 = planar; 0 = no data)
    const cv = concavity(lv, H[lv.name]);
    const pack = new Uint8Array(N * 4);
    for (let k = 0; k < N; k++) { pack[k * 4] = ao[k * 2]; pack[k * 4 + 1] = ao[k * 2 + 1]; pack[k * 4 + 2] = water[lv.name][k]; pack[k * 4 + 3] = cv[k]; }
    // L4's seam band: sky / glow visibility and concavity fade into L3's, like its heights
    if (lv === FINE) {
      const P3 = packs.L3, g3 = LEVELS[3].grid, st3 = LEVELS[3].size / (g3 - 1), h3 = LEVELS[3].size / 2;
      for (let j = 0; j < nz; j++) for (let i = 0; i < nx; i++) {
        const w = smoothstep(0, FINE.band, Math.min(i, nx - 1 - i, j, nz - 1 - j) * FINE.step);
        if (w >= 1) continue;
        const fx = (FINE.x0 + i * FINE.step + h3) / st3, fz = (FINE.z0 + j * FINE.step + h3) / st3;
        const oi = Math.min(g3 - 2, Math.floor(fx)), oj = Math.min(g3 - 2, Math.floor(fz)), u = fx - oi, v = fz - oj, k0 = oj * g3 + oi;
        for (const c of [0, 1, 3]) {
          const o = (P3[k0 * 4 + c] * (1 - u) + P3[(k0 + 1) * 4 + c] * u) * (1 - v) + (P3[(k0 + g3) * 4 + c] * (1 - u) + P3[(k0 + g3 + 1) * 4 + c] * u) * v;
          const k = (j * nx + i) * 4 + c;
          pack[k] = Math.round(o + (pack[k] - o) * w);
        }
      }
    }
    // border: sky / glow visibility fade to the outer level's (each level's horizon search has its own
    // resolution and reach, so flat lake surfaces showed a brightness step along the level seam)
    const li = LEVELS.indexOf(lv), outerPack = li > 0 ? packs[LEVELS[li - 1].name] : null;
    if (outerPack) {
      const g = lv.grid;
      const olv = LEVELS[li - 1], og = olv.grid, ostep = olv.size / (og - 1), ohalf = olv.size / 2;
      const step = lv.size / (g - 1), half = lv.size / 2;
      for (let j = 0; j < g; j++) for (let i = 0; i < g; i++) {
        const x = -half + i * step, z = -half + j * step;
        const w = smoothstep(0.9, 1.0, Math.max(Math.abs(x), Math.abs(z)) / half);
        if (w <= 0) continue;
        let fx = (x + ohalf) / ostep, fz = (z + ohalf) / ostep;
        fx = Math.min(og - 1.001, Math.max(0, fx)); fz = Math.min(og - 1.001, Math.max(0, fz));
        const oi = Math.floor(fx), oj = Math.floor(fz), u = fx - oi, v = fz - oj, k0 = oj * og + oi;
        for (const c of [0, 1]) {
          const o = (outerPack[k0 * 4 + c] * (1 - u) + outerPack[(k0 + 1) * 4 + c] * u) * (1 - v) + (outerPack[(k0 + og) * 4 + c] * (1 - u) + outerPack[(k0 + og + 1) * 4 + c] * u) * v;
          const k = (j * g + i) * 4 + c;
          pack[k] = Math.round(pack[k] * (1 - w) + o * w);
        }
      }
    }
    packs[lv.name] = pack;
    fs.writeFileSync(`${OUT}/${lv.name}.attr`, Buffer.from(pack.buffer));
    console.log(`AO ${lv.name} ${((Date.now() - t0) / 1000).toFixed(1)}s`);
    await previews(lv, H[lv.name], pack);
  }

  // village lights are generated separately: node tools/lights.mjs
  const { ratio, i0, i1, j0, j1, ...fine } = FINE;
  fs.writeFileSync(`${OUT}/meta.json`, JSON.stringify({ CENTER, LEVELS, FINE: fine, SCENE, EARTH_R }, null, 1));
}

// multi-scale concavity (ring-average minus centre, divided by radius): gullies / ledge backs
// hold snow (> 128), ribs / arêtes / block edges are scoured (< 128)
// (L4: the same 3.1 m / 10.9 m radii as L3 plus 1.2 m: the gaps between blocks and the cracks)
function concavity(lv, A) {
  const { nx, nz, step } = spec(lv), out = new Uint8Array(nx * nz);
  const radii = lv.name === 'L4' ? [[3, 0.3], [8, 0.35], [28, 0.35]] : lv.name === 'L3' ? [[2, 0.5], [7, 0.5]] : [[1, 0.6], [3, 0.4]];
  const at = (i, j) => A[Math.min(nz - 1, Math.max(0, j)) * nx + Math.min(nx - 1, Math.max(0, i))];
  for (let j = 0; j < nz; j++) for (let i = 0; i < nx; i++) {
    const h = A[j * nx + i];
    let k = 0;
    for (const [R, w] of radii) {
      const d = Math.round(R * 0.7071);
      const avg = (at(i + R, j) + at(i - R, j) + at(i, j + R) + at(i, j - R) + at(i + d, j + d) + at(i - d, j + d) + at(i + d, j - d) + at(i - d, j - d)) / 8;
      k += w * (avg - h) / (R * step);
    }
    out[j * nx + i] = Math.round(Math.min(255, Math.max(1, 128 + k * 160)));
  }
  return out;
}

async function previews(lv, A, pack) {
  const { nx: gx, nz: gz, step } = spec(lv), img = Buffer.alloc(gx * gz * 3);
  for (let j = 0; j < gz; j++) for (let i = 0; i < gx; i++) {
    const k = j * gx + i;
    const hx = A[j * gx + Math.min(gx - 1, i + 1)] - A[j * gx + Math.max(0, i - 1)];
    const hz = A[Math.min(gz - 1, j + 1) * gx + i] - A[Math.max(0, j - 1) * gx + i];
    let nx = -hx / (2 * step), nz = -hz / (2 * step), ny = 1; const l = Math.hypot(nx, ny, nz);
    const shade = Math.max(0, (nx * 0.6 + ny * 0.6 - nz * 0.5) / l);
    const ao = pack[k * 4] / 255;
    const wtr = pack[k * 4 + 2] > 0;
    img[k * 3] = wtr ? 30 : 255 * shade * ao * 0.9;
    img[k * 3 + 1] = wtr ? 60 : 255 * shade * ao * 0.9;
    img[k * 3 + 2] = wtr ? 140 : 255 * shade * ao;
  }
  await sharp(img, { raw: { width: gx, height: gz, channels: 3 } }).resize(Math.min(gx, 1024)).png().toFile(`${OUT}/${lv.name}_preview.png`);
}

// ---------------------------------------------------------------- village lights
function buildLights(H, water) {
  const rnd = mulberry32(42);
  const lights = [];
  const lake = SCENE.lakeLevel;
  for (const name of ['L1', 'L0']) {
    const lv = LEVELS.find(l => l.name === name), g = lv.grid, A = H[name], W = water[name];
    const step = lv.size / (g - 1), half = lv.size / 2;
    // distance to water (cells), chamfer transform
    const D = new Float32Array(g * g).fill(1e9);
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
    const cellArea = step * step;
    for (let j = 1; j < g - 1; j++) for (let i = 1; i < g - 1; i++) {
      const k = j * g + i;
      if (W[k]) continue;
      const x = -half + i * step, z = -half + j * step;
      if (name === 'L0' && Math.abs(x) < 25000 && Math.abs(z) < 25000) continue; // L1 covers it
      const h = A[k];
      const sx = (A[k + 1] - A[k - 1]) / (2 * step), sz = (A[k + g] - A[k - g]) / (2 * step);
      const slope = Math.hypot(sx, sz);
      if (slope > 0.32) continue;
      const dW = D[k] * step;
      const rel = h - lake;
      // suitability: shoreline towns + valley floors, fading with altitude and slope
      let s = Math.exp(-dW / 900) * 1.0 + 0.35 * smoothstep(0.12, 0.0, slope) * smoothstep(900, 300, h);
      s *= smoothstep(0.32, 0.08, slope) * smoothstep(1300, 350, h);
      // town clustering
      const cl = fbm2(x / 2600 + 11, z / 2600 - 5, 4);
      const cl2 = fbm2(x / 700 - 3, z / 700 + 8, 3);
      s *= smoothstep(-0.12, 0.35, cl) * (0.55 + 0.9 * smoothstep(-0.2, 0.4, cl2));
      const density = s * 0.00042; // lights per m^2 at s=1  (~420 / km^2)
      let expected = density * cellArea * (name === 'L0' ? 0.35 : 1);
      while (expected > 0) {
        if (rnd() < Math.min(1, expected)) {
          const jx = x + (rnd() - 0.5) * step, jz = z + (rnd() - 0.5) * step;
          const warm = rnd() < 0.78 ? 1 : 0;
          const inten = 0.4 + 1.6 * rnd() ** 3;
          lights.push(jx, h + 4 + rnd() * 6, jz, inten, warm);
        }
        expected -= 1;
      }
      // shoreline road: lights near the water's edge
      if (name === 'L1' && dW > 15 && dW < 70 && rel < 60 && rnd() < 0.55) {
        lights.push(x + (rnd() - 0.5) * step, h + 6, z + (rnd() - 0.5) * step, 0.9 + 0.4 * rnd(), 1);
      }
    }
  }
  const arr = new Float32Array(lights);
  fs.writeFileSync(`${OUT}/lights.f32`, Buffer.from(arr.buffer));
  console.log('lights', arr.length / 5);
}

// ---------------------------------------------------------------- worker: horizon AO
function workerSculpt() {
  const { bufs, j0, j1 } = workerData;
  const lv = LEVELS[3], g = lv.grid, step = lv.size / (g - 1), half = lv.size / 2;
  const S = new Float32Array(bufs.S), Dt = new Float32Array(bufs.Dt), Wb = new Float32Array(bufs.Wb);
  const PX = new Float32Array(bufs.PX), PZ = new Float32Array(bufs.PZ), Lm = new Float32Array(bufs.Lm);
  for (let j = j0; j < j1; j++) for (let i = 0; i < g; i++) {
    const k = j * g + i, p = sculptParts(-half + i * step, -half + j * step);
    if (p) { S[k] = p.h; Dt[k] = p.det; Wb[k] = p.w; PX[k] = p.x; PZ[k] = p.z; Lm[k] = p.lump; }
  }
  parentPort.postMessage('done');
}

// L4 pass 1: the sculpt's parts at every L4 vertex (rows j0..j1)
function workerFine1() {
  const { bufs, j0, j1 } = workerData, F = FINE, B = {};
  for (const key in bufs) B[key] = new Float32Array(bufs[key]);
  for (let j = j0; j < j1; j++) for (let i = 0; i < F.nx; i++) {
    const k = j * F.nx + i, p = sculptParts(F.x0 + i * F.step, F.z0 + j * F.step);
    if (!p) continue;   // (never: L4 lies inside the sculpt's full-weight disc, r < 420 m)
    B.S[k] = p.h; B.Dt[k] = p.det; B.Lm[k] = p.lump; B.PX[k] = p.x; B.PZ[k] = p.z; B.Rg[k] = p.ridge; B.Cv[k] = p.cv;
  }
  parentPort.postMessage('done');
}
// L4 pass 2: fine relief (needs pass 1's local gradient) and the clamps -> heights A and snow surface Sm
function workerFine2() {
  const { bufs, j0, j1 } = workerData, F = FINE, B = {};
  for (const key in bufs) B[key] = new Float32Array(bufs[key]);
  for (let j = j0; j < j1; j++) for (let i = 0; i < F.nx; i++) {
    const k = j * F.nx + i, x = B.PX[k], z = B.PZ[k], gx = B.GX[k], gz = B.GZ[k];
    const y = B.S[k] + B.Dt[k];
    const [rel, snow] = fineRelief(x, z, y, gx, gz, Math.hypot(gx, gz), B.Dt[k] - B.Lm[k], B.Rg[k], B.Cv[k], B.FW[k], B.SB[k]);
    // (the clamps' cut faces - walkway wall, path ramp, strut benches - run along x: face family 0 at the cut's
    // own height and slope; the cut slope below the path gets outcrops)
    B.A[k] = sculptClamp(x, z, y + rel, (s, yy, fam = 0, st = true) => faceFam(x, z, yy, s, fam, false, st));
    B.Sm[k] = sculptClamp(x, z, B.S[k] + B.Lm[k] + snow);
  }
  parentPort.postMessage('done');
}
// L4 pass 3: the clamps again on the band-limited heights (the blur must not fill clear volumes or sink floors)
function workerFine3() {
  const { bufs, j0, j1 } = workerData, F = FINE, B = {};
  for (const key in bufs) B[key] = new Float32Array(bufs[key]);
  for (let j = j0; j < j1; j++) for (let i = 0; i < F.nx; i++) {
    const k = j * F.nx + i, x = B.PX[k], z = B.PZ[k];
    // (the soft face relief: the crisp sub-2 m cracks re-cut here, unblurred, were knife-blade shards)
    B.A[k] = sculptClamp(x, z, B.A[k], (s, yy, fam = 0, st = true) => faceFam(x, z, yy, s, fam, true, st));
  }
  parentPort.postMessage('done');
}
// run a row-parallel worker mode over `rows` rows
async function runRows(rows, mode, bufs) {
  const nW = NW, per = Math.ceil(rows / nW);
  await Promise.all([...Array(nW)].map((_, w) => new Promise((res, rej) => {
    const wk = new Worker(new URL(import.meta.url), { workerData: { mode, bufs, j0: w * per, j1: Math.min(rows, (w + 1) * per) } });
    wk.on('message', res); wk.on('error', rej);
  })));
}

function workerMain() {
  if (workerData.mode === 'sculpt') return workerSculpt();
  if (workerData.mode === 'fine1') return workerFine1();
  if (workerData.mode === 'fine2') return workerFine2();
  if (workerData.mode === 'fine3') return workerFine3();
  const { shared, level, j0, j1, outSab } = workerData;
  const ALL = [...LEVELS, FINE];
  const S = ALL.map(lv => makeSampler(lv, new Float32Array(shared[lv.name])));
  const li = ALL.findIndex(l => l.name === level), lv = spec(ALL[li]);
  const A = new Float32Array(shared[level]), g = lv.nx, gz = lv.nz, step = lv.step;
  const out = new Uint8Array(outSab);
  const finest = (x, z) => { for (let k = S.length - 1; k >= 0; k--) if (S[k].inside(x, z, S[k].step)) return S[k].at(x, z); return 0; };
  const NDIR = li === 0 ? 8 : 16;
  const maxD = [60000, 30000, 15000, 8000, 8000][li];
  // (eye 1.5 m above the vertex; L4 0.5 m, so the gaps between its blocks and its cracks get their occlusion)
  const eye = li === 4 ? 0.5 : 1.5;
  const sunAz = SCENE.sunAz * Math.PI / 180;
  const sunDir = [Math.sin(sunAz), -Math.cos(sunAz)]; // (east, south) components
  const dirs = [...Array(NDIR)].map((_, d) => { const a = (d + 0.5) / NDIR * Math.PI * 2; return [Math.cos(a), Math.sin(a)]; });
  for (let j = j0; j < j1; j++) for (let i = 0; i < g; i++) {
    const k = j * g + i, x = lv.x0 + i * step, z = lv.z0 + j * step, h = A[k] + eye;
    const im = Math.max(0, i - 1), ip = Math.min(g - 1, i + 1), jm = Math.max(0, j - 1), jp = Math.min(gz - 1, j + 1);
    const sx = (A[j * g + ip] - A[j * g + im]) / ((ip - im) * step), sz = (A[jp * g + i] - A[jm * g + i]) / ((jp - jm) * step);
    let vis = 0;
    const horizonIn = dir => {
      let maxT = -10, d = step * 0.8;
      while (d < maxD) {
        const px = x + dir[0] * d, pz = z + dir[1] * d;
        const t = (finest(px, pz) - h - d * d / (2 * EARTH_R)) / d;
        if (t > maxT) maxT = t;
        d *= 1.09; d += step * 0.15;
      }
      return Math.atan(maxT);
    };
    for (const dir of dirs) {
      const aP = Math.atan(sx * dir[0] + sz * dir[1]);         // tangent plane elevation in this dir
      const aH = Math.max(aP, horizonIn(dir));
      const sP = Math.sin(aP), sH = Math.sin(aH);
      vis += (1 - sH) / Math.max(1e-3, 1 - sP);
    }
    vis /= NDIR;
    const aSun = horizonIn(sunDir);
    const glow = 1 - smoothstep(0.0, 0.16, aSun);
    out[k * 2] = Math.round(255 * Math.min(1, Math.max(0, vis)));
    out[k * 2 + 1] = Math.round(255 * glow);
  }
  parentPort.postMessage('done');
}

if (isMainThread) { if (process.argv[1] && process.argv[1].endsWith('terrain.mjs')) main(); }
else workerMain();
