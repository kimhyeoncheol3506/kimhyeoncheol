import type { PlatformKey, Prisma, ReviewStatus } from "@prisma/client";
import { prisma } from "@/lib/db";
import { assertCan, campaignWhere, NotFoundError, type Ctx } from "@/lib/auth/context";
import { seesAllClients } from "@/lib/auth/permissions";
import { classify, scoreCandidate, type CandidateScore } from "@/lib/analysis/engine";
import type { CandidateInput } from "@/lib/validation/schemas";
import { audit } from "./audit";

export const CANDIDATE_PAGE_SIZE = 12;

/** 비관리자는 미연결 후보 + 접근 가능한 캠페인에 연결된 후보만 */
function candidateWhere(ctx: Ctx): Prisma.ContentCandidateWhereInput {
  if (seesAllClients(ctx.role)) return { organizationId: ctx.organizationId };
  return {
    organizationId: ctx.organizationId,
    OR: [{ campaignId: null }, { campaign: { clientId: { in: ctx.clientIds } } }],
  };
}

export interface CandidateFilter {
  q?: string;
  platform?: PlatformKey;
  review?: ReviewStatus;
  page?: number;
  sort?: "recent" | "relevance";
}

export async function listCandidates(ctx: Ctx, f: CandidateFilter = {}) {
  assertCan(ctx, "campaign:read");
  const page = Math.max(1, f.page ?? 1);
  const where: Prisma.ContentCandidateWhereInput = {
    AND: [
      candidateWhere(ctx),
      f.platform ? { platform: f.platform } : {},
      f.review ? { reviewStatus: f.review } : {},
      f.q
        ? {
            OR: [
              { title: { contains: f.q, mode: "insensitive" } },
              { accountName: { contains: f.q, mode: "insensitive" } },
              { summary: { contains: f.q, mode: "insensitive" } },
            ],
          }
        : {},
    ],
  };
  const [total, rows] = await Promise.all([
    prisma.contentCandidate.count({ where }),
    prisma.contentCandidate.findMany({
      where,
      orderBy: f.sort === "relevance" ? [{ relevanceScore: { sort: "desc", nulls: "last" } }] : [{ createdAt: "desc" }],
      skip: (page - 1) * CANDIDATE_PAGE_SIZE,
      take: CANDIDATE_PAGE_SIZE,
      include: { campaign: { select: { id: true, name: true } } },
    }),
  ]);
  return { total, page, pageCount: Math.max(1, Math.ceil(total / CANDIDATE_PAGE_SIZE)), rows };
}

export async function createCandidate(ctx: Ctx, input: CandidateInput) {
  assertCan(ctx, "candidate:write");
  const dup = await prisma.contentCandidate.findFirst({ where: { organizationId: ctx.organizationId, postUrl: input.postUrl } });
  if (dup) throw new Error("이미 등록된 게시물 URL 입니다.");
  const category = classify(`${input.title} ${input.summary}`).category;
  const c = await prisma.contentCandidate.create({
    data: {
      organizationId: ctx.organizationId,
      platform: input.platform,
      accountName: input.accountName,
      profileUrl: input.profileUrl ?? null,
      postUrl: input.postUrl,
      title: input.title,
      summary: input.summary,
      category,
      source: "MANUAL",
      lastCheckedAt: new Date(),
    },
  });
  await audit(ctx, "candidate.create", "ContentCandidate", c.id, `홍보 후보 등록: ${c.title}`);
  return c;
}

async function loadCampaignForScoring(ctx: Ctx, campaignId: string) {
  const c = await prisma.campaign.findFirst({
    where: { ...campaignWhere(ctx), id: campaignId },
    include: { brief: true, client: { include: { brandProfile: true } } },
  });
  if (!c || !c.brief) throw new NotFoundError("캠페인을 찾을 수 없습니다.");
  return c;
}

/** 선택한 캠페인 기준으로 후보 점수를 계산 (저장하지 않음) */
export async function scoreCandidatesFor(ctx: Ctx, campaignId: string, candidateIds: string[]) {
  const c = await loadCampaignForScoring(ctx, campaignId);
  const cands = await prisma.contentCandidate.findMany({ where: { AND: [candidateWhere(ctx), { id: { in: candidateIds } }] } });
  const out: Record<string, CandidateScore> = {};
  for (const cand of cands) out[cand.id] = scoreAgainst(cand, c);
  return out;
}

function scoreAgainst(
  cand: { platform: PlatformKey; title: string; summary: string; category: string | null },
  c: Awaited<ReturnType<typeof loadCampaignForScoring>>,
) {
  const b = c.brief!;
  return scoreCandidate(
    cand,
    { keywords: b.keywords, bannedKeywords: b.bannedKeywords, coreTarget: b.coreTarget, desiredPlatforms: b.desiredPlatforms, category: b.category },
    c.client.brandProfile ? { coreTarget: c.client.brandProfile.coreTarget, bannedPhrases: c.client.brandProfile.bannedPhrases } : null,
  );
}

/** 후보를 캠페인에 연결하고 점수·적합성 근거를 저장 */
export async function linkCandidate(ctx: Ctx, candidateId: string, campaignId: string) {
  assertCan(ctx, "candidate:write");
  const c = await loadCampaignForScoring(ctx, campaignId);
  const cand = await prisma.contentCandidate.findFirst({ where: { AND: [candidateWhere(ctx), { id: candidateId }] } });
  if (!cand) throw new NotFoundError();
  const s = scoreAgainst(cand, c);
  const updated = await prisma.contentCandidate.update({
    where: { id: cand.id },
    data: {
      campaignId,
      category: s.category,
      targetMatch: s.targetMatch,
      relevanceScore: s.relevanceScore,
      suitable: s.suitable,
      suitabilityNote: s.note,
      lastCheckedAt: new Date(),
    },
  });
  await audit(ctx, "candidate.link", "ContentCandidate", cand.id, `'${cand.title}' → 캠페인 '${c.name}' 연결 (관련성 ${s.relevanceScore})`);
  return updated;
}

export async function setCandidateReview(ctx: Ctx, candidateId: string, status: ReviewStatus) {
  assertCan(ctx, "candidate:write");
  const cand = await prisma.contentCandidate.findFirst({ where: { AND: [candidateWhere(ctx), { id: candidateId }] } });
  if (!cand) throw new NotFoundError();
  await prisma.contentCandidate.update({ where: { id: cand.id }, data: { reviewStatus: status } });
  await audit(ctx, "candidate.review", "ContentCandidate", cand.id, `'${cand.title}' 검토 상태 → ${status}`);
}

export async function candidateOptionsFor(ctx: Ctx, campaignId?: string) {
  return prisma.contentCandidate.findMany({
    where: { AND: [candidateWhere(ctx), campaignId ? { OR: [{ campaignId }, { campaignId: null }] } : {}] },
    select: { id: true, title: true, platform: true, accountName: true, campaignId: true, suitable: true },
    orderBy: [{ campaignId: { sort: "asc", nulls: "last" } }, { createdAt: "desc" }],
    take: 200,
  });
}
