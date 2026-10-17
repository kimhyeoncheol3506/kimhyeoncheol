"use server";
import type { ReviewStatus } from "@prisma/client";
import { revalidatePath } from "next/cache";
import { requireCtx } from "@/lib/auth/current";
import { createCandidate, linkCandidate, setCandidateReview } from "@/lib/services/candidates";
import { candidateSchema, formToObject, zodErrors } from "@/lib/validation/schemas";
import { toActionError } from "@/lib/actions";
import type { ActionState } from "@/lib/action-state";

export async function createCandidateAction(_prev: ActionState, fd: FormData): Promise<ActionState> {
  const ctx = await requireCtx();
  const parsed = candidateSchema.safeParse(formToObject(fd));
  if (!parsed.success) return { ok: false, message: "입력값을 확인하세요.", errors: zodErrors(parsed.error) };
  try {
    const c = await createCandidate(ctx, parsed.data);
    revalidatePath("/opportunities");
    return { ok: true, message: `후보 '${c.title}'을(를) 등록했습니다. (자동 분류: ${c.category})` };
  } catch (e) {
    return toActionError(e);
  }
}

export async function linkCandidateAction(_prev: ActionState, fd: FormData): Promise<ActionState> {
  const ctx = await requireCtx();
  try {
    const c = await linkCandidate(ctx, String(fd.get("candidateId")), String(fd.get("campaignId")));
    revalidatePath("/opportunities");
    revalidatePath(`/campaigns/${c.campaignId}`);
    return { ok: true, message: `연결 완료 · 관련성 ${c.relevanceScore} · ${c.suitable ? "적합" : "부적합"}` };
  } catch (e) {
    return toActionError(e);
  }
}

export async function reviewCandidateAction(_prev: ActionState, fd: FormData): Promise<ActionState> {
  const ctx = await requireCtx();
  const status = String(fd.get("status")) as ReviewStatus;
  if (!["UNREVIEWED", "SUITABLE", "UNSUITABLE", "ON_HOLD"].includes(status)) return { ok: false, message: "잘못된 상태입니다." };
  try {
    await setCandidateReview(ctx, String(fd.get("candidateId")), status);
    revalidatePath("/opportunities");
    return { ok: true, message: "검토 상태를 변경했습니다." };
  } catch (e) {
    return toActionError(e);
  }
}
