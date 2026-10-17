import type { ServiceChannel } from "@prisma/client";
import { classify } from "@/lib/analysis/engine";
import { checkUrl } from "@/lib/validation/url";

/**
 * 광고 문의 원문(크몽 메시지 등)에서 견적에 필요한 정보를 규칙 기반으로 추출한다.
 * - 링크는 형식만 확인하고 접속(크롤링)하지 않는다.
 * - 추출하지 못한 정보는 missingInfo 로 돌려 고객에게 되묻도록 한다 (추측으로 채우지 않음).
 */

export type BusinessType = "RESTAURANT" | "CAFE" | "BEAUTY" | "MEDICAL" | "EDUCATION" | "COMMERCE" | "APP" | "LOCAL_SERVICE" | "FINANCE" | "OTHER";

export const BUSINESS_TYPE_LABEL: Record<BusinessType, string> = {
  RESTAURANT: "음식점",
  CAFE: "카페·디저트",
  BEAUTY: "뷰티·미용",
  MEDICAL: "병원·의료",
  EDUCATION: "교육·학원",
  COMMERCE: "쇼핑몰·상품",
  APP: "앱·서비스",
  LOCAL_SERVICE: "지역 서비스업",
  FINANCE: "금융·투자",
  OTHER: "기타",
};

export type LinkKind = "HOMEPAGE" | "INSTAGRAM" | "BLOG" | "YOUTUBE" | "NAVER_PLACE" | "SMARTSTORE" | "APP_STORE" | "TIKTOK" | "OTHER";

export const LINK_KIND_LABEL: Record<LinkKind, string> = {
  HOMEPAGE: "홈페이지",
  INSTAGRAM: "인스타그램",
  BLOG: "블로그",
  YOUTUBE: "유튜브",
  NAVER_PLACE: "네이버 플레이스",
  SMARTSTORE: "스마트스토어",
  APP_STORE: "앱 스토어",
  TIKTOK: "틱톡",
  OTHER: "기타 링크",
};

export type QuestionKind = "PRICE" | "BUDGET" | "RECOMMEND" | "FEASIBILITY" | "TIMELINE" | "PERFORMANCE";

export const QUESTION_LABEL: Record<QuestionKind, string> = {
  PRICE: "가격·견적",
  BUDGET: "적정 예산",
  RECOMMEND: "추천 광고 종류",
  FEASIBILITY: "진행 가능 여부",
  TIMELINE: "기간·일정",
  PERFORMANCE: "예상 효과",
};

export interface ParsedLink {
  url: string;
  kind: LinkKind;
}

export interface ParsedInquiry {
  brand: string | null;
  businessType: BusinessType;
  category: string;
  links: ParsedLink[];
  keywords: string[];
  requestedChannels: ServiceChannel[];
  wantsFullPackage: boolean;
  questions: QuestionKind[];
  budgetMentionedKrw: number | null;
  region: string | null;
  referencesCompetitor: boolean;
  missingInfo: string[];
  notes: string[];
}

const URL_RE = /(https?:\/\/[^\s<>"'()]+|www\.[^\s<>"'()]+)/gi;

function linkKind(host: string, path: string): LinkKind {
  const h = host.toLowerCase();
  if (h.includes("instagram.com")) return "INSTAGRAM";
  if (h.includes("youtube.com") || h === "youtu.be") return "YOUTUBE";
  if (h.includes("tiktok.com")) return "TIKTOK";
  if (h === "blog.naver.com" || h === "m.blog.naver.com" || h.endsWith("tistory.com") || h.includes("brunch.co.kr")) return "BLOG";
  if (h.includes("place.naver.com") || h === "naver.me" || (h.includes("map.naver.com") && path.includes("place"))) return "NAVER_PLACE";
  if (h.includes("smartstore.naver.com")) return "SMARTSTORE";
  if (h.includes("apps.apple.com") || h.includes("play.google.com")) return "APP_STORE";
  return "HOMEPAGE";
}

export function extractLinks(text: string): ParsedLink[] {
  const out: ParsedLink[] = [];
  const seen = new Set<string>();
  for (const m of text.matchAll(URL_RE)) {
    const raw = m[0].replace(/[.,)\]>]+$/, "");
    const withProto = raw.startsWith("www.") ? `https://${raw}` : raw;
    const r = checkUrl(withProto);
    if (!r.valid || !r.normalized || seen.has(r.normalized)) continue;
    seen.add(r.normalized);
    const u = new URL(r.normalized);
    out.push({ url: r.normalized, kind: linkKind(u.hostname, u.pathname) });
  }
  return out;
}

