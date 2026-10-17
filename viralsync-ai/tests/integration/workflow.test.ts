import { beforeAll, describe, expect, it } from "vitest";
import { prisma } from "@/lib/db";
import { ForbiddenError } from "@/lib/auth/context";
import { DemoProvider } from "@/lib/ai/demo-provider";
import type { AIProvider } from "@/lib/ai/types";
import { createClient, updateClient, getClient } from "@/lib/services/clients";
import { createCampaign, getCampaign, runAnalysis, updateCampaign } from "@/lib/services/campaigns";
import { createCandidate, linkCandidate } from "@/lib/services/candidates";
import { decideContent, editContent, generateContent, submitForReview } from "@/lib/services/content";
import { executePublication, precheck, schedulePublication } from "@/lib/services/publications";
import { campaignSummary, dashboard, publicationRows } from "@/lib/services/reports";
import { publicationsCsv } from "@/lib/export";
import { clientSchema, briefSchema } from "@/lib/validation/schemas";
import { ctxOf, grant, makeOrg } from "./helpers";

let env: Awaited<ReturnType<typeof makeOrg>>;
let clientId: string;
let campaignId: string;

beforeAll(async () => {
  env = await makeOrg("flow");
});

describe("end-to-end campaign workflow (service layer, real DB)", () => {
  it("registers and edits a client", async () => {
    const manager = await ctxOf(env.users.manager.id);
    const input = clientSchema.parse({
      name: "통합테스트 커피",
      contactName: "홍길동",
      budget: "1000000",
      productDescription: "원두 정기구독 서비스. 매주 로스팅한 원두 배송",
      coreTarget: "홈카페 직장인",
      bannedPhrases: "최저가",
      requiredPhrases: "#테스트커피",
    });
    const c = await createClient(manager, input);
    clientId = c.id;
    // 등록한 매니저는 자동으로 접근 권한을 얻는다
    const m2 = await ctxOf(env.users.manager.id);
    expect(m2.clientIds).toContain(c.id);
    await updateClient(m2, c.id, { ...input, name: "통합테스트 커피(수정)" });
    const got = await getClient(m2, c.id);
    expect(got.name).toBe("통합테스트 커피(수정)");
    expect(got.brandProfile?.requiredPhrases).toEqual(["#테스트커피"]);
    await grant([env.users.writer.id, env.users.reviewer.id, env.users.viewer.id], c.id);
  });

  it("accepts a brief, edits it, and classifies it", async () => {
    const manager = await ctxOf(env.users.manager.id);
    const brief = briefSchema.parse({
      clientId,
      title: "원두 구독 캠페인",
      targetUrl: "https://coffee.example/sub",
      targetType: "PRODUCT",
      goal: "PURCHASES",
      coreTarget: "홈카페 직장인",
      budget: "500000",
      desiredPlatforms: ["INSTAGRAM", "X"],
      keywords: "원두, 커피, 홈카페",
      bannedKeywords: "최저가",
      description: "가을 시즌 원두 정기구독을 알리는 캠페인입니다. 홈카페 직장인 대상.",
    });
    const c = await createCampaign(manager, brief);
    campaignId = c.id;
    await updateCampaign(manager, c.id, { ...brief, title: "원두 구독 캠페인 v2" });
    const r = await runAnalysis(await ctxOf(env.users.writer.id), c.id);
    expect(r.category).toBe("쇼핑·상품");
    const cp = await getCampaign(manager, c.id);
    expect(cp.status).toBe("ANALYZED");
    expect(cp.name).toBe("원두 구독 캠페인 v2");
    expect((cp.brief?.urlCheck as { analyzed: boolean }).analyzed).toBe(false);
  });

  it("scores and links a candidate post", async () => {
    const writer = await ctxOf(env.users.writer.id);
    const cand = await createCandidate(writer, { platform: "INSTAGRAM", accountName: "@cafe", postUrl: `https://sns.example/p/${Date.now()}`, title: "홈카페 원두 추천", summary: "커피 원두 고르는 법" });
    const linked = await linkCandidate(writer, cand.id, campaignId);
    expect(linked.relevanceScore).toBeGreaterThanOrEqual(50);
    expect(linked.suitable).toBe(true);
    expect(linked.suitabilityNote).toBeTruthy();
  });

  it("generates drafts with demo provider and records cost + metadata", async () => {
    const writer = await ctxOf(env.users.writer.id);
    const cand = await prisma.contentCandidate.findFirstOrThrow({ where: { campaignId } });
    const r = await generateContent(writer, { campaignId, candidateId: cand.id, types: ["COMMENT", "SNS_POST", "INFORMATIVE"] }, new DemoProvider());
    expect(r.ok).toBe(true);
    expect(r.created).toBe(3);
    const rows = await prisma.generatedContent.findMany({ where: { campaignId } });
    expect(rows).toHaveLength(3);
    for (const row of rows) {
      expect(row.model).toBe("demo-template-v1");
      expect(row.createdById).toBe(env.users.writer.id);
      expect(row.disclosure).toContain("광고");
    }
    expect(await prisma.costRecord.count({ where: { campaignId, type: "AI_GENERATION" } })).toBe(1);
  });

  it("reports AI errors without creating content", async () => {
    const failing: AIProvider = {
      id: "fake",
      model: "fake-1",
      generate: async () => ({ ok: false, drafts: [], provider: "fake", model: "fake-1", costKrw: 0, errorCode: "AI_AUTH", errorMessage: "AI API 키 인증에 실패했습니다." }),
    };
    const before = await prisma.generatedContent.count({ where: { campaignId } });
    const r = await generateContent(await ctxOf(env.users.writer.id), { campaignId, types: ["COMMENT"] }, failing);
    expect(r.ok).toBe(false);
    expect(r.errorCode).toBe("AI_AUTH");
    expect(await prisma.generatedContent.count({ where: { campaignId } })).toBe(before);
  });

  it("records edits as revisions and runs review: self-approval blocked, approve & reject", async () => {
    const writer = await ctxOf(env.users.writer.id);
    const reviewer = await ctxOf(env.users.reviewer.id);
    const rows = await prisma.generatedContent.findMany({ where: { campaignId }, orderBy: { createdAt: "asc" } });
    await editContent(writer, rows[0].id, `${rows[0].body} #테스트커피`, "필수 해시태그 추가");
    expect(await prisma.contentRevision.count({ where: { contentId: rows[0].id } })).toBe(1);

    await submitForReview(writer, rows.map((r) => r.id));
    expect((await getCampaign(reviewer, campaignId)).status).toBe("PENDING_REVIEW");

    // 작성자는 승인 권한 없음
    await expect(decideContent(writer, rows[0].id, "APPROVED")).rejects.toBeInstanceOf(ForbiddenError);
    // 반려는 사유 필수
    await expect(decideContent(reviewer, rows[2].id, "REJECTED")).rejects.toThrow("사유");

    await decideContent(reviewer, rows[0].id, "APPROVED");
    await decideContent(reviewer, rows[1].id, "APPROVED");
    await decideContent(reviewer, rows[2].id, "REJECTED", "문체 불일치");
    const approval = await prisma.approval.findFirstOrThrow({ where: { contentId: rows[0].id } });
    expect(approval.reviewerId).toBe(env.users.reviewer.id);
    expect(approval.createdAt).toBeInstanceOf(Date);
    expect((await getCampaign(reviewer, campaignId)).status).toBe("APPROVED");
  });

  it("blocks self-approval by the creator even with approval rights", async () => {
    const admin = await ctxOf(env.users.admin.id);
    const r = await generateContent(admin, { campaignId, types: ["QUESTION"] }, new DemoProvider());
    expect(r.ok).toBe(true);
    const own = await prisma.generatedContent.findFirstOrThrow({ where: { campaignId, type: "QUESTION" } });
    await submitForReview(admin, [own.id]);
    await expect(decideContent(admin, own.id, "APPROVED")).rejects.toThrow("본인이 생성한");
    await decideContent(await ctxOf(env.users.reviewer.id), own.id, "CHANGES_REQUESTED", "다시");
  });

  it("prechecks, schedules, simulates, records metrics and counts per platform", async () => {
    const manager = await ctxOf(env.users.manager.id);
    const approved = await prisma.generatedContent.findMany({ where: { campaignId, status: "APPROVED" }, orderBy: { createdAt: "asc" } });
    expect(approved.length).toBe(2);

    // 미승인 문구는 사전검사 차단
    const rejected = await prisma.generatedContent.findFirstOrThrow({ where: { campaignId, status: "REJECTED" } });
    const pcRejected = await precheck(manager, rejected.id);
    expect(pcRejected.ok).toBe(false);
    expect(pcRejected.items.find((i) => i.key === "approved")?.passed).toBe(false);

    const pc = await precheck(manager, approved[0].id, "INSTAGRAM");
    expect(pc.items.find((i) => i.key === "disclosure")?.passed).toBe(true);

    const s1 = await schedulePublication(manager, approved[0].id, "INSTAGRAM");
    expect(s1.publication.status).toBe("QUEUED");
    expect((await getCampaign(manager, campaignId)).status).toBe("READY_TO_RUN");

    // 동일 문구·플랫폼 재등록 → 중복 차단
    const dup = await schedulePublication(manager, approved[0].id, "INSTAGRAM");
    expect(dup.publication.status).toBe("BLOCKED");
    expect(dup.publication.errorCode).toBe("PRECHECK_DUPLICATE");

    const s2 = await schedulePublication(manager, approved[1].id, "INSTAGRAM");
    expect(s2.publication.status).toBe("QUEUED");

    // 실제 게시는 공식 API 미설정이므로 거부
    await expect(executePublication(manager, s1.publication.id, "LIVE")).rejects.toBeInstanceOf(ForbiddenError);

    let successes = 0;
    for (const id of [s1.publication.id, s2.publication.id]) {
      let res = await executePublication(manager, id, "SIMULATED");
      // 재현된 일시 오류는 재시도
      for (let i = 0; i < 5 && !res.result.ok && res.result.retryable; i++) res = await executePublication(manager, id, "SIMULATED");
      if (res.result.ok) successes++;
      expect(res.publication.mode).toBe("SIMULATED");
      expect(res.publication.executedById).toBe(env.users.manager.id);
    }
    expect(successes).toBeGreaterThan(0);

    const metrics = await prisma.performanceMetric.findMany({ where: { campaignId } });
    expect(metrics).toHaveLength(successes);
    for (const m of metrics) {
      expect(m.source).toBe("SIMULATED");
      expect(m.clicks).toBeGreaterThan(0);
    }

    const d = await dashboard(manager, { clientId });
    expect(d.perPlatform.INSTAGRAM.simulated).toBe(successes);
    expect(d.perPlatform.X.simulated).toBe(0);
    expect(d.published).toBe(successes);
    expect(d.perPlatform.INSTAGRAM.live).toBe(0);
    expect(d.metrics.bySource.SIMULATED.clicks).toBe(metrics.reduce((a, m) => a + (m.clicks ?? 0), 0));
    expect(d.blocked).toBe(1);

    const status = (await getCampaign(manager, campaignId)).status;
    expect(status).toBe("COMPLETED");
  });

  it("exports CSV rows that match the database", async () => {
    const manager = await ctxOf(env.users.manager.id);
    const rows = await publicationRows(manager, { clientId });
    const csv = publicationsCsv(rows, true);
    const lines = csv.trim().split("\r\n");
    expect(lines[0]).toContain("고객명");
    expect(lines.length - 1).toBe(await prisma.publication.count({ where: { campaignId, status: { in: ["SUCCESS", "FAILED"] } } }));
    expect(csv).toContain("모의");
    const summary = await campaignSummary(manager, { clientId });
    expect(summary[0].campaignId).toBe(campaignId);
    expect(summary[0].aiCost).toBe(0);
  });

  it("hides cost and PII from roles without permission", async () => {
    const viewer = await ctxOf(env.users.viewer.id);
    const d = await dashboard(viewer, {});
    expect(d.aiCost).toBeNull();
    expect(d.monthRequestAmount).toBeNull();
    const c = await getClient(viewer, clientId);
    expect(c.piiHidden).toBe(true);
    expect(c.budget).toBe(0);
    const rows = await publicationRows(viewer, {});
    expect(rows.every((r) => r.aiCost === null)).toBe(true);
  });
});
