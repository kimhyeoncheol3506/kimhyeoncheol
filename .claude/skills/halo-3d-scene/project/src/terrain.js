// Nested-grid terrain from baked DEM levels (L0 far .. L3 sculpted near field) + lake water.
import * as THREE from 'three';
import { NOISE, ATMOS, FARDIP } from './glsl/common.js';
import { WATER } from './glsl/water.js';
import { FAR, FAR_R7 } from './glsl/far.js';
import { ROCK, rockUniforms } from './glsl/rock.js';
import { EARTH_R, LAKE_Y, DECK_Y } from './config.js';
import { VIEWS, refToWorld } from './views.js';

export const LAMPS_MAX = 24;
const GEODBG = typeof location !== 'undefined' && new URLSearchParams(location.search).has('geodbg');
// '&nofar': the pre-round-8 far field (L0 at 312 m, L1's outer band blended into it) for A/B comparisons
const NOFAR = typeof location !== 'undefined' && new URLSearchParams(location.search).has('nofar');
// '&farr7': the round-8 geometry with the pre-round-8 far shading (glsl/far.js FAR_R7)
const FARR7 = typeof location !== 'undefined' && new URLSearchParams(location.search).has('farr7');
// '&nosum': L1 without the pass-2 summit / crest pass (tools/farsummit.mjs, meta.SUMMIT) for A/B comparisons
const NOSUM = typeof location !== 'undefined' && new URLSearchParams(location.search).has('nosum');

const terrainVert = /* glsl */ `
#include <common>
#include <logdepthbuf_pars_vertex>
${FARDIP}
attribute vec4 attr;
attribute vec3 nrmS;
attribute float rockM;
attribute float keyV;           // key-light visibility (tools/farkey.mjs; inner levels: L1's, bilinear)
varying vec3 vPos;
varying vec3 vNrm;
varying vec3 vNrmS;
varying vec4 vAttr;
varying float vRock;
varying float vKey;
uniform float uEarthR;
void main(){
  vPos = position;
  vKey = keyV;
  vNrm = normal;
  vNrmS = nrmS;
  vAttr = attr;
  vRock = rockM;
  vec3 p = position;
  float r2 = dot(p.xz, p.xz);
  p.y -= r2 / (2.0 * uEarthR) + farOff(position);
  gl_Position = projectionMatrix * viewMatrix * vec4(p, 1.0);
  #include <logdepthbuf_vertex>
}
`;

const terrainFrag = /* glsl */ `
#include <common>
#include <logdepthbuf_pars_fragment>
${NOISE}
${ATMOS}
varying vec3 vPos;
varying vec3 vNrm;
varying vec3 vNrmS;             // ~5 m smoothed normal (snow placement)
varying vec4 vAttr;
varying float vRock;            // L3.rock: 0 = not sculpted, else 1/255 + baked outcrop relief (0..6 m)
varying float vKey;             // key-light visibility (cast shadows of the ranges; glsl/far.js)
uniform float uDetail;          // 1 for near levels, 0 for far
uniform vec4 uLampPos[${LAMPS_MAX}];   // xyz, radius
uniform vec4 uLampCol[${LAMPS_MAX}];   // rgb*intensity, w = spot-ness unused
uniform int uLampCount;
uniform sampler2D uReflTex;     // planar reflection (lights) of the lake
uniform vec2 uResolution;
uniform float uLakeY;
uniform sampler2D uTownGlow;    // light-pollution map over L1 extent
uniform float uTownGlowSize;

float rockNoise(vec3 p){ return gfbm3(p, 5); }
${WATER}
${NOFAR || FARR7 ? FAR_R7 : FAR}

#define LAMPS_MAX ${LAMPS_MAX}
${ROCK}

void main(){
  #include <logdepthbuf_fragment>
  vec3 V = vPos - cameraPosition;
  float dist = length(V);
  vec3 vd = V / dist;
  vec3 n0 = normalize(vNrm);
  float skyVis = vAttr.x, glowVis = vAttr.y;
  float water = step(0.5, vAttr.z);

  vec3 col;
  if (water > 0.5 && abs(vPos.y - uLakeY) < 25.0) {
    col = lakeColor(vPos, vd, skyVis);   // glsl/water.js
  } else {
    // ---------------- land (glsl/rock.js)
    #ifdef GEODBG
    // (URL flag &geodbg: plain clay under the twilight dome + a raking key, to judge the geometry alone)
    col = vec3(0.45) * (skyIrradiance(n0, skyVis, glowVis) + 0.5 * max(dot(n0, normalize(vec3(-0.6, 0.45, 0.35))), 0.0) * vec3(0.10, 0.09, 0.08));
    #else
    col = shadeLand(dist, n0, skyVis, glowVis);
    #endif
  }
  col = applyAtmos(col, cameraPosition, vPos);
  gl_FragColor = vec4(col, 1.0);
}
`;

