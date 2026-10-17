"use server";
import { revalidatePath } from "next/cache";
import { requireCtx } from "@/lib/auth/current";
import { runAnalysis } from "@/lib/services/campaigns";
import { toActionError } from "@/lib/actions";
import type { ActionState } from "@/lib/action-state";

export async function analyzeCampaign(_prev: ActionState, fd: FormData): Promise<ActionState> {
  const ctx = await requireCtx();
  const id = String(fd.get("id"));
  try {
    const r = await runAnalysis(ctx, id);
    revalidatePath(`/campaigns/${id}`);
    return { ok: true, message: `분석 완료: ${r.category} > ${r.subcategory} (데이터 충실도: ${r.dataSufficiency === "SUFFICIENT" ? "충분" : r.dataSufficiency === "LIMITED" ? "제한적" : "부족"})` };
  } catch (e) {
    return toActionError(e);
  }
}
