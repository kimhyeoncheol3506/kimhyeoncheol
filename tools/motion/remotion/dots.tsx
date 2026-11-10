// 챗GPT 닷츠 영상용 클립(2026-11-10). 사실은 오픈에이아이 공식 도움말(learn.chatgpt.com)·요금 안내에 있는 것만:
//  DotsNight  = 콜드 오픈: 밤에 나는 자고(컴퓨터 꺼짐) 닷츠는 클라우드에서 일함 → 아침 알림 "정할 것 1개"(예시 화면)
//  DotsPlans  = 요금제별 닷츠: Free·Go·Plus 없음, Pro 100·200·500달러에만 있음
//  DotsReview = 자동 검토 3갈래: 그냥 진행 · 승인 요청 · 사람에게 넘김(비밀번호 바꾸기)
// 실제 로고는 그리지 않는다(주황 동그라미 캐릭터는 직접 그린 것).
import React from 'react';
import {AbsoluteFill, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';

const BG = 'radial-gradient(circle at 50% 38%, #3A1C06 0%, #140A04 72%)';
const ACC = '#FF8A1F';
const ACC2 = '#FFE0B0';
const MUTE = '#9C8A78';
const Font = () => <style>{`@font-face{font-family:P;src:url(${staticFile('Pretendard-Black.otf')})}`}</style>;
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

// 주황 동그라미 닷(눈 두 개) — 직접 그린 캐릭터
const Dot: React.FC<{size: number; blink?: number; glow?: number}> = ({size, blink = 1, glow = 1}) => (
  <div style={{width: size, height: size, borderRadius: '50%', background: `radial-gradient(circle at 35% 30%, #FFC27A, ${ACC} 55%, #C25A00)`,
    boxShadow: `0 0 ${80 * glow}px ${ACC}aa`, position: 'relative'}}>
    {[0.34, 0.6].map((x, i) => (
      <div key={i} style={{position: 'absolute', left: size * x, top: size * 0.38, width: size * 0.1, height: size * 0.16 * blink, borderRadius: size,
        background: '#2A1404', transform: `translateY(${(1 - blink) * size * 0.06}px)`}} />
    ))}
  </div>
);

const TASKS = ['장소 견적 비교', '참석 인원 갱신', '메일 초안 작성', '마감 일정 확인'];
export const DotsNight: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const fade = interpolate(f, [0, 10], [0, 1], clamp);
  const hour = interpolate(f, [15, 170], [23, 31], clamp); // 밤 11시 → 아침 7시
  const h = Math.floor(hour) % 24;
  const night = interpolate(f, [150, 185], [1, 0], clamp);
  const pop = spring({frame: f - 185, fps, config: {damping: 12}});
  const blink = f % 60 < 4 ? 0.2 : 1;
  return (
    <AbsoluteFill style={{background: BG, fontFamily: 'P', color: '#fff', opacity: fade}}>
      <Font />
      <div style={{position: 'absolute', inset: 0, background: `linear-gradient(180deg, rgba(10,6,30,${0.65 * night}), transparent)`}} />
      {/* 왼쪽: 나 */}
      <div style={{position: 'absolute', left: 150, top: 150, width: 640, height: 640, borderRadius: 40, background: '#1F1208', border: `3px solid ${MUTE}55`}}>
        <div style={{position: 'absolute', top: 30, width: '100%', textAlign: 'center', fontSize: 52, color: ACC2}}>나</div>
        <div style={{position: 'absolute', top: 150, width: '100%', textAlign: 'center', fontSize: 210}}>{night > 0.5 ? '😴' : '🙂'}</div>
        <div style={{position: 'absolute', top: 420, width: '100%', textAlign: 'center', fontSize: 46, color: MUTE}}>
          {night > 0.5 ? '💻 내 컴퓨터 꺼짐' : '☀ 일어났어요'}
        </div>
        <div style={{position: 'absolute', top: 30, right: 40, fontSize: 70, opacity: night}}>🌙</div>
      </div>
      {/* 가운데 시계 */}
      <div style={{position: 'absolute', left: 810, top: 400, width: 300, textAlign: 'center'}}>
        <div style={{fontSize: 40, color: MUTE}}>{h < 12 && h >= 5 ? '오전' : h >= 12 ? '오후' : '밤'}</div>
        <div style={{fontSize: 110, color: ACC2}}>{`${h === 0 ? 12 : h > 12 ? h - 12 : h}시`}</div>
      </div>
      {/* 오른쪽: 닷츠(클라우드) */}
      <div style={{position: 'absolute', left: 1130, top: 150, width: 640, height: 640, borderRadius: 40, background: '#2A1606', border: `4px solid ${ACC}`, boxShadow: `0 0 60px ${ACC}44`}}>
        <div style={{position: 'absolute', top: 30, width: '100%', textAlign: 'center', fontSize: 52, color: ACC}}>☁ 내 닷츠 · 클라우드</div>
        <div style={{position: 'absolute', left: 40, top: 130}}><Dot size={150} blink={blink} /></div>
        <div style={{position: 'absolute', left: 220, top: 125, width: 390}}>
          {TASKS.map((t, i) => {
            const on = interpolate(f, [30 + i * 35, 45 + i * 35], [0, 1], clamp);
            return (
              <div key={i} style={{fontSize: 40, margin: '14px 0', opacity: 0.25 + 0.75 * on, color: on > 0.9 ? '#fff' : MUTE}}>
                <span style={{color: ACC, marginRight: 14}}>{on > 0.9 ? '✓' : '…'}</span>{t}
              </div>
            );
          })}
        </div>
        <div style={{position: 'absolute', bottom: 40, width: '100%', textAlign: 'center', fontSize: 40, color: ACC2}}>내가 자는 동안에도 계속</div>
      </div>
      {/* 아침 알림 */}
      <div style={{position: 'absolute', left: 560, top: 830, width: 800, padding: '26px 40px', borderRadius: 30, background: '#FFF4E6', color: '#2A1404',
        fontSize: 46, opacity: pop, transform: `translateY(${(1 - pop) * 80}px) scale(${0.9 + 0.1 * pop})`, boxShadow: `0 20px 60px #000a`, textAlign: 'center'}}>
        🟠 <b style={{color: '#C25A00'}}>정할 것 1개</b> · 견적 메일, 보낼까요?
      </div>
      <div style={{position: 'absolute', right: 40, bottom: 22, fontSize: 28, color: MUTE}}>예시 화면</div>
    </AbsoluteFill>
  );
};

