import { beforeAll, describe, expect, it } from "vitest";
import { prisma } from "@/lib/db";
import { ForbiddenError, NotFoundError } from "@/lib/auth/context";
import { DemoProvider } from "@/lib/ai/demo-provider";
import { createClient } from "@/lib/services/clients";
import { createCampaign, getCampaign } from "@/lib/services/campaigns";
import { decideContent, editContent, generateContent, submitForReview } from "@/lib/services/content";
import { decideRequest, latestRequestFor, listRequests, myInboxCount } from "@/lib/services/approvals";
import { convertInquiry, createInquiry, getInquiry, saveQuote } from "@/lib/services/inquiries";
import { saveTeam, setUserTeam } from "@/lib/services/teams";
import { briefSchema, clientSchema } from "@/lib/validation/schemas";
import { ctxOf, makeOrg } from "./helpers";

let A: Awaited<ReturnType<typeof makeOrg>>;
let B: Awaited<ReturnType<typeof makeOrg>>;
let clientId: string;
let campaignId: string;

beforeAll(async () => {
  A = await makeOrg("ap-a");
  B = await makeOrg("ap-b");
  await prisma.approvalRule.createMany({
    data: [
      { organizationId: A.org.id, gate: "CONTENT", name: "2단계 문구", steps: ["REVIEWER", "ADMIN"] },
      { organizationId: A.org.id, gate: "QUOTE", name: "50만원 이상", minAmount: 500_000, steps: ["ADMIN"] },
      { organizationId: A.org.id, gate: "CONTRACT", name: "50만원 이상 계약", minAmount: 500_000, steps: ["ADMIN"], aiPrecheck: false },
    ],
  });
  const admin = await ctxOf(A.users.admin.id);
  clientId = (await createClient(admin, clientSchema.parse({ name: "결재 테스트 고객", contactName: "담당", budget: "0", bannedPhrases: "최저가" }))).id;
  campaignId = (
    await createCampaign(admin, briefSchema.parse({ clientId, title: "결재 캠페인", targetType: "PRODUCT", goal: "PURCHASES", budget: "0", desiredPlatforms: ["INSTAGRAM"], keywords: "원두", description: "원두 정기구독 캠페인 설명입니다." }))
  ).id;
});

describe("팀 기반 조직", () => {
  it("gives team members and the team lead access to the team's clients", async () => {
    const admin = await ctxOf(A.users.admin.id);
    expect((await ctxOf(A.users.writer.id)).clientIds).not.toContain(clientId);
    const team = await saveTeam(admin, null, { name: "콘텐츠팀", description: "", leadId: A.users.reviewer.id });
    await prisma.client.update({ where: { id: clientId }, data: { teamId: team.id } });
    await setUserTeam(admin, A.users.writer.id, team.id);
    expect((await ctxOf(A.users.writer.id)).clientIds).toContain(clientId);
    expect((await ctxOf(A.users.reviewer.id)).clientIds).toContain(clientId); // 팀장
    expect((await ctxOf(A.users.viewer.id)).clientIds).not.toContain(clientId);
    await expect(saveTeam(await ctxOf(A.users.manager.id), null, { name: "x", description: "", leadId: null })).rejects.toBeInstanceOf(ForbiddenError);
  });
});

describe("다단계 문구 결재", () => {
  it("routes through reviewer then admin, enforcing order and segregation of duties", async () => {
    const writer = await ctxOf(A.users.writer.id);
    await generateContent(writer, { campaignId, types: ["COMMENT"] }, new DemoProvider());
    const content = await prisma.generatedContent.findFirstOrThrow({ where: { campaignId } });
    await submitForReview(writer, [content.id]);
    const req = (await latestRequestFor(await ctxOf(A.users.admin.id), "GeneratedContent", content.id))!;
    expect(req.steps.map((s) => s.requiredRole)).toEqual(["REVIEWER", "ADMIN"]);

    const reviewer = await ctxOf(A.users.reviewer.id);
    expect(await myInboxCount(reviewer)).toBe(1);
    const admin = await ctxOf(A.users.admin.id);
    expect(await myInboxCount(await ctxOf(A.users.manager.id))).toBe(0); // 매니저 차례 아님

    await decideContent(reviewer, content.id, "APPROVED");
    expect((await prisma.generatedContent.findUniqueOrThrow({ where: { id: content.id } })).status).toBe("PENDING_REVIEW");
    // 같은 사람이 두 단계를 결재할 수 없음 (검토자는 2단계 역할도 아님)
    await expect(decideRequest(reviewer, req.id, "APPROVED")).rejects.toBeInstanceOf(ForbiddenError);
    expect(await myInboxCount(admin)).toBe(1);
    expect(await decideRequest(admin, req.id, "APPROVED")).toBe("APPROVED");
    expect((await prisma.generatedContent.findUniqueOrThrow({ where: { id: content.id } })).status).toBe("APPROVED");
    expect(await prisma.approval.count({ where: { contentId: content.id, decision: "APPROVED" } })).toBe(1);
    expect((await getCampaign(admin, campaignId)).status).toBe("APPROVED");
  });

  it("lets the AI pre-check block approval but allow rejection", async () => {
    const writer = await ctxOf(A.users.writer.id);
    await generateContent(writer, { campaignId, types: ["SNS_POST"] }, new DemoProvider());
    const c = await prisma.generatedContent.findFirstOrThrow({ where: { campaignId, type: "SNS_POST" } });
    await editContent(writer, c.id, `${c.body} 최저가 보장`, "금지어 테스트");
    await submitForReview(writer, [c.id]);
    const req = (await latestRequestFor(await ctxOf(A.users.admin.id), "GeneratedContent", c.id))!;
    expect((req.aiReview as { passed: boolean }).passed).toBe(false);
    expect(req.risk).not.toBe("LOW");
    const reviewer = await ctxOf(A.users.reviewer.id);
    await expect(decideRequest(reviewer, req.id, "APPROVED")).rejects.toThrow("AI 1차 검토");
    await expect(decideRequest(reviewer, req.id, "REJECTED")).rejects.toThrow("사유");
    await decideRequest(reviewer, req.id, "REJECTED", "금지어 포함");
    expect((await prisma.generatedContent.findUniqueOrThrow({ where: { id: c.id } })).status).toBe("REJECTED");
  });
});

