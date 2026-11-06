// Scene-wide constants (keep in sync with tools/terrain.mjs SCENE)
import * as THREE from 'three';

// Location: Brienzer Rothorn (46.787 N, 8.047 E) above Lake Brienz, facing the Bernese Alps.
export const DECK_Y = 2180;          // ring roof-deck altitude (m)
export const LAKE_Y = 564;           // Lake Brienz surface
export const HERO_AZ = 210;          // azimuth the hero camera looks along (through the gorge, toward the lake)
// Ring frame -> world: rotation about Y so that the ring's front (+Z ref) faces back toward the camera.
export function ringYaw() {
  const a = HERO_AZ * Math.PI / 180, dx = Math.sin(a), dz = -Math.cos(a);
  return Math.atan2(-dx, -dz);
}
export const EARTH_R = 6371000;

// Ring geometry (meters). Bridges run along +/-Z (north/south), hero view looks west (-X).
export const RING = {
  Ro: 55,            // outer radius of the ring body
  Ri: 42.6,          // void radius (inner fascia)
};

// Sunset direction: azimuth from north clockwise, elevation (sun below horizon = blue hour)
export const SUN_AZ = 214;          // refs put the glow core 2-5 deg right of the hero axis (210)
export const SUN_EL = -4.0;
export function sunDirection() {
  const az = THREE.MathUtils.degToRad(SUN_AZ), el = THREE.MathUtils.degToRad(SUN_EL);
  // x east, z south
  return new THREE.Vector3(Math.sin(az) * Math.cos(el), Math.sin(el), -Math.cos(az) * Math.cos(el)).normalize();
}

