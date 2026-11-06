// Near-field land material for the terrain shader: photographic dolomite (CC0 Poly Haven scans, world-space
// triplanar at three scales), snow lying on every ledge and filling the recesses of that relief, forest, valley
// floor; lit by the twilight dome (skyIrradiance), a soft key from camera-left with relief shadows, the structure's
// lamps and town glow.
// Interface with terrain.js (terrain owner): ROCK is inserted into terrainFrag after its varyings / uniforms and
// NOISE, ATMOS, WATER, FAR; terrainFrag calls  col = shadeLand(dist, n0, skyVis, glowVis);  for every land
// fragment and applies applyAtmos itself. shadeLand may read the varyings vPos (world position), vNrm (normal),
// vNrmS (~5 m smoothed normal), vAttr (x sky visibility, y glow visibility, z water, w baked concavity 0.5-centred,
// 0 = none) and vRock (L3.rock outcrop relief), and the uniforms uDetail, uLampPos/uLampCol/uLampCount,
// uTownGlow/uTownGlowSize. Extra uniforms (the photographic maps) come from rockUniforms(), which terrain.js merges
// into every terrain level's material. Everything is derived from world-space vPos and the normals, so it works
// at any grid resolution (no uv / tangent attributes).
import * as THREE from 'three';

// ---- photographic maps, packed two per set: tX = albedo.rgb (sRGB, each channel scaled to a linear mean of 0.18:
// neutral grey, the shader keeps only the photo's light / dark structure) + normalised height (a: mean 0.5, sd ~0.16),
// tXN = normal.xy (signs checked against the height map) + ao (b). Snow: one map, normal.xy + height + ao.
async function bitmap(url) {
  const r = await fetch(url);
  if (!r.ok) throw new Error('fetch ' + url);
  // flipY: row 0 = bottom of the photo, so texture v runs up the photo (its baked top light stays on top)
  return createImageBitmap(await r.blob(), { colorSpaceConversion: 'none', premultiplyAlpha: 'none', imageOrientation: 'flipY' });
}
function pixels(bm, S) {
  const c = new OffscreenCanvas(S, S), g = c.getContext('2d', { willReadFrequently: true });
  g.imageSmoothingQuality = 'high';
  g.drawImage(bm, 0, 0, S, S);
  bm.close();
  return g.getImageData(0, 0, S, S).data;
}
function dataTex(data, S, srgb) {
  const t = new THREE.DataTexture(data, S, S, THREE.RGBAFormat, THREE.UnsignedByteType);
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.magFilter = THREE.LinearFilter;
  t.minFilter = THREE.LinearMipmapLinearFilter;
  t.generateMipmaps = true;
  t.anisotropy = 4;
  t.colorSpace = srgb ? THREE.SRGBColorSpace : THREE.NoColorSpace;
  t.needsUpdate = true;
  return t;
}
// height -> mean 0.5, sd 40/255 (sets differ a lot in range); returns per-pixel normalised byte height
function normHeight(H, S) {
  let s = 0, s2 = 0, n = 0;
  for (let i = 0; i < S * S * 4; i += 16) { s += H[i]; s2 += H[i] * H[i]; n++; }
  const m = s / n, sd = Math.max(1, Math.sqrt(Math.max(0, s2 / n - m * m)));
  const out = new Uint8Array(S * S);
  for (let i = 0, j = 0; j < S * S; i += 4, j++) out[j] = Math.max(0, Math.min(255, Math.round(128 + (H[i] - m) / sd * 40)));
  return out;
}
// sign of the normal map's x / y channels relative to -grad(height) (DirectX vs OpenGL maps, flipped rows)
function normalSigns(N, Hn, S) {
  let cx = 0, cy = 0;
  for (let y = 2; y < S - 2; y += 3) for (let x = 2; x < S - 2; x += 3) {
    const j = y * S + x, i = j * 4;
    cx -= (N[i] - 128) * (Hn[j + 1] - Hn[j - 1]);
    cy -= (N[i + 1] - 128) * (Hn[j + S] - Hn[j - S]);
  }
  return [cx < 0, cy < 0];
}
const LIN = Array.from({ length: 256 }, (_, v) => { const c = v / 255; return c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4); });
// linear (0..1, 4096 steps) -> sRGB byte
const ENC = Uint8Array.from({ length: 4096 }, (_, k) => { const c = k / 4095; return Math.round(255 * (c <= 0.0031308 ? c * 12.92 : 1.055 * Math.pow(c, 1 / 2.4) - 0.055)); });
async function packRock(id, S) {
  const [D, N, A, H] = (await Promise.all(['diff', 'nor', 'ao', 'disp'].map(m => bitmap(`./data/tex/${id}/${m}.jpg`)))).map(b => pixels(b, S));
  const Hn = normHeight(H, S), [fx, fy] = normalSigns(N, Hn, S);
  const n = S * S, mean = [0, 0, 0];
  for (let i = 0; i < n * 4; i += 4) { mean[0] += LIN[D[i]]; mean[1] += LIN[D[i + 1]]; mean[2] += LIN[D[i + 2]]; }
  const k = mean.map(m => 0.18 * n / Math.max(m, 1e-6) * 4095);
  const alb = new Uint8Array(n * 4), nrm = new Uint8Array(n * 4);
  for (let i = 0, j = 0; j < n; i += 4, j++) {
    for (let c = 0; c < 3; c++) alb[i + c] = ENC[Math.min(4095, Math.round(LIN[D[i + c]] * k[c]))];
    alb[i + 3] = Hn[j];
    nrm[i] = fx ? 255 - N[i] : N[i]; nrm[i + 1] = fy ? 255 - N[i + 1] : N[i + 1]; nrm[i + 2] = A[i]; nrm[i + 3] = 255;
  }
  return { alb: dataTex(alb, S, true), nrm: dataTex(nrm, S, false) };
}
async function packSnow(id, S) {
  const [N, A, H] = (await Promise.all(['nor', 'ao', 'disp'].map(m => bitmap(`./data/tex/${id}/${m}.jpg`)))).map(b => pixels(b, S));
  const Hn = normHeight(H, S), [fx, fy] = normalSigns(N, Hn, S);
  const t = new Uint8Array(S * S * 4);
  for (let i = 0, j = 0; j < S * S; i += 4, j++) {
    t[i] = fx ? 255 - N[i] : N[i]; t[i + 1] = fy ? 255 - N[i + 1] : N[i + 1]; t[i + 2] = Hn[j]; t[i + 3] = A[i];
  }
  return dataTex(t, S, false);
}

// (p2) land tuning knobs (uniforms, so a capture can compare settings without a shader recompile):
// uLandTune  x glow-light gain, y valley light under the cloud sea, z sky-light cut on bare near rock, w outcrop noise
// uLandTune2 x snow drift slope, y forest crown albedo gain, z wall-ledge threshold bonus, w snow crust albedo spread
// (p2 settings, picked from p2_*_b comparisons: glow 1.4x, valley 0.75x, bare-rock cut 0.5, drift slope 0.2, crust 0.6)
// (r9: drift slope 0.26, was 0.2: the snow domes 0.3-3 km out still read smooth)
export const LAND_TUNE = [[1.4, 0.75, 0.5, 1.3], [0.26, 1.0, 0.2, 0.6]];
// (r9 p2) A/B switches of the r9 changes (uniforms: a capture compares them without a recompile; these = shipped look)
// uLandAB  x ledge / cap test on the vertex normal (1) or the facet normal (0, p1) of sheer facets, y strat beds on,
//          z ledge test beyond ~0.13 m per pixel on, w macro layer on
// uLandAB2 x facet-normal override strength, y rock ribs on, z drift relief on, w outcrops 'r9 p2' (1) or 'p1' (0)
// uLandAB3 x dome light on the far snow, y key on the far snow, z snow hue (0 = r8 periwinkle, 1 = greyer steel blue),
//          w lee shade of the crests
// uLandAB4 x macro relief out of the ledge test beyond ~0.13 m per pixel, y floor of the outcrop threshold on the
//          crests, z darkening of the outcrop pieces, w outcrop pieces + wall joints on (cost check)
// uLandAB5 x the ~5 m normal following a much steeper vertex normal (p1: 1), y outcrop pieces shrink away past ~5 km
//          (1) or fade to grey (0), z outcrop pieces only from ~0.2 m per pixel (1) or ~0.1 (0), w unused
// (p2 picks, out/snow9_ab1 / ab2: the macro relief out of the far ledge test removed the pen hatching (f540 flank
// gy/gx 2.85 -> 1.50, f1200 wall 2.20 -> 1.41); the steep vertex normal at half weight gives the hero pinnacles back
// some of their snow (f240 L* 18.0 -> 19.5) without the hanging streaks of r8 at f540 / f750)
export const LAND_AB = [[1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1], [1, -0.04, 0.5, 1], [0.5, 1, 0, 0]];

// (r9) convexity of the L2 DEM (8 km at 6.25 m round the ring; read from the baked data, nothing rebaked): r = the
// height above its ~25 m surroundings (128 + 16 per m), g = above its ~90 m surroundings (128 + 4 per m). The snow
// fields 0.3-4 km out lie on L2, whose baked concavity (attr.w) is ~0 on its 6 m grid: this gives shadeLand their
// crests, knolls and wind lips (scoured, rock breaking through) and their drift-filled hollows
async function landConvexity() {
  const base = './data/terrain/';
  const meta = await (await fetch(base + 'meta.json')).json();
  const lv = meta.LEVELS.find(l => l.name === 'L2');
  const r = await fetch(base + 'L2.f32');
  if (!lv || !r.ok) throw new Error('L2.f32');
  const H = new Float32Array(await r.arrayBuffer()), g = lv.grid;
  if (H.length !== g * g) throw new Error('L2 size');
  // separable box blur (edges clamped), radius rr cells
  const cl = i => Math.min(g - 1, Math.max(0, i));
  const box = (src, rr) => {
    const tmp = new Float32Array(g * g), out = new Float32Array(g * g), k = 1 / (2 * rr + 1);
    for (let j = 0; j < g; j++) {
      const row = j * g;
      let s = 0;
      for (let i = -rr; i <= rr; i++) s += src[row + cl(i)];
      for (let i = 0; i < g; i++) { tmp[row + i] = s * k; s += src[row + cl(i + rr + 1)] - src[row + cl(i - rr)]; }
    }
    for (let i = 0; i < g; i++) {
      let s = 0;
      for (let j = -rr; j <= rr; j++) s += tmp[cl(j) * g + i];
      for (let j = 0; j < g; j++) { out[j * g + i] = s * k; s += tmp[cl(j + rr + 1) * g + i] - tmp[cl(j - rr) * g + i]; }
    }
    return out;
  };
  const b1 = box(box(H, 2), 2), b2 = box(box(H, 7), 7);
  const t = new Uint8Array(g * g * 4), q = v => Math.max(0, Math.min(255, Math.round(v)));
  for (let k = 0; k < g * g; k++) {
    t[k * 4] = q(128 + 16 * (H[k] - b1[k])); t[k * 4 + 1] = q(128 + 4 * (H[k] - b2[k])); t[k * 4 + 2] = 128; t[k * 4 + 3] = 255;
  }
  const tex = dataTex(t, g, false);
  tex.wrapS = tex.wrapT = THREE.ClampToEdgeWrapping;
  return { tLandC: { value: tex }, uLandC: { value: new THREE.Vector4(-lv.size / 2, -lv.size / 2, lv.size / (g - 1), g) } };
}
async function landConvexityOrFlat() {
  try { return await landConvexity(); } catch (e) {
    console.warn('land convexity', e);
    return { tLandC: { value: dataTex(new Uint8Array([128, 128, 128, 255]), 1, false) }, uLandC: { value: new THREE.Vector4(0, 0, 1, 1) } };
  }
}

