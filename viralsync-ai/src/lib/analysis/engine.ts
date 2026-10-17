import type { CampaignGoal, PlatformKey, TargetType } from "@prisma/client";
import { RISKY_PHRASES, TAXONOMY } from "./taxonomy";

/**
 * 규칙 기반 분석 엔진 (rule-based-v1)
 * - 키워드 사전·입력 항목 충실도로 점수를 산출하며, 모든 점수에 산출 기준과 근거를 함께 반환한다.
 * - 입력이 부족하면 value=null(분석 불가)로 표시한다. 실제 성과 예측이 아니다.
 */
export const ENGINE_VERSION = "rule-based-v1";

export type ScoreKey = "topicFit" | "targetFit" | "brandFit" | "contentRelevance" | "trafficPotential" | "policyRisk";

export interface Score {
  value: number | null;
  /** 추정 | 분석 불가 */
  kind: "ESTIMATE" | "UNAVAILABLE";
  criteria: string;
  evidence: string[];
}

export interface AnalysisResult {
  engine: string;
  category: string;
  subcategory: string;
  categoryConfidence: number;
  matchedKeywords: string[];
  dataSufficiency: "SUFFICIENT" | "LIMITED" | "INSUFFICIENT";
  scores: Record<ScoreKey, Score>;
  notes: string[];
}

export const SCORE_LABEL: Record<ScoreKey, string> = {
  topicFit: "주제 일치도",
  targetFit: "타깃 적합도",
  brandFit: "브랜드 적합도",
  contentRelevance: "콘텐츠 관련성",
  trafficPotential: "예상 유입 가능성",
  policyRisk: "광고 정책 위험도",
};

export interface BriefForAnalysis {
  title: string;
  description: string;
  keywords: string[];
  bannedKeywords: string[];
  coreTarget: string;
  targetType: TargetType;
  goal: CampaignGoal;
  desiredPlatforms: PlatformKey[];
  targetUrl?: string | null;
}

export interface BrandForAnalysis {
  companyIntro: string;
  productDescription: string;
  coreTarget: string;
  toneOfVoice: string;
  bannedPhrases: string[];
  requiredPhrases: string[];
}

const norm = (s: string) => s.toLowerCase().replace(/\s+/g, " ");

/** 2글자 이상 토큰 (한국어 조사 일부 제거) */
export function tokens(s: string): string[] {
  return norm(s)
    .split(/[^0-9a-z가-힣]+/)
    .map((t) => t.replace(/(은|는|이|가|을|를|의|에|와|과|로|으로|에서|도|만)$/u, ""))
    .filter((t) => t.length >= 2);
}

function overlap(a: string, b: string): { ratio: number; common: string[] } {
  const ta = new Set(tokens(a));
  const tb = new Set(tokens(b));
  if (ta.size === 0 || tb.size === 0) return { ratio: 0, common: [] };
  const common = [...ta].filter((t) => tb.has(t) || [...tb].some((x) => x.includes(t) || t.includes(x)));
  return { ratio: common.length / Math.min(ta.size, tb.size), common };
}

const clamp = (n: number) => Math.max(0, Math.min(100, Math.round(n)));

export interface ClassifyResult {
  category: string;
  subcategory: string;
  confidence: number;
  matched: string[];
}

/** 텍스트를 대분류·소분류로 분류. 키워드가 하나도 맞지 않으면 기타/일반. */
export function classify(text: string): ClassifyResult {
  const t = norm(text);
  let best: ClassifyResult = { category: "기타", subcategory: "일반", confidence: 0, matched: [] };
  let bestScore = 0;
  for (const cat of TAXONOMY) {
    let catScore = 0;
    let topSub = cat.subcategories[0]?.name ?? "일반";
    let topSubScore = 0;
    const catMatched: string[] = [];
    for (const sub of cat.subcategories) {
      const hits = sub.keywords.filter((k) => t.includes(k));
      const s = hits.reduce((acc, k) => acc + (k.length >= 3 ? 1.5 : 1), 0);
      catScore += s;
      catMatched.push(...hits);
      if (s > topSubScore) {
        topSubScore = s;
        topSub = sub.name;
      }
    }
    if (catScore > bestScore) {
      bestScore = catScore;
      best = { category: cat.name, subcategory: topSub, confidence: 0, matched: catMatched };
    }
  }
  best.confidence = bestScore === 0 ? 0 : clamp(35 + bestScore * 15);
  return best;
}

