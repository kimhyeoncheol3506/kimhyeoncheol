// 제미나이 4 카본 영상용 클립(2026-11-10). 숫자는 구글 공식 발표 글(2026-10-28)·Gemini API 변경 기록에 있는 것만:
//  CarbonOpen  = 10월 13일 아르곤 → 2주 → 10월 28일 카본, 보안 3시험(88.2 · 54.8 · 71.0%), 자물쇠 '보안 전문가 먼저'
//  CarbonZero  = Terminal-Bench 4.0 성공한 커닝 0.0%(시도 0.4%) · Gray Swan 숨은 명령 아르곤 0.7% → 카본 0.0%
//  CarbonPrice = 소개 가격 아르곤과 같음(입력 2 · 출력 10달러 / 100만 토큰), 소개 기간 뒤 4 · 20달러
// 실제 회사 로고는 그리지 않는다(글자·기호만). 화면 모양: 짙은 초록 #04140F · 민트 #3DF5B0 · 흰색.
import React from 'react';
import {AbsoluteFill, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';

const BG = 'radial-gradient(circle at 50% 38%, #0D3A2B 0%, #04140F 70%)';
const ACC = '#3DF5B0';
const SUB = '#9CC9B6';
const Font = () => <style>{`@font-face{font-family:P;src:url(${staticFile('Pretendard-Black.otf')})}`}</style>;
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

// 떨어지는 빗줄기(영상 look: sky rain 과 맞춤)
const Rain: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <>
      {Array.from({length: 40}).map((_, i) => {
        const x = (i * 211) % 1920, sp = 6 + ((i * 37) % 8), len = 60 + ((i * 53) % 120);
        const y = ((f * sp + i * 97) % (1080 + len)) - len;
        return <div key={i} style={{position: 'absolute', left: x, top: y, width: 2, height: len, background: ACC, opacity: 0.07 + 0.08 * ((i * 13) % 10) / 10}} />;
      })}
    </>
  );
};

