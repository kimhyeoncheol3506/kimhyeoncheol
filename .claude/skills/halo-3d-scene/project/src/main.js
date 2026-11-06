import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { sunDirection, DECK_Y, RING } from './config.js';
import { createSky } from './sky.js';
import { createTerrain, LAMPS_MAX } from './terrain.js';
import { LAND_AB } from './glsl/rock.js';
import { Post } from './post.js';
import { VIEWS, applyView, refToWorld } from './views.js';
import { cameraAt, TOTAL, SHOTS } from './timeline.js';

const qs = new URLSearchParams(location.search);
const W = +qs.get('w') || window.innerWidth;
const H = +qs.get('h') || window.innerHeight;
const CAPTURE = qs.has('capture');

const renderer = new THREE.WebGLRenderer({ antialias: false, logarithmicDepthBuffer: true, preserveDrawingBuffer: true, powerPreference: 'high-performance' });
renderer.setPixelRatio(1);
renderer.setSize(W, H, !CAPTURE);
renderer.outputColorSpace = THREE.LinearSRGBColorSpace;
renderer.autoClear = false;
document.body.appendChild(renderer.domElement);

const camera = new THREE.PerspectiveCamera(40, W / H, 0.2, 600000);
const scene = new THREE.Scene();

// uniforms shared by every custom material
const shared = {
  uniforms: {
    uSunDir: { value: sunDirection() },
    uSkyExposure: { value: 1.0 },
    uHorizonDip: { value: 0.025 },
    uFarDip: { value: 0 },
    uDipWin: { value: new THREE.Vector2(600, 1800) },          // camera-relative far-field dip (tan): >0 lowers sky + terrain beyond ~4-12 km
    uFogDensity: { value: 1 / 15000 },
    uSkyView: { value: new THREE.Vector4(1, 0, 0, 0) },        // per-view sky framing (zoom, centre el, glow az offset, sky dip): common.js skyView
    uTime: { value: 0 },
    uLampPos: { value: [...Array(LAMPS_MAX)].map(() => new THREE.Vector4()) },
    uLampCol: { value: [...Array(LAMPS_MAX)].map(() => new THREE.Vector4()) },
    uLampCount: { value: 0 },
    uReflTex: { value: null },
    uResolution: { value: new THREE.Vector2(W, H) },
  },
};
const black = new THREE.DataTexture(new Uint8Array([0, 0, 0, 255]), 1, 1); black.needsUpdate = true;
shared.uniforms.uReflTex.value = black;

const post = new Post(renderer, W, H);
const sky = createSky(shared);
scene.add(sky);

const modules = { shared, scene, camera, renderer, post };
window.APP = modules;

const controls = new OrbitControls(camera, renderer.domElement);
controls.target.copy(refToWorld([0, -0.3, 0]));
controls.enableDamping = true;
controls.maxDistance = 20000;
applyView(camera, VIEWS[qs.get('view') || 7]);
controls.target.copy(refToWorld(VIEWS[qs.get('view') || 7].tgt));

async function init() {
  const terrain = await createTerrain(shared);
  scene.add(terrain);
  modules.terrain = terrain;
  try {
    const { createStructure } = await import('./structure.js');
    const st = await createStructure(shared, terrain);
    scene.add(st);
    modules.structure = st;
  } catch (e) { console.warn('structure', e); }
  try {
    const { createVillageLights } = await import('./lights.js');
    modules.village = createVillageLights(shared, terrain, renderer, scene);
  } catch (e) { console.warn('lights', e); }
  if (!qs.has('noclouds')) try {
    const { Clouds } = await import('./clouds.js');
    modules.clouds = await Clouds.create(renderer, shared, post, W, H, CAPTURE ? 1 : 0.5);
  } catch (e) { console.warn('clouds', e); }
  // MATTE: camera-projected reference background (src/matte.js): '&nomatte' off (render path as before),
  // '&mattew' outputs its weight as grey. Captures start with it off until setView / setMatte selects a projector.
  // It needs the reference backgrounds in data/matte (baked from ref/, neither is in the public repo): skipped without.
  const hasMatte = !qs.has('nomatte') && await fetch('data/matte/force.json')
    .then(r => r.ok && /json/.test(r.headers.get('content-type') || '')).catch(() => false);
  if (hasMatte) try {
    const { Matte } = await import('./matte.js');
    modules.matte = post.matte = await Matte.create(renderer, post, camera, { showW: qs.has('mattew') });
    modules.matte.set(CAPTURE ? 0 : +(qs.get('view') || 7));
  } catch (e) { console.warn('matte', e); }
}