/** 홍보 대상 유형별 잘 맞는 플랫폼 */
const TYPE_PLATFORM_FIT: Record<TargetType, PlatformKey[]> = {
  BLOG: ["BLOG", "FACEBOOK", "X"],
  YOUTUBE: ["YOUTUBE", "X", "FACEBOOK", "BLOG"],
  SHORTS: ["YOUTUBE", "TIKTOK", "INSTAGRAM"],
  REELS: ["INSTAGRAM", "FACEBOOK", "TIKTOK"],
  APP: ["INSTAGRAM", "TIKTOK", "YOUTUBE", "X"],
  PRODUCT: ["INSTAGRAM", "BLOG", "YOUTUBE", "FACEBOOK"],
  OTHER: ["INSTAGRAM", "X", "FACEBOOK", "BLOG", "YOUTUBE", "TIKTOK"],
};

/** 목표별 플랫폼 성향 (조회형 / 전환형) — 경험적 가정이며 실측값이 아님 */
const GOAL_PLATFORM_AFFINITY: Record<CampaignGoal, PlatformKey[]> = {
  VIEWS: ["YOUTUBE", "TIKTOK", "INSTAGRAM"],
  CLICKS: ["X", "FACEBOOK", "BLOG", "INSTAGRAM"],
  VISITS: ["BLOG", "INSTAGRAM", "FACEBOOK"],
  INSTALLS: ["TIKTOK", "INSTAGRAM", "YOUTUBE"],
  INQUIRIES: ["BLOG", "FACEBOOK", "INSTAGRAM"],
  PURCHASES: ["INSTAGRAM", "YOUTUBE", "BLOG"],
};

export function findRiskyPhrases(text: string): string[] {
  const t = norm(text);
  return RISKY_PHRASES.filter((p) => t.includes(p.toLowerCase()));
}

