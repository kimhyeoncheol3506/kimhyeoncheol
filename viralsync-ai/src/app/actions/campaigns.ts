"use server";
import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { requireCtx } from "@/lib/auth/current";
import { createCampaign, softDeleteCampaign, updateCampaign } from "@/lib/services/campaigns";
import { briefSchema, formToObject, zodErrors } from "@/lib/validation/schemas";
import { toActionError } from "@/lib/actions";
import type { ActionState } from "@/lib/action-state";

export async function saveCampaign(_prev: ActionState, fd: FormData): Promise<ActionState> {
  const ctx = await requireCtx();
  const id = String(fd.get("id") ?? "");
  const parsed = briefSchema.safeParse(formToObject(fd, ["desiredPlatforms"]));
  if (!parsed.success) return { ok: false, message: "입력값을 확인하세요.", errors: zodErrors(parsed.error) };
  let targetId = id;
  try {
    if (id) await updateCampaign(ctx, id, parsed.data);
    else targetId = (await createCampaign(ctx, parsed.data)).id;
  } catch (e) {
    return toActionError(e);
  }
  revalidatePath("/campaigns");
  revalidatePath(`/campaigns/${targetId}`);
  redirect(`/campaigns/${targetId}?saved=1`);
}

export async function deleteCampaign(fd: FormData) {
  const ctx = await requireCtx();
  await softDeleteCampaign(ctx, String(fd.get("id")));
  revalidatePath("/campaigns");
  redirect("/campaigns");
}
