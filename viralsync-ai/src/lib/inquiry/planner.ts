import type { ServiceChannel } from "@prisma/client";
import type { BusinessType, ParsedInquiry } from "./parser";

export const CHANNEL_LABEL: Record<ServiceChannel, string> = {
  BLOG: "블로그 포스팅",
  EXPERIENCE_GROUP: "블로그 체험단",
  NAVER_PLACE: "네이버 플레이스",
  INSTAGRAM: "인스타그램",
  YOUTUBE: "유튜브·쇼츠",
  TIKTOK: "틱톡",
  SEARCH_AD: "네이버 검색광고",
  META_AD: "메타(인스타·페북) 광고",
  KARROT: "당근 지역광고",
  PACKAGE: "종합 패키지",
  MONTHLY_SNS: "월 정액 SNS·숏폼 운영",
};

export const SERVICE_CHANNELS: ServiceChannel[] = ["BLOG", "EXPERIENCE_GROUP", "NAVER_PLACE", "INSTAGRAM", "YOUTUBE", "TIKTOK", "SEARCH_AD", "META_AD", "KARROT", "PACKAGE", "MONTHLY_SNS"];

/** 업종별 추천 매체 우선순위와 이유 (운영 경험 기반 기본값 — 서비스 상품 카탈로그로 실제 판매 상품이 결정됨) */
const PLAYBOOK: Record<BusinessType, [ServiceChannel, string][]> = {
  RESTAURANT: [
    ["NAVER_PLACE", "음식점은 지도·플레이스 검색에서 방문이 결정되는 비중이 커 기본 정보·사진·소식 정비가 우선입니다."],
    ["EXPERIENCE_GROUP", "방문 후기 콘텐츠가 검색 결과에 쌓이도록 광고 표시를 지킨 체험단을 운영합니다."],
    ["INSTAGRAM", "메뉴·매장 분위기를 릴스로 보여 주기 좋은 업종입니다."],
    ["META_AD", "매장 반경 지역 타깃으로 노출할 수 있습니다 (매체비 별도)."],
    ["KARROT", "동네 기반 고객에게 직접 노출됩니다."],
    ["BLOG", "대표 키워드 정보성 포스팅으로 검색 유입을 보완합니다."],
  ],
  CAFE: [
    ["INSTAGRAM", "카페·디저트는 비주얼 중심 탐색이 많아 인스타 운영 효과가 큽니다."],
    ["NAVER_PLACE", "지도 검색 노출과 기본 정보 정비가 필요합니다."],
    ["EXPERIENCE_GROUP", "방문 후기 콘텐츠를 확보합니다."],
    ["META_AD", "지역 타깃 광고로 신규 고객에게 노출합니다 (매체비 별도)."],
    ["KARROT", "동네 기반 노출에 적합합니다."],
  ],
  BEAUTY: [
    ["NAVER_PLACE", "예약 전 플레이스에서 리뷰·가격을 확인하는 고객이 많습니다."],
    ["INSTAGRAM", "시술 전후(동의받은) 사진·스타일 콘텐츠에 적합합니다."],
    ["EXPERIENCE_GROUP", "광고 표시를 지킨 체험 후기를 확보합니다."],
    ["META_AD", "지역·관심사 타깃 광고가 가능합니다 (매체비 별도)."],
    ["BLOG", "시술 정보성 포스팅으로 검색 유입을 만듭니다."],
  ],
  MEDICAL: [
    ["BLOG", "정보성 콘텐츠 위주로 운영합니다 (의료광고 심의 기준 준수)."],
    ["NAVER_PLACE", "기본 정보·진료 시간 정비가 필요합니다."],
    ["SEARCH_AD", "증상·진료 키워드 검색광고가 가능합니다 (심의·매체 정책 확인)."],
  ],
  EDUCATION: [
    ["BLOG", "학부모·수강생이 검색으로 정보를 찾는 업종입니다."],
    ["SEARCH_AD", "지역+과목 키워드 검색광고가 효과적입니다 (매체비 별도)."],
    ["YOUTUBE", "강의 맛보기 쇼츠로 신뢰를 쌓습니다."],
    ["META_AD", "관심사 타깃 광고로 상담 신청을 유도합니다 (매체비 별도)."],
    ["INSTAGRAM", "수업 현장·후기(동의) 콘텐츠를 운영합니다."],
  ],
  COMMERCE: [
    ["INSTAGRAM", "상품 비주얼·사용 장면 콘텐츠에 적합합니다."],
    ["META_AD", "구매 전환 최적화 광고를 운영합니다 (매체비 별도)."],
    ["BLOG", "상품 정보성 리뷰 콘텐츠로 검색 유입을 만듭니다."],
    ["SEARCH_AD", "상품 키워드 검색광고로 구매 의도 고객을 잡습니다 (매체비 별도)."],
    ["YOUTUBE", "쇼츠 상품 소개 영상을 제작합니다."],
  ],
  APP: [
    ["META_AD", "앱 설치 캠페인 최적화가 가능합니다 (매체비 별도)."],
    ["TIKTOK", "숏폼 중심 사용자층에 앱을 알리기 좋습니다."],
    ["YOUTUBE", "기능 소개 쇼츠를 제작합니다."],
    ["INSTAGRAM", "릴스·피드로 사용 장면을 보여 줍니다."],
    ["BLOG", "앱 소개·사용법 포스팅으로 검색 유입을 보완합니다."],
  ],
  LOCAL_SERVICE: [
    ["NAVER_PLACE", "지역 서비스는 플레이스 검색 비중이 큽니다."],
    ["BLOG", "지역+서비스 키워드 포스팅으로 문의를 만듭니다."],
    ["SEARCH_AD", "지역 키워드 검색광고가 효과적입니다 (매체비 별도)."],
    ["KARROT", "동네 기반 노출에 적합합니다."],
    ["INSTAGRAM", "작업 사례 콘텐츠를 운영합니다."],
  ],
  FINANCE: [
    ["BLOG", "정보 제공형 콘텐츠만 운영합니다 (표시 의무·금지 표현 준수)."],
    ["SEARCH_AD", "매체 심사를 통과한 범위에서 검색광고를 운영합니다."],
  ],
  OTHER: [
    ["BLOG", "검색 기반 유입의 기본 채널입니다."],
    ["INSTAGRAM", "브랜드 인지도를 쌓는 기본 SNS 채널입니다."],
    ["SEARCH_AD", "구매·문의 의도가 있는 검색 고객에게 노출합니다 (매체비 별도)."],
    ["META_AD", "타깃 광고로 신규 고객에게 노출합니다 (매체비 별도)."],
  ],
};

