import React from "react";
import { AbsoluteFill, Sequence, useCurrentFrame, interpolate, Easing, Audio, staticFile } from "remotion";
import { ThreeCanvas } from "@remotion/three";
import { Box, Cyl, Ball, Surface } from "../style/toon";
import { Look } from "../style/puppet";
import { Rig, CamSet, Person, Lights, Desk, Door, Sign, Clock, Calendar, ChartScreen, Stairs, Chip, Grade, seg, lerp, clamp, V3 } from "../style/kit";
import { Floor, WallDoor, SideWall, Glow, Shaft, Plant, Shelf, Frame, WindowCity, Lamp, Monitor, Chair, Cooler, Cabinet, Rug, Dust } from "../style/props";
import words from "../../public/words.json";

const FPS = 30, LEAD = 6, TAIL = 8;
const analyst: Look = { skin: "#fbe3c8", body: "#3f7bff", outfit: "shirt", hair: "short", hairColor: "#1b1b2a", glasses: true, badge: "#ff3b3b", shoe: "#1b1b2a" };
const ceo: Look = { skin: "#fbe3c8", body: "#14161e", outfit: "leather", hair: "swept", hairColor: "#14141c", shoe: "#0b0d1a" };
const kress: Look = { skin: "#f7d4b5", body: "#1a2f7a", outfit: "blazer", shirt: "#ffffff", hair: "bob", hairColor: "#5a3420", badge: "#ff3b3b", shoe: "#2a1a12" };
const crowdLooks: Look[] = [
  { skin: "#fbe3c8", body: "#e53e3e", outfit: "hoodie", hair: "short", hairColor: "#222" }, { skin: "#f3c9a0", body: "#22a867", outfit: "shirt", hair: "bob", hairColor: "#a0522d" },
  { skin: "#fbe3c8", body: "#f0b429", outfit: "suit", tie: "#1d2f66", hair: "grey" }, { skin: "#f6d6bd", body: "#7c4dff", outfit: "hoodie", hair: "swept", hairColor: "#111", glasses: true },
  { skin: "#fbe3c8", body: "#2d3142", outfit: "suit", tie: "#ff3b3b", hair: "short", hairColor: "#3b2a1a" }, { skin: "#f3c9a0", body: "#ff7a29", outfit: "shirt", hair: "bob", hairColor: "#111" },
];
const WALK = 3.4; // phase per world unit -> feet never slide
type Ctx = { t: number; f: number };

const Scene: React.FC<{ start: number; end: number; first?: boolean; trans?: "ghost" | "zoom" | "flash"; bg: string; children: (c: Ctx) => React.ReactNode }> = ({ start, end, first, trans = "ghost", bg, children }) => {
  const from = Math.round(start * FPS) - (first ? 0 : LEAD), dur = Math.round(end * FPS) - from + TAIL;
  return <Sequence from={from} durationInFrames={dur} layout="none"><Inner from={from} first={first} trans={trans} bg={bg} children={children} /></Sequence>;
};
const Inner: React.FC<{ from: number; first?: boolean; trans: string; bg: string; children: (c: Ctx) => React.ReactNode }> = ({ from, first, trans, bg, children }) => {
  const f = useCurrentFrame(), t = (f + from) / FPS;
  const k = first ? 1 : clamp(f / (LEAD + 2));
  const sc = !first && trans === "zoom" ? lerp(1.35, 1, Easing.out(Easing.cubic)(k)) : 1;
  return (
    <AbsoluteFill style={{ opacity: first ? 1 : trans === "flash" ? 1 : k, transform: `scale(${sc})`, background: bg, filter: "saturate(1.32) contrast(1.07) brightness(1.02)" }}>
      <ThreeCanvas width={720} height={1280} camera={{ fov: 64, position: [0, 2, 8], near: 0.1, far: 120 }} gl={{ antialias: true }}>
        <color attach="background" args={[bg]} />{children({ t, f })}
      </ThreeCanvas>
      {!first && trans === "flash" ? <AbsoluteFill style={{ background: "#fff", opacity: 1 - clamp(f / 7) }} /> : null}
    </AbsoluteFill>
  );
};

