// The ring restaurant: concrete annulus, glazing, interior, bridges, pavilions, struts, LEDs.
// Built in the ring frame (bridges +/-X, front +Z, y=0 = roof deck top) and rotated into the world
// so that front faces east (+X world) and the bridges run north/south.
import * as THREE from 'three';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';
import { DECK_Y, ringYaw } from './config.js';
import { VERT, CONCRETE_FRAG, EMISSIVE_FRAG, GLASS_FRAG, STEEL_FRAG, INTERIOR_FRAG } from './glsl/structure.js';
import { LAMPS_MAX } from './terrain.js';
import { cameraAt, TOTAL } from './timeline.js';
import { VIEWS, refToWorld } from './views.js';
import { loadTex } from './tex.js';

const TAU = Math.PI * 2, D2R = Math.PI / 180;
// outer glazed slot (deg from +X toward the front), lens-shaped (refs 4 / 11): full height only between
// a0 + SLOT_TAPER and a1 - SLOT_TAPER, the sill curving up to a point at a0 / a1 under a straight head.
// Keep in sync with SLOT_A0 / SLOT_A1 / SLOT_TAPER in glsl.
const SLOTS = [[36, 144]];
const SLOT_TAPER = 16;
const SLOT_NM = 32;   // mullion bays across the slot (3.2 m at r 54.4, refs 4 / 7 / 11 at 100%; = SLOT_NM in glsl)
// refs 3 / 4 / 7: a thin fascia over the glass (~0.8 m) and a low sill upstand, the lower wall + fillet below
const Y_SLOT_TOP = -0.8, Y_SLOT_BOT = -7.0;
// sill height of the slot at angle d (deg); Y_SLOT_TOP (zero height) outside it
function slotSill(d) {
  const [a0, a1] = SLOTS[0], e = Math.min(d - a0, a1 - d);
  if (e <= 0) return Y_SLOT_TOP;
  const f = Math.min(1, e / SLOT_TAPER), k = 1 - (1 - f) * (1 - f);
  return Y_SLOT_TOP - (Y_SLOT_TOP - Y_SLOT_BOT) * k;
}
const R_SPINE = 51.6;           // restaurant spine wall (lounge side faces the terrace, slat side faces the slot)
const lin = hex => new THREE.Color(hex);   // r187: Color('#hex') is already linear
const R_CAN = 44.4;            // canopy / roof inner edge: 2.6 m deep overhang over the terrace (ref 1)
const Y_CAN = -1.9;            // canopy soffit = inner glazing head (5.4 m glazing under a 1.9 m fascia; keep = Y_CANOPY in glsl)
const Y_CEIL = -0.8;           // restaurant ceiling (= outer slot head; keep = Y_CEIL in glsl)
const v3 = c => new THREE.Vector3(c.r, c.g, c.b);

// ---------------------------------------------------------------- geometry helpers
function revolve(prof, nrm, th0 = 0, th1 = TAU, segs = 720) {
  const n = prof.length, pos = [], nor = [], uv = [], idx = [];
  for (let i = 0; i <= segs; i++) {
    const t = th0 + (th1 - th0) * i / segs, c = Math.cos(t), s = Math.sin(t);
    for (let j = 0; j < n; j++) {
      const [r, y] = prof[j], [nr, ny] = nrm[j];
      pos.push(r * c, y, r * s); nor.push(nr * c, ny, nr * s); uv.push(i / segs, j / (n - 1));
    }
  }
  for (let i = 0; i < segs; i++) for (let j = 0; j < n - 1; j++) {
    const a = i * n + j, b = a + 1, c = a + n, d = c + 1;
    idx.push(a, b, c, b, d, c);
  }
  return finish(pos, nor, uv, idx);
}
function finish(pos, nor, uv, idx) {
  // make winding agree with the supplied normals
  const P = i => new THREE.Vector3(pos[i * 3], pos[i * 3 + 1], pos[i * 3 + 2]);
  for (let t = 0; t < idx.length; t += 3) {
    const a = P(idx[t]), b = P(idx[t + 1]), c = P(idx[t + 2]);
    const gn = b.clone().sub(a).cross(c.clone().sub(a));
    if (gn.lengthSq() < 1e-12) continue;
    const k = idx[t];
    const sn = new THREE.Vector3(nor[k * 3], nor[k * 3 + 1], nor[k * 3 + 2]);
    if (gn.dot(sn) < 0) { const tmp = idx[t + 1]; idx[t + 1] = idx[t + 2]; idx[t + 2] = tmp; }
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  g.setAttribute('normal', new THREE.Float32BufferAttribute(nor, 3));
  g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2));
  g.setIndex(idx);
  return g;
}
const flatH = (r0, r1, y, up) => revolve([[r0, y], [r1, y]], [[0, up ? 1 : -1], [0, up ? 1 : -1]]);
const cyl = (r, y0, y1, out, th0, th1, segs) => revolve([[r, y0], [r, y1]], [[out ? 1 : -1, 0], [out ? 1 : -1, 0]], th0, th1, segs);
function arc(cr, cy, rad, a0, a1, n = 12) {
  const p = [], q = [];
  for (let i = 0; i <= n; i++) { const a = a0 + (a1 - a0) * i / n; p.push([cr + rad * Math.cos(a), cy + rad * Math.sin(a)]); q.push([Math.cos(a), Math.sin(a)]); }
  return [p, q];
}
function box(w, h, d) { return new THREE.BoxGeometry(w, h, d); }
// place a geometry at ring polar coords: theta (rad), radius, y; local +x = radial, +z = tangential
function polarMatrix(th, r, y, sx = 1, sy = 1, sz = 1, extraRotY = 0) {
  const m = new THREE.Matrix4();
  const q = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 1, 0), -th + extraRotY);
  m.compose(new THREE.Vector3(r * Math.cos(th), y, r * Math.sin(th)), q, new THREE.Vector3(sx, sy, sz));
  return m;
}
function instanced(geo, mat, mats, cols) {
  const im = new THREE.InstancedMesh(geo, mat, mats.length);
  mats.forEach((m, i) => im.setMatrixAt(i, m));
  if (cols) cols.forEach((c, i) => im.setColorAt(i, c));
  im.instanceMatrix.needsUpdate = true;
  im.frustumCulled = false;
  return im;
}
// tube between two points
function tubeMatrix(a, b, radius) {
  const d = b.clone().sub(a), len = d.length();
  const q = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 1, 0), d.clone().normalize());
  return new THREE.Matrix4().compose(a.clone().add(b).multiplyScalar(0.5), q, new THREE.Vector3(radius, len, radius));
}
function rounded(outline, n) { return outline; }

// Every film camera (cameraAt sampled each 0.1 s) and every reference camera, in the ring frame. Figures are
// simple stand-ins: up close they read as mannequins, so any that comes near a camera is left out.
function cameraSamples(ringInv) {
  const out = [];
  const push = (p, fov) => out.push({ p: p.clone().applyMatrix4(ringInv), k: 1080 / (2 * Math.tan(fov * D2R / 2)) });
  for (let i = 0; i <= Math.round(TOTAL * 10); i++) { const c = cameraAt(i / 10); push(c.pos, c.fov); }
  for (const v of Object.values(VIEWS)) push(refToWorld(v.pos), v.fov);
  return out;
}
// true if a 1.75 m figure at ring-frame point p comes within minD of a camera or would stand taller than
// maxPx (1080p frame) in it
function nearCamera(cams, p, minD, maxPx = 1e9) {
  for (const c of cams) {
    const d = c.p.distanceTo(p);
    if (d < minD || 1.75 / d * c.k > maxPx) return true;
  }
  return false;
}
const posOf = m => new THREE.Vector3().setFromMatrixPosition(m);

// rounded-rectangle outline in (s, y) with corner radii (top, bottom) -> list of [s, y]
function roundRectOutline(s0, s1, y0, y1, rt, rb, n = 10) {
  const pts = [];
  const corner = (cx, cy, r, a0, a1) => { for (let i = 0; i <= n; i++) { const a = a0 + (a1 - a0) * i / n; pts.push([cx + r * Math.cos(a), cy + r * Math.sin(a)]); } };
  corner(s1 - rt, y1 - rt, rt, 0, Math.PI / 2);
  corner(s0 + rt, y1 - rt, rt, Math.PI / 2, Math.PI);
  corner(s0 + rb, y0 + rb, rb, Math.PI, 1.5 * Math.PI);
  corner(s1 - rb, y0 + rb, rb, 1.5 * Math.PI, 2 * Math.PI);
  return pts;
}
// reveal (return surface) of an opening: outline at r0 extruded to r1, theta = s / R0
function revealGeometry(outline, R0, r0, r1) {
  const pos = [], nor = [], uv = [], idx = [];
  const n = outline.length;
  // centroid for inward normal
  let cs = 0, cy = 0; outline.forEach(([s, y]) => { cs += s; cy += y; }); cs /= n; cy /= n;
  for (let i = 0; i <= n; i++) {
    const [s, y] = outline[i % n];
    const th = s / R0, c = Math.cos(th), si = Math.sin(th);
    // inward normal in (s,y) plane -> towards opening centre
    const [sp, yp] = outline[(i + 1) % n], [sm, ym] = outline[(i - 1 + n) % n];
    let ts = sp - sm, ty = yp - ym; const tl = Math.hypot(ts, ty); ts /= tl; ty /= tl;
    let ns = -ty, ny = ts;
    if (ns * (cs - s) + ny * (cy - y) < 0) { ns = -ns; ny = -ny; }
    // tangential direction in xz for s
    const tx = -si, tz = c;
    for (const r of [r0, r1]) {
      pos.push(r * c, y, r * si);
      nor.push(tx * ns, ny, tz * ns);
      uv.push(i / n, r === r0 ? 0 : 1);
    }
  }
  for (let i = 0; i < n; i++) { const a = i * 2, b = a + 1, c = a + 2, d = a + 3; idx.push(a, b, c, b, d, c); }
  return finish(pos, nor, uv, idx);
}

