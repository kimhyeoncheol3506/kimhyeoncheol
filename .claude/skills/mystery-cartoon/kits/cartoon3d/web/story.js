// "로마 제9군단 실종" sample — timed to voice.wav (11.75 s, 30 fps, 353 frames).
// words (s): 서기0.00 2세기0.34 로마0.84 최정예1.17 제9군단이1.68 기록에서2.51 사라졌습니다3.18 | 오천4.47 명의4.93 병사5.40 그런데5.87 전투6.56 기록도7.03 시신도7.73 없었죠8.43 | 그들은9.41 대체9.99 어디로10.39 간10.97 걸까요11.17
export const FPS = 30, TOTAL = 353, DECK = 6;
export const SHOTS = [
  { id: 'hook', a: 0, b: 71, light: 'golden' },
  { id: 'march', a: 72, b: 133, light: 'mist' },
  { id: 'army', a: 134, b: 175, light: 'golden' },
  { id: 'empty', a: 176, b: 282, light: 'night' },
  { id: 'fog', a: 283, b: 352, light: 'mist2' },
];
export const shotAt = (f) => SHOTS.find((s) => f >= s.a && f <= s.b) || SHOTS[SHOTS.length - 1];

const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
export const smooth = (t) => { t = clamp(t); return t * t * t * (t * (t * 6 - 15) + 10); };
const lerp = (a, b, t) => a + (b - a) * t;
const lerp3 = (a, b, t) => a.map((v, i) => lerp(v, b[i], t));
const ramp = (f, a, b) => clamp((f - a) / (b - a));

// ---------- lights ----------
const W_ = { waterDeep: '#2c6c8c', waterShal: '#5aaec4', glint: '#effaff' };
export const LIGHTS = {
  golden: { az: 8, el: 9, sky: '#9a90c8', ground: '#6a4c40', hemi: 1.0, sun: '#ffb46c', sunI: 2.9, fog: '#f0b88c', fogNear: 40, fogFar: 520,
    skyTop: '#6f6eb0', skyHor: '#ffc27e', sunDisc: '#fff0c8', sunSize: 0.0035, sat: 1.12, gain: '#fff2e2', waterDeep: '#3d5a86', waterShal: '#d99a6e',
    glint: '#ffe2a8', vig: 0.28, shadowExt: 22 },
  mist: { az: 150, el: 28, sky: '#c9d2dc', ground: '#6f735f', hemi: 1.3, sun: '#f6efe2', sunI: 1.4, fog: '#c4ccd4', fogNear: 5, fogFar: 42,
    skyTop: '#93a3b6', skyHor: '#d3dae0', sat: 0.92, vig: 0.3, shadowExt: 25, ...W_ },
  mist2: { az: 200, el: 22, sky: '#8796c4', ground: '#2c3150', hemi: 1.15, sun: '#c6d2ff', sunI: 1.0, fog: '#7f8db8', fogNear: 4, fogFar: 36,
    skyTop: '#2a3466', skyHor: '#8a98c2', sunDisc: '#eef2ff', sunSize: 0.002, sat: 0.95, gain: '#e4e9ff', vig: 0.4, shadowExt: 20, ...W_ },
  night: { az: 210, el: 34, sky: '#5b6fb0', ground: '#1d2440', hemi: 1.0, sun: '#a9bcff', sunI: 1.3, fog: '#2e3d70', fogNear: 18, fogFar: 150,
    skyTop: '#0e1638', skyHor: '#3d528e', sunDisc: '#eef2ff', sunSize: 0.0025, sat: 1.05, gain: '#dfe6ff', vig: 0.36, shadowExt: 22, ...W_ },
};
export const lightFor = (S, f) => ({ ...LIGHTS[S.light] });

