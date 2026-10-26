import { beforeAll, describe, expect, it } from "vitest";
import { prisma } from "@/lib/db";
import { ForbiddenError } from "@/lib/auth/context";
import { DemoProvider } from "@/lib/ai/demo-provider";
import type { AIProvider } from "@/lib/ai/types";
import { createClient } from "@/lib/services/clients";
import { createCampaign } from "@/lib/services/campaigns";
import { campaignBoard, runChannelPack, secretaryReport } from "@/lib/services/company";
import { aiBudgetStatus, assertAiBudget, BudgetError, setAiBudget } from "@/lib/services/budget";
import { executePublication } from "@/lib/services/publications";
import { PACK_CHANNELS } from "@/lib/company/channels";
import { briefSchema, clientSchema } from "@/lib/validation/schemas";
import { ctxOf, grant, makeOrg } from "./helpers";

let A: Awaited<ReturnType<typeof makeOrg>>;
let campaignId: string;

/** 호출되면 안 되는 유료 Provider — 예산 차단 확인용 */
const paid: AIProvider = {
  id: "anthropic",
  model: "test-paid",
  generate: async () => {
    throw new Error("유료 Provider 가 호출되었습니다");
  },
};

beforeAll(async () => {
  A = await makeOrg("company");
  const admin = await ctxOf(A.users.admin.id);
  const clientId = (await createClient(admin, clientSchema.parse({ name: "바른숨 필라테스(테스트)", contactName: "원장", budget: "0", bannedPhrases: "살 빠짐 보장" }))).id;
  campaignId = (
    await createCampaign(
      admin,
      briefSchema.parse({ clientId, title: "유튜브 채널 오픈 홍보", targetType: "YOUTUBE", goal: "VIEWS", budget: "0", desiredPlatforms: PACK_CHANNELS, keywords: "퇴근스트레칭, 필라테스", description: "퇴근 후 20분 스트레칭 유튜브 채널을 알리는 캠페인입니다." }),
    )
  ).id;
  await grant([A.users.manager.id, A.users.writer.id, A.users.viewer.id], clientId);
});

describe("AI 팀에 맡기기 (채널 패키지)", () => {
  it("creates channel-specific drafts for the five channels and sends them all to approval", async () => {
    const manager = await ctxOf(A.users.manager.id);
    const r = await runChannelPack(manager, campaignId, PACK_CHANNELS, new DemoProvider());
    expect(r.failed).toBeNull();
    expect(r.done).toEqual(PACK_CHANNELS);
    // 쓰레드1 + 릴스2 + 유튜브2 + 페이스북1 + 틱톡2
    expect(r.created).toBe(8);
    expect(r.submitted).toBe(8);

    const contents = await prisma.generatedContent.findMany({ where: { campaignId } });
    expect(contents.every((c) => c.status === "PENDING_REVIEW" && c.platform)).toBe(true);
    const scripts = contents.filter((c) => c.type === "SHORT_SCRIPT");
    expect(scripts.map((c) => c.platform).sort()).toEqual(["INSTAGRAM", "TIKTOK", "YOUTUBE"]);
    for (const s of scripts) {
      expect(s.body).toContain("#1 (0~3초)");
      expect(s.body).toContain("광고");
    }
    expect(await prisma.approvalRequest.count({ where: { organizationId: A.org.id, status: "PENDING", entityId: { in: contents.map((c) => c.id) } } })).toBe(8);
    expect(await prisma.auditLog.count({ where: { organizationId: A.org.id, action: "company.channel_pack" } })).toBe(1);
    expect(await prisma.auditLog.count({ where: { organizationId: A.org.id, action: "content.generate.shortform" } })).toBe(3);
  });

  it("shows the board: drafting done, waiting on approval, per-channel counts", async () => {
    const admin = await ctxOf(A.users.admin.id);
    const b = await campaignBoard(admin, campaignId);
    expect(b.stages.find((s) => s.label === "콘텐츠 제작")?.state).toBe("done");
    expect(b.stages.find((s) => s.staff === "captain")).toMatchObject({ state: "waiting", detail: "결재 대기 8건" });
    expect(b.stages.find((s) => s.label === "성과")?.state).toBe("todo");
    expect(b.channels.find((c) => c.platform === "TIKTOK")).toMatchObject({ drafts: 2, pending: 2, published: 0 });
  });

  it("the secretary reports in at most five lines and tells the captain what to decide", async () => {
    const lines = await secretaryReport(await ctxOf(A.users.admin.id));
    expect(lines.length).toBeLessThanOrEqual(5);
    expect(lines.find((l) => l.label === "캡틴이 할 일")?.text).toContain("결재 8건");
    expect(lines.find((l) => l.label === "결과")?.text).toContain("결재 대기 8건");
    // 비용 권한이 없는 역할에게는 예산 줄이 없다
    expect((await secretaryReport(await ctxOf(A.users.writer.id))).some((l) => l.label === "예산")).toBe(false);
  });

  it("viewers cannot run the AI team", async () => {
    await expect(runChannelPack(await ctxOf(A.users.viewer.id), campaignId, ["THREADS"], new DemoProvider())).rejects.toBeInstanceOf(ForbiddenError);
  });
});

describe("예산 한도", () => {
  it("only admins set the cap; cap 0 blocks paid AI but never the free demo engine", async () => {
    const admin = await ctxOf(A.users.admin.id);
    const manager = await ctxOf(A.users.manager.id);
    await expect(setAiBudget(manager, 1000)).rejects.toBeInstanceOf(ForbiddenError);
    await setAiBudget(admin, 0);
    await expect(assertAiBudget(manager, "anthropic")).rejects.toBeInstanceOf(BudgetError);
    await expect(assertAiBudget(manager, "demo")).resolves.toBeUndefined();

    const r = await runChannelPack(manager, campaignId, ["THREADS", "TIKTOK"], paid);
    expect(r.created).toBe(0);
    expect(r.failed?.platform).toBe("THREADS"); // 첫 매체에서 멈추고 다음 매체로 넘어가지 않음
    expect(r.failed?.message).toContain("0원");
  });

  it("stops once this month's AI spend reaches the cap", async () => {
    const admin = await ctxOf(A.users.admin.id);
    await setAiBudget(admin, 5000);
    await prisma.costRecord.create({ data: { organizationId: A.org.id, type: "AI_GENERATION", amountKrw: 5000, description: "테스트 사용액" } });
    expect(await aiBudgetStatus(admin)).toMatchObject({ used: 5000, cap: 5000, reached: true });
    await expect(assertAiBudget(admin, "anthropic")).rejects.toThrow(/상한/);
    await setAiBudget(admin, null);
    await expect(assertAiBudget(admin, "anthropic")).resolves.toBeUndefined();
  });
});

describe("실패 대응", () => {
  it("refuses a third retry of a failed publication", async () => {
    const manager = await ctxOf(A.users.manager.id);
    const content = await prisma.generatedContent.findFirstOrThrow({ where: { campaignId } });
    await prisma.generatedContent.update({ where: { id: content.id }, data: { status: "APPROVED" } });
    const pub = await prisma.publication.create({
      data: { organizationId: A.org.id, campaignId, contentId: content.id, platform: "THREADS", status: "FAILED", retryCount: 2, contentHash: "t", errorCode: "SIM_RATE_LIMITED" },
    });
    await expect(executePublication(manager, pub.id, "SIMULATED")).rejects.toThrow(/재시도 2회/);
  });
});
