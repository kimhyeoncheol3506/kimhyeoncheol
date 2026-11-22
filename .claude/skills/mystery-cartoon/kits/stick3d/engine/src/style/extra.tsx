// Extra reusable props + helpers (v4). Logged in rules/ACTION-LIBRARY.md.
import React, { useMemo } from "react";
import * as THREE from "three";
import { useThree } from "@react-three/fiber";
import { LineSegments2 } from "three/examples/jsm/lines/LineSegments2.js";
import { LineSegmentsGeometry } from "three/examples/jsm/lines/LineSegmentsGeometry.js";
import { LineMaterial } from "three/examples/jsm/lines/LineMaterial.js";
import { Box, Cyl, Ball, CanvasPlane, INK } from "./toon";
import { V3, lerp, clamp } from "./kit";
import { Glow } from "./props";

const ramp = (() => { const d = new Uint8Array([90, 170, 255]); const t = new THREE.DataTexture(d, 3, 1, THREE.RedFormat); t.minFilter = t.magFilter = THREE.NearestFilter; t.needsUpdate = true; return t; })();

/* ---------- camera ---------- */
export type Key = { t: number; pos: V3; look: V3; fov?: number; roll?: number };
const cr = (p0: number, p1: number, p2: number, p3: number, u: number) => 0.5 * (2 * p1 + (-p0 + p2) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u * u + (-p0 + 3 * p1 - 3 * p2 + p3) * u * u * u);
const smooth = (u: number) => u * u * (3 - 2 * u);
// Catmull-Rom camera path through keys (smooth, no stop-go); first/last segment eased.
export function camAt(t: number, keys: Key[]) {
  const n = keys.length; if (t <= keys[0].t) return keys[0]; if (t >= keys[n - 1].t) return keys[n - 1];
  let i = 0; while (i < n - 2 && t > keys[i + 1].t) i++;
  let u = (t - keys[i].t) / (keys[i + 1].t - keys[i].t);
  // ease in on the first segment, ease out on the last (velocity-continuous at inner keys)
  if (n === 2) u = smooth(u); else if (i === 0) u = 2 * u * u - u * u * u; else if (i === n - 2) u = u + u * u - u * u * u;
  const a = keys[Math.max(0, i - 1)], b = keys[i], c = keys[i + 1], d = keys[Math.min(n - 1, i + 2)];
  const v = (k: "pos" | "look") => [0, 1, 2].map((j) => cr(a[k][j], b[k][j], c[k][j], d[k][j], u)) as V3;
  return { t, pos: v("pos"), look: v("look"), fov: lerp(b.fov ?? 62, c.fov ?? 62, smooth(u)), roll: lerp(b.roll ?? 0, c.roll ?? 0, smooth(u)) };
}
// Camera: path + micro handheld (<=0.004) + optional in-story impact shake [time, amplitude] decaying < 0.5 s
export const Cam: React.FC<{ t: number; keys: Key[]; impacts?: [number, number][]; quake?: number; fovKick?: number[] }> = ({ t, keys, impacts = [], quake = 0, fovKick = [] }) => {
  const { camera } = useThree();
  const k = camAt(t, keys);
  let sh = quake; for (const [ti, a] of impacts) if (t >= ti && t < ti + 0.5) sh += a * Math.exp(-(t - ti) * 9);
  let fk = 0; for (const ti of fovKick) if (t >= ti) fk += Math.exp(-(t - ti) * 5) * clamp((t - ti) / 0.06);
  const h = 0.004;
  camera.position.set(k.pos[0] + Math.sin(t * 1.7) * h + Math.sin(t * 57) * sh, k.pos[1] + Math.sin(t * 2.3 + 1) * h + Math.cos(t * 49) * sh, k.pos[2] + Math.sin(t * 1.3) * h);
  const cam = camera as THREE.PerspectiveCamera; cam.fov = (k.fov ?? 62) - fk * 5; cam.near = 0.1; cam.far = 200; cam.updateProjectionMatrix();
  camera.up.set(Math.sin(k.roll ?? 0), Math.cos(k.roll ?? 0), 0);
  camera.lookAt(k.look[0], k.look[1], k.look[2]);
  return null;
};

