// Volumetric sea of clouds: depth-aware raymarch over a curved slab, twilight sky lighting,
// warm light from towns below and from the ring structure. Near the ring a terrain-hugging layer
// (from the L2 heightfield) sends tongues of cloud up the gorge walls.
import * as THREE from 'three';
import * as COMMON from './glsl/common.js';
import { CLOUDS, DECK_Y, EARTH_R, HERO_AZ } from './config.js';
import { VIEWS, refToWorld } from './views.js';

const { NOISE, ATMOS } = COMMON;
// far-field dip (common.js FARDIP, integrator m5+); no-op fallback for builds without it
const FARDIP = COMMON.FARDIP || /* glsl */ `
#ifndef FAR_DIP_U
#define FAR_DIP_U
uniform float uFarDip;
uniform vec2 uDipWin;
#endif
float farOffC(vec3 p, vec3 cam){ return 0.0; }
`;

const fsVert = /* glsl */ `varying vec2 vUv; void main(){ vUv = uv; gl_Position = vec4(position.xy, 0.0, 1.0); }`;

// cloud-sea layout (coverage / tops / gaps per column), shared by the raymarch and the composite (undercast)
const COLUMN = /* glsl */ `
uniform sampler2D tWeather;
uniform sampler2D tWin;      // heavily blurred town map: opens windows over the lake shores
uniform float uTownSize;
uniform float uBase, uTop;
uniform float uCovBias, uCovScale, uWin;
uniform vec3 uRingC;
uniform float uEarthR;
uniform vec4 uGapSeg;        // broken region: capsule from xz (P0) to zw (P1), world metres
uniform vec3 uGapW;          // half width at P0 (m), widening per metre along, mean island coverage inside
uniform vec4 uGapSeg2;       // second capsule along the lake
uniform vec2 uGapW2;
uniform vec2 uHeroDir;      // world xz unit vector of the hero line of sight (ring -> lake)
uniform sampler2D tSight;    // line-of-sight windows onto the lakeshore towns (sightTex)
uniform float uSightSize, uSightW, uHole, uWell;
uniform vec2 uWindDir;       // xz unit vector: fibres, banks and the far sea are stretched along it
uniform sampler2D tTerr;     // L2 heightfield (m)
uniform float uTerrSize;
uniform float uTerrCov;      // (r8 p2) coverage drop over ground that rises into the layer

float altOf(vec3 p){ return p.y + dot(p.xz, p.xz) / (2.0 * uEarthR); }
float sat(float x){ return clamp(x, 0.0, 1.0); }
// Broken region over Lake Brienz and the slope between the ring and the lake (the hero line of sight
// crosses the layer 1-6 km out). Domain-warped capsule so the edge is ragged; returns 0..1.
float capsule(vec2 q, vec4 seg, float w0, float grow){
  vec2 a = seg.xy, ab = seg.zw - seg.xy;
  float L = length(ab);
  float s = dot(q - a, ab) / (L * L);
  float h = clamp(s, 0.0, 1.0);
  float d = length(q - a - ab * h);
  float hw = w0 + grow * h * L;
  // close softly beyond both ends
  return (1.0 - smoothstep(hw * 0.45, hw, d)) * smoothstep(-200.0, 300.0, s * L) * smoothstep(1.15, 0.95, s);
}
float gapField(vec2 xz){
  vec4 w = texture2D(tWeather, xz / 11000.0 + vec2(0.17, 0.83));
  vec4 w2 = texture2D(tWeather, xz / 3100.0 + vec2(0.57, 0.39));
  // the big warp only far out: near the ring the gap must stay on the hero line of sight
  float wk = mix(0.3, 1.0, smoothstep(1500.0, 5000.0, length(xz - uRingC.xz)));
  vec2 q = xz + (w.gb - 0.5) * 2200.0 * wk + (w2.gb - 0.5) * 700.0;
  // A: where the hero line of sight crosses the layer; B: over the lake itself and its shore towns
  return max(capsule(q, uGapSeg, uGapW.x, uGapW.y), capsule(q, uGapSeg2, uGapW2.x, uGapW2.y));
}

// weight of the low near layer: 0.45-1 km from the ring, within ~30-50 deg of the hero azimuth (the walls
// beside it keep the full sea, piled against the slopes)
float nearW(vec2 xz, float rr){
  vec2 d = xz - uRingC.xz;
  return smoothstep(1000.0, 450.0, rr) * smoothstep(0.62, 0.88, dot(d, uHeroDir) / max(length(d), 1.0));
}

// Hole down the gorge axis: the long-lens hero cameras (views 7/11/6/5, far-field dip) see the lake band just
// under the ring along lines of sight that cross the layer ~0.6-1.3 km out on the gorge axis (+-12-17 deg; the
// lake itself is 4-7 km out, below the base); beside it they end on the valley walls, which keep their cloud.
// Lines of sight through the ring void cross the layer 4-10 km out: there the sea stays (billows over the lake).
float heroGap(vec2 xz, float rr, float n){
  vec2 d = xz - uRingC.xz;
  float c = dot(d, uHeroDir) / max(length(d), 1.0);
  return smoothstep(0.957, 0.983, c + n * 0.025) * smoothstep(560.0, 700.0, rr) * smoothstep(1400.0, 1080.0, rr);
}

float gBankC = 0.0;   // out (column): weight of the flat bank under the deck
float gTopB = 0.0;    // out (column): top altitude averaged over ~0.3 km around (the walls of a trough between heaps)
float gLane = 0.0, gHRay = 0.0;   // out (column): sight-window lane strength and sight-line altitude (the bake)

// column: x coverage, y top altitude (before the 3D lumps), z sight window (floor: altitude of the sight line,
// fract: lane strength), w gap (0..1)
vec4 column(vec2 xz){
  vec4 a = texture2D(tWeather, xz / 30000.0 + vec2(0.31, 0.62));
  vec4 b = texture2D(tWeather, xz / 6000.0 + vec2(0.71, 0.13));
  vec4 f = texture2D(tWeather, xz / 1900.0 + vec2(0.43, 0.27));
  vec4 m = texture2D(tWeather, xz / 800.0 + vec2(0.19, 0.58));
  // (r5 p2) the bank fields stretched x2.2 along the wind (az ~110, across the hero line of sight): banks and lanes
  // that read as layered decks, not an isotropic carpet; a fixed stretch (one that varied with distance sheared the
  // extruded layout into streaks)
  vec2 wn = vec2(-uWindDir.y, uWindDir.x);
  vec2 xa = uWindDir * dot(xz, uWindDir) / 2.2 + wn * dot(xz, wn);
  vec4 bA = texture2D(tWeather, xa / 6000.0 + vec2(0.71, 0.13));
  vec4 fA = texture2D(tWeather, xa / 1900.0 + vec2(0.43, 0.27));
  // radial zones around the ring (hero line of sight): under the deck (< ~0.4 km) a flat bank fills the slot
  // (seen through the ring void with wells in it; the frame bottoms of the hero views); 0.55-2.2 km along the
  // gorge axis a clean hole (just under the ring in the hero views); 0.45-1 km beside it a low layer; beyond
  // ~0.8 km the broken region (islands) where the lake shows through
  float rr = length(xz - uRingC.xz) + (f.g - 0.5) * 300.0;
  // (round 4's clean hole down the gorge axis, uHole: closed since round 5 - the sea covers most of the view under
  // the ring, and the hero cameras see the lake and its towns through 2-3 ragged line-of-sight windows instead)
  float ho = heroGap(xz, rr, m.g + f.r - 1.0) * uHole;
  // line-of-sight windows (sightTex): densityC carves a ~+-80 m tube around the hero line of sight to the lights
  // (lowering the whole lane made radial trenches: dark vertical slots down the frame); lane strength and the sight
  // line's altitude are packed into .z
  vec2 sw = texture2D(tSight, xz / uSightSize + 0.5).rg;
  float lane = smoothstep(0.25, 0.55, sw.x + (m.g - 0.5) * 0.35 + (f.r - 0.48) * 0.25) * uSightW;
  float g = max(gapField(xz) * smoothstep(650.0, 900.0, rr), ho);
  float nr = nearW(xz, rr);
  // the bank: a flat layer with a ragged front ~0.35-0.7 km out that slopes down into the sea (frame bottoms of the hero views)
  float r0 = length(xz - uRingC.xz);
  // (the 2D layout has no features below ~100 m: extruded over the layer's height they showed as vertical streaks;
  // the small scales are 3D: lumps and erosion in densityC)
  // (r5: a wide front ramp 0.33-0.7 km: its top slopes down into the sea; the 150 m ramp stood as a cliff of cloud with
  // vertical streaks down its face at the frame bottoms)
  float nb = smoothstep(700.0, 330.0, r0 + (f.b - 0.5) * 160.0 + (f.g - 0.5) * 100.0);
  // far from the ring the sea is calmer and more continuous (fewer troughs between the 6 km heap fields)
  float fz = smoothstep(3500.0, 10000.0, rr);
  // (r5 p2: ~1.4x the contrast of the bank fields: coverage is mostly clearly in or out - banks with lanes between
  // them; near the 0.28 threshold everywhere, the heaps were a carpet of similar small puffs)
  float cov = (a.r - 0.5) * 0.6 + (bA.r - 0.5) * 1.8 * (1.0 - 0.5 * nr) * (1.0 - 0.4 * fz) + (fA.r - 0.48) * (0.5 + 0.4 * nr)
            + (f.b - 0.5) * 0.2 * nr + uCovBias + 0.08 * fz;
  // inside the broken region coverage is islands and lanes (~0.5-1.5 km: no small puffs) around a low mean (uGapW.z)
  // (r5: driven by the 6 km field more than the 1.9 km one: 1-3 km cloud masses with a few irregular gaps, not a
  // carpet of small islands; p2: ~2.4x the contrast - a few large banks with dark lanes, puffs only along their edges)
  // (the 1.9 km field leads: banks ~1-2 km across and ~3-4 km along the wind; the 6 km one opened 5-10 km holes)
  float ci = uGapW.z + (bA.r - 0.5) * 1.1 + (fA.r - 0.48) * 1.9 + (f.b - 0.5) * 0.2;
  cov = mix(cov, ci, g);
  cov = mix(cov, -0.2 + (f.r - 0.48) * 0.4, ho);   // (the gorge hole is clean: soft-edged, no rim wisps left as lone puffs)
  cov -= uWin * smoothstep(0.04, 0.45, texture2D(tWin, xz / uTownSize + 0.5).r);
  // (r8 p2) valley fog: over ground that rises into the layer (plateaus and ridges ~1.5-1.75 km) the sea thins out - it
  // lies in the valleys and meets the slopes at ~1.5-1.6 km (the L2 heightfield, 8 km around the ring, faded out at its edge)
  vec2 tq = xz / uTerrSize;
  float te = smoothstep(0.5, 0.4, max(abs(tq.x), abs(tq.y))) * uTerrCov;
  if (te > 0.0) cov -= te * smoothstep(uTop - 300.0, uTop - 60.0, texture2D(tTerr, tq + 0.5).r + (f.r - 0.48) * 200.0);
  cov = mix(cov, 0.9, nb);
  cov = sat(cov * uCovScale);
  // domed heaps: thick where coverage is high, thinning toward the gaps (top sinks below the base)
  // (gentle: densityC cuts the heap edges horizontally at coverage ~0.28; steep flanks showed vertical streaks)
  float k = smoothstep(0.0, 0.8, cov);
  float top = mix(uTop - 230.0, uTop + (b.g - 0.5) * 120.0, k * (2.0 - k));
  // islands inside the broken region are flat lenses (wider than tall), not towers; beyond ~2.5 km (seen through
  // the ring void at a glancing angle) they rise toward the sea top, so they read as billows over navy lanes
  // (their top rises slowly with coverage: rounded flanks, not steep extruded walls)
  // (r5 p2: the banks' tops differ by up to ~+-120 m (bA.g): decks at different heights, some overlapping others)
  float iT = uBase + 40.0 + (190.0 + 60.0 * smoothstep(2200.0, 4500.0, rr)) * smoothstep(0.2, 0.7, cov) + (bA.g - 0.5) * 260.0;
  top = mix(top, min(top, iT), smoothstep(0.03, 0.55, g));
  // (r5: no low near layer any more - its sunken heaps under the ring read as one smooth dome with streaked flanks;
  // nearW still feeds the fringe lumps of densityC)
  // layered decks: the tops sit on two levels ~80 m apart (0.4-1.5 km plateaus with gentle steps between them; the
  // sharper 110 m step stood as a wall)
  top += (smoothstep(0.35, 0.65, bA.b) - 0.5) * 80.0;
  // the bank under the deck: flat ~1930 m (the hero lines of sight 25-29 deg down meet its front edge at the frame
  // bottoms; shallower ones pass over it into the hole); densityC makes it a ~100 m thick layer
  // (r5: over its front ramp the bank top sinks to the sea's and its base follows (densityC): a sloping deck, not a cliff)
  top = mix(top, uBase + 430.0 + (f.g - 0.5) * 30.0, smoothstep(0.0, 1.0, nb));
  // ragged wells in the bank on the gorge axis under the deck: seen through the ring void from above (view 8,
  // the top-down crane) as dark gaps down the slot (the void shows the bank level ~0-275 m out, +-140 m across)
  if (r0 < 700.0) {
    vec2 d = xz - uRingC.xz;
    vec2 hd = vec2(dot(d, uHeroDir), dot(d, vec2(-uHeroDir.y, uHeroDir.x)));
    vec4 h = texture2D(tWeather, xz / 520.0 + vec2(0.61, 0.07));
    // (r5: one ragged well in the void, with soft, lens-shaped rims - from the top-down view the bank's lit tops fill
    // most of the void; sharp-edged wells read as drilled shafts, and the walls of a second well ~220 m out stood as a
    // bright vertical streak at the bottom of the hero frames)
    // (p2: ~25% smaller - from above the well dominated the void as a dark shaft)
    float wl = 1.0 - length((hd - vec2(105.0, 30.0)) / vec2(32.0, 23.0));
    vec4 h2 = texture2D(tWeather, xz / 190.0 + vec2(0.23, 0.71));   // (r5: torn rim)
    // (p2: opens inside the ellipse only - with smoothstep(-0.5, ..) the hole reached ~1.5x out and still dominated the
    // void from above)
    // (r9: x uWell - CLOUDS.well 0 in the film: diving through the void, the well read as a dark blob in the sea)
    wl = smoothstep(0.0, 0.8, wl + (h.r - 0.5) * 1.1 + (h.g - 0.5) * 0.5 + (h2.r - 0.5) * 0.9) * nb * uWell;
    cov = mix(cov, 0.0, wl);
    top = mix(top, uBase - 160.0, wl);
    g = max(g, wl);
    // (the bank top's puffs are 3D now - the lumps and the erosion of densityC: a 2D puff field with 8-60 m
    // features stood as thin vertical sheets at the frame bottoms of the hero views)
  }
  gBankC = nb; gLane = lane; gHRay = sw.y; gTopB = top;
  return vec4(cov, top, floor(sw.y) + min(lane, 0.999), g);
}

// The layout is static: column() is baked once at load into an atlas of two 1024^2 tiles around the ring (2.4 km at
// 2.3 m, 24 km at 23 m texels; A: cov, top, gap, bank weight; B: lane, sight-line altitude), so the march reads
// 2 texels per column instead of ~8 weather fetches and the capsule maths. Beyond 12 km: the analytic column().
uniform sampler2D tColA, tColB;
uniform vec2 uColSize;       // tile sizes (m): near, far
uniform float uColOn;
vec4 columnT(vec2 uv){
  vec4 A = texture2D(tColA, uv); vec3 B = texture2D(tColB, uv).rgb;
  gBankC = A.w; gTopB = B.z;
  return vec4(A.x, A.y, floor(B.y) + min(B.x, 0.999), A.z);
}
vec4 columnC(vec2 xz){
  vec2 d = xz - uRingC.xz, h = vec2(0.5 / 1024.0);
  vec2 u0 = d / uColSize.x + 0.5, u1 = d / uColSize.y + 0.5;
  bool in0 = uColOn > 0.5 && all(greaterThan(u0, h)) && all(lessThan(u0, 1.0 - h));
  bool in1 = uColOn > 0.5 && all(greaterThan(u1, h)) && all(lessThan(u1, 1.0 - h));
  vec4 c;
  if (in0) c = columnT(vec2(u0.x * 0.5, u0.y));
  else if (in1) c = columnT(vec2(0.5 + u1.x * 0.5, u1.y));
  else c = column(xz);
  return c;
}
`;

