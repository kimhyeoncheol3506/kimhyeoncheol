// GLSL for the ring structure. Ring frame ("local"): origin ring centre at deck top, y up,
// bridges on +/-X, hero/front side +Z. theta = atan(z, x).
import { NOISE, ATMOS } from './common.js';
import { LAMPS_MAX } from '../terrain.js';

export const RING_CONST = /* glsl */ `
#define R_OUT 55.0
#define R_GLASS_OUT 54.4
#define R_GLAZE_IN 47.0
#define R_CANOPY 44.4
#define R_DOWN 45.5       // canopy downlight row over the walkway
#define R_RAIL 42.8
#define R_VOID 42.6
#define Y_SOFFIT -9.3
#define Y_TERRACE -7.3
#define Y_CANOPY -1.9
#define Y_SLOT_TOP -0.8
#define Y_SLOT_BOT -7.0
#define SLOT_A0 36.0
#define SLOT_A1 144.0
#define SLOT_TAPER 16.0
#define SLOT_NM 32.0      // slot mullion bays (3.2 m at R_GLASS_OUT; = SLOT_NM in structure.js)
#define R_SPINE 51.6
#define Y_CEIL -0.8
#define DEG 0.017453292
uniform vec3 uWarm;        // 2700K LED color (linear)
uniform vec3 uInteriorCol; // interior glow
uniform float uLedI;
uniform float uGlazeI;
uniform float uDownI;
uniform vec4 uLampPos[${LAMPS_MAX}];
uniform vec4 uLampCol[${LAMPS_MAX}];
uniform int uLampCount;
uniform mat4 uRingInv;     // world -> ring local

float sdRoundBox(vec2 p, vec2 b, vec4 r){
  r.xy = (p.x > 0.0) ? r.xy : r.zw;
  r.x = (p.y > 0.0) ? r.x : r.y;
  vec2 q = abs(p) - b + r.x;
  return min(max(q.x, q.y), 0.0) + length(max(q, 0.0)) - r.x;
}
float thetaDeg(vec3 lp){ float t = atan(lp.z, lp.x) / DEG; return t < 0.0 ? t + 360.0 : t; }
// signed distance (meters along the facade at R_OUT) to the outer openings; < 0 inside an opening
float openingSDF(vec3 lp){
  float th = thetaDeg(lp);
  float s = th * DEG * R_OUT;
  float d = 1e5;
  // glazed front slot 36-144 deg, lens-shaped (refs 4 / 11): straight head, the sill curving up to a point at each
  // end over SLOT_TAPER deg, full height between (= slotSill() in structure.js)
  {
    float e = min(th - SLOT_A0, SLOT_A1 - th);
    float f = clamp(e / SLOT_TAPER, 0.0, 1.0);
    float sill = Y_SLOT_TOP - (Y_SLOT_TOP - Y_SLOT_BOT) * (1.0 - (1.0 - f) * (1.0 - f));
    d = min(d, max(max(lp.y - Y_SLOT_TOP, sill - lp.y), -e * DEG * R_OUT));
  }
  // bridge portals at 0 and 180 deg: 8 m wide, floor -5.4 .. -0.6
  for (int k = 0; k < 2; k++) {
    float sc = 180.0 * float(k) * DEG * R_OUT;
    float ds = s - sc;
    if (k == 0 && ds > 0.5 * 360.0 * DEG * R_OUT) ds -= 360.0 * DEG * R_OUT;
    d = min(d, sdRoundBox(vec2(ds, lp.y + 3.0), vec2(4.0, 2.4), vec4(1.2, 0.25, 1.2, 0.25)));
  }
  return d;
}
float slotWeight(float th){
  float w = smoothstep(SLOT_A0, SLOT_A0 + SLOT_TAPER * 0.6, th) * (1.0 - smoothstep(SLOT_A1 - SLOT_TAPER * 0.6, SLOT_A1, th));
  return w;
}
// Twilight fill the shared dome model lacks for the ring: bounce from the sunlit-blue cloud sea and
// snow below (downward / vertical faces) and a slight warm-neutral shift measured on the refs' concrete.
// (round 7: a third of round 6's: the bounce lifted every underside to the value of the walls, so the ring read one
// flat grey; the refs' soffits and lower curves are the darkest concrete on the ring)
vec3 ringFill(vec3 wn){
  float dn = clamp(0.5 - 0.5 * wn.y, 0.0, 1.0);
  return vec3(0.045, 0.044, 0.068) * dn * dn * uSkyExposure;
}
const vec3 CONC_TINT = vec3(1.03, 1.0, 0.93);
// (round 7) The near world's key: soft light from the bright sky up and left of the hero views (az 110, 15 deg up:
// = KEY in rock.js and far.js), so the ring is modelled like the rock beside it. Refs 4 / 5 / 7 / 11: the outer wall
// where it turns to camera-left reads pale warm grey (L* 55-62), where it faces the camera mid grey, turned away a
// dark blue-grey (L* 25-30); the deck pale; undersides dark. Returns the irradiance (without uSkyExposure / vis).
const vec3 RKEY = vec3(0.908, 0.259, 0.330);
vec3 ringKey(vec3 wn){
  float kd = dot(wn, RKEY);
  float k = smoothstep(0.3, 0.95, kd);
  // (pass 2) a weak cool key: at 0.32 warm the camera-left end of the outer wall read L* 44-46 #6d6568 against the
  // refs' even cool blue-grey (refs 4 / 5 / 7 / 11: L* 25-31, b* -13; it only looks pale beside the dark rock)
  return vec3(0.085, 0.095, 0.125) * k * k;
}
// faces not turned to the key lose part of the dome too (the bright half of the sky is behind them): the wall facing
// the camera reads mid grey under the pale deck (ref 11: face L* 29 under a deck at 45), turned away darker still
float ringShade(vec3 wn){
  // (pass 2: 0.8..1 - at 0.5 the shade end crushed to L* 21 against the refs' 28-33)
  float s = mix(0.8, 1.0, smoothstep(-0.5, 0.7, dot(wn, RKEY)));
  return mix(s, 1.0, max(wn.y, 0.0));
}
`;

// Analytic warm lighting from LED lines, glazing bands, canopy downlights and lamps.
export const RING_LIGHT = /* glsl */ `
// per-material scaling of the diffuse glazing wash / canopy downlight pools (the polished terrace floor takes
// most of its warmth from reflections, not from diffuse light: ref 1 reads pale grey between the LED lines)
#ifndef GLAZE_K
  #define GLAZE_K 1.0
#endif
#ifndef DOWN_K
  #define DOWN_K 1.0
#endif
float lineE(vec2 pr, vec2 nr, vec2 src, float I){
  vec2 d = src - pr; float dist = length(d) + 1e-3; vec2 L = d / dist;
  float ndl = max(dot(nr, L) * 0.9 + 0.1, 0.0);
  return I * ndl / (0.06 + dist * (0.9 + dist * 0.35));
}
float glazeE(vec2 pr, vec2 nr, float rg, float y0, float y1, float dirSign, float I){
  float yc = clamp(pr.y, y0, y1);
  vec2 d = vec2(rg, yc) - pr; float dist = length(d) + 1e-3; vec2 L = d / dist;
  float emit = max(-L.x * dirSign, 0.0);           // glass emits toward dirSign*r
  float ndl = max(dot(nr, L) * 0.85 + 0.15, 0.0);
  float span = clamp((y1 - y0) / (dist + 0.6), 0.0, 3.0);
  return I * ndl * (0.35 + 0.65 * emit) * span / (0.5 + dist * 0.6 + dist * dist * 0.05);
}
vec3 ringLocalLight(vec3 lp, vec3 ln, vec3 wp, vec3 wn){
  float r = length(lp.xz);
  vec2 rad = lp.xz / max(r, 1e-3);
  vec2 pr = vec2(r, lp.y);
  vec2 nr = vec2(dot(ln.xz, rad), ln.y);
  float th = thetaDeg(lp);
  float E = 0.0;
  // LED lines (r, y)
  E += lineE(pr, nr, vec2(42.72, -9.36), uLedI * 2.2);       // soffit inner edge reveal
  E += lineE(pr, nr, vec2(46.92, -7.24), uLedI * 0.7);       // terrace, glazing base
  E += lineE(pr, nr, vec2(42.96, -7.10), uLedI * 0.7);       // terrace, balustrade base
  E += lineE(pr, nr, vec2(R_CANOPY + 0.22, 0.06), uLedI * 0.3); // roof balustrade base (soft line)
  float sw = slotWeight(th);
  E += lineE(pr, nr, vec2(55.05, -7.95), uLedI * 0.1 * sw);  // faint outer line under the slot only (refs 4 / 11: dark underside)
  // (round 7) a hidden cove along the outer bottom edge washes the lower curve warm (refs 5 / 6 / 7 / 11: a bright
  // amber band ~1 m tall along the foot of the outer wall, the soffit beyond it dark)
  // (kept thin: ref 4's centre column runs dark band head 26 / band 60 / dark 23 / warm line 42 / dark 21)
  E += lineE(pr, nr, vec2(55.2, -9.45), uLedI * 0.15) * step(53.3, r);
  // (pass 2) ...and its hot edge: a narrow amber line where the wall turns into the soffit, over the dark wall above
  // and the dark underside (refs 5 / 6 at 100%: L* 41 #775a4a, b* +12, ~0.5 m, between a wall at 35 and the soffit)
  {
    vec2 dc = pr - vec2(54.55, -8.95);
    E += uLedI * 0.75 * exp(-dot(dc, dc) / 0.09) * step(53.3, r) * max(dot(nr, vec2(0.7, -0.7)) * 0.8 + 0.2, 0.0);
  }
  // soffit: broad warm wash from the inner reveal LED and the outer fillet line, cool blue-grey between
  float dn = max(-nr.y, 0.0) * step(lp.y, -9.0);
  // (ref 3: warm and bright along the inner reveal, falling to blue-grey mid-soffit)
  E += dn * (0.8 * exp(-max(r - 42.7, 0.0) / 2.6) + 0.25 * exp(-max(53.6 - r, 0.0) / 1.6));
  E += lineE(pr, nr, vec2(54.75, Y_SLOT_BOT + 0.05), uLedI * 0.08 * sw); // slot sill (faint: no bright line under the band)
  // glazing bands
  E += glazeE(pr, nr, R_GLAZE_IN, Y_TERRACE, Y_CANOPY, -1.0, uGlazeI * GLAZE_K);
  E += glazeE(pr, nr, R_GLASS_OUT, Y_SLOT_BOT, Y_SLOT_TOP, 1.0, uGlazeI * sw * 0.9);
  // canopy downlight pools on the terrace (every 2.5 m of arc at R_DOWN)
  float arc = th * DEG * R_DOWN;
  float cellA = (fract(arc / 2.5) - 0.5) * 2.5;
  vec2 dd = vec2(cellA, r - R_DOWN);
  float h = Y_CANOPY - lp.y;
  if (h > 0.0 && r > 42.0 && r < 47.5) {
    float sg = 0.3 + 0.1 * h;
    float pool = exp(-dot(dd, dd) / (2.0 * sg * sg));
    E += uDownI * 1.4 * DOWN_K * pool * max(ln.y, 0.0) / (1.0 + h * h * 0.06);
  }
  vec3 col = uWarm * E;
  // discrete lamps (strut collars / footings / pavilions)
  for (int i = 0; i < ${LAMPS_MAX}; i++) {
    if (i >= uLampCount) break;
    vec3 L = uLampPos[i].xyz - wp; float d2 = dot(L, L); L *= inversesqrt(max(d2, 1e-6));
    col += uLampCol[i].rgb * max(dot(wn, L) * 0.85 + 0.15, 0.0) / (d2 + uLampPos[i].w * uLampPos[i].w) / (1.0 + d2 * 0.008);
  }
  return col;
}
`;