const COMPLIANCE: Partial<Record<ServiceChannel, string>> = {
  BLOG: "원고형 포스팅도 대가를 받은 경우 ‘광고·협찬’ 표시를 본문 첫머리에 넣습니다 (공정위 추천·보증 심사지침).",
  EXPERIENCE_GROUP: "체험단 게시물에는 ‘제품·서비스를 제공받아 작성’ 등 경제적 이해관계를 반드시 표시합니다. 후기 내용을 대신 써 주거나 강요하지 않습니다.",
  NAVER_PLACE: "리뷰 대리 작성·대가성 리뷰 조작은 하지 않습니다. 정보·사진·소식 정비와 정상적인 리뷰 요청 안내만 진행합니다.",
  INSTAGRAM: "협찬 게시물에는 유료 파트너십 표시를 사용합니다.",
  META_AD: "광고 소재는 메타 광고 정책 심사를 거치며, 매체비는 고객 계정에서 직접 결제하는 것을 권장합니다.",
  SEARCH_AD: "검색광고는 매체 검수를 거치며, 매체비는 고객 광고 계정에서 직접 충전·결제하는 것을 권장합니다.",
  YOUTUBE: "유료 PPL·협찬 영상은 ‘유료 프로모션 포함’ 표시를 켭니다.",
  TIKTOK: "브랜디드 콘텐츠 표시를 사용합니다.",
};

export interface CatalogItem {
  id: string;
  name: string;
  channel: ServiceChannel;
  unitPrice: number;
  unit: string;
  mediaSpendSeparate: boolean;
  active: boolean;
}

export interface ChannelRec {
  channel: ServiceChannel;
  label: string;
  reason: string;
  requested: boolean;
  available: boolean;
}

export interface PlanItem {
  packageId: string;
  name: string;
  channel: ServiceChannel;
  quantity: number;
  unit: string;
  unitPrice: number;
  subtotal: number;
  mediaSpendSeparate: boolean;
}

export type TierKey = "BASIC" | "STANDARD" | "PREMIUM";

export interface PlanTier {
  key: TierKey;
  label: string;
  items: PlanItem[];
  total: number;
  mediaSpend: { min: number; max: number } | null;
}

export interface MediaPlan {
  channels: ChannelRec[];
  tiers: PlanTier[];
  recommendedTier: TierKey;
  fullPackage: CatalogItem | null;
  compliance: string[];
  assumptions: string[];
}

const TIER_META: Record<TierKey, { label: string; channels: number; spend: [number, number] }> = {
  BASIC: { label: "실속형", channels: 2, spend: [300_000, 500_000] },
  STANDARD: { label: "표준형", channels: 3, spend: [500_000, 1_000_000] },
  PREMIUM: { label: "집중형", channels: 5, spend: [1_000_000, 2_000_000] },
};