// ---------- cameras ----------
const HERO = [-30, DECK, 0];
const CAMS = {
  hook: [
    { f: 0, pos: [-27.9, 7.36, 0.9], look: [-30, 7.3, 0], fov: 32 },
    { f: 14, pos: [-28.0, 7.36, 0.85], look: [-30, 7.3, 0], fov: 31 },
    { f: 60, pos: [-22.5, 9.6, 6.5], look: [-33, 6.6, 0], fov: 46, roll: -2 },
    { f: 71, pos: [-22.3, 9.7, 6.7], look: [-33, 6.6, 0], fov: 45, roll: -2 },
  ],
  march: [
    { f: 72, pos: [-33, 7.4, -9.5], look: [-37, 7.0, 0], fov: 42 },
    { f: 133, pos: [-38, 7.7, -9.0], look: [-45, 6.9, 0], fov: 39 },
  ],
  army: [
    { f: 134, pos: [-22.5, 16.5, 10.5], look: [-37, 6.0, 0], fov: 46 },
    { f: 175, pos: [-24, 14.8, 9.0], look: [-37, 6.2, 0], fov: 42 },
  ],
  empty: [
    { f: 176, pos: [-24, 14.8, 9.0], look: [-37, 6.2, 0], fov: 42 },
    { f: 200, pos: [-25.5, 13.5, 8.0], look: [-37, 6.2, 0.3], fov: 42 },
    { f: 240, pos: [-34.0, 7.6, 3.4], look: [-37, 6.15, 0.5], fov: 36 },
    { f: 282, pos: [-35.6, 6.75, 1.7], look: [-37, 6.12, 0.5], fov: 30, roll: -3 },
  ],
  fog: [
    { f: 283, pos: [2, 7.6, 0.5], look: [60, 7.6, 0], fov: 42 },
    { f: 320, pos: [7, 7.6, 0.3], look: [60, 7.6, 0], fov: 37, roll: 1.5 },
    { f: 352, pos: [12, 7.6, 0.2], look: [60, 7.55, 0], fov: 31, roll: 4 },
  ],
};
const KICKS = [{ f: 176, a: 0.03 }, { f: 336, a: 0.05 }];
export const camAt = (f) => {
  const S = shotAt(f), K = CAMS[S.id];
  let c;
  if (f <= K[0].f) c = { ...K[0] };
  else if (f >= K[K.length - 1].f) c = { ...K[K.length - 1] };
  else for (let i = 0; i < K.length - 1; i++) if (f >= K[i].f && f <= K[i + 1].f) {
    const t = smooth((f - K[i].f) / (K[i + 1].f - K[i].f)), a = K[i], b = K[i + 1];
    c = { pos: lerp3(a.pos, b.pos, t), look: lerp3(a.look, b.look, t), fov: lerp(a.fov, b.fov, t), roll: lerp(a.roll || 0, b.roll || 0, t) };
  }
  for (const k of KICKS) { const d = f - k.f; if (d >= 0 && d < 7) { const s = (d % 2 ? -1 : 1) * k.a * (1 - d / 7); c.look = [c.look[0], c.look[1] + s * 3, c.look[2] + s * 2]; c.roll = (c.roll || 0) + s * 20; } }
  c.flash = f >= 72 && f < 78 ? (1 - (f - 72) / 6) * 0.6 : f >= 176 && f < 182 ? (1 - (f - 176) / 6) * 0.85 : f >= 283 && f < 288 ? (1 - (f - 283) / 5) * 0.4 : 0;
  c.shadowAt = S.id === 'march' ? [-40, 6, 0] : S.id === 'fog' ? [20, 6, 0] : [-35, 6, 0];
  return c;
};

// ---------- lens ----------
const dist = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);
export const dofAt = (f) => {
  const S = shotAt(f), C = camAt(f);
  switch (S.id) {
    case 'hook': return { focus: dist(C.pos, [-30, 7.3, 0]), cinf: lerp(13, 2, smooth(ramp(f, 14, 50))) };
    case 'march': return { focus: dist(C.pos, [-38, 7, 0]), cinf: 4 };
    case 'army': return { focus: 20, cinf: 0 };
    case 'empty': return { focus: dist(C.pos, [-37, 6.15, 0.5]), cinf: lerp(0, 13, smooth(ramp(f, 210, 250))) };
    case 'fog': return { focus: dist(C.pos, [30, 7, 0]), cinf: 5 };
  }
  return { focus: 10, cinf: 0 };
};

// ---------- world state ----------
export const worldAt = (f) => {
  const S = shotAt(f);
  const W = { collapse: 0, banner: 'gone', bannerFall: 0, old: S.id === 'empty' || S.id === 'fog', braceFall: 0, helmet: null };
  if (S.id === 'empty') W.helmet = { x: -37, y: DECK + 0.14, z: 0.5, rx: 0.25, ry: 0.9, rz: 1.75, s: 0.19 };
  return W;
};

