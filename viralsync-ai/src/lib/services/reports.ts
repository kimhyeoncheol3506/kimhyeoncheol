import type { MetricSource, PlatformKey, Prisma } from "@prisma/client";
import { prisma } from "@/lib/db";
import { assertCan, campaignWhere, clientWhere, type Ctx } from "@/lib/auth/context";
import { can, seesAllClients } from "@/lib/auth/permissions";
import { PLATFORMS } from "@/lib/labels";

export interface ReportFilter {
  from?: Date;
  to?: Date;
  clientId?: string;
  platform?: PlatformKey;
  /** 직원(캠페인 담당자) */
  userId?: string;
}

export function parseReportFilter(sp: Record<string, string | string[] | undefined>): ReportFilter {
  const s = (k: string) => (typeof sp[k] === "string" && sp[k] ? (sp[k] as string) : undefined);
  const d = (k: string) => {
    const v = s(k);
    if (!v) return undefined;
    const x = new Date(v);
    return Number.isNaN(x.getTime()) ? undefined : x;
  };
  const to = d("to");
  if (to) to.setUTCHours(23, 59, 59, 999);
  const platform = s("platform");
  return {
    from: d("from"),
    to,
    clientId: s("clientId"),
    platform: platform && (PLATFORMS as string[]).includes(platform) ? (platform as PlatformKey) : undefined,
    userId: s("userId"),
  };
}

function campaignFilter(ctx: Ctx, f: ReportFilter): Prisma.CampaignWhereInput {
  return { ...campaignWhere(ctx), ...(f.clientId ? { clientId: f.clientId } : {}), ...(f.userId ? { ownerId: f.userId } : {}) };
}

function range(f: ReportFilter) {
  return f.from || f.to ? { ...(f.from ? { gte: f.from } : {}), ...(f.to ? { lte: f.to } : {}) } : undefined;
}

export interface MetricTotals {
  clicks: number;
  visits: number;
  conversions: number;
  bySource: Record<MetricSource, { clicks: number; visits: number; conversions: number; records: number }>;
  unmeasured: number;
}

function emptyTotals(): MetricTotals {
  const z = () => ({ clicks: 0, visits: 0, conversions: 0, records: 0 });
  return { clicks: 0, visits: 0, conversions: 0, bySource: { SIMULATED: z(), DEMO_SEED: z(), VERIFIED: z(), NOT_MEASURED: z() }, unmeasured: 0 };
}

