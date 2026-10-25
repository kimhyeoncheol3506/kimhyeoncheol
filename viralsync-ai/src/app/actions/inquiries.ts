"use server";
import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { requireCtx } from "@/lib/auth/current";
import { convertInquiry, createInquiry, markLost, overrideInquiry, saveQuote } from "@/lib/services/inquiries";
import { formToObject, inquiryOverrideSchema, inquirySchema, TIER_KEYS, zodErrors } from "@/lib/validation/schemas";
import type { TierKey } from "@/lib/inquiry/planner";
import { toActionError } from "@/lib/actions";
import type { ActionState } from "@/lib/action-state";

function tierOf(fd: FormData): TierKey | undefined {
  const t = String(fd.get("tier") ?? "");
  return (TIER_KEYS as readonly string[]).includes(t) ? (t as TierKey) : undefined;
}

export async function createInquiryAction(_prev: ActionState, fd: FormData): Promise<ActionState> {
  const ctx = await requireCtx();
  const parsed = inquirySchema.safeParse(formToObject(fd));
  if (!parsed.success) return { ok: false, message: "입력값을 확인하세요.", errors: zodErrors(parsed.error) };
  let id: string;
  try {
    id = (await createInquiry(ctx, parsed.data)).id;
  } catch (e) {
    return toActionError(e);
  }
  revalidatePath("/inquiries");
  redirect(`/inquiries/${id}`);
}

export async function overrideInquiryAction(_prev: ActionState, fd: FormData): Promise<ActionState> {
  const ctx = await requireCtx();
  const id = String(fd.get("id"));
  const parsed = inquiryOverrideSchema.safeParse(formToObject(fd, ["requestedChannels"]));
  if (!parsed.success) return { ok: false, message: "입력값을 확인하세요.", errors: zodErrors(parsed.error) };
  try {
    await overrideInquiry(ctx, id, parsed.data);
  } catch (e) {
    return toActionError(e);
  }
  revalidatePath(`/inquiries/${id}`);
  return { ok: true, message: "분석 내용을 반영해 견적과 답변을 다시 만들었습니다." };
}

export async function saveQuoteAction(_prev: ActionState, fd: FormData): Promise<ActionState> {
  const ctx = await requireCtx();
  const id = String(fd.get("id"));
  const tier = tierOf(fd);
  if (!tier) return { ok: false, message: "견적안을 선택하세요." };
  let pending = false;
  try {
    pending = (await saveQuote(ctx, id, tier, String(fd.get("replyDraft") ?? ""))).pendingApproval;
  } catch (e) {
    return toActionError(e);
  }
  revalidatePath(`/inquiries/${id}`);
  revalidatePath("/inquiries");
  revalidatePath("/approvals");
  return {
    ok: true,
    message: pending ? "견적이 결재 기준 이상이라 결재를 요청했습니다. 승인 후 고객에게 보내세요." : "견적과 답변을 저장했습니다. 답변을 복사해 고객에게 보내세요.",
  };
}

export async function convertInquiryAction(_prev: ActionState, fd: FormData): Promise<ActionState> {
  const ctx = await requireCtx();
  const id = String(fd.get("id"));
  let r: Awaited<ReturnType<typeof convertInquiry>>;
  try {
    r = await convertInquiry(ctx, id, tierOf(fd));
  } catch (e) {
    return toActionError(e);
  }
  revalidatePath("/inquiries");
  revalidatePath("/campaigns");
  revalidatePath("/approvals");
  if (r.pending) {
    revalidatePath(`/inquiries/${id}`);
    return { ok: true, message: "계약 금액이 결재 기준 이상이라 결재를 요청했습니다. 최종 승인되면 자동으로 캠페인이 생성됩니다." };
  }
  redirect(`/campaigns/${r.campaignId}?converted=1`);
}

export async function markLostAction(_prev: ActionState, fd: FormData): Promise<ActionState> {
  const ctx = await requireCtx();
  const id = String(fd.get("id"));
  try {
    await markLost(ctx, id, String(fd.get("reason") ?? ""));
  } catch (e) {
    return toActionError(e);
  }
  revalidatePath(`/inquiries/${id}`);
  revalidatePath("/inquiries");
  return { ok: true, message: "미계약으로 종료했습니다." };
}
