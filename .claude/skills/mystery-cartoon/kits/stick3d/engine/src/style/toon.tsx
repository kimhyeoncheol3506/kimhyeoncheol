import React, { useMemo } from "react";
import * as THREE from "three";
import { LineSegments2 } from "three/examples/jsm/lines/LineSegments2.js";
import { LineSegmentsGeometry } from "three/examples/jsm/lines/LineSegmentsGeometry.js";
import { LineMaterial } from "three/examples/jsm/lines/LineMaterial.js";
import { useThree } from "@react-three/fiber";

export const INK = "#0b0d1a";
const ramp = (() => { const d = new Uint8Array([90, 170, 255]); const t = new THREE.DataTexture(d, 3, 1, THREE.RedFormat); t.minFilter = t.magFilter = THREE.NearestFilter; t.needsUpdate = true; return t; })();

// Toon box with thick ink outline (fat lines, width in px)
export const Box: React.FC<{ p: [number, number, number]; s: [number, number, number]; color: string; rot?: [number, number, number]; line?: number; opacity?: number }> = ({ p, s, color, rot = [0, 0, 0], line = 4 }) => {
  const { size } = useThree();
  const geo = useMemo(() => new THREE.BoxGeometry(1, 1, 1), []);
  const edges = useMemo(() => { const g = new LineSegmentsGeometry(); g.setPositions(new THREE.EdgesGeometry(geo).attributes.position.array as Float32Array); return g; }, [geo]);
  const mat = useMemo(() => new LineMaterial({ color: new THREE.Color(INK).getHex(), linewidth: line, resolution: new THREE.Vector2(size.width, size.height) }), [size, line]);
  const seg = useMemo(() => new LineSegments2(edges, mat), [edges, mat]);
  return (
    <group position={p} rotation={rot} scale={s}>
      <mesh geometry={geo}><meshToonMaterial color={color} gradientMap={ramp} /></mesh>
      <primitive object={seg} />
    </group>
  );
};

// Tiled brick wall as one plane with canvas texture (grout lines in ink)
export const BrickWall: React.FC<{ p: [number, number, number]; rot?: [number, number, number]; s: [number, number]; a: string; b: string; repeat?: [number, number] }> = ({ p, rot = [0, 0, 0], s, a, b, repeat = [6, 10] }) => {
  const tex = useMemo(() => {
    const c = document.createElement("canvas"); c.width = c.height = 256; const g = c.getContext("2d")!;
    for (let r = 0; r < 4; r++) for (let k = -1; k < 3; k++) { g.fillStyle = (r + k) % 2 ? a : b; g.fillRect(k * 128 + (r % 2) * 64, r * 64, 128, 64); }
    g.strokeStyle = INK; g.lineWidth = 5; for (let r = 0; r <= 4; r++) { g.beginPath(); g.moveTo(0, r * 64); g.lineTo(256, r * 64); g.stroke(); }
    for (let r = 0; r < 4; r++) for (let k = 0; k < 3; k++) { const x = k * 128 + (r % 2) * 64; g.beginPath(); g.moveTo(x, r * 64); g.lineTo(x, r * 64 + 64); g.stroke(); }
    const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(...repeat); t.colorSpace = THREE.SRGBColorSpace; return t;
  }, [a, b, repeat]);
  return <mesh position={p} rotation={rot}><planeGeometry args={s} /><meshBasicMaterial map={tex} /></mesh>;
};

// Generic canvas-textured plane (text signs, charts, calendars); redrawn every frame
export const CanvasPlane: React.FC<{ p: [number, number, number]; s: [number, number]; rot?: [number, number, number]; px?: [number, number]; draw: (c: CanvasRenderingContext2D, W: number, H: number) => void; face?: boolean; frame?: string; additive?: boolean }> = ({ p, s, rot = [0, 0, 0], px = [512, 512], draw, face, frame, additive }) => {
  const { camera } = useThree();
  const { cv, tex } = useMemo(() => { const cv = document.createElement("canvas"); cv.width = px[0]; cv.height = px[1]; const tex = new THREE.CanvasTexture(cv); tex.colorSpace = THREE.SRGBColorSpace; return { cv, tex }; }, []);
  draw(cv.getContext("2d")!, px[0], px[1]); tex.needsUpdate = true;
  const ref = React.useRef<THREE.Group>(null);
  React.useLayoutEffect(() => { if (face && ref.current) ref.current.quaternion.copy(camera.quaternion); });
  return (<group ref={ref} position={p} rotation={rot}>
    <mesh><planeGeometry args={s} /><meshBasicMaterial map={tex} transparent alphaTest={additive ? 0 : 0.02} blending={additive ? THREE.AdditiveBlending : THREE.NormalBlending} depthWrite={!additive} /></mesh>
    {frame ? <Box p={[0, 0, -0.03]} s={[s[0] + 0.12, s[1] + 0.12, 0.05]} color={frame} line={4} /> : null}
  </group>);
};