// All varyings are centroid-sampled. With the 4x MSAA scene target the fragment shader of a pixel that a
// triangle only partly covers otherwise runs at the pixel centre, outside the triangle: thin slivers seen at
// grazing angles (path deck, far ceilings, terrace floor edges) extrapolate the perspective-correct varyings
// without bound (1/w -> 0), so exp()/divisions on them returned 1e5+ or NaN in one MSAA sample, which the
// resolve spread into 16376 (= 65504 / 4) hot pixels and NaN pixels -> one-frame white bloom discs.
// (vNormal* stay unit length in the vertex stage; a zero normal from a degenerate lathe ring maps to +Y.)
const VARYINGS = /* glsl */ `
centroid varying vec3 vWorld; centroid varying vec3 vLocal; centroid varying vec3 vNormalW; centroid varying vec3 vNormalL;
centroid varying vec2 vUv; centroid varying vec3 vInstCol; centroid varying vec3 vAxis;
`;
// final guard on every structure fragment: finite, non-negative, below the brightest authored emitter
// (D3D min/max return the non-NaN operand, so a stray NaN lands on 0 instead of blooming)
const SAFE_OUT = /* glsl */ `
vec3 safeOut(vec3 c){ return min(max(c, vec3(0.0)), vec3(48.0)); }
vec3 safeN(vec3 v){ float l = length(v); return l > 1e-6 ? v / l : vec3(0.0, 1.0, 0.0); }
`;

export const VERT = /* glsl */ `
#include <common>
#include <logdepthbuf_pars_vertex>
${VARYINGS}
uniform mat4 uRingInv;
vec3 safeNrm(vec3 v){ float l = length(v); return l > 1e-6 ? v / l : vec3(0.0, 1.0, 0.0); }
void main(){
  vec4 lp = vec4(position, 1.0);
  vec3 ln = normal;
  #ifdef USE_INSTANCING
    lp = instanceMatrix * lp;
    ln = mat3(instanceMatrix) * ln;
  #endif
  vec4 wp = modelMatrix * lp;
  vWorld = wp.xyz;
  vLocal = (uRingInv * wp).xyz;
  vNormalW = safeNrm(mat3(modelMatrix) * ln);
  vNormalL = safeNrm(mat3(uRingInv) * vNormalW);
  vUv = uv;
  vec3 ax = vec3(0.0, 1.0, 0.0);
  #ifdef USE_INSTANCING
    ax = mat3(instanceMatrix) * ax;
  #endif
  vAxis = safeNrm(mat3(modelMatrix) * ax);
  #ifdef USE_INSTANCING_COLOR
    vInstCol = instanceColor;
  #else
    vInstCol = vec3(1.0);
  #endif
  gl_Position = projectionMatrix * viewMatrix * wp;
  #include <logdepthbuf_vertex>
}
`;

