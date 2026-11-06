// Free-flight drone film (45 s, 30 fps), filmed in the real 3D scene: no reference matte (shots never set `matte`)
// and no far-field dip (dip 0). Every shot is a camera flight through the world: a centripetal Catmull-Rom path
// travelled at a physical speed profile (m/s keys, smoothly interpolated, scaled to the path length) or through timed
// knots (monotone cubic of arc length vs time), an aim that is either keyed to the path knots (gimbal shots; `framing`
// puts the ring at a chosen screen position with a level horizon) or blended toward the flight direction (FPV
// shots), banking from the lateral acceleration (FPV: roll = atan(a_lat / g), returned as cameraAt().roll - main.js
// applies it with camera.rotateZ after lookAt), and a little deterministic drift / buffeting.
// Music: out/music/film45.wav ('Uprising', Scott Buckley, CC BY 4.0), 60 BPM in 3/4: bars every 3 s, phrases at
// 0, 6, 12, 15 (the drop), 21, 27, 33, 39; booms 10-13 in the near-silent gap; hit 37.15; ring-out 42-45 (faded 43-45).
// Every cut falls on the frame of a beat (half-frame time just before it: motion-blur sub-frames never straddle it);
// shot lengths vary 1-12 s: 10 | 1 1 (booms) | 6 (drop) | 3 3 3 1 2 3 (climax) | 12.
// Arc: one long take that glides in from ~470 m ENE and settles into the hero orbit on the 6 s accent -> two
// one-second cuts on the booms (strut, glazing) -> one take that runs in over the front rim and noses over into the
// void, falling on the drop, dives down the slot and pulls out toward the glow -> climax: a rising flyby past the
// pinnacle, an FPV take under the ring and out under its far rim, a glazing glide, a strut whip, a glide under
// the front rim, the deck run -> a long rising, swinging pull-back over the final statement, fading to black with
// the ring-out.
// Framing rule: look toward the glow and slightly down (cloud sea, gorge, valley); keep a bright element (glazing,
// lit soffit / struts or the afterglow band) in every frame and the upper cloud layer small.
import * as THREE from 'three';
import { DECK_Y, ringYaw } from './config.js';

export const FPS = 30;
const D2R = Math.PI / 180, GRAV = 9.81, ROLL_MAX = 32 * D2R;
const V = (x, y, z) => new THREE.Vector3(x, y, z);
const sat = x => Math.min(1, Math.max(0, x));
const smooth = x => x * x * (3 - 2 * x);

// ---- places
// world point at azimuth az (deg from north, clockwise) and horizontal distance d (m) from the ring centre, dy above the deck
const polar = (az, d, dy) => V(Math.sin(az * D2R) * d, DECK_Y + dy, -Math.cos(az * D2R) * d);
// ring frame (m): +X along the WNW bridge, +Z toward the hero side (az 30), y above the deck top (views.js refToWorld, x R)
const YAW = ringYaw(), CY = Math.cos(YAW), SY = Math.sin(YAW);
const ring = (x, y, z) => V(x * CY + z * SY, DECK_Y + y, -x * SY + z * CY);

// framing: an aim point (100 m out) that puts world point pt at screen position (sx, sy) (0..1 from the top left of a
// 16:9 frame, level horizon) for a camera at pos with vertical fov
const _cam = new THREE.PerspectiveCamera(50, 16 / 9, 0.1, 1e6);
function aimFor(pos, pt, sx, sy, fov) {
  const d = pt.clone().sub(pos), h = Math.hypot(d.x, d.z);
  let A = Math.atan2(d.x, -d.z), E = Math.atan2(d.y, h);
  const vf = fov * D2R, hf = 2 * Math.atan(Math.tan(vf / 2) * 16 / 9);
  _cam.fov = fov; _cam.updateProjectionMatrix(); _cam.position.copy(pos);
  for (let i = 0; i < 12; i++) {
    _cam.up.set(0, 1, 0); _cam.lookAt(pos.clone().add(V(Math.sin(A) * Math.cos(E), Math.sin(E), -Math.cos(A) * Math.cos(E))));
    _cam.updateMatrixWorld();
    const p = pt.clone().project(_cam), px = (p.x + 1) / 2, py = (1 - p.y) / 2;
    A += (px - sx) * hf * 0.8; E += (sy - py) * vf * 0.8;
  }
  return pos.clone().add(V(Math.sin(A) * Math.cos(E), Math.sin(E), -Math.cos(A) * Math.cos(E)).multiplyScalar(100));
}
// aim knots for path knots: frame point pt (one or per knot) at screen positions [[sx, sy], ...] (one or per knot)
const framing = (path, pt, scr, fov) => path.map((p, i) => aimFor(p, Array.isArray(pt) ? pt[i] : pt, ...(Array.isArray(scr[0]) ? scr[i] : scr), Array.isArray(fov) ? fov[0] + (fov[1] - fov[0]) * i / (path.length - 1) : fov));
const RC = V(0, DECK_Y - 4, 0);   // ring centre (mid-height of the body)

