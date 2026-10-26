import type { Prisma, Subscription, SubscriptionStatus } from "@prisma/client";
import { prisma } from "@/lib/db";
import { assertCan, clientWhere, NotFoundError, type Ctx } from "@/lib/auth/context";
import { seesAllClients } from "@/lib/auth/permissions";
import { chargeFor, MONEY, MONTHLY_PLANS, REFERRAL_DISCOUNT, TRIAL } from "@/lib/business/playbook";
import { won } from "@/lib/format";
import { audit } from "./audit";

/** 월 정액 SNS·숏폼 운영대행 계약 (PART 3, 8-2, 10-4, 11-3) */

function subWhere(ctx: Ctx): Prisma.SubscriptionWhereInput {
  return { organizationId: ctx.organizationId, client: { deletedAt: null, ...(seesAllClients(ctx.role) ? {} : { id: { in: ctx.clientIds } }) } };
}

/** 판매 중인 월 정액 패키지 (서비스 상품의 ‘월 정액 SNS·숏폼 운영’) — 없으면 책의 기본 패키지 */
export async function monthlyPlans(ctx: Ctx) {
  const rows = await prisma.servicePackage.findMany({ where: { organizationId: ctx.organizationId, channel: "MONTHLY_SNS", active: true }, orderBy: { unitPrice: "asc" } });
  return rows.length ? rows.map((r) => ({ name: r.name, monthlyFee: r.unitPrice, deliverables: r.deliverables })) : MONTHLY_PLANS.map((p) => ({ name: p.name, monthlyFee: p.monthlyFee, deliverables: [...p.deliverables] }));
}

export function period(d: Date): string {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
}

function dueDateFor(p: string, billingDay: number): Date {
  const [y, m] = p.split("-").map(Number);
  const last = new Date(y, m, 0).getDate();
  return new Date(y, m - 1, Math.min(billingDay, last), 23, 59, 59);
}

export interface SubscriptionInput {
  clientId: string;
  planName: string;
  monthlyFee: number;
  deliverables: string[];
  vatIncluded: boolean;
  billingDay: number;
  trial: boolean;
  startDate: Date;
  portfolioConsent: boolean;
  caseStudyConsent: boolean;
  referredById: string | null;
  notes: string;
}

export async function createSubscription(ctx: Ctx, i: SubscriptionInput) {
  assertCan(ctx, "sales:manage");
  const client = await prisma.client.findFirst({ where: { ...clientWhere(ctx), id: i.clientId } });
  if (!client) throw new NotFoundError("고객을 찾을 수 없습니다.");
  if (!i.planName.trim() || i.monthlyFee <= 0) throw new Error("패키지와 월 금액을 확인하세요.");
  if (i.billingDay < 1 || i.billingDay > 28) throw new Error("결제일은 1~28일 중에서 고르세요.");
  if (i.referredById === i.clientId) throw new Error("소개한 고객은 다른 고객이어야 합니다.");
  const open = await prisma.subscription.findFirst({ where: { clientId: i.clientId, status: { in: ["TRIAL", "ACTIVE", "SUSPENDED"] } } });
  if (open) throw new Error("이 고객에게 진행 중인 계약이 이미 있습니다.");
  const trialEnd = new Date(i.startDate.getTime() + TRIAL.days * 86_400_000);
  const sub = await prisma.subscription.create({
    data: {
      organizationId: ctx.organizationId,
      clientId: i.clientId,
      planName: i.planName.trim(),
      monthlyFee: i.monthlyFee,
      deliverables: i.deliverables,
      vatIncluded: i.vatIncluded,
      billingDay: i.billingDay,
      status: i.trial ? "TRIAL" : "ACTIVE",
      trialStart: i.trial ? i.startDate : null,
      trialEnd: i.trial ? trialEnd : null,
      firstMonthDiscount: i.trial ? TRIAL.firstMonthDiscount : 0,
      startDate: i.trial ? null : i.startDate,
      portfolioConsent: i.portfolioConsent,
      caseStudyConsent: i.caseStudyConsent,
      referredById: i.referredById,
      notes: i.notes,
    },
  });
  await prisma.client.update({ where: { id: i.clientId }, data: { ownAccount: true } });
  if (!i.trial) await issueInvoice(sub, period(i.startDate), true);
  await audit(ctx, "subscription.create", "Subscription", sub.id, `${client.name}: ${sub.planName} ${won(sub.monthlyFee)}/월 ${i.trial ? `· ${TRIAL.days}일 무료 체험` : "· 유료 시작"}`);
  return sub;
}

