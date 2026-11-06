// Village / road lights (sodium + LED points) and their streaked reflections in the lake.
// Reflection: the brighter lamps are mirrored about the lake plane into a screen-aligned RT, each drawn as its
// own thin glitter streak (per-lamp length, ripple wiggle and dashes); glsl/water.js samples it on lake pixels.
// Also hands the lake shader a coarse L1 heightfield (uHF) so reflected rays can hit the surrounding slopes.
import * as THREE from 'three';
import { LAKE_Y, EARTH_R } from './config.js';
import { FARDIP } from './glsl/common.js';

// lights.f32 intensities are pre-scaled by tools/lights.mjs I_SCALE (keeps the shared town-glow map in range)
const I_SCALE = 0.3;

// Three passes share this shader: uPool = 0 lamp cores + small halos (scene), uMirror = 1 mirrored glitter
// streaks (reflection RT), uPool = 1 light-pollution pools lighting the ground under the towns (every 3rd lamp).
const vert = /* glsl */ `
#include <common>
#include <logdepthbuf_pars_vertex>
${FARDIP}
attribute vec2 info;          // intensity, warm + 2 * class + 8 * dir (warm 1 = sodium orange .. 0 = 3000 K LED;
                              // class 0 house / window / farm, 1 town street + hot spot, 2 main road / quay;
                              // dir 0 none, 1..32 street / road direction in pi / 32 steps)
attribute float dens;         // local lamp density (lamps / m2 over ~120 m), computed at load
uniform float uEarthR;
uniform float uMirror;        // 1 = render mirrored about the lake plane
uniform float uPool;          // 1 = wide ground-glow pools instead of lamp cores
uniform float uLakeY;
uniform float uGain;
uniform float uKeep;          // max share of a town's projected area covered by lamp cores (thinning)
uniform float uPoolGain;
uniform float uStreakLen;     // mirror pass: base glitter-streak length (px)
uniform float uTime;
uniform float uFogDensity;
uniform vec2 uResolution;
varying vec3 vCol;            // core colour * peak * transmission
varying vec3 vHaloCol;
varying float vCore;          // core radius / sprite radius
varying float vSq;            // vertical squash of the sprite footprint (pools: ground foreshortening)
varying vec3 vStreak;         // mirror pass: sprite size (px), streak length (px), per-lamp seed;
                              // scene pass: x = halo radius / sprite radius
varying vec4 vSeg;            // scene pass: lit-road segment screen direction, half length (px), sprite size (px)
varying vec3 vLine;           // lit-road segment colour
float hash11(float n){ return fract(sin(n * 0.1031 + 7.13) * 43758.5453); }
void main(){
  vec3 p = position;
  float id = float(gl_VertexID);
  bool pool = uPool > 0.5;
  vSq = 1.0;
  vStreak = vec3(1.0);
  vSeg = vec4(1.0, 0.0, 0.0, 1.0);
  vLine = vec3(0.0);
  float dcode = floor(info.y * 0.125 + 0.001);
  float rem = info.y - 8.0 * dcode;
  float cls = floor(rem * 0.5 + 0.01);
  float warm = rem - 2.0 * cls;
  if (pool && mod(id, 3.0) > 0.5) { gl_Position = vec4(2.0, 2.0, 2.0, 1.0); gl_PointSize = 1.0; vCol = vHaloCol = vec3(0.0); vCore = 1.0; return; }
  float above = p.y - uLakeY;
  if (uMirror > 0.5) p.y = 2.0 * uLakeY - p.y;
  float r2 = dot(p.xz, p.xz);
  vec3 pc = p; pc.y -= r2 / (2.0 * uEarthR) + farOff(p);
  float d = max(-(viewMatrix * vec4(pc, 1.0)).z, 1.0);
  vec3 toCam = cameraPosition - pc;
  float dist = length(toCam);
  // sine of the view elevation over the (roughly level) town ground
  float vy = clamp(abs(toCam.y) / dist, 0.02, 1.0);
  // pools: pulled toward the camera along the view ray (same screen spot) so the ground right in front of
  // the lamp does not depth-clip the near half of the pool
  if (pool) pc += toCam / dist * min(120.0, dist * 0.3);
  vec4 mv = viewMatrix * vec4(pc, 1.0);
  gl_Position = projectionMatrix * mv;
  float hs = hash11(id), hs2 = hash11(id + 517.0), hs3 = hash11(id + 911.0);
  float I = info.x * (0.96 + 0.04 * sin(uTime * 1.3 + id * 1.7));
  // aerial perspective for the lamps: kept light (refs: towns 4-15 km away stay vivid), slightly reddening
  vec3 T = exp(-dist * uFogDensity * vec3(0.12, 0.16, 0.23));
  float pxm = projectionMatrix[1][1] * uResolution.y * 0.5 / d;
  // salmon-peach / amber lamp colours (refs, warm pixels by brightness: #d4a389 at L150-200, #f8d4b0 above):
  // deep sodium .. warm LED, per-lamp jitter; warm < 0.2: the paler LED street lighting some towns use
  // (round 5: refs mix pale yellow-white lamps into the orange towns - colour temperature varies town to town)
  // (pass 2: paler and pinker, no deep-sodium end - refs 4, 6, 7, 11 brightest dots #f1c7b7..#f4cab4 (sRGB
  // g/r 0.83, b/r 0.76), ref 8 #fff2d0 up close; the palette is linear, so ~(1, 0.66, 0.52) at its centre)
  // (the grade's blue white balance pinks the clipped cores: the brightest dots measured #fcd2c8 at (1, 0.68, 0.52),
  // so the cores sit a little more yellow than the target)
  vec3 col = warm < 0.2 ? mix(vec3(1.0, 0.82, 0.62), vec3(1.0, 0.69, 0.48), warm * 5.0)
                        : mix(vec3(1.0, 0.69, 0.48), vec3(1.0, 0.58, 0.40), (warm - 0.2) * 1.25);
  col *= vec3(1.0, 0.95 + 0.1 * hs2, 0.9 + 0.16 * hs);
  if (pool) {
    // ~120 m light-pollution pool (lit streets / facades / snow under the town), drawn as the ground
    // ellipse it lights (squashed by the view elevation): the warm carpet keeps the same surface
    // brightness from above and at grazing angles, and hugs the valley floor instead of a tall disc
    // bleeding over the lake / up the slopes. Weaker for the near towns (refs 2, 4: dark ground with warm
    // pockets between the lamps, not a lilac haze); full strength for the far towns, where it carries the
    // light of the lamps thinned out below
    // (pass 2: only over dense town cores - lamps / m2 over 120 m: town cores ~2-4e-3, residential ~1e-3, roads
    // and hamlets < 5e-4 - and 100 m instead of 120 m; over the thinned far towns the pools showed as flat painted
    // ellipses with 2-4 lamps inside, view 4. The far boost is lower for the same reason)
    float size = min(100.0 * pxm, 80.0);
    gl_PointSize = max(size, 1.0);
    vSq = clamp(max(vy * 1.15, 2.5 / max(size, 1.0)), 0.06, 1.0);   // >= 2.5 px tall: no sub-pixel shimmer
    vCol = vec3(0.0);
    vHaloCol = vec3(1.0, 0.62, 0.46) * 0.018 * uPoolGain * uGain * I * T * smoothstep(1.0, 4.0, size)
             * mix(0.25, 0.6, smoothstep(5000.0, 14000.0, dist)) * smoothstep(2e-4, 1.5e-3, dens)
             * mix(0.3, 1.0, smoothstep(1500.0, 4000.0, dist));   // ~1 km away (the gorge group, view 8): a painted disc
    vCore = 1.0;
    #include <logdepthbuf_vertex>
    return;
  }
  // peak HDR value of the point core (1/d: the sprite stays >= 1.3 px); house / window lamps stay small
  // orange-peach dots (ceiling below the bloom threshold), street lamps brighter, only main roads, quays and
  // hot spots clip toward pale peach and bloom (refs 2, 4: luma >= 200 only on the main roads)
  float ceilP = cls < 0.5 ? 1.7 : (cls < 1.5 ? 2.5 : 3.2);
  float praw = uGain * 3.4 * I * (3000.0 / d);
  float peak = ceilP * praw / (praw + 2.2);
  float core = (cls < 0.5 ? 1.2 : 1.5) + (cls < 0.5 ? 1.2 : 2.0) * clamp(peak / 2.6, 0.0, 1.0);
  // screen-space crowding: once a town's lamps overlap on screen (distant / grazing towns: thousands of
  // lamps in a few hundred pixels summed into a cream blow-out), keep only a random subset so the town
  // stays a field of discrete orange dots (refs 2, 4, 7, 8) and the glow pools carry the rest; bright
  // street / hot-spot lamps survive longest. Each lamp fades over a band, so moving cameras do not pop.
  // Energy-conserving: the survivors carry the light of the culled lamps (x 1 / kept share, capped), so a
  // thinned far town keeps its total brightness and still reads through the cloud gaps (cores stay small)
  float apx = pxm * pxm * vy / max(dens, 1e-7);              // projected ground area per lamp (px2)
  float keep = min(1.0, uKeep * apx / (core * core));
  float rank = hs3 * mix(1.0, 0.4, smoothstep(0.5, 1.8, info.x * uGain)) * (cls > 1.5 ? 0.6 : 1.0);
  float vis = 1.0 - smoothstep(keep, keep * 1.3 + 0.002, rank);
  if (vis <= 0.0) { gl_Position = vec4(2.0, 2.0, 2.0, 1.0); gl_PointSize = 1.0; vCol = vHaloCol = vec3(0.0); vCore = 1.0; return; }
  // (applied after the brightness ceiling: a thinned far town's survivors may exceed it, so its few cores
  // keep the HDR punch that carries them through the cloud gaps)
  // (round 5: cap 2.8 -> 2.5 with the stronger thinning: the dense shore-town cores clipped to cream)
  // (pass 2: uKeep 0.55 -> 0.4, cap 2.5 -> 3.0: about half the dots, each brighter - ref 7's towns have ~31 dots
  // per 10k px at median luma ~170, ours had 81 at ~146, a uniform speckle)
  peak *= min(1.0 / max(keep * 1.15, 0.01), 3.0) * vis;
  float halo = core * (2.2 + 1.4 * smoothstep(0.8, 2.6, peak));
  float size = halo;
  // lit road / street between the lamps: each directed lamp draws a short screen-space segment along its
  // street (main roads 30 m, town streets 16 m: about twice the lamp spacing, jittered spacing makes the
  // overlaps irregular), so roads read as continuous winding lines brighter than the house lights (refs 2,
  // 4, 8) instead of a runway of separate beads; vanishes once the segment shrinks below ~2 px.
  // (round 5: about a third of the lamps draw none and the gains are halved, so roads read as faint dotted
  // strings with a few continuous lit stretches; at 0.32 / 0.16 the shore road and quays were one neon line)
  if (dcode > 0.5 && uMirror < 0.5 && hash11(id + 2203.0) > 0.33) {
    float a = (dcode - 1.0) * (PI / 32.0);
    vec3 D = vec3(cos(a), 0.0, sin(a)) * (cls > 1.5 ? 15.0 : 8.0);
    vec4 c0 = projectionMatrix * viewMatrix * vec4(pc - D, 1.0), c1 = projectionMatrix * viewMatrix * vec4(pc + D, 1.0);
    if (c0.w > 1.0 && c1.w > 1.0) {
      vec2 s = (c1.xy / c1.w - c0.xy / c0.w) * 0.5 * uResolution;
      float L = length(s);
      float hl = min(0.5 * L, 18.0);
      // (pass 2) fades out again once the segment is long on screen: up close the lamps are separate pools of
      // light (ref 8, the film's top-down shot), a bright line through each lone lamp read as a '+' spike
      float ls = smoothstep(1.0, 3.0, L) * smoothstep(22.0, 9.0, L);
      if (ls > 0.0) {
        size = max(size, 2.0 * hl + 3.0);
        vSeg = vec4(s / max(L, 1e-3), hl, size);
        vLine = col * T * min(peak, 1.5) * ls * (cls > 1.5 ? 0.17 : 0.08);
      }
    }
  }
  vSeg.w = size;
  vStreak.x = halo / size;
  vCore = core / size;
  vCol = col * peak * T;
  vHaloCol = vec3(0.92, 0.62, 0.50) * 0.08 * peak * smoothstep(0.7, 2.2, peak) * T;
  if (uMirror > 0.5) {
    // glitter streak of the mirrored lamp. Only the brighter lamps (streets / quays / hot spots) and only
    // lights close to the water level reflect (refs 2, 7: thin warm columns under the bright shore lamps,
    // the lake between them stays navy). Fresnel boosted: wind-tilted facets widen the glitter path.
    vec3 v = normalize(p - cameraPosition);
    float F = 0.02 + 0.98 * pow(1.0 - abs(v.y), 5.0);
    // (round 5: brighter lamps only, and only about half of them - lamps behind trees / walls / boats, facing
    // away: a broken row of short glints under a lit shore, not a curtain of identical streaks)
    float hs4 = hash11(id + 1301.0), hs5 = hash11(id + 1777.0);
    float rf = min(F * 3.5, 1.0) * smoothstep(250.0, 30.0, above) * smoothstep(0.4, 1.3, peak) * step(0.4, hs5);
    if (rf < 0.004) { gl_Position = vec4(2.0, 2.0, 2.0, 1.0); gl_PointSize = 1.0; vCol = vHaloCol = vec3(0.0); vCore = 1.0; return; }
    // per-lamp length (wave state differs along the shore), long at grazing views, short glints from above
    // (p2: spread 0.5 .. 1.3x (was 0.3 .. 1.1x, mostly short) and up to 64 px: the film's wide shots want visible
    // columns under the shore lights, ~20-60 px at 1080p)
    float len = uStreakLen * (0.5 + 0.8 * hs4 * hs4) * mix(1.0, 0.4, smoothstep(0.15, 0.7, vy)) * (0.8 + 0.2 * smoothstep(1.0, 2.4, peak));
    len = clamp(len, 2.0, 64.0);
    float S = len + 3.0;
    // the sprite hangs below the mirror image (2 px stub above it), streak runs down the screen
    gl_Position.y -= (0.5 * S - 2.0) * 2.0 / uResolution.y * gl_Position.w;
    gl_PointSize = S;
    // desaturated toward the refs' streak colour (#c89a86 core, #ac7c6e tails)
    // (sqrt(T): the lake pixel gets the slant-path haze again in the terrain shader)
    // (round 5: less desaturated and dimmer - at full size the glints read as white strokes; refs 7, 11: soft
    // amber columns a little dimmer than their lamps)
    vCol = mix(col, vec3(1.0, 0.62, 0.48), 0.4) * peak * sqrt(T) * rf * 0.75;
    vStreak = vec3(S, len, hs4 * 91.7 + hs * 13.1);
    vCore = 1.0;
    vHaloCol = vec3(0.0);
    #include <logdepthbuf_vertex>
    return;
  }
  gl_PointSize = size;
  #include <logdepthbuf_vertex>
}`;
const frag = /* glsl */ `
#include <common>
#include <logdepthbuf_pars_fragment>
uniform float uMirror;
varying vec3 vCol;
varying vec3 vHaloCol;
varying float vCore;
varying float vSq;
varying vec3 vStreak;
varying vec4 vSeg;
varying vec3 vLine;
void main(){
  #include <logdepthbuf_fragment>
  if (uMirror > 0.5) {
    // glitter streak: ~1.5 px wide column, bright head at the mirror image, tail fading down the screen,
    // wiggled sideways and broken into irregular dashes by the ripples (different for every lamp)
    float S = vStreak.x, len = vStreak.y, sd = vStreak.z;
    float y = gl_PointCoord.y * S - 2.0;
    float x = (gl_PointCoord.x - 0.5) * S + 0.5 * sin(y * 0.55 + sd * 3.0) * smoothstep(1.0, 6.0, y);
    float w = 0.6 + 0.3 * fract(sd * 7.31);
    float ax = exp(-x * x / (w * w));
    float ay = y < 0.0 ? exp(y * 1.5) : 0.4 * exp(-y / 1.2) + 0.6 * exp(-y / (0.6 * len)) * smoothstep(len, 0.4 * len, y);
    float g = 0.5 * sin(y * 0.83 + sd * 5.1) + 0.5 * sin(y * 0.29 + sd * 2.3);
    ay *= mix(1.0, 0.15 + 0.85 * smoothstep(-0.3, 0.4, g), smoothstep(1.5, 4.0, y));
    vec3 sc = vCol * ax * ay;
    if (max(sc.r, max(sc.g, sc.b)) < 0.0004) discard;
    gl_FragColor = vec4(sc, 1.0);
    return;
  }
  vec2 c = gl_PointCoord - 0.5;
  c.y /= vSq;
  float r = length(c) * 2.0, rc = r / vCore, rh = r / vStreak.x;
  vec3 col = vCol * exp(-rc * rc * 3.2) + vHaloCol * exp(-rh * rh * 4.0);
  if (vSeg.z > 0.0) {
    // lit-road segment (~1.5 px wide line through the lamp, tapered ends)
    vec2 pp = (gl_PointCoord - 0.5) * vSeg.w;
    pp.y = -pp.y;
    float along = dot(pp, vSeg.xy);
    float dd = length(pp - vSeg.xy * clamp(along, -vSeg.z, vSeg.z));
    col += vLine * exp(-dd * dd / 0.5) * smoothstep(vSeg.z + 0.5, vSeg.z - 2.5, abs(along));
  }
  if (max(col.r, max(col.g, col.b)) < 0.0004) discard;
  gl_FragColor = vec4(col, 1.0);
}`;

