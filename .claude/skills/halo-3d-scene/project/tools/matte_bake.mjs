// Bake the matte backgrounds data/matte/bg_<n>.png from ref/<n>.webp.
// usage: node tools/matte_bake.mjs raw [views]       -> the refs as PNG (no cleanup)
//        node tools/matte_bake.mjs clean [views]     -> the ref's own ring structure removed + inpainted:
//   hole = our structure silhouette from the same camera (out/shots/mstruct_v<n>_struct.png, tools/matte_cap.mjs
//   mode 'struct': 0 = structure) dilated by DIL px + the traced polygons in tools/matte_masks.json (ref px),
//   filled by push-pull (pyramid) inpainting with a little texture from the surround; out/matte/hole_<n>.png for checks
// r7 pass 2: the hole is filled by offset clones of the ref's own texture (cloneFill: visible part first, from
//   out/shots/<WT|final>_v<n>_w.png, then the part hidden behind our structure), 'clone' regions from a given source
//   rect; 'force' polygons -> data/matte/force_<n>.png + force.json (src/matte.js: w = max(farness, force)).
//   env: SP (struct capture tag, e.g. m1), WT (weight capture tag), PDIL (polygon dilation px, 4), SOFT (candidate
//   soft-min, 4), NOCLONE=1 (pass-1 push-pull only), NOSTAGE2=1 (no hidden-hole clone)
import sharp from 'sharp';
import fs from 'node:fs';

const mode = process.argv[2] || 'raw';
const views = (process.argv[3] || '1,2,3,4,5,6,7,8,9,10,11').split(',').map(Number);
const W = 1672, H = 941;
const OUT = process.env.OUT || 'data/matte';      // env OUT: bake elsewhere (checks)
fs.mkdirSync(OUT, { recursive: true });
fs.mkdirSync('out/matte', { recursive: true });
const masks = fs.existsSync('tools/matte_masks.json') ? JSON.parse(fs.readFileSync('tools/matte_masks.json', 'utf8')) : {};

const DIL = { default: 6, 9: 14, 3: 10, 1: 8 }, ROI = { default: 16 }, WARM = +(process.env.WARM || 6);

// polygon fill (even-odd, pixel centres)
function fillPoly(m, pts) {
  const ys = pts.map(p => p[1]);
  for (let y = Math.max(0, Math.floor(Math.min(...ys))); y <= Math.min(H - 1, Math.ceil(Math.max(...ys))); y++) {
    const xs = [];
    for (let i = 0; i < pts.length; i++) {
      const [x0, y0] = pts[i], [x1, y1] = pts[(i + 1) % pts.length];
      if ((y0 <= y + 0.5) !== (y1 <= y + 0.5)) xs.push(x0 + (y + 0.5 - y0) / (y1 - y0) * (x1 - x0));
    }
    xs.sort((a, b) => a - b);
    for (let k = 0; k + 1 < xs.length; k += 2)
      for (let x = Math.max(0, Math.ceil(xs[k] - 0.5)); x <= Math.min(W - 1, Math.floor(xs[k + 1] - 0.5)); x++) m[y * W + x] = 1;
  }
}
function dilate(m, r) {
  // separable square-ish (two passes: box in x, then y) then round by distance check is overkill: use a disc via row offsets
  const out = new Uint8Array(W * H);
  const offs = [];
  for (let dy = -r; dy <= r; dy++) offs.push([dy, Math.floor(Math.sqrt(r * r - dy * dy))]);
  // row run-length: for each set pixel, mark spans
  const rowHas = new Int32Array(W + 1);
  for (let y = 0; y < H; y++) {
    for (const [dy, hw] of offs) {
      const yy = y + dy; if (yy < 0 || yy >= H) continue;
      // prefix sums of row yy
      let s = 0; rowHas[0] = 0;
      for (let x = 0; x < W; x++) { s += m[yy * W + x]; rowHas[x + 1] = s; }
      for (let x = 0; x < W; x++) {
        if (out[y * W + x]) continue;
        const a = Math.max(0, x - hw), b = Math.min(W, x + hw + 1);
        if (rowHas[b] - rowHas[a] > 0) out[y * W + x] = 1;
      }
    }
  }
  return out;
}