// bakes column() into the atlas tiles (uWhich 0: A, 1: B); vUv spans the atlas, the left half is the near tile.
// B also gets the top altitude averaged over a ~0.3 km disc (from the A tiles baked first): the surroundings of a
// trough between heaps, which hide most of the dome from it
const colFrag = /* glsl */ `
precision highp float;
varying vec2 vUv;
uniform float uWhich;
${COLUMN}
float topA(vec2 xz){
  vec2 d = xz - uRingC.xz, u0 = d / uColSize.x + 0.5, u1 = clamp(d / uColSize.y + 0.5, 0.001, 0.999);
  bool in0 = all(greaterThan(u0, vec2(0.001))) && all(lessThan(u0, vec2(0.999)));
  return texture2D(tColA, in0 ? vec2(u0.x * 0.5, u0.y) : vec2(0.5 + u1.x * 0.5, u1.y)).y;
}
void main(){
  float far = step(0.5, vUv.x);
  vec2 xz = uRingC.xz + (vec2(fract(vUv.x * 2.0), vUv.y) - 0.5) * mix(uColSize.x, uColSize.y, far);
  vec4 c = column(xz);
  if (uWhich < 0.5) { gl_FragColor = vec4(c.x, c.y, c.w, gBankC); return; }
  float s = topA(xz), ws = 1.0;
  for (int k = 0; k < 3; k++) for (int j = 0; j < 8; j++) {
    float r = 95.0 * float(k + 1), a = (float(j) + 0.5 * float(k)) * 0.7853982, w = 1.0 - 0.2 * float(k);
    s += topA(xz + r * vec2(cos(a), sin(a))) * w; ws += w;
  }
  gl_FragColor = vec4(gLane, gHRay, s / ws, 1.0);
}
`;