// cut on the frame of beat time T (s): half-frame time just before frame T*FPS
const at = T => (Math.round(T * FPS) - 0.5) / FPS;

// ---- speed profile: m/s keys at evenly spaced shot-local times, Catmull-Rom interpolated; the integral is scaled
// to the path length (shot.scale reports the factor: ~1 means the keys are the real speeds)
function profile(keys) {
  const n = keys.length - 1, N = 2048, cum = new Float64Array(N + 1);
  const v = x => {
    if (n === 0) return keys[0];
    const f = Math.min(n - 1e-9, Math.max(0, x * n)), i = Math.floor(f), u = f - i;
    const p0 = keys[Math.max(0, i - 1)], p1 = keys[i], p2 = keys[i + 1], p3 = keys[Math.min(n, i + 2)];
    return Math.max(0.05, 0.5 * (2 * p1 + (p2 - p0) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u * u + (3 * p1 - p0 - 3 * p2 + p3) * u * u * u));
  };
  for (let i = 1; i <= N; i++) cum[i] = cum[i - 1] + 0.5 * (v((i - 1) / N) + v(i / N)) / N;
  const tot = cum[N];
  const S = x => { const f = sat(x) * N, i = Math.min(N - 1, Math.floor(f)); return (cum[i] + (cum[i + 1] - cum[i]) * (f - i)) / tot; };
  S.mean = tot;   // mean of the keyed speed over the shot
  return S;
}

// ---- shot construction
// path: knots (Vector3); aim: knots (same count, gimbal aim keyed to the path), a single point, or null (look along
// the flight); look: 0 = aim only .. 1 = flight direction (number or per-knot keys); tilt: deg added to the pitch of
// the flight direction (FPV camera uptilt); speed: m/s keys; fov: [start, end] or number; bank: 0 (gimbal, level)
// .. 1 (full coordinated-turn roll); drift: hover drift / buffeting amplitude (m; ~0.1 deg of aim per m)
function shot(o) {
  const s = { dip: 0, look: 0, tilt: 0, bank: 0, drift: 0.3, ...o };
  s.curve = new THREE.CatmullRomCurve3(s.path, false, 'centripetal');
  s.curve.arcLengthDivisions = 4000;
  s.len = s.curve.getLength();
  if (Array.isArray(s.aim) && s.aim.length > 1) s.aimCurve = new THREE.CatmullRomCurve3(s.aim, false, 'centripetal');
  if (Array.isArray(s.look)) s.lookKeys = s.look;
  s.S = profile(s.speed || [1]);
  return s;
}
// timed knots (shot.times: absolute film time at which each path knot is passed): the arc length is a monotone cubic
// (Fritsch-Carlson) of time through the knots - continuous speed, never backwards, stops where two knots are close in
// space but apart in time
function timed(s) {
  const n = s.path.length, D = 4000, lens = s.curve.getLengths(D), len = lens[D];
  const L = s.path.map((_, i) => { const f = i / (n - 1) * D, k = Math.min(D - 1, Math.floor(f)); return (lens[k] + (lens[k + 1] - lens[k]) * (f - k)) / len; });
  const X = s.times.map(t => (t - s.start) / s.dur), d = [], m = [];
  for (let i = 0; i < n - 1; i++) d.push((L[i + 1] - L[i]) / (X[i + 1] - X[i]));
  m[0] = d[0]; m[n - 1] = d[n - 2];
  for (let i = 1; i < n - 1; i++) m[i] = d[i - 1] * d[i] <= 0 ? 0 : ((X[i + 1] - X[i]) * d[i - 1] + (X[i] - X[i - 1]) * d[i]) / (X[i + 1] - X[i - 1]);
  for (let i = 0; i < n - 1; i++) {
    if (d[i] <= 1e-9) { m[i] = m[i + 1] = 0; continue; }
    const a = m[i] / d[i], b = m[i + 1] / d[i], h = a * a + b * b;
    if (h > 9) { const k = 3 / Math.sqrt(h); m[i] = k * a * d[i]; m[i + 1] = k * b * d[i]; }
  }
  return x => {
    let i = 0; while (i < n - 2 && x > X[i + 1]) i++;
    const h = X[i + 1] - X[i], t = sat((x - X[i]) / h), t2 = t * t, t3 = t2 * t;
    return sat((2 * t3 - 3 * t2 + 1) * L[i] + (t3 - 2 * t2 + t) * h * m[i] + (3 * t2 - 2 * t3) * L[i + 1] + (t3 - t2) * h * m[i + 1]);
  };
}
const keyAt = (keys, x) => {   // smooth interpolation of evenly spaced scalar keys
  const n = keys.length - 1; if (n === 0) return keys[0];
  const f = sat(x) * n, i = Math.min(n - 1, Math.floor(f)), u = smooth(f - i);
  return keys[i] + (keys[i + 1] - keys[i]) * u;
};