// push-pull inpainting of the hole (m = 1) in a float RGB image
function pushPull(img, m) {
  const c = new Float32Array(W * H * 3), a = new Float32Array(W * H);
  for (let i = 0; i < W * H; i++) { const k = m[i] ? 0 : 1; a[i] = k; for (let ch = 0; ch < 3; ch++) c[i * 3 + ch] = img[i * 3 + ch] * k; }
  return ppGen(c, a, W, H);
}
// push-pull on any w x h image: c = premultiplied RGB (c * a), a = 1 known / 0 unknown -> filled RGB
function ppGen(c, a, w, h) {
  const levels = [];
  levels.push({ w, h, c, a });
  while (w > 1 || h > 1) {
    const nw = Math.max(1, (w + 1) >> 1), nh = Math.max(1, (h + 1) >> 1);
    const nc = new Float32Array(nw * nh * 3), na = new Float32Array(nw * nh);
    for (let y = 0; y < nh; y++) for (let x = 0; x < nw; x++) {
      let sa = 0; const sc = [0, 0, 0];
      for (let dy = 0; dy < 2; dy++) for (let dx = 0; dx < 2; dx++) {
        const xx = Math.min(w - 1, 2 * x + dx), yy = Math.min(h - 1, 2 * y + dy), i = yy * w + xx;
        sa += a[i]; for (let ch = 0; ch < 3; ch++) sc[ch] += c[i * 3 + ch];
      }
      const o = y * nw + x;
      // premultiplied average, alpha saturated so coarse levels count as full
      const k = sa > 0 ? Math.min(1, sa) / sa : 0;
      na[o] = Math.min(1, sa); for (let ch = 0; ch < 3; ch++) nc[o * 3 + ch] = sc[ch] * k;
    }
    w = nw; h = nh; c = nc; a = na;
    levels.push({ w, h, c, a });
  }
  // pull: fill each level's missing alpha from the (bilinear) coarser level
  for (let l = levels.length - 2; l >= 0; l--) {
    const L = levels[l], C = levels[l + 1];
    for (let y = 0; y < L.h; y++) for (let x = 0; x < L.w; x++) {
      const i = y * L.w + x;
      if (L.a[i] >= 1) continue;
      const fx = Math.min(C.w - 1, Math.max(0, (x + 0.5) / 2 - 0.5)), fy = Math.min(C.h - 1, Math.max(0, (y + 0.5) / 2 - 0.5));
      const x0 = Math.floor(fx), y0 = Math.floor(fy), x1 = Math.min(C.w - 1, x0 + 1), y1 = Math.min(C.h - 1, y0 + 1);
      const tx = fx - x0, ty = fy - y0;
      const rem = 1 - L.a[i];
      for (let ch = 0; ch < 3; ch++) {
        const v = (C.c[(y0 * C.w + x0) * 3 + ch] * (1 - tx) + C.c[(y0 * C.w + x1) * 3 + ch] * tx) * (1 - ty)
          + (C.c[(y1 * C.w + x0) * 3 + ch] * (1 - tx) + C.c[(y1 * C.w + x1) * 3 + ch] * tx) * ty;
        L.c[i * 3 + ch] += v * rem;
      }
      L.a[i] = 1;
    }
  }
  return levels[0].c;
}

