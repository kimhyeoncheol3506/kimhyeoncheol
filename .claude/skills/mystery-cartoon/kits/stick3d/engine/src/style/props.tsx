import React from "react";
import * as THREE from "three";
import { Box, Cyl, Ball, CanvasPlane, Surface, INK } from "./toon";
import { V3 } from "./kit";

export const Floor: React.FC<{ kind: "plank" | "tile" | "carpet" | "marble"; a: string; b: string; w?: number; d?: number; unit?: number }> = ({ kind, a, b, w = 24, d = 24, unit = 2.2 }) => (
  <Surface p={[0, 0, -2]} s={[w, d]} rot={[-Math.PI / 2, 0, 0]} kind={kind} a={a} b={b} unit={unit} />
);

// Back wall with a real doorway hole (so characters can walk THROUGH it). Wall spans x:[-W/2,W/2], y:[0,9].
export const WallDoor: React.FC<{ z: number; W: number; kind: "brick" | "wood" | "plain"; a: string; b: string; door?: { x: number; w: number; h: number }; unit?: number; base?: string }> = ({ z, W, kind, a, b, door, unit = 1.6, base }) => {
  const H = 9;
  const pieces: [number, number, number, number][] = [];
  if (!door) pieces.push([-W / 2, W / 2, 0, H]); else {
    const l = door.x - door.w / 2 - 0.25, r = door.x + door.w / 2 + 0.25;
    pieces.push([-W / 2, l, 0, H], [r, W / 2, 0, H], [l, r, door.h + 0.3, H]);
  }
  return (<>
    {pieces.map(([x0, x1, y0, y1], i) => <Surface key={i} p={[(x0 + x1) / 2, (y0 + y1) / 2, z]} s={[x1 - x0, y1 - y0]} kind={kind} a={a} b={b} unit={unit} />)}
    {base ? pieces.slice(0, door ? 2 : 1).map(([x0, x1], i) => <Box key={"b" + i} p={[(x0 + x1) / 2, 0.22, z + 0.06]} s={[x1 - x0, 0.44, 0.12]} color={base} line={3} />) : null}
  </>);
};

export const SideWall: React.FC<{ x: number; kind: "brick" | "wood" | "plain"; a: string; b: string; d?: number; unit?: number }> = ({ x, kind, a, b, d = 24, unit = 1.6 }) => (
  <Surface p={[x, 4.5, -2]} s={[d, 9]} rot={[0, x < 0 ? Math.PI / 2 : -Math.PI / 2, 0]} kind={kind} a={a} b={b} unit={unit} />
);

export const Glow: React.FC<{ p: V3; r: number; color: string; o?: number }> = ({ p, r, color, o = 0.6 }) => (
  <CanvasPlane p={p} s={[r * 2, r * 2]} px={[128, 128]} face additive draw={(c, W, H) => { c.clearRect(0, 0, W, H); const g = c.createRadialGradient(W / 2, H / 2, 2, W / 2, H / 2, W / 2); g.addColorStop(0, color); g.addColorStop(1, "rgba(0,0,0,0)"); c.globalAlpha = o; c.fillStyle = g; c.fillRect(0, 0, W, H); }} />
);
export const Shaft: React.FC<{ p: V3; s: [number, number]; rot?: V3; color?: string; o?: number }> = ({ p, s, rot, color = "255,236,150", o = 0.28 }) => (
  <CanvasPlane p={p} s={s} rot={rot} px={[64, 256]} additive draw={(c, W, H) => { c.clearRect(0, 0, W, H); const g = c.createLinearGradient(0, 0, 0, H); g.addColorStop(0, `rgba(${color},${o})`); g.addColorStop(1, `rgba(${color},0)`); c.fillStyle = g; c.fillRect(0, 0, W, H); const g2 = c.createLinearGradient(0, 0, W, 0); g2.addColorStop(0, "rgba(0,0,0,1)"); g2.addColorStop(0.5, "rgba(0,0,0,0)"); g2.addColorStop(1, "rgba(0,0,0,1)"); c.globalCompositeOperation = "destination-out"; c.globalAlpha = 0.7; c.fillStyle = g2; c.fillRect(0, 0, W, H); }} />
);