// sparse snow-dusted spruce on the ledges > 600 m below the deck, under the cloud sea (instanced lathe tiers)
const treeVert = /* glsl */ `
#include <common>
#include <logdepthbuf_pars_vertex>
varying vec3 vPos;
varying vec3 vNrm;
varying float vTop;
uniform float uEarthR;
void main(){
  vec4 wp = modelMatrix * instanceMatrix * vec4(position, 1.0);
  vPos = wp.xyz;
  vNrm = mat3(modelMatrix * instanceMatrix) * normal;
  vTop = position.y / 10.5;
  vec3 p = wp.xyz;
  p.y -= dot(p.xz, p.xz) / (2.0 * uEarthR);
  gl_Position = projectionMatrix * viewMatrix * vec4(p, 1.0);
  #include <logdepthbuf_vertex>
}
`;
const treeFrag = /* glsl */ `
#include <common>
#include <logdepthbuf_pars_fragment>
${NOISE}
${ATMOS}
varying vec3 vPos;
varying vec3 vNrm;
varying float vTop;
uniform vec4 uLampPos[${LAMPS_MAX}];
uniform vec4 uLampCol[${LAMPS_MAX}];
uniform int uLampCount;
void main(){
  #include <logdepthbuf_fragment>
  vec3 n = normalize(vNrm);
  vec3 alb = srgb2lin(vec3(0.085, 0.115, 0.10));
  // snow caught on the upper side of each tier, patchy
  float sn = smoothstep(0.05, 0.55, n.y + 0.45 * (vnoise3(vPos * 1.7) - 0.5));
  alb = mix(alb, vec3(0.80, 0.82, 0.88), sn * 0.8);
  vec3 col = alb * skyIrradiance(n, 0.55 + 0.4 * vTop, 0.6);
  for (int i = 0; i < ${LAMPS_MAX}; i++) {
    if (i >= uLampCount) break;
    vec3 L = uLampPos[i].xyz - vPos;
    float d2 = dot(L, L);
    col += alb * uLampCol[i].rgb * max(dot(n, L * inversesqrt(d2)) * 0.7 + 0.3, 0.0) / (d2 + uLampPos[i].w * uLampPos[i].w);
  }
  col = applyAtmos(col, cameraPosition, vPos);
  gl_FragColor = vec4(col, 1.0);
}
`;
function createConifers(heightAt, rockAt, shared, deckY) {
  // keep trees >= 55 m from the reference cameras (a 10 m spruce right under a hero camera fills a corner)
  const cams = Object.values(VIEWS).map(v => refToWorld(v.pos));
  // slender spruce (height : width ~ 3 : 1), drooping tiers
  const prof = [[0.0, 0], [0.25, 0], [0.25, 0.8], [1.9, 1.0], [0.8, 3.3], [1.6, 3.4], [0.6, 5.7], [1.15, 5.8], [0.4, 8.0], [0.65, 8.1], [0, 10.5]];
  const geo = new THREE.LatheGeometry(prof.map(([x, y]) => new THREE.Vector2(x, y)), 7);
  const mat = new THREE.ShaderMaterial({ vertexShader: treeVert, fragmentShader: treeFrag, uniforms: { ...shared.uniforms, uEarthR: { value: EARTH_R } } });
  let s = 9127;
  const rnd = () => { s = (s * 16807) % 2147483647; return (s - 1) / 2147483646; };
  const N = 2600, mesh = new THREE.InstancedMesh(geo, mat, N);
  const m = new THREE.Matrix4(), q = new THREE.Quaternion(), up = new THREE.Vector3(0, 1, 0);
  let n = 0;
  for (let k = 0; k < 200000 && n < N; k++) {
    // (denser near the ring: the gorge walls framing the hero views)
    const a = rnd() * Math.PI * 2, rr = 62 + Math.pow(rnd(), 1.1) * 660;
    const x = Math.cos(a) * rr, z = Math.sin(a) * rr, y = heightAt(x, z);
    // (round 5: only well below the cloud sea - the refs show no trees near ring altitude; the big spruce in the
    // hero foregrounds are gone)
    if (y > deckY - 600) continue;
    // (pass 2: none on the slot's floor around the ring (sculpt frame |z| < 300 m, x -280..300): from above (view 8)
    // the ring frames ~500 m of that floor, and they were hundreds of dots through every cloud gap in the void)
    const hA = 210 * Math.PI / 180, hx = Math.sin(hA), hz = -Math.cos(hA), scx = -(x * hx + z * hz), scz = x * hz - z * hx;
    if (Math.abs(scz) < 300 && scx > -280 && scx < 300) continue;
    if (cams.some(c => Math.hypot(c.x - x, c.y - y, c.z - z) < 28)) continue;
    const sx = (heightAt(x + 1.5, z) - heightAt(x - 1.5, z)) / 3, sz = (heightAt(x, z + 1.5) - heightAt(x, z - 1.5)) / 3;
    const sl = Math.hypot(sx, sz);
    if (sl > (rr < 260 ? 1.45 : 1.2) || sl < 0.05) continue;
    // on snow between the outcrops, not on the blocks
    if (rockAt(x, z) > 0.2) continue;
    // clumps: trees gather in loose groves, favouring benches (flatter spots)
    const cl = Math.sin(x * 0.043 + Math.sin(z * 0.031) * 2.0) * Math.sin(z * 0.047 + Math.sin(x * 0.029) * 2.0);
    if (cl + 0.35 * (0.7 - sl) < 0.05 + 0.5 * rnd()) continue;
    const sc = 0.75 + 0.9 * rnd() * rnd();
    q.setFromAxisAngle(up, rnd() * 6.28);
    m.compose(new THREE.Vector3(x, y - 0.6, z), q, new THREE.Vector3(sc * (0.8 + 0.3 * rnd()), sc * (0.95 + 0.4 * rnd()), sc));
    mesh.setMatrixAt(n++, m);
  }
  mesh.count = n;
  mesh.frustumCulled = false;
  mesh.name = 'conifers';
  return mesh;
}

