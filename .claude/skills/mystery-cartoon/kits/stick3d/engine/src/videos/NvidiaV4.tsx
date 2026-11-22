// NVIDIA v4 — fresh direction (no layout reused from the v3 demo). 9:16 720x1280 30fps.
// S1 trading floor at night: giant up-arrow snaps & spears the floor, analyst jumps back, mug flies.
// S2 keynote stage: CEO lifts the crown off his head, sets it on the lectern, walks off into the wings.
// S3 giant casino table: tiny analyst pushes W1, six dominoes fall, chain runs all the way to "SINCE 2012".
// S4 Wall Street golden hour: Kress crosses the street, faces the press pack, banner unrolls NOV 17.
// S5 night arena: the AI throne on top of the globe shakes, the crown falls, the whole world watches.
import React from "react";
import { AbsoluteFill, Sequence, useCurrentFrame, Easing, Audio, staticFile } from "remotion";
import { ThreeCanvas } from "@remotion/three";
import { Box, Cyl, Ball, CanvasPlane, Surface, INK } from "../style/toon";
import { Look } from "../style/puppet";
import { Person, Lights, Desk, Clock, Calendar, Grade, seg, lerp, clamp, V3 } from "../style/kit";
import { Floor, WallDoor, SideWall, Glow, Shaft, Plant, Shelf, Frame, WindowCity, Lamp, Monitor, Chair, Cooler, Cabinet, Rug, Dust } from "../style/props";
import { Cam, Key, camAt, FaceGroup, hand, Arrow3D, Domino, Globe, Crown, Throne, SpotCone, Curtain, Lectern, Building, StreetLamp, StreetSign, Taxi, Hydrant, Bench, Bin, Barrier, PressCam, ChipStack, Card, Dice, HangLamp, Mug, Stars } from "../style/extra";
import { Captions } from "../Main";

const FPS = 30, LEAD = 6, TAIL = 8, WALK = 3.4;
type Ctx = { t: number; f: number };
type Trans = "ghost" | "zoom" | "flash" | "whip";

const analyst: Look = { skin: "#fbe3c8", body: "#ff8a1c", outfit: "hoodie", hair: "short", hairColor: "#1b1b2a", glasses: true, badge: "#2fd46a", shoe: "#1b1b2a" };
const ceo: Look = { skin: "#f1d0b0", body: "#16171f", outfit: "leather", hair: "swept", hairColor: "#c9c9d2", shoe: "#0b0d1a" };
const kress: Look = { skin: "#f7d4b5", body: "#1f8a8a", outfit: "blazer", shirt: "#ffffff", hair: "bob", hairColor: "#5a3420", badge: "#ffc23a", shoe: "#2a1a12" };
const crowd: Look[] = [
  { skin: "#fbe3c8", body: "#e53e3e", outfit: "hoodie", hair: "short", hairColor: "#222" }, { skin: "#c98e62", body: "#22a867", outfit: "shirt", hair: "bob", hairColor: "#1a1010" },
  { skin: "#fbe3c8", body: "#f0b429", outfit: "suit", tie: "#1d2f66", hair: "grey" }, { skin: "#8d5a3a", body: "#7c4dff", outfit: "hoodie", hair: "swept", hairColor: "#111", glasses: true },
  { skin: "#f6d6bd", body: "#2d3142", outfit: "suit", tie: "#ff3b3b", hair: "short", hairColor: "#3b2a1a" }, { skin: "#e0b48c", body: "#ff7a29", outfit: "shirt", hair: "bob", hairColor: "#5a3420" },
  { skin: "#fbe3c8", body: "#2f8cff", outfit: "blazer", shirt: "#fff", hair: "swept", hairColor: "#c47a2a" }, { skin: "#a86b45", body: "#ff4fa0", outfit: "hoodie", hair: "short", hairColor: "#111", glasses: true },
];

/* ---------- scene wrapper with 4 transition kinds ---------- */
const Scene: React.FC<{ start: number; end: number; first?: boolean; trans?: Trans; bg: string; children: (c: Ctx) => React.ReactNode }> = ({ start, end, first, trans = "ghost", bg, children }) => {
  const from = Math.round(start * FPS) - (first ? 0 : LEAD), dur = Math.round(end * FPS) - from + TAIL;
  return <Sequence from={from} durationInFrames={dur} layout="none"><Inner from={from} first={first} trans={trans} bg={bg} children={children} /></Sequence>;
};
const Inner: React.FC<{ from: number; first?: boolean; trans: Trans; bg: string; children: (c: Ctx) => React.ReactNode }> = ({ from, first, trans, bg, children }) => {
  const f = useCurrentFrame(), t = (f + from) / FPS;
  const k = first ? 1 : clamp(f / (LEAD + 2)), ke = Easing.out(Easing.cubic)(k);
  const sc = !first && trans === "zoom" ? lerp(1.35, 1, ke) : 1;
  const tx = !first && trans === "whip" ? (1 - ke) * 720 : 0, blur = !first && trans === "whip" ? (1 - ke) * 14 : 0;
  return (
    <AbsoluteFill style={{ opacity: first || trans === "flash" || trans === "whip" ? 1 : k, transform: `translateX(${tx}px) scale(${sc})`, background: bg, filter: `saturate(1.32) contrast(1.07) brightness(1.02)${blur > 0.2 ? ` blur(${blur.toFixed(1)}px)` : ""}` }}>
      <ThreeCanvas width={720} height={1280} camera={{ fov: 60, position: [0, 2, 8], near: 0.1, far: 200 }} gl={{ antialias: true }}>
        <color attach="background" args={[bg]} />{children({ t, f })}
      </ThreeCanvas>
      {!first && trans === "flash" ? <AbsoluteFill style={{ background: "#fff", opacity: 1 - clamp(f / 7) }} /> : null}
    </AbsoluteFill>
  );
};
const yawTo = (cam: V3, p: V3) => Math.atan2(cam[0] - p[0], cam[2] - p[2]);
// local (billboard) offset -> world, for a puppet at p seen from cam
const toWorld = (p: V3, loc: V3, cam: V3): V3 => { const y = yawTo(cam, p); return [p[0] + loc[0] * Math.cos(y) + loc[2] * Math.sin(y), p[1] + loc[1], p[2] - loc[0] * Math.sin(y) + loc[2] * Math.cos(y)]; };

