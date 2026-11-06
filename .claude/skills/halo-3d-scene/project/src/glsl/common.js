// Shared GLSL: noise, twilight sky model, irradiance and aerial perspective.
// All radiance values are linear HDR, calibrated so that the final tone curve (post.js) lands on
// colors sampled from the reference images.

export const NOISE = /* glsl */ `
float hash12(vec2 p){ vec3 p3 = fract(vec3(p.xyx) * .1031); p3 += dot(p3, p3.yzx + 33.33); return fract((p3.x + p3.y) * p3.z); }
float hash13(vec3 p3){ p3 = fract(p3 * .1031); p3 += dot(p3, p3.zyx + 31.32); return fract((p3.x + p3.y) * p3.z); }
vec2 hash22(vec2 p){ vec3 p3 = fract(vec3(p.xyx) * vec3(.1031, .1030, .0973)); p3 += dot(p3, p3.yzx + 33.33); return fract((p3.xx + p3.yz) * p3.zy); }
vec3 hash33(vec3 p3){ p3 = fract(p3 * vec3(.1031, .1030, .0973)); p3 += dot(p3, p3.yxz + 33.33); return fract((p3.xxy + p3.yxx) * p3.zyx); }

float vnoise2(vec2 p){
  vec2 i = floor(p), f = fract(p); vec2 u = f * f * (3.0 - 2.0 * f);
  return mix(mix(hash12(i), hash12(i + vec2(1, 0)), u.x), mix(hash12(i + vec2(0, 1)), hash12(i + vec2(1, 1)), u.x), u.y);
}
float vnoise3(vec3 p){
  vec3 i = floor(p), f = fract(p); vec3 u = f * f * (3.0 - 2.0 * f);
  return mix(mix(mix(hash13(i), hash13(i + vec3(1,0,0)), u.x), mix(hash13(i + vec3(0,1,0)), hash13(i + vec3(1,1,0)), u.x), u.y),
             mix(mix(hash13(i + vec3(0,0,1)), hash13(i + vec3(1,0,1)), u.x), mix(hash13(i + vec3(0,1,1)), hash13(i + vec3(1,1,1)), u.x), u.y), u.z);
}
// gradient noise 3D, range ~[-1,1]
float gnoise3(vec3 p){
  vec3 i = floor(p), f = fract(p);
  vec3 u = f * f * f * (f * (f * 6.0 - 15.0) + 10.0);
  #define GRD(o) dot(hash33(i + o) * 2.0 - 1.0, f - o)
  return 1.6 * mix(mix(mix(GRD(vec3(0,0,0)), GRD(vec3(1,0,0)), u.x), mix(GRD(vec3(0,1,0)), GRD(vec3(1,1,0)), u.x), u.y),
                   mix(mix(GRD(vec3(0,0,1)), GRD(vec3(1,0,1)), u.x), mix(GRD(vec3(0,1,1)), GRD(vec3(1,1,1)), u.x), u.y), u.z);
  #undef GRD
}
float fbm2(vec2 p, int oct){
  float s = 0.0, a = 0.5;
  for (int i = 0; i < 8; i++) { if (i >= oct) break; s += a * vnoise2(p); p = p * 2.03 + vec2(17.1, -9.3); a *= 0.5; }
  return s;
}
float fbm3(vec3 p, int oct){
  float s = 0.0, a = 0.5;
  for (int i = 0; i < 8; i++) { if (i >= oct) break; s += a * vnoise3(p); p = p * 2.03 + vec3(17.1, -9.3, 4.7); a *= 0.5; }
  return s;
}
float gfbm3(vec3 p, int oct){
  float s = 0.0, a = 0.5;
  for (int i = 0; i < 8; i++) { if (i >= oct) break; s += a * gnoise3(p); p = p * 2.07 + vec3(17.1, -9.3, 4.7); a *= 0.5; }
  return s;
}
`;

// Far-field dip: the AI refs combine a ~10 deg elevated view of the ring with a horizon right behind it.
// Everything beyond ~4-12 km (terrain, lights, cloud sea, sky) is rotated down about the camera by atan(uFarDip).
export const FARDIP = /* glsl */ `
#ifndef FAR_DIP_U
#define FAR_DIP_U
uniform float uFarDip;
uniform vec2 uDipWin;
#endif
// ramp window (m from the camera): it must sit where the cloud tops' depression angle still exceeds the dip,
// otherwise nearer undipped cloud rises above the lowered horizon (fold). ~0.6-1.8 km for a camera ~450 m above the tops.
float farOffC(vec3 p, vec3 cam){ float dh = length(p.xz - cam.xz); return uFarDip * dh * smoothstep(uDipWin.x, uDipWin.y, dh); }
#define farOff(p) farOffC(p, cameraPosition)
`;