/* ---------- held props: group that turns (yaw only) with the puppet billboard ---------- */
export const FaceGroup: React.FC<{ p: V3; children: React.ReactNode }> = ({ p, children }) => {
  const { camera } = useThree(); const ref = React.useRef<THREE.Group>(null);
  React.useLayoutEffect(() => { if (ref.current) ref.current.rotation.y = Math.atan2(camera.position.x - p[0], camera.position.z - p[2]); });
  return <group ref={ref} position={p}>{children}</group>;
};
// local position of an IK hand target (same units as Pose.armR) for a puppet of height h
export const hand = (h: number, tgt: [number, number], sq = 0, flip = false, dz = 0.06): V3 => [(flip ? -1 : 1) * tgt[0] * h * (1 - sq * 0.55), tgt[1] * h * (1 + sq), dz];

/* ---------- outlined extrusion (any polygon) ---------- */
export const Extrude: React.FC<{ pts: [number, number][]; depth: number; color: string; p?: V3; rot?: V3; s?: number; line?: number }> = ({ pts, depth, color, p = [0, 0, 0], rot = [0, 0, 0], s = 1, line = 4 }) => {
  const { size } = useThree();
  const geo = useMemo(() => { const sh = new THREE.Shape(pts.map(([x, y]) => new THREE.Vector2(x, y))); const g = new THREE.ExtrudeGeometry(sh, { depth, bevelEnabled: false }); g.translate(0, 0, -depth / 2); return g; }, [JSON.stringify(pts), depth]);
  const seg = useMemo(() => { const e = new LineSegmentsGeometry(); e.setPositions(new THREE.EdgesGeometry(geo, 30).attributes.position.array as Float32Array); return new LineSegments2(e, new LineMaterial({ color: new THREE.Color(INK).getHex(), linewidth: line, resolution: new THREE.Vector2(size.width, size.height) })); }, [geo, size, line]);
  return <group position={p} rotation={rot} scale={s}><mesh geometry={geo}><meshToonMaterial color={color} gradientMap={ramp} /></mesh><primitive object={seg} /></group>;
};
// Big 3D arrow, tip at +y (length L centred on origin)
export const Arrow3D: React.FC<{ p: V3; rot?: V3; L?: number; color?: string; depth?: number }> = ({ p, rot, L = 3.4, color = "#2fd46a", depth = 0.5 }) => {
  const hw = 0.82, sw = 0.36, hb = L / 2 - 1.15;
  return <Extrude p={p} rot={rot} depth={depth} color={color} line={5} pts={[[0, L / 2], [hw, hb], [sw, hb], [sw, -L / 2], [-sw, -L / 2], [-sw, hb], [-hw, hb]]} />;
};

/* ---------- domino (pivots on its leading bottom edge; falls toward local +x) ---------- */
export const Domino: React.FC<{ p: V3; yaw?: number; h: number; w: number; th: number; ang: number; label?: string; pips?: number; face?: string; small?: boolean }> = ({ p, yaw = 0, h, w, th, ang, label, pips = 0, face = "#fbf4e2", small }) => (
  <group position={p} rotation={[0, yaw, 0]}>
    <group position={[th / 2, 0, 0]} rotation={[0, 0, -ang]}>
      <Box p={[-th / 2, h / 2, 0]} s={[th, h, w]} color={face} line={small ? 2 : 4} />
      {!small ? <CanvasPlane p={[-th - 0.012, h / 2, 0]} rot={[0, -Math.PI / 2, 0]} s={[w * 0.92, h * 0.95]} px={[240, Math.round(240 * h / w)]} draw={(c, W, H) => {
        c.fillStyle = face; c.fillRect(0, 0, W, H); c.strokeStyle = INK; c.lineWidth = 10; c.beginPath(); c.moveTo(W * 0.12, H / 2); c.lineTo(W * 0.88, H / 2); c.stroke();
        c.fillStyle = "#1a2350"; c.font = `900 ${W * 0.36}px Inter, Arial`; c.textAlign = "center"; c.textBaseline = "middle"; if (label) c.fillText(label, W / 2, H * 0.25);
        c.fillStyle = "#e5233a"; const r = W * 0.07; const cols = pips > 3 ? 2 : 1, rows = Math.ceil(pips / cols);
        for (let i = 0; i < pips; i++) { const cx = cols === 1 ? W / 2 : W * (i % 2 ? 0.68 : 0.32), cy = H * 0.58 + (Math.floor(i / cols) + 0.5) * (H * 0.36 / rows); c.beginPath(); c.arc(cx, cy, r, 0, 7); c.fill(); }
      }} /> : <Box p={[-th - 0.01, h / 2, 0]} s={[0.02, 0.05, w * 0.7]} color={INK} line={1} />}
    </group>
  </group>
);

