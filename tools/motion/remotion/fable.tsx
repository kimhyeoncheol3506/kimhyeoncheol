// 클로드 페이블 5.2 영상용 클립(2026-11-10, 일꾼D). 숫자는 앤트로픽 발표 글·연구 글에 있는 것만:
//  FableOpen  = 모델 사다리(하이쿠·소네트·오퍼스 5.5 위에 페이블 5.2) → "그런데 시작은 오퍼스로?" (콜드 오픈)
//  FableCost  = FrontierCode 2.0 정확도-비용: 페이블 하이 45.3% ≈ 오퍼스 맥스 45.5%, 비용 약 절반 / 페이블 엑스하이 49.1%
//  FableDevices = 전자 기기 3개(음성비서 허브·USB 스피커폰·가상 애완동물), 회로 수정 0번, 기판마다 하루 안에
// 실제 회사 로고는 그리지 않는다(이름 글자만). 날짜 글자 없음.
import React from 'react';
import {AbsoluteFill, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';

const BG = 'radial-gradient(circle at 50% 30%, #2A1840 0%, #120C1E 70%)';
const PINK = '#FF5C8A';
const SKY = '#A0E7FF';
const DIM = '#9A9ABA';
const Font = () => <style>{`@font-face{font-family:P;src:url(${staticFile('Pretendard-Black.otf')})}`}</style>;
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

const Grid: React.FC<{f: number}> = ({f}) => (
  <svg width={1920} height={1080} style={{position: 'absolute', inset: 0, opacity: 0.35}}>
    {Array.from({length: 25}).map((_, i) => (
      <line key={'v' + i} x1={960 + (i - 12) * 40} y1={600} x2={960 + (i - 12) * 190} y2={1080} stroke={SKY} strokeOpacity={0.25} />
    ))}
    {Array.from({length: 8}).map((_, i) => {
      const y = 600 + Math.pow((i + ((f / 40) % 1)) / 8, 2) * 480;
      return <line key={'h' + i} x1={0} y1={y} x2={1920} y2={y} stroke={SKY} strokeOpacity={0.2} />;
    })}
  </svg>
);

// ── 1. 콜드 오픈: 사다리
const RUNGS = [
  {n: '하이쿠 5.5', c: DIM},
  {n: '소네트 5.5', c: DIM},
  {n: '오퍼스 5.5', c: SKY},
  {n: '페이블 5.2', c: PINK},
];
export const FableOpen: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const fade = interpolate(f, [0, 10], [0, 1], clamp);
  const q = spring({frame: f - 150, fps, config: {damping: 12}});
  const arrow = interpolate(f, [150, 190], [0, 1], clamp);
  return (
    <AbsoluteFill style={{background: BG, fontFamily: 'P', color: '#fff', opacity: fade}}>
      <Font />
      <Grid f={f} />
      <div style={{position: 'absolute', top: 70, width: '100%', textAlign: 'center', fontSize: 58, color: '#d8cfee'}}>앤트로픽 모델 사다리</div>
      {RUNGS.map((r, i) => {
        const p = spring({frame: f - 12 - i * 22, fps, config: {damping: 14}});
        const top = 800 - i * 160;
        const w = 560 + i * 60;
        const big = i === 3;
        return (
          <div key={i} style={{position: 'absolute', left: 300 + (3 - i) * 0, top, width: w, height: 120, borderRadius: 26,
            background: big ? `linear-gradient(90deg, ${PINK}, #FF8FB0)` : 'rgba(255,255,255,.07)', border: `4px solid ${r.c}`,
            boxShadow: big ? `0 0 ${60 + 20 * Math.sin(f / 6)}px ${PINK}aa` : 'none', display: 'flex', alignItems: 'center', paddingLeft: 40,
            fontSize: big ? 66 : 54, color: big ? '#1a0b14' : r.c, opacity: p, transform: `translateY(${(1 - p) * 60}px) scale(${0.9 + 0.1 * p})`}}>
            {r.n}{big && <span style={{marginLeft: 26, fontSize: 40, padding: '6px 20px', borderRadius: 999, background: '#1a0b14', color: PINK}}>NEW · 한 단계 위</span>}
          </div>
        );
      })}
      {/* 오퍼스 칸을 가리키는 화살표 */}
      <svg width={1920} height={1080} style={{position: 'absolute', inset: 0}}>
        <path d={`M 1480 380 C 1400 450, 1250 520, ${1040 + 0 * arrow} 540`} fill="none" stroke={SKY} strokeWidth={10}
          strokeDasharray={900} strokeDashoffset={900 * (1 - arrow)} strokeLinecap="round" />
        <polygon points="1030,540 1072,505 1075,562" fill={SKY} opacity={arrow > 0.95 ? 1 : 0} />
      </svg>
      <div style={{position: 'absolute', left: 1300, top: 170, width: 560, textAlign: 'center', opacity: q, transform: `scale(${0.6 + 0.4 * q}) rotate(-4deg)`}}>
        <div style={{fontSize: 52, color: '#fff'}}>그런데 시작은</div>
        <div style={{fontSize: 92, color: SKY, textShadow: `0 0 40px ${SKY}88`}}>오퍼스로<span style={{color: PINK}}>?</span></div>
      </div>
    </AbsoluteFill>
  );
};

