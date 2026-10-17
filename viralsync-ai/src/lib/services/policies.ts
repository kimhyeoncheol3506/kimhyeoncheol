import { prisma } from "@/lib/db";
import { assertCan, NotFoundError, type Ctx } from "@/lib/auth/context";
import type { PolicyInput } from "@/lib/validation/schemas";
import { audit } from "./audit";

export async function listPolicies(ctx: Ctx) {
  return prisma.policyReview.findMany({
    where: { organizationId: ctx.organizationId },
    orderBy: [{ platform: "asc" }, { updatedAt: "desc" }],
    include: { owner: { select: { name: true } } },
  });
}

export async function getPolicy(ctx: Ctx, id: string) {
  const p = await prisma.policyReview.findFirst({ where: { id, organizationId: ctx.organizationId } });
  if (!p) throw new NotFoundError();
  return p;
}

/** 공식 문서 확인 없이 '검토 완료'로 저장할 수 없도록 검토일·결과 입력을 강제 */
function validateCompletion(input: PolicyInput) {
  if (input.status === "COMPLETED" && (!input.lastReviewedAt || !input.result.trim()))
    throw new Error("검토 완료로 저장하려면 마지막 검토일과 검토 결과(공식 문서 확인 내용)를 입력하세요.");
}

export async function createPolicy(ctx: Ctx, input: PolicyInput) {
  assertCan(ctx, "policy:write");
  validateCompletion(input);
  const p = await prisma.policyReview.create({
    data: { organizationId: ctx.organizationId, ...input, lastReviewedAt: input.lastReviewedAt ?? null, ownerId: input.ownerId ?? null },
  });
  await audit(ctx, "policy.create", "PolicyReview", p.id, `${p.platform} 정책 검토 등록`);
  return p;
}

export async function updatePolicy(ctx: Ctx, id: string, input: PolicyInput) {
  assertCan(ctx, "policy:write");
  validateCompletion(input);
  const before = await getPolicy(ctx, id);
  const p = await prisma.policyReview.update({
    where: { id },
    data: { ...input, lastReviewedAt: input.lastReviewedAt ?? null, ownerId: input.ownerId ?? null },
  });
  await audit(ctx, "policy.update", "PolicyReview", id, `${p.platform} 정책 검토 수정 (${before.status} → ${p.status})`, {
    changeSummary: input.changeSummary,
  });
  return p;
}

/** 이번 달 검토 일정: 예정일이 이번 달이거나 이미 지난 항목 */
export function monthlySchedule<T extends { nextReviewAt: Date; status: string }>(rows: T[], now = new Date()) {
  const end = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth() + 1, 1));
  return {
    overdue: rows.filter((r) => r.nextReviewAt < now),
    thisMonth: rows.filter((r) => r.nextReviewAt >= now && r.nextReviewAt < end),
  };
}

export async function policyHistory(ctx: Ctx, id: string) {
  return prisma.auditLog.findMany({
    where: { organizationId: ctx.organizationId, entityType: "PolicyReview", entityId: id },
    orderBy: { createdAt: "desc" },
    include: { actor: { select: { name: true } } },
  });
}
