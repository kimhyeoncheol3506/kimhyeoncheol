import type { ApprovalDecision, ApprovalGate, ApprovalRequestStatus, Prisma, RiskLevel, Role } from "@prisma/client";
import { prisma } from "@/lib/db";
import { assertCan, ForbiddenError, NotFoundError, type Ctx } from "@/lib/auth/context";
import { seesAllClients } from "@/lib/auth/permissions";
import { loadCtx } from "@/lib/auth/load-ctx";
import { resolveRule, roleCanDecide } from "@/lib/approval/rules";
import type { AiReview } from "@/lib/approval/ai-review";
import { ROLE_LABEL } from "@/lib/labels";
import { QC_KEYS } from "@/lib/business/playbook";
import { audit } from "./audit";
import { recomputeCampaignStatus } from "./campaigns";

type Tx = Prisma.TransactionClient;

export interface OpenRequestInput {
  gate: ApprovalGate;
  entityType: string;
  entityId: string;
  clientId: string | null;
  title: string;
  amount?: number | null;
  risk: RiskLevel;
  aiReview: AiReview;
  payload?: Record<string, unknown>;
}

/**
 * 결재 요청 생성. 규칙상 결재가 필요 없으면 null 을 반환한다 (호출부가 즉시 진행).
 * 같은 대상의 진행 중 요청은 취소하고 새로 연다.
 */
export async function openRequest(tx: Tx, ctx: Ctx, input: OpenRequestInput) {
  const rules = await tx.approvalRule.findMany({ where: { organizationId: ctx.organizationId, gate: input.gate } });
  const { rule, steps } = resolveRule(rules, { gate: input.gate, amount: input.amount, risk: input.risk });
  await tx.approvalRequest.updateMany({
    where: { organizationId: ctx.organizationId, entityType: input.entityType, entityId: input.entityId, gate: input.gate, status: "PENDING" },
    data: { status: "CANCELLED", decidedAt: new Date() },
  });
  if (steps.length === 0) return null;
  const req = await tx.approvalRequest.create({
    data: {
      organizationId: ctx.organizationId,
      gate: input.gate,
      entityType: input.entityType,
      entityId: input.entityId,
      clientId: input.clientId,
      title: input.title,
      amount: input.amount ?? null,
      risk: input.risk,
      ruleId: rule?.id ?? null,
      aiReview: input.aiReview as unknown as Prisma.InputJsonValue,
      payload: (input.payload ?? undefined) as Prisma.InputJsonValue | undefined,
      requestedById: ctx.userId,
      steps: { create: steps.map((requiredRole, order) => ({ order, requiredRole })) },
    },
  });
  await audit(
    ctx,
    "approval.request",
    "ApprovalRequest",
    req.id,
    `결재 요청: ${input.title} (${steps.map((s) => ROLE_LABEL[s]).join(" → ")})${input.aiReview.passed ? "" : " · AI 1차 검토 차단 항목 있음"}`,
    undefined,
    tx,
  );
  return req;
}

function scopeWhere(ctx: Ctx): Prisma.ApprovalRequestWhereInput {
  return {
    organizationId: ctx.organizationId,
    ...(seesAllClients(ctx.role) ? {} : { OR: [{ clientId: null }, { clientId: { in: ctx.clientIds } }] }),
  };
}

const include = {
  steps: { orderBy: { order: "asc" as const }, include: { decidedBy: { select: { name: true } } } },
  requestedBy: { select: { id: true, name: true } },
  rule: { select: { name: true, aiPrecheck: true } },
};

export type RequestWithSteps = Prisma.ApprovalRequestGetPayload<{ include: typeof include }>;

/** 이 사용자가 지금 이 요청의 현재 단계를 결재할 수 있는지와, 불가하면 이유 */
export function decideBlocker(ctx: Ctx, req: RequestWithSteps): string | null {
  if (req.status !== "PENDING") return "이미 종료된 결재입니다.";
  const step = req.steps.find((s) => s.order === req.currentStep);
  if (!step) return "결재 단계를 찾을 수 없습니다.";
  if (!roleCanDecide(ctx.role, step.requiredRole)) return `${ROLE_LABEL[step.requiredRole]} 차례입니다.`;
  if (req.requestedById === ctx.userId) return "본인이 요청한 결재는 직접 승인할 수 없습니다.";
  if (req.steps.some((s) => s.decidedById === ctx.userId)) return "같은 결재의 다른 단계를 이미 처리했습니다 (한 사람이 두 단계를 결재할 수 없음).";
  return null;
}

