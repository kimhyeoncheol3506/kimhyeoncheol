"use server";
import { revalidatePath } from "next/cache";
import { requireCtx } from "@/lib/auth/current";
import { connectWithToken, createQuickPost, disconnectThreads } from "@/lib/services/threads";
import { toActionError } from "@/lib/actions";
import type { ActionState } from "@/lib/action-state";

export async function publishQuickPostAction(_prev: ActionState, fd: FormData): Promise<ActionState> {
  const ctx = await requireCtx();
  const file = fd.get("image");
  if (!(file instanceof File) || file.size === 0) return { ok: false, message: "사진이나 스크린샷을 선택하거나 붙여넣으세요." };
  const mode = String(fd.get("mode")) === "LIVE" ? "LIVE" : "SIMULATED";
  try {
    const post = await createQuickPost(ctx, {
      image: new Uint8Array(await file.arrayBuffer()),
      caption: String(fd.get("caption") ?? ""),
      isAd: fd.get("isAd") === "on",
      mode,
    });
    revalidatePath("/threads");
    if (post.status === "FAILED") return { ok: false, message: `게시 실패 [${post.errorCode}] ${post.errorMessage ?? ""}` };
    return {
      ok: true,
      message: mode === "LIVE" ? `스레드에 게시했습니다!${post.permalink ? ` ${post.permalink}` : ""}` : "[모의] 게시 완료 — 실제 스레드에는 올라가지 않았습니다.",
    };
  } catch (e) {
    return toActionError(e);
  }
}

export async function connectThreadsTokenAction(_prev: ActionState, fd: FormData): Promise<ActionState> {
  const ctx = await requireCtx();
  try {
    const name = await connectWithToken(ctx, String(fd.get("token") ?? ""));
    revalidatePath("/threads");
    return { ok: true, message: `${name} 계정을 연결했습니다.` };
  } catch (e) {
    return toActionError(e);
  }
}

export async function disconnectThreadsAction(): Promise<ActionState> {
  const ctx = await requireCtx();
  try {
    await disconnectThreads(ctx);
    revalidatePath("/threads");
    return { ok: true, message: "연결을 해제했습니다." };
  } catch (e) {
    return toActionError(e);
  }
}