/* =================== S1 0 – 4.75  "Nvidia just lost $1.7 trillion in six weeks." =================== */
const K1: Key[] = [
  { t: 0, pos: [3.2, 6.6, 7.6], look: [1.0, 1.2, -0.8], fov: 60 },
  { t: 0.83, pos: [2.9, 5.6, 8.0], look: [0.0, 2.6, -1.6], fov: 60 },
  { t: 1.2, pos: [2.7, 4.2, 8.2], look: [0.4, 2.0, -1.6], fov: 60 },
  { t: 2.7, pos: [2.2, 3.0, 8.4], look: [1.0, 2.6, -2.2], fov: 56 },
  { t: 3.45, pos: [1.2, 3.1, 6.4], look: [0.0, 2.7, -7.0], fov: 56 },
  { t: 4.95, pos: [0.3, 3.4, 5.4], look: [0.0, 2.6, -7.5], fov: 56 },
];
const A0 = 0.83, AL = 1.16, AX = -1.7, AZ = -1.7;
const arrowY = (t: number) => t < A0 ? 6.6 + Math.sin(t * 1.3) * 0.04 : lerp(6.6, 1.45, clamp((t - A0) / (AL - A0)) ** 2);
const arrowR = (t: number) => t < A0 ? Math.sin(t * 1.1) * 0.03 : t < AL ? Math.PI * 0.93 * Easing.inOut(Easing.sin)(clamp((t - A0) / (AL - A0))) : Math.PI * 0.93 + 0.07 * Math.exp(-(t - AL) * 6) * Math.sin((t - AL) * 28);
const J0 = 1.16, JD = 0.42;
const anaS1 = (t: number) => {
  const jt = clamp((t - J0) / JD), air = t > J0 && t < J0 + JD ? Math.sin(jt * Math.PI) * 0.7 : 0;
  const land = t >= J0 + JD ? Math.max(0, 1 - (t - J0 - JD) / 0.2) : 0;
  const sq = t < 0.98 ? 0 : t < J0 ? -0.16 * seg(t, 0.98, J0, Easing.linear) : t < J0 + JD ? 0.14 : -0.24 * land;
  return { x: lerp(1.5, 2.4, Easing.out(Easing.quad)(jt)), y: air, sq };
};
const sipK = (t: number) => seg(t, 0.0, 0.25, Easing.inOut(Easing.sin)) * (1 - seg(t, 0.45, 0.65, Easing.inOut(Easing.sin)));
const mugHand = (t: number): [number, number] => { const k = sipK(t); return [lerp(0.25, 0.07, k), lerp(0.40, 0.53, k)]; };
const MR = 1.2; // mug released (jump)
const S1 = ({ t, f }: Ctx) => {
  const a = anaS1(t), P: V3 = [a.x, a.y, 0.9], h = 3.5;
  const shock = t >= J0, nerv = t < A0 ? 0 : t < J0 ? 0.35 : t < 2.6 ? 0.8 : 0.35;
  const cam = camAt(t, K1).pos;
  // mug: held until MR, then a ballistic arc
  const camR = camAt(MR, K1).pos, rel = toWorld([lerp(1.5, 2.4, Easing.out(Easing.quad)(clamp((MR - J0) / JD))), Math.sin(clamp((MR - J0) / JD) * Math.PI) * 0.7, 0.9], hand(h, mugHand(MR), 0.14, false, 0.12), camR);
  const dt = t - MR, v = [-1.6, 4.6, 1.0], g = 20;
  const tLand = (v[1] + Math.sqrt(v[1] * v[1] + 2 * g * (rel[1] + 0.12 - 0.18))) / g;
  const fl = Math.min(dt, tLand), slide = Math.max(0, dt - tLand);
  const mugW: V3 = [rel[0] + v[0] * fl + (dt > tLand ? -0.5 * (1 - Math.exp(-slide * 6)) : 0), dt > tLand ? 0.18 : rel[1] + 0.12 + v[1] * fl - 0.5 * g * fl * fl, rel[2] + v[2] * fl + (dt > tLand ? 0.3 * (1 - Math.exp(-slide * 6)) : 0)];
  const puddle = dt > tLand ? seg(t, MR + tLand, MR + tLand + 0.7) : 0;
  const prog = clamp(t / 4.5), k17 = seg(t, AL, AL + 1.1, Easing.out(Easing.cubic)), pop = seg(t, AL, AL + 0.28, Easing.out(Easing.back(3)));
  const debris = [0, 1, 2, 3, 4].map((i) => { const ang = i * 1.3 + 0.4, vv: V3 = [Math.cos(ang) * 2.6, 4.2 + i * 0.6, Math.sin(ang) * 1.8], d = Math.max(0, t - AL), tl = (vv[1] + Math.sqrt(vv[1] ** 2 + 2 * g * 0.1)) / g, q = Math.min(d, tl); return [AX + vv[0] * q, Math.max(0.08, 0.1 + vv[1] * q - 0.5 * g * q * q), AZ + vv[2] * q] as V3; });
  return (<>
    <Cam t={t} keys={K1} impacts={[[AL, 0.07]]} />
    <Lights warm="#cdf6ff" />
    <Floor kind="tile" a="#12505c" b="#0f4450" unit={1.8} w={30} d={30} />
    <WallDoor z={-8} W={30} kind="plain" a="#0d3a48" b="#0d3a48" base="#061e26" />
    <SideWall x={-11} kind="plain" a="#0f4452" b="#0f4452" /><SideWall x={11} kind="plain" a="#0f4452" b="#0f4452" />
    <WindowCity p={[-8.0, 4.8, -7.9]} s={[3.6, 4.2]} dusk /><WindowCity p={[8.0, 4.8, -7.9]} s={[3.6, 4.2]} dusk />
    {/* LED index wall */}
    <Box p={[0, 5.0, -7.75]} s={[9.6, 4.8, 0.2]} color="#0a1a22" />
    <CanvasPlane p={[0, 5.0, -7.6]} s={[9.2, 4.4]} px={[920, 440]} frame={t > AL && Math.sin(f * 0.9) > 0 ? "#ff2b3b" : "#1d6f7f"} draw={(c, W, H) => {
      c.fillStyle = "#06141c"; c.fillRect(0, 0, W, H); c.strokeStyle = "rgba(80,220,240,.16)"; c.lineWidth = 2; for (let i = 1; i < 8; i++) { c.beginPath(); c.moveTo(0, H * i / 8); c.lineTo(W, H * i / 8); c.stroke(); c.beginPath(); c.moveTo(W * i / 8, 0); c.lineTo(W * i / 8, H); c.stroke(); }
      c.fillStyle = "#7fe8ff"; c.font = "800 34px Inter, Arial"; c.textAlign = "left"; c.fillText("AI CHIP INDEX  •  LIVE", 24, 46);
      const pts: [number, number][] = [[0.03, 0.62], [0.12, 0.55], [0.2, 0.48], [0.28, 0.4], [0.36, 0.3], [0.42, 0.24], [0.5, 0.42], [0.58, 0.5], [0.66, 0.62], [0.74, 0.7], [0.84, 0.82], [0.97, 0.92]];
      const n = Math.max(0.01, (t < AL ? lerp(0, 5, clamp(t / AL)) : lerp(5, pts.length - 1, prog * 1.15 - 0.15)));
      c.lineWidth = 9; c.lineJoin = "round"; c.strokeStyle = t < AL ? "#2fd46a" : "#ff2b3b"; c.beginPath(); let lx = 0, ly = 0;
      for (let i = 0; i <= Math.min(Math.floor(n), pts.length - 1); i++) { lx = pts[i][0] * W; ly = pts[i][1] * H; i ? c.lineTo(lx, ly) : c.moveTo(lx, ly); }
      const i0 = Math.floor(n); if (i0 < pts.length - 1) { const r = n - i0; lx = lerp(pts[i0][0], pts[i0 + 1][0], r) * W; ly = lerp(pts[i0][1], pts[i0 + 1][1], r) * H; c.lineTo(lx, ly); } c.stroke();
      c.fillStyle = c.strokeStyle; c.beginPath(); c.arc(lx, ly, 13, 0, 7); c.fill();
      if (t > AL) { c.save(); c.translate(W * 0.5, H * 0.36); const s = 0.55 + 0.45 * pop; c.scale(s, s); c.font = "900 170px Inter, Arial"; c.textAlign = "center"; c.textBaseline = "middle"; c.lineWidth = 14; c.strokeStyle = "#000"; const txt = `-$${(1.7 * k17).toFixed(1)}T`; c.strokeText(txt, 0, 0); c.fillStyle = "#ff2b3b"; c.fillText(txt, 0, 0); c.restore(); }
    }} />
    <Glow p={[0, 5, -7.0]} r={5.4} color={t > AL ? "rgba(255,40,60,0.8)" : "rgba(40,220,255,0.6)"} o={t > AL ? 0.32 + 0.1 * Math.sin(f * 0.9) : 0.18} />
    {/* six week flip tiles */}
    <Box p={[0, 2.15, -7.7]} s={[8.2, 1.1, 0.2]} color="#0a1a22" />
    {[0, 1, 2, 3, 4, 5].map((i) => { const fk = seg(t, 3.43 + i * 0.13, 3.55 + i * 0.13, Easing.inOut(Easing.cubic)); return (
      <group key={i} position={[-3.1 + i * 1.24, 2.15, -7.5]} rotation={[fk * Math.PI, 0, 0]}>
        <CanvasPlane p={[0, 0, 0.02]} s={[1.08, 0.82]} px={[160, 120]} frame="#0b0d1a" draw={(c, W, H) => { c.fillStyle = "#1d6f7f"; c.fillRect(0, 0, W, H); c.fillStyle = "#dff9ff"; c.font = "900 56px Inter, Arial"; c.textAlign = "center"; c.textBaseline = "middle"; c.fillText(`W${i + 1}`, W / 2, H / 2 + 3); }} />
        <CanvasPlane p={[0, 0, -0.02]} rot={[Math.PI, 0, 0]} s={[1.08, 0.82]} px={[160, 120]} draw={(c, W, H) => { c.fillStyle = "#ff2b3b"; c.fillRect(0, 0, W, H); c.fillStyle = "#fff"; c.font = "900 50px Inter, Arial"; c.textAlign = "center"; c.textBaseline = "middle"; c.fillText(`W${i + 1}▼`, W / 2, H / 2 + 3); }} />
      </group>); })}
    {/* ticker strip */}
    <CanvasPlane p={[0, 7.85, -7.6]} s={[16, 0.6]} px={[1600, 60]} draw={(c, W, H) => { c.fillStyle = "#04121a"; c.fillRect(0, 0, W, H); c.font = "800 40px Inter, Arial"; c.textBaseline = "middle"; const txt = "AI ▼ 9.8%    CHIPS ▼ 7.1%    TECH ▼ 4.4%    GPU ▼ 8.2%    "; const tw = c.measureText(txt).width; const off = -((f * 9) % tw); for (let k = 0; k < 3; k++) { c.fillStyle = "#ff4a5a"; c.fillText(txt, off + k * tw, H / 2 + 2); } }} />
    {/* furniture & dressing */}
    <Desk p={[-4.6, 0, -4.2]} w={3.6} top="#d9f1f5" leg="#7aa9b4" /><Monitor p={[-5.2, 1.1, -4.3]} rot={[0, 0.3, 0]} screen="#ff3b4b" /><Monitor p={[-4.0, 1.1, -4.3]} rot={[0, 0.15, 0]} screen="#1d6f7f" />
    <Desk p={[4.8, 0, -4.4]} w={3.6} top="#d9f1f5" leg="#7aa9b4" /><Monitor p={[4.3, 1.1, -4.5]} rot={[0, -0.2, 0]} screen="#ff3b4b" /><Monitor p={[5.5, 1.1, -4.5]} rot={[0, -0.3, 0]} screen="#ff3b4b" />
    <Desk p={[-5.6, 0, 1.2]} w={3.2} top="#d9f1f5" leg="#7aa9b4" /><Monitor p={[-5.8, 1.1, 1.1]} rot={[0, 0.5, 0]} screen="#ff3b4b" />
    <Chair p={[-4.6, 0, -2.8]} rotY={0.3} color="#1d6f7f" /><Chair p={[4.8, 0, -3.0]} rotY={-0.4} color="#1d6f7f" /><Chair p={[-5.0, 0, 2.6]} rotY={0.8} color="#ff8a1c" />
    <Shelf p={[-9.4, 0, -7.2]} w={2.6} rows={4} seed={3} wood="#0a2a34" /><Cabinet p={[9.2, 0, -7.0]} color="#3c7f8f" /><Cooler p={[7.4, 0, -6.6]} />
    <Plant p={[-2.6, 0, -6.8]} s={1.2} /><Plant p={[2.8, 0, -6.8]} s={1.2} /><Plant p={[7.2, 0, 1.4]} s={1.1} />
    {[-6.6, 6.6].map((x) => <React.Fragment key={x}><Cyl p={[x, 4.5, -5.4]} rt={0.42} h={9} color="#1a5c6a" /><Cyl p={[x, 0.2, -5.4]} rt={0.6} h={0.4} color="#ffc23a" /></React.Fragment>)}
    <Clock p={[-6.6, 6.2, -4.95]} r={0.5} t={t} /><Frame p={[5.6, 3.0, -7.9]} s={[1.2, 0.9]} art={2} /><Lamp p={[-7.6, 0, -1.2]} h={3} color="#cdf6ff" />
    <Rug p={[1.0, 0, 0.8]} s={[6.8, 3.6]} a="#0b3540" b="#ff8a1c" />
    {/* the arrow: hangs, cables snap on "lost", spears the floor on "$1.7" */}
    {t < A0 ? [-0.5, 0.5].map((dx) => <Cyl key={dx} p={[AX + dx, (arrowY(t) + 1.7 + 14) / 2, AZ]} rt={0.03} h={14 - arrowY(t) - 1.7} color="#c9d3e0" line={1} />) : [-0.5, 0.5].map((dx) => { const rec = seg(t, A0, A0 + 0.35, Easing.out(Easing.back(2))); const top = 14, bot = lerp(arrowY(A0) + 1.7, 11.5, rec); return <Cyl key={dx} p={[AX + dx + Math.sin((t - A0) * 18 + dx) * 0.1 * (1 - rec), (top + bot) / 2, AZ]} rt={0.03} h={top - bot} color="#c9d3e0" line={1} />; })}
    <Arrow3D p={[AX, arrowY(t), AZ]} rot={[0, 0.35, arrowR(t)]} L={3.4} color={t < AL ? "#2fd46a" : "#25b85a"} />
    {t >= AL ? <CanvasPlane p={[AX, 0.03, AZ]} rot={[-Math.PI / 2, 0, 0]} s={[3.2 * seg(t, AL, AL + 0.08), 3.2 * seg(t, AL, AL + 0.08) + 0.001]} px={[256, 256]} draw={(c, W, H) => { c.clearRect(0, 0, W, H); c.strokeStyle = INK; c.lineWidth = 7; for (let i = 0; i < 7; i++) { const a = i * 0.9 + 0.3; c.beginPath(); c.moveTo(W / 2, H / 2); let x = W / 2, y = H / 2; for (let k = 1; k < 4; k++) { x += Math.cos(a + Math.sin(k * 3 + i) * 0.5) * 34; y += Math.sin(a + Math.sin(k * 3 + i) * 0.5) * 34; c.lineTo(x, y); } c.stroke(); } }} /> : null}
    {t >= AL ? debris.map((d, i) => <Box key={i} p={d} s={[0.22, 0.14, 0.2]} rot={[t * 7 + i, t * 5, i]} color="#12505c" line={2} />) : null}
    <Glow p={[AX, 0.8, AZ + 0.4]} r={2.6} color="rgba(255,255,220,1)" o={t > AL ? 0.9 * Math.exp(-(t - AL) * 6) : 0} />
    <Shaft p={[-1.2, 4.2, -2]} s={[2.6, 9]} rot={[0, 0, 0.42]} color="140,240,255" o={0.16} /><Dust t={t} area={[6, 6, 4]} color="rgba(190,245,255,.9)" />
    {/* the analyst */}
    <Person p={P} sy={0} h={h} look={analyst} f={f} pose={{ mood: shock ? (t < 2.4 ? "shock" : "worry") : t < A0 ? (sipK(t) > 0.5 ? "smile" : "deadpan") : "worry", nerv, sweat: t > A0 ? 1 : 0, squash: a.sq, air: a.y > 0 ? 1 : 0,
      arms: shock && t > MR ? (t > 1.75 ? "head" : "up") : undefined, armK: 1, armR: t < MR ? mugHand(t) : undefined, armL: t < MR && t > 0.9 ? [-0.2, 0.62] : undefined, armLK: seg(t, 0.9, 1.05),
      lookX: t < A0 ? 0 : t < 2.6 ? -1 : Math.sin(f * 0.11), tilt: t > J0 && t < J0 + JD ? 0.1 : 0 }} />
    {t < MR ? <FaceGroup p={P}><Mug p={hand(h, mugHand(t), a.sq, false, 0.12).map((v, i) => i === 1 ? v + 0.12 : v) as V3} s={1.1} /></FaceGroup> : <Mug p={mugW} rot={[0, 0, dt < tLand ? -dt * 9 : Math.PI / 2]} s={1.1} />}
    {puddle > 0 ? <CanvasPlane p={[mugW[0] - 0.3, 0.025, mugW[2] + 0.1]} rot={[-Math.PI / 2, 0, 0]} s={[1.5 * puddle + 0.01, 1.0 * puddle + 0.01]} px={[128, 96]} draw={(c, W, H) => { c.clearRect(0, 0, W, H); c.fillStyle = "#5a3214"; c.strokeStyle = INK; c.lineWidth = 4; c.beginPath(); c.ellipse(W / 2, H / 2, W * 0.45, H * 0.4, 0, 0, 7); c.fill(); c.stroke(); }} /> : null}
    {void cam}
  </>);
};