// points on an arc in the ring frame: centre (cx, cz), radius r, angle a0 -> a1 (deg, from +X toward +Z), y0 -> y1
const arc = (cx, cz, r, a0, a1, y0, y1, n = 5) => [...Array(n)].map((_, i) => { const u = i / (n - 1), a = (a0 + (a1 - a0) * u) * D2R; return ring(cx + r * Math.cos(a), y0 + (y1 - y0) * u, cz + r * Math.sin(a)); });
const rep = (p, n) => [...Array(n)].map(() => p.clone());
// gimbal aim knots from headings: 100 m from each path knot along ring-frame heading yaw (deg, 0 = down the gorge
// toward the glow (-Z), + = toward +X, i.e. right) and pitch (deg); yaw / pitch one value or one per knot
const heading = (path, yaw, pitch) => path.map((p, i) => {
  const y = (Array.isArray(yaw) ? yaw[i] : yaw) * D2R, e = (Array.isArray(pitch) ? pitch[i] : pitch) * D2R;
  const dx = Math.sin(y) * Math.cos(e), dz = -Math.cos(y) * Math.cos(e);
  return p.clone().add(V(dx * CY + dz * SY, Math.sin(e), -dx * SY + dz * CY).multiplyScalar(100));
});
// knot times for a path flown from t0 to t1 with speed keys v (m/s, one per knot): segment durations from the chord
// lengths at the mean of their end speeds, scaled to fit [t0, t1]
function paced(t0, t1, path, v) {
  const d = path.slice(1).map((p, i) => p.distanceTo(path[i]) / (0.5 * (v[i] + v[i + 1])));
  const k = (t1 - t0) / d.reduce((a, b) => a + b, 0);
  let t = t0;
  return [t0, ...d.map(x => (t += x * k))];
}

