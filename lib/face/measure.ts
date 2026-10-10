// MediaPipe Face Landmarker 의 얼굴 점(랜드마크)으로 관상에 쓰는 비율을 잰다.
// 얼굴이 기울어져 있어도 같은 값이 나오도록, 턱→이마 축을 기준으로 좌표를 회전시켜서 잰다.

export type Pt = { x: number; y: number };

export type FaceMetrics = {
  upper: number; // 이마(상정) 비율
  middle: number; // 눈썹~코끝(중정) 비율
  lower: number; // 코끝~턱(하정) 비율
  foreheadWidth: number; // 이마 너비 / 얼굴 너비
  eyeSize: number; // 눈 길이 / 얼굴 너비
  eyeOpen: number; // 눈 세로 / 눈 길이
  eyeGap: number; // 눈 사이 간격 / 눈 길이
  eyeTilt: number; // 눈꼬리 각도(도), +면 올라감
  noseWidth: number; // 콧방울 너비 / 얼굴 너비
  noseLength: number; // 콧대 길이 / 얼굴 높이
  mouthWidth: number; // 입 너비 / 얼굴 너비
  lipThickness: number; // 입술 두께 / 얼굴 높이
  mouthCurve: number; // 입꼬리 높이 / 얼굴 높이, +면 올라감
  jawWidth: number; // 턱 너비 / 얼굴 너비
  cheekbone: number; // 광대 돌출 정도
  chinLength: number; // 턱 길이 / 얼굴 높이
};

// MediaPipe 얼굴 메시 인덱스
const I = {
  top: 10, chin: 152, glabella: 9, noseBottom: 2, bridge: 168,
  faceL: 234, faceR: 454, foreL: 103, foreR: 332, jawL: 172, jawR: 397,
  rOut: 33, rIn: 133, rUp: 159, rLow: 145, lIn: 362, lOut: 263, lUp: 386, lLow: 374,
  alaL: 64, alaR: 294, mouthL: 61, mouthR: 291, lipTop: 0, lipBottom: 17, lipInUp: 13, lipInLow: 14,
};

/** 점 목록(이미지 좌표, y는 아래로 증가)을 받아 얼굴 비율을 계산 */
export function measureFace(points: Pt[]): FaceMetrics {
  // 얼굴 축: 턱 → 이마 방향을 '위'로 잡는다
  const c = points[I.chin];
  const t = points[I.top];
  const ux = t.x - c.x;
  const uy = t.y - c.y;
  const ul = Math.hypot(ux, uy);
  const up = { x: ux / ul, y: uy / ul };
  const right = { x: -up.y, y: up.x };
  const P = (i: number) => {
    const p = points[i];
    const dx = p.x - c.x;
    const dy = p.y - c.y;
    return { x: dx * right.x + dy * right.y, y: dx * up.x + dy * up.y }; // y: 위로 +
  };
  const d = (a: number, b: number) => {
    const p = P(a);
    const q = P(b);
    return Math.hypot(p.x - q.x, p.y - q.y);
  };

  const faceH = d(I.top, I.chin);
  const faceW = d(I.faceL, I.faceR);
  const upperH = P(I.top).y - P(I.glabella).y;
  const middleH = P(I.glabella).y - P(I.noseBottom).y;
  const lowerH = P(I.noseBottom).y - P(I.chin).y;
  const sum = upperH + middleH + lowerH;

  const eyeW = (d(I.rOut, I.rIn) + d(I.lIn, I.lOut)) / 2;
  const eyeH = (d(I.rUp, I.rLow) + d(I.lUp, I.lLow)) / 2;

  // 눈꼬리 각도: 안쪽 눈머리 → 바깥 눈꼬리가 위로 향하면 +
  const tilt = (inner: number, outer: number) => {
    const a = P(inner);
    const b = P(outer);
    return (Math.atan2(b.y - a.y, Math.abs(b.x - a.x)) * 180) / Math.PI;
  };
  const eyeTilt = (tilt(I.rIn, I.rOut) + tilt(I.lIn, I.lOut)) / 2;

  const cornersY = (P(I.mouthL).y + P(I.mouthR).y) / 2;
  const centerY = (P(I.lipInUp).y + P(I.lipInLow).y) / 2;

  const foreW = d(I.foreL, I.foreR);
  const jawW = d(I.jawL, I.jawR);

  return {
    upper: upperH / sum,
    middle: middleH / sum,
    lower: lowerH / sum,
    foreheadWidth: foreW / faceW,
    eyeSize: eyeW / faceW,
    eyeOpen: eyeH / eyeW,
    eyeGap: d(I.rIn, I.lIn) / eyeW,
    eyeTilt,
    noseWidth: d(I.alaL, I.alaR) / faceW,
    noseLength: d(I.bridge, I.noseBottom) / faceH,
    mouthWidth: d(I.mouthL, I.mouthR) / faceW,
    lipThickness: d(I.lipTop, I.lipBottom) / faceH,
    mouthCurve: (cornersY - centerY) / faceH,
    jawWidth: jawW / faceW,
    cheekbone: faceW / ((foreW + jawW) / 2),
    chinLength: d(I.lipBottom, I.chin) / faceH,
  };
}