export async function dashboard(ctx: Ctx, f: ReportFilter = {}) {
  assertCan(ctx, "campaign:read");
  const showCost = can(ctx.role, "cost:read");
  const cw = campaignFilter(ctx, f);
  const dr = range(f);
  const pubWhere: Prisma.PublicationWhereInput = {
    organizationId: ctx.organizationId,
    campaign: cw,
    ...(f.platform ? { platform: f.platform } : {}),
  };
  const monthStart = new Date();
  monthStart.setUTCDate(1);
  monthStart.setUTCHours(0, 0, 0, 0);

  const [clients, activeCampaigns, monthCampaigns, successByPlatform, failed, blocked, pendingReview, metrics, costs, recent] = await Promise.all([
    prisma.client.count({ where: { ...clientWhere(ctx), ...(f.clientId ? { id: f.clientId } : {}) } }),
    prisma.campaign.count({ where: { ...cw, status: { in: ["ANALYZED", "PENDING_REVIEW", "CHANGES_REQUESTED", "APPROVED", "READY_TO_RUN"] } } }),
    prisma.campaign.aggregate({ where: { ...cw, createdAt: { gte: monthStart } }, _sum: { budget: true }, _count: true }),
    prisma.publication.groupBy({
      by: ["platform", "mode"],
      where: { ...pubWhere, status: "SUCCESS", ...(dr ? { executedAt: dr } : {}) },
      _count: { _all: true },
    }),
    prisma.publication.count({ where: { ...pubWhere, status: "FAILED", ...(dr ? { updatedAt: dr } : {}) } }),
    prisma.publication.count({ where: { ...pubWhere, status: "BLOCKED", ...(dr ? { createdAt: dr } : {}) } }),
    prisma.generatedContent.count({ where: { organizationId: ctx.organizationId, status: "PENDING_REVIEW", campaign: cw } }),
    prisma.performanceMetric.findMany({
      where: {
        organizationId: ctx.organizationId,
        campaign: cw,
        ...(f.platform ? { publication: { platform: f.platform } } : {}),
        ...(dr ? { date: dr } : {}),
      },
      select: { clicks: true, visits: true, conversions: true, source: true },
    }),
    showCost
      ? prisma.costRecord.groupBy({
          by: ["campaignId", "type"],
          where: { organizationId: ctx.organizationId, campaign: cw, ...(dr ? { incurredAt: dr } : {}) },
          _sum: { amountKrw: true },
        })
      : Promise.resolve([]),
    prisma.auditLog.findMany({
      where: { organizationId: ctx.organizationId, ...(seesAllClients(ctx.role) ? {} : { actorId: ctx.userId }) },
      orderBy: { createdAt: "desc" },
      take: 8,
      include: { actor: { select: { name: true } } },
    }),
  ]);

  const perPlatform = Object.fromEntries(PLATFORMS.map((p) => [p, { simulated: 0, live: 0 }])) as Record<PlatformKey, { simulated: number; live: number }>;
  for (const g of successByPlatform) perPlatform[g.platform][g.mode === "LIVE" ? "live" : "simulated"] += g._count._all;
  const published = Object.values(perPlatform).reduce((a, b) => a + b.simulated + b.live, 0);

  const totals = emptyTotals();
  for (const m of metrics) {
    const b = totals.bySource[m.source];
    b.records++;
    if (m.clicks == null && m.visits == null && m.conversions == null) {
      totals.unmeasured++;
      continue;
    }
    b.clicks += m.clicks ?? 0;
    b.visits += m.visits ?? 0;
    b.conversions += m.conversions ?? 0;
    totals.clicks += m.clicks ?? 0;
    totals.visits += m.visits ?? 0;
    totals.conversions += m.conversions ?? 0;
  }

  let aiCost = 0;
  let adSpend = 0;
  const perCampaignCost = new Map<string, { ai: number; ad: number; other: number }>();
  for (const c of costs as { campaignId: string | null; type: string; _sum: { amountKrw: number | null } }[]) {
    const amt = c._sum.amountKrw ?? 0;
    if (c.type === "AI_GENERATION") aiCost += amt;
    if (c.type === "AD_SPEND") adSpend += amt;
    if (!c.campaignId) continue;
    const e = perCampaignCost.get(c.campaignId) ?? { ai: 0, ad: 0, other: 0 };
    if (c.type === "AI_GENERATION") e.ai += amt;
    else if (c.type === "AD_SPEND") e.ad += amt;
    else e.other += amt;
    perCampaignCost.set(c.campaignId, e);
  }
  const campaignNames = perCampaignCost.size
    ? await prisma.campaign.findMany({ where: { id: { in: [...perCampaignCost.keys()] } }, select: { id: true, name: true } })
    : [];
  const campaignCosts = campaignNames
    .map((c) => {
      const e = perCampaignCost.get(c.id)!;
      return { id: c.id, name: c.name, ai: e.ai, ad: e.ad, total: e.ai + e.ad + e.other };
    })
    .sort((a, b) => b.total - a.total);

  return {
    showCost,
    clients,
    activeCampaigns,
    monthRequestAmount: showCost ? (monthCampaigns._sum.budget ?? 0) : null,
    monthRequestCount: monthCampaigns._count,
    published,
    perPlatform,
    failed,
    blocked,
    pendingReview,
    metrics: totals,
    aiCost: showCost ? aiCost : null,
    adSpend: showCost ? adSpend : null,
    campaignCosts: showCost ? campaignCosts : [],
    recent,
  };
}

export interface PublicationRow {
  id: string;
  client: string;
  campaign: string;
  campaignId: string;
  platform: PlatformKey;
  contentType: string;
  targetUrl: string | null;
  owner: string;
  approver: string;
  executedAt: Date | null;
  mode: string;
  status: string;
  errorCode: string | null;
  retryCount: number;
  clicks: number | null;
  visits: number | null;
  conversions: number | null;
  metricSource: MetricSource | "NOT_MEASURED";
  aiCost: number | null;
}