// Upright (yaw-only) billboard: never tilts with camera pitch, so feet stay on the floor
export const Billboard: React.FC<{ p: [number, number, number]; h: number; draw: (c: CanvasRenderingContext2D, W: number, H: number) => void }> = ({ p, h, draw }) => {
  const { camera } = useThree();
  const W = 512, H = 768;
  const { cv, tex } = useMemo(() => { const cv = document.createElement("canvas"); cv.width = W; cv.height = H; const tex = new THREE.CanvasTexture(cv); tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 4; return { cv, tex }; }, []);
  draw(cv.getContext("2d")!, W, H); tex.needsUpdate = true;
  const ref = React.useRef<THREE.Group>(null);
  React.useLayoutEffect(() => { if (ref.current) ref.current.rotation.y = Math.atan2(camera.position.x - p[0], camera.position.z - p[2]); });
  return <group ref={ref} position={[p[0], p[1] + h * 0.483, p[2]]}><mesh><planeGeometry args={[h * W / H, h]} /><meshBasicMaterial map={tex} transparent alphaTest={0.02} /></mesh></group>;
};

// soft contact shadow on the floor
export const Shadow: React.FC<{ p: [number, number, number]; r: number; o?: number }> = ({ p, r, o = 0.45 }) => {
  const tex = useMemo(() => { const c = document.createElement("canvas"); c.width = c.height = 128; const g = c.getContext("2d")!; const rg = g.createRadialGradient(64, 64, 4, 64, 64, 62); rg.addColorStop(0, `rgba(0,0,0,${o})`); rg.addColorStop(1, "rgba(0,0,0,0)"); g.fillStyle = rg; g.fillRect(0, 0, 128, 128); const t = new THREE.CanvasTexture(c); return t; }, [o]);
  return <mesh position={[p[0], p[1] + 0.02, p[2]]} rotation={[-Math.PI / 2, 0, 0]}><planeGeometry args={[r * 2, r * 1.2]} /><meshBasicMaterial map={tex} transparent depthWrite={false} /></mesh>;
};

export const Ball: React.FC<{ p: [number, number, number]; r: number; color: string; s?: [number, number, number]; ink?: number }> = ({ p, r, color, s = [1, 1, 1], ink = 0.07 }) => (
  <group position={p} scale={s}>
    <mesh><sphereGeometry args={[r, 20, 16]} /><meshToonMaterial color={color} gradientMap={ramp} /></mesh>
    <mesh><sphereGeometry args={[r + ink, 20, 16]} /><meshBasicMaterial color={INK} side={THREE.BackSide} /></mesh>
  </group>
);
export const Cyl: React.FC<{ p: [number, number, number]; rt: number; rb?: number; h: number; color: string; line?: number; rot?: [number, number, number] }> = ({ p, rt, rb, h, color, line = 3, rot = [0, 0, 0] }) => {
  const { size } = useThree();
  const geo = useMemo(() => new THREE.CylinderGeometry(rt, rb ?? rt, h, 20), [rt, rb, h]);
  const edges = useMemo(() => { const g = new LineSegmentsGeometry(); g.setPositions(new THREE.EdgesGeometry(geo, 35).attributes.position.array as Float32Array); return g; }, [geo]);
  const mat = useMemo(() => new LineMaterial({ color: new THREE.Color(INK).getHex(), linewidth: line, resolution: new THREE.Vector2(size.width, size.height) }), [size, line]);
  const seg = useMemo(() => new LineSegments2(edges, mat), [edges, mat]);
  return <group position={p} rotation={rot}><mesh geometry={geo}><meshToonMaterial color={color} gradientMap={ramp} /></mesh><primitive object={seg} /></group>;
};