export const ATMOS = /* glsl */ `
uniform vec3 uSunDir;       // direction toward the (below-horizon) sun
uniform float uSkyExposure;
uniform float uFogDensity;
uniform float uTime;
uniform float uHorizonDip;
// per-view sky framing (round 5, default (1, 0, 0, 0) = off; see skyView): x zoom k, y zoom-centre elevation (rad,
// above the dipped horizon), z glow azimuth offset (rad, + = clockwise / to the right), w sky-only dip (tan: the sky
// is looked up w lower, so + raises the band on screen, - hides more of its hot base behind the far peaks)
uniform vec4 uSkyView;
#ifndef FAR_DIP_U
#define FAR_DIP_U
uniform float uFarDip;
uniform vec2 uDipWin;
#endif
vec3 farDipDir(vec3 d){ return normalize(vec3(d.x, d.y + uFarDip * length(d.xz), d.z)); }

vec3 srgb2lin(vec3 c){ return pow(c, vec3(2.2)); }

// pixel footprint of the sky lookup (rad, in sky space after skyView): sky.js sets it per fragment from fwidth (in
// uniform control flow); other callers (glass / lake reflections) keep this coarse default (fine detail faded out)
float gSkyPx = 0.003;

// The glow azimuth (unit xz): the sun's, turned by uSkyView.z. It moves only the sky's glow, cloud rows and cloud
// lighting (the refs disagree on where the glow sits: ~207 deg in ref 7 .. ~245 in ref 5); the scene keeps uSunDir.
vec2 skyGlowH(){
  vec2 s = normalize(uSunDir.xz);
  float c = cos(uSkyView.z), n = sin(uSkyView.z);
  return vec2(c * s.x - n * s.y, n * s.x + c * s.y);
}
vec3 skySunDir(){ vec2 g = skyGlowH() * length(uSunDir.xz); return normalize(vec3(g.x, uSunDir.y, g.y)); }

// Per-view sky framing. The hero cameras use 1.3-2x longer lenses than the AI refs were drawn with (v4 14 deg vs
// ~27, v7 / v11 25 vs ~40, v5 / v6 28 vs ~36), so the band, its cloud rows and the masses came out 1.3-2x too large
// in the frame (v7 showed only the lowest ~4 deg of sky: all of it peach-salmon band and blurred row bodies).
// skyView zooms the sky out by k about the point c on the skyline at the glow azimuth (stereographic about c:
// conformal, so cells keep their shape; the horizon through c stays put; the only other fixed point is c's antipode,
// behind the camera), so the sky matches the refs in pixel terms; then a sky-only dip seats the band's hot base on
// the far skyline. Identity at the default (1, 0, 0, 0).
vec3 skyView(vec3 d){
  float k = uSkyView.x;
  if (k > 0.0 && abs(k - 1.0) > 1e-3) {             // (0: a material without the uniform -> off)
    vec2 g = skyGlowH();
    float ce = uSkyView.y;
    vec3 c = vec3(g.x * cos(ce), sin(ce), g.y * cos(ce));
    vec3 r = vec3(-g.y, 0.0, g.x);                    // horizontal, to the right of the glow
    vec3 u = cross(r, c);                              // up through c
    vec2 X = k * vec2(dot(d, r), dot(d, u)) / max(1.0 + dot(d, c), 1e-4);
    float q = dot(X, X);
    d = (2.0 * (X.x * r + X.y * u) + (1.0 - q) * c) / (1.0 + q);
  }
  d.y -= uSkyView.w * length(d.xz);
  return normalize(d);
}

// Azimuthal distance (rad) between direction d and the glow azimuth: 0 sunward .. PI anti-sun.
float skySunAz(vec3 d){
  return acos(clamp(dot(normalize(d.xz + vec2(1e-5)), skyGlowH()), -1.0, 1.0));
}

// ---------------- photographic sky (round 8): a real dusk sky (CC0 HDRIs, Poly Haven belfast_sunset_puresky; pass 2:
// + cedar_bridge_sunset_1's billowing masses right of the glow) baked by tools/skybake.mjs into data/sky/sky.png:
// equirect, u = compass azimuth / 360, rows from the zenith down to uSkyTexP.w; the HDRI's sun turned to the scene's
// glow azimuth and dropped below the horizon, its clear sky graded onto the refs' twilight colours (a bluer variant
// of skyClear's knots) with the clouds keeping their photographic ratio to it.
// Log2-encoded 8-bit: radiance = exp2(y + v * z). sky.js loads it and sets uSkyTexP.x = 1; until then (or in a
// material without the shared uniforms: x = 0) the analytic sky + procedural deck below is used.
uniform sampler2D uSkyTex;
uniform vec4 uSkyTexP;     // x on, y log2 min, z log2 range, w bottom elevation of the texture (rad)
// texture footprint: sky.js passes screen-space gradients of the lookup (gSkyGrad = 1); reflections (glass, lake)
// sample a fixed blurred mip
vec2 gSkyDx = vec2(0.0), gSkyDy = vec2(0.0);
float gSkyGrad = 0.0;
float gSkyLod = 2.5;
// Parallax: the photo's clouds are taken to lie on a plane SKY_PAR_H above the deck, seen from the ring centre (the
// photo's viewpoint). A camera elsewhere sees the plane point along its ray from the ring centre: overhead clouds
// shift ~6 deg per 300 m of camera travel, the far rows near the horizon hardly at all (closed form of
// normalize(ro + d * k - O), k = (H - ro.y) / d.y, without the huge k at grazing angles; d.y <= 0: unchanged).
const vec3 SKY_O = vec3(0.0, 2180.0, 0.0);
const float SKY_PAR_H = 3000.0;
vec3 skyParallax(vec3 ro, vec3 d){
  float s = max(d.y, 0.0) / max(SKY_O.y + SKY_PAR_H - ro.y, 400.0);
  return normalize(d + (ro - SKY_O) * s);
}
// texture coordinates of direction d seen from ro (after the stills' far-field dip / sky framing)
vec2 skyUV(vec3 ro, vec3 d){
  d = skyParallax(ro, skyView(farDipDir(d)));
  float az = atan(d.x + 1e-7, -d.z);
  float el = asin(clamp(d.y, -1.0, 1.0));
  return vec2(az * 0.15915494, (el - uSkyTexP.w) / (1.5707963 - uSkyTexP.w));
}
vec3 skyPhoto(vec3 ro, vec3 d){
  vec2 uv = skyUV(ro, d);
  vec3 v = gSkyGrad > 0.5 ? textureGrad(uSkyTex, uv, gSkyDx, gSkyDy).rgb : textureLod(uSkyTex, uv, gSkyLod).rgb;
  return exp2(uSkyTexP.y + v * uSkyTexP.z) * uSkyExposure;
}

// Clear twilight sky radiance (no cloud layer). e = elevation above the dipped horizon in radians (uHorizonDip
// 0.025: e = d.y + 0.025, so the knots below sit at d.y = -1.0, 0.3, 1.3, 2.6, 3.5, 4.4, 5.3, 6.2, 7.2, 8.5, 10 deg).
// Linear values are pre-compensated for the tone shoulder in post.js (comments give the landing sRGB).
// Refs (2, 4, 6, 7, 11, 1, measured above the peaks): the hot band sits right on the skyline, 0.3-3 deg up:
// orange #fc9b59 on the peaks -> peach #fbaa70 (not red), peach #eea681 at ~3.5 deg, dusty rose #d99d8d / #be9396 at 4-5 deg,
// mauve-lavender #a389a1 / #847ea4 at 6-7 deg, blue-lavender #6a73a3 by ~8.5 deg, #5c6da1 at 10 deg.
// (Round 3 put the core below the skyline: the hero views only showed the red upper part of the band.)
vec3 skyClearA(vec3 d);
// round 8: the photographic sky (clouds included) wherever it is loaded; callers are reflections (glass, lake)
vec3 skyClear(vec3 d){ return uSkyTexP.x > 0.5 ? skyPhoto(cameraPosition, d) : skyClearA(d); }
// the analytic clear sky (fallback; its knots are also the bake's target, tools/skybake.mjs targetClear)
vec3 skyClearA(vec3 d){
  d = farDipDir(d);
  d = skyView(d);
  float e = d.y + uHorizonDip;
  float t = skySunAz(d);
  // Pass 2: the refs' orange core is one azimuth sector (~12-15 deg half-width) with a stepped vertical ramp
  // (critique, x-bin p90 of refs 4, 6, 7, 2): deep orange on the skyline #fc9352, paler peach #f8a572 ~2-3 deg up,
  // salmon-mauve #937b8c ~4.4 deg, lavender #6d7095 ~5.3 deg, blue #51669a by ~6.6 deg (knots below at d.y 0.3, 1.0,
  // 2.0, 2.8, 3.6, 4.4, 5.3, 6.6 deg). Outside the core the low band is dim dusty rose -> mauve (#8a6e7e .. #776e87)
  // out to ~35 deg, then the lavender anti-sun sky (#5d5675) -- no longer peach across the whole frame width.
  // (post's clarity lifts the band against the dark ridges by ~10 %: the first knots are set below their targets)
  // Round 5 (refs 7 / 2 measured per 10 px row, clear-sky pixels, skyline ~0 deg): deep orange right on the skyline
  // #f78458, a brighter yellow-orange core #fcba72 ~1.5 deg up, #f3a67b at 2.3, peach-rose #e29d84 at 2.8, dusty rose
  // #b88a8e at 3.2, mauve #9e8193 at 3.6, lavender #8d82a6 at 5.3, #777aa9 at 6.2, #6571a7 by 7 deg. Round 4's band
  // was redder (#fe8c4e core) and ~1 deg too tall. h: elevation above the far skyline (uSkyView.w seats it per view).
  // Pass 3: the band now sits on the far skyline the hero views actually show (e ~3.2 deg: the Bernese Alps' crest
  // line in the dipped frame; with the base at 1.6 deg the hot core hid behind the peaks and only the peach-rose
  // upper band showed), 0.72x as tall (refs 7 / 11: golden core 45-72 px above the peaks), with ref 7's golden core
  // #fdc174 and a less red skyline (#f89056 / #f0a362; ours was #fc8a57 / #eb7d51 at 100 %).
  // (only the warm core is compressed: the mauve -> lavender rise above it is ~1.1x its round-4 height; ref 7 shows
  // lavender #6d78ad .. #9185a8 up to the frame top where the fully compressed band gave blue #57689d)
  float u = e - 0.055;
  float h = u < 0.03 ? u / 0.72 : 0.041667 + (u - 0.03) * 0.9;
  vec3 s = vec3(0.74, 0.22, 0.08);
  s = mix(s, vec3(0.90, 0.29, 0.095), smoothstep(-0.004, 0.0035, h));  // #f89056 orange on the skyline
  s = mix(s, vec3(0.88, 0.35, 0.115), smoothstep(0.0035, 0.0105, h));  // #f0a362
  s = mix(s, vec3(0.96, 0.47, 0.16), smoothstep(0.0105, 0.019, h));    // #fcb978
  s = mix(s, vec3(0.98, 0.54, 0.19), smoothstep(0.019, 0.026, h));     // #fdc174 golden core
  s = mix(s, vec3(0.95, 0.47, 0.19), smoothstep(0.026, 0.033, h));     // #fbb877
  s = mix(s, vec3(0.90, 0.40, 0.20), smoothstep(0.033, 0.040, h));     // #f8ad7e
  s = mix(s, vec3(0.76, 0.34, 0.22), smoothstep(0.040, 0.049, h));     // #e8a283 peach-rose
  s = mix(s, vec3(0.45, 0.24, 0.24), smoothstep(0.049, 0.056, h));     // #b8837d dusty rose
  s = mix(s, vec3(0.30, 0.205, 0.27), smoothstep(0.056, 0.063, h));    // #9e8193 mauve
  s = mix(s, vec3(0.25, 0.19, 0.28), smoothstep(0.063, 0.075, h));     // #8f7c97
  s = mix(s, vec3(0.22, 0.19, 0.31), smoothstep(0.075, 0.092, h));     // #8d82a6 lavender
  s = mix(s, vec3(0.15, 0.165, 0.315), smoothstep(0.092, 0.108, h));   // #777aa9
  s = mix(s, vec3(0.105, 0.145, 0.31), smoothstep(0.108, 0.122, h));   // #6571a7
  // ~15-40 deg off the core: the dim dusty-rose / mauve wing of the band
  vec3 m = vec3(0.22, 0.12, 0.16);
  m = mix(m, vec3(0.30, 0.165, 0.19), smoothstep(-0.004, 0.0035, h));  // dusty rose on the skyline
  m = mix(m, vec3(0.26, 0.16, 0.22), smoothstep(0.0035, 0.030, h));
  m = mix(m, vec3(0.19, 0.15, 0.25), smoothstep(0.030, 0.055, h));     // mauve
  m = mix(m, vec3(0.14, 0.145, 0.27), smoothstep(0.055, 0.080, h));    // lavender
  m = mix(m, vec3(0.10, 0.140, 0.30), smoothstep(0.080, 0.115, h));
  // anti-sun: blue earth shadow, pink-mauve Belt of Venus, lavender
  vec3 a = vec3(0.070, 0.076, 0.150);
  a = mix(a, vec3(0.10, 0.085, 0.16), smoothstep(0.0, 0.0296, e));
  a = mix(a, vec3(0.16, 0.11, 0.19), smoothstep(0.0296, 0.0667, e));
  a = mix(a, vec3(0.09, 0.105, 0.245), smoothstep(0.0667, 0.126, e));
  vec3 col = mix(a, m, exp(-t * t / 0.36));      // rose wing: ~34 deg
  col = mix(col, s, exp(-t * t / 0.075));        // orange core: ~16 deg (1/e)
  // upper sky, shared by all azimuths: #55689c at 7-10 deg -> #4b6298 at ~17 deg -> zenith
  col = mix(col, mix(vec3(0.088, 0.125, 0.29), vec3(0.10, 0.145, 0.32), smoothstep(1.6, 0.6, t)), smoothstep(0.17, 0.20, e));
  col = mix(col, vec3(0.080, 0.125, 0.295), smoothstep(0.20, 0.33, e));
  col = mix(col, vec3(0.064, 0.105, 0.265), smoothstep(0.33, 1.2, e));
  // violet tint high over the glow (ref 9: #4c5389 gaps 20-50 deg up)
  col *= mix(vec3(1.0), vec3(1.14, 0.94, 0.92), exp(-t * t / 0.6) * smoothstep(0.2, 0.35, e) * (1.0 - smoothstep(0.7, 1.3, e)));
  // pass 2: deep violet-navy gaps 22-60 deg up on the sunward side (ref 9: #3d4078 .. #454474 between the lumps, ours
  // was #5c68a4; outside the ring upper left #272742 .. #4d568c); the hero frames end below ~16 deg (sky frame)
  col *= mix(vec3(1.0), vec3(0.58, 0.46, 0.56), exp(-t * t / 0.9) * smoothstep(0.27, 0.62, e) * (1.0 - 0.5 * smoothstep(1.1, 1.45, e)));
  // below horizon: darken smoothly (only seen in env/reflections)
  col *= mix(1.0, 0.55, smoothstep(0.0, -0.15, e));
  return col * uSkyExposure;
}

// ---------------- cloud deck (round 5 pass 2: a volumetric layer marched along the view ray)
// The user circled round 4's deck (smooth airbrushed blobs, brushy smears, 'flame' shapes low down); pass 1's
// heightfield deck (hemispherical heads on a flat base) read as floating slabs and boxes with vertical walls, and its
// smallest heads as opaque specks. Refs at 100 % (7, 4, 11, 5, 2, 9): stratocumulus masses with soft-but-crisp lumpy
// outlines and ragged undersides that break into fragments, many thin dark rows across the glow band (perspective-
// squeezed far cells) with lit lower fringes, dark slate cores, a cellular altocumulus field overhead (ref 9: dark
// violet gaps, salmon-lit lumps, dark cores).
// The deck is now a density field SKY_BASE .. SKY_BASE + SKY_TM km up on the curved earth (world anchored in km:
// parallax), marched front to back along the view ray with soft density edges, lit per sample by the sky dome (through
// the cloud above) and by the glow (through the cloud toward it: lit bases and fringes, dark cores). Octaves fade out
// where a pixel can no longer resolve them (no shimmer). Only skyDeck / skyClouds are the interface (skyFull, water.js
// reflections; glass reflections get a coarse march).
const float SKY_RE = 6371.0;   // earth radius (km)
const float SKY_BASE = 4.9;    // deck base plane altitude (km): far enough above the camera (~2.2 km) that the band's
                               // rows sit 30-170 km out and squeeze into thin lines (a 3.6 km base brought the masses
                               // to 8-16 km: blurry undulating undersides)
const float SKY_TM = 1.9;      // deck depth (km)
const float SKY_DDIP = 0.026;  // deck-only dip (tan): the deck's own horizon sits just under the far skyline (sky frame
                               // d.y ~0.03), so the rows right above the peaks are the far, thin ones
const float SKY_SIG = 36.0;    // extinction at full density (1/km): the far rows read opaque dark slate, not mauve veils
// 2D gradient noise, ~[-1,1]: rounder and less blocky than value noise
float skyGN(vec2 p){
  vec2 i = floor(p), f = fract(p);
  vec2 u = f * f * f * (f * (f * 6.0 - 15.0) + 10.0);
  #define SG(o) dot(hash22(i + o) * 2.0 - 1.0, f - o)
  float r = mix(mix(SG(vec2(0, 0)), SG(vec2(1, 0)), u.x), mix(SG(vec2(0, 1)), SG(vec2(1, 1)), u.x), u.y);
  #undef SG
  return r * 1.5;
}
const mat2 SKY_ROT = mat2(1.62, 1.18, -1.18, 1.62);   // octave step: x2 scale, 36 deg turn
// art-directed coverage (direction based; eh: elevation above the far skyline in the sky frame, t: azimuth from the
// glow): dark masses upper left of the hero views, the hot core showing between the rows right on the skyline, a dense
// altocumulus field overhead toward the glow (ref 9), thinner high anti-sun
float skyCovBias(vec3 d, float eh, float t){
  vec2 dh = normalize(d.xz + vec2(1e-5));
  float a1 = acos(clamp(dot(dh, vec2(-0.1736, 0.9848)), -1.0, 1.0));   // az 190
  float b = 0.0;
  b += 0.20 * exp(-a1 * a1 / 0.12) * smoothstep(0.05, 0.10, eh) * (1.0 - smoothstep(0.30, 0.50, eh));
  // big dark masses across the upper hero sky (refs 5, 11, 4, 7: the top third carries the largest, darkest clouds)
  b += 0.07 * smoothstep(0.07, 0.13, eh) * (1.0 - smoothstep(0.30, 0.45, eh));
  // the hot core 0-1.5 deg above the skyline (screen) stays mostly clear: only the far rows' thin streaks cross it
  b -= 0.24 * (1.0 - smoothstep(0.015, 0.045, eh));
  b += 0.20 * exp(-t * t / 0.8) * smoothstep(0.22, 0.40, eh);
  b -= 0.10 * smoothstep(0.45, 1.0, eh) * (1.0 - exp(-t * t / 0.8));
  return b;
}
// ray length (km) from the camera to H km above it, for a direction with sine s and horizontal cosine c (curved
// earth: the height gained over a horizontal distance h is h tan(el) + h^2 / 2R)
float skyRayH(float s, float c, float H){ return 2.0 * H / (s + sqrt(s * s + 2.0 * H * c * c / SKY_RE)); }
// resolvable weight of an octave of feature size S (km) at fp km per px
float skyLod(float S, float fp){ return smoothstep(1.0, 2.0, S / max(3.0 * fp, 1e-4)); }

// One ray through the deck (km): deck direction d, its horizontal cosine c and unit heading dh, the deck origin X0
// (camera position + drift), the base height H0 above the camera, the coverage bias, the fixed row frame g (the sun's
// azimuth: not the per-view glow offset, so the deck stays put between views), coarse (reflections).
struct SkyRay { vec3 d; float c; vec2 dh; vec2 X0; float H0; float bias; vec2 g; float fa; bool coarse; };
// position on the ray at distance x: (X km, height above the base plane km)
vec3 skyAt(SkyRay r, float x){
  float hx = x * r.c;
  return vec3(r.X0 + r.dh * hx, x * r.d.y + hx * hx / (2.0 * SKY_RE) - r.H0);
}
// coverage at X (km), ~[-1, 1]: masses ~8 / 4 / 1.7 km across, domain-warped, stretched 2x across the glow
// azimuth (the refs' masses are long and low); far out (rw) stratocumulus rows ~9 x 1.8 km take over, which
// perspective squeezes into the band's long thin rows
float skyCov(SkyRay r, vec2 X, float rw){
  vec2 Xg = vec2(dot(X, vec2(-r.g.y, r.g.x)), dot(X, r.g));      // (across, along) the glow azimuth
  vec2 q = Xg * vec2(0.085, 0.18);
  q += 0.38 * vec2(skyGN(q * 0.55 + 3.1), skyGN(q * 0.55 - 7.7));
  // (pass 2: a weak small octave: a strong one scattered the band with look-alike 1-2 km lenses, polka dots)
  float c = 0.66 * skyGN(q + 1.3) + 0.34 * skyGN(SKY_ROT * q * 1.1 - 4.1) + 0.08 * skyGN(q * 4.6 + 8.4);
  if (rw > 0.0) {
    vec2 a = Xg * vec2(0.065, 0.6);
    a.x += 0.8 * skyGN(a * vec2(0.4, 0.7) + 2.7);
    float w = 0.75 * skyGN(a + 5.3) + 0.35 * skyGN(a * vec2(2.2, 1.9) - 1.9) + 0.15 * skyGN(Xg * vec2(0.3, 1.1) + 3.3);
    c = mix(c, 0.35 * c + w, rw);
  }
  return c + r.bias;
}
// cloud field (> 0 inside) at X (km), z km above the base plane, coverage cv: a core height ~0.3 km up with a steep
// profile below it (flattish bases) and a gentle one above (heads rise with the coverage; where it is low only thin
// lenses remain: the far rows), shaped by billowy 3D octaves (~1.2 / 0.4 / 0.15 / 0.06 km: rounded lobes with sharp
// creases between them) that fade out where a pixel no longer resolves them; signed noise erodes the bases into
// ragged undersides and hanging fragments. full = false: the big octave only (light probes, reflections).
// m.x: 0 near .. 1 far (the rows: thin lenses, sparser, so the low band is not an overcast of stacked far cells);
// m.y: 1 overhead (< ~10 km out: a cellular altocumulus field, ref 9: the octaves carve ~0.2-1 km cells out of an
// even coverage instead of the masses' 7 km gaps)
float skyField(vec2 X, float z, float cv, vec2 m, float fp, bool full){
  float zc = 0.30 + 0.10 * skyGN(X * 0.45 + 9.1);
  float pz = z < zc ? (zc - z) * mix(3.6, 4.5, m.x) : (z - zc) * mix(1.35, 3.2, m.x);
  float F = mix(1.6, 0.5, m.y) * (cv - mix(0.15, 0.27, m.x)) + mix(0.05, 0.07, m.y) - 0.5 * pz * pz;
  if (F < -0.5) return F;                            // (the octaves add at most ~0.45)
  vec3 P = vec3(X.x, z * 1.5, X.y);
  F += (mix(0.28, 0.34, m.y) + 0.08 * m.x) * (abs(gnoise3(P * mix(0.8, 1.6, m.y) + vec3(3.3, 0.7, 1.1))) - 0.33);
  if (!full || F < -0.32) return F;
  vec3 Q = vec3(X.x, z, X.y);
  float eb = 1.0 - smoothstep(zc - 0.2, zc + 0.15, z);   // base erosion weight
  float w2 = skyLod(0.4, fp), w3 = skyLod(0.15, fp), w4 = skyLod(0.06, fp);
  if (w2 > 0.0) F += w2 * (0.16 * (abs(gnoise3(Q * 2.5 - 1.7)) - 0.30) + 0.07 * eb * gnoise3(Q * 3.1 + 7.3));
  if (w3 > 0.0 && F > -0.14) F += w3 * (0.07 * (abs(gnoise3(Q * 6.7 + 4.1)) - 0.30) + 0.04 * eb * gnoise3(Q * 8.3 - 2.9));
  if (w4 > 0.0 && F > -0.05) F += w4 * 0.035 * (abs(gnoise3(Q * 17.0 - 6.2)) - 0.30);
  return F;
}
// (a steep ramp: soft-but-crisp outlines ~1-3 px wide on the masses; F * 7 blurred them over ~9 px at 30 km)
float skyDens(float F){ return clamp(F * 30.0, 0.0, 1.0); }
// per-ray light: glow colour and strength (incl. the phase toward the glow), dome colours below / above
struct SkyLit { vec3 warm; float G; vec3 cDn; vec3 cUp; vec3 Ls; vec3 bgL; };

// Returns vec4(colour, coverage) of the deck in front of bg (the clear sky behind, for the haze on far clouds).
vec4 skyDeck(vec3 ro, vec3 d, vec3 bg){
  if (uSkyTexP.x > 0.5) return vec4(0.0);           // round 8: the photographic sky carries its own clouds
  d = farDipDir(d);
  d = skyView(d);
  float e = d.y + uHorizonDip;
  if (e <= 0.002) return vec4(0.0);
  float eh = e - 0.055;                               // above the far skyline (skyClear's band base)
  float t = skySunAz(d);
  SkyRay r;
  float c0 = length(d.xz);
  r.d = normalize(vec3(d.x, d.y - SKY_DDIP * c0, d.z));
  r.c = length(r.d.xz);
  r.dh = r.d.xz / max(r.c, 1e-4);
  r.H0 = max(SKY_BASE - ro.y * 0.001, 0.6);         // base height above the camera (km)
  r.X0 = ro.xz * 0.001 + vec2(uTime * 0.003, 0.0);
  r.bias = skyCovBias(d, eh, t);
  r.g = normalize(uSunDir.xz + vec2(1e-5));
  // reflections (glass, lake: coarse gSkyPx) get a short march without the fine octaves and light probes
  r.coarse = gSkyPx > 0.002;
  // footprint per km of ray for the octave fades: a pixel on the deck is stretched along the ray by ~1 / sin(el) at
  // grazing angles (geometric mean of the two axes: fine lumps on the far rows aliased into a busy scribble)
  r.fa = gSkyPx * sqrt(clamp(0.5 / max(abs(r.d.y), 1e-3), 1.0, 12.0));
  float xa = skyRayH(r.d.y, r.c, r.H0), xb = skyRayH(r.d.y, r.c, r.H0 + SKY_TM);
  if (xa > 420.0) return vec4(0.0);
  xb = min(xb, xa + 60.0);
  float N = r.coarse ? 10.0 : clamp((xb - xa) / 0.12, 40.0, 112.0);
  float dx = (xb - xa) / N;
  // per-ray jitter (the sub-frame jitter of the camera decorrelates it between sub-frames)
  float j = hash12(d.xz * 4801.0 + d.y * 1531.0);

  // light: glow from the sunward horizon (salmon-orange near the sun azimuth, dusty rose -> mauve away from it),
  // strong overhead toward the sun (ref 9: salmon-lit lumps, dark cores), weak on the band's masses 3-20 deg up (refs
  // 1, 2, 4, 7: dark slate with lit lower fringes); forward scattering toward the glow lights the thin fringes
  SkyLit li;
  float ang = acos(clamp(dot(d, skySunDir()), -1.0, 1.0));
  vec3 warm = mix(vec3(1.0, 0.40, 0.13), vec3(1.15, 0.50, 0.16), exp(-ang * ang / 0.15));
  // (pass 2: pinker high up, ref 9's lit lumps #d28980 .. #e37f6c; orange-brown read muddy)
  warm = mix(warm, vec3(0.95, 0.37, 0.24), smoothstep(0.35, 0.9, ang));
  li.warm = mix(warm, vec3(0.30, 0.16, 0.24), smoothstep(1.2, 2.4, ang));
  float sector = exp(-t * t / 0.35) * smoothstep(0.30, 0.80, e) * (1.0 - 0.5 * smoothstep(1.2, 1.55, e));
  float ph = 0.30 + 1.6 * exp(-ang * ang / 0.05) + 0.5 * exp(-ang * ang / 0.5);
  li.G = (0.06 + 0.10 * exp(-t * t / 0.8) + 0.85 * sector) * ph;
  float hiE = smoothstep(0.04, 0.25, e);
  // dome light: slate-navy, blue-dominant (refs' rows / masses p50 #444e73 .. #52608b, B - R ~0x30-0x38)
  li.cDn = mix(vec3(0.009, 0.018, 0.058), vec3(0.012, 0.022, 0.066), hiE);
  li.cUp = mix(vec3(0.042, 0.056, 0.138), vec3(0.068, 0.090, 0.200), hiE);
  vec2 sd = skyGlowH();
  // (from steeper below high up: ref 9's lumps 20-50 deg up toward the glow are lit salmon on their undersides)
  li.Ls = normalize(vec3(sd.x, mix(-0.35, -0.85, smoothstep(0.25, 0.6, e)), sd.y));
  li.bgL = bg / max(uSkyExposure, 1e-3);

  // coarse steps through clear air; at the first cloud sample back up and continue at a quarter step (less depth
  // noise in the lighting), back to coarse after a run of empty fine samples
  vec3 acc = vec3(0.0);
  float Tr = 1.0;
  float x = xa + j * dx, st = dx, nOut = 0.0;
  for (int i = 0; i < 176; i++) {
    if (x > xb || Tr < 0.03) break;
    vec3 p = skyAt(r, x);
    if (p.z < 0.0 || p.z > SKY_TM) { x += st; continue; }
    float fp = x * r.fa;
    float hd = x * r.c;
    vec2 m = vec2(smoothstep(35.0, 85.0, hd), 1.0 - smoothstep(6.0, 14.0, hd));
    float cv = skyCov(r, p.xy, m.x);
    float F = skyField(p.xy, p.z, cv, m, fp, !r.coarse);
    if (F <= 0.0) {
      nOut += 1.0;
      if (st < dx && nOut > 5.0) st = dx;
      x += st;
      continue;
    }
    if (st == dx && !r.coarse) { st = 0.25 * dx; x -= 0.75 * dx; nOut = 0.0; continue; }
    nOut = 0.0;
    float dens = skyDens(F);
    float a = 1.0 - exp(-SKY_SIG * dens * st);
    // sky dome through the cloud above (probe 0.25 km up) and the depth inside; glow through the cloud toward it
    // (probes 0.03 / 0.12 / 0.35 km along Ls: only a thin skin on the bases and fringes toward the glow is lit, the
    // cores and the thin rows' bodies stay dark slate)
    float Tu, Tl;
    if (r.coarse) { Tu = exp(-1.2 * dens); Tl = exp(-3.0 * dens); }
    else {
      // (two probes up, 0.07 / 0.25 km: the sky-lit upper skin of each mass is lighter lavender-grey, its lower body
      // dark slate: a vertical gradient across every row and mass instead of a flat fill)
      float du1 = skyDens(skyField(p.xy, p.z + 0.07, cv, m, fp, false));
      float du2 = skyDens(skyField(p.xy, p.z + 0.25, cv, m, fp, false));
      vec3 p3 = vec3(p.x, p.z, p.y);
      vec3 q1 = p3 + li.Ls * 0.03, q2 = p3 + li.Ls * 0.12, q3 = p3 + li.Ls * 0.35;
      float d1 = skyDens(skyField(q1.xz, q1.y, cv, m, fp, false)), d2 = skyDens(skyField(q2.xz, q2.y, cv, m, fp, false));
      float d3 = skyDens(skyField(q3.xz, q3.y, cv, m, fp, false));
      Tu = exp(-1.4 * du1 - 1.0 * du2 - 0.3 * dens);
      Tl = exp(-4.0 * d1 - 3.0 * d2 - 3.0 * d3 - 1.5 * dens);
    }
    vec3 L = mix(li.cDn, li.cUp, Tu * (0.45 + 0.55 * smoothstep(0.1, 1.0, p.z))) + li.warm * li.G * Tl;
    // aerial perspective: the far rows sink into the band's haze
    L = mix(L, li.bgL, 0.10 * smoothstep(80.0, 250.0, x));
    acc += Tr * a * L;
    Tr *= 1.0 - a;
    x += st;
  }
  float A = 1.0 - Tr;
  if (A < 1e-4) return vec4(0.0);
  return vec4(acc / A * uSkyExposure, A * smoothstep(0.002, 0.012, e));
}
vec4 skyClouds(vec3 ro, vec3 d){ return skyDeck(ro, d, skyClear(d)); }

vec3 skyFullA(vec3 ro, vec3 d){
  vec3 s = skyClearA(d);
  vec4 cl = skyDeck(ro, d, s);
  return mix(s, cl.rgb, cl.a);
}
// the sky dome (sky.js) and the glazing's sharp reflections: the photographic sky, or the analytic sky + deck
vec3 skyFull(vec3 ro, vec3 d){ return uSkyTexP.x > 0.5 ? skyPhoto(ro, d) : skyFullA(ro, d); }

// Diffuse irradiance (already divided by PI, i.e. multiply by albedo) from the twilight dome.
// nrm: world normal; vis: sky visibility (AO); glowVis: horizon visibility toward the sun.
// Calibrated so that: concrete deck (albedo .6) -> #777b9a, outer walls -> #42455a, open snow -> #7782b5.
vec3 skyIrradiance(vec3 n, float vis, float glowVis){
  vec3 Eup  = vec3(0.250, 0.290, 0.540);
  vec3 Ehor = vec3(0.085, 0.094, 0.165);
  vec3 Edn  = vec3(0.050, 0.055, 0.088);
  vec3 Eglw = vec3(0.150, 0.080, 0.055);
  float y = n.y;
  vec3 E = y > 0.0 ? mix(Ehor, Eup, pow(y, 0.85)) : mix(Ehor, Edn, -y);
  vec3 sh = normalize(vec3(uSunDir.x, 0.0, uSunDir.z));
  float fs = max(dot(n, sh), 0.0) * (1.0 - abs(y) * 0.6);
  E += Eglw * fs * fs * glowVis;
  return E * vis * uSkyExposure;
}

// Airlight color: blue-violet, slightly warmer toward the sunset azimuth (refs: #5a6288 / #7d5d78; round 8 pass 2:
// the warm end peach-grey rather than pink-lilac, the refs' horizon off the band. The sky bake's horizon haze,
// tools/skybake.mjs FOG_COOL / FOG_WARM, uses the same two colours)
vec3 fogColor(vec3 d){
  d = farDipDir(d);
  d = skyView(d);
  vec2 sh = skyGlowH();
  float c = dot(normalize(d.xz + 1e-5), sh);
  float t = acos(clamp(c, -1.0, 1.0));
  float w = 0.3 * exp(-t * t / 0.09) + 0.10 * exp(-t * t / 0.6);
  vec3 cool = srgb2lin(vec3(0.353, 0.384, 0.533));
  vec3 warm = srgb2lin(vec3(0.500, 0.390, 0.440));
  return mix(cool, warm, w) * uSkyExposure;
}

// Aerial perspective: exponential height fog (uFogDensity = extinction per m at deck altitude, scale height
// FOG_HS). Twilight airlight is dim, so the haze removes more light than it adds: surfaces darken and turn
// blue over 10-30 km (snow #7782b5 -> ~#525c86 at 20 km, red extinguished first) before flattening into the
// airlight (far ridges ~#4e577b, horizon haze #5a6288). Low valleys and the cloud sea haze over faster
// than the high summits, which keeps the far ranges layered.
// The airlight colour depends on the path: over short / mid paths the lit air above the cloud sea is a saturated
// navy (refs: shadowed ranges at 10-20 km #273d67..#2c426d, not grey-violet), over long ones it whitens into the
// horizon haze (fogColor). The air under the cloud sea (below its base) sits in the deck's shadow and adds only a
// dim deep navy, so the lake valley seen through the gaps stays dark (refs #16-20..#23 navy).
const float FOG_HS = 1700.0;
const float FOG_Y0 = 2180.0;
const float FOG_YC = 1500.0;
const vec3 FOG_NAVY = vec3(0.064, 0.124, 0.270);
// pass 2: slate rather than saturated blue (it drove the lake's red toward zero in view 4)
const vec3 FOG_LOW = vec3(0.026, 0.035, 0.074);
float fogInt(float y){ return FOG_HS * exp(-(y - FOG_Y0) / FOG_HS); }   // column above y (in units of uFogDensity)
// The two terms of the aerial perspective along ro -> p: final = col * Te + air. Shared helper (pass 2) so other
// shaders that pre-compensate the haze (water.js) use exactly the airlight applyAtmos adds.
void atmosTerms(vec3 ro, vec3 p, out vec3 Te, out vec3 air){
  vec3 v = p - ro;
  float dist = max(length(v), 1e-3);
  vec3 d = v / dist;
  float od, odL;
  if (abs(v.y) > 1.0) {
    float k = uFogDensity * dist / abs(v.y);
    float ya = min(ro.y, p.y), yb = max(ro.y, p.y), Fa = fogInt(ya);
    od = k * (Fa - fogInt(yb));
    odL = k * (Fa - fogInt(clamp(FOG_YC, ya, yb)));   // part of the path below the cloud-sea base
  } else {
    od = uFogDensity * exp(-(ro.y - FOG_Y0) / FOG_HS) * dist;
    odL = ro.y < FOG_YC ? od : 0.0;
  }
  float odH = max(od - odL, 0.0);
  vec3 ext = vec3(1.18, 0.95, 0.72);
  Te = exp(-od * ext);
  air = mix(FOG_NAVY * uSkyExposure, fogColor(d), smoothstep(0.4, 2.2, odH)) * (1.0 - exp(-odH * 0.32));
  air += FOG_LOW * uSkyExposure * (1.0 - exp(-odL * 0.32)) * (p.y < ro.y ? exp(-odH * ext) : vec3(1.0));
}
vec3 atmosAir(vec3 ro, vec3 p){ vec3 Te, air; atmosTerms(ro, p, Te, air); return air; }
vec3 applyAtmos(vec3 col, vec3 ro, vec3 p){
  vec3 Te, air;
  atmosTerms(ro, p, Te, air);
  // Shadowed mid-distance surfaces (gorge walls, cloud-sea troughs 0.15-3 km out) turn navy (pass 2; refs #17243a /
  // #242f47, blue ~0x20 above red, where ours stayed neutral purple-grey #242433: the dim twilight airlight is far
  // too weak there to tint them). Only the darks (lit snow, the glow side and lights keep their hue), not below the
  // cloud-sea base (the lake / valley floor seen through the gaps: FOG_LOW handles those), fading where the haze
  // takes over.
  float dist = length(p - ro);
  float wm = smoothstep(150.0, 1500.0, dist) * exp(-1.2 * dot(-log(max(Te, vec3(1e-4))), vec3(0.333)))
           * smoothstep(1150.0, 1500.0, p.y) * (1.0 - smoothstep(0.02, 0.16, dot(col, vec3(0.2126, 0.7152, 0.0722))));
  return col * Te * mix(vec3(1.0), vec3(0.62, 0.86, 1.12), wm) + air;
}
`;