// ---------- actors (2D cards) ----------
const blinkAt = (f, seed) => { const per = 38 + (seed * 17) % 31, ph = (f + seed * 13) % per; return ph < 2 ? 0.5 : ph < 4 ? 1 : 0; };
const R = (T, who, o, pos, extra = {}) => ({ key: who + JSON.stringify(o), draw: (p) => T.romanFront(p, who, o), x: pos[0], y: pos[1], z: pos[2], ...extra });
const q = (x, n = 2) => Math.round(x * 10 ** n) / 10 ** n;

export const actorsAt = (f, T) => {
  const S = shotAt(f), out = [];
  const tint = S.light === 'golden' ? '#ffe2c8' : S.light === 'mist' ? '#e8edf2' : '#c8d2ff';
  switch (S.id) {
    case 'hook': {
      // hero legionary close-up, then the ranks behind him revealed
      out.push(R(T, 'legion', { L: 'shield', expr: f > 52 ? 'squint' : 'stern', seed: 3, blink: blinkAt(f, 3), look: f < 30 ? 0 : 0.25, bob: q(Math.sin(f * 0.12) * 0.006, 3) }, HERO, { tint }));
      for (let r = 0; r < 3; r++) for (const z of [-1.7, 0, 1.7]) {
        const sd = 4 + r * 3 + (z > 0 ? 2 : z < 0 ? 1 : 0);
        out.push(R(T, 'legion', { L: 'shield', expr: 'stern', seed: sd, blink: blinkAt(f, sd), look: 0.2 }, [-32.2 - r * 1.9, DECK, z], { tint }));
      }
      break;
    }
    case 'march': {
      // column marching left into the mist; on "사라졌습니다" they fade out front-to-back
      for (let i = 0; i < 12; i++) {
        const file = i % 2, row = Math.floor(i / 2);
        const x = -33 - row * 1.7 - (f - 72) * 0.055, z = file ? 0.85 : -0.85;
        const fadeStart = 92 + row * 4;
        const alpha = 1 - smooth(ramp(f, fadeStart, fadeStart + 14));
        if (alpha <= 0.01) continue;
        const sd = 20 + i;
        out.push(R(T, 'legion', { L: 'shield', expr: 'stern', seed: sd, facing: -1, step: q(((f * 0.055 * 1.1 + i * 0.23) % 1), 2) }, [x, DECK, z], { tint, alpha: q(alpha, 2) }));
      }
      break;
    }
    case 'army': {
      // the whole legion in formation (5,000 men)
      for (let r = 0; r < 6; r++) for (let c = 0; c < 6; c++) {
        const sd = 40 + ((r * 6 + c) % 5);
        out.push(R(T, 'legion', { L: 'shield', expr: 'stern', seed: sd, look: 0.3 }, [-31 - r * 2.2, DECK, -4.2 + c * 1.7], { tint, bob: 0 }));
      }
      break;
    }
    case 'fog': {
      // one last faint figure walking away into the fog
      const a = 0.75 * (1 - smooth(ramp(f, 300, 340)));
      if (a > 0.01) out.push(R(T, 'legion', { L: 'shield', expr: 'stern', seed: 9, facing: 1, step: q((f * 0.05) % 1, 2) }, [27 + (f - 283) * 0.05, DECK, 0.2], { tint, alpha: q(a, 2) }));
      break;
    }
  }
  return out;
};

// ---------- 2D effects ----------
const FX = (key, draw, pos, s, extra = {}) => ({ key, draw, x: pos[0], y: pos[1], z: pos[2], s, blob: false, shadow: false, order: 5, ...extra });
export const fxAt = (f, T) => {
  const S = shotAt(f), out = [];
  if (S.id === 'hook' || S.id === 'empty') { // drifting leaves = wind over the field
    for (let i = 0; i < 7; i++) {
      const t = ((f * 0.011 + i / 7) % 1), cols = ['#d9822b', '#c4452c', '#e6b13a'];
      const x = -27 - t * 8 + Math.sin(i * 3.1) * 0.6, y = DECK + 2.6 - t * 2.6 + Math.sin(t * 9 + i) * 0.25, z = -2 + i * 0.6;
      out.push(FX('leaf' + i % 3, (p) => T.fxLeaf(p, cols[i % 3]), [x, y, z], 0.12, { roll: q(t * 8 + i, 1), tint: S.id === 'empty' ? '#8fa0e0' : '#ffffff' }));
    }
  }
  return out;
};