export function analyzeBrief(brief: BriefForAnalysis, brand: BrandForAnalysis | null): AnalysisResult {
  const briefText = [brief.title, brief.description, brief.keywords.join(" "), brief.coreTarget].join(" ");
  const fullText = [briefText, brand?.productDescription ?? "", brand?.companyIntro ?? ""].join(" ");
  const cls = classify(fullText);
  const notes: string[] = [];

  const filled = [
    brief.description.trim().length >= 20,
    brief.keywords.length > 0,
    brief.coreTarget.trim().length > 0,
    !!brand && (brand.productDescription.trim().length > 0 || brand.companyIntro.trim().length > 0),
  ].filter(Boolean).length;
  const dataSufficiency = filled >= 3 ? "SUFFICIENT" : filled >= 2 ? "LIMITED" : "INSUFFICIENT";
  if (dataSufficiency !== "SUFFICIENT")
    notes.push("입력 정보가 부족해 일부 점수는 신뢰도가 낮거나 산출할 수 없습니다. 상세 설명·키워드·타깃을 보강하세요.");
  if (brief.targetUrl)
    notes.push("홍보 대상 URL 의 내용은 자동으로 수집·분석하지 않았습니다. 입력된 텍스트만 분석했습니다.");

  // 1) 주제 일치도
  const topicFit: Score =
    cls.confidence === 0
      ? {
          value: null,
          kind: "UNAVAILABLE",
          criteria: "의뢰 텍스트가 분류 사전 키워드와 얼마나 명확히 일치하는지 (키워드 가중 합)",
          evidence: ["분류 사전과 일치하는 키워드가 없어 '기타'로 분류했습니다."],
        }
      : {
          value: cls.confidence,
          kind: "ESTIMATE",
          criteria: "의뢰 텍스트가 분류 사전 키워드와 얼마나 명확히 일치하는지 (35 + 키워드 가중합×15, 최대 100)",
          evidence: [`일치 키워드: ${cls.matched.join(", ")}`, `분류: ${cls.category} > ${cls.subcategory}`],
        };

  // 2) 타깃 적합도
  let targetFit: Score;
  if (!brief.coreTarget.trim()) {
    targetFit = {
      value: null,
      kind: "UNAVAILABLE",
      criteria: "의뢰 타깃과 브랜드 핵심 타깃의 표현 일치율",
      evidence: ["의뢰에 핵심 타깃이 입력되지 않았습니다."],
    };
  } else if (!brand?.coreTarget.trim()) {
    targetFit = {
      value: 50,
      kind: "ESTIMATE",
      criteria: "의뢰 타깃과 브랜드 핵심 타깃의 표현 일치율",
      evidence: ["브랜드 프로필에 핵심 타깃이 없어 중립값(50)으로 추정했습니다."],
    };
  } else {
    const o = overlap(brief.coreTarget, brand.coreTarget);
    targetFit = {
      value: clamp(30 + o.ratio * 70),
      kind: "ESTIMATE",
      criteria: "의뢰 타깃과 브랜드 핵심 타깃의 표현 일치율 (30 + 일치율×70)",
      evidence: [o.common.length ? `공통 표현: ${o.common.join(", ")}` : "공통 표현이 없습니다."],
    };
  }

  // 3) 브랜드 적합도
  let brandFit: Score;
  const brandText = brand ? `${brand.productDescription} ${brand.companyIntro}` : "";
  if (!brandText.trim()) {
    brandFit = {
      value: null,
      kind: "UNAVAILABLE",
      criteria: "의뢰 내용과 브랜드 소개·상품 설명의 표현 일치율, 금지 표현 포함 여부",
      evidence: ["브랜드 소개·상품 설명이 등록되지 않았습니다."],
    };
  } else {
    const o = overlap(briefText, brandText);
    const bannedHits = (brand?.bannedPhrases ?? []).filter((p) => p && norm(briefText).includes(norm(p)));
    brandFit = {
      value: clamp(35 + o.ratio * 65 - bannedHits.length * 20),
      kind: "ESTIMATE",
      criteria: "의뢰 내용과 브랜드 소개·상품 설명의 표현 일치율 (35 + 일치율×65, 금지 표현 1건당 -20)",
      evidence: [
        o.common.length ? `공통 표현: ${o.common.slice(0, 8).join(", ")}` : "공통 표현이 적습니다.",
        ...(bannedHits.length ? [`의뢰문에 브랜드 금지 표현 포함: ${bannedHits.join(", ")}`] : []),
      ],
    };
  }

  // 4) 콘텐츠 관련성 (홍보 대상 유형 ↔ 희망 SNS 궁합)
  const good = TYPE_PLATFORM_FIT[brief.targetType];
  const fitPlatforms = brief.desiredPlatforms.filter((p) => good.includes(p));
  const contentRelevance: Score = {
    value: brief.desiredPlatforms.length ? clamp(30 + (fitPlatforms.length / brief.desiredPlatforms.length) * 70) : null,
    kind: brief.desiredPlatforms.length ? "ESTIMATE" : "UNAVAILABLE",
    criteria: "홍보 대상 유형에 적합한 플랫폼 비율 (30 + 적합 플랫폼 비율×70)",
    evidence: [
      `적합 플랫폼: ${fitPlatforms.join(", ") || "없음"}`,
      `유형별 권장: ${good.join(", ")}`,
    ],
  };

  // 5) 예상 유입 가능성 (가정 기반 추정치)
  const affinity = GOAL_PLATFORM_AFFINITY[brief.goal];
  const goalHits = brief.desiredPlatforms.filter((p) => affinity.includes(p)).length;
  const kw = Math.min(brief.keywords.length, 5);
  const trafficPotential: Score =
    dataSufficiency === "INSUFFICIENT"
      ? {
          value: null,
          kind: "UNAVAILABLE",
          criteria: "목표-플랫폼 성향 일치 수, 키워드 수, 입력 충실도 기반의 가정 점수",
          evidence: ["입력 정보가 부족하여 산출하지 않았습니다."],
        }
      : {
          value: clamp(20 + goalHits * 12 + kw * 6 + (dataSufficiency === "SUFFICIENT" ? 10 : 0)),
          kind: "ESTIMATE",
          criteria: "20 + 목표 성향 일치 플랫폼×12 + 키워드 수(최대 5)×6 + 입력 충실 시 10. 실측 데이터 없이 만든 추정치이며 실제 유입 예측이 아닙니다.",
          evidence: [`목표 성향 일치 플랫폼 ${goalHits}개`, `키워드 ${brief.keywords.length}개`],
        };

  // 6) 광고 정책 위험도 (높을수록 위험)
  const cat = TAXONOMY.find((c) => c.name === cls.category);
  const risky = findRiskyPhrases(briefText);
  const bannedInBrief = brief.bannedKeywords.filter((k) => k && norm(`${brief.title} ${brief.description}`).includes(norm(k)));
  const sensitivePts = cat?.sensitive === "HIGH" ? 45 : cat?.sensitive === "MEDIUM" ? 25 : 0;
  const policyRisk: Score = {
    value: clamp(10 + sensitivePts + risky.length * 12 + bannedInBrief.length * 10),
    kind: "ESTIMATE",
    criteria: "기본 10 + 민감 분야(높음 45/보통 25) + 과장·단정 표현 1건당 12 + 금지 키워드 사용 1건당 10. 높을수록 위험",
    evidence: [
      cat?.sensitive ? `민감 분야: ${cls.category} (${cat.sensitive === "HIGH" ? "높음" : "보통"})` : "민감 분야 아님",
      risky.length ? `과장·단정 표현: ${risky.join(", ")}` : "과장·단정 표현 없음",
      ...(bannedInBrief.length ? [`의뢰문에 금지 키워드 사용: ${bannedInBrief.join(", ")}`] : []),
    ],
  };
  if (cat?.sensitive === "HIGH")
    notes.push(`${cls.category} 분야는 플랫폼별 광고 제한(사전 인증·표시 의무)이 있을 수 있어 정책 센터 확인이 필요합니다.`);

  return {
    engine: ENGINE_VERSION,
    category: cls.category,
    subcategory: cls.subcategory,
    categoryConfidence: cls.confidence,
    matchedKeywords: cls.matched,
    dataSufficiency,
    scores: { topicFit, targetFit, brandFit, contentRelevance, trafficPotential, policyRisk },
    notes,
  };
}