async function fetchBin(url, Type) {
  const r = await fetch(url);
  if (!r.ok) throw new Error('fetch ' + url);
  return new Type(await r.arrayBuffer());
}

export async function createTerrain(shared) {
  const base = './data/terrain/';
  const meta = await (await fetch(base + 'meta.json')).json();
  if (NOFAR) delete meta.MID;
  if (NOFAR && meta.FAR) { delete meta.FAR; meta.LEVELS[1] = { ...meta.LEVELS[1], file: 'L1.blend' }; }
  // round 8 pass 2: L1's outer band (12.3-24.9 km) with peaked summits and serrated crests (tools/farsummit.mjs)
  else if (meta.SUMMIT && !NOSUM) meta.LEVELS[1] = { ...meta.LEVELS[1], file: meta.SUMMIT.file };
  const group = new THREE.Group();
  group.name = 'terrain';
  const levels = meta.LEVELS;
  const mats = [];

  // town glow map (computed from lights over L1 extent)
  const lights = await fetchBin(base + 'lights.f32', Float32Array);
  // round 8: with the polar far level the far lights (placed on L0's 312 m / L1's blended band) sit on the new
  // surface: per-light height corrections from tools/fardem.mjs
  if (meta.FAR) try {
    const dy = await fetchBin(base + 'lights_dy.f32', Float32Array);
    if (dy.length * 5 === lights.length) for (let i = 0; i < dy.length; i++) lights[i * 5 + 1] += dy[i];
  } catch (e) { console.warn('lights_dy', e); }
  const TG = 512, tgSize = levels[1].size;
  const tg = new Float32Array(TG * TG);
  for (let i = 0; i < lights.length; i += 5) {
    const u = Math.floor((lights[i] / tgSize + 0.5) * TG), v = Math.floor((lights[i + 2] / tgSize + 0.5) * TG);
    if (u >= 0 && v >= 0 && u < TG && v < TG) tg[v * TG + u] += lights[i + 3];
  }
  blurFloat(tg, TG, 3); blurFloat(tg, TG, 3);
  for (let i = 0; i < tg.length; i++) tg[i] = Math.min(1, tg[i] * 0.12);
  const tgTex = new THREE.DataTexture(tg, TG, TG, THREE.RedFormat, THREE.FloatType);
  tgTex.magFilter = tgTex.minFilter = THREE.LinearFilter;
  tgTex.needsUpdate = true;
  shared.townGlow = { tex: tgTex, size: tgSize };
  const rockU = await rockUniforms();   // glsl/rock.js (shared by every level)

  // L0..L3: square DEM levels centred on the ring; L4 (meta.FINE, 0.39 m): a rectangle snapped to L3's vertex
  // lines, whose outer band fades into L3's surface (heights, attributes and - below - normals)
  const fine = meta.FINE ? { ...meta.FINE, fine: true } : null;
  const all = (fine ? [...levels, fine] : levels).map((lv, i) => ({ ...lv, idx: i }));
  // round 8: the mid level LM (tools/farmid.mjs, 4-12 km at 15.6 m with sub-DEM relief) nests between L1 and L2
  // (idx 1.5: far shading like L1, no placement queries)
  if (meta.MID) all.splice(2, 0, { ...meta.MID, fine: true, mid: true, idx: 1.5 });
  const lvGrid = lv => lv.fine ? lv : { x0: -lv.size / 2, z0: -lv.size / 2, nx: lv.grid, nz: lv.grid, step: lv.size / (lv.grid - 1) };
  let L3N = null;   // L3's normals (L4's seam band blends into them)
  // key-light visibility (tools/farkey.mjs): L1's grid, sampled bilinearly for the other square levels (255 = lit)
  const L1key = meta.FAR ? await fetchBin(base + 'L1.key', Uint8Array).catch(() => null) : null;
  const keyFromL1 = pos => {
    const n = pos.length / 3, out = new Uint8Array(n).fill(255);
    if (!L1key) return out;
    const g = levels[1].grid, st = levels[1].size / (g - 1), h = levels[1].size / 2;
    for (let v = 0; v < n; v++) {
      const fx = (pos[v * 3] + h) / st, fz = (pos[v * 3 + 2] + h) / st;
      if (fx < 0 || fz < 0 || fx >= g - 1 || fz >= g - 1) continue;
      const i = Math.floor(fx), j = Math.floor(fz), u = fx - i, w = fz - j, k = j * g + i;
      out[v] = Math.round((L1key[k] * (1 - u) + L1key[k + 1] * u) * (1 - w) + (L1key[k + g] * (1 - u) + L1key[k + g + 1] * u) * w);
    }
    return out;
  };
  const makeMat = li => {
    const mat = new THREE.ShaderMaterial({
      defines: GEODBG ? { GEODBG: 1 } : {},
      vertexShader: terrainVert,
      fragmentShader: terrainFrag,
      uniforms: {
        ...shared.uniforms,
        uDetail: { value: li >= 2 ? 1 : 0 },
        uEarthR: { value: EARTH_R },
        uLakeY: { value: LAKE_Y },
        uTownGlow: { value: tgTex },
        uTownGlowSize: { value: tgSize },
        ...rockU,
      },
    });
    mats.push(mat);
    return mat;
  };
  // round 8: the polar far level (tools/fardem.mjs) takes L0's place: L1's edge out to ~240 km at the DEM's own
  // resolution (z12 ~26 m within ~60 km), instead of L0's 312 m cells that rounded the Bernese Alps into domes
  // (pass 2: with its summit / crest pass, LF.sum.f32 / LF.sum.nrm, unless '&nosum')
  if (meta.FAR) group.add(await createFarLevel(base, meta.FAR, makeMat(0), meta.SUMMIT && meta.SUMMIT.lf && !NOSUM ? '.sum' : ''));
  for (let li = 0; li < all.length; li++) {
    const lv = all[li];
    const LI = lv.idx;   // the level's own index (L0..L4; 1.5 = LM)
    if (LI === 0 && meta.FAR) continue;
    const [H, A] = await Promise.all([fetchBin(base + (lv.file || lv.name) + '.f32', Float32Array), fetchBin(base + lv.name + '.attr', Uint8Array)]);
    const { x0: gx0, z0: gz0, nx: g, nz: gzN, step } = lvGrid(lv), N = g * gzN;
    // baked outcrop mask (sculpted near field only); other levels use the shader's procedural field
    const RK = LI >= 3 ? await fetchBin(base + lv.name + '.rock', Uint8Array).catch(() => new Uint8Array(N)) : new Uint8Array(N);
    const pos = new Float32Array(N * 3), nrm = new Float32Array(N * 3);
    for (let j = 0; j < gzN; j++) for (let i = 0; i < g; i++) {
      const k = j * g + i;
      pos[k * 3] = gx0 + i * step; pos[k * 3 + 1] = H[k]; pos[k * 3 + 2] = gz0 + j * step;
      const im = Math.max(0, i - 1), ip = Math.min(g - 1, i + 1), jm = Math.max(0, j - 1), jp = Math.min(gzN - 1, j + 1);
      const sx = (H[j * g + ip] - H[j * g + im]) / ((ip - im) * step), sz = (H[jp * g + i] - H[jm * g + i]) / ((jp - jm) * step);
      const l = Math.hypot(sx, 1, sz);
      nrm[k * 3] = -sx / l; nrm[k * 3 + 1] = 1 / l; nrm[k * 3 + 2] = -sz / l;
    }
    // smoothed normal (gradient over a +-rs cell window, ~5 m on L3 / L4): where snow can lie is decided
    // by the slope at that scale, not by every joint / ledge riser of the grid
    // (L4: of a box-blurred copy, so its 0.4 m blocks do not alias into the sparse +-12 cell stencil)
    const rs = LI === 4 ? 12 : LI === 3 ? 3 : LI === 2 ? 1 : 0;
    let nrmS = nrm;
    if (rs > 0) {
      nrmS = new Float32Array(N * 3);
      let Hs = H;
      if (LI === 4) { Hs = H.slice(); boxBlur(Hs, g, gzN, 4); boxBlur(Hs, g, gzN, 4); }
      const c = (i, j) => Hs[Math.min(gzN - 1, Math.max(0, j)) * g + Math.min(g - 1, Math.max(0, i))];
      for (let j = 0; j < gzN; j++) for (let i = 0; i < g; i++) {
        let sx = 0, sz = 0;
        for (const b of [-rs, 0, rs]) { sx += c(i + rs, j + b) - c(i - rs, j + b); sz += c(i + b, j + rs) - c(i + b, j - rs); }
        sx /= 6 * rs * step; sz /= 6 * rs * step;
        const k = j * g + i, l = Math.hypot(sx, 1, sz);
        nrmS[k * 3] = -sx / l; nrmS[k * 3 + 1] = 1 / l; nrmS[k * 3 + 2] = -sz / l;
      }
    }
    if (LI === 3) L3N = { nrm, nrmS, ...lvGrid(lv) };
    // L4's seam band: normals fade into L3's (bilinear), so the shading matches across the seam
    if (LI === 4 && L3N) {
      const n3 = (arr, x, z, out) => {
        const fx = (x - L3N.x0) / L3N.step, fz = (z - L3N.z0) / L3N.step;
        const i = Math.min(L3N.nx - 2, Math.floor(fx)), j = Math.min(L3N.nz - 2, Math.floor(fz)), u = fx - i, v = fz - j, k = j * L3N.nx + i;
        for (let c = 0; c < 3; c++) out[c] = (arr[k * 3 + c] * (1 - u) + arr[(k + 1) * 3 + c] * u) * (1 - v) + (arr[(k + L3N.nx) * 3 + c] * (1 - u) + arr[(k + L3N.nx + 1) * 3 + c] * u) * v;
      };
      const t = [0, 0, 0];
      for (let j = 0; j < gzN; j++) for (let i = 0; i < g; i++) {
        const de = Math.min(i, g - 1 - i, j, gzN - 1 - j) * step;
        if (de >= lv.band) continue;
        const w = de / lv.band, w2 = w * w * (3 - 2 * w), k = j * g + i, x = gx0 + i * step, z = gz0 + j * step;
        for (const arr of nrmS === nrm ? [nrm] : [nrm, nrmS]) {
          n3(arr === nrm ? L3N.nrm : L3N.nrmS, x, z, t);
          let a = t[0] + (arr[k * 3] - t[0]) * w2, b = t[1] + (arr[k * 3 + 1] - t[1]) * w2, c = t[2] + (arr[k * 3 + 2] - t[2]) * w2;
          const l = Math.hypot(a, b, c) || 1;
          arr[k * 3] = a / l; arr[k * 3 + 1] = b / l; arr[k * 3 + 2] = c / l;
        }
      }
    }
    // hole where the next finer level takes over (cells entirely inside it)
    const inner = all[li + 1] ? lvGrid(all[li + 1]) : null;
    const ix0 = inner ? inner.x0 - 1e-3 : 0, ix1 = inner ? inner.x0 + (inner.nx - 1) * inner.step + 1e-3 : 0;
    const iz0 = inner ? inner.z0 - 1e-3 : 0, iz1 = inner ? inner.z0 + (inner.nz - 1) * inner.step + 1e-3 : 0;
    const idx = new Uint32Array((g - 1) * (gzN - 1) * 6);
    let ni = 0;
    for (let j = 0; j < gzN - 1; j++) for (let i = 0; i < g - 1; i++) {
      const x0 = gx0 + i * step, x1 = x0 + step, z0 = gz0 + j * step, z1 = z0 + step;
      if (inner && x0 >= ix0 && x1 <= ix1 && z0 >= iz0 && z1 <= iz1) continue;
      const a = j * g + i, b = a + 1, c = a + g, d = c + 1;
      idx[ni++] = a; idx[ni++] = c; idx[ni++] = b; idx[ni++] = b; idx[ni++] = c; idx[ni++] = d;
    }
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    const nrmA = new THREE.BufferAttribute(nrm, 3);
    geo.setAttribute('normal', nrmA);
    geo.setAttribute('nrmS', nrmS === nrm ? nrmA : new THREE.BufferAttribute(nrmS, 3));   // (one GPU buffer when equal)
    geo.setAttribute('attr', new THREE.BufferAttribute(A, 4, true));
    geo.setAttribute('rockM', new THREE.BufferAttribute(RK, 1, true));
    geo.setAttribute('keyV', new THREE.BufferAttribute(LI === 1 && L1key ? L1key : keyFromL1(pos), 1, true));
    geo.setIndex(new THREE.BufferAttribute(idx.subarray(0, ni), 1));
    geo.boundingSphere = new THREE.Sphere(new THREE.Vector3(), Math.max(g, gzN) * step);
    const mesh = new THREE.Mesh(geo, makeMat(LI));
    mesh.frustumCulled = false;
    mesh.name = lv.name;
    mesh.userData.level = LI;
    group.add(mesh);
    // keep L2..L4 heights for placement queries
    if (LI >= 2) group.userData['H' + LI] = { H, x0: gx0, z0: gz0, nx: g, nz: gzN, step, RK };
  }
  group.userData.lights = lights;
  group.userData.heightAt = (x, z) => {
    for (const k of ['H4', 'H3', 'H2']) {
      const L = group.userData[k];
      if (!L) continue;
      const fx = (x - L.x0) / L.step, fz = (z - L.z0) / L.step;
      if (fx < 0 || fz < 0 || fx >= L.nx - 1 || fz >= L.nz - 1) continue;
      const i = Math.floor(fx), j = Math.floor(fz), u = fx - i, v = fz - j, a = j * L.nx + i;
      return (L.H[a] * (1 - u) + L.H[a + 1] * u) * (1 - v) + (L.H[a + L.nx] * (1 - u) + L.H[a + L.nx + 1] * u) * v;
    }
    return 0;
  };
  // baked outcrop relief (0..1 = 0..6 m) at world (x, z); 0 outside the sculpted near field
  const rockAt = (x, z) => {
    const L = group.userData.H3;
    const i = Math.round((x - L.x0) / L.step), j = Math.round((z - L.z0) / L.step);
    if (i < 0 || j < 0 || i >= L.nx || j >= L.nz) return 0;
    return Math.max(0, L.RK[j * L.nx + i] - 1) / 254;
  };
  group.add(createConifers(group.userData.heightAt, rockAt, shared, DECK_Y));
  return group;
}

