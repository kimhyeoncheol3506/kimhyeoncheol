// Film camera checker: samples timeline cameraAt() every frame against the live scene of the running dev server
// (PORT) and reports, per shot, the minimum clearance to the terrain (3D, from terrain.userData.heightAt), to the
// structure (exact point-triangle distance to every ring / bridge / pavilion / strut / path mesh), to outdoor
// figures and to the cloud ceiling, plus the camera's angular speed (full orientation incl. roll, as main.js aims
// it: up = +Y, lookAt tgt), angular/linear acceleration and pitch. Exit code 1 when a limit is violated.
//
// usage: node tools/filmcheck.mjs [--fps 30] [--json out/filmcheck.json] [--plot out/shots/film_paths.png] [--map] [--wisp 200]
//   (with the dev server running: node tools/filmcheck.mjs, env PORT if not 5173)  ~15 s, no clouds needed
//   --wisp  clouds.js uWisp (m): the cloud ceiling is CLOUDS.top + wisp + 60
//   node tools/filmcheck.mjs --flashes out/prevall   scans rendered frames for single-frame flashes instead (no server)
//   --plot  top view (ring frame) of the terrain with every shot's camera path and aim
//   --map   ASCII height map (ring frame, 10 m units relative to the deck, cols x -6..6 R, rows z -8..10 R)
// limits (defaults below) can be relaxed per shot in src/timeline.js with  check: { terrain: 6, structure: 1, ... }
import fs from 'node:fs';
import sharp from 'sharp';
import { launch } from './shot.mjs';

const arg = (k, d) => { const i = process.argv.indexOf('--' + k); return i > 0 ? process.argv[i + 1] : d; };
const flag = k => process.argv.includes('--' + k);
const fps = +arg('fps', 30);
// m, except rot (deg/s of the full camera orientation) and pitch (deg); figureInView: figures inside the frame
const LIMITS = { terrain: 15, structure: 1.5, figure: 1.0, figureInView: 4, cloud: 0, rot: 12, pitch: 80 };
const WARN = { angAcc: 40, linAcc: 40 };   // deg/s^2, m/s^2: hints of a jerk inside a shot (warning only)

// --flashes <dir>: no camera check; scan rendered frames (tools/render.mjs output) for single-frame flashes, i.e. a
// frame with far more near-white pixels than both neighbours (NaN/Inf or extreme HDR pixels blown up by the bloom)
if (arg('flashes', null)) {
  const dir = arg('flashes'), files = fs.readdirSync(dir).filter(f => /\.(jpg|png)$/.test(f)).sort();
  const cnt = [], pos = [];
  for (const f of files) {
    const { data, info } = await sharp(`${dir}/${f}`).removeAlpha().raw().toBuffer({ resolveWithObject: true });
    let n = 0, sx = 0, sy = 0;
    for (let i = 0; i < info.width * info.height; i++) if (data[i * 3] > 245 && data[i * 3 + 1] > 245 && data[i * 3 + 2] > 240) { n++; sx += i % info.width; sy += Math.floor(i / info.width); }
    cnt.push(n); pos.push(n ? `${Math.round(sx / n)},${Math.round(sy / n)}` : '-');
  }
  let nf = 0;
  for (let i = 1; i < cnt.length - 1; i++) {
    const nb = Math.max(cnt[i - 1], cnt[i + 1]);
    if (cnt[i] > nb + 25 && cnt[i] > 2 * nb) { nf++; console.log(`FLASH ${files[i]}  white px ${cnt[i - 1]} > ${cnt[i]} < ${cnt[i + 1]}  centroid ${pos[i]}`); }
  }
  console.log(nf ? `${nf} single-frame flash(es) in ${files.length} frames` : `OK: no flashes in ${files.length} frames`);
  process.exit(nf ? 1 : 0);
}