/* =================== S2 4.75 – 8.99  "Then CEO Jensen Huang resigned, days before earnings." =================== */
const ST = 1.0, LX = 0.9, LZ = 0.25, CZ = -0.7, CH = 3.7;
const K2: Key[] = [
  { t: 4.5, pos: [-2.8, 3.1, 11.8], look: [0.6, 3.6, -1.0], fov: 58 },
  { t: 6.0, pos: [-1.2, 3.6, 8.0], look: [0.8, 3.7, -0.8], fov: 52 },
  { t: 7.05, pos: [0.3, 3.8, 6.2], look: [0.9, 3.5, -0.6], fov: 48 },
  { t: 7.8, pos: [1.7, 3.6, 6.8], look: [2.3, 3.3, -0.8], fov: 52 },
  { t: 9.3, pos: [5.0, 3.4, 8.0], look: [5.8, 3.2, -1.4], fov: 56 },
];
const W0 = 7.75, W1 = 9.0;
const ceoX = (t: number) => lerp(LX, 8.0, seg(t, W0, W1, Easing.inOut(Easing.sin)));
const S2 = ({ t, f }: Ctx) => {
  const x = ceoX(t), P: V3 = [x, ST, CZ], moving = t > W0 && t < W1, dist = x - LX;
  const cam = camAt(t, K2).pos;
  // crown: on head -> lifted (6.77-7.2) -> carried to lectern (7.2-7.5) -> resting
  const grab = seg(t, 6.77, 7.0), lift = seg(t, 7.0, 7.2, Easing.inOut(Easing.sin)), carry = seg(t, 7.2, 7.5, Easing.inOut(Easing.sin)), placed = t >= 7.5;
  const headLoc = hand(CH, [0, 0.79 + 0.07 * lift], 0, false, 0.05);
  const headW = toWorld(P, headLoc, cam), lect: V3 = [LX, ST + 1.6 + 0.12, LZ + 0.05];
  const crownW: V3 = placed ? [lect[0], lect[1] + 0.05 * Math.exp(-(t - 7.5) * 10) * Math.abs(Math.sin((t - 7.5) * 30)), lect[2]] : carry > 0 ? [lerp(headW[0], lect[0], carry), lerp(headW[1], lect[1], carry) + Math.sin(carry * Math.PI) * 0.25, lerp(headW[2], lect[2], carry)] : headW;
  const handsY = carry > 0 ? lerp(0.82, 0.47, carry) : lerp(0.79, 0.84, lift);
  const holding = t > 6.77 && t < 7.55, release = seg(t, 7.5, 7.7);
  const wave = t > 5.35 && t < 6.35, waveK = seg(t, 5.35, 5.55) * (1 - seg(t, 6.15, 6.35));
  const slide = t < 6.77 ? 0 : t < 8.31 ? 1 : 2, stamp = seg(t, 6.77, 7.0, Easing.out(Easing.back(3))), circ = seg(t, 8.45, 8.95);
  return (<>
    <Cam t={t} keys={K2} />
    <Lights warm="#ffd2f0" />
    <Floor kind="carpet" a="#3a0f2e" b="#330d29" unit={1.6} w={34} d={34} />
    {/* stage */}
    <Box p={[0, ST / 2, -1.5]} s={[18, ST, 8]} color="#2a1846" />
    <Surface p={[0, ST + 0.01, -1.5]} s={[18, 8]} rot={[-Math.PI / 2, 0, 0]} kind="plank" a="#6b3a1f" b="#5e321a" unit={1.6} />
    <Box p={[0, ST - 0.06, 2.52]} s={[18, 0.12, 0.08]} color="#ffc23a" line={2} />
    {/* LED screen with slides */}
    <Box p={[1.0, 5.6, -5.25]} s={[12.4, 6.0, 0.3]} color="#120a22" />
    <CanvasPlane p={[1.0, 5.6, -5.05]} s={[12, 5.6]} px={[960, 448]} draw={(c, W, H) => {
      if (slide === 0) { const g = c.createLinearGradient(0, 0, W, H); g.addColorStop(0, "#4a1a8a"); g.addColorStop(1, "#c2185b"); c.fillStyle = g; c.fillRect(0, 0, W, H); c.fillStyle = "#2fd46a"; c.strokeStyle = INK; c.lineWidth = 10; c.fillRect(W / 2 - 70, 70, 140, 140); c.strokeRect(W / 2 - 70, 70, 140, 140); c.fillStyle = "#0e2a1a"; c.fillRect(W / 2 - 40, 100, 80, 80); c.fillStyle = "#fff"; c.font = "900 92px Inter, Arial"; c.textAlign = "center"; c.textBaseline = "middle"; c.fillText("AI KEYNOTE", W / 2, 300); c.font = "800 50px Inter, Arial"; c.fillStyle = "#ffd6f0"; c.fillText("with THE CEO", W / 2, 380); }
      else if (slide === 1) { c.fillStyle = "#1a0614"; c.fillRect(0, 0, W, H); c.save(); c.translate(W / 2, H / 2); c.rotate(-0.12); const s = 0.4 + 0.6 * stamp; c.scale(s, s); c.strokeStyle = "#ff2b3b"; c.lineWidth = 18; c.strokeRect(-380, -100, 760, 200); c.fillStyle = "#ff2b3b"; c.font = "900 150px Inter, Arial"; c.textAlign = "center"; c.textBaseline = "middle"; c.fillText("RESIGNED", 0, 8); c.restore(); }
      else { c.fillStyle = "#fffaf0"; c.fillRect(0, 0, W, H); c.fillStyle = "#e23b3b"; c.fillRect(0, 0, W, 110); c.fillStyle = "#fff"; c.font = "900 80px Inter, Arial"; c.textAlign = "center"; c.textBaseline = "middle"; c.fillText("EARNINGS", W / 2, 58); c.fillStyle = INK; c.font = "900 200px Inter, Arial"; c.fillText("NOV 17", W / 2, 280); c.strokeStyle = "#e23b3b"; c.lineWidth = 14; c.beginPath(); c.ellipse(W / 2, 280, 380, 120, -0.05, 0, Math.PI * 2 * circ); c.stroke(); }
      if (t > 6.7 && t < 6.8 || t > 8.25 && t < 8.35) { c.fillStyle = "rgba(255,255,255,.5)"; for (let y = 0; y < H; y += 24) c.fillRect(0, y + (f * 7) % 24, W, 6); }
    }} />
    <Glow p={[1.0, 5.6, -4.6]} r={6} color={slide === 1 ? "rgba(255,40,70,0.9)" : "rgba(200,80,255,0.7)"} o={0.25} />
    {/* curtains, wings (exit on the right goes BEHIND the leg curtain) */}
    <Curtain p={[-7.4, 4.6, 0.6]} s={[2.8, 9.2]} /><Curtain p={[7.3, 4.6, 0.6]} s={[2.6, 9.2]} /><Curtain p={[0, 8.6, 0.65]} s={[18, 1.8]} folds={16} />
    <Curtain p={[-6.6, 4.6, -5.2]} s={[2.4, 9.2]} color="#7a0c22" /><Curtain p={[8.2, 4.6, -5.2]} s={[2.4, 9.2]} color="#7a0c22" />
    {/* lighting truss */}
    <Box p={[0, 9.4, -1.0]} s={[16, 0.25, 0.25]} color="#3a3a4a" line={2} />
    {[-5, -2.5, 2.5, 5].map((x) => <React.Fragment key={x}><Cyl p={[x, 9.0, -1.0]} rt={0.22} rb={0.3} h={0.6} color="#1b1b2a" line={2} /><Glow p={[x, 8.7, -0.8]} r={0.8} color="rgba(255,200,255,1)" o={0.6} /></React.Fragment>)}
    <SpotCone p={[LX, 9.0, CZ + 0.4]} h={9.0 - ST} r={1.7} color="#fff1c8" o={0.12} />
    <Glow p={[LX, ST + 0.05, CZ + 0.4]} r={1.8} color="rgba(255,240,200,1)" o={0.35} />
    {/* stage dressing */}
    <Lectern p={[LX, ST, LZ]} />
    {[-4.2, 4.6].map((xx) => <Box key={xx} p={[xx, ST + 0.35, 1.7]} s={[1.4, 0.7, 0.8]} color="#1b1b2a" rot={[-0.5, 0, 0]} />)}
    <Plant p={[-5.4, ST, -3.8]} s={1.3} pot="#ffc23a" /><Plant p={[6.6, ST, -3.8]} s={1.3} pot="#ffc23a" />
    {[-8.8, 9.6].map((xx) => <React.Fragment key={xx}><Box p={[xx, 1.4, 1.2]} s={[1.6, 2.8, 1.4]} color="#1b1b2a" /><Ball p={[xx, 1.9, 1.95]} r={0.45} color="#3a3a4a" /><Ball p={[xx, 0.8, 1.95]} r={0.3} color="#3a3a4a" /></React.Fragment>)}
    {/* audience: seat rows + heads from behind (foreground layer) */}
    {[4.6, 6.2, 7.8].map((z, r) => Array.from({ length: 9 }, (_, i) => { const xx = -8 + i * 2 + (r % 2) * 0.6; const head = (i * 5 + r * 3) % 4 !== 0; return <React.Fragment key={r + "-" + i}><Box p={[xx, 0.9, z]} s={[1.6, 1.8, 0.3]} color="#7a0c22" line={3} />{head ? <Ball p={[xx, 2.1 + Math.sin(f * 0.07 + i + r) * 0.02, z - 0.3]} r={0.44} color={["#1b1b2a", "#2a1a12", "#3a2a4a", "#20203a"][(i + r) % 4]} /> : null}</React.Fragment>; }))}
    <group position={[-6.0, 0, 9.2]}><Cyl p={[0, 1.0, 0]} rt={0.05} h={2.0} color="#2b3350" line={2} /><PressCam p={[0, 2.2, 0]} s={1.6} /></group>
    <Dust t={t} area={[3, 7, 2]} color="rgba(255,235,200,.9)" />
    {/* the CEO */}
    <Person p={P} sy={ST} h={CH} look={ceo} f={f} pose={{ mood: t < 5.35 ? "smile" : t < 6.4 ? "grin" : t < 6.77 ? "deadpan" : "worry", nerv: t > 7.6 ? 0.25 : 0, sweat: 0, hunch: t > 7.5 ? 0.8 * seg(t, 7.5, 7.8) : 0,
      walk: moving ? dist * WALK : undefined, speed: moving ? 0.8 : 0,
      armR: holding ? [0.12, handsY] : wave ? [0.25 + Math.sin(f * 0.6) * 0.03, 0.72] : undefined, armRK: holding ? grab * (1 - release) : wave ? waveK : 1,
      armL: holding ? [-0.12, handsY] : undefined, armLK: grab * (1 - release), lookX: t > 7.6 ? 0.6 : 0 }} />
    <Crown p={crownW} s={0.62} rot={[0, 0.3, placed ? 0 : carry * 0.2]} />
    {placed ? <Glow p={[lect[0], lect[1] + 0.3, lect[2] + 0.2]} r={0.9} color="rgba(255,230,120,1)" o={0.5 + 0.15 * Math.sin(f * 0.3)} /> : null}
    {void holding}
  </>);
};