async function issueInvoice(sub: Subscription, p: string, isFirstPaidMonth: boolean, tx: Prisma.TransactionClient = prisma) {
  let amount = chargeFor(sub, isFirstPaidMonth);
  // 월 중간에 시작해 결제일이 이미 지났으면 첫 청구는 7일 뒤가 기한
  const due = dueDateFor(p, sub.billingDay);
  const dueDate = isFirstPaidMonth && due.getTime() < Date.now() + 86_400_000 ? new Date(Date.now() + 7 * 86_400_000) : due;
  // 소개 할인: 소개받은 고객의 첫 유료 달
  if (isFirstPaidMonth && sub.referredById) amount = Math.max(0, amount - REFERRAL_DISCOUNT);
  return tx.payment.upsert({
    where: { subscriptionId_period: { subscriptionId: sub.id, period: p } },
    create: { organizationId: sub.organizationId, subscriptionId: sub.id, period: p, amount, dueDate, note: isFirstPaidMonth ? `첫 유료 달${sub.firstMonthDiscount ? ` ${sub.firstMonthDiscount}% 할인` : ""}${sub.referredById ? ` · 소개 할인 ${won(REFERRAL_DISCOUNT)}` : ""}` : "" },
    update: {},
  });
}

export async function getSubscription(ctx: Ctx, id: string) {
  assertCan(ctx, "campaign:read");
  const s = await prisma.subscription.findFirst({
    where: { ...subWhere(ctx), id },
    include: { client: true, referredBy: { select: { id: true, name: true } }, payments: { orderBy: { period: "desc" } } },
  });
  if (!s) throw new NotFoundError();
  return s;
}

/** 무료 체험 → 유료 전환 (첫 달 할인 청구서 발행) */
export async function startPaid(ctx: Ctx, id: string) {
  assertCan(ctx, "sales:manage");
  const s = await getSubscription(ctx, id);
  if (s.status !== "TRIAL") throw new Error("무료 체험 중인 계약만 유료로 전환할 수 있습니다.");
  const now = new Date();
  const updated = await prisma.$transaction(async (tx) => {
    const u = await tx.subscription.update({ where: { id }, data: { status: "ACTIVE", startDate: now } });
    await issueInvoice(u, period(now), true, tx);
    await tx.prospect.updateMany({ where: { clientId: s.clientId }, data: { stage: "WON" } });
    return u;
  });
  await audit(ctx, "subscription.paid", "Subscription", id, `${s.client.name}: 유료 전환 (첫 달 ${s.firstMonthDiscount}% 할인)`);
  return updated;
}

/** 입금 기록. 미납으로 중지된 계약은 미납이 2회 미만이 되면 다시 운영 */
export async function markPaid(ctx: Ctx, paymentId: string, paid: boolean) {
  assertCan(ctx, "sales:manage");
  const p = await prisma.payment.findFirst({ where: { id: paymentId, subscription: subWhere(ctx) }, include: { subscription: { include: { client: { select: { name: true } } } } } });
  if (!p) throw new NotFoundError();
  await prisma.payment.update({ where: { id: paymentId }, data: { paidAt: paid ? new Date() : null } });
  await audit(ctx, paid ? "payment.paid" : "payment.unpaid", "Payment", paymentId, `${p.subscription.client.name} ${p.period} ${won(p.amount)} ${paid ? "입금 확인" : "입금 취소"}`);
  await refreshSubscription(ctx, p.subscriptionId);
}

