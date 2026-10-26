import type { ContentStatus, ContentType, PlatformKey, Prisma } from "@prisma/client";
import type { AnalysisResult } from "@/lib/analysis/engine";
import { reviewContent } from "@/lib/approval/ai-review";
import { riskFromScore } from "@/lib/approval/rules";
import { CONTENT_TYPE_LABEL } from "@/lib/labels";
import { decideRequest, openRequest } from "./approvals";
import { prisma } from "@/lib/db";
import { assertCan, campaignWhere, ForbiddenError, NotFoundError, type Ctx } from "@/lib/auth/context";
import { seesAllClients } from "@/lib/auth/permissions";
import type { AIProvider } from "@/lib/ai/types";
import { defaultDisclosure, inspectDraft } from "@/lib/ai/guardrails";
import { audit } from "./audit";
import { assertAiBudget } from "./budget";
import { recomputeCampaignStatus } from "./campaigns";

export const ALL_CONTENT_TYPES: ContentType[] = [
  "COMMENT",
  "REPLY",
  "INFORMATIVE",
  "QUESTION",
  "EMPATHY",
  "SNS_POST",
  "YOUTUBE_META",
  "SHORT_HOOK",
  "SHORT_SCRIPT",
  "BLOG_COPY",
  "AD_DISCLOSURE",
];

function contentWhere(ctx: Ctx): Prisma.GeneratedContentWhereInput {
  return {
    organizationId: ctx.organizationId,
    campaign: { deletedAt: null, ...(seesAllClients(ctx.role) ? {} : { clientId: { in: ctx.clientIds } }) },
  };
}

export interface GenerateInput {
  campaignId: string;
  candidateId?: string;
  platform?: PlatformKey;
  types: ContentType[];
}

export interface GenerateOutcome {
  ok: boolean;
  created: number;
  ids: string[];
  provider: string;
  model: string;
  costKrw: number;
  errorCode?: string;
  errorMessage?: string;
}

export async function generateContent(ctx: Ctx, input: GenerateInput, provider: AIProvider): Promise<GenerateOutcome> {
  assertCan(ctx, "content:generate");
  if (input.types.length === 0) throw new Error("생성할 문구 유형을 하나 이상 선택하세요.");
  const c = await prisma.campaign.findFirst({
    where: { ...campaignWhere(ctx), id: input.campaignId },
    include: { brief: true, client: { include: { brandProfile: true } } },
  });
  if (!c || !c.brief) throw new NotFoundError("캠페인을 찾을 수 없습니다.");
  const cand = input.candidateId
    ? await prisma.contentCandidate.findFirst({ where: { id: input.candidateId, organizationId: ctx.organizationId } })
    : null;
  if (input.candidateId && !cand) throw new NotFoundError("연결할 게시물을 찾을 수 없습니다.");
  const bp = c.client.brandProfile;
  const brand = {
    companyIntro: bp?.companyIntro ?? "",
    productDescription: bp?.productDescription ?? "",
    toneOfVoice: bp?.toneOfVoice ?? "",
    bannedPhrases: bp?.bannedPhrases ?? [],
    requiredPhrases: bp?.requiredPhrases ?? [],
  };
  const platform = input.platform ?? cand?.platform ?? c.brief.desiredPlatforms[0] ?? null;
  await assertAiBudget(ctx, provider.id);

  const result = await provider.generate(
    {
      clientName: c.client.name,
      campaignName: c.name,
      goal: c.brief.goal,
      targetType: c.brief.targetType,
      coreTarget: c.brief.coreTarget,
      keywords: c.brief.keywords,
      bannedKeywords: c.brief.bannedKeywords,
      description: c.brief.description,
      targetUrl: c.brief.targetUrl,
      brand,
      candidate: cand ? { platform: cand.platform, accountName: cand.accountName, title: cand.title, summary: cand.summary } : null,
      platform,
    },
    input.types,
  );

  if (!result.ok) {
    await audit(ctx, "content.generate.error", "Campaign", c.id, `AI 생성 실패 (${result.errorCode})`, { provider: result.provider, errorCode: result.errorCode });
    return { ok: false, created: 0, ids: [], provider: result.provider, model: result.model, costKrw: 0, errorCode: result.errorCode, errorMessage: result.errorMessage };
  }

  const disclosure = defaultDisclosure(c.client.name);
  const perDraftCost = result.drafts.length ? Math.ceil(result.costKrw / result.drafts.length) : 0;
  const ids: string[] = [];
  await prisma.$transaction(async (tx) => {
    for (const d of result.drafts) {
      const row = await tx.generatedContent.create({
        data: {
          organizationId: ctx.organizationId,
          campaignId: c.id,
          candidateId: cand?.id ?? null,
          type: d.type,
          platform,
          body: d.body,
          disclosure,
          warnings: inspectDraft(d.body, { bannedPhrases: [...brand.bannedPhrases, ...c.brief!.bannedKeywords], requiredPhrases: brand.requiredPhrases }),
          model: result.model,
          provider: result.provider,
          costKrw: perDraftCost,
          createdById: ctx.userId,
        },
      });
      ids.push(row.id);
    }
    await tx.costRecord.create({
      data: {
        organizationId: ctx.organizationId,
        clientId: c.clientId,
        campaignId: c.id,
        type: "AI_GENERATION",
        amountKrw: result.costKrw,
        description: `${result.provider}/${result.model} 문구 ${result.drafts.length}건 생성${result.inputTokens != null ? ` (in ${result.inputTokens} / out ${result.outputTokens} tokens)` : ""}`,
      },
    });
    await audit(ctx, "content.generate", "Campaign", c.id, `문구 ${result.drafts.length}건 생성 (${result.model})`, { provider: result.provider }, tx);
    const shorts = result.drafts.filter((d) => d.type === "SHORT_SCRIPT").length;
    if (shorts) await audit(ctx, "content.generate.shortform", "Campaign", c.id, `숏폼 영상 대본 ${shorts}건 작성${platform ? ` (${platform})` : ""}`, undefined, tx);
  });
  return { ok: true, created: result.drafts.length, ids, provider: result.provider, model: result.model, costKrw: result.costKrw };
}

