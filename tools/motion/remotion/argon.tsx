// 제미나이 아르곤 영상용 클립(2026-11-07). 숫자는 출처 facts 에 있는 것만:
//  가격 = ai.google.dev 가격표(11/30까지 2·10달러 → 12/1부터 4·20달러), 경주 = 김경원의 AI 자체 테스트(레고 모션그래픽).
import React from 'react';
import {AbsoluteFill, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';

const BG = 'radial-gradient(circle at 50% 35%, #12305E 0%, #071226 70%)';
const Font = () => <style>{`@font-face{font-family:P;src:url(${staticFile('Pretendard-Black.otf')})}`}</style>;

export const ArgonPrice: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const flip = spring({frame: f - 75, fps, config: {damping: 12}});
  const fade = interpolate(f, [0, 10], [0, 1], {extrapolateRight: 'clamp'});
  const row = (label: string, a: number, b: number, y: number, d: number) => {
    const p = spring({frame: f - 75 - d, fps, config: {damping: 14}});
    const v = a + (b - a) * p;
    return (
      <div style={{position: 'absolute', left: 300, top: y, width: 1320, display: 'flex', alignItems: 'center', gap: 40}}>
        <div style={{width: 300, fontSize: 64, color: '#9FC4FF'}}>{label}</div>
        <div style={{fontSize: 150, color: p > 0.5 ? '#FFD54F' : '#fff', textShadow: p > 0.5 ? '0 0 50px #FFD54F99' : 'none', width: 520}}>${v.toFixed(0)}</div>
        <div style={{fontSize: 56, color: '#ccd'}}>/ 100만 토큰</div>
      </div>
    );
  };
  return (
    <AbsoluteFill style={{background: BG, fontFamily: 'P', color: '#fff', opacity: fade}}>
      <Font />
      <div style={{position: 'absolute', top: 110, width: '100%', textAlign: 'center', fontSize: 70}}>API 가격, <span style={{color: '#FFD54F'}}>12월 1일부터 두 배</span></div>
      <div style={{position: 'absolute', top: 230, width: '100%', textAlign: 'center', fontSize: 52, color: '#9FC4FF'}}>
        {flip < 0.5 ? '11월 30일까지' : '12월 1일부터'}
      </div>
      {row('입력', 2, 4, 360, 0)}
      {row('출력', 10, 20, 590, 8)}
      <div style={{position: 'absolute', top: 880, width: '100%', textAlign: 'center', fontSize: 44, color: '#aab'}}>개발자용 API 기준 · 제미나이 앱 구독료 이야기가 아니에요</div>
    </AbsoluteFill>
  );
};

const RACE = [
  {name: '클로드 오퍼스 5.5', min: 79, usd: 19.66, color: '#FF8A3D'},
  {name: 'GPT-6.1 솔', min: 19, usd: 0.85, color: '#7CF7B0'},
  {name: '제미나이 4 아르곤', min: 40, usd: 1.68, color: '#5AB0FF'},
];
export const ArgonRace: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const fade = interpolate(f, [0, 10], [0, 1], {extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{background: BG, fontFamily: 'P', color: '#fff', opacity: fade}}>
      <Font />
      <div style={{position: 'absolute', top: 90, width: '100%', textAlign: 'center', fontSize: 64}}>같은 숙제 · <span style={{color: '#FFD54F'}}>레고 모션그래픽</span></div>
      <div style={{position: 'absolute', top: 180, width: '100%', textAlign: 'center', fontSize: 40, color: '#9FC4FF'}}>한 유튜버의 자체 테스트 · 한 번씩 실행</div>
      {RACE.map((r, i) => {
        const p = spring({frame: f - 20 - i * 6, fps, config: {damping: 30}, durationInFrames: 90});
        const c = spring({frame: f - 120 - i * 8, fps, config: {damping: 14}});
        return (
          <div key={r.name} style={{position: 'absolute', left: 160, top: 300 + i * 200, width: 1600}}>
            <div style={{fontSize: 48, marginBottom: 14}}>{r.name}</div>
            <div style={{display: 'flex', alignItems: 'center', gap: 30}}>
              <div style={{height: 70, width: `${(r.min / 79) * 1100 * p}px`, borderRadius: 14, background: r.color, boxShadow: `0 0 30px ${r.color}88`}} />
              <div style={{fontSize: 64}}>{Math.round(r.min * p)}분</div>
              <div style={{fontSize: 52, color: '#FFD54F', opacity: c, transform: `scale(${0.6 + 0.4 * c})`}}>{r.usd.toFixed(2)}달러</div>
            </div>
          </div>
        );
      })}
    </AbsoluteFill>
  );
};
