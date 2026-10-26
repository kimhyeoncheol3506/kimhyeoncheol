import { describe, expect, it } from "vitest";
import { resolveRule, riskFromScore, roleCanDecide, type RuleLike } from "@/lib/approval/rules";
import { reviewContent, reviewQuote } from "@/lib/approval/ai-review";
import { AI_STAFF, staffByKey } from "@/lib/company/staff";

const r = (o: Partial<RuleLike>): RuleLike => ({ id: Math.random().toString(), gate: "QUOTE", minAmount: null, minRisk: null, steps: [], aiPrecheck: true, active: true, ...o });

describe("resolveRule", () => {
  const rules = [r({ id: "q1", minAmount: 1_000_000, steps: ["ADMIN"] }), r({ id: "q3", minAmount: 3_000_000, steps: ["CAMPAIGN_MANAGER", "ADMIN"] }), r({ id: "off", minAmount: 0, steps: ["REVIEWER", "CAMPAIGN_MANAGER", "ADMIN"], active: false })];
  it("applies amount thresholds and picks the strictest matching rule", () => {
    expect(resolveRule(rules, { gate: "QUOTE", amount: 500_000 }).steps).toEqual([]);
    expect(resolveRule(rules, { gate: "QUOTE", amount: 1_200_000 }).rule?.id).toBe("q1");
    expect(resolveRule(rules, { gate: "QUOTE", amount: 5_000_000 }).steps).toEqual(["CAMPAIGN_MANAGER", "ADMIN"]);
  });
  it("applies risk thresholds", () => {
    const c = [r({ gate: "CONTENT", steps: ["REVIEWER"] }), r({ gate: "CONTENT", minRisk: "HIGH", steps: ["REVIEWER", "ADMIN"] })];
    expect(resolveRule(c, { gate: "CONTENT", risk: "MEDIUM" }).steps).toEqual(["REVIEWER"]);
    expect(resolveRule(c, { gate: "CONTENT", risk: "HIGH" }).steps).toEqual(["REVIEWER", "ADMIN"]);
  });
  it("always requires at least one human approval for ad content", () => {
    expect(resolveRule([], { gate: "CONTENT" }).steps).toEqual(["REVIEWER"]);
    expect(resolveRule([], { gate: "CONTRACT", amount: 9e9 }).steps).toEqual([]);
  });
});

describe("roles & risk", () => {
  it("lets admins act on any step but others only on their own role", () => {
    expect(roleCanDecide("ADMIN", "REVIEWER")).toBe(true);
    expect(roleCanDecide("REVIEWER", "REVIEWER")).toBe(true);
    expect(roleCanDecide("REVIEWER", "ADMIN")).toBe(false);
    expect(roleCanDecide("CAMPAIGN_MANAGER", "REVIEWER")).toBe(false);
  });
  it("maps policy risk scores and warnings", () => {
    expect(riskFromScore(10, false)).toBe("LOW");
    expect(riskFromScore(10, true)).toBe("MEDIUM");
    expect(riskFromScore(70, false)).toBe("HIGH");
    expect(riskFromScore(null, false)).toBe("LOW");
  });
});

describe("compliance agent (AI 1차 검토)", () => {
  it("blocks missing disclosure, fake testimonials and banned phrases; warns on hype", () => {
    expect(reviewContent({ body: "좋은 원두 소개", disclosure: "", warnings: [], bannedPhrases: [] }).passed).toBe(false);
    const fake = reviewContent({ body: "제가 써봤는데 최고", disclosure: "[광고]", warnings: [], bannedPhrases: [] });
    expect(fake.passed).toBe(false);
    expect(fake.findings.some((f) => f.severity === "warn" && f.message.includes("과장"))).toBe(true);
    expect(reviewContent({ body: "최저가 원두", disclosure: "[광고]", warnings: [], bannedPhrases: ["최저가"] }).passed).toBe(false);
    expect(reviewContent({ body: "원두 정기구독 안내", disclosure: "[광고] 협찬", warnings: [], bannedPhrases: [] })).toEqual({ agent: "compliance", passed: true, findings: [] });
  });
  it("blocks guaranteed results and off-platform payment in quotes", () => {
    expect(reviewQuote({ reply: "상위노출 보장해 드립니다. 광고·협찬 표시", total: 100, mediaSpendSeparate: false }).passed).toBe(false);
    expect(reviewQuote({ reply: "계좌로 입금 주시면 할인. 광고·협찬 표시", total: 100, mediaSpendSeparate: false }).passed).toBe(false);
    const ok = reviewQuote({ reply: "광고·협찬 표시를 합니다.", total: 100, mediaSpendSeparate: true });
    expect(ok.passed).toBe(true);
    expect(ok.findings[0].message).toContain("매체비");
  });
});

describe("AI staff roster", () => {
  it("has a secretary plus ten staff, and every hand-off points at a real staff member or the captain", () => {
    expect(AI_STAFF.map((a) => a.key)).toEqual(["secretary", "sales", "intake", "strategist", "copywriter", "shortform", "compliance", "publisher", "analyst", "success", "finance"]);
    expect(AI_STAFF.filter((a) => a.handsOffTo).map((a) => a.handsOffTo)).toEqual(["QUOTE", "CONTENT", "CONTENT"]);
    for (const s of AI_STAFF) {
      if (s.next && s.next !== "captain") expect(staffByKey(s.next), `${s.key}.next`).toBeDefined();
      expect(s.steps.length).toBeGreaterThan(1);
      expect(s.doesNot.length).toBeGreaterThan(0);
    }
  });
});