// photographic cast concrete (Poly Haven concrete_wall_006, CC0, 2k): diffuse + normal map for CONCRETE_FRAG.
// Without the files the ring falls back to the procedural concrete (uConcOn 0).
async function loadConcrete() {
  try {
    const t = await loadTex('concrete_wall_006', ['diff', 'nor']);
    return { tConcD: { value: t.diff }, tConcN: { value: t.nor }, uConcOn: { value: 1 } };
  } catch (e) {
    console.warn('concrete maps', e);
    const px = (r, g, b) => { const d = new THREE.DataTexture(new Uint8Array([r, g, b, 255]), 1, 1); d.needsUpdate = true; return d; };
    return { tConcD: { value: px(128, 128, 128) }, tConcN: { value: px(128, 128, 255) }, uConcOn: { value: 0 } };
  }
}

// ---------------------------------------------------------------- materials
function makeMaterials(shared, ringInv, concMaps) {
  const U = {
    ...shared.uniforms,
    ...concMaps,
    uWarm: { value: new THREE.Vector3(1.0, 0.56, 0.24) },
    uInteriorCol: { value: new THREE.Vector3(1.0, 0.60, 0.30) },   // amber (refs 4/7: far band #d79a5a..#f2c48a)
    uLedI: { value: 2.6 },
    uGlazeI: { value: 1.25 },
    uDownI: { value: 1.6 },
    uRingInv: { value: ringInv },
  };
  shared.ringUniforms = U;
  const mk = (frag, extra = {}, defines = {}, opts = {}) => new THREE.ShaderMaterial({
    vertexShader: VERT, fragmentShader: frag, uniforms: { ...U, ...extra }, defines, ...opts,
  });
  const concrete = (surf, alb = '#989285', ao = 1, defs = {}) => mk(CONCRETE_FRAG, { uAlbedo: { value: v3(lin(alb)) }, uAO: { value: ao } }, { SURF: surf, ...defs });
  const emissive = (rgb, k, defs = {}) => mk(EMISSIVE_FRAG, { uEmit: { value: new THREE.Vector3(...rgb).multiplyScalar(k) } }, defs);
  const glass = (f0, tint, defines = {}, edge = 0, fmax = 1) => mk(GLASS_FRAG, { uF0: { value: f0 }, uTint: { value: tint }, uEdgeGlow: { value: edge }, uRailH: { value: 1.1 }, uFmax: { value: fmax } }, defines,
    { transparent: true, depthWrite: false, side: THREE.DoubleSide, blending: THREE.CustomBlending, blendSrc: THREE.OneFactor, blendDst: THREE.OneMinusSrcAlphaFactor });
  const steel = (tint, rough, defines = {}) => mk(STEEL_FRAG, { uTint: { value: new THREE.Vector3(...tint) }, uRough: { value: rough } }, defines);
  const interior = (alb, pattern = 0, emis = 0, defines = {}) => mk(INTERIOR_FRAG, { uAlbedo: { value: v3(lin(alb)) }, uPattern: { value: pattern }, uEmissive: { value: emis } }, defines);
  return { U, concrete, emissive, glass, steel, interior };
}

