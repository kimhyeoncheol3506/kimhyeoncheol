// Voynich (KO) sample — 3 scenes, 9:16 720x1280 30fps, voice = 여의도여자.
// S1 1912 antique bookshop at night: the dealer walks in, the strange book glows on the counter, coins drop on "샀습니다".
// S2 cool study: three scholars behind a desk, year board flips 1912 -> 2024, chalkboard of glyphs gets a red X, hands on heads.
// S3 golden lab: book on a pedestal under a spot, carbon-14 readout counts to 600 years (1404-1438), scientist jumps back.
import React from "react";
import { AbsoluteFill, Sequence, useCurrentFrame, Easing, Audio, staticFile } from "remotion";
import { ThreeCanvas } from "@remotion/three";
import { Box, Cyl, Ball, CanvasPlane } from "../style/toon";
import { Look } from "../style/puppet";
import { Person, Lights, Desk, Clock, Grade, seg, lerp, clamp, V3 } from "../style/kit";
import { Floor, WallDoor, SideWall, Glow, Shaft, Plant, Shelf, Frame, Lamp, Cabinet, Rug, Dust } from "../style/props";
import { Cam, Key, SpotCone, HangLamp } from "../style/extra";
import { Captions } from "../Main";

const FPS = 30, LEAD = 6, TAIL = 8, WALK = 3.4;
const KF = "Pretendard, 'Malgun Gothic', Arial";
type Ctx = { t: number; f: number };
type Trans = "ghost" | "zoom" | "flash";

const dealer: Look = { skin: "#f6d6bd", body: "#4a3426", outfit: "suit", tie: "#b8322f", hair: "grey", glasses: true, hat: "#2a1a12", shoe: "#1b120c" };
const keeper: Look = { skin: "#e8c4a0", body: "#5b6b3a", outfit: "hoodie", hair: "grey", shoe: "#1b120c" };
const sch: Look[] = [
  { skin: "#fbe3c8", body: "#2f5d8a", outfit: "blazer", shirt: "#fff", hair: "swept", hairColor: "#3b2a1a", glasses: true },
  { skin: "#e0b48c", body: "#7a2f3a", outfit: "suit", tie: "#f0c23a", hair: "grey", glasses: true },
  { skin: "#f7d4b5", body: "#2f7a5a", outfit: "shirt", hair: "bob", hairColor: "#1a1010" },
];
const sci: Look = { skin: "#fbe3c8", body: "#f2f2f2", outfit: "blazer", shirt: "#7ec8ff", hair: "swept", hairColor: "#1b1b2a", glasses: true, badge: "#ffc23a" };

const Scene: React.FC<{ start: number; end: number; first?: boolean; trans?: Trans; bg: string; children: (c: Ctx) => React.ReactNode }> = ({ start, end, first, trans = "ghost", bg, children }) => {
  const from = Math.round(start * FPS) - (first ? 0 : LEAD), dur = Math.round(end * FPS) - from + TAIL;
  return <Sequence from={from} durationInFrames={dur} layout="none"><Inner from={from} first={first} trans={trans} bg={bg} children={children} /></Sequence>;
};
const Inner: React.FC<{ from: number; first?: boolean; trans: Trans; bg: string; children: (c: Ctx) => React.ReactNode }> = ({ from, first, trans, bg, children }) => {
  const f = useCurrentFrame(), t = (f + from) / FPS;
  const k = first ? 1 : clamp(f / (LEAD + 2)), ke = Easing.out(Easing.cubic)(k);
  const sc = !first && trans === "zoom" ? lerp(1.35, 1, ke) : 1;
  return (
    <AbsoluteFill style={{ opacity: first || trans === "flash" ? 1 : k, transform: `scale(${sc})`, background: bg, filter: "saturate(1.32) contrast(1.07) brightness(1.02)" }}>
      <ThreeCanvas width={720} height={1280} camera={{ fov: 60, position: [0, 2, 8], near: 0.1, far: 200 }} gl={{ antialias: true }}>
        <color attach="background" args={[bg]} />{children({ t, f })}
      </ThreeCanvas>
      {!first && trans === "flash" ? <AbsoluteFill style={{ background: "#fff", opacity: 1 - clamp(f / 7) }} /> : null}
    </AbsoluteFill>
  );
};

