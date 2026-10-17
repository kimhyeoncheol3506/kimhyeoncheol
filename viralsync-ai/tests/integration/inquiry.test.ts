import { beforeAll, describe, expect, it } from "vitest";
import { prisma } from "@/lib/db";
import { ForbiddenError, NotFoundError } from "@/lib/auth/context";
import { convertInquiry, createInquiry, getInquiry, listInquiries, markLost, overrideInquiry, saveQuote } from "@/lib/services/inquiries";
import { listTasks, updateTask } from "@/lib/services/tasks";
import { createPackage, updatePackage } from "@/lib/services/packages";
import { getCampaign } from "@/lib/services/campaigns";
import { inquiryOverrideSchema, packageSchema, taskUpdateSchema } from "@/lib/validation/schemas";
import { ctxOf, makeOrg } from "./helpers";

let A: Awaited<ReturnType<typeof makeOrg>>;
let B: Awaited<ReturnType<typeof makeOrg>>;
const SHABU = `'테스트 샤브' 브랜드의 광고대행 문의드립니다.\n▶홈페이지 : https://shabu-test.example\n예산은 얼마정도로 잡아야 할지, 광고 종류 추천 부탁드립니다.`;

beforeAll(async () => {
  A = await makeOrg("inq-a");
  B = await makeOrg("inq-b");
});

describe("문의 → 견적 → 계약 전환 → 집행", () => {
  let inquiryId: string;
  let campaignId: string;

  it("analyzes a pasted inquiry into plan, quote and reply", async () => {
    const m = await ctxOf(A.users.manager.id);
    const q = await createInquiry(m, { source: "KMONG", customerName: "테스트고객", rawText: SHABU });
    inquiryId = q.id;
    const got = await getInquiry(m, q.id);
    expect(got.status).toBe("NEW");
    expect(got.parsedData?.brand).toBe("테스트 샤브");
    expect(got.planData?.tiers).toHaveLength(3);
    expect(got.quoteTotal).toBeGreaterThan(0);
    expect(got.replyDraft).toContain("크몽 안전결제");
  });

  it("re-plans after the manager corrects the analysis", async () => {
    const m = await ctxOf(A.users.manager.id);
    await overrideInquiry(m, inquiryId, inquiryOverrideSchema.parse({ brand: "테스트 샤브 본점", businessType: "RESTAURANT", keywords: "샤브 맛집", requestedChannels: ["BLOG"], budget: "1,000,000" }));
    const got = await getInquiry(m, inquiryId);
    expect(got.parsedData?.brand).toBe("테스트 샤브 본점");
    expect(got.planData?.tiers[0].items.map((i) => i.channel)).toEqual(["BLOG"]);
    expect(got.parsedData?.missingInfo.some((x) => x.startsWith("월 예산"))).toBe(false);
  });

  it("saves the quote and converts into client, campaign and tasks", async () => {
    const m = await ctxOf(A.users.manager.id);
    await saveQuote(m, inquiryId, "STANDARD", "답변 본문");
    expect((await getInquiry(m, inquiryId)).status).toBe("QUOTED");
    const r = await convertInquiry(m, inquiryId);
    campaignId = r.campaignId;
    const q = await getInquiry(m, inquiryId);
    expect(q.status).toBe("WON");
    // 전환한 매니저는 새 고객에 접근 가능하고, 분석이 자동 실행됨
    const m2 = await ctxOf(A.users.manager.id);
    const c = await getCampaign(m2, campaignId);
    expect(c.client.name).toBe("테스트 샤브 본점");
    expect(c.status).toBe("ANALYZED");
    expect(c.brief?.description).toContain("[고객 문의 원문]");
    const std = q.planData!.tiers.find((t) => t.key === "STANDARD")!;
    expect(c.budget).toBe(std.total);
    const tasks = await listTasks(m2, { campaignId });
    expect(tasks.map((t) => t.channel).sort()).toEqual(std.items.map((i) => i.channel).sort());
    await expect(convertInquiry(m2, inquiryId)).rejects.toThrow("이미 계약 전환");
  });

  it("requires a deliverable or note to complete a task", async () => {
    const w = await ctxOf(A.users.manager.id);
    const all = await listTasks(w, { campaignId });
    expect(all.every((x) => x.note === "")).toBe(true); // 시스템 문구가 완료 조건을 채우지 않도록
    const t = all.find((x) => x.channel === "META_AD") ?? all[0];
    await expect(updateTask(w, t.id, taskUpdateSchema.parse({ status: "DONE" }))).rejects.toThrow("결과물 URL");
    // 내부망 URL 은 입력 검증 단계에서 거부
    expect(() => taskUpdateSchema.parse({ status: "DONE", deliverableUrl: "http://localhost/x" })).toThrow();
    const done = await updateTask(w, t.id, taskUpdateSchema.parse({ status: "DONE", deliverableUrl: "https://blog.example/post/1" }));
    expect(done.completedAt).toBeInstanceOf(Date);
  });

  it("marks lost inquiries", async () => {
    const m = await ctxOf(A.users.manager.id);
    const q = await createInquiry(m, { source: "PHONE", customerName: "미계약고객", rawText: "블로그 가격이 궁금합니다 얼마인가요?" });
    await markLost(m, q.id, "예산 부족");
    expect((await getInquiry(m, q.id)).status).toBe("LOST");
    expect((await listInquiries(m, { status: "LOST" })).rows.map((r) => r.id)).toContain(q.id);
  });
});

describe("권한·격리", () => {
  it("hides inquiries and tasks from other organizations and roles", async () => {
    const mA = await ctxOf(A.users.manager.id);
    const q = await createInquiry(mA, { source: "KMONG", customerName: "격리", rawText: "블로그 포스팅 가능한가요? 가격 알려주세요" });
    await expect(getInquiry(await ctxOf(B.users.admin.id), q.id)).rejects.toBeInstanceOf(NotFoundError);
    await expect(getInquiry(await ctxOf(A.users.viewer.id), q.id)).rejects.toBeInstanceOf(ForbiddenError);
    await expect(getInquiry(await ctxOf(A.users.writer.id), q.id)).rejects.toBeInstanceOf(ForbiddenError);
    const tasksB = await listTasks(await ctxOf(B.users.admin.id));
    expect(tasksB).toHaveLength(0);
  });

  it("lets only admins change prices, and the quote follows the catalog", async () => {
    const mA = await ctxOf(A.users.manager.id);
    const input = packageSchema.parse({ name: "새 상품", channel: "KARROT", unitPrice: "90000", unit: "회", leadTimeDays: "3" });
    await expect(createPackage(mA, input)).rejects.toBeInstanceOf(ForbiddenError);
    const admin = await ctxOf(A.users.admin.id);
    const blog = await prisma.servicePackage.findFirstOrThrow({ where: { organizationId: A.org.id, channel: "BLOG" } });
    await updatePackage(admin, blog.id, { ...packageSchema.parse({ name: blog.name, channel: "BLOG", unitPrice: "250000", unit: "월", leadTimeDays: "7" }), active: true });
    const q = await createInquiry(mA, { source: "KMONG", customerName: "가격", rawText: "블로그 포스팅 가능한가요? 키워드는 테스트 입니다" });
    const basic = (await getInquiry(mA, q.id)).planData!.tiers.find((t) => t.key === "BASIC")!;
    expect(basic.items[0].unitPrice).toBe(250000);
  });
});