// ---------------------------------------------------------------- build
export async function createStructure(shared, terrain) {
  const root = new THREE.Group();
  root.name = 'structure';
  root.position.set(0, DECK_Y, 0);
  root.rotation.y = ringYaw();
  root.updateMatrixWorld(true);
  const ringInv = root.matrixWorld.clone().invert();
  const M = makeMaterials(shared, ringInv, await loadConcrete());
  const add = (geo, mat, name) => { const m = new THREE.Mesh(geo, mat); m.name = name || ''; m.frustumCulled = false; root.add(m); return m; };

  const conc = M.concrete(0);
  // refs 4 / 5 / 7 / 11: pale, calm concrete on the deck, the outer wall and the inner fascia
  const roofMat = M.concrete(1, '#d2ccc2');   // (paler diffuse, weaker grazing sheen: ref 8 top-down deck L51)
  const wallMat = M.concrete(2, '#a39d91');
  const soffitMat = M.concrete(3, '#8d867a');
  // pale grey polished stone (ref 1): lit mostly by reflections, the diffuse glazing wash / downlight pools kept low
  const terrazzo = M.concrete(4, '#85878b', 1, { GLAZE_K: 0.35, DOWN_K: 0.22 });   // (soft warm glow at the glazing base)
  const fascia = M.concrete(5, '#a39d91');
  const canopyMat = M.concrete(6, '#81786a', 0.5);   // ref 1 soffit L39
  const led = M.emissive([1.0, 0.62, 0.30], 14);
  const ledSoft = M.emissive([1.0, 0.60, 0.28], 7);
  // ring LED lines dim with distance (FAR_DIM at > 90 m): up close they read as crisp strips (ref 1), from the
  // drone views the refs show a soft warm line under the people, never a neon outline (refs 4 / 7 / 8 / 11)
  const ledTerr = M.emissive([1.0, 0.62, 0.30], 14, { FAR_DIM: 0.3 });
  const ledRoof = M.emissive([1.0, 0.60, 0.28], 6, { FAR_DIM: 0.45 });
  const glassIn = M.glass(0.05, 0.03, {}, 0, 0.45);
  // outer slot glass: low reflectance so the lit room, not the sky, sets the band (refs 4 / 7: p10 ~16)
  const glassOut = M.glass(0.04, 0.03, { SLOT_MASK: 1 }, 0, 0.45);   // (the oblique ends of the band mirror the sky)
  const railGlass = M.glass(0.06, 0.03, { RAIL: 1 }, 0.7);
  const railGlassRoof = M.glass(0.06, 0.03, { RAIL: 1 }, 0.3);
  const stainless = M.steel([0.62, 0.60, 0.58], 0.18);
  const bronze = M.steel([0.09, 0.075, 0.06], 0.3);
  const mullionMat = M.steel([0.045, 0.042, 0.04], 0.35);   // near-black anodised (#161c2a in the refs)
  const capRail = M.steel([0.55, 0.50, 0.42], 0.25);
  const capBronze = M.steel([0.26, 0.19, 0.12], 0.2);   // balustrade cap rails (ref 1: dark bronze)
  const strutSteel = M.steel([0.40, 0.39, 0.40], 0.16, { STRUT: 1 });   // dark satin struts: soft mirror of sky + rock

  // ---------------- ring body
  add(flatH(R_CAN, 55.0, 0, true), roofMat, 'roof');
  add(cyl(55.0, -7.8, 0, true), wallMat, 'outerWall');
  {
    const [p, q] = arc(53.5, -7.8, 1.5, 0, -Math.PI / 2, 16);
    add(revolve(p, q), soffitMat, 'fillet');
  }
  add(flatH(42.85, 53.5, -9.3, false), soffitMat, 'soffit');
  {
    const [p, q] = arc(42.85, -9.05, 0.25, -Math.PI / 2, -Math.PI, 6);
    add(revolve(p, q), soffitMat, 'innerRound');
  }
  add(cyl(42.6, -9.05, -7.15, false), fascia, 'lowerFascia');
  // balustrade shoe: a slim dark bronze channel (ref 1), not a lit concrete upstand
  add(flatH(42.6, 42.95, -7.15, true), bronze, 'upstandTop');
  add(cyl(42.95, -7.3, -7.15, true), bronze, 'upstandIn');
  add(flatH(42.95, 47.0, -7.3, true), terrazzo, 'terrace');
  add(flatH(R_CAN, 47.15, Y_CAN, false), canopyMat, 'canopySoffit');
  add(cyl(R_CAN, Y_CAN, 0, false), fascia, 'canopyFascia');
  // top edge lips
  add(flatH(R_CAN - 0.05, R_CAN + 0.05, 0.0, true), fascia);

  // LED lines (thin emissive rings)
  const ledRing = (r, y, w, h, mat) => {
    const g = revolve([[r - w / 2, y], [r + w / 2, y], [r + w / 2, y + h], [r - w / 2, y + h]], [[0, -1], [1, 0], [0, 1], [-1, 0]].map(n => n), 0, TAU, 720);
    return add(g, mat || led);
  };
  ledRing(42.72, -9.40, 0.10, 0.06, M.emissive([1.0, 0.62, 0.30], 14, { FAR_DIM: 0.5 }));   // soffit inner edge reveal (ref 3)
  ledRing(46.92, -7.30, 0.06, 0.035, ledTerr);       // terrace glazing base
  ledRing(43.00, -7.15, 0.05, 0.03, ledTerr);        // balustrade base
  ledRing(R_CAN + 0.22, 0.0, 0.05, 0.03, ledRoof);   // roof balustrade base (refs: people against a soft glow, not a line)
  // outer face / fillet line: a faint warm line under the slot's full-height run only (ref 7 #775541; refs 4 / 11
  // show a dark underside elsewhere)
  add(cyl(55.03, -8.0, -7.86, true, (SLOTS[0][0] + 12) * D2R, (SLOTS[0][1] - 12) * D2R, 160), M.emissive([1.0, 0.60, 0.30], 0.35), 'outerLed');

  // ---------------- outer wall openings: reveals + glazing + interior wall
  // lens outline in (arc metres at R 55, y), densely sampled along both edges (the reveal is built from straight
  // segments between outline points: a long straight edge would cut a chord through the ring)
  const slotOutlines = [];
  for (const [a0, a1] of SLOTS) {
    const o = [], n = 160;
    for (let i = 0; i <= n; i++) { const d = a1 - (a1 - a0) * i / n; o.push([d * D2R * 55, Y_SLOT_TOP]); }
    for (let i = 1; i < n; i++) { const d = a0 + (a1 - a0) * i / n; o.push([d * D2R * 55, slotSill(d)]); }
    slotOutlines.push(o);
  }
  const portalOutlines = [];
  for (const c of [0, 180]) {
    const sc = c * D2R * 55;
    portalOutlines.push(roundRectOutline(sc - 4, sc + 4, -5.4, -0.6, 1.2, 0.25, 8));
  }
  const revealMat = M.concrete(11, '#989285');   // (ring-polar mapping of the photo concrete)
  for (const o of slotOutlines) add(revealGeometry(o, 55, 55.0, 54.4), revealMat, 'slotReveal');
  for (const o of portalOutlines) add(revealGeometry(o, 55, 55.0, 53.6), revealMat, 'portalReveal');
  // slot glass + mullions (SLOT_NM bays of 3.2 m: refs 4 / 7 / 11 show a crisp dark rhythm of wide bays): slim
  // near-black fins (0.07 x 0.12 m) standing just proud of the glass; the glass shader draws them >= 1 px wide far away
  for (const [a0, a1] of SLOTS) {
    add(cyl(54.4, Y_SLOT_BOT, Y_SLOT_TOP, true, a0 * D2R - 0.02, a1 * D2R + 0.02, 200), glassOut, 'slotGlass');
  }
  {
    const mats = [];
    for (const [a0, a1] of SLOTS) {
      for (let i = 1; i < SLOT_NM; i++) {
        const d = a0 + (a1 - a0) * i / SLOT_NM, th = d * D2R, ys = slotSill(d), hm = Y_SLOT_TOP - ys;
        if (hm > 0.25) mats.push(polarMatrix(th, 54.3, (Y_SLOT_TOP + ys) / 2, 0.24, hm, 0.075));   // (structural fins 0.24 deep)
      }
    }
    root.add(instanced(box(1, 1, 1), mullionMat, mats));
  }
  // faint sill line along the full-height run of the slot
  for (const [a0, a1] of SLOTS) add(cyl(54.75, Y_SLOT_BOT - 0.02, Y_SLOT_BOT + 0.04, true, (a0 + SLOT_TAPER) * D2R, (a1 - SLOT_TAPER) * D2R, 160), M.emissive([1.0, 0.60, 0.28], 0.6), 'sillLed');
  // portal glow (recessed, warm lit back face)
  for (const c of [0, 180]) {
    const g = cyl(53.62, -5.4, -0.6, true, (c - 4.1) * D2R, (c + 4.1) * D2R, 16);
    add(g, M.interior('#e6dccb', 5), 'portalBack');
  }

  // ---------------- inner glazing + fins + mullions
  // low-iron, coated: the restaurant reads through it along the terrace (ref 1); MULLIONS keeps the 1.5 m
  // bronze rhythm visible on the far arc (ref 4) where the real 70 mm mullions are sub-pixel
  add(cyl(47.0, -7.3, Y_CAN, false, 0, TAU, 720), M.glass(0.04, 0.02, { MULLIONS: 1 }, 0, 0.09), 'innerGlass');   // (low cap: no orange horizon band across the glazing in view 1)
  {
    const mats = [], yc = (Y_CAN - 7.3) / 2, hg = Y_CAN + 7.3;
    const n = Math.round(TAU * 47 / 3.0);   // (pass 2: 3.0 m bays, ref 1 at 100% ~70 px apart near the camera; = 98 in GLASS_FRAG)
    for (let i = 0; i < n; i++) mats.push(polarMatrix(i / n * TAU, 47.03, yc, 0.07, hg, 0.05));
    root.add(instanced(box(1, 1, 1), mullionMat, mats));   // (ref 1: slim near-black mullions, not sky-lit bars)
    // slim dark bronze piers at the 12 joints (the far band in refs 4 / 7 shows dark piers, not pale pilasters)
    const fins = [];
    for (let k = 0; k < 12; k++) fins.push(polarMatrix((15 + 30 * k) * D2R, 47.1, yc, 0.7, hg, 0.45));
    root.add(instanced(box(1, 1, 1), bronze, fins));
    // roof joints: cover strip proud of the deck (stainless)
    const j = [];
    for (let k = 0; k < 12; k++) j.push(polarMatrix((15 + 30 * k) * D2R, (R_CAN + 55) / 2, 0.005, 55 - R_CAN, 0.01, 0.12));
    root.add(instanced(box(1, 1, 1), capRail, j));
  }

  // ---------------- balustrades (terrace r 42.8, roof r 45.9)
  // arcs: [[th0, th1], ...] in rad (default the full circle)
  const balustrade = (r, y, h, postStep, glassMat = railGlass, arcs = [[0, TAU]]) => {
    const posts = [];
    for (const [t0, t1] of arcs) {
      const sg = Math.max(8, Math.round(720 * (t1 - t0) / TAU));
      add(cyl(r, y, y + h, false, t0, t1, sg), glassMat, 'railGlass');
      const n = Math.round((t1 - t0) * r / postStep), full = t1 - t0 > TAU - 1e-6;
      for (let i = 0; i < (full ? n : n + 1); i++) posts.push(polarMatrix(t0 + (t1 - t0) * i / n, r, y + h / 2, 0.05, h, 0.04));
      // slim rectangular dark-bronze cap rail clamped over the glass edge (ref 1 at 100%: ~45 x 40 mm with one warm
      // specular line, not a fat tube mirroring the sky); hard-edged profile
      const c0 = r - 0.024, c1 = r + 0.024, y0 = y + h - 0.025, y1 = y + h + 0.018;
      add(revolve([[c0, y0], [c1, y0], [c1, y0], [c1, y1], [c1, y1], [c0, y1], [c0, y1], [c0, y0]],
        [[0, -1], [0, -1], [1, 0], [1, 0], [0, 1], [0, 1], [-1, 0], [-1, 0]], t0, t1, sg), capBronze, 'capRail');
    }
    root.add(instanced(box(1, 1, 1), bronze, posts));
  };
  balustrade(42.8, -7.15, 1.1, 1.8);
  balustrade(R_CAN + 0.1, 0.0, 1.1, 3.0, railGlassRoof);
  // outer roof edge: glass balustrade with a slim cap rail (refs 3 / 7: guests lean on it against the sky), no LED
  // glow in the glass (no warm outline around the ring from the drones)
  // (open over the bridge roofs at 0 / 180 deg)
  const gap = 4.2 / 54.75;
  balustrade(54.75, 0.0, 1.1, 3.0, M.glass(0.06, 0.03, {}, 0, 0.5), [[gap, Math.PI - gap], [Math.PI + gap, TAU - gap]]);

  // ---------------- interior
  const cams = cameraSamples(ringInv);
  buildInterior(root, M, add, cams);
  buildPeople(root, M, cams);

  // ---------------- bridges + pavilions + struts
  const lamps = [];
  const H = ringHeight(root, terrain);
  for (const side of [1, -1]) buildBridge(root, M, add, side, lamps, { H, conc, roofMat, fascia, glassIn, railGlass, railGlassRoof, bronze, capRail, led, ledSoft, stainless, terrazzo, strutSteel });
  try { buildPath(root, M, add, terrain, lamps, { conc, railGlass, bronze, stainless, led }); } catch (e) { console.warn('path', e); }

  // ---------------- lamps -> shared uniforms (world space)
  const LP = shared.uniforms.uLampPos.value, LC = shared.uniforms.uLampCol.value;
  lamps.slice(0, LAMPS_MAX).forEach((l, i) => {
    const w = l.p.clone().applyMatrix4(root.matrixWorld);
    LP[i].set(w.x, w.y, w.z, l.r);
    LC[i].set(l.c[0] * l.i, l.c[1] * l.i, l.c[2] * l.i, 0);
  });
  shared.uniforms.uLampCount.value = Math.min(LAMPS_MAX, lamps.length);
  root.userData.lamps = lamps;
  return root;
}