/* ===== S1 0-4.75: "lost $1.7 trillion in six weeks" — nervous analyst, jump-back shock ===== */
const S1 = ({ t, f }: Ctx) => {
  const prog = seg(t, 0.3, 3.4, Easing.linear), k = seg(t, 1.16, 2.26, Easing.out(Easing.cubic)), pop = seg(t, 1.16, 1.45, Easing.out(Easing.back(3)));
  const J0 = 1.16, jt = clamp((t - J0) / 0.42);
  const air = t > J0 && t < J0 + 0.42 ? Math.sin(jt * Math.PI) * 0.75 : 0;
  const land = t >= J0 + 0.42 ? Math.max(0, 1 - (t - J0 - 0.42) / 0.2) : 0;
  const sq = t < J0 - 0.15 ? 0 : t < J0 ? -0.16 * seg(t, J0 - 0.15, J0, Easing.linear) : t < J0 + 0.42 ? 0.16 : -0.24 * land;
  const shock = t >= J0, nerv = t < J0 ? 0.3 : t < 2.6 ? 0.8 : 0.3;
  const x = lerp(1.0, 1.5, seg(t, J0, J0 + 0.42)), shake = 0;
  return (<>
    <Rig t={t} t0={0} t1={4.9} from={[2.2, 1.7, 6.0]} to={[1.3, 2.0, 4.8]} lookFrom={[0.8, 2.1, -1]} lookTo={[1.2, 2.2, 0]} roll={[0.05, -0.03]} kicks={[1.16, 3.43]} />
    <Lights warm="#d8e4ff" />
    <Floor kind="carpet" a="#1c3a9a" b="#17318a" unit={1.4} />
    <WallDoor z={-7} W={26} kind="plain" a="#2f58c8" b="#2f58c8" base="#1a2b6e" />
    <SideWall x={-9} kind="plain" a="#2a4fb8" b="#2a4fb8" />
    <WindowCity p={[-4.6, 4.6, -6.85]} s={[3.4, 3.6]} dusk /><WindowCity p={[5.2, 4.6, -6.85]} s={[3.4, 3.6]} dusk />
    <Frame p={[-0.6, 5.6, -6.85]} s={[1.4, 1.0]} art={1} /><Clock p={[0.9, 5.6, -6.8]} r={0.5} t={t} />
    <Shelf p={[-7.6, 0, -6.4]} w={3.2} rows={4} seed={2} wood="#2b3350" /><Cabinet p={[3.6, 0, -6.2]} /><Cooler p={[7.0, 0, -6]} /><Plant p={[-2.2, 0, -5.8]} s={1.2} /><Plant p={[6.6, 0, -4]} s={1.0} />
    {/* big trading wall */}
    <Box p={[0, 4.6, -3.4]} s={[5.8, 3.6, 0.3]} color="#1a2040" />
    <ChartScreen p={[0 + shake, 4.6, -3.2]} s={[5.4, 3.2]} prog={prog} big={t > 1.16 ? `-$${(1.7 * k).toFixed(1)}T` : undefined} bigK={0.55 + 0.45 * pop} />
    {[0, 1, 2, 3, 4, 5].map((i) => <Box key={i} p={[-2.5 + i * 1.0, 2.55, -3.1]} s={[0.8, 0.5, 0.15]} color={t > 3.43 + i * 0.13 ? "#ff3b3b" : "#3a4a80"} line={3} />)}
    <Glow p={[0, 4.6, -2.6]} r={4.2} color="rgba(255,60,60,0.5)" o={t > 1.16 ? 0.35 : 0.1} />
    {/* desks with monitors */}
    <Desk p={[-2.6, 0, -2.0]} w={3.4} top="#e1e8fa" /><Monitor p={[-2.9, 1.1, -2.1]} rot={[0, 0.3, 0]} screen="#ff4040" /><Monitor p={[-1.8, 1.1, -2.1]} rot={[0, 0.2, 0]} />
    <Desk p={[3.4, 0, -2.2]} w={3.4} top="#e1e8fa" /><Monitor p={[3.0, 1.1, -2.3]} rot={[0, -0.3, 0]} screen="#ff4040" /><Chair p={[3.4, 0, -0.6]} rotY={0.5} />
    <Rug p={[1.0, 0, 0.8]} s={[5.2, 3.2]} a="#16296e" b="#e5b43a" />
    <Chip p={[-4.8, 0.9, 1.2]} s={1.0} /><Box p={[-4.8, 0.3, 1.2]} s={[1.5, 0.6, 1.5]} color="#2b3350" />
    <Shaft p={[-1.2, 3.6, -1]} s={[2.4, 8]} rot={[0, 0, 0.4]} color="150,190,255" o={0.18} /><Dust t={t} area={[6, 6, 4]} color="rgba(190,215,255,.9)" />
    <Person p={[x, air, 0.6]} sy={0} h={3.6} look={analyst} f={f} pose={{ mood: shock ? "shock" : "worry", nerv, sweat: 1, squash: sq, arms: shock ? (t > 1.9 ? "head" : "up") : "chest", armK: shock ? 1 : 0.8, lookX: Math.sin(f * 0.11), tilt: t > J0 && t < J0 + 0.5 ? -0.12 : 0, air: air > 0 ? 1 : 0 }} />
  </>);
};