const { browser, page } = await launch(320, 180, '&noclouds');
const res = await page.evaluate(async (fps, LIMITS, wantMap, wantPlot, wisp) => {
  const tl = await import('/src/timeline.js');
  const cfg = await import('/src/config.js');
  const views = await import('/src/views.js');
  const APP = window.APP;
  const hAt = APP.terrain.userData.heightAt;
  const R = cfg.RING.Ro, DECK = cfg.DECK_Y, yaw = cfg.ringYaw();
  const cy = Math.cos(yaw), sy = Math.sin(yaw);
  const toRing = p => [p.x * cy - p.z * sy, p.y - DECK, p.x * sy + p.z * cy];          // world -> ring frame (m)
  const toWorldXZ = (x, z) => [x * cy + z * sy, -x * sy + z * cy];                      // ring frame (m) -> world
  const selfTest = toRing(views.refToWorld([1, 0.5, -2])).map(v => +(v / R).toFixed(3));

  // ---- structure triangle index (world space), 4 m grid
  const scene = APP.scene; scene.updateMatrixWorld(true);
  const tris = [], labels = [], labIdx = new Map(), triLab = [];
  const lab = s => { if (!labIdx.has(s)) { labIdx.set(s, labels.length); labels.push(s); } return labIdx.get(s); };
  const M = APP.camera.matrixWorld.clone(), V = APP.camera.position.clone();
  const addMesh = (m, label) => {
    const g = m.geometry, pos = g && g.attributes.position; if (!pos) return;
    const idx = g.index, n = idx ? idx.count : pos.count, li = lab(label);
    const inst = m.isInstancedMesh ? m.count : 1;
    for (let k = 0; k < inst; k++) {
      M.copy(m.matrixWorld);
      if (m.isInstancedMesh) { const im = M.clone(); m.getMatrixAt(k, im); M.multiply(im); }
      const vs = new Float32Array(pos.count * 3);
      for (let i = 0; i < pos.count; i++) { V.fromBufferAttribute(pos, i).applyMatrix4(M); vs[i * 3] = V.x; vs[i * 3 + 1] = V.y; vs[i * 3 + 2] = V.z; }
      for (let t = 0; t + 2 < n; t += 3) {
        const a = idx ? idx.getX(t) : t, b = idx ? idx.getX(t + 1) : t + 1, c = idx ? idx.getX(t + 2) : t + 2;
        tris.push(vs[a * 3], vs[a * 3 + 1], vs[a * 3 + 2], vs[b * 3], vs[b * 3 + 1], vs[b * 3 + 2], vs[c * 3], vs[c * 3 + 1], vs[c * 3 + 2]);
        triLab.push(li);
      }
    }
  };
  const isFig = m => m.material && m.material.defines && m.material.defines.SURF === 10;
  if (APP.structure) APP.structure.traverse(m => {
    if (!m.isMesh || !m.visible) return;
    const d = (m.material && m.material.defines) || {};
    addMesh(m, isFig(m) ? 'figure' : d.STRUT ? 'strut' : (m.name || (m.parent && m.parent.name) || 'ring'));
  });
  APP.terrain.traverse(m => { if (m.isMesh && m.name === 'conifers') addMesh(m, 'conifer'); });
  const T = new Float32Array(tris), TL = Int32Array.from(triLab), NT = TL.length;
  const CELL = 4, grid = new Map(), key = (i, j, k) => ((i + 2048) * 4096 + (j + 2048)) * 4096 + (k + 2048);
  for (let t = 0; t < NT; t++) {
    const o = t * 9;
    const x0 = Math.floor(Math.min(T[o], T[o + 3], T[o + 6]) / CELL), x1 = Math.floor(Math.max(T[o], T[o + 3], T[o + 6]) / CELL);
    const y0 = Math.floor(Math.min(T[o + 1], T[o + 4], T[o + 7]) / CELL), y1 = Math.floor(Math.max(T[o + 1], T[o + 4], T[o + 7]) / CELL);
    const z0 = Math.floor(Math.min(T[o + 2], T[o + 5], T[o + 8]) / CELL), z1 = Math.floor(Math.max(T[o + 2], T[o + 5], T[o + 8]) / CELL);
    if ((x1 - x0 + 1) * (y1 - y0 + 1) * (z1 - z0 + 1) > 4000) continue;   // degenerate giant triangle
    for (let i = x0; i <= x1; i++) for (let j = y0; j <= y1; j++) for (let k = z0; k <= z1; k++) {
      const kk = key(i, j, k); let a = grid.get(kk); if (!a) grid.set(kk, a = []); a.push(t);
    }
  }
  // closest point on triangle (Ericson), squared distance
  const triD2 = (px, py, pz, o) => {
    const ax = T[o], ay = T[o + 1], az = T[o + 2], bx = T[o + 3], by = T[o + 4], bz = T[o + 5], cx = T[o + 6], cyy = T[o + 7], cz = T[o + 8];
    const abx = bx - ax, aby = by - ay, abz = bz - az, acx = cx - ax, acy = cyy - ay, acz = cz - az;
    const apx = px - ax, apy = py - ay, apz = pz - az;
    const d1 = abx * apx + aby * apy + abz * apz, d2 = acx * apx + acy * apy + acz * apz;
    let qx, qy, qz;
    if (d1 <= 0 && d2 <= 0) { qx = ax; qy = ay; qz = az; }
    else {
      const bpx = px - bx, bpy = py - by, bpz = pz - bz;
      const d3 = abx * bpx + aby * bpy + abz * bpz, d4 = acx * bpx + acy * bpy + acz * bpz;
      if (d3 >= 0 && d4 <= d3) { qx = bx; qy = by; qz = bz; }
      else {
        const vc = d1 * d4 - d3 * d2;
        if (vc <= 0 && d1 >= 0 && d3 <= 0) { const v = d1 / (d1 - d3); qx = ax + v * abx; qy = ay + v * aby; qz = az + v * abz; }
        else {
          const cpx = px - cx, cpy = py - cyy, cpz = pz - cz;
          const d5 = abx * cpx + aby * cpy + abz * cpz, d6 = acx * cpx + acy * cpy + acz * cpz;
          if (d6 >= 0 && d5 <= d6) { qx = cx; qy = cyy; qz = cz; }
          else {
            const vb = d5 * d2 - d1 * d6;
            if (vb <= 0 && d2 >= 0 && d6 <= 0) { const w = d2 / (d2 - d6); qx = ax + w * acx; qy = ay + w * acy; qz = az + w * acz; }
            else {
              const va = d3 * d6 - d5 * d4;
              if (va <= 0 && d4 - d3 >= 0 && d5 - d6 >= 0) { const w = (d4 - d3) / ((d4 - d3) + (d5 - d6)); qx = bx + w * (cx - bx); qy = by + w * (cyy - by); qz = bz + w * (cz - bz); }
              else { const den = 1 / (va + vb + vc), v = vb * den, w = vc * den; qx = ax + abx * v + acx * w; qy = ay + aby * v + acy * w; qz = az + abz * v + acz * w; }
            }
          }
        }
      }
    }
    return (px - qx) ** 2 + (py - qy) ** 2 + (pz - qz) ** 2;
  };
  const stamp = new Int32Array(NT).fill(-1); let qn = 0;
  // nearest structure triangle within maxD; returns {d, l} per label class (figure vs rest)
  // fw/cosV: view direction and cos of the half-diagonal field of view, for figures that are in frame
  const nearest = (p, fw, cosV, maxD = 30) => {
    qn++;
    const best = { s: maxD * maxD, sl: -1, f: maxD * maxD, fv: maxD * maxD };
    for (let r = 1; ; r *= 2) {
      const ci = Math.floor(p.x / CELL), cj = Math.floor(p.y / CELL), ck = Math.floor(p.z / CELL);
      for (let i = ci - r; i <= ci + r; i++) for (let j = cj - r; j <= cj + r; j++) for (let k = ck - r; k <= ck + r; k++) {
        const a = grid.get(key(i, j, k)); if (!a) continue;
        for (const t of a) {
          if (stamp[t] === qn) continue; stamp[t] = qn;
          const d2 = triD2(p.x, p.y, p.z, t * 9);
          if (labels[TL[t]] === 'figure') {
            if (d2 < best.f) best.f = d2;
            if (d2 < best.fv) {
              const o = t * 9, cx = (T[o] + T[o + 3] + T[o + 6]) / 3 - p.x, cyy = (T[o + 1] + T[o + 4] + T[o + 7]) / 3 - p.y, cz = (T[o + 2] + T[o + 5] + T[o + 8]) / 3 - p.z;
              if ((cx * fw.x + cyy * fw.y + cz * fw.z) >= cosV * Math.hypot(cx, cyy, cz)) best.fv = d2;
            }
          } else if (d2 < best.s) { best.s = d2; best.sl = TL[t]; }
        }
      }
      const reach = r * CELL;   // the searched cube covers at least this distance around p
      if ((Math.sqrt(best.s) <= reach && Math.sqrt(best.f) <= reach && Math.sqrt(best.fv) <= reach) || reach >= maxD) break;
    }
    return { s: Math.sqrt(best.s), sl: best.sl >= 0 ? labels[best.sl] : '-', f: Math.sqrt(best.f), fv: Math.sqrt(best.fv) };
  };
  // ---- terrain: 3D distance to the heightfield surface (polar samples out to 46 m)
  const RAD = [1.5, 3, 5, 7.5, 10, 13, 16, 20, 25, 30, 38, 46], NA = 32;
  const terrainClr = p => {
    const h0 = hAt(p.x, p.z);
    if (h0 >= p.y) return p.y - h0;
    let best = p.y - h0;
    for (const r of RAD) {
      if (r >= best) break;
      for (let a = 0; a < NA; a++) {
        const an = (a + (r % 2) * 0.5) * 2 * Math.PI / NA, h = hAt(p.x + r * Math.cos(an), p.z + r * Math.sin(an));
        const d = h >= p.y ? r : Math.hypot(r, p.y - h);
        if (d < best) best = d;
      }
    }
    return best;
  };
  // clouds.js returns zero density above uTop + uWisp + 60 (uWisp = 200, the wall-hugging wisps near the ring)
  const ceiling = cfg.CLOUDS.top + wisp + 60;
  const altOf = p => p.y + (p.x * p.x + p.z * p.z) / (2 * cfg.EARTH_R);

  // ---- sample the film
  const cam = new APP.camera.constructor();
  const N = Math.round(tl.TOTAL * fps), shots = {}, path = [];
  let prev = null;
  for (let f = 0; f < N; f++) {
    const t = f / fps, c = tl.cameraAt(t);
    const s = shots[c.shot] || (shots[c.shot] = {
      t0: t, t1: t, n: 0, check: (tl.SHOTS.find(x => x.name === c.shot) || {}).check || {},
      terr: [1e9, 0], str: [1e9, 0, ''], fig: [1e9, 0], figV: [1e9, 0], cloud: [1e9, 0], rot: [0, 0], angAcc: [0, 0], linAcc: [0, 0],
      v: [1e9, 0], pitch: [90, -90], fov: [c.fov, c.fov], viol: {},
    });
    s.t1 = t; s.n++; s.fov[1] = c.fov;
    const p = c.pos;
    cam.position.copy(p); cam.up.set(0, 1, 0); cam.lookAt(c.tgt); cam.updateMatrixWorld();
    const q = cam.quaternion.clone(), fw = c.tgt.clone().sub(p).normalize();
    const pitch = Math.asin(Math.max(-1, Math.min(1, fw.y))) * 180 / Math.PI;
    const cosV = Math.cos(Math.atan(Math.tan(c.fov * Math.PI / 360) * Math.hypot(1, 16 / 9)));
    const tc = terrainClr(p), nn = nearest(p, fw, cosV), cl = altOf(p) - ceiling;
    if (tc < s.terr[0]) s.terr = [tc, t];
    if (nn.s < s.str[0]) s.str = [nn.s, t, nn.sl];
    if (nn.f < s.fig[0]) s.fig = [nn.f, t];
    if (nn.fv < s.figV[0]) s.figV = [nn.fv, t];
    if (cl < s.cloud[0]) s.cloud = [cl, t];
    s.pitch = [Math.min(s.pitch[0], pitch), Math.max(s.pitch[1], pitch)];
    const L = { ...LIMITS, ...s.check };
    // violation spans per kind: [first t, last t, worst value]
    const bad = (k, cond, val) => {
      if (!cond) return;
      const e = s.viol[k] || (s.viol[k] = [t, t, val]), mx = k === 'rot' || k === 'pitch';
      e[1] = t; e[2] = mx ? Math.max(Math.abs(e[2]), Math.abs(val)) : Math.min(e[2], val);
    };
    bad('terrain', tc < L.terrain, tc); bad('structure', nn.s < L.structure, nn.s);
    bad('figure', nn.f < L.figure, nn.f); bad('figureInView', nn.fv < L.figureInView, nn.fv);
    bad('cloud', cl < L.cloud, cl); bad('pitch', Math.abs(pitch) > L.pitch, pitch);
    if (prev && prev.shot === c.shot) {
      const rot = prev.q.angleTo(q) * 180 / Math.PI * fps, v = p.distanceTo(prev.p) * fps;
      if (rot > s.rot[0]) s.rot = [rot, t];
      bad('rot', rot > L.rot, rot);
      s.v = [Math.min(s.v[0], v), Math.max(s.v[1], v)];
      if (prev.rot !== undefined) {
        const aa = Math.abs(rot - prev.rot) * fps, la = Math.abs(v - prev.v) * fps;
        if (aa > s.angAcc[0]) s.angAcc = [aa, t];
        if (la > s.linAcc[0]) s.linAcc = [la, t];
      }
      prev = { p: p.clone(), q, shot: c.shot, rot, v };
    } else prev = { p: p.clone(), q, shot: c.shot };
    if (wantPlot && f % 2 === 0) { const r = toRing(p), g = toRing(p.clone().add(fw.clone().multiplyScalar(30))); path.push([c.shot, r[0], r[2], g[0], g[2], r[1]]); }
  }
  let map = null, plot = null;
  if (wantMap) {
    const xs = [], zs = [], lines = [];
    for (let x = -6; x <= 6.01; x += 0.25) xs.push(x);
    for (let z = -8; z <= 10.01; z += 0.5) zs.push(z);
    lines.push('      ' + xs.map(x => (Math.abs(x % 1) < 1e-6 ? String(Math.round(x)).padStart(4) : '    ')).join(''));
    for (const z of zs) lines.push(z.toFixed(1).padStart(5) + ' ' + xs.map(x => { const [wx, wz] = toWorldXZ(x * R, z * R); return String(Math.round((hAt(wx, wz) - DECK) / 10)).padStart(4); }).join(''));
    map = lines.join('\n');
  }
  if (wantPlot) {
    let x0 = -4, x1 = 4, z0 = -4, z1 = 4;
    for (const [, x, z] of path) { x0 = Math.min(x0, x / R - 0.5); x1 = Math.max(x1, x / R + 0.5); z0 = Math.min(z0, z / R - 0.5); z1 = Math.max(z1, z / R + 0.5); }
    x0 = Math.max(x0, -25); x1 = Math.min(x1, 25); z0 = Math.max(z0, -25); z1 = Math.min(z1, 25);
    const px = 900 / Math.max(x1 - x0, z1 - z0), W = Math.round((x1 - x0) * px), H = Math.round((z1 - z0) * px);
    const hm = new Float32Array(W * H);
    for (let j = 0; j < H; j++) for (let i = 0; i < W; i++) { const [wx, wz] = toWorldXZ((x0 + (i + 0.5) / px) * R, (z0 + (j + 0.5) / px) * R); hm[j * W + i] = hAt(wx, wz) - DECK; }
    plot = { x0, z0, px, W, H, hm: Array.from(hm), R };
  }
  const tot = { tris: NT, cells: grid.size, labels };
  return { selfTest, ceiling, N, shots, map, plot, path, tot };
}, fps, LIMITS, flag('map'), !!arg('plot', null), +arg('wisp', 200));

