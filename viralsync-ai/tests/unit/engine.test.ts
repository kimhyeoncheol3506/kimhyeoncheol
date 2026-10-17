import { describe, expect, it } from "vitest";
import { analyzeBrief, classify, scoreCandidate } from "@/lib/analysis/engine";
import { CATEGORY_NAMES } from "@/lib/analysis/taxonomy";

const brand = {
  companyIntro: "홈트 앱 회사",
  productDescription: "하루 15분 홈트 앱. 운동 기록과 맞춤 루틴 제공",
  coreTarget: "운동을 시작하려는 30대 직장인",
  toneOfVoice: "",
  bannedPhrases: ["살 빠짐 보장"],
  requiredPhrases: [],
};

describe("taxonomy", () => {
  it("has the 14 required top-level categories", () => {
    expect(CATEGORY_NAMES).toEqual(["교육", "엔터테인먼트", "시사", "정치", "역사", "경제·금융", "IT·AI", "여행·맛집", "뷰티·패션", "건강·생활", "게임", "앱·소프트웨어", "쇼핑·상품", "기타"]);
  });
});

describe("classify", () => {
  it("maps keywords to categories and subcategories", () => {
    expect(classify("민감 피부용 선크림 스킨케어").category).toBe("뷰티·패션");
    expect(classify("제주 맛집 여행 코스").category).toBe("여행·맛집");
    expect(classify("주식 투자 etf 수익률").category).toBe("경제·금융");
    const r = classify("생성형 ai 챗봇 만들기");
    expect(r.category).toBe("IT·AI");
    expect(r.subcategory).toBe("인공지능");
  });
  it("falls back to 기타 with zero confidence", () => {
    const r = classify("zzz qqq");
    expect(r.category).toBe("기타");
    expect(r.confidence).toBe(0);
  });
});

describe("analyzeBrief", () => {
  it("returns all six scores with criteria and evidence", () => {
    const r = analyzeBrief(
      {
        title: "홈트 앱 설치 캠페인",
        description: "하루 15분 홈트 앱 설치를 유도하는 캠페인. 운동 초보 직장인 대상.",
        keywords: ["홈트", "운동", "다이어트"],
        bannedKeywords: [],
        coreTarget: "30대 직장인",
        targetType: "APP",
        goal: "INSTALLS",
        desiredPlatforms: ["INSTAGRAM", "TIKTOK"],
      },
      brand,
    );
    expect(r.category).toBe("건강·생활");
    expect(r.dataSufficiency).toBe("SUFFICIENT");
    for (const s of Object.values(r.scores)) {
      expect(s.criteria.length).toBeGreaterThan(5);
      expect(s.evidence.length).toBeGreaterThan(0);
    }
    expect(r.scores.contentRelevance.value).toBe(100);
  });

  it("marks scores as unavailable instead of inventing them when data is missing", () => {
    const r = analyzeBrief(
      { title: "이벤트", description: "", keywords: [], bannedKeywords: [], coreTarget: "", targetType: "OTHER", goal: "CLICKS", desiredPlatforms: ["X"] },
      null,
    );
    expect(r.dataSufficiency).toBe("INSUFFICIENT");
    expect(r.scores.targetFit.value).toBeNull();
    expect(r.scores.brandFit.value).toBeNull();
    expect(r.scores.trafficPotential.value).toBeNull();
    expect(r.scores.trafficPotential.kind).toBe("UNAVAILABLE");
  });

  it("raises policy risk for sensitive categories and exaggerated phrases", () => {
    const low = analyzeBrief({ title: "원두 구독", description: "커피 원두 정기 배송", keywords: ["원두"], bannedKeywords: [], coreTarget: "", targetType: "PRODUCT", goal: "PURCHASES", desiredPlatforms: ["INSTAGRAM"] }, null);
    const high = analyzeBrief({ title: "주식 투자 리딩", description: "원금 보장 100% 수익 보장 주식 투자", keywords: ["주식"], bannedKeywords: [], coreTarget: "", targetType: "OTHER", goal: "INQUIRIES", desiredPlatforms: ["X"] }, null);
    expect(high.scores.policyRisk.value!).toBeGreaterThan(low.scores.policyRisk.value! + 40);
    expect(high.notes.join(" ")).toContain("경제·금융");
  });
});

describe("scoreCandidate", () => {
  const brief = { keywords: ["홈트", "운동"], bannedKeywords: ["다이어트약"], coreTarget: "30대 직장인", desiredPlatforms: ["INSTAGRAM" as const], category: "건강·생활" };
  it("scores relevant posts as suitable with reasons", () => {
    const s = scoreCandidate({ platform: "INSTAGRAM", title: "직장인 홈트 루틴", summary: "하루 15분 운동" }, brief, brand);
    expect(s.suitable).toBe(true);
    expect(s.relevanceScore).toBeGreaterThanOrEqual(50);
    expect(s.note).toContain("분류 일치");
  });
  it("marks posts with banned keywords or sensitive categories as unsuitable", () => {
    expect(scoreCandidate({ platform: "INSTAGRAM", title: "홈트 운동 다이어트약 후기", summary: "" }, brief, brand).suitable).toBe(false);
    expect(scoreCandidate({ platform: "INSTAGRAM", title: "선거 정당 공약 정리 운동", summary: "투표" }, brief, brand).suitable).toBe(false);
  });
});
