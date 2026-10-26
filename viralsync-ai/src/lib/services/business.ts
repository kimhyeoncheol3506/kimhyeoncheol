import { prisma } from "@/lib/db";
import { assertCan, type Ctx } from "@/lib/auth/context";
import { CLIENT_GOALS, failureSignals, MONEY, priceRaiseSignal, spinoffConditions } from "@/lib/business/playbook";
import { ROADMAP_KEYS } from "@/lib/business/roadmap";
import { won } from "@/lib/format";
import { audit } from "./audit";

/** 사업 운영 숫자: 재무(PART 10)·실패 신호(16)·분사 조건(13)·가격 인상(11-4)·실행표(17) */

function monthStart(offset = 0, now = new Date()) {
  return new Date(now.getFullYear(), now.getMonth() + offset, 1);
}

export async function businessProfile(ctx: Ctx) {
  return prisma.organization.findUniqueOrThrow({
    where: { id: ctx.organizationId },
    select: { name: true, positioning: true, targetIndustry: true, businessStartDate: true, cashReserveKrw: true },
  });
}

export async function saveBusinessProfile(ctx: Ctx, i: { positioning: string; targetIndustry: string; businessStartDate: Date | null; cashReserveKrw: number | null }) {
  assertCan(ctx, "finance:manage");
  if (i.positioning.length > 120) throw new Error("포지셔닝 한 문장은 120자 이내로 줄여 주세요.");
  await prisma.organization.update({ where: { id: ctx.organizationId }, data: { positioning: i.positioning.trim(), targetIndustry: i.targetIndustry.trim(), businessStartDate: i.businessStartDate, cashReserveKrw: i.cashReserveKrw } });
  await audit(ctx, "business.profile", "Organization", ctx.organizationId, `사업 기본값 저장${i.cashReserveKrw != null ? ` · 잔고 ${won(i.cashReserveKrw)}` : ""}`);
}

export async function listFixedCosts(ctx: Ctx) {
  assertCan(ctx, "cost:read");
  return prisma.fixedCost.findMany({ where: { organizationId: ctx.organizationId }, orderBy: [{ active: "desc" }, { monthlyKrw: "desc" }] });
}

export async function saveFixedCost(ctx: Ctx, id: string | null, i: { name: string; category: string; monthlyKrw: number; active: boolean }) {
  assertCan(ctx, "finance:manage");
  if (!i.name.trim() || i.monthlyKrw < 0) throw new Error("항목 이름과 금액을 확인하세요.");
  if (id) {
    const f = await prisma.fixedCost.findFirst({ where: { id, organizationId: ctx.organizationId } });
    if (!f) throw new Error("항목을 찾을 수 없습니다.");
    await prisma.fixedCost.update({ where: { id }, data: i });
  } else await prisma.fixedCost.create({ data: { ...i, organizationId: ctx.organizationId } });
  await audit(ctx, "finance.fixed", "FixedCost", id, `고정비 ‘${i.name}’ ${won(i.monthlyKrw)}/월${i.active ? "" : " (중지)"}`);
}

export async function deleteFixedCost(ctx: Ctx, id: string) {
  assertCan(ctx, "finance:manage");
  await prisma.fixedCost.deleteMany({ where: { id, organizationId: ctx.organizationId } });
}