/* ===== S2 4.75-8.99: CEO resigns, packs a box, trudges THROUGH the doorway ===== */
const ceoPos = (t: number) => {
  const A: V3 = [1.6, 0, -1.8], B: V3 = [4.65, 0, -6.3], C: V3 = [4.65, 0, -9.1];
  const k1 = seg(t, 7.3, 8.0, Easing.inOut(Easing.sin)), k2 = seg(t, 8.65, 9.2, Easing.linear);
  const x = lerp(lerp(A[0], B[0], k1), C[0], k2), z = lerp(lerp(A[2], B[2], k1), C[2], k2);
  const dist = Math.hypot(B[0] - A[0], B[2] - A[2]) * k1 + Math.abs(C[2] - B[2]) * k2;
  return { x, z, dist, moving: (t > 7.3 && t < 8.0) || (t > 8.65 && t < 9.2) };
};
const S2 = ({ t, f }: Ctx) => {
  const c = ceoPos(t), hasBox = t > 6.95, mark = seg(t, 8.31, 8.8, Easing.out(Easing.cubic)), open = seg(t, 8.2, 8.75, Easing.inOut(Easing.cubic)), reach = seg(t, 8.0, 8.2) * (1 - seg(t, 8.75, 8.95));
  const dx = c.x - 1.6;
  const camA = { t0: 4.75, t1: 7.3 };
  return (<>
    {t < 7.3 ? <Rig t={t} t0={camA.t0} t1={camA.t1} from={[-2.0, 1.6, 5.6]} to={[1.2, 2.0, 3.6]} lookFrom={[0.8, 2.0, -2.4]} lookTo={[1.5, 2.1, -1.8]} roll={[-0.04, 0.02]} kicks={[5.96, 6.77]} />
      : <Rig t={t} t0={7.3} t1={8.9} from={[1.2, 2.0, 3.6]} to={[3.9, 1.9, -1.8]} lookFrom={[1.5, 2.1, -1.8]} lookTo={[4.6, 2.0, -7.0]} roll={[0.02, -0.03]} ease={Easing.inOut(Easing.sin)} />}
    <Lights warm="#ffd9a0" />
    <Floor kind="plank" a="#8a4a28" b="#7a3f22" unit={2} />
    <WallDoor z={-7} W={26} kind="wood" a="#b2713d" b="#a2662f" door={{ x: 4.6, w: 2.4, h: 4.2 }} unit={1.5} base="#5a2e18" />
    <SideWall x={-8} kind="wood" a="#b2713d" b="#a2662f" />
    {/* hallway behind the door */}
    <Box p={[4.6, 3, -10.4]} s={[10, 8, 0.2]} color="#fff0c8" line={1} /><Glow p={[4.6, 2.4, -8]} r={3} color="rgba(255,245,200,0.9)" o={0.6} />
    <Door p={[4.6, 0, -6.88]} color="#6d4a96" open={open} />
    <WindowCity p={[-2.8, 4.4, -6.9]} s={[3.6, 3.4]} dusk /><Frame p={[1.4, 5.4, -6.9]} s={[1.6, 1.2]} art={2} /><Frame p={[-6, 4.6, -6.9]} s={[1.3, 1.7]} art={0} />
    <Calendar p={[2.7, 4.2, -6.85]} month="NOV" day="17" s={1.9} mark="EARNINGS" markK={mark} />
    <Shelf p={[-6.6, 0, -6.4]} w={3} rows={4} seed={5} wood="#6a3a1f" /><Plant p={[0.2, 0, -6.2]} s={1.3} /><Plant p={[6.6, 0, -5.8]} s={1.1} /><Lamp p={[-4.3, 0, -5.8]} />
    <Rug p={[-1.0, 0, -1.2]} s={[6.4, 4.2]} a="#7d1f2b" b="#e8c06a" />
    <Desk p={[-1.2, 0, -2.4]} w={4.6} top="#d49a52" leg="#7d4524" d={2} />
    <Monitor p={[-2.0, 1.1, -2.6]} rot={[0, 0.25, 0]} screen="#27406f" /><Sign p={[0.4, 1.3, -1.6]} s={[1.0, 0.34]} text="CEO" bg="#f3d27a" size={64} face /><Chip p={[-0.1, 1.2, -2.6]} s={0.6} />
    {!hasBox ? <Box p={[0.9, 1.35, -2.4]} s={[1.0, 0.7, 0.8]} color="#d9a766" rot={[0, 0.2, 0]} /> : null}
    <Chair p={[-1.4, 0, -3.8]} rotY={0.2} color="#7d1f2b" />
    <Shaft p={[-3, 4.5, -2]} s={[2.2, 9]} rot={[0, 0, 0.5]} o={0.22} /><Dust t={t} area={[5, 6, 3]} />
    <Person p={[c.x, 0, c.z]} h={3.7} look={ceo} f={f} pose={{ mood: t < 5.35 ? "deadpan" : t < 6.77 ? "smile" : "worry", nerv: t < 6.77 ? 0 : 0.35, sweat: t > 6.77 ? 0.9 : 0, flip: dx < -0.01, walk: c.moving ? c.dist * WALK : undefined, speed: c.moving ? 0.7 : 0, hunch: t > 6.77 ? 0.9 : 0, arms: reach > 0.01 ? "point" : hasBox ? "box" : t > 5.9 ? "chest" : "down", armK: reach > 0.01 ? reach : seg(t, 6.77, 7.1), tilt: t > 6.77 && t < 7.0 ? 0.06 : 0 }} />
    {hasBox ? <Box p={[c.x - 0.55 * lerp(0, 1, reach > 0.01 || t > 8.9 ? 1 : 0) + 0.0, lerp(1.55, 1.25, reach > 0.01 || t > 8.9 ? 1 : 0) + (c.moving ? Math.abs(Math.sin(c.dist * WALK)) * 0.05 : 0), c.z + 0.35]} s={[1.15, 0.8, 0.8]} color="#d9a766" rot={[0, 0.15, 0]} /> : null}
  </>);
};