// ── 2. 정확도-비용 그래프
export const FableCost: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const fade = interpolate(f, [0, 10], [0, 1], clamp);
  const X0 = 260, X1 = 1660, Y0 = 880, Y1 = 330;
  // 점수 30~52% 를 화면에. 비용 축은 로그 느낌(숫자 표기 없음)
  const y = (s: number) => Y0 - ((s - 30) / 22) * (Y0 - Y1);
  const opus = {x: 1380, y: y(45.5)};
  const fh = {x: 900, y: y(45.3)};
  const fx = {x: 1180, y: y(49.1)};
  const pO = spring({frame: f - 20, fps, config: {damping: 12}});
  const pH = spring({frame: f - 75, fps, config: {damping: 12}});
  const arr = interpolate(f, [110, 150], [0, 1], clamp);
  const pX = spring({frame: f - 175, fps, config: {damping: 10}});
  const Dot: React.FC<{x: number; y: number; c: string; p: number; label: string; sub: string; dx?: number; dy?: number}> = ({x, y, c, p, label, sub, dx = 0, dy = -150}) => (
    <>
      <div style={{position: 'absolute', left: x - 24, top: y - 24, width: 48, height: 48, borderRadius: 24, background: c,
        boxShadow: `0 0 40px ${c}`, transform: `scale(${p})`}} />
      <div style={{position: 'absolute', left: x - 220 + dx, top: y + dy, width: 440, textAlign: 'center', opacity: p}}>
        <div style={{fontSize: 46, color: c}}>{label}</div>
        <div style={{fontSize: 38, color: '#fff'}}>{sub}</div>
      </div>
    </>
  );
  return (
    <AbsoluteFill style={{background: BG, fontFamily: 'P', color: '#fff', opacity: fade}}>
      <Font />
      <div style={{position: 'absolute', top: 60, width: '100%', textAlign: 'center', fontSize: 58}}>코딩 시험 <span style={{color: PINK}}>점수 vs 일 하나당 비용</span></div>
      <div style={{position: 'absolute', top: 140, width: '100%', textAlign: 'center', fontSize: 34, color: '#b8acd6'}}>프런티어코드 2.0 · 앤트로픽 발표</div>
      <svg width={1920} height={1080} style={{position: 'absolute', inset: 0}}>
        <line x1={X0} y1={Y0} x2={X1} y2={Y0} stroke="#6f6590" strokeWidth={4} />
        <line x1={X0} y1={Y0} x2={X0} y2={Y1 - 20} stroke="#6f6590" strokeWidth={4} />
        <line x1={X0} y1={opus.y} x2={X1} y2={opus.y} stroke={SKY} strokeOpacity={0.35 * pO} strokeWidth={3} strokeDasharray="14 12" />
        <path d={`M ${opus.x - 40} ${opus.y + 60} L ${opus.x - 40 - (opus.x - fh.x - 80) * arr} ${opus.y + 60}`} stroke={PINK} strokeWidth={10} strokeLinecap="round" />
        {arr > 0.97 && <polygon points={`${fh.x + 40},${opus.y + 60} ${fh.x + 75},${opus.y + 38} ${fh.x + 75},${opus.y + 82}`} fill={PINK} />}
      </svg>
      <div style={{position: 'absolute', left: X0 - 40, top: Y1 - 90, fontSize: 36, color: '#b8acd6'}}>점수 ↑</div>
      <div style={{position: 'absolute', left: X1 - 360, top: Y0 + 24, width: 400, textAlign: 'right', fontSize: 36, color: '#b8acd6'}}>일 하나당 비용 →</div>
      <Dot {...opus} c={SKY} p={pO} label="오퍼스 5.5 · 맥스" sub="45.5%" dx={60} dy={-170} />
      <Dot {...fh} c={PINK} p={pH} label="페이블 5.2 · 하이" sub="45.3%" dx={-290} dy={-50} />
      <div style={{position: 'absolute', left: (fh.x + opus.x) / 2 - 220, top: opus.y + 90, width: 440, textAlign: 'center', fontSize: 50, color: PINK, opacity: arr}}>비용 약 절반</div>
      <Dot {...fx} c={'#FFD27A'} p={pX} label="페이블 5.2 · 엑스하이" sub="49.1% · 공개 모델 최고" dx={-320} dy={-60} />
    </AbsoluteFill>
  );
};

