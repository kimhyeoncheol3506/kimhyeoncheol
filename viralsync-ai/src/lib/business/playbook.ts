/**
 * 사업 실행 백과(제1권 마케팅 에이전시)의 규칙을 코드로 옮긴 것.
 * 금액·기간은 책의 대략치이며, 실제 운영 전 세무사·노무사 등에게 최신 수치를 확인한다.
 */

/** 첫 페르소나 업종 (PART 2-3) — 캡틴 결정: 네일샵부터 집중 */
export const TARGET_INDUSTRIES = ["네일샵", "미용실", "카페", "학원", "PT샵"] as const;
export const DEFAULT_TARGET_INDUSTRY = "네일샵";

/** 포지셔닝 한 문장 (PART 5-1) — 캡틴 결정: 책 문장 그대로 */
export const DEFAULT_POSITIONING = "동네 사장님들을 위한, AI로 빠르고 저렴한 SNS 운영 파트너";

/** 월 정액 패키지 (PART 3-1, 8-2 소량 패키지) */
export const MONTHLY_PLANS = [
  { name: "소량 (릴스 4편)", monthlyFee: 150_000, deliverables: ["인스타 릴스 4편"], note: "29만 원이 부담될 때 양을 줄여 시작 (가격은 깎지 않음)" },
  { name: "라이트", monthlyFee: 290_000, deliverables: ["인스타 릴스 8편", "게시물 4개"], note: "사장님은 사진만 전송" },
  { name: "스탠다드", monthlyFee: 590_000, deliverables: ["인스타 릴스 8편", "게시물 4개", "카카오 채널 관리", "월 1회 리포트 통화 30분"], note: "라이트 + 카카오 채널" },
  { name: "프리미엄", monthlyFee: 990_000, deliverables: ["인스타 릴스 8편", "게시물 4개", "카카오 채널 관리", "월 1회 리포트 통화 30분", "블로그·네이버 플레이스 등록 대행", "이벤트 기획 1건"], note: "스탠다드 + 블로그·플레이스·이벤트" },
] as const;

/** 조건부 무료 체험 (PART 3-4) */
export const TRIAL = { days: 14, firstMonthDiscount: 50, freeSlots: 3 };

/** 업셀·교차판매 (PART 11-2) */
export const UPSELLS = [
  { name: "카카오 채널 자동응답 세팅", price: "월 +15만 원" },
  { name: "네이버 플레이스 사진 촬영", price: "건별 20만 원" },
];

/** 추천 프로그램 (PART 11-3): 소개한 쪽·소개받은 쪽 각 한 달 할인 */
export const REFERRAL_DISCOUNT = 50_000;

/** 돈 관리 원칙 (PART 6-1, 10, 12-1) */
export const MONEY = {
  fixedCostLimit: 80_000, // 월 고정 지출(도구) 한도
  taxReservePct: 10, // 매출의 10% 세금 예치
  salaryCapPct: 50, // 내 월급은 월 매출의 50% 이하
  reserveMonths: 3, // 비상금 = 고정비 3개월치
  dangerMonths: 2, // 잔고가 고정비 2개월치 미만이면 위험
  suspendAfterMissed: 2, // 미납 2회 → 서비스 중지
  salaryFastTarget: 1_500_000, // 월급 150만 원까지는 빨리 올리기
};

/** 단골 목표 단계 (PART 7-3) */
export const CLIENT_GOALS = [3, 6, 10];

/** 검수 체크리스트 — 올리기 전 필수 7개 (PART 9-1) */
export const QC_CHECKLIST = [
  { key: "typo", label: "가게 이름·가격·전화번호 오타 확인" },
  { key: "competitor", label: "경쟁 가게 이름·상표가 배경에 잘못 나오지 않음" },
  { key: "ai_artifact", label: "AI 생성 특유의 기형(손가락·글자 왜곡) 없음" },
  { key: "owner_ok", label: "사장님 승인 없이 올리지 않음 (승인 예정 포함)" },
  { key: "music", label: "음악은 유료 음원 라이브러리 또는 무료 라이선스 곡만" },
  { key: "tags", label: "해시태그·위치태그(플레이스 연동) 입력" },
  { key: "timing", label: "예약 시간이 손님 시간대(점심·저녁 전)" },
] as const;
export const QC_KEYS = QC_CHECKLIST.map((c) => c.key);

