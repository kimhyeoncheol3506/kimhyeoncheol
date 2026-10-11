// 채널 후보 목록
// - 채널 ID는 2026-10-11 YouTube 공개 검색 결과 페이지에서 채널명·핸들·구독자 표기를 대조해 확인했다.
//   이름이 같거나 비슷한 사칭·팬 채널(구독자 수 명~수십 명)이 다수 존재하므로 반드시 채널 ID로 식별한다.
// - priorClass(사전 페이스리스 판정)는 운영자의 사전 지식에 근거한 '추정'이다. 영상을 직접 확인하기 전에는
//   어떤 채널도 '페이스리스 확정'으로 표기하지 않는다. 실제 데이터 수집 후 영상별 판정과 사용자 확인으로 갱신한다.

import type { CandidateChannel } from "./types";

export const VERIFIED_AT = "2026-10-11";

export const CANDIDATES: CandidateChannel[] = [
  // ───────── 초기 후보 10개 (요청서 7항) ─────────
  {
    key: "pilot",
    name: "재테크읽어주는 파일럿",
    channelId: "UCaWi2foADm_lKAKnmeQwLSA",
    handle: "@재테크읽어주는파일럿",
    url: "https://www.youtube.com/channel/UCaWi2foADm_lKAKnmeQwLSA",
    verifiedNote: "검색 표기 구독자 128만명 · 동명 유사 채널(구독자 9명·10명·1.1천명) 존재",
    list: "initial",
    priorClass: "E",
    priorReason: "진행자 출연 영상과 내레이션+자료 화면 영상이 섞여 있을 가능성 — 영상별 판정 필요",
    decision: "selected",
    decisionReason: "사용자 선정 우선 분석 후보. 채널 전체가 아니라 얼굴 비노출 영상만 벤치마킹 대상으로 사용",
    userPick: true,
    description:
      "경제·주식·부동산을 내레이션과 자료 화면 중심으로 전달하는 영상이 분석 대상입니다. 채널 전체가 아닌 실제 얼굴 비노출 영상만 골라야 합니다.",
  },
  {
    key: "moneyinside",
    name: "머니인사이드",
    channelId: "UCxfko2YOD6DODYRGzeOPhIQ",
    handle: "@moneyinside7",
    url: "https://www.youtube.com/@moneyinside7",
    verifiedNote: "검색 표기 구독자 217만명 · 별도 '머니인사이드 쇼츠' 채널 존재",
    list: "initial",
    priorClass: "D",
    priorReason: "전문가 출연 인터뷰 중심으로 알려짐 (추정)",
    decision: "excluded",
    decisionReason: "인터뷰 출연자 노출 중심(D 추정) — 페이스리스 재현 적합성 낮음",
    userPick: false,
    description: "전문가 인터뷰형 경제 채널. 주제 선정 참고용으로만 사용합니다.",
  },
  {
    key: "firstecon",
    name: "경제의 시작",
    channelId: "UCzjmNt4AViR0rQpP6n99ZxA",
    handle: "@FirstEcon",
    url: "https://www.youtube.com/@FirstEcon",
    verifiedNote: "검색 표기 구독자 1.32만명",
    list: "initial",
    priorClass: "B",
    priorReason: "경제·기업 이야기를 애니메이션으로 전달 (사용자 확인 자료 기준, 영상별 확인 필요)",
    decision: "selected",
    decisionReason: "사용자 선정 우선 분석 후보. 소규모 채널이라 구독자 대비 성과 분석에 적합",
    userPick: true,
    description:
      "경제·기업 이야기를 애니메이션으로 전달하는 형식. 얼굴 없이 스토리텔링 영상을 제작할 때 참고할 만합니다.",
  },
  {
    key: "jisik",
    name: "지식한입",
    channelId: "UCi9Sl8GnFdYoqEVXnojBPJw",
    handle: "@지식한입",
    url: "https://www.youtube.com/@지식한입",
    verifiedNote: "검색 표기 구독자 147만명 · 유사명 '지식 한입'(1.15천명) 존재",
    list: "initial",
    priorClass: "A",
    priorReason: "내레이션+자료 화면·그래픽 중심의 기업·경제 해설 (추정)",
    decision: "selected",
    decisionReason: "페이스리스 추정(A) · 기업 흥망 스토리텔링 구조 참고",
    userPick: false,
    description: "기업·산업·경제 이슈를 내레이션과 그래픽으로 풀어내는 해설형 채널입니다.",
  },
  {
    key: "talent",
    name: "달란트투자",
    channelId: "UCBM86JVoHLqg9irpR2XKvGw",
    handle: "@talentinvestment",
    url: "https://www.youtube.com/@talentinvestment",
    verifiedNote: "검색 표기 구독자 159만명 · 사칭 의심 채널 다수(달란트투자TV 등)",
    list: "initial",
    priorClass: "D",
    priorReason: "출연자 대담·인터뷰 중심으로 알려짐 (추정)",
    decision: "excluded",
    decisionReason: "출연자 노출 중심(D 추정)",
    userPick: false,
    description: "투자 대담형 채널. 주제 트렌드 참고용.",
  },
  {
    key: "sosumonkey",
    name: "소수몽키",
    channelId: "UCC3yfxS5qC6PCwDzetUuEWg",
    handle: "@sosumonkey",
    url: "https://www.youtube.com/@sosumonkey",
    verifiedNote: "검색 표기 구독자 116만명 · 유사명 채널 다수",
    list: "initial",
    priorClass: "E",
    priorReason: "차트·자료 화면 해설 영상과 출연 영상이 혼재할 가능성 (추정)",
    decision: "selected",
    decisionReason: "혼합형(E) — 얼굴 노출이 적은 차트 해설 영상만 조건부 포함",
    userPick: false,
    description: "미국 주식 중심 해설. 차트·자료 화면 활용 방식 참고.",
  },
  {
    key: "chaeboosim",
    name: "채부심 - 채상욱의 부동산 심부름센터",
    channelId: "UCD9vzSxZ69pjcnf8hgCQXVQ",
    handle: "@chaeboosim",
    url: "https://www.youtube.com/@chaeboosim",
    verifiedNote: "검색 표기 구독자 29.4만명",
    list: "initial",
    priorClass: "D",
    priorReason: "진행자 본인 출연 해설 중심 (추정)",
    decision: "excluded",
    decisionReason: "진행자 노출 중심(D 추정)",
    userPick: false,
    description: "부동산 해설 채널. 부동산 주제 수요 참고용.",
  },
  {
    key: "hsacademy",
    name: "이효석아카데미",
    channelId: "UCxvdCnvGODDyuvnELnLkQWw",
    handle: "@hs_academy",
    url: "https://www.youtube.com/@hs_academy",
    verifiedNote: "검색 표기 구독자 72.1만명 · 동명 사칭 의심 채널 존재",
    list: "initial",
    priorClass: "D",
    priorReason: "진행자 출연 시황·강의형 (추정)",
    decision: "excluded",
    decisionReason: "진행자 노출 중심(D 추정)",
    userPick: false,
    description: "시황·강의형 채널. 거시경제 주제 참고용.",
  },
  {
    key: "moneygraphy",
    name: "머니그라피",
    channelId: "UCwXOKS-z1t9u6Axmm3blXug",
    handle: "@Moneygraphy",
    url: "https://www.youtube.com/@Moneygraphy",
    verifiedNote: "검색 표기 구독자 88.9만명",
    list: "initial",
    priorClass: "D",
    priorReason: "출연진이 등장하는 기획·예능형 경제 콘텐츠 (추정)",
    decision: "excluded",
    decisionReason: "출연자 노출 중심(D 추정)",
    userPick: false,
    description: "기획형 경제 예능. 주제 기획 참고용.",
  },
  {
    key: "hkmarket",
    name: "한경 코리아마켓",
    channelId: "UCGCGxsbmG_9nincyI7xypow",
    handle: "@hk_koreamarket",
    url: "https://www.youtube.com/@hk_koreamarket",
    verifiedNote: "검색 표기 구독자 75.7만명 · 동명 채널(15명) 존재",
    list: "initial",
    priorClass: "D",
    priorReason: "언론사 앵커·출연자 방송형 (추정)",
    decision: "excluded",
    decisionReason: "진행자·출연자 노출 중심(D 추정)",
    userPick: false,
    description: "언론사 시황 채널. 시의성 높은 주제 확인용.",
  },
  // ───────── 교체 후보 (페이스리스 추정 채널) ─────────
  {
    key: "moneycomics",
    name: "머니코믹스",
    channelId: "UCJo6G1u0e_-wS-JQn3T-zEw",
    handle: "@moneymoneycomics",
    url: "https://www.youtube.com/@moneymoneycomics",
    verifiedNote: "검색 표기 구독자 144만명",
    list: "replacement",
    priorClass: "B",
    priorReason: "채널명·검색 결과상 만화·애니메이션 형식 (추정)",
    decision: "selected",
    decisionReason: "애니메이션형 교체 후보 · '경제·기업사 애니메이션 채널' 슬롯 후보",
    userPick: false,
    description: "경제 이야기를 만화·애니메이션으로 전달하는 채널로 추정됩니다. 영상별 확인 필요.",
  },
  {
    key: "manhwaecon",
    name: "만화 경제학",
    channelId: "UCOrRuK7IJq1a7scuEPYIm3w",
    handle: "@만화경제학",
    url: "https://www.youtube.com/@만화경제학",
    verifiedNote: "검색 표기 구독자 9.28만명",
    list: "replacement",
    priorClass: "B",
    priorReason: "'경제 애니메이션' 검색 상위 노출, 채널명상 만화형 (추정)",
    decision: "selected",
    decisionReason: "애니메이션형 교체 후보 · '경제·기업사 애니메이션 채널' 슬롯 후보",
    userPick: false,
    description: "경제 개념을 만화로 설명하는 채널로 추정됩니다.",
  },
  {
    key: "econstory",
    name: "경제스토리",
    channelId: "UCxzIrYFs4aE0QeLwbRloJhg",
    handle: "@economic-story0",
    url: "https://www.youtube.com/@economic-story0",
    verifiedNote: "검색 표기 구독자 5.31만명",
    list: "replacement",
    priorClass: "U",
    priorReason: "'경제 애니메이션' 검색 결과 — 형식 확인 전",
    decision: "pending",
    decisionReason: "제작 방식 확인 필요 · '경제·기업사 애니메이션 채널' 슬롯 후보",
    userPick: false,
    description: "경제 이야기형 채널. 페이스리스 여부 확인 필요.",
  },
  {
    key: "satto",
    name: "사또의 경제 이야기",
    channelId: "UCYTzG803E2YrAXsmc56Jv4g",
    handle: "@ksattoeco",
    url: "https://www.youtube.com/@ksattoeco",
    verifiedNote: "검색 표기 구독자 9.14만명",
    list: "replacement",
    priorClass: "U",
    priorReason: "'기업사 이야기' 검색 결과 — 형식 확인 전",
    decision: "pending",
    decisionReason: "제작 방식 확인 필요",
    userPick: false,
    description: "경제·기업 이야기 채널. 페이스리스 여부 확인 필요.",
  },
  {
    key: "econdetective",
    name: "경제명탐정",
    channelId: "UC1eyYJRpM_g5WBp60mmRwCQ",
    handle: "@경제명탐정",
    url: "https://www.youtube.com/@경제명탐정",
    verifiedNote: "검색 표기 구독자 20만명",
    list: "replacement",
    priorClass: "U",
    priorReason: "'경제의 시작' 유사 검색 결과 — 형식 확인 전",
    decision: "pending",
    decisionReason: "제작 방식 확인 필요",
    userPick: false,
    description: "경제 해설 채널. 페이스리스 여부 확인 필요.",
  },
];