/* ---------- globe with procedural continents ---------- */
export const Globe: React.FC<{ p: V3; r: number; rotY?: number; tilt?: number }> = ({ p, r, rotY = 0, tilt = 0.25 }) => {
  const tex = useMemo(() => {
    const c = document.createElement("canvas"); c.width = 1024; c.height = 512; const g = c.getContext("2d")!;
    const grd = g.createLinearGradient(0, 0, 0, 512); grd.addColorStop(0, "#2f7de0"); grd.addColorStop(0.5, "#1f62d0"); grd.addColorStop(1, "#2f7de0"); g.fillStyle = grd; g.fillRect(0, 0, 1024, 512);
    const blobs: [number, number, number, number][] = [[180, 160, 120, 90], [240, 300, 70, 120], [520, 150, 110, 70], [560, 290, 80, 120], [760, 170, 170, 90], [850, 360, 70, 50], [430, 60, 60, 25], [980, 140, 60, 50], [60, 120, 50, 60]];
    for (const [x, y, rx, ry] of blobs) { g.fillStyle = "#3fbf5a"; g.strokeStyle = INK; g.lineWidth = 6; g.beginPath(); for (let k = 0; k <= 40; k++) { const a = (k / 40) * Math.PI * 2, w = 1 + 0.22 * Math.sin(a * 3 + x) + 0.12 * Math.sin(a * 7 + y); const px = x + Math.cos(a) * rx * w, py = y + Math.sin(a) * ry * w; k ? g.lineTo(px, py) : g.moveTo(px, py); } g.closePath(); g.fill(); g.stroke(); g.fillStyle = "#7ad66a"; g.beginPath(); g.ellipse(x - rx * 0.2, y - ry * 0.2, rx * 0.35, ry * 0.3, 0.3, 0, 7); g.fill(); }
    g.strokeStyle = "rgba(255,255,255,.18)"; g.lineWidth = 3; for (let k = 1; k < 6; k++) { g.beginPath(); g.moveTo(0, k * 512 / 6); g.lineTo(1024, k * 512 / 6); g.stroke(); } for (let k = 0; k < 12; k++) { g.beginPath(); g.moveTo(k * 1024 / 12, 0); g.lineTo(k * 1024 / 12, 512); g.stroke(); }
    g.fillStyle = "#f2f6ff"; g.fillRect(0, 0, 1024, 26); g.fillRect(0, 490, 1024, 22);
    const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; return t;
  }, []);
  return (<group position={p} rotation={[tilt * 0.3, 0, tilt]}>
    <mesh rotation={[0, rotY, 0]}><sphereGeometry args={[r, 64, 40]} /><meshToonMaterial map={tex} gradientMap={ramp} /></mesh>
    <mesh><sphereGeometry args={[r + 0.12, 48, 32]} /><meshBasicMaterial color={INK} side={THREE.BackSide} /></mesh>
  </group>);
};

/* ---------- crown ---------- */
export const Crown: React.FC<{ p: V3; s?: number; rot?: V3 }> = ({ p, s = 1, rot }) => (
  <group position={p} scale={s} rotation={rot}>
    <Cyl p={[0, 0.16, 0]} rt={0.46} rb={0.42} h={0.32} color="#ffc928" line={3} />
    {[0, 1, 2, 3, 4].map((i) => { const a = (i / 5) * Math.PI * 2; return <React.Fragment key={i}><Cyl p={[Math.sin(a) * 0.38, 0.5, Math.cos(a) * 0.38]} rt={0.0} rb={0.14} h={0.4} color="#ffc928" line={2} /><Ball p={[Math.sin(a) * 0.4, 0.74, Math.cos(a) * 0.4]} r={0.07} color="#fff3a0" ink={0.03} /></React.Fragment>; })}
    <Ball p={[0, 0.17, 0.45]} r={0.1} color="#e5233a" ink={0.03} /><Ball p={[0.33, 0.17, 0.32]} r={0.08} color="#2f8cff" ink={0.03} /><Ball p={[-0.33, 0.17, 0.32]} r={0.08} color="#2fd46a" ink={0.03} />
  </group>
);