const marchFrag = /* glsl */ `
precision highp float;
precision highp sampler3D;
#define PI 3.14159265359
${NOISE}
${ATMOS}
${FARDIP}
varying vec2 vUv;
uniform sampler2D tDepth;
uniform sampler3D tShape;
uniform sampler3D tDetail;
uniform sampler2D tTown;     // town light density (L1 extent)
uniform sampler2D tGlowW;    // wider blur: town light spreading onto the cloud bases around the gaps
uniform sampler3D tCurl;     // curl128.bin: rgb curl swirl (0.5 = none, sd ~0.17), a billow Worley fbm (cells 8/16/32)
uniform float uPixA;        // pixel angle (rad): footprint (m) = t * uPixA
uniform float uJit;          // march jitter offset of this sub-frame (van der Corput of the sub-frame index)
uniform sampler2D tBlue;     // 64^2 blue-noise ranks (0..1): per-pixel march offset
uniform float uEro, uLQ;     // fine erosion on (1) / off; light samples see the coarse erosion octave (1) / its mean
uniform float uRefine;       // fine steps at the first contact with a cloud (1) / off
uniform float uLite;         // light march: 1 = 2 up samples and no down sample
uniform mat4 uInvProj;
uniform mat4 uCamWorld;
uniform vec3 uCamPos;
uniform float uLogFar;
uniform float uDensity, uExt;
uniform int uSteps;
uniform float uFrame;
uniform float uRingI;
uniform vec3 uWarm;
uniform vec3 uAmbTop, uAmbBot, uGlowCol, uTownCol;
uniform float uWisp, uHug, uDbg, uSkip;
uniform float uHaze;
uniform vec3 uHazeCol;
uniform vec4 uComp;          // component gains (debug / tuning): heaps, wall wisps, stratus floor, gap veils
uniform vec2 uComp2;         // x: wisp halo gain, y: fringe lump gain
uniform vec2 uSightOn;       // sight-window sets 0 / 1 on (1) for this camera (Clouds.render)
uniform sampler3D tBillow;   // (r8) billow128.bin: rg billow fbm (rolls of every size, creases between), ba Perlin fbm
uniform vec4 uR8;            // (r8) x: billow relief (1) / r5 Worley lobes (0), y: density gain near, z: min density ramp (m), w: relief depth (m)
uniform float uWindV;        // (r8) drift of the cloud relief along uWindDir (m/s of film time)
uniform vec4 uR8b;           // (r8) x / y: tile (m) of the coarse / mid billow octave, z: fine octave weight, w: sky-occlusion exponent of the heap height
uniform vec4 uR8c;           // (r8) x: roll relief gain, y: Worley lump gain (r5: 1, 1), z / w: spare
uniform vec4 uR9;            // (r8 p2) fine detail: x relief (m), y tile (m) of the finest octave, z shell texture, w halo gate
uniform vec4 uR9b;           // (r8 p2) x: sky floor of the flanks, y: silver lining, z: mid-octave swirl (m), w: glow multi-scatter
uniform float uFineL;        // (r8 p2) the near light samples see the fine detail (1) / not
uniform vec2 uPhase;         // (r8 p2) sub-pixel phase (uv) of this sub-frame's march (Clouds.render)
uniform vec4 uR10;           // (r9) near field: x density gain, y / z its fade-out (m from the camera), w finest fineD octave weight
uniform vec4 uR10b;          // (r9) x: light contrast of the fine relief (turrets lit, clefts shaded), y: density ramp factor near,
                             // z: bump-normal shading of the fine relief, w: share of the near density gain the light samples see
uniform vec4 uR10c;          // (r9 p2) x / y: billow polarity of the coarse / mid relief octave (0: ridged 1 - |Perlin| as r8, 1: rounded
                             // lobes |Perlin| with sharp creases), z: near glow coupled to the sky occlusion, w: near glow gain
uniform vec4 uR10d;          // (r9 p2) x: near cavity of the mid octave's creases, y: closing depth (m) of terrain inside the cloud,
                             // z: near weight of the sky light's diffuse tail (x 0.2), w: wall-wisp gain beyond ~1 km from the ring
uniform vec4 uR10e;          // (r9 p2) x: fade-out (m from the camera) of the near density-ramp factor uR10b.y, y: cell-size variation
                             // (share of the mid lobes by the curl field), z: upper edge of the mid-octave cavity, w: lid share of the closing
uniform vec4 uR10f;          // (r9 p2) x: glow coupled to the sky occlusion at every distance, y / z / w: spare
${COLUMN}
float remap(float v, float a, float b, float c, float d){ return c + (v - a) / (b - a) * (d - c); }

// solve altitude(ro + rd t) = H ; returns roots (t0 <= t1), or (1e9,1e9) when none
vec2 solveAlt(vec3 ro, vec3 rd, float H){
  float a = dot(rd.xz, rd.xz) / (2.0 * uEarthR);
  float b = rd.y + dot(ro.xz, rd.xz) / uEarthR;
  float c = altOf(ro) - H;
  if (a < 1e-12) { float t = -c / b; return vec2(t, 1e9); }
  float disc = b * b - 4.0 * a * c;
  if (disc < 0.0) return vec2(1e9);
  float s = sqrt(disc);
  return vec2((-b - s) / (2.0 * a), (-b + s) / (2.0 * a));
}

float terrH(vec2 xz){
  vec2 uv = xz / uTerrSize + 0.5;
  if (uv.x < 0.002 || uv.y < 0.002 || uv.x > 0.998 || uv.y > 0.998) return -9999.0;
  return texture2D(tTerr, uv).r;
}

// Lumpy top surface: Perlin-Worley rolls (~250-550 m) and Worley lumps (70-275 m) displace the column top;
// below that surface (and inside the coverage edge) the cloud is carved by warped Worley erosion (cells 80..4 m)
// and its density then rises over a short ramp. A thin stratus floor fills the troughs between the heaps.
// q: 2 = primary samples (all octaves), 1 = light samples (coarse erosion octave), 0 = no erosion (its mean)
float gSkin = 45.0;   // erosion depth (m): how far the fine structure carves into the cloud surface
float gRamp = 8.0;    // density ramp (m) below the carved surface, grows with the step and the pixel footprint
float gFarL = 0.0;    // 0 near .. 1 beyond ~6 km from the camera: flatter, layered tops (no cauliflower carpet)
float gH = 1.0;       // out: height of the sample within its heap (0 base .. 1 top), for sky occlusion
float gFp = 1.0;      // pixel footprint (m) at the primary sample (its light samples reuse it)
float gEc = 0.5;      // out: coarse erosion octave (0..1), drives the wall wisps
float gFib = 0.5;     // out: fine fibre octave (0..1, 0.5 where it is not resolved)
float gCav = 0.0;     // out: erosion of the visible surface on the tops (0 billow crown .. 1 deep cleft): cavity AO
float gCavM = 0.0;    // (r9 p2) out: the same from the mid octave (the creases between the 10-75 m lobes), for the near field

// Fine structure (0 = keep .. 1 = carved away): billow Worley fbm (curl128 a), cells ~180/90/45 m, plus fibres
// (cells ~20/10/5 m, stretched x1.7 along the wind and swirled ~50 m by the curl channels and the coarse octave)
// that fade out below ~2.6 m footprint (r5: both octaves ~2x larger and the fibres weighted 0.55 instead of 0.18 -
// the old 80..4 m cells were sub-pixel from the hero cameras 1-5 km away and read as a uniform grain, the billows as
// smooth blobs). Billowed (the cell centres survive as cauliflower crowns); toward the undersides densityC carves
// deeper, tearing the belly into tufts. (Inverted Worley there left its cell walls as flat sheets: curtain streaks.)
// (r5 p2: a mid octave, cells ~54/27/13 m, between them: the cauliflower lobes 10-40 px wide from the hero cameras -
// the coarse cells read as 40-80 px blobs and the fibres as texture; the light samples next to the primary see it, so
// every lobe gets a sky-lit crown and a self-shadowed belly)
// q: 3 = all octaves (primary samples), 2 = coarse + mid (the near light samples), 1 = coarse octave
float gEm = 0.5;      // out: mid octave (0..1, 0.5 where it is not evaluated)
float gFf = 0.0;      // (r9) out (fineD): its two fine octaves alone (fineF of the same point)
// (r8) free-flight relief: billow fbm (1 - |Perlin|) instead of Worley lobes - rounded rolls of every size with sharp
// creases between them, the way a cloud top looks from 30 m to 3 km (the Worley octaves made a cauliflower carpet of
// equal round lumps: 'anime'). Coarse: rolls ~400-50 m; mid: 100-12 m, swirled by the curl channels; fine: Perlin
// wisps 30-4 m, mip-faded below a pixel (world-space and filtered: no shimmer in motion).
float erosion8(vec3 p, int q){
  vec2 wd = uWindDir, wn = vec2(-wd.y, wd.x);
  vec3 qa = vec3(dot(p.xz, wd) / 1.3, p.y * 1.25, dot(p.xz, wn));
  vec4 ca = textureLod(tCurl, qa / 1430.0 + vec3(0.21, 0.13, 0.47), max(log2(gFp / 11.2), 0.0));
  float b0 = textureLod(tBillow, qa / uR8b.x + vec3(0.17, 0.61, 0.29), max(log2(gFp * 128.0 / uR8b.x), 0.0)).r;
  // (r9 p2) uR10c.x / y (0 or 1, the same everywhere: no morphing with distance): the relief kept as |Perlin| - rounded lobes
  // with sharp creases between them (cauliflower, the refs' tops); 1 - |Perlin| raised sharp crests round soft bowls (lichen)
  b0 = mix(b0, 1.0 - b0, uR10c.x);
  float w = sat(0.5 + (b0 - 0.5) * 1.9);
  gEc = w; gEm = 0.5;
  if (q > 1) {
    // (p2: swirl uR9b.z ~25 m instead of 60: the curled creases of the mid octave read as marble / tadpole swirls)
    vec3 pm = qa + (ca.rgb - 0.5) * uR9b.z;
    float m = textureLod(tBillow, pm / uR8b.y + vec3(0.63, 0.29, 0.81), max(log2(gFp * 128.0 / uR8b.y), 0.0)).g;
    m = mix(m, 1.0 - m, uR10c.y);
    gEm = sat(0.5 + (m - 0.5) * 1.9);
    // (r9 p2) the share of the mid lobes varies with the curl field (uR10e.y; 0: 0.38 everywhere as r8): patches of small
    // lobes next to smooth large rolls - cells of every size, not a field of equal pillows (bubble wrap)
    float wm = clamp(0.38 + (ca.r - 0.5) * uR10e.y, 0.06, 0.75);
    w = w * (1.0 - wm) + gEm * wm;
  }
  if (q > 2) {
    float fF = 1.0 - smoothstep(0.6, 2.4, gFp);
    if (fF > 0.0) {
      vec3 pf = qa + (ca.rgb - 0.5) * 40.0 + (gEm - 0.5) * vec3(30.0, 12.0, 30.0);
      float b = textureLod(tBillow, pf / 110.0 + vec3(0.37, 0.71, 0.13), max(log2(gFp / 0.86), 0.0) + 0.5).b;
      gFib = mix(0.5, sat(0.5 + (b - 0.5) * 1.7), fF);
      w = mix(w, w * (1.0 - uR8b.z) + gFib * uR8b.z, fF);
    }
  }
  return 1.0 - w;
}
// (r8 p2) fine detail of the primary samples: two Perlin octaves (tile uR9.y: ~7-2 m features; x4: ~56-7 m), stretched
// x1.6 along the wind (fibres) and swirled by the mid octave. Mip-filtered by the pixel footprint and weighted down as
// each octave blurs, so it fades to its mean (0.5) where it is not resolved: world-space and filtered, no shimmer, no grey
// smear. Mean 0.5, sd ~0.4 where both octaves are resolved (unclamped).
float fineD(vec3 p){
  vec2 wd = uWindDir, wn = vec2(-wd.y, wd.x);
  vec3 qf = vec3(dot(p.xz, wd) / 1.6, p.y * 1.2, dot(p.xz, wn)) + (gEm - 0.5) * vec3(16.0, 6.0, 16.0);
  float T0 = uR9.y, T1 = uR9.y * 4.0;
  float l0 = log2(gFp * 128.0 / T0), l1 = log2(gFp * 128.0 / T1);
  float w1 = 1.0 - smoothstep(1.0, 3.0, l1);
  if (w1 <= 0.0) return 0.5;
  float w0 = 1.0 - smoothstep(1.0, 3.0, l0);
  float n1 = textureLod(tBillow, qf / T1 + vec3(0.83, 0.19, 0.41), max(l1, 0.0)).b;
  float n0 = w0 > 0.0 ? textureLod(tBillow, qf / T0 + vec3(0.11, 0.53, 0.77), max(l0, 0.0)).a : 0.5;
  // (r9) a finest octave (tile / 4: ~1.8-0.4 m) where it is resolved (the close passes, tops < ~300 m away): ragged
  // fringes and turrets on every billow edge instead of the smooth outline of the 2-7 m octave
  float T2 = T0 * 0.25, l2 = log2(gFp * 128.0 / T2);
  float w2 = (1.0 - smoothstep(1.0, 3.0, l2)) * uR10.w;
  float n2 = w2 > 0.0 ? textureLod(tBillow, qf / T2 + vec3(0.47, 0.31, 0.29), max(l2, 0.0)).a : 0.5;
  gFf = ((n0 - 0.5) * 0.45 * w0 + (n2 - 0.5) * w2) * 2.6;
  return 0.5 + (n1 - 0.5) * 0.75 * w1 * 2.6 + gFf;
}
// (r9) the two fine octaves of fineD alone (~7-0.4 m; same coordinates, LOD and weights; gEm of the primary sample):
// the lit samples near the camera take its slope as a bump normal of the relief
float fineF(vec3 p){
  vec2 wd = uWindDir, wn = vec2(-wd.y, wd.x);
  vec3 qf = vec3(dot(p.xz, wd) / 1.6, p.y * 1.2, dot(p.xz, wn)) + (gEm - 0.5) * vec3(16.0, 6.0, 16.0);
  float T0 = uR9.y, T2 = T0 * 0.25;
  float l0 = log2(gFp * 128.0 / T0), l2 = log2(gFp * 128.0 / T2);
  float w0 = 1.0 - smoothstep(1.0, 3.0, l0), w2 = (1.0 - smoothstep(1.0, 3.0, l2)) * uR10.w;
  float n0 = w0 > 0.0 ? textureLod(tBillow, qf / T0 + vec3(0.11, 0.53, 0.77), max(l0, 0.0)).a : 0.5;
  float n2 = w2 > 0.0 ? textureLod(tBillow, qf / T2 + vec3(0.47, 0.31, 0.29), max(l2, 0.0)).a : 0.5;
  return ((n0 - 0.5) * 0.45 * w0 + (n2 - 0.5) * w2) * 2.6;
}
float erosion(vec3 p, int q){
  if (uR8.x > 0.5) return erosion8(p, q);
  // (r5: no lump warp - with it, and with the distance-dependent wind stretch, the noise coordinates were sheared
  // along the line of sight: the carved billows read as combed fur, their flanks as streaks)
  vec2 wd = uWindDir, wn = vec2(-wd.y, wd.x);
  vec3 qa = vec3(dot(p.xz, wd) / 1.3, p.y, dot(p.xz, wn));
  vec4 ca = textureLod(tCurl, qa / 1430.0 + vec3(0.21, 0.13, 0.47), max(log2(gFp / 11.2), 0.0));
  float w = sat(0.5 + (ca.a - 0.4804) / 0.1106 * 0.28);
  gEc = w; gEm = 0.5;
  if (q > 1) {
    // (mip-mapped: it fades to its mean where the cells fall below a pixel - no fade-out switch needed)
    vec3 pm = qa + (ca.rgb - 0.5) * 30.0;
    float m = textureLod(tCurl, pm / 430.0 + vec3(0.63, 0.29, 0.81), max(log2(gFp / 3.36), 0.0)).a;
    gEm = sat(0.5 + (m - 0.4804) / 0.1106 * 0.3);
    w = w * 0.5 + gEm * 0.5;
  }
  if (q > 2) {
    // (p2: faded over 1-3.2 m footprint: kept to 4.5 m, the density threshold re-sharpened the mip-blurred 5-10 m cells
    // into 2-4 px salt-like dots over the thin tops of views 5 / 6)
    float fF = 1.0 - smoothstep(1.0, 3.2, gFp);
    if (fF > 0.0) {
      vec3 pf = qa + (ca.rgb - 0.5) * 49.0 + (ca.a - 0.48) * vec3(58.0, 23.0, 58.0);
      pf.x /= 1.3;
      // (one mip up: the 5 m cells broke the crisp bank edges of the long lenses into salt-like dots)
      float b = textureLod(tCurl, pf / 156.0 + vec3(0.37, 0.71, 0.13), max(log2(gFp / 1.22), 0.0) + 1.0).a;
      gFib = mix(0.5, sat(0.5 + (b - 0.4804) / 0.1106 * 0.28), fF);
      w = mix(w, w * 0.7 + sat(0.5 + (b - 0.4804) / 0.1106 * 0.28) * 0.3, fF);
    }
  }
  return 1.0 - w;
}

float gBoost = 1.0;   // density gain of the primary sample's neighbourhood (denser, crisper near clouds)
float gFL = 0.0;      // (r8 p2) this light sample sees the fine detail (densityC q 2)
float gFree = 0.0;    // out: clear height (m) above the cloud surface when the sample is in empty space, else 0

float gTw = 0.0;       // out: closeness to a sight-window wall (0..1): lit like a torn edge, not a dark trough
float gSurf = 0.0;     // (r8) out: the rolled top surface before the billow relief (primary samples)
float gFd = 0.5;       // (r9) out: fine detail (fineD) of the primary sample's outer shell (0.5: none / not resolved)
float gBfE = 99.0;     // (r9) out: depth (m) of the primary sample below the displaced, carved surface (99: fineD not evaluated)
float densityC(vec3 p, vec4 c, float bk, float lod, float far, int q){
  bool hi = q > 2;
  float alt = altOf(p);
  gFree = alt - uTop - 220.0;
  if (alt < uBase - 10.0 || alt > uTop + uWisp + 60.0) return 0.0;
  // (r8) the relief drifts with the wind as a whole (uWindV m/s along uWindDir; the layout stays): a film shot sees
  // the cloud move, not boil - the r5 drift of the rolls alone (~1.7 m/s against fixed erosion) morphed the billows
  vec3 pn = p;
  p -= vec3(uWindDir.x, 0.0, uWindDir.y) * (uTime * uWindV);
  vec3 qs = vec3(p.x, p.y * 1.4, p.z) / 2200.0 + vec3(uTime * 0.0002, 0.0, uTime * 0.00008);
  vec4 s = textureLod(tShape, qs, lod);
  // normalised (~N(0,1)) Perlin-Worley rolls and Worley-fbm lumps (stats of shape128.bin)
  float zr = (s.r - 0.668) / 0.078;
  float zw = (s.g * 0.5 + s.b * 0.3 + s.a * 0.2 - 0.477) / 0.11;
  float bc = sat(0.5 + zr * 0.2);
  // (r5: relief x1.8 / x1.5, the bank under the deck included: billowed rolls with dark troughs, not a smooth carpet)
  // (r8: uR8c.x / y scale the rolls / the Worley lumps - the lumps raise a round head on every 70-275 m cell: cauliflower)
  float surf = c.y + (zr * 81.0 * uR8c.x * (1.0 - 0.3 * gFarL) + zw * 30.0 * uR8c.y * (1.0 - 0.85 * gFarL)) * (1.0 - 0.3 * gFarL);
  // flat-ish tops with gentle domes: what rises above the mean top is compressed (no towers)
  float cap = max(uTop + 80.0, c.y - 20.0);   // (the gorge fill under the deck is not capped)
  surf = surf > cap ? cap + (surf - cap) * 0.6 : surf;
  // (sky occlusion is measured against the column top: a dome that rises above it is lit, a trough below it is dark)
  float surfAO = min(surf, c.y + 30.0);
  float below = surf - alt;
  // terrain-hugging layer: cloud piles against the slopes; only next to the ring does it climb the
  // gorge walls (wisps below the deck) - elsewhere ridges above ~1900 m stay clear of it; within ~0.5 km of the
  // ring it is faint (on the vertical slot walls it read as smoke columns / a waterfall from above)
  // (r8: the wall mist only for the primary samples - the light samples skip the terrain fetch; its shadow is negligible)
  float hT = q > 2 ? terrH(pn.xz) : -9999.0;
  float above = alt - hT;
  float rr = length(pn.xz - uRingC.xz);
  float hugTop = uTop + 40.0 + uWisp * smoothstep(1300.0, 350.0, rr);
  // (p2: 0.4 instead of 0.12 next to the ring - translucent torn mist on the pinnacle walls, refs 9/11/2)
  float hug = above > -40.0 ? exp(-max(above, 0.0) / 50.0) * step(alt, hugTop) * (1.0 - 0.85 * c.w) * mix(1.0, 0.4, smoothstep(650.0, 400.0, rr)) * uHug : 0.0;
  // (r9 p2: x uR10d.w beyond ~1 km - on the ribs and pinnacles out in the sea the 50 m skin stood from the base to the tops
  // as pink vertical smoke plumes; the torn mist on the ring's pinnacles stays)
  hug *= mix(1.0, uR10d.w, smoothstep(600.0, 1000.0, rr));
  float strat = alt - uBase;
  // (gFree: clear height above the lumpy top, before the +-50 m lumps and the erosion, for the empty-space skip)
  gFree = hug < 0.02 && strat > 110.0 ? -below : 0.0;
  if (below < -120.0 && hug < 0.05 && strat > 110.0) return 0.0;
  // fringe of the sea (low coverage, gap edges): isotropic 3D Worley lumps (~100-200 m) erode the heap
  // flanks into billows, and the heaps lift off the floor into rounded puffs instead of extruded walls
  // (and the near layer below the ring: smaller billows close to the hero cameras)
  // (in the broken region and the bank the lumps are squashed: layered banks, wider than tall)
  float fr = max(max(max(1.0 - smoothstep(0.18, 0.52, c.x), c.w), 0.7 * nearW(pn.xz, rr)), 0.7 * bk);
  float e3 = 0.0;
  if (fr > 0.01 && far < 0.99) {
    // (a constant vertical squash: one that varied across the gap edges sheared the noise into vertical streaks)
    vec4 s2 = textureLod(tShape, vec3(p.x, p.y * 1.8, p.z) / 820.0 + vec3(0.37 + uTime * 0.0005, 0.0, 0.11 + uTime * 0.0002), lod);
    e3 = (s2.g * 0.5 + s2.b * 0.3 + s2.a * 0.2 - 0.477) / 0.11 * fr * (1.0 - far) * (1.0 - 0.6 * gFarL) * uComp2.y;
  }
  below += e3 * 24.0;
  float bot = uBase - 10.0 + max(fr, c.w) * 90.0 - e3 * 40.0;
  // coverage as a horizontal depth (m) inside the heap edge, shifted in 3D by the 70-275 m lumps and carved by the
  // erosion like the tops (an extruded 2D contour showed as vertical streaks); over its last ~140 m the top sinks
  // and the base rises (lens-shaped, rounded edges)
  // (and opened along the troughs of the rolls: dark lanes between the billowed masses)
  float Fc = (c.x - 0.28) * 650.0 + zw * 35.0 + zr * 50.0;
  float lens = max(0.0, 140.0 - Fc) * 0.5;
  below = min(below - lens, Fc);
  // islands in the broken region are lenses: the base rises toward their edges as the top sinks there,
  // so their flanks round off instead of hanging as vertical curtains above the lake
  bot = mix(bot, max(bot - 60.0, uBase + 70.0 - (c.y - uBase - 70.0) * 0.7 - e3 * 30.0), smoothstep(0.2, 0.7, c.w));
  // the bank is a ~100 m thick layer with a ragged soft belly (dark slot below it from the hero views); it stays
  // thin across its front edge (a sheet sloping down to the sea, not a curtain hanging into the valley)
  bot = mix(bot, c.y - 120.0 - e3 * 25.0, smoothstep(0.0, 1.0, bk));
  // a deck, not towers: the sea is at most ~100-220 m thick under its lumpy top, thinnest in the troughs of the
  // rolls (seen from the ring ~400 m above the tops, full-height heaps showed 300 m walls as cloud towers)
  // (r8: ~320 m - down to the base inside a bank: with ~160 m the roll troughs and the billow creases cut through the
  // thin deck everywhere, and the sea fell apart into a popcorn carpet of separate puffs; the gaps are the layout's)
  bot = max(bot, surf - mix(160.0, 320.0, uR8.x) - zr * 45.0 - e3 * 20.0);
  // fine structure (q 0: its mean); its strength varies across the heap with s.g so the texture is not uniform.
  // Only evaluated where it can matter: in the carved shell under the surface, the belly fade, the floor, the veils
  // and the wall wisps (deep inside, or outside the envelope, the result does not depend on it)
  float hb = sat((alt - bot) / max(surf - bot, 60.0));
  // (the bank's belly fades over ~55 m only: with the full fade the thin bank was translucent, the void a dark shaft)
  float wb = mix(140.0 - fr * 60.0, 55.0, bk);
  float zb = (alt - lens + (bc - 0.5) * 120.0 * (1.0 - 0.6 * bk) - bot) / wb;
  bool shell = below > 0.0 && zb > 0.0 && (below < 1.2 * gSkin + gRamp || zb < 1.0);
  bool thin = (strat < 110.0 && c.x > 0.22 && c.w < 0.45) || (c.w > 0.35 && strat > 30.0 && strat < 190.0) || hug > 0.05;
  // sight-window tube (below): distance in lane strength x altitude (1 = its edge); the erosion is evaluated around it
  // too (p2: deep in a heap it was not, and the window had smooth cylinder walls - a cookie-cut hole)
  // (p2: each set's tubes are cut only for cameras near that set's cameras (uSightOn, Clouds.render): from elsewhere,
  // e.g. view 4's long lens, another camera's tube stood as a dark vertical slot; the set index is packed in 4000 m
  // steps on the sight-line altitude)
  float hs = floor(c.z), si = floor(hs / 4000.0);
  float lz = fract(c.z) * (si < 0.5 ? uSightOn.x : uSightOn.y);
  float tr0 = lz > 0.01 ? length(vec2((1.0 - lz) * 1.2, (alt - (hs - 4000.0 * si) + (bc - 0.5) * 50.0) / 90.0)) : 9.0;
  float E = 0.5;
  gEc = 0.5; gFib = 0.5; gEm = 0.5;
  if (q > 0 && far < 0.99 && uEro > 0.5 && (shell || thin || tr0 < 1.7))
    E = mix(0.5, erosion(p, q), (1.0 - far) * sat(0.7 + 0.6 * s.g));
  float ek = E * mix(1.0, 0.75, hb);
  // tops and edges: carved ek * gSkin deep (more feathered on the islands of the broken region), then the density
  // rises over gRamp (soft enough for the step: no slicing); bellies: a ~100 m fade carved deeper (torn tufts)
  // (the far sea is carved less: smoother, layered tops instead of a popcorn carpet)
  float ecv = ek * gSkin * (1.0 + 0.3 * smoothstep(0.2, 0.8, c.w) * (1.0 - bk)) * (1.0 - 0.45 * gFarL);
  // (r8 p2) fine detail (fineD) in the outer ~40 m and the halo above it: +-uR9.x m of relief at 2-56 m (torn,
  // fibrous edges instead of melted wax) - a no-op where it is not resolved
  float fd = 0.5;
  // (the near light samples (q 2: 6-7 m up / toward the glow) see it too (uFineL): every fibre gets a lit crown and a
  // shaded underside - the texture is in the light, not only in the outline)
  bool fOn = (hi || (q == 2 && gFL > 0.5)) && uR9.x > 0.0 && far < 0.99 && below > -45.0 && below - ecv < 40.0 + gRamp && zb > -0.3;
  if (fOn) fd = fineD(p);
  float bf = below + (fd - 0.5) * uR9.x;
  float d = sat((bf - ecv) / gRamp)
          * smoothstep(0.0, 1.0, (zb - 0.8 * ek + (fd - 0.5) * 0.25) / max(1.0 - 0.8 * ek, 0.2));
  // and the density of the outer ~25 m varies with it (texture inside every billow: the visible depth and the light vary)
  d *= mix(1.0, sat(0.3 + 1.4 * fd), uR9.z * (1.0 - smoothstep(0.0, 25.0, bf - ecv)));
  // islands, fringe and near-layer heaps fade out ~70-260 m under their lumpy tops (soft bellies instead of
  // extruded column walls that hung as vertical curtains above the lake)
  d *= mix(1.0, smoothstep(260.0, 70.0, below), max(smoothstep(0.15, 0.6, c.w), smoothstep(0.3, 0.7, fr)) * 0.8);
  // patchy stratus floor between the heaps (only where the sea is not broken)
  // (not under the islands of the broken region: its extruded edges hung there as vertical curtains)
  float ds = 0.3 * smoothstep(0.26, 0.42, c.x + (bc - 0.5) * 0.12) * smoothstep(0.0, 40.0, strat) * smoothstep(110.0, 50.0, strat + (bc - 0.5) * 80.0)
           * (1.0 - smoothstep(0.1, 0.45, c.w)) * (1.0 - 0.7 * E);
  // veils: a thin, torn sheet ~40-170 m above the base in the gaps, partly hiding the valley floor
  float dv = 0.06 * smoothstep(0.35, 0.8, c.w) * smoothstep(30.0, 80.0, strat) * smoothstep(190.0, 120.0, strat + (bc - 0.5) * 80.0)
           * sat(1.4 - 2.0 * E);
  // wisps: ragged (detail-noise) sheet on the walls, thinning with height up to hugTop
  float hz = sat((hugTop - alt) / max(hugTop - uTop, 60.0));
  // (p2: torn by the fibres too: tendrils, not smooth smoke)
  float wn = sat(0.5 + 1.2 * (gEc - 0.5) * (1.0 - far) + (bc - 0.5) + (gFib - 0.5) * 0.9);
  float dh = sat(wn * hug * (0.4 + 0.6 * hz) * 2.2 - 0.75) * smoothstep(hugTop, hugTop - 60.0, alt);
  // (density-weighted, continuous: a hard switch between components made bright/dark speckles)
  if (hi) {
    gH = (d * sat((alt - uBase + 40.0) / max(surfAO - uBase + 40.0, 60.0)) + dh * (0.6 + 0.4 * sat(above / 120.0)) + (ds + dv) * 0.25) / (d + dh + ds + dv + 1e-4);
    // (from the coarse and mid octaves: the fibres in the shading read as speckle; p2: the mid octave's clefts shade
    // the lobes 10-40 px wide)
    // (r8 p2: from the coarse octave only, smooth: the mid octave's creases formed closed dark iso-bands - marble)
    gCav = smoothstep(0.75, 0.2, gEc) * smoothstep(0.15, 0.55, hb) * d / (d + dh + ds + dv + 1e-4) * 0.6;
    // (r9 p2) with the lobes rounded (uR10c.y) the mid octave's low values are narrow creases, not wide bowls (the r8 p2
    // marble): dark clefts between the lit lobes of the near tops
    // (uR10e.z: the upper edge - at 0.42 the low patches of the fbm sum shaded as broad dark-brown blobs, holes not clefts)
    gCavM = smoothstep(uR10e.z, 0.04, gEm) * smoothstep(0.15, 0.55, hb) * d / (d + dh + ds + dv + 1e-4);
    gSurf = surf;
    // (r9) the fine relief where it displaces the visible surface (outer ~20 m): high = a turret pushed out, low = a cleft
    gFd = mix(0.5, fd, 1.0 - smoothstep(0.0, 20.0, bf - ecv));
    gBfE = fOn ? bf - ecv : 99.0;
  }
  // sight-window tube: clear around the hero line of sight to the lights, flat like the view of the lit ground
  // through it (wider than tall: a taller tube cut a trench into the deck, a dark slot down the frame); ragged by
  // the erosion and the rolls (r5: an elliptical cross-section in lane strength x altitude - a rounded hole; the product
  // of two ramps cut rectangular windows with straight edges)
  // (p2: its radius torn by the erosion and the fibres (~+-0.4) and a wider soft edge: the density thins over ~40-100 m
  // into translucent torn edges instead of a rounded-rectangle hole with smooth walls)
  // (coarse + mid octaves only: the fibres tore the thinned edge into salt-like dots)
  float tr = tr0 + (mix(gEc, gEm, 0.5) - 0.5) * 1.3;
  float tube = smoothstep(1.05, 0.4, tr) * smoothstep(0.0, 0.12, lz);
  if (hi) gTw = smoothstep(1.6, 0.9, tr) * (1.0 - tube) * smoothstep(0.0, 0.12, lz);
  // wisps (r5): a faint fibrous halo just outside the carved billows - torn edges and tendrils
  float cvd = ecv - bf;
  // (r8 p2: gated by the fine detail (uR9.w): torn fibres near the camera; where they are not resolved, no halo - a
  // smooth halo round every billow read as a defocused, melted outline)
  float dw = 0.08 * uComp2.x * smoothstep(0.0, 6.0, cvd) * smoothstep(40.0, 0.0, cvd) * sat((gFib - 0.5) * 4.0 + 0.5) * smoothstep(0.0, 0.5, zb)
           * mix(1.0, 2.0 * sat((fd - 0.56) * 3.0), uR9.w);
  d = max(d, dw);
  // (density variation in 3D: a 2D factor showed as vertical streaks through the translucent flanks)
  return max(max(d * uComp.x, dh * uComp.y), max(ds * uComp.z, dv * uComp.w)) * uDensity * (0.7 + 0.6 * s.g) * gBoost * (1.0 - tube);
}
float density(vec3 p, float lod, float far, int q){ vec4 c = columnC(p.xz); return densityC(p, c, gBankC, lod, far, q); }

float hg(float c, float g){ float g2 = g * g; return (1.0 - g2) / (4.0 * PI * pow(1.0 + g2 - 2.0 * g * c, 1.5)); }

void main(){
  // (r8 p2) below the frame resolution each sub-frame marches the rays through one full-resolution pixel centre of every
  // 2x2 block (uPhase), and the composite reads the texels back at that phase: K = 4 film sub-frames sample all four
  // (detail of a full-resolution march at the cost of a half-resolution one)
  vec2 uvP = vUv + uPhase;
  vec4 ndc = vec4(uvP * 2.0 - 1.0, 1.0, 1.0);
  vec4 vv = uInvProj * ndc; vv /= vv.w;
  vec3 dv = normalize(vv.xyz);
  vec3 rd = normalize(mat3(uCamWorld) * dv);
  vec3 ro = uCamPos;
  float dep = texture2D(tDepth, uvP).r;
  float sceneT = 1e9;
  if (dep < 0.9999) {
    float w = exp2(dep * uLogFar) - 1.0;
    sceneT = w / max(-dv.z, 1e-4);
  }
#ifdef CLOUD_DBG
  if (uDbg > 0.5) {
    // debug map (URL flag cdbg; compiled only then) where the (dipped) ray crosses the mid-layer in front of the scene:
    // red = gap field, green = coverage, blue = ring distance rings (500 m)
    float tq = 10.0;
    for (int i = 0; i < 420; i++) {
      vec3 pm = ro + rd * tq;
      pm.y += farOffC(pm, ro);
      if (tq > sceneT || tq > 80000.0) break;
      if (altOf(pm) < uBase + 150.0) {
        vec4 cm = column(pm.xz);
        float rk = fract(length(pm.xz - uRingC.xz) / 500.0);
        gl_FragColor = vec4(vec3(cm.w, cm.x, step(0.94, rk)) * 0.6, 0.4);
        return;
      }
      tq *= 1.02;
    }
  }
#endif
  // slab intersection (curved)
  float topMax = uTop + max(uWisp, 160.0) + 40.0;
  float camAlt = altOf(ro);
  float t0 = 1e9, t1 = -1.0;
  // far-field dip (common.js FARDIP): the march runs along the image-space ray and samples the undipped
  // cloud field (p.y + farOff); the slab range is the union of the plain and the fully dipped ray
  for (int k = 0; k < 2; k++) {
    vec3 rk = rd; float kk = 1.0;
    if (k == 1) { if (uFarDip == 0.0) break; rk = vec3(rd.x, rd.y + uFarDip * length(rd.xz), rd.z); kk = length(rk); rk /= kk; }
    vec2 tt = solveAlt(ro, rk, topMax) / kk;
    vec2 tb = solveAlt(ro, rk, uBase) / kk;
    float a0, a1;
    if (camAlt > topMax) { a0 = tt.x; a1 = tt.y; }
    else { a0 = 0.0; a1 = tt.y; }
    if (camAlt > uBase) { if (tb.x > 0.0 && tb.x < 1e8) a1 = min(a1, tb.x); }
    else { a0 = max(a0, tb.y); }
    if (a1 > a0 && a0 < 1e8) { t0 = min(t0, a0); t1 = max(t1, a1); }
  }
  t0 = max(t0, 0.0);
  t1 = min(min(t1, sceneT), 90000.0);
  vec3 col = vec3(0.0);
  float T = 1.0;
  float depthAcc = 0.0, wAcc = 0.0;
  if (t1 > t0 && t0 < 1e8) {
    // per-pixel jitter fixed over time (white-noise hash: interleaved gradient noise left its diagonal hatching on
    // the carved billows), stratified over the K sub-frames of a still / film frame by the van der Corput offset of
    // the sub-frame index (uJit): every video frame averages the same K offsets -> no flicker
    // (r5: a 64^2 blue-noise rank map instead: its error is high-frequency, which the composite's 3x3 tent removes;
    // the white-noise hash left visible grain on the billow rims)
    float ign = fract(texture2D(tBlue, (floor(gl_FragCoord.xy) + 0.5) / 64.0).r + uJit);
    // glow light: from the sunset horizon, a few degrees up
    vec3 Ld = normalize(vec3(uSunDir.x, 0.05, uSunDir.z));
    float cosV = dot(rd, Ld);
    // three scattering octaves (Wrenninge): fainter, softer, less forward each time
    float ph0 = mix(hg(cosV, 0.35), hg(cosV, -0.15), 0.35) * 4.0 * PI;
    float ph1 = mix(hg(cosV, 0.28), hg(cosV, -0.08), 0.35) * 4.0 * PI;
    float ph2 = 1.0;
    float span = t1 - t0;
    int N = uSteps;
    float baseStep = span / float(N);
    // the step grows with distance and in empty space; the jitter is applied inside every step (not once
    // at the start) so the sample positions stay decorrelated between pixels -> no contour banding.
    // At the first contact with a cloud the march backs up one step and resolves the next ~60 m in fine steps
    // (~4 px footprint): crisp billows even through the long lenses, whose normal step is 15-30 m
    float t = t0, stepK = 1.0, tc = t0, fineEnd = -1.0, fineCap = -1.0, tS = -1e9;
    vec3 Sp = vec3(0.0);
    bool armed = true;
    for (int i = 0; i < 400; i++) {
      if (i >= N || tc > t1 || T < 0.015) break;
      // (r8: beyond 4 km the step grows faster - the rays grazing the far sea toward the horizon were half the march cost
      // of a free camera above the tops; there the sea is a few pixels high and hazed)
      float fsx = max(tc - 4000.0, 0.0);
      float dtN = clamp(baseStep, max(3.0, tc * 0.0025 + fsx * 0.01), 6.0 + tc * 0.006 + fsx * 0.02);
      // (p2: fine steps ~4 px instead of 8, and a ramp ~1.1 of them (below): crisp lobe silhouettes that the jittered
      // samples still resolve - with a ramp under one step the thin tops sampled as noise)
      float dtF = clamp(4.0 * tc * uPixA, 1.5, dtN);
      float dt = tc < fineEnd ? dtF : dtN * stepK;
      float tp = tc;
      t = tc + dt * ign;
      tc += dt;
      if (t > t1) break;
      vec3 p = ro + rd * t;
      p.y += farOffC(p, ro);
      float far = smoothstep(7000.0, 26000.0, t);
      // (p2: the noise LOD and the density ramp follow the fine step at this distance, not the current step: with the
      // current one the density field changed where the fine stretch after a contact ended - at grazing angles that
      // edge showed as contour stripes over the tops, view 4)
      float lod = clamp(log2(max(dtF, 1.0) / 14.0), 0.0, 5.0);
      gFp = t * uPixA;
      // erosion depth and density ramp: crisp billows near the camera (the ramp ~1-3 px), wider where the step
      // or the pixel footprint grows (no slicing, no sub-pixel detail)
      // (r5: deeper carve, crisper ramp ~5 px: the billows read at 100%)
      // (p2: ramp ~3.5 px / 0.8 step: the lobes' edges are crisp)
      // (r8: uR8 - the relief depth and a world-space minimum ramp: seen from 30-100 m the cloud is soft fog with
      // torn edges, not a hard surface; and less dense - a ~25 m mean free path, translucent edges and veils)
      gSkin = max(max(uR8.w, 9.6 * gFp), 0.96 * dtF);
      // (r9: x uR10b.y near the camera (fading out with the density gain): the near tops' edges ~1.5-2.5 px of the
      // half-resolution march instead of ~4, crisp where the denser near field keeps the jittered samples quiet)
      float nf = 1.0 - smoothstep(uR10.y, uR10.z, t);
      // (r9 p2: that factor fades out by uR10e.x m instead (>= uR10.z): the 0.5-3 km sea under the ring / glazing had ~9 px
      // soft rims - cotton balls)
      gRamp = max(max(uR8.z, 4.4 * gFp), 1.1 * dtF) * mix(1.0, uR10b.y, 1.0 - smoothstep(uR10.y, max(uR10e.x, uR10.z), t)) + t * 0.0006;
      gFarL = smoothstep(1200.0, 6000.0, t);
      // the AI refs' sea reads denser and crisper than a physically thin stratocumulus seen from ~1 km
      // (p2: x1.35 more: a ~10 m mean free path in the body, so lobes of 10-40 m read as solid rounded forms; the veils,
      // wisps and torn edges keep their low densities)
      // (r9: x uR10.x within ~0.3 km, fading out by ~1.4 km - a ~5 m mean free path on the near tops: their billows, turrets
      // and fringes read as crisp forms, not as a fog that blurs every relief under it; smooth in t: no popping in motion)
      float gB0 = uR8.y * mix(1.0, 0.67, smoothstep(1500.0, 7000.0, t)), gN = mix(uR10.x, 1.0, smoothstep(uR10.y, uR10.z, t));
      gBoost = gB0 * gN;
      vec4 cc = columnC(p.xz);
      float bk = gBankC, topB = gTopB;
      float dens = densityC(p, cc, bk, lod, far, 3);
      float tw = gTw;
      if (armed && dens > 0.0015 && uRefine > 0.5) {
        armed = false;
        fineEnd = tp + dt + 40.0; fineCap = tp + 120.0;
        if (dt > 1.5 * dtF) { tc = tp; stepK = 1.0; continue; }
      }
      // (p2: thin cloud keeps the fine steps, up to 120 m past the contact: coarse steps through it undersampled the
      // 13-54 m octave - a 1-2 px stipple over the thin, far tops of views 5 / 6. Like the near-top steps below, only
      // while half the step budget is left: the grazing long-lens rays of view 4 ran out of steps - a clear band with a
      // hard edge under the ring)
      bool rich = i < N / 2;
      if (rich && dens > 0.0015 && dens < 0.35 * gBoost * uDensity) fineEnd = max(fineEnd, min(tc + dtF, fineCap));
      // thin wisps and veils near a lit sample reuse its light (most of the march cost is the light samples)
      bool reuse = dens < 0.06 && t - tS < max(50.0, 0.012 * t);
      if (dens > 0.0015 && reuse) {
        float Ts = exp(-dens * uExt * dt);
        col += T * (Sp - Sp * Ts);
        depthAcc += t * T * (1.0 - Ts); wAcc += T * (1.0 - Ts);
        T *= Ts;
      }
      if (dens > 0.0015 && !reuse) {
        float alt = altOf(p);
        float hAO = gH, cav = gCav;
        // (r9 p2) near field: the clefts between the lobes see a narrow cone of the dome and none of the low glow
        // (at most 0.75: a cleft still sees a cone of the dome - with all of it gone the ring's warm light left brown smudges)
        float cavM = min(gCavM * uR10d.x * nf, 0.75);
        // (r9) light contrast of the fine relief (2-56 m and, near, ~0.4-1.8 m; the light samples 6-30 m off do not resolve
        // it): turrets pushed out of the surface catch the sky and the glow, the clefts between them are shaded - texture
        // in the light at every scale, not only in the outline; 1 where the detail is not resolved (far)
        float fsh = clamp(1.0 + (gFd - 0.5) * 2.0 * uR10b.x, 0.35, 1.25);
        // (r9) and its slope as a bump normal (uR10b.z: strength; 2 extra fetch pairs, only on the near shell): each turret
        // is sky-lit on top and toward the glow, shaded on its far side - rounded forms instead of flat dark stains where
        // the denser near field shows the relief (from the samples' current gEm / gFp: those of the primary)
        float fshU = 1.0, fshL = 1.0;
        if (uR10b.z > 0.0 && gBfE < 3.0 * gRamp + 6.0) {
          vec3 pw = p - vec3(uWindDir.x, 0.0, uWindDir.y) * (uTime * uWindV);
          float h = max(1.0, 3.0 * gFp);
          vec2 g = (vec2(fineF(pw + vec3(h, 0.0, 0.0)), fineF(pw + vec3(0.0, 0.0, h))) - gFf) * (uR9.x * uR10b.z / h);
          vec3 n = normalize(vec3(-g.x, 1.0, -g.y));
          float sw = 1.0 - smoothstep(gRamp, 3.0 * gRamp + 6.0, gBfE);
          fshU = mix(1.0, 0.4 + 0.7 * n.y, sw);
          fshL = mix(1.0, clamp((dot(n, Ld) + 0.6) / (Ld.y + 0.6), 0.25, 1.8), sw);
        }
        // (r9) the light samples see uR10b.w of the near density gain (0: the r8 density): with the full gain the first
        // up sample 6 m over a near top was either clear or black - hard-edged dark stains (camouflage) over the near tops
        gBoost = gB0 * mix(1.0, gN, uR10b.w);
        float lodL = lod + 1.0;
        // optical depth toward the glow: 7 m (coarse + mid erosion: lobe self-shadowing) and 30 m (coarse) in the same
        // column, then ~80-280 m (the neighbouring heaps)
        // (p2: 7 m with the mid octave instead of 13 m coarse-only: each 10-40 m lobe shades its own far side)
        // (r8: deep in the ray (T < 0.2: under 20% of what is left reaches the camera) the light samples skip the relief)
        int lq = uLQ > 0.5 && T > 0.2 ? 2 : 0, lq1 = uLQ > 0.5 && T > 0.2 ? 1 : 0;
        float odL, odU = 0.0;
        int nU = uLite > 0.5 ? 2 : 3;
        if (t > 6000.0) {
          // (r8) light LOD beyond 6 km (the grazing rays over the far sea were most of the frame cost): 2 glow samples and
          // 1 sky sample without relief - their lobes are a few pixels there
          odL = densityC(p + Ld * 30.0, cc, bk, lodL + 1.0, far, 0) * 48.0 + density(p + Ld * 170.0, lodL + 1.0, far, 0) * 200.0;
          odU = densityC(p + vec3(0.0, 20.0, 0.0), cc, bk, lodL + 1.0, far, 0) * 54.0;
        } else {
          odL = densityC(p + Ld * 7.0, cc, bk, lodL, far, lq) * 14.0 + densityC(p + Ld * 30.0, cc, bk, lodL, far, lq1) * 34.0
              + density(p + Ld * 170.0, lodL + 1.0, far, 0) * 200.0;
          // optical depth toward the sky (up) and toward the ground (down): same column
          // (p2: the first up sample at 6 m sees the mid octave: sky-lit lobe crowns over shadowed bellies - the cauliflower)
          float sp = 0.0, sl = 12.0;
          // (r8 p2: the first up sample sees the fine detail (uFineL; the sky light is most of the light at blue hour) -
          // the glow sample does not: it cost ~15% of a low pass)
          for (int j = 0; j < 3; j++) { if (j >= nU) break; gFL = j == 0 ? uFineL : 0.0; odU += densityC(p + vec3(0.0, sp + 0.5 * sl, 0.0), cc, bk, lodL, far, j == 0 ? lq : 0) * sl; sp += sl; sl *= 3.4; }
          gFL = 0.0;
          if (nU == 2) odU *= 1.35;
        }
        float odD = uLite > 0.5 ? 40.0 * (1.0 - hAO) : densityC(p - vec3(0.0, 55.0, 0.0), cc, bk, lodL, far, 0) * 110.0;
        float e = uExt;
        // sky dome: single + multiple scattering tail
        // chromatic: light that diffuses deep into the layer (and into troughs) is the blue zenith light
        vec3 chro = vec3(1.25, 1.08, 0.82);
        // (r5: x2.0 extinction toward the sky: the clefts under the billow crowns read darker)
        // (r9 p2: the diffuse tail x uR10d.z near the camera - at 0.2 the shaded flanks of the near tops never got darker
        // than L* ~35, a milky lilac)
        float tl = 0.2 * mix(1.0, uR10d.z, nf);
        vec3 skyVis = exp(-odU * e * 2.0 * chro) * (1.0 - tl) + exp(-odU * e * 0.2 * chro) * tl;
        float botVis = exp(-odD * e * 0.6);
        // heap tops see the whole dome, flanks and troughs much less of it; so do the clefts between the billows
        // (p2: the torn walls of a sight window see the dome like a heap edge, not like a deep trough: no dark curtains)
        hAO = mix(hAO, max(hAO, 0.8), tw);
        // (r8: the flank of a bank still sees about half the dome - its floor and the exponent soften with uR8)
        // (r8 p2: that floor x uR9b.x ~0.4 - 6-9%: with 14-22% the shaded flanks never got darker than L* 22-29; the refs'
        // undersides are deep blue-slate)
        skyVis *= mix(mix(vec3(0.03, 0.05, 0.09), vec3(0.14, 0.17, 0.22) * uR9b.x, uR8.x), vec3(1.0), pow(hAO, mix(4.0, uR8b.w, uR8.x))) * (1.0 - 0.6 * cav) * (1.0 - cavM);
        // (r5) troughs: below the tops around (topB, ~0.3 km mean) the cloud sees little of the dome and no glow -
        // navy clefts between the lit rolls (p2: darker, less blue - the refs' clefts are near-black slate)
        // (r8: measured on the rolled surface, not the sample: the billow relief carves 50-80 m into every top, and the
        // carved crowns read as troughs - the whole sea turned navy from above; only real troughs between banks, and
        // to ~0.5 of the light (uR8.x: the r5 darkening otherwise))
        float tro = mix(sat((topB + 40.0 - alt) / 100.0), 0.6 * sat((topB - 30.0 - gSurf) / 120.0), uR8.x) * (1.0 - tw);
        skyVis *= mix(vec3(1.0), vec3(0.10, 0.115, 0.14), tro);
        // gorge walls hide most of the dome from the cloud deep in the cleft under / in front of the ring
        // (the bank there reads darker and deeper, like the clouds below the ring in the refs)
        if (length(p.xz - uRingC.xz) < 1500.0) {
          // (the walls across the gorge axis: the cleft runs along the hero azimuth)
          vec2 ax = vec2(-uHeroDir.y, uHeroDir.x) * 110.0;
          float oc = sat((terrH(p.xz + ax) - alt) / 110.0) + sat((terrH(p.xz - ax) - alt) / 110.0);
          // (the bank right under the deck, seen through the void from above, keeps lit tops)
          skyVis *= max(1.0 - 0.36 * oc * mix(1.0, 0.35, smoothstep(330.0, 200.0, length(p.xz - uRingC.xz))), 0.2);
        }
        vec3 S = uAmbTop * skyVis * fsh * fshU + uAmbBot * (0.3 + 0.5 * botVis);
        // horizon glow, 3 octaves (the low glow barely reaches into the troughs between heaps)
        float g0 = exp(-odL * e), g1 = exp(-odL * e * 0.35), g2 = exp(-odL * e * 0.12);
        float powder = 1.0 - exp(-dens * e * 50.0);
        // (r8 p2: the multiple-scattering octaves x uR9b.w - their isotropic glow tinted the whole sea mauve; the glow
        // rims the tops that face it and the thin edges toward it: a forward lobe (silver lining, uR9b.y) through
        // what little cloud lies toward the glow)
        float silver = uR9b.y * hg(cosV, 0.8) * 4.0 * PI * g0 * (1.0 - 0.6 * powder);
        // (r9 p2) near field: the glow (a band a few degrees over the horizon) reaches only what sees the sky - the creases and
        // shaded flanks keep the blue sky light (blue-slate), not a glow tint (brownish-pink); uR10c.w: its gain there (mauve)
        // (uR10f.x: everywhere - the low flanks of the heaps 1-3 km out caught the glow through their thin edges: pink vertical
        // smoke plumes; the warm light stays on the tops that face it)
        float gN2 = mix(1.0, sat(skyVis.g * 1.15), max(uR10c.z * nf, uR10f.x)) * mix(1.0, uR10c.w, nf) * (1.0 - cavM) * (1.0 - cavM);
        S += uGlowCol * (g0 * ph0 + (0.35 * g1 * ph1 + 0.12 * g2 * ph2) * uR9b.w + silver) * mix(0.6, 1.0, powder) * mix(mix(0.03, 0.2, uR8.x), 1.0, hAO * hAO) * (1.0 - 0.4 * cav) * (1.0 - 0.8 * tro) * fsh * fshL * gN2;
        // towns below light the undersides; diffuses upward through the layer
        // (focused term right above the lights + a ~2.5 km spread that reaches the gap edges: peach rims)
        vec2 tuv = p.xz / uTownSize + 0.5;
        float town = texture2D(tTown, tuv).r, townW = texture2D(tGlowW, tuv).r;
        S += uTownCol * (town * town + 0.3 * townW * townW) * exp(-max(alt - uBase, 0.0) / 140.0) * (0.3 + 0.7 * botVis);
        // the ring's warm light (torus light at the soffit level)
        vec3 rp = p - uRingC;
        float rr = length(rp.xz);
        vec2 dq = vec2(rr - 50.0, rp.y);
        float d2 = dot(dq, dq);
        S += uWarm * uRingI / (d2 + 900.0) * exp(-sqrt(d2) / 220.0);
        Sp = S; tS = t;
        float sig = dens * e;
        float Ts = exp(-sig * dt);
        col += T * (S - S * Ts);
        float contrib = T * (1.0 - Ts);
        depthAcc += t * contrib; wAcc += contrib;
        T *= Ts;
      }
      // humid blue-violet haze inside the cloud layer: the far sea and valleys fade into it
      float Th = exp(-uHaze * dt);
      col += T * uHazeCol * (1.0 - Th);
      depthAcc += t * T * (1.0 - Th); wAcc += T * (1.0 - Th);
      T *= Th;
      // (p2: in clear air within ~80 m of the lumpy top the step stays ~2 fine steps, not uSkip x the coarse one: thin
      // lumps on the tops were hit or missed by the stretched steps depending on the pixel's fixed jitter rank - a
      // stipple over the far tops of views 5 / 6); only within 5 km: the grazing long-lens rays of view 4 skim the tops
      // for 10+ km and ran out of steps (a hard horizontal cut)
      stepK = dens > 0.0015 ? 1.0 : (gFree < 80.0 && t < 5000.0 && rich ? min(1.0, 2.0 * dtF / dtN) : uSkip);
      // (r5: re-armed as soon as the fine stretch ends in clear air: every billow of a rolling surface gets its fine
      // steps - armed once per ray, the later billows were sampled at the coarse step and showed as grain)
      if (!armed && dens <= 0.0015 && tc > fineEnd) armed = true;
      // empty-space skip well above the cloud surface: the clear height allows a jump, assuming the ray's descent plus
      // 0.3 m/m (tops can rise between columns) and ignoring the dip unless it is fully on (it only slows descent)
      if (dens <= 0.0015 && gFree > 100.0) {
        float rate = rd.y + (length(p.xz - ro.xz) > uDipWin.y ? uFarDip * length(rd.xz) : 0.0);
        tc = max(tc, tp + min((gFree - 70.0) / (max(-rate, 0.0) + 0.3), 250.0));
      }
    }
    // (r9 p2) ground inside the cloud: the march ends on it, and where a ridge lies just under the tops only a few metres of
    // cloud were left in front of it - its forest stipple and ridge lines showed through the closed sea. The rest of the ray
    // is closed with the cloud's density at the ground point, or in the lid 15 / 40 m over it (a ridge in a clear pocket under a
    // thin lens), over uR10d.y m, lit like the last lit sample (0 above the tops and in the gaps: the ground there and the walls
    // above the sea keep their look)
    if (uR10d.y > 0.0 && sceneT < 1e8 && t1 > sceneT - 1.0 && T > 0.015 && tS > -1e8) {
      vec3 pE = ro + rd * (sceneT - 1.5);
      pE.y += farOffC(pE, ro);
      gFp = sceneT * uPixA;
      float lodE = clamp(log2(max(4.0 * gFp, 1.0) / 14.0), 0.0, 5.0), farE = smoothstep(7000.0, 26000.0, sceneT);
      float dE = max(density(pE, lodE, farE, 1), max(density(pE + vec3(0.0, 15.0, 0.0), lodE, farE, 1),
                     density(pE + vec3(0.0, 40.0, 0.0), lodE, farE, 1)) * uR10e.w);
      float Tc = exp(-dE * uExt * uR10d.y * smoothstep(9000.0, 5000.0, sceneT));
      col += T * (Sp - Sp * Tc);
      depthAcc += sceneT * T * (1.0 - Tc); wAcc += T * (1.0 - Tc);
      T *= Tc;
    }
  }
  // aerial perspective over the clouds
  if (wAcc > 1e-4) {
    float dAvg = depthAcc / wAcc;
    vec3 pAvg = ro + rd * dAvg;
    vec3 fogged = applyAtmos(col / max(1.0 - T, 1e-4), ro, pAvg);
    col = fogged * (1.0 - T);
  }
  gl_FragColor = vec4(col, T);
}
`;