export interface CandidateForScoring {
  platform: PlatformKey;
  title: string;
  summary: string;
  category?: string | null;
}

export interface CandidateScore {
  category: string;
  targetMatch: number;
  relevanceScore: number;
  suitable: boolean;
  note: string;
}

/** 후보 게시물이 특정 캠페인에 얼마나 적합한지 산출 */
export function scoreCandidate(
  cand: CandidateForScoring,
  brief: Pick<BriefForAnalysis, "keywords" | "bannedKeywords" | "coreTarget" | "desiredPlatforms"> & {
    category?: string | null;
  },
  brand: Pick<BrandForAnalysis, "coreTarget" | "bannedPhrases"> | null,
): CandidateScore {
  const text = `${cand.title} ${cand.summary}`;
  const t = norm(text);
  const category = cand.category ?? classify(text).category;
  const reasons: string[] = [];

  const kwHits = brief.keywords.filter((k) => k && t.includes(norm(k)));
  const sameCat = !!brief.category && category === brief.category;
  const platformOk = brief.desiredPlatforms.includes(cand.platform);
  const relevanceScore = clamp(15 + (sameCat ? 35 : 0) + Math.min(kwHits.length, 4) * 10 + (platformOk ? 10 : 0));
  reasons.push(sameCat ? `분류 일치(${category})` : `분류 불일치(게시물: ${category} / 캠페인: ${brief.category ?? "미분석"})`);
  reasons.push(kwHits.length ? `키워드 일치: ${kwHits.join(", ")}` : "캠페인 키워드 미포함");
  reasons.push(platformOk ? "희망 SNS 에 포함된 플랫폼" : "희망 SNS 가 아닌 플랫폼");

  const targetText = `${brief.coreTarget} ${brand?.coreTarget ?? ""}`;
  const o = overlap(text, targetText);
  const targetMatch = targetText.trim() ? clamp(25 + o.ratio * 75 + (sameCat ? 10 : 0)) : 40;
  if (o.common.length) reasons.push(`타깃 표현 일치: ${o.common.slice(0, 5).join(", ")}`);

  const banned = [...brief.bannedKeywords, ...(brand?.bannedPhrases ?? [])].filter((k) => k && t.includes(norm(k)));
  const sensitive = TAXONOMY.find((c) => c.name === category)?.sensitive === "HIGH" && category !== brief.category;
  let suitable = relevanceScore >= 50 && banned.length === 0 && !sensitive;
  if (banned.length) reasons.push(`금지 키워드 포함: ${banned.join(", ")} → 부적합`);
  if (sensitive) reasons.push(`민감 분야(${category}) 게시물 → 부적합`);
  if (relevanceScore < 50 && !banned.length && !sensitive) reasons.push("관련성 50 미만 → 부적합");
  if (cand.title.trim().length < 2) suitable = false;

  return { category, targetMatch, relevanceScore, suitable, note: reasons.join(" · ") };
}