/* ---------- throne (seat top at y = 1.6 above base) ---------- */
export const Throne: React.FC<{ p: V3; rot?: V3; red?: string; gold?: string }> = ({ p, rot, red = "#a0202e", gold = "#ffc23a" }) => (
  <group position={p} rotation={rot}>
    <Box p={[0, 0.2, 0]} s={[3.0, 0.4, 2.6]} color={gold} /><Box p={[0, 1.0, 0.1]} s={[2.4, 1.2, 2.0]} color={red} />
    <Box p={[0, 3.0, -0.8]} s={[2.6, 3.6, 0.45]} color={red} /><Box p={[0, 4.95, -0.8]} s={[3.0, 0.4, 0.6]} color={gold} />
    <Ball p={[-1.35, 5.3, -0.8]} r={0.24} color={gold} /><Ball p={[1.35, 5.3, -0.8]} r={0.24} color={gold} /><Ball p={[0, 5.45, -0.8]} r={0.32} color="#2fd46a" />
    <Box p={[-1.45, 1.9, 0.1]} s={[0.4, 1.0, 2.0]} color={gold} /><Box p={[1.45, 1.9, 0.1]} s={[0.4, 1.0, 2.0]} color={gold} />
    <CanvasPlane p={[0, 3.2, -0.56]} s={[1.6, 1.0]} px={[320, 200]} draw={(c, W, H) => { c.fillStyle = red; c.fillRect(0, 0, W, H); c.fillStyle = gold; c.font = "900 120px Inter, Arial"; c.textAlign = "center"; c.textBaseline = "middle"; c.fillText("AI", W / 2, H / 2 + 6); }} />
  </group>
);

/* ---------- light cone (additive), curtain, lectern ---------- */
export const SpotCone: React.FC<{ p: V3; h: number; r: number; color?: string; o?: number; rot?: V3 }> = ({ p, h, r, color = "#fff2c0", o = 0.16, rot }) => (
  <group position={p} rotation={rot}><mesh position={[0, -h / 2, 0]}><coneGeometry args={[r, h, 32, 1, true]} /><meshBasicMaterial color={color} transparent opacity={o} blending={THREE.AdditiveBlending} depthWrite={false} side={THREE.DoubleSide} /></mesh></group>
);
export const Curtain: React.FC<{ p: V3; s: [number, number]; color?: string; rot?: V3; folds?: number }> = ({ p, s, color = "#b3122e", rot, folds = 7 }) => (
  <CanvasPlane p={p} s={s} rot={rot} px={[Math.round(s[0] * 60), Math.round(s[1] * 60)]} draw={(c, W, H) => {
    c.fillStyle = color; c.fillRect(0, 0, W, H); const fw = W / folds;
    for (let i = 0; i < folds; i++) { const g = c.createLinearGradient(i * fw, 0, (i + 1) * fw, 0); g.addColorStop(0, "rgba(0,0,0,.42)"); g.addColorStop(0.45, "rgba(255,255,255,.16)"); g.addColorStop(1, "rgba(0,0,0,.30)"); c.fillStyle = g; c.fillRect(i * fw, 0, fw, H); }
    c.strokeStyle = INK; c.lineWidth = 4; c.strokeRect(2, 2, W - 4, H - 4); c.fillStyle = "#ffc23a"; c.fillRect(0, H - 14, W, 10);
  }} />
);
export const Lectern: React.FC<{ p: V3; h?: number; color?: string; label?: string }> = ({ p, h = 1.6, color = "#2a1846", label = "AI" }) => (
  <group position={p}>
    <Box p={[0, h / 2, 0]} s={[1.3, h, 0.8]} color={color} /><Box p={[0, h + 0.06, 0.05]} s={[1.5, 0.12, 1.0]} color="#ffc23a" rot={[0.18, 0, 0]} />
    <Box p={[0, 0.05, 0]} s={[1.6, 0.1, 1.0]} color="#1a0f2e" line={2} />
    <Cyl p={[-0.5, h + 0.14, 0.25]} rt={0.03} h={0.25} color="#9aa0b8" line={2} rot={[0.4, 0, 0]} /><Ball p={[-0.5, h + 0.28, 0.3]} r={0.08} color="#2b3350" ink={0.03} />
    <CanvasPlane p={[0, h * 0.58, 0.41]} s={[0.95, 0.6]} px={[240, 150]} draw={(c, W, H) => { c.fillStyle = "#2fd46a"; c.fillRect(0, 0, W, H); c.strokeStyle = INK; c.lineWidth = 10; c.strokeRect(5, 5, W - 10, H - 10); c.fillStyle = "#08121a"; c.font = "900 92px Inter, Arial"; c.textAlign = "center"; c.textBaseline = "middle"; c.fillText(label, W / 2, H / 2 + 4); }} />
  </group>
);