// Concrete with pattern variants: SURF 0 generic, 1 roof pavers, 2 outer wall (formwork, openings),
// 3 soffit, 4 terrazzo floor, 5 fascia/inner faces, 6 canopy soffit, 7 interior side of outer wall (cream)
export const CONCRETE_FRAG = /* glsl */ `
#include <common>
#include <logdepthbuf_pars_fragment>
${NOISE}
${ATMOS}
${RING_CONST}
${RING_LIGHT}
${VARYINGS}
${SAFE_OUT}
uniform vec3 uAlbedo;
uniform float uAO;
uniform sampler2D tConcD;   // photographic cast concrete (Poly Haven concrete_wall_006, CC0): diffuse (sRGB -> linear)
uniform sampler2D tConcN;   // its OpenGL normal map
uniform float uConcOn;      // 0 if the maps did not load (flat 1x1 stand-ins)
const vec3 LUMW = vec3(0.2126, 0.7152, 0.0722);
// Photographic concrete on a 2.4 m tile: uvm in metres (already offset per formwork panel: every pour different, no
// visible repeat); gx / gy are its screen gradients taken from the continuous ring coordinates, so neither the panel
// offsets nor the theta wrap leave mip seams. Returns the albedo factor (mean 1: tone, pores, blowholes, stains and a
// little of the photo's own hue); tn = tangent-space normal (xy scaled by amp).
// iso (horizontal faces): the photo's vertical run-off streaks read as radial brush marks on the soffits (ref 9 is
// a calm cast soffit), so a second cut rotated 90 deg is averaged in and the broad layer is dropped.
// hp (polished floor): high-pass against a sample 4 mip levels coarser: only pores / aggregate, no cloudy stains.
// uvB: the continuous (not per-panel offset) coordinates for the broad layer, so weathering runs across the joints
// instead of every panel showing its own stain (a checkerboard from the bridges, ref 10)
vec3 concTex(vec2 uvm, vec2 uvB, vec2 gx, vec2 gy, float amp, float iso, float hp, out vec3 tn){
  vec2 uv = uvm / 2.4; uvB /= 2.4; gx /= 2.4; gy /= 2.4;
  vec3 m = textureLod(tConcD, vec2(0.5), 12.0).rgb;
  vec3 c = textureGrad(tConcD, uv, gx, gy).rgb;
  float lm = max(dot(m, LUMW), 1e-4);
  float l = dot(c, LUMW) / lm;
  tn = textureGrad(tConcN, uv, gx, gy).xyz * 2.0 - 1.0;
  vec3 hue = mix(vec3(1.0), c / max(m * l, vec3(1e-4)), 0.12);
  // (pass 2) high-pass: the photo's 0.3-2 m cloudy stains read as dirty camouflage on the big soffits / fascias
  // (ref 9: pale, even concrete with crisp joints and fine grain). Each cut is divided by a sample ~3.5 mips coarser
  // (never finer than ~0.1 m) and keeps 35% of that broad layer, with the fine grain lifted a little.
  float lod0 = log2(max(max(length(gx), length(gy)) * 2048.0, 1.0));
  float lodC = max(lod0 + 3.5, 6.5);
  float hpK = 1.0 - hp;
  float lcA = max(dot(textureLod(tConcD, uv, lodC).rgb, LUMW) / lm, 0.25);
  l = mix(l, pow(max(l / lcA, 0.0), 1.2) * mix(1.0, lcA, 0.35), hpK);
  if (iso > 0.5) {
    // (u, v) -> (v, -u): the rotated cut's normal xy maps back as (-y, x)
    vec2 ub = vec2(uv.y, -uv.x) + vec2(0.53, 0.29), gxb = vec2(gx.y, -gx.x), gyb = vec2(gy.y, -gy.x);
    float lb = dot(textureGrad(tConcD, ub, gxb, gyb).rgb, LUMW) / lm;
    float lcB = max(dot(textureLod(tConcD, ub, lodC).rgb, LUMW) / lm, 0.25);
    lb = mix(lb, pow(max(lb / lcB, 0.0), 1.2) * mix(1.0, lcB, 0.35), hpK);
    vec3 nb = textureGrad(tConcN, ub, gxb, gyb).xyz * 2.0 - 1.0;
    l = 1.0 + (0.5 * (l + lb) - 1.0) * 1.35;
    tn = vec3(0.5 * (tn.xy + vec2(-nb.y, nb.x)) * 1.3, 0.5 * (tn.z + nb.z));
  }
  float l2 = 1.0;
  if (hp > 0.5) {
    l /= max(dot(textureGrad(tConcD, uv, gx * 16.0, gy * 16.0).rgb, LUMW) / lm, 0.2);
  } else {
    // a second cut at 3.1x the frequency: sub-centimetre pores and grain up close (mip-mapped: it averages to 1
    // before it could shimmer)
    mat2 rf = mat2(0.6, -0.8, 0.8, 0.6);
    vec2 uf = rf * uv * 3.1 + 0.71;
    float lf = dot(textureGrad(tConcD, uf, rf * gx * 3.1, rf * gy * 3.1).rgb, LUMW) / lm;
    l *= mix(1.0, lf, 0.35);
  }
  if (hp < 0.5 && iso < 0.5) {
    // broad weathering: the same photo 4.3x larger and rotated, luminance only
    mat2 rot = mat2(0.8, 0.6, -0.6, 0.8);
    l2 = mix(1.0, dot(textureGrad(tConcD, rot * uvB * 0.23 + 0.37, rot * gx * 0.23, rot * gy * 0.23).rgb, LUMW) / lm, 0.3);
  }
  vec3 f = l * hue * l2;
  // the coarse mips of the normal map are the photo's broad undulations: under the soffit washes they lit up as
  // 1-3 m cloudy blotches from the drones, so the normals calm down with distance (the fine relief stays up close)
  tn.xy *= amp * uConcOn * mix(1.0, 0.4, smoothstep(4.0, 7.0, lod0) * hpK);
  return mix(vec3(1.0), f, amp * uConcOn);
}
// photo-concrete mapping on the ring: horizontal faces (arc at 48 m, radius), faces looking out / in (arc, height),
// faces looking along the arc (radius, height). T / B = ring-frame directions of +u / +v; gradients from dFdx(lp).
void polarMap(vec3 lp, vec3 ln, float r, float th, vec3 tang, vec3 radl, vec3 dpx, vec3 dpy,
              out vec2 uv, out vec2 gx, out vec2 gy, out vec3 T, out vec3 B){
  float at = abs(dot(ln, tang)), ar = abs(dot(ln, radl)), ay = abs(ln.y);
  if (ay >= at && ay >= ar) {
    float k = 48.0 / max(r, 1.0);
    uv = vec2(th * DEG * 48.0, r); T = tang; B = radl;
    gx = vec2(dot(dpx, tang) * k, dot(dpx, radl)); gy = vec2(dot(dpy, tang) * k, dot(dpy, radl));
  } else if (ar >= at) {
    uv = vec2(th * DEG * r, lp.y); T = tang; B = vec3(0.0, 1.0, 0.0);
    gx = vec2(dot(dpx, tang), dpx.y); gy = vec2(dot(dpy, tang), dpy.y);
  } else {
    uv = vec2(r, lp.y); T = radl; B = vec3(0.0, 1.0, 0.0);
    gx = vec2(dot(dpx, radl), dpx.y); gy = vec2(dot(dpy, radl), dpy.y);
  }
}
// box faces (bridges, pavilions, plinths): planar along the dominant ring-frame axis
void planarMap(vec3 lp, vec3 ln, vec3 dpx, vec3 dpy, out vec2 uv, out vec2 gx, out vec2 gy, out vec3 T, out vec3 B){
  vec3 a = abs(ln);
  if (a.y >= a.x && a.y >= a.z) { uv = lp.xz; gx = dpx.xz; gy = dpy.xz; T = vec3(1.0, 0.0, 0.0); B = vec3(0.0, 0.0, 1.0); }
  else if (a.x >= a.z) { uv = lp.zy; gx = dpx.zy; gy = dpy.zy; T = vec3(0.0, 0.0, 1.0); B = vec3(0.0, 1.0, 0.0); }
  else { uv = lp.xy; gx = dpx.xy; gy = dpy.xy; T = vec3(1.0, 0.0, 0.0); B = vec3(0.0, 1.0, 0.0); }
}
// tie hole (plugged cone, 70 mm at the face) at panel-local position q (m) on a grid of pitch g: albedo factor. From afar the
// dot is drawn at least ~1.4 px across with its contrast scaled by true coverage (refs 3 / 9 keep the regular grid
// of holes readable on the soffit from 80 m), and fades out before the grid could beat against the pixels
float tieHole(vec2 q, vec2 g, float px){
  vec2 f = (fract(q / g) - 0.5) * g;
  float d = length(f);
  const float rh = 0.035;
  float rw = max(rh, px * 0.85);
  float cov = sqrt(rh / rw);   // (well above the true coverage: the refs' grid of holes reads clearly from afar)
  float h = 1.0 - smoothstep(rw * 0.6, rw + px * 0.5, d);
  float rim = smoothstep(rh * 1.3, rh * 1.9, d) * (1.0 - smoothstep(rh * 1.9, rh * 3.0, d)) * (1.0 - smoothstep(0.005, 0.02, px));
  return 1.0 + 0.06 * rim - 0.72 * h * cov * (1.0 - smoothstep(0.16, 0.3, px));
}
// polished-stone aggregate: one round chip per cell (m) at a random spot, dark / pale / mid; antialiased by the pixel
// footprint and faded out before a cell gets near a pixel (no sparkle in the film)
float speckle(vec2 q, float cell, float px){
  vec2 c = floor(q / cell), f = q / cell - c;
  vec2 o = 0.28 + 0.44 * hash22(c + 3.1);
  float t = hash12(c + 7.7), rad = 0.16 + 0.16 * hash12(c + 1.3);
  float aa = px / cell + 0.03;
  float d = 1.0 - smoothstep(rad - aa, rad + aa, length(f - o));
  float tone = t < 0.5 ? -0.4 : (t < 0.78 ? 0.25 : -0.15);
  return 1.0 + tone * d * (1.0 - smoothstep(cell * 0.2, cell * 0.7, px));
}
void main(){
  #include <logdepthbuf_fragment>
  vec3 lp = vLocal;
  float r = length(lp.xz);
  float th = thetaDeg(lp);
  vec3 wn = safeN(vNormalW) * (gl_FrontFacing ? 1.0 : -1.0);
  vec3 ln = safeN(vNormalL) * (gl_FrontFacing ? 1.0 : -1.0);
  // ring-frame screen derivatives (taken before any discard) and the polar frame
  vec3 dpx = dFdx(lp), dpy = dFdy(lp);
  vec3 tang = vec3(-lp.z, 0.0, lp.x) / max(r, 1e-3), radl = vec3(lp.x, 0.0, lp.z) / max(r, 1e-3);
  #if SURF == 2 || SURF == 7
    float od = openingSDF(lp);
    #if SURF == 2
      if (od < 0.0) discard;
    #else
      if (od < 0.0) discard;
    #endif
  #endif
  vec3 alb = uAlbedo;
  float dist = length(vWorld - cameraPosition);
  // pixel footprint (m) for pattern AA, from the screen derivatives: right for the long-lens drone views too
  // (dist * 0.0012 assumed a ~60 deg lens and erased all fine detail at 14-25 deg)
  float px = max(max(length(dpx), length(dpy)), dist * 1e-4);
  // large-scale mottling (the photo maps carry the fine tone, pores and stains)
  float mott = fbm3(vWorld * 0.35, 4);
  float mott2 = vnoise3(vWorld * 2.2);
  #if SURF == 10
    alb *= vInstCol;   // figures: plain clothing colour per instance
  #else
    alb *= 0.95 + 0.06 * mott + 0.04 * (mott2 - 0.5);
  #endif
  float joint = 0.0;
  float specMask = 0.0;
  // photo concrete: mapping (tuv, gradients, frame) and amplitude set per surface below; tamp 0 = none
  vec2 tuv = vec2(0.0), tgx = vec2(0.0), tgy = vec2(0.0);
  vec3 tT = tang, tB = radl;
  float tamp = 0.0;
  float tiso = step(0.7, abs(ln.y)), thp = 0.0;   // horizontal faces: no directional run-off streaks
  #if SURF == 0
    planarMap(lp, ln, dpx, dpy, tuv, tgx, tgy, tT, tB);
  #elif SURF != 4 && SURF != 8 && SURF != 9 && SURF != 10
    polarMap(lp, ln, r, th, tang, radl, dpx, dpy, tuv, tgx, tgy, tT, tB);
  #endif
  vec2 tuv0 = tuv;   // continuous coordinates (broad weathering layer)
  #if SURF == 1
    // roof pavers 1.5 (tangential) x 1.2 (radial), 12 radial joints at 15+30k
    float sArc = th * DEG * r;
    vec2 tc = vec2(sArc / 1.5, (r - R_CANOPY) / 1.2);
    vec2 tf = abs(fract(tc) - 0.5) * vec2(1.5, 1.2);           // distance from the tile centre (m)
    vec2 tdist = vec2(0.75, 0.6) - tf;                          // distance to the joint (m)
    // joints stay readable from the aerial views: drawn >= ~1 px wide, contrast scaled by true coverage
    float fw = max(length(fwidth(lp.xz)), 1e-4);
    float jw = 0.012, wv = max(jw, fw * 0.75);
    float cov = max(jw / wv, 0.6);
    joint = max(1.0 - smoothstep(wv * 0.5, wv, tdist.x), 1.0 - smoothstep(wv * 0.5, wv, tdist.y));
    // refs 4 / 7 / 11: the deck reads as a calm pale annulus, the paver grid barely visible from the air
    alb *= 1.0 - 0.30 * cov * joint;
    // (pass 2: ref 8 shows ~+-3 L* slab to slab; the mean is kept)
    float tile = hash12(floor(tc)), tile2 = hash12(floor(tc) + 7.7);
    alb *= 0.89 + 0.21 * tile;
    alb *= mix(vec3(0.985, 1.0, 1.015), vec3(1.03, 1.0, 0.96), tile2);      // warm / cool stones
    alb *= 1.02 - 0.1 * smoothstep(0.5, 0.85, fbm2(lp.xz * 0.12, 3));   // weathering / damp patches
    float jd = abs(mod(th - 15.0 + 15.0, 30.0) - 15.0) * DEG * r;  // distance to radial joint
    float jm = 1.0 - smoothstep(0.22, 0.26, jd);
    alb = mix(alb, alb * 0.6, jm);
    specMask = jm * (1.0 - smoothstep(0.02, 0.05, jd));
    // each paver its own cut of the photo, kept calm (refs 7 / 8: a pale, quiet deck)
    tuv += hash22(floor(tc)) * 17.0;
    tamp = 0.3;
  #elif SURF == 2
    // formwork (ref 10 at 100%): tall panels 2.4 m wide over the full lift height, dominant vertical joints, one
    // horizontal lift line at mid-height, two columns of tie holes per panel, 12 vertical construction joints
    float sArc = th * DEG * R_OUT;
    // (pass 2) board-form: wide panels 3.6 x 1.3 m in horizontal courses, the course joints dominant (ref 5 at 100%,
    // x 450-780: horizontal panels with darker joints; the tall vertical panels read as fine vertical streaks)
    vec2 PSZ = vec2(3.6, 1.3);
    vec2 pc = vec2(sArc / PSZ.x + 0.5 * mod(floor(-lp.y / PSZ.y), 2.0), (-lp.y) / PSZ.y);
    vec2 pf = fract(pc);
    vec2 pd = min(pf, 1.0 - pf) * PSZ;
    float jw = max(0.012, px * 0.5);
    joint = max(0.6 * (1.0 - smoothstep(jw * 0.8, jw * 1.8, pd.x)), 1.0 - smoothstep(jw, jw * 2.2, pd.y));
    float pid = hash12(floor(pc)), pid2 = hash12(floor(pc) + 19.1), pid3 = hash12(floor(pc) + 5.3);
    // pour-to-pour variation: tone (+-10%: ref 10 shows ~+-4 L* panel to panel), a slight warm/cool cast, a gradient
    // across the panel, darker bleed at the edges
    alb *= 0.9 + 0.2 * pid;
    alb *= mix(vec3(0.99, 0.995, 1.02), vec3(1.02, 1.0, 0.97), pid2);
    alb *= 1.0 + 0.06 * (pid3 - 0.5) * (pf.x * 2.0 - 1.0) + 0.04 * (pid - 0.5) * (pf.y * 2.0 - 1.0);
    alb *= 1.0 - 0.07 * exp(-pd.y / 0.1);
    // tie holes: 3 columns x 2 rows per board panel
    alb *= tieHole(pf * PSZ, vec2(1.2, 0.65), px);
    alb *= 1.0 - 0.24 * joint * (1.0 - smoothstep(0.03, 0.25, px));
    tuv += hash22(floor(pc)) * 17.0;
    tamp = 0.75;
    float jd = abs(mod(th - 15.0 + 15.0, 30.0) - 15.0) * DEG * R_OUT;
    alb *= 1.0 - 0.35 * (1.0 - smoothstep(0.2, 0.26, jd));
    // rain streaks below the openings
    float streak = vnoise3(vec3(sArc * 2.6, lp.y * 0.08, 0.0));
    alb *= 1.0 - 0.05 * smoothstep(0.5, 0.9, streak) * smoothstep(-0.5, -5.0, lp.y);   // (pass 2: 0.14 -> 0.05)
    // run-off staining from the cornice and the slot sill, fading downward
    float drip = smoothstep(0.55, 0.95, vnoise2(vec2(sArc * 0.8, 0.5))) * vnoise2(vec2(sArc * 6.0, lp.y * 0.4));
    float below = exp(-max(-lp.y - 0.2, 0.0) / 2.5) + exp(-max(od, 0.0) / 1.2) * step(lp.y, Y_SLOT_BOT);
    alb *= 1.0 - 0.14 * drip * clamp(below, 0.0, 1.0);
  #elif SURF == 3
    // soffit panels (ref 9 at 100%: crisp rectangular panels, a regular 2 x 3 grid of tie holes in each): radial
    // joints every 3.75 deg (3.1 m at r 48), concentric joints every 1.8 m from r 44.6
    float jw = max(0.012, px * 0.5);
    float jr = abs(fract((r - 44.6) / 1.8 + 0.5) - 0.5) * 1.8;
    joint = max(1.0 - smoothstep(jw, jw * 2.0, abs(mod(th + 1.875, 3.75) - 1.875) * DEG * r), 1.0 - smoothstep(jw, jw * 2.0, jr));
    alb *= 1.0 - 0.36 * joint * (1.0 - smoothstep(0.08, 0.4, px));
    vec2 sid = vec2(floor(th / 3.75), floor((r - 44.6) / 1.8));
    alb *= 0.955 + 0.07 * hash12(sid);   // pour-to-pour tone (ref 9: every panel a shade different, but calm)
    // tie holes: 3 along the arc x 2 across in every panel; shutter lines every 0.6 m running with the arc
    // (footprint between the two axes: the soffit is seen obliquely from below, and the larger axis alone blurred
    // the holes away from the bridges, ref 9)
    float pw3 = 3.75 * DEG * r;
    float pxh = mix(sqrt(length(dpx) * length(dpy)), px, 0.5);
    alb *= tieHole(vec2(mod(th, 3.75) * DEG * r, r - 44.6), vec2(pw3 / 3.0, 0.9), pxh);
    float shl = abs(fract((r - 42.85) / 0.6) - 0.5) * 0.6;
    alb *= 1.0 - 0.05 * (1.0 - smoothstep(0.004, 0.012 + px * 0.5, 0.3 - shl)) * (1.0 - smoothstep(0.02, 0.1, px));
    tuv += hash22(sid) * 17.0;
    tamp = 0.9;
  #elif SURF == 4
    // polished pale-grey stone (ref 1): fine speckle, large slabs with transverse joints every 1.5 m and a faint
    // cloudy veining; slab-to-slab tone shifts
    // (pass 2) rectangular slabs in running bond: three rows of 1.35 m across the walk, transverse joints every 1.5 m
    // (ref 1); isotropic cloudiness (the arc-stretched noise read as streaks along the walk)
    float sArc = th * DEG * r;
    float row = floor((r - 42.95) / 1.35);
    float sOff = sArc / 1.5 + 0.5 * mod(row, 2.0);
    float jd = abs(fract(sOff) - 0.5) * 1.5;
    float jr = abs(fract((r - 42.95) / 1.35) - 0.5) * 1.35;
    joint = 1.0 - smoothstep(0.004, 0.010 + px * 0.5, min(0.75 - jd, 0.675 - jr));
    alb *= 1.0 - 0.32 * joint;
    vec2 slab = vec2(floor(sOff), row);
    alb *= 0.95 + 0.08 * hash12(slab + 3.0);
    alb *= 0.96 + 0.06 * fbm2(vec2(sArc, r) * 1.1, 3);
    // aggregate: the concrete photo at 1/2 scale, high-passed (ref 1 at 100%: a fine granular speckle of chips and
    // pores, no cloudy blotches; mip-mapped, so it fades to the slab tone at distance), each slab its own cut; faded
    // at grazing view, where the unfiltered photo smeared into streaks along the view
    polarMap(lp, ln, r, th, tang, radl, dpx, dpy, tuv, tgx, tgy, tT, tB);
    tuv = tuv * 2.0 + hash22(slab + 5.0) * 17.0; tgx *= 2.0; tgy *= 2.0;
    // isotropic footprint (the 8x anisotropic sampling kept the photo sharp across the view and smeared it along:
    // hairy streaks along the walk); faded further at grazing view
    float gmx = max(length(tgx), length(tgy));
    tgx *= gmx / max(length(tgx), 1e-7); tgy *= gmx / max(length(tgy), 1e-7);
    // (the photo's run-off streaks, cross-cut on horizontal faces, read as hairlines along the walk: kept faint, the
    // stochastic chips below carry the stone's grain)
    tamp = mix(0.2, 0.7, smoothstep(0.08, 0.4, abs(dot(normalize(cameraPosition - vWorld), wn))));
    thp = 1.0;
    // chips: isotropic footprint (larger axis), so they fade instead of aliasing into streaks at grazing view
    // (a 4.5 cm chip layer read as rows of dashes along the walk: left out)
    float pxs = max(length(dpx), length(dpy)) + dist * 1e-4;
    alb *= speckle(vec2(sArc, r), 0.022, pxs) * speckle(vec2(sArc, r) + 0.37, 0.011, pxs);
    specMask = 1.0;
  #elif SURF == 6
    // canopy soffit with recessed downlights every 2.5 m at r=46.4
    float arc = th * DEG * R_DOWN;
    vec2 dd = vec2((fract(arc / 2.5) - 0.5) * 2.5, r - R_DOWN);
    float dl = 1.0 - smoothstep(0.07, 0.09, length(dd));
    if (dl > 0.0) { gl_FragColor = vec4(safeOut(applyAtmos(uWarm * 16.0, cameraPosition, vWorld)), 1.0); return; }
    // cast panels (ref 1): radial joints midway between the downlights (2.5 m of arc at the downlight row), one
    // joint along the arc, tie holes in a row 0.3 m beside each radial joint
    float jw = max(0.01, px * 0.5);
    vec2 pq = vec2(arc / 2.5, r < 45.95 ? 0.0 : 1.0);
    float pj = (0.5 - abs(fract(pq.x) - 0.5)) * 2.5;
    joint = max(1.0 - smoothstep(jw, jw * 2.0, pj), 1.0 - smoothstep(jw, jw * 2.0, abs(r - 45.95)));
    alb *= 1.0 - 0.3 * joint * (1.0 - smoothstep(0.03, 0.25, px));
    alb *= 0.94 + 0.1 * hash12(floor(pq) + 2.0);
    alb *= tieHole(vec2(fract(pq.x) * 2.5 + 0.65, r - 44.4), vec2(1.9, 0.85), px);
    tuv += hash22(floor(pq)) * 17.0;
    tamp = 0.8;
  #elif SURF == 0 || SURF == 11 || SURF == 5
    // bridges, pavilions, plinths, slot / portal reveals, fascias: cast panels (3.6 x 1.5 m on the fascias, 3 x 1.5 m
    // elsewhere) with faint joints, tie holes, pour-to-pour tone (refs 3 / 10)
    vec2 psz = SURF == 5 ? vec2(3.6, 1.5) : vec2(3.0, 1.5);
    vec2 pq0 = tuv / psz;
    vec2 pf0 = fract(pq0);
    vec2 pd0 = min(pf0, 1.0 - pf0) * psz;
    float jw = max(0.01, px * 0.5);
    joint = 1.0 - smoothstep(jw, jw * 2.0, min(pd0.x, pd0.y));
    alb *= 1.0 - 0.22 * joint * (1.0 - smoothstep(0.03, 0.25, px));
    alb *= 0.95 + 0.07 * hash12(floor(pq0) + 4.0);
    alb *= tieHole(pf0 * psz, psz / vec2(4.0, 2.0), px);
    tuv += hash22(floor(pq0)) * 17.0;
    tamp = SURF == 5 ? 0.75 : 0.9;
  #elif SURF == 8
    // snow drift (vUv.x = 0 at the glass): fine crystal sparkle
    alb = uAlbedo * (0.97 + 0.03 * mott);
    float sp = step(0.996, hash13(floor(vWorld * 70.0)));
  #elif SURF == 9
    // walkway: pale broom-finished concrete, damp; LED lines along both edges (vUv.x across)
    float ex = min(vUv.x, 1.0 - vUv.x) * 2.4;
    alb *= 0.9 + 0.12 * vnoise2(vec2(vUv.y * 2.0, vUv.x * 7.0));
    alb *= 1.0 - 0.06 * step(0.5, fract(vUv.y * 2.0 / 3.0)) * (1.0 - smoothstep(0.02, 0.2, px));
    float wet = smoothstep(0.35, 0.75, fbm2(vec2(vUv.y * 0.6, vUv.x * 2.5), 4));
    tuv = vec2(vUv.x * 2.4, vUv.y); tgx = dFdx(tuv); tgy = dFdy(tuv);
    tuv0 = tuv;
    tamp = 0.8;
  #endif
  // apply the photo concrete: albedo, and its normal map (ring frame) on the lighting normals
  vec3 wnG = wn;   // geometric normal (the polished floor's mirror image stays smooth)
  if (tamp > 0.0) {
    vec3 tn;
    alb *= concTex(tuv, tuv0, tgx, tgy, tamp, tiso, thp, tn);
    #if SURF != 9
      ln = safeN(tT * tn.x + tB * tn.y + ln * max(tn.z, 0.2));
      wn = safeN(transpose(mat3(uRingInv)) * ln);
    #endif
  }
  #if SURF == 2
    // (round 7) the eased arris at the roof edge turns up to the sky: the bright lip of refs 4 / 7 / 11 (~0.3 m)
    // (ref 4's centre column: the lip reads L* 60-62 between the deck at 47 and the dark band head at 26)
    {
      float bev = smoothstep(-0.55, -0.08, lp.y);
      ln = safeN(ln + vec3(0.0, 2.0, 0.0) * bev);
      wn = safeN(transpose(mat3(uRingInv)) * ln);
      alb *= 1.0 + 0.8 * bev;
    }
  #endif

  // sky light with analytic occlusion per surface family
  float vis = uAO;
  #if SURF == 4
    vis *= mix(0.18, 0.75, smoothstep(45.3, 42.6, r));      // under the 2.6 m canopy
  #elif SURF == 3
    vis *= 0.72;
  #elif SURF == 11
    // (round 7) the slot / portal reveals darken into the recess toward the glass (a dark frame around the lit band)
    vis *= mix(0.45, 1.0, smoothstep(54.3, 55.0, r));
  #endif
  // (round 7) tops a cooler, brighter sky white (refs 4 / 11 deck #5d6a8c..#606a90, L* 45 over a mid-grey wall)
  vec3 E = skyIrradiance(wn, vis, 0.15) * mix(vec3(1.0), vec3(1.24, 1.30, 1.36), max(wn.y, 0.0)) + ringFill(wn) * vis;
  #if SURF == 2
    // (round 7) the wall pales toward the roof edge and darkens down toward the curve into the soffit (ref 11: L* ~50
    // under the lip, ~32 above the warm foot)
    // (pass 2: steeper, and a cooler blue-grey: refs 4 / 5 / 11 the face b* -13..-15, p90 45-50 only in the top third
    // under the lip, p10 22-25 at the foot; ours read b* -1..-5)
    E *= mix(0.6, 1.16, pow(smoothstep(-7.8, -0.6, lp.y), 1.4)) * vec3(0.92, 0.98, 1.13);
  #endif
  // (round 7) form light: the key from camera-left, the shade side darker; recessed / covered faces get the key
  // only as far as they see the open sky (vis)
  E = E * ringShade(wn) + ringKey(wn) * vis * vis * uSkyExposure;
  #if SURF == 3
    // (round 7) the refs disagree on the underside: from the drones (4 / 7 / 11) the curve into the soffit and the soffit
    // edge read darkest on the ring, but looking straight up (refs 9 / 3) the soffit is pale cast concrete. Seen face-on
    // from below it keeps round 6's value; at the drones' grazing view the dark of the shade side.
    E *= mix(1.0, 2.4, smoothstep(0.2, 0.75, dot(normalize(cameraPosition - vWorld), wn)));
  #endif
  #if SURF == 6
    // the canopy soffit sees the lit terrace floor and the glazing, not the blue cloud sea: warm bounce instead of
    // most of the cool fill (ref 1: soffit #986e53, L37)
    E = E * 0.55 + uWarm * 0.16 + uInteriorCol * 0.05;
  #endif
  E += ringLocalLight(lp, ln, vWorld, wn);
  #if SURF == 6 || SURF == 4
    // warm spill of the restaurant through the inner glazing
    E += uInteriorCol * (SURF == 6 ? 0.17 : 0.05) * exp(-max(R_GLAZE_IN - r, 0.0) * 0.9) * (SURF == 6 ? 1.0 : max(ln.y, 0.0));
  #endif
  #if SURF == 4
    // the two base LED strips wash the stone in a bright warm band ~0.4 m wide along the balustrade and the glazing
    // (ref 1: the brightest floor is right at both edges)
    // (pass 2: narrower and weaker: the near floor read 6 L* too bright and too warm, b* +12 vs ref +2)
    E += uWarm * uLedI * (0.9 * exp(-max(r - 42.95, 0.0) / 0.26) + 0.75 * exp(-max(R_GLAZE_IN - r, 0.0) / 0.25)) * max(ln.y, 0.0);
  #elif SURF == 8
    E += uWarm * uLedI * 0.55 * exp(-vUv.x * 4.0);          // base LED grazing the drift
  #elif SURF == 9
    E += uWarm * uLedI * 0.45 * exp(-ex / 0.35);
  #endif
  vec3 col = alb * E;

  // subtle sheen: horizon reflection at grazing angles (roof), polished terrazzo reflections
  vec3 V = normalize(cameraPosition - vWorld);
  #if SURF == 4
    wn = wnG;
  #endif
  float fres = pow(1.0 - max(dot(V, wn), 0.0), 5.0);
  vec3 R = reflect(-V, wn);
  #if SURF == 4
    // reflected glow of the glazing/LEDs: streaks on the polished floor
    col += uWarm * uLedI * 0.012 * (0.2 + fres) * smoothstep(44.5, 47.0, r);
    // mirror image of the lit restaurant glazing (ref 1): trace the reflected ray to the r = 47 glass band
    vec3 Rl = mat3(uRingInv) * R;
    float win = 0.0;
    float qa = dot(Rl.xz, Rl.xz), qb = 2.0 * dot(lp.xz, Rl.xz), qc = dot(lp.xz, lp.xz) - R_GLAZE_IN * R_GLAZE_IN;
    float disc = qb * qb - 4.0 * qa * qc;
    if (disc > 0.0 && qa > 1e-5) {
      float tg = (-qb + sqrt(disc)) / (2.0 * qa);
      float yh = lp.y + Rl.y * tg;
      // the polished (not mirror) stone blurs the image more the further the reflected ray travels
      float fe = 0.2 + 0.06 * tg;
      win = smoothstep(Y_TERRACE, Y_TERRACE + 0.3, yh) * (1.0 - smoothstep(Y_CANOPY - fe, Y_CANOPY + fe, yh));
      float blur = exp(-tg * 0.04);
      // faint bay-to-bay variation only (ref 1: a smooth warm sheen, no fluted streaks)
      vec2 hit = lp.xz + Rl.xz * tg;
      float bay = atan(hit.y, hit.x) * R_GLAZE_IN / 1.5;
      float streak = 0.93 + 0.07 * hash12(vec2(floor(bay), 5.0));
      col += uInteriorCol * 0.75 * win * (0.03 + 0.85 * fres) * blur * streak;
      col += uWarm * uLedI * 0.6 * exp(-abs(yh - Y_TERRACE - 0.03) / 0.04) * (0.04 + 0.6 * fres) * blur;   // glazing-base LED
    }
    // the balustrade base LED and the glow it lights in the glass edge, mirrored in the stone (ref 1: a bright warm
    // streak along the foot of the balustrade, spreading with the distance the reflected ray travels)
    {
      float qc2 = dot(lp.xz, lp.xz) - 43.0 * 43.0;
      float d2 = qb * qb - 4.0 * qa * qc2;
      if (d2 > 0.0 && qa > 1e-5 && qc2 > 0.0) {
        float tb = (-qb - sqrt(d2)) / (2.0 * qa);
        if (tb > 0.0) {
          float yb = lp.y + Rl.y * tb;
          // (pass 2: a crisper, stronger band: ref 1 p90 78 right beside the balustrade base)
          float wl = 0.018 + 0.012 * tb;
          float e = exp(-abs(yb + 7.12) / wl) + 0.22 * exp(-max(yb + 7.15, 0.0) / 0.3) * step(-7.2, yb);
          col += uWarm * uLedI * e * (0.06 + 0.9 * fres) * exp(-tb * 0.05);
        }
      }
    }
    // above the glazing head the mirrored ray meets the warm-lit canopy soffit, beyond the canopy edge the sky:
    // feathered over 2 m so neither edge draws a hard dark wedge across the floor
    vec3 envc = R.y > 0.0 ? skyClear(R) * 0.6 : fogColor(R) * 0.5;
    if (Rl.y > 1e-3) {
      float rc = length(lp.xz + Rl.xz * ((Y_CANOPY - lp.y) / Rl.y));
      float canW = smoothstep(R_CANOPY - 1.0, R_CANOPY + 1.0, rc) * (1.0 - win);
      envc = mix(envc, uWarm * 0.30 + uInteriorCol * 0.06, canW);
      // the canopy downlights mirrored in the polished stone: a row of soft warm glints, blurring with the
      // distance the reflected ray travels (ref 1)
      vec2 hc = lp.xz + Rl.xz * ((Y_CANOPY - lp.y) / Rl.y);
      float tcd = (Y_CANOPY - lp.y) / Rl.y;
      float ah = atan(hc.y, hc.x);
      float ac = (ah < 0.0 ? ah + 6.2831853 : ah) * R_DOWN;   // (same 0..360 deg cells as the soffit)
      vec2 dg = vec2((fract(ac / 2.5) - 0.5) * 2.5, length(hc) - R_DOWN);
      float sgg = 0.05 + 0.035 * tcd;
      col += uWarm * 16.0 * 0.0064 / (2.0 * sgg * sgg + 0.0064) * exp(-dot(dg, dg) / (2.0 * sgg * sgg)) * (0.05 + 0.6 * fres) * canW;
    }
    col += envc * (0.03 + 0.5 * fres);
  #elif SURF == 8
    col += uWarm * sp * (0.4 + 3.0 * exp(-vUv.x * 4.0)) + skyClear(R) * sp * 0.6;
  #elif SURF == 9
    // damp sheen: sky + mirrored LED lines, stronger in the wet patches
    float wk = 0.25 + 0.75 * wet;
    col += skyClear(R) * (0.02 + 0.5 * fres) * wk;
    col += uWarm * uLedI * 0.5 * exp(-ex / 0.1) * (0.15 + 0.85 * fres) * wk;
    col += uWarm * uLedI * 0.08 * exp(-ex / 0.6) * fres * wk;
  #elif SURF == 1
    // rough paving: brightest seen from above, darker at grazing view (micro-shadowing of the coarse surface):
    // ref 8 top-down deck L51 vs ref 7 (12 deg) L43; weak grazing sheen
    col *= 0.6 + 0.4 * max(dot(V, wn), 0.0);
    col += skyClear(R) * vec3(0.8, 0.92, 1.15) * (0.03 + 0.12 * fres);
    col += uWarm * specMask * 0.4;
  #else
    col += (R.y > 0.0 ? skyClear(R) : fogColor(R)) * 0.035 * fres;
  #endif
  col = applyAtmos(col, cameraPosition, vWorld);
  gl_FragColor = vec4(safeOut(col), 1.0);
}
`;