/* ===== S3 8.99-13.35: six drops down the steps, tumble, SINCE 2012 ===== */
const N = 6, DX = 1.7, DY = 0.9, X0 = -4.0, SZ = -1.5;
const topY = (i: number) => (N - i) * DY, stepX = (i: number) => X0 + i * DX;
const LAND = [9.2, 9.62, 10.02, 10.42, 10.8];
const stairPos = (t: number) => {
  let i = 0, x = stepX(0), y = topY(0), sq = 0, air = 0, tilt = 0, mode: "stand" | "hop" | "fall" | "down" = "stand";
  for (let h = 0; h < LAND.length; h++) {
    const tk = LAND[h] - 0.3;
    if (t >= tk - 0.12 && t < tk) sq = -0.16 * seg(t, tk - 0.12, tk, Easing.linear);
    if (t >= tk && t < LAND[h]) { const u = (t - tk) / 0.3; x = lerp(stepX(h), stepX(h + 1), u); y = lerp(topY(h), topY(h + 1), u) + Math.sin(u * Math.PI) * 0.85; sq = 0.14 * Math.sin(u * Math.PI); air = 1; mode = "hop"; i = h; }
    if (t >= LAND[h]) { x = stepX(h + 1); y = topY(h + 1); sq = -0.24 * Math.max(0, 1 - (t - LAND[h]) / 0.2); i = h + 1; }
  }
  const tf = 10.98, tl = 11.5;
  if (t >= tf) { const u = clamp((t - tf) / (tl - tf)); x = lerp(stepX(5), stepX(6) + 0.3, u); y = lerp(topY(5), 0, u * u) + Math.sin(u * Math.PI) * 0.5; tilt = -u * Math.PI * 2; air = u < 1 ? 1 : 0; sq = u < 1 ? 0.08 : -0.3 * Math.max(0, 1 - (t - tl) / 0.3); mode = u < 1 ? "fall" : "down"; i = 6; }
  return { x, y, sq, air, tilt, mode, i };
};
const S3 = ({ t, f }: Ctx) => {
  const q = stairPos(t), qc = stairPos(Math.max(8.99, t - 0.22));
  const pull = seg(t, 11.3, 13.3, Easing.inOut(Easing.cubic));
  const stamp = seg(t, 12.36, 12.62, Easing.out(Easing.back(4)));
  const camPos: V3 = [lerp(qc.x - 2.2, 1.4, pull), lerp(qc.y + 1.5, 4.2, pull), lerp(6.2, 14.5, pull)], look: V3 = [lerp(qc.x + 0.7, 1.4, pull), lerp(qc.y + 0.9, 3.0, pull), SZ];
  return (<>
    <CamSet t={t} pos={camPos} look={look} fov={64} roll={0.04 * (1 - pull)} kicks={[...LAND, 12.36]} hand={0.8} />
    <Lights warm="#ffc9c0" />
    <Floor kind="marble" a="#2a3050" b="#222845" unit={2.4} />
    <WallDoor z={-5.6} W={34} kind="plain" a="#3c4268" b="#3c4268" base="#e5483f" />
    <Surface p={[0, 3.2, -5.55]} s={[34, 0.5]} kind="plain" a="#e5483f" b="#e5483f" />
    <ChartScreen p={[-3, 5.6, -5.4]} s={[6, 3.4]} prog={seg(t, 9.0, 11.2, Easing.linear)} label="WEEKLY" />
    <Frame p={[4.4, 4.6, -5.45]} s={[1.6, 1.2]} art={1} /><Shelf p={[8.4, 0, -5]} w={3} rows={4} seed={9} wood="#2b3350" /><Plant p={[-9.4, 0, -4.4]} s={1.3} /><Plant p={[11, 0, -3.6]} s={1.2} />
    <Stairs n={N} x0={X0} dx={DX} dy={DY} z={SZ} colors={["#ff4a3f", "#d93a34"]} />
    {Array.from({ length: N }, (_, i) => <Sign key={i} p={[stepX(i), topY(i) - 0.5, SZ + 1.15]} s={[1.3, 0.55]} text={`W${i + 1}`} bg={t >= (i === 0 ? 0 : LAND[i - 1]) ? "#ffffff" : "#aab"} size={50} />)}
    {Array.from({ length: N }, (_, i) => <Cyl key={"r" + i} p={[stepX(i), topY(i) + 0.55, SZ + 1.1]} rt={0.05} h={1.1} color="#d8d8e0" line={2} />)}
    <Sign p={[3.4, 6.6 + (1 - stamp) * 0.9, -5.3]} s={[5.8, 2.0]} text={"SINCE 2012"} bg="#ffd23a" fg="#111" size={96} rot={[0, 0, -0.06]} />
    <Shaft p={[2, 5, -2]} s={[2.4, 10]} rot={[0, 0, -0.45]} color="255,120,120" o={0.18} /><Dust t={t} area={[9, 6, 3]} color="rgba(255,200,190,.9)" />
    <Person p={[q.x, q.y, SZ]} sy={q.mode === "hop" || q.mode === "fall" ? 0 : q.y} h={3.5} look={analyst} f={f} pose={{ mood: q.mode === "down" ? "shock" : "worry", nerv: 0.3, sweat: 1, squash: q.sq, air: q.air, tilt: q.tilt, arms: q.air ? "up" : "head", armK: 1, lookX: Math.sin(f * 0.13) }} />
  </>);
};