// Composite + undercast: ground and air under the cloud sea only see the dome through the gaps, so the sky-lit
// (blue-grey) part of the scene below the base is darkened with the cover overhead and the depth below the base;
// the warm part (lamps, their pools and reflections) is kept.
const compFrag = /* glsl */ `
varying vec2 vUv;
uniform sampler2D tScene;
uniform sampler2D tCloud;
uniform sampler2D tDepth;
uniform mat4 uInvProj;
uniform mat4 uCamWorld;
uniform vec3 uCamPos;
uniform float uLogFar;
uniform vec3 uUnder;         // x: sky light left under full cover, y: share of that darkening in open gaps, z: lake share
uniform vec3 uSkyTint;       // max r/b, g/b of the sky-lit scene (fog, snow, rock): the part that is darkened
uniform vec2 uTexel;         // cloud target texel
uniform float uSharp;        // (r8 p2) falloff of the reconstruction tent (1.3: the r5 Gaussian)
uniform vec2 uPhase;         // (r8 p2) sub-pixel phase (uv) of the march of this sub-frame
${FARDIP}
${COLUMN}
void main(){
  float dep = texture2D(tDepth, vUv).r;
  // reconstruction: depth-aware 3x3 tent over the cloud target (the per-pixel march jitter left salt-and-pepper
  // speckle on the cloud edges); taps across a depth edge (ring, ridge silhouettes) are rejected
  // (p2: a Gaussian of sigma 0.75 px (centre 30%) instead of the 4:2:1 tent (centre 25%) plus the outlier clamp below)
  // (and the centre is first clamped to the range of its same-surface neighbours: a lone outlier - the jitter residue
  // in thin translucent cloud - is removed, texture that spans 2+ px is kept)
  // (r8 p2: the cloud texels are read back at the phase of their march, uPhase)
  vec2 uvC = vUv - uPhase;
  vec4 c = vec4(0.0), c0 = texture2D(tCloud, uvC), lo = vec4(1e9), hi = vec4(-1e9); float wsum = 0.0;
  for (int j = -1; j <= 1; j++) for (int i = -1; i <= 1; i++) {
    if (i == 0 && j == 0) continue;
    vec2 o = vec2(float(i), float(j)) * uTexel;
    float wd = exp2(-abs(texture2D(tDepth, vUv + o).r - dep) * uLogFar * 6.0);
    vec4 cs = texture2D(tCloud, uvC + o);
    if (wd > 0.5) { lo = min(lo, cs); hi = max(hi, cs); }
    // (r8 p2: uSharp - narrower when the march runs below the frame resolution: the tent over half-resolution texels was a
    // ~3 px blur at 1080p; the K film sub-frames average the march jitter instead)
    float w = exp2(-float(i * i + j * j) * uSharp) * wd;
    c += cs * w; wsum += w;
  }
  c0 = hi.a > -1e8 ? clamp(c0, lo, hi) : c0;
  c = (c + c0) / (wsum + 1.0);
  vec3 s = texture2D(tScene, vUv).rgb;
  if (dep < 0.9999 && c.a > 0.003) {
    vec4 vv = uInvProj * vec4(vUv * 2.0 - 1.0, 1.0, 1.0); vv /= vv.w;
    vec3 dv = normalize(vv.xyz);
    float st = (exp2(dep * uLogFar) - 1.0) / max(-dv.z, 1e-4);
    vec3 p = uCamPos + normalize(mat3(uCamWorld) * dv) * st;
    p.y += farOffC(p, uCamPos);   // (the far field is drawn dipped: undo it)
    float alt = altOf(p);
    if (alt < uTop + 200.0) {
      // cover and cloud top overhead, averaged over ~1 km (the dome the ground sees through a gap is a wide cone)
      vec4 c0 = columnC(p.xz) * 0.4 + (columnC(p.xz + vec2(390.0, 225.0)) + columnC(p.xz + vec2(-390.0, 225.0))
              + columnC(p.xz - vec2(0.0, 450.0))) * 0.2;
      float cv = c0.x;
      // under the sea (below the base) or under the bank / heaps (below the mean top around, e.g. a slot floor
      // seen through a hole in the bank under the deck)
      float dz = max(smoothstep(uBase + 60.0, uBase - 300.0, alt), smoothstep(-40.0, 160.0, c0.y - alt) * smoothstep(0.3, 0.6, cv));
      dz *= mix(uUnder.z, 1.0, smoothstep(568.0, 590.0, alt));
      float sh = 1.0 - (1.0 - uUnder.x) * dz * mix(uUnder.y, 1.0, smoothstep(0.2, 0.65, cv));
      // sky-lit part: up to uSkyTint x blue in each channel (fog, snow, rock); the warm excess is lamp light
      vec3 sky = min(s, max(s.b, 0.0) * uSkyTint);
      // (what is left of the sky light down there is the diffuse zenith blue through the deck: navy, not mauve)
      // (p2: a darker, less blue tint: the refs' valley floor under the sea is near-black slate, L* 10-14)
      s += sky * (sh * mix(vec3(1.0), vec3(0.72, 0.82, 0.95), dz) - 1.0);
    }
  }
  gl_FragColor = vec4(s * c.a + c.rgb, 1.0);
}
`;

