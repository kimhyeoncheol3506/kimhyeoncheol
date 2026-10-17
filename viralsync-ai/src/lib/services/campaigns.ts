import type { CampaignStatus, Prisma } from "@prisma/client";
import { prisma } from "@/lib/db";
import { assertCan, campaignWhere, canAccessClient, clientWhere, NotFoundError, type Ctx } from "@/lib/auth/context";
import { analyzeBrief, type AnalysisResult } from "@/lib/analysis/engine";
import { checkUrl } from "@/lib/validation/url";
import type { BriefInput } from "@/lib/validation/schemas";
import { audit } from "./audit";
import { PAGE_SIZE } from "./clients";

export interface CampaignFilter {
  q?: string;
  status?: CampaignStatus;
  clientId?: string;
  page?: number;
}

export async function listCampaigns(ctx: Ctx, f: CampaignFilter = {}) {
  assertCan(ctx, "campaign:read");
  const page = Math.max(1, f.page ?? 1);
  const where: Prisma.CampaignWhereInput = {
    ...campaignWhere(ctx),
    ...(f.status ? { status: f.status } : {}),
    ...(f.clientId ? { clientId: f.clientId } : {}),
    ...(f.q ? { OR: [{ name: { contains: f.q, mode: "insensitive" } }, { client: { name: { contains: f.q, mode: "insensitive" } } }] } : {}),
  };
  const [total, rows] = await Promise.all([
    prisma.campaign.count({ where }),
    prisma.campaign.findMany({
      where,
      orderBy: { createdAt: "desc" },
      skip: (page - 1) * PAGE_SIZE,
      take: PAGE_SIZE,
      include: {
        client: { select: { id: true, name: true } },
        owner: { select: { name: true } },
        brief: { select: { targetType: true, goal: true, category: true, desiredPlatforms: true } },
        _count: { select: { contents: true, publications: true } },
      },
    }),
  ]);
  return { total, page, pageCount: Math.max(1, Math.ceil(total / PAGE_SIZE)), rows };
}

export async function listCampaignOptions(ctx: Ctx) {
  return prisma.campaign.findMany({
    where: campaignWhere(ctx),
    select: { id: true, name: true, status: true, client: { select: { name: true } } },
    orderBy: { createdAt: "desc" },
  });
}

export async function getCampaign(ctx: Ctx, id: string) {
  assertCan(ctx, "campaign:read");
  const c = await prisma.campaign.findFirst({
    where: { ...campaignWhere(ctx), id },
    include: {
      client: { include: { brandProfile: true } },
      owner: { select: { id: true, name: true } },
      brief: true,
      candidates: { orderBy: { relevanceScore: "desc" } },
      contents: {
        orderBy: { createdAt: "desc" },
        include: {
          candidate: { select: { title: true, platform: true, postUrl: true } },
          createdBy: { select: { name: true } },
          approvals: { include: { reviewer: { select: { name: true } } }, orderBy: { createdAt: "desc" } },
          revisions: { orderBy: { createdAt: "desc" }, include: { editor: { select: { name: true } } } },
        },
      },
      publications: { orderBy: { createdAt: "desc" }, include: { executedBy: { select: { name: true } } } },
    },
  });
  if (!c) throw new NotFoundError();
  return c;
}

export async function createCampaign(ctx: Ctx, input: BriefInput) {
  assertCan(ctx, "campaign:write");
  const client = await prisma.client.findFirst({ where: { ...clientWhere(ctx), id: input.clientId } });
  if (!client) throw new NotFoundError("고객을 찾을 수 없거나 접근 권한이 없습니다.");
  const urlCheck = input.targetUrl ? checkUrl(input.targetUrl) : null;
  return prisma.$transaction(async (tx) => {
    const c = await tx.campaign.create({
      data: {
        organizationId: ctx.organizationId,
        clientId: client.id,
        name: input.title,
        ownerId: ctx.userId,
        budget: input.budget,
        startDate: input.startDate ?? null,
        endDate: input.endDate ?? null,
        brief: {
          create: {
            title: input.title,
            targetUrl: urlCheck?.normalized ?? null,
            urlCheck: (urlCheck ?? undefined) as Prisma.InputJsonValue | undefined,
            targetType: input.targetType,
            goal: input.goal,
            coreTarget: input.coreTarget,
            desiredPlatforms: input.desiredPlatforms,
            keywords: input.keywords,
            bannedKeywords: input.bannedKeywords,
            description: input.description,
          },
        },
      },
    });
    await audit(ctx, "campaign.create", "Campaign", c.id, `광고 의뢰 '${c.name}' 접수 (${client.name})`, undefined, tx);
    return c;
  });
}