const Card: React.FC<{x: number; date: string; name: string; on: number; glow?: boolean}> = ({x, date, name, on, glow}) => (
  <div style={{position: 'absolute', left: x, top: 250, width: 520, height: 300, borderRadius: 32, background: glow ? '#0F3C2D' : '#0A241B',
    border: `4px solid ${glow ? ACC : '#2C5A49'}`, boxShadow: glow ? `0 0 70px ${ACC}55` : 'none', opacity: on, transform: `translateY(${(1 - on) * 50}px)`,
    display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center'}}>
    <div style={{fontSize: 44, color: SUB}}>{date}</div>
    <div style={{fontSize: 96, color: glow ? ACC : '#fff', marginTop: 10}}>{name}</div>
  </div>
);

export const CarbonOpen: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const fade = interpolate(f, [0, 8], [0, 1], clamp);
  const a = spring({frame: f - 6, fps, config: {damping: 16}});
  const arrow = interpolate(f, [30, 55], [0, 1], clamp);
  const b = spring({frame: f - 55, fps, config: {damping: 12}});
  const G = [{k: '찾기', v: 88.2}, {k: '확인', v: 54.8}, {k: '고치기', v: 71.0}];
  const lock = spring({frame: f - 185, fps, config: {damping: 11}});
  return (
    <AbsoluteFill style={{background: BG, fontFamily: 'P', color: '#fff', opacity: fade, overflow: 'hidden'}}>
      <Font />
      <Rain />
      <div style={{position: 'absolute', top: 90, width: '100%', textAlign: 'center', fontSize: 62}}>구글이 <span style={{color: ACC}}>2주 만에</span> 또?</div>
      <Card x={250} date="10월 13일" name="아르곤" on={a} />
      <div style={{position: 'absolute', left: 800, top: 370, width: 320, textAlign: 'center', fontSize: 52, color: ACC, opacity: arrow}}>
        <div>+2주</div>
        <div style={{height: 8, width: `${100 * arrow}%`, margin: '10px auto 0', background: ACC, borderRadius: 4}} />
      </div>
      <Card x={1150} date="10월 28일" name="카본" on={b} glow />
      {G.map((g, i) => {
        const p = interpolate(f, [90 + i * 18, 150 + i * 18], [0, 1], clamp);
        const o = interpolate(f, [85 + i * 18, 100 + i * 18], [0, 1], clamp);
        return (
          <div key={g.k} style={{position: 'absolute', left: 300 + i * 460, top: 620, width: 400, opacity: o}}>
            <div style={{display: 'flex', justifyContent: 'space-between', fontSize: 44}}>
              <span>{g.k}</span><span style={{color: ACC}}>{(g.v * p).toFixed(1)}%</span>
            </div>
            <div style={{marginTop: 14, height: 34, borderRadius: 17, background: '#0E2C22', overflow: 'hidden', border: '2px solid #2C5A49'}}>
              <div style={{height: '100%', width: `${g.v * p}%`, background: `linear-gradient(90deg, ${ACC}, #B8FFE4)`}} />
            </div>
          </div>
        );
      })}
      <div style={{position: 'absolute', top: 760, width: '100%', textAlign: 'center', fontSize: 34, color: SUB, opacity: interpolate(f, [150, 170], [0, 1], clamp)}}>
        보안 시험 3개 · 구글 발표 숫자
      </div>
      <div style={{position: 'absolute', top: 850, width: '100%', textAlign: 'center', opacity: lock, transform: `scale(${0.6 + 0.4 * lock})`}}>
        <span style={{fontSize: 64, padding: '12px 46px 20px', borderRadius: 26, background: '#04140F', border: `5px solid ${ACC}`, boxShadow: `0 0 50px ${ACC}66`}}>
          🔒 아무나 못 쓴다?
        </span>
      </div>
    </AbsoluteFill>
  );
};

const Meter: React.FC<{y: number; label: string; from: number; to: number; start: number; note: string}> = ({y, label, from, to, start, note}) => {
  const f = useCurrentFrame();
  const p = interpolate(f, [start, start + 45], [0, 1], clamp);
  const v = from + (to - from) * p;
  const on = interpolate(f, [start - 15, start], [0, 1], clamp);
  return (
    <div style={{position: 'absolute', left: 260, top: y, width: 1400, opacity: on}}>
      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end'}}>
        <div style={{fontSize: 52}}>{label}</div>
        <div style={{fontSize: 130, color: p >= 1 ? ACC : '#fff', textShadow: p >= 1 ? `0 0 50px ${ACC}88` : 'none', lineHeight: 1}}>{v.toFixed(1)}%</div>
      </div>
      <div style={{marginTop: 18, fontSize: 36, color: SUB}}>{note}</div>
    </div>
  );
};

export const CarbonZero: React.FC = () => {
  const f = useCurrentFrame();
  const fade = interpolate(f, [0, 8], [0, 1], clamp);
  return (
    <AbsoluteFill style={{background: BG, fontFamily: 'P', color: '#fff', opacity: fade, overflow: 'hidden'}}>
      <Font />
      <Rain />
      <div style={{position: 'absolute', top: 90, width: '100%', textAlign: 'center', fontSize: 64}}>꼼수와 공격, <span style={{color: ACC}}>얼마나 줄었을까?</span></div>
      <Meter y={250} label="시험에서 성공한 커닝" from={0} to={0} start={20} note="Terminal-Bench 4.0 · 커닝 시도도 0.4%뿐" />
      <Meter y={560} label="숨은 명령에 넘어간 비율" from={0.7} to={0} start={60} note="Gray Swan 시험 · 아르곤 0.7% → 카본 0.0%" />
      <div style={{position: 'absolute', top: 900, width: '100%', textAlign: 'center', fontSize: 40, color: SUB, opacity: interpolate(f, [110, 130], [0, 1], clamp)}}>
        구글 발표 숫자 · 시험한 범위 안에서
      </div>
    </AbsoluteFill>
  );
};

const Tag: React.FC<{x: number; name: string; on: number; glow?: boolean}> = ({x, name, on, glow}) => (
  <div style={{position: 'absolute', left: x, top: 260, width: 560, height: 380, borderRadius: 34, background: glow ? '#0F3C2D' : '#0A241B',
    border: `4px solid ${glow ? ACC : '#2C5A49'}`, opacity: on, transform: `scale(${0.8 + 0.2 * on})`, textAlign: 'center'}}>
    <div style={{fontSize: 64, marginTop: 34, color: glow ? ACC : '#fff'}}>{name}</div>
    <div style={{fontSize: 46, marginTop: 40}}>넣을 때 <span style={{fontSize: 80, color: ACC}}>2달러</span></div>
    <div style={{fontSize: 46, marginTop: 14}}>받을 때 <span style={{fontSize: 80, color: ACC}}>10달러</span></div>
  </div>
);

export const CarbonPrice: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const fade = interpolate(f, [0, 8], [0, 1], clamp);
  const a = spring({frame: f - 6, fps, config: {damping: 16}});
  const b = spring({frame: f - 30, fps, config: {damping: 14}});
  const eq = spring({frame: f - 55, fps, config: {damping: 9}});
  const later = interpolate(f, [100, 125], [0, 1], clamp);
  return (
    <AbsoluteFill style={{background: BG, fontFamily: 'P', color: '#fff', opacity: fade, overflow: 'hidden'}}>
      <Font />
      <Rain />
      <div style={{position: 'absolute', top: 100, width: '100%', textAlign: 'center', fontSize: 62}}>개발자용 소개 가격 · <span style={{color: ACC}}>100만 토큰당</span></div>
      <Tag x={290} name="아르곤" on={a} />
      <div style={{position: 'absolute', left: 860, top: 370, width: 200, textAlign: 'center', fontSize: 170, color: ACC, opacity: eq, transform: `scale(${eq})`}}>=</div>
      <Tag x={1070} name="카본" on={b} glow />
      <div style={{position: 'absolute', top: 720, width: '100%', textAlign: 'center', opacity: later, transform: `translateY(${(1 - later) * 30}px)`}}>
        <span style={{fontSize: 52, padding: '12px 40px 20px', borderRadius: 24, background: '#0A241B', border: '3px solid #2C5A49'}}>
          소개 기간이 끝나면 → <span style={{color: ACC}}>4달러 · 20달러</span>
        </span>
      </div>
      <div style={{position: 'absolute', top: 880, width: '100%', textAlign: 'center', fontSize: 38, color: SUB, opacity: later}}>구글 발표 글 기준 · 카본 소개 기간 끝나는 날은 미발표</div>
    </AbsoluteFill>
  );
};
