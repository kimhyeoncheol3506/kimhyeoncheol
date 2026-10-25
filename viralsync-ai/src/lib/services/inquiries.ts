import type { CampaignGoal, InquiryStatus, PlatformKey, Prisma, ServiceChannel, TargetType } from "@prisma/client";
import { prisma } from "@/lib/db";
import { assertCan, NotFoundError, type Ctx } from "@/lib/auth/context";
import { parseInquiry, type BusinessType, type ParsedInquiry } from "@/lib/inquiry/parser";
import { buildMediaPlan, type MediaPlan, type TierKey } from "@/lib/inquiry/planner";
import { buildReply } from "@/lib/inquiry/reply";
import type { InquiryInput, InquiryOverride } from "@/lib/validation/schemas";
import { audit } from "./audit";
import { catalogOf } from "./packages";
import { runAnalysis } from "./campaigns";
import { openRequest } from "./approvals";
import { reviewQuote } from "@/lib/approval/ai-review";

export const INQUIRY_PAGE_SIZE = 15;

export async function listInquiries(ctx: Ctx, f: { status?: InquiryStatus; q?: string; page?: number } = {}) {
  assertCan(ctx, "inquiry:manage");
  const page = Math.max(1, f.page ?? 1);
  const where: Prisma.InquiryWhereInput = {
    organizationId: ctx.organizationId,
    ...(f.status ? { status: f.status } : {}),
    ...(f.q ? { OR: [{ customerName: { contains: f.q, mode: "insensitive" } }, { rawText: { contains: f.q, mode: "insensitive" } }] } : {}),
  };
  const [total, rows, counts] = await Promise.all([
    prisma.inquiry.count({ where }),
    prisma.inquiry.findMany({
      where,
      orderBy: { receivedAt: "desc" },
      skip: (page - 1) * INQUIRY_PAGE_SIZE,
      take: INQUIRY_PAGE_SIZE,
      include: { assignee: { select: { name: true } } },
    }),
    prisma.inquiry.groupBy({ by: ["status"], where: { organizationId: ctx.organizationId }, _count: { _all: true } }),
  ]);
  const byStatus = Object.fromEntries(counts.map((c) => [c.status, c._count._all])) as Partial<Record<InquiryStatus, number>>;
  return { total, page, pageCount: Math.max(1, Math.ceil(total / INQUIRY_PAGE_SIZE)), rows, byStatus };
}

export async function getInquiry(ctx: Ctx, id: string) {
  assertCan(ctx, "inquiry:manage");
  const q = await prisma.inquiry.findFirst({
    where: { id, organizationId: ctx.organizationId },
    include: { assignee: { select: { name: true } }, client: { select: { id: true, name: true } }, campaign: { select: { id: true, name: true } } },
  });
  if (!q) throw new NotFoundError();
  return { ...q, parsedData: q.parsed as unknown as ParsedInquiry | null, planData: q.plan as unknown as MediaPlan | null };
}

async function analyze(organizationId: string, customerName: string, source: InquiryInput["source"], parsed: ParsedInquiry, selectedTier?: TierKey | null) {
  const plan = buildMediaPlan(parsed, await catalogOf(organizationId));
  const tier = selectedTier ?? plan.recommendedTier;
  const replyDraft = buildReply({ customerName, source, parsed, plan, selectedTier: tier });
  return { plan, tier, replyDraft, quoteTotal: plan.tiers.find((t) => t.key === tier)?.total ?? null };
}

/** 문의 원문 접수 → 자동 분석·견적·답변 초안 */
export async function createInquiry(ctx: Ctx, input: InquiryInput) {
  assertCan(ctx, "inquiry:manage");
  const parsed = parseInquiry(input.rawText);
  const a = await analyze(ctx.organizationId, input.customerName, input.source, parsed);
  const q = await prisma.inquiry.create({
    data: {
      organizationId: ctx.organizationId,
      source: input.source,
      customerName: input.customerName,
      contactInfo: input.contactInfo ?? null,
      rawText: input.rawText,
      parsed: parsed as unknown as Prisma.InputJsonValue,
      plan: a.plan as unknown as Prisma.InputJsonValue,
      selectedTier: a.tier,
      quoteTotal: a.quoteTotal,
      replyDraft: a.replyDraft,
      assigneeId: ctx.userId,
    },
  });
  await audit(ctx, "inquiry.create", "Inquiry", q.id, `문의 접수: ${input.customerName} (${input.source})`);
  return q;
}