export async function listRequests(ctx: Ctx, f: { status?: ApprovalRequestStatus; gate?: ApprovalGate; mine?: boolean } = {}) {
  assertCan(ctx, "campaign:read");
  const rows = await prisma.approvalRequest.findMany({
    where: { ...scopeWhere(ctx), ...(f.status ? { status: f.status } : {}), ...(f.gate ? { gate: f.gate } : {}) },
    orderBy: { createdAt: "desc" },
    take: 100,
    include,
  });
  return f.mine ? rows.filter((r) => decideBlocker(ctx, r) === null) : rows;
}

/** 사이드바 배지용: 지금 내가 결재할 건수 */
export async function myInboxCount(ctx: Ctx) {
  const rows = await prisma.approvalRequest.findMany({ where: { ...scopeWhere(ctx), status: "PENDING" }, include });
  return rows.filter((r) => decideBlocker(ctx, r) === null).length;
}

export async function latestRequestFor(ctx: Ctx, entityType: string, entityId: string, gate?: ApprovalGate) {
  return prisma.approvalRequest.findFirst({
    where: { ...scopeWhere(ctx), entityType, entityId, ...(gate ? { gate } : {}), NOT: { status: "CANCELLED" } },
    orderBy: { createdAt: "desc" },
    include,
  });
}

/** 결재 (승인 / 반려 / 수정 요청). 마지막 단계 승인 시 업무별 후속 처리를 실행한다. */
export async function decideRequest(ctx: Ctx, requestId: string, decision: ApprovalDecision, comment?: string, checklist: string[] = []) {
  assertCan(ctx, "approval:decide");
  const req = await prisma.approvalRequest.findFirst({ where: { ...scopeWhere(ctx), id: requestId }, include });
  if (!req) throw new NotFoundError();
  const blocker = decideBlocker(ctx, req);
  if (blocker) throw new ForbiddenError(blocker);
  const ai = req.aiReview as unknown as AiReview | null;
  if (decision === "APPROVED" && (req.rule?.aiPrecheck ?? true) && ai && !ai.passed)
    throw new Error("AI 1차 검토에서 차단된 항목이 있어 승인할 수 없습니다. 반려하거나 수정을 요청하세요.");
  if (decision !== "APPROVED" && !comment?.trim()) throw new Error("반려 또는 수정 요청 시 사유를 입력하세요.");
  // 홍보 문구 승인 전 검수 체크리스트 7개 (사업 실행 백과 PART 9-1)
  const checked = QC_KEYS.filter((k) => checklist.includes(k));
  if (req.gate === "CONTENT" && decision === "APPROVED" && checked.length < QC_KEYS.length)
    throw new Error(`검수 체크리스트 ${QC_KEYS.length}개를 모두 확인해야 승인할 수 있습니다 (${checked.length}/${QC_KEYS.length}).`);

  const step = req.steps.find((s) => s.order === req.currentStep)!;
  const isLast = req.currentStep === req.steps.length - 1;
  const finalStatus: ApprovalRequestStatus | null = decision === "APPROVED" ? (isLast ? "APPROVED" : null) : decision;

  await prisma.$transaction(async (tx) => {
    await tx.approvalStep.update({ where: { id: step.id }, data: { decision, decidedById: ctx.userId, comment: comment?.trim() || null, decidedAt: new Date(), checklist: req.gate === "CONTENT" ? checked : [] } });
    await tx.approvalRequest.update({
      where: { id: req.id },
      data: finalStatus ? { status: finalStatus, decidedAt: new Date() } : { currentStep: req.currentStep + 1 },
    });
    await audit(
      ctx,
      `approval.${decision.toLowerCase()}`,
      "ApprovalRequest",
      req.id,
      `${req.title} — ${step.order + 1}단계(${ROLE_LABEL[step.requiredRole]}) ${decision === "APPROVED" ? "승인" : decision === "REJECTED" ? "반려" : "수정 요청"}${finalStatus === "APPROVED" ? " · 최종 승인" : ""}`,
      { comment },
      tx,
    );
    if (finalStatus) await applyOutcome(tx, ctx, req, finalStatus, comment);
  });

  // 계약 전환은 트랜잭션 밖에서 요청자 권한으로 실행 (고객·캠페인·작업 생성)
  if (finalStatus === "APPROVED" && req.gate === "CONTRACT") {
    const requester = req.requestedById ? await loadCtx(req.requestedById) : null;
    const { performConversion } = await import("./inquiries");
    await performConversion(requester ?? ctx, req.entityId, (req.payload as { tier?: string } | null)?.tier as never);
  }
  return finalStatus ?? "PENDING";
}

