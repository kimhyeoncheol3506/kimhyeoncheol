import { describe, expect, it } from "vitest";
import { chargeFor, churnSignals, dmDraft, failureSignals, MONTHLY_PLANS, priceRaiseSignal, QC_KEYS, spinoffConditions } from "@/lib/business/playbook";
import { currentWeek, ROADMAP, ROADMAP_KEYS } from "@/lib/business/roadmap";
import { parseProspectLines } from "@/lib/services/sales";
import { reviewContent } from "@/lib/approval/ai-review";
import { DemoProvider } from "@/lib/ai/demo-provider";
import type { GenerationContext } from "@/lib/ai/types";

const DAY = 86_400_000;

describe("사업 실행 백과 규칙", () => {
  it("packages follow the book and first paid month is discounted", () => {
    expect(MONTHLY_PLANS.map((p) => p.monthlyFee)).toEqual([150_000, 290_000, 590_000, 990_000]);
    expect(chargeFor({ monthlyFee: 290_000, firstMonthDiscount: 50 }, true)).toBe(145_000);
    expect(chargeFor({ monthlyFee: 290_000, firstMonthDiscount: 50 }, false)).toBe(290_000);
  });

  it("diagnostic DM mentions the shop and never claims AI or pressure", () => {
    const dm = dmDraft({ name: "하늘미용실", lastPostAt: new Date(Date.now() - 100 * DAY) }, "동네 SNS 파트너");
    expect(dm).toContain("하늘미용실 사장님");
    expect(dm).toContain("멈춰");
    expect(dm).toContain("무료로 20초 릴스 시안");
    expect(dm).not.toMatch(/AI|오늘 계약|지금 바로 결제/);
  });

  it("churn, failure, price-raise and spin-off signals", () => {
    const now = new Date("2026-10-26T00:00:00Z");
    expect(churnSignals({ reportViewedAt: null, pendingClientApprovals: 2, oldestPendingDays: 4, missedPayments: 1 }, now)).toHaveLength(3);
    expect(churnSignals({ reportViewedAt: new Date(now.getTime() - 3 * DAY), pendingClientApprovals: 0, oldestPendingDays: 0, missedPayments: 0 }, now)).toEqual([]);
    expect(failureSignals({ monthlyRevenue: [400, 300, 200, 100], newInquiriesThisMonth: 0, cashReserve: 100, fixedCosts: 100 })).toHaveLength(3);
    expect(failureSignals({ monthlyRevenue: [100, 200], newInquiriesThisMonth: 3, cashReserve: null, fixedCosts: 100 })).toEqual([]);
    expect(priceRaiseSignal(1)).toBeNull();
    expect(priceRaiseSignal(2)).toContain("20%");
    expect(spinoffConditions({ monthlyProfit: [1_000_000, 1_200_000, 1_100_000], manualDocs: 10, churnRatePct: 5 }).every((c) => c.ok)).toBe(true);
    expect(spinoffConditions({ monthlyProfit: [1_000_000, 900_000, 1_100_000], manualDocs: 3, churnRatePct: null }).some((c) => c.ok)).toBe(false);
  });

  it("roadmap keys are unique and the week is computed from the start date", () => {
    expect(new Set(ROADMAP_KEYS).size).toBe(ROADMAP_KEYS.length);
    expect(ROADMAP[0].weeks).toEqual([1, 4]);
    expect(currentWeek(null)).toBeNull();
    expect(currentWeek(new Date("2026-10-01T00:00:00Z"), new Date("2026-10-16T00:00:00Z"))).toBe(3);
    expect(QC_KEYS).toHaveLength(7);
  });

  it("parses pasted spreadsheet rows (comma or tab) and skips a header", () => {
    const { rows, errors } = parseProspectLines("가게이름,업종,지역,인스타,팔로워,마지막게시일,월게시수\n하늘 미용실, 미용실, 망원동, @haneul, 1,200, 2026-07-02, 1\n결\t미용실\t망원동\t\t\t2026/07/02\t");
    expect(rows).toHaveLength(2);
    expect(rows[0]).toMatchObject({ name: "하늘 미용실", region: "망원동", instagram: "@haneul", followers: 1, postsPerMonth: null });
    expect(errors.some((e) => e.includes("YYYY-MM-DD"))).toBe(true);
  });
});

describe("가게 본인 계정 운영대행", () => {
  const ctx: GenerationContext = {
    clientName: "하늘 미용실", campaignName: "가을 펌", goal: "VISITS", targetType: "OTHER", coreTarget: "직장인", keywords: ["펌"], bannedKeywords: [], description: "가을 펌",
    brand: { companyIntro: "", productDescription: "자연스러운 펌을 합니다.", toneOfVoice: "", bannedPhrases: [], requiredPhrases: [] }, platform: "INSTAGRAM",
  };
  it("drops third-party ad tags on the shop's own account but still blocks fake reviews", async () => {
    const own = await new DemoProvider().generate({ ...ctx, ownAccount: true }, ["SNS_POST", "SHORT_SCRIPT", "YOUTUBE_META"]);
    for (const d of own.drafts) expect(d.body).not.toMatch(/#광고|유료 광고|\(광고\)/);
    const third = await new DemoProvider().generate(ctx, ["SNS_POST"]);
    expect(third.drafts[0].body).toContain("#광고");
    expect(reviewContent({ body: own.drafts[0].body, disclosure: "", warnings: [], bannedPhrases: [], ownAccount: true }).passed).toBe(true);
    expect(reviewContent({ body: own.drafts[0].body, disclosure: "", warnings: [], bannedPhrases: [] }).passed).toBe(false);
    expect(reviewContent({ body: "제가 직접 해보니 좋아요", disclosure: "", warnings: [], bannedPhrases: [], ownAccount: true }).passed).toBe(false);
  });
});
