// 클로드 '개인 재무' 영상용 클립(2026-11-10, 일꾼E). 숫자는 claude.com 공식 소개 글의 예시에 있는 것만:
//  FinOpen  = 콜드 오픈: 영수증이 쏟아지다 도넛 그래프로 모임 → "내 돈, 어디 갔지?" → 클로드에게 묻는 말풍선
//  FinLink  = 연결 흐름: 나 → Plaid(내가 직접 로그인) → 은행 → 클로드(읽기 전용). 비밀번호 칸은 클로드에 안 감
//  FinSpend = 공식 예시: 이번 달 지출 $4,309.37, 절반 넘게 월세·공과금, 식음료 $1,024.51
// 실제 회사 로고는 그리지 않는다(이름 글자만). 날짜 글자 없음.
import React from 'react';
import {AbsoluteFill, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';

const BG = 'radial-gradient(circle at 50% 35%, #3A1219 0%, #140A0C 70%)';
const RED = '#FF4757';
const APR = '#FFD6A5';
const DIM = '#8A6E72';
const Font = () => <style>{`@font-face{font-family:P;src:url(${staticFile('Pretendard-Black.otf')})}`}</style>;
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

const Dots: React.FC<{f: number}> = ({f}) => {
  const s = 48;
  const ox = (f * 0.35) % s;
  const out: React.ReactNode[] = [];
  for (let y = 24; y < 1080; y += s)
    for (let x = -s; x < 1920 + s; x += s) {
      const a = 0.08 + 0.1 * (0.5 + 0.5 * Math.sin(x / 140 + y / 90 + f / 18));
      out.push(<circle key={x + '_' + y} cx={x + ox} cy={y} r={2.4} fill={APR} opacity={a} />);
    }
  return <svg width={1920} height={1080} style={{position: 'absolute', inset: 0}}>{out}</svg>;
};

// 도넛 한 조각(시작~끝 비율 0..1)
const arc = (cx: number, cy: number, r: number, a0: number, a1: number) => {
  const p = (t: number) => [cx + r * Math.cos(2 * Math.PI * t - Math.PI / 2), cy + r * Math.sin(2 * Math.PI * t - Math.PI / 2)];
  const [x0, y0] = p(a0);
  const [x1, y1] = p(Math.max(a0 + 0.0001, a1));
  return `M ${x0} ${y0} A ${r} ${r} 0 ${a1 - a0 > 0.5 ? 1 : 0} 1 ${x1} ${y1}`;
};

const Receipt: React.FC<{w: number; h: number}> = ({w, h}) => (
  <div style={{width: w, height: h, background: '#FFF6EC', borderRadius: 6, boxShadow: '0 12px 30px rgba(0,0,0,.5)', padding: 14, boxSizing: 'border-box'}}>
    {[0.8, 0.55, 0.7, 0.4, 0.65].map((k, i) => (
      <div key={i} style={{height: 8, width: `${k * 100}%`, background: i === 4 ? RED : '#C9B8AA', borderRadius: 4, marginBottom: 10}} />
    ))}
  </div>
);

// ── 1. 콜드 오픈
export const FinOpen: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const fade = interpolate(f, [0, 10], [0, 1], clamp);
  const gather = interpolate(f, [70, 110], [0, 1], clamp);           // 영수증이 가운데로 모임
  const ring = interpolate(f, [100, 150], [0, 1], clamp);            // 도넛이 그려짐
  const q = spring({frame: f - 120, fps, config: {damping: 12}});
  const bub = spring({frame: f - 175, fps, config: {damping: 14}});
  const N = 18;
  return (
    <AbsoluteFill style={{background: BG, fontFamily: 'P', color: '#fff', opacity: fade}}>
      <Font />
      <Dots f={f} />
      {Array.from({length: N}).map((_, i) => {
        const x0 = 120 + ((i * 263) % 1680);
        const fall = interpolate(f, [i * 3, i * 3 + 45], [-260, 260 + ((i * 97) % 520)], clamp);
        const rot = ((i * 37) % 50) - 25 + Math.sin(f / 9 + i) * 6;
        const x = x0 + (760 - x0) * gather;
        const y = fall + (400 - fall) * gather;
        const sc = 1 - 0.85 * gather;
        return (
          <div key={i} style={{position: 'absolute', left: x, top: y, transform: `rotate(${rot * (1 - gather)}deg) scale(${sc})`, opacity: 1 - gather}}>
            <Receipt w={150} h={200} />
          </div>
        );
      })}
      <svg width={1920} height={1080} style={{position: 'absolute', inset: 0}}>
        <path d={arc(960, 520, 210, 0, 0.52 * ring)} stroke={RED} strokeWidth={70} fill="none" />
        <path d={arc(960, 520, 210, 0.53, 0.53 + 0.23 * ring)} stroke={APR} strokeWidth={70} fill="none" />
        <path d={arc(960, 520, 210, 0.77, 0.77 + 0.22 * ring)} stroke={DIM} strokeWidth={70} fill="none" />
      </svg>
      <div style={{position: 'absolute', left: 760, top: 440, width: 400, textAlign: 'center', fontSize: 150, color: '#fff', opacity: q, transform: `scale(${0.4 + 0.6 * q})`, textShadow: `0 0 40px ${RED}`}}>?</div>
      <div style={{position: 'absolute', top: 70, width: '100%', textAlign: 'center', fontSize: 84, opacity: q, transform: `translateY(${(1 - q) * -40}px)`}}>
        이번 달 내 돈, <span style={{color: RED}}>어디 갔지?</span>
      </div>
      <div style={{position: 'absolute', left: 560, top: 830, width: 800, padding: '26px 40px', borderRadius: 40, background: '#FFF6EC', color: '#2A0D12',
        fontSize: 52, textAlign: 'center', opacity: bub, transform: `scale(${0.7 + 0.3 * bub})`, boxShadow: `0 0 50px ${RED}66`}}>
        클로드에게 <span style={{color: RED}}>그냥 묻기</span> 💬
      </div>
    </AbsoluteFill>
  );
};