/* =================== S3 8.99 – 13.35  "Six straight weekly drops, the longest streak since 2012." =================== */
const YAW = 0.55, DIR: V3 = [Math.cos(YAW), 0, -Math.sin(YAW)], S0: V3 = [-2.6, 0, 1.0], SP = 1.6, DH = 4.0, DW = 1.9, DT = 0.5;
const bigStart = (i: number) => 9.1 + i * 0.32;
const bigAng = (i: number, t: number) => { const end = i < 5 ? 1.257 : Math.PI / 2, d = i < 5 ? 0.68 : 0.76; return end * clamp((t - bigStart(i)) / d) ** 2; };
const smallP = (s: number): V3 => [8.4 + 8 * Math.sin(s / 8), 0, -5.74 - 0.8 * s];
const smallYaw = (s: number) => Math.atan2(0.8, Math.cos(s / 8));
const NS = 30, SS = 0.75, SMALL0 = 11.46;
const smallAng = (k: number, t: number) => { const end = k < NS - 1 ? 1.257 : Math.PI / 2; return end * clamp((t - (SMALL0 + k * 0.029)) / 0.3) ** 2; };
const SIGN_S = (NS - 1) * SS + 1.4, SIGN_T = 12.36;
const K3: Key[] = [
  { t: 8.79, pos: [-6.6, 1.8, 6.6], look: [-1.6, 1.9, -0.6], fov: 60 },
  { t: 9.7, pos: [-5.0, 2.1, 6.8], look: [0.4, 1.9, -1.8], fov: 60 },
  { t: 10.9, pos: [-1.4, 3.4, 8.2], look: [4.0, 1.6, -3.6], fov: 60 },
  { t: 12.0, pos: [2.6, 9.5, 4.0], look: [9.0, 0.8, -14.0], fov: 60 },
  { t: 13.6, pos: [6.6, 7.0, -7.5], look: [11.8, 2.0, -24.0], fov: 56 },
];
const S3 = ({ t, f }: Ctx) => {
  const HP: V3 = [S0[0] - DIR[0] * 0.6 - Math.sin(YAW) * 0.55, 0, S0[2] - DIR[2] * 0.6 - Math.cos(YAW) * 0.55];
  const reach = seg(t, 8.82, 9.04, Easing.inOut(Easing.sin)), push = seg(t, 9.04, 9.14), back = seg(t, 9.2, 9.45);
  const hop = t > 9.22 && t < 9.5 ? Math.sin(clamp((t - 9.22) / 0.28) * Math.PI) * 0.35 : 0;
  const sq = t > 9.12 && t < 9.22 ? -0.12 : t > 9.5 && t < 9.65 ? -0.18 * (1 - (t - 9.5) / 0.15) : hop > 0 ? 0.1 : 0;
  const hx = HP[0] - 0.5 * Easing.out(Easing.quad)(clamp((t - 9.22) / 0.28)), hz = HP[2] + 0.3 * Easing.out(Easing.quad)(clamp((t - 9.22) / 0.28));
  const signUp = t < SIGN_T ? 0 : Easing.out(Easing.back(2.2))(clamp((t - SIGN_T) / 0.3));
  const sp = smallP(SIGN_S), sy = smallYaw(SIGN_S);
  const lastLand = bigStart(5) + 0.76;
  return (<>
    <Cam t={t} keys={K3} impacts={[[lastLand, 0.03]]} />
    <Lights warm="#fff0c8" />
    <Surface p={[8, 0, -14]} s={[44, 60]} rot={[-Math.PI / 2, 0, 0]} kind="carpet" a="#13804a" b="#117644" unit={3.2} />
    {/* printed felt markings */}
    <CanvasPlane p={[-4.6, 0.02, 4.2]} rot={[-Math.PI / 2, 0, 0.2]} s={[6, 3]} px={[600, 300]} draw={(c, W, H) => { c.clearRect(0, 0, W, H); c.strokeStyle = "#ffd36a"; c.lineWidth = 8; c.beginPath(); c.ellipse(W / 2, H * 1.3, W * 0.48, H * 1.05, 0, Math.PI * 1.08, Math.PI * 1.92); c.stroke(); c.fillStyle = "#ffd36a"; c.font = "900 60px Inter, Arial"; c.textAlign = "center"; c.fillText("PLACE BETS", W / 2, H * 0.62); }} />
    {/* padded rim of the table */}
    <Box p={[-14, 0.7, -14]} s={[1.6, 1.4, 60]} color="#5a2a14" /><Box p={[30, 0.7, -14]} s={[1.6, 1.4, 60]} color="#5a2a14" /><Box p={[8, 0.7, -44]} s={[44, 1.4, 1.6]} color="#5a2a14" />
    {/* casino glows beyond the table */}
    {Array.from({ length: 10 }, (_, i) => <Glow key={i} p={[-16 + i * 5, 3 + (i % 3), -48]} r={2.4} color={["rgba(255,80,160,1)", "rgba(255,210,80,1)", "rgba(80,200,255,1)"][i % 3]} o={0.45 + 0.2 * Math.sin(f * 0.2 + i)} />)}
    {/* hanging lamps */}
    <HangLamp p={[-3, 9.5, -1]} /><HangLamp p={[6, 9.5, -8]} /><HangLamp p={[12, 9.5, -20]} />
    <Shaft p={[-3, 5.2, -1]} s={[3.2, 8.6]} color="255,236,170" o={0.2} />
    {/* big dominoes W1..W6 */}
    {Array.from({ length: 6 }, (_, i) => <Domino key={i} p={[S0[0] + DIR[0] * SP * i, 0, S0[2] + DIR[2] * SP * i]} yaw={YAW} h={DH} w={DW} th={DT} ang={bigAng(i, t)} label={`W${i + 1}`} pips={i + 1} />)}
    {/* the chain keeps going: small dominoes winding to the sign */}
    {Array.from({ length: NS }, (_, k) => <Domino key={"s" + k} p={smallP(k * SS)} yaw={smallYaw(k * SS)} h={1.6} w={0.8} th={0.22} ang={smallAng(k, t)} small />)}
    {/* SINCE 2012 sign: hinged, flips up when the last domino hits it */}
    <group position={sp} rotation={[0, -0.25, 0]}>
      <Box p={[-2.6, 0.5, 0]} s={[0.2, 1.0, 0.2]} color="#2b3350" line={2} /><Box p={[2.6, 0.5, 0]} s={[0.2, 1.0, 0.2]} color="#2b3350" line={2} />
      <group position={[0, 0.3, 0]} rotation={[-(1 - signUp) * Math.PI / 2, 0, 0]}>
        <Box p={[0, 1.45, -0.06]} s={[6.4, 2.5, 0.12]} color="#2b3350" line={3} />
        <CanvasPlane p={[0, 1.45, 0.01]} s={[6.2, 2.3]} px={[620, 230]} draw={(c, W, H) => { c.fillStyle = "#ffd23a"; c.fillRect(0, 0, W, H); c.strokeStyle = INK; c.lineWidth = 12; c.strokeRect(6, 6, W - 12, H - 12); c.fillStyle = "#111"; c.font = "900 120px Inter, Arial"; c.textAlign = "center"; c.textBaseline = "middle"; c.fillText("SINCE 2012", W / 2, H * 0.42); c.fillStyle = "#e5233a"; c.font = "900 54px Inter, Arial"; c.fillText("▼ LONGEST STREAK ▼", W / 2, H * 0.82); }} />
      </group>
    </group>
    <Glow p={[sp[0], 2.0, sp[2] + 1]} r={4} color="rgba(255,220,90,1)" o={0.5 * signUp} />
    {/* casino dressing */}
    <ChipStack p={[-7.4, 0, 2.4]} n={9} color="#e5233a" /><ChipStack p={[-8.4, 0, 0.6]} n={6} color="#2f6bff" /><ChipStack p={[-7.6, 0, 1.6]} n={12} color="#111" /><ChipStack p={[1.4, 0, 3.6]} n={7} color="#7c4dff" />
    <ChipStack p={[-1.2, 0, -5.6]} n={10} color="#e5233a" r={0.7} /><ChipStack p={[0.4, 0, -6.6]} n={5} color="#2fd46a" r={0.7} />
    <Card p={[-7.2, 0, 0.6]} rotY={0.4} label="A" /><Card p={[-0.6, 0, 3.0]} rotY={-0.25} label="K" red /><Card p={[2.6, 0, -9]} rotY={0.6} label="Q" red s={1.4} />
    <Dice p={[3.2, 0.6, 1.4]} rot={[0, 0.5, 0]} s={1.2} /><Dice p={[-8.6, 0.5, -2.4]} rot={[0, 1.1, 0]} />
    <group position={[-7, 0, -12]} rotation={[0, f * 0.02, 0]}><Cyl p={[0, 0.35, 0]} rt={3.2} h={0.7} color="#5a2a14" /><Cyl p={[0, 0.75, 0]} rt={2.6} h={0.12} color="#e5233a" line={2} />{Array.from({ length: 8 }, (_, i) => <Box key={i} p={[Math.sin(i * 0.785) * 1.5, 0.85, Math.cos(i * 0.785) * 1.5]} s={[0.3, 0.1, 1.8]} rot={[0, i * 0.785, 0]} color={i % 2 ? "#111" : "#e5233a"} line={1} />)}<Cyl p={[0, 1.1, 0]} rt={0.3} h={0.6} color="#ffc23a" /></group>
    <Dust t={t} area={[7, 7, 4]} color="rgba(255,240,190,.9)" />
    {/* the analyst (tiny vs. the giant dominoes) */}
    <Person p={[hx, hop, hz]} sy={0} h={2.6} look={analyst} f={f} pose={{ mood: t < 9.25 ? "deadpan" : t < 10.2 ? "shock" : "worry", nerv: t > 9.3 ? 0.4 : 0, sweat: t > 9.3 ? 1 : 0, squash: sq, air: hop > 0 ? 1 : 0, tilt: t < 9.14 ? 0.08 * reach : 0,
      armR: t < 9.2 ? [lerp(0.2, 0.31, reach) + 0.02 * push, lerp(0.3, 0.5, reach)] : undefined, armRK: 1 - back, arms: t > 9.25 ? "head" : "down", armK: seg(t, 9.25, 9.45), lookX: t > 9.3 ? 1 : 0.3 }} />
  </>);
};