/* ---------- drawing helpers: fake Voynich glyphs + herbal page ---------- */
const rnd = (s: number) => { const x = Math.sin(s * 127.1) * 43758.5453; return x - Math.floor(x); };
function glyphLine(c: CanvasRenderingContext2D, x0: number, y: number, w: number, sz: number, seed: number, col = "#3a2414") {
  let x = x0, i = 0; c.strokeStyle = col; c.lineWidth = sz * 0.13; c.lineCap = "round";
  while (x < x0 + w - sz) {
    const r = rnd(seed + i * 1.7); c.beginPath();
    if (r < 0.28) c.arc(x + sz * 0.3, y, sz * 0.26, 0, Math.PI * 2);
    else if (r < 0.5) c.arc(x + sz * 0.3, y, sz * 0.26, 0.6, Math.PI * 1.7);
    else if (r < 0.72) { c.moveTo(x, y + sz * 0.3); c.lineTo(x + sz * 0.15, y - sz * 0.55); c.quadraticCurveTo(x + sz * 0.65, y - sz * 0.6, x + sz * 0.45, y + sz * 0.3); }
    else if (r < 0.86) { c.moveTo(x, y); c.bezierCurveTo(x + sz * 0.2, y - sz * 0.6, x + sz * 0.5, y + sz * 0.6, x + sz * 0.6, y - sz * 0.1); }
    else { c.moveTo(x + sz * 0.1, y + sz * 0.3); c.lineTo(x + sz * 0.1, y - sz * 0.7); c.moveTo(x - sz * 0.05, y - sz * 0.35); c.lineTo(x + sz * 0.4, y - sz * 0.35); }
    c.stroke(); x += sz * (0.55 + r * 0.35); if (rnd(seed + i * 3.3) > 0.8) x += sz * 0.55; i++;
  }
}
function herbalPage(c: CanvasRenderingContext2D, W: number, H: number, seed: number, glow = 0) {
  c.fillStyle = "#ead7a6"; c.fillRect(0, 0, W, H);
  const g = c.createRadialGradient(W / 2, H / 2, W * 0.2, W / 2, H / 2, W * 0.8); g.addColorStop(0, "rgba(0,0,0,0)"); g.addColorStop(1, "rgba(120,70,20,.35)"); c.fillStyle = g; c.fillRect(0, 0, W, H);
  for (let l = 0; l < 4; l++) glyphLine(c, W * 0.08, H * (0.09 + l * 0.06), W * 0.84, W * 0.055, seed * 10 + l * 7);
  // plant: roots, stem, leaves, flowers
  const cx = W * 0.5, base = H * 0.78;
  c.strokeStyle = "#6a3e1a"; c.lineWidth = W * 0.012; for (let r = 0; r < 5; r++) { c.beginPath(); c.moveTo(cx, base); c.quadraticCurveTo(cx + (r - 2) * W * 0.06, base + H * 0.05, cx + (r - 2) * W * 0.11, base + H * 0.09); c.stroke(); }
  c.strokeStyle = "#2f6a2a"; c.lineWidth = W * 0.016; c.beginPath(); c.moveTo(cx, base); c.bezierCurveTo(cx - W * 0.08, H * 0.6, cx + W * 0.08, H * 0.5, cx, H * 0.36); c.stroke();
  for (let k = 0; k < 6; k++) { const yy = H * (0.42 + k * 0.055), s = k % 2 ? 1 : -1; c.save(); c.translate(cx + s * W * 0.02, yy); c.rotate(s * 0.7); c.fillStyle = k % 3 ? "#4f8f3a" : "#3c7a30"; c.beginPath(); c.ellipse(s * W * 0.1, 0, W * 0.11, W * 0.04, 0, 0, 7); c.fill(); c.strokeStyle = "#1e3a14"; c.lineWidth = W * 0.006; c.stroke(); c.restore(); }
  [["#3a5fc8", -0.09], ["#c8423a", 0.0], ["#3a5fc8", 0.09]].forEach(([col, dx]) => { c.fillStyle = col as string; c.beginPath(); c.arc(cx + (dx as number) * W, H * 0.33 - Math.abs(dx as number) * H * 0.2, W * 0.045, 0, 7); c.fill(); c.strokeStyle = "#2a1a10"; c.lineWidth = W * 0.007; c.stroke(); });
  for (let l = 0; l < 2; l++) glyphLine(c, W * 0.08, H * (0.9 + l * 0.05), W * 0.84, W * 0.05, seed * 13 + l * 5);
  if (glow > 0) { c.fillStyle = `rgba(255,210,110,${0.25 * glow})`; c.fillRect(0, 0, W, H); }
}
const Book: React.FC<{ p: V3; rotY?: number; s?: number; glow?: number }> = ({ p, rotY = 0, s = 1, glow = 0 }) => (
  <group position={p} rotation={[0, rotY, 0]} scale={s}>
    <Box p={[0, -0.03, 0]} s={[2.25, 0.08, 1.42]} color="#6b3a1f" line={3} />
    <CanvasPlane p={[-0.55, 0.025, 0]} rot={[-Math.PI / 2, 0, -0.03]} s={[1.05, 1.32]} px={[300, 380]} draw={(c, W, H) => herbalPage(c, W, H, 1, glow)} />
    <CanvasPlane p={[0.55, 0.025, 0]} rot={[-Math.PI / 2, 0, 0.03]} s={[1.05, 1.32]} px={[300, 380]} draw={(c, W, H) => herbalPage(c, W, H, 2, glow)} />
    <Box p={[0, 0.02, 0]} s={[0.04, 0.06, 1.32]} color="#3a2414" line={1} />
  </group>
);
const Txt: React.FC<{ p: V3; s: [number, number]; lines: string[]; bg?: string; fg?: string; size?: number; frame?: string; rot?: V3 }> = ({ p, s, lines, bg = "#2a1a10", fg = "#ffd98a", size = 70, frame = "#0b0d1a", rot }) => (
  <CanvasPlane p={p} s={s} rot={rot} frame={frame} px={[Math.round(s[0] * 200), Math.round(s[1] * 200)]} draw={(c, W, H) => { c.fillStyle = bg; c.fillRect(0, 0, W, H); c.fillStyle = fg; c.font = `900 ${size}px ${KF}`; c.textAlign = "center"; c.textBaseline = "middle"; lines.forEach((l, i) => c.fillText(l, W / 2, H / 2 + (i - (lines.length - 1) / 2) * size * 1.15)); }} />
);

