"use server";
import type { ApprovalGate, RiskLevel, Role } from "@prisma/client";
import { revalidatePath } from "next/cache";
import { requireCtx } from "@/lib/auth/current";
import { deleteTeam, saveTeam } from "@/lib/services/teams";
import { deleteRule, saveRule } from "@/lib/services/approvals";
import { toActionError } from "@/lib/actions";
import type { ActionState } from "@/lib/action-state";

const ROLES: Role[] = ["ADMIN", "CAMPAIGN_MANAGER", "CONTENT_WRITER", "REVIEWER", "VIEWER"];

export async function saveTeamAction(_prev: ActionState, fd: FormData): Promise<ActionState> {
  const ctx = await requireCtx();
  const id = String(fd.get("id") ?? "") || null;
  try {
    await saveTeam(ctx, id, { name: String(fd.get("name") ?? ""), description: String(fd.get("description") ?? ""), leadId: String(fd.get("leadId") ?? "") || null });
  } catch (e) {
    return toActionError(e);
  }
  revalidatePath("/organization");
  return { ok: true, message: id ? "팀을 수정했습니다." : "팀을 만들었습니다." };
}

export async function deleteTeamAction(_prev: ActionState, fd: FormData): Promise<ActionState> {
  const ctx = await requireCtx();
  try {
    await deleteTeam(ctx, String(fd.get("id")));
  } catch (e) {
    return toActionError(e);
  }
  revalidatePath("/organization");
  return { ok: true, message: "팀을 삭제했습니다." };
}

export async function saveRuleAction(_prev: ActionState, fd: FormData): Promise<ActionState> {
  const ctx = await requireCtx();
  const id = String(fd.get("id") ?? "") || null;
  const gate = String(fd.get("gate")) as ApprovalGate;
  if (!["CONTENT", "QUOTE", "CONTRACT"].includes(gate)) return { ok: false, message: "업무를 선택하세요." };
  const minAmountRaw = String(fd.get("minAmount") ?? "").replace(/[^\d]/g, "");
  const minRiskRaw = String(fd.get("minRisk") ?? "");
  const steps = fd.getAll("steps").map(String).filter((s): s is Role => (ROLES as string[]).includes(s));
  const name = String(fd.get("name") ?? "").trim();
  if (!name) return { ok: false, message: "규칙 이름을 입력하세요." };
  try {
    await saveRule(ctx, id, {
      gate,
      name,
      minAmount: minAmountRaw ? Number(minAmountRaw) : null,
      minRisk: ["LOW", "MEDIUM", "HIGH"].includes(minRiskRaw) ? (minRiskRaw as RiskLevel) : null,
      steps,
      aiPrecheck: fd.get("aiPrecheck") === "on",
      active: id ? fd.get("active") === "on" : true,
    });
  } catch (e) {
    return toActionError(e);
  }
  revalidatePath("/settings/approval-rules");
  revalidatePath("/organization");
  return { ok: true, message: "결재 규칙을 저장했습니다." };
}

export async function deleteRuleAction(_prev: ActionState, fd: FormData): Promise<ActionState> {
  const ctx = await requireCtx();
  try {
    await deleteRule(ctx, String(fd.get("id")));
  } catch (e) {
    return toActionError(e);
  }
  revalidatePath("/settings/approval-rules");
  return { ok: true, message: "규칙을 삭제했습니다." };
}