/** "키워드는 A, B, C 입니다" / "키워드: A / B" 형태 */
export function extractKeywords(text: string): string[] {
  // 한글에는 \b 단어 경계가 동작하지 않으므로 종결 어미는 명시적으로 끊는다
  const m = text.match(/키워드\s*(?:는|은|:|：)\s*([^\n]+?)(?:\s*(?:입니다|이에요|예요|이요)(?=$|[\s<>.,!?~])|[<>.\n]|$)/);
  if (!m) return [];
  return m[1]
    .split(/[,，、/·]|\s{2,}/)
    .map((s) => s.trim().replace(/^["'“”‘’]|["'“”‘’]$/g, ""))
    .filter((s) => s.length >= 1 && s.length <= 30)
    .slice(0, 15);
}

/** '브랜드명' 브랜드 / 브랜드명 : X / [X] 매장 */
export function extractBrand(text: string): string | null {
  const patterns = [
    /['"‘“]([^'"’”\n]{1,30})['"’”]\s*(?:브랜드|매장|가게|식당|업체|상호)/,
    /(?:브랜드명|상호명|상호|업체명|매장명)\s*[:：은는]?\s*([^\n,]{1,30})/,
    /['"‘“]([^'"’”\n]{2,30})['"’”]/,
  ];
  for (const re of patterns) {
    const m = text.match(re);
    if (m) return m[1].trim();
  }
  return null;
}

const BUSINESS_RULES: [BusinessType, RegExp][] = [
  ["MEDICAL", /(병원|의원|치과|한의원|피부과|성형|클리닉|약국)/],
  ["FINANCE", /(대출|보험|투자|주식|코인|재테크)/],
  ["CAFE", /(카페|커피|디저트|베이커리|빵집)/],
  ["RESTAURANT", /(음식점|식당|맛집|샤브|고기|횟집|술집|주점|레스토랑|치킨|피자|국밥|분식|뷔페|요리|메뉴)/],
  ["BEAUTY", /(미용실|헤어|네일|피부관리|왁싱|속눈썹|뷰티|화장품|에스테틱)/],
  ["EDUCATION", /(학원|과외|강의|교육|클래스|코딩|어학|입시)/],
  ["APP", /(앱|어플|애플리케이션|플랫폼 서비스|다운로드|설치)/],
  ["COMMERCE", /(쇼핑몰|스마트스토어|상품|제품|판매|구매|스토어)/],
  ["LOCAL_SERVICE", /(인테리어|청소|이사|헬스장|필라테스|요가|부동산|사진관|세탁)/],
];

export function detectBusinessType(text: string): BusinessType {
  for (const [t, re] of BUSINESS_RULES) if (re.test(text)) return t;
  return "OTHER";
}

const CHANNEL_RULES: [ServiceChannel, RegExp][] = [
  ["EXPERIENCE_GROUP", /(체험단|리뷰어|방문\s*리뷰)/],
  ["BLOG", /(블로그|블러그|포스팅|원고)/],
  ["NAVER_PLACE", /(플레이스|지도\s*노출|네이버\s*지도)/],
  ["INSTAGRAM", /(인스타|instagram|릴스|피드)/i],
  ["YOUTUBE", /(유튜브|youtube|쇼츠|영상)/i],
  ["TIKTOK", /(틱톡|tiktok)/i],
  ["SEARCH_AD", /(검색광고|파워링크|키워드\s*광고|네이버\s*광고)/],
  ["META_AD", /(메타\s*광고|페이스북\s*광고|페북|sns\s*광고|스폰서\s*광고)/i],
  ["KARROT", /(당근)/],
];

const QUESTION_RULES: [QuestionKind, RegExp][] = [
  ["PRICE", /(가격|비용|견적|단가|얼마)/],
  ["BUDGET", /(예산)/],
  ["RECOMMEND", /(추천|어떤\s*(?:광고|것|방법)|종류)/],
  ["FEASIBILITY", /(가능할까|가능한지|가능한가|가능\s*여부|되나요|될까요|할\s*수\s*있)/],
  ["TIMELINE", /(기간|언제|일정|며칠|얼마나\s*걸)/],
  ["PERFORMANCE", /(효과|매출|상위\s*노출|순위|회수)/],
];

const REGIONS = /(서울|부산|대구|인천|광주|대전|울산|세종|경기|강원|충북|충남|전북|전남|경북|경남|제주|[가-힣]{1,4}(?:구|시|동|역))(?=\s|에|의|,|$)/;

function extractBudget(text: string): number | null {
  const m = text.match(/(\d[\d,]*(?:\.\d+)?)\s*(만\s*원|만원|원)/);
  if (!m) return null;
  const n = Number(m[1].replace(/,/g, ""));
  if (!Number.isFinite(n)) return null;
  return m[2].includes("만") ? Math.round(n * 10_000) : Math.round(n);
}

export function parseInquiry(raw: string): ParsedInquiry {
  const text = raw.replace(/\r/g, "");
  const textNoUrl = text.replace(URL_RE, " ");
  const links = extractLinks(text);
  const keywords = extractKeywords(textNoUrl);
  const brand = extractBrand(textNoUrl);
  const businessType = detectBusinessType(textNoUrl);
  const category = classify(`${textNoUrl} ${keywords.join(" ")}`).category;
  // "▶인스타그램 : 주소" 처럼 링크 라벨로 쓰인 줄은 '요청 매체'가 아니라 운영 채널 정보이므로 제외
  const requestText = textNoUrl
    .split("\n")
    .filter((line) => !/^\W*(홈페이지|인스타그램|인스타|블로그|유튜브|틱톡|플레이스|스마트스토어)\s*[:：]/.test(line.trim()))
    .join("\n");
  const requestedChannels = CHANNEL_RULES.filter(([, re]) => re.test(requestText)).map(([c]) => c);
  const wantsFullPackage = /(종합\s*광고|광고\s*대행|전체\s*마케팅|통합\s*마케팅|종합\s*마케팅)/.test(textNoUrl);
  const questions = QUESTION_RULES.filter(([, re]) => re.test(textNoUrl)).map(([q]) => q);
  const budgetMentionedKrw = extractBudget(textNoUrl);
  const regionMatch = textNoUrl.match(REGIONS);
  const referencesCompetitor = /(유사한|비슷한|처럼|같은\s*느낌|벤치마킹|참고)/.test(textNoUrl);

  const notes: string[] = [];
  if (links.length) notes.push("링크는 형식만 확인했습니다. 실제 페이지 내용은 담당자가 직접 확인해야 합니다.");
  if (businessType === "MEDICAL") notes.push("의료 광고는 의료법상 사전 심의·표현 제한이 있어 별도 검토가 필요합니다.");
  if (businessType === "FINANCE") notes.push("금융·투자 광고는 관련 법령상 표시 의무·금지 표현이 있어 별도 검토가 필요합니다.");
  if (referencesCompetitor) notes.push("경쟁사와 유사한 방식을 원합니다. 경쟁사 콘텐츠를 모방·도용하지 않고 형식만 참고하도록 안내하세요.");
  if (/(상위\s*노출|1페이지|1위)/.test(textNoUrl)) notes.push("상위노출·순위는 보장할 수 없다고 안내해야 합니다.");

  const missingInfo: string[] = [];
  if (!brand) missingInfo.push("브랜드(상호)명");
  if (!links.length) missingInfo.push("홈페이지·SNS·플레이스 링크");
  if (budgetMentionedKrw == null) missingInfo.push("월 예산 범위 (대행비 + 광고 매체비)");
  if (!regionMatch && ["RESTAURANT", "CAFE", "BEAUTY", "LOCAL_SERVICE", "MEDICAL"].includes(businessType)) missingInfo.push("매장 지역(상권)과 주요 고객층");
  if (!/(기간|개월|주간|이번\s*달|다음\s*달)/.test(textNoUrl)) missingInfo.push("희망 진행 기간·시작일");
  if (!/(목표|매출|방문|예약|문의|설치|구매)/.test(textNoUrl)) missingInfo.push("가장 중요한 목표 (방문·예약·문의·구매 등)");
  if (requestedChannels.includes("BLOG") && keywords.length === 0) missingInfo.push("노출을 원하는 키워드");

  return {
    brand,
    businessType,
    category,
    links,
    keywords,
    requestedChannels,
    wantsFullPackage,
    questions,
    budgetMentionedKrw,
    region: regionMatch?.[1] ?? null,
    referencesCompetitor,
    missingInfo,
    notes,
  };
}