/* =================== S1 0 – 5.85 bookshop =================== */
const K1: Key[] = [
  { t: 0, pos: [-0.2, 2.75, 1.9], look: [-0.3, 1.3, 0.5], fov: 50 },
  { t: 1.15, pos: [0.3, 2.9, 4.6], look: [0.1, 1.9, 0.1], fov: 56 },
  { t: 2.4, pos: [1.0, 2.8, 7.0], look: [0.5, 2.1, -0.1], fov: 58 },
  { t: 3.8, pos: [0.0, 2.8, 4.6], look: [0.0, 1.7, 0.3], fov: 54, roll: -0.03 },
  { t: 5.95, pos: [0.9, 2.7, 5.4], look: [0.7, 2.0, 0.5], fov: 56 },
];
const S1 = ({ t, f }: Ctx) => {
  const wk = seg(t, 0.9, 2.3, Easing.inOut(Easing.sin)), dx = lerp(3.2, 0.95, wk), moving = t > 0.9 && t < 2.3;
  const dealerMood = t < 2.4 ? "smile" : t < 4.6 ? "worry" : "grin";
  const pay = seg(t, 4.5, 4.75, Easing.in(Easing.quad)), bounce = t > 4.75 ? Math.abs(Math.sin((t - 4.75) * 14)) * Math.exp(-(t - 4.75) * 7) * 0.15 : 0;
  const coinY = lerp(2.5, 1.33, pay) + bounce, coinX = lerp(0.9, 0.45, pay);
  const glow = 0.5 + 0.5 * Math.sin(t * 3);
  return (<>
    <Cam t={t} keys={K1} impacts={[[4.75, 0.03]]} />
    <Lights warm="#ffcf8a" />
    <Floor kind="plank" a="#6a3a1e" b="#5e331a" unit={1.6} w={26} d={26} />
    <WallDoor z={-4} W={26} kind="wood" a="#5a3420" b="#4e2c1a" base="#2a160c" door={{ x: -5.2, w: 2.2, h: 4.0 }} />
    <SideWall x={-7} kind="wood" a="#4e2c1a" b="#44261a" /><SideWall x={7} kind="wood" a="#4e2c1a" b="#44261a" />
    {[-4.4, -1.4, 1.6, 4.6].map((x, i) => <Shelf key={x} p={[x, 0, -3.5]} w={2.8} rows={5} seed={i + 2} wood="#3e2214" />)}
    <Txt p={[0, 6.6, -3.85]} s={[5.6, 0.9]} lines={["고서점 · ANTIQUARIAT · 1912"]} size={52} bg="#1e120a" fg="#ffcf6a" />
    <Clock p={[4.0, 6.5, -3.85]} r={0.55} t={t} speed={6} />
    <Frame p={[-4.2, 6.3, -3.85]} s={[1.3, 1.0]} art={1} />
    <HangLamp p={[0.2, 5.4, -0.6]} color="#c9852a" o={1.2} />
    <Glow p={[-0.3, 1.6, 0.7]} r={1.3} color="rgba(255,200,90,1)" o={0.35 * glow} />
    {/* counter */}
    <Box p={[0, 0.6, 0.6]} s={[4.2, 1.2, 1.3]} color="#7a4426" />
    <Box p={[0, 1.24, 0.6]} s={[4.5, 0.1, 1.5]} color="#9a5a32" />
    {[-1.4, 0, 1.4].map((x) => <Box key={x} p={[x, 0.6, 1.27]} s={[1.1, 0.8, 0.04]} color="#8a4e2c" line={2} />)}
    <Book p={[-0.35, 1.32, 0.6]} rotY={0.12} s={0.7} glow={glow * 0.6} />
    <Lamp p={[-1.75, 1.29, 0.45]} h={0.8} color="#ffd27a" /><Glow p={[-1.75, 2.25, 0.5]} r={0.9} color="rgba(255,210,120,1)" o={0.55} />
    {[0, 1, 2, 3].map((i) => <Box key={i} p={[1.65, 1.36 + i * 0.13, 0.35 + (i % 2) * 0.05]} s={[0.8, 0.12, 0.55]} color={["#8a2a2a", "#2a4a8a", "#3a6a3a", "#7a5a2a"][i]} line={2} />)}
    {t > 4.45 ? [0, 1, 2].map((i) => <Cyl key={i} p={[coinX + i * 0.16, coinY + (t > 4.75 ? 0.02 : i * 0.08), 0.75 + i * 0.05]} rt={0.11} h={0.04} color="#f2c03a" line={2} />) : null}
    <Plant p={[-5.8, 0, -1.5]} s={1.2} /><Rug p={[1.5, 0.01, 2.6]} s={[3.2, 2.2]} a="#7a2a2a" b="#a8483a" />
    <Person p={[-1.1, 0, -0.35]} h={3.2} look={keeper} f={f} pose={{ mood: t < 4.75 ? "deadpan" : "grin", arms: t < 2.4 ? "down" : "point", armK: seg(t, 2.4, 2.8), lookX: 0.5 }} />
    <Person p={[dx, 0, 1.55]} h={3.35} look={dealer} f={f} pose={{ walk: (3.2 - dx) * WALK, speed: moving ? 1 : 0, flip: moving, mood: dealerMood as any, arms: t > 4.4 ? "point" : t > 2.4 ? "chest" : "down", armK: t > 4.4 ? seg(t, 4.4, 4.6) * (1 - seg(t, 5.1, 5.4)) : seg(t, 2.4, 2.7), lookX: -0.6, nerv: t > 2.4 && t < 4.5 ? 0.3 : 0, sweat: t > 3.0 && t < 4.6 ? 0.6 : 0 }} />
    <Dust t={t} area={[3, 4, 2]} color="rgba(255,220,150,.8)" />
  </>);
};