/** 업무별 결재 결과 반영 */
async function applyOutcome(tx: Tx, ctx: Ctx, req: RequestWithSteps, status: ApprovalRequestStatus, comment?: string) {
  if (req.gate === "CONTENT") {
    const contentStatus = status === "APPROVED" ? "APPROVED" : status === "REJECTED" ? "REJECTED" : "CHANGES_REQUESTED";
    const own = await tx.generatedContent.findUniqueOrThrow({ where: { id: req.entityId }, select: { campaign: { select: { client: { select: { ownAccount: true } } } } } });
    // 고객 본인 계정 운영대행이면 내부 승인 뒤 사장님 승인을 받아야 게시할 수 있다
    const clientStatus = contentStatus === "APPROVED" && own.campaign.client.ownAccount ? ("PENDING" as const) : undefined;
    const content = await tx.generatedContent.update({ where: { id: req.entityId }, data: { status: contentStatus, ...(clientStatus ? { clientStatus } : {}) } });
    // 기존 승인 이력(보고서·CSV 의 ‘승인자’)과 호환되도록 최종 결정자를 Approval 에도 기록
    await tx.approval.create({
      data: { contentId: content.id, reviewerId: ctx.userId, decision: contentStatus === "APPROVED" ? "APPROVED" : contentStatus, comment: comment?.trim() || null },
    });
    await recomputeCampaignStatus(tx, content.campaignId);
  }
  if (req.gate === "QUOTE") {
    await tx.inquiry.update({ where: { id: req.entityId }, data: { status: status === "APPROVED" ? "QUOTED" : "NEW" } });
  }
  // CONTRACT 반려 시 문의는 ‘견적 발송’ 상태로 남는다 (승인 시 전환은 decideRequest 에서 실행)
}

export async function listRules(ctx: Ctx) {
  return prisma.approvalRule.findMany({ where: { organizationId: ctx.organizationId }, orderBy: [{ gate: "asc" }, { minAmount: "asc" }] });
}

export interface RuleInput {
  gate: ApprovalGate;
  name: string;
  minAmount: number | null;
  minRisk: RiskLevel | null;
  steps: Role[];
  aiPrecheck: boolean;
  active: boolean;
}

export async function saveRule(ctx: Ctx, id: string | null, input: RuleInput) {
  assertCan(ctx, "user:manage");
  if (input.steps.length > 4) throw new Error("결재 단계는 최대 4단계까지 설정할 수 있습니다.");
  if (input.gate === "CONTENT" && input.steps.length === 0) throw new Error("홍보 문구는 사람 승인 원칙상 최소 1단계가 필요합니다.");
  if (id) {
    const r = await prisma.approvalRule.findFirst({ where: { id, organizationId: ctx.organizationId } });
    if (!r) throw new NotFoundError();
    await prisma.approvalRule.update({ where: { id }, data: input });
  } else {
    await prisma.approvalRule.create({ data: { ...input, organizationId: ctx.organizationId } });
  }
  await audit(ctx, "approval.rule", "ApprovalRule", id, `결재 규칙 ‘${input.name}’ 저장: ${input.steps.map((s) => ROLE_LABEL[s]).join(" → ") || "결재 없음"}`);
}

export async function deleteRule(ctx: Ctx, id: string) {
  assertCan(ctx, "user:manage");
  const r = await prisma.approvalRule.findFirst({ where: { id, organizationId: ctx.organizationId } });
  if (!r) throw new NotFoundError();
  await prisma.approvalRule.delete({ where: { id } });
  await audit(ctx, "approval.rule.delete", "ApprovalRule", id, `결재 규칙 ‘${r.name}’ 삭제`);
}

/** 기본 결재 규칙 (조직 생성·시드 시) */
export const DEFAULT_RULES: Omit<RuleInput, "active">[] = [
  { gate: "CONTENT", name: "홍보 문구 기본", minAmount: null, minRisk: null, steps: ["REVIEWER"], aiPrecheck: true },
  { gate: "CONTENT", name: "고위험 문구 (민감 업종·주의 표현)", minAmount: null, minRisk: "HIGH", steps: ["REVIEWER", "ADMIN"], aiPrecheck: true },
  { gate: "QUOTE", name: "100만원 이상 견적", minAmount: 1_000_000, minRisk: null, steps: ["ADMIN"], aiPrecheck: true },
  { gate: "CONTRACT", name: "150만원 이상 계약", minAmount: 1_500_000, minRisk: null, steps: ["CAMPAIGN_MANAGER", "ADMIN"], aiPrecheck: false },
];