const PLANS = [
  {n: 'Free', p: '0달러', on: false},
  {n: 'Go', p: '', on: false},
  {n: 'Plus', p: '', on: false},
  {n: 'Pro', p: '100 · 200 · 500달러', on: true},
];
export const DotsPlans: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const fade = interpolate(f, [0, 10], [0, 1], clamp);
  return (
    <AbsoluteFill style={{background: BG, fontFamily: 'P', color: '#fff', opacity: fade}}>
      <Font />
      <div style={{position: 'absolute', top: 90, width: '100%', textAlign: 'center', fontSize: 66}}>요금제별 <span style={{color: ACC}}>닷츠</span> 있나요?</div>
      <div style={{position: 'absolute', top: 185, width: '100%', textAlign: 'center', fontSize: 36, color: MUTE}}>챗GPT 요금 안내 비교표 기준 · 2026년 11월</div>
      <div style={{position: 'absolute', left: 170, top: 290, width: 1580, display: 'flex', gap: 40}}>
        {PLANS.map((p, i) => {
          const s = spring({frame: f - 15 - i * 22, fps, config: {damping: 14}});
          const mark = spring({frame: f - 40 - i * 22, fps, config: {damping: 9}});
          return (
            <div key={i} style={{flex: p.on ? 1.6 : 1, height: 520, borderRadius: 34, background: p.on ? '#3A1C06' : '#1F1208',
              border: p.on ? `5px solid ${ACC}` : `3px solid ${MUTE}55`, boxShadow: p.on ? `0 0 70px ${ACC}66` : 'none',
              opacity: s, transform: `translateY(${(1 - s) * 60}px)`, position: 'relative', textAlign: 'center'}}>
              <div style={{marginTop: 50, fontSize: 70, color: p.on ? ACC : '#fff'}}>{p.n}</div>
              <div style={{marginTop: 50, fontSize: 170, transform: `scale(${mark})`, color: p.on ? ACC : MUTE}}>{p.on ? '✓' : '✕'}</div>
              <div style={{position: 'absolute', bottom: 50, width: '100%', fontSize: p.on ? 44 : 38, color: p.on ? ACC2 : MUTE}}>
                {p.on ? '월 100 · 200 · 500달러' : '닷츠 없음'}
              </div>
            </div>
          );
        })}
      </div>
      <div style={{position: 'absolute', top: 880, width: '100%', textAlign: 'center', fontSize: 50, color: ACC2,
        opacity: interpolate(f, [130, 150], [0, 1], clamp)}}>닷츠는 <span style={{color: ACC}}>프로 요금제부터</span></div>
    </AbsoluteFill>
  );
};