/* ---------- city / street ---------- */
export const Building: React.FC<{ p: V3; s: V3; color: string; face?: "+x" | "-x" | "+z"; seed?: number; lit?: number; trim?: string }> = ({ p, s, color, face = "+z", seed = 1, lit = 0.35, trim = "#2b2244" }) => {
  const [w, h, d] = s; const fw = face === "+z" ? w : d;
  const fp: V3 = face === "+z" ? [0, h / 2, d / 2 + 0.02] : face === "+x" ? [w / 2 + 0.02, h / 2, 0] : [-w / 2 - 0.02, h / 2, 0];
  const fr: V3 = face === "+z" ? [0, 0, 0] : face === "+x" ? [0, Math.PI / 2, 0] : [0, -Math.PI / 2, 0];
  return (<group position={p}>
    <Box p={[0, h / 2, 0]} s={s} color={color} /><Box p={[0, h + 0.2, 0]} s={[w + 0.3, 0.4, d + 0.3]} color={trim} line={3} />
    <CanvasPlane p={fp} rot={fr} s={[fw * 0.96, h * 0.96]} px={[Math.round(fw * 26), Math.round(h * 26)]} draw={(c, W, H) => {
      c.clearRect(0, 0, W, H); const cw = 20, chh = 28; let n = seed * 17;
      for (let y = 24; y < H - 40; y += chh + 14) for (let x = 14; x < W - cw - 6; x += cw + 12) { n = (n * 9301 + 49297) % 233280; const on = n / 233280 < lit; c.fillStyle = on ? "#ffd770" : "rgba(30,24,60,.75)"; c.fillRect(x, y, cw, chh); c.strokeStyle = INK; c.lineWidth = 2; c.strokeRect(x, y, cw, chh); }
    }} />
  </group>);
};
export const StreetLamp: React.FC<{ p: V3; h?: number; on?: number; flip?: boolean }> = ({ p, h = 5.2, on = 1, flip }) => (
  <group position={p} rotation={[0, flip ? Math.PI : 0, 0]}>
    <Cyl p={[0, h / 2, 0]} rt={0.09} rb={0.14} h={h} color="#2b3350" line={2} /><Box p={[0.45, h, 0]} s={[1.0, 0.1, 0.1]} color="#2b3350" line={2} />
    <Cyl p={[0.9, h - 0.15, 0]} rt={0.12} rb={0.32} h={0.3} color="#ffe9a8" line={2} />{on > 0 ? <Glow p={[0.9, h - 0.35, 0]} r={1.1} color="rgba(255,220,140,1)" o={0.55 * on} /> : null}
  </group>
);
export const StreetSign: React.FC<{ p: V3; a: string; b?: string; h?: number }> = ({ p, a, b, h = 4.2 }) => (
  <group position={p}>
    <Cyl p={[0, h / 2, 0]} rt={0.07} h={h} color="#2b3350" line={2} />
    <CanvasPlane p={[0, h - 0.1, 0.06]} s={[2.4, 0.5]} px={[480, 100]} frame="#f2f2f2" draw={(c, W, H) => { c.fillStyle = "#11804a"; c.fillRect(0, 0, W, H); c.strokeStyle = "#fff"; c.lineWidth = 6; c.strokeRect(8, 8, W - 16, H - 16); c.fillStyle = "#fff"; c.font = "900 64px Inter, Arial"; c.textAlign = "center"; c.textBaseline = "middle"; c.fillText(a, W / 2, H / 2 + 3); }} />
    {b ? <CanvasPlane p={[0.06, h - 0.7, 0]} rot={[0, Math.PI / 2, 0]} s={[2.0, 0.45]} px={[400, 90]} frame="#f2f2f2" draw={(c, W, H) => { c.fillStyle = "#11804a"; c.fillRect(0, 0, W, H); c.fillStyle = "#fff"; c.font = "900 56px Inter, Arial"; c.textAlign = "center"; c.textBaseline = "middle"; c.fillText(b, W / 2, H / 2 + 3); }} /> : null}
  </group>
);
export const Taxi: React.FC<{ p: V3; rotY?: number; color?: string }> = ({ p, rotY = 0, color = "#ffc928" }) => (
  <group position={p} rotation={[0, rotY, 0]}>
    <Box p={[0, 0.75, 0]} s={[4.2, 0.9, 1.9]} color={color} /><Box p={[-0.2, 1.55, 0]} s={[2.4, 0.75, 1.7]} color={color} />
    <Box p={[-0.2, 1.55, 0.86]} s={[2.1, 0.5, 0.02]} color="#9fd4ff" line={2} /><Box p={[-0.2, 1.55, -0.86]} s={[2.1, 0.5, 0.02]} color="#9fd4ff" line={2} />
    <Box p={[-0.2, 2.05, 0]} s={[0.7, 0.25, 0.4]} color="#fff" line={2} /><Box p={[0, 0.85, 0.96]} s={[4.0, 0.12, 0.02]} color="#111" line={1} />
    {[-1.3, 1.3].map((x) => [-0.9, 0.9].map((z) => <Cyl key={x + "," + z} p={[x, 0.42, z]} rt={0.42} h={0.3} color="#1b1b2a" rot={[Math.PI / 2, 0, 0]} />))}
    <Box p={[2.12, 0.85, 0.6]} s={[0.06, 0.2, 0.35]} color="#fff6c0" line={2} /><Box p={[2.12, 0.85, -0.6]} s={[0.06, 0.2, 0.35]} color="#fff6c0" line={2} />
  </group>
);
export const Hydrant: React.FC<{ p: V3 }> = ({ p }) => (<group position={p}><Cyl p={[0, 0.45, 0]} rt={0.22} h={0.9} color="#e5233a" /><Ball p={[0, 0.92, 0]} r={0.22} color="#e5233a" /><Cyl p={[0, 0.55, 0]} rt={0.09} h={0.7} color="#c01a2e" rot={[0, 0, Math.PI / 2]} /></group>);
export const Bench: React.FC<{ p: V3; rotY?: number }> = ({ p, rotY = 0 }) => (<group position={p} rotation={[0, rotY, 0]}><Box p={[0, 0.75, 0]} s={[2.4, 0.14, 0.7]} color="#8a5a32" /><Box p={[0, 1.25, -0.32]} s={[2.4, 0.6, 0.1]} color="#8a5a32" /><Box p={[-1.0, 0.36, 0]} s={[0.12, 0.72, 0.6]} color="#2b3350" line={2} /><Box p={[1.0, 0.36, 0]} s={[0.12, 0.72, 0.6]} color="#2b3350" line={2} /></group>);
export const Bin: React.FC<{ p: V3; color?: string }> = ({ p, color = "#2f8c5a" }) => (<group position={p}><Cyl p={[0, 0.55, 0]} rt={0.38} rb={0.32} h={1.1} color={color} /><Cyl p={[0, 1.12, 0]} rt={0.42} h={0.08} color="#2b3350" line={2} /></group>);
export const Barrier: React.FC<{ p: V3; w?: number; rotY?: number }> = ({ p, w = 2.6, rotY = 0 }) => (<group position={p} rotation={[0, rotY, 0]}><Box p={[0, 1.0, 0]} s={[w, 0.25, 0.08]} color="#ffd23a" line={2} /><Box p={[0, 0.55, 0]} s={[w, 0.08, 0.06]} color="#2b3350" line={2} />{[-w / 2 + 0.1, w / 2 - 0.1].map((x) => <Box key={x} p={[x, 0.55, 0]} s={[0.1, 1.1, 0.5]} color="#2b3350" line={2} />)}</group>);
export const PressCam: React.FC<{ p: V3; s?: number }> = ({ p, s = 1 }) => (<group position={p} scale={s}><Box p={[0, 0, 0]} s={[0.42, 0.32, 0.3]} color="#1b1b2a" line={2} /><Cyl p={[0, 0, 0.26]} rt={0.12} h={0.3} color="#2b3350" line={2} rot={[Math.PI / 2, 0, 0]} /><Box p={[-0.08, 0.22, 0]} s={[0.16, 0.12, 0.14]} color="#d8d8e0" line={1} /></group>);
export const ChipStack: React.FC<{ p: V3; n: number; color: string; r?: number }> = ({ p, n, color, r = 0.55 }) => (<group position={p}>{Array.from({ length: n }, (_, i) => <Cyl key={i} p={[Math.sin(i * 2.1) * 0.03, 0.09 + i * 0.18, Math.cos(i * 1.7) * 0.03]} rt={r} h={0.17} color={i % 2 ? color : "#f7f2e6"} line={2} />)}</group>);
export const Card: React.FC<{ p: V3; rotY?: number; label?: string; red?: boolean; s?: number }> = ({ p, rotY = 0, label = "A", red, s = 1 }) => (
  <CanvasPlane p={[p[0], p[1] + 0.03, p[2]]} rot={[-Math.PI / 2, 0, rotY]} s={[1.6 * s, 2.3 * s]} px={[160, 230]} frame={INK} draw={(c, W, H) => { c.fillStyle = "#fffdf6"; c.fillRect(0, 0, W, H); c.fillStyle = red ? "#e5233a" : "#111"; c.font = "900 54px Inter, Arial"; c.textAlign = "center"; c.textBaseline = "middle"; c.fillText(label, 34, 40); c.font = "900 110px Inter, Arial"; c.fillText(red ? "♥" : "♠", W / 2, H / 2 + 10); }} />
);
export const Dice: React.FC<{ p: V3; rot?: V3; s?: number }> = ({ p, rot, s = 1 }) => (
  <group position={p} rotation={rot} scale={s}><Box p={[0, 0, 0]} s={[1, 1, 1]} color="#f7f2e6" />
    {[[0, 0.51, 0], [0.25, 0.51, 0.25], [-0.25, 0.51, -0.25], [0.25, 0.51, -0.25], [-0.25, 0.51, 0.25]].map((q, i) => <Ball key={i} p={q as V3} r={0.09} color="#e5233a" ink={0.0} />)}
    {[[0, 0, 0.51], [0.25, 0.25, 0.51], [-0.25, -0.25, 0.51]].map((q, i) => <Ball key={"f" + i} p={q as V3} r={0.09} color="#111" ink={0.0} />)}
  </group>
);
export const HangLamp: React.FC<{ p: V3; color?: string; o?: number }> = ({ p, color = "#1d7a4a", o = 1 }) => (
  <group position={p}><Cyl p={[0, 3, 0]} rt={0.03} h={6} color="#2b3350" line={1} /><Cyl p={[0, 0, 0]} rt={0.35} rb={1.2} h={0.7} color={color} /><Glow p={[0, -0.6, 0]} r={1.8} color="rgba(255,236,170,1)" o={0.55 * o} /></group>
);
export const Mug: React.FC<{ p: V3; rot?: V3; s?: number; color?: string }> = ({ p, rot, s = 1, color = "#ffffff" }) => (
  <group position={p} rotation={rot} scale={s}><Cyl p={[0, 0, 0]} rt={0.17} rb={0.15} h={0.36} color={color} line={2} /><Cyl p={[0, 0.17, 0]} rt={0.14} h={0.02} color="#5a3214" line={1} /><Box p={[0.21, 0.0, 0]} s={[0.09, 0.2, 0.05]} color={color} line={2} /></group>
);
export const Stars: React.FC<{ p: V3; s: [number, number]; t: number; top?: string; bottom?: string; n?: number }> = ({ p, s, t, top = "#0a0624", bottom = "#3a1a6e", n = 140 }) => (
  <CanvasPlane p={p} s={s} px={[Math.round(s[0] * 14), Math.round(s[1] * 14)]} draw={(c, W, H) => {
    const g = c.createLinearGradient(0, 0, 0, H); g.addColorStop(0, top); g.addColorStop(1, bottom); c.fillStyle = g; c.fillRect(0, 0, W, H);
    for (let i = 0; i < n; i++) { const x = ((i * 7919) % 1000) / 1000 * W, y = ((i * 104729) % 1000) / 1000 * H * 0.85, tw = 0.5 + 0.5 * Math.sin(t * 3 + i); c.fillStyle = `rgba(255,255,240,${0.35 + 0.65 * tw})`; c.beginPath(); c.arc(x, y, 1.2 + (i % 3) * 0.9, 0, 7); c.fill(); }
  }} />
);