export const Plant: React.FC<{ p: V3; s?: number; pot?: string }> = ({ p, s = 1, pot = "#c0643a" }) => (
  <group position={p} scale={s}><Cyl p={[0, 0.35, 0]} rt={0.42} rb={0.3} h={0.7} color={pot} />
    <Ball p={[0, 1.15, 0]} r={0.55} color="#35b060" s={[1, 1.15, 1]} /><Ball p={[-0.38, 0.95, 0.12]} r={0.38} color="#43c46e" /><Ball p={[0.4, 1.0, -0.1]} r={0.4} color="#2c9c54" /><Ball p={[0.05, 1.55, 0.05]} r={0.32} color="#4ed17c" /></group>
);
export const Shelf: React.FC<{ p: V3; w?: number; rows?: number; seed?: number; wood?: string }> = ({ p, w = 3, rows = 4, seed = 1, wood = "#7a4a2a" }) => {
  const cols = ["#d94a4a", "#3a6fd8", "#e5b43a", "#2f9e6a", "#7a54d6", "#e0743a", "#f2f2f2", "#2b3350"];
  return (<group position={p}>
    <Box p={[0, rows * 0.55, 0]} s={[w, rows * 1.1 + 0.15, 0.7]} color={wood} />
    {Array.from({ length: rows }, (_, r) => { let x = -w / 2 + 0.2, i = 0; const items: React.ReactNode[] = []; while (x < w / 2 - 0.35) { const bw = 0.13 + ((seed * 7 + r * 13 + i * 5) % 5) * 0.035, bh = 0.62 + ((seed * 3 + r * 11 + i * 7) % 4) * 0.11; items.push(<Box key={i} p={[x + bw / 2, r * 1.1 + 0.15 + bh / 2 + 0.07, 0.16]} s={[bw, bh, 0.45]} color={cols[(seed + r * 3 + i) % cols.length]} line={2} />); x += bw + 0.015; i++; } return <React.Fragment key={r}>{items}</React.Fragment>; })}
  </group>);
};
export const Frame: React.FC<{ p: V3; s: [number, number]; art?: number; rot?: V3 }> = ({ p, s, art = 0, rot }) => (
  <CanvasPlane p={p} s={s} rot={rot} px={[Math.round(s[0] * 200), Math.round(s[1] * 200)]} frame="#e8c06a" draw={(c, W, H) => {
    const pal = [["#8ed0ff", "#ffd36a", "#3a9e6a"], ["#ffb38a", "#7a54d6", "#2b3350"], ["#bfe9ff", "#e5483f", "#1d2f66"]][art % 3];
    c.fillStyle = pal[0]; c.fillRect(0, 0, W, H); c.fillStyle = pal[1]; c.beginPath(); c.arc(W * 0.7, H * 0.3, H * 0.16, 0, 7); c.fill(); c.fillStyle = pal[2]; c.beginPath(); c.moveTo(0, H); c.lineTo(W * 0.35, H * 0.4); c.lineTo(W * 0.62, H * 0.75); c.lineTo(W * 0.82, H * 0.55); c.lineTo(W, H); c.fill();
  }} />
);
export const WindowCity: React.FC<{ p: V3; s: [number, number]; dusk?: boolean }> = ({ p, s, dusk }) => (
  <CanvasPlane p={p} s={s} px={[Math.round(s[0] * 160), Math.round(s[1] * 160)]} frame="#2b3350" draw={(c, W, H) => {
    const g = c.createLinearGradient(0, 0, 0, H); g.addColorStop(0, dusk ? "#2a2f7a" : "#4aa8ff"); g.addColorStop(1, dusk ? "#ff9a5a" : "#cfeaff"); c.fillStyle = g; c.fillRect(0, 0, W, H);
    for (let i = 0; i < 9; i++) { const bw = W / 8, bh = H * (0.35 + ((i * 37) % 50) / 100), x = i * bw * 0.95 - 10; c.fillStyle = dusk ? "#141a46" : "#5d7fc4"; c.fillRect(x, H - bh, bw, bh); c.fillStyle = dusk ? "#ffd36a" : "#dff0ff"; for (let yy = H - bh + 10; yy < H - 8; yy += 18) for (let xx = x + 6; xx < x + bw - 8; xx += 14) if (((xx * 7 + yy * 3) | 0) % 5 > 1) c.fillRect(xx, yy, 6, 8); }
    c.strokeStyle = INK; c.lineWidth = 6; c.beginPath(); c.moveTo(W / 2, 0); c.lineTo(W / 2, H); c.moveTo(0, H / 2); c.lineTo(W, H / 2); c.stroke();
  }} />
);
export const Lamp: React.FC<{ p: V3; h?: number; color?: string }> = ({ p, h = 2.6, color = "#ffe9a8" }) => (
  <group position={p}><Cyl p={[0, 0.08, 0]} rt={0.35} h={0.16} color="#2b3350" /><Cyl p={[0, h / 2, 0]} rt={0.05} h={h} color="#8c92a8" line={2} /><Cyl p={[0, h + 0.1, 0]} rt={0.3} rb={0.5} h={0.6} color={color} /></group>
);
export const Monitor: React.FC<{ p: V3; rot?: V3; s?: number; screen?: string }> = ({ p, rot, s = 1, screen = "#1c2a5a" }) => (
  <group position={p} rotation={rot} scale={s}><Box p={[0, 0.07, 0]} s={[0.5, 0.06, 0.4]} color="#2b3350" line={2} /><Box p={[0, 0.3, 0]} s={[0.1, 0.4, 0.1]} color="#2b3350" line={2} /><Box p={[0, 0.78, 0]} s={[1.2, 0.74, 0.08]} color="#1b1f33" line={3} /><Box p={[0, 0.78, 0.05]} s={[1.08, 0.62, 0.02]} color={screen} line={1} /></group>
);
export const Chair: React.FC<{ p: V3; rotY?: number; color?: string }> = ({ p, rotY = 0, color = "#3b4a8a" }) => (
  <group position={p} rotation={[0, rotY, 0]}><Cyl p={[0, 0.35, 0]} rt={0.06} h={0.7} color="#2b3350" line={2} /><Box p={[0, 0.78, 0]} s={[1.0, 0.18, 1.0]} color={color} /><Box p={[0, 1.4, -0.45]} s={[1.0, 1.1, 0.14]} color={color} /><Box p={[0, 0.05, 0]} s={[0.9, 0.08, 0.9]} color="#2b3350" line={2} /></group>
);
export const Cooler: React.FC<{ p: V3 }> = ({ p }) => (<group position={p}><Cyl p={[0, 0.7, 0]} rt={0.4} h={1.4} color="#e8eef8" /><Cyl p={[0, 1.8, 0]} rt={0.32} h={0.9} color="#7ec8ff" /><Box p={[0, 1.1, 0.4]} s={[0.2, 0.12, 0.1]} color="#e23b3b" line={2} /></group>);
export const Cabinet: React.FC<{ p: V3; w?: number; h?: number; color?: string }> = ({ p, w = 1.6, h = 2.2, color = "#8a96b8" }) => (<group position={p}><Box p={[0, h / 2, 0]} s={[w, h, 0.9]} color={color} />{[0.3, 0.55, 0.8].map((k) => <Box key={k} p={[0, h * k, 0.47]} s={[w - 0.2, 0.04, 0.04]} color={INK} line={2} />)}{[0.18, 0.42, 0.68].map((k) => <Box key={k} p={[0, h * k, 0.5]} s={[0.3, 0.07, 0.07]} color="#d8d8e0" line={2} />)}</group>);
export const Rug: React.FC<{ p: V3; s: [number, number]; a: string; b: string }> = ({ p, s, a, b }) => (
  <CanvasPlane p={[p[0], p[1] + 0.02, p[2]]} s={s} rot={[-Math.PI / 2, 0, 0]} px={[256, Math.round(256 * s[1] / s[0])]} draw={(c, W, H) => { c.fillStyle = a; c.fillRect(0, 0, W, H); c.strokeStyle = b; c.lineWidth = 14; c.strokeRect(18, 18, W - 36, H - 36); c.strokeStyle = INK; c.lineWidth = 6; c.strokeRect(3, 3, W - 6, H - 6); c.strokeStyle = b; c.lineWidth = 5; c.strokeRect(46, 46, W - 92, H - 92); }} />
);
export const Dust: React.FC<{ t: number; n?: number; area: [number, number, number]; color?: string; fall?: boolean }> = ({ t, n = 14, area, color = "rgba(255,240,200,.9)", fall }) => (
  <>{Array.from({ length: n }, (_, i) => { const u = (t * (fall ? 0.5 : 0.07) + i * 0.137) % 1; return <Glow key={i} p={[Math.sin(i * 12.9) * area[0], fall ? area[1] * (1 - u) : area[1] * (0.3 + ((i * 0.37) % 1) * 0.7) + Math.sin(t + i) * 0.1, -1 + Math.cos(i * 7.7) * area[2]]} r={fall ? 0.09 : 0.06} color={color} o={0.8} />; })}</>
);