export async function updateCampaign(ctx: Ctx, id: string, input: BriefInput) {
  assertCan(ctx, "campaign:write");
  const existing = await prisma.campaign.findFirst({ where: { ...campaignWhere(ctx), id } });
  if (!existing) throw new NotFoundError();
  if (!canAccessClient(ctx, input.clientId)) throw new NotFoundError("고객을 찾을 수 없거나 접근 권한이 없습니다.");
  const client = await prisma.client.findFirst({ where: { ...clientWhere(ctx), id: input.clientId } });
  if (!client) throw new NotFoundError("고객을 찾을 수 없습니다.");
  const urlCheck = input.targetUrl ? checkUrl(input.targetUrl) : null;
  const briefData = {
    title: input.title,
    targetUrl: urlCheck?.normalized ?? null,
    urlCheck: (urlCheck ?? undefined) as Prisma.InputJsonValue | undefined,
    targetType: input.targetType,
    goal: input.goal,
    coreTarget: input.coreTarget,
    desiredPlatforms: input.desiredPlatforms,
    keywords: input.keywords,
    bannedKeywords: input.bannedKeywords,
    description: input.description,
  };
  return prisma.$transaction(async (tx) => {
    const c = await tx.campaign.update({
      where: { id },
      data: {
        name: input.title,
        clientId: client.id,
        budget: input.budget,
        startDate: input.startDate ?? null,
        endDate: input.endDate ?? null,
        // 의뢰 내용이 바뀌면 기존 분석은 무효 → 초안으로 되돌림 (실행 이후 단계는 유지)
        ...(["DRAFT", "ANALYZED"].includes(existing.status) ? { status: "DRAFT" as const } : {}),
        brief: {
          upsert: {
            create: briefData,
            update: { ...briefData, category: null, subcategory: null, scores: undefined, analyzedAt: null },
          },
        },
      },
    });
    await audit(ctx, "campaign.update", "Campaign", id, `캠페인 '${c.name}' 수정`, undefined, tx);
    return c;
  });
}

export async function runAnalysis(ctx: Ctx, id: string): Promise<AnalysisResult> {
  assertCan(ctx, "analysis:run");
  const c = await prisma.campaign.findFirst({
    where: { ...campaignWhere(ctx), id },
    include: { brief: true, client: { include: { brandProfile: true } } },
  });
  if (!c || !c.brief) throw new NotFoundError();
  const b = c.brief;
  const bp = c.client.brandProfile;
  const result = analyzeBrief(
    {
      title: b.title,
      description: b.description,
      keywords: b.keywords,
      bannedKeywords: b.bannedKeywords,
      coreTarget: b.coreTarget,
      targetType: b.targetType,
      goal: b.goal,
      desiredPlatforms: b.desiredPlatforms,
      targetUrl: b.targetUrl,
    },
    bp
      ? {
          companyIntro: bp.companyIntro,
          productDescription: bp.productDescription,
          coreTarget: bp.coreTarget,
          toneOfVoice: bp.toneOfVoice,
          bannedPhrases: bp.bannedPhrases,
          requiredPhrases: bp.requiredPhrases,
        }
      : null,
  );
  await prisma.$transaction(async (tx) => {
    await tx.campaignBrief.update({
      where: { id: b.id },
      data: {
        category: result.category,
        subcategory: result.subcategory,
        scores: result as unknown as Prisma.InputJsonValue,
        analyzedAt: new Date(),
        analysisEngine: result.engine,
      },
    });
    if (c.status === "DRAFT") await tx.campaign.update({ where: { id }, data: { status: "ANALYZED" } });
    await audit(ctx, "campaign.analyze", "Campaign", id, `'${c.name}' 분석: ${result.category} > ${result.subcategory}`, undefined, tx);
  });
  return result;
}

export async function softDeleteCampaign(ctx: Ctx, id: string) {
  assertCan(ctx, "campaign:write");
  const c = await prisma.campaign.findFirst({ where: { ...campaignWhere(ctx), id } });
  if (!c) throw new NotFoundError();
  await prisma.campaign.update({ where: { id }, data: { deletedAt: new Date() } });
  await audit(ctx, "campaign.delete", "Campaign", id, `캠페인 '${c.name}' 삭제(보관)`);
}

/**
 * 콘텐츠·실행 상태로부터 캠페인 상태를 다시 계산한다.
 * 초안 → AI 분석 완료 → 검토 대기 → 승인 완료 → 실행 대기 → 실행 완료/실패
 */
export async function recomputeCampaignStatus(tx: Prisma.TransactionClient, campaignId: string): Promise<CampaignStatus> {
  const c = await tx.campaign.findUniqueOrThrow({
    where: { id: campaignId },
    include: { contents: { select: { status: true } }, publications: { select: { status: true } }, brief: { select: { analyzedAt: true } } },
  });
  const pubs = c.publications.filter((p) => p.status !== "BLOCKED");
  const contents = c.contents.map((x) => x.status);
  let next: CampaignStatus;
  if (pubs.some((p) => p.status === "QUEUED")) next = "READY_TO_RUN";
  else if (pubs.length > 0) next = pubs.some((p) => p.status === "SUCCESS") ? "COMPLETED" : "FAILED";
  else if (contents.includes("PENDING_REVIEW")) next = "PENDING_REVIEW";
  else if (contents.includes("APPROVED")) next = "APPROVED";
  else if (contents.includes("CHANGES_REQUESTED") || contents.includes("REJECTED")) next = "CHANGES_REQUESTED";
  else next = c.brief?.analyzedAt ? "ANALYZED" : "DRAFT";
  if (next !== c.status) await tx.campaign.update({ where: { id: campaignId }, data: { status: next } });
  return next;
}
