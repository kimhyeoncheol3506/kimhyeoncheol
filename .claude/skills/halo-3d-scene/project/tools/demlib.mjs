// Shared DEM helpers: fetch AWS Terrain Tiles (terrarium) and resample to a local metric grid.
import sharp from 'sharp';
import fs from 'node:fs';
import path from 'node:path';

const tileDir = 'data/dem/tiles';
fs.mkdirSync(tileDir, { recursive: true });

export function makeProjection(lat0, lon0) {
  const mPerDegLat = 111132.92 - 559.82 * Math.cos(2 * lat0 * Math.PI / 180);
  const mPerDegLon = 111412.84 * Math.cos(lat0 * Math.PI / 180);
  // local (x east, z south) -> [lat, lon]
  return (x, z) => [lat0 - z / mPerDegLat, lon0 + x / mPerDegLon];
}

const cache = new Map();
async function loadTile(zoom, x, y) {
  const key = `${zoom}_${x}_${y}`;
  if (cache.has(key)) return cache.get(key);
  const f = path.join(tileDir, key + '.png');
  if (!fs.existsSync(f)) {
    for (let attempt = 0; ; attempt++) {
      try {
        const res = await fetch(`https://s3.amazonaws.com/elevation-tiles-prod/terrarium/${zoom}/${x}/${y}.png`);
        if (!res.ok) throw new Error('HTTP ' + res.status);
        fs.writeFileSync(f, Buffer.from(await res.arrayBuffer()));
        break;
      } catch (e) { if (attempt >= 4) throw e; await new Promise(r => setTimeout(r, 1500)); }
    }
  }
  const { data } = await sharp(f).removeAlpha().raw().toBuffer({ resolveWithObject: true });
  const h = new Float32Array(65536);
  for (let i = 0; i < 65536; i++) h[i] = data[i * 3] * 256 + data[i * 3 + 1] + data[i * 3 + 2] / 256 - 32768;
  cache.set(key, h);
  return h;
}

// Returns Float32Array grid*grid heights covering [-size/2, size/2]^2 around (lat0, lon0).
export async function fetchGrid({ lat0, lon0, size, zoom, grid }) {
  const toLL = makeProjection(lat0, lon0);
  const n = 2 ** zoom;
  const tx = lon => (lon + 180) / 360 * n;
  const ty = lat => { const r = lat * Math.PI / 180; return (1 - Math.log(Math.tan(r) + 1 / Math.cos(r)) / Math.PI) / 2 * n; };
  const half = size / 2;
  const [latN] = toLL(0, -half), [latS] = toLL(0, half), [, lonW] = toLL(-half, 0), [, lonE] = toLL(half, 0);
  const x0 = Math.floor(tx(lonW)), x1 = Math.floor(tx(lonE)), y0 = Math.floor(ty(latN)), y1 = Math.floor(ty(latS));
  const jobs = [];
  for (let y = y0; y <= y1; y++) for (let x = x0; x <= x1; x++) jobs.push([x, y]);
  console.log(`  z${zoom}: ${jobs.length} tiles`);
  for (let i = 0; i < jobs.length; i += 24) await Promise.all(jobs.slice(i, i + 24).map(([x, y]) => loadTile(zoom, x, y)));
  const px = (gx, gy) => {
    const tX = Math.floor(gx / 256), tY = Math.floor(gy / 256);
    const t = cache.get(`${zoom}_${tX}_${tY}`);
    return t ? t[(gy - tY * 256) * 256 + (gx - tX * 256)] : 0;
  };
  const out = new Float32Array(grid * grid);
  const step = size / (grid - 1);
  for (let j = 0; j < grid; j++) for (let i = 0; i < grid; i++) {
    const [la, lo] = toLL(-half + i * step, -half + j * step);
    const gx = tx(lo) * 256 - 0.5, gy = ty(la) * 256 - 0.5;
    const ix = Math.floor(gx), iy = Math.floor(gy), fx = gx - ix, fy = gy - iy;
    // bicubic (Catmull-Rom) for smoother upsampling
    let acc = 0;
    for (let m = -1; m <= 2; m++) {
      const wy = cr(m - fy);
      let row = 0;
      for (let k = -1; k <= 2; k++) row += px(ix + k, iy + m) * cr(k - fx);
      acc += row * wy;
    }
    out[j * grid + i] = acc;
  }
  return out;
}
function cr(t) { t = Math.abs(t); return t < 1 ? 1.5 * t ** 3 - 2.5 * t * t + 1 : t < 2 ? -0.5 * t ** 3 + 2.5 * t * t - 4 * t + 2 : 0; }
