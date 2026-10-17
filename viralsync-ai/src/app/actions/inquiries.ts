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
  try {
    await saveQuote(ctx, id, tier, String(fd.get("replyDraft") ?? ""));
  } catch (e) {
    return toActionError(e);
  }
  revalidatePath(`/inquiries/${id}`);
  revalidatePath("/inquiries");
  return { ok: true, message: "견적과 답변을 저장했습니다. 답변을 복사해 고객에게 보내세요." };
}

export async function convertInquiryAction(_prev: ActionState, fd: FormData): Promise<ActionState> {
  const ctx = await requireCtx();
  let campaignId: string;
  try {
    campaignId = (await convertInquiry(ctx, String(fd.get("id")), tierOf(fd))).campaignId;
  } catch (e) {
    return toActionError(e);
  }
  revalidatePath("/inquiries");
  revalidatePath("/campaigns");
  redirect(`/campaigns/${campaignId}?converted=1`);
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