// ---------------------------------------------------------------- interior
function buildInterior(root, M, add, cams) {
  // Restaurant storey (floor -7.3, ceiling Y_CEIL -0.8) between the inner glazing (47.0) and the outer wall (54.4).
  // A spine wall at R_SPINE splits it: lounge + window tables facing the terrace; along the outer slot a
  // dining gallery (banquette against the spine, clothed tables with lamps, chairs and guests at the glass).
  // The spine stops the eye passing straight through to the void.
  // warm amber palette: the far band across the void reads #d79a5a..#f2c48a in refs 4 / 7, not cream
  const floor = M.interior('#9a7252', 2);
  const ceil = M.interior('#e2c9a4', 1);
  const cream = M.interior('#d6b88f');
  const plaster = M.interior('#d8bc96', 5);
  const gallery = M.interior('#c6a277', 6);
  const wallIn = M.interior('#c9a983', 5, 0, { OPENING_DISCARD: 1 });
  add(flatH(47.0, 54.4, -7.3, true), floor, 'intFloor');
  add(flatH(47.0, 54.4, Y_CEIL, false), ceil, 'intCeil');
  add(cyl(47.1, Y_CAN, Y_CEIL, true), cream, 'bulkhead');
  add(cyl(54.38, -7.3, Y_CEIL, false, 0, TAU, 720), wallIn, 'intWall');
  for (const [a0, a1] of [[4, 176], [184, 356]]) {
    add(cyl(R_SPINE - 0.15, -7.3, Y_CEIL, false, a0 * D2R, a1 * D2R, 360), plaster, 'spineIn');
    add(cyl(R_SPINE + 0.15, -7.3, Y_CEIL, true, a0 * D2R, a1 * D2R, 360), gallery, 'spineOut');
  }

  const rnd = mulberry(7);
  const deg = th => ((th / D2R) % 360 + 360) % 360;
  const isSlot = th => { const d = deg(th); return SLOTS.some(([a0, a1]) => d > a0 + 6 && d < a1 - 6); };
  const nearJoint = (th, tol, r = 47) => { const m = Math.abs(((deg(th) - 15) % 30 + 30) % 30 - 15); return 15 - m < tol / r / D2R; };
  const nearPortal = th => { const d = deg(th); return d < 9 || d > 351 || Math.abs(d - 180) < 9; };

  // partition walls at the 12 joints (art on both faces), lounge side only: on the slot side they stood right
  // behind the outer glass and read as pale pilasters across the lit facade band (refs 4 / 7 show none)
  const parts = [], arts = [];
  for (let k = 0; k < 12; k++) {
    const th = (15 + 30 * k) * D2R;
    parts.push(polarMatrix(th, (47.15 + R_SPINE) / 2, (Y_CEIL - 7.25) / 2, R_SPINE - 47.15, Y_CEIL + 7.25, 0.3));
    for (const sgn of [1, -1]) {
      const m = polarMatrix(th + sgn * 0.17 / 50, 49.6, -4.4, 1.4, 1.1, 1, sgn > 0 ? 0 : Math.PI);
      arts.push(m);
    }
  }
  root.add(instanced(box(1, 1, 1), plaster, parts));

  // round columns half-engaged in the spine every 7.5 deg (not at the partitions), on both faces: on the slot
  // side they frame curtained bays and give the gallery depth (ref 3)
  const cols = [], yCol = (Y_CEIL - 7.3) / 2, hCol = Y_CEIL + 7.3;
  for (let i = 0; i < 48; i++) {
    const th = 7.5 * i * D2R;
    if (nearPortal(th) || nearJoint(th, 1)) continue;
    cols.push(polarMatrix(th, R_SPINE - 0.3, yCol, 0.32, hCol, 0.32));
  }
  // (gallery-side columns are added in the gallery loop below, between every other pair of tables)

  // guests: seated figures share the chair / banquette matrices; clothing + hair colours per instance
  const sitters = [], sitCol = [], sitHair = [];
  const CLOTH = ['#1c1d24', '#23262e', '#2e2a28', '#14161b', '#3b2a26', '#4a4038', '#5e2a26', '#24303f', '#8a7a64', '#c9c0b0', '#6b5a48'].map(lin);
  const HAIR = ['#1a130e', '#2b1e15', '#3a2a1c', '#5a4430', '#8a6d4c', '#b8a68a', '#6e6a66'].map(lin);
  const pick = a => a[Math.floor(rnd() * a.length)];
  // diners closer than ~9 m to a camera (the terrace walk passes 2-3 m from the window row) are left out
  const seat = (th, r, y, rot) => {
    const s = 0.94 + rnd() * 0.12, m = polarMatrix(th, r, y, s, s, s, rot), c = pick(CLOTH), h = pick(HAIR);
    if (nearCamera(cams, posOf(m), 9)) return;
    sitters.push(m); sitCol.push(c); sitHair.push(h);
  };

  // dining: window row (r 48.0, every 3 m) and slot gallery (r 52.75, every 2.6 m). Linen cloths, a small
  // lamp on every table, drum pendants over the window row and every other gallery table.
  const cloths = [], chairs = [], pend = [], pendB = [], cords = [], tlamp = [], tstem = [];
  const chairsW = [];   // window-row chairs: pale upholstery, they face the terrace glazing (ref 1)
  const chairAt = (th, r, rot, p) => { (r < 50 ? chairsW : chairs).push(polarMatrix(th, r, -6.86, 0.5, 1.1, 0.5, rot)); if (rnd() < p) seat(th, r, -6.81, rot); };
  const lampAt = (th, r, y0 = -7.3) => { tlamp.push(polarMatrix(th, r, y0 + 1.14, 0.085, 0.13, 0.085)); tstem.push(polarMatrix(th, r, y0 + 0.96, 0.012, 0.36, 0.012)); };
  const pendantAt = (th, r, s = 1, y = -3.29) => {
    pend.push(polarMatrix(th, r, y, 0.28 * s, 0.32 * s, 0.28 * s));
    pendB.push(polarMatrix(th, r, y - 0.158 * s, 0.27 * s, 1, 0.27 * s));
    const yt = y + 0.16 * s;
    cords.push(polarMatrix(th, r, (Y_CEIL + yt) / 2, 0.008, Y_CEIL - yt, 0.008));
  };
  for (let s = 0; s < TAU * 48.0; s += 3.0) {
    const th = s / 48.0;
    if (nearJoint(th, 1.6) || nearPortal(th)) continue;
    cloths.push(polarMatrix(th, 48.0, -6.67, 0.46, 0.27, 0.46));
    for (const d of [-1, 1]) chairAt(th + d * 0.78 / 48.0, 48.0, -d * Math.PI / 2, 0.85);
    if (rnd() < 0.5) chairAt(th, 48.78, 0, 0.8);                         // third seat facing the view
    lampAt(th, 48.0);
    // (no drum pendants over the window row: ref 1 shows linear ceiling lights and downlights, and the big white
    // drums right behind the terrace glass read as props; their light pools stay in INTERIOR_FRAG)
  }
  // Slot gallery (refs 3 / 4 / 7 / 11 at 100%: cream lounge furniture, table lamps, plants and guests fill the lower
  // half of the band under a dark ceiling zone with point spots, every bay different). From the drones the line of
  // sight through the slot falls only ~0.3 m per metre, so a flat floor showed one thin row of furniture under a tall
  // lit wall (a backdrop, not a room): the gallery steps up in three tiers toward the spine (0.7 m risers), each a row
  // of furniture facing the view, so the lit treads, cream upholstery and lamps stack up to about half the glass.
  // Front row at the glass: club armchairs, an olive tree now and then; tier 1: clothed 2-tops with lamps; tier 2:
  // banquettes against the spine. (Dark wall above with picture lights: INTERIOR_FRAG pattern 6.)
  const Y_T1 = -6.6, Y_T2 = -5.9, R_T1 = 53.55, R_T2 = 52.65;
  const riser = M.interior('#5c4130');   // walnut
  for (const [a0, a1] of SLOTS) {
    const t0 = (a0 + 4) * D2R, t1 = (a1 - 4) * D2R;
    for (const [ty, r0, r1] of [[Y_T1, R_T2, R_T1], [Y_T2, R_SPINE + 0.15, R_T2]]) {
      add(revolve([[r0, ty], [r1, ty]], [[0, 1], [0, 1]], t0, t1, 240), floor, 'tierTop');
      add(cyl(r1, -7.3, ty, true, t0, t1, 240), riser, 'tierRiser');
    }
  }
  // pale round columns half-engaged in the spine between some of the tables, each with a warm sconce
  const galCols = [];
  const banq = [], gPlants = [], globes = [], armG = [], armGCol = [], lowT = [], gLamp = [], gStem = [], candle = [];
  // mostly cream / oat / stone upholstery (refs 4 / 7 at 100%: the brightest values in the band are pale seats lit
  // from above), a few cognac and charcoal pieces
  const ARMC = ['#ded3c1', '#cfc2ac', '#bdb19f', '#e6ddcf', '#8f8578', '#6f4b34', '#4a4642'].map(lin);
  const grnd = mulberry(53);   // gallery layout (own stream: the lounge and window rows keep their draw)
  let gi = 0;
  for (let s = 0; s < TAU * 52.75; s += 2.6) {
    const th = s / 52.75;
    if (!isSlot(th) || nearJoint(th, 1.5, 53)) continue;
    // tier 2: high-backed banquette against the spine, a clothed table with its lamp
    cloths.push(polarMatrix(th, 52.36, Y_T2 + 0.63, 0.29, 0.27, 0.29));
    banq.push(polarMatrix(th, 52.0, Y_T2, 0.6, 1, 2.45, Math.PI));
    for (const d of [-1, 1]) if (grnd() < 0.62) seat(th + d * 0.42 / 52, 51.98, Y_T2 + 0.42, Math.PI);
    lampAt(th, 52.36, Y_T2);
    // tier 1: a clothed 2-top facing the view (chairs either side along the arc) or two armchairs and a low table
    const armAt = (a, r, y, rot) => {
      armG.push(polarMatrix(a, r, y, 0.74, 0.95, 0.74, rot)); armGCol.push(ARMC[Math.floor(grnd() * ARMC.length)]);
      if (grnd() < 0.6) seat(a, r + 0.02, y + 0.4, rot);
    };
    if (grnd() < 0.6) {
      cloths.push(polarMatrix(th, 53.1, Y_T1 + 0.63, 0.3, 0.27, 0.3));
      lampAt(th, 53.1, Y_T1);
      for (const d of [-1, 1]) {
        chairs.push(polarMatrix(th + d * 0.66 / 53.1, 53.1, Y_T1 + 0.44, 0.5, 1.1, 0.5, -d * Math.PI / 2));
        if (grnd() < 0.7) seat(th + d * 0.66 / 53.1, 53.1, Y_T1 + 0.49, -d * Math.PI / 2);
      }
    } else {
      for (const d of [-1, 1]) armAt(th + d * 0.5 / 53.1, 53.05, Y_T1, Math.PI + d * 0.25);
      lowT.push(polarMatrix(th, 53.32, Y_T1 + 0.22, 0.24, 0.4, 0.24));
      candle.push(polarMatrix(th, 53.32, Y_T1 + 0.48, 0.04, 0.07, 0.04));
    }
    // front row at the glass: two armchairs facing the view (sometimes one beside an olive tree), offset half a cell
    // from the tiers so the rows read as a scattered lounge, not stacked columns
    const tf = th + 1.3 / 52.75, u = grnd();
    if (u < 0.7) {
      for (const d of [-1, 1]) armAt(tf + d * 0.46 / 53.95, 53.93, -7.3, Math.PI + d * 0.15);
    } else {
      gPlants.push([tf - 0.5 / 53.95, 53.95, 0]);
      armAt(tf + 0.45 / 53.95, 53.93, -7.3, Math.PI + 0.2);
    }
    if (grnd() < 0.25) galCols.push(polarMatrix(th + 1.3 / 52.75, R_SPINE + 0.3, (Y_CEIL + Y_T2) / 2, 0.28, Y_CEIL - Y_T2, 0.28));
    // an olive tree or a linen floor lamp on the upper tier now and then (tall shapes up into the dark wall)
    const v = grnd();
    if (v < 0.16) gPlants.push([th + 1.25 / 52.3, 52.3, Y_T2 + 7.3]);
    else if (v < 0.36) {
      const a = th + 1.25 / 52.3;
      gLamp.push(polarMatrix(a, 52.3, Y_T2 + 1.55, 0.21, 0.3, 0.21)); gStem.push(polarMatrix(a, 52.3, Y_T2 + 0.75, 0.015, 1.5, 0.015));
    }
    // small ceiling spots / mini pendants just under the ceiling (refs 4 / 7: point lights in a dark top zone, not
    // a row of globes across the middle of the band)
    for (let q = 0; q < 3; q++) {
      if (grnd() < 0.35) continue;
      const a = th + (q - 1) * 0.86 / 53.5 + (grnd() - 0.5) * 0.3 / 53.5, rr = 52.6 + grnd() * 1.4, y = -1.25 - 0.35 * grnd();
      globes.push(polarMatrix(a, rr, y, 0.06, 0.06, 0.06));
      cords.push(polarMatrix(a, rr, (y + Y_CEIL) / 2, 0.005, Y_CEIL - y, 0.005));
    }
    gi++;
  }
  const walnut = M.interior('#4a2f1e'), chairMat = M.interior('#4d4038'), linen = M.interior('#ebe5da');
  const shade = M.interior('#fff', 7, 2.5), diffuser = M.interior('#fff', 0, 9.0), lampShade = M.interior('#fff', 7, 5.5);
  root.add(instanced(new THREE.CylinderGeometry(1, 1.04, 1, 28), linen, cloths));
  if (chairs.length) root.add(instanced(chairGeometry(), chairMat, chairs));
  root.add(instanced(chairGeometry(), M.interior('#a8988a'), chairsW));
  // taupe boucle banquettes (ref 4 at 100%: pale seats lit from above against dark tables, chairs and guests)
  root.add(instanced(sofaGeometry(1.1), M.interior('#a08a72'), banq));
  // gallery front row: club armchairs in mixed upholstery, low walnut tables with a candle lamp, linen floor lamps
  root.add(instanced(armchairGeometry(), M.interior('#ffffff'), armG, armGCol));
  root.add(instanced(new THREE.CylinderGeometry(1, 1, 1, 24), walnut, lowT));
  if (galCols.length) root.add(instanced(new THREE.CylinderGeometry(1, 1, 1, 24, 1, true), M.interior('#d9c8ab', 8), galCols));
  if (candle.length) root.add(instanced(new THREE.CylinderGeometry(0.8, 1, 1, 10, 1, true), M.interior('#fff', 7, 4.0), candle));
  if (gLamp.length) {
    root.add(instanced(new THREE.CylinderGeometry(0.8, 1, 1, 18, 1, true), M.interior('#fff', 7, 2.4), gLamp));
    root.add(instanced(new THREE.CylinderGeometry(1, 1, 1, 4), M.interior('#2a2420'), gStem));
  }
  if (pend.length) root.add(instanced(new THREE.CylinderGeometry(1, 1, 1, 28, 1, true), shade, pend));
  const disc = new THREE.CircleGeometry(1, 24); disc.rotateX(Math.PI / 2);
  root.add(instanced(disc, diffuser, pendB));
  root.add(instanced(new THREE.CylinderGeometry(1, 1, 1, 4), M.interior('#2a2420'), cords));
  root.add(instanced(new THREE.CylinderGeometry(0.75, 1, 1, 16, 1, true), lampShade, tlamp));
  root.add(instanced(new THREE.SphereGeometry(1, 12, 8), M.interior('#fff', 0, 7.0), globes));   // (gallery ceiling spots)
  root.add(instanced(new THREE.CylinderGeometry(1, 1, 1, 4), M.interior('#3a2c20'), tstem));

  // lounge groups against the spine (between the columns): boucle sofa, two armchairs, walnut coffee table,
  // ochre art above, a linen floor lamp beside every other sofa
  const sofas = [], arm = [], coffee = [], cush = [], flamp = [], fstem = [], lGlobes = [], lCords = [];
  for (let i = 0; i < 48; i++) {
    const th = (3.75 + 7.5 * i) * D2R;
    if (nearJoint(th, 3.2, 51) || nearPortal(th)) continue;
    sofas.push(polarMatrix(th, R_SPINE - 0.65, -7.3, 0.95, 1, 2.3));
    for (const d of [-0.55, 0.55]) if (rnd() < 0.55) seat(th + d / 50.9, R_SPINE - 0.6, -6.88, 0);
    coffee.push(polarMatrix(th, R_SPINE - 1.75, -7.06, 0.5, 0.42, 0.5));
    for (const d of [-1, 1]) {
      const a = th + d * 1.15 / 50, rot = Math.PI + d * 0.4;
      arm.push(polarMatrix(a, R_SPINE - 2.75, -7.3, 0.85, 1, 0.85, rot));
      if (rnd() < 0.6) seat(a, R_SPINE - 2.72, -6.88, rot);
    }
    cush.push(polarMatrix(th + 0.55 / 51, R_SPINE - 0.85, -6.72, 0.16, 0.42, 0.42));
    // trio of glass globes over the coffee table: the far arc's band (refs 1, 4) reads as many small lights
    for (let q = 0; q < 3; q++) {
      const a = th + (q - 1) * 0.36 / 49.85, rr = R_SPINE - 1.75 + (q === 1 ? 0.22 : -0.1), y = -3.3 - 0.4 * ((q * 5 + i) % 3) / 2;
      lGlobes.push(polarMatrix(a, rr, y, 0.12, 0.12, 0.12));
      lCords.push(polarMatrix(a, rr, (y + Y_CEIL) / 2, 0.006, Y_CEIL - y, 0.006));
    }
    if (i % 2) arts.push(polarMatrix(th, R_SPINE - 0.17, -4.6, 1.9, 1.25, 1, -Math.PI / 2));
    else {
      const a = th + 1.55 / 51;
      flamp.push(polarMatrix(a, R_SPINE - 0.55, -5.75, 0.2, 0.3, 0.2));
      fstem.push(polarMatrix(a, R_SPINE - 0.55, -6.55, 0.015, 1.5, 0.015));
    }
  }
  const boucle = M.interior('#d9cfbf'), ochre = M.interior('#8a4a1e');
  root.add(instanced(sofaGeometry(), boucle, sofas));
  root.add(instanced(sofaGeometry(), boucle, arm));
  root.add(instanced(new THREE.CylinderGeometry(1, 1, 1, 28), walnut, coffee));
  root.add(instanced(box(1, 1, 1), ochre, cush));
  root.add(instanced(new THREE.PlaneGeometry(1, 1), M.interior('#888', 3), arts));
  root.add(instanced(new THREE.CylinderGeometry(0.8, 1, 1, 18, 1, true), M.interior('#fff', 7, 2.6), flamp));
  root.add(instanced(new THREE.CylinderGeometry(1, 1, 1, 4), M.interior('#2a2420'), fstem));
  root.add(instanced(new THREE.SphereGeometry(1, 12, 8), M.interior('#fff', 0, 6.0), lGlobes));
  root.add(instanced(new THREE.CylinderGeometry(1, 1, 1, 4), M.interior('#2a2420'), lCords));

  // seated guests (body + head share one matrix)
  root.add(instanced(seatedGeometry(), M.interior('#fff', 9), sitters, sitCol));
  const head = new THREE.SphereGeometry(0.105, 10, 8); head.scale(1, 1.12, 0.92); head.translate(0.03, 0.82, 0);
  root.add(instanced(head, M.interior('#fff', 9), sitters, sitHair));
  // a few staff / standing guests in the gallery and the lounge
  const stand = [], stCol = [], stHair = [];
  for (let i = 0; i < 360; i += 4.5) {
    const th = (i + 1.7) * D2R;
    if (nearPortal(th) || nearJoint(th, 2.0, 50)) continue;
    const slot = isSlot(th);
    if (rnd() > (slot ? 0.4 : 0.45)) continue;
    const r = slot ? 53.62 + rnd() * 0.12 : 48.9 + rnd() * 0.9, s = 0.95 + rnd() * 0.1;   // (slot: on the front row's floor)
    const m = polarMatrix(th, r, -7.3, s, s, s, rnd() * TAU), c = pick(CLOTH), h = pick(HAIR);
    if (nearCamera(cams, posOf(m).setY(-6.3), 12)) continue;
    stand.push(m); stCol.push(c); stHair.push(h);
  }
  root.add(instanced(standingGeometry(), M.interior('#fff', 9), stand, stCol));
  const head2 = new THREE.SphereGeometry(0.105, 10, 8); head2.scale(1, 1.12, 0.92); head2.translate(0, 1.6, 0);
  root.add(instanced(head2, M.interior('#fff', 9), stand, stHair));

  // potted olive trees: between window tables and along the slot gallery
  const pots = [], crowns = [], trunks = [];
  const tree = (th, r, sc = 1, dy = 0) => {
    pots.push(polarMatrix(th, r, -6.95 + dy, 0.36, 0.7, 0.36));
    trunks.push(polarMatrix(th, r, -5.9 + dy, 0.055, 1.6, 0.055));
    for (let c = 0; c < 7; c++) {
      const a = rnd() * TAU, rad = (0.15 + rnd() * 0.35) * sc;
      crowns.push(polarMatrix(th + Math.sin(a) * rad / r, r + Math.cos(a) * rad, -4.95 + dy + rnd() * 0.75, (0.32 + rnd() * 0.2) * sc, 0.26 + rnd() * 0.14, (0.32 + rnd() * 0.2) * sc, rnd() * 3));
    }
  };
  for (let i = 0; i < 24; i++) { const th = (7.5 + 15 * i) * D2R; if (i % 3 === 1 && !nearPortal(th)) tree(th, 49.6); }
  for (const [th, r, dy] of gPlants) if (!nearJoint(th, 2.0, 53)) tree(th, r, 0.8, dy);
  root.add(instanced(new THREE.CylinderGeometry(1, 0.78, 1, 18), M.interior('#5a534c'), pots));
  root.add(instanced(new THREE.CylinderGeometry(0.7, 1, 1, 6), M.interior('#3a2c22'), trunks));
  root.add(instanced(new THREE.IcosahedronGeometry(1, 1), M.interior('#7c8460', 4), crowns));
}