// ── 2. 연결 흐름
const Node: React.FC<{x: number; y: number; title: string; sub: string; color: string; p: number; icon: React.ReactNode}> = ({x, y, title, sub, color, p, icon}) => (
  <div style={{position: 'absolute', left: x - 170, top: y - 150, width: 340, height: 300, borderRadius: 34, border: `5px solid ${color}`,
    background: 'rgba(20,10,12,.88)', boxShadow: `0 0 40px ${color}55`, opacity: p, transform: `translateY(${(1 - p) * 50}px)`,
    display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center'}}>
    <div style={{height: 120, display: 'flex', alignItems: 'center'}}>{icon}</div>
    <div style={{fontSize: 56, color: '#fff', marginTop: 10}}>{title}</div>
    <div style={{fontSize: 34, color, marginTop: 6}}>{sub}</div>
  </div>
);
const Bank = () => (
  <svg width={130} height={110} viewBox="0 0 130 110"><polygon points="65,6 124,38 6,38" fill={APR} />
    {[22, 50, 78, 106].map((x) => <rect key={x} x={x - 7} y={44} width={14} height={46} fill={APR} />)}<rect x={6} y={94} width={118} height={12} fill={APR} /></svg>
);
const Person = () => (
  <svg width={110} height={110} viewBox="0 0 110 110"><circle cx={55} cy={34} r={24} fill="#fff" /><path d="M 12 108 C 14 70, 96 70, 98 108 Z" fill="#fff" /></svg>
);
const Bridge = () => (
  <svg width={150} height={100} viewBox="0 0 150 100"><path d="M 6 80 Q 75 -10 144 80" stroke={RED} strokeWidth={10} fill="none" />
    {[30, 55, 75, 95, 120].map((x) => <line key={x} x1={x} y1={80} x2={x} y2={x === 75 ? 36 : 50} stroke={RED} strokeWidth={6} />)}<rect x={0} y={80} width={150} height={10} fill={RED} /></svg>
);
const Spark = () => (
  <svg width={110} height={110} viewBox="0 0 110 110">{[0, 45, 90, 135].map((a) => (
    <rect key={a} x={49} y={8} width={12} height={94} rx={6} fill={RED} transform={`rotate(${a} 55 55)`} />))}</svg>
);

export const FinLink: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const fade = interpolate(f, [0, 10], [0, 1], clamp);
  const pts = [
    {x: 300, title: '나', sub: '직접 로그인', color: '#fff', icon: <Person />},
    {x: 760, title: 'Plaid', sub: '잇는 다리', color: RED, icon: <Bridge />},
    {x: 1210, title: '은행', sub: '내 계좌', color: APR, icon: <Bank />},
    {x: 1640, title: '클로드', sub: '읽기 전용', color: RED, icon: <Spark />},
  ];
  const ps = pts.map((_, i) => spring({frame: f - 8 - i * 14, fps, config: {damping: 14}}));
  const key = interpolate(f, [70, 140], [0, 1], clamp);              // 열쇠(로그인)가 나→Plaid→은행
  const data = interpolate(f, [150, 200], [0, 1], clamp);            // 은행→클로드 읽기
  const no = spring({frame: f - 205, fps, config: {damping: 10}});
  const kx = 300 + (1210 - 300) * key;
  return (
    <AbsoluteFill style={{background: BG, fontFamily: 'P', color: '#fff', opacity: fade}}>
      <Font />
      <Dots f={f} />
      <div style={{position: 'absolute', top: 80, width: '100%', textAlign: 'center', fontSize: 64}}>
        은행 로그인은 <span style={{color: RED}}>내가 직접</span>
      </div>
      <svg width={1920} height={1080} style={{position: 'absolute', inset: 0}}>
        <line x1={470} y1={500} x2={590} y2={500} stroke="#fff" strokeOpacity={0.35} strokeWidth={6} strokeDasharray="14 12" />
        <line x1={930} y1={500} x2={1040} y2={500} stroke="#fff" strokeOpacity={0.35} strokeWidth={6} strokeDasharray="14 12" />
        <line x1={1380} y1={500} x2={1470} y2={500} stroke={APR} strokeOpacity={0.3 + 0.7 * data} strokeWidth={8} />
        {data > 0 && data < 1 && <circle cx={1380 + 90 * data} cy={500} r={14} fill={APR} />}
      </svg>
      {pts.map((p, i) => <Node key={i} x={p.x} y={500} title={p.title} sub={p.sub} color={p.color} p={ps[i]} icon={p.icon} />)}
      {key > 0 && key < 1 && (
        <div style={{position: 'absolute', left: kx - 40, top: 300, fontSize: 80, transform: `rotate(${Math.sin(f / 4) * 10}deg)`}}>🔑</div>
      )}
      <div style={{position: 'absolute', left: 1440, top: 700, width: 400, padding: '20px 26px', borderRadius: 24, background: 'rgba(255,255,255,.06)',
        border: `4px solid ${RED}`, opacity: no, transform: `scale(${0.7 + 0.3 * no})`}}>
        <div style={{fontSize: 30, color: DIM}}>은행 비밀번호</div>
        <div style={{fontSize: 56, color: '#fff', letterSpacing: 8, position: 'relative'}}>●●●●●●
          <div style={{position: 'absolute', left: -10, right: -10, top: 34, height: 8, background: RED, transform: 'rotate(-8deg)'}} /></div>
        <div style={{fontSize: 36, color: RED, marginTop: 6}}>클로드는 못 봐요</div>
      </div>
      <div style={{position: 'absolute', left: 180, top: 760, width: 1100, fontSize: 44, color: APR, opacity: no}}>
        👀 잔액 · 거래 내역만 <span style={{color: '#fff'}}>읽기</span> &nbsp;·&nbsp; 💸 옮기기 ✕
      </div>
    </AbsoluteFill>
  );
};

// ── 3. 공식 예시 지출 분석
const fmtUSD = (v: number) => '$' + v.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
export const FinSpend: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const fade = interpolate(f, [0, 10], [0, 1], clamp);
  const total = 4309.37;
  const food = 1024.51;
  const cnt = interpolate(f, [10, 70], [0, 1], clamp);
  const s1 = interpolate(f, [70, 120], [0, 1], clamp);               // 월세·공과금(절반 넘게)
  const s2 = interpolate(f, [130, 170], [0, 1], clamp);              // 식음료
  const s3 = interpolate(f, [175, 205], [0, 1], clamp);              // 그 밖
  const l1 = spring({frame: f - 90, fps, config: {damping: 14}});
  const l2 = spring({frame: f - 145, fps, config: {damping: 14}});
  const l3 = spring({frame: f - 185, fps, config: {damping: 14}});
  const half = 0.52, fr = food / total;
  const ease = (x: number) => 1 - Math.pow(1 - x, 3);
  return (
    <AbsoluteFill style={{background: BG, fontFamily: 'P', color: '#fff', opacity: fade}}>
      <Font />
      <Dots f={f} />
      <div style={{position: 'absolute', top: 64, left: 140, fontSize: 56, color: APR}}>"이번 달 내 돈 어디 갔어?"</div>
      <svg width={1920} height={1080} style={{position: 'absolute', inset: 0}}>
        <circle cx={600} cy={590} r={280} stroke="rgba(255,255,255,.07)" strokeWidth={96} fill="none" />
        <path d={arc(600, 590, 280, 0, half * ease(s1))} stroke={RED} strokeWidth={96} fill="none" />
        {s2 > 0 && <path d={arc(600, 590, 280, half + 0.005, half + 0.005 + fr * ease(s2))} stroke={APR} strokeWidth={96} fill="none" />}
        {s3 > 0 && <path d={arc(600, 590, 280, half + fr + 0.01, half + fr + 0.01 + (1 - half - fr - 0.015) * ease(s3))} stroke={DIM} strokeWidth={96} fill="none" />}
      </svg>
      <div style={{position: 'absolute', left: 340, top: 520, width: 520, textAlign: 'center'}}>
        <div style={{fontSize: 38, color: DIM}}>이번 달 지출</div>
        <div style={{fontSize: 68, color: '#fff', textShadow: `0 0 30px ${RED}88`}}>{fmtUSD(total * ease(cnt))}</div>
      </div>
      {[
        {p: l1, c: RED, k: '월세 · 공과금', v: '절반 넘게'},
        {p: l2, c: APR, k: '식음료', v: fmtUSD(food)},
        {p: l3, c: DIM, k: '그 밖', v: '나머지'},
      ].map((r, i) => (
        <div key={i} style={{position: 'absolute', left: 1080, top: 330 + i * 170, width: 720, height: 130, borderRadius: 28, background: 'rgba(255,255,255,.05)',
          border: `4px solid ${r.c}`, display: 'flex', alignItems: 'center', padding: '0 36px', boxSizing: 'border-box', opacity: r.p,
          transform: `translateX(${(1 - r.p) * 120}px)`}}>
          <div style={{width: 34, height: 34, borderRadius: 17, background: r.c, marginRight: 26}} />
          <div style={{fontSize: 50, flex: 1}}>{r.k}</div>
          <div style={{fontSize: 56, color: r.c}}>{r.v}</div>
        </div>
      ))}
      <div style={{position: 'absolute', left: 1080, top: 860, fontSize: 32, color: DIM, opacity: l3}}>클로드 공식 소개 글의 예시 금액</div>
    </AbsoluteFill>
  );
};