export async function endSubscription(ctx: Ctx, id: string, reason: string) {
  assertCan(ctx, "sales:manage");
  const s = await getSubscription(ctx, id);
  if (s.status === "ENDED") return s;
  const endDate = new Date(Date.now() + s.noticeDays * 86_400_000);
  const u = await prisma.subscription.update({ where: { id }, data: { status: "ENDED", endDate, notes: [s.notes, `종료: ${reason}`].filter(Boolean).join("\n") } });
  await audit(ctx, "subscription.end", "Subscription", id, `${s.client.name}: 계약 종료 (${s.noticeDays}일 통보) — ${reason || "사유 미입력"}`);
  return u;
}

/** 미납 건수 (기한 지났는데 입금 없음) */
export function overdueCount(payments: { dueDate: Date; paidAt: Date | null }[], now = new Date()) {
  return payments.filter((p) => !p.paidAt && p.dueDate < now).length;
}

/**
 * 이번 달 청구서 발행 + 미납 2회 자동 중지 / 해소 시 재개. 화면을 열 때마다 불러도 안전(같은 달 중복 없음).
 */
export async function refreshSubscription(ctx: Ctx, id: string, now = new Date()) {
  const s = await prisma.subscription.findFirstOrThrow({ where: { id, organizationId: ctx.organizationId }, include: { payments: true, client: { select: { name: true } } } });
  if (s.status === "ACTIVE" || s.status === "SUSPENDED") {
    const cur = period(now);
    if (!s.payments.some((p) => p.period === cur)) await issueInvoice(s, cur, s.payments.length === 0);
  }
  const payments = await prisma.payment.findMany({ where: { subscriptionId: id } });
  const missed = overdueCount(payments, now);
  let status: SubscriptionStatus = s.status;
  if (s.status === "ACTIVE" && missed >= MONEY.suspendAfterMissed) status = "SUSPENDED";
  if (s.status === "SUSPENDED" && missed < MONEY.suspendAfterMissed) status = "ACTIVE";
  if (status !== s.status) {
    await prisma.subscription.update({ where: { id }, data: { status } });
    await audit(ctx, status === "SUSPENDED" ? "subscription.suspend" : "subscription.resume", "Subscription", id, `${s.client.name}: ${status === "SUSPENDED" ? `미납 ${missed}회 → 서비스 자동 중지` : "미납 해소 → 운영 재개"}`);
  }
  return { status, missed };
}

export async function listSubscriptions(ctx: Ctx) {
  assertCan(ctx, "campaign:read");
  const subs = await prisma.subscription.findMany({ where: subWhere(ctx), select: { id: true, status: true } });
  for (const s of subs.filter((x) => x.status === "ACTIVE" || x.status === "SUSPENDED")) await refreshSubscription(ctx, s.id);
  return prisma.subscription.findMany({
    where: subWhere(ctx),
    orderBy: [{ status: "asc" }, { createdAt: "desc" }],
    include: { client: { select: { id: true, name: true, industry: true } }, payments: { orderBy: { period: "desc" } } },
  });
}

/** MRR·미수금·체험 종료 임박 */
export function subscriptionSummary(subs: Awaited<ReturnType<typeof listSubscriptions>>, now = new Date()) {
  const active = subs.filter((s) => s.status === "ACTIVE");
  const mrr = active.reduce((a, s) => a + s.monthlyFee, 0);
  const receivable = subs.flatMap((s) => s.payments).filter((p) => !p.paidAt && p.dueDate < now);
  const trialsEnding = subs.filter((s) => s.status === "TRIAL" && s.trialEnd && s.trialEnd.getTime() - now.getTime() < 3 * 86_400_000);
  return {
    mrr,
    paying: active.length,
    trials: subs.filter((s) => s.status === "TRIAL").length,
    suspended: subs.filter((s) => s.status === "SUSPENDED").length,
    receivableAmount: receivable.reduce((a, p) => a + p.amount, 0),
    receivableCount: receivable.length,
    trialsEnding,
  };
}
