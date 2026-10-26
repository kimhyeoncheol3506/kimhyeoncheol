"use server";
import type { ContentType, PlatformKey } from "@prisma/client";
import { revalidatePath } from "next/cache";
import { requireCtx } from "@/lib/auth/current";
import { getProvider } from "@/lib/ai";
import { ALL_CONTENT_TYPES, editContent, generateContent, submitForReview, type Decision } from "@/lib/services/content";
import { decideRequest } from "@/lib/services/approvals";
import { PLATFORMS } from "@/lib/labels";
import { toActionError } from "@/lib/actions";
import { won } from "@/lib/format";
import type { ActionState } from "@/lib/action-state";

export async function generateAction(_prev: ActionState, fd: FormData): Promise<ActionState> {
  const ctx = await requireCtx();
  const campaignId = String(fd.get("campaignId") ?? "");
  if (!campaignId) return { ok: false, message: "캠페인을 선택하세요.", errors: { campaignId: "캠페인을 선택하세요." } };
  const types = fd.getAll("types").map(String).filter((t): t is ContentType => (ALL_CONTENT_TYPES as string[]).includes(t));
  if (types.length === 0) return { ok: false, message: "생성할 문구 유형을 하나 이상 선택하세요.", errors: { types: "하나 이상 선택하세요." } };
  const platformRaw = String(fd.get("platform") ?? "");
  const platform = (PLATFORMS as string[]).includes(platformRaw) ? (platformRaw as PlatformKey) : undefined;
  const candidateId = String(fd.get("candidateId") ?? "") || undefined;
  try {
    const { provider } = getProvider();
    const r = await generateContent(ctx, { campaignId, candidateId, platform, types }, provider);
    if (!r.ok) return { ok: false, message: `AI 생성 실패 [${r.errorCode}] ${r.errorMessage ?? ""}` };
    revalidatePath("/content");
    revalidatePath(`/campaigns/${campaignId}`);
    return { ok: true, message: `${r.created}건의 초안을 생성했습니다. (모델: ${r.model}, 비용: ${won(r.costKrw)})` };
  } catch (e) {
    return toActionError(e);
  }
}

export async function editContentAction(_prev: ActionState, fd: FormData): Promise<ActionState> {
  const ctx = await requireCtx();
  try {
    const c = await editContent(ctx, String(fd.get("id")), String(fd.get("body") ?? ""), String(fd.get("note") ?? "") || undefined);
    revalidatePath(`/campaigns/${c.campaignId}`);
    revalidatePath("/content");
    revalidatePath("/approvals");
    return { ok: true, message: "수정 내용을 저장했습니다. 수정 이력에 기록되었습니다." };
  } catch (e) {
    return toActionError(e);
  }
}

export async function submitAction(_prev: ActionState, fd: FormData): Promise<ActionState> {
  const ctx = await requireCtx();
  const ids = fd.getAll("ids").map(String).filter(Boolean);
  if (ids.length === 0) return { ok: false, message: "검토 요청할 문구를 선택하세요." };
  try {
    const n = await submitForReview(ctx, ids);
    revalidatePath("/content");
    revalidatePath("/approvals");
    const campaignId = String(fd.get("campaignId") ?? "");
    if (campaignId) revalidatePath(`/campaigns/${campaignId}`);
    return { ok: true, message: `${n}건을 검토 요청했습니다.` };
  } catch (e) {
    return toActionError(e);
  }
}

/** 결재함: 결재 요청 단위 결정 (문구·견적·계약 공통) */
export async function decideRequestAction(_prev: ActionState, fd: FormData): Promise<ActionState> {
  const ctx = await requireCtx();
  const decision = String(fd.get("decision")) as Decision;
  if (!["APPROVED", "REJECTED", "CHANGES_REQUESTED"].includes(decision)) return { ok: false, message: "잘못된 요청입니다." };
  try {
    const status = await decideRequest(ctx, String(fd.get("id")), decision, String(fd.get("comment") ?? ""), fd.getAll("checklist").map(String));
    revalidatePath("/", "layout");
    const label = decision === "APPROVED" ? (status === "APPROVED" ? "최종 승인했습니다." : "승인했습니다. 다음 결재자에게 넘어갑니다.") : decision === "REJECTED" ? "반려했습니다." : "수정을 요청했습니다.";
    return { ok: true, message: label };
  } catch (e) {
    return toActionError(e);
  }
}