/** 담당자가 분석 결과(브랜드·업종·키워드·요청 매체·예산)를 고친 뒤 견적·답변을 다시 만든다 */
export async function overrideInquiry(ctx: Ctx, id: string, o: InquiryOverride) {
  const q = await getInquiry(ctx, id);
  if (q.status === "WON") throw new Error("이미 계약 전환된 문의입니다.");
  const base = q.parsedData ?? parseInquiry(q.rawText);
  const parsed: ParsedInquiry = {
    ...base,
    brand: o.brand,
    businessType: o.businessType as BusinessType,
    keywords: o.keywords,
    requestedChannels: o.requestedChannels as ServiceChannel[],
    budgetMentionedKrw: o.budget,
    missingInfo: base.missingInfo.filter(
      (m) => !(o.brand && m.startsWith("브랜드")) && !(o.budget != null && m.startsWith("월 예산")) && !(o.keywords.length && m.startsWith("노출을 원하는 키워드")),
    ),
  };
  const a = await analyze(ctx.organizationId, q.customerName, q.source, parsed);
  await prisma.inquiry.update({
    where: { id },
    data: {
      parsed: parsed as unknown as Prisma.InputJsonValue,
      plan: a.plan as unknown as Prisma.InputJsonValue,
      selectedTier: a.tier,
      quoteTotal: a.quoteTotal,
      replyDraft: a.replyDraft,
    },
  });
  await audit(ctx, "inquiry.reanalyze", "Inquiry", id, `문의 분석 수정·재견적 (${q.customerName})`);
}

/** 견적안 선택 + 답변 저장 → 결재 규칙에 따라 ‘견적 결재 대기’ 또는 바로 ‘견적 발송’ */
export async function saveQuote(ctx: Ctx, id: string, tier: TierKey, replyDraft: string) {
  const q = await getInquiry(ctx, id);
  if (q.status === "WON") throw new Error("이미 계약 전환된 문의입니다.");
  const t = q.planData?.tiers.find((x) => x.key === tier);
  if (!t) throw new Error("견적안을 찾을 수 없습니다. 다시 분석하세요.");
  if (!replyDraft.trim()) throw new Error("답변 내용을 입력하세요.");
  const ai = reviewQuote({ reply: replyDraft, total: t.total, mediaSpendSeparate: t.items.some((i) => i.mediaSpendSeparate) });
  return prisma.$transaction(async (tx) => {
    const req = await openRequest(tx, ctx, {
      gate: "QUOTE",
      entityType: "Inquiry",
      entityId: id,
      clientId: null,
      title: `${q.parsedData?.brand ?? q.customerName} 견적 ${t.label} ${t.total.toLocaleString()}원`,
      amount: t.total,
      risk: ai.findings.length ? "MEDIUM" : "LOW",
      aiReview: ai,
    });
    await tx.inquiry.update({
      where: { id },
      data: { selectedTier: tier, quoteTotal: t.total, replyDraft: replyDraft.trim(), status: req ? "PENDING_APPROVAL" : "QUOTED" },
    });
    await audit(ctx, "inquiry.quote", "Inquiry", id, `견적 ${t.label} ${t.total.toLocaleString()}원 · 답변 저장${req ? " · 결재 요청" : ""}`, undefined, tx);
    return { pendingApproval: !!req };
  });
}

export async function markLost(ctx: Ctx, id: string, reason: string) {
  const q = await getInquiry(ctx, id);
  if (q.status === "WON") throw new Error("이미 계약 전환된 문의입니다.");
  await prisma.inquiry.update({ where: { id }, data: { status: "LOST", lostReason: reason.trim() || null } });
  await audit(ctx, "inquiry.lost", "Inquiry", id, `문의 종료(미계약): ${reason || "사유 없음"}`);
}