// ── 3. 기기 3개
const Hub: React.FC = () => (
  <svg width={300} height={300} viewBox="0 0 300 300">
    <path d="M60 230 L240 230 L240 120 Q150 60 60 120 Z" fill="#2b2140" stroke={SKY} strokeWidth={8} />
    {Array.from({length: 5}).map((_, i) => <circle key={i} cx={100 + i * 25} cy={170} r={7} fill={SKY} />)}
    <rect x={95} y={200} width={110} height={10} rx={5} fill={PINK} />
  </svg>
);
const Puck: React.FC = () => (
  <svg width={300} height={300} viewBox="0 0 300 300">
    <ellipse cx={150} cy={170} rx={115} ry={55} fill="#2b2140" stroke={SKY} strokeWidth={8} />
    <ellipse cx={150} cy={160} rx={70} ry={30} fill="none" stroke={PINK} strokeWidth={8} />
    <path d="M150 225 L150 280" stroke={DIM} strokeWidth={10} strokeLinecap="round" />
  </svg>
);
const Pet: React.FC = () => (
  <svg width={300} height={300} viewBox="0 0 300 300">
    <ellipse cx={150} cy={160} rx={95} ry={120} fill="#2b2140" stroke={SKY} strokeWidth={8} />
    <rect x={95} y={95} width={110} height={90} rx={14} fill="#122a33" stroke={SKY} strokeWidth={4} />
    <circle cx={130} cy={135} r={8} fill={SKY} /><circle cx={170} cy={135} r={8} fill={SKY} />
    <path d="M130 158 Q150 172 170 158" stroke={SKY} strokeWidth={5} fill="none" />
    {[110, 150, 190].map((x) => <circle key={x} cx={x} cy={225} r={13} fill={PINK} />)}
  </svg>
);
const DEV = [
  {n: '음성비서 허브', C: Hub},
  {n: 'USB 스피커폰', C: Puck},
  {n: '가상 애완동물', C: Pet},
];
export const FableDevices: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const fade = interpolate(f, [0, 10], [0, 1], clamp);
  const bottom = interpolate(f, [200, 225], [0, 1], clamp);
  return (
    <AbsoluteFill style={{background: BG, fontFamily: 'P', color: '#fff', opacity: fade}}>
      <Font />
      <Grid f={f} />
      <div style={{position: 'absolute', top: 70, width: '100%', textAlign: 'center', fontSize: 60}}>한 문단 지시로 <span style={{color: PINK}}>기기 3개</span></div>
      <div style={{position: 'absolute', top: 160, width: '100%', textAlign: 'center', fontSize: 36, color: '#b8acd6'}}>회로 기판 · 3D 프린팅 케이스 · 소프트웨어까지</div>
      {DEV.map((d, i) => {
        const p = spring({frame: f - 20 - i * 30, fps, config: {damping: 13}});
        const ok = spring({frame: f - 120 - i * 18, fps, config: {damping: 10}});
        const x = 170 + i * 560;
        return (
          <div key={i} style={{position: 'absolute', left: x, top: 260, width: 460, height: 560, borderRadius: 34, background: 'rgba(255,255,255,.06)',
            border: `3px solid ${SKY}55`, opacity: p, transform: `translateY(${(1 - p) * 80}px)`}}>
            <div style={{position: 'absolute', left: 80, top: 50}}><d.C /></div>
            <div style={{position: 'absolute', top: 380, width: '100%', textAlign: 'center', fontSize: 48}}>{d.n}</div>
            <div style={{position: 'absolute', top: 460, width: '100%', textAlign: 'center'}}>
              <span style={{display: 'inline-block', fontSize: 40, padding: '8px 28px', borderRadius: 999, background: PINK, color: '#1a0b14',
                transform: `scale(${ok})`}}>✓ 작동</span>
            </div>
          </div>
        );
      })}
      <div style={{position: 'absolute', top: 880, width: '100%', textAlign: 'center', fontSize: 52, opacity: bottom}}>
        회로 수정 <span style={{color: PINK}}>0번</span> · 기판마다 <span style={{color: SKY}}>하루 안에</span>
      </div>
    </AbsoluteFill>
  );
};