// Polar far level LF (tools/fardem.mjs): rings of meta.FAR.rings[j] vertices each (6400 / 3200 / 1600 per band; ring 0
// = L1's edge vertices), vertex order ring by ring; quads between rings of equal count, transition strips where the
// count halves (every other inner vertex, no T-junctions). Files: LF.xz (x, z), LF.f32 (heights), LF.nrm (int8 normal),
// LF.attr (sky / glow visibility, water, concavity as the other levels).
async function createFarLevel(base, FAR, mat, sfx = '') {
  const [XZ, H, NR, A] = await Promise.all([fetchBin(base + 'LF.xz', Float32Array), fetchBin(base + 'LF' + sfx + '.f32', Float32Array),
    fetchBin(base + 'LF' + sfx + '.nrm', Int8Array), fetchBin(base + 'LF.attr', Uint8Array)]);
  let KV = await fetchBin(base + 'LF.key', Uint8Array).catch(() => null);
  if (!KV || KV.length !== H.length) KV = new Uint8Array(H.length).fill(255);   // (missing / stale: all lit)
  const N = H.length, R = FAR.rings;
  const pos = new Float32Array(N * 3);
  for (let v = 0; v < N; v++) { pos[v * 3] = XZ[v * 2]; pos[v * 3 + 1] = H[v]; pos[v * 3 + 2] = XZ[v * 2 + 1]; }
  let ni = 0;
  for (let j = 0; j + 1 < R.length; j++) ni += R[j + 1] === R[j] ? R[j] * 6 : R[j + 1] * 9;
  const idx = new Uint32Array(ni);
  ni = 0;
  let v0 = 0;
  for (let j = 0; j + 1 < R.length; j++) {
    const n = R[j], m = R[j + 1], v1 = v0 + n;
    if (m === n) {
      for (let k = 0; k < n; k++) {
        const a = v0 + k, b = v0 + (k + 1) % n, c = v1 + k, d = v1 + (k + 1) % n;
        idx[ni++] = a; idx[ni++] = b; idx[ni++] = c; idx[ni++] = b; idx[ni++] = d; idx[ni++] = c;
      }
    } else {   // m = n / 2
      for (let k = 0; k < m; k++) {
        const i0 = v0 + 2 * k, i1 = v0 + 2 * k + 1, i2 = v0 + (2 * k + 2) % n, o0 = v1 + k, o1 = v1 + (k + 1) % m;
        idx[ni++] = i0; idx[ni++] = i1; idx[ni++] = o0;
        idx[ni++] = i1; idx[ni++] = i2; idx[ni++] = o1;
        idx[ni++] = i1; idx[ni++] = o1; idx[ni++] = o0;
      }
    }
    v0 = v1;
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  const nrm = new THREE.BufferAttribute(NR, 3, true);   // (one GPU buffer for both: no smoothed normal out here)
  geo.setAttribute('normal', nrm);
  geo.setAttribute('nrmS', nrm);
  geo.setAttribute('attr', new THREE.BufferAttribute(A, 4, true));
  geo.setAttribute('rockM', new THREE.BufferAttribute(new Uint8Array(N), 1, true));
  geo.setAttribute('keyV', new THREE.BufferAttribute(KV, 1, true));
  geo.setIndex(new THREE.BufferAttribute(idx, 1));
  geo.boundingSphere = new THREE.Sphere(new THREE.Vector3(), 260000);
  const mesh = new THREE.Mesh(geo, mat);
  mesh.frustumCulled = false;
  mesh.name = FAR.name;
  mesh.userData.level = 0;
  return mesh;
}

// separable box blur (radius r cells) of an nx x nz grid, in place
function boxBlur(a, nx, nz, r) {
  const t = new Float32Array(Math.max(nx, nz));
  for (let j = 0; j < nz; j++) {
    for (let i = 0; i < nx; i++) t[i] = a[j * nx + i];
    let s = 0, c = 0;
    for (let i = -r; i < nx + r; i++) {
      if (i + r < nx) { s += t[i + r]; c++; }
      if (i - r - 1 >= 0) { s -= t[i - r - 1]; c--; }
      if (i >= 0 && i < nx) a[j * nx + i] = s / c;
    }
  }
  for (let i = 0; i < nx; i++) {
    for (let j = 0; j < nz; j++) t[j] = a[j * nx + i];
    let s = 0, c = 0;
    for (let j = -r; j < nz + r; j++) {
      if (j + r < nz) { s += t[j + r]; c++; }
      if (j - r - 1 >= 0) { s -= t[j - r - 1]; c--; }
      if (j >= 0 && j < nz) a[j * nx + i] = s / c;
    }
  }
}

function blurFloat(a, n, r) {
  const t = new Float32Array(a.length);
  for (let j = 0; j < n; j++) for (let i = 0; i < n; i++) {
    let s = 0, c = 0;
    for (let k = -r; k <= r; k++) { const x = i + k; if (x >= 0 && x < n) { s += a[j * n + x]; c++; } }
    t[j * n + i] = s / c;
  }
  for (let j = 0; j < n; j++) for (let i = 0; i < n; i++) {
    let s = 0, c = 0;
    for (let k = -r; k <= r; k++) { const y = j + k; if (y >= 0 && y < n) { s += t[y * n + i]; c++; } }
    a[j * n + i] = s / c;
  }
}
