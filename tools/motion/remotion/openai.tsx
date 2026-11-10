// GPT-6.1 테라 영상용 클립(2026-11-10, 일꾼F). 숫자는 오픈에이아이 공식 문서(learn.chatgpt.com)에 있는 것만:
//  TerraOpen  = 콜드 오픈: 눈(이미지 읽기)이 화면을 훑고, 커서(손)가 버튼을 누르고, 글이 써진다 → "GPT-6.1 테라"
//  TerraLook  = 공식 예시 다시 그림: 거래처 상품 사진 4장 ↔ 상품 목록 4줄을 선으로 짝짓고 '정보 갱신'
//  TerraPrice = API 가격 막대(100만 토큰당): 입력 2→1달러, 출력 12→5달러 (5.6 테라 → 6.1 테라)
// 실제 회사 로고는 그리지 않는다(이름 글자만). 날짜 글자·이모지 없음(헤드리스 크롬 글꼴 문제 피하기).
import React from 'react';
import {AbsoluteFill, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';

const BG = 'radial-gradient(ellipse at 50% 20%, #0E3440 0%, #06141B 65%)';
const TEAL = '#22D3EE';
const YEL = '#FDE68A';
const DIM = '#7A8C99';
const Font = () => <style>{`@font-face{font-family:P;src:url(${staticFile('Pretendard-Black.otf')})}`}</style>;
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

const Aurora: React.FC<{f: number}> = ({f}) => (
  <svg width={1920} height={1080} style={{position: 'absolute', inset: 0, opacity: 0.55}}>
    <defs>
      <linearGradient id="au" x1="0" x2="1">
        <stop offset="0" stopColor={TEAL} stopOpacity="0" />
        <stop offset="0.5" stopColor={TEAL} stopOpacity="0.35" />
        <stop offset="1" stopColor={YEL} stopOpacity="0" />
      </linearGradient>
    </defs>
    {[0, 1, 2].map((i) => (
      <path key={i} fill="url(#au)"
        d={`M0 ${200 + i * 70} C 480 ${120 + i * 60 + 40 * Math.sin(f / 30 + i)}, 1440 ${300 + i * 50 - 40 * Math.cos(f / 25 + i)}, 1920 ${180 + i * 80} L1920 ${260 + i * 80} C 1440 ${380 + i * 50}, 480 ${200 + i * 60}, 0 ${280 + i * 70} Z`} />
    ))}
  </svg>
);

// 눈 모양(SVG)
const Eye: React.FC<{x: number; y: number; s: number; look: number}> = ({x, y, s, look}) => (
  <svg width={220} height={140} style={{position: 'absolute', left: x - 110, top: y - 70, transform: `scale(${s})`}}>
    <path d="M10 70 Q110 -10 210 70 Q110 150 10 70 Z" fill="#06141B" stroke={TEAL} strokeWidth={8} />
    <circle cx={110 + look * 40} cy={70} r={30} fill={TEAL} />
    <circle cx={110 + look * 40} cy={70} r={12} fill="#06141B" />
  </svg>
);

// 커서(손 대신 화살표)
const Cursor: React.FC<{x: number; y: number; press: number}> = ({x, y, press}) => (
  <svg width={80} height={100} style={{position: 'absolute', left: x, top: y, transform: `scale(${1 - 0.15 * press})`}}>
    <path d="M6 4 L6 78 L26 60 L40 92 L54 86 L40 54 L68 54 Z" fill={YEL} stroke="#06141B" strokeWidth={5} />
  </svg>
);

// ── 1. 콜드 오픈
export const TerraOpen: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const fade = interpolate(f, [0, 10], [0, 1], clamp);
  const win = spring({frame: f - 4, fps, config: {damping: 16}});
  const scan = interpolate(f, [20, 80], [0, 1], clamp);           // 눈이 화면을 훑음
  const look = Math.sin(f / 9) * (f < 90 ? 1 : 0.2);
  const cx = interpolate(f, [80, 120], [1500, 1060], clamp);       // 커서가 버튼으로
  const cy = interpolate(f, [80, 120], [820, 640], clamp);
  const press = interpolate(f, [120, 126, 134], [0, 1, 0], clamp);
  const done = f > 128;
  const typed = Math.floor(interpolate(f, [135, 185], [0, 18], clamp));
  const text = '결과부터 쉬운 말로 정리했어요'.slice(0, typed);
  const title = spring({frame: f - 175, fps, config: {damping: 12}});
  const W0 = 520, H0 = 230, WW = 880, WH = 520;
  return (
    <AbsoluteFill style={{background: BG, fontFamily: 'P', color: '#fff', opacity: fade}}>
      <Font />
      <Aurora f={f} />
      {/* 앱 화면 */}
      <div style={{position: 'absolute', left: W0, top: H0, width: WW, height: WH, borderRadius: 28, background: 'rgba(10,40,50,.85)',
        border: `4px solid ${TEAL}`, boxShadow: `0 0 60px ${TEAL}44`, transform: `scale(${0.85 + 0.15 * win})`, opacity: win}}>
        <div style={{height: 56, borderBottom: `3px solid ${TEAL}55`, display: 'flex', alignItems: 'center', paddingLeft: 24, gap: 14}}>
          {[0, 1, 2].map((i) => <div key={i} style={{width: 18, height: 18, borderRadius: 9, background: i === 0 ? YEL : DIM}} />)}
          <div style={{marginLeft: 20, fontSize: 30, color: '#bfe9f2'}}>상품 관리</div>
        </div>
        {[0, 1, 2].map((i) => (
          <div key={i} style={{position: 'absolute', left: 40 + i * 270, top: 90, width: 240, height: 170, borderRadius: 18, background: '#0B2A33',
            border: `3px solid ${scan * 3 > i ? YEL : '#1d4a55'}`}}>
            <div style={{position: 'absolute', left: 70, top: 35, width: 100, height: 100, borderRadius: i === 1 ? 50 : 16, background: [TEAL, YEL, '#7DD3C0'][i], opacity: 0.85}} />
          </div>
        ))}
        {[0, 1].map((i) => (
          <div key={i} style={{position: 'absolute', left: 40, top: 300 + i * 50, width: 520 - i * 140, height: 22, borderRadius: 11, background: '#1d4a55'}} />
        ))}
        <div style={{position: 'absolute', left: 560, top: 400, width: 260, height: 76, borderRadius: 38, background: done ? YEL : TEAL,
          color: '#06141B', fontSize: 36, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>{done ? '갱신 완료' : '정보 갱신'}</div>
        <div style={{position: 'absolute', left: 40, top: 410, fontSize: 32, color: YEL}}>{text}</div>
      </div>
      {/* 스캔 선 */}
      <div style={{position: 'absolute', left: W0, top: H0 + 60 + scan * (WH - 80), width: WW, height: 6, background: TEAL,
        boxShadow: `0 0 30px ${TEAL}`, opacity: scan > 0 && scan < 1 ? 0.9 : 0}} />
      <Eye x={360} y={420} s={0.6 + 0.4 * win} look={look} />
      <div style={{position: 'absolute', left: 250, top: 510, width: 220, textAlign: 'center', fontSize: 40, color: TEAL, opacity: win}}>보고</div>
      <Cursor x={cx} y={cy} press={press} />
      <div style={{position: 'absolute', left: 1490, top: 600, width: 220, textAlign: 'center', fontSize: 40, color: YEL, opacity: interpolate(f, [80, 100], [0, 1], clamp)}}>누르고</div>
      <div style={{position: 'absolute', left: 560, top: 790, width: 300, fontSize: 40, color: '#fff', opacity: interpolate(f, [135, 150], [0, 1], clamp)}}>쓰고</div>
      {/* 제목 */}
      <div style={{position: 'absolute', top: 70, width: '100%', textAlign: 'center', opacity: title, transform: `translateY(${(1 - title) * -40}px)`}}>
        <span style={{fontSize: 96, color: '#fff', textShadow: '0 6px 0 #000'}}>GPT-6.1 </span>
        <span style={{fontSize: 96, color: TEAL, textShadow: `0 0 40px ${TEAL}aa, 0 6px 0 #000`}}>테라</span>
      </div>
      <div style={{position: 'absolute', top: 850, width: '100%', textAlign: 'center', fontSize: 50, color: YEL, opacity: title}}>
        보고 · 누르고 · 쓰는 새 모델
      </div>
    </AbsoluteFill>
  );
};

// ── 2. 사진 ↔ 목록 맞추기
const PHOTOS = [
  {shape: 'shoe', c: TEAL, row: 2},
  {shape: 'bag', c: YEL, row: 0},
  {shape: 'cup', c: '#7DD3C0', row: 3},
  {shape: 'cap', c: '#F9A8D4', row: 1},
];
const ROWS = ['가죽 가방 · 노랑', '야구 모자 · 분홍', '운동화 · 하늘색', '머그컵 · 민트'];
const Shape: React.FC<{k: string; c: string}> = ({k, c}) => (
  <svg width={150} height={110} viewBox="0 0 150 110">
    {k === 'shoe' && <path d="M15 80 L15 45 Q40 40 60 55 Q95 70 135 72 L135 90 L15 90 Z" fill={c} />}
    {k === 'bag' && <><rect x="30" y="40" width="90" height="60" rx="10" fill={c} /><path d="M50 42 Q75 0 100 42" stroke={c} strokeWidth="9" fill="none" /></>}
    {k === 'cup' && <><rect x="40" y="25" width="60" height="70" rx="8" fill={c} /><path d="M100 40 Q128 50 100 78" stroke={c} strokeWidth="9" fill="none" /></>}
    {k === 'cap' && <><path d="M30 75 Q35 25 80 25 Q122 25 122 75 Z" fill={c} /><rect x="70" y="70" width="70" height="12" rx="6" fill={c} /></>}
  </svg>
);
export const TerraLook: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const fade = interpolate(f, [0, 10], [0, 1], clamp);
  const PX = 330, RX = 1060, Y = (i: number) => 260 + i * 170;
  return (
    <AbsoluteFill style={{background: BG, fontFamily: 'P', color: '#fff', opacity: fade}}>
      <Font />
      <Aurora f={f} />
      <div style={{position: 'absolute', top: 60, width: '100%', textAlign: 'center', fontSize: 60}}>
        거래처 사진 <span style={{color: TEAL}}>↔</span> <span style={{color: YEL}}>상품 목록</span> 맞추기
      </div>
      <div style={{position: 'absolute', top: 150, width: '100%', textAlign: 'center', fontSize: 34, color: '#9fc6cf'}}>오픈AI 공식 예시를 다시 그림</div>
      {PHOTOS.map((p, i) => {
        const a = spring({frame: f - 10 - i * 8, fps, config: {damping: 14}});
        return (
          <div key={i} style={{position: 'absolute', left: PX, top: Y(i) - 70, width: 220, height: 140, borderRadius: 20, background: '#0B2A33',
            border: `4px solid ${p.c}`, display: 'flex', alignItems: 'center', justifyContent: 'center', opacity: a, transform: `translateX(${(1 - a) * -80}px)`}}>
            <Shape k={p.shape} c={p.c} />
          </div>
        );
      })}
      {ROWS.map((r, i) => {
        const a = spring({frame: f - 20 - i * 8, fps, config: {damping: 14}});
        const matched = PHOTOS.findIndex((p) => p.row === i);
        const ok = f > 80 + matched * 28 + 22;
        return (
          <div key={i} style={{position: 'absolute', left: RX, top: Y(i) - 55, width: 560, height: 110, borderRadius: 20,
            background: ok ? 'rgba(253,230,138,.15)' : 'rgba(255,255,255,.06)', border: `4px solid ${ok ? YEL : '#2b5560'}`,
            display: 'flex', alignItems: 'center', paddingLeft: 30, fontSize: 42, opacity: a, transform: `translateX(${(1 - a) * 80}px)`}}>
            {r}
            <span style={{marginLeft: 'auto', marginRight: 30, fontSize: 44, color: YEL, opacity: ok ? 1 : 0}}>✓</span>
          </div>
        );
      })}
      <svg width={1920} height={1080} style={{position: 'absolute', inset: 0}}>
        {PHOTOS.map((p, i) => {
          const t = interpolate(f, [80 + i * 28, 102 + i * 28], [0, 1], clamp);
          const x1 = PX + 230, y1 = Y(i), x2 = RX - 10, y2 = Y(p.row);
          const len = Math.hypot(x2 - x1, y2 - y1) + 60;
          return <path key={i} d={`M ${x1} ${y1} C ${x1 + 150} ${y1}, ${x2 - 150} ${y2}, ${x2} ${y2}`} fill="none" stroke={p.c} strokeWidth={8}
            strokeLinecap="round" strokeDasharray={len} strokeDashoffset={len * (1 - t)} />;
        })}
      </svg>
      <div style={{position: 'absolute', top: 865, width: '100%', textAlign: 'center', fontSize: 48, color: YEL,
        opacity: interpolate(f, [200, 215], [0, 1], clamp)}}>짝지은 뒤 [ 정보 갱신 ]</div>
    </AbsoluteFill>
  );
};

// ── 3. 가격 막대(5.6 테라 → 6.1 테라)
export const TerraPrice: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const fade = interpolate(f, [0, 10], [0, 1], clamp);
  const drop = spring({frame: f - 50, fps, config: {damping: 16}, durationInFrames: 60});
  const UNIT = 40;                      // 1달러 = 40px
  const groups = [
    {k: '입력', old: 2, now: 1, x: 520},
    {k: '출력', old: 12, now: 5, x: 1140},
  ];
  const BASE = 780;
  return (
    <AbsoluteFill style={{background: BG, fontFamily: 'P', color: '#fff', opacity: fade}}>
      <Font />
      <Aurora f={f} />
      <div style={{position: 'absolute', top: 60, width: '100%', textAlign: 'center', fontSize: 62}}>
        <span style={{color: DIM}}>5.6 테라</span> → <span style={{color: TEAL}}>6.1 테라</span>
      </div>
      <div style={{position: 'absolute', top: 150, width: '100%', textAlign: 'center', fontSize: 34, color: '#9fc6cf'}}>100만 토큰당 · 오픈AI API 가격표</div>
      <div style={{position: 'absolute', left: 340, top: BASE, width: 1240, height: 6, background: '#2b5560'}} />
      {groups.map((g, gi) => {
        const hOld = g.old * UNIT;
        const hNow = (g.old + (g.now - g.old) * drop) * UNIT;
        const val = g.old + (g.now - g.old) * drop;
        return (
          <React.Fragment key={gi}>
            {/* 예전 막대(흐린 테두리) */}
            <div style={{position: 'absolute', left: g.x, top: BASE - hOld, width: 150, height: hOld, borderRadius: '16px 16px 0 0',
              border: `4px dashed ${DIM}`, boxSizing: 'border-box'}} />
            <div style={{position: 'absolute', left: g.x - 40, top: BASE - hOld - 70, width: 230, textAlign: 'center', fontSize: 44, color: DIM}}>{g.old}달러</div>
            {/* 새 막대 */}
            <div style={{position: 'absolute', left: g.x + 190, top: BASE - hNow, width: 150, height: hNow, borderRadius: '16px 16px 0 0',
              background: `linear-gradient(180deg, ${TEAL}, #0E7490)`, boxShadow: `0 0 40px ${TEAL}66`}} />
            <div style={{position: 'absolute', left: g.x + 150, top: BASE - hNow - 80, width: 230, textAlign: 'center', fontSize: 58, color: TEAL}}>
              {Number.isInteger(Math.round(val * 10) / 10) ? Math.round(val) : val.toFixed(1)}달러
            </div>
            <div style={{position: 'absolute', left: g.x - 20, top: BASE + 24, width: 380, textAlign: 'center', fontSize: 48}}>{g.k}</div>
          </React.Fragment>
        );
      })}
      <div style={{position: 'absolute', left: 1480, top: 330, width: 400, textAlign: 'center', fontSize: 60, color: YEL, textShadow: '0 4px 0 #000', zIndex: 5,
        opacity: interpolate(f, [110, 125], [0, 1], clamp), transform: 'rotate(-4deg)'}}>
        입력은 절반<br />출력은<br />절반보다 더
      </div>
    </AbsoluteFill>
  );
};