/** 재무 요약 — 매출은 ‘입금 확인’ 기준 */
export async function financeSummary(ctx: Ctx, now = new Date()) {
  assertCan(ctx, "cost:read");
  const org = ctx.organizationId;
  const from = monthStart(-5, now);
  const [subs, paid, unpaid, fixed, aiCosts, profile, inquiries, replied, waitlist, ended, manualsDone] = await Promise.all([
    prisma.subscription.findMany({ where: { organizationId: org, status: { in: ["ACTIVE", "TRIAL", "SUSPENDED"] } }, select: { status: true, monthlyFee: true } }),
    prisma.payment.findMany({ where: { organizationId: org, paidAt: { gte: from } }, select: { amount: true, paidAt: true } }),
    prisma.payment.findMany({ where: { organizationId: org, paidAt: null, dueDate: { lt: now } }, select: { amount: true } }),
    prisma.fixedCost.findMany({ where: { organizationId: org, active: true } }),
    prisma.costRecord.findMany({ where: { organizationId: org, type: "AI_GENERATION", incurredAt: { gte: from } }, select: { amountKrw: true, incurredAt: true } }),
    businessProfile(ctx),
    prisma.inquiry.count({ where: { organizationId: org, createdAt: { gte: monthStart(0, now) } } }),
    prisma.prospect.count({ where: { organizationId: org, repliedAt: { gte: monthStart(0, now) } } }),
    prisma.prospect.count({ where: { organizationId: org, stage: "WAITLIST", updatedAt: { gte: monthStart(0, now) } } }),
    prisma.subscription.count({ where: { organizationId: org, status: "ENDED", updatedAt: { gte: new Date(now.getTime() - 30 * 86_400_000) } } }),
    prisma.roadmapCheck.count({ where: { organizationId: org, itemKey: "w20-manuals" } }),
  ]);
  const active = subs.filter((s) => s.status === "ACTIVE");
  const mrr = active.reduce((a, s) => a + s.monthlyFee, 0);
  const fixedTotal = fixed.reduce((a, f) => a + f.monthlyKrw, 0);
  const toolTotal = fixed.filter((f) => f.category === "도구·구독").reduce((a, f) => a + f.monthlyKrw, 0);

  const months = Array.from({ length: 6 }, (_, i) => monthStart(i - 5, now));
  const key = (d: Date) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
  const series = months.map((m) => {
    const k = key(m);
    const revenue = paid.filter((p) => p.paidAt && key(p.paidAt) === k).reduce((a, p) => a + p.amount, 0);
    const ai = aiCosts.filter((c) => key(c.incurredAt) === k).reduce((a, c) => a + c.amountKrw, 0);
    return { month: k, revenue, ai, profit: revenue - fixedTotal - ai };
  });
  const thisMonth = series[series.length - 1];
  const paying = active.length;
  const goal = CLIENT_GOALS.find((g) => g > paying) ?? CLIENT_GOALS[CLIENT_GOALS.length - 1];
  const churnRate = paying + ended > 0 ? Math.round((ended / (paying + ended)) * 100) : null;
  // 시작한 지 한 달이 안 된 사업은 ‘3개월 연속 하락’ 판단에서 빈 달을 빼고 본다
  const started = series.findIndex((s) => s.revenue > 0);
  const failure = failureSignals({
    monthlyRevenue: started >= 0 ? series.slice(started).map((s) => s.revenue) : [],
    newInquiriesThisMonth: inquiries + replied,
    cashReserve: profile.cashReserveKrw,
    fixedCosts: fixedTotal,
  });
  return {
    profile,
    mrr,
    paying,
    goal,
    trials: subs.filter((s) => s.status === "TRIAL").length,
    receivable: unpaid.reduce((a, p) => a + p.amount, 0),
    receivableCount: unpaid.length,
    fixed,
    fixedTotal,
    toolTotal,
    toolOver: toolTotal > MONEY.fixedCostLimit,
    series,
    thisMonth,
    taxReserve: Math.round((thisMonth.revenue * MONEY.taxReservePct) / 100),
    salaryCap: Math.round((thisMonth.revenue * MONEY.salaryCapPct) / 100),
    reserveTarget: fixedTotal * MONEY.reserveMonths,
    reserveOk: profile.cashReserveKrw != null && profile.cashReserveKrw >= fixedTotal * MONEY.reserveMonths && fixedTotal > 0,
    newSpendingBlocked: profile.cashReserveKrw == null || profile.cashReserveKrw < fixedTotal * MONEY.reserveMonths,
    forecast: [1, 2, 3].map((i) => ({ month: key(monthStart(i, now)), inflow: mrr, outflow: fixedTotal + Math.round((mrr * MONEY.taxReservePct) / 100) })),
    failure,
    priceRaise: priceRaiseSignal(waitlist),
    spinoff: spinoffConditions({ monthlyProfit: series.map((s) => s.profit), manualDocs: manualsDone ? 10 : 0, churnRatePct: churnRate }),
    churnRate,
  };
}

/** 52주 실행표 체크 */
export async function roadmapChecks(ctx: Ctx) {
  const rows = await prisma.roadmapCheck.findMany({ where: { organizationId: ctx.organizationId } });
  return new Map(rows.map((r) => [r.itemKey, r.doneAt]));
}

export async function toggleRoadmap(ctx: Ctx, itemKey: string, done: boolean) {
  assertCan(ctx, "sales:manage");
  if (!ROADMAP_KEYS.includes(itemKey)) throw new Error("없는 항목입니다.");
  if (done) await prisma.roadmapCheck.upsert({ where: { organizationId_itemKey: { organizationId: ctx.organizationId, itemKey } }, create: { organizationId: ctx.organizationId, itemKey, doneById: ctx.userId }, update: {} });
  else await prisma.roadmapCheck.deleteMany({ where: { organizationId: ctx.organizationId, itemKey } });
}
