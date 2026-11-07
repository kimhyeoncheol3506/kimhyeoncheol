// 제미나이 옴니 1.2 플래시 영상용 클립(2026-11-07). 숫자는 구글 공식 발표·가격표에 있는 것만:
//  OmniLength = 1.1 최대 10초 → 1.2 최대 15초(3~15초, 1초 단위) · OmniTurns = 공식 예시(배경을 대화로 차례차례 바꾸기)
//  OmniPrice = 720p 초당 약 0.07달러, 15초 약 1.04달러, 30% 인하 / 해상도별 초당 가격(360p 0.023, 1080p 0.104, 4K 0.209)
import React from 'react';
import {AbsoluteFill, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';

const BG = 'radial-gradient(circle at 50% 35%, #2A1C4A 0%, #0E0A1C 72%)';
const ACC = '#FFC23D';
const ACC2 = '#7CF0FF';
const Font = () => <style>{`@font-face{font-family:P;src:url(${staticFile('Pretendard-Black.otf')})}`}</style>;
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

export const OmniLength: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const fade = interpolate(f, [0, 10], [0, 1], clamp);
  const a = interpolate(f, [15, 60], [0, 10], clamp);
  const b = interpolate(f, [80, 140], [10, 15], clamp);
  const sec = f < 80 ? a : b;
  const W = 1400, X0 = 260;
  const pop = spring({frame: f - 140, fps, config: {damping: 10}});
  return (
    <AbsoluteFill style={{background: BG, fontFamily: 'P', color: '#fff', opacity: fade}}>
      <Font />
      <div style={{position: 'absolute', top: 120, width: '100%', textAlign: 'center', fontSize: 64}}>한 번에 만드는 영상 길이</div>
      <div style={{position: 'absolute', top: 260, width: '100%', textAlign: 'center', fontSize: 230, color: f < 80 ? '#fff' : ACC,
        textShadow: f < 80 ? 'none' : `0 0 60px ${ACC}88`, transform: `scale(${1 + 0.12 * pop * (f > 140 ? 1 : 0)})`}}>
        {Math.round(sec)}<span style={{fontSize: 110}}>초</span>
      </div>
      <div style={{position: 'absolute', left: X0, top: 640, width: W, height: 90, borderRadius: 20, background: '#231a3d', overflow: 'hidden', display: 'flex'}}>
        {Array.from({length: 15}).map((_, i) => {
          const on = i < sec;
          return <div key={i} style={{flex: 1, margin: 4, borderRadius: 8, background: on ? (i < 10 ? ACC2 : ACC) : 'transparent', opacity: on ? 1 : 0.2,
            border: '2px solid #3a2f5c'}} />;
        })}
      </div>
      <div style={{position: 'absolute', left: X0 + (W * 10) / 15 - 3, top: 610, width: 6, height: 150, background: '#fff', opacity: 0.6}} />
      <div style={{position: 'absolute', left: X0 + (W * 10) / 15 - 150, top: 780, width: 300, textAlign: 'center', fontSize: 42, color: ACC2}}>옴니 1.1 · 10초</div>
      <div style={{position: 'absolute', left: X0 + W - 150, top: 780, width: 300, textAlign: 'center', fontSize: 42, color: ACC, opacity: interpolate(f, [130, 150], [0, 1], clamp)}}>옴니 1.2 · 15초</div>
      <div style={{position: 'absolute', top: 900, width: '100%', textAlign: 'center', fontSize: 40, color: '#b9b0d6'}}>3초부터 15초까지 · 1초 단위로 고르기</div>
    </AbsoluteFill>
  );
};