async function bin(url) { const r = await fetch(url); return new Uint8Array(await r.arrayBuffer()); }

// march jitter per sub-frame: stills and film frames (main.js renderStill / renderFrame) jitter the camera by
// (halton(k+1, 2) - 0.5, halton(k+1, 3) - 0.5) px for sub-frame k = 0..K-1, so k is recovered from the view offset
// and the march offset is the van der Corput radical inverse of k: any K sub-frames are stratified and every film
// frame averages the same K offsets. Without a view offset (interactive, K=1): cycle over 4 frames.
const halton = (i, b) => { let f = 1, r = 0; while (i > 0) { f /= b; r += f * (i % b); i = Math.floor(i / b); } return r; };
const HALT = Array.from({ length: 256 }, (_, k) => [halton(k + 1, 2) - 0.5, halton(k + 1, 3) - 0.5]);
function subFrame(camera, frame) {
  const v = camera.view;
  if (!v || !v.enabled) return frame % 4;
  for (let k = 0; k < HALT.length; k++) if (Math.abs(HALT[k][0] - v.offsetX) < 1e-6 && Math.abs(HALT[k][1] - v.offsetY) < 1e-6) return k;
  return frame % 4;
}
const vdc = k => halton(k, 2);
const PHASE = [[-1, -1], [1, 1], [1, -1], [-1, 1]];   // (r8 p2) march phases (cloud texels / 4) of marches 0..3 of a frame