let time = 0, frameNo = 0;
function render(t) {
  time = t;
  shared.uniforms.uTime.value = t;
  camera.updateMatrixWorld();
  if (modules.village) modules.village.update(camera, t);
  renderer.setRenderTarget(post.sceneRT);
  renderer.setClearColor(0x000000, 1);
  renderer.clear();
  renderer.render(scene, camera);
  let hdr = post.sceneRT;
  if (modules.clouds) hdr = modules.clouds.render(post.sceneRT, camera, t, frameNo++);
  modules.lastHdr = hdr;
  post.finish(hdr, t, null);
}
modules.render = render;
modules.post = post;
// grade tuning (tools/gradetune.mjs): re-run tone + grade on the last HDR frame into a small 8-bit target
let gradeRT = null;
modules.snapHdr = () => {   // keep a copy of the last HDR frame (one per tuned view)
  const rt = new THREE.WebGLRenderTarget(W, H, { type: THREE.HalfFloatType, depthBuffer: false });
  renderer.setRenderTarget(rt); renderer.setClearColor(0x000000, 1); renderer.clear();
  post.accMat.uniforms.tSrc.value = modules.lastHdr.texture; post.accMat.uniforms.uW.value = 1;
  post.pass(post.accMat, rt);
  return rt;
};
modules.regrade = (params, hdr = modules.lastHdr, w = 418, h = 235) => {
  if (!gradeRT || gradeRT.width !== w) gradeRT = new THREE.WebGLRenderTarget(w, h);
  Object.assign(post.params, params);
  post.finish(hdr, time, gradeRT);
  const px = new Uint8Array(w * h * 4);
  renderer.readRenderTargetPixels(gradeRT, 0, 0, w, h, px);
  return px;
};

// ---- film rendering: timeline camera, K sub-frames with motion blur (shutter fraction of a frame)
// and sub-pixel jitter, accumulated in HDR before bloom + tone mapping.
const halton = (i, b) => { let f = 1, r = 0; while (i > 0) { f /= b; r += f * (i % b); i = Math.floor(i / b); } return r; };
let landAB2 = null;
function setTimelineCamera(t) {
  const c = cameraAt(t);
  camera.position.copy(c.pos); camera.up.set(0, 1, 0); camera.lookAt(c.tgt);
  if (c.roll) camera.rotateZ(c.roll);
  camera.fov = c.fov; camera.updateProjectionMatrix();
  shared.uniforms.uFarDip.value = c.dip || 0;
  setSkyView(c.sky);
  // free-flight film: no shot carries `matte`, so the background is the 3D world (matte off)
  if (modules.setMatte) modules.setMatte(c.matte || 0, 1, 30, 0);
  // per-shot snow outcrops (rock.js uLandAB2.w: r9 p2 pieces 1 / p1 0) - every terrain level's copy of the uniform
  if (!landAB2 || !landAB2.length) { landAB2 = []; scene.traverse(o => { const u = o.material && o.material.uniforms; if (u && u.uLandAB2 && !landAB2.includes(u.uLandAB2)) landAB2.push(u.uLandAB2); }); }
  for (const u of landAB2) u.value.w = c.outcrop ?? LAND_AB[1][3];
  return c;
}
// sky framing [zoom k, zoom centre el (rad), glow azimuth offset (deg, + = right), sky-only dip (tan)]; none = off
function setSkyView(s) {
  const [k, ce, az, w] = s || [1, 0, 0, 0];
  shared.uniforms.uSkyView.value.set(k, ce, az * Math.PI / 180, w);
}
modules.renderFrame = (t, { K = 1, shutter = 0.5, fps = 30 } = {}) => {
  post.clearAccum();
  let fade = 1;
  for (let k = 0; k < K; k++) {
    const tk = t + ((k + 0.5) / K - 0.5) * shutter / fps;
    const c = setTimelineCamera(tk);
    if (k === 0 || Math.abs(tk - t) < 1e-6) fade = c.fade;
    if (K > 1) camera.setViewOffset(W, H, halton(k + 1, 2) - 0.5, halton(k + 1, 3) - 0.5, W, H);
    shared.uniforms.uTime.value = tk;
    camera.updateMatrixWorld();
    if (modules.village) modules.village.update(camera, tk);
    renderer.setRenderTarget(post.sceneRT);
    renderer.setClearColor(0x000000, 1);
    renderer.clear();
    renderer.render(scene, camera);
    let hdr = post.sceneRT;
    if (modules.clouds) hdr = modules.clouds.render(post.sceneRT, camera, tk, frameNo++);
    post.accumulate(hdr, 1 / K);
    camera.clearViewOffset();
  }
  fade = cameraAt(t).fade;
  post.finish(post.accumRT, t, null, fade);
  return cameraAt(t).shot;
};
// stills: K jittered sub-frames of the current (static) camera, accumulated like film frames
modules.renderStill = (t, K = 8) => {
  post.clearAccum();
  for (let k = 0; k < K; k++) {
    if (K > 1) camera.setViewOffset(W, H, halton(k + 1, 2) - 0.5, halton(k + 1, 3) - 0.5, W, H);
    shared.uniforms.uTime.value = t;
    camera.updateMatrixWorld();
    if (modules.village) modules.village.update(camera, t);
    renderer.setRenderTarget(post.sceneRT);
    renderer.setClearColor(0x000000, 1);
    renderer.clear();
    renderer.render(scene, camera);
    let hdr = post.sceneRT;
    if (modules.clouds) hdr = modules.clouds.render(post.sceneRT, camera, t, frameNo++);
    post.accumulate(hdr, 1 / K);
    camera.clearViewOffset();
  }
  modules.lastHdr = post.accumRT;
  post.finish(post.accumRT, t, null);
};
modules.TOTAL = TOTAL;
modules.SHOTS = SHOTS;

