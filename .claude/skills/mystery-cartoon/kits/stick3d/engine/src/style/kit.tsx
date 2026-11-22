import React from "react";
import { interpolate, Easing } from "remotion";
import { useThree } from "@react-three/fiber";
import * as THREE from "three";
import { Box, BrickWall, Billboard, CanvasPlane, Shadow } from "./toon";
import { drawPuppet, Look, Pose, INK } from "./puppet";

export const clamp = (x: number, a = 0, b = 1) => Math.min(b, Math.max(a, x));
export const seg = (t: number, a: number, b: number, e: (x: number) => number = Easing.out(Easing.cubic)) => e(clamp((t - a) / (b - a)));
export const lerp = (a: number, b: number, k: number) => a + (b - a) * k;
export type V3 = [number, number, number];
export const mix3 = (a: V3, b: V3, k: number): V3 => [lerp(a[0], b[0], k), lerp(a[1], b[1], k), lerp(a[2], b[2], k)];

// Camera rig: eased move between two poses + handheld drift
export const Rig: React.FC<{ t: number; t0: number; t1: number; from: V3; to: V3; lookFrom: V3; lookTo: V3; fov?: number; roll?: [number, number]; ease?: (x: number) => number; hand?: number; kicks?: number[]; shakeAt?: [number, number, number] }> = ({ t, t0, t1, from, to, lookFrom, lookTo, fov = 64, roll = [0, 0], ease = Easing.inOut(Easing.cubic), hand = 0.2, kicks = [], shakeAt }) => {
  const { camera } = useThree();
  const k = ease(clamp((t - t0) / (t1 - t0)));
  const a = mix3(from, to, k), l = mix3(lookFrom, lookTo, k);
  const h = 0.018 * hand;
  let kk = 0; for (const ki of kicks) if (t > ki) kk += Math.exp(-(t - ki) * 7);
  if (shakeAt) kk += shakeAt[2] * clamp((t - shakeAt[0]) / (shakeAt[1] - shakeAt[0]));
  const sx = Math.sin(t * 61) * kk * 0.012, sy = Math.cos(t * 53) * kk * 0.012;
  camera.position.set(a[0] + Math.sin(t * 1.7) * h + sx, a[1] + Math.sin(t * 2.3 + 1) * h + sy, a[2] + Math.sin(t * 1.3) * h);
  (camera as THREE.PerspectiveCamera).fov = fov - Math.min(kk, 1.3) * 6; (camera as THREE.PerspectiveCamera).updateProjectionMatrix();
  camera.up.set(Math.sin(lerp(roll[0], roll[1], k)), Math.cos(lerp(roll[0], roll[1], k)), 0);
  camera.lookAt(l[0], l[1], l[2]); camera.updateMatrixWorld(); return null;
};

export const Person: React.FC<{ p: V3; h?: number; look: Look; pose: Omit<Pose, "t"> & { t?: number }; f: number; shadow?: boolean; sy?: number }> = ({ p, h = 2.5, look, pose, f, shadow = true, sy }) => (
  <>{shadow ? <Shadow p={[p[0], sy ?? p[1], p[2]]} r={h * 0.32} /> : null}
  <Billboard p={p} h={h} draw={(c, W, H) => drawPuppet(c, W, H, look, { ...pose, t: pose.t ?? f })} /></>
);

export const Lights: React.FC<{ warm?: string }> = ({ warm = "#fff2d8" }) => (<><ambientLight intensity={1.55} /><directionalLight position={[4, 8, 5]} intensity={1.3} color={warm} /><directionalLight position={[-5, 3, 2]} intensity={0.5} color="#9ab8ff" /></>);