/* =================== S2 5.85 – 10.3 study =================== */
const K2: Key[] = [
  { t: 5.7, pos: [-3.0, 3.3, 4.8], look: [-2.3, 3.4, -1.5], fov: 56 },
  { t: 7.25, pos: [-0.7, 2.6, 5.2], look: [-0.1, 2.3, 0], fov: 56 },
  { t: 8.5, pos: [1.7, 2.7, 4.8], look: [0.7, 2.7, -1.5], fov: 56, roll: 0.02 },
  { t: 9.45, pos: [0.3, 3.5, 7.8], look: [0, 3.0, -1.5], fov: 62 },
  { t: 10.45, pos: [0.2, 3.6, 8.3], look: [0, 3.1, -1.5], fov: 62 },
];
const S2 = ({ t, f }: Ctx) => {
  const yr = Math.round(lerp(1912, 2024, seg(t, 5.98, 7.4, Easing.inOut(Easing.cubic))));
  const fail = seg(t, 9.44, 9.75), xk = seg(t, 9.44, 9.9);
  return (<>
    <Cam t={t} keys={K2} impacts={[[9.44, 0.025]]} />
    <Lights warm="#bcd4ff" />
    <Floor kind="carpet" a="#2a3a6a" b="#24335e" unit={2} />
    <WallDoor z={-4} W={26} kind="plain" a="#2c4a7a" b="#2c4a7a" base="#14234a" />
    <SideWall x={-7} kind="plain" a="#284270" b="#284270" /><SideWall x={7} kind="plain" a="#284270" b="#284270" />
    {/* chalkboard of glyphs */}
    <Box p={[0.6, 4.1, -3.9]} s={[5.4, 3.0, 0.12]} color="#5a3a1e" />
    <CanvasPlane p={[0.6, 4.1, -3.82]} s={[5.0, 2.6]} px={[1000, 520]} draw={(c, W, H) => {
      c.fillStyle = "#1f3a2e"; c.fillRect(0, 0, W, H);
      for (let l = 0; l < 6; l++) glyphLine(c, 40, 70 + l * 78, W - 80, 46, 50 + l * 9, "rgba(240,240,230,.9)");
      c.fillStyle = "rgba(255,240,140,.95)"; c.font = `900 64px ${KF}`; c.textAlign = "center"; c.fillText("= ? ? ?", W * 0.78, H * 0.92);
      if (xk > 0) { c.strokeStyle = "#ff3b3b"; c.lineWidth = 30; c.lineCap = "round"; c.beginPath(); c.moveTo(W * 0.15, H * 0.12); c.lineTo(W * 0.15 + W * 0.7 * Math.min(1, xk * 2), H * 0.12 + H * 0.76 * Math.min(1, xk * 2)); c.stroke(); if (xk > 0.5) { const k = (xk - 0.5) * 2; c.beginPath(); c.moveTo(W * 0.85, H * 0.12); c.lineTo(W * 0.85 - W * 0.7 * k, H * 0.12 + H * 0.76 * k); c.stroke(); } }
    }} />
    {/* year flip board */}
    <Box p={[-3.1, 4.6, -3.9]} s={[2.3, 1.5, 0.12]} color="#1b1f33" />
    <CanvasPlane p={[-3.1, 4.6, -3.82]} s={[2.1, 1.3]} px={[420, 260]} draw={(c, W, H) => { c.fillStyle = "#fffaf0"; c.fillRect(0, 0, W, H); c.fillStyle = "#e23b3b"; c.fillRect(0, 0, W, 64); c.fillStyle = "#fff"; c.font = `900 44px ${KF}`; c.textAlign = "center"; c.textBaseline = "middle"; c.fillText("YEAR", W / 2, 34); c.fillStyle = "#0b0d1a"; c.font = `900 150px ${KF}`; c.fillText(String(yr), W / 2, 168); }} />
    <Shelf p={[-5.2, 0, -3.5]} w={2.6} rows={5} seed={5} wood="#3a2a4a" /><Shelf p={[5.0, 0, -3.5]} w={2.6} rows={5} seed={7} wood="#3a2a4a" />
    <Glow p={[0, 3.2, 0.2]} r={2.4} color="rgba(190,215,255,1)" o={0.25} />
    <Shaft p={[2.6, 4.2, -2.0]} s={[1.6, 7]} rot={[0, 0, 0.35]} color="200,220,255" o={0.22} />
    {/* scholars behind desk */}
    {sch.map((lk, i) => { const x = -1.7 + i * 1.7, nerv = t > 7.3 ? 0.35 + fail * 0.4 : 0.1; return (
      <Person key={i} p={[x, 0, -0.3]} h={3.0} look={lk} f={f + i * 7} pose={{ mood: t > 9.44 ? "shock" : t > 7.28 ? "worry" : "deadpan", arms: t > 9.44 ? "head" : i === 1 ? "point" : "chest", armK: t > 9.44 ? fail : 0.8, nerv, sweat: t > 7.6 ? 0.5 + fail * 0.5 : 0, lookX: i === 0 ? 0.5 : -0.3, squash: t > 9.44 && t < 9.7 ? -0.12 : 0, hunch: t > 8.5 ? 0.3 : 0 }} />); })}
    <Desk p={[0, 0, 0.9]} w={5.8} top="#7a5236" leg="#5a3a22" d={1.5} />
    {[-2.2, -1.0, 1.3, 2.3].map((x, i) => <React.Fragment key={x}>{Array.from({ length: 3 + i }, (_, k) => <Box key={k} p={[x, 1.17 + k * 0.06, 0.8 + (k % 2) * 0.04]} s={[0.75, 0.05, 0.55]} color={k % 2 ? "#f4f0e2" : "#ffffff"} line={1} />)}</React.Fragment>)}
    <Book p={[0.1, 1.18, 0.95]} s={0.55} rotY={-0.1} />
    {/* magnifier */}
    <group position={[0.75, 1.3, 1.25]} rotation={[-1.2, 0, 0.5 + Math.sin(t * 2) * 0.1]}><Cyl p={[0, 0, 0]} rt={0.28} h={0.05} color="#d6f0ff" line={3} /><Box p={[0, 0, -0.45]} s={[0.08, 0.06, 0.5]} color="#3a2414" line={2} /></group>
    {t > 9.44 ? <Dust t={t - 9.44} n={12} area={[2.6, 4.5, 1.5]} color="rgba(255,255,255,.95)" fall /> : <Dust t={t} area={[3, 4, 2]} color="rgba(200,220,255,.7)" />}
    <Cabinet p={[-6.0, 0, -2]} color="#3a4a7a" />
  </>);
};