const GOAL_BY_TYPE: Record<BusinessType, CampaignGoal> = {
  RESTAURANT: "VISITS",
  CAFE: "VISITS",
  BEAUTY: "VISITS",
  LOCAL_SERVICE: "INQUIRIES",
  MEDICAL: "INQUIRIES",
  EDUCATION: "INQUIRIES",
  COMMERCE: "PURCHASES",
  APP: "INSTALLS",
  FINANCE: "INQUIRIES",
  OTHER: "INQUIRIES",
};

const PLATFORMS_BY_CHANNEL: Partial<Record<ServiceChannel, PlatformKey[]>> = {
  BLOG: ["BLOG"],
  EXPERIENCE_GROUP: ["BLOG"],
  INSTAGRAM: ["INSTAGRAM"],
  YOUTUBE: ["YOUTUBE"],
  TIKTOK: ["TIKTOK"],
  META_AD: ["INSTAGRAM", "FACEBOOK"],
};

/**
 * 계약 전환 요청. 결재 규칙(금액 기준)에 해당하면 결재 요청만 만들고, 최종 승인 시 자동으로 전환된다.
 */
export async function convertInquiry(ctx: Ctx, id: string, tierKey?: TierKey): Promise<{ pending: true } | { pending: false; clientId: string; campaignId: string }> {
  assertCan(ctx, "client:write");
  assertCan(ctx, "campaign:write");
  const q = await getInquiry(ctx, id);
  if (q.status === "WON") throw new Error("이미 계약 전환된 문의입니다.");
  if (q.status === "PENDING_APPROVAL") throw new Error("견적 결재가 끝나지 않았습니다. 결재 완료 후 계약 전환하세요.");
  const plan = q.planData;
  const tier = plan?.tiers.find((t) => t.key === (tierKey ?? (q.selectedTier as TierKey | null) ?? plan.recommendedTier));
  if (!plan || !tier || tier.items.length === 0) throw new Error("선택한 견적안에 상품이 없습니다. 서비스 상품을 먼저 등록하세요.");
  const req = await prisma.$transaction((tx) =>
    openRequest(tx, ctx, {
      gate: "CONTRACT",
      entityType: "Inquiry",
      entityId: id,
      clientId: null,
      title: `${q.parsedData?.brand ?? q.customerName} 계약 ${tier.label} ${tier.total.toLocaleString()}원`,
      amount: tier.total,
      risk: "LOW",
      aiReview: { agent: "compliance", passed: true, findings: [] },
      payload: { tier: tier.key },
    }),
  );
  if (req) return { pending: true };
  return { pending: false, ...(await performConversion(ctx, id, tier.key)) };
}

