// 페이스리스 판정 (간접 근거 기반). API로는 영상 화면을 볼 수 없으므로
// 자동 판정은 최대 '추정' 수준이며, '확정'은 사용자가 영상을 직접 확인해 입력한 경우에만 부여한다.

import type { Confidence, FacelessClass, FacelessJudgement } from "../types";

export const CLASS_LABELS: Record<FacelessClass, string> = {
  A: "A 내레이션+자료 화면",
  B: "B 애니메이션·모션그래픽",
  C: "C 차트·스크린캐스트",
  D: "D 진행자·출연자 노출",
  E: "E 혼합형",
  U: "U 확인 불가",
};

export const CONFIDENCE_LABELS: Record<Confidence, string> = {
  confirmed: "확정(직접 확인)",
  estimated: "추정",
  unverified: "확인 필요",
};

const FACE_SIGNALS = /(인터뷰|출연|게스트|대담|초대석|라이브|LIVE|생방송|방송|토론|강연|브이로그|vlog|직접 만나|모시고|와 함께|님과|교수|대표님|박사님)/i;
const ANIM_SIGNALS = /(애니메이션|animation|animated|모션그래픽|일러스트|만화|코믹|motion)/i;
const CHART_SIGNALS = /(차트|그래프|스크린|화면 공유|HTS|MTS|지표 분석|데이터로 보는)/i;

/**
 * 영상 1개에 대한 간접 판정.
 * - 제목·설명에 출연/인터뷰/라이브 신호 → D 추정
 * - 라이브 방송(진행 중/종료된 라이브) → D 추정
 * - 그 외에는 채널의 사전 판정(prior)을 따르되 확인 수준은 '추정'
 */
export function judgeVideo(
  title: string,
  description: string | null,
  liveContent: "none" | "live" | "upcoming" | "completed",
  prior: FacelessJudgement,
): FacelessJudgement {
  const text = `${title}\n${description ?? ""}`;
  const evidence: string[] = [];
  if (liveContent !== "none") {
    evidence.push("라이브 방송 형식 (API liveBroadcastContent/liveStreamingDetails)");
    return { cls: "D", confidence: "estimated", evidence };
  }
  const face = text.match(FACE_SIGNALS);
  if (face) {
    evidence.push(`제목·설명에 인물 출연 신호 '${face[0]}'`);
    return { cls: prior.cls === "D" ? "D" : "E", confidence: "estimated", evidence };
  }
  const anim = text.match(ANIM_SIGNALS);
  if (anim) evidence.push(`제목·설명에 애니메이션 신호 '${anim[0]}'`);
  const chart = text.match(CHART_SIGNALS);
  if (chart) evidence.push(`제목·설명에 차트 신호 '${chart[0]}'`);
  if (prior.cls === "U") {
    if (anim) return { cls: "B", confidence: "unverified", evidence };
    if (chart) return { cls: "C", confidence: "unverified", evidence };
    return { cls: "U", confidence: "unverified", evidence: [...evidence, "간접 근거 없음"] };
  }
  evidence.push(`채널 사전 판정(${CLASS_LABELS[prior.cls]})을 따름`);
  return { cls: prior.cls, confidence: prior.confidence === "confirmed" ? "estimated" : prior.confidence, evidence };
}

export interface FacelessShare {
  total: number;
  facelessCount: number; // A/B/C
  mixedCount: number; // E
  faceCount: number; // D
  unknownCount: number; // U
  facelessRatio: number | null; // A/B/C ÷ (판정 가능 영상)
  dominant: FacelessClass;
}

export function channelShare(judgements: FacelessJudgement[]): FacelessShare {
  const c = { A: 0, B: 0, C: 0, D: 0, E: 0, U: 0 } as Record<FacelessClass, number>;
  for (const j of judgements) c[j.cls]++;
  const known = judgements.length - c.U;
  const faceless = c.A + c.B + c.C;
  let dominant: FacelessClass = "U";
  let max = 0;
  for (const k of ["A", "B", "C", "E", "D"] as FacelessClass[]) {
    if (c[k] > max) {
      max = c[k];
      dominant = k;
    }
  }
  return {
    total: judgements.length,
    facelessCount: faceless,
    mixedCount: c.E,
    faceCount: c.D,
    unknownCount: c.U,
    facelessRatio: known > 0 ? faceless / known : null,
    dominant,
  };
}

/** 최종 분석 대상 적합 여부: A/B/C 우선, E는 얼굴 노출이 적은 경우(페이스리스 비중 60% 이상)만 */
export function eligibleForBenchmark(cls: FacelessClass, facelessRatio: number | null): boolean {
  if (cls === "A" || cls === "B" || cls === "C") return true;
  if (cls === "E") return facelessRatio != null && facelessRatio >= 0.6;
  return false;
}