export const CLOUDS = {
  base: 1500,        // cloud sea base altitude (~1 km above the lake)
  top: 1780,         // mean cloud tops (~400 m below the deck; lumps reach ~1900): low enough that the hero
                     // line of sight under the ring clears the gorge fill and reaches the lake; wisps to top + 240
  // broken region over Lake Brienz: a ragged capsule from ~0.7 km out at az 200 (the hero line of sight
  // down to the lake crosses the layer 0.7-2.5 km out; clouds.js fills the saddle under the deck high and
  // keeps a low broken layer 0.45-1 km out along the hero azimuth) along the lake to beyond Interlaken (az 231, 15 km)
  // + a second capsule along the lake itself (Brienz 3.7 km .. Interlaken end 15 km) for top-down views
  gap: { p0: [-240, 658], p1: [-11660, 9440], w0: 1300, grow: 0.14, k: 0.38,   // (r8 p2: 0.38, was 0.56: the lake valley about half open) k: mean coverage of the islands inside the gap (0.2: ~70% open, 0.4: ~35-60% open)
    lake0: [-700, 3800], lake1: [-11400, 10500], lakeW: 1300, lakeGrow: 0.05 },
  // line-of-sight windows (clouds.js sightTex): the lakeshore lights seen below the ring in a set's view at these
  // distances (km from its camera; window radius on the ground, m) show through gaps in the sea for the set's
  // cameras; w: strength (0 = closed sea); r: a set's windows are cut only for cameras within r m of one of its
  // cameras (fading out over the next 40 m). (r5 p2: not view 4 - from its long lens the tubes stood as a dark slot)
  // (r8: w 0 - free-flight film: the valley is open between the banks everywhere; the windows were cut for the stills'
  // hero cameras only and faded in and out as a film camera passed them)
  sight: { w: 0, sets: [
    { view: 7, cams: [7, 11, 5, 6], r: 100, bands: [[6.1, 6.4, 210], [7.95, 8.35, 330], [10.2, 10.85, 750]] },
    { view: 2, cams: [2], r: 25, bands: [[3.6, 4.1, 320]] },
  ] },
  // (r8) free-flight look: [billow relief on (1) / r5 Worley lobes (0), density gain near the camera, min density ramp (m),
  // relief depth (m)]; r5: [0, 1.95, 3.5, 104]
  // (p2: min ramp 2.5 m instead of 8: with 8 m the near tops were a defocused smear 30-40 px wide in low passes)
  r8: [1, 1.3, 2.5, 50],
  // (r8 p2) fine detail of the primary samples (clouds.js fineD): [relief (m) of the 2-56 m octaves, tile (m) of the finest
  // octave, density texture of the outer shell (0..1), the halo round the billows gated by them (1) / smooth (0)]
  // (r9: shell texture 0.45 - with the denser near field its thin patches opened onto the darker inside: flat stains)
  r9: [14, 56, 0.45, 1],
  // (r8 p2) [sky light floor of the shaded flanks (x the r8 floor 14-22%), silver lining toward the glow, swirl (m) of the
  // mid billow octave (p1: 60 - marble swirls), glow multiple-scattering weight (p1: 1 - a mauve wash over the whole sea)]
  r9b: [0.2, 0.04, 25, 0.5],
  // (r9) near field of the close passes (tops 30-300 m off the camera): [density gain (x the r8 gain) of the view rays within
  // r10[1] m of the camera, faded out by r10[2] m, weight of the finest fineD octave (~0.4-1.8 m)]; with the r8 ~15 m mean free
  // path the near tops were a 5-10 m deep fog that blurred every relief under it (cotton wool); the wide views keep the r8 sea
  // (x2.6 to 2.6 km: the near tops read as snow-covered rock)
  r10: [2.0, 400, 2000, 0.3],
  // (r9) [light contrast of the fine relief by its height (0 = off; turrets lit, clefts shaded at 0.35..1.25 of the light),
  // density ramp factor near the camera (1 = r8), bump-normal shading of the fine relief (0 = off), share of the near gain
  // the light samples see (1: hard-edged dark stains over the near tops; 0: they light the r8 density)]
  r10b: [0, 0.6, 0.25, 0],   // (r9 p2: bump 0.25, p1 0.5 - its hard-edged blotches read as lichen on granite)
  // (r9 p2) [billow polarity of the coarse / mid relief octave (0: ridged as r8, 1: rounded lobes with sharp creases; 0 or 1 only),
  // near glow coupled to the sky occlusion (creases: blue-slate, not brownish-pink), near glow gain (mauve tops)]
  r10c: [0, 1, 1, 0.6],
  // (r9 p2) [near cavity of the mid octave's creases, closing depth (m) of ground inside the cloud (0: off - terrain stipple through
  // the tops), near weight of the sky light's diffuse tail (1 = r8), wall-wisp gain beyond ~1 km from the ring (pink plumes)]
  r10d: [0.7, 120, 0.3, 1],
  // (r9 p2) [fade-out (m from the camera) of the near density-ramp factor r10b[1] (<= r10[2]: as p1), cell-size variation (share of
  // the mid lobes varies by +-this x the curl field; 0: as r8), upper edge of the mid-octave cavity, lid share of the closing (0: the
  // ground point only)]
  r10e: [2000, 0, 0.3, 1],
  // (r9 p2) [glow coupled to the sky occlusion at every distance (0: near only - pink plumes on the flanks 1-3 km out), -, -, -]
  r10f: [1, 0, 0, 0],
  sharp: 3.0,        // (r8 p2) composite tent falloff when res < 1 (1.3: a ~3 px blur over the half-resolution march)
  phase: 1,          // (r8 p2) res < 1: the K sub-frames of a still / film frame march at the 4 pixel phases of each cloud texel
                     // (K = 4: the detail of a full-resolution march at the cost of a half-resolution one; 0 = off)
  phaseFp: 0,        // (r8 p2) with the phases: noise LOD / ramp / fine steps at the full-resolution footprint (1) / the march's (0)
  well: 0,           // (r9) the ragged well in the bank under the void (view 8's dark gap; 0 = closed: in the film's dive
                     // through the void it read as a dark blob in the sea)
  terrCov: 0.5,      // (r8 p2) coverage drop over ground rising into the layer (plateaus, ridges: clear)
  fineL: 1,          // (r8 p2) the near light samples see the fine detail: texture in the light, not only the outline
  cov: 0.38,         // (r8 p2: 0.38, p1 0.44) coverage bias of the sea (r5: 0.5): banks with open lanes between them, not one carpet
  fringe: 0.3,       // (r8) Worley lumps on the bank edges (r5: 0.6): puffs only where a bank frays
  // (r8) [tile (m) of the coarse billow octave (rolls ~1/4..1/32 of it), of the mid octave, fine octave weight, sky-occlusion
  // exponent of the height within a heap (r5: 4)]
  r8b: [2600, 600, 0.38, 2.5],
  r8c: [1.2, 0.35, 0, 0],   // (r8) [roll relief gain, Worley lump gain, -, -] (r5: 1, 1): rolling banks, not cauliflower heads
  wind: 2.5,         // (r8) m/s: the cloud relief drifts along the wind (clouds.js uWindDir, az ~110) - motion, not boiling
  res: 0.5,          // (r8) cloud march resolution (fraction of the frame; the composite upsamples it): the film budget
                     // (1080p K=4 with clouds in ~1.5 s) - 1 for full-resolution stills
};