/* =================== S4 13.35 – 17.75  "Interim chief Colette Kress now faces Wall Street on November 17." =================== */
const K4: Key[] = [
  { t: 13.15, pos: [-3.4, 2.6, 12.5], look: [-1.8, 3.4, -6], fov: 60 },
  { t: 14.4, pos: [-1.2, 2.4, 11.2], look: [-1.0, 3.2, -6], fov: 58 },
  { t: 15.33, pos: [-1.8, 2.6, 11.0], look: [2.4, 2.9, -1.5], fov: 55 },
  { t: 16.4, pos: [-1.4, 2.7, 10.4], look: [3.8, 2.9, 0.0], fov: 54 },
  { t: 17.95, pos: [-0.6, 2.9, 9.4], look: [3.0, 3.6, -8], fov: 56 },
];
const KW0 = 13.48, KW1 = 15.33;
const S4 = ({ t, f }: Ctx) => {
  const wk = seg(t, KW0, KW1, Easing.inOut(Easing.sin)), kx = lerp(-6.2, 1.4, wk), moving = t > KW0 && t < KW1;
  const unroll = seg(t, 16.54, 16.85, Easing.out(Easing.quad)), flashOn = t > 15.77;
  const reps: [number, number][] = [[5.4, 0.4], [6.6, 1.6], [5.6, 2.9], [7.2, -0.4], [6.8, 3.9], [7.8, 2.2]];
  const raise = seg(t, 15.33, 15.7, Easing.out(Easing.back(1.6)));
  const cam = camAt(t, K4).pos; void cam;
  return (<>
    <Cam t={t} keys={K4} fovKick={[15.77]} />
    <Lights warm="#ffd2a0" />
    <Stars p={[0, 22, -70]} s={[150, 60]} t={t} top="#5a3a9a" bottom="#ff9a4a" n={0} />
    <Glow p={[0, 8, -60]} r={14} color="rgba(255,200,90,1)" o={0.9} /><Ball p={[0, 7, -66]} r={4} color="#ffd36a" ink={0} />
    {/* street */}
    <Surface p={[0, 0, -20]} s={[8, 70]} rot={[-Math.PI / 2, 0, 0]} kind="plain" a="#3a3550" b="#3a3550" />
    {Array.from({ length: 14 }, (_, i) => <Box key={i} p={[0, 0.02, 6 - i * 4.6]} s={[0.22, 0.02, 2.0]} color="#ffd23a" line={1} />)}
    {Array.from({ length: 7 }, (_, i) => <Box key={"z" + i} p={[-3.3 + i * 1.1, 0.025, 2.0]} s={[0.6, 0.02, 2.6]} color="#f2efe6" line={1} />)}
    {[-1, 1].map((s) => <React.Fragment key={s}><Surface p={[s * 6, 0.18, -20]} s={[4, 70]} rot={[-Math.PI / 2, 0, 0]} kind="tile" a="#d8c2a8" b="#cdb59a" unit={1.4} /><Box p={[s * 4.05, 0.09, -20]} s={[0.12, 0.18, 70]} color="#a99a8a" line={2} /></React.Fragment>)}
    {/* buildings (sunlit fronts face the street) */}
    {[[-1, 4, 16, "#d9935a"], [-1, -4, 22, "#b46a4a"], [-1, -12, 18, "#e0a86a"], [-1, -20, 26, "#9a5a52"], [-1, -28, 20, "#d4885a"], [1, 4, 18, "#c27a5a"], [1, -4, 14, "#e4b07a"], [1, -12, 24, "#a0605a"], [1, -20, 18, "#d99a62"], [1, -28, 28, "#b8704e"]].map(([s, z, hh, col], i) =>
      <Building key={i} p={[(s as number) * 11.5, 0, z as number]} s={[7, hh as number, 7.6]} color={col as string} face={(s as number) < 0 ? "+x" : "-x"} seed={i + 2} lit={0.25} />)}
    {/* the exchange at the end of the street */}
    <group position={[0, 0, -36]}>
      <Box p={[0, 7, -2]} s={[16, 14, 4]} color="#e8dcc4" />
      {[0, 1, 2].map((i) => <Box key={i} p={[0, 0.3 + i * 0.3, 1.2 - i * 0.5]} s={[14 - i, 0.3, 1.2]} color="#d8ccb4" line={2} />)}
      {[-5, -3, -1, 1, 3, 5].map((x) => <Cyl key={x} p={[x, 5.2, 0.4]} rt={0.5} h={8.6} color="#f2ead8" />)}
      <Box p={[0, 9.9, 0.4]} s={[13, 0.8, 1.4]} color="#e8dcc4" />
      <CanvasPlane p={[0, 11.4, 0.42]} s={[13, 2.2]} px={[650, 110]} draw={(c, W, H) => { c.clearRect(0, 0, W, H); c.fillStyle = "#e8dcc4"; c.strokeStyle = INK; c.lineWidth = 6; c.beginPath(); c.moveTo(4, H - 4); c.lineTo(W / 2, 6); c.lineTo(W - 4, H - 4); c.closePath(); c.fill(); c.stroke(); }} />
      {[-6.4, 6.4].map((x) => <React.Fragment key={x}><Cyl p={[x, 12.2, 0.4]} rt={0.05} h={3} color="#2b3350" line={1} /><CanvasPlane p={[x + 0.6, 13.1, 0.4]} s={[1.2, 0.8]} px={[120, 80]} draw={(c, W, H) => { c.fillStyle = "#2f6bff"; c.fillRect(0, 0, W, H); c.fillStyle = "#fff"; c.fillRect(0, H / 3, W, H / 6); c.fillStyle = "#e5233a"; c.fillRect(0, H * 2 / 3, W, H / 3); }} /></React.Fragment>)}
      {/* banner unrolls from the roller */}
      <Cyl p={[0, 9.2, 1.3]} rt={0.18} h={6.4} color="#ffc23a" rot={[0, 0, Math.PI / 2]} />
      <CanvasPlane p={[0, 9.2 - 3.0 * unroll, 1.25]} s={[6, 6 * unroll + 0.001]} px={[600, 600]} draw={(c, W, H) => { c.fillStyle = "#fffaf0"; c.fillRect(0, 0, W, H); c.fillStyle = "#e23b3b"; c.fillRect(0, 0, W, 150); c.fillStyle = "#fff"; c.font = "900 120px Inter, Arial"; c.textAlign = "center"; c.textBaseline = "middle"; c.fillText("NOV", W / 2, 80); c.fillStyle = INK; c.font = "900 330px Inter, Arial"; c.fillText("17", W / 2, 380); c.strokeStyle = INK; c.lineWidth = 14; c.strokeRect(7, 7, W - 14, H - 14); }} />
      <Cyl p={[0, 9.2 - 6.0 * unroll, 1.3]} rt={0.12} h={6.2} color="#ffc23a" rot={[0, 0, Math.PI / 2]} />
    </group>
    {/* street furniture */}
    <StreetSign p={[-4.6, 0.18, 4.4]} a="WALL ST" b="BROAD ST" />
    {[-1, 1].map((s) => [6, -6, -18].map((z) => <StreetLamp key={s + "," + z} p={[s * 4.5, 0.18, z]} flip={s > 0} on={0.8} />))}
    <Taxi p={[-2.0, 0, -6.5]} /><Taxi p={[2.0, 0, -15]} rotY={Math.PI} color="#ffd23a" />
    <Hydrant p={[-4.8, 0.18, -1.6]} /><Bench p={[-6.6, 0.18, -4.5]} rotY={Math.PI / 2} /><Bin p={[-5.0, 0.18, -8.0]} />
    <Box p={[-6.8, 1.1, -12]} s={[0.9, 2.2, 0.9]} color="#2f6bff" />
    {[-1, 1].map((s) => [-2, -10].map((z) => <React.Fragment key={s + "t" + z}><Box p={[s * 6.6, 0.25, z]} s={[1.2, 0.14, 1.2]} color="#5a3420" line={2} /><Cyl p={[s * 6.6, 1.2, z]} rt={0.08} h={2} color="#5a3420" line={2} /><Ball p={[s * 6.6, 2.8, z]} r={0.9} color="#3fae5a" /></React.Fragment>))}
    <group position={[-4.3, 0.18, -2.4]}><Cyl p={[0, 2.2, 0]} rt={0.1} h={4.4} color="#2b3350" line={2} /><Box p={[0, 4.6, 0]} s={[0.5, 1.3, 0.5]} color="#2b3350" />{[0, 1, 2].map((i) => <Ball key={i} p={[0, 5.0 - i * 0.4, 0.26]} r={0.14} color={i === 0 ? "#ff3b3b" : "#3a3a4a"} ink={0.02} />)}</group>
    <Barrier p={[4.7, 0.18, 1.4]} rotY={Math.PI / 2} w={4.4} />
    <Shaft p={[1.5, 6, -6]} s={[4, 14]} rot={[0, 0, -0.3]} color="255,200,120" o={0.18} /><Dust t={t} area={[6, 6, 5]} color="rgba(255,220,170,.9)" />
    {/* press pack */}
    {reps.map(([x, z], i) => { const P: V3 = [x, 0.18, z], h = 3.2, up = raise * (0.8 + 0.2 * Math.sin(i)); const tgt: [number, number] = [lerp(0.2, 0.08, up), lerp(0.42, 0.6, up)];
      const flash = flashOn && Math.sin(f * 0.9 + i * 2.3) > 0.8;
      return <React.Fragment key={i}><Person p={P} sy={0.18} h={h} look={crowd[(i + 2) % 8]} f={f + i * 5} pose={{ mood: t > 15.5 ? (i % 2 ? "shock" : "grin") : "deadpan", armR: tgt, armL: [-0.12, lerp(0.4, 0.58, up)], lookX: -1, nerv: 0 }} />
        <FaceGroup p={P}><PressCam p={hand(h, tgt, 0, false, 0.25).map((v, j) => j === 1 ? v + 0.05 : v) as V3} s={1.2} />{flash ? <Glow p={hand(h, tgt, 0, false, 0.4)} r={1.2} color="rgba(255,255,255,1)" o={1} /> : null}</FaceGroup></React.Fragment>; })}
    {/* Kress */}
    <Person p={[kx, 0, 2.2]} h={3.6} look={kress} f={f} pose={{ mood: t < 15.33 ? "deadpan" : t < 16.97 ? "worry" : "gulp", nerv: t < 15.4 ? 0 : t < 16.9 ? 0.35 : 0.6, sweat: t < 15.6 ? 0 : 1, walk: moving ? (kx + 6.2) * WALK : undefined, speed: moving ? 0.8 : 0,
      arms: t > 16.97 ? "chest" : "down", armK: seg(t, 16.97, 17.25), lookX: t > 15.33 ? 1 : 0.4, hunch: t > 16.9 ? 0.5 : 0, squash: t > 16.97 && t < 17.3 ? -0.05 * Math.sin(clamp((t - 16.97) / 0.33) * Math.PI) : 0 }} />
  </>);
};

