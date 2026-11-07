import React from 'react';
import {AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig, staticFile} from 'remotion';

// neogul-edit 규칙집 색(R-L2, R-L6): 다크 #181614, 상승 빨강, 결론 노랑
const C = {bg: '#181614', text: '#FFFFFF', muted: '#A39D94', red: '#F2262B', yellow: '#E3C04B', bar: '#5A5752'};
const font = `@font-face{font-family:P;src:url(${staticFile('Pretendard-ExtraBold.otf')});font-weight:900}`;

type Props = {title: string; from: number; to: number; unit: string; bars: {label: string; value: number}[]};

export const CounterBars: React.FC<Props> = ({title, from, to, unit, bars}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const n = Math.round(interpolate(f, [10, 70], [from, to], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}));
  const max = Math.max(...bars.map((b) => b.value));
  return (
    <AbsoluteFill style={{background: C.bg, fontFamily: 'P', color: C.text, padding: 96}}>
      <style>{font}</style>
      <div style={{fontSize: 68, fontWeight: 900}}>{title}</div>
      <div style={{fontSize: 200, fontWeight: 900, color: C.red, marginTop: 30}}>
        {n.toLocaleString('ko-KR')}<span style={{fontSize: 80}}>{unit}</span>
      </div>
      <div style={{display: 'flex', alignItems: 'flex-end', gap: 60, height: 380, marginTop: 20}}>
        {bars.map((b, i) => {
          const s = spring({frame: f - 60 - i * 8, fps, config: {damping: 14}});
          const last = i === bars.length - 1;
          return (
            <div key={b.label} style={{flex: 1, textAlign: 'center'}}>
              <div style={{fontSize: 40, fontWeight: 900, opacity: s, color: last ? C.yellow : C.text}}>{b.value.toLocaleString('ko-KR')}</div>
              <div style={{height: (300 * b.value / max) * s, background: last ? C.red : C.bar, borderRadius: 8, marginTop: 10}} />
              <div style={{fontSize: 34, color: C.muted, marginTop: 14}}>{b.label}</div>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