// Room shell: floor + back wall + side wall. tiles=brick|plain
export const Room: React.FC<{ wall: [string, string]; side?: [string, string]; floor: string; w?: number; d?: number; plain?: boolean }> = ({ wall, side, floor, w = 22, d = 14, plain }) => (
  <>
    <Box p={[0, -0.1, 0]} s={[w, 0.2, d * 2]} color={floor} line={2} />
    {plain ? <Box p={[0, 4, -d / 2]} s={[w, 10, 0.2]} color={wall[0]} line={2} /> : <BrickWall p={[0, 4, -d / 2]} s={[w, 10]} a={wall[0]} b={wall[1]} repeat={[w / 1.6, 10 / 1.2]} />}
    {side ? <BrickWall p={[-w / 2, 4, 0]} rot={[0, Math.PI / 2, 0]} s={[d * 2, 10]} a={side[0]} b={side[1]} repeat={[d * 2 / 1.6, 10 / 1.2]} /> : null}
  </>
);

export const Desk: React.FC<{ p: V3; w?: number; top?: string; leg?: string; d?: number }> = ({ p, w = 3.4, top = "#e9edf7", leg = "#aab7dc", d = 1.7 }) => (
  <group position={p}><Box p={[0, 1.0, 0]} s={[w, 0.2, d]} color={top} /><Box p={[-w / 2 + 0.12, 0.5, 0]} s={[0.2, 1, d - 0.1]} color={leg} /><Box p={[w / 2 - 0.12, 0.5, 0]} s={[0.2, 1, d - 0.1]} color={leg} /><Box p={[0, 0.55, -d / 2 + 0.1]} s={[w - 0.2, 0.9, 0.12]} color={leg} /></group>
);

export const Door: React.FC<{ p: V3; color?: string; open?: number; label?: string; w?: number; h?: number }> = ({ p, color = "#9fc2ee", open = 0, label, w = 2.4, h = 4.2 }) => (
  <group position={p}>
    <Box p={[-w / 2 - 0.12, h / 2, 0]} s={[0.24, h + 0.3, 0.3]} color="#fafafa" /><Box p={[w / 2 + 0.12, h / 2, 0]} s={[0.24, h + 0.3, 0.3]} color="#fafafa" /><Box p={[0, h + 0.15, 0]} s={[w + 0.48, 0.3, 0.3]} color="#fafafa" />
    <group position={[-w / 2, 0, 0.12]} rotation={[0, open * 1.25, 0]}><Box p={[w / 2, h / 2, 0]} s={[w, h, 0.14]} color={color} />
      <Box p={[w * 0.82, h * 0.48, 0.12]} s={[0.24, 0.12, 0.1]} color="#d8b24a" line={2} />
      {label ? <CanvasPlane p={[w / 2, h * 0.62, 0.09]} s={[w * 0.85, 0.7]} px={[512, 170]} draw={(c, W, H) => { c.fillStyle = "#fff"; c.fillRect(0, 0, W, H); c.strokeStyle = INK; c.lineWidth = 10; c.strokeRect(5, 5, W - 10, H - 10); c.fillStyle = "#1a2a66"; c.font = "900 64px Inter, Arial"; c.textAlign = "center"; c.textBaseline = "middle"; c.fillText(label, W / 2, H / 2 + 4); }} /> : null}
    </group>
  </group>
);

export const Sign: React.FC<{ p: V3; s: [number, number]; text: string; bg?: string; fg?: string; rot?: V3; size?: number; frame?: string; face?: boolean }> = ({ p, s, text, bg = "#fff", fg = "#111", rot, size = 90, frame = "#0b0d1a", face }) => (
  <CanvasPlane p={p} s={s} rot={rot} face={face} px={[Math.round(s[0] * 220), Math.round(s[1] * 220)]} frame={frame} draw={(c, W, H) => { c.fillStyle = bg; c.fillRect(0, 0, W, H); c.fillStyle = fg; c.font = `900 ${size}px Inter, Arial`; c.textAlign = "center"; c.textBaseline = "middle"; const ls = text.split("\n"); ls.forEach((l, i) => c.fillText(l, W / 2, H / 2 + (i - (ls.length - 1) / 2) * size * 1.05)); }} />
);