// Outdoor figures: guests on the roof deck along the inner balustrade (refs 4, 7, 11) and on the terrace (refs 1, 8).
// Only distant specks survive: anything within 30 m of a film / reference camera, or that would stand taller
// than ~36 px in a 1080p frame, is dropped (the terrace walk and view 1 keep only the far arc's strollers).
function buildPeople(root, M, cams) {
  const rnd = mulberry(31);
  const COAT = ['#2a2c33', '#33363f', '#3d3833', '#3b4352', '#4a3430', '#5e5244', '#6a3030', '#7f725f', '#334034', '#a09482', '#22242a'].map(lin);
  const HAIR = ['#120d0a', '#22180f', '#3a2a1c', '#2b2b2e', '#6a5440', '#8f8f8f', '#1c2433'].map(lin);   // incl. beanies
  const mats = [], col = [], hair = [];
  const person = (th, r, y) => {
    const s = 0.92 + rnd() * 0.14;
    const m = polarMatrix(th, r, y, s, s, s, rnd() * TAU);
    const c = COAT[Math.floor(rnd() * COAT.length)], h = HAIR[Math.floor(rnd() * HAIR.length)];
    if (nearCamera(cams, posOf(m).setY(y + 1.0), 30, 36)) return;
    mats.push(m); col.push(c); hair.push(h);
  };
  const nearPortal = d => d < 7 || d > 353 || Math.abs(d - 180) < 7;
  // roof deck: small groups of 1-3 leaning on the inner glass rail, a few further out
  for (let d = 0; d < 360; d += 3.2) {
    if (nearPortal(d) || rnd() > 0.5) continue;
    const n = 1 + Math.floor(rnd() * 2.6), th0 = (d + rnd() * 2) * D2R;
    for (let k = 0; k < n; k++) person(th0 + k * (0.55 + rnd() * 0.25) / 45, R_CAN + 0.45 + rnd() * (rnd() < 0.8 ? 0.4 : 4.0), 0.0);
  }
  // roof deck, outer edge: couples and small groups at the outer glass rail (refs 3 / 4 / 7 / 11: a row of
  // silhouettes along the top of the facade band)
  for (let d = 0; d < 360; d += 3.6) {
    if (nearPortal(d) || rnd() > 0.42) continue;
    const n = 1 + Math.floor(rnd() * 2.4), th0 = (d + rnd() * 2) * D2R;
    for (let k = 0; k < n; k++) person(th0 + k * (0.55 + rnd() * 0.25) / 54, 54.25 - rnd() * 0.3, 0.0);
  }
  // terrace: strollers and couples at the balustrade
  for (let d = 0; d < 360; d += 4.0) {
    if (rnd() > 0.45) continue;
    const n = 1 + Math.floor(rnd() * 2.2), th0 = (d + rnd() * 3) * D2R, r = rnd() < 0.6 ? 43.25 + rnd() * 0.3 : 44.0 + rnd() * 2.4;
    for (let k = 0; k < n; k++) person(th0 + k * 0.6 / 44, r + (rnd() - 0.5) * 0.3, -7.3);
  }
  if (!mats.length) return;
  const fig = M.concrete(10, '#ffffff');
  root.add(instanced(standingGeometry(), fig, mats, col));
  const head = new THREE.SphereGeometry(0.105, 10, 8); head.scale(1, 1.12, 0.92); head.translate(0, 1.6, 0);
  root.add(instanced(head, fig, mats, hair));
}