// r7 pass 2: exemplar (offset-clone) fill of the VISIBLE hole. Push-pull alone leaves flat grey mush (ghost struts);
// each connected component of hole n (our matte w > 0, out/shots/<WT>_v<n>_w.png, dilated) instead copies the ref's
// own texture (rock / cloud / sky) from the best-matching offset beside it, plus a smooth push-pull correction of the
// colour difference on a ring around the component (seamless join). 'clone' regions (tools/matte_masks.json) are
// filled from a given source rectangle, mirror-tiled (v3's sky band). Returns the filled RGB (Float32, 3 ch).
const RING = 5, DCLAMP = 24, GLOW = 16, NCAND = 8, SOFT = +(process.env.SOFT || 4), SRCM = +(process.env.SRCM ?? 4), PDIL = +(process.env.PDIL || 4);
const RADII = [10, 14, 20, 28, 38, 50, 66, 86, 110, 140, 180, 230, 300];
const mirror = (v, a, b) => { const L = b - a, t = ((v - a) % (2 * L) + 2 * L) % (2 * L); return a + (t < L ? t : 2 * L - 1 - t); };
async function cloneFill(n, img, m, f) {
  const out = Float32Array.from(f), done = new Uint8Array(W * H);
  // clone regions: source rect [x0, y0, x1, y1] (ref px), mirror-tiled, optionally shifted by d = [dx, dy]
  for (const c of (masks.clone || {})[n] || []) {
    const cm = new Uint8Array(W * H); fillPoly(cm, c.poly);
    const [x0, y0, x1, y1] = c.src, [ox, oy] = c.d || [0, 0];
    const src = (x, y) => mirror(y + oy, y0, y1) * W + mirror(x + ox, x0, x1);
    // smooth correction (as for the offset clones): push-pull of the difference ref - source on a ring of known
    // pixels around the region, so the region's edges do not show
    const ys = c.poly.map(p => p[1]), xs = c.poly.map(p => p[0]), M = RING + 12;
    const wx0 = Math.max(0, Math.min(...xs) - M), wy0 = Math.max(0, Math.min(...ys) - M);
    const ww = Math.min(W, Math.max(...xs) + M + 1) - wx0, wh = Math.min(H, Math.max(...ys) + M + 1) - wy0;
    const rg = dilate(cm, RING);
    const dc = new Float32Array(ww * wh * 3), da = new Float32Array(ww * wh);
    for (let y = wy0; y < wy0 + wh; y++) for (let x = wx0; x < wx0 + ww; x++) {
      const i = y * W + x; if (!rg[i] || m[i]) continue;
      const s = src(x, y), o = (y - wy0) * ww + (x - wx0);
      if (0.3 * (img[i * 3] - img[s * 3]) + 0.6 * (img[i * 3 + 1] - img[s * 3 + 1]) + 0.1 * (img[i * 3 + 2] - img[s * 3 + 2]) > GLOW && img[i * 3] - img[i * 3 + 2] > WARM) continue;
      da[o] = 1;
      for (let ch = 0; ch < 3; ch++) dc[o * 3 + ch] = img[i * 3 + ch] - img[s * 3 + ch];
    }
    const D = ppGen(dc, da, ww, wh);
    for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
      const i = y * W + x; if (!cm[i] || !m[i]) continue;
      const s = src(x, y), inW = x >= wx0 && y >= wy0 && x < wx0 + ww && y < wy0 + wh, o = (y - wy0) * ww + (x - wx0);
      for (let ch = 0; ch < 3; ch++) out[i * 3 + ch] = img[s * 3 + ch] + (inW ? Math.max(-DCLAMP, Math.min(DCLAMP, D[o * 3 + ch])) : 0);
      done[i] = 1;
    }
  }
  let vis;
  const wf = `out/shots/${process.env.WT || 'final'}_v${n}_w.png`;
  if (fs.existsSync(wf)) {
    const w = await sharp(wf).removeAlpha().resize(W, H).raw().toBuffer();
    const t = new Uint8Array(W * H); for (let i = 0; i < W * H; i++) t[i] = w[i * 3] > 4 ? 1 : 0;
    vis = dilate(t, 4); for (let i = 0; i < W * H; i++) vis[i] &= m[i] & (1 - done[i]);
  } else { vis = Uint8Array.from(m); for (let i = 0; i < W * H; i++) vis[i] &= 1 - done[i]; }
  const n1 = clonePass(vis, img, m, out, done);
  // stage 2 (moving cameras): the rest of the hole (behind our structure at the ref camera), from the ref + stage 1
  const cur = new Float32Array(W * H * 3), m2 = new Uint8Array(W * H);
  for (let i = 0; i < W * H; i++) {
    m2[i] = m[i] && !done[i] ? 1 : 0;
    for (let ch = 0; ch < 3; ch++) cur[i * 3 + ch] = m[i] ? out[i * 3 + ch] : img[i * 3 + ch];
  }
  const n2 = process.env.NOSTAGE2 ? [0, 0] : clonePass(m2, cur, m2, out, done);
  console.log(`  view ${n}: visible hole ${n1[1]}/${n1[0]} components cloned, hidden hole ${n2[1]}/${n2[0]}`);
  return { out, done };
}