const WAYS = [
  {g: '▶', t: '그냥 진행', s: '허락된 범위 안', c: ACC2},
  {g: '✋', t: '승인 요청', s: '예: 메일 보내기 전', c: ACC},
  {g: '🙋', t: '사람에게 넘김', s: '예: 비밀번호 바꾸기', c: '#FF5A36'},
];
export const DotsReview: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const fade = interpolate(f, [0, 10], [0, 1], clamp);
  const move = interpolate(f, [15, 60], [0, 1], clamp);
  const scan = (f % 40) / 40;
  return (
    <AbsoluteFill style={{background: BG, fontFamily: 'P', color: '#fff', opacity: fade}}>
      <Font />
      <div style={{position: 'absolute', top: 70, width: '100%', textAlign: 'center', fontSize: 64}}>행동하기 전에 <span style={{color: ACC}}>자동 검토</span></div>
      {/* 행동 카드 */}
      <div style={{position: 'absolute', left: 120 + 260 * move, top: 420, width: 330, padding: '30px 20px', borderRadius: 26, background: '#2A1606',
        border: `3px solid ${ACC2}88`, textAlign: 'center', fontSize: 44}}>
        📤 하려는 행동<div style={{fontSize: 32, color: MUTE, marginTop: 10}}>계정 · 정보 나누기</div>
      </div>
      {/* 검문소 */}
      <div style={{position: 'absolute', left: 760, top: 280, width: 330, height: 480, borderRadius: 34, background: '#1F1208', border: `5px solid ${ACC}`,
        boxShadow: `0 0 70px ${ACC}55`, overflow: 'hidden', textAlign: 'center'}}>
        <div style={{position: 'absolute', left: 0, right: 0, top: 480 * scan - 20, height: 40, background: `linear-gradient(180deg,transparent,${ACC}66,transparent)`}} />
        <div style={{margin: '70px auto 10px', width: 120, height: 140, background: `linear-gradient(180deg, ${ACC2}, ${ACC})`,
          clipPath: 'polygon(50% 0, 100% 15%, 100% 55%, 50% 100%, 0 55%, 0 15%)', display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: 80, color: '#2A1404'}}>✓</div>
        <div style={{fontSize: 52, color: ACC}}>자동 검토</div>
        <div style={{fontSize: 32, color: ACC2, marginTop: 20, lineHeight: 1.5}}>내 지시 · 맞춤 규칙<br />기본 안전 규칙</div>
      </div>
      {/* 세 갈래 */}
      {WAYS.map((w, i) => {
        const s = spring({frame: f - 75 - i * 35, fps, config: {damping: 13}});
        return (
          <div key={i} style={{position: 'absolute', left: 1180, top: 250 + i * 190, width: 620, height: 160, borderRadius: 26, background: '#2A1606',
            border: `4px solid ${w.c}`, opacity: s, transform: `translateX(${(1 - s) * 80}px)`, display: 'flex', alignItems: 'center'}}>
            <div style={{width: 130, textAlign: 'center', fontSize: 80}}>{w.g}</div>
            <div>
              <div style={{fontSize: 54, color: w.c}}>{w.t}</div>
              <div style={{fontSize: 34, color: MUTE}}>{w.s}</div>
            </div>
          </div>
        );
      })}
      <div style={{position: 'absolute', top: 905, width: '100%', textAlign: 'center', fontSize: 40, color: ACC2,
        opacity: interpolate(f, [190, 210], [0, 1], clamp)}}>닷츠는 필요한 검사를 <span style={{color: ACC}}>스스로 끌 수 없어요</span></div>
    </AbsoluteFill>
  );
};
