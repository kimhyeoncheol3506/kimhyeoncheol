// Fetch AWS Terrain Tiles (terrarium) and resample to a local metric grid.
// usage: node tools/dem.mjs <name> <lat> <lon> <sizeMeters> <zoom> <grid> [offsetEastM offsetSouthM]
// Output: data/dem/<name>.f32 (grid*grid float32 heights, row-major, row = +Z (south), col = +X (east))
//         data/dem/<name>.json, data/dem/<name>_shade.png
import sharp from 'sharp';
import fs from 'node:fs';
import path from 'node:path';

const [, , name, latS, lonS, sizeS, zoomS, gridS, offES = '0', offSS = '0'] = process.argv;
const lat0 = +latS, lon0 = +lonS, size = +sizeS, zoom = +zoomS, grid = +gridS;
const offE = +offES, offS = +offSS; // grid center offset from origin (meters)
const dir = 'data/dem', tileDir = path.join(dir, 'tiles');
fs.mkdirSync(tileDir, { recursive: true });

const R = 6378137;
const mPerDegLat = 111132.92 - 559.82 * Math.cos(2 * lat0 * Math.PI / 180);
const mPerDegLon = 111412.84 * Math.cos(lat0 * Math.PI / 180);
const n = 2 ** zoom;
const tileXf = lon => (lon + 180) / 360 * n;
const tileYf = lat => { const r = lat * Math.PI / 180; return (1 - Math.log(Math.tan(r) + 1 / Math.cos(r)) / Math.PI) / 2 * n; };

// local (x east, z south) -> lat/lon
const toLL = (x, z) => [lat0 - z / mPerDegLat, lon0 + x / mPerDegLon];

const half = size / 2;
const [latN] = toLL(0, offS - half), [latS2] = toLL(0, offS + half);
const [, lonW] = toLL(offE - half, 0), [, lonE] = toLL(offE + half, 0);
const tx0 = Math.floor(tileXf(lonW)), tx1 = Math.floor(tileXf(lonE));
const ty0 = Math.floor(tileYf(latN)), ty1 = Math.floor(tileYf(latS2));
console.log(`tiles z${zoom}: x ${tx0}..${tx1}, y ${ty0}..${ty1} (${(tx1 - tx0 + 1) * (ty1 - ty0 + 1)})`);

const tiles = new Map();
async function getTile(x, y) {
  const key = `${zoom}_${x}_${y}`;
  if (tiles.has(key)) return tiles.get(key);
  const f = path.join(tileDir, key + '.png');
  if (!fs.existsSync(f)) {
    for (let attempt = 0; attempt < 4; attempt++) {
      try {
        const res = await fetch(`https://s3.amazonaws.com/elevation-tiles-prod/terrarium/${zoom}/${x}/${y}.png`);
        if (!res.ok) throw new Error('HTTP ' + res.status);
        fs.writeFileSync(f, Buffer.from(await res.arrayBuffer()));
        break;
      } catch (e) { if (attempt === 3) throw e; await new Promise(r => setTimeout(r, 1000)); }
    }
  }
  const { data } = await sharp(f).removeAlpha().raw().toBuffer({ resolveWithObject: true });
  const h = new Float32Array(256 * 256);
  for (let i = 0; i < 65536; i++) h[i] = data[i * 3] * 256 + data[i * 3 + 1] + data[i * 3 + 2] / 256 - 32768;
  tiles.set(key, h);
  return h;
}

// preload in parallel batches
const jobs = [];
for (let y = ty0; y <= ty1; y++) for (let x = tx0; x <= tx1; x++) jobs.push([x, y]);
for (let i = 0; i < jobs.length; i += 16) await Promise.all(jobs.slice(i, i + 16).map(([x, y]) => getTile(x, y)));

function px(gx, gy) { // global pixel coords at zoom
  const tx = Math.floor(gx / 256), ty = Math.floor(gy / 256);
  const t = tiles.get(`${zoom}_${tx}_${ty}`);
  if (!t) return 0;
  return t[(gy - ty * 256) * 256 + (gx - tx * 256)];
}
function sample(lat, lon) {
  const gx = tileXf(lon) * 256 - 0.5, gy = tileYf(lat) * 256 - 0.5;
  const x0 = Math.floor(gx), y0 = Math.floor(gy), fx = gx - x0, fy = gy - y0;
  const a = px(x0, y0), b = px(x0 + 1, y0), c = px(x0, y0 + 1), d = px(x0 + 1, y0 + 1);
  return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy;
}

const out = new Float32Array(grid * grid);
const step = size / (grid - 1);
let mn = 1e9, mx = -1e9;
for (let j = 0; j < grid; j++) for (let i = 0; i < grid; i++) {
  const x = offE - half + i * step, z = offS - half + j * step;
  const [la, lo] = toLL(x, z);
  const h = sample(la, lo);
  out[j * grid + i] = h; mn = Math.min(mn, h); mx = Math.max(mx, h);
}
fs.writeFileSync(path.join(dir, name + '.f32'), Buffer.from(out.buffer));
fs.writeFileSync(path.join(dir, name + '.json'), JSON.stringify({ name, lat0, lon0, size, zoom, grid, offE, offS, step, min: mn, max: mx }, null, 1));
console.log(`${name}: ${grid}^2, step ${step.toFixed(2)} m, h ${mn.toFixed(0)}..${mx.toFixed(0)}`);

// hillshade preview (light from NW) with hypsometric tint
const img = Buffer.alloc(grid * grid * 3);
for (let j = 0; j < grid; j++) for (let i = 0; i < grid; i++) {
  const h = out[j * grid + i];
  const hx = out[j * grid + Math.min(grid - 1, i + 1)] - out[j * grid + Math.max(0, i - 1)];
  const hz = out[Math.min(grid - 1, j + 1) * grid + i] - out[Math.max(0, j - 1) * grid + i];
  let nx = -hx / (2 * step), nz = -hz / (2 * step), ny = 1; const l = Math.hypot(nx, ny, nz); nx /= l; ny /= l; nz /= l;
  const shade = Math.max(0, nx * -0.5 + ny * 0.7 + nz * -0.5);
  const t = (h - mn) / (mx - mn);
  let r = 60 + 190 * t, g = 90 + 150 * t, b = 60 + 180 * t;
  if (h < 0.5 + (+process.env.WATER || -1e9)) { r = 40; g = 70; b = 160; }
  const k = (i + j * grid) * 3;
  img[k] = Math.min(255, r * shade * 1.2); img[k + 1] = Math.min(255, g * shade * 1.2); img[k + 2] = Math.min(255, b * shade * 1.2);
}
await sharp(img, { raw: { width: grid, height: grid, channels: 3 } }).png().toFile(path.join(dir, name + '_shade.png'));
