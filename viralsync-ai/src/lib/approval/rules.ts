import type { ApprovalGate, RiskLevel, Role } from "@prisma/client";

export const RISK_RANK: Record<RiskLevel, number> = { LOW: 0, MEDIUM: 1, HIGH: 2 };

export interface RuleLike {
  id: string;
  gate: ApprovalGate;
  minAmount: number | null;
  minRisk: RiskLevel | null;
  steps: Role[];
  aiPrecheck: boolean;
  active: boolean;
}

/**
 * 조건에 맞는 규칙 중 가장 엄격한(단계가 가장 많은) 규칙을 고른다.
 * 맞는 규칙이 없으면 null (= 결재 없이 진행). 단, 홍보 문구는 사람 승인 원칙상 최소 1단계를 보장한다.
 */
export function resolveRule<R extends RuleLike>(rules: R[], q: { gate: ApprovalGate; amount?: number | null; risk?: RiskLevel }): { rule: R | null; steps: Role[] } {
  const matching = rules.filter(
    (r) =>
      r.active &&
      r.gate === q.gate &&
      (r.minAmount == null || (q.amount ?? 0) >= r.minAmount) &&
      (r.minRisk == null || RISK_RANK[q.risk ?? "LOW"] >= RISK_RANK[r.minRisk]),
  );
  const rule = matching.sort((a, b) => b.steps.length - a.steps.length || (b.minAmount ?? 0) - (a.minAmount ?? 0))[0] ?? null;
  let steps = rule?.steps ?? [];
  if (q.gate === "CONTENT" && steps.length === 0) steps = ["REVIEWER"];
  return { rule, steps };
}

/** 이 역할이 해당 단계를 결재할 수 있는지 (관리자는 모든 단계 대결 가능) */
export function roleCanDecide(role: Role, required: Role): boolean {
  return role === "ADMIN" || role === required;
}

export function riskFromScore(policyRisk: number | null | undefined, hasWarnings: boolean): RiskLevel {
  const base: RiskLevel = policyRisk == null ? "LOW" : policyRisk >= 60 ? "HIGH" : policyRisk >= 35 ? "MEDIUM" : "LOW";
  return hasWarnings && base === "LOW" ? "MEDIUM" : base;
}