// Shots end at absolute times (s); hard cuts between them.
// the plunge: an accelerating run in over the front rim that noses over into the void, already falling on the drop
// (15.0) and crossing the deck plane at 15.3, then a dive down the slot under the ring that pulls out toward the glow
const PLUNGE_A = [ring(0, 34, 112), ring(0, 28, 84), ring(0, 23, 56), ring(0, 19, 32), ring(0, 13, 11), ring(0, 0, -3)];
const PLUNGE_B = [ring(0, -17, -17), ring(0.3, -35, -33), ring(1, -52, -53), ring(2.2, -66, -79), ring(4, -80, -110), ring(6.5, -90, -146)];
// the opening approach: a long descending, curving glide in from ~470 m ENE that settles into the hero orbit
const OPEN = [polar(62, 470, 88), polar(56, 390, 72), polar(50, 320, 58), polar(44, 265, 46), polar(37, 228, 38), polar(28, 214, 35), polar(19, 212, 33)];
// the finale: from close off the ring's NE flank a long rising, swinging pull-back to ~400 m NNE, ~150 m up
const FINALE = [polar(64, 118, 10), polar(58, 155, 22), polar(51, 205, 42), polar(45, 255, 66), polar(39, 305, 94), polar(33, 355, 124), polar(28, 400, 154)];
const FLYBY = arc(0, 0, 112, 128, 84, -6, 13, 5);
export const SHOTS = [
  // 1. OPEN (0-10, the grand build into the accent): one continuous take - a fast, descending, curving glide in from
  //    ~470 m ENE and ~90 m above the deck (ring ~21 % of the frame width) that brakes into the hero orbit ~212 m out
  //    (ring ~55 %) by the 6 s accent and keeps orbiting from ref 11's camera toward ref 7's; the pinnacles sweep
  //    against the far cloud sea and the Alps (parallax from the orbit and the descent)
  shot({ name: 'open', end: at(10), speed: [58, 50, 40, 29, 21, 19, 18], path: OPEN,
    aim: framing(OPEN, RC, [[0.6, 0.62], [0.58, 0.61], [0.55, 0.6], [0.53, 0.59], [0.52, 0.58], [0.5, 0.58], [0.47, 0.58]], [36, 30]), fov: [36, 30] }),
  // 2. STRUT (10-11, boom): a one-second whip under the ESE bridge's uplit rear strut pair, the soffit overhead and
  //    the blue gorge behind
  shot({ name: 'strut', end: at(11), speed: [16, 17, 16], drift: 0.2,
    path: arc(-54, -12, 23, 272, 312, -21, -19, 3),
    aim: rep(ring(-54, -14, -10), 3), fov: 62, check: { rot: 45 } }),
  // 3. GLAZE (11-12, boom): a one-second glide ~20 m off the front glazing slot (structure.js SLOTS: 36-144 deg),
  //    the diners inside, looking ahead along the facade
  shot({ name: 'glaze', end: at(12), speed: [17, 17, 17], drift: 0.15,
    path: arc(0, 0, 75, 70, 83, -2.5, -2, 3),
    aim: arc(0, 0, 55, 96, 109, -4.5, -4.5, 3), fov: 56, check: { rot: 25 } }),
  // 4. PLUNGE (12-18, one take across the drop): see PLUNGE_A / PLUNGE_B (paced to 19.0, cut at 18 low over the cloud
  //    bank, so the speeds hold to the cut); the gimbal looks down the gorge toward the
  //    glow throughout (pitch -22 -> -38 on the drop, the far rim's glazing across the top of the frame, then lifting
  //    ahead of the dive from the deck plane on -> -10): the slot floor and the cloud bank's dark well stay low
  // (r10: outcrop 0 here and in flyby / under / deck - the snow shoulder W of the ring passes ~100-400 m off the
  // camera, where the r9 p2 outcrop pieces (rock.js uLandAB2.w) read as camouflage blotches; the p1 outcrops instead)
  shot({ name: 'plunge', end: at(18), bank: 0.5, drift: 0.2, outcrop: 0,
    times: [...paced(12.0, 15.3, PLUNGE_A, [27, 31, 35, 37, 38, 40]), ...paced(15.3, 19.0, [PLUNGE_A[5], ...PLUNGE_B], [40, 42, 44, 45, 46, 46, 46]).slice(1)],
    path: [...PLUNGE_A, ...PLUNGE_B],
    aim: heading([...PLUNGE_A, ...PLUNGE_B], [0, 0, 0, 0, 0, 0, 0, 1, 2, 4, 6, 8], [-22, -27, -32, -36, -38.5, -37, -30, -23, -18, -14, -12, -10]),
    fov: [54, 62], check: { rot: 25 } }),
  // 5. FLYBY (18-21): a fast rising pass ~57 m off the ring's NE flank, the ESE pinnacle sliding by in the foreground,
  //    crossing the deck plane
  shot({ name: 'flyby', end: at(21), speed: [31, 32, 32, 32, 31], drift: 0.3, outcrop: 0,
    path: FLYBY, aim: framing(FLYBY, RC, [[0.38, 0.56], [0.42, 0.56], [0.47, 0.55], [0.52, 0.55], [0.56, 0.54]], 50), fov: 50, check: { rot: 25 } }),
  // 6. UNDER (21-24, one FPV take between the hits): in under the front rim, under the ring along the gorge axis (the
  //    soffit and the void overhead, the strut pairs to both sides), out under the far rim toward the cloud sea and the
  //    glow, starting to bank right and descend
  shot({ name: 'under', end: at(24), speed: [40, 42, 44, 46, 47], bank: 0.35, drift: 0.25, look: 0.75, tilt: 6, outcrop: 0,
    path: [ring(0, -24.5, 55), ring(0, -27, 24), ring(0.5, -29, -8), ring(2.5, -33, -40), ring(5.5, -39, -70)],
    aim: ring(60, -40, -1000), fov: 66, check: { rot: 45 } }),
  // 7. GLAZE2 (24-27): a glide ~20 m off the front glazing slot the other way (toward the WNW bridge), the facade's
  //    curve leading in
  shot({ name: 'glaze2', end: at(27), speed: [25, 24, 23], drift: 0.15,
    path: arc(0, 0, 75, 122, 68, -0.5, -3, 5),
    aim: arc(0, 0, 55, 96, 42, -4.5, -4.5, 5), fov: 56, check: { rot: 25 } }),
  // 8. STRUT2 (27-28, the phrase): the one-second whip answered on the WNW bridge's strut pair - wider, swinging the
  //    other way and sinking under the soffit
  shot({ name: 'strut2', end: at(28), speed: [18, 19, 18], drift: 0.2,
    path: arc(54, -12, 30, 236, 272, -15, -22, 3),
    aim: rep(ring(54, -14, -10), 3), fov: 62, check: { rot: 45 } }),
  // 9. SOFFIT (28-30): a rising lateral glide ~27 m off and ~15 -> 7 m below the front rim, looking up under the lit
  //    glazing and soffit into the slot and the glow beyond (ref 3's angle)
  shot({ name: 'soffit', end: at(30), speed: [27, 28, 28], drift: 0.2,
    path: arc(0, 0, 82, 117, 77, -24, -16, 3), aim: rep(ring(0, -12, -20), 3), fov: 60, check: { rot: 25 } }),
  // 10. DECK (30-33): FPV low over the roof deck (~8 m) from the front rim straight across the void and the far arc
  //    toward the glow - the terrace and the void's cloud well below, the Alps ahead (refs 1 / 10)
  shot({ name: 'deck', end: at(33), speed: [30, 29, 28], bank: 0.6, drift: 0.2, look: 0.5, tilt: -13, outcrop: 0,
    path: [ring(-10, 8, 62), ring(-4, 7, 32), ring(2, 7.5, 2), ring(6, 9, -24)],
    aim: rep(ring(10, -40, -520), 4), fov: 60, check: { rot: 20 } }),
  // 11. FINALE (33-45, the final statement and the ring-out): one take from close off the ring's NE flank: a long
  //    rising, swinging pull-back (still ~30 m/s at the fade) to ~400 m NNE, ~150 m up, looking down ~-16 deg past the
  //    ring into the gorge and the valley; the ring ends ~18 % of the frame; fade to black
  shot({ name: 'finale', end: 45.0, times: [33.0, 35.0, 37.15, 39.0, 41.0, 43.0, 45.0], path: FINALE,
    aim: framing(FINALE, RC, [[0.56, 0.56], [0.54, 0.58], [0.52, 0.6], [0.51, 0.61], [0.5, 0.62], [0.5, 0.62], [0.5, 0.62]], [40, 44]), fov: [40, 44] }),
];
let acc0 = 0;
for (const s of SHOTS) {
  s.start = acc0; s.dur = s.end - acc0; acc0 = s.end;
  if (s.times) { s.S = timed(s); s.scale = 1; } else s.scale = s.len / (s.S.mean * s.dur);
}
export const TOTAL = acc0;