const landAB = () => ({ uLandAB: { value: new THREE.Vector4(...LAND_AB[0]) }, uLandAB2: { value: new THREE.Vector4(...LAND_AB[1]) },
  uLandAB3: { value: new THREE.Vector4(...LAND_AB[2]) }, uLandAB4: { value: new THREE.Vector4(...LAND_AB[3]) },
  uLandAB5: { value: new THREE.Vector4(...LAND_AB[4]) } });

export async function rockUniforms() {
  const LC = await landConvexityOrFlat();
  try {
    // A: cliff_side (layered cliff, stood upright on the walls: the dolomite's vertical pillars, flutes and chimneys),
    // B: marble_cliff_03 (blocky jointed cliff: blocks, ledges, cracks; also the macro layer seen from above),
    // C: rock_face_03 (knobbly fractured rock: grain), snow_02 (soft wind-packed snow, no footprints)
    // (B at 2k: it carries the near walls (v10 / v1 / v9) at 5-20 m, where 1k texels were magnified ~2.5x)
    const [A, B, C, S] = await Promise.all([packRock('cliff_side', 2048), packRock('marble_cliff_03', 2048),
      packRock('rock_face_03', 1024), packSnow('snow_02', 1024)]);
    return {
      tRockA: { value: A.alb }, tRockAN: { value: A.nrm }, tRockB: { value: B.alb }, tRockBN: { value: B.nrm },
      tRockC: { value: C.alb }, tRockCN: { value: C.nrm }, tSnowN: { value: S }, uTexOn: { value: 1 },
      uLandTune: { value: new THREE.Vector4(...LAND_TUNE[0]) }, uLandTune2: { value: new THREE.Vector4(...LAND_TUNE[1]) }, ...LC, ...landAB(),
    };
  } catch (e) {
    console.warn('rock textures', e);
    const one = (v) => dataTex(new Uint8Array(v), 1, false);
    const a = one([116, 116, 116, 128]), nn = one([128, 128, 255, 255]);
    return {
      tRockA: { value: a }, tRockAN: { value: nn }, tRockB: { value: a }, tRockBN: { value: nn },
      tRockC: { value: a }, tRockCN: { value: nn }, tSnowN: { value: one([128, 128, 128, 255]) }, uTexOn: { value: 0 },
      uLandTune: { value: new THREE.Vector4(...LAND_TUNE[0]) }, uLandTune2: { value: new THREE.Vector4(...LAND_TUNE[1]) }, ...LC, ...landAB(),
    };
  }
}