modules.setView = n => { applyView(camera, VIEWS[n]); controls.target.copy(refToWorld(VIEWS[n].tgt)); shared.uniforms.uFarDip.value = VIEWS[n].dip || 0; setSkyView(VIEWS[n].sky); };
// MATTE: a reference view selects its own projector (exact camera: no border feather); the film timeline calls
// setMatte(n, strength, featherPx, force) per shot (n = 0: off; force: the stills' force-far mask, 0 for moving cameras)
{ const sv = modules.setView; modules.setView = n => { sv(n); if (modules.matte) modules.matte.set(n, 1, 0, 1); }; }
modules.setMatte = (n, strength = 1, feather = 120, force = 0) => { if (modules.matte) modules.matte.set(n, strength, feather, force); };
modules.setCamera = (pos, tgt, fov, roll = 0) => {
  camera.position.set(...pos); camera.up.set(0, 1, 0); camera.lookAt(...tgt);
  if (roll) camera.rotateZ(roll);
  camera.fov = fov; camera.updateProjectionMatrix();
};
modules.capture = () => renderer.domElement.toDataURL('image/png');

modules.ready = init().then(() => { document.body.dataset.ready = '1'; return true; });

if (CAPTURE) document.body.classList.add('capture');
if (!CAPTURE) {
  const hud = document.getElementById('hud');
  const bar = document.getElementById('views');
  const names = { 2: 'Arrival', 4: 'Long lens', 7: 'Hero', 5: 'West cliff', 6: 'East cliff', 8: 'Top', 9: 'Below', 3: 'Underside', 1: 'Terrace', 10: 'Walkway', 11: 'Drone' };
  for (const [n, label] of Object.entries(names)) {
    const b = document.createElement('button'); b.textContent = label;
    b.onclick = () => { film = null; modules.setView(+n); };
    bar.appendChild(b);
  }
  const fb = document.createElement('button'); fb.textContent = '▶ Film'; fb.className = 'film';
  fb.onclick = () => { film = film === null ? performance.now() / 1000 : null; };
  bar.appendChild(fb);
  let last = performance.now(), frames = 0, acc = 0, film = qs.has('film') ? 0 : null;
  window.addEventListener('keydown', e => {
    const map = { '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '0': 10, '-': 11 };
    if (map[e.key]) { film = null; modules.setView(map[e.key]); }
    if (e.key === 'v' || e.key === 'V') { film = film === null ? performance.now() / 1000 : null; }
    if (e.key === 'p') console.log(JSON.stringify({ pos: camera.position.toArray().map(v => +v.toFixed(2)), tgt: controls.target.toArray().map(v => +v.toFixed(2)), fov: camera.fov }));
  });
  const loop = () => {
    requestAnimationFrame(loop);
    const now = performance.now(); const dt = now - last; last = now; acc += dt; frames++;
    if (acc > 500) { if (hud) hud.textContent = `${(1000 * frames / acc).toFixed(1)} fps`; acc = 0; frames = 0; }
    if (film !== null) { if (film === 0) film = now / 1000; const ft = (now / 1000 - film) % TOTAL; setTimelineCamera(ft); if (hud) hud.dataset.shot = cameraAt(ft).shot; }
    else controls.update();
    render(now / 1000);
  };
  modules.ready.then(loop);
  window.addEventListener('resize', () => {
    if (qs.get('w')) return;
    const w = window.innerWidth, h = window.innerHeight;
    renderer.setSize(w, h); camera.aspect = w / h; camera.updateProjectionMatrix();
    post.setSize(w, h); shared.uniforms.uResolution.value.set(w, h);
    if (modules.clouds) modules.clouds.setSize(w, h);
  });
}
