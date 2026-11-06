// Matte captures in one browser session (one GPU lock).
// usage: node tools/matte_cap.mjs tag '[{"v":7,"mode":"on","K":2}, {"v":7,"mode":"w"}, {"v":7,"mode":"off"},
//          {"v":4,"mode":"on","side":30,"yaw":2}, {"v":7,"mode":"struct","K":4}]'
// modes: on (setView n: its own matte), off (same camera, matte off), w (matte weight as grey),
//        struct (weight with the terrain hidden: the structure's own silhouette, for tools/matte_bake.mjs)
// side / up (m, camera right / up) and yaw (deg, + = turn left): a moving-camera test with view v's matte (feather 120 px, or j.feather)
// -> out/shots/<tag>_v<v>[_<mode>].png, plus cmp_<tag>_v<v>.png (ref | ours) for mode 'on' at the exact camera
import fs from 'node:fs';
import { launch, compare } from './shot.mjs';
import { gpuRest } from './gpulock.mjs';

const tag = process.argv[2] || 'matte';
const jobs = JSON.parse(process.argv[3] || '[{"v":7,"mode":"on"}]');
const W = 1672, H = 941;
const { browser, page } = await launch(W, H, process.env.Q || '');
for (const j of jobs) {
  const t0 = Date.now();
  if (j.mode === 'bench') {
    // cost of the matte: N sub-frame passes + composites, synced by a 1-px readback (gl.finish does not block on ANGLE)
    const r = await page.evaluate((j) => {
      const A = window.APP, M = A.matte, gl = A.renderer.getContext(), px = new Uint8Array(4);
      A.setView(j.v); A.render(10);
      const sync = () => { A.renderer.setRenderTarget(null); gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px); };
      const N = 40; sync();
      let t = performance.now();
      for (let i = 0; i < N; i++) { M.clear(); M.sub(1); }
      sync(); const sub = (performance.now() - t) / N;
      t = performance.now();
      for (let i = 0; i < N; i++) M.composite(null, 1);
      sync(); const comp = (performance.now() - t) / N;
      t = performance.now();
      for (let i = 0; i < 10; i++) A.render(10);
      sync(); const full = (performance.now() - t) / 10;
      return { sub, comp, full, type: M.type };
    }, j);
    console.log('bench', JSON.stringify(r));
    continue;
  }
  const ms = await page.evaluate(async (j) => {
    const A = window.APP;
    A.setView(j.v);
    if (j.side || j.up || j.yaw) {
      const c = A.camera, THREE_V = c.position.constructor;
      const right = new THREE_V().setFromMatrixColumn(c.matrixWorld, 0), up = new THREE_V().setFromMatrixColumn(c.matrixWorld, 1);
      c.position.addScaledVector(right, j.side || 0).addScaledVector(up, j.up || 0);
      c.rotateOnWorldAxis(new THREE_V(0, 1, 0), (j.yaw || 0) * Math.PI / 180);
      c.updateMatrixWorld();
      A.setMatte(j.v, 1, j.feather ?? 120);
    }
    if (j.mode === 'off') A.setMatte(0);
    const showW = j.mode === 'w' || j.mode === 'struct';
    if (A.matte) A.matte.showW = showW;
    const hide = j.mode === 'struct';
    if (A.terrain) A.terrain.visible = !hide;
    const t1 = performance.now();
    const K = j.K || 1;
    if (K > 1) A.renderStill(10, K); else { A.render(10); A.render(10); }
    A.renderer.getContext().finish();
    const dt = performance.now() - t1;
    if (A.matte) A.matte.showW = false;
    if (A.terrain) A.terrain.visible = true;
    return dt;
  }, j);
  const url = await page.evaluate(() => window.APP.capture());
  const exact = !(j.side || j.up || j.yaw);
  const name = `${tag}_v${j.v}${j.mode === 'on' && exact ? '' : '_' + j.mode}${exact ? '' : `_s${j.side || 0}y${j.yaw || 0}`}`;
  const file = `out/shots/${name}.png`;
  fs.writeFileSync(file, Buffer.from(url.split(',')[1], 'base64'));
  if (j.mode === 'on' && exact) {
    const r = await compare(`ref/${j.v}.webp`, file, `out/shots/cmp_${tag}_v${j.v}.png`);
    console.log(name, `${ms.toFixed(0)} ms render`, `dE=${r.dE} dL=${r.dL}`);
  } else console.log(name, `${ms.toFixed(0)} ms render`);
  await gpuRest(Date.now() - t0);
}
await browser.close();
