// Radiance .hdr (RGBE) reader + equirect helpers for the sky bake (round 8). As a script: analyse an HDRI
// (sun / glow position, radiance percentiles) and write a quick tone-mapped perspective preview toward its glow.
// usage: node tools/skyhdr.mjs <in.hdr> <outPrefix> [ev=0]
import fs from 'node:fs';
import sharp from 'sharp';

export function readHDR(file) {
  const buf = fs.readFileSync(file);
  let p = 0;
  const line = () => { let s = ''; while (buf[p] !== 0x0a) s += String.fromCharCode(buf[p++]); p++; return s; };
  if (!line().startsWith('#?')) throw new Error('not a radiance file');
  for (;;) { const l = line(); if (l === '') break; if (l.startsWith('FORMAT') && !l.includes('32-bit_rle_rgbe')) throw new Error(l); }
  const m = line().match(/-Y (\d+) \+X (\d+)/);
  if (!m) throw new Error('unsupported orientation');
  const h = +m[1], w = +m[2];
  const out = new Float32Array(w * h * 3);
  const sc = new Uint8Array(w * 4);
  for (let y = 0; y < h; y++) {
    if (buf[p] === 2 && buf[p + 1] === 2 && ((buf[p + 2] << 8) | buf[p + 3]) === w) {
      p += 4;
      for (let c = 0; c < 4; c++) {
        let x = 0;
        while (x < w) {
          let n = buf[p++];
          if (n > 128) { n -= 128; const v = buf[p++]; for (let k = 0; k < n; k++) sc[(x++) * 4 + c] = v; }
          else for (let k = 0; k < n; k++) sc[(x++) * 4 + c] = buf[p++];
        }
      }
    } else {
      for (let x = 0; x < w; x++) for (let c = 0; c < 4; c++) sc[x * 4 + c] = buf[p++];
    }
    for (let x = 0; x < w; x++) {
      const e = sc[x * 4 + 3], o = (y * w + x) * 3;
      if (e === 0) { out[o] = out[o + 1] = out[o + 2] = 0; continue; }
      const f = Math.pow(2, e - 136);
      out[o] = sc[x * 4] * f; out[o + 1] = sc[x * 4 + 1] * f; out[o + 2] = sc[x * 4 + 2] * f;
    }
  }
  return { w, h, data: out };
}

// bilinear lookup in an equirect (u 0..1 wraps, v 0 = zenith .. 1 = nadir)
export function sampleEq(img, u, v, out) {
  const { w, h, data } = img;
  let x = u * w - 0.5, y = Math.min(Math.max(v * h - 0.5, 0), h - 1.001);
  const x0 = Math.floor(x), y0 = Math.floor(y), fx = x - x0, fy = y - y0;
  const xa = ((x0 % w) + w) % w, xb = (xa + 1) % w;
  const ia = (y0 * w + xa) * 3, ib = (y0 * w + xb) * 3, ic = ((y0 + 1) * w + xa) * 3, id = ((y0 + 1) * w + xb) * 3;
  for (let c = 0; c < 3; c++)
    out[c] = (data[ia + c] * (1 - fx) + data[ib + c] * fx) * (1 - fy) + (data[ic + c] * (1 - fx) + data[id + c] * fx) * fy;
  return out;
}

const lum = (r, g, b) => 0.2126 * r + 0.7152 * g + 0.0722 * b;

