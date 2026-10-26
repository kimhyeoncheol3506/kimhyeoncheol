"use server";
import type { PlatformKey } from "@prisma/client";
import { revalidatePath } from "next/cache";
import { requireCtx } from "@/lib/auth/current";
import { getProvider } from "@/lib/ai";
import { runChannelPack } from "@/lib/services/company";
import { CHANNEL_LABEL } from "@/lib/company/channels";
import { PLATFORMS } from "@/lib/labels";
import { toActionError } from "@/lib/actions";
import type { ActionState } from "@/lib/action-state";

export async function channelPackAction(_prev: ActionState, fd: FormData): Promise<ActionState> {
  const ctx = await requireCtx();
  const campaignId = String(fd.get("campaignId") ?? "");
  const platforms = fd.getAll("platforms").map(String).filter((p): p is PlatformKey => (PLATFORMS as string[]).includes(p));
  if (platforms.length === 0) return { ok: false, message: "홍보할 매체를 하나 이상 고르세요." };
  try {
    const r = await runChannelPack(ctx, campaignId, platforms, getProvider().provider);
    revalidatePath(`/campaigns/${campaignId}`);
    revalidatePath("/", "layout");
    const head = `${r.done.map((p) => CHANNEL_LABEL[p]).join("·") || "없음"} — 초안 ${r.created}건, 결재 요청 ${r.submitted}건`;
    if (r.failed) return { ok: false, message: `${head}. ${CHANNEL_LABEL[r.failed.platform]}에서 멈췄습니다: ${r.failed.message}` };
    return { ok: true, message: `AI 팀이 작업했습니다: ${head}. 결재함에서 확인하세요.` };
  } catch (e) {
    return toActionError(e);
  }
}