// seated figure: seat top at y=0, back toward +x, facing -x (the table)
function seatedGeometry() {
  const parts = [];
  const b = (w, h, d, x, y, z, rz = 0) => { const g = box(w, h, d); if (rz) g.rotateZ(rz); g.translate(x, y, z); parts.push(g.toNonIndexed()); };
  b(0.46, 0.15, 0.36, -0.10, 0.075, 0);          // thighs
  b(0.13, 0.46, 0.30, -0.33, -0.17, 0);          // shins
  b(0.25, 0.56, 0.40, 0.10, 0.42, 0, 0.12);      // torso, leaning in
  b(0.11, 0.42, 0.10, 0.05, 0.40, 0.24, 0.5);    // arms toward the table
  b(0.11, 0.42, 0.10, 0.05, 0.40, -0.24, 0.5);
  return mergeGeometries(parts);
}
// standing figure: feet at y=0, facing -x
function standingGeometry() {
  const parts = [];
  // coat / torso: lathe from the hips to the neck, flattened front-to-back
  const prof = [[0.001, 0.80], [0.150, 0.80], [0.170, 0.92], [0.155, 1.08], [0.180, 1.28], [0.205, 1.40], [0.170, 1.47], [0.060, 1.52], [0.050, 1.56], [0.001, 1.56]];
  const torso = new THREE.LatheGeometry(prof.map(([r, y]) => new THREE.Vector2(r, y)), 12);
  torso.scale(0.62, 1, 1);
  parts.push(torso.toNonIndexed());
  const limb = (r0, r1, len, x, y, z, rz = 0, rx = 0) => {
    const g = new THREE.CylinderGeometry(r1, r0, len, 7); g.translate(0, -len / 2, 0);
    if (rx) g.rotateX(rx); if (rz) g.rotateZ(rz); g.translate(x, y, z); parts.push(g.toNonIndexed());
  };
  limb(0.085, 0.055, 0.84, 0, 0.84, 0.085, 0.04);     // legs (hip -> ankle), slight stride
  limb(0.085, 0.055, 0.84, 0, 0.84, -0.085, -0.04);
  limb(0.055, 0.04, 0.60, 0, 1.43, 0.215, 0, 0.12);   // arms
  limb(0.055, 0.04, 0.60, 0, 1.43, -0.215, 0, -0.12);
  const feet = box(0.24, 0.07, 0.1); feet.translate(-0.04, 0.035, 0.085); parts.push(feet.toNonIndexed());
  const f2 = box(0.24, 0.07, 0.1); f2.translate(-0.04, 0.035, -0.085); parts.push(f2.toNonIndexed());
  return mergeGeometries(parts.map(p => { p.deleteAttribute('uv'); return p; }));
}

function chairGeometry() {
  const seat = box(1, 0.1, 1); seat.translate(0, 0, 0);
  const back = box(0.12, 0.9, 1); back.translate(0.45, 0.4, 0);
  const base = new THREE.CylinderGeometry(0.06, 0.06, 0.5, 6); base.translate(0, -0.25, 0);
  const g = mergeGeometries([seat.toNonIndexed(), back.toNonIndexed(), base.toNonIndexed()]);
  g.scale(1, 0.8, 1); g.translate(0, 0.0, 0);
  return g;
}
// club armchair (unit cube footprint, scaled per instance): deep seat, chunky arms, back toward +x
function armchairGeometry() {
  const seat = box(1, 0.4, 1); seat.translate(0, 0.2, 0);
  const back = box(0.26, 0.44, 1); back.translate(0.37, 0.62, 0);
  const a1 = box(0.92, 0.22, 0.18); a1.translate(0.02, 0.5, 0.41);
  const a2 = box(0.92, 0.22, 0.18); a2.translate(0.02, 0.5, -0.41);
  return mergeGeometries([seat, back, a1, a2].map(x => x.toNonIndexed()));
}
// seat 0.42 high, back rising to backH (high-backed banquettes in the slot gallery: dark masses across the band)
function sofaGeometry(backH = 0.84) {
  const seat = box(1, 0.42, 1); seat.translate(0, 0.21, 0);
  const back = box(0.22, backH - 0.42, 1); back.translate(0.39, (backH + 0.42) / 2, 0);
  const a1 = box(1, 0.25, 0.12); a1.translate(0, 0.55, 0.44);
  const a2 = box(1, 0.25, 0.12); a2.translate(0, 0.55, -0.44);
  const g = mergeGeometries([seat, back, a1, a2].map(x => x.toNonIndexed()));
  return g;
}