function quantityFor(channel: ServiceChannel, tier: TierKey, keywordCount: number): number {
  // 블로그는 요청 키워드 전부를 모든 안에 반영 (키워드 1개 = 상품 1단위, 최대 5)
  if (channel === "BLOG") return Math.max(1, Math.min(keywordCount, 5));
  if (channel === "EXPERIENCE_GROUP") return tier === "PREMIUM" ? 2 : 1;
  return 1;
}

export function buildMediaPlan(parsed: Pick<ParsedInquiry, "businessType" | "requestedChannels" | "keywords" | "budgetMentionedKrw" | "wantsFullPackage">, catalog: CatalogItem[]): MediaPlan {
  const active = catalog.filter((c) => c.active);
  const cheapest = (ch: ServiceChannel) =>
    active.filter((c) => c.channel === ch).sort((a, b) => a.unitPrice - b.unitPrice)[0] ?? null;

  const playbook = PLAYBOOK[parsed.businessType] ?? PLAYBOOK.OTHER;
  const ordered: ChannelRec[] = [];
  const push = (channel: ServiceChannel, reason: string, requested: boolean) => {
    if (channel === "PACKAGE" || ordered.some((o) => o.channel === channel)) return;
    ordered.push({ channel, label: CHANNEL_LABEL[channel], reason, requested, available: !!cheapest(channel) });
  };
  // 고객이 직접 요청한 매체를 먼저
  for (const ch of parsed.requestedChannels) {
    const pb = playbook.find(([c]) => c === ch);
    push(ch, pb ? `고객 요청 · ${pb[1]}` : "고객이 직접 요청한 매체입니다.", true);
  }
  for (const [ch, reason] of playbook) push(ch, reason, false);

  const usable = ordered.filter((o) => o.available);
  const requestedCount = usable.filter((o) => o.requested).length;
  const tiers: PlanTier[] = (Object.keys(TIER_META) as TierKey[]).map((key) => {
    const meta = TIER_META[key];
    // 고객이 매체를 지정했다면: 실속형 = 요청 매체만, 표준형 = +1, 집중형 = +3
    const n = requestedCount > 0 ? requestedCount + { BASIC: 0, STANDARD: 1, PREMIUM: 3 }[key] : meta.channels;
    const items: PlanItem[] = usable.slice(0, n).map((o) => {
      const pkg = cheapest(o.channel)!;
      const quantity = quantityFor(o.channel, key, parsed.keywords.length);
      return {
        packageId: pkg.id,
        name: pkg.name,
        channel: o.channel,
        quantity,
        unit: pkg.unit,
        unitPrice: pkg.unitPrice,
        subtotal: pkg.unitPrice * quantity,
        mediaSpendSeparate: pkg.mediaSpendSeparate,
      };
    });
    const needsSpend = items.some((i) => i.mediaSpendSeparate);
    return {
      key,
      label: meta.label,
      items,
      total: items.reduce((a, i) => a + i.subtotal, 0),
      mediaSpend: needsSpend ? { min: meta.spend[0], max: meta.spend[1] } : null,
    };
  });

  let recommendedTier: TierKey = "STANDARD";
  if (parsed.budgetMentionedKrw != null) {
    const fit = [...tiers].reverse().find((t) => t.total + (t.mediaSpend?.min ?? 0) <= parsed.budgetMentionedKrw!);
    recommendedTier = fit?.key ?? "BASIC";
  }

  const assumptions = [
    "견적은 서비스 상품 카탈로그 단가 기준이며 VAT·매체비 포함 여부는 운영 정책에 따릅니다.",
    "권장 매체비는 경험적 범위이며 실제 성과를 보장하지 않습니다.",
  ];
  if (parsed.keywords.length) assumptions.push(`블로그 수량은 요청 키워드 ${parsed.keywords.length}개 기준입니다 (키워드 검색량·경쟁도는 별도 확인 필요).`);
  const missing = ordered.filter((o) => !o.available);
  if (missing.length) assumptions.push(`카탈로그에 상품이 없어 견적에서 제외: ${missing.map((m) => m.label).join(", ")}`);

  const compliance = [...new Set(tiers.flatMap((t) => t.items.map((i) => COMPLIANCE[i.channel]).filter((x): x is string => !!x)))];
  compliance.unshift("상위노출·매출 등 성과는 보장하지 않으며, 모든 홍보물에 광고임을 표시합니다.");

  return {
    channels: ordered,
    tiers,
    recommendedTier,
    fullPackage: parsed.wantsFullPackage ? (active.find((c) => c.channel === "PACKAGE") ?? null) : null,
    compliance,
    assumptions,
  };
}