/* ===== S4 13.35-17.75: Kress walks to the Wall Street door, nervous, crowd roars ===== */
const S4 = ({ t, f }: Ctx) => {
  const wk = seg(t, 13.5, 15.4, Easing.inOut(Easing.sin)), kx = lerp(-3.6, 0.5, wk), kz = lerp(2.6, -6.25, wk);
  const dist = Math.hypot(4.1, 8.85) * wk, moving = t > 13.5 && t < 15.4, reach = seg(t, 15.4, 15.75) * (1 - seg(t, 16.3, 16.6));
  const open = seg(t, 15.77, 16.3, Easing.out(Easing.cubic)), cal = seg(t, 16.97, 17.25, Easing.out(Easing.back(3)));
  const breath = seg(t, 17.2, 17.6, Easing.inOut(Easing.sin));
  return (<>
    <Rig t={t} t0={13.35} t1={17.8} from={[-4.6, 1.8, 8.4]} to={[0.4, 2.0, -0.4]} lookFrom={[-2.6, 2.1, 0]} lookTo={[0.4, 2.6, -6.5]} roll={[-0.05, 0.02]} kicks={[15.77]} />
    <Lights />
    <Floor kind="tile" a="#cfd9f0" b="#e8eefc" unit={1.8} />
    <Rug p={[0, 0, -2.2]} s={[2.8, 14]} a="#e0302f" b="#ffd23a" />
    <WallDoor z={-7} W={26} kind="plain" a="#f1f4fc" b="#f1f4fc" door={{ x: 0, w: 3.6, h: 5 }} base="#3a63d8" />
    <SideWall x={-5.2} kind="plain" a="#e8edf9" b="#e8edf9" />
    <Surface p={[-5.18, 0.5, -2]} s={[24, 1.0]} rot={[0, Math.PI / 2, 0]} kind="plain" a="#3a63d8" b="#3a63d8" />
    {/* the hall behind the door: gold light + roaring crowd */}
    <Box p={[0, 3.5, -11.2]} s={[12, 9, 0.2]} color="#ffd86a" line={1} /><Glow p={[0, 2.6, -8.2]} r={4.4} color="rgba(255,235,150,1)" o={open * 0.9} />
    {open > 0 ? [-1.5, -0.6, 0.4, 1.4, -1.0, 0.0, 1.0].map((x, i) => <Person key={i} p={[x, 0, -8.4 - (i % 3) * 0.7]} h={3.1} look={crowdLooks[i % 6]} f={f + i * 7} pose={{ mood: i % 2 ? "shock" : "grin", arms: "up", armK: 0.6 + 0.4 * Math.sin(f * 0.35 + i), nerv: 0 }} />) : null}
    {open > 0.5 ? [0, 1, 2, 3, 4].map((i) => { const on = Math.sin(f * 0.9 + i * 2.1) > 0.82; return on ? <Glow key={i} p={[-1.8 + i * 0.9, 2.6 + (i % 2) * 0.8, -7.6]} r={1.1} color="rgba(255,255,255,1)" o={1} /> : null; }) : null}
    <Door p={[0, 0, -6.88]} color="#2447b8" open={open} label="WALL ST." w={3.6} h={5} />
    <Frame p={[-3.6, 3.6, -6.9]} s={[1.6, 1.2]} art={0} /><Frame p={[3.9, 3.4, -6.9]} s={[1.3, 1.8]} art={2} /><Clock p={[5.4, 4.6, -6.85]} r={0.55} t={t} />
    <Plant p={[-4.2, 0, -5.5]} s={1.4} /><Plant p={[4.6, 0, -5.5]} s={1.4} /><Cabinet p={[-4.4, 0, -2]} w={1.4} h={2.1} /><Lamp p={[4.6, 0, -2.6]} h={3} />
    <Sign p={[-4.4, 3.0, -1.4]} s={[1.4, 1.0]} text={"SAFETY\nFIRST"} bg="#ffd23a" size={44} rot={[0, 1.1, 0]} />
    <Shaft p={[-2, 4, -1]} s={[2.4, 9]} rot={[0, 0, 0.35]} o={0.2} /><Dust t={t} area={[4, 6, 5]} />
    <Calendar p={[-2.4, 3.7, -3.0]} month="NOV" day="17" s={2.0 * cal + 0.001} rot={[0, 0.25, 0]} />
    <Person p={[kx, 0, kz]} h={3.7} look={kress} f={f} pose={{ mood: t < 15.6 ? "deadpan" : t < 17.2 ? "gulp" : "worry", nerv: t < 15.8 ? 0 : t < 17.2 ? 0.6 : 0.3, sweat: t < 15.6 ? 0 : 1, walk: moving ? dist * WALK : undefined, speed: moving ? 0.85 : 0, arms: reach > 0.01 ? "point" : t > 16.5 ? "chest" : "down", armK: reach > 0.01 ? reach : t > 16.5 ? seg(t, 16.5, 16.8) : 0, squash: 0.05 * Math.sin(breath * Math.PI), lookX: 0, hunch: t > 15.8 ? 0.6 : 0 }} />
  </>);
};

