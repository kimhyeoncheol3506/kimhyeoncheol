import { beforeAll, describe, expect, it } from "vitest";
import { prisma } from "@/lib/db";
import { ForbiddenError } from "@/lib/auth/context";
import { DemoProvider } from "@/lib/ai/demo-provider";
import { QC_KEYS } from "@/lib/business/playbook";
import { createCampaign } from "@/lib/services/campaigns";
import { generateContent, submitForReview } from "@/lib/services/content";
import { decideRequest, latestRequestFor } from "@/lib/services/approvals";
import { precheck } from "@/lib/services/publications";
import { convertProspect, createProspect, importProspects, salesStats, setStage } from "@/lib/services/sales";
import { createSubscription, getSubscription, markPaid, refreshSubscription, startPaid } from "@/lib/services/subscriptions";
import { clientCare, ensurePortalToken, getPortal, portalDecide } from "@/lib/services/portal";
import { financeSummary, saveBusinessProfile, saveFixedCost, toggleRoadmap, roadmapChecks } from "@/lib/services/business";
import { briefSchema } from "@/lib/validation/schemas";
import { ctxOf, makeOrg } from "./helpers";

let A: Awaited<ReturnType<typeof makeOrg>>;
let clientId: string;

beforeAll(async () => {
  A = await makeOrg("biz");
});

describe("영업 리스트", () => {
  it("adds, imports without duplicates, records DM and converts to an own-account client", async () => {
    const m = await ctxOf(A.users.manager.id);
    await expect(createProspect(await ctxOf(A.users.writer.id), { name: "x", industry: "", region: "" })).rejects.toBeInstanceOf(ForbiddenError);
    const p = await createProspect(m, { name: "하늘미용실", industry: "미용실", region: "망원동", instagram: "@haneul" });
    const r = await importProspects(m, "하늘미용실, 미용실, 망원동, @haneul\n결미용실, 미용실, 망원동, @gyeol, 300, 2026-06-01, 0");
    expect(r).toMatchObject({ created: 1, skipped: 1 });
    const sent = await setStage(m, p.id, "DM_SENT");
    expect(sent.dmSentAt).not.toBeNull();
    const s = await salesStats(m);
    expect(s.dmToday).toBe(1);
    expect(s.total).toBe(2);

    const conv = await convertProspect(m, p.id);
    clientId = conv.clientId;
    const client = await prisma.client.findUniqueOrThrow({ where: { id: clientId } });
    expect(client).toMatchObject({ ownAccount: true, industry: "미용실", promoUrl: "https://www.instagram.com/haneul" });
    expect((await ctxOf(A.users.manager.id)).clientIds).toContain(clientId); // 등록한 매니저가 담당
    expect((await convertProspect(m, p.id)).created).toBe(false);
  });
});

describe("월 정액 계약", () => {
  it("trial → paid (50% first month) → overdue twice suspends → paying resumes", async () => {
    const m = await ctxOf(A.users.manager.id);
    const sub = await createSubscription(m, { clientId, planName: "라이트", monthlyFee: 290_000, deliverables: ["릴스 8편"], vatIncluded: false, billingDay: 25, trial: true, startDate: new Date(), portfolioConsent: true, caseStudyConsent: false, referredById: null, notes: "" });
    expect(sub.status).toBe("TRIAL");
    expect(sub.trialEnd!.getTime() - sub.trialStart!.getTime()).toBe(14 * 86_400_000);
    await expect(createSubscription(m, { clientId, planName: "라이트", monthlyFee: 290_000, deliverables: [], vatIncluded: false, billingDay: 25, trial: true, startDate: new Date(), portfolioConsent: true, caseStudyConsent: false, referredById: null, notes: "" })).rejects.toThrow("진행 중인 계약");

    await startPaid(m, sub.id);
    let s = await getSubscription(m, sub.id);
    expect(s.status).toBe("ACTIVE");
    expect(s.payments).toHaveLength(1);
    expect(s.payments[0].amount).toBe(145_000);
    expect(await prisma.prospect.count({ where: { clientId, stage: "WON" } })).toBe(1);

    // 지난 두 달 미납을 만들어 자동 중지 확인
    const past = (n: number) => new Date(Date.now() - n * 30 * 86_400_000);
    for (const n of [2, 1]) await prisma.payment.create({ data: { organizationId: A.org.id, subscriptionId: sub.id, period: `2000-0${n}`, amount: 290_000, dueDate: past(n) } });
    expect(await refreshSubscription(m, sub.id)).toMatchObject({ status: "SUSPENDED", missed: 2 });
    s = await getSubscription(m, sub.id);
    await markPaid(m, s.payments.find((p) => p.period === "2000-01")!.id, true);
    expect((await getSubscription(m, sub.id)).status).toBe("ACTIVE");
    expect(await prisma.auditLog.count({ where: { organizationId: A.org.id, action: { in: ["subscription.suspend", "subscription.resume"] } } })).toBe(2);
  });
});