console.log(`frames ${res.N} @${fps} fps  structure tris ${res.tot.tris} (${res.tot.cells} cells)  cloud ceiling ${res.ceiling.toFixed(0)} m  ring-frame self test [1,0.5,-2] -> ${res.selfTest}`);
console.log('limits', JSON.stringify(LIMITS), '(per-shot overrides via SHOTS[i].check)');
const f1 = (v, w = 6) => (v >= 29.9 ? '>30' : v.toFixed(1)).padStart(w);
let nViol = 0;
console.log('shot          time         terrain        structure (nearest)       fig/inView  cloud   rot d/s     angAcc  linAcc  v m/s      pitch     fov');
for (const [n, s] of Object.entries(res.shots)) {
  const viol = Object.entries(s.viol).map(([k, [a, b, v]]) => `${k}(${v.toFixed(1)})@${a.toFixed(2)}-${b.toFixed(2)}`);
  const warn = [];
  if (s.angAcc[0] > WARN.angAcc) warn.push(`angAcc@${s.angAcc[1].toFixed(2)}`);
  if (s.linAcc[0] > WARN.linAcc) warn.push(`linAcc@${s.linAcc[1].toFixed(2)}`);
  nViol += viol.length;
  console.log(`${n.padEnd(10)} ${s.t0.toFixed(2).padStart(6)}-${s.t1.toFixed(2).padStart(6)}  ${s.terr[0].toFixed(1).padStart(7)}@${s.terr[1].toFixed(2).padStart(5)}  ${f1(s.str[0])}@${s.str[1].toFixed(2).padStart(5)} ${s.str[2].slice(0, 12).padEnd(12)} ${f1(s.fig[0], 5)}/${f1(s.figV[0], 4).trim().padEnd(4)} ${s.cloud[0].toFixed(0).padStart(6)}  ${s.rot[0].toFixed(1).padStart(5)}@${s.rot[1].toFixed(2).padStart(5)}  ${s.angAcc[0].toFixed(0).padStart(6)}  ${s.linAcc[0].toFixed(0).padStart(6)}  ${s.v[0].toFixed(1)}..${s.v[1].toFixed(1)}`.padEnd(150) +
    `${s.pitch[0].toFixed(0).padStart(4)}..${s.pitch[1].toFixed(0).padEnd(4)} ${s.fov.map(v => v.toFixed(0)).join('>')}` +
    (viol.length ? '  VIOLATION ' + viol.join(' ') : '') + (warn.length ? '  warn ' + warn.join(' ') : ''));
}
console.log(nViol ? `${nViol} violation(s)` : 'OK: no violations');
if (res.map) console.log(res.map);
if (arg('json', null)) fs.writeFileSync(arg('json'), JSON.stringify({ ceiling: res.ceiling, limits: LIMITS, shots: res.shots }, null, 1));