/* ===== S5 17.75-22: the throne shakes, the world watches ===== */
const S5 = ({ t, f }: Ctx) => {
  const amp = t > 18.95 && t < 20.2 ? Math.min(1, (t - 18.95) / 0.3) * (1 - seg(t, 19.9, 20.2, Easing.linear)) * 0.12 : 0, sx = Math.sin(f * 1.9) * amp, sr = Math.sin(f * 1.3) * amp * 0.45;
  const crowd: [number, number, number][] = [[-3.0, 0.4, 0], [3.0, 0.4, 1], [-4.8, -0.8, 2], [4.8, -0.8, 3], [-3.4, 1.8, 4], [3.4, 1.8, 5], [-5.6, 1.0, 0], [5.6, 1.0, 1], [-1.9, -2.0, 2], [1.9, -2.0, 3]];
  return (<>
    <Rig t={t} t0={17.75} t1={22.1} from={[0.4, 0.9, 10.2]} to={[-0.8, 1.8, 7.6]} lookFrom={[0, 2.8, -2]} lookTo={[0, 3.2, -2]} roll={[0.02, 0.07]} kicks={[19.07, 21.2]} />
    <Lights warm="#ffe9b0" />
    <Floor kind="marble" a="#241a58" b="#1c1450" unit={2.4} />
    <WallDoor z={-8} W={30} kind="wood" a="#4b2a7a" b="#3f2268" unit={1.4} base="#c9a43a" />
    {[-5.5, 5.5].map((x) => <React.Fragment key={x}><Cyl p={[x, 3.5, -6]} rt={0.7} h={7} color="#e8d9a8" /><Cyl p={[x, 0.15, -6]} rt={0.95} h={0.3} color="#c9a43a" /><Cyl p={[x, 7.1, -6]} rt={0.95} h={0.3} color="#c9a43a" /></React.Fragment>)}
    <Frame p={[-8.6, 4.6, -7.9]} s={[1.6, 2.2]} art={1} /><Frame p={[8.6, 4.6, -7.9]} s={[1.6, 2.2]} art={2} />
    <Rug p={[0, 0, 1.6]} s={[3, 11]} a="#a0202e" b="#ffd23a" />
    <Box p={[0, 0.2, -1.2]} s={[7, 0.4, 5]} color="#d8b24a" /><Box p={[0, 0.6, -1.4]} s={[5.8, 0.4, 4]} color="#e0c05a" />
    <group position={[sx, 0, 0]} rotation={[0, 0, sr]}>
      <Box p={[0, 1.2, -1.6]} s={[2.4, 0.8, 2.0]} color="#a0202e" /><Box p={[0, 3.4, -2.5]} s={[2.6, 4.0, 0.45]} color="#a0202e" /><Box p={[0, 5.6, -2.5]} s={[2.9, 0.5, 0.55]} color="#d8b24a" />
      <Box p={[-1.5, 2.0, -1.6]} s={[0.4, 1.4, 2.0]} color="#d8b24a" /><Box p={[1.5, 2.0, -1.6]} s={[0.4, 1.4, 2.0]} color="#d8b24a" />
      <Chip p={[0, 1.95, -1.5]} s={1.0} rot={[0, f * 0.01 + sr * 3, 0]} /><Glow p={[0, 2.4, -1.0]} r={2.6} color="rgba(60,255,120,0.9)" o={0.5 + 0.2 * Math.sin(f * 0.4)} />
    </group>
    <Sign p={[0, 6.6, -7.7]} s={[5.6, 1.2]} text="AI THRONE" bg="#d8b24a" fg="#2a1a12" size={92} />
    <Shaft p={[0, 5.5, -1.5]} s={[3.2, 10]} color="255,240,170" o={0.3} /><Dust t={t} n={18} area={[5, 7, 2]} color="rgba(255,225,150,.9)" fall={t > 18.95} />
    {crowd.map(([x, z, i], n) => { const wob = 0.5 + 0.5 * Math.sin(f * 0.25 + n); return <Person key={n} p={[x, 0, z + 1.2]} h={3.3} look={crowdLooks[(i + n) % 6]} f={f + n * 9} pose={{ mood: n % 3 ? "shock" : "worry", nerv: 0.2, sweat: n % 2 ? 0.7 : 0, lookX: -Math.sign(x) * 1, flip: x > 0, arms: n % 3 === 0 ? "head" : "down", armK: 1, squash: 0.03 * wob }} />; })}
  </>);
};