/** 계약 확정: 고객 + 브랜드 프로필 + 캠페인(의뢰서) + 매체별 집행 작업을 한 번에 생성 */
export async function performConversion(ctx: Ctx, id: string, tierKey?: TierKey) {
  assertCan(ctx, "client:write");
  assertCan(ctx, "campaign:write");
  const q = await getInquiry(ctx, id);
  if (q.status === "WON") throw new Error("이미 계약 전환된 문의입니다.");
  const parsed = q.parsedData;
  const plan = q.planData;
  if (!parsed || !plan) throw new Error("분석 결과가 없습니다. 다시 분석하세요.");
  const tier = plan.tiers.find((t) => t.key === (tierKey ?? (q.selectedTier as TierKey | null) ?? plan.recommendedTier));
  if (!tier || tier.items.length === 0) throw new Error("선택한 견적안에 상품이 없습니다. 서비스 상품을 먼저 등록하세요.");

  const channels = tier.items.map((i) => i.channel);
  const platforms = [...new Set(channels.flatMap((c) => PLATFORMS_BY_CHANNEL[c] ?? []))];
  const onlyBlog = channels.every((c) => c === "BLOG" || c === "EXPERIENCE_GROUP");
  const targetType: TargetType = parsed.businessType === "APP" ? "APP" : parsed.businessType === "COMMERCE" ? "PRODUCT" : onlyBlog ? "BLOG" : "OTHER";
  const homepage = parsed.links.find((l) => l.kind === "HOMEPAGE") ?? parsed.links[0];
  const name = parsed.brand ?? q.customerName;
  const now = Date.now();
  const packages = await prisma.servicePackage.findMany({ where: { organizationId: ctx.organizationId, id: { in: tier.items.map((i) => i.packageId) } } });

  const result = await prisma.$transaction(async (tx) => {
    const client = await tx.client.create({
      data: {
        organizationId: ctx.organizationId,
        name,
        contactName: q.customerName,
        contactEmail: null,
        contactPhone: q.contactInfo,
        promoUrl: homepage?.url ?? null,
        budget: tier.total,
        contractStart: new Date(now),
        managerId: ctx.userId,
        brandProfile: {
          create: {
            companyIntro: "",
            productDescription: "",
            coreTarget: parsed.region ? `${parsed.region} 지역 고객` : "",
            bannedPhrases: [],
            requiredPhrases: [],
            toneOfVoice: "",
          },
        },
      },
    });
    if (ctx.role !== "ADMIN") await tx.clientAccess.create({ data: { userId: ctx.userId, clientId: client.id } });
    const campaign = await tx.campaign.create({
      data: {
        organizationId: ctx.organizationId,
        clientId: client.id,
        name: `${name} ${tier.label} 광고 운영`,
        ownerId: ctx.userId,
        budget: tier.total,
        startDate: new Date(now),
        endDate: new Date(now + 30 * 86_400_000),
        brief: {
          create: {
            title: `${name} ${tier.label} 광고 운영`,
            targetUrl: homepage?.url ?? null,
            urlCheck: homepage ? { valid: true, reason: "문의에서 추출한 링크 (형식만 확인)", analyzed: false } : undefined,
            targetType,
            goal: GOAL_BY_TYPE[parsed.businessType],
            coreTarget: parsed.region ? `${parsed.region} 지역 고객` : "",
            desiredPlatforms: platforms.length ? platforms : ["BLOG"],
            keywords: parsed.keywords,
            bannedKeywords: [],
            description: `[고객 문의 원문]\n${q.rawText}`.slice(0, 5000),
          },
        },
      },
    });
    for (const item of tier.items) {
      const pkg = packages.find((p) => p.id === item.packageId);
      await tx.fulfillmentTask.create({
        data: {
          organizationId: ctx.organizationId,
          campaignId: campaign.id,
          packageId: pkg?.id ?? null,
          channel: item.channel,
          // 매체비 안내는 제목에 둔다 — note 는 담당자의 실제 작업 기록 전용 (완료 조건으로 쓰임)
          title: `${item.name}${item.quantity > 1 ? ` × ${item.quantity}` : ""}${item.mediaSpendSeparate ? " (매체비 별도·고객 계정 결제)" : ""}`,
          quantity: item.quantity,
          unitPrice: item.unitPrice,
          dueDate: new Date(now + (pkg?.leadTimeDays ?? 7) * 86_400_000),
          assigneeId: ctx.userId,
        },
      });
    }
    await tx.inquiry.update({ where: { id }, data: { status: "WON", clientId: client.id, campaignId: campaign.id, selectedTier: tier.key, quoteTotal: tier.total } });
    await audit(ctx, "inquiry.convert", "Inquiry", id, `계약 전환: ${name} ${tier.label} ${tier.total.toLocaleString()}원 (작업 ${tier.items.length}건)`, undefined, tx);
    return { clientId: client.id, campaignId: campaign.id };
  });

  // 관리자 외 역할은 방금 받은 고객 접근 권한으로 분석 실행
  const freshCtx: Ctx = { ...ctx, clientIds: [...ctx.clientIds, result.clientId] };
  try {
    await runAnalysis(freshCtx, result.campaignId);
  } catch {
    // 분석 실패는 전환을 막지 않는다 (캠페인 상세에서 다시 실행 가능)
  }
  return result;
}