if (res.plot) {
  const { x0, z0, px, W, H, hm, R } = res.plot;
  const buf = Buffer.alloc(W * H * 3);
  for (let i = 0; i < W * H; i++) {
    const h = hm[i], k = Math.max(0, Math.min(1, (h + 400) / 500));        // -400 m .. +100 m rel. deck
    const contour = Math.abs(((h % 20) + 20) % 20 - 10) > 9.0 ? 0.75 : 1;
    const above = h > 0 ? 1 : 0;
    buf[i * 3] = (30 + 170 * k + 50 * above) * contour; buf[i * 3 + 1] = (40 + 160 * k + 40 * above) * contour; buf[i * 3 + 2] = (70 + 150 * k) * contour;
  }
  const X = x => ((x / R - x0) * px).toFixed(1), Z = z => ((z / R - z0) * px).toFixed(1);
  const cols = ['#ff5050', '#ffb030', '#f0f040', '#60ff60', '#40e0ff', '#5080ff', '#c060ff', '#ff60c0', '#ffffff', '#a0ffa0', '#ffa0a0', '#a0a0ff', '#ffd0a0', '#60c0a0'];
  const names = [...new Set(res.path.map(p => p[0]))];
  let svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}">`;
  svg += `<circle cx="${X(0)}" cy="${Z(0)}" r="${(px).toFixed(1)}" fill="none" stroke="#000" stroke-width="2"/><circle cx="${X(0)}" cy="${Z(0)}" r="${(px * 42.6 / 55).toFixed(1)}" fill="none" stroke="#000" stroke-width="1"/>`;
  svg += `<line x1="${X(-82)}" y1="${Z(0)}" x2="${X(-55)}" y2="${Z(0)}" stroke="#000" stroke-width="3"/><line x1="${X(55)}" y1="${Z(0)}" x2="${X(82)}" y2="${Z(0)}" stroke="#000" stroke-width="3"/>`;
  names.forEach((n, ni) => {
    const pts = res.path.filter(p => p[0] === n), c = cols[ni % cols.length];
    for (let i = 0; i < pts.length; i += 6) svg += `<line x1="${X(pts[i][1])}" y1="${Z(pts[i][2])}" x2="${X(pts[i][3])}" y2="${Z(pts[i][4])}" stroke="${c}" stroke-opacity="0.45" stroke-width="1"/>`;
    svg += `<polyline fill="none" stroke="${c}" stroke-width="2.5" points="${pts.map(p => X(p[1]) + ',' + Z(p[2])).join(' ')}"/>`;
    svg += `<circle cx="${X(pts[0][1])}" cy="${Z(pts[0][2])}" r="4" fill="${c}"/>`;
    svg += `<text x="${+X(pts[0][1]) + 6}" y="${+Z(pts[0][2]) - 6}" font-family="Arial" font-size="14" fill="${c}" stroke="#000" stroke-width="0.6">${ni + 1} ${n}</text>`;
  });
  svg += `<text x="8" y="${H - 10}" font-family="Arial" font-size="13" fill="#fff">ring frame, +Z (hero side) down, grid 1 R = ${R} m; contours 20 m; light = above deck</text></svg>`;
  await sharp(buf, { raw: { width: W, height: H, channels: 3 } }).composite([{ input: Buffer.from(svg) }]).png().toFile(arg('plot'));
  console.log('plot ->', arg('plot'));
}
await browser.close();
process.exit(nViol ? 1 : 0);