/** 반박 대응 스크립트 (PART 8-3) */
export const OBJECTIONS = [
  { q: "AI가 만든 영상이라 티 나지 않아요?", a: "시안 단계에서 사장님이 직접 보고 고르십니다. 올라가는 건 사장님이 승인한 것만 올라갑니다." },
  { q: "우리 애가 하고 있어요", a: "그럼 제가 받아서 올리는 걸 도와드리는 방식도 가능해요. 방향은 사장님이 잡고 저는 손발이 되는 겁니다." },
  { q: "효과가 있을까요?", a: "솔직히 한 달로는 모릅니다. 그래서 2주 무료로 해 보고, 사장님이 ‘이건 되겠다’ 싶을 때 결정하시면 됩니다." },
  { q: "가격이 부담돼요", a: "가격은 그대로 두고 양을 줄여 드릴게요. 월 15만 원에 릴스 4편으로 시작해 보시겠어요?" },
  { q: "AI 쓰시는 거예요?", a: "네, AI 보조 도구로 시안을 빠르게 만들고, 사람이 하나하나 검수합니다. 올라가는 건 사장님 승인한 것만입니다." },
];

/** 고객 인터뷰 질문 (PART 7-4, 부록 D-3) */
export const INTERVIEW_QUESTIONS = [
  "가게에서 제일 많이 팔리는 건 무엇인가요?",
  "주로 어떤 손님이 오시나요? (나이·동네·시간대)",
  "손님이 가장 많이 칭찬하는 점은요?",
  "사장님이 꼭 자랑하고 싶은 것은요?",
  "근처 비슷한 가게와 다른 점은요?",
  "손님이 제일 많은 요일·시간대는요?",
  "지금 SNS 에서 가장 아쉬운 점은요?",
  "올리면 안 되는 것(얼굴·가격·메뉴 등)이 있나요?",
  "이번 달 알리고 싶은 행사·신메뉴가 있나요?",
  "사진·영상을 보내 주실 수 있는 시간대는요?",
];

/** 진단형 첫 DM (PART 7-2, 부록 B) — 사람이 직접 보내는 초안 */
export function dmDraft(p: { name: string; industry?: string; lastPostAt?: Date | null; postsPerMonth?: number | null }, positioning = ""): string {
  const gap =
    p.lastPostAt && Date.now() - p.lastPostAt.getTime() > 60 * 86_400_000
      ? "최근 몇 달 업로드가 멈춰 있어서 아쉬웠어요."
      : p.postsPerMonth != null && p.postsPerMonth < 4
        ? "업로드가 한 달에 몇 개뿐이라 아쉬웠어요."
        : "릴스가 조금만 더 있으면 좋겠다 싶었어요.";
  return [
    `${p.name} 사장님 안녕하세요, 동네에서 SNS 운영을 돕고 있는 사람입니다.`,
    positioning ? `(${positioning})` : "",
    `사장님 가게 인스타 보니까 분위기가 정말 좋은데 ${gap}`,
    "혹시 인스타 릴스는 따로 신경 쓰기 힘드셨나요? 제가 무료로 20초 릴스 시안 하나 만들어 드릴게요.",
    "쓸모 있으면 쓰시고, 아니면 안 쓰셔도 됩니다. 가게 사진 두 장만 보내 주시면 돼요.",
  ]
    .filter(Boolean)
    .join("\n");
}

/** 3페이지 제안서 (PART 8-1) 의 3쪽 조건 문구 */
export function trialTerms(): string[] {
  return [
    `첫 ${TRIAL.days}일 무료 운영 (시작일·종료일 계약서에 명시)`,
    `월 정액 전환 시 첫 달 ${TRIAL.firstMonthDiscount}% 할인, 두 번째 달부터 정가`,
    "대신 결과물을 포트폴리오로 사용하는 데 동의 (저작권은 사장님께)",
    "모든 게시물은 사장님 승인 후에만 올라갑니다",
  ];
}

/** 주간 소통 메시지 (PART 9-4) — 카톡으로 사람이 직접 보내는 초안 */
export function mondayMessage(clientName: string, items: { day: string; title: string }[]): string {
  return [`${clientName} 사장님, 이번 주 업로드 예정표입니다 🙂`, ...(items.length ? items.map((i) => `• ${i.day} ${i.title}`) : ["• 이번 주 예정 게시물 준비 중 (사진 보내 주시면 바로 만들어요)"]), "확인 부탁드려요. 수정할 점 있으면 편하게 말씀 주세요!"].join("\n");
}