export const ROCK = /* glsl */ `
uniform sampler2D tRockA;
uniform sampler2D tRockAN;
uniform sampler2D tRockB;
uniform sampler2D tRockBN;
uniform sampler2D tRockC;
uniform sampler2D tRockCN;
uniform sampler2D tSnowN;
uniform float uTexOn;
uniform vec4 uLandTune;
uniform vec4 uLandTune2;
uniform sampler2D tLandC;       // (r9) L2 DEM convexity (landConvexity)
uniform vec4 uLandC;            // its x0, z0, cell (m), texels
uniform vec4 uLandAB;           // (r9 p2) A/B switches, LAND_AB
uniform vec4 uLandAB2;
uniform vec4 uLandAB3;
uniform vec4 uLandAB4;
uniform vec4 uLandAB5;

// ---- world-space triplanar sampling with explicit gradients (mip + anisotropic filtering, safe inside the
// projection branches). gTW: projection weights (x: YZ plane, y: XZ, z: XY), gDPX / gDPY: screen derivatives of vPos
// for the normal maps (read softer), gDAX / gDAY: the same for albedo + height (read near the pixel footprint).
vec3 gTW = vec3(0.0, 1.0, 0.0);
vec3 gDPX = vec3(0.0), gDPY = vec3(0.0);
vec3 gDAX = vec3(0.0), gDAY = vec3(0.0);

mat2 rot2(float a){ float c = cos(a), s = sin(a); return mat2(c, s, -s, c); }
// one layer: the walls (x / z projections) sample tV at tile size sc (m; x along the photo's u, y along v) turned by
// rotV; the horizontal projection samples tH at sh (m) turned by rotH. A: albedo.rgb + height, g: world-space slope
// of the relief (-grad h, from the normal map), ao. Weighted over the projections.
void triRock(sampler2D tV, sampler2D tVN, sampler2D tH, sampler2D tHN, vec3 p, vec2 sc, float sh, float rotV, float rotH,
    out vec4 A, out vec3 g, out float ao){
  A = vec4(0.0); g = vec3(0.0); ao = 0.0;
  vec2 isc = 1.0 / sc, ss = vec2(min(sc.x, sc.y)) * isc;
  mat2 R = rot2(rotV);
  if (gTW.x > 0.0) {
    vec2 uv = (R * p.zy) * isc + vec2(0.37, 0.11), dx = (R * gDPX.zy) * isc, dy = (R * gDPY.zy) * isc;
    vec4 a = textureGrad(tV, uv, (R * gDAX.zy) * isc, (R * gDAY.zy) * isc), n = textureGrad(tVN, uv, dx, dy);
    vec2 t = ((n.xy * 2.0 - 1.0) * ss) * R;
    A += gTW.x * a; ao += gTW.x * n.z; g += gTW.x * vec3(0.0, t.y, t.x);
  }
  if (gTW.z > 0.0) {
    vec2 uv = (R * p.xy) * isc + vec2(0.71, 0.53), dx = (R * gDPX.xy) * isc, dy = (R * gDPY.xy) * isc;
    vec4 a = textureGrad(tV, uv, (R * gDAX.xy) * isc, (R * gDAY.xy) * isc), n = textureGrad(tVN, uv, dx, dy);
    vec2 t = ((n.xy * 2.0 - 1.0) * ss) * R;
    A += gTW.z * a; ao += gTW.z * n.z; g += gTW.z * vec3(t.x, t.y, 0.0);
  }
  if (gTW.y > 0.0) {
    mat2 Rh = rot2(rotH);
    float ih = 1.0 / sh;
    vec2 uv = (Rh * p.xz) * ih + vec2(0.13, 0.89), dx = (Rh * gDPX.xz) * ih, dy = (Rh * gDPY.xz) * ih;
    vec4 a = textureGrad(tH, uv, (Rh * gDAX.xz) * ih, (Rh * gDAY.xz) * ih), n = textureGrad(tHN, uv, dx, dy);
    vec2 t = (n.xy * 2.0 - 1.0) * Rh;
    A += gTW.y * a; ao += gTW.y * n.z; g += gTW.y * vec3(t.x, 0.0, t.y);
  }
}
// height only (same mapping as triRock), for the relief shadow probes
float triH(sampler2D tV, sampler2D tH, vec3 p, vec2 sc, float sh, float rotV, float rotH){
  float h = 0.0;
  vec2 isc = 1.0 / sc;
  mat2 R = rot2(rotV);
  if (gTW.x > 0.0) h += gTW.x * textureGrad(tV, (R * p.zy) * isc + vec2(0.37, 0.11), (R * gDPX.zy) * isc, (R * gDPY.zy) * isc).a;
  if (gTW.z > 0.0) h += gTW.z * textureGrad(tV, (R * p.xy) * isc + vec2(0.71, 0.53), (R * gDPX.xy) * isc, (R * gDPY.xy) * isc).a;
  if (gTW.y > 0.0) {
    mat2 Rh = rot2(rotH);
    float ih = 1.0 / sh;
    h += gTW.y * textureGrad(tH, (Rh * p.xz) * ih + vec2(0.13, 0.89), (Rh * gDPX.xz) * ih, (Rh * gDPY.xz) * ih).a;
  }
  return h;
}
// snow relief (normal.xy, height, ao) at tile size sc, same scheme
vec4 triSnow(vec3 p, float sc, float rot, out vec3 g){
  vec4 o = vec4(0.0);
  g = vec3(0.0);
  float isc = 1.0 / sc;
  mat2 R = rot2(rot);
  if (gTW.x > 0.0) {
    vec4 n = textureGrad(tSnowN, (R * p.zy) * isc + 0.29, (R * gDPX.zy) * isc, (R * gDPY.zy) * isc);
    vec2 t = (n.xy * 2.0 - 1.0) * R;
    o += gTW.x * n; g += gTW.x * vec3(0.0, t.y, t.x);
  }
  if (gTW.z > 0.0) {
    vec4 n = textureGrad(tSnowN, (R * p.xy) * isc + 0.61, (R * gDPX.xy) * isc, (R * gDPY.xy) * isc);
    vec2 t = (n.xy * 2.0 - 1.0) * R;
    o += gTW.z * n; g += gTW.z * vec3(t.x, t.y, 0.0);
  }
  if (gTW.y > 0.0) {
    vec4 n = textureGrad(tSnowN, (R * p.xz) * isc + 0.83, (R * gDPX.xz) * isc, (R * gDPY.xz) * isc);
    vec2 t = (n.xy * 2.0 - 1.0) * R;
    o += gTW.y * n; g += gTW.y * vec3(t.x, 0.0, t.y);
  }
  return o;
}
float lum3(vec3 c){ return dot(c, vec3(0.2126, 0.7152, 0.0722)); }
// layer weight: a tile of sc metres carries detail while it spans enough pixels (fp: m per pixel)
float scaleFade(float sc, float fp){ return 1.0 - smoothstep(sc * 0.025, sc * 0.10, fp); }

// the relief layers (macro: upright pillars on the walls, jointed blocks from above; mid: jointed blocks and
// ledges; fine: knobbly grain; micro: the same grain at 0.8 m for the rock within ~20 m of the camera). Tile sizes /
// turns shared by the shading and the shadow probes.
#define L1_SC vec2(64.0, 30.0)
#define L1_SH 40.0
// (m9: 0.3, was 1.5708 - the photo's layers stood upright as pillars: seen from the free-flight cameras the walls read
// as tree bark (out/shots/base_fF / fG); the dolomite's bedding now dips gently (~17 deg; level, a1, read as a layer
// cake), the joints of the mid layer cut it)
#define L1_RV 0.3
#define L1_RH 0.6
#define L2_SC vec2(10.0)
#define L2_RV 0.22
#define L2_RH 2.1
#define L3_SC vec2(2.4)
#define L3_RV -0.5
#define L3_RH 1.3
#define L4_SC vec2(0.8)
#define L4_RV 1.9
#define L4_RH -2.4
// relief height in metres per normalised unit (sd ~0.16): macro pillars ~ +-3 m, blocks ~ +-0.6 m
#define L1_M 19.0
#define L2_M 4.0

// rock ribs: ridged gradient noise stretched vertically (on the slopes the bands run down the fall line, on the
// walls they follow the pillars), two sizes (the small one fades to its mean before it aliases); ~0..1, high along
// the ribs. (A noise in a frame turned to the local fall line would multiply ~2 km world coordinates by a direction
// that varies over metres: moire.)
float ribNoise(vec3 q, float fp){
  float r1 = 1.0 - abs(gnoise3(q / vec3(23.0, 60.0, 23.0)));
  float r2 = 1.0 - abs(gnoise3(q / vec3(8.0, 21.0, 8.0) + 3.7));
  // (m8: the small ribs fade from ~0.15 m per pixel (was 0.5): at 300-600 m they too speckled the snowfields)
  // (m9: the large ones fade too, from ~2.5 m per pixel: the valley slopes 3-15 km out, film wide shots)
  return 0.6 * mix(r1, 0.68, smoothstep(2.5, 8.0, fp)) + 0.4 * mix(r2, 0.68, smoothstep(0.15, 0.6, fp));
}

// conifer crowns (m9) on a jittered ground grid (xz, cells of TREE_C m), one tree per cell where a hash falls below the
// stand density. Each tree is drawn on the ground it hides from the camera: a teardrop from its crown's base disc
// (radius ~0.4 cell) up to its tip ls cells farther from the camera (vh: horizontal view direction), so the crowns
// stand up as cones on screen. Returns x = cover (antialiased over aa cells), y = position up the crown (0 base ..
// 1 tip), z = across the crown (-1 .. 1), w = tree random; the tree nearest the camera wins.
#define TREE_C 6.5
vec4 treeCrowns(vec2 p, vec2 vh, float ls, float dens, float aa){
  vec2 i = floor(p - vh * (0.5 * ls));
  vec4 o = vec4(0.0, 0.0, 0.0, 0.5);
  float bs = -9.0, keep = 1.0;
  for (int b = -1; b <= 1; b++) for (int a = -1; a <= 1; a++) {
    vec2 g = i + vec2(float(a), float(b));
    vec3 h = hash33(vec3(g, 7.31));
    if (h.z > dens) continue;
    vec2 d = p - (g + 0.2 + 0.6 * h.xy);
    float s = dot(d, vh);
    float rr = fract(h.x * 13.7 + h.y * 5.3);
    // (p2: each tree its own height, 0.6-1.0x: one length for all drew a field of identical parallel strokes)
    float lt = ls * (0.6 + 0.4 * fract(h.y * 7.1 + h.x * 3.3));
    float t = clamp(s / max(lt, 1e-3), 0.0, 1.0);
    vec2 e = d - vh * (t * lt);
    float r = (0.30 + 0.16 * rr) * (1.0 - 0.85 * t);
    float m = smoothstep(r + aa, r - aa, length(e));
    keep *= 1.0 - m;
    if (m > 0.3 && s > bs) { bs = s; o.yzw = vec3(t, dot(e, vec2(-vh.y, vh.x)) / max(r, 1e-3), rr); }
  }
  o.x = 1.0 - keep;
  return o;
}

// rock blocks on the slopes: Euclidean Voronoi cells (cell size BLK_SC m: columns, taller than wide), x = distance
// to the joint (F2 - F1, cell units), yzw = cell random; rel = position relative to the cell's centre (cell units)
#define BLK_SC vec3(3.4, 8.0, 3.4)
vec4 blockCell(vec3 p, out vec3 rel){
  vec3 i = floor(p), f = fract(p);
  float d1 = 9.0, d2 = 9.0;
  vec3 h1 = vec3(0.5), o1 = vec3(0.0);
  for (int c = -1; c <= 1; c++) for (int b = -1; b <= 1; b++) for (int a = -1; a <= 1; a++) {
    vec3 gc = vec3(float(a), float(b), float(c));
    vec3 h = hash33(i + gc);
    vec3 o = gc + 0.15 + 0.7 * h - f;
    float d = dot(o, o);
    if (d < d1) { d2 = d1; d1 = d; h1 = h; o1 = o; } else if (d < d2) d2 = d;
  }
  rel = -o1;
  return vec4(sqrt(d2) - sqrt(d1), h1);
}

// soft key from the bright sky up and left of the hero views (the same az ~110 / 15 deg key as far.js's farLight)
const vec3 KEY = vec3(0.908, 0.259, 0.330);

// land radiance (before aerial perspective)
vec3 shadeLand(float dist, vec3 n0, float skyVis, float glowVis){
  vec3 col;
  float alt = vPos.y;
  float nearF = uDetail * (1.0 - smoothstep(600.0, 3000.0, dist));
  // baked concavity (+ gullies / ledge backs, - ribs / block edges); 0 = level baked without it
  float curv = vAttr.w > 0.002 ? clamp((vAttr.w - 0.502) * 2.0, -1.0, 1.0) : 0.0;
  float big = fbm2(vPos.xz / 1400.0, 4);
  vec3 nS = normalize(vNrmS);
  // (r9) the DEM's convexity round the ring (landConvexity: m above the ~25 m / ~90 m surroundings, 0 beyond L2's
  // 8 km): crests, knolls and wind lips (crest) against hollows and drift-filled gullies (hollow) on the snow fields
  // 0.3-4 km out, where the baked concavity (curv) is ~0 on the 6 m grid
  vec2 cuv = ((vPos.xz - uLandC.xy) / uLandC.z + 0.5) / uLandC.w;
  vec2 cvx = (texture2D(tLandC, cuv).rg - 0.50196) * vec2(15.94, 63.75)
           * (1.0 - smoothstep(0.46, 0.5, max(abs(cuv.x - 0.5), abs(cuv.y - 0.5))));
  float crest = clamp(0.6 * smoothstep(0.25, 1.8, cvx.x) + 0.6 * smoothstep(1.5, 8.0, cvx.y), 0.0, 1.0);
  float hollow = clamp(0.5 * smoothstep(-0.2, -1.5, cvx.x) + 0.6 * smoothstep(-1.0, -7.0, cvx.y), 0.0, 1.0);
  // snow line ~1150 m (patchy), everything above holds snow where it can
  // (p2: ~1050 m, was 1150: the clearings and meadows on the lake's slopes go grey-white, critique 2)
  float snowLine = 1050.0 + 300.0 * (big - 0.47) * 2.0;
  float altMask = smoothstep(snowLine - 200.0, snowLine + 200.0, alt);

  // ---- photographic relief at four scales (each fades out as its tile shrinks below ~10-40 pixels)
  vec3 dPX = dFdx(vPos), dPY = dFdy(vPos);
  float lx = length(dPX), ly = length(dPY);
  float fp = max(max(min(lx, ly), max(lx, ly) * 0.125), 1e-4);
  // (r9) the heightfield draws a sheer face as tall thin triangles between two grid columns, and their interpolated
  // vertex normals (central differences across the break) tilt up to ~45 deg: the pinnacles' walls and the sides of
  // their flat-topped blocks were snowed, textured and lit as moderate slopes - white streaks hanging down the faces,
  // photos smeared down them. Where the facet itself (screen derivatives of the position: exact on a plane) is much
  // steeper than its vertex normal, the facet's normal is used (seen from ~30 m on; near levels only, out to ~3 km:
  // the far ranges keep their smooth DEM normals)
  vec3 nG = cross(dPX, dPY);
  float lg = length(nG);
  float tallW = uDetail * smoothstep(0.02, 0.05, fp) * (1.0 - smoothstep(2500.0, 3900.0, dist));
  // (p2) the vertex normal kept for the ledge / cap test (p1 critique 4: on the facet normal the hero pinnacles lost
  // the snow plastered on their ledges and the caps along their rims), and the override's weight (ovr: the vertical
  // joints of the sheer faces below)
  vec3 n0v = n0;
  float ovr = 0.0;
  if (tallW > 0.0 && lg > 0.05 * lx * ly && lg > 1e-12) {
    nG = nG / lg * (dot(nG, n0) < 0.0 ? -1.0 : 1.0);
    ovr = smoothstep(0.2, 0.4, n0.y - nG.y) * tallW;
    n0 = normalize(mix(n0, nG, ovr * uLandAB2.x) + vec3(0.0, 1e-4, 0.0));
  }
  // (r9) where a facet is much steeper than its ~5 m surroundings (the spires, fins and block sides of the pinnacles)
  // the smoothed normal called it gentle: snow held on vertical faces as hanging white streaks ('icicles', ESE
  // pinnacle, film t 18 / 25) and the horizontal projection stretched the photos down them (WNW pinnacle, t 11). There
  // the snow, the projections and the terminator follow the facet - seen from ~30 m on (closer, per-facet switches
  // drew the mesh's polygons on the near walls)
  // (p2: x uLandAB5.x - at full strength the hero pinnacles (t 8) lost the snow plastered on their spires, critique 4)
  nS = normalize(mix(nS, n0, smoothstep(0.22, 0.45, nS.y - n0.y) * smoothstep(0.02, 0.05, fp) * uLandAB5.x) + vec3(0.0, 1e-4, 0.0));
  // albedo / height are read at the pixel footprint (crisp near rock; the film's jittered sub-frames supersample it);
  // the normal maps ~0.6 mip level softer: the key light turns normal-map detail at the pixel's own frequency into a
  // one-pixel checker (and film shimmer)
  gDAX = dPX; gDAY = dPY;
  gDPX = dPX * 1.5; gDPY = dPY * 1.5;
  // projection weights: the azimuth (x vs z wall projection) from the ~5 m normal (per-facet switches drew polygon
  // seams across the near walls), the up / side split mostly from it too, a little from the vertex normal (a facet
  // much steeper than its surroundings is not smeared by the horizontal projection; more of it switched the
  // projections in streaks along the near field's long thin sculpted ribs)
  vec3 nM = normalize(0.35 * n0 + nS + vec3(0.0, 1e-3, 0.0));
  vec2 az = nS.xz + 0.05 * nM.xz;
  az /= max(length(az), 1e-4);
  vec3 nP = vec3(az.x * length(nM.xz), nM.y, az.y * length(nM.xz));
  // (narrow blends: most pixels read one projection, two only within ~10 deg of the diagonals)
  vec3 tw = pow(abs(nP), vec3(6.0));
  tw /= max(tw.x + tw.y + tw.z, 1e-6);
  tw = max(tw - 0.07, 0.0);
  gTW = tw / max(tw.x + tw.y + tw.z, 1e-6);
  float texF = uTexOn * nearF;
  float f1 = texF * scaleFade(L1_SC.y, fp) * uLandAB.w, f2 = texF * scaleFade(L2_SC.x, fp), f3 = texF * scaleFade(L3_SC.x, fp);
  float f4 = texF * scaleFade(L4_SC.x, fp);
  // (the macro layer also fades out where its ~3 cm texels are magnified (rock within ~10 m): its strata, blurred and
  // stretched over the near wall, drew long parallel streaks; the mid / fine / micro layers carry the near rock)
  float f1s = f1;
  f1 *= smoothstep(0.003, 0.012, fp);
  vec4 A1 = vec4(0.18, 0.18, 0.18, 0.5), A2 = A1, A3 = A1, A4 = A1;
  vec3 g1 = vec3(0.0), g2 = vec3(0.0), g3 = vec3(0.0), g4 = vec3(0.0);
  float ao1 = 1.0, ao2 = 1.0, ao3 = 1.0, ao4 = 1.0;
  // smooth domain warp (+-7 m over ~50 m): breaks the tiling period of the macro / mid layers without seams, and
  // lets the pillars wander
  vec3 wp = (vec3(vnoise3(vPos / 53.0), vnoise3(vPos / 53.0 + 7.3), vnoise3(vPos / 53.0 + 3.1)) - 0.5) * 14.0 * step(1e-3, texF);
  vec3 p1 = vPos + wp, p2 = vPos + 13.7 - 0.6 * wp, p3 = vPos + 5.3;
  if (f1 > 0.0) triRock(tRockA, tRockAN, tRockB, tRockBN, p1, L1_SC, L1_SH, L1_RV, L1_RH, A1, g1, ao1);
  if (f2 > 0.0) triRock(tRockB, tRockBN, tRockB, tRockBN, p2, L2_SC, L2_SC.x, L2_RV, L2_RH, A2, g2, ao2);
  if (f3 > 0.0) triRock(tRockC, tRockCN, tRockC, tRockCN, p3, L3_SC, L3_SC.x, L3_RV, L3_RH, A3, g3, ao3);
  if (f4 > 0.05) triRock(tRockC, tRockCN, tRockC, tRockCN, vPos + 2.9, L4_SC, L4_SC.x, L4_RV, L4_RH, A4, g4, ao4);
  // relief height (normalised units, sd ~0.16 per layer; the grain only frays the outlines), what is no longer
  // resolved (faded layers), and slope
  float H = (A1.a - 0.5) * f1 + (A2.a - 0.5) * 0.75 * f2 + (A3.a - 0.5) * 0.25 * f3;
  float sdU = 0.16 * length(vec3(1.0 - f1s, 0.75 * (1.0 - f2), 0.25 * (1.0 - f3)));
  vec3 g = g1 * (1.8 * f1) + g2 * (1.4 * f2) + g3 * (1.0 * f3) + g4 * (0.8 * f4);
  g -= n0 * dot(g, n0);
  // (ledges / block outlines follow the macro and mid relief only: the grain made a salt-and-pepper of specks)
  // (m9: the macro layer 1.2, was 2.0: with its bedding no longer upright it put a snow line on every bed - zebra
  // walls in the FPV passes, a1_fF)
  float gentle = smoothstep(0.5, 0.85, nS.y);
  float steepF = 1.0 - smoothstep(0.35, 0.6, nS.y);
  // (p2: on the sheer walls the macro layer no longer places ledges at all: its gently dipping beds put a snow dash on
  // every bed - the FPV cliff (p1_fF) was one zebra of horizontal dashes)
  // (p2: the macro relief fades out of it from ~0.13 m per pixel: its gently dipping beds put a snow ledge on every bed
  // of the 40-60 deg slopes seen from 0.3-1.5 km - the 'pen hatching' / zebra of p1 critique 2, f540 / f1200)
  vec3 gL = g1 * (1.2 * f1 * (1.0 - steepF) * (1.0 - uLandAB4.x * smoothstep(0.13, 0.3, fp))) + g2 * (1.6 * f2);
  gL -= n0 * dot(gL, n0);
  float aoT = mix(1.0, ao1, 0.6 * f1) * mix(1.0, ao2, 0.7 * f2) * mix(1.0, ao3, 0.6 * f3) * mix(1.0, ao4, 0.5 * f4);

  // ---- rock ribs (refs 6 / 7 / 2 / 11: bands of broken rock running down the slopes between white chutes, from the
  // foreground out to ~3 km): ridged noise up the fall line, the baked outcrops and convex ribs, never the gullies.
  // rkS: rock-ness of the slope (0 ~ half rock on a 60 deg slope, < 0 snow)
  float rk = vRock > 0.5 / 255.0 ? (vRock - 1.0 / 255.0) * 255.0 / 254.0 * uLandAB2.y : 0.0;
  // (only where snow can lie: on the walls it changes nothing)
  float hold = nS.y + 0.22 * curv;
  float rib = hold > 0.44 && uLandAB2.y > 0.5 ? ribNoise(vPos + 0.3 * wp, fp) : 0.68;
  float rkS = 1.6 * (rib - 0.68) + 0.9 * rk - 0.9 * curv + 0.55 * steepF - 0.25 * gentle;
  // (p2) seen from ~150 m to 3 km (farB below) the rock comes in irregular outcrops of ~5-80 m: an isotropic noise,
  // clustered on the convex breaks and wind-scoured crests at any slope. The stretched ribs, the sculpted ribs (rk) and
  // the beds thresholded there into parallel pen strokes of one length and direction (p1 critique 4: fE / fA / fJ);
  // they weigh far less in that range. Each octave fades to its mean before it falls below ~3 px.
  float farB0 = smoothstep(0.13, 0.3, fp);
  if (farB0 > 0.0) {
    float blob = 0.55 * gnoise3(vPos / 70.0 + 2.3) + 0.3 * gnoise3(vPos / 23.0 + 6.1) * (1.0 - smoothstep(2.3, 6.0, fp))
               + 0.15 * gnoise3(vPos / 8.0 + 1.9) * (1.0 - smoothstep(0.8, 2.0, fp));
    float rkF = 0.5 * (rib - 0.68) + 0.25 * rk - 1.5 * curv + 0.55 * steepF - 0.3 * gentle + uLandTune.w * blob;
    rkS = mix(rkS, rkF, farB0);
  }

  // ---- rock blocks on the slopes (refs 7 / 6: angular blocks of 1-4 m standing out of the snow, each with a snow
  // cap above a lit or shadowed front), in the rib bands only (clusters, not an even sprinkle), of mixed sizes; on
  // the walls none (the macro photo's slabs and joints carry them: stacked cells read as crazy paving). Resolved only
  // while a block spans more than ~18 px (smaller, they were a field of regular dots)
  float fB = texF * (1.0 - smoothstep(BLK_SC.x / 40.0, BLK_SC.x / 18.0, fp)) * (1.0 - steepF);
  vec4 bc = vec4(1.0, 0.5, 0.5, 0.5);
  vec3 bRel = vec3(0.0);
  // (one fixed cell size: dividing world coordinates (~2000 m) by a scale that varies with the slope packed
  // dozens of cells into a few metres - contour-line moire)
  vec3 pB = vPos + 0.5 * wp;
  float pres = 0.0;
  if (fB > 0.0) {
    bc = blockCell(pB / BLK_SC, bRel);
    // the cell is a block with the probability of the rib field (~10-20 m features: nearly constant over a cell;
    // re-evaluating it at the cell centre cost ~8% of the terrain pass)
    pres = step(bc.y, smoothstep(-0.6, 0.15, rkS));
  }
  // footprint: the cell interior (a per-cell size), its outline frayed by the photo relief
  float be = bc.x + 0.5 * H;
  float bw = max(fwidth(be) * 0.7, 0.015);
  float bth = 0.08 + 0.3 * bc.w;
  float blkIn = smoothstep(bth - bw, bth + bw, be);
  float blk = pres * blkIn * fB;
  vec3 rW = bRel * BLK_SC;
  rW -= n0 * dot(rW, n0);
  vec3 lean = (bc.yzw - 0.5) * 0.5;
  lean -= n0 * dot(lean, n0);
  // (a low dome only: strong domes read as cobbles)
  vec3 dome = (rW * 0.12 + lean) * pres * fB;
  // rock shading normal: dome + photographic relief (harder on the slopes, where the blocks stand free)
  vec3 nb = normalize(n0 + dome + g * (1.0 + 0.5 * gentle));

  // ---- snow (crisp edges, antialiased by the pixel footprint of each threshold):
  // 1. cover: the ~5 m slope (wind-packed snow clings up to ~62 deg), broken by the 1.6 m facets (risers bare)
  // (m9) a sub-facet wobble on the snow thresholds: they test interpolated normals, whose iso-lines run straight inside
  // each terrain triangle - seen from 20-50 m (FPV passes) the snow edges drew the mesh as polygons (p1_fN / fO); it
  // fades out before it falls below ~3 px
  float wob = (0.06 * gnoise3(vPos / 3.1 + 2.7) + 0.035 * gnoise3(vPos / 1.13 + 5.1) * (1.0 - smoothstep(0.04, 0.12, fp)))
            * (1.0 - smoothstep(0.1, 0.35, fp)) * uTexOn;
  // (p2: from ~0.15 m per pixel on the riser test reads mostly the ~5 m normal: the steep sides of the sculpted ribs,
  // thresholded on the vertex normal, drew the parallel pen strokes over the 30-55 deg slopes seen from 300-900 m,
  // p1 / p2a_fE, fA)
  float cover = smoothstep(0.45, 0.49, hold + wob) * smoothstep(0.30, 0.36, mix(n0.y, nS.y, 0.8 * farB0) + 0.08 * curv + wob);
  // 2. outcrops: the rib bands frayed by the photographic relief (rock pokes through where the relief stands proud),
  // plus the blocks; at 1-3 km (relief faded) the bands alone, kept crisp - dark ribs between white chutes, not
  // the grey dapple a threshold widened by the unresolved relief gave
  // (the mid blocks and the grain weigh more here than in H: on the 35-50 deg slopes the rock breaks through in
  // 1-5 m pieces, not in macro-tile blobs)
  // (m8: from ~0.15 m per pixel on (the peaks of view 2 at 300-600 m) the 10 m blocks of the mid layer weigh much
  // less: they broke the snow into a speckle of 20-50 px rock dots ('hedgehog'); ref 2 has big continuous snowfields
  // between the rock ribs. The hero slopes (v4 / 5 / 6 / 7 / 11) are at ~0.08-0.12 m per pixel and keep their blocks)
  float farB = smoothstep(0.13, 0.3, fp);
  float Ho = (A1.a - 0.5) * 0.7 * f1 + (A2.a - 0.5) * f2 * (1.0 - 0.65 * farB) + (A3.a - 0.5) * 0.5 * f3;
  float sdO = 0.16 * length(vec3(0.7 * (1.0 - f1s), 1.0 - f2, 0.5 * (1.0 - f3)));
  // (m9, free-flight film: seen from ~150 m to 3 km the photo relief thresholded on its own drew a scribble of thin
  // tan flecks over every snow slope (out/shots/base_fA / base_fE). There the rock now comes in coherent pieces:
  // limestone strata outcropping along the contours where the slope steepens (the Rothorn's bedding), the ribs and
  // convex breaks; the photo relief only frays their edges, and the gentle snow between them stays clean)
  float strat = 0.0;
  if (farB > 0.0) {
    // bedding ~3-6 m thick, gently dipping, its continuity varying over ~250 m; only the harder beds crop out (a few
    // per 100 m of height), broken along the band by ~60-150 m gaps, where the slope steepens past ~30 deg
    // (a1: every bed on every slope drew contour-line zebra stripes)
    float sy = vPos.y + 0.06 * vPos.x - 0.04 * vPos.z + 30.0 * vnoise3(vPos / vec3(240.0, 400.0, 240.0));
    float sb = abs(gnoise3(vec3(vPos.x / 260.0, sy / 23.0, vPos.z / 260.0)));
    float hard = smoothstep(0.45, 0.75, vnoise3(vec3(vPos.x / 90.0, sy / 41.0, vPos.z / 90.0) + 1.7));
    strat = smoothstep(0.30, 0.08, sb) * smoothstep(0.88, 0.70, nS.y) * hard;
    strat *= 1.0 - smoothstep(1.5, 5.0, fp);
    // (p2: only a third as strong, and only where the outcrop field is already rocky: alone the beds drew layer-cake
    // contour stripes over whole slopes, p1_fJ / fA)
    strat *= 0.35 * smoothstep(-0.2, 0.3, rkS) * uLandAB.y;
  }
  // (the macro layer's beds less still: thresholded on the 40-50 deg slopes they drew parallel strokes, a2_fA / fE)
  // (p2: none of the macro layer at all from ~0.3 m per pixel (was 0.25 of it): its beds, projected onto the 30-55 deg
  // slopes, still decided the snow edge wherever the outcrop field sat near its threshold - parallel strokes, p2a_fE)
  Ho = (Ho - (A1.a - 0.5) * 0.7 * f1 * farB) * (1.0 - 0.6 * farB);
  // (as the relief fades the bands widen: ~40% rock on the 30-50 deg slopes at 1-3 km, refs 5 / 8 / 4)
  // (the baked outcrop relief about half from ~0.2 m per pixel: its 1.6 m terraces thresholded into fine contour
  // stripes over the 40-50 deg slopes of the near field seen from 300-600 m, a3 / a4_fA)
  float R = Ho + 0.30 * (rkS + 0.3 * (1.0 - texF) * (1.0 - 0.5 * gentle)) * (1.0 + 0.8 * (1.0 - texF)) + 0.45 * strat * farB
          - 0.08 * rk * farB + 0.6 * wob;
  // (m8: near (< 0.13 m per pixel) a little more rock breaks through: the hero slopes round the strut feet are ~50%
  // rock in refs 7 / 4 / 11, ours were ~35%)
  float depth = mix(0.20, -0.08, smoothstep(0.92, 0.66, nS.y)) + 0.07 * farB * smoothstep(0.5, 0.7, nS.y) - 0.035 * (1.0 - farB);
  float hw = max(fwidth(R) * 0.6, 0.006) + 0.35 * sdO;
  float outc = max(blk, smoothstep(depth - hw, depth + hw, R));
  // (r9) rock breaking through the open snow fields seen from ~0.15-4 km (refs 2 / 7 / 4 / 11: the gentle snow carries a
  // scatter of dark rock tips and scree, dense on the wind-scoured crests and knolls and on the steeper rolls, none in
  // the drifted hollows; ours were smooth white plastic domes with a clean bright crest line, L* sd ~4): ~10 m and ~4 m
  // pieces in ~150 m clusters. Each octave fades to its mean before it falls below ~3 px, and the edge widens by the
  // variance it leaves (the cover turns fractional instead of thresholding its mean: no shimmer). (Edge width from
  // the noise's own slope: no screen derivatives inside the branch)
  // (on every level, by distance: most of the film's smooth domes lie 3-6 km out, on L2's edge and the mid level LM,
  // where the near shading still weighs > 50%; gone as the far look takes over by ~8 km)
  // (p2: fades out 5-7.5 km, was 6-9 km: frame budget)
  // (p2: past ~5 km the pieces shrink away (threshold raised) instead of fading to grey (uLandAB5.y); uLandAB5.z: they
  // start only from ~0.2 m per pixel, off the hero pinnacles)
  float spotFar = smoothstep(5000.0, 7500.0, dist);
  float spotW = mix(smoothstep(0.1, 0.2, fp), smoothstep(0.2, 0.35, fp), uLandAB5.z) * cover * uTexOn
              * (1.0 - spotFar * (1.0 - uLandAB5.y)) * step(dist, 7500.0) * uLandAB4.w;
  float spotC = 0.0;
  if (spotW > 0.0) {
    float zone = vnoise3(vPos / vec3(150.0, 90.0, 150.0) + 3.3);
    float a0 = 1.0 - smoothstep(3.5, 8.0, fp), a1 = 1.0 - smoothstep(1.2, 3.0, fp), a2 = 1.0 - smoothstep(0.45, 1.1, fp);
    // (~28 m groups, ~10 m and ~4 m pieces, a little longer up and down: on the slopes they run down the fall line)
    // (each octave only while it is resolved: no screen derivatives here, so the branches are safe)
    float sp = 0.0;
    if (a0 > 0.0) sp += 0.5 * gnoise3(vPos / vec3(28.0, 40.0, 28.0) + 2.2) * a0;
    if (a1 > 0.0) sp += 0.4 * gnoise3(vPos / vec3(10.0, 15.0, 10.0) + 4.4) * a1;
    if (a2 > 0.0) sp += 0.25 * gnoise3(vPos / vec3(3.9, 5.5, 3.9) + 1.1) * a2;
    float dens = 0.75 * crest + 0.3 * smoothstep(0.95, 0.72, nS.y) + 0.6 * (zone - 0.5) - 0.8 * hollow - 1.0 * clamp(curv, -0.5, 0.5);
    float th = 0.26 - 0.5 * dens;
    float sw = max(fp * (0.06 * a0 + 0.14 * a1 + 0.22 * a2), 0.012) + 0.55 * length(vec3(0.5 * (1.0 - a0), 0.4 * (1.0 - a1), 0.25 * (1.0 - a2)));
    // (p2) p1 critique 1: the edge widened by the faded octaves' variance turned the cover fractional - a soft grey
    // camouflage mottle spread evenly over the domes, not rock. Now hard-edged pieces (~1-2 px edges; a faded octave
    // only shrinks the pieces, smoothly over many frames) set in lines along the crests and wind lips (crest) and the
    // fall-line ribs (rib), the gentle snow between them clean (refs 2 / 7: dark blocks along the ribs, clean snow)
    float densN = 1.15 * crest + 0.25 * smoothstep(0.95, 0.72, nS.y) + 0.25 * (zone - 0.5) + 0.7 * (rib - 0.68)
                - 1.0 * hollow - 1.0 * clamp(curv, -0.5, 0.5);
    // (floored: on the knife ridges the crest would be one solid dark line; there rock teeth with snow gaps)
    float thN = max(0.30 - 0.6 * densN, uLandAB4.y);
    float swN = max(fp * (0.06 * a0 + 0.14 * a1 + 0.22 * a2), 0.012) + 0.06 * length(vec3(0.5 * (1.0 - a0), 0.4 * (1.0 - a1), 0.25 * (1.0 - a2)));
    th = mix(th, thN, uLandAB2.w) + 0.7 * spotFar * uLandAB5.y; sw = mix(sw, swN, uLandAB2.w);
    spotC = smoothstep(th - sw, th + sw, sp) * spotW;
    outc = max(outc, spotC);
    spotC *= uLandAB2.w;
  }
  // 3. ledges: solid snow on every up-facing step of the macro / mid relief (block caps, ledges on the sheer faces;
  // the blocks tilt harder for this test than for the shading: a bare rock front under each cap); the test
  // amplifies the relief (mipmapped normal maps flatten the small ledges); on the sheer faces the ledges are broken
  // into runs, and some stretches of wall are wind-scoured
  // (p2: on the vertex normal (n0v) where the facet override steepened a sheer facet: the hero pinnacles keep the
  // snow plastered on their ledges and rims (p1 critique 4), the clusters below still break it into patches)
  vec3 nbA = normalize(mix(n0, n0v, uLandAB.x) + 2.5 * dome + 2.4 * gL);
  float scour = smoothstep(0.3, 0.7, vnoise3(vPos / vec3(28.0, 20.0, 28.0) + 8.0));
  // (m9: the sheer faces' bonus 0.08, was 0.15: ~half the ledge snow on the walls - real dolomite walls hold snow on
  // the bigger ledges and in the cracks, not on every step)
  float lt = nbA.y + 0.12 * H + 0.2 * curv + wob - steepF * (0.10 * smoothstep(0.3, 0.7, vnoise3(vPos / vec3(5.0, 2.0, 5.0) + 2.3)) + 0.05 * scour - 0.08);
  float lw = max(fwidth(lt) * 0.7, 0.012) + 0.8 * sdU;
  // (on the slope blocks only the truly up-facing tops are capped: a lower bar left just a rock rim round each
  // snow-covered block - crazy paving - instead of a rock front under a cap)
  // (p2: on the sheer walls only the truly up-facing ledges, n.y > ~0.75 (was 0.55))
  float lthr = 0.55 + 0.2 * blk * gentle + uLandTune2.z * steepF;
  float ledge = smoothstep(lthr - lw, lthr + lw, lt) * step(1e-3, texF);
  // (m9) on the sheer faces the ledge snow comes in patches (~20-40 m: drifted-in ledge systems beside wind-stripped
  // rock): an even snow line on every bed drew fine zebra stripes over the walls seen from 50-600 m (a3_fA / fF)
  // (p2: clustered at two sizes with uneven spacing (~5-40 m), on ~a quarter of the wall: at most ~5% of a sheer wall
  // holds snow, refs 7 / 4)
  float lclu = smoothstep(0.42, 0.7, vnoise3(vPos / vec3(36.0, 17.0, 36.0) + 4.1)) * smoothstep(0.3, 0.6, mix(vnoise3(vPos / vec3(9.0, 6.0, 9.0) + 1.3), 0.5, smoothstep(0.5, 1.2, fp)));
  ledge *= mix(1.0, lclu, steepF) * mix(1.0, uLandAB.z, farB);
  float snow = max(cover * (1.0 - outc), ledge);
  // far terrain: smoother transitions (sub-pixel features average out)
  float farF = smoothstep(3000.0, 20000.0, dist);
  snow = mix(snow, farSnow(vPos, n0, curv), farF);   // glsl/far.js
  snow *= altMask;

  // ---- conifer forest (m9): stands below a ragged tree line (~1550-1800 m) on slopes up to ~50 deg, broken by
  // clearings (~60-300 m), avalanche gullies (baked concavity) and the open fields of the valley floor (dark navy at
  // twilight). Drawn as single crowns while a crown spans more than ~3 px (the slopes ~0.2-2 km out), else as their
  // mean cover, which closes to a dark canopy at grazing views (the trees hide the snow between them)
  float forestN = fbm2(vPos.xz / 220.0 + 3.0, 4);
  float clearN = mix(fbm2(vPos.xz / 75.0 + 17.0, 3), 0.47, smoothstep(5.0, 14.0, fp));
  float stand = smoothstep(1800.0, 1520.0, alt + 260.0 * (forestN - 0.47) + 90.0 * (clearN - 0.47))
              * smoothstep(0.50, 0.68, n0.y - 0.12 * curv);
  stand *= smoothstep(0.30, 0.42, forestN + 0.3 * (clearN - 0.47)) * (1.0 - smoothstep(0.93, 0.985, n0.y) * smoothstep(1000.0, 700.0, alt));
  float forest = 0.0;          // canopy cover of the pixel
  vec4 tc = vec4(0.0, 0.0, 0.0, 0.5);
  float tRes = 0.0;            // share of single resolved crowns (shading normal)
  vec2 vh = vec2(1.0, 0.0);
  float clump = 0.5;
  if (stand > 0.002) {
    vec3 vdir = (vPos - cameraPosition) / max(dist, 1e-3);
    float mu = clamp(-dot(vdir, nS), 0.06, 1.0);
    float cotE = sqrt(1.0 - mu * mu) / mu;
    // (p2) the stand grows in clumps (groups of ~5-30 trees, ~20-60 m) with gaps of open snow between them, denser
    // lower down: single cones evenly spaced on bare snow read as game props (p1 critique 7), and the closed canopy
    // as a flat black blanket from 1-3 km (critique 2). Far, its mean (the canopy grain fades before ~4 px)
    float cl = 0.65 * fbm2(vPos.xz / 48.0 + 11.0, 3) + 0.35 * vnoise2(vPos.xz / 17.0 + 3.3);
    // (far: stands and thinned patches of ~150-600 m, so the slopes 3-10 km out keep a grain; their mean from ~16 m
    // per pixel)
    float clF = mix(smoothstep(0.22, 0.62, fbm2(vPos.xz / 160.0 + 5.0, 3)), 0.55, smoothstep(16.0, 40.0, fp));
    clump = mix(smoothstep(0.3, 0.52, cl + 0.12 * smoothstep(1600.0, 1100.0, alt)), 0.2 + 0.8 * clF, smoothstep(2.0, 5.0, fp));
    // (p2: no lone trees where the stand is thin - near the tree line ~20% of the cells held one evenly spaced crown,
    // which seen from 0.3-1 km drew the parallel 'pen hatching' over the 1600-1800 m slopes, p2b_fE / fA; the stand
    // there now thins out in clumps)
    float sd = clamp((stand * clump - 0.12) * 1.6, 0.0, 1.0);
    // mean cover: crowns ~3 m in radius, ~12 m of dense crown, one per 6.5 m cell at full density (~50% from above,
    // ~85% at 45 deg, closed at grazing views)
    float covM = 1.0 - exp(-sd * (0.72 + 1.0 * cotE));
    float lsF = 12.0 * cotE / TREE_C;
    float tLod = max(smoothstep(0.10, 0.22, fp / TREE_C), smoothstep(1.1, 1.6, lsF));
    forest = covM;
    if (tLod < 0.999) {
      vh = vdir.xz / max(length(vdir.xz), 1e-4);
      tc = treeCrowns(vPos.xz / TREE_C, vh, min(lsF, 1.6), sd, max(0.7 * fp / TREE_C, 0.02));
      tRes = 1.0 - tLod;
      forest = mix(tc.x, covM, tLod);
    }
  }

  // ---- dolomite albedo: the photos' light / dark structure (contrast-boosted, hue mostly removed) on a cool grey
  // base (shadowed rock lands #10131e..#1a1c28, mid #3a3f55, lit faces up to #4c516c; warmth only from the glow /
  // lamp light); cracks and cavities from the height and AO maps at full darkness
  // (the macro photo's tone only half, and less where it is magnified (rock within ~10 m): stretched over 30-60 m
  // its light / dark patches read as marbling / blurred mottling up close)
  float mag1 = smoothstep(0.012, 0.03, fp);
  // (p2: the macro photo's gently dipping beds half as strong on the sheer facets (ovr): horizontal smear over the
  // block faces, p1 critique 5 - their vertical joints are drawn below)
  vec3 tx = mix(vec3(1.0), A1.rgb / 0.18, 0.55 * f1 * mix(0.4, 1.0, mag1) * (1.0 - 0.5 * ovr)) * mix(vec3(1.0), A2.rgb / 0.18, 0.8 * f2)
          * mix(vec3(1.0), A3.rgb / 0.18, 0.7 * f3) * mix(vec3(1.0), A4.rgb / 0.18, 0.6 * f4);
  tx = clamp(mix(vec3(lum3(tx)), tx, 0.2), 0.03, 6.0);
  // (near by a lighter grey: the key below models it, lit faces grey beside the snow (ref lit rock / snow ~0.3-0.4 in
  // linear light), shadow faces stay deep under a weaker fill; farther out the darker tone that the dome light
  // alone gives)
  // (m8b: near base neutral (was a cool 0.315 / 0.33 / 0.365): the lit faces take the warm key below and read
  // dolomite taupe (refs 7 / 4 / 11 / 2 lit rock ~#7a6458), the shadow sides go navy by the blue dome alone)
  vec3 rock = srgb2lin(mix(vec3(0.30, 0.31, 0.33), vec3(0.325, 0.315, 0.315), nearF)) * pow(tx, vec3(1.6));
  // recesses of the relief and the baked gullies / chimneys sink to near black (refs: p5 ~#0b0e18)
  rock *= mix(1.0, smoothstep(-0.40, 0.14, H), 0.92 * texF) * (1.0 - 0.5 * max(curv, 0.0));
  // the joints between blocks: dark cracks
  rock *= 1.0 - 0.6 * pres * (1.0 - blkIn) * fB;
  // large-scale tone (a little variation between faces, no blotches)
  rock *= 0.88 + 0.24 * vnoise3(vPos / 37.0);
  // (p2) the sheer facets (WNW block, t 11; the spires): vertical joints every ~2-6 m and pillar tone (ref 4 wall:
  // vertical joints and pillars, gy/gx ~0.9; ours a horizontally smeared box, gy/gx 1.66). Ridged noise stretched 1:4
  // up the wall; the fine joints fade before they fall below ~8 px, the wide ones before ~6 px
  if (ovr > 0.01 && texF > 0.0 && uLandAB4.w > 0.5) {
    float jf1 = 1.0 - smoothstep(0.08, 0.22, fp), jf2 = 1.0 - smoothstep(0.25, 0.6, fp);
    float jn = jf1 > 0.0 ? 1.0 - abs(gnoise3(vPos / vec3(2.4, 9.5, 2.4) + 4.7)) : 0.5;
    float jw = jf2 > 0.0 ? 1.0 - abs(gnoise3(vPos / vec3(6.0, 24.0, 6.0) + 1.3)) : 0.5;
    float pil = 0.8 + 0.4 * vnoise3(vPos / vec3(4.0, 28.0, 4.0) + 6.2);
    rock *= mix(1.0, pil * (1.0 - 0.7 * smoothstep(0.84, 0.96, jn) * jf1) * (1.0 - 0.55 * smoothstep(0.82, 0.95, jw) * jf2), ovr * texF);
  }
  // (p2) the rock pieces breaking through the snow fields: rough, self-shadowed - near black against the snow (ref 2:
  // rock p5 L* 3-10 beside snow p50 38)
  rock *= 1.0 - uLandAB4.z * spotC;
  // snow: sky-lit blue (B > R, G > R), deeper blue in the concave couloirs
  vec3 snowA = vec3(0.58, 0.78, 1.0) * mix(vec3(1.0), vec3(0.88, 0.93, 1.03), max(curv, 0.0));
  // snow relief: soft wind ripples (two scales), the snow drapes the macro relief
  vec3 gs = vec3(0.0);
  float snowAO = 1.0;
  float fs1 = texF * scaleFade(5.0, fp), fs2 = texF * scaleFade(1.6, fp);
  if (fs1 > 0.0 && snow > 0.001) {
    vec3 ga; vec4 s1 = triSnow(vPos, 5.0, 0.7, ga);
    gs += ga * 0.55 * fs1;
    snowAO *= mix(1.0, s1.w, 0.5 * fs1);
    if (fs2 > 0.0) { vec3 gb; vec4 s2 = triSnow(vPos + 3.1, 1.6, 2.3, gb); gs += gb * 0.35 * fs2; snowAO *= mix(1.0, s2.w, 0.4 * fs2); }
  }
  // (r9) the hollows and drift-filled gullies of the snow fields see less of the sky: a large-scale shade that models
  // the domes and ridges 0.3-4 km out (their snow was one flat fill)
  snowAO *= 1.0 - 0.2 * hollow * smoothstep(0.1, 0.3, fp);
  // (p2) the lee band below the crests and wind lips (the slopes turned downwind, ENE, within ~50 m of a crest: cornice
  // shade and drifted lee snow, p1 critique 3 - the crests read as one bright ribbon)
  float leeC = smoothstep(0.5, 4.0, cvx.y) * smoothstep(0.05, 0.35, dot(nS.xz, vec2(0.92, -0.38)));
  snowAO *= 1.0 - 0.25 * leeC * uLandAB3.w * smoothstep(0.1, 0.3, fp);
  // (m9) wind-drift relief on the open snow (drifts, wind lips and scoured hollows 12-50 m across, ~2.5x longer down
  // the WSW wind): from ~50 m to 3 km out the snow was one smooth lavender sheet between the outcrops (base_fA / fB /
  // fE). Value noise with its analytic gradient (far.js farVN, world-fixed); each octave fades to flat before it
  // falls below ~4 px (no crawl in the film)
  // (p2: five octaves 100 m .. 6 m (was 50 .. 12.5 m), each ~1.3x steeper: the big snow domes seen from 0.3-1.5 km were
  // still smooth plastic (p1 critique 1: local L* sd 3-6, refs 11-19); the 6 m octave breaks the FPV passes' facets)
  // (r9: each octave in its own wind frame (+-20 deg about the WSW wind), ~1.7x longer along it (was 2.5x for all):
  // one stretched frame for every octave drew the 'pen hatching' - parallel strokes of one direction and length over
  // the 30-55 deg slopes seen from 0.3-1 km (out/report_r8_valley.md); and rougher on the wind-scoured crests,
  // smoother in the drift-filled hollows)
  if (snow > 0.001 && uTexOn > 0.5) {
    float dAmp = uLandTune2.x * (1.0 + 0.6 * crest - 0.4 * hollow) * uLandAB2.z;
    for (int k = 0; k < 5; k++) {
      float L = 100.0 / exp2(float(k));
      float w = 1.0 - smoothstep(L / 10.0, L / 4.0, fp);
      if (w <= 0.0) continue;
      float ang = 0.35 + 0.35 * sin(float(k) * 2.4);
      vec2 wa = vec2(cos(ang), sin(ang)), wc = vec2(-wa.y, wa.x);
      vec2 q = vec2(dot(vPos.xz, wa), dot(vPos.xz, wc));
      vec2 sc2 = vec2(1.0 / (1.7 * L), 1.0 / L);
      vec3 nv = farVN(q * sc2 + float(k) * 7.13 + 1.3);
      vec2 gq = nv.yz * sc2 * (dAmp * L) * w;
      gs.xz -= wa * gq.x + wc * gq.y;
    }
  }
  // (m8b: from ~0.15 m per pixel on (the view 2 peaks) a greyer, lavender snow: ref 2 snow #666b8d..#707497 (b* -11..
  // -17), ours was periwinkle #5f72b0 (b* -37))
  // (hero slopes ~0.09 m per pixel, the view 2 peaks / view 8 walls 0.15-0.25)
  float farB2 = smoothstep(0.11, 0.2, fp);
  // (m9: (0.62, 0.69, 0.80), was (0.70, 0.68, 0.76): the free-flight slopes 0.2-3 km out read pink-lavender, R ~ G
  // (#66648c); the refs' snow is steel blue, G > R (#3a425d .. #666b8d))
  // (p2: (0.66, 0.71, 0.80): the shaded snow read periwinkle, b* -36 (refs -18 .. -28); the glow light below warms the
  // faces turned to the sunset)
  // (p2: (0.66, 0.70, 0.75): the domes' snow still read too blue, b* ~-29 against ref 2's ~-24)
  snowA = mix(snowA, mix(vec3(0.66, 0.71, 0.80), vec3(0.66, 0.70, 0.75), uLandAB3.z), 0.85 * farB2);
  // (p2) wind crust and fresh powder: +-10% albedo in patches ~25-90 m, world-fixed (the 23 m octave fades before it
  // falls below ~4 px)
  if (snow > 0.001) {
    float crust = 0.6 * vnoise3(vPos / vec3(90.0, 40.0, 90.0) + 5.5) + 0.4 * mix(vnoise3(vPos / 23.0 + 9.1), 0.5, smoothstep(2.3, 6.0, fp));
    snowA *= 1.0 + uLandTune2.w * (crust - 0.5);
    // (r9) the scoured crests a greyer wind crust, the hollows' deep drifted snow a little whiter
    snowA *= 1.0 - (0.14 * crest - 0.05 * hollow) * farB;
  }
  // (and a lighter rock there: ref 2's buttresses are lavender-taupe, L* p90 41-50)
  // (m9: on the big steep faces only - see the rock key below; the small outcrops / blocks on the snow slopes seen from
  // 0.2-3 km are darker instead (rough, self-shadowed pieces: grey-black against the snow; they read as tan flecks))
  // (a2: from ~55 deg, was ~40: the 40-50 deg snow slopes' outcrops still took the warm 1.6x key - tan strokes)
  float bigF = 1.0 - smoothstep(0.35, 0.6, nS.y);
  rock *= (1.0 + 0.3 * farB2 * bigF) * (1.0 - 0.45 * farB2 * (1.0 - bigF));
  snowA = mix(snowA, farSnowAlbedo(vPos), farF);
  rock = mix(rock, farRockAlbedo(vPos, n0), farF);
  vec3 alb = mix(rock, snowA, snow);
  // valley floor (meadows / fields under thin snow)
  alb = mix(alb, srgb2lin(vec3(0.30, 0.31, 0.33)), smoothstep(1000.0, 750.0, alt) * smoothstep(0.85, 0.97, n0.y));
  // forest: near-black spruce crowns lightly dusted with snow (more toward the tips and higher up) over the ground of
  // the stand (snow or meadow) in their shade (m9: the old flat stand albedo carried 10-22% open snow - the valley
  // slopes read ~4x too bright, report_r5_lights)
  // (p2: crowns a little lighter and more snow-loaded toward the tops, the load varying from clump to clump; the
  // ground of the gaps less shaded: median slope L* 12 against the refs' 18-28, critique 2)
  // (the load varies by clump near by, by stand (~190 m) farther out: the slopes 1-8 km out keep a grain)
  float load = (0.09 + 0.09 * altMask) * (0.5 + 1.0 * mix(vnoise2(vPos.xz / 31.0 + 7.7), vnoise2(vPos.xz / 190.0 + 2.1), smoothstep(3.0, 8.0, fp)));
  vec3 crownA = mix(srgb2lin(vec3(0.062, 0.08, 0.084)) * uLandTune2.y, snowA, load * (1.0 + tRes * (2.2 * tc.y - 0.8)));
  alb = mix(alb * (1.0 - 0.35 * stand * clump), crownA, forest);

  // shading normal: rock carries the full relief; snow drapes the macro / mid relief with its own ripples (and the
  // rounded caps on the blocks)
  vec3 gSn = g1 * (0.5 * f1) + g2 * (0.25 * f2) + gs;
  gSn -= n0 * dot(gSn, n0);
  // (the open snow follows the ~5 m surface half-way: the 1.6 m grid's facets showed in the smooth snow)
  // (p2: the ~5 m normal weighs 2:1 over the vertex normal (was 1:1): seen from 20-40 m the snow showed the mesh's
  // triangles as flat facets, p1_fN / fO)
  vec3 nSn = normalize(normalize(0.5 * n0 + nS) + gSn + 0.6 * dome * blkIn);
  vec3 n = normalize(mix(nb, nSn, snow));
  float ao = mix(aoT, snowAO, snow);
  // resolved crowns: a cone's normal (across the crown, up, toward the camera; the key lights one flank of each tree),
  // darker toward the crown's base
  if (tRes > 0.0) {
    vec3 nC = normalize(vec3(-vh.y, 0.0, vh.x) * (0.9 * clamp(tc.z, -1.0, 1.0)) + vec3(0.0, 0.55, 0.0) - vec3(vh.x, 0.0, vh.y) * 0.4);
    n = normalize(mix(n, nC, forest * tRes));
    ao *= mix(1.0, 0.55 + 0.45 * tc.y, forest * tRes);
  }

  // ---- relief shadows from the key: probe the macro + mid relief (in metres) toward the light at 1.5 and 5 m; the
  // pillars and blocks cast soft shadows into the cracks and onto the snow at their feet (skipped on open snow)
  float kn = dot(n0, KEY);
  vec3 Kt = KEY - n0 * kn;
  float ktl = length(Kt);
  float shadowK = 1.0;
  float foot = pres * (1.0 - blkIn) * fB * smoothstep(0.0, 0.12, be);
  if (f2 > 0.0 && kn > -0.2 && ktl > 1e-3 && dist < 1500.0 && (snow < 0.999 || foot > 0.0)) {
    Kt /= ktl;
    float tanE = kn / ktl;
    float h0 = (A1.a - 0.5) * L1_M * f1 + (A2.a - 0.5) * L2_M * f2;
    float occ = 0.0;
    for (int i = 0; i < 2; i++) {
      float s = i == 0 ? 1.5 : 5.0;
      vec3 q = Kt * s;
      float hs = (f1 > 0.0 ? (triH(tRockA, tRockB, p1 + q, L1_SC, L1_SH, L1_RV, L1_RH) - 0.5) * L1_M * f1 : 0.0)
               + (triH(tRockB, tRockB, p2 + q, L2_SC, L2_SC.x, L2_RV, L2_RH) - 0.5) * L2_M * f2;
      occ = max(occ, smoothstep(0.0, 0.25 + 0.12 * s, hs - h0 - s * tanE));
    }
    shadowK = 1.0 - 0.85 * occ * f2;
  }
  // snow at the feet of the blocks in their lee (the side away from the key): a soft shade fading out across the
  // joint (an all-round ring outlined every cell: a giraffe pattern)
  float rl = length(rW);
  float lee = rl > 1e-3 ? smoothstep(0.0, 0.6, dot(-rW / rl, KEY)) : 0.0;
  ao *= 1.0 - 0.35 * lee * foot * snow;

  // (the dome fill weaker on bare rock near by, and bluer: its shadow sides go deep blue-black (refs #10131e..
  // #181924), the key models it)
  float bareN = (1.0 - snow) * (1.0 - forest) * nearF;
  // (m8: 0.2x the dome on bare near rock (was 0.38x): its shadow sides and crevices land near black, refs p5 ~#090c17)
  // (m8b: the cut eases off with the pixel footprint (0.8 at the hero slopes' ~0.1 m per pixel, 0.15 from ~0.2 m:
  // the view 2 peaks, the view 8 walls): there whole faces turned from the key went black, refs 2 / 8 show them
  // as mid-dark taupe; only the near crevices sink to black. Tint indigo near (the refs' darkest rock #0c0f1a,
  // a* > 0), less blue at the view 2 distance (ref 2 shaded rock lavender-grey))
  // (m9: tint (0.82, 0.95, 1.4), was (0.86, 0.92, 1.5): under the grade's red white balance the shaded walls of the FPV
  // passes read purple-brown (#23202a, a2_fF); ref 7's walls are a neutral blue-grey #373847)
  // (p2: 0.62, was 0.8: the FPV cliff (p1_fF) had a median L* 7, 44% of it near black; ref 7's pinnacle rock median
  // L* 28, its shaded faces mid blue-grey - the relief AO and cracks still sink to black)
  vec3 E = skyIrradiance(n, skyVis * ao, glowVis) * (1.0 - mix(uLandTune.z, 0.15, farB2) * bareN) * mix(vec3(1.0), vec3(0.82, 0.95, 1.4), bareN * (1.0 - 0.6 * farB2));
  // light bounced off the surrounding snow fields onto steep and overhanging faces (the dome model's
  // ground term assumes a ~0.2 albedo ground; here nearly everything around is snow) - kept low on the rock
  E += skyIrradiance(vec3(0.0, 1.0, 0.0), skyVis * skyVis, 0.0) * mix(0.03, 0.12, snow) * (0.5 - 0.5 * n.y) * nearF * ao;
  // the key: faces turned to camera-left read lit grey / white, the others fall into blue shadow, and the
  // photographic relief shows as light and shade; occluded by the sky visibility, the relief AO and its shadows
  // (a crisp terminator on the ~5 m faces - whole faces turned away from it fall into blue shadow, as in refs 2 / 4
  // - times the soft response of the detailed relief). Cool on the rock (warm only from the glow rim and lamps),
  // sky-blue on the snow.
  // (m8: stronger form shading - the art director wants clearly separated lit and shaded planes: a harder terminator
  // on the relief (rock from n.K 0.05 to 0.6, was -0.2..0.75), a brighter, more neutral key on the rock (lit faces
  // grey beside near-black shadow sides) and a brighter key on the snow (lit snow blue-white, shaded snow mid blue))
  float kd = dot(n, KEY);
  float key = smoothstep(-0.05, 0.4, dot(normalize(nS + 0.5 * n0), KEY)) * mix(smoothstep(0.05, 0.6, kd), smoothstep(-0.05, 0.45, kd), snow);
  key *= skyVis * mix(1.0, skyVis, snow) * ao * shadowK;
  // (r9) from ~2 km on, the ranges' cast shadows along the key (vKey, as far.js's farLight; near, the relief probes)
  key *= mix(1.0, 0.2 + 0.8 * vKey, smoothstep(1500.0, 3500.0, dist));
  // (m8b: the snow's flat 1.25x dome boost -> by slope, a steeper snow terminator: the snow had one flat L* 25-50
  // band in every view; refs: shaded snow p10 ~20, lit snow up to L* 57-61. The rock key warm
  // (lit dolomite taupe, refs ~#7a6458 b* +5; the neutral key read violet-grey))
  // (the key lights the right walls (faces turned to camera-left), the left walls live on the dome: the dome on the
  // snow modelled by slope (steep 0.8x .. up-facing 1.3x) for the spread inside each wall, the key kept moderate)
  // (m9, art director: 'shadows not nearly dark enough, light not bright enough'; free-flight slopes measured L p10 /
  // p50 / p90 79 / 106 / 123 against the refs' 14-21 / 49-69 / 97-109: the dome on the snow 0.6x (steep) .. 1.0x (flat),
  // was 0.8 .. 1.25x, and a ~2x snow key below (r7 critique 3 asked for the same))
  // (r9: on the snow above the cloud sea out to ~7 km on every level (was faded from 600 m, and none on the mid level
  // LM): the snow domes and ridges 1-6 km out had no key and no slope modelling - flat white plastic; gone as the far
  // light takes over by ~8 km)
  float nearK = mix(nearF, max(nearF, (1.0 - smoothstep(5000.0, 9000.0, dist)) * smoothstep(1650.0, 1950.0, alt)), snow);
  E *= 1.0 + snow * nearK * mix(-0.4, 0.0, smoothstep(0.25, 0.85, n.y));
  // (p2) the far snow fields: dome light vs key (uLandAB3 x / y: lit and shaded facets of the domes >= 12 L* apart)
  float snF = snow * farB2 * (1.0 - farF);
  E *= mix(1.0, uLandAB3.x, snF);
  // (the rock key 1.6x at the view 2 distance: ref 2's lit buttress faces reach L* 41-50, ours 24-30)
  // (m9: only on the big steep faces (the buttresses): the small outcrops on the snow slopes 0.2-3 km out took it
  // too and read as a sprinkle of golden flecks in the free-flight views; there a less saturated key)
  // (m9: (0.60, 0.45, 0.33), was (0.64, 0.47, 0.27): the lit walls read golden-yellow wood in the FPV passes (base_fF);
  // the refs' lit dolomite is a pinker taupe, ~#7a6458 = 1 : 0.64 : 0.5 in linear light)
  // (p2: (0.53, 0.48, 0.43), was (0.60, 0.45, 0.33): the FPV rock read as a brown smear (critique 5); the warmth now
  // comes mostly from the glow light below, on the faces turned to the sunset)
  vec3 rkc = mix(vec3(0.40, 0.40, 0.42), vec3(0.53, 0.48, 0.43) * (1.0 + 0.6 * farB2), max(bigF, 1.0 - farB2));
  E += mix(rkc, vec3(0.25, 0.30, 0.41), max(snow, forest)) * key * nearK * uSkyExposure * mix(1.0, uLandAB3.y, snF);
  // warm rim of the sunset glow on rock edges and faces turned toward it (refs: tan lit faces beside blue snow)
  vec3 shz = normalize(vec3(uSunDir.x, 0.0, uSunDir.z) + vec3(0.0, 0.25, 0.0));
  float rim = max(dot(nb, shz), 0.0);
  // (m8b: 0.43x - the left walls' rock edges read orange-brown, refs 11 / 4 left rock #64544c..#685248)
  E += vec3(0.065, 0.04, 0.025) * rim * rim * glowVis * skyVis * (1.0 - snow) * (1.0 - forest) * nearF * uSkyExposure;
  // (p2) the glow light: faces turned to the sunset (SSW, ~10 deg up) catch the bright low sky - lavender-peach on the
  // snow, warm grey on the rock - raking, so the drift relief and the outcrops model in it; the faces turned away
  // keep the cool dome light (p1 critique 1: snow had no warm / cool split by orientation; refs 2 / 4: glow-side snow
  // b* ~-8 at L* 60-75, shaded snow b* -18 .. -28). Above the cloud sea only (below it the deck hides the glow)
  vec3 gdir = normalize(vec3(uSunDir.x, 0.0, uSunDir.z) + vec3(0.0, 0.2, 0.0));
  float gli = smoothstep(0.0, 0.75, dot(n, gdir)) * smoothstep(-0.15, 0.35, dot(nS, gdir));
  float gW = glowVis * skyVis * (1.0 - farF) * smoothstep(1550.0, 1800.0, alt) * (1.0 - 0.7 * forest) * uSkyExposure;
  E += mix(vec3(0.17, 0.115, 0.08), vec3(0.30, 0.20, 0.16), snow) * gli * gW * uLandTune.x;
  // (m9) under the cloud sea (base ~1.5 km) the deck hides most of the dome: the valley lies in its dim shade (refs:
  // slopes and valley floor #111f3b..#313d5c; ours read about as light as the lake, report_r5_lights)
  // (p2: 0.62x, was 0.4x: the valley slopes were a flat black blanket, L* 12 against the refs' 18-28, critique 2)
  E *= mix(1.0, uLandTune.y, smoothstep(1650.0, 1350.0, alt));
  col = alb * E;
  // (m9) the valley under the cloud sea keeps this shading at every distance (forest / meadows / settlements in the
  // deck's shade); far.js's farLight (tuned for the ranges above the sea) takes over only above ~1.7 km and beyond
  // ~25 km
  float valW = smoothstep(1950.0, 1650.0, alt) * (1.0 - smoothstep(18000.0, 30000.0, dist));
  col = mix(col, farLight(col, alb, n, vPos, snow, skyVis, glowVis), farF * (1.0 - valW));

  // warm lamps of the structure (uplights, bridge abutments): the point falloff plus an amber wash over the rock
  // round each foot (refs 3 / 9 / 7 / 6 / 4: warm pools ~15-30 m across on the faces below the bridge ends; with a
  // 1/d^2 tail the 18 lamps tinted the whole gorge brown, this 1/d^4 one stays local); wrapped, so side faces catch
  // it, and only lightly occluded by the relief AO
  // (m8: the hero views' long lenses frame only ~20-60 m of slope round each strut foot, and the plain 1/d^2 tails
  // of the foot, strut-top and abutment lamps lit all of it: on the blue snow a lavender-pink wash (v11 snow
  // #898092 where ref 11 has #586a93; with the lamps off ours was #42537f). The point light is now windowed to a pool
  // (1 / (1 + (d/R)^4), R 17 m on rock, 9 m on snow), brighter inside it, and a little more golden than the lamp:
  // amber pools at the feet and along the walkway, the blue twilight snow right beyond them)
  for (int i = 0; i < LAMPS_MAX; i++) {
    if (i >= uLampCount) break;
    vec3 L = uLampPos[i].xyz - vPos;
    float d2 = dot(L, L);
    float d = sqrt(d2);
    L /= max(d, 1e-3);
    float nl = dot(n, L);
    // (the pool reaches ~17 m up the bare rock (ref 7: the pillar behind the left strut foot glows ~15-20 m up), only
    // ~9 m over the snow, where a weaker warm light mixes with the blue to pink)
    float win = d2 / mix(290.0, 85.0, snow);
    win = 1.0 / (1.0 + win * win);
    float ws = 1.0 + d2 / 110.0;
    float att = max(nl * 0.85 + 0.15, 0.0) * ao / (d2 + uLampPos[i].w * uLampPos[i].w) * win;
    float wash = (0.6 + 0.4 * nl) * mix(1.0, ao, 0.3) * 0.012 / (ws * ws);
    // (the bare rock round the bridge ends also catches the warm light of the glazed ring and abutments over
    // ~28 m (ref 7 / 4 towers: lit faces neutral-warm grey #44-4c, not blue), the snow beside it stays blue)
    float wb = 1.0 + d2 / 800.0;
    float bnc = max(nl * 0.6 + 0.4, 0.0) * ao * 0.0022 / (wb * wb) * (1.0 - snow) * nearF;
    // (m8b: amber, not pink-beige: refs' pools ~1 : 0.82 : 0.66 at L* 60-80 (#c8a080..#e0b080); ours read 1 : 0.87 :
    // 0.83 - the lamp tint cut in blue, the pool brighter, the wall wash warm)
    col += alb * uLampCol[i].rgb * (vec3(1.0, 0.78, 0.50) * (2.6 * att + 1.4 * wash) + vec3(1.0, 0.84, 0.64) * 1.3 * bnc);
  }

  // town light pollution on valley floors
  vec2 tuv = vPos.xz / uTownGlowSize + 0.5;
  if (all(greaterThan(tuv, vec2(0.0))) && all(lessThan(tuv, vec2(1.0)))) {
    float tg = texture2D(uTownGlow, tuv).r;
    col += alb * srgb2lin(vec3(1.0, 0.62, 0.32)) * tg * 0.25 * smoothstep(1200.0, 300.0, alt);
  }
  // snow sparkle (tiny, near only; m9: only while its 17 cm cells span > ~3 px - smaller, they twinkled from frame
  // to frame in the film)
  if (dist < 250.0 && fp < 0.06) {
    float sp = hash13(floor(vPos * 6.0));
    col += snow * step(0.9985, sp) * 0.4 * (1.0 - dist / 250.0) * (1.0 - smoothstep(0.03, 0.06, fp)) * E;
  }
  return col;
}
`;
