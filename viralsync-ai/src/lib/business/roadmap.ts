/** 52주 실행 로드맵 (PART 17) + 각 PART 의 ◆실행 항목. key 는 완료 체크 저장용이라 바꾸지 않는다. */
export interface RoadmapItem {
  key: string;
  text: string;
  part: string;
  /** 앱에서 이 일을 하는 화면 */
  href?: string;
}

export interface RoadmapStage {
  title: string;
  weeks: [number, number];
  goal: string;
  items: RoadmapItem[];
}

export const ROADMAP: RoadmapStage[] = [
  {
    title: "1~4주: 준비와 첫 발신",
    weeks: [1, 4],
    goal: "무료 체험 계약 1건",
    items: [
      { key: "w1-assets", text: "통장 잔고·시간·장비 현황을 한 장에 적기", part: "PART 1" },
      { key: "w1-goal", text: "3개월 뒤 월 매출 목표 숫자 정하기", part: "PART 1" },
      { key: "w1-time", text: "매일 사업에 쓸 ‘절대 시간’ 2시간을 캘린더에 예약", part: "PART 1" },
      { key: "w1-idea", text: "위생 검사 4문항에 답하고 내 사업을 한 문장으로 쓰기", part: "PART 2" },
      { key: "w1-industry", text: "집중 업종 1개 고르기 → 그 업종 사장님 5명 계정 표로 정리", part: "PART 2", href: "/sales" },
      { key: "w1-positioning", text: "포지셔닝 한 문장 쓰기", part: "PART 5", href: "/roadmap#settings" },
      { key: "w1-name", text: "이름 후보 5개 → 키프리스(kipris.or.kr) 검색 → 확정", part: "PART 5" },
      { key: "w1-logo", text: "캔바 무료로 텍스트 로고 제작, 모든 채널 같은 색·문구·사진", part: "PART 5" },
      { key: "w1-dummy", text: "내 포트폴리오 계정 개설 후 소개란 세팅 (매일 1개 업로드 시작)", part: "PART 5" },
      { key: "w2-biz", text: "홈택스 사업자등록 (간이과세, 업종코드는 126 에 전화 확인)", part: "PART 4" },
      { key: "w2-accounts", text: "통장 3개 개설: A 사업입금 · B 사업지출 · C 내 월급", part: "PART 10", href: "/finance" },
      { key: "w2-contract", text: "계약서 양식 A4 1장 완성 (7개 조항)", part: "PART 4", href: "/subscriptions" },
      { key: "w2-tools", text: "월 고정 지출 8만 원 한도로 구독 정리, 업무→도구 매핑표", part: "PART 6", href: "/finance" },
      { key: "w2-prompts", text: "자주 쓰는 프롬프트 10개를 메모장에 저장", part: "PART 6" },
      { key: "w2-packages", text: "패키지 표 1장 (가격·포함 내역·납품물)", part: "PART 3", href: "/services" },
      { key: "w2-process", text: "6공정 표 A4 1장 (인터뷰→아이디어 20→시나리오 3→영상→검수→예약 발행)", part: "PART 3" },
      { key: "w3-list", text: "사냥 리스트 100개 작성", part: "PART 7", href: "/sales" },
      { key: "w3-dm20", text: "DM 첫 20통 (하루 10통)", part: "PART 7", href: "/sales" },
      { key: "w3-own7", text: "내 계정 콘텐츠 누적 7개", part: "PART 5" },
      { key: "w4-dm100", text: "DM 총 100통 완료", part: "PART 7", href: "/sales" },
      { key: "w4-mockups", text: "무료 시안 3개 제작", part: "PART 7" },
      { key: "w4-meet", text: "만남 1건 이상", part: "PART 7", href: "/sales" },
      { key: "w4-trial", text: "무료 체험 계약 1건", part: "PART 7", href: "/subscriptions" },
    ],
  },
  {
    title: "5~8주: 첫 유료 전환",
    weeks: [5, 8],
    goal: "첫 유료 계약 1건 (월 29만 원)",
    items: [
      { key: "w5-portfolio", text: "무료 체험 고객 서비스 + 결과를 포트폴리오로 정리", part: "PART 17" },
      { key: "w5-trial2", text: "두 번째 무료 체험 고객 유치", part: "PART 17", href: "/sales" },
      { key: "w6-proposal", text: "제안서 3페이지 템플릿 완성", part: "PART 8", href: "/sales" },
      { key: "w6-objections", text: "반박 스크립트를 휴대폰 메모에 저장", part: "PART 8", href: "/sales" },
      { key: "w6-report", text: "월 보고서 양식 1장 (반 장)", part: "PART 8" },
      { key: "w7-paid1", text: "첫 유료 계약 1건", part: "PART 17", href: "/subscriptions" },
    ],
  },
  {
    title: "9~16주: 반복의 계절",
    weeks: [9, 16],
    goal: "단골 3명 (월 87만 원)",
    items: [
      { key: "w9-dm", text: "DM 하루 10통 유지", part: "PART 7", href: "/sales" },
      { key: "w9-qc", text: "검수 체크리스트를 프린트해 모니터 옆에 부착", part: "PART 9" },
      { key: "w9-bench", text: "벤치마킹 폴더: 매주 잘된 릴스 10개 + ‘잘되는 공식’ 메모 (100개까지)", part: "PART 9" },
      { key: "w9-weekly", text: "월요일 예정표 · 금요일 결과 요약 카톡 루틴", part: "PART 9", href: "/clients" },
      { key: "w9-cashflow", text: "현금흐름표 매월 1일 10분", part: "PART 10", href: "/finance" },
      { key: "w9-tax", text: "세금 예치 통장에 매출 10% 자동이체", part: "PART 10", href: "/finance" },
      { key: "w12-clients3", text: "유료 고객 3명", part: "PART 7", href: "/subscriptions" },
      { key: "w12-failure", text: "나의 실패 신호 3개 정해 두기", part: "PART 16", href: "/dashboard" },
      { key: "w12-strategy", text: "매월 마지막 주 금요일 ‘전략의 날’ (숫자 리뷰 1시간)", part: "PART 16" },
    ],
  },
  {
    title: "17~28주: 단골 5~6명",
    weeks: [17, 28],
    goal: "월 매출 150~350만 원",
    items: [
      { key: "w17-churn", text: "이탈 경고등 체크를 월 보고 시간에 포함", part: "PART 11", href: "/clients" },
      { key: "w17-upsell", text: "매월 기존 고객 1명에게 업셀 제안", part: "PART 11", href: "/clients" },
      { key: "w17-referral", text: "3개월 유지 고객에게 소개 할인 안내 (양쪽 5만 원)", part: "PART 11", href: "/subscriptions" },
      { key: "w20-hate", text: "내가 제일 싫어하는 업무 1개 → 그 매뉴얼부터 쓰기", part: "PART 15" },
      { key: "w20-parttime", text: "첫 아르바이트(편집보조) 검토 — 4대보험·근로계약서 먼저", part: "PART 15" },
      { key: "w20-manuals", text: "업무 매뉴얼 10개 축적", part: "PART 12" },
      { key: "w24-newsletter", text: "투자정보 뉴스레터 무료 견본 3회 발행 실험 (권유 금지)", part: "제2권" },
    ],
  },
  {
    title: "29~40주: 법인 설계",
    weeks: [29, 40],
    goal: "비상금 3개월치",
    items: [
      { key: "w29-corp", text: "월 매출 300만 원 돌파 시 법인 설립 상담 예약", part: "PART 12" },
      { key: "w29-upsell-product", text: "두 번째 사업(기존 고객 대상 업셀 상품) 아이디어 5개", part: "PART 13" },
      { key: "w29-reserve", text: "비상금 3개월 고정비 달성", part: "PART 12", href: "/finance" },
      { key: "w33-boundary", text: "‘권유’와 ‘정보’ 경계 예문 10개 → 전문가 상담 1회", part: "제2권" },
    ],
  },
  {
    title: "41~52주: 분사 결정",
    weeks: [41, 52],
    goal: "분사 조건 3개 확인 (미충족 시 억지 분사 금지)",
    items: [
      { key: "w41-spinoff", text: "분사 조건 3개 확인 (이익 100만+ 3개월, 2주 무인 매뉴얼, 이탈률 10% 미만)", part: "PART 13", href: "/dashboard" },
      { key: "w41-plan", text: "충족 시 두 번째 법인 계획, 미충족 시 첫 회사 강화", part: "PART 13" },
      { key: "w52-review", text: "연간 회고: 뭘 팔았나, 뭘 팔기 싫었나, 내년에 뭘 더 팔까", part: "PART 17" },
    ],
  },
];

export const ROADMAP_KEYS = ROADMAP.flatMap((s) => s.items.map((i) => i.key));

/** 시작일 기준 현재 주차 (1부터) */
export function currentWeek(start: Date | null, now = new Date()): number | null {
  if (!start) return null;
  return Math.max(1, Math.floor((now.getTime() - start.getTime()) / (7 * 86_400_000)) + 1);
}
