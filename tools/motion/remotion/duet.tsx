// 클로드 듀엣 영상용 클립(2026-11-10, 일꾼C). 숫자는 쓰지 않는다(예시 화면). 실제 로고는 그리지 않는다(글자·기호 타일만).
//  DuetBrief = 아침에 AI가 먼저 말을 거는 브리핑(콜드 오픈, 제품 페이지 '아침 브리핑' 설명)
//  DuetCheck = 몇 시간마다 연결 앱을 살피고 필요할 때만 연락(발표 글 'every few hours')
//  DuetGuard = 승인 카드(받는 사람·내용·보낼 곳) + 일하는 AI 바깥의 별도 검사기(안전 글)
import React from 'react';
import {AbsoluteFill, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';

const BG = 'radial-gradient(circle at 50% 30%, #1A2340 0%, #0A0F1E 70%)';
const ACC = '#E8E8FF';
const RED = '#FF4F6D';
const DIM = '#8A90A8';
const Font = () => <style>{`@font-face{font-family:P;src:url(${staticFile('Pretendard-Black.otf')})}`}</style>;
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const useFade = () => interpolate(useCurrentFrame(), [0, 10], [0, 1], clamp);

const Stars: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <>
      {Array.from({length: 40}).map((_, i) => {
        const x = (i * 337) % 1920, y = (i * 191) % 1080;
        const o = 0.25 + 0.25 * Math.sin(f / 9 + i);
        return <div key={i} style={{position: 'absolute', left: x, top: y, width: 4, height: 4, borderRadius: 2, background: ACC, opacity: o}} />;
      })}
    </>
  );
};

const BRIEF = [
  {g: '📌', t: '오후 미팅 자료, 초안 준비했어요', s: '확인 필요', red: true},
  {g: '✉️', t: '거래처 답장 초안을 써 뒀어요', s: '확인 필요', red: true},
  {g: '🧾', t: '청구서 정리는 진행 중이에요', s: '알려만 드려요', red: false},
];
export const DuetBrief: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const fade = useFade();
  const phone = spring({frame: f, fps, config: {damping: 18}});
  const glow = 0.5 + 0.5 * Math.sin(f / 7);
  return (
    <AbsoluteFill style={{background: BG, fontFamily: 'P', color: '#fff', opacity: fade}}>
      <Font />
      <Stars />
      <div style={{position: 'absolute', left: 130, top: 260, width: 760, fontSize: 96, lineHeight: 1.22}}>
        AI가 <span style={{color: RED}}>먼저</span><br />말을 걸어요
        <div style={{fontSize: 46, color: '#B9C0DA', marginTop: 44}}>예시 화면 · 클로드 듀엣 아침 브리핑</div>
      </div>
      <div style={{position: 'absolute', left: 1020, top: 70, width: 620, height: 940, borderRadius: 70, border: '6px solid #3A4466',
        background: '#0F1530', transform: `translateX(${(1 - phone) * 500}px) rotate(${(1 - phone) * 8}deg)`, boxShadow: `0 0 90px ${RED}22`}}>
        <div style={{textAlign: 'center', marginTop: 70, fontSize: 70, color: ACC}}>좋은 아침이에요</div>
        <div style={{textAlign: 'center', fontSize: 34, color: '#9AA3C4', marginTop: 10}}>오늘 꼭 챙길 일 · 두 가지</div>
        {BRIEF.map((n, i) => {
          const p = spring({frame: f - 35 - i * 32, fps, config: {damping: 14}});
          return (
            <div key={i} style={{position: 'absolute', left: 30, top: 300 + i * 170, width: 560, height: 145, borderRadius: 30,
              background: n.red ? 'rgba(255,79,109,0.13)' : 'rgba(232,232,255,0.08)', border: `3px solid ${n.red ? RED : '#3A4466'}`,
              display: 'flex', alignItems: 'center', gap: 22, padding: '0 24px', boxSizing: 'border-box',
              opacity: p, transform: `translateX(${(1 - p) * 120}px)`}}>
              <div style={{fontSize: 58}}>{n.g}</div>
              <div>
                <div style={{fontSize: 32}}>{n.t}</div>
                <div style={{fontSize: 27, color: n.red ? RED : '#9AA3C4', marginTop: 6}}>듀엣 · {n.s}</div>
              </div>
            </div>
          );
        })}
        <div style={{position: 'absolute', left: 230, top: 840, width: 160, height: 12, borderRadius: 6, background: ACC, opacity: 0.4 + 0.4 * glow}} />
      </div>
    </AbsoluteFill>
  );
};