/* =================== S5 17.75 – 22  "The AI throne is shaking, and the whole world is watching." =================== */
const G: V3 = [0, 4.6, -2], GR = 4.4, TB = 8.85;
const K5: Key[] = [
  { t: 17.55, pos: [2.4, 8.8, 5.2], look: [0, 11.0, -2], fov: 56 },
  { t: 19.0, pos: [1.3, 9.4, 4.6], look: [0, 11.2, -2], fov: 54 },
  { t: 19.95, pos: [1.6, 9.2, 7.0], look: [0.4, 9.4, -1], fov: 56 },
  { t: 21.3, pos: [0, 4.4, 20.5], look: [0, 6.0, -2], fov: 60 },
  { t: 22.3, pos: [0, 4.5, 21.2], look: [0, 6.0, -2], fov: 60 },
];
const quakeAmp = (t: number) => clamp((t - 19.0) / 0.25) * (1 - seg(t, 19.9, 20.4, Easing.linear));
const CROWN0 = 19.55;
const crownSim = (t: number) => {
  const p: V3 = [0.1, TB + 1.94, -1.75]; const v: V3 = [0.7, 1.4, 2.6]; let spin = 0;
  if (t <= CROWN0) return { p, spin };
  const n = Math.floor((t - CROWN0) * 240), dt = 1 / 240, rr = GR + 0.32;
  for (let i = 0; i < n; i++) {
    v[1] -= 20 * dt; p[0] += v[0] * dt; p[1] += v[1] * dt; p[2] += v[2] * dt;
    const d: V3 = [p[0] - G[0], p[1] - G[1], p[2] - G[2]], L = Math.hypot(...d);
    if (L < rr && p[1] < TB + 1.2) { const nn: V3 = [d[0] / L, d[1] / L, d[2] / L]; p[0] = G[0] + nn[0] * rr; p[1] = G[1] + nn[1] * rr; p[2] = G[2] + nn[2] * rr; const vn = v[0] * nn[0] + v[1] * nn[1] + v[2] * nn[2]; if (vn < 0) { for (let j = 0; j < 3; j++) v[j] -= 1.45 * vn * nn[j]; } for (let j = 0; j < 3; j++) v[j] *= 0.992; }
    if (p[1] < 0.3) { p[1] = 0.3; if (v[1] < 0) v[1] *= -0.4; v[0] *= 0.9; v[2] *= 0.9; }
    spin += Math.hypot(...v) * dt * 1.6;
  }
  return { p, spin };
};
const S5 = ({ t, f }: Ctx) => {
  const amp = quakeAmp(t), sx = Math.sin(f * 2.3) * 0.08 * amp, sr = Math.sin(f * 1.9) * 0.05 * amp;
  const cr = crownSim(t), onSeat = t <= CROWN0;
  const hop = onSeat && amp > 0 ? Math.abs(Math.sin(f * 1.15)) * 0.08 * amp : 0;
  const ring: { x: number; z: number; side: number }[] = [];
  for (let i = 0; i < 18; i++) { const a = -1.25 + (i / 17) * 2.5, R = 8.4 + (i % 3) * 1.3; ring.push({ x: Math.sin(a) * R, z: G[2] + Math.cos(a) * R, side: Math.sign(Math.sin(a)) || 1 }); }
  return (<>
    <Cam t={t} keys={K5} quake={0.03 * amp} />
    <Lights warm="#ffe2b0" />
    <Stars p={[0, 14, -40]} s={[110, 50]} t={t} />
    <Floor kind="marble" a="#2a1a5e" b="#22154e" unit={2.6} w={60} d={60} />
    {/* distant skyline ring: every window lit (the world is up, watching) */}
    {Array.from({ length: 9 }, (_, i) => <Building key={i} p={[-24 + i * 6, 0, -26 - (i % 2) * 3]} s={[5, 10 + ((i * 7) % 9), 4]} color="#1f1550" face="+z" seed={i + 11} lit={0.7} trim="#120a30" />)}
    {/* the globe and the throne on top */}
    <Globe p={G} r={GR} rotY={t * 0.18} />
    <Glow p={[G[0], G[1], G[2] + 2]} r={7.5} color="rgba(80,160,255,1)" o={0.22} />
    <Cyl p={[0, TB - 0.1, -2]} rt={1.5} rb={1.9} h={0.8} color="#ffc23a" />
    <group position={[sx, 0, 0]} rotation={[0, 0, sr]}>
      <group position={[0, 0, 0]}><Throne p={[0, TB + 0.3, -2]} /></group>
      {onSeat ? <Crown p={[cr.p[0], cr.p[1] + hop, cr.p[2]]} s={0.9} rot={[0, f * 0.01, Math.sin(f * 1.3) * 0.15 * amp]} /> : null}
    </group>
    {!onSeat ? <Crown p={cr.p} s={0.9} rot={[cr.spin, cr.spin * 0.6, 0.3]} /> : null}
    <Glow p={[0, TB + 3.4, -1.4]} r={3} color="rgba(255,220,120,1)" o={0.4 + 0.1 * Math.sin(f * 0.3)} />
    {/* giant screens on pylons broadcasting the throne */}
    {[-1, 1].map((s) => <group key={s} position={[s * 11, 0, -6]} rotation={[0, -s * 0.5, 0]}>
      <Cyl p={[0, 3.5, 0]} rt={0.25} h={7} color="#2b3350" line={2} />
      <CanvasPlane p={[0, 8.5, 0]} s={[5, 3]} px={[400, 240]} frame="#120a30" draw={(c, W, H) => { c.fillStyle = "#1a0f40"; c.fillRect(0, 0, W, H); c.fillStyle = "#a0202e"; c.fillRect(W / 2 - 50, 60, 100, 130); c.fillStyle = "#ffc23a"; c.fillRect(W / 2 - 66, 50, 132, 22); c.fillStyle = "#ff2b3b"; c.beginPath(); c.arc(34, 32, 12, 0, 7); c.fill(); c.fillStyle = "#fff"; c.font = "900 30px Inter, Arial"; c.textAlign = "left"; c.fillText("LIVE", 54, 43); c.font = "900 34px Inter, Arial"; c.textAlign = "center"; c.fillText("AI THRONE", W / 2, 224); }} />
    </group>)}
    {[-1, 1].map((s) => <Shaft key={"sh" + s} p={[s * 6, 6, -6]} s={[2.6, 14]} rot={[0, 0, s * 0.45]} color="190,170,255" o={0.2} />)}
    <Dust t={t} n={16} area={[6, 9, 3]} color="rgba(255,225,150,.9)" fall={amp > 0} />
    {/* the watching world (present all along, revealed by the pull-back) */}
    {ring.map((r, i) => { const P: V3 = [r.x, 0, r.z], h = 3.0, phone = i % 3 !== 1, tgt: [number, number] = [0.2, 0.66];
      return <React.Fragment key={i}><Person p={P} h={h} look={crowd[i % 8]} f={f + i * 9} pose={{ mood: i % 4 === 0 ? "shock" : i % 4 === 2 ? "worry" : "deadpan", lookX: -r.side, flip: r.side > 0, nerv: 0.15, sweat: i % 5 === 0 ? 0.6 : 0, armR: phone ? tgt : undefined, arms: phone ? undefined : "head", armK: 1, squash: 0.02 * Math.sin(f * 0.2 + i) }} />
        {phone ? <FaceGroup p={P}><Box p={hand(h, tgt, 0, r.side > 0, 0.12).map((v, j) => j === 1 ? v + 0.12 : v) as V3} s={[0.28, 0.46, 0.05]} color="#1b1b2a" line={2} /><Glow p={hand(h, tgt, 0, r.side > 0, 0.18).map((v, j) => j === 1 ? v + 0.12 : v) as V3} r={0.45} color="rgba(170,220,255,1)" o={0.7} /></FaceGroup> : null}</React.Fragment>; })}
  </>);
};