// offset-clone the components of vis (m = unknown pixels of img) into out, marking done = 2; -> [components, cloned]
function clonePass(vis, img, m, out, done) {
  // sources must keep SRCM px from the hole: right next to it lie the ref strut's dark outline and glow, which small
  // offsets would copy into the fill as stripes
  const mS = dilate(m, SRCM);
  // connected components (8-neighbour)
  const lab = new Int32Array(W * H).fill(-1), ring = new Int32Array(W * H).fill(-1);
  let nc = 0, ncl = 0;
  for (let s0 = 0; s0 < W * H; s0++) {
    if (!vis[s0] || lab[s0] >= 0) continue;
    const C = [s0]; lab[s0] = nc;
    for (let k = 0; k < C.length; k++) {
      const p = C[k], px = p % W, py = (p - px) / W;
      for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) {
        const x = px + dx, y = py + dy; if (x < 0 || y < 0 || x >= W || y >= H) continue;
        const q = y * W + x; if (vis[q] && lab[q] < 0) { lab[q] = nc; C.push(q); }
      }
    }
    // ring: known pixels within RING px of the component
    const B = [];
    let bx0 = W, by0 = H, bx1 = 0, by1 = 0;
    for (const p of C) {
      const px = p % W, py = (p - px) / W;
      bx0 = Math.min(bx0, px); bx1 = Math.max(bx1, px); by0 = Math.min(by0, py); by1 = Math.max(by1, py);
      for (let dy = -RING; dy <= RING; dy++) for (let dx = -RING; dx <= RING; dx++) {
        const x = px + dx, y = py + dy; if (x < 0 || y < 0 || x >= W || y >= H) continue;
        const q = y * W + x; if (!m[q] && ring[q] !== nc) { ring[q] = nc; B.push(q); }
      }
    }
    nc++;
    if (C.length < 6 || B.length < 8) continue;
    // offsets ranked by the variance (+ 1/4 mean^2) of the ring difference, a mild preference for near sources and
    // for sources outside the hole. Elongated components (struts): no offsets within 35 deg of their long axis (the
    // source would be the rest of the ref's strut)
    let mx = 0, my = 0;
    for (const p of C) { mx += p % W; my += (p - p % W) / W; }
    mx /= C.length; my /= C.length;
    let sxx = 0, syy = 0, sxy = 0;
    for (const p of C) { const x = p % W - mx, y = (p - p % W) / W - my; sxx += x * x; syy += y * y; sxy += x * y; }
    const tr = sxx + syy, det = sxx * syy - sxy * sxy, l1 = tr / 2 + Math.sqrt(Math.max(0, tr * tr / 4 - det)), l2 = tr - l1;
    const axis = 0.5 * Math.atan2(2 * sxy, sxx - syy), elong = l1 > 4 * Math.max(l2, 1e-6);
    const cands = [];
    for (const r of RADII) for (let k = 0; k < 24; k++) {
      const a = k / 24 * 2 * Math.PI, dx = Math.round(r * Math.cos(a)), dy = Math.round(r * Math.sin(a));
      if (bx0 + dx < 0 || bx1 + dx >= W || by0 + dy < 0 || by1 + dy >= H) continue;
      if (elong && Math.abs(Math.cos(a - axis)) > Math.cos(35 * Math.PI / 180)) continue;
      const lim = C.length * 0.5; let bad = 0;
      for (const p of C) { if (mS[p + dy * W + dx]) { if (++bad > lim) break; } }
      if (bad > lim) continue;
      let s1 = 0, s2 = 0, nb = 0;
      for (const p of B) {
        const q = p + dy * W + dx, px = p % W + dx, py = (p - p % W) / W + dy;
        if (px < 0 || py < 0 || px >= W || py >= H || m[q]) continue;
        for (let ch = 0; ch < 3; ch++) { const d = img[p * 3 + ch] - img[q * 3 + ch]; s1 += d; s2 += d * d; }
        nb += 3;
      }
      if (nb < B.length) continue;
      const mu = s1 / nb, sc = (s2 / nb - mu * mu + 0.25 * mu * mu) * (1 + r / 400) * (1 + 3 * bad / C.length);
      cands.push({ sc, dx, dy });
    }
    if (!cands.length) continue;
    cands.sort((a, b) => a.sc - b.sc);
    if (process.env.DEBUG && C.length > 1500) console.log(`   comp ${C.length}px x${bx0}-${bx1} y${by0}-${by1} elong ${elong} axis ${(axis * 180 / Math.PI).toFixed(0)}`,
      cands.slice(0, NCAND).map(c => `${c.dx},${c.dy}`).join(' '));
    const M = RING + 12;
    const wx0 = Math.max(0, bx0 - M), wy0 = Math.max(0, by0 - M), ww = Math.min(W, bx1 + M + 1) - wx0, wh = Math.min(H, by1 + M + 1) - wy0;
    // per pixel, a soft minimum over the candidates of the local mismatch |D| (the push-pull interpolated ring
    // difference): a strut crossing rock and sky takes rock from the rock side and sky from the sky side
    const acc = new Float32Array(C.length * 3), accW = new Float32Array(C.length), best = new Float32Array(C.length).fill(1e9);
    const sel = cands.slice(0, NCAND).map(({ dx, dy }) => {
      const dc = new Float32Array(ww * wh * 3), da = new Float32Array(ww * wh);
      for (const p of B) {
        const q = p + dy * W + dx, px = p % W, py = (p - px) / W;
        if (px + dx < 0 || py + dy < 0 || px + dx >= W || py + dy >= H || m[q]) continue;
        // the ref strut's glow just outside the hole: a warm ring much brighter than the source is not trusted
        const dl = 0.3 * (img[p * 3] - img[q * 3]) + 0.6 * (img[p * 3 + 1] - img[q * 3 + 1]) + 0.1 * (img[p * 3 + 2] - img[q * 3 + 2]);
        if (dl > GLOW && img[p * 3] - img[p * 3 + 2] > WARM) continue;
        const o = (py - wy0) * ww + (px - wx0); da[o] = 1;
        for (let ch = 0; ch < 3; ch++) dc[o * 3 + ch] = img[p * 3 + ch] - img[q * 3 + ch];
      }
      return { dx, dy, D: ppGen(dc, da, ww, wh) };
    });
    const cost = (s, k) => {
      const p = C[k], q = p + s.dy * W + s.dx; if (mS[q]) return 1e9;
      const px = p % W, py = (p - px) / W, o = (py - wy0) * ww + (px - wx0);
      return Math.abs(s.D[o * 3]) + Math.abs(s.D[o * 3 + 1]) + Math.abs(s.D[o * 3 + 2]);
    };
    for (const s of sel) for (let k = 0; k < C.length; k++) best[k] = Math.min(best[k], cost(s, k));
    for (const s of sel) for (let k = 0; k < C.length; k++) {
      const c = cost(s, k); if (c >= 1e9) continue;
      const wk = Math.exp(-(c - best[k]) / SOFT); if (wk < 1e-3) continue;
      const p = C[k], q = p + s.dy * W + s.dx, px = p % W, py = (p - px) / W, o = (py - wy0) * ww + (px - wx0);
      for (let ch = 0; ch < 3; ch++) acc[k * 3 + ch] += wk * (img[q * 3 + ch] + Math.max(-DCLAMP, Math.min(DCLAMP, s.D[o * 3 + ch])));
      accW[k] += wk;
    }
    for (let k = 0; k < C.length; k++) {
      if (accW[k] <= 0) continue;
      const p = C[k];
      for (let ch = 0; ch < 3; ch++) out[p * 3 + ch] = acc[k * 3 + ch] / accW[k];
      done[p] = 2;
    }
    ncl++;
  }
  return [nc, ncl];
}

