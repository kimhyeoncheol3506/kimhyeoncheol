// Remotion 시험 장면(5초): 숫자가 올라가는 인포그래픽. 글꼴은 --public-dir ../../assets/fonts 의 Pretendard.
import React from 'react';
import {AbsoluteFill, Composition, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';

const Counter: React.FC<{to: number; label: string; sub: string}> = ({to, label, sub}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const p = spring({frame: f - 10, fps, config: {damping: 200}, durationInFrames: 70});
  const bar = spring({frame: f - 40, fps, config: {damping: 14}});
  const fade = interpolate(f, [0, 12], [0, 1], {extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{background: 'radial-gradient(circle at 50% 40%, #2A0820, #10050E 70%)', fontFamily: 'P', color: '#fff', opacity: fade}}>
      <style>{`@font-face{font-family:P;src:url(${staticFile('Pretendard-Black.otf')})}`}</style>
      <div style={{position: 'absolute', top: 160, width: '100%', textAlign: 'center', fontSize: 64, color: '#FFB3DA'}}>{label}</div>
      <div style={{position: 'absolute', top: 300, width: '100%', textAlign: 'center', fontSize: 260, color: '#FF4FB0', textShadow: '0 0 60px #FF4FB088'}}>
        {(to * p).toFixed(1)}<span style={{fontSize: 120, color: '#fff'}}>배</span>
      </div>
      <div style={{position: 'absolute', left: 360, top: 700, width: 1200, height: 40, borderRadius: 20, background: '#2a2030'}}>
        <div style={{width: `${100 * bar}%`, height: '100%', borderRadius: 20, background: 'linear-gradient(90deg,#FF4FB0,#FFB3DA)'}} />
      </div>
      <div style={{position: 'absolute', top: 790, width: '100%', textAlign: 'center', fontSize: 48, color: '#ccc'}}>{sub}</div>
    </AbsoluteFill>
  );
};

export const Root: React.FC = () => (
  <Composition id="CounterDemo" component={Counter} durationInFrames={150} fps={30} width={1920} height={1080}
    defaultProps={{to: 444.6, label: '회사가 말한 비용 차이', sub: '회사 자체 평가 · 좋은 쪽 숫자'}} />
);
