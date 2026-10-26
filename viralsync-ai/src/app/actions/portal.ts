"use server";
import { revalidatePath } from "next/cache";
import { requireCtx } from "@/lib/auth/current";
import { ensurePortalToken, portalDecide, portalUpload, TOKEN_RE } from "@/lib/services/portal";
import { toActionError } from "@/lib/actions";
import type { ActionState } from "@/lib/action-state";

/** 사장님 링크 화면의 액션 — 로그인 대신 링크 토큰으로 고객을 확인한다 */
export async function portalDecideAction(_p: ActionState, fd: FormData): Promise<ActionState> {
  const token = String(fd.get("token") ?? "");
  if (!TOKEN_RE.test(token)) return { ok: false, message: "링크가 올바르지 않습니다." };
  const decision = String(fd.get("decision")) === "APPROVED" ? "APPROVED" : "CHANGES_REQUESTED";
  try {
    await portalDecide(token, String(fd.get("contentId")), decision, String(fd.get("comment") ?? ""));
  } catch (e) {
    return toActionError(e);
  }
  revalidatePath(`/c/${token}`);
  return { ok: true, message: decision === "APPROVED" ? "승인했습니다. 예정된 시간에 올라갑니다." : "수정 요청을 전달했습니다." };
}

export async function portalUploadAction(_p: ActionState, fd: FormData): Promise<ActionState> {
  const token = String(fd.get("token") ?? "");
  if (!TOKEN_RE.test(token)) return { ok: false, message: "링크가 올바르지 않습니다." };
  const files = fd.getAll("photos").filter((f): f is File => f instanceof File && f.size > 0);
  if (files.length === 0) return { ok: false, message: "사진을 골라 주세요." };
  if (files.length > 10) return { ok: false, message: "한 번에 10장까지 보낼 수 있습니다." };
  try {
    for (const f of files) await portalUpload(token, new Uint8Array(await f.arrayBuffer()), String(fd.get("note") ?? ""));
  } catch (e) {
    return toActionError(e);
  }
  revalidatePath(`/c/${token}`);
  return { ok: true, message: `사진 ${files.length}장을 보냈습니다. 감사합니다!` };
}

export async function portalLinkAction(_p: ActionState, fd: FormData): Promise<ActionState> {
  const ctx = await requireCtx();
  const clientId = String(fd.get("clientId"));
  try {
    await ensurePortalToken(ctx, clientId, fd.get("rotate") === "1");
  } catch (e) {
    return toActionError(e);
  }
  revalidatePath(`/clients/${clientId}`);
  return { ok: true, message: fd.get("rotate") === "1" ? "새 링크를 만들었습니다. 이전 링크는 이제 열리지 않습니다." : "사장님 링크를 만들었습니다." };
}