const CUTS = [0, 4.75, 8.99, 13.35, 17.75, 22.03];
export const NvidiaV4: React.FC = () => {
  const f = useCurrentFrame(), t = f / FPS;
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      <Audio src={staticFile("mix.wav")} />
      <Scene first start={CUTS[0]} end={CUTS[1]} bg="#0b2a33">{(c) => <S1 {...c} />}</Scene>
      <Scene start={CUTS[1]} end={CUTS[2]} bg="#1a0b2e">{(c) => <S2 {...c} />}</Scene>
      <Scene start={CUTS[2]} end={CUTS[3]} bg="#04140e" trans="zoom">{(c) => <S3 {...c} />}</Scene>
      <Scene start={CUTS[3]} end={CUTS[4]} bg="#ff9a4a" trans="whip">{(c) => <S4 {...c} />}</Scene>
      <Scene start={CUTS[4]} end={CUTS[5]} bg="#120a2e" trans="flash">{(c) => <S5 {...c} />}</Scene>
      <Grade t={t} shaft={false} tint={t < 4.75 ? "rgba(0,180,220,.07)" : t < 8.99 ? "rgba(200,40,160,.07)" : t < 13.35 ? "rgba(255,210,90,.05)" : t < 17.75 ? "rgba(255,140,40,.08)" : "rgba(90,40,200,.10)"} />
      <Captions />
    </AbsoluteFill>
  );
};