describe("견적·계약 결재", () => {
  const TEXT = "'결재샤브' 브랜드 광고대행 문의드립니다. 예산은 얼마나 잡아야 할지, 광고 종류 추천 부탁드립니다.";

  it("holds large quotes for admin approval and blocks contract conversion meanwhile", async () => {
    const m = await ctxOf(A.users.manager.id);
    const q = await createInquiry(m, { source: "KMONG", customerName: "결재고객", rawText: TEXT });
    const full = await getInquiry(m, q.id);
    const premium = full.planData!.tiers.find((t) => t.key === "PREMIUM")!;
    expect(premium.total).toBeGreaterThanOrEqual(500_000);
    expect((await saveQuote(m, q.id, "PREMIUM", full.replyDraft!)).pendingApproval).toBe(true);
    expect((await getInquiry(m, q.id)).status).toBe("PENDING_APPROVAL");
    await expect(convertInquiry(m, q.id, "PREMIUM")).rejects.toThrow("견적 결재");
    const req = (await latestRequestFor(m, "Inquiry", q.id, "QUOTE"))!;
    await expect(decideRequest(m, req.id, "APPROVED")).rejects.toBeInstanceOf(ForbiddenError); // 요청자·역할
    await decideRequest(await ctxOf(A.users.admin.id), req.id, "APPROVED");
    expect((await getInquiry(m, q.id)).status).toBe("QUOTED");
  });

  it("blocks quotes promising results or direct payment", async () => {
    const m = await ctxOf(A.users.manager.id);
    const q = await createInquiry(m, { source: "KMONG", customerName: "직거래", rawText: TEXT });
    await saveQuote(m, q.id, "PREMIUM", "상위노출 보장! 계좌로 입금하시면 10% 할인");
    const req = (await latestRequestFor(m, "Inquiry", q.id, "QUOTE"))!;
    await expect(decideRequest(await ctxOf(A.users.admin.id), req.id, "APPROVED")).rejects.toThrow("AI 1차 검토");
  });

  it("converts the inquiry automatically after contract approval, under the requester's name", async () => {
    const m = await ctxOf(A.users.manager.id);
    const q = await createInquiry(m, { source: "KMONG", customerName: "계약고객", rawText: TEXT });
    const full = await getInquiry(m, q.id);
    await saveQuote(m, q.id, "BASIC", full.replyDraft!);
    const basic = full.planData!.tiers.find((t) => t.key === "BASIC")!;
    if ((await getInquiry(m, q.id)).status === "PENDING_APPROVAL") {
      await decideRequest(await ctxOf(A.users.admin.id), (await latestRequestFor(m, "Inquiry", q.id, "QUOTE"))!.id, "APPROVED");
    }
    const r = await convertInquiry(m, q.id, "PREMIUM");
    expect(r.pending).toBe(true);
    expect((await getInquiry(m, q.id)).status).not.toBe("WON");
    const req = (await latestRequestFor(m, "Inquiry", q.id, "CONTRACT"))!;
    expect((req.payload as { tier: string }).tier).toBe("PREMIUM");
    await decideRequest(await ctxOf(A.users.admin.id), req.id, "APPROVED");
    const after = await getInquiry(m, q.id);
    expect(after.status).toBe("WON");
    const m2 = await ctxOf(A.users.manager.id);
    expect(m2.clientIds).toContain(after.clientId); // 요청자(매니저)가 새 고객 담당
    const camp = await getCampaign(m2, after.campaignId!);
    expect(camp.ownerId).toBe(A.users.manager.id);
    expect(camp.budget).toBeGreaterThan(basic.total);
  });

  it("isolates approval requests between organizations", async () => {
    const reqA = (await listRequests(await ctxOf(A.users.admin.id))).length;
    expect(reqA).toBeGreaterThan(0);
    expect(await listRequests(await ctxOf(B.users.admin.id))).toHaveLength(0);
    const any = await prisma.approvalRequest.findFirstOrThrow({ where: { organizationId: A.org.id, status: "PENDING" } });
    await expect(decideRequest(await ctxOf(B.users.admin.id), any.id, "APPROVED")).rejects.toBeInstanceOf(NotFoundError);
  });
});