export interface ContentFilter {
  status?: ContentStatus;
  campaignId?: string;
  type?: ContentType;
  q?: string;
  page?: number;
}

export const CONTENT_PAGE_SIZE = 10;

export async function listContent(ctx: Ctx, f: ContentFilter = {}) {
  assertCan(ctx, "campaign:read");
  const page = Math.max(1, f.page ?? 1);
  const where: Prisma.GeneratedContentWhereInput = {
    ...contentWhere(ctx),
    ...(f.status ? { status: f.status } : {}),
    ...(f.campaignId ? { campaignId: f.campaignId } : {}),
    ...(f.type ? { type: f.type } : {}),
    ...(f.q ? { body: { contains: f.q, mode: "insensitive" } } : {}),
  };
  const [total, rows] = await Promise.all([
    prisma.generatedContent.count({ where }),
    prisma.generatedContent.findMany({
      where,
      orderBy: { createdAt: "desc" },
      skip: (page - 1) * CONTENT_PAGE_SIZE,
      take: CONTENT_PAGE_SIZE,
      include: {
        campaign: { select: { id: true, name: true, client: { select: { name: true } } } },
        candidate: { select: { title: true, platform: true, postUrl: true } },
        createdBy: { select: { name: true } },
        approvals: { orderBy: { createdAt: "desc" }, take: 1, include: { reviewer: { select: { name: true } } } },
        _count: { select: { revisions: true } },
      },
    }),
  ]);
  return { total, page, pageCount: Math.max(1, Math.ceil(total / CONTENT_PAGE_SIZE)), rows };
}

async function getOwnedContent(ctx: Ctx, id: string) {
  const content = await prisma.generatedContent.findFirst({
    where: { ...contentWhere(ctx), id },
    include: { campaign: { include: { brief: true, client: { include: { brandProfile: true } } } } },
  });
  if (!content) throw new NotFoundError();
  return content;
}

/** 문구 수정 → 수정 이력 저장. 승인된 문구를 수정하면 다시 검토가 필요하다. */
export async function editContent(ctx: Ctx, id: string, body: string, note?: string) {
  assertCan(ctx, "content:edit");
  const text = body.trim();
  if (!text) throw new Error("문구를 입력하세요.");
  if (text.length > 5000) throw new Error("문구가 너무 깁니다 (최대 5000자).");
  const content = await getOwnedContent(ctx, id);
  if (content.body === text) return content;
  const published = await prisma.publication.count({ where: { contentId: id, status: "SUCCESS" } });
  if (published > 0) throw new Error("이미 게시(모의 포함)된 문구는 수정할 수 없습니다. 새 초안을 생성하세요.");
  const bp = content.campaign.client.brandProfile;
  return prisma.$transaction(async (tx) => {
    await tx.contentRevision.create({ data: { contentId: id, editorId: ctx.userId, before: content.body, after: text, note: note || null } });
    const updated = await tx.generatedContent.update({
      where: { id },
      data: {
        body: text,
        warnings: inspectDraft(text, {
          bannedPhrases: [...(bp?.bannedPhrases ?? []), ...(content.campaign.brief?.bannedKeywords ?? [])],
          requiredPhrases: bp?.requiredPhrases ?? [],
        }),
        ...(content.status === "APPROVED" || content.status === "REJECTED" || content.status === "CHANGES_REQUESTED" ? { status: "DRAFT" as const } : {}),
      },
    });
    await recomputeCampaignStatus(tx, content.campaignId);
    await audit(ctx, "content.edit", "GeneratedContent", id, `문구 수정${note ? `: ${note}` : ""}`, undefined, tx);
    return updated;
  });
}