export const Clock: React.FC<{ p: V3; r?: number; t: number; speed?: number }> = ({ p, r = 0.7, t, speed = 1 }) => (
  <CanvasPlane p={p} s={[r * 2, r * 2]} px={[300, 300]} draw={(c, W, H) => {
    c.clearRect(0, 0, W, H); c.fillStyle = "#e23b3b"; c.strokeStyle = INK; c.lineWidth = 8; c.beginPath(); c.arc(W / 2, H / 2, W / 2 - 6, 0, 7); c.fill(); c.stroke();
    c.fillStyle = "#fff"; c.beginPath(); c.arc(W / 2, H / 2, W / 2 - 30, 0, 7); c.fill(); c.stroke();
    c.fillStyle = INK; c.font = "800 28px Inter, Arial"; c.textAlign = "center"; c.textBaseline = "middle";
    for (let i = 1; i <= 12; i++) { const a = i / 12 * Math.PI * 2 - Math.PI / 2; c.fillText(String(i), W / 2 + Math.cos(a) * 98, H / 2 + Math.sin(a) * 98); }
    const hand = (a: number, l: number, wd: number, col: string) => { c.strokeStyle = col; c.lineWidth = wd; c.lineCap = "round"; c.beginPath(); c.moveTo(W / 2, H / 2); c.lineTo(W / 2 + Math.sin(a) * l, H / 2 - Math.cos(a) * l); c.stroke(); };
    hand(t * speed * 0.3, 70, 9, INK); hand(t * speed * 3.6, 100, 6, "#e23b3b");
  }} />
);

// Calendar page: month + big day; optional circled marker
export const Calendar: React.FC<{ p: V3; month: string; day: string; s?: number; mark?: string; markK?: number; rot?: V3; face?: boolean }> = ({ p, month, day, s = 1.6, mark, markK = 0, rot, face }) => (
  <CanvasPlane p={p} s={[s, s * 1.15]} rot={rot} face={face} px={[400, 460]} frame={INK} draw={(c, W, H) => {
    c.fillStyle = "#fffaf0"; c.fillRect(0, 0, W, H); c.fillStyle = "#e23b3b"; c.fillRect(0, 0, W, 120); c.fillStyle = "#fff"; c.font = "900 78px Inter, Arial"; c.textAlign = "center"; c.textBaseline = "middle"; c.fillText(month, W / 2, 62);
    c.fillStyle = INK; c.font = "900 220px Inter, Arial"; c.fillText(day, W / 2, 270);
    if (mark) { c.strokeStyle = "#e23b3b"; c.lineWidth = 12; c.beginPath(); c.ellipse(W / 2, 270, 170 * markK, 115 * markK, -0.06, 0, Math.PI * 2 * markK); c.stroke(); c.fillStyle = "#e23b3b"; c.font = "900 60px Inter, Arial"; c.fillText(mark, W / 2, 400); }
  }} />
);

export const ChartScreen: React.FC<{ p: V3; s: [number, number]; prog: number; up?: boolean; label?: string; shake?: number; big?: string; bigK?: number }> = ({ p, s, prog, up, label = "AI CHIPS", shake = 0, big, bigK = 1 }) => (
  <CanvasPlane p={[p[0] + shake, p[1], p[2]]} s={s} px={[Math.round(s[0] * 150), Math.round(s[1] * 150)]} frame="#2b3350" draw={(c, W, H) => {
    c.fillStyle = "#0e1630"; c.fillRect(0, 0, W, H); c.strokeStyle = "rgba(120,160,255,.25)"; c.lineWidth = 2; for (let i = 1; i < 6; i++) { c.beginPath(); c.moveTo(0, H * i / 6); c.lineTo(W, H * i / 6); c.stroke(); }
    c.fillStyle = "#9fb4ff"; c.font = `800 ${H * 0.07}px Inter, Arial`; c.textAlign = "left"; c.fillText(label, 24, H * 0.1);
    const pts: [number, number][] = [[0.04, 0.2], [0.18, 0.15], [0.3, 0.28], [0.42, 0.22], [0.55, 0.5], [0.68, 0.45], [0.8, 0.78], [0.96, 0.92]];
    const n = prog * (pts.length - 1); c.strokeStyle = up ? "#31d46a" : "#ff3b3b"; c.lineWidth = H * 0.028; c.lineJoin = "round"; c.beginPath();
    let lx = 0, ly = 0; for (let i = 0; i <= Math.floor(n); i++) { const q = pts[i]; const y = up ? 1 - q[1] : q[1]; i ? c.lineTo(q[0] * W, y * H) : c.moveTo(q[0] * W, y * H); lx = q[0] * W; ly = y * H; }
    const i0 = Math.floor(n); if (i0 < pts.length - 1) { const a = pts[i0], b = pts[i0 + 1], r = n - i0; const x = lerp(a[0], b[0], r) * W, yy = (up ? 1 - lerp(a[1], b[1], r) : lerp(a[1], b[1], r)) * H; c.lineTo(x, yy); lx = x; ly = yy; }
    c.stroke(); c.fillStyle = up ? "#31d46a" : "#ff3b3b"; c.beginPath(); c.arc(lx, ly, H * 0.04, 0, 7); c.fill();
    if (big) { c.save(); c.translate(W * 0.5, H * 0.32); c.scale(bigK, bigK); c.fillStyle = "#ff3b3b"; c.strokeStyle = "#000"; c.lineWidth = H * 0.03; c.font = `900 ${H * 0.34}px Inter, Arial`; c.textAlign = "center"; c.textBaseline = "middle"; c.strokeText(big, 0, 0); c.fillText(big, 0, 0); c.restore(); }
  }} />
);

