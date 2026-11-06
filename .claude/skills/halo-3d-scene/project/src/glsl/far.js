// Distant ranges (beyond ~3 km): snow pattern, albedo and light, included by the terrain fragment shader after
// NOISE/ATMOS. terrain.js blends these in with farF = smoothstep(3 km, 20 km); farLight re-weights its own result
// so the far look is effectively complete by ~8 km (see farW below).
// Refs: crisp ranges of bright lit snow faces (#b9bfd8..#dfe0ee after the haze) beside blue shadow faces, dark rock
// ribs streaking down the steep faces with snow in the couloirs between them, dark navy lower slopes. The DEM (31 m
// out to 25 km) carries the real ridges; on top of it a fall-line rib / couloir relief (~70 m apart) drives both
// the snow and the light so rock streaks and shading line up. (The round-3 isotropic 300 m relief drew cow-print
// blotches of rock on lavender snow.)
export const FAR = /* glsl */ `
// per-fragment cache: farSnow (called first by terrain.js) stores the relief normal, DEM normal and raw snow
vec3 gFarNb = vec3(0.0, 1.0, 0.0);
vec3 gFarN0 = vec3(0.0, 1.0, 0.0);
float gFarSnow = 0.0;
float gFarHave = 0.0;
// effective far weight: the far look takes over between 2.8 and 8 km (terrain.js's farF only reaches 1 at 20 km)
float farW(float dist){ return smoothstep(2800.0, 8000.0, dist); }
// value noise with its analytic derivative: (v, dv/dx, dv/dy)
vec3 farVN(vec2 p){
  vec2 i = floor(p), f = fract(p);
  vec2 u = f * f * (3.0 - 2.0 * f), du = 6.0 * f * (1.0 - f);
  float a = hash12(i), b = hash12(i + vec2(1.0, 0.0)), c = hash12(i + vec2(0.0, 1.0)), e = hash12(i + vec2(1.0, 1.0));
  float k = a - b - c + e;
  return vec3(a + (b - a) * u.x + (c - a) * u.y + k * u.x * u.y, du * (vec2(b - a, c - a) + k * u.yx));
}
// Fall-line ribs: value noise stretched along 4 fixed horizontal directions (~70 m across, ~450 m along), blended by
// how well each matches the local downhill direction (per-pixel frames drew contour-line moire).
// Returns (value 0..1: 1 = rib crest, 0 = couloir floor; world gradient per m).
vec4 farRibs(vec3 pos, vec3 n0){
  vec2 gd = n0.xz / max(length(n0.xz), 1e-3);
  vec4 s = vec4(0.0);
  float wsum = 0.0;
  for (int i = 0; i < 4; i++) {
    float a = float(i) * 0.7854;
    vec2 dir = vec2(cos(a), sin(a)), per = vec2(-dir.y, dir.x);
    float w = pow(abs(dot(gd, dir)), 6.0) + 1e-3;
    vec2 c = vec2(dot(pos.xz, per) / 48.0, dot(pos.xz, dir) / 380.0 + pos.y / 700.0) + float(i) * 7.3;
    // pass 2: irregular rib spacing (evenly spaced ribs read as comb marks); the warp's own gradient is ignored
    c.x += 1.6 * vnoise2(vec2(c.x * 0.23, c.y * 0.9) + 3.7);
    vec3 n1 = farVN(c), n2 = farVN(c * vec2(2.3, 1.7) + 3.1);
    vec2 g = n1.yz * 0.65 + n2.yz * vec2(2.3, 1.7) * 0.35;
    vec3 gw = vec3(per.x * g.x / 48.0 + dir.x * g.y / 380.0, g.y / 700.0, per.y * g.x / 48.0 + dir.y * g.y / 380.0);
    s += w * vec4(n1.x * 0.65 + n2.x * 0.35, gw);
    wsum += w;
  }
  s /= wsum;
  // the blend flattens contrast: restore it
  return vec4(0.5 + (s.x - 0.5) * 1.7, s.yzw * 1.7);
}
// Aretes: sharp-crested spurs running down the fall line every ~200 m (ridged value noise on the same 4-direction
// scheme). On the smooth DEM shoulders (rounded pre-alpine ridges, 312 m L0 cells beyond 25 km) they split each face
// into a lit and a shadowed flank with a crisp crest line: the jagged look of the refs' ranges.
// Returns (crest 0..1, world gradient per m of the ridged profile).
vec4 farAretes(vec3 pos, vec3 n0){
  vec2 gd = n0.xz / max(length(n0.xz), 1e-3);
  vec4 s = vec4(0.0);
  float wsum = 0.0;
  for (int i = 0; i < 4; i++) {
    float a = float(i) * 0.7854 + 0.39;
    vec2 dir = vec2(cos(a), sin(a)), per = vec2(-dir.y, dir.x);
    float w = pow(abs(dot(gd, dir)), 4.0) + 1e-3;
    vec2 c = vec2(dot(pos.xz, per) / 210.0, dot(pos.xz, dir) / 1100.0 + pos.y / 1500.0) + float(i) * 3.7 + 11.0;
    vec3 n1 = farVN(c);
    float sg = n1.x > 0.5 ? 1.0 : -1.0;
    vec2 g = -2.0 * sg * n1.yz;                              // d/dc of 1 - |2v - 1|
    vec3 gw = vec3(per.x * g.x / 210.0 + dir.x * g.y / 1100.0, g.y / 1500.0, per.y * g.x / 210.0 + dir.y * g.y / 1100.0);
    s += w * vec4(1.0 - abs(2.0 * n1.x - 1.0), gw);
    wsum += w;
  }
  return s / wsum;
}
// Round 5: gullies and spurs (~650 m apart, ~2.6 km long, ridged: V-shaped gullies between sharp spurs) on the same
// 4-direction fall-line scheme. The hero lenses magnify the far ranges ~2x over the refs, so the 312 m DEM cells of
// the Bernese Alps span 15-30 px: without relief at this scale every face read as one smooth airbrushed plane.
vec4 farGullies(vec3 pos, vec3 n0){
  vec2 gd = n0.xz / max(length(n0.xz), 1e-3);
  vec4 s = vec4(0.0);
  float wsum = 0.0;
  for (int i = 0; i < 4; i++) {
    float a = float(i) * 0.7854 + 0.2;
    vec2 dir = vec2(cos(a), sin(a)), per = vec2(-dir.y, dir.x);
    float w = pow(abs(dot(gd, dir)), 4.0) + 1e-3;
    vec2 c = vec2(dot(pos.xz, per) / 650.0, dot(pos.xz, dir) / 2600.0 + pos.y / 3200.0) + float(i) * 5.1 + 23.0;
    c.x += 0.8 * vnoise2(vec2(c.x * 0.31, c.y * 1.3) + 1.9);
    vec3 n1 = farVN(c);
    float sg = n1.x > 0.5 ? 1.0 : -1.0;
    vec2 g = -2.0 * sg * n1.yz;
    vec3 gw = vec3(per.x * g.x / 650.0 + dir.x * g.y / 2600.0, g.y / 3200.0, per.y * g.x / 650.0 + dir.y * g.y / 2600.0);
    s += w * vec4(1.0 - abs(2.0 * n1.x - 1.0), gw);
    wsum += w;
  }
  return s / wsum;
}
// Round 8: fine streaks (~22 m across, ~150 m along the fall line): the rock steps and snow runnels that texture every
// face of the refs' ranges at the pixel scale (from the hero distances the 48 m ribs alone left smooth airbrushed snow)
vec4 farStreaks(vec3 pos, vec3 n0){
  vec2 gd = n0.xz / max(length(n0.xz), 1e-3);
  vec4 s = vec4(0.0);
  float wsum = 0.0;
  for (int i = 0; i < 4; i++) {
    float a = float(i) * 0.7854 + 0.55;
    vec2 dir = vec2(cos(a), sin(a)), per = vec2(-dir.y, dir.x);
    float w = pow(abs(dot(gd, dir)), 6.0) + 1e-3;
    vec2 c = vec2(dot(pos.xz, per) / 22.0, dot(pos.xz, dir) / 150.0 + pos.y / 320.0) + float(i) * 4.9 + 31.0;
    c.x += 1.3 * vnoise2(vec2(c.x * 0.29, c.y * 1.1) + 6.3);
    vec3 n1 = farVN(c);
    vec2 g = n1.yz;
    s += w * vec4(n1.x, per.x * g.x / 22.0 + dir.x * g.y / 150.0, g.y / 320.0, per.y * g.x / 22.0 + dir.y * g.y / 150.0);
    wsum += w;
  }
  s /= wsum;
  return vec4(0.5 + (s.x - 0.5) * 1.8, s.yzw * 1.8);
}
// world size of a pixel on the far surface (m): sets the relief / rock-streak level of detail (farSnow, called in
// uniform control flow, stores it)
float gFarPx = 50.0;
// round 8 pass 2: isotropic sub-DEM undulation (~170 m / ~65 m: wind drifts, benches, the roll of the snowfields),
// shading only: between the DEM vertices the lit snowfields were one flat fill (critique: 32-42% flat 5x5 windows,
// refs ~20%). World gradient (per m) of the undulation height, faded by the pixel footprint.
vec2 farUndul(vec2 xz, float px){
  vec3 u1 = farVN(xz / 170.0 + 2.3), u2 = farVN(xz / 65.0 + 7.1);
  float w1 = 1.0 - smoothstep(30.0, 70.0, px), w2 = 1.0 - smoothstep(12.0, 28.0, px);
  return u1.yz * (30.0 / 170.0) * w1 + u2.yz * (10.0 / 65.0) * w2;
}
// round 8 pass 2: multi-octave breakup of the snow line (~40 / 15 / 6 m: outcrops in the snowfields, snow patches on
// the rock); each octave fades with the pixel footprint and hands its variance to varU (the coverage turns fractional
// where it averages out instead of thresholding its mean)
float farBreak(vec2 xz, float px, out float varU){
  float a1 = 1.0 - smoothstep(10.0, 24.0, px), a2 = 1.0 - smoothstep(4.0, 9.0, px), a3 = 1.0 - smoothstep(1.6, 3.6, px);
  float b = (vnoise2(xz / 40.0 + 1.7) - 0.5) * a1 + 0.6 * (vnoise2(xz / 15.0 + 4.4) - 0.5) * a2
          + 0.35 * (vnoise2(xz / 6.0 + 9.1) - 0.5) * a3;
  varU = 0.03 * ((1.0 - a1) * (1.0 - a1) + 0.36 * (1.0 - a2) * (1.0 - a2) + 0.12 * (1.0 - a3) * (1.0 - a3));
  return b;
}
// snow fraction: snow holds on anything under ~50 deg and in the couloirs; rib crests and the flanks of the ribs on
// steep faces stay dark rock (streaks down the fall line), the shoulders are a near-continuous white
float farSnow(vec3 pos, vec3 n0, float curv){
  // (geometric mean of the two screen axes: the grazing axis alone faded the relief on every face seen side-on)
  gFarPx = max(sqrt(length(dFdx(pos)) * length(dFdy(pos))), 1.0);
  if (length(pos - cameraPosition) < 2800.0) return 0.0;   // no far weight there: skip the cost
  // the DEM flattens the real 35-50 deg faces: exaggerate its slope for snow and light (round 8: x1.55, was 1.8 -
  // L0's 312 m cells are gone: LF / L1 / LM carry the faces at 16-60 m)
  vec3 nE = normalize(vec3(n0.x * 1.55, n0.y, n0.z * 1.55));
  float steep = smoothstep(0.85, 0.45, nE.y);
  vec4 rb = farRibs(pos, n0);
  vec4 ar = farAretes(pos, n0);
  vec4 gu = farGullies(pos, n0);
  vec4 st = farStreaks(pos, n0);
  // relief, faded where a pixel no longer resolves it (no shimmer): ribs ~17 m on steep faces, a ripple on the
  // shoulders; arete flanks ~40 m (weaker on flat ground); gully / spur flanks ~110 m
  // (round 8 pass 2: each gone by ~2.5-3 px per period - the p2c pan test (tools/farpan.mjs + farflick.mjs) showed
  // the 48 m ribs crawling on the 20-30 km faces at ~20 m per pixel; were 14-36 / 60-150 / 200-500 / 6-15 m)
  float wR = 1.0 - smoothstep(9.0, 20.0, gFarPx), wA = 1.0 - smoothstep(35.0, 80.0, gFarPx);
  float wG = 1.0 - smoothstep(110.0, 250.0, gFarPx);
  float wS = 1.0 - smoothstep(4.0, 9.0, gFarPx);
  float slopeW = smoothstep(0.98, 0.8, nE.y);
  // pass 2: the fine streaks in patches (~400 m), not one uniform comb over every face (critique: parallel brush
  // strokes, all 3-6 px wide)
  float stM = 0.3 + 0.7 * smoothstep(0.25, 0.75, vnoise2(pos.xz / 420.0 + 2.9));
  vec2 un = farUndul(pos.xz, gFarPx);
  // (and a ~25 m grain - drifts, small steps and boulders under the snow - so the snowfields carry pixel-scale shading
  // in telephoto; gone by ~10 m per pixel)
  vec3 gr = farVN(pos.xz / 25.0 + 5.7);
  un += gr.yz * (2.5 / 25.0) * (1.0 - smoothstep(4.0, 10.0, gFarPx));
  vec3 g = rb.yzw * mix(9.0, 17.0, steep) * wR + ar.yzw * mix(18.0, 42.0, steep) * slopeW * wA
         + gu.yzw * mix(90.0, 200.0, steep) * slopeW * wG + st.yzw * mix(3.0, 7.0, steep) * slopeW * wS * stM
         + vec3(un.x, 0.0, un.y) * (1.0 - 0.5 * steep);
  g -= nE * dot(g, nE);
  vec3 nb = normalize(nE - g);
  // shoulders: the slope decides (white blanket, a few ribs show); steep faces: the ribs decide (bare rock ribs, white
  // couloirs between them) so the rock reads as streaks down the fall line, not as bands along the cliff belts
  // (each pattern fades to its mean where its relief does: unresolved rock streaks shimmered)
  float rx = mix(0.47, rb.x, wR), ax = mix(0.5, ar.x, wA), gx = mix(0.5, gu.x, wG), sx = mix(0.5, st.x, wS);
  // round 8: the moderate slopes are textured too (refs: runnels and rock steps on most faces, white only on the
  // flattest shoulders) - the ribs + streaks weigh by slope (+-0.06 on the shoulders .. +-0.33 at ~40 deg)
  float txA = mix(0.17, 0.6, smoothstep(0.93, 0.62, nE.y));
  float txt = txA * ((rx - 0.47) + 0.6 * stM * (sx - 0.5));
  // (pass 2: the arete / gully terms ~1.4x: crisper rock spurs and snow gullies on the faces)
  // (round 8: wind-scoured convex crests and knolls show rock - the rounded pre-alpine tops were smooth white domes)
  // (round 8 pass 2: the 210 m arete / 650 m gully terms ~0.6x and the DEM's own concavity ~1.7x: the large-scale
  // terms drew 20-60 px rock blobs in telephoto (refs: 3-10 px outcrops); the snow now sits in the DEM's real
  // gullies, the rock on its convex ribs)
  float gentle = nb.y + 0.25 * curv - txt - 0.3 * max(-curv, 0.0) * (0.5 + sx) - 0.10 * steep * smoothstep(0.75, 0.95, ax)
               - 0.09 * steep * smoothstep(0.70, 0.95, gx);
  // steep faces: bare rock on the spurs, snow down the gullies (the large-scale streaking of the refs' faces)
  // (round 8: base 0.49, was 0.45: the steep faces ~40-50% snow streaks, refs 4 / 7; the big north faces read as
  // one flat dark plane)
  float couloir = 0.51 - 0.6 * (rx - 0.47) - 0.3 * stM * (sx - 0.5) + 0.6 * (nb.y - nE.y) + 0.28 * curv
                - 0.12 * smoothstep(0.7, 0.95, ax) - 0.12 * smoothstep(0.62, 0.92, gx) + 0.09 * (1.0 - smoothstep(0.08, 0.35, gx));
  float cw = smoothstep(0.66, 0.46, nE.y);
  float hold = mix(gentle, couloir, cw);
  // the highest summits are plastered (ice faces), the shoulders below ~2400 m more broken
  hold += 0.08 * smoothstep(3000.0, 3800.0, pos.y) - 0.12 * smoothstep(2600.0, 1800.0, pos.y);
  // pass 2: more bare rock on the steep faces (refs: dark faces streaked with snow, not a white blanket)
  hold -= 0.11 * steep;
  // round 8 pass 2: the north faces hold more snow (no melt / wind crust: the shaded faces of the S views were one
  // dark rock silhouette, critique p50 L* 25.6)
  hold += 0.08 * smoothstep(0.05, 0.5, -nE.z);
  // round 8 pass 2: broken, mottled cover (outcrops in the snowfields, snow patches on the rock; was a fine 18 m
  // speckle on a crisp 1 px edge: two flat fills, cel-shaded)
  float vB;
  // (p2b: ~1.7x - at 0.1-0.2 the big rib / arete / DEM-concavity terms still drew 20-60 px blobs, critique item 1)
  float brA = mix(0.18, 0.32, smoothstep(0.95, 0.6, nE.y));
  hold += brA * farBreak(pos.xz, gFarPx, vB);
  // the snow / rock edge: ~1 px where the patterns are resolved, widened by the variance of those that a pixel
  // averages (sub-pixel ribs / streaks / outcrops -> a fractional cover, the mid tones of the refs' faces; temporally
  // stable: no octave is thresholded below the pixel)
  float kR = mix(txA, 0.6, cw), kS = mix(0.6 * txA, 0.3, cw) * stM, kA = mix(0.10 * steep, 0.12, cw), kG = mix(0.09 * steep, 0.2, cw);
  float vU = 0.03 * ((1.0 - wR) * (1.0 - wR) * kR * kR + (1.0 - wS) * (1.0 - wS) * kS * kS)
           + 0.02 * ((1.0 - wA) * (1.0 - wA) * kA * kA + (1.0 - wG) * (1.0 - wG) * kG * kG) + brA * brA * vB;
  float hw = sqrt(vU + 0.36 * fwidth(hold) * fwidth(hold) + 0.0002);
  float s = smoothstep(0.445 - 1.7 * hw, 0.445 + 1.7 * hw, hold);
  gFarNb = nb; gFarN0 = n0; gFarSnow = s; gFarHave = 1.0;
  return s;
}
vec3 farSnowAlbedo(vec3 pos){ return vec3(0.84, 0.86, 0.92); }
// (round 5: darker rock: the refs' far faces are dark rock streaked with snow, crisp against the lit snow)
// (round 8: 0.155, was 0.19: the art director's 'shadows not nearly dark enough' - rock streaks crisp on the snow)
vec3 farRockAlbedo(vec3 pos, vec3 n0){ return srgb2lin(vec3(0.155, 0.157, 0.185)); }
// Light on the far ranges (replaces alb * skyIrradiance): a strong key from the bright sky up and left of the hero
// view (az ~74, 25 deg up) with a crisp terminator, so faces turned to camera-left read as bright snow and the others
// fall into blue shadow; a navy sky fill that is weaker on steep faces; the sunset glow on faces turned to it; faint
// alpenglow on the highest snow. The key is warm-neutral because the haze (applyAtmos) takes out red first: lit snow
// lands near-white lavender at 10-20 km, shadows navy. Uses its own albedo (far snow / rock / forest / valley floor).
vec3 farLight(vec3 col, vec3 alb, vec3 n, vec3 pos, float snow, float skyVis, float glowVis){
  float dist = length(pos - cameraPosition);
  float farF = smoothstep(3000.0, 20000.0, dist);     // the weight terrain.js applies to this result
  if (dist < 2800.0 || farF < 1e-4 || gFarHave < 0.5) return col;
  float y = pos.y;
  vec3 n0 = gFarN0;
  // albedo: snow above the patchy snow line, dark conifer forest below ~1800 m, open valley floors
  float s = gFarSnow * smoothstep(1000.0, 1400.0, y + 200.0 * (vnoise2(pos.xz / 1400.0) - 0.5));
  vec3 nb = gFarNb;
  // round 8 pass 2: a thin dusting on the rock (more on the moderate slopes) and some tone inside both fills (wind
  // crust / old snow, lighter and darker rock bands): refs 4 / 7 show gradients inside the snow and the rock
  // (each noise fades to its mean once a pixel spans ~1/3 of its cell: no shimmer on the horizon ranges)
  #define FAR_FADE(sc) (1.0 - smoothstep(0.25 * (sc), 0.6 * (sc), gFarPx))
  float dust = (0.03 + 0.12 * smoothstep(0.6, 0.9, nb.y)) * mix(0.5, vnoise2(pos.xz / 55.0 + 3.3), FAR_FADE(55.0));
  s = mix(dust * smoothstep(1400.0, 1800.0, y), 1.0, s);
  // p2b: pixel-scale texture inside both fills (critique: 20-60 px flat rock blobs and flat snow in telephoto, refs
  // 3-10 px outcrops): snow-filled ledges and patches in the rock, small outcrops in the snow (~16 / ~11 m); where a
  // pixel can no longer resolve them they leave their mean cover
  float stp = smoothstep(0.8, 0.45, nb.y), alt = smoothstep(1500.0, 1900.0, y);
  float led = smoothstep(0.56, 0.76, vnoise2(pos.xz / 16.0 + 1.1) * 0.65 + vnoise2(pos.xz / 7.0 + 3.9) * 0.35) * (0.9 - 0.5 * stp) * alt;
  float dot_ = smoothstep(0.68, 0.84, vnoise2(pos.xz / 11.0 + 7.7)) * (0.35 + 0.5 * stp) * alt;
  s = mix(s + (1.0 - s) * 0.12 * (0.9 - 0.5 * stp) * alt - s * 0.05 * (0.35 + 0.5 * stp) * alt,
          min(max(s, led), 1.0 - 0.9 * dot_), FAR_FADE(16.0));
  vec3 a = mix(farRockAlbedo(pos, n0) * (1.0 + 0.6 * (vnoise2(pos.xz / 90.0 + 6.2) - 0.5) * FAR_FADE(90.0)),
               farSnowAlbedo(pos) * (0.92 + 0.16 * (vnoise2(pos.xz / 230.0 + 1.3) - 0.5) * FAR_FADE(230.0)
               + 0.12 * (vnoise2(pos.xz / 30.0 + 2.1) - 0.5) * FAR_FADE(30.0) + 0.10 * (vnoise2(pos.xz / 12.0 + 8.4) - 0.5) * FAR_FADE(12.0)), s);
  #undef FAR_FADE
  float fN = vnoise2(pos.xz / 260.0) * 0.7 + vnoise2(pos.xz / 90.0 + 4.0) * 0.3;
  float forest = smoothstep(1850.0, 1550.0, y + 320.0 * (fN - 0.5)) * smoothstep(0.55, 0.8, n0.y) * smoothstep(0.25, 0.45, fN);
  a = mix(a, mix(srgb2lin(vec3(0.075, 0.095, 0.10)), farSnowAlbedo(pos), 0.18), forest);
  a = mix(a, srgb2lin(vec3(0.30, 0.31, 0.33)), smoothstep(950.0, 750.0, y) * smoothstep(0.85, 0.97, n0.y));
  // round 8 pass 2: where the point lies relative to the glow, seen from the camera (per point: stable while the
  // camera turns): gvd 1 = straight into the glow, -1 = straight away from it
  vec3 vd = (pos - cameraPosition) / dist;
  vec2 SH = normalize(uSunDir.xz + vec2(1e-5));
  float gvd = dot(vd.xz, SH) / max(length(vd.xz), 1e-3);
  float glowV = smoothstep(0.6, 0.97, gvd);      // within ~15-55 deg of the glow
  float antiV = smoothstep(-0.1, -0.7, gvd);     // away from it (> ~95 deg)
  // key from az 110, 15 deg up: faces turned to camera-left lit, faces toward the camera ~40 %, faces turned
  // right in shadow (round 3's az 74 / 25 deg lit two thirds of the visible faces)
  const vec3 K = vec3(0.908, 0.259, 0.330);
  // the lower ridges (Brienz / Faulhorn group) sit in the shade of the higher ranges around them: darker in front,
  // the high Bernese snow brightest (refs: near ridges darker, far ones lighter)
  float hk = mix(0.3, 1.2, smoothstep(1800.0, 2950.0, y));
  // pass 2: a crisper terminator (sharp lit / shadow split along the crests; was smoothstep(0.06, 0.7)); the key
  // pre-compensates the haze's red-first extinction with distance so lit snow lands neutral lavender (#918daa, R ~ G)
  // instead of periwinkle; a darker, less saturated fill so the shadow faces reach the refs' #263960 / #152850
  // round 5: inside the lit faces the key still follows the relief (a saturated key painted each face one flat tone)
  float kd = dot(nb, K);
  // (round 8 pass 2: Lambert-like inside the lit faces (was saturated from n.K 0.36: one flat white per face); the
  // terminator itself stays crisp)
  float key = smoothstep(0.04, 0.30, kd) * (0.42 + 0.9 * clamp(kd, 0.0, 1.0)) * hk;
  // round 8: cast shadows of the ranges along the key (vKey, baked per vertex by tools/farkey.mjs: a ridge rising
  // above the key's 15 deg shades the valley and the lee faces behind it); a little sky key stays in them
  // (pass 2: floor 0.2, was 0.12)
  key *= 0.2 + 0.8 * vKey;
  // round 8 pass 2: looking into the glow the ranges are back-lit: the faces turned to the camera fall into shade, only
  // the faces turned to the light and the crest rims stay lit (critique: fI's lit snow L* p99 77.7, as bright as the
  // glow sky above it; ref 4 ~52-56, >15 L* under its sky)
  float camF = smoothstep(0.0, 0.6, dot(nb, -vd));
  // (p2b: 0.2 + 0.35, was 0.3 + 0.45 over a wider window: fI's range fell to L* p99 52, a flat purple-grey veil)
  key *= 1.0 - glowV * (0.2 + 0.35 * camF);
  float up = max(nb.y, 0.0);
  // (round 8: the far key ~10% brighter: the refs' lit snow on the horizon ranges reads near-white through the haze)
  // (round 8: the far key's red pre-compensation is mostly done by the extinction restore below)
  vec3 kc = mix(vec3(1.10, 0.97, 0.86), vec3(1.30, 1.08, 0.94), smoothstep(5000.0, 25000.0, dist));
  // (round 8: a bluer fill, ~15% darker near, a little brighter on the horizon ranges: refs 4 / 7 / 1 show their
  // shadow faces mid blue (#3a4d7a..#4d5883 after the haze; ours #2d395c), the nearer ridges dark navy)
  // (round 8 pass 2: the sky dome by (1 + n.y) / 2 like a real hemisphere, was n.y^2: a 45-55 deg face sees half the
  // sky, and its snow in shade is mid blue (ref 4 L* 40-48, ours 25-34) while the dark rock stays dark)
  float fillD = mix(1.0, 1.15, smoothstep(8000.0, 25000.0, dist));
  // (p2b: ~1.7x and less saturated: p2a's shaded snow still L* ~35 #415389, ref 4's #6f7aa8..#7b6f95 at 40-48; the
  // rock albedo keeps the shaded rock dark)
  vec3 E = (vec3(0.072, 0.112, 0.205) + vec3(0.085, 0.12, 0.19) * up) * fillD + kc * key;
  // the glow-side sky (horizontal: how far a face turns toward the glow azimuth, scaled by its steepness)
  float sw = dot(nb.xz, SH);
  float swp = max(sw, 0.0);
  float hi = smoothstep(2800.0, 3900.0, y);
  // the glow on faces turned to it: the high summits only (pass 1's warm cast on the mid faces read purple-grey)
  E += vec3(0.24, 0.10, 0.05) * swp * swp * (0.08 + 0.92 * hi) * glowVis;
  // round 8: the bright western sky lights every face turned to it (lavender-rose, cooler low down): from the free
  // cameras looking north / east the camera-facing slopes are those faces, and under the az 110 key alone they were
  // one flat shadow tone (the hero views see these faces only edge-on, as the rose right flanks of refs 4 / 7)
  // (pass 2: ~3x, and wrapped: critique fJ, the snow of the E ranges #58649b darker than the sky behind them; refs
  // 20-40 km snow L* >= 50)
  E += mix(vec3(0.17, 0.14, 0.19), vec3(0.22, 0.14, 0.11), hi) * smoothstep(-0.2, 0.75, sw) * (0.55 + 0.45 * up)
     * glowVis * mix(0.6, 1.0, skyVis);
  // alpenglow on the high snow (#c97d6e .. #f89b61 on the glow side) (pass 2: on the faces turned to the glow, not on
  // every high face: it lit the camera-facing snow of the glow views)
  E += vec3(0.20, 0.085, 0.055) * hi * s * (0.12 + 0.88 * smoothstep(-0.1, 0.7, sw));
  vec3 fc = a * E * mix(0.75, 1.0, skyVis) * uSkyExposure;
  // blue mist over the cloud sea: the lower slopes of the ranges fade into it (refs: hazy navy bases, crisp tops)
  // (pass 2: darker and weaker, and not over the lit snow)
  fc = mix(fc, vec3(0.034, 0.060, 0.150) * uSkyExposure, 0.55 * (1.0 - 0.6 * key * s) * smoothstep(2500.0, 1750.0, y + 150.0 * (fN - 0.5)));
  // round 8: the haze (applyAtmos: optical depth ~1.2 at 25 km) passes only 25-40% of the surface light, so lit snow
  // and shadow faces of the horizon ranges converged on one pale lavender (m7; and a 1.4x brighter fill / key barely
  // moved the pixels). Restore ~40% of the extinction (in optical depth) for the far terrain: the ranges stay veiled
  // by the air light but keep their contrast - crisp white snow beside blue shadow faces, as in refs 4 / 7 / 1.
  // (wavelength-dependent: it also neutralises the red-first extinction of the lit snow)
  // (pass 2: ~half of it toward the glow (the air toward the light is bright: the back-lit ranges stay veiled and
  // well under the glow sky), ~1.3x away from it (the E / N ranges kept their snow under the sky's L*))
  vec3 Te, air;
  atmosTerms(cameraPosition, pos, Te, air);
  fc *= pow(max(Te, vec3(0.03)), vec3(-0.4 * smoothstep(5000.0, 20000.0, dist) * (1.0 - 0.4 * glowV + 0.6 * antiV)));
  // terrain.js returns mix(col, result, farF): pre-scale so the visible blend is mix(col, fc, farW)
  return col + (fc - col) * (farW(dist) / farF);
}
`;