const TURNS = [
  {g: '🎪', n: '줄무늬 천막'},
  {g: '🌳', n: '참나무 숲'},
  {g: '🐴', n: '마구간'},
  {g: '🧺', n: '시장 축제'},
  {g: '🏰', n: '돌 성'},
];
export const OmniTurns: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const fade = interpolate(f, [0, 10], [0, 1], clamp);
  const idx = Math.min(4, Math.floor(Math.max(0, f - 20) / 45));
  return (
    <AbsoluteFill style={{background: BG, fontFamily: 'P', color: '#fff', opacity: fade}}>
      <Font />
      <div style={{position: 'absolute', top: 70, width: '100%', textAlign: 'center', fontSize: 60}}>말 한마디로 <span style={{color: ACC}}>배경만</span> 바꾸기</div>
      <div style={{position: 'absolute', top: 160, width: '100%', textAlign: 'center', fontSize: 36, color: '#b9b0d6'}}>구글 공식 예시 · 인물 · 갑옷 · 화면 구도는 그대로</div>
      <div style={{position: 'absolute', left: 260, top: 250, width: 900, height: 520, borderRadius: 30, overflow: 'hidden', border: `4px solid ${ACC}`,
        boxShadow: `0 0 60px ${ACC}44`, background: '#1b1430'}}>
        {TURNS.map((t, i) => {
          const p = spring({frame: f - 20 - i * 45, fps, config: {damping: 16}});
          return (
            <div key={i} style={{position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center',
              background: ['#3b2a55', '#173a26', '#3a2d1c', '#4a2a1a', '#2a2f3a'][i], opacity: i === 0 ? 1 : p, transform: `translateX(${(1 - p) * 60}px)`}}>
              <div style={{fontSize: 260, opacity: 0.55}}>{t.g}</div>
            </div>
          );
        })}
        <div style={{position: 'absolute', left: 300, top: 250, fontSize: 170}}>🧍‍♀️</div>
        <div style={{position: 'absolute', left: 470, top: 250, fontSize: 170}}>🧍‍♂️</div>
        <div style={{position: 'absolute', left: 30, bottom: 24, fontSize: 40, padding: '6px 20px', borderRadius: 16, background: '#000a'}}>{`턴 ${idx + 1} · ${TURNS[idx].n}`}</div>
      </div>
      <div style={{position: 'absolute', left: 1220, top: 250, width: 460}}>
        {TURNS.map((t, i) => {
          const p = spring({frame: f - 14 - i * 45, fps, config: {damping: 18}});
          return (
            <div key={i} style={{height: 88, marginBottom: 14, borderRadius: 22, background: i === idx ? '#3a2c10' : '#1d1735',
              border: `3px solid ${i === idx ? ACC : '#3a2f5c'}`, display: 'flex', alignItems: 'center', gap: 18, padding: '0 22px',
              opacity: p, transform: `translateX(${(1 - p) * 40}px)`}}>
              <div style={{fontSize: 46}}>💬</div>
              <div style={{fontSize: 34}}>{i === 0 ? '처음 만든 영상' : `“배경을 ${t.n}으로”`}</div>
            </div>
          );
        })}
      </div>
      <div style={{position: 'absolute', top: 900, width: '100%', textAlign: 'center', fontSize: 44, color: ACC2}}>처음부터 다시 만들지 않고 · <span style={{color: ACC}}>고칠 것만</span> 말로</div>
    </AbsoluteFill>
  );
};

const RES = [
  {r: '360p', s: 0.023, note: '초안용'},
  {r: '720p', s: 0.07, note: '기본'},
  {r: '1080p', s: 0.104, note: '키워서'},
  {r: '4K', s: 0.209, note: '키워서'},
];
export const OmniPrice: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const fade = interpolate(f, [0, 10], [0, 1], clamp);
  const cut = spring({frame: f - 40, fps, config: {damping: 14}});
  return (
    <AbsoluteFill style={{background: BG, fontFamily: 'P', color: '#fff', opacity: fade}}>
      <Font />
      <div style={{position: 'absolute', top: 80, width: '100%', textAlign: 'center', fontSize: 64}}>개발자 API 가격 · <span style={{color: ACC}}>30% 내림</span></div>
      <div style={{position: 'absolute', top: 190, width: '100%', textAlign: 'center', fontSize: 120, color: ACC, textShadow: `0 0 50px ${ACC}88`,
        transform: `scale(${0.7 + 0.3 * cut})`, opacity: cut}}>15초 ≈ 1.04달러</div>
      <div style={{position: 'absolute', top: 350, width: '100%', textAlign: 'center', fontSize: 40, color: '#b9b0d6'}}>720p 기준 · 1초에 약 0.07달러</div>
      {RES.map((x, i) => {
        const p = spring({frame: f - 80 - i * 14, fps, config: {damping: 26}, durationInFrames: 60});
        return (
          <div key={x.r} style={{position: 'absolute', left: 260, top: 460 + i * 120, width: 1400, display: 'flex', alignItems: 'center', gap: 28}}>
            <div style={{width: 170, fontSize: 52, color: i === 1 ? ACC : '#fff'}}>{x.r}</div>
            <div style={{height: 64, width: `${(x.s / 0.209) * 600 * p}px`, borderRadius: 14, background: i === 1 ? ACC : ACC2, opacity: i === 1 ? 1 : 0.75}} />
            <div style={{fontSize: 46, whiteSpace: 'nowrap'}}>{`${(x.s * p).toFixed(3)}달러/초`}</div>
            <div style={{fontSize: 34, color: '#b9b0d6', whiteSpace: 'nowrap'}}>{x.note}</div>
          </div>
        );
      })}
      <div style={{position: 'absolute', top: 960, width: '100%', textAlign: 'center', fontSize: 34, color: '#8f86ad'}}>구글 Gemini API 가격표 · 2026년 11월 기준 · 앱 구독료와는 별개</div>
    </AbsoluteFill>
  );
};