if (process.argv[1].endsWith('skyhdr.mjs')) {
  const [, , inp, pre, evS = '0'] = process.argv;
  const img = readHDR(inp);
  const { w, h, data } = img;
  // brightest pixel (sun) and the glow column (elevation 0.5 .. 6 deg)
  let mx = 0, mi = 0;
  for (let i = 0; i < w * h; i++) { const l = lum(data[i * 3], data[i * 3 + 1], data[i * 3 + 2]); if (l > mx) { mx = l; mi = i; } }
  const sx = mi % w, sy = Math.floor(mi / w);
  const col = new Float64Array(w);
  for (let y = Math.round(h / 2 - 6 / 180 * h); y < Math.round(h / 2 - 0.5 / 180 * h); y++)
    for (let x = 0; x < w; x++) { const i = (y * w + x) * 3; col[x] += lum(data[i], data[i + 1], data[i + 2]); }
  let best = 0, gx = 0;
  for (let x = 0; x < w; x++) { let s = 0; for (let k = -14; k <= 14; k++) s += col[(x + k + w) % w]; if (s > best) { best = s; gx = x; } }
  const elev = y => 90 - (y + 0.5) / h * 180;
  console.log(`${w}x${h}; max L ${mx.toFixed(2)} at u=${(sx / w).toFixed(4)} el=${elev(sy).toFixed(2)}; glow u=${(gx / w).toFixed(4)}`);
  // luminance percentiles per elevation band
  for (const [e0, e1] of [[0, 2], [2, 5], [5, 10], [10, 20], [20, 40], [40, 70], [70, 90]]) {
    const ls = [];
    for (let y = Math.round((90 - e1) / 180 * h); y < Math.round((90 - e0) / 180 * h); y++)
      for (let x = 0; x < w; x += 2) { const i = (y * w + x) * 3; ls.push(lum(data[i], data[i + 1], data[i + 2])); }
    ls.sort((a, b) => a - b);
    const q = f => ls[Math.floor(f * (ls.length - 1))].toFixed(3);
    console.log(`el ${e0}-${e1}: p5 ${q(0.05)} p50 ${q(0.5)} p95 ${q(0.95)} p99.9 ${q(0.999)}`);
  }
  // perspective previews toward the glow: yaw offsets 0 / 90 / 180, pitch 10, vertical fov 60, plus overhead
  const ev = Math.pow(2, +evS);
  let ref = 0; { const ls = []; for (let y = Math.round(30 / 180 * h); y < Math.round(80 / 180 * h); y++) for (let x = 0; x < w; x += 4) { const i = (y * w + x) * 3; ls.push(lum(data[i], data[i + 1], data[i + 2])); } ls.sort((a, b) => a - b); ref = ls[Math.floor(ls.length / 2)]; }
  const PW = 640, PH = 360, tiles = [];
  for (const [yaw, pitch] of [[0, 12], [-60, 12], [60, 12], [180, 12], [0, 55], [0, 89]]) {
    const px = Buffer.alloc(PW * PH * 3), s = [0, 0, 0];
    const f = (PH / 2) / Math.tan(30 * Math.PI / 180);
    const cy = Math.cos(pitch * Math.PI / 180), sy2 = Math.sin(pitch * Math.PI / 180);
    const az0 = gx / w * 2 * Math.PI + yaw * Math.PI / 180;
    for (let j = 0; j < PH; j++) for (let i = 0; i < PW; i++) {
      // camera space: x right, y up, z forward
      const x = (i + 0.5 - PW / 2) / f, y = (PH / 2 - j - 0.5) / f;
      // pitch about x, then yaw about the vertical
      const fy = y * cy + sy2, fz = cy - y * sy2;
      const n = Math.hypot(x, fy, fz);
      const el = Math.asin(fy / n), az = az0 + Math.atan2(x, fz);
      sampleEq(img, ((az / (2 * Math.PI)) % 1 + 1) % 1, (Math.PI / 2 - el) / Math.PI, s);
      for (let c = 0; c < 3; c++) {
        const v = s[c] / ref * 0.18 * ev;
        const t = v / (1 + v);              // simple Reinhard
        px[(j * PW + i) * 3 + c] = Math.round(255 * Math.pow(Math.min(t * 1.4, 1), 1 / 2.2));
      }
    }
    tiles.push(await sharp(px, { raw: { width: PW, height: PH, channels: 3 } }).png().toBuffer());
  }
  await sharp({ create: { width: PW * 3 + 8, height: PH * 2 + 4, channels: 3, background: '#000' } })
    .composite(tiles.map((t, k) => ({ input: t, left: (k % 3) * (PW + 4), top: Math.floor(k / 3) * (PH + 4) })))
    .jpeg({ quality: 88 }).toFile(`${pre}_persp.jpg`);
}
