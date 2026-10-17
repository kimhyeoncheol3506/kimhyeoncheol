import { describe, expect, it } from "vitest";
import { DemoProvider } from "@/lib/ai/demo-provider";
import { FAKE_EXPERIENCE_PATTERNS, inspectDraft } from "@/lib/ai/guardrails";
import { ALL_CONTENT_TYPES } from "@/lib/services/content";
import { hasDisclosure } from "@/lib/services/publications";

const ctx = {
  clientName: "테스트커피",
  campaignName: "원두 구독",
  goal: "PURCHASES",
  targetType: "PRODUCT",
  coreTarget: "홈카페 직장인",
  keywords: ["원두", "홈카페"],
  bannedKeywords: [],
  description: "원두 정기구독",
  targetUrl: "https://coffee.example",
  brand: { companyIntro: "로스터리", productDescription: "매주 로스팅한 원두를 배송합니다.", toneOfVoice: "", bannedPhrases: ["최저가"], requiredPhrases: ["#테스트커피"] },
  candidate: { platform: "INSTAGRAM" as const, accountName: "@x", title: "홈카페 루틴", summary: "" },
};

describe("DemoProvider", () => {
  it("generates every content type with ad disclosure and without fake experiences", async () => {
    const r = await new DemoProvider().generate(ctx, ALL_CONTENT_TYPES);
    expect(r.ok).toBe(true);
    expect(r.drafts).toHaveLength(ALL_CONTENT_TYPES.length);
    expect(r.costKrw).toBe(0);
    for (const d of r.drafts) {
      expect(hasDisclosure(d.body), `${d.type} 에 광고 표시 없음`).toBe(true);
      for (const p of FAKE_EXPERIENCE_PATTERNS) expect(d.body).not.toContain(p);
      expect(d.body).not.toContain("최저가");
      expect(d.body, `${d.type} 에 필수 표현 없음`).toContain("#테스트커피");
    }
  });
});

describe("inspectDraft", () => {
  it("flags fake testimonials, banned phrases, exaggeration and missing required phrases", () => {
    const w = inspectDraft("제가 써봤는데 최저가 100% 만족", { bannedPhrases: ["최저가"], requiredPhrases: ["#브랜드"] });
    expect(w.some((x) => x.includes("허위 체험담"))).toBe(true);
    expect(w.some((x) => x.includes("금지 표현"))).toBe(true);
    expect(w.some((x) => x.includes("과장"))).toBe(true);
    expect(w.some((x) => x.includes("필수 표현 누락"))).toBe(true);
    expect(inspectDraft("정보 공유드립니다 #브랜드 (광고)", { bannedPhrases: [], requiredPhrases: ["#브랜드"] })).toEqual([]);
  });
});