// Stairs (descending steps toward +x)
export const Stairs: React.FC<{ n: number; x0: number; dx: number; dy: number; z?: number; colors?: string[] }> = ({ n, x0, dx, dy, z = 0, colors }) => (
  <>{Array.from({ length: n }, (_, i) => <Box key={i} p={[x0 + i * dx, (n - i) * dy / 2 - 0.1, z]} s={[dx, (n - i) * dy, 2.2]} color={colors ? colors[i % colors.length] : "#e5483f"} />)}</>
);

export const Chip: React.FC<{ p: V3; s?: number; glow?: string; rot?: V3 }> = ({ p, s = 1, glow = "#35d36a", rot }) => (
  <group position={p} scale={s} rotation={rot}>
    <Box p={[0, 0, 0]} s={[1.3, 0.22, 1.3]} color={glow} />
    <Box p={[0, 0.2, 0]} s={[0.8, 0.18, 0.8]} color="#1c2a22" />
    {[-0.5, -0.2, 0.2, 0.5].map((x) => <React.Fragment key={x}><Box p={[x, -0.05, 0.75]} s={[0.1, 0.1, 0.25]} color="#d8d8e0" line={2} /><Box p={[x, -0.05, -0.75]} s={[0.1, 0.1, 0.25]} color="#d8d8e0" line={2} /></React.Fragment>)}
  </group>
);

// Screen-space overlay: soft light shaft + vignette + warm/cool grade
export const Grade: React.FC<{ t: number; shaft?: boolean; tint?: string }> = ({ t, shaft = true, tint = "rgba(255,200,120,0)" }) => (
  <>
    {shaft ? <div style={{ position: "absolute", inset: 0, background: `linear-gradient(${112 + Math.sin(t * 0.5) * 2}deg, transparent 28%, rgba(255,236,140,.22) 34%, rgba(255,236,140,.22) 52%, transparent 58%)`, mixBlendMode: "screen" }} /> : null}
    <div style={{ position: "absolute", inset: 0, background: tint }} />
    <div style={{ position: "absolute", inset: 0, background: "radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0) 55%, rgba(5,8,30,.45) 100%)" }} />
  </>
);

export const CamSet: React.FC<{ t: number; pos: V3; look: V3; fov?: number; roll?: number; kicks?: number[]; hand?: number; shakeAt?: [number, number, number] }> = ({ t, pos, look, fov = 64, roll = 0, kicks = [], hand = 1, shakeAt }) => (
  <Rig t={t} t0={0} t1={1} from={pos} to={pos} lookFrom={look} lookTo={look} fov={fov} roll={[roll, roll]} kicks={kicks} hand={hand} shakeAt={shakeAt} />
);