// the pre-round-8 far look (URL flag '&nofar', with L0 and L1's blended band: A/B comparisons)
export const FAR_R7 = /* glsl */ `
// per-fragment cache: farSnow (called first by terrain.js) stores the relief normal, DEM normal and raw snow
vec3 gFarNb = vec3(0.0, 1.0, 0.0);
vec3 gFarN0 = vec3(0.0, 1.0, 0.0);
float gFarSnow = 0.0;
float gFarHave = 0.0;
// effective far weight: the far look takes over between 2.8 and 8 km (terrain.js's farF only reaches 1 at 20 km)
float farW(float dist){ return smoothstep(2800.0, 8000.0, dist); }
// value noise with its analytic derivative: (v, dv/dx, dv/dy)
vec3 farVN(vec2 p){
  vec2 i = floor(p), f = fract(p);
  vec2 u = f * f * (3.0 - 2.0 * f), du = 6.0 * f * (1.0 - f);
  float a = hash12(i), b = hash12(i + vec2(1.0, 0.0)), c = hash12(i + vec2(0.0, 1.0)), e = hash12(i + vec2(1.0, 1.0));
  float k = a - b - c + e;
  return vec3(a + (b - a) * u.x + (c - a) * u.y + k * u.x * u.y, du * (vec2(b - a, c - a) + k * u.yx));
}
// Fall-line ribs: value noise stretched along 4 fixed horizontal directions (~70 m across, ~450 m along), blended by
// how well each matches the local downhill direction (per-pixel frames drew contour-line moire).
// Returns (value 0..1: 1 = rib crest, 0 = couloir floor; world gradient per m).
vec4 farRibs(vec3 pos, vec3 n0){
  vec2 gd = n0.xz / max(length(n0.xz), 1e-3);
  vec4 s = vec4(0.0);
  float wsum = 0.0;
  for (int i = 0; i < 4; i++) {
    float a = float(i) * 0.7854;
    vec2 dir = vec2(cos(a), sin(a)), per = vec2(-dir.y, dir.x);
    float w = pow(abs(dot(gd, dir)), 6.0) + 1e-3;
    vec2 c = vec2(dot(pos.xz, per) / 48.0, dot(pos.xz, dir) / 380.0 + pos.y / 700.0) + float(i) * 7.3;
    // pass 2: irregular rib spacing (evenly spaced ribs read as comb marks); the warp's own gradient is ignored
    c.x += 1.6 * vnoise2(vec2(c.x * 0.23, c.y * 0.9) + 3.7);
    vec3 n1 = farVN(c), n2 = farVN(c * vec2(2.3, 1.7) + 3.1);
    vec2 g = n1.yz * 0.65 + n2.yz * vec2(2.3, 1.7) * 0.35;
    vec3 gw = vec3(per.x * g.x / 48.0 + dir.x * g.y / 380.0, g.y / 700.0, per.y * g.x / 48.0 + dir.y * g.y / 380.0);
    s += w * vec4(n1.x * 0.65 + n2.x * 0.35, gw);
    wsum += w;
  }
  s /= wsum;
  // the blend flattens contrast: restore it
  return vec4(0.5 + (s.x - 0.5) * 1.7, s.yzw * 1.7);
}
// Aretes: sharp-crested spurs running down the fall line every ~200 m (ridged value noise on the same 4-direction
// scheme). On the smooth DEM shoulders (rounded pre-alpine ridges, 312 m L0 cells beyond 25 km) they split each face
// into a lit and a shadowed flank with a crisp crest line: the jagged look of the refs' ranges.
// Returns (crest 0..1, world gradient per m of the ridged profile).
vec4 farAretes(vec3 pos, vec3 n0){
  vec2 gd = n0.xz / max(length(n0.xz), 1e-3);
  vec4 s = vec4(0.0);
  float wsum = 0.0;
  for (int i = 0; i < 4; i++) {
    float a = float(i) * 0.7854 + 0.39;
    vec2 dir = vec2(cos(a), sin(a)), per = vec2(-dir.y, dir.x);
    float w = pow(abs(dot(gd, dir)), 4.0) + 1e-3;
    vec2 c = vec2(dot(pos.xz, per) / 210.0, dot(pos.xz, dir) / 1100.0 + pos.y / 1500.0) + float(i) * 3.7 + 11.0;
    vec3 n1 = farVN(c);
    float sg = n1.x > 0.5 ? 1.0 : -1.0;
    vec2 g = -2.0 * sg * n1.yz;                              // d/dc of 1 - |2v - 1|
    vec3 gw = vec3(per.x * g.x / 210.0 + dir.x * g.y / 1100.0, g.y / 1500.0, per.y * g.x / 210.0 + dir.y * g.y / 1100.0);
    s += w * vec4(1.0 - abs(2.0 * n1.x - 1.0), gw);
    wsum += w;
  }
  return s / wsum;
}
// Round 5: gullies and spurs (~650 m apart, ~2.6 km long, ridged: V-shaped gullies between sharp spurs) on the same
// 4-direction fall-line scheme. The hero lenses magnify the far ranges ~2x over the refs, so the 312 m DEM cells of
// the Bernese Alps span 15-30 px: without relief at this scale every face read as one smooth airbrushed plane.
vec4 farGullies(vec3 pos, vec3 n0){
  vec2 gd = n0.xz / max(length(n0.xz), 1e-3);
  vec4 s = vec4(0.0);
  float wsum = 0.0;
  for (int i = 0; i < 4; i++) {
    float a = float(i) * 0.7854 + 0.2;
    vec2 dir = vec2(cos(a), sin(a)), per = vec2(-dir.y, dir.x);
    float w = pow(abs(dot(gd, dir)), 4.0) + 1e-3;
    vec2 c = vec2(dot(pos.xz, per) / 650.0, dot(pos.xz, dir) / 2600.0 + pos.y / 3200.0) + float(i) * 5.1 + 23.0;
    c.x += 0.8 * vnoise2(vec2(c.x * 0.31, c.y * 1.3) + 1.9);
    vec3 n1 = farVN(c);
    float sg = n1.x > 0.5 ? 1.0 : -1.0;
    vec2 g = -2.0 * sg * n1.yz;
    vec3 gw = vec3(per.x * g.x / 650.0 + dir.x * g.y / 2600.0, g.y / 3200.0, per.y * g.x / 650.0 + dir.y * g.y / 2600.0);
    s += w * vec4(1.0 - abs(2.0 * n1.x - 1.0), gw);
    wsum += w;
  }
  return s / wsum;
}
// world size of a pixel on the far surface (m): sets the relief / rock-streak level of detail (farSnow, called in
// uniform control flow, stores it)
float gFarPx = 50.0;
// snow fraction: snow holds on anything under ~50 deg and in the couloirs; rib crests and the flanks of the ribs on
// steep faces stay dark rock (streaks down the fall line), the shoulders are a near-continuous white
float farSnow(vec3 pos, vec3 n0, float curv){
  // (geometric mean of the two screen axes: the grazing axis alone faded the relief on every face seen side-on)
  gFarPx = max(sqrt(length(dFdx(pos)) * length(dFdy(pos))), 1.0);
  if (length(pos - cameraPosition) < 2800.0) return 0.0;   // no far weight there: skip the cost
  // the coarse DEM flattens the real 35-50 deg faces: exaggerate its slope (x1.8) for snow and light
  vec3 nE = normalize(vec3(n0.x * 1.8, n0.y, n0.z * 1.8));
  float steep = smoothstep(0.85, 0.45, nE.y);
  vec4 rb = farRibs(pos, n0);
  vec4 ar = farAretes(pos, n0);
  vec4 gu = farGullies(pos, n0);
  // relief, faded where a pixel no longer resolves it (no shimmer): ribs ~17 m on steep faces, a ripple on the
  // shoulders; arete flanks ~40 m (weaker on flat ground); gully / spur flanks ~110 m
  float wR = 1.0 - smoothstep(14.0, 36.0, gFarPx), wA = 1.0 - smoothstep(60.0, 150.0, gFarPx);
  float wG = 1.0 - smoothstep(200.0, 500.0, gFarPx);
  float slopeW = smoothstep(0.98, 0.8, nE.y);
  vec3 g = rb.yzw * mix(9.0, 17.0, steep) * wR + ar.yzw * mix(18.0, 42.0, steep) * slopeW * wA
         + gu.yzw * mix(90.0, 200.0, steep) * slopeW * wG;
  g -= nE * dot(g, nE);
  vec3 nb = normalize(nE - g);
  // shoulders: the slope decides (white blanket, a few ribs show); steep faces: the ribs decide (bare rock ribs, white
  // couloirs between them) so the rock reads as streaks down the fall line, not as bands along the cliff belts
  // (each pattern fades to its mean where its relief does: unresolved rock streaks shimmered)
  float rx = mix(0.47, rb.x, wR), ax = mix(0.5, ar.x, wA), gx = mix(0.5, gu.x, wG);
  // (pass 2: the arete / gully terms ~1.4x: crisper rock spurs and snow gullies on the faces)
  float gentle = nb.y + 0.15 * curv - 0.1 * (rx - 0.42) - 0.16 * steep * smoothstep(0.75, 0.95, ax)
               - 0.15 * steep * smoothstep(0.70, 0.95, gx);
  // steep faces: bare rock on the spurs, snow down the gullies (the large-scale streaking of the refs' faces)
  float couloir = 0.45 - 0.6 * (rx - 0.47) + 0.6 * (nb.y - nE.y) + 0.15 * curv - 0.20 * smoothstep(0.7, 0.95, ax)
                - 0.20 * smoothstep(0.62, 0.92, gx) + 0.14 * (1.0 - smoothstep(0.08, 0.35, gx));
  float hold = mix(gentle, couloir, smoothstep(0.66, 0.46, nE.y));
  // the highest summits are plastered (ice faces), the shoulders below ~2400 m more broken
  hold += 0.08 * smoothstep(3000.0, 3800.0, pos.y) - 0.12 * smoothstep(2600.0, 1800.0, pos.y);
  // pass 2: more bare rock on the steep faces (refs: dark faces streaked with snow, not a white blanket) and a fine
  // rock speckle (~18 m: boulders / rock steps poking through, micro-contrast) that fades before it can shimmer
  hold -= 0.11 * steep;
  float spk = (1.0 - smoothstep(9000.0, 22000.0, length(pos - cameraPosition))) * (1.0 - smoothstep(5.0, 14.0, gFarPx));
  hold += 0.16 * spk * (vnoise2(pos.xz / 18.0 + 5.1) - 0.5) * (0.4 + 0.6 * steep);
  float s = smoothstep(0.41, 0.48, hold);
  gFarNb = nb; gFarN0 = n0; gFarSnow = s; gFarHave = 1.0;
  return s;
}
vec3 farSnowAlbedo(vec3 pos){ return vec3(0.84, 0.86, 0.92); }
// (round 5: darker rock: the refs' far faces are dark rock streaked with snow, crisp against the lit snow)
vec3 farRockAlbedo(vec3 pos, vec3 n0){ return srgb2lin(vec3(0.19, 0.19, 0.22)); }
// Light on the far ranges (replaces alb * skyIrradiance): a strong key from the bright sky up and left of the hero
// view (az ~74, 25 deg up) with a crisp terminator, so faces turned to camera-left read as bright snow and the others
// fall into blue shadow; a navy sky fill that is weaker on steep faces; the sunset glow on faces turned to it; faint
// alpenglow on the highest snow. The key is warm-neutral because the haze (applyAtmos) takes out red first: lit snow
// lands near-white lavender at 10-20 km, shadows navy. Uses its own albedo (far snow / rock / forest / valley floor).
vec3 farLight(vec3 col, vec3 alb, vec3 n, vec3 pos, float snow, float skyVis, float glowVis){
  float dist = length(pos - cameraPosition);
  float farF = smoothstep(3000.0, 20000.0, dist);     // the weight terrain.js applies to this result
  if (dist < 2800.0 || farF < 1e-4 || gFarHave < 0.5) return col;
  float y = pos.y;
  vec3 n0 = gFarN0;
  // albedo: snow above the patchy snow line, dark conifer forest below ~1800 m, open valley floors
  float s = gFarSnow * smoothstep(1000.0, 1400.0, y + 200.0 * (vnoise2(pos.xz / 1400.0) - 0.5));
  vec3 a = mix(farRockAlbedo(pos, n0), farSnowAlbedo(pos), s);
  float fN = vnoise2(pos.xz / 260.0) * 0.7 + vnoise2(pos.xz / 90.0 + 4.0) * 0.3;
  float forest = smoothstep(1850.0, 1550.0, y + 320.0 * (fN - 0.5)) * smoothstep(0.55, 0.8, n0.y) * smoothstep(0.25, 0.45, fN);
  a = mix(a, mix(srgb2lin(vec3(0.075, 0.095, 0.10)), farSnowAlbedo(pos), 0.18), forest);
  a = mix(a, srgb2lin(vec3(0.30, 0.31, 0.33)), smoothstep(950.0, 750.0, y) * smoothstep(0.85, 0.97, n0.y));
  vec3 nb = gFarNb;
  // key from az 110, 15 deg up: faces turned to camera-left lit, faces toward the camera ~40 %, faces turned
  // right in shadow (round 3's az 74 / 25 deg lit two thirds of the visible faces)
  const vec3 K = vec3(0.908, 0.259, 0.330);
  vec3 S = normalize(vec3(uSunDir.x, 0.06, uSunDir.z));
  // the lower ridges (Brienz / Faulhorn group) sit in the shade of the higher ranges around them: darker in front,
  // the high Bernese snow brightest (refs: near ridges darker, far ones lighter)
  float hk = mix(0.3, 1.2, smoothstep(1800.0, 2950.0, y));
  // pass 2: a crisper terminator (sharp lit / shadow split along the crests; was smoothstep(0.06, 0.7)); the key
  // pre-compensates the haze's red-first extinction with distance so lit snow lands neutral lavender (#918daa, R ~ G)
  // instead of periwinkle; a darker, less saturated fill so the shadow faces reach the refs' #263960 / #152850
  // round 5: inside the lit faces the key still follows the relief (a saturated key painted each face one flat tone)
  float kd = dot(nb, K);
  // pass 2 (critique: lit snow fell from m6's p95 #878daf to #777ea3, the median drifted purple-grey): the key is back
  // at m6's level on the well-lit faces (up to 1.1x), the fill bluer (shadow faces navy, B - R ~0x35 as in the refs)
  float key = smoothstep(0.10, 0.36, kd) * (0.80 + 0.30 * smoothstep(0.3, 0.85, kd)) * hk;
  float up = max(nb.y, 0.0);
  vec3 kc = mix(vec3(1.10, 0.97, 0.86), vec3(1.42, 1.04, 0.80), smoothstep(5000.0, 25000.0, dist));
  vec3 E = vec3(0.026, 0.046, 0.118) + vec3(0.105, 0.135, 0.245) * up * up + kc * key;
  float sw = max(dot(nb, S), 0.0);
  float hi = smoothstep(2800.0, 3900.0, y);
  // the glow on faces turned to it: the high summits only (pass 1's warm cast on the mid faces read purple-grey)
  E += vec3(0.24, 0.10, 0.05) * sw * sw * (0.08 + 0.92 * hi) * glowVis;
  // alpenglow on the high snow (#c97d6e .. #f89b61 on the glow side)
  E += vec3(0.20, 0.085, 0.055) * hi * s * (0.3 + 0.7 * sw);
  vec3 fc = a * E * mix(0.75, 1.0, skyVis) * uSkyExposure;
  // blue mist over the cloud sea: the lower slopes of the ranges fade into it (refs: hazy navy bases, crisp tops)
  // (pass 2: darker and weaker, and not over the lit snow)
  fc = mix(fc, vec3(0.034, 0.060, 0.150) * uSkyExposure, 0.55 * (1.0 - 0.6 * key * s) * smoothstep(2500.0, 1750.0, y + 150.0 * (fN - 0.5)));
  // terrain.js returns mix(col, result, farF): pre-scale so the visible blend is mix(col, fc, farW)
  return col + (fc - col) * (farW(dist) / farF);
}
`;