/* ---------- captions: 1-2 word groups, word-synced ---------- */
const SCRIPT = "Nvidia just lost $1.7 trillion in six weeks. Then CEO Jensen Huang resigned, days before earnings. Six straight weekly drops, the longest streak since 2012. Interim chief Colette Kress now faces Wall Street on November 17. The AI throne is shaking, and the whole world is watching.".split(/\s+/);
type G = { text: string; a: number; b: number };
const groups: G[] = (() => {
  const g: G[] = []; let cur: number[] = [];
  const flush = () => { if (!cur.length) return; g.push({ text: cur.map((i) => SCRIPT[i].replace(/[.,]$/, "")).join(" "), a: words[cur[0]].start, b: words[cur[cur.length - 1]].end }); cur = []; };
  words.forEach((_, i) => { cur.push(i); if (cur.length === 2 || /[.,]$/.test(SCRIPT[i])) flush(); });
  flush(); return g;
})();
const Captions: React.FC = () => {
  const f = useCurrentFrame(), t = f / FPS;
  const idx = groups.findIndex((g, i) => t >= g.a - 0.02 && t < (groups[i + 1]?.a ?? 99) - 0.02); const g = groups[Math.max(0, idx)];
  const sc = interpolate(t - g.a, [0, 0.12], [0.75, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.back(2.6)) });
  return <div style={{ position: "absolute", left: 30, right: 30, top: 880, textAlign: "center", fontFamily: "Inter, Arial", fontWeight: 900, fontSize: 88, lineHeight: 1.05, color: "#fff", WebkitTextStroke: "12px #000", paintOrder: "stroke fill", transform: `scale(${sc})`, textShadow: "0 8px 0 rgba(0,0,0,.35)" }}>{g.text}</div>;
};