/** 사용자 선정 3번째 슬롯: 실제 채널명 확정 전. 아래 후보 중 하나를 설정 화면에서 지정한다. */
export const SLOT3 = {
  label: "경제·기업사 애니메이션 채널",
  description:
    "기업의 성장과 몰락, 산업 변화를 그래픽으로 설명하는 채널군입니다. 실제 채널명을 확정하기 전 개별 채널 검증이 필요합니다.",
  candidateIds: [
    "UCJo6G1u0e_-wS-JQn3T-zEw", // 머니코믹스
    "UCOrRuK7IJq1a7scuEPYIm3w", // 만화 경제학
    "UCi9Sl8GnFdYoqEVXnojBPJw", // 지식한입
    "UCxzIrYFs4aE0QeLwbRloJhg", // 경제스토리
  ],
};

/** 사용자가 첨부 자료에서 엄선한 정밀 분석 대상 (3번째는 확정 전이므로 null) */
export const USER_PICKS: (string | null)[] = ["UCzjmNt4AViR0rQpP6n99ZxA", "UCaWi2foADm_lKAKnmeQwLSA", null];

/** 최종 선정 10개: 페이스리스 적합성을 1차 필터로 적용 (D 추정 채널 제외, 교체 후보로 보충) */
export function finalSelection(): CandidateChannel[] {
  return CANDIDATES.filter((c) => c.decision !== "excluded").slice(0, 10);
}

export function candidateById(id: string): CandidateChannel | undefined {
  return CANDIDATES.find((c) => c.channelId === id);
}