// emissive (LED strips, lamp shades, light slots)
export const EMISSIVE_FRAG = /* glsl */ `
#include <common>
#include <logdepthbuf_pars_fragment>
${NOISE}
${ATMOS}
${VARYINGS}
${SAFE_OUT}
uniform vec3 uEmit;
void main(){
  #include <logdepthbuf_fragment>
  vec3 e = uEmit;
  #ifdef FAR_DIM
    // LED lines: crisp strips up close, a soft warm line (not a neon outline) from the drone views
    e *= mix(1.0, FAR_DIM, smoothstep(35.0, 90.0, length(vWorld - cameraPosition)));
  #endif
  vec3 col = applyAtmos(e, cameraPosition, vWorld);
  gl_FragColor = vec4(safeOut(col), 1.0);
}
`;

// Glass: Fresnel reflection of an analytic environment, transmission via premultiplied blending
export const GLASS_FRAG = /* glsl */ `
#include <common>
#include <logdepthbuf_pars_fragment>
${NOISE}
${ATMOS}
${RING_CONST}
${VARYINGS}
${SAFE_OUT}
uniform float uF0;
uniform float uTint;
uniform float uEdgeGlow;   // balustrade: warm glow in lower part
uniform float uRailH;
uniform float uFmax;       // cap on grazing reflectance (thin coated glass reads transparent longer)
void main(){
  #include <logdepthbuf_fragment>
  #ifdef SLOT_MASK
    if (openingSDF(vLocal * vec3(R_OUT / R_GLASS_OUT, 1.0, R_OUT / R_GLASS_OUT)) > 0.0) discard;
  #endif
  vec3 n = safeN(vNormalW) * (gl_FrontFacing ? 1.0 : -1.0);
  vec3 V = normalize(cameraPosition - vWorld);
  float c = max(dot(V, n), 0.0);
  float F = min(uF0 + (1.0 - uF0) * pow(1.0 - c, 5.0), uFmax);
  vec3 R = reflect(-V, n);
  vec3 env;
  if (R.y > 0.0) env = skyFull(vWorld, R);
  else env = mix(fogColor(R), srgb2lin(vec3(0.40, 0.41, 0.54)) * uSkyExposure, smoothstep(0.0, -0.1, R.y));
  #ifdef MULLIONS
    // the inner glazing looks down onto the warm-lit terrazzo, not the blue cloud sea
    if (R.y < 0.0) env = mix(env, srgb2lin(vec3(0.46, 0.38, 0.30)) * uSkyExposure, smoothstep(0.0, -0.08, R.y));
  #endif
  vec3 col = env * F;
  float a = clamp(F + uTint, 0.0, 1.0);
  #ifdef MULLIONS
    // bronze mullions every 3.0 m, drawn at least ~0.7 px wide (coverage-weighted) so the far arc keeps its rhythm.
    // On the real mullion boxes (98 around), and only far away: near the camera the boxes themselves read, and the
    // drawn lines (wide at grazing angles) turned the terrace glazing into a dark slatted wall (ref 1: clear glass)
    float sm = thetaDeg(vLocal) / 360.0 * 98.0;
    float dm = (0.5 - abs(fract(sm) - 0.5)) * 3.0134;             // metres to the nearest mullion
    float pw = max(length(fwidth(vLocal.xz)), 1e-4);              // metres per pixel
    float wv = max(0.035, pw * 0.7);
    float far = smoothstep(35.0, 70.0, length(vWorld - cameraPosition));
    float ml = (1.0 - smoothstep(wv * 0.6, wv, dm)) * clamp(0.05 / wv, 0.45, 1.0) * smoothstep(0.004, 0.02, pw) * far;
    col = mix(col, srgb2lin(vec3(0.10, 0.08, 0.07)) * uSkyExposure * 0.3, ml);
    a = mix(a, 1.0, ml);
  #endif
  #ifdef SLOT_MASK
    // near-black mullions every 1.6 m (refs 4 / 7 / 11: a crisp dark rhythm across the lit band), drawn at least ~1 px
    // wide (coverage-weighted) on the real mullion fins, so they hold from the drone views without aliasing
    {
      float sm = (thetaDeg(vLocal) - SLOT_A0) / (SLOT_A1 - SLOT_A0) * SLOT_NM;
      float pitch = (SLOT_A1 - SLOT_A0) * DEG * R_GLASS_OUT / SLOT_NM;
      float dm = (0.5 - abs(fract(sm) - 0.5)) * pitch;
      float pw = max(length(fwidth(vLocal.xz)), 1e-4);
      float wv = max(0.08, pw * 0.85);
      float ml = (1.0 - smoothstep(wv * 0.55, wv, dm)) * clamp(0.12 / wv, 0.6, 1.0) * smoothstep(0.003, 0.015, pw);
      col = mix(col, srgb2lin(vec3(0.07, 0.08, 0.11)) * uSkyExposure * 0.25, ml);
      a = mix(a, 1.0, ml);
    }
  #endif
  #ifdef RAIL
    // LED light trapped in the glass edge: warm glow in the lower part of the panel
    float hh = clamp(vUv.y, 0.0, 1.0);
    vec3 glow = uWarm * uEdgeGlow * (exp(-hh * 6.0) * 0.9 + 0.08) * mix(1.0, 0.35, smoothstep(35.0, 90.0, length(vWorld - cameraPosition)));
    col += glow;
  #endif
  col = applyAtmos(col, cameraPosition, vWorld);
  gl_FragColor = vec4(safeOut(col), clamp(a, 0.0, 1.0));
}
`;