export async function submitForReview(ctx: Ctx, ids: string[]) {
  assertCan(ctx, "content:edit");
  const rows = await prisma.generatedContent.findMany({
    where: { ...contentWhere(ctx), id: { in: ids }, status: { in: ["DRAFT", "CHANGES_REQUESTED"] } },
    include: { campaign: { include: { brief: true, client: { include: { brandProfile: true } } } } },
  });
  if (rows.length === 0) throw new Error("검토 요청할 수 있는 초안이 없습니다.");
  await prisma.$transaction(async (tx) => {
    await tx.generatedContent.updateMany({ where: { id: { in: rows.map((r) => r.id) } }, data: { status: "PENDING_REVIEW" } });
    for (const r of rows) await openContentRequest(tx, ctx, r);
    for (const cid of new Set(rows.map((r) => r.campaignId))) await recomputeCampaignStatus(tx, cid);
    await audit(ctx, "content.submit", "GeneratedContent", null, `문구 ${rows.length}건 검토 요청`, { ids: rows.map((r) => r.id) }, tx);
  });
  return rows.length;
}

type ContentForRequest = Prisma.GeneratedContentGetPayload<{ include: { campaign: { include: { brief: true; client: { include: { brandProfile: true } } } } } }>;

/** 문구 1건의 결재 요청 (AI 1차 검토 + 위험도에 따른 결재 라인) */
export async function openContentRequest(tx: Prisma.TransactionClient, ctx: Ctx, c: ContentForRequest) {
  const bp = c.campaign.client.brandProfile;
  const scores = c.campaign.brief?.scores as unknown as AnalysisResult | null;
  const ai = reviewContent({
    body: c.body,
    disclosure: c.disclosure,
    warnings: c.warnings,
    bannedPhrases: [...(bp?.bannedPhrases ?? []), ...(c.campaign.brief?.bannedKeywords ?? [])],
  });
  return openRequest(tx, ctx, {
    gate: "CONTENT",
    entityType: "GeneratedContent",
    entityId: c.id,
    clientId: c.campaign.clientId,
    title: `${c.campaign.name} · ${CONTENT_TYPE_LABEL[c.type]}`,
    risk: riskFromScore(scores?.scores.policyRisk.value, c.warnings.length > 0 || ai.findings.length > 0),
    aiReview: ai,
  });
}

export type Decision = "APPROVED" | "REJECTED" | "CHANGES_REQUESTED";

/**
 * 문구 결재. 결재 라인(규칙)에 따라 여러 단계일 수 있으며, 마지막 단계 승인 시 문구가 ‘승인’된다.
 * 본인이 생성한 문구는 스스로 결재할 수 없다(직무 분리).
 */
export async function decideContent(ctx: Ctx, id: string, decision: Decision, comment?: string) {
  assertCan(ctx, "approval:decide");
  const content = await getOwnedContent(ctx, id);
  if (content.status !== "PENDING_REVIEW") throw new Error("검토 대기 상태의 문구만 결정할 수 있습니다.");
  if (content.createdById === ctx.userId) throw new ForbiddenError("본인이 생성한 문구는 직접 승인·반려할 수 없습니다.");
  let req = await prisma.approvalRequest.findFirst({ where: { organizationId: ctx.organizationId, entityType: "GeneratedContent", entityId: id, status: "PENDING" } });
  if (!req) {
    // 결재 요청 없이 검토 대기가 된 이전 데이터: 생성자 명의로 요청을 연다
    const full = await prisma.generatedContent.findUniqueOrThrow({ where: { id }, include: { campaign: { include: { brief: true, client: { include: { brandProfile: true } } } } } });
    if (!content.createdById) throw new Error("요청자를 알 수 없는 문구입니다. 다시 검토 요청하세요.");
    const requesterCtx: Ctx = { ...ctx, userId: content.createdById, role: "CONTENT_WRITER" };
    req = await prisma.$transaction((tx) => openContentRequest(tx, requesterCtx, full));
    if (!req) throw new Error("결재 요청을 만들 수 없습니다.");
  }
  return decideRequest(ctx, req.id, decision, comment);
}