describe("가게 본인 계정: 내부 결재 + 검수 7개 + 사장님 승인", () => {
  it("requires the QC checklist, then the owner's approval via the portal link before posting", async () => {
    await prisma.clientAccess.createMany({ data: [A.users.writer.id, A.users.reviewer.id].map((userId) => ({ userId, clientId })) });
    const admin = await ctxOf(A.users.admin.id);
    const writer = await ctxOf(A.users.writer.id);
    const campaignId = (await createCampaign(admin, briefSchema.parse({ clientId, title: "가을 펌", targetType: "REELS", goal: "VISITS", budget: "0", desiredPlatforms: ["INSTAGRAM"], keywords: "펌", description: "가을 펌 릴스 운영입니다." }))).id;
    const g = await generateContent(writer, { campaignId, platform: "INSTAGRAM", types: ["SNS_POST"] }, new DemoProvider());
    const content = await prisma.generatedContent.findUniqueOrThrow({ where: { id: g.ids[0] } });
    expect(content.disclosure).toBe("");
    expect(content.body).not.toContain("#광고");
    await submitForReview(writer, [content.id]);
    const req = (await latestRequestFor(admin, "GeneratedContent", content.id))!;
    expect((req.aiReview as { passed: boolean }).passed).toBe(true);

    const reviewer = await ctxOf(A.users.reviewer.id);
    await expect(decideRequest(reviewer, req.id, "APPROVED", undefined, QC_KEYS.slice(0, 6))).rejects.toThrow("6/7");
    await decideRequest(reviewer, req.id, "APPROVED", undefined, QC_KEYS);
    const step = await prisma.approvalStep.findFirstOrThrow({ where: { requestId: req.id } });
    expect(step.checklist).toHaveLength(7);
    expect((await prisma.generatedContent.findUniqueOrThrow({ where: { id: content.id } })).clientStatus).toBe("PENDING");

    const pc = await precheck(await ctxOf(A.users.manager.id), content.id, "INSTAGRAM");
    expect(pc.items.find((i) => i.key === "disclosure")?.passed).toBe(true);
    expect(pc.items.find((i) => i.key === "clientApproval")?.passed).toBe(false);
    expect(pc.ok).toBe(false);

    await expect(ensurePortalToken(await ctxOf(A.users.viewer.id), clientId)).rejects.toBeInstanceOf(ForbiddenError);
    const token = await ensurePortalToken(admin, clientId);
    expect(token).toMatch(/^[A-Za-z0-9_-]{32}$/);
    expect(await getPortal("x".repeat(32))).toBeNull();
    const portal = (await getPortal(token))!;
    expect(portal.pending.map((p) => p.id)).toEqual([content.id]);
    expect((await clientCare(admin, clientId)).pendingApprovals).toBe(1);

    await expect(portalDecide(token, content.id, "CHANGES_REQUESTED", " ")).rejects.toThrow("한 줄");
    await portalDecide(token, content.id, "APPROVED", "");
    expect((await precheck(await ctxOf(A.users.manager.id), content.id, "INSTAGRAM")).items.find((i) => i.key === "clientApproval")?.passed).toBe(true);
    await expect(portalDecide(token, content.id, "APPROVED", "")).rejects.toThrow("이미 처리");

    // 새 링크를 만들면 이전 링크는 못 쓴다
    const fresh = await ensurePortalToken(admin, clientId, true);
    expect(fresh).not.toBe(token);
    expect(await getPortal(token)).toBeNull();
    expect(await prisma.auditLog.count({ where: { organizationId: A.org.id, action: "portal.approve", actorId: null } })).toBe(1);
  });
});

describe("재무·실행표", () => {
  it("computes tax reserve, salary cap, reserve target and failure signals; only admins edit", async () => {
    const admin = await ctxOf(A.users.admin.id);
    const m = await ctxOf(A.users.manager.id);
    await expect(saveFixedCost(m, null, { name: "x", category: "기타", monthlyKrw: 1, active: true })).rejects.toBeInstanceOf(ForbiddenError);
    await saveFixedCost(admin, null, { name: "AI 구독", category: "도구·구독", monthlyKrw: 90_000, active: true });
    await saveFixedCost(admin, null, { name: "건강보험", category: "보험·세금", monthlyKrw: 160_000, active: true });
    await saveBusinessProfile(admin, { positioning: "동네 사장님 SNS 파트너", targetIndustry: "미용실", businessStartDate: new Date(), cashReserveKrw: 300_000 });
    const f = await financeSummary(m);
    expect(f.fixedTotal).toBe(250_000);
    expect(f.toolOver).toBe(true); // 도구·구독 8만 원 초과
    expect(f.reserveTarget).toBe(750_000);
    expect(f.failure.some((x) => x.includes("2개월치"))).toBe(true);
    expect(f.taxReserve).toBe(Math.round(f.thisMonth.revenue * 0.1));
    expect(f.mrr).toBe(290_000);
    await expect(financeSummary(await ctxOf(A.users.writer.id))).rejects.toBeInstanceOf(ForbiddenError);

    await toggleRoadmap(m, "w1-assets", true);
    await toggleRoadmap(m, "w1-assets", true); // 중복 없음
    expect((await roadmapChecks(m)).has("w1-assets")).toBe(true);
    await toggleRoadmap(m, "w1-assets", false);
    expect((await roadmapChecks(m)).has("w1-assets")).toBe(false);
    await expect(toggleRoadmap(m, "nope", true)).rejects.toThrow("없는 항목");
  });
});