// Polished / brushed stainless steel with analytic environment + warm lamp highlights.
// STRUT: the big polished struts read as a dark mirror (ref 3): sky on the upper faces, dark ranges / rock /
// cloud sea on the body, warm uplight on the undersides, a bright collar where they meet the soffit.
export const STEEL_FRAG = /* glsl */ `
#include <common>
#include <logdepthbuf_pars_fragment>
${NOISE}
${ATMOS}
${RING_CONST}
${RING_LIGHT}
${VARYINGS}
${SAFE_OUT}
uniform vec3 uTint;
uniform float uRough;
vec3 envSteel(vec3 p, vec3 lp, vec3 R){
  vec3 e;
  if (R.y > 0.0) e = skyClear(R);
  else e = mix(fogColor(R), srgb2lin(vec3(0.40, 0.41, 0.54)) * uSkyExposure, smoothstep(0.0, -0.12, R.y));
  #ifdef STRUT
    vec3 Rl = mat3(uRingInv) * R;
    // distant ranges along the horizon (dark blue-grey), cloud sea below a little darker than the fog
    float hz = exp(-abs(R.y - 0.025) / 0.035);
    e = mix(e, srgb2lin(vec3(0.25, 0.26, 0.36)) * uSkyExposure, hz * 0.65);
    e *= R.y < 0.0 ? 0.78 : 1.0;
    // the pinnacle behind the strut fills the outward (cliff-side) half of the reflection
    float outw = Rl.x * sign(lp.x) / max(length(Rl.xz), 1e-3);
    float rock = smoothstep(-0.1, 0.6, outw) * smoothstep(0.35, -0.05, R.y);
    e = mix(e, srgb2lin(vec3(0.20, 0.17, 0.18)) * uSkyExposure, rock * 0.85);
    // ref 3: the mirror reads dark (#494350 body, #3f455f..#4a5177 sky faces): darker, cooler env overall
    e *= vec3(0.50, 0.52, 0.60);
  #endif
  // the warm-lit soffit overhead when we are under the ring
  float r = length(lp.xz);
  if (R.y > 0.05 && lp.y < Y_SOFFIT && r < 62.0) {
    float t = (Y_SOFFIT - lp.y) / R.y;
    vec2 hit = lp.xz + (mat3(uRingInv) * R).xz * t;
    float hr = length(hit);
    float onSoffit = smoothstep(42.0, 43.0, hr) * (1.0 - smoothstep(53.0, 55.0, hr));
    vec3 sof = uWarm * uLedI * 0.04 * (1.0 + 3.0 * exp(-(hr - 42.7) * 0.8)) + srgb2lin(vec3(0.35, 0.33, 0.40)) * 0.25;
    // warm glow of the soffit around the strut heads (struts meet the soffit at r 48, theta +-22 deg off each bridge)
    vec2 cd = abs(hit) - vec2(44.5, 17.98);
    sof += uWarm * uLedI * 0.3 * exp(-dot(cd, cd) / 12.0);
    e = mix(e, sof, onSoffit);
  }
  return e;
}
void main(){
  #include <logdepthbuf_fragment>
  vec3 n = safeN(vNormalW) * (gl_FrontFacing ? 1.0 : -1.0);
  vec3 ln = safeN(vNormalL) * (gl_FrontFacing ? 1.0 : -1.0);
  vec3 V = normalize(cameraPosition - vWorld);
  // brushed: perturb normal along the tube axis with fine streak noise
  float br = vnoise2(vec2(vUv.x * 900.0, vUv.y * 6.0)) - 0.5;
  n = safeN(n + 0.03 * br * vec3(1.0, 0.3, 1.0));
  vec3 R = reflect(-V, n);
  // cheap roughness: average 3 jittered env samples (around the tube for the struts: axial polish lines)
  vec3 t1 = safeN(cross(n, vec3(0.0001, 1.0, 0.0001)));
  vec3 t2 = cross(n, t1);
  #ifdef STRUT
    t1 = safeN(cross(vAxis, n) + 1e-4); t2 = vAxis;
  #endif
  vec3 env = envSteel(vWorld, vLocal, R) * 0.4
           + envSteel(vWorld, vLocal, safeN(R + (t1 * 0.6 + t2 * 0.2) * uRough)) * 0.3
           + envSteel(vWorld, vLocal, safeN(R - (t1 * 0.6 - t2 * 0.2) * uRough)) * 0.3;
  float c = max(dot(V, n), 0.0);
  vec3 F0 = uTint;
  vec3 F = F0 + (1.0 - F0) * pow(1.0 - c, 5.0);
  vec3 col = env * F;
  #ifdef STRUT
    // (pass 2) matte cast concrete legs, not a satin mirror (ref 6 at 100%: shade faces near black L* 13-15 #202128,
    // the sky-lit face a cool mid grey ~40 #555e7f b* -20, warmth only as a hot pool at the foot): the dome and the
    // cool key on a pale concrete albedo, the side away from the bright sky in deep shade; a faint sheen at grazing only
    vec3 sAlb = srgb2lin(vec3(0.52, 0.52, 0.55)) * (0.92 + 0.12 * vnoise2(vec2(vUv.x * 9.0, vUv.y * 4.0)));
    float skd = smoothstep(-0.35, 0.75, dot(n, RKEY));
    // seen from below (refs 3 / 9: the camera under the ring) the legs read pale cast concrete lit by the bright cloud
    // sea and the lamps, like the soffit (view-dependent, as SURF 3): from the drones the deep shade side stays
    float below = smoothstep(-0.05, -0.45, V.y);
    vec3 sE = (skyIrradiance(n, 1.0, 0.15) * mix(mix(0.16, 0.7, below), 1.0, skd * skd) * vec3(1.0, 1.0, 0.94) + ringKey(n) * 1.4 * uSkyExposure) * 0.85;
    sE *= 1.0 + 2.2 * below * (0.4 + 0.6 * max(-n.y, 0.0));
    sE += uWarm * 0.05 * below * max(n.y, 0.0);   // the warm soffit overhead
    col = sAlb * sE + env * F * 0.05;
  #endif
  // lamp specular (uplights at footings, collar LEDs)
  for (int i = 0; i < ${LAMPS_MAX}; i++) {
    if (i >= uLampCount) break;
    vec3 L = uLampPos[i].xyz - vWorld; float d2 = dot(L, L); L *= inversesqrt(max(d2, 1e-6));
    vec3 H = safeN(L + V);
    float sp = pow(max(dot(n, H), 0.0), 40.0) * 6.0 + pow(max(dot(n, H), 0.0), 6.0) * 0.6;
    #ifdef STRUT
      // (pass 2) matte: no lamp highlights along the tube (they read as a brass sheen); a crisp warm rim only where
      // the uplight grazes the silhouette near the foot
      float rim = pow(1.0 - c, 4.0) * max(dot(n, L), 0.0) * exp(-max(vLocal.y + 24.0, 0.0) / 3.0);
      col += uLampCol[i].rgb * 0.05 * rim / (1.0 + d2 * 0.3);
      col += uLampCol[i].rgb * sAlb * 0.04 * max(dot(n, L), 0.0) / (d2 + 4.0);
      // (round 7) the uplight's wash up the tube, (pass 2) confined to the foot: ref 6 / 4 show a hot amber pool over
      // the bottom ~15% of the leg (L* 50-75), the rest of the leg cool grey / dark (uplights only: lamps below)
      float wl = max(dot(n, L), 0.0) * smoothstep(0.05, 0.45, -L.y);
      col += uLampCol[i].rgb * sAlb * 0.5 * wl / (1.0 + d2 * 0.5) * exp(-max(vLocal.y + 24.0, 0.0) / 1.8);
    #else
      col += uLampCol[i].rgb * F0 * sp / (d2 + uLampPos[i].w * uLampPos[i].w);
      col += uLampCol[i].rgb * 0.06 * max(dot(n, L), 0.0) / (d2 + 4.0);
    #endif
  }
  // warm bounce from the soffit LEDs near the top
  #ifdef STRUT
    col += ringLocalLight(vLocal, ln, vWorld, n) * 0.04 * F0;
  #else
    col += ringLocalLight(vLocal, ln, vWorld, n) * 0.25 * F0;
  #endif
  #ifdef STRUT
    // uplight grazing the underside along the whole tube, strongest near the footing
    float dn = max(-n.y, 0.0), side = 1.0 - abs(dot(n, V));
    // (pass 2: near the foot only; along the whole tube it lifted the shade side to L* 24 against the refs' <= 16)
    col += uWarm * sAlb * 0.5 * dn * dn * (0.03 + exp(-max(vLocal.y + 25.0, 0.0) / 2.2));   // warm undersides (#754e31)
    // the flare under the soffit / haunch catches the warm glow of its lamp: a soft gradient, no bright line
    float ytop = length(vLocal.xz) < 54.0 ? Y_SOFFIT : -7.9;
    float k = exp(-max(ytop - vLocal.y, 0.0) / 1.3);
    col += uWarm * uLedI * F0 * k * (0.12 + 0.3 * max(n.y, 0.0) + 0.12 * side);
  #endif
  col = applyAtmos(col, cameraPosition, vWorld);
  gl_FragColor = vec4(safeOut(col), 1.0);
}
`;