const CUTS = [0, 4.75, 8.99, 13.35, 17.75, 22.0];
export const NvidiaDemo: React.FC = () => {
  const f = useCurrentFrame(), t = f / FPS;
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      <Audio src={staticFile("mix.wav")} />
      <Scene first start={CUTS[0]} end={CUTS[1]} bg="#2a4fa8">{(c) => <S1 {...c} />}</Scene>
      <Scene start={CUTS[1]} end={CUTS[2]} bg="#925b32">{(c) => <S2 {...c} />}</Scene>
      <Scene start={CUTS[2]} end={CUTS[3]} bg="#343850" trans="zoom">{(c) => <S3 {...c} />}</Scene>
      <Scene start={CUTS[3]} end={CUTS[4]} bg="#e3e9f6">{(c) => <S4 {...c} />}</Scene>
      <Scene start={CUTS[4]} end={CUTS[5]} bg="#171b42" trans="flash">{(c) => <S5 {...c} />}</Scene>
      <Grade t={t} shaft={false} tint={t > 17.7 ? "rgba(70,30,160,.14)" : t > 4.7 && t < 9 ? "rgba(255,150,40,.10)" : t < 4.7 ? "rgba(40,80,255,.08)" : "rgba(0,0,0,0)"} />
      <Captions />
    </AbsoluteFill>
  );
};