const APPS = [
  {g: '✉️', n: '메일'},
  {g: '⏰', n: '캘린더'},
  {g: '💬', n: '메신저'},
  {g: '🧾', n: '회계'},
  {g: '🛒', n: '가게'},
  {g: '📁', n: '문서'},
];
export const DuetCheck: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const fade = useFade();
  const sweep = interpolate(f, [20, 150], [0, 360], clamp);       // 한 바퀴 = 한 번 살펴보기
  const R = 330, cx = 960, cy = 590;
  const lit = Math.floor(sweep / 60);                              // 지나간 앱 수
  const alert = spring({frame: f - 160, fps, config: {damping: 12}});
  return (
    <AbsoluteFill style={{background: BG, fontFamily: 'P', color: '#fff', opacity: fade}}>
      <Font />
      <Stars />
      <div style={{position: 'absolute', top: 60, width: '100%', textAlign: 'center', fontSize: 66}}>
        <span style={{color: ACC}}>몇 시간마다</span> 한 번씩 살펴보기
      </div>
      <svg width={1920} height={1080} style={{position: 'absolute', left: 0, top: 0}}>
        <circle cx={cx} cy={cy} r={R} fill="none" stroke="#2A3356" strokeWidth={10} strokeDasharray="6 22" />
        <path d={`M ${cx} ${cy} L ${cx + R * Math.sin((sweep * Math.PI) / 180)} ${cy - R * Math.cos((sweep * Math.PI) / 180)}`} stroke={ACC} strokeWidth={8} strokeLinecap="round" opacity={sweep < 360 ? 0.9 : 0.25} />
      </svg>
      <div style={{position: 'absolute', left: cx - 120, top: cy - 120, width: 240, height: 240, borderRadius: 120, background: '#141B38',
        border: `5px solid ${ACC}`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 50, color: ACC}}>듀엣</div>
      {APPS.map((a, i) => {
        const ang = (i * 60 + 30) * (Math.PI / 180);
        const on = i < lit;
        const x = cx + R * Math.sin(ang), y = cy - R * Math.cos(ang);
        return (
          <div key={i} style={{position: 'absolute', left: x - 90, top: y - 70, width: 180, height: 140, borderRadius: 28,
            background: on ? '#1F2A50' : '#121833', border: `4px solid ${on ? ACC : '#2A3356'}`, display: 'flex', flexDirection: 'column',
            alignItems: 'center', justifyContent: 'center'}}>
            <div style={{fontSize: 52}}>{a.g}</div>
            <div style={{fontSize: 32, color: on ? '#fff' : DIM}}>{a.n} {on ? '✓' : ''}</div>
          </div>
        );
      })}
      <div style={{position: 'absolute', left: 1290, top: 250 - alert * 40, width: 600, padding: '24px 30px', borderRadius: 30, background: RED,
        boxSizing: 'border-box', opacity: alert, boxShadow: `0 0 60px ${RED}88`}}>
        <div style={{fontSize: 38, whiteSpace: 'nowrap'}}>🔔 꼭 보셔야 할 일이 생겼어요</div>
        <div style={{fontSize: 30, color: '#FFE4EA', marginTop: 6}}>필요할 때만 연락해요</div>
      </div>
      <div style={{position: 'absolute', left: 70, top: 250, fontSize: 36, color: '#9AA3C4', opacity: alert}}>나머지는 조용히 · 예시 화면</div>
    </AbsoluteFill>
  );
};