for (const n of views) {
  const ref = sharp(`ref/${n}.webp`).removeAlpha();
  if (mode === 'raw') { await ref.png().toFile(`${OUT}/bg_${n}.png`); console.log('raw', n); continue; }
  const img = await ref.raw().toBuffer();
  let m = new Uint8Array(W * H);
  const sf = `out/shots/${process.env.SP || 'mstruct'}_v${n}_struct.png`;
  if (fs.existsSync(sf)) {
    const s = await sharp(sf).removeAlpha().resize(W, H).raw().toBuffer();
    // grey weight (0 = structure); env SMODE=premult: a capture of ref * w (structure = much darker than the ref)
    const pm = process.env.SMODE === 'premult';
    for (let i = 0; i < W * H; i++) {
      const ss = s[i * 3] + s[i * 3 + 1] + s[i * 3 + 2], rs = img[i * 3] + img[i * 3 + 1] + img[i * 3 + 2];
      m[i] = pm ? (rs > 12 && ss < 0.5 * rs ? 1 : 0) : (s[i * 3] < 128 ? 1 : 0);
    }
    // the ref's own structure near ours: warm / neutral-bright pixels (lit glazing, concrete) within ROI px of our
    // silhouette (the background there is blue: clouds, shaded snow, rock, sky)
    const roi = dilate(m, ROI[n] ?? ROI.default);
    const warm = new Uint8Array(W * H);
    for (let i = 0; i < W * H; i++) {
      if (!roi[i]) continue;
      const r = img[i * 3], g = img[i * 3 + 1], b = img[i * 3 + 2];
      warm[i] = (r - b > WARM) || (r + g + b > 3 * 150 && r >= b - 4) ? 1 : 0;
    }
    const sm = dilate(m, DIL[n] ?? DIL.default), wm = dilate(warm, 2);
    for (let i = 0; i < W * H; i++) m[i] = sm[i] | wm[i];
  }
  // traced polygons, widened by PDIL px so the ref strut's dark edges are not cloned into the fill
  const pm = new Uint8Array(W * H);
  for (const poly of masks[n] || []) fillPoly(pm, poly);
  const pmd = PDIL > 0 ? dilate(pm, PDIL) : pm;
  for (let i = 0; i < W * H; i++) m[i] |= pmd[i];
  const pp = pushPull(img, m);
  const { out: f, done } = process.env.NOCLONE ? { out: pp, done: new Uint8Array(W * H) } : await cloneFill(n, img, m, pp);
  // grain: the ref's own fine texture (hi-pass noise level) re-added in the push-pull hole so the fill is not glassy
  const out = Buffer.alloc(W * H * 3);
  let seed = 12345 + n;
  const rnd = () => { seed = (seed * 1664525 + 1013904223) >>> 0; return seed / 4294967296; };
  for (let i = 0; i < W * H; i++) for (let ch = 0; ch < 3; ch++) {
    const v = m[i] ? f[i * 3 + ch] + (done[i] ? 0 : (rnd() - 0.5) * 3) : img[i * 3 + ch];
    out[i * 3 + ch] = Math.max(0, Math.min(255, Math.round(v)));
  }
  // keep mask in alpha: 0 inside the 'exclude' polygons (feathered), where the ref never shows (src/matte.js w *= a)
  const ex = (masks.exclude || {})[n];
  if (ex) {
    const xm = new Uint8Array(W * H);
    for (const poly of ex) fillPoly(xm, poly);
    const a = await sharp(Buffer.from(xm.map(v => v ? 0 : 255)), { raw: { width: W, height: H, channels: 1 } }).blur(6).raw().toBuffer();
    const o4 = Buffer.alloc(W * H * 4);
    for (let i = 0; i < W * H; i++) { o4[i * 4] = out[i * 3]; o4[i * 4 + 1] = out[i * 3 + 1]; o4[i * 4 + 2] = out[i * 3 + 2]; o4[i * 4 + 3] = a[i]; }
    await sharp(o4, { raw: { width: W, height: H, channels: 4 } }).png().toFile(`${OUT}/bg_${n}.png`);
  } else await sharp(out, { raw: { width: W, height: H, channels: 3 } }).png().toFile(`${OUT}/bg_${n}.png`);
  // force-far mask (r7 pass 2): ref-space polygons where the ref shows sky / far landscape but our near rock stands;
  // src/matte.js w = max(farness, force). Feathered 1.2 px, times our structure's weight (struct capture: 0 = ring)
  // so the ring / struts stay ours. data/matte/force.json lists the views that have one.
  const fp = (masks.force || {})[n];
  if (fp) {
    const fm = new Uint8Array(W * H);
    let sw = null;
    for (const poly of fp) {
      if (!poly.seed) { fillPoly(fm, poly); continue; }
      // { seed: [x, y] }: flood fill of the non-structure region around the seed (e.g. the ring's inner opening)
      sw = sw || await sharp(sf).removeAlpha().resize(W, H).raw().toBuffer();
      const st = [poly.seed[1] * W + poly.seed[0]];
      fm[st[0]] = 1;
      while (st.length) {
        const p = st.pop(), px = p % W, py = (p - px) / W;
        for (const [dx, dy] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
          const x = px + dx, y = py + dy; if (x < 0 || y < 0 || x >= W || y >= H) continue;
          const q = y * W + x; if (!fm[q] && sw[q * 3] > 128) { fm[q] = 1; st.push(q); }
        }
      }
    }
    const fb = await sharp(Buffer.from(fm.map(v => v * 255)), { raw: { width: W, height: H, channels: 1 } }).blur(1.2).extractChannel(0).raw().toBuffer();
    if (fs.existsSync(sf)) {
      const s = await sharp(sf).removeAlpha().resize(W, H).raw().toBuffer();
      for (let i = 0; i < W * H; i++) fb[i] = Math.round(fb[i] * s[i * 3] / 255);
    }
    await sharp(fb, { raw: { width: W, height: H, channels: 1 } }).png().toFile(`${OUT}/force_${n}.png`);
  } else if (fs.existsSync(`${OUT}/force_${n}.png`)) fs.unlinkSync(`${OUT}/force_${n}.png`);
  const hole = Buffer.alloc(W * H); for (let i = 0; i < W * H; i++) hole[i] = m[i] * 255;
  await sharp(hole, { raw: { width: W, height: H, channels: 1 } }).png().toFile(`out/matte/hole_${n}.png`);
  console.log('clean', n);
}
if (mode === 'clean') {
  const fv = Object.keys(masks.force || {}).filter(k => fs.existsSync(`${OUT}/force_${k}.png`)).map(Number);
  fs.writeFileSync(`${OUT}/force.json`, JSON.stringify(fv));
}
