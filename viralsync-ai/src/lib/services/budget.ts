import { prisma } from "@/lib/db";
import { assertCan, type Ctx } from "@/lib/auth/context";
import { won } from "@/lib/format";
import { audit } from "./audit";

function monthStart(now = new Date()) {
  return new Date(now.getFullYear(), now.getMonth(), 1);
}

/** 이번 달 AI 운영비 사용액과 상한 */
export async function aiBudgetStatus(ctx: Ctx) {
  const [org, spent] = await Promise.all([
    prisma.organization.findUniqueOrThrow({ where: { id: ctx.organizationId }, select: { aiMonthlyBudgetKrw: true } }),
    prisma.costRecord.aggregate({
      where: { organizationId: ctx.organizationId, type: "AI_GENERATION", incurredAt: { gte: monthStart() } },
      _sum: { amountKrw: true },
    }),
  ]);
  const used = spent._sum.amountKrw ?? 0;
  const cap = org.aiMonthlyBudgetKrw;
  return { used, cap, reached: cap != null && used >= cap };
}

export class BudgetError extends Error {}

/**
 * 유료 AI 호출 전 예산 확인. 데모 Provider(0원)는 항상 허용한다.
 * 상한에 도달하면 새 호출을 멈춘다 — 비용을 미리 알 수 없는 호출이 상한을 넘기지 않도록.
 */
export async function assertAiBudget(ctx: Ctx, providerId: string) {
  if (providerId === "demo") return;
  const b = await aiBudgetStatus(ctx);
  if (b.cap === 0) throw new BudgetError("AI 운영비 상한이 0원(추가 지출 금지)이라 유료 AI 를 호출하지 않았습니다. 조직 화면에서 상한을 정하세요.");
  if (b.reached) throw new BudgetError(`이번 달 AI 운영비 상한(${won(b.cap!)})에 도달해 멈췄습니다. 사용 ${won(b.used)}. 상한을 올리거나 다음 달에 진행하세요.`);
}

export async function setAiBudget(ctx: Ctx, cap: number | null) {
  assertCan(ctx, "user:manage");
  if (cap != null && (!Number.isInteger(cap) || cap < 0)) throw new Error("상한은 0 이상의 정수(원)로 입력하세요.");
  await prisma.organization.update({ where: { id: ctx.organizationId }, data: { aiMonthlyBudgetKrw: cap } });
  await audit(ctx, "company.budget", "Organization", ctx.organizationId, `월 AI 운영비 상한: ${cap == null ? "미설정" : won(cap)}`);
}