// position and aim direction of shot s at shot-local time fraction x (0..1)
const _a = V(0, 0, 0), _b = V(0, 0, 0);
function frame(s, x) {
  const u = s.S(x), tau = s.curve.getUtoTmapping(u);
  const pos = s.curve.getPoint(tau);
  // flight direction (central difference over +-8 m along the path: smooths the curvature steps at the knots)
  const e = 8 / s.len;
  s.curve.getPoint(s.curve.getUtoTmapping(Math.min(1, u + e)), _a);
  s.curve.getPoint(s.curve.getUtoTmapping(Math.max(0, u - e)), _b);
  const fly = _a.clone().sub(_b);
  if (fly.lengthSq() < 1e-8) fly.set(0, 0, -1); else fly.normalize();
  if (s.tilt) { const h = Math.hypot(fly.x, fly.z) || 1e-6, p = Math.atan2(fly.y, h) + s.tilt * D2R; fly.set(fly.x / h * Math.cos(p), Math.sin(p), fly.z / h * Math.cos(p)); }
  let tgt = s.aimCurve ? s.aimCurve.getPoint(tau) : s.aim ? (Array.isArray(s.aim) ? s.aim[0] : s.aim).clone() : null;
  const look = s.lookKeys ? keyAt(s.lookKeys, tau) : tgt ? s.look : 1;
  const dir = tgt ? tgt.clone().sub(pos).normalize() : fly.clone();
  if (look > 0) dir.lerp(fly, look).normalize();
  return { pos, dir };
}

