import { describe, expect, it } from "vitest";
import { extractKeywords, parseInquiry } from "@/lib/inquiry/parser";
import { buildMediaPlan, type CatalogItem } from "@/lib/inquiry/planner";
import { buildReply } from "@/lib/inquiry/reply";

// 실제 문의 스크린샷을 본뜬 샘플 (상호·URL 은 가상)
const BLOG_INQUIRY = `안녕하세요 ! 데모샵 입니다 혹시 https://demo-shop.example 사이트도 블러그 가능할까요 ?
네 키워드는 강남 피부관리, 강남 왁싱, 역삼 피부샵 입니다 <
혹시 가능한지 여쭙고싶고 가격도 알고 싶습니다,`;

const SHABU_INQUIRY = `안녕하세요.
'한우담 샤브' 브랜드의 광고대행에 대해 문의드리고 싶어 연락드렸습니다.
▶홈페이지 : http://hanwoodam.example.com
▶인스타그램 : https://www.instagram.com/hanwoodam_demo

○○샤브와 비슷한 느낌의 음식점으로,
현재 ○○샤브가 하고 있는 광고와 유사한 형태로 광고하고싶습니다.

예산은 얼마정도로 잡아야 할지, 광고의 종류는 어떤 것들을 추천하는지 확인 부탁드립니다.`;

const CATALOG: CatalogItem[] = (
  [
    ["BLOG", 220000, "월", false],
    ["EXPERIENCE_GROUP", 330000, "회", false],
    ["NAVER_PLACE", 150000, "월", false],
    ["INSTAGRAM", 300000, "월", false],
    ["META_AD", 200000, "월", true],
    ["KARROT", 100000, "회", false],
    ["PACKAGE", 380000, "월", false],
  ] as const
).map(([channel, unitPrice, unit, m], i) => ({ id: `p${i}`, name: `${channel} 상품`, channel, unitPrice, unit, mediaSpendSeparate: m, active: true }));

describe("parseInquiry — 블로그 키워드 문의", () => {
  const p = parseInquiry(BLOG_INQUIRY);
  it("extracts keywords without trailing endings, link and questions", () => {
    expect(p.keywords).toEqual(["강남 피부관리", "강남 왁싱", "역삼 피부샵"]);
    expect(p.links).toEqual([{ url: "https://demo-shop.example/", kind: "HOMEPAGE" }]);
    expect(p.requestedChannels).toEqual(["BLOG"]); // '블러그' 오타도 인식
    expect(p.questions).toEqual(expect.arrayContaining(["PRICE", "FEASIBILITY"]));
    expect(p.businessType).toBe("BEAUTY");
  });
  it("asks for missing info instead of guessing", () => {
    expect(p.brand).toBeNull();
    expect(p.missingInfo).toEqual(expect.arrayContaining(["브랜드(상호)명", "월 예산 범위 (대행비 + 광고 매체비)"]));
  });
});

describe("parseInquiry — 음식점 종합광고 문의", () => {
  const p = parseInquiry(SHABU_INQUIRY);
  it("detects brand, restaurant, links and full-package intent", () => {
    expect(p.brand).toBe("한우담 샤브");
    expect(p.businessType).toBe("RESTAURANT");
    expect(p.links.map((l) => l.kind)).toEqual(["HOMEPAGE", "INSTAGRAM"]);
    expect(p.wantsFullPackage).toBe(true);
    expect(p.questions).toEqual(expect.arrayContaining(["BUDGET", "RECOMMEND"]));
    expect(p.referencesCompetitor).toBe(true);
  });
  it("does not treat a labelled Instagram link as a requested ad channel", () => {
    expect(p.requestedChannels).toEqual([]);
  });
});

describe("extractKeywords", () => {
  it("handles colon form and slashes", () => {
    expect(extractKeywords("키워드: 성수 카페 / 성수 베이커리")).toEqual(["성수 카페", "성수 베이커리"]);
    expect(extractKeywords("키워드 없음")).toEqual([]);
  });
});

describe("buildMediaPlan", () => {
  it("quotes only the requested channel in BASIC and covers every keyword", () => {
    const plan = buildMediaPlan(parseInquiry(BLOG_INQUIRY), CATALOG);
    const basic = plan.tiers.find((t) => t.key === "BASIC")!;
    expect(basic.items.map((i) => [i.channel, i.quantity])).toEqual([["BLOG", 3]]);
    expect(basic.total).toBe(660000);
    const std = plan.tiers.find((t) => t.key === "STANDARD")!;
    expect(std.items.length).toBe(2);
    expect(std.total).toBeGreaterThan(basic.total);
  });
  it("recommends restaurant playbook channels and notes media spend separately", () => {
    const plan = buildMediaPlan(parseInquiry(SHABU_INQUIRY), CATALOG);
    expect(plan.channels[0].channel).toBe("NAVER_PLACE");
    const premium = plan.tiers.find((t) => t.key === "PREMIUM")!;
    expect(premium.items.some((i) => i.channel === "META_AD")).toBe(true);
    expect(premium.mediaSpend).not.toBeNull();
    expect(plan.fullPackage?.unitPrice).toBe(380000);
    expect(plan.compliance.join(" ")).toContain("체험단");
  });
  it("excludes channels with no package in the catalog", () => {
    const plan = buildMediaPlan(parseInquiry(BLOG_INQUIRY), CATALOG.filter((c) => c.channel !== "BLOG"));
    expect(plan.channels.find((c) => c.channel === "BLOG")?.available).toBe(false);
    expect(plan.tiers.every((t) => t.items.every((i) => i.channel !== "BLOG"))).toBe(true);
    expect(plan.assumptions.join(" ")).toContain("제외");
  });
  it("picks the largest tier that fits a stated budget", () => {
    const p = parseInquiry("'숲속베이커리' 카페입니다. 성수동 매장이고 인스타랑 플레이스 관리 맡기고 싶어요. 월 50만원 정도 생각중");
    expect(p.budgetMentionedKrw).toBe(500000);
    expect(p.region).toBe("성수동");
    const plan = buildMediaPlan(p, CATALOG);
    const chosen = plan.tiers.find((t) => t.key === plan.recommendedTier)!;
    expect(chosen.total).toBeLessThanOrEqual(500000);
  });
});

describe("buildReply", () => {
  it("answers the questions, discloses ads, and never promises results or off-platform payment", () => {
    const p = parseInquiry(SHABU_INQUIRY);
    const r = buildReply({ customerName: "고객", source: "KMONG", parsed: p, plan: buildMediaPlan(p, CATALOG) });
    expect(r).toContain("‘한우담 샤브’");
    expect(r).toContain("[예상 견적]");
    expect(r).toContain("크몽 안전결제");
    expect(r).toContain("광고·협찬 표시");
    expect(r).toContain("보장해 드리지는 않습니다");
    expect(r).not.toMatch(/계좌|입금|상위노출 보장|100%/);
  });
});