type Kind = "brick" | "wood" | "plain" | "plank" | "tile" | "carpet" | "marble";
const texCache = new Map<string, THREE.CanvasTexture>();
export function patternTex(kind: Kind, a: string, b: string, rep: [number, number]) {
  const key = [kind, a, b, rep.join(",")].join("|"); const hit = texCache.get(key); if (hit) return hit;
  const c = document.createElement("canvas"); c.width = c.height = 256; const g = c.getContext("2d")!;
  g.fillStyle = a; g.fillRect(0, 0, 256, 256); g.strokeStyle = INK; g.lineWidth = 5;
  if (kind === "brick") { for (let r = 0; r < 4; r++) for (let k = -1; k < 3; k++) { g.fillStyle = (r + k) % 2 ? a : b; g.fillRect(k * 128 + (r % 2) * 64, r * 64, 128, 64); } for (let r = 0; r <= 4; r++) { g.beginPath(); g.moveTo(0, r * 64); g.lineTo(256, r * 64); g.stroke(); } for (let r = 0; r < 4; r++) for (let k = 0; k < 3; k++) { const x = k * 128 + (r % 2) * 64; g.beginPath(); g.moveTo(x, r * 64); g.lineTo(x, r * 64 + 64); g.stroke(); } }
  if (kind === "wood") { for (let k = 0; k < 4; k++) { g.fillStyle = k % 2 ? a : b; g.fillRect(k * 64, 0, 64, 256); g.strokeStyle = "rgba(0,0,0,.18)"; g.lineWidth = 3; for (let y = 10; y < 256; y += 34) { g.beginPath(); g.moveTo(k * 64 + 8, y + (k * 7) % 11); g.bezierCurveTo(k * 64 + 24, y - 8, k * 64 + 40, y + 10, k * 64 + 58, y); g.stroke(); } g.strokeStyle = INK; g.lineWidth = 5; g.beginPath(); g.moveTo(k * 64, 0); g.lineTo(k * 64, 256); g.stroke(); } }
  if (kind === "plank") { for (let r = 0; r < 4; r++) { g.fillStyle = r % 2 ? a : b; g.fillRect(0, r * 64, 256, 64); g.strokeStyle = "rgba(0,0,0,.16)"; g.lineWidth = 3; for (let x = 8; x < 256; x += 46) { g.beginPath(); g.moveTo(x, r * 64 + 14); g.bezierCurveTo(x + 14, r * 64 + 8, x + 24, r * 64 + 26, x + 38, r * 64 + 20); g.stroke(); } g.strokeStyle = INK; g.lineWidth = 5; g.beginPath(); g.moveTo(0, r * 64); g.lineTo(256, r * 64); g.stroke(); g.beginPath(); const x = (r * 90) % 256; g.moveTo(x, r * 64); g.lineTo(x, r * 64 + 64); g.stroke(); } }
  if (kind === "tile" || kind === "marble") { g.fillStyle = b; g.fillRect(0, 0, 128, 128); g.fillRect(128, 128, 128, 128); g.strokeStyle = kind === "marble" ? "rgba(0,0,0,.35)" : INK; g.lineWidth = 4; g.strokeRect(0, 0, 256, 256); g.beginPath(); g.moveTo(128, 0); g.lineTo(128, 256); g.moveTo(0, 128); g.lineTo(256, 128); g.stroke(); }
  if (kind === "carpet") { g.fillStyle = b; for (let y = 0; y < 256; y += 64) for (let x = 0; x < 256; x += 64) if (((x + y) / 64) % 2 === 0) g.fillRect(x, y, 64, 64); g.strokeStyle = "rgba(0,0,30,.35)"; g.lineWidth = 3; g.strokeRect(0, 0, 256, 256); }
  const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(...rep); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; texCache.set(key, t); return t;
}
// Textured plane, repeat computed from world size (unit = world units per texture tile)
export const Surface: React.FC<{ p: [number, number, number]; s: [number, number]; rot?: [number, number, number]; kind: Kind; a: string; b: string; unit?: number }> = ({ p, s, rot = [0, 0, 0], kind, a, b, unit = 1.6 }) => {
  const tex = patternTex(kind, a, b, [s[0] / unit, s[1] / unit]);
  return <mesh position={p} rotation={rot}><planeGeometry args={s} /><meshBasicMaterial map={tex} /></mesh>;
};
