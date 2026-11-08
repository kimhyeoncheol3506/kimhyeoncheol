// 메타 뮤즈 영상용 클립(2026-11-07). 숫자는 쓰지 않는다(예시 화면).
//  MuseOpen = 앱을 닫아도 일하고 알림을 보낸다(메타 발표), MuseParts = 에이전트 뼈대 4부품(옆자리 연구원 정리),
//  MuseApprove = 승인 범위 5단계(한 번 ~ 영구, 가운데 이름은 모름 → 점만 찍는다).
import React from 'react';
import {AbsoluteFill, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';

const BG = 'radial-gradient(circle at 50% 35%, #3A1C12 0%, #140C08 72%)';
const ACC = '#FF7A59';
const ACC2 = '#FFE3A3';
const Font = () => <style>{`@font-face{font-family:P;src:url(${staticFile('Pretendard-Black.otf')})}`}</style>;
const useFade = () => interpolate(useCurrentFrame(), [0, 10], [0, 1], {extrapolateRight: 'clamp'});

const NOTES = [
  {icon: '🍝', t: '토요일 저녁 식당, 자리 찾았어요', s: '예약할까요? · 승인 필요'},
  {icon: '💳', t: '잊고 있던 구독을 찾았어요', s: '해지할까요? · 승인 필요'},
  {icon: '👟', t: '찜한 운동화 할인 시작', s: '살까요? · 승인 필요'},
  {icon: '✈️', t: '항공권 가격이 내려갔어요', s: '알려만 드려요'},
];
export const MuseOpen: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const fade = useFade();
  const phone = spring({frame: f, fps, config: {damping: 18}});
  return (
    <AbsoluteFill style={{background: BG, fontFamily: 'P', color: '#fff', opacity: fade}}>
      <Font />
      <div style={{position: 'absolute', left: 140, top: 250, width: 700, fontSize: 92, lineHeight: 1.25}}>
        앱을 <span style={{color: ACC}}>닫았는데</span><br />알림이 <span style={{color: ACC2}}>계속</span> 와요
        <div style={{fontSize: 44, color: '#d9b8a8', marginTop: 40}}>예시 화면 · 메타 뮤즈</div>
      </div>
      <div style={{position: 'absolute', left: 1000, top: 70, width: 620, height: 940, borderRadius: 70, border: '6px solid #5a3a2e',
        background: '#1d120d', transform: `translateY(${(1 - phone) * 300}px)`, boxShadow: `0 0 80px ${ACC}33`}}>
        <div style={{textAlign: 'center', marginTop: 60, fontSize: 120, color: '#f4e6dc'}}>7:42</div>
        <div style={{textAlign: 'center', fontSize: 34, color: '#b9998a'}}>토요일 아침</div>
        {NOTES.map((n, i) => {
          const p = spring({frame: f - 30 - i * 30, fps, config: {damping: 14}});
          return (
            <div key={i} style={{position: 'absolute', left: 30, top: 330 + i * 150, width: 560, height: 130, borderRadius: 30,
              background: 'rgba(255,240,230,0.12)', display: 'flex', alignItems: 'center', gap: 22, padding: '0 24px', boxSizing: 'border-box',
              opacity: p, transform: `translateY(${(1 - p) * -60}px) scale(${0.9 + 0.1 * p})`}}>
              <div style={{fontSize: 60}}>{n.icon}</div>
              <div>
                <div style={{fontSize: 33}}>{n.t}</div>
                <div style={{fontSize: 27, color: i < 3 ? ACC : ACC2, marginTop: 6}}>Muse · {n.s}</div>
              </div>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

const PARTS = [
  {g: '👀', n: '눈', s: '연결한 앱', x: -560, y: -250},
  {g: '🖐', n: '손', s: '클라우드 컴퓨터', x: 560, y: -250},
  {g: '📒', n: '수첩', s: '기억 (Memory.md)', x: -560, y: 250},
  {g: '🛡', n: '감시자', s: '센티넬', x: 560, y: 250},
];
export const MuseParts: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const fade = useFade();
  const core = spring({frame: f - 5, fps, config: {damping: 12}});
  const pulse = 1 + 0.03 * Math.sin(f / 6);
  return (
    <AbsoluteFill style={{background: BG, fontFamily: 'P', color: '#fff', opacity: fade}}>
      <Font />
      <div style={{position: 'absolute', top: 60, width: '100%', textAlign: 'center', fontSize: 60}}>AI 비서의 <span style={{color: ACC}}>뼈대</span></div>
      <svg width={1920} height={1080} style={{position: 'absolute', left: 0, top: 0}}>
        {PARTS.map((p, i) => {
          const k = spring({frame: f - 40 - i * 28, fps, config: {damping: 20}});
          return <line key={i} x1={960} y1={580} x2={960 + p.x * k} y2={580 + p.y * k} stroke={ACC} strokeWidth={6} strokeDasharray="14 12" opacity={0.7} />;
        })}
      </svg>
      <div style={{position: 'absolute', left: 960 - 170, top: 580 - 170, width: 340, height: 340, borderRadius: 170,
        background: `radial-gradient(circle, ${ACC} 0%, #8A2E18 80%)`, transform: `scale(${core * pulse})`, display: 'flex',
        flexDirection: 'column', alignItems: 'center', justifyContent: 'center', boxShadow: `0 0 90px ${ACC}88`}}>
        <div style={{fontSize: 96}}>🧠</div>
        <div style={{fontSize: 46}}>생각하는 모델</div>
      </div>
      {PARTS.map((p, i) => {
        const k = spring({frame: f - 55 - i * 28, fps, config: {damping: 13}});
        return (
          <div key={i} style={{position: 'absolute', left: 960 + p.x - 230, top: 580 + p.y - 95, width: 460, height: 190, borderRadius: 34,
            background: '#2A1711', border: `3px solid ${i === 3 ? ACC2 : ACC}`, display: 'flex', alignItems: 'center', gap: 24,
            padding: '0 28px', boxSizing: 'border-box', opacity: k, transform: `scale(${0.6 + 0.4 * k})`}}>
            <div style={{fontSize: 84}}>{p.g}</div>
            <div>
              <div style={{fontSize: 58, color: i === 3 ? ACC2 : '#fff'}}>{p.n}</div>
              <div style={{fontSize: 34, color: '#e2c4b4'}}>{p.s}</div>
            </div>
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

export const MuseApprove: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const fade = useFade();
  const knob = interpolate(f, [40, 110, 150, 190], [0, 4, 4, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const warn = interpolate(f, [175, 195], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const X0 = 360, W = 1200;
  return (
    <AbsoluteFill style={{background: BG, fontFamily: 'P', color: '#fff', opacity: fade}}>
      <Font />
      <div style={{position: 'absolute', top: 140, width: '100%', textAlign: 'center', fontSize: 72}}>얼마나 <span style={{color: ACC}}>믿고 맡길까?</span></div>
      <div style={{position: 'absolute', top: 250, width: '100%', textAlign: 'center', fontSize: 44, color: '#e2c4b4'}}>승인 범위 · 다섯 단계 중에서 고르기</div>
      <div style={{position: 'absolute', left: X0, top: 548, width: W, height: 24, borderRadius: 12, background: `linear-gradient(90deg, ${ACC2}, ${ACC})`}} />
      {[0, 1, 2, 3, 4].map(i => {
        const on = Math.round(knob) === i;
        return <div key={i} style={{position: 'absolute', left: X0 + (W * i) / 4 - 26, top: 534, width: 52, height: 52, borderRadius: 26,
          background: on ? '#fff' : '#3a2219', border: `5px solid ${on ? ACC : '#7a4a38'}`}} />;
      })}
      <div style={{position: 'absolute', left: X0 + (W * knob) / 4 - 60, top: 500, width: 120, height: 120, borderRadius: 60, background: '#fff',
        boxShadow: `0 0 50px ${ACC}`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 64}}>✋</div>
      <div style={{position: 'absolute', left: X0 - 120, top: 660, width: 240, textAlign: 'center', fontSize: 52, color: ACC2}}>한 번만</div>
      <div style={{position: 'absolute', left: X0 + W - 120, top: 660, width: 240, textAlign: 'center', fontSize: 52, color: ACC}}>영구</div>
      <div style={{position: 'absolute', top: 800, width: '100%', textAlign: 'center', fontSize: 56, opacity: warn, color: ACC}}>
        처음엔 <span style={{color: '#fff'}}>한 번만</span>부터!
      </div>
    </AbsoluteFill>
  );
};