export function fridayMessage(clientName: string, s: { posts: number; views: number | null; best?: string | null }): string {
  return [
    `${clientName} 사장님, 이번 주 결과 요약입니다.`,
    `• 올린 게시물 ${s.posts}개${s.views != null ? ` · 조회수 합계 ${s.views.toLocaleString("ko-KR")}` : ""}`,
    s.best ? `• 가장 반응 좋은 게시물: ${s.best}` : "",
    "다음 주도 사진 보내 주시면 바로 준비하겠습니다. 좋은 주말 보내세요!",
  ]
    .filter(Boolean)
    .join("\n");
}

export interface ChurnInput {
  reportViewedAt: Date | null;
  lastReportSentAt?: Date | null;
  pendingClientApprovals: number;
  oldestPendingDays: number;
  missedPayments: number;
}

/** 이탈 경고등 (PART 11-1) — 보고서 미확인·응답 지연·미납 */
export function churnSignals(c: ChurnInput, now = new Date()): string[] {
  const out: string[] = [];
  if (!c.reportViewedAt || now.getTime() - c.reportViewedAt.getTime() > 35 * 86_400_000) out.push("보고서를 한 달 넘게 열어 보지 않음");
  if (c.pendingClientApprovals > 0 && c.oldestPendingDays >= 3) out.push(`승인 답이 ${c.oldestPendingDays}일째 없음`);
  if (c.missedPayments > 0) out.push(`미납 ${c.missedPayments}회`);
  return out;
}

export interface HealthInput {
  monthlyRevenue: number[]; // 오래된 달 → 최근 달 (입금 기준)
  newInquiriesThisMonth: number;
  cashReserve: number | null;
  fixedCosts: number;
}

/** 실패 신호 (PART 16-1) */
export function failureSignals(h: HealthInput): string[] {
  const out: string[] = [];
  const r = h.monthlyRevenue;
  if (r.length >= 4 && r[r.length - 1] < r[r.length - 2] && r[r.length - 2] < r[r.length - 3] && r[r.length - 3] < r[r.length - 4])
    out.push("3개월 연속 월매출 하락 → 가격·상품·채널 중 하나를 바꿀 때");
  if (h.newInquiriesThisMonth === 0) out.push("이번 달 신규 문의 0건 → 영업 활동량 부족 (안 보여서 없는 것)");
  if (h.cashReserve != null && h.fixedCosts > 0 && h.cashReserve < h.fixedCosts * MONEY.dangerMonths)
    out.push("잔고가 고정비 2개월치 미만 → 신규 지출 중단 + 매출 활동 2배");
  return out;
}

export interface SpinoffInput {
  monthlyProfit: number[]; // 최근 달들의 순이익(내 월급 제외)
  manualDocs: number; // 매뉴얼 문서 수
  churnRatePct: number | null; // 월 이탈률
}

/** 분사 조건 (PART 13-1) */
export function spinoffConditions(s: SpinoffInput) {
  const last3 = s.monthlyProfit.slice(-3);
  return [
    { label: "순이익 월 100만 원 이상 3개월 연속", ok: last3.length === 3 && last3.every((p) => p >= 1_000_000) },
    { label: "내 개입 없이 2주 운영 가능한 매뉴얼 (문서 10개 이상)", ok: s.manualDocs >= 10 },
    { label: "고객 이탈률 월 10% 미만", ok: s.churnRatePct != null && s.churnRatePct < 10 },
  ];
}

/** 가격 인상 신호 (PART 11-4): 수락 못 한 대기 고객 월 2건 이상 */
export function priceRaiseSignal(waitlistThisMonth: number): string | null {
  return waitlistThisMonth >= 2 ? `대기 고객 ${waitlistThisMonth}명 → 신규 고객부터 20% 인상 검토 (기존 고객은 3개월 뒤, 30일 전 공지)` : null;
}

/** 이번 달 청구 금액 — 첫 유료 달 할인 반영 */
export function chargeFor(sub: { monthlyFee: number; firstMonthDiscount: number }, isFirstPaidMonth: boolean): number {
  return isFirstPaidMonth ? Math.round((sub.monthlyFee * (100 - sub.firstMonthDiscount)) / 100) : sub.monthlyFee;
}