// ---------------------------------------------------------------- bridges, pavilions, struts
function buildBridge(root, M, add, side, lamps, mt) {
  const g = new THREE.Group();
  // side = +1 -> +X bridge, -1 -> -X bridge (mirrored so the open walkway faces +Z on both)
  g.scale.set(side, 1, 1);
  root.add(g);
  const A = (geo, mat, name) => { const m = new THREE.Mesh(geo, mat); m.name = name || ''; m.frustumCulled = false; g.add(m); return m; };
  const B = (w, h, d, x, y, z, mat, name) => { const geo = box(w, h, d); geo.translate(x, y, z); return A(geo, mat, name); };
  const x0 = 54.6, x1 = 73.0, L = x1 - x0, xc = (x0 + x1) / 2;

  // roof slab (walkable, flush with deck), floor slab, spine
  // roof: concrete over the open walkway and a rear edge beam; glazed skylight over the corridor (ref 8 top view)
  B(L, 0.6, 0.75, xc, -0.3, -3.375, mt.roofMat, 'bridgeRoof');
  B(L, 0.6, 3.45, xc, -0.3, 2.025, mt.roofMat, 'bridgeRoof');
  B(L, 0.03, 3.3, xc, -0.08, -1.35, mt.glassIn, 'skylight');
  const sky = [];
  for (let x = x0 + 1.5; x < x1; x += 1.5) sky.push(new THREE.Matrix4().compose(new THREE.Vector3(x, -0.1, -1.35), new THREE.Quaternion(), new THREE.Vector3(0.06, 0.1, 3.3)));
  g.add(instanced(box(1, 1, 1), mt.bronze, sky));
  B(L, 0.8, 7.5, xc, -5.8, 0, mt.conc, 'bridgeFloor');
  B(L + 6, 1.2, 3.0, xc - 3, -6.8, -0.75, mt.bronze, 'spine');
  B(L, 0.02, 3.0, xc, -5.39, 2.25, mt.terrazzo, 'walkFloor');
  B(L, 0.02, 4.5, xc, -5.39, -1.5, M.interior('#8c7660', 2), 'corrFloor');   // (pass 2: darker oak, a deep room)
  // corridor furniture: a row of two-tops along the glazing
  {
    const t = [], c = [], wal = M.interior('#6e4a31'), ch = M.interior('#a19486');
    for (let x = x0 + 2.2; x < x1 - 1; x += 2.6) {
      t.push(new THREE.Matrix4().compose(new THREE.Vector3(x, -4.65, -2.6), new THREE.Quaternion(), new THREE.Vector3(0.42, 0.045, 0.42)));
      for (const d of [-1, 1]) c.push(new THREE.Matrix4().compose(new THREE.Vector3(x + d * 0.72, -4.96, -2.6), new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 1, 0), d > 0 ? 0 : Math.PI), new THREE.Vector3(0.5, 1.1, 0.5)));
    }
    g.add(instanced(new THREE.CylinderGeometry(1, 1, 1, 24), wal, t));
    g.add(instanced(chairGeometry(), ch, c));
  }
  // corridor (rear, z -3.75 .. 0.75): glass both faces, fascia band
  // (round 7) the rear face is a warm-lit wall, not a second glazing: seen through the front glass the corridor reads as
  // a lit room (refs 4 / 5 / 7 / 11: the bridges glow warm beside the ring), not a grey tube showing the sky behind
  // (pass 2) a dark walnut wall lit in sconce pools (pattern 10), not an evenly lit tan wall: the refs' bridges read as
  // dark glazed corridors with hot lamp spots (refs 4 / 7 / 11: p50 27-34, p90 62-78)
  B(L, 4.4, 0.04, xc, -3.2, -3.75, M.interior('#7a6250', 10), 'corrBackWall');
  B(L, 4.4, 0.04, xc, -3.2, 0.75, mt.glassIn, 'corrGlassFront');
  B(L, 0.4, 0.3, xc, -0.8, -3.6, mt.conc);
  const corrMull = [];
  for (let x = x0 + 1.5; x < x1; x += 1.5) for (const z of [-3.75, 0.75]) corrMull.push(new THREE.Matrix4().compose(new THREE.Vector3(x, -3.2, z), new THREE.Quaternion(), new THREE.Vector3(0.06, 4.4, 0.12)));
  g.add(instanced(box(1, 1, 1), mt.bronze, corrMull));
  // corridor interior: cove lines along the skylight edges, warm-lit ceiling strip over the rear beam
  B(L, 0.05, 0.08, xc, -0.66, -2.95, mt.ledSoft, 'corrCove');
  B(L, 0.05, 0.08, xc, -0.66, 0.28, mt.ledSoft, 'corrCove');
  B(L, 0.04, 0.7, xc, -0.62, -3.35, M.interior('#efe6d6', 0, 3.2));   // (round 7: x2, the refs' bridges glow warm)
  // open walkway (front, z 0.75 .. 3.75): balustrade glass + LED
  const rg = new THREE.PlaneGeometry(L, 1.1); rg.translate(xc, -5.4 + 0.55, 3.72);
  A(rg, mt.railGlass, 'walkRail');
  B(L, 0.04, 0.06, xc, -4.27, 3.72, mt.capRail);
  B(L, 0.03, 0.05, xc, -5.37, 3.6, mt.led, 'walkLed');
  B(L, 0.03, 0.05, xc, -5.37, 0.9, mt.ledSoft);
  // roof rails (both edges): plain glass on the slab edge, no LED lines (ref 10: a calm concrete roof slab)
  for (const z of [-3.72, 3.72]) {
    const r2 = new THREE.PlaneGeometry(L, 1.1); r2.translate(xc, 0.55, z);
    A(r2, mt.railGlassRoof);
    B(L, 0.04, 0.06, xc, 1.12, z, mt.capRail);
  }

  // pavilion at the cliff: x 73..82, z -6..6, two storeys (-9.5..-5.4 lower, -5.4..0 upper)
  const px0 = 73, px1 = 82, pxc = (px0 + px1) / 2;
  B(9, 0.6, 12, pxc, -0.3, 0, mt.roofMat, 'pavRoof');
  B(9, 0.5, 12, pxc, -5.65, 0, mt.conc);
  B(9, 0.5, 12, pxc, -9.75, 0, mt.conc);
  B(1.0, 9.5, 12, px1 + 0.5, -4.75, 0, mt.conc, 'pavBack');
  // glazed faces (front +z, rear -z, gorge face x=73)
  for (const z of [6, -6]) {
    B(9, 4.6, 0.04, pxc, -3.0, z, mt.glassIn);
    B(9, 3.6, 0.04, pxc, -7.5, z, mt.glassIn);
  }
  B(0.04, 3.6, 12, px0, -7.5, 0, mt.glassIn);
  B(0.04, 4.6, 4.0, px0, -3.0, 4.0, mt.glassIn);
  B(0.04, 4.6, 4.0, px0, -3.0, -4.0, mt.glassIn);
  const pm = [];
  for (let x = px0 + 1.5; x < px1; x += 1.5) for (const z of [-6, 6]) { pm.push(new THREE.Matrix4().compose(new THREE.Vector3(x, -3.0, z), new THREE.Quaternion(), new THREE.Vector3(0.06, 4.6, 0.12))); pm.push(new THREE.Matrix4().compose(new THREE.Vector3(x, -7.5, z), new THREE.Quaternion(), new THREE.Vector3(0.06, 3.6, 0.12))); }
  for (let z = -4.5; z <= 4.5; z += 1.5) pm.push(new THREE.Matrix4().compose(new THREE.Vector3(px0, -7.5, z), new THREE.Quaternion(), new THREE.Vector3(0.12, 3.6, 0.06)));
  g.add(instanced(box(1, 1, 1), mt.bronze, pm));
  // pavilion interiors: warm floors/ceilings/back wall
  B(8.6, 0.04, 11.6, pxc, -5.38, 0, M.interior('#d8c3a5', 2));
  B(8.6, 0.04, 11.6, pxc, -9.48, 0, M.interior('#d8c3a5', 2));
  // (round 7: brighter: refs 4 / 5 / 6 show the pavilions as the brightest warm volumes beside the ring)
  B(8.6, 0.05, 11.6, pxc, -0.62, 0, M.interior('#efe6d6', 0, 3.8));
  B(8.6, 0.05, 11.6, pxc, -5.92, 0, M.interior('#efe6d6', 0, 3.5));
  B(0.1, 9.0, 11.6, px1 - 0.1, -4.9, 0, M.interior('#e2d6c2'));
  // pavilion roof rails
  for (const z of [-5.95, 5.95]) { const r2 = new THREE.PlaneGeometry(9, 1.1); r2.translate(pxc, 0.55, z); A(r2, mt.railGlassRoof); B(9, 0.04, 0.06, pxc, 1.12, z, mt.capRail); }
  // LED under pavilion slabs
  B(9, 0.04, 0.06, pxc, -9.98, 5.95, mt.led);
  B(9, 0.04, 0.06, pxc, -5.92, 5.95, mt.led);

  // ---------------- struts (inverted V, front and back), in bridge-local coords
  // dark satin steel tubes (pass 2: A 3.0 m, B 2.3 m across; refs 9 / 10 measure strut / ring width ~0.04, about
  // twice pass 1) with a long smooth trumpet flare into the soffit (ref 3) and a flared shoe on the plinth
  const RA = 1.5, RB = 1.15, RC = 3.1;
  const collarGeo = trumpetGeometry(RC, RA, 4.5);
  const shoeGeo = trumpetGeometry(2.4, RA, 2.8);
  const tubeGeo = new THREE.CylinderGeometry(1, 1, 1, 64, 1, true);
  // chamfered concrete haunch where strut B meets the bridge floor slab (ref 9: squared blocks at the junction)
  const haunchGeo = new THREE.CylinderGeometry(2.6, 2.15, 1.7, 4, 1); haunchGeo.rotateY(Math.PI / 4);
  for (const fz of [1, -1]) {
    const pol = (r, thDeg, y) => new THREE.Vector3(r * Math.cos(thDeg * D2R), y, fz * r * Math.sin(thDeg * D2R));
    const topA = pol(48, 22, -9.3), topB = pol(57, 3, -7.4), foot = pol(62, 10, -25);
    const ta = tubeMatrix(topA, foot, RA), tb = tubeMatrix(topB, foot, RB);
    g.add(instanced(tubeGeo, mt.strutSteel, [ta, tb]));
    // collar at soffit (flare opening upward), shoe at footing
    const cm = new THREE.Matrix4().compose(topA.clone().add(new THREE.Vector3(0, -0.01, 0)), new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, -1, 0), foot.clone().sub(topA).normalize()), new THREE.Vector3(1, 1, 1));
    const c = new THREE.Mesh(collarGeo, mt.strutSteel); c.applyMatrix4(cm); c.frustumCulled = false; g.add(c);
    const hB = topB.clone().setY(-7.05);
    const hm = new THREE.Mesh(haunchGeo, mt.conc); hm.position.copy(hB); hm.frustumCulled = false; g.add(hm);
    const cb = new THREE.Mesh(trumpetGeometry(1.45, RB, 1.2), mt.strutSteel);
    cb.applyMatrix4(new THREE.Matrix4().compose(topB.clone().setY(-7.88), new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, -1, 0), foot.clone().sub(topB).normalize()), new THREE.Vector3(1, 1, 1)));
    cb.frustumCulled = false; g.add(cb);
    // (no LED halo ring at the collar: it read as a neon ellipse; the lamp inside the flare washes the soffit instead)
    const s = new THREE.Mesh(shoeGeo, mt.strutSteel);
    const dirUp = topA.clone().add(topB).multiplyScalar(0.5).sub(foot).normalize();
    s.applyMatrix4(new THREE.Matrix4().compose(foot.clone(), new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, -1, 0), dirUp), new THREE.Vector3(1, 1, 1)));
    s.frustumCulled = false; g.add(s);
    // plinth: squat octagonal concrete block under the shoe
    const plg = new THREE.CylinderGeometry(3.0, 3.4, 3.6, 8); plg.translate(0, -2.0, 0);
    const pl = new THREE.Mesh(plg, mt.conc); pl.position.copy(foot).add(new THREE.Vector3(0.4, -0.6, 0)); pl.rotation.y = 0.3; pl.frustumCulled = false; g.add(pl);
    // if the cliff face is not under the plinth, a keyed concrete corbel runs outward until it is buried in rock
    if (mt.H) {
      let reach = -1;
      for (let d = 0; d <= 30; d += 0.5) {
        const q = foot.clone().add(new THREE.Vector3(d, 0, 0));
        if (mt.H(q.x * side, q.z) > foot.y - 3.5) { reach = d; break; }
      }
      if (reach > 1.0) {
        const len = reach + 3.0, cg = box(len, 4.2, 3.4); cg.translate(foot.x + len / 2, foot.y - 2.7, foot.z);
        const cm2 = new THREE.Mesh(cg, mt.conc); cm2.frustumCulled = false; g.add(cm2);
      }
      if (reach < 0) console.warn('strut footing: no rock within 30 m', side, fz);
    }
    // lamps (in ring frame; g has scale.x = side)
    const toRing = p => new THREE.Vector3(p.x * side, p.y, p.z);
    lamps.push({ p: toRing(foot.clone().add(new THREE.Vector3(-1.5, 1.5, 0))), c: [1.0, 0.6, 0.3], i: 40, r: 2.8 });
    // soft warm glow of the soffit around the strut head (ref 3), from a lamp low in the flare
    lamps.push({ p: toRing(topA.clone().add(new THREE.Vector3(0, -1.4, 0))), c: [1.0, 0.6, 0.3], i: 55, r: 2.2 });
  }
  // pavilion glow onto rock + bridge underside glow
  const toRing = p => new THREE.Vector3(p.x * side, p.y, p.z);
  // (kept soft: the rock hugs the pavilion, and bright snow right next to a point lamp blooms into a white blob
  // in the walkway shot)
  lamps.push({ p: toRing(new THREE.Vector3(76.0, -8.0, 8.0)), c: [1.0, 0.6, 0.3], i: 11, r: 5 });
  lamps.push({ p: toRing(new THREE.Vector3(76.0, -8.0, -8.0)), c: [1.0, 0.6, 0.3], i: 8, r: 5 });
  lamps.push({ p: toRing(new THREE.Vector3(64, -6.5, 4.5)), c: [1.0, 0.6, 0.3], i: 30, r: 2 });
}