// 64^2 blue-noise ranks by void-and-cluster (Ulichney 1993; Gaussian sigma 1.5, toroidal), ~0.1 s at load
function blueNoise(n = 64) {
  const N = n * n, K = new Float32Array(N), E = new Float32Array(N), on = new Uint8Array(N), rank = new Float32Array(N);
  for (let y = 0; y < n; y++) for (let x = 0; x < n; x++) {
    const dx = Math.min(x, n - x), dy = Math.min(y, n - y);
    K[y * n + x] = Math.exp(-(dx * dx + dy * dy) / (2 * 1.5 * 1.5));
  }
  const flip = (i, s) => { on[i] = s > 0 ? 1 : 0; const ix = i % n, iy = (i / n) | 0;
    for (let y = 0; y < n; y++) { const ky = ((y - iy + n) % n) * n, ry = y * n; for (let x = 0; x < n; x++) E[ry + x] += s * K[ky + (x - ix + n) % n]; } };
  const tight = () => { let b = -1, m = -1e9; for (let i = 0; i < N; i++) if (on[i] && E[i] > m) { m = E[i]; b = i; } return b; };
  const voidp = () => { let b = -1, m = 1e9; for (let i = 0; i < N; i++) if (!on[i] && E[i] < m) { m = E[i]; b = i; } return b; };
  let seed = 12345; const rnd = () => (seed = (seed * 1664525 + 1013904223) >>> 0) / 4294967296;
  const n0 = Math.round(N * 0.1);
  for (let k = 0; k < n0;) { const i = Math.floor(rnd() * N); if (!on[i]) { flip(i, 1); k++; } }
  for (let it = 0; it < 4 * N; it++) { const c = tight(); flip(c, -1); const v = voidp(); if (v === c) { flip(c, 1); break; } flip(v, 1); }
  const init = on.slice(), Ei = E.slice();
  for (let r = n0 - 1; r >= 0; r--) { const c = tight(); flip(c, -1); rank[c] = r; }
  on.set(init); E.set(Ei);
  for (let r = n0; r < N; r++) { const v = voidp(); flip(v, 1); rank[v] = r; }
  for (let i = 0; i < N; i++) rank[i] = (rank[i] + 0.5) / N;
  const t = new THREE.DataTexture(rank, n, n, THREE.RedFormat, THREE.FloatType);
  t.magFilter = t.minFilter = THREE.NearestFilter; t.wrapS = t.wrapT = THREE.RepeatWrapping; t.needsUpdate = true;
  return t;
}

