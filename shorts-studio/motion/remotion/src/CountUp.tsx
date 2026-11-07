import React from 'react';
import {AbsoluteFill, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig, Easing} from 'remotion';

// 숫자 카운트업 인포그래픽: "순자산 8억", "밥값 8만원대" 같은 금액·비율을 강조할 때.
export const countUpSchema = {
  label: '순자산',
  value: 800000000,
  unit: '원',
  caption: '30대 중반 비혼 여자',
  accent: '#FFD23F',
  bg1: '#1b1430',
  bg2: '#3a1f5c',
};
type Props = typeof countUpSchema;

const fontFace = `
@font-face{font-family:'BlackHan';src:url('${staticFile('BlackHanSans-Regular.ttf')}');}
@font-face{font-family:'Pretendard';src:url('${staticFile('Pretendard-ExtraBold.otf')}');}`;

// 한국식 금액 표기: 800000000 → 8억 / 14000000 → 1400만
const won = (n: number) => {
  const eok = Math.floor(n / 1e8);
  const man = Math.floor((n % 1e8) / 1e4);
  if (eok && man) return `${eok}억 ${man.toLocaleString()}만`;
  if (eok) return `${eok}억`;
  if (man) return `${man.toLocaleString()}만`;
  return n.toLocaleString();
};

export const CountUp: React.FC<Props> = ({label, value, unit, caption, accent, bg1, bg2}) => {
  const frame = useCurrentFrame();
  const {fps, durationInFrames} = useVideoConfig();
  const pop = spring({frame, fps, config: {damping: 12}});
  const p = interpolate(frame, [10, 75], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  const shown = Math.round(value * p);
  const capIn = interpolate(frame, [80, 95], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const out = interpolate(frame, [durationInFrames - 10, durationInFrames], [1, 0], {extrapolateLeft: 'clamp'});
  const bar = interpolate(frame, [10, 75], [0, 860], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  return (
    <AbsoluteFill style={{background: `linear-gradient(160deg, ${bg1}, ${bg2})`, opacity: out, alignItems: 'center', justifyContent: 'center'}}>
      <style>{fontFace}</style>
      <div style={{fontFamily: 'Pretendard', color: '#fff', fontSize: 84, opacity: pop, marginBottom: 30}}>{label}</div>
      <div style={{fontFamily: 'BlackHan', color: accent, fontSize: 230, transform: `scale(${0.6 + 0.4 * pop})`, textShadow: '0 12px 0 rgba(0,0,0,.35)'}}>
        {won(shown)}{unit}
      </div>
      <div style={{width: 860, height: 26, borderRadius: 13, background: 'rgba(255,255,255,.15)', marginTop: 50}}>
        <div style={{width: bar, height: 26, borderRadius: 13, background: accent}} />
      </div>
      <div style={{fontFamily: 'Pretendard', color: '#fff', fontSize: 64, marginTop: 70, opacity: capIn, transform: `translateY(${(1 - capIn) * 30}px)`}}>{caption}</div>
    </AbsoluteFill>
  );
};
