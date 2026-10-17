"use server";
import type { PlatformKey } from "@prisma/client";
import { revalidatePath } from "next/cache";
import { requireCtx } from "@/lib/auth/current";
import { executePublication, schedulePublication } from "@/lib/services/publications";
import { PLATFORMS, PLATFORM_LABEL } from "@/lib/labels";
import { toActionError } from "@/lib/actions";
import type { ActionState } from "@/lib/action-state";

function refresh(campaignId?: string) {
  revalidatePath("/executions");
  revalidatePath("/dashboard");
  revalidatePath("/reports");
  if (campaignId) revalidatePath(`/campaigns/${campaignId}`);
}

export async function scheduleAction(_prev: ActionState, fd: FormData): Promise<ActionState> {
  const ctx = await requireCtx();
  const p = String(fd.get("platform") ?? "");
  const platform = (PLATFORMS as string[]).includes(p) ? (p as PlatformKey) : undefined;
  try {
    const { publication, precheck } = await schedulePublication(ctx, String(fd.get("contentId")), platform);
    refresh(publication.campaignId);
    if (publication.status === "BLOCKED")
      return { ok: false, message: `사전검사에서 차단되었습니다: ${precheck.items.filter((i) => !i.passed && i.severity === "block").map((i) => i.label).join(", ")}` };
    return { ok: true, message: `${PLATFORM_LABEL[publication.platform]} 실행 대기열에 등록했습니다.` };
  } catch (e) {
    return toActionError(e);
  }
}

export async function executeAction(_prev: ActionState, fd: FormData): Promise<ActionState> {
  const ctx = await requireCtx();
  const mode = String(fd.get("mode")) === "LIVE" ? "LIVE" : "SIMULATED";
  try {
    const { publication, result } = await executePublication(ctx, String(fd.get("id")), mode);
    refresh(publication.campaignId);
    return result.ok
      ? { ok: true, message: `${mode === "SIMULATED" ? "[모의] " : ""}실행 성공 (${result.externalId})${mode === "SIMULATED" ? " · 모의 실적이 기록되었습니다." : ""}` }
      : { ok: false, message: `실행 실패 [${result.errorCode}] ${result.errorMessage ?? ""}${result.retryable ? " · 재시도할 수 있습니다." : ""}` };
  } catch (e) {
    return toActionError(e);
  }
}