export async function publicationRows(ctx: Ctx, f: ReportFilter = {}): Promise<PublicationRow[]> {
  assertCan(ctx, "campaign:read");
  const showCost = can(ctx.role, "cost:read");
  const dr = range(f);
  const rows = await prisma.publication.findMany({
    where: {
      organizationId: ctx.organizationId,
      campaign: campaignFilter(ctx, f),
      status: { in: ["SUCCESS", "FAILED"] },
      ...(f.platform ? { platform: f.platform } : {}),
      ...(dr ? { executedAt: dr } : {}),
    },
    orderBy: { executedAt: "desc" },
    take: 2000,
    include: {
      campaign: { select: { id: true, name: true, client: { select: { name: true } }, owner: { select: { name: true } } } },
      content: {
        select: {
          type: true,
          costKrw: true,
          approvals: { where: { decision: "APPROVED" }, orderBy: { createdAt: "desc" }, take: 1, include: { reviewer: { select: { name: true } } } },
        },
      },
      metrics: true,
    },
  });
  return rows.map((p) => {
    const m = p.metrics[0];
    return {
      id: p.id,
      client: p.campaign.client.name,
      campaign: p.campaign.name,
      campaignId: p.campaign.id,
      platform: p.platform,
      contentType: p.content.type,
      targetUrl: p.targetUrl,
      owner: p.campaign.owner?.name ?? "-",
      approver: p.content.approvals[0]?.reviewer.name ?? "-",
      executedAt: p.executedAt,
      mode: p.mode,
      status: p.status,
      errorCode: p.errorCode,
      retryCount: p.retryCount,
      clicks: m?.clicks ?? null,
      visits: m?.visits ?? null,
      conversions: m?.conversions ?? null,
      metricSource: m?.source ?? "NOT_MEASURED",
      aiCost: showCost ? p.content.costKrw : null,
    };
  });
}

export interface CampaignSummaryRow {
  campaignId: string;
  client: string;
  campaign: string;
  owner: string;
  success: number;
  failed: number;
  clicks: number;
  visits: number;
  conversions: number;
  sources: string;
  adSpend: number | null;
  aiCost: number | null;
  totalCost: number | null;
}

export async function campaignSummary(ctx: Ctx, f: ReportFilter = {}): Promise<CampaignSummaryRow[]> {
  const showCost = can(ctx.role, "cost:read");
  const rows = await publicationRows(ctx, f);
  const dr = range(f);
  const campaigns = await prisma.campaign.findMany({
    where: campaignFilter(ctx, f),
    select: { id: true, name: true, client: { select: { name: true } }, owner: { select: { name: true } } },
  });
  const costs = showCost
    ? await prisma.costRecord.groupBy({
        by: ["campaignId", "type"],
        where: { organizationId: ctx.organizationId, campaignId: { in: campaigns.map((c) => c.id) }, ...(dr ? { incurredAt: dr } : {}) },
        _sum: { amountKrw: true },
      })
    : [];
  const out: CampaignSummaryRow[] = campaigns.map((c) => {
    const rs = rows.filter((r) => r.campaignId === c.id);
    const cs = costs.filter((x) => x.campaignId === c.id);
    const ad = cs.filter((x) => x.type === "AD_SPEND").reduce((a, b) => a + (b._sum.amountKrw ?? 0), 0);
    const ai = cs.filter((x) => x.type === "AI_GENERATION").reduce((a, b) => a + (b._sum.amountKrw ?? 0), 0);
    const other = cs.filter((x) => x.type === "OTHER").reduce((a, b) => a + (b._sum.amountKrw ?? 0), 0);
    return {
      campaignId: c.id,
      client: c.client.name,
      campaign: c.name,
      owner: c.owner?.name ?? "-",
      success: rs.filter((r) => r.status === "SUCCESS").length,
      failed: rs.filter((r) => r.status === "FAILED").length,
      clicks: rs.reduce((a, r) => a + (r.clicks ?? 0), 0),
      visits: rs.reduce((a, r) => a + (r.visits ?? 0), 0),
      conversions: rs.reduce((a, r) => a + (r.conversions ?? 0), 0),
      sources: [...new Set(rs.filter((r) => r.status === "SUCCESS").map((r) => r.metricSource))].join("/") || "-",
      adSpend: showCost ? ad : null,
      aiCost: showCost ? ai : null,
      totalCost: showCost ? ad + ai + other : null,
    };
  });
  return out.filter((r) => r.success + r.failed > 0 || (r.totalCost ?? 0) > 0).sort((a, b) => b.success - a.success);
}

export async function staffOptions(ctx: Ctx) {
  return prisma.user.findMany({ where: { organizationId: ctx.organizationId, active: true }, select: { id: true, name: true, role: true }, orderBy: { name: "asc" } });
}
