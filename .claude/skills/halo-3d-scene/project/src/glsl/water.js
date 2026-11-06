// Lake surface shading, included by the terrain fragment shader (needs NOISE, ATMOS, uReflTex, uResolution).
// uHF / uHFSize (coarse L1 heightfield) are injected into the terrain materials by lights.js; without them
// (uHFSize = 0) the reflected-slope march is skipped and the lake mirrors the sky only.
export const WATER = /* glsl */ `
uniform sampler2D uHF;
uniform float uHFSize;
uniform float uLakePx;      // screen pixel angle (rad), set per frame by lights.js (0: not set)
// manual bilinear fetch of the 125 m heightfield (float textures need not filter linearly: nearest
// sampling stair-stepped the mirrored-slope edge into 125 m blocks); texel i sits on L1 vertex 4 i
float lakeHF(vec2 xz){
  float n = float(textureSize(uHF, 0).x);
  vec2 f = clamp((xz / uHFSize + 0.5) * (n - 1.0), vec2(0.0), vec2(n - 1.001));
  ivec2 i = ivec2(floor(f));
  vec2 u = f - floor(f);
  float a = texelFetch(uHF, i, 0).r, b = texelFetch(uHF, i + ivec2(1, 0), 0).r;
  float c = texelFetch(uHF, i + ivec2(0, 1), 0).r, d = texelFetch(uHF, i + ivec2(1, 1), 0).r;
  return mix(mix(a, b, u.x), mix(c, d, u.x), u.y);
}
vec3 lakeColor(vec3 pos, vec3 vd, float skyVis){
  vec2 wp = pos.xz;
  float dist = length(pos - cameraPosition);
  // wind field: gusts drift down the lake axis (Brienz -> Interlaken, WSW); rough cat's-paw patches,
  // calm glassy patches and long thin wind slicks (calm lines) between them
  vec2 ax = vec2(-0.866, 0.5), pe = vec2(-0.5, -0.866);
  vec2 q = vec2(dot(wp, ax), dot(wp, pe));
  float gust = fbm2(q * vec2(1.0 / 2600.0, 1.0 / 900.0) + vec2(uTime * 0.004, 3.1), 4);
  // cat's paws: gust patches 150-600 m inside the big wind field (round 5; refs 4, 7, 11: the lake is mottled
  // into paler mirror-calm and darker rippled patches, luma p10-p90 ~23, not one flat sheet)
  float paw = fbm2(q * vec2(1.0 / 520.0, 1.0 / 210.0) + vec2(uTime * 0.012, 7.7), 3);
  // (0.6 -> 0.4: at full size the paws striped the lake into brush-stroke bands; refs: a smooth mirror whose
  // variation is mostly the slow gradient and the mirrored hills)
  float rough = smoothstep(0.30, 0.68, gust + 0.4 * (paw - 0.44) + 0.12 * (vnoise2(q * vec2(1.0 / 420.0, 1.0 / 150.0)) - 0.5));
  // pixel footprint on the water (m), along the view (stretched by the grazing angle): fine detail fades out
  // before it falls below ~2 px (no shimmer in the 1080p film)
  float fpL = dist * (uLakePx > 0.0 ? uLakePx : 6e-4) / max(-vd.y, 0.03);
  // slicks meander (warped) and break up along their length
  float qy = q.y + 380.0 * gnoise3(vec3(q * (1.0 / 3500.0), 6.1));
  float slick = smoothstep(0.12, 0.0, abs(gnoise3(vec3(q.x / 2600.0, qy / 520.0, 1.7))));
  slick *= smoothstep(0.35, 0.75, gnoise3(vec3(q * vec2(1.0 / 2600.0, 1.0 / 1100.0), 4.2)) + 0.5);
  // slicks only show as glossy lines at grazing angles; seen steeply from above (view 8, film top-down)
  // they read as thin parallel scratches over the lake
  slick *= 1.0 - smoothstep(0.25, 0.55, -vd.y);
  rough *= 1.0 - 0.3 * slick;

  // wind ripples; sub-pixel at distance, so the normal perturbation fades out (no sparkle aliasing)
  float near = 1.0 - smoothstep(1200.0, 8000.0, dist);
  float wv = gnoise3(vec3(wp * 0.02, uTime * 0.05)) * 0.6 + gnoise3(vec3(wp * 0.11, uTime * 0.12)) * 0.4 * near;
  float amp = (0.002 + 0.016 * near) * (0.3 + rough);
  vec3 n = normalize(vec3(wv * amp, 1.0, gnoise3(vec3(wp.yx * 0.02, 3.0)) * amp));
  vec3 r = reflect(vd, n);
  r.y = max(r.y, 0.003);
  float fres = 0.02 + 0.98 * pow(1.0 - max(dot(-vd, n), 0.0), 5.0);

  // reflected ray against the surrounding slopes: dark mirrored mountainsides near the shores,
  // sky / sunset glow where the ray escapes down the valley axis (far end of the lake)
  // Soft hit: coverage grows as the ray passes within a distance-scaled clearance of the slope (ripples blur
  // the mirrored ridge line), march start jittered per pixel (no banding from the geometric step sequence)
  float hit = 0.0, hy = 0.0, th = 0.0;
  // (round 5: jitter hashed from the world position, not interleaved-gradient screen noise: that printed a fine
  // diagonal stripe pattern into the mirrored band; the sub-frames' sub-pixel jitter moves the position, so the
  // accumulated stills / film frames average it out)
  float t = 40.0 * (1.0 + hash12(pos.xz * 0.731 + vec2(17.3, 5.9)));
  if (uHFSize > 0.0) {
    for (int i = 0; i < 56; i++) {
      vec3 q3 = pos + r * t;
      if (abs(q3.x) > uHFSize * 0.5 || abs(q3.z) > uHFSize * 0.5 || q3.y > 4300.0) break;
      float h = lakeHF(q3.xz);
      float soft = 6.0 + 0.012 * t;
      float o = smoothstep(soft, -soft, q3.y - h);
      if (o > hit) { hit = o; hy = h; th = t; }
      if (hit > 0.999) break;
      t += 30.0 + t * 0.07;
    }
    t = max(th, 40.0);
  }
  // clear dome only (the mottled sunset-lit cloud deck turned the lake pink). Wave facets tilted away from
  // the camera mirror lower sky: at grazing angles (far end, toward Interlaken) that picks up the mauve /
  // salmon glow band - more on the rough patches, a clean mirror on the calm ones
  // (round 5) rippled water mirrors a broad band of the sky at any angle, down into the lavender / rose band near
  // the horizon: rough patches read greyer slate, calm ones mirror the deeper dome (refs 7, 11)
  float low = smoothstep(0.24, 0.04, r.y) * (0.35 + 0.65 * rough);
  vec3 sky = skyClear(r);
  sky = mix(sky, 0.5 * (skyClear(normalize(vec3(r.x, r.y * 0.45, r.z))) + skyClear(normalize(vec3(r.x, r.y * 0.12, r.z)))), clamp(0.55 * low + 0.4 * rough, 0.0, 0.8));
  // (m9) the glow's reflection: toward the sunset azimuth the wind-tilted facets mirror the bright low band over a
  // long column down the lake, strongest on the rough patches (film wide shots over the lake toward the glow, art
  // director: 'long reflections of the glow'; a1_fK: the far end read flat grey-lilac)
  vec2 gH = normalize(uSunDir.xz + vec2(1e-4, 0.0));
  float tg = smoothstep(0.85, 0.985, dot(normalize(r.xz + vec2(1e-4, 0.0)), gH)) * smoothstep(0.6, 0.1, r.y);
  if (tg > 0.0) {
    vec3 glowS = skyClear(normalize(vec3(r.x, max(0.012, r.y * 0.06), r.z)));
    sky = mix(sky, max(sky, glowS), tg * (0.45 + 0.5 * rough));
  }
  // steep views (top-down, view 8): the lake mirrors the altocumulus field overhead, so it reads as dark
  // water with a faint pattern of slate cloud and clearer gaps instead of a flat sheet. Coverage only, in
  // the clouds' unlit slate: their sunset-lit undersides mirrored as warm mottling (read as algae / mud)
  float ov = smoothstep(0.32, 0.62, r.y);
  if (ov > 0.0) {
    float ca = skyClouds(pos, r).a;
    sky = mix(sky, vec3(0.040, 0.055, 0.135) * uSkyExposure, ca * ov * 0.6);
  }
  // mirrored slopes: forest / fields below the snow line, snowfields above, lit by the same twilight dome
  vec3 sn = normalize(vec3(-r.x, 0.8, -r.z));
  vec3 alb = mix(vec3(0.010, 0.014, 0.018), vec3(0.36, 0.39, 0.46), smoothstep(1250.0, 2100.0, hy));
  // the airlight between the water and the mirrored hill is kept cool and dim: refs show the dark-hill
  // reflections as a deeper navy than the open water, fading softly into it (not a warm mauve band)
  vec3 slope = applyAtmos(alb * skyIrradiance(sn, 0.75, 0.35), pos, pos + r * t) * vec3(0.5, 0.58, 0.78);
  // rough water smears the mirrored shoreline (partly sky, partly slope); (round 5) the ripples keep mixing in
  // sky, so the band under the far shore is only a few luma darker than the open water (ref 7: -8 luma; ours
  // was -27, a near-black band that outlined the stair-stepped shoreline)
  // (0.62 -> 0.74 once the shore towns stopped outlining it: refs 2, 4, 6 keep a clearly darker mirrored-slope
  // band along the far shore, the open middle mirroring the paler sky)
  // (m9: up to 0.86, was 0.74: from the film's high wide shots the lake read as a matte lilac sheet; a clearer mirror
  // of the dark shores beside the bright sky reads as water)
  // (p2: up to 0.92: still no visible mirrored shores from the high cameras, p1 critique 6)
  vec3 refl = mix(sky, slope, hit * (0.92 - 0.25 * rough));

  // dark steel-navy body (less saturated: refs' lake is grey-navy, blue - red ~ 45 in sRGB); the AI refs'
  // lake is a glossy mirror, so the reflectance is lifted above Fresnel: calm patches mirror the dome,
  // wind patches go darker and matte (low-frequency +-10 luma variation over the lake, refs 4, 8)
  // (round 5: body darker and greyer, calm / rough reflectance contrast wider - the patches survive the haze)
  // (pass 2: body and reflectance floor lifted ~18%, greyer: tuned to view 7 alone, the darkest ref, the lake
  // read darker and bluer than the refs in views 4, 6, 11 (luma 72-88, blue - red 30-45) and no lighter than the land)
  vec3 deep = vec3(0.011, 0.017, 0.030) * (1.0 - 0.35 * rough);
  float F = clamp(0.42 + fres * 1.2, 0.0, 0.9) * mix(1.35, 0.66, rough) * (1.0 + 0.08 * slick);
  // (m9: (0.72, 0.87, 1.0), was (0.8, 0.9, 1.0): the free-flight lake read grey-mauve, R > G (#4c475d); refs steel
  // blue, G > R (#394662 .. #414f70))
  // (p2: (0.56, 0.81, 1.0): the lake still read lilac, a* +8 against the refs' +3 (ref 7 #3b4661), p1 critique 6;
  // (0.64, 0.84, 1.0) moved it only to +7.6)
  vec3 col = mix(deep, refl * vec3(0.56, 0.81, 1.0), clamp(F, 0.0, 0.92));
  // fine wind-ripple mottling (gradient noise, only mildly stretched along the crests: the grazing view itself
  // squashes it into short horizontal streaks; a lattice noise stretched 6:1 read as parallel scratches).
  // Fixed in the world (no swimming under a moving camera); each octave fades out below ~2.5 px
  float rip = 0.0;
  for (int k = 0; k < 3; k++) {
    float La = 72.0 / exp2(float(k));
    float w = smoothstep(2.5, 5.0, La / fpL);
    rip += w * gnoise3(vec3(q.x / La, q.y / (1.8 * La), float(k) * 3.7 + uTime * 0.02)) * (k == 0 ? 0.5 : 0.35);
  }
  col *= 1.0 + 0.4 * rip * (0.45 + 0.55 * rough) * (1.0 - 0.6 * hit);
  // greyer slate overall (refs: lake blue - red ~40 in sRGB at luma ~70; ours was a saturated cobalt, 65)
  col = mix(vec3(dot(col, vec3(0.2126, 0.7152, 0.0722))), col, 0.55);

  // reflected village lights: per-lamp glitter streaks (lights.js mirror pass); ripples wiggle them
  // sideways, slowly varying wind patches modulate them (no distance banding: it striped every streak alike)
  vec2 suv = gl_FragCoord.xy / uResolution;
  float wob = gnoise3(vec3(wp * 0.035, uTime * 0.25)) * 0.7 + gnoise3(vec3(dist * 0.09, wp.x * 0.004 + wp.y * 0.004, uTime * 0.4)) * 0.3;
  vec2 o = vec2(wob * (0.4 + 1.2 * rough) / uResolution.x, 0.0);
  vec3 rl = texture2D(uReflTex, suv + o).rgb;
  float dash = 0.7 + 0.6 * smoothstep(-0.3, 0.3, gnoise3(vec3(wp * 0.003, uTime * 0.2)));
  // (p2: 3.2x, was 2.2x: the town lights' streaks were barely visible from the film's high wide shots)
  col += rl * dash * 3.2;
  col *= mix(0.7, 1.0, skyVis);

  // The blue-hour airlight over the 3-15 km slant paths down to 564 m (applyAtmos, applied by terrain.js
  // after this) is mauve and alone brighter than the refs' lake tones (dark navy #16223d..#2a3a5c, the darkest
  // area of every ref that shows the lake). Over the water, pre-compensate most of it into a dimmer steel-blue
  // haze: final = col*Te + (1-k)*air + k*airBlue. Te / air come from ATMOS applyAtmos itself, so this
  // follows the sky owner's fog constants.
  vec3 TeA, air; atmosTerms(cameraPosition, pos, TeA, air);
  vec3 Te = max(TeA, vec3(0.05));
  // (pass 2: less blue and ~12% brighter: (0.7, 0.8, 1.0) at 0.5x the airlight's luma left the lake blue - red ~48
  // in sRGB, refs 35-41)
  // (m9: (0.72, 0.86, 1.0), was (0.8, 0.87, 1.0), see the reflectance tint above)
  // (p2: (0.58, 0.80, 1.0), see the reflectance tint)
  vec3 airBlue = vec3(0.58, 0.80, 1.0) * (dot(air, vec3(0.2126, 0.7152, 0.0722)) * 0.62 / 0.84);
  // fades toward the far end (Interlaken, 6-16 km) and toward the glow: there the mauve airlight + glow
  // mirror stay (ref 4: lake grades from grey-navy in front to lilac #45506f toward the far end)
  vec2 gd = normalize(uSunDir.xz + vec2(1e-4, 0.0));
  float towardGlow = smoothstep(0.3, 0.95, dot(normalize(vd.xz + vec2(1e-4, 0.0)), gd));
  // (pass 2: 0.85 -> 0.72, and the mauve airlight comes back from ~4 km on and more toward the glow: the lake
  // lightens toward the far end and the sunset side, refs 4, 11: #45506f..#49546c there, and greys a little)
  // (p2: 0.82 and less fade (0.5 / 0.3): the mauve airlight left the free-flight lake lilac, a* +8)
  // (p2b: 0.95, fades 0.3 / 0.25, and a ~10% brighter steel-blue haze: the tints alone moved the lake only to a* +7)
  col += 0.95 * (1.0 - 0.3 * smoothstep(4000.0, 14000.0, dist) - 0.25 * towardGlow) * (airBlue - air) / Te;
  return col;
}
`;