// Restaurant interior: warm ambient, downlight pools, pendant and table-lamp glow
export const INTERIOR_FRAG = /* glsl */ `
#include <common>
#include <logdepthbuf_pars_fragment>
${NOISE}
${ATMOS}
${RING_CONST}
${VARYINGS}
${SAFE_OUT}
uniform vec3 uAlbedo;
uniform float uEmissive;
// 1 ceiling (downlights, linear slots, window-head coves), 2 floor (oak), 3 artwork, 4 olive foliage,
// 5 plaster wall with downlight scallops, 6 gallery wall (plaster + walnut wainscot), 7 lamp shade (emissive),
// 9 guests (clothing / hair from instance colour)
uniform float uPattern;
// arc offset (m) of point p to the nearest fixture on a circle of radius rr, spacing sp
float cellArc(float th, float rr, float sp, float ph){ return (fract(th * DEG * rr / sp + ph) - 0.5) * sp; }
// ceiling downlight rows (r) at 1.6 m spacing
float downRow(int k){ return k == 0 ? 47.75 : (k == 1 ? 49.0 : (k == 2 ? 50.4 : (k == 3 ? 52.3 : 53.7))); }
void main(){
  #include <logdepthbuf_fragment>
  vec3 lp = vLocal;
  #ifdef OPENING_DISCARD
    if (openingSDF(lp) < 0.0) discard;
  #endif
  vec3 ln = safeN(vNormalL) * (gl_FrontFacing ? 1.0 : -1.0);
  float r = length(lp.xz);
  float th = thetaDeg(lp);
  vec3 alb = uAlbedo * vInstCol;
  if (uPattern == 7.0) {
    // linen shade: glowing diffuser, brighter toward the open bottom rim
    float b = 0.55 + 0.45 * smoothstep(0.2, 1.0, 1.0 - vUv.y);
    vec3 e = uWarm * uEmissive * b + vec3(0.35, 0.25, 0.12) * uEmissive * 0.25;
    gl_FragColor = vec4(safeOut(applyAtmos(e, cameraPosition, vWorld)), 1.0); return;
  }
  if (uEmissive > 0.0) { gl_FragColor = vec4(safeOut(applyAtmos(uWarm * uEmissive, cameraPosition, vWorld)), 1.0); return; }
  float sw = slotWeight(th);
  float h = Y_CEIL - lp.y;                       // depth below the ceiling
  float z = lp.y - Y_TERRACE;                    // height above the floor
  float up = ln.y;
  vec2 radv = lp.xz / max(r, 1e-3);
  vec3 lnT = vec3(dot(ln.xz, vec2(-radv.y, radv.x)), ln.y, dot(ln.xz, radv));   // (tangential, up, radial)
  // warm multi-bounce ambient, kept low so furniture and guests read dark against the lit planes;
  // low surfaces sit in the shadow of tables and chairs
  float occ = mix(0.5, 1.0, smoothstep(0.1, 1.4, z));
  vec3 E = uInteriorCol * (0.70 + 0.35 * max(up, 0.0) + 0.08 * max(-up, 0.0)) * mix(0.50, 0.46, sw) * occ;
  // window-head coves wash the upper room near both glazings
  float nearIn = exp(-max(r - R_GLAZE_IN, 0.0) * 0.9), nearOut = exp(-max(R_GLASS_OUT - r, 0.0) * 0.9);
  E += uWarm * 0.22 * (nearIn + nearOut * sw) * smoothstep(5.5, 0.5, h);
  // downlight grid: tight pools on up-facing surfaces
  for (int k = 0; k < 5; k++) {
    float rr = downRow(k);
    vec2 dd = vec2(cellArc(th, rr, 1.6, 0.5), r - rr);
    float sig = max(0.18 + 0.16 * h, 0.06);
    E += uWarm * uDownI * 0.42 * exp(-dot(dd, dd) / (2.0 * sig * sig)) * max(up, 0.0) / (1.0 + h * h * 0.05)
       * (1.0 + 2.4 * sw * step(R_SPINE, r));   // (gallery: brightly lit seats, cloths and treads, refs 4 / 7)
  }
  // drum pendants over the window tables (r 48.0 / 3 m)
  {
    vec2 dd = vec2(cellArc(th, 48.0, 3.0, 0.5), r - 48.0);
    float hp = max(-3.45 - lp.y, 0.05);
    float sg = 0.30 + 0.32 * hp;
    float pool = exp(-dot(dd, dd) / (2.0 * sg * sg));
    E += uWarm * 1.2 * pool * (max(up, 0.0) * 0.8 + 0.2) / (1.0 + hp * hp * 0.6);
  }
  // table lamps on every dining table (window row y -6.16; gallery tiers: r 52.36 y -4.76 and r 53.1 y -5.46): bright
  // pool on the cloth, glow on faces and the banquette nearby
  for (int k = 0; k < 3; k++) {
    float rr = k == 0 ? 48.0 : (k == 1 ? 52.36 : 53.1), sp = k == 0 ? 3.0 : 2.6;
    vec3 d = vec3(cellArc(th, k == 0 ? rr : 52.75, sp, 0.5) * (k == 0 ? 1.0 : rr / 52.75), lp.y - (k == 0 ? -6.16 : (k == 1 ? -4.76 : -5.46)), r - rr);
    float d2 = dot(d, d);
    vec3 L = -d / sqrt(d2 + 1e-4);
    float ndl = max(dot(lnT, L) * 0.7 + 0.3, 0.0);
    E += uWarm * 0.32 * ndl / (0.03 + d2 * 1.6) * (k == 0 ? 1.0 : sw);
  }
  if (uPattern == 1.0) {
    // ivory ceiling: dense round downlights, linear slots along the spine, cove slots at both window heads
    for (int k = 0; k < 5; k++) {
      float rr = downRow(k);
      vec2 dd = vec2(cellArc(th, rr, 1.6, 0.5), r - rr);
      float d = length(dd);
      if (d < 0.055) { gl_FragColor = vec4(safeOut(applyAtmos(uWarm * 30.0, cameraPosition, vWorld)), 1.0); return; }
      E += uWarm * 0.45 * exp(-d * d / 0.05);                       // trim halo
    }
    float sl = abs(cellArc(th, 51.95, 3.6, 0.0));
    if (abs(r - 51.95) < 0.025 && sl < 1.3) { gl_FragColor = vec4(safeOut(applyAtmos(uWarm * 8.0, cameraPosition, vWorld)), 1.0); return; }
    // linear LED lines along the lounge ceiling, parallel to the terrace glazing (ref 1: bright strips running away
    // with the walk), 3 cm wide, drawn coverage-weighted so they hold as a soft line from far away
    {
      float pr = max(fwidth(r), 1e-4), wl = max(0.045, pr);
      float dl2 = min(abs(r - 48.55), abs(r - 50.15));
      float seg = step(abs(cellArc(th, r, 4.8, 0.0)), 2.25);   // 4.5 m runs with gaps at the coffer joints
      float ll = (1.0 - smoothstep(wl * 0.5, wl * 0.5 + pr, dl2)) * seg * 0.045 / wl;
      E += uWarm * 1.2 * exp(-dl2 * dl2 / 0.08) * seg;          // soft spill on the ceiling around the strip
      if (ll > 0.0) { vec3 cl = mix(alb * E, uWarm * 18.0, ll); gl_FragColor = vec4(safeOut(applyAtmos(cl, cameraPosition, vWorld)), 1.0); return; }
    }
    if ((r > R_GLAZE_IN + 0.12 && r < R_GLAZE_IN + 0.30) || (r > R_GLASS_OUT - 0.30 && r < R_GLASS_OUT - 0.12)) {
      gl_FragColor = vec4(safeOut(applyAtmos(uWarm * 7.0, cameraPosition, vWorld)), 1.0); return;
    }
    E += uWarm * 0.9 * (exp(-(r - R_GLAZE_IN - 0.3) * 1.8) + exp(-(R_GLASS_OUT - 0.3 - r) * 1.8));
    // recessed ceiling coffers: a darker reveal ring every 3 bays gives the plane some depth
    float cof = abs(cellArc(th, r, 4.8, 0.0));
    E *= 1.0 - 0.25 * (1.0 - smoothstep(0.03, 0.08, cof));
    E += uInteriorCol * 0.10;   // uplight from the lit floor and tables
  } else if (uPattern == 2.0) {
    // wide-plank smoked oak, planks run along the arc
    float s = th * DEG * r;
    float pr = r * 5.0;                       // 0.2 m boards
    float id = floor(pr);
    alb *= 0.85 + 0.2 * hash12(vec2(id, floor(s / 2.4 + hash12(vec2(id, 3.0)))));
    alb *= 0.94 + 0.08 * vnoise2(vec2(s * 6.0, pr * 0.5));
    alb *= 1.0 - 0.3 * (1.0 - smoothstep(0.0, 0.04, min(fract(pr), 1.0 - fract(pr))));
    // rugs under the gallery's front-row armchairs
    float rug = step(abs(cellArc(th, 52.75, 2.6, 0.0)), 0.95) * step(abs(r - 53.95), 0.4) * sw;
    alb = mix(alb, srgb2lin(vec3(0.42, 0.33, 0.27)) * (0.9 + 0.1 * vnoise2(lp.xz * 30.0)), rug);
  } else if (uPattern == 3.0) {
    // abstract ochre / gold / rust canvases
    vec2 q = vUv * vec2(3.0, 2.0);
    float sd = 13.0 * hash12(floor(vWorld.xz * 0.5));
    float a = fbm2(q * 1.6 + sd, 5);
    float b = fbm2(q * 3.5 - 4.0 + sd, 4);
    float pal = hash12(floor(vWorld.xz * 0.5) + 3.0);
    vec3 c0 = mix(srgb2lin(vec3(0.62, 0.52, 0.38)), srgb2lin(vec3(0.45, 0.47, 0.50)), step(0.5, pal));   // ochre-taupe or slate
    alb = mix(c0, srgb2lin(vec3(0.24, 0.20, 0.17)), smoothstep(0.35, 0.65, a));
    alb = mix(alb, srgb2lin(vec3(0.88, 0.82, 0.70)), smoothstep(0.58, 0.78, b));
    alb = mix(alb, srgb2lin(vec3(0.12, 0.10, 0.09)), smoothstep(0.7, 0.8, fbm2(q * 6.0 + sd, 3)) * 0.8);
    float frame = step(0.95, max(abs(vUv.x - 0.5), abs(vUv.y - 0.5)) * 2.0);
    alb = mix(alb, srgb2lin(vec3(0.16, 0.12, 0.09)), frame);
    E += uWarm * 0.7;   // picture lights
  } else if (uPattern == 4.0) {
    // olive crown: silver-green leaf clusters, darker inside
    float l = vnoise3(vWorld * 9.0), l2 = vnoise3(vWorld * 23.0);
    alb = mix(srgb2lin(vec3(0.24, 0.27, 0.15)), srgb2lin(vec3(0.52, 0.56, 0.40)), smoothstep(0.3, 0.8, l * 0.6 + l2 * 0.5));
    E *= 0.6 + 0.4 * max(up, 0.0);
  } else if (uPattern == 5.0 || uPattern == 6.0) {
    // wall: scallops from the downlights 0.6 m off the wall, every 1.6 m
    float ca = cellArc(th, r, 1.6, 0.5);
    float sig = max(0.12 + 0.2 * h, 0.06);
    float sc = exp(-ca * ca / (2.0 * sig * sig)) * smoothstep(0.15, 0.7, h) * exp(-h * 0.32);
    E += uWarm * 1.25 * sc;
    alb *= 0.95 + 0.07 * vnoise2(vec2(th * DEG * r * 3.0, lp.y * 3.0));   // trowelled plaster
    if (uPattern == 5.0) {
      // walls fall off toward the floor: the band reads bright above, darker and denser at table height (refs 4 / 7)
      E *= mix(0.45, 1.05, smoothstep(0.5, 4.2, z));
      // (pass 2) seen from the terrace the lounge's back wall stands darker, so the room reads deep (ref 1 p10 ~14)
      E *= 1.0 - 0.35 * (1.0 - smoothstep(18.0, 45.0, length(vWorld - cameraPosition)));
      // far LOD of the lounge seen across the void (refs 4 / 7 / 11: bright head over a dark, dense middle of
      // guests, plants and furniture): crowd silhouettes painted on the inward face of the spine wall, only from
      // > 50 m where the real figures are a few pixels and mostly culled near the cameras
      float fd = smoothstep(50.0, 80.0, length(vWorld - cameraPosition)) * smoothstep(0.3, 0.7, -lnT.z);
      float sA = th * DEG * r;
      float aa = max(fwidth(sA) + fwidth(z), 1e-3);   // (derivatives outside the non-uniform branch)
      if (fd > 0.0) {
        float cw = 0.62, cid = floor(sA / cw), fx = (fract(sA / cw) - 0.5) * cw;
        float hc = hash12(vec2(cid, 11.0)), tall = mix(1.25, 1.85, hash12(vec2(cid, 12.0)));
        float body = (1.0 - smoothstep(0.17 - aa, 0.17 + aa, abs(fx))) * (1.0 - smoothstep(tall - 0.25 - aa, tall - 0.25 + aa, z));
        float headm = 1.0 - smoothstep(0.11 - aa, 0.11 + aa, length(vec2(fx, z - tall + 0.12)));
        float fig = max(body, headm) * step(0.3, hc);
        // plants / tall lamps now and then, low furniture masses all along
        float tallM = (1.0 - smoothstep(2.3 - aa, 2.3 + aa, z)) * smoothstep(0.62, 0.66, vnoise2(vec2(sA * 0.9, 4.0)));
        float furn = (1.0 - smoothstep(0.85 - aa, 0.85 + aa, z)) * smoothstep(0.3, 0.4, vnoise2(vec2(sA * 1.7, 9.0)));
        float m = max(max(fig, tallM), furn) * fd;
        alb = mix(alb, srgb2lin(vec3(0.16, 0.11, 0.08)), m * 0.92);
      }
    }
    if (uPattern == 6.0) {
      // Gallery wall behind the slot as the drones see it (refs 3 / 4 / 7 / 11 at 100%): a soft warm room with pale
      // drapes, columns of light, lit pictures and dark furniture, every glazing bay different (never a stamped
      // repeat): pleated sand-linen drapes; limewash raked by one or two ceiling wall-washers; a canvas under its
      // picture light. (A backlit display case averaged into a lit blank panel from the drones.) A dark walnut
      // wainscot runs behind the banquettes of the raised tier, a bright warm cove washes the head and the wall dims
      // toward the furniture.
      float sArc = th * DEG * r;
      float pw = max(length(fwidth(lp.xz)), 1e-4);
      float aw = pw + fwidth(z) + 1e-4;                    // metres per pixel (derivatives in uniform control flow)
      float sm6 = (th - SLOT_A0) / (SLOT_A1 - SLOT_A0) * SLOT_NM;
      float bay6 = (SLOT_A1 - SLOT_A0) * DEG * r / SLOT_NM;
      float bid = floor(sm6);
      float bx = (fract(sm6) - 0.5) * bay6;                // m from the bay centre
      vec3 kb = vec3(hash12(vec2(bid, 4.0)), hash12(vec2(bid, 5.0)), hash12(vec2(bid, 6.0)));
      // (pass 2: dark smoked plaster above the tiers, so the band reads as a deep room with lit furniture and point
      // lights rather than a lit backdrop: ref 7 band top sixth L*31, wall above the furniture <= 25)
      // (round 7: paler again: ref 4 at 100% shows a bright cream room, L* 53-76 at table height, dark seats against it)
      vec3 lime = srgb2lin(vec3(0.60, 0.52, 0.43)) * (0.9 + 0.14 * vnoise2(vec2(sArc * 0.8, z * 0.5)));
      // slim bronze reveal on every bay line (radially behind the mullions: the two rhythms never beat)
      float rv = (0.5 - abs(fract(sm6) - 0.5)) * bay6;
      lime *= 1.0 - 0.5 * (1.0 - smoothstep(0.02, 0.04 + pw, rv)) * (1.0 - smoothstep(0.03, 0.12, pw));
      vec3 wcol = lime;
      float lift = 0.0;
      float zw = 2.95;                                      // wainscot top (tier-2 banquette backs reach z 2.5)
      if (kb.x < 0.3) {
        // drapes drawn across the bay, softly grazed by the cove above
        float pl = sin(sArc * 6.2832 / 0.17 + 0.6 * sin(sArc * 1.3 + bid));
        float plA = 1.0 - smoothstep(0.03, 0.09, pw);      // pleats fade before they alias
        vec3 cur = srgb2lin(vec3(0.66, 0.58, 0.48)) * (0.86 + 0.16 * vnoise2(vec2(sArc * 0.7, z * 0.3 + bid)));
        cur *= 1.0 - plA * 0.16 * (0.5 + 0.5 * pl * abs(pl));
        // broad soft folds, still a few pixels wide from the drones
        float pl2 = sin(sArc * 6.2832 / 0.45 + 2.5 * vnoise2(vec2(sArc * 0.8, bid)));
        cur *= 1.0 - (1.0 - smoothstep(0.1, 0.18, aw)) * 0.3 * (0.5 + 0.5 * pl2);   // (gone before 2.5 px per fold)
        float inB = 1.0 - smoothstep(bay6 * 0.5 - 0.14 - aw, bay6 * 0.5 - 0.12 + aw, abs(bx));
        wcol = mix(lime, cur, inB);
        lift = 0.15 * inB * exp(-h / 2.0);
      } else if (kb.x < 0.64) {
        // one or two wall-washers in the ceiling rake columns of light down the limewash
        // (narrow scallops fading down the wall: from the drones a pair of light columns, not a lit blank panel)
        float ca6 = kb.z < 0.7 ? abs(bx - (kb.y - 0.5) * 0.3) - 0.7 : bx - (kb.y - 0.5) * 0.7;
        float sg6 = 0.08 + 0.12 * h;
        lift = (1.0 + 0.9 * kb.y) * exp(-ca6 * ca6 / (2.0 * sg6 * sg6)) * smoothstep(0.1, 0.6, h) * exp(-h * 0.42);
      } else {
        // a canvas under a picture light
        vec2 csz = vec2(0.5 + 0.35 * kb.z, 0.4 + 0.3 * kb.y);
        vec2 cq = vec2(bx - (kb.y - 0.5) * 0.5, z - 3.1 - 0.5 * kb.z);
        float inC = (1.0 - smoothstep(csz.x - aw, csz.x + aw, abs(cq.x))) * (1.0 - smoothstep(csz.y - aw, csz.y + aw, abs(cq.y)));
        vec2 q = cq / csz;
        float a = fbm2(q * 2.0 + bid * 3.1, 4), b = fbm2(q * 3.0 - 4.0 + bid, 3);
        vec3 c0 = mix(srgb2lin(vec3(0.66, 0.52, 0.34)), srgb2lin(vec3(0.42, 0.46, 0.52)), step(0.55, kb.z));
        vec3 cd = srgb2lin(vec3(0.13, 0.11, 0.10));
        // bold abstract fields (light shapes on a dark ground or the reverse): a picture, not a lit blank panel
        vec3 art = kb.y > 0.5 ? mix(cd, c0, smoothstep(0.44, 0.56, a)) : mix(c0, cd, smoothstep(0.44, 0.56, a));
        art = mix(art, srgb2lin(vec3(0.86, 0.80, 0.68)), smoothstep(0.62, 0.74, b));
        art = mix(art, mix(c0, cd, 0.45), smoothstep(0.08, 0.2, aw));   // (shapes average out before they shimmer)
        float fw6 = 0.035;
        float inner = (1.0 - smoothstep(csz.x - fw6 - aw, csz.x - fw6 + aw, abs(cq.x))) * (1.0 - smoothstep(csz.y - fw6 - aw, csz.y - fw6 + aw, abs(cq.y)));
        art = mix(srgb2lin(vec3(0.12, 0.09, 0.07)), art, mix(inner, 0.85, smoothstep(0.02, 0.07, aw)));
        wcol = mix(lime, art, inC);
        // picture-light pool spilling down from above the frame
        float py = cq.y - csz.y;
        lift = 1.0 * exp(-cq.x * cq.x / (2.0 * pow(csz.x * 0.85 + 0.15, 2.0))) * smoothstep(0.7, -0.1, py) * smoothstep(-2.0 * csz.y - 0.6, -csz.y, cq.y);
      }
      vec3 walnut = srgb2lin(vec3(0.20, 0.13, 0.09)) * (0.8 + 0.35 * hash12(vec2(floor(sArc / 0.45), 2.0)));
      float wain = 1.0 - smoothstep(zw - aw, zw + aw, z);
      alb = mix(wcol, walnut, wain);
      alb = mix(alb, srgb2lin(vec3(0.75, 0.58, 0.32)), (1.0 - smoothstep(0.02, 0.02 + aw, abs(z - zw - 0.03))) * (1.0 - smoothstep(0.03, 0.1, aw)));   // brass rail
      // dim room light on the wall above the tiers; only the picture lights / washers and a faint cove at the head
      // (ref 7: the band's top sixth is the darkest, with point spots)
      // (round 7: brighter overall: the user found the light not bright enough; refs 4 / 7 / 11 at 100%: the band's
      // head glows warm white under the ceiling, the walls are lit warm, the furniture reads dark against them)
      // (pass 2: the room light back to ~half: at 0.86-0.9 the walls and drapes washed the band flat, p50 46-51 against
      // the refs' 30-40; the light lives in the washer / picture pools and the head cove)
      E *= mix(0.48, 0.55, smoothstep(3.0, 5.5, z));
      E += uWarm * lift * 2.6;
      E += mix(uWarm, vec3(1.0, 0.80, 0.55), 0.5) * 1.7 * exp(-h / 0.7) * smoothstep(0.0, 0.1, h);
    }
  } else if (uPattern == 8.0) {
    // gallery column: warm pool of its own sconce (y -4.05) up and down the shaft, darker below the tables
    float dy = lp.y + 4.05;
    E += uWarm * 1.6 * exp(-dy * dy / 0.35) * (0.4 + 0.6 * max(lnT.z, 0.0));
    E *= mix(0.6, 1.0, smoothstep(0.3, 2.5, z));
    alb *= 0.96 + 0.06 * vnoise2(vec2(th * 40.0, lp.y * 4.0));
  } else if (uPattern == 9.0) {
    // guests: matte fabric; faces / hands pick up the table lamp from below
    E *= 0.8;
  } else if (uPattern == 10.0) {
    // (pass 2) bridge corridor back wall (bridge-local: |x| 54.6..73 along the bridge, y -5.4..-1.0): a dark walnut room
    // lit in discrete pools - a sconce between every other pair of mullions, a soft wash under the ceiling strip.
    // Refs 4 / 7 / 11 seen through the glass: p10 15-17, p50 27-34, p90 62-78, #483f3e..#66493c; an evenly lit tan
    // wall (round 7) read as an orange box.
    float s = abs(lp.x), zw = lp.y + 5.4;
    float bay = floor((s - 55.35) / 3.0);
    float dx = (fract((s - 55.35) / 3.0) - 0.5) * 3.0, dy = zw - 2.35;
    float kI = 0.45 + 0.9 * hash12(vec2(bay, sign(lp.x) + 7.0));   // every sconce a little different
    float sg = 0.22 + 0.3 * abs(dy);
    E = mix(uInteriorCol, uWarm, 0.5) * 0.07 * (0.6 + 0.4 * smoothstep(0.0, 1.5, zw));
    E += uWarm * kI * 8.0 * exp(-dx * dx / (2.0 * sg * sg)) * exp(-abs(dy) / 0.9);
    E += uWarm * kI * 16.0 * exp(-(dx * dx + dy * dy) / 0.06);                   // the sconce itself
    E += uWarm * 3.4 * exp(-(4.4 - zw) / 0.6);                                     // ceiling strip wash at the head (ref 4: the panes glow brightest up top)
    alb *= 0.92 + 0.12 * hash12(vec2(floor(s / 0.9), 3.0));                        // panel boards
  }
  vec3 col = alb * E;
  // up close (the terrace walk, ref 1) the restaurant reads warm white, not amber: the deep amber of the band seen
  // from the drones (refs 4 / 7) is the glass and the distance. Ease the saturation within ~40 m.
  // (ref 1 at 100%: the near interior is still a warm #edb56e, only a touch paler than the band from the air)
  // The slot gallery reads a paler warm beige from the drones too (refs 7 / 11 band top #c49a73..#ca9464).
  float nearK = 1.0 - smoothstep(18.0, 45.0, length(vWorld - cameraPosition));
  float lc = dot(col, vec3(0.2126, 0.7152, 0.0722));
  col = mix(col, mix(vec3(lc), col, mix(0.85, 0.74, nearK)), max(nearK, 0.8 * step(R_SPINE, r) * sw));
  col *= 1.0 + 0.15 * nearK;   // (ref 1: the near lounge is bright, warm white)
  // (round 7) brighter rooms with warm-white cores (user: the light is not bright enough; refs 4 / 7 / 11 at 100%:
  // the lit planes go near white-yellow, amber only where the light falls off)
  // (pass 2) the lift only on the lit planes, the darks pressed down: x1.35 on everything lifted the floor, furniture
  // and drapes (band p10 21 / p02 16 against the refs' 13-15 / 7-8); monotonic, so the lamp peaks keep their order
  float lc1 = dot(col, vec3(0.2126, 0.7152, 0.0722));
  col *= mix(0.5, 1.45, smoothstep(0.03, 0.32, lc1));
  // warm-white cores, golden rather than peach (refs' brightest 2%: #f3d39a / #ffbf6b; ours read #f9cea8)
  float lc2 = dot(col, vec3(0.2126, 0.7152, 0.0722));
  col = mix(col, lc2 * vec3(1.22, 0.99, 0.56), 0.6 * smoothstep(0.22, 1.2, lc2));
  col = applyAtmos(col, cameraPosition, vWorld);
  gl_FragColor = vec4(safeOut(col), 1.0);
}
`;
