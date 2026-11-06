// Small deterministic gradient-noise library (Perlin 2D/3D + fbm/ridged helpers).
function mulberry32(a) {
  return () => { a |= 0; a = (a + 0x6D2B79F5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
}
const rnd = mulberry32(1337);
const P = new Uint8Array(512);
{
  const p = [...Array(256).keys()];
  for (let i = 255; i > 0; i--) { const j = Math.floor(rnd() * (i + 1)); [p[i], p[j]] = [p[j], p[i]]; }
  for (let i = 0; i < 512; i++) P[i] = p[i & 255];
}
const fade = t => t * t * t * (t * (t * 6 - 15) + 10);
const lerp = (a, b, t) => a + (b - a) * t;
function g2(h, x, y) { switch (h & 7) { case 0: return x + y; case 1: return -x + y; case 2: return x - y; case 3: return -x - y; case 4: return x; case 5: return -x; case 6: return y; default: return -y; } }
function g3(h, x, y, z) {
  const hh = h & 15, u = hh < 8 ? x : y, v = hh < 4 ? y : hh === 12 || hh === 14 ? x : z;
  return ((hh & 1) ? -u : u) + ((hh & 2) ? -v : v);
}
export function perlin2(x, y) {
  const X = Math.floor(x), Y = Math.floor(y); x -= X; y -= Y;
  const xi = X & 255, yi = Y & 255, u = fade(x), v = fade(y);
  const a = P[xi] + yi, b = P[xi + 1] + yi;
  return lerp(lerp(g2(P[a], x, y), g2(P[b], x - 1, y), u), lerp(g2(P[a + 1], x, y - 1), g2(P[b + 1], x - 1, y - 1), u), v) * 0.7;
}
export function perlin3(x, y, z) {
  const X = Math.floor(x), Y = Math.floor(y), Z = Math.floor(z); x -= X; y -= Y; z -= Z;
  const xi = X & 255, yi = Y & 255, zi = Z & 255, u = fade(x), v = fade(y), w = fade(z);
  const A = P[xi] + yi, AA = P[A] + zi, AB = P[A + 1] + zi, B = P[xi + 1] + yi, BA = P[B] + zi, BB = P[B + 1] + zi;
  return lerp(
    lerp(lerp(g3(P[AA], x, y, z), g3(P[BA], x - 1, y, z), u), lerp(g3(P[AB], x, y - 1, z), g3(P[BB], x - 1, y - 1, z), u), v),
    lerp(lerp(g3(P[AA + 1], x, y, z - 1), g3(P[BA + 1], x - 1, y, z - 1), u), lerp(g3(P[AB + 1], x, y - 1, z - 1), g3(P[BB + 1], x - 1, y - 1, z - 1), u), v), w);
}
export function fbm2(x, y, oct = 5, lac = 2.03, gain = 0.5) {
  let s = 0, a = 1, n = 0;
  for (let i = 0; i < oct; i++) { s += a * perlin2(x, y); n += a; x = x * lac + 17.3; y = y * lac - 9.1; a *= gain; }
  return s / n;
}
export function fbm3(x, y, z, oct = 5, lac = 2.03, gain = 0.5) {
  let s = 0, a = 1, n = 0;
  for (let i = 0; i < oct; i++) { s += a * perlin3(x, y, z); n += a; x = x * lac + 17.3; y = y * lac - 9.1; z = z * lac + 3.7; a *= gain; }
  return s / n;
}
// ridged multifractal in [0,1]-ish, sharp crests
export function ridged3(x, y, z, oct = 5, lac = 2.1, gain = 0.55) {
  let s = 0, a = 1, n = 0, w = 1;
  for (let i = 0; i < oct; i++) {
    let r = 1 - Math.abs(perlin3(x, y, z) * 1.6); r = r * r * w; w = Math.min(1, r * 1.5);
    s += a * r; n += a; x = x * lac + 17.3; y = y * lac - 9.1; z = z * lac + 3.7; a *= gain;
  }
  return s / n;
}
export const smoothstep = (a, b, x) => { const t = Math.min(1, Math.max(0, (x - a) / (b - a))); return t * t * (3 - 2 * t); };
export const smin = (a, b, k) => { const h = Math.max(k - Math.abs(a - b), 0) / k; return Math.min(a, b) - h * h * k * 0.25; };
export const smax = (a, b, k) => -smin(-a, -b, k);
export { mulberry32 };