// deterministic drift / buffeting: a few incommensurate sines (world-stable in time, no per-frame noise)
const wob = (t, f, ph) => Math.sin(t * f + ph) * 0.6 + Math.sin(t * f * 2.31 + ph * 1.7) * 0.3 + Math.sin(t * f * 5.13 + ph * 2.9) * 0.1;

export function cameraAt(t) {
  let s = SHOTS[SHOTS.length - 1];
  for (const x of SHOTS) if (t < x.end) { s = x; break; }
  const lt = sat((t - s.start) / s.dur);
  const { pos, dir } = frame(s, lt);
  // roll: coordinated-turn bank, atan(lateral acceleration / g), from second differences of the path over +-0.25 s;
  // the lateral axis is up x v / |v|, so the bank fades out in a vertical dive (no heading to bank about)
  // (averaged over five instants 0.2 s apart: the path is only C1 at its knots, and the bank must build smoothly)
  let roll = 0;
  if (s.bank) for (const o of [-0.4, -0.2, 0, 0.2, 0.4]) {
    // (the stencil stays inside the shot: near its ends it holds the bank of 0.35 s in, no clamped-difference spike)
    const h = 0.35, x = Math.min(1 - h / s.dur, Math.max(h / s.dur, lt + o / s.dur)), p0 = frame(s, x).pos, pa = frame(s, x - h / s.dur).pos, pb = frame(s, x + h / s.dur).pos;
    const vel = pb.clone().sub(pa).multiplyScalar(0.5 / h);
    const acc = pb.clone().add(pa).addScaledVector(p0, -2).multiplyScalar(1 / (h * h));
    const sp = vel.length();
    if (sp > 0.5) roll += s.bank * Math.atan((acc.x * vel.z - acc.z * vel.x) / sp / GRAV) / 5;   // acc . (up x v) / |v|
  }
  roll = ROLL_MAX * Math.tanh(roll / ROLL_MAX);   // soft limit
  // drift: position wander + aim buffeting (FPV shots shake a little faster)
  const a = s.drift, fq = s.bank ? 2.2 : 0.7;
  pos.x += a * wob(t, 0.9, 1.3); pos.y += a * 0.6 * wob(t, 1.1, 4.1); pos.z += a * wob(t, 0.8, 2.7);
  const tgt = pos.clone().addScaledVector(dir, 100);
  tgt.x += a * 0.18 * wob(t, fq, 0.4); tgt.y += a * 0.15 * wob(t, fq * 1.13, 3.3); tgt.z += a * 0.18 * wob(t, fq * 0.93, 5.2);
  roll += a * 0.004 * wob(t, fq * 0.8, 2.2) * (s.bank ? 3 : 1);
  const fov = Array.isArray(s.fov) ? s.fov[0] + (s.fov[1] - s.fov[0]) * smooth(lt) : s.fov;
  const fade = Math.min(1, t / 0.6, Math.max(0, (TOTAL - t) / 1.8));
  return { pos, tgt, fov, roll, dip: s.dip, sky: s.sky, outcrop: s.outcrop, fade, shot: s.name, local: lt };
}