// terrain height (ring frame, relative to the deck) at ring-frame (x, z), or null without terrain
function ringHeight(root, terrain) {
  const hAt = terrain && terrain.userData && terrain.userData.heightAt;
  if (!hAt) return null;
  const mw = root.matrixWorld, deckY = mw.elements[13];
  return (x, z) => { const w = new THREE.Vector3(x, 0, z).applyMatrix4(mw); return hAt(w.x, w.z) - deckY; };
}

// ---------------------------------------------------------------- cliff approach path (ref 10)
// 2.4 m cantilevered walkway at bridge-floor level, following the rock contour from the front (+Z) of the
// -X pavilion along the cliff; glass balustrades both sides (gorge side hangs 0.3 m below the slab),
// stainless top rails, LED at both bases, snow drifts against the glass.
function strip(N, J, f) {
  const pos = [], nor = [], uv = [], idx = [];
  for (let i = 0; i < N; i++) for (let j = 0; j <= J; j++) {
    const [p, n, u] = f(i, j); pos.push(p.x, p.y, p.z); nor.push(n.x, n.y, n.z); uv.push(u[0], u[1]);
  }
  for (let i = 0; i < N - 1; i++) for (let j = 0; j < J; j++) { const a = i * (J + 1) + j, b = a + 1, c = a + J + 1, d = c + 1; idx.push(a, b, c, b, d, c); }
  return finish(pos, nor, uv, idx);
}
function buildPath(root, M, add, terrain, lamps, mt) {
  const hAt = terrain && terrain.userData && terrain.userData.heightAt;
  if (!hAt) return;
  const mw = root.matrixWorld, deckY = mw.elements[13];
  const H = (x, z) => { const w = new THREE.Vector3(x, 0, z).applyMatrix4(mw); return hAt(w.x, w.z) - deckY; };
  const Y = -5.4, W = 2.4, hw = W / 2;
  // the path climbs away from the pavilion door (ref 10: seen from the walker, it runs down toward the bridge at
  // ~10 deg): bridge-floor level at the door, about deck level 30 m further on, +1 m at its far end
  const Yz = z => { const u = Math.min(1, Math.max(0, (z - 9.5) / 40)); return Y + 6.4 * u * u * (3 - 2 * u); };
  // centreline: out of the pavilion's front door, then 1.7 m off the rock contour at the path's level
  const ctl = [new THREE.Vector3(-79.5, Y, 6.1), new THREE.Vector3(-79.7, Y, 9.5)];
  for (let z = 13; z <= 55; z += 3) {
    let xc = -125;
    const yz = Yz(z);
    for (let x = -72; x > -125; x -= 0.25) if (H(x, z) > yz - 0.4) { xc = x; break; }
    ctl.push(new THREE.Vector3(Math.min(xc + 1.7, -79.7), yz, z));
  }
  for (let it = 0; it < 4; it++) for (let i = 2; i < ctl.length - 1; i++) ctl[i].x = (ctl[i - 1].x + 2 * ctl[i].x + ctl[i + 1].x) / 4;
  const curve = new THREE.CatmullRomCurve3(ctl, false, 'centripetal');
  const len = curve.getLength(), N = Math.ceil(len / 0.5) + 1;
  const P = curve.getSpacedPoints(N - 1);
  const A = P.map((p, i) => { const t = P[Math.min(i + 1, N - 1)].clone().sub(P[Math.max(i - 1, 0)]); t.y = 0; t.normalize(); return new THREE.Vector3(-t.z, 0, t.x); }); // across, toward the rock (-X)
  // point across the path (s, toward the rock) at height dy over the deck
  const at = (i, s, dy) => P[i].clone().addScaledVector(A[i], s).setY(P[i].y + dy);
  const UP = new THREE.Vector3(0, 1, 0), DN = new THREE.Vector3(0, -1, 0);
  const pathMat = M.concrete(9, '#a69d90'), snowMat = M.concrete(8, '#cad0de');

  add(strip(N, 1, (i, j) => [at(i, (j * 2 - 1) * hw, 0), UP, [j, i * 0.5]]), pathMat, 'pathDeck');
  add(strip(N, 1, (i, j) => [at(i, (j * 2 - 1) * hw, -0.35), DN, [j, i * 0.5]]), mt.conc, 'pathSoffit');
  for (const s of [-1, 1]) add(strip(N, 1, (i, j) => [at(i, s * hw, -0.35 * (1 - j)), A[i].clone().multiplyScalar(s), [i * 0.5, j]]), mt.conc);
  // balustrades: gorge side (s=-1) hangs 0.3 m below the deck edge
  for (const s of [-1, 1]) {
    const y0 = s < 0 ? -0.3 : 0, off = s * (hw - (s < 0 ? -0.02 : 0.03));
    add(strip(N, 1, (i, j) => [at(i, off, j ? 1.15 : y0), A[i].clone().multiplyScalar(-s), [i * 0.5 / W, j ? 1 : y0 / 1.15]]), mt.railGlass, 'pathGlass');
    const rail = new THREE.CatmullRomCurve3(P.map((_, i) => at(i, off, 1.17)));
    add(new THREE.TubeGeometry(rail, N * 2, 0.045, 8, false), mt.stainless, 'pathRail');
    const posts = [];
    for (let i = 0; i < N; i += 3) {
      const p = at(i, off, 0.575), q = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(1, 0, 0), A[i]);
      posts.push(new THREE.Matrix4().compose(p, q, new THREE.Vector3(0.05, 1.15, 0.06)));
    }
    root.add(instanced(box(1, 1, 1), mt.bronze, posts));
    // snow drift banked against the glass (deeper on the gorge side)
    const rnd = mulberry(s > 0 ? 11 : 23), amp = s < 0 ? 0.36 : 0.22;
    const hgt = []; for (let i = 0; i < N; i++) hgt.push(amp * (0.45 + 0.55 * rnd()));
    for (let it = 0; it < 3; it++) for (let i = 1; i < N - 1; i++) hgt[i] = (hgt[i - 1] + hgt[i] + hgt[i + 1]) / 3;
    // LED line at the glass base, riding just above the drift
    add(strip(N, 1, (i, j) => [at(i, s * (hw - 0.03 - j * 0.04), hgt[i] * 0.9 + 0.02), UP, [j, i]]), mt.led, 'pathLed');
    const prof = [[0, 1], [0.12, 0.9], [0.3, 0.55], [0.5, 0.2], [0.65, 0]];
    const sg = strip(N, prof.length - 1, (i, j) => {
      const [d, k] = prof[j], w = hgt[i] / amp;
      return [at(i, s * (hw - 0.04 - d * (0.35 + 0.4 * w)), hgt[i] * k + 0.004), UP, [d, i * 0.5]];
    });
    sg.computeVertexNormals();
    add(sg, snowMat, 'pathSnow');
  }
  for (const f of [0.15, 0.4, 0.65, 0.9]) {
    const i = Math.round(f * (N - 1));
    lamps.push({ p: at(i, -hw - 0.6, -0.8), c: [1.0, 0.6, 0.3], i: 22, r: 1.6 });
  }
  root.userData.path = P;
}

// concave trumpet flare: wide radius rw at y=0 narrowing to rn at y=-h (opening upward, axis -Y)
function trumpetGeometry(rw, rn, h) {
  const pts = [];
  for (let i = 0; i <= 16; i++) {
    const t = i / 16;
    const r = rn + (rw - rn) * Math.pow(1 - t, 2.4);
    pts.push(new THREE.Vector2(r, -h * t));
  }
  for (const p of pts) p.y -= 0.15;
  pts.unshift(new THREE.Vector2(rw + 0.15, -0.15));
  pts.unshift(new THREE.Vector2(rw + 0.15, 0.0));
  pts.unshift(new THREE.Vector2(0.01, 0.0));
  const g = new THREE.LatheGeometry(pts, 48);
  return g;
}

function mulberry(a) { return () => { a |= 0; a = (a + 0x6D2B79F5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