// Glitter streaks (mirror pass) run DOWN the screen from each mirror image (toward the camera), with only a
// short stub upward: from the high cameras the specular point of a shore lamp sits right under the lamp, and
// wave facets cannot reflect it from water lying beyond it (a symmetric smear threw combs of streaks from the
// near-shore towns out over the lake). Each lamp draws its own streak sprite (a full-screen vertical blur of
// all mirror images gave a uniform barcode curtain of equal-length soft columns over the whole near lake).

export function createVillageLights(shared, terrain, renderer, scene) {
  const L = terrain.userData.lights;
  const n = L.length / 5;
  const pos = new Float32Array(n * 3), info = new Float32Array(n * 2);
  for (let i = 0; i < n; i++) {
    pos[i * 3] = L[i * 5]; pos[i * 3 + 1] = L[i * 5 + 1]; pos[i * 3 + 2] = L[i * 5 + 2];
    info[i * 2] = L[i * 5 + 3]; info[i * 2 + 1] = L[i * 5 + 4];
  }
  // local lamp density (lamps / m2, 3x3 cells of 40 m) for the vertex shader's screen-space thinning
  const dens = new Float32Array(n);
  {
    const C = 40, cnt = new Map(), key = (i, j) => (i + 32768) * 65536 + (j + 32768);
    const ci = new Int32Array(n * 2);
    for (let i = 0; i < n; i++) {
      const a = Math.floor(pos[i * 3] / C), b = Math.floor(pos[i * 3 + 2] / C), k = key(a, b);
      ci[i * 2] = a; ci[i * 2 + 1] = b;
      cnt.set(k, (cnt.get(k) || 0) + 1);
    }
    for (let i = 0; i < n; i++) {
      let s = 0;
      for (let dj = -1; dj <= 1; dj++) for (let di = -1; di <= 1; di++) s += cnt.get(key(ci[i * 2] + di, ci[i * 2 + 1] + dj)) || 0;
      dens[i] = s / (9 * C * C);
    }
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  geo.setAttribute('info', new THREE.BufferAttribute(info, 2));
  geo.setAttribute('dens', new THREE.BufferAttribute(dens, 1));
  geo.boundingSphere = new THREE.Sphere(new THREE.Vector3(), 1e7);
  // (round 5: uKeep 0.9 -> 0.55: the visible core is ~0.47 core radius, so 0.9 still let a far town's dots cover
  // ~60% of its area - a fuzzy cream blob at 6-10 km (view 7); 0.55 leaves ~40%: separate dots with dark gaps,
  // still dense enough for the carpets of refs 2, 6)
  // (pass 2: 0.55 -> 0.4, see the cap in the vertex shader)
  const tune = { uKeep: { value: 0.4 }, uPoolGain: { value: 3.0 }, uStreakLen: { value: 24 } };   // shared by the three passes
  const mk = (mirror, pool = 0) => new THREE.ShaderMaterial({
    vertexShader: vert, fragmentShader: frag,
    uniforms: { ...shared.uniforms, ...tune, uEarthR: { value: EARTH_R }, uMirror: { value: mirror }, uPool: { value: pool }, uLakeY: { value: LAKE_Y }, uGain: { value: 0.85 / I_SCALE } },
    transparent: true, depthWrite: false, depthTest: !mirror, blending: THREE.AdditiveBlending,
  });
  // ground-glow pools first, lamp cores on top
  const poolPts = new THREE.Points(geo, mk(0, 1));
  poolPts.frustumCulled = false;
  poolPts.renderOrder = 4;
  scene.add(poolPts);
  const pts = new THREE.Points(geo, mk(0));
  pts.frustumCulled = false;
  pts.renderOrder = 5;
  scene.add(pts);

  // screen pixel angle for the lake's ripple-detail fade (glsl/water.js uLakePx), one object shared by every
  // terrain material, updated per frame
  const lakePx = { value: 0 };
  terrain.traverse(o => { const u = o.material && o.material.uniforms; if (u && u.uLakeY) u.uLakePx = lakePx; });
  // coarse L1 heightfield (125 m) for the lake's reflected-slope march (glsl/water.js uHF / uHFSize)
  const l1 = terrain.children.find(m => m.name === 'L1');
  if (l1) {
    const pa = l1.geometry.attributes.position.array, g = Math.round(Math.sqrt(pa.length / 3)), k = 4, hg = Math.floor((g - 1) / k) + 1;
    const hf = new Float32Array(hg * hg);
    for (let j = 0; j < hg; j++) for (let i = 0; i < hg; i++) hf[j * hg + i] = pa[((j * k) * g + i * k) * 3 + 1];
    const tex = new THREE.DataTexture(hf, hg, hg, THREE.RedFormat, THREE.FloatType);
    tex.magFilter = tex.minFilter = THREE.LinearFilter;
    tex.needsUpdate = true;
    const size = pa[(g - 1) * 3] - pa[0];
    terrain.traverse(o => {
      const u = o.material && o.material.uniforms;
      if (u && u.uLakeY) { u.uHF = { value: tex }; u.uHFSize = { value: size }; }
    });
  }

  // reflection pass: mirrored lamps drawn as glitter streaks into a full-res screen-aligned RT, sampled by
  // the lake shader (full res: the streaks are ~1.5 px wide)
  const reflScene = new THREE.Scene();
  const reflPts = new THREE.Points(geo, mk(1));
  reflPts.frustumCulled = false;
  reflScene.add(reflPts);
  const res = shared.uniforms.uResolution.value;
  const opts = { type: THREE.HalfFloatType, depthBuffer: false, minFilter: THREE.LinearFilter, magFilter: THREE.LinearFilter };
  let rt;
  const alloc = () => {
    if (rt) rt.dispose();
    rt = new THREE.WebGLRenderTarget(Math.round(res.x), Math.round(res.y), opts);
    shared.uniforms.uReflTex.value = rt.texture;
  };
  alloc();
  const fwd = new THREE.Vector3();

  return {
    points: pts,
    tune,
    update(camera) {
      if (rt.width !== Math.round(res.x) || rt.height !== Math.round(res.y)) alloc();
      // glitter-path length: a fixed angle (~0.02 rad) in screen px, shorter when looking steeply down
      camera.getWorldDirection(fwd);
      const pxRad = 0.5 * res.y / Math.tan(THREE.MathUtils.degToRad(camera.fov) * 0.5);
      lakePx.value = 1 / pxRad;
      // (round 5: 0.02 -> 0.013 rad: refs 7, 11 show short broken glints, 3-15 px, under the shore lamps)
      // (m9: 0.017 rad - the film's wide shots want longer reflections of the shore lights (art director); the
      // per-lamp spread (0.3 .. 1.1x) keeps most of them short glints)
      // (p2: 0.026 rad: from the high wide shots (p1_fK) the streaks were 7-24 px at 1080p, barely visible; critique
      // asked for 20-60 px)
      tune.uStreakLen.value = 0.026 * pxRad * (1 - 0.5 * THREE.MathUtils.smoothstep(-fwd.y, 0.35, 0.95));
      renderer.setRenderTarget(rt);
      renderer.setClearColor(0x000000, 1);
      renderer.clear();
      renderer.render(reflScene, camera);
    },
  };
}