function boxBlur(a, n, r) {
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

// lake-shore window map: the town light map blurred to ~1 km (r=5 px of 98 m), normalised;
// r=14 gives the ~2.5 km spread of town light onto the cloud bases around the gaps
function windowTex(townTex, r = 5, k = 0.6) {
  const src = townTex.image.data, n = townTex.image.width;
  const a = Float32Array.from(src);
  boxBlur(a, n, r); boxBlur(a, n, r); boxBlur(a, n, r);
  let mx = 0; for (let i = 0; i < a.length; i++) mx = Math.max(mx, a[i]);
  for (let i = 0; i < a.length; i++) a[i] = Math.min(1, a[i] / (mx * k + 1e-6));
  const t = new THREE.DataTexture(a, n, n, THREE.RedFormat, THREE.FloatType);
  t.magFilter = t.minFilter = THREE.LinearFilter; t.needsUpdate = true;
  return t;
}

// Line-of-sight windows: the hero cameras with the far-field dip (views 7, 11, 4, 5, 6, 2) see the lakeshore towns
// through 2-3 gaps in the sea (ref 7). CLOUDS.sight.sets: each set picks the lights inside the lower frame (below the
// ring) of its view, in distance bands [km from that camera, km, disk radius m]; each band's window targets the
// light-weighted centre of its lights, and a disk around it is traced back to each camera of the set through the
// layer (1470-1960 m, undipped like the march: the line of sight crosses it 1-5 km out on a long slant), splatted
// every 20 m into a 12 km map (25 m texels). R: lane strength (each window normalised to 1), G: altitude of the
// sight line there (densityC carves a tube around it: a hole the size of the target, not a radial slot down the frame).
async function sightTex() {
  const L = new Float32Array(await (await fetch('./data/terrain/lights.f32')).arrayBuffer());
  const n = 480, size = 12000;
  const sm = (e0, e1, x) => { const t = Math.min(1, Math.max(0, (x - e0) / (e1 - e0))); return t * t * (3 - 2 * t); };
  const W0 = 600, W1 = 1800, asp = 1672 / 941;   // uDipWin (main.js), the refs' aspect
  const cam = v => {
    const p = refToWorld(VIEWS[v].pos), f = refToWorld(VIEWS[v].tgt).sub(p).normalize();
    const r = new THREE.Vector3().crossVectors(f, new THREE.Vector3(0, 1, 0)).normalize();
    return { p, f, r, u: new THREE.Vector3().crossVectors(r, f), th: Math.tan(VIEWS[v].fov * Math.PI / 360), dip: VIEWS[v].dip || 0 };
  };
  const out = new Float32Array(n * n * 2), wA = new Float32Array(n * n), hA = new Float32Array(n * n), d = new THREE.Vector3();
  const tg = [], gate = [];
  for (const [si, set] of CLOUDS.sight.sets.entries()) {
    const c0 = cam(set.view), cams = set.cams.map(cam);
    gate.push({ pos: cams.map(c => c.p), r: set.r || 100 });
    for (const [b0, b1, rad] of set.bands) {
      // the band's lights in the lower frame of the set's view
      let sx = 0, sy = 0, sz = 0, sw = 0;
      for (let i = 0; i + 3 < L.length; i += 5) {
        const x = L[i], y = L[i + 1], z = L[i + 2], S = Math.hypot(x - c0.p.x, z - c0.p.z);
        if (S < b0 * 1000 || S > b1 * 1000) continue;
        d.set(x, y - c0.dip * S * sm(W0, W1, S), z).sub(c0.p);
        const zc = d.dot(c0.f);
        if (zc <= 0) continue;
        const px = (d.dot(c0.r) / zc / (c0.th * asp) + 1) / 2, py = (1 - d.dot(c0.u) / zc / c0.th) / 2;
        if (px < 0.15 || px > 0.81 || py < 0.51 || py > 1) continue;
        const w = L[i + 3] + 1e-3;
        sx += x * w; sy += y * w; sz += z * w; sw += w;
      }
      if (sw === 0) continue;
      const tx = sx / sw, ty = sy / sw, tz = sz / sw;
      tg.push([set.view, Math.round(tx), Math.round(tz)]);
      wA.fill(0); hA.fill(0);
      for (const c of cams) for (let j = -6; j <= 6; j++) for (let i = -6; i <= 6; i++) {
        if (i * i + j * j > 36) continue;
        const x = tx + i / 6 * rad, z = tz + j / 6 * rad, S = Math.hypot(x - c.p.x, z - c.p.z);
        const yd = ty - c.dip * S * sm(W0, W1, S);
        const hAt = s => c.p.y + (yd - c.p.y) * s / S + c.dip * s * sm(W0, W1, s);   // undipped height of the image ray
        const sOf = h => { let lo = 0, hi = S; for (let it = 0; it < 24; it++) { const m = (lo + hi) / 2; if (hAt(m) > h) lo = m; else hi = m; } return (lo + hi) / 2; };
        for (let s = sOf(1960), s1 = sOf(1470); s <= s1; s += 20) {
          const fx = ((c.p.x + (x - c.p.x) * s / S) / size + 0.5) * n - 0.5, fz = ((c.p.z + (z - c.p.z) * s / S) / size + 0.5) * n - 0.5;
          const ix = Math.floor(fx), iz = Math.floor(fz), u = fx - ix, v = fz - iz;
          if (ix < 0 || iz < 0 || ix >= n - 1 || iz >= n - 1) continue;
          const o = iz * n + ix, h = hAt(s), w00 = (1 - u) * (1 - v), w10 = u * (1 - v), w01 = (1 - u) * v, w11 = u * v;
          wA[o] += w00; wA[o + 1] += w10; wA[o + n] += w01; wA[o + n + 1] += w11;
          hA[o] += w00 * h; hA[o + 1] += w10 * h; hA[o + n] += w01 * h; hA[o + n + 1] += w11 * h;
        }
      }
      for (let k = 0; k < 3; k++) { boxBlur(wA, n, 2); boxBlur(hA, n, 2); }
      let mx = 0; for (let i = 0; i < wA.length; i++) mx = Math.max(mx, wA[i]);
      for (let i = 0; i < wA.length; i++) {
        const w = wA[i] / (mx + 1e-9);
        // (G: the sight-line altitude + 4000 m x the set index: densityC switches each set's tubes by uSightOn)
        if (w > out[i * 2]) { out[i * 2] = w; out[i * 2 + 1] = hA[i] / (wA[i] + 1e-9) + 4000 * si; }
      }
    }
  }
  console.log(`clouds: sight windows [view, x, z] ${JSON.stringify(tg)}`);
  const t = new THREE.DataTexture(out, n, n, THREE.RGFormat, THREE.FloatType);
  t.magFilter = t.minFilter = THREE.LinearFilter; t.needsUpdate = true;
  return { tex: t, size, gate };
}
// heightfield 8 km around the ring at 12.5 m: L2, with the carved L3 gorge/pinnacles inside its 1.6 km
async function terrainTex() {
  const meta = await (await fetch('./data/terrain/meta.json')).json();
  const get = async lv => ({ H: new Float32Array(await (await fetch(`./data/terrain/${lv.name}.f32`)).arrayBuffer()), g: lv.grid, size: lv.size });
  const [L2, L3] = await Promise.all([get(meta.LEVELS[2]), get(meta.LEVELS[3])]);
  const sample = (L, x, z) => {
    const fx = (x / L.size + 0.5) * (L.g - 1), fz = (z / L.size + 0.5) * (L.g - 1);
    if (fx < 0 || fz < 0 || fx >= L.g - 1 || fz >= L.g - 1) return null;
    const i = Math.floor(fx), j = Math.floor(fz), u = fx - i, v = fz - j, a = j * L.g + i, H = L.H;
    return (H[a] * (1 - u) + H[a + 1] * u) * (1 - v) + (H[a + L.g] * (1 - u) + H[a + L.g + 1] * u) * v;
  };
  const n = 640, size = L2.size, a = new Float32Array(n * n);
  for (let j = 0; j < n; j++) for (let i = 0; i < n; i++) {
    const x = ((i + 0.5) / n - 0.5) * size, z = ((j + 0.5) / n - 0.5) * size;
    a[j * n + i] = sample(L3, x, z) ?? sample(L2, x, z) ?? 0;
  }
  const t = new THREE.DataTexture(a, n, n, THREE.RedFormat, THREE.FloatType);
  t.magFilter = t.minFilter = THREE.LinearFilter; t.needsUpdate = true;
  return { tex: t, size };
}

export class Clouds {
  static async create(renderer, shared, post, w, h, scale) {
    const c = new Clouds();
    const [shape, detail, weather, terr, curl, sight, billow] = await Promise.all([bin('./data/noise/shape128.bin'), bin('./data/noise/detail32.bin'),
      bin('./data/noise/weather512.bin'), terrainTex(), bin('./data/noise/curl128.bin'), sightTex(), bin('./data/noise/billow128.bin')]);
    // 8-bit noise is uploaded as half float: UNORM8 bilinear results are quantised to 1/255 on this
    // hardware, which terraced the heap tops (coverage and lumps have large gains) into contour bands
    const half = data => { const o = new Uint16Array(data.length); for (let i = 0; i < data.length; i++) o[i] = THREE.DataUtils.toHalfFloat(data[i] / 255); return o; };
    // (the erosion volume stays 8-bit: half the bandwidth of its 3 fetches per sample, and it has no large gains)
    const t3 = (data, n, hf = true) => {
      const t = new THREE.Data3DTexture(hf ? half(data) : data, n, n, n);
      t.format = THREE.RGBAFormat; t.type = hf ? THREE.HalfFloatType : THREE.UnsignedByteType;
      t.wrapS = t.wrapT = t.wrapR = THREE.RepeatWrapping;
      t.minFilter = THREE.LinearMipmapLinearFilter; t.magFilter = THREE.LinearFilter;
      t.generateMipmaps = true; t.unpackAlignment = 1; t.needsUpdate = true;
      return t;
    };
    const wt = new THREE.DataTexture(half(weather), 512, 512, THREE.RGBAFormat, THREE.HalfFloatType);
    wt.wrapS = wt.wrapT = THREE.RepeatWrapping; wt.magFilter = THREE.LinearFilter; wt.minFilter = THREE.LinearMipmapLinearFilter; wt.generateMipmaps = true; wt.needsUpdate = true;
    c.renderer = renderer; c.post = post; c.scale = scale; c.sightGate = sight.gate;
    const lin = hex => { const k = new THREE.Color(hex); return new THREE.Vector3(k.r, k.g, k.b); }; // Color() already converts sRGB hex to linear
    const dbg = /[?&]cdbg/.test(location.search);
    c.mat = new THREE.ShaderMaterial({
      vertexShader: fsVert, fragmentShader: marchFrag, depthTest: false, depthWrite: false, defines: dbg ? { CLOUD_DBG: 1 } : {},
      uniforms: {
        ...shared.uniforms,
        tDepth: { value: null }, tShape: { value: t3(shape, 128) }, tDetail: { value: t3(detail, 32) }, tWeather: { value: wt },
        tCurl: { value: t3(curl, 128, false) }, uPixA: { value: 1e-3 }, uJit: { value: 0 }, tBlue: { value: blueNoise() },
        tBillow: { value: t3(billow, 128, false) }, uR8: { value: new THREE.Vector4(...CLOUDS.r8) }, uWindV: { value: CLOUDS.wind },
        uR8b: { value: new THREE.Vector4(...CLOUDS.r8b) }, uR8c: { value: new THREE.Vector4(...CLOUDS.r8c) },
        uR9: { value: new THREE.Vector4(...(CLOUDS.r9 || [0, 56, 0, 0])) }, uR9b: { value: new THREE.Vector4(...(CLOUDS.r9b || [1, 0, 60, 1])) },
        uFineL: { value: CLOUDS.fineL ?? 0 }, uPhase: { value: new THREE.Vector2(0, 0) },
        uR10: { value: new THREE.Vector4(...(CLOUDS.r10 || [1, 300, 1400, 0])) }, uR10b: { value: new THREE.Vector4(...(CLOUDS.r10b || [0, 1, 0, 1])) },
        uR10c: { value: new THREE.Vector4(...(CLOUDS.r10c || [0, 0, 0, 1])) }, uR10d: { value: new THREE.Vector4(...(CLOUDS.r10d || [0, 0, 1, 1])) },
        uR10e: { value: new THREE.Vector4(...(CLOUDS.r10e || [0, 0, 0, 0])) }, uR10f: { value: new THREE.Vector4(...(CLOUDS.r10f || [0, 0, 0, 0])) },
        uWindDir: { value: new THREE.Vector2(0.94, 0.34).normalize() }, uEro: { value: 1 }, uLQ: { value: 1 }, uRefine: { value: 1 }, uLite: { value: 1 },
        tSight: { value: sight.tex }, uSightSize: { value: sight.size }, uSightW: { value: CLOUDS.sight.w }, uHole: { value: 0 }, uWell: { value: CLOUDS.well ?? 1 },
        uSightOn: { value: new THREE.Vector2(1, 1) },
        tColA: { value: null }, tColB: { value: null }, uColSize: { value: new THREE.Vector2(2400, 24000) }, uColOn: { value: 0 },
        tTown: { value: shared.townGlow.tex }, uTownSize: { value: shared.townGlow.size },
        tWin: { value: windowTex(shared.townGlow.tex) }, tGlowW: { value: windowTex(shared.townGlow.tex, 14, 0.5) },
        tTerr: { value: terr.tex }, uTerrSize: { value: terr.size }, uTerrCov: { value: CLOUDS.terrCov ?? 0 },
        uInvProj: { value: new THREE.Matrix4() }, uCamWorld: { value: new THREE.Matrix4() }, uCamPos: { value: new THREE.Vector3() },
        uLogFar: { value: 1 }, uBase: { value: CLOUDS.base }, uTop: { value: CLOUDS.top },
        uCovBias: { value: CLOUDS.cov ?? 0.5 }, uCovScale: { value: 1.0 }, uDensity: { value: 1.0 }, uExt: { value: 0.05 }, uWin: { value: 0.35 },
        // (p2: 300 - the fine steps over thin cloud and next to the tops used up 200 on grazing rays, which then ended
        // short of the cloud: terrain showed through)
        uSteps: { value: 300 }, uFrame: { value: 0 },
        uRingC: { value: new THREE.Vector3(0, DECK_Y - 9, 0) }, uRingI: { value: 3500 },
        uWarm: { value: new THREE.Vector3(1.0, 0.56, 0.24) },
        // (r5: neutral grey-blue crowns; the clefts and troughs carry the navy. p2: greener and x1.1 - the crowns read
        // mauve (green the lowest channel) and ~8-15 L* too dark)
        // (r8: x1.5 and less blue - the free-camera sea measured L* p50 25-29 / p95 42-45 against the refs' 31-40 / 46-57,
        // and bluer (#364062 against #4a5270 .. #5a5f7a))
        // (r8 p2: steel blue '#6f7c94' x1.6 - with '#7f8290' the sea read lavender, R = G; the refs' G > R by 6-8)
        uAmbTop: { value: lin('#6f7c94').multiplyScalar(1.6) },
        // (r8 p2: x0.6 - with the sky floor x0.2 the shaded flanks reach L* ~10-15: deep blue-slate undersides)
        uAmbBot: { value: lin('#0e1830').multiplyScalar(0.6) },
        // (r5: x1.75, p2: x1.2 and less red - warm-neutral lit crowns; r8: x1.4 and pinker, less orange: the free-camera
        // tops read beige)
        uGlowCol: { value: lin('#f2a68e').multiplyScalar(0.1) },
        uTownCol: { value: lin('#ffb08a').multiplyScalar(0.6) },
        uEarthR: { value: EARTH_R },
        // (p2: fringe lumps x0.6 - at full strength the islands broke into a polka-dot carpet of round puffs)
        uComp: { value: new THREE.Vector4(1, 1, 1, 1) }, uComp2: { value: new THREE.Vector2(1, CLOUDS.fringe ?? 0.6) },
        uWisp: { value: 200 }, uHug: { value: 1 }, uDbg: { value: dbg ? 1 : 0 }, uSkip: { value: 1.8 },
        uHaze: { value: 3.0e-5 }, uHazeCol: { value: lin('#34455f') },
        uGapSeg: { value: new THREE.Vector4(...CLOUDS.gap.p0, ...CLOUDS.gap.p1) },
        uGapW: { value: new THREE.Vector3(CLOUDS.gap.w0, CLOUDS.gap.grow, CLOUDS.gap.k) },
        uGapSeg2: { value: new THREE.Vector4(...CLOUDS.gap.lake0, ...CLOUDS.gap.lake1) },
        uGapW2: { value: new THREE.Vector2(CLOUDS.gap.lakeW, CLOUDS.gap.lakeGrow) },
        uHeroDir: { value: new THREE.Vector2(Math.sin(HERO_AZ * Math.PI / 180), -Math.cos(HERO_AZ * Math.PI / 180)) },
      },
    });
    // (the composite shares the march uniforms by reference: layout, camera, depth)
    c.comp = new THREE.ShaderMaterial({
      vertexShader: fsVert, fragmentShader: compFrag, depthTest: false, depthWrite: false,
      uniforms: { ...c.mat.uniforms, tScene: { value: null }, tCloud: { value: null },
        uUnder: { value: new THREE.Vector3(0.22, 0.6, 0.55) }, uSkyTint: { value: new THREE.Vector3(0.7, 0.8, 1.0) },
        uTexel: { value: new THREE.Vector2(1, 1) }, uSharp: { value: 1.3 } },
    });
    // bake the static layout into the column atlas (COLUMN columnC); URL flag nocolcache: analytic column() everywhere
    const bake = new THREE.ShaderMaterial({ vertexShader: fsVert, fragmentShader: colFrag, depthTest: false, depthWrite: false,
      uniforms: { ...c.mat.uniforms, uWhich: { value: 0 } } });
    const atlas = () => {
      const t = new THREE.WebGLRenderTarget(2048, 1024, { type: THREE.HalfFloatType, depthBuffer: false });
      t.texture.minFilter = t.texture.magFilter = THREE.LinearFilter;
      return t;
    };
    c.colA = atlas(); c.colB = atlas();
    // (pass 1 reads the A tiles of pass 0; no atlas texture is bound while it is the render target)
    c.rebake = () => {
      const u = c.mat.uniforms;
      u.tColA.value = null; u.tColB.value = null;
      bake.uniforms.uWhich.value = 0; post.pass(bake, c.colA);
      u.tColA.value = c.colA.texture;
      bake.uniforms.uWhich.value = 1; post.pass(bake, c.colB);
      u.tColB.value = c.colB.texture;
    };
    c.rebake();
    c.mat.uniforms.tColA.value = c.colA.texture; c.mat.uniforms.tColB.value = c.colB.texture;
    c.mat.uniforms.uColOn.value = /[?&]nocolcache/.test(location.search) ? 0 : 1;
    c.timing = /[?&]ctime/.test(location.search);   // URL flag ctime: log the slowest march strip per frame
    c.reuse = !/[?&]nocreuse/.test(location.search);
    c.phase = (CLOUDS.phase ?? 0) && !/[?&]nocphase/.test(location.search);   // (r8 p2) URL flag nocphase: march phases off
    c.phaseFp = !!CLOUDS.phaseFp;
    c.setSize(w, h);
    return c;
  }
  setSize(w, h) {
    if (this.rt) this.rt.dispose();
    // (r8) CLOUDS.res: the march at a fraction of the frame's resolution (film budget); the composite upsamples it
    const s = this.scale * (CLOUDS.res || 1);
    this.rt = new THREE.WebGLRenderTarget(Math.round(w * s), Math.round(h * s), { type: THREE.HalfFloatType, depthBuffer: false });
    this.rt.texture.minFilter = this.rt.texture.magFilter = THREE.LinearFilter;
    this.comp.uniforms.uTexel.value.set(1 / this.rt.width, 1 / this.rt.height);
    this.comp.uniforms.uSharp.value = (CLOUDS.res || 1) < 1 ? (CLOUDS.sharp ?? 1.3) : 1.3;
    this.lastPose = null;
  }
  render(sceneRT, camera, t, frame = 0) {
    const u = this.mat.uniforms;
    u.tDepth.value = sceneRT.depthTexture;
    u.uInvProj.value.copy(camera.projectionMatrixInverse);
    u.uCamWorld.value.copy(camera.matrixWorld);
    u.uCamPos.value.copy(camera.position);
    u.uLogFar.value = Math.log2(camera.far + 1);
    u.uFrame.value = frame;
    // (r8 p2) with the march phases (below) the K sub-frames sample every full-resolution pixel: the noise LOD, the
    // density ramp and the fine steps can follow the full-resolution footprint (this.phaseFp; the march at half
    // resolution otherwise blurs the density field itself to its own texel, which the phases cannot recover)
    const fullFp = this.phase && this.phaseFp && camera.view && camera.view.enabled && sceneRT.height > 1.1 * this.rt.height;
    const pixA = 2 * Math.tan(camera.fov * Math.PI / 360) / Math.max(fullFp ? sceneRT.height : this.rt.height, 1);
    u.uPixA.value = pixA;
    // sight-window sets: on within r of one of the set's cameras, faded out over the next 40 m (film moves fade them)
    const on = this.sightGate.map(s => {
      let d = 1e9; for (const p of s.pos) d = Math.min(d, p.distanceTo(camera.position));
      return 1 - THREE.MathUtils.smoothstep(d, s.r, s.r + 40);
    });
    u.uSightOn.value.set(on[0] ?? 0, on[1] ?? 0);
    // Sub-frame reuse: an odd sub-frame of a still / film frame (main.js: K sub-frames with sub-pixel jitter) keeps
    // the cloud buffer of the previous sub-frame when the camera moved < 0.3 px in between (stills, slow film moves),
    // so the march runs ~K/2 times per frame with its jitter stratified over those runs (vdc(k >> 1)); the kept
    // buffer is off by the sub-pixel AA jitter only. URL flag nocreuse: march every sub-frame.
    const jit = camera.view && camera.view.enabled, k = subFrame(camera, frame);
    const e = camera.matrixWorld.elements, L = this.lastPose;
    let keep = false;
    if (this.reuse && jit && (k & 1) && L && camera.fov === L.fov && camera.aspect === L.aspect) {
      let dr = 0;
      for (const i of [0, 1, 2, 4, 5, 6, 8, 9, 10]) dr = Math.max(dr, Math.abs(e[i] - L.e[i]));
      keep = dr < 0.3 * pixA && Math.hypot(e[12] - L.e[12], e[13] - L.e[13], e[14] - L.e[14]) < 0.3 * pixA * 400;
    }
    if (!keep) {
      const m = this.reuse && jit && !(k & 1) ? k >> 1 : k;
      u.uJit.value = vdc(m);
      // (r8 p2) march phase: +-0.25 cloud texel (+-0.5 px at res 0.5: the four pixel centres of each 2x2 block, diagonal
      // pair first) per march of a jittered still / film frame; a kept buffer keeps its phase (the composite reads it)
      const sw = sceneRT.width || this.rt.width / (CLOUDS.res || 1);
      const ph = PHASE[m & 3], on = jit && this.phase && this.rt.width < 0.9 * sw;
      u.uPhase.value.set(on ? ph[0] * 0.25 / this.rt.width : 0, on ? ph[1] * 0.25 / this.rt.height : 0);
      this.lastPose = { e: e.slice(), fov: camera.fov, aspect: camera.aspect };
      this.march();
    }
    this.comp.uniforms.tScene.value = sceneRT.texture;
    this.comp.uniforms.tCloud.value = this.rt.texture;
    this.post.pass(this.comp, this.post.cloudRT);
    return this.post.cloudRT;
  }
  march() {
    // the march runs in horizontal strips of ~60k px, each flushed as its own GPU submission: a single
    // full-screen march draw (~0.5-1 s on the Radeon 780M at 1080p) cannot be preempted, and long
    // non-preemptible submissions next to other GPU clients are what the bugcheck-0x119 crashes point to
    // (strips: <= ~150 ms each)
    const rt = this.rt, gl = this.renderer.getContext();
    const n = Math.max(1, Math.ceil(rt.width * rt.height / 60000));
    // (URL flag ctime: a 1-px read after each strip waits for the GPU, so the strip times are real)
    const timing = this.timing, px = timing ? new Float32Array(4) : null;
    const sync = () => { this.renderer.setRenderTarget(rt); gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.FLOAT, px); return performance.now(); };
    let tPrev = timing ? sync() : 0, worst = 0, total = 0;
    rt.scissorTest = true;
    for (let i = 0; i < n; i++) {
      const y0 = Math.floor(i * rt.height / n), y1 = Math.floor((i + 1) * rt.height / n);
      rt.scissor.set(0, y0, rt.width, y1 - y0);
      this.post.pass(this.mat, rt);
      gl.flush();
      if (timing) { const tn = sync(); worst = Math.max(worst, tn - tPrev); total += tn - tPrev; tPrev = tn; }
    }
    rt.scissorTest = false;
    rt.scissor.set(0, 0, rt.width, rt.height);
    if (timing) { this.lastTiming = { strips: n, worst, total }; console.log(`clouds: ${n} strips, march ${total.toFixed(0)} ms, worst strip ${worst.toFixed(0)} ms`); }
  }
}