/* =================== S3 10.3 – 15.13 golden lab =================== */
const K3: Key[] = [
  { t: 10.15, pos: [-1.3, 2.35, 1.6], look: [-1.25, 1.35, 0.15], fov: 50 },
  { t: 11.6, pos: [-1.5, 2.8, 5.4], look: [-0.2, 2.3, -0.6], fov: 58 },
  { t: 12.6, pos: [0.5, 3.0, 5.0], look: [0.7, 3.0, -1.6], fov: 56 },
  { t: 13.15, pos: [0.6, 3.1, 4.1], look: [0.6, 3.1, -1.8], fov: 52, roll: 0.04 },
  { t: 15.2, pos: [0.4, 2.9, 4.0], look: [0.5, 2.8, -1.8], fov: 52, roll: 0.06 },
];
const HIT = 13.12;
const S3 = ({ t, f }: Ctx) => {
  const cnt = Math.round(600 * seg(t, 11.1, HIT, Easing.out(Easing.cubic))), pop = seg(t, HIT, HIT + 0.3, Easing.out(Easing.back(3)));
  const jt = clamp((t - HIT) / 0.42), air = t > HIT && t < HIT + 0.42 ? Math.sin(jt * Math.PI) * 0.6 : 0;
  const land = t >= HIT + 0.42 ? Math.max(0, 1 - (t - HIT - 0.42) / 0.2) : 0;
  const sq = t < HIT - 0.15 ? 0 : t < HIT ? -0.15 : t < HIT + 0.42 ? 0.14 : -0.22 * land;
  const sx = lerp(0.1, -0.35, Easing.out(Easing.quad)(jt));
  return (<>
    <Cam t={t} keys={K3} impacts={[[HIT, 0.06]]} />
    <Lights warm="#ffd08a" />
    <Floor kind="tile" a="#c99a52" b="#b98a44" unit={1.4} />
    <WallDoor z={-4} W={26} kind="plain" a="#8a5a2a" b="#8a5a2a" base="#4a2a12" />
    <SideWall x={-7} kind="plain" a="#7a4e24" b="#7a4e24" /><SideWall x={7} kind="plain" a="#7a4e24" b="#7a4e24" />
    {/* readout screen */}
    <Box p={[0.8, 3.15, -1.95]} s={[2.5, 2.0, 0.14]} color="#1b1f33" />
    <CanvasPlane p={[0.8, 3.15, -1.86]} s={[2.3, 1.8]} px={[690, 540]} frame="#ffc23a" draw={(c, W, H) => {
      c.fillStyle = "#0e1630"; c.fillRect(0, 0, W, H); c.strokeStyle = "rgba(255,200,120,.18)"; c.lineWidth = 2; for (let i = 1; i < 6; i++) { c.beginPath(); c.moveTo(0, H * i / 6); c.lineTo(W, H * i / 6); c.stroke(); }
      c.textAlign = "center"; c.textBaseline = "middle"; c.fillStyle = "#ffd98a"; c.font = `900 46px ${KF}`; c.fillText("방사성 탄소 연대측정", W / 2, 50); c.font = `800 30px ${KF}`; c.fillStyle = "#9fb4ff"; c.fillText("CARBON-14 · 종이 샘플 #4", W / 2, 96);
      c.save(); c.translate(W / 2, H * 0.48); const s = 1 + 0.35 * pop * Math.exp(-(t - HIT) * 2.5); c.scale(s, s); c.font = `900 190px ${KF}`; c.lineWidth = 14; c.strokeStyle = "#000"; c.strokeText(String(cnt), 0, 0); c.fillStyle = t >= HIT ? "#ffcf3a" : "#ffffff"; c.fillText(String(cnt), 0, 0); c.restore();
      c.font = `900 56px ${KF}`; c.fillStyle = "#fff"; c.fillText("년 전", W / 2, H * 0.7);
      c.fillStyle = "#2a3350"; c.fillRect(60, H * 0.82, W - 120, 26); c.fillStyle = "#ffc23a"; c.fillRect(60, H * 0.82, (W - 120) * clamp(cnt / 600), 26);
      if (t > HIT) { c.globalAlpha = pop; c.fillStyle = "#ff5a3a"; c.font = `900 44px ${KF}`; c.fillText("1404 – 1438", W / 2, H * 0.93); c.globalAlpha = 1; }
    }} />
    <Glow p={[0.8, 3.15, -1.6]} r={2.6} color="rgba(255,190,80,1)" o={t > HIT ? 0.35 : 0.15} />
    {/* pedestal + book under spot */}
    <Cyl p={[-1.25, 0.6, 0.15]} rt={0.55} rb={0.7} h={1.2} color="#e8d2a0" />
    <Book p={[-1.25, 1.25, 0.15]} s={0.48} rotY={0.25} glow={1} />
    <SpotCone p={[-1.25, 6.0, 0.15]} h={5} r={1.3} color="#ffe2a0" o={0.18} />
    <Glow p={[-1.25, 1.4, 0.3]} r={1.2} color="rgba(255,220,130,1)" o={0.5 + 0.15 * Math.sin(t * 4)} />
    {/* lab dressing */}
    <Desk p={[3.4, 0, -1.2]} w={2.6} top="#e9edf7" leg="#aab7dc" />
    {[0, 1, 2, 3].map((i) => <Cyl key={i} p={[2.6 + i * 0.5, 1.4, -1.2]} rt={0.12} rb={0.2} h={0.5} color={["#7ec8ff", "#ff9a7a", "#9aff9a", "#ffd27a"][i]} line={2} />)}
    <Shelf p={[-4.6, 0, -3.5]} w={2.8} rows={5} seed={9} wood="#6a4220" /><Frame p={[3.6, 5.0, -3.85]} s={[1.4, 1.0]} art={2} />
    <Txt p={[-1.6, 5.6, -3.85]} s={[3.2, 0.8]} lines={["연대측정 연구실"]} size={70} bg="#3a2210" fg="#ffd98a" />
    <Person p={[sx, air, 0.4]} sy={0} h={3.1} look={sci} f={f} pose={{ mood: t >= HIT ? "shock" : t > 11.9 ? "worry" : "deadpan", arms: t >= HIT ? "head" : "point", armK: t >= HIT ? seg(t, HIT, HIT + 0.2) : seg(t, 11.0, 11.4), squash: sq, lookX: 0.6, sweat: t > HIT ? 1 : 0, nerv: t > HIT ? 0.6 : 0.1, air: air > 0 ? 1 : 0 }} />
    <Dust t={t} area={[3, 4.5, 2]} color="rgba(255,220,140,.9)" />
  </>);
};

export const Voynich: React.FC = () => (
  <AbsoluteFill style={{ background: "#000" }}>
    <Audio src={staticFile("mix.wav")} />
    <Scene first start={0} end={5.85} bg="#2a1810">{(c) => <S1 {...c} />}</Scene>
    <Scene start={5.85} end={10.3} trans="zoom" bg="#101a33">{(c) => <S2 {...c} />}</Scene>
    <Scene start={10.3} end={15.14} trans="flash" bg="#3a2210">{(c) => <S3 {...c} />}</Scene>
    <AbsoluteFill style={{ pointerEvents: "none" }}><GradeTop /></AbsoluteFill>
    <Captions />
  </AbsoluteFill>
);
const GradeTop: React.FC = () => { const f = useCurrentFrame(); return <Grade t={f / FPS} shaft={false} />; };
void Ball;