const ROWS = [
  {k: '받는 사람', v: '거래처 담당자 · 참조 한 명'},
  {k: '보낼 곳', v: '내 회사 메일 계정'},
  {k: '내용', v: '견적서와 다음 일정 안내'},
];
export const DuetGuard: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const fade = useFade();
  const card = spring({frame: f - 5, fps, config: {damping: 16}});
  const scan = interpolate(f, [95, 165], [0, 1], clamp);
  const ok = spring({frame: f - 170, fps, config: {damping: 12}});
  const tap = spring({frame: f - 215, fps, config: {damping: 10}});
  return (
    <AbsoluteFill style={{background: BG, fontFamily: 'P', color: '#fff', opacity: fade}}>
      <Font />
      <Stars />
      <div style={{position: 'absolute', top: 60, width: '100%', textAlign: 'center', fontSize: 64}}>
        보내기 전에 <span style={{color: RED}}>멈추고 보여 주기</span>
      </div>
      <div style={{position: 'absolute', left: 170, top: 210, width: 900, height: 700, borderRadius: 44, background: '#121A36', border: `4px solid ${ACC}`,
        transform: `scale(${0.8 + 0.2 * card})`, opacity: card, boxSizing: 'border-box', padding: '40px 50px'}}>
        <div style={{fontSize: 54, color: ACC}}>✋ 승인 요청 · 메일 보내기</div>
        {ROWS.map((r, i) => {
          const p = spring({frame: f - 25 - i * 22, fps, config: {damping: 16}});
          return (
            <div key={i} style={{marginTop: 34, display: 'flex', gap: 30, opacity: p, transform: `translateX(${(1 - p) * -60}px)`}}>
              <div style={{width: 200, fontSize: 40, color: RED}}>{r.k}</div>
              <div style={{fontSize: 40}}>{r.v}</div>
            </div>
          );
        })}
        <div style={{position: 'absolute', left: 50, bottom: 50, display: 'flex', gap: 30}}>
          <div style={{width: 330, height: 110, borderRadius: 55, background: RED, display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: 50, transform: `scale(${1 - 0.08 * tap})`, boxShadow: tap > 0.5 ? `0 0 60px ${RED}` : 'none'}}>{tap > 0.5 ? '승인됨 ✓' : '승인'}</div>
          <div style={{width: 330, height: 110, borderRadius: 55, border: `4px solid ${DIM}`, display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: 50, color: DIM}}>나중에</div>
        </div>
      </div>
      <div style={{position: 'absolute', left: 1180, top: 300, width: 580, height: 520, borderRadius: 44, border: `4px dashed ${DIM}`, boxSizing: 'border-box',
        display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', opacity: interpolate(f, [70, 95], [0, 1], clamp)}}>
        <div style={{fontSize: 130}}>🛡</div>
        <div style={{fontSize: 46, marginTop: 10}}>따로 떨어진 검사기</div>
        <div style={{fontSize: 34, color: '#9AA3C4', marginTop: 8}}>일하는 AI 바깥에서</div>
        <div style={{width: 420, height: 18, borderRadius: 9, background: '#2A3356', marginTop: 34}}>
          <div style={{width: `${100 * scan}%`, height: '100%', borderRadius: 9, background: ACC}} />
        </div>
        <div style={{fontSize: 40, marginTop: 24, color: ok > 0.5 ? ACC : DIM, opacity: Math.max(ok, 0.001)}}>내 뜻과 맞아요 ✓</div>
      </div>
      <svg width={1920} height={1080} style={{position: 'absolute', left: 0, top: 0}}>
        <line x1={1075} y1={560} x2={1175} y2={560} stroke={ACC} strokeWidth={6} strokeDasharray="12 10" opacity={scan > 0 ? 0.8 : 0} />
      </svg>
    </AbsoluteFill>
  );
};
