"use server";
import { revalidatePath } from "next/cache";
import { requireCtx } from "@/lib/auth/current";
import { updateTask } from "@/lib/services/tasks";
import { formToObject, taskUpdateSchema, zodErrors } from "@/lib/validation/schemas";
import { toActionError } from "@/lib/actions";
import type { ActionState } from "@/lib/action-state";

export async function updateTaskAction(_prev: ActionState, fd: FormData): Promise<ActionState> {
  const ctx = await requireCtx();
  const parsed = taskUpdateSchema.safeParse(formToObject(fd));
  if (!parsed.success) return { ok: false, message: Object.values(zodErrors(parsed.error))[0] ?? "입력값을 확인하세요.", errors: zodErrors(parsed.error) };
  try {
    const t = await updateTask(ctx, String(fd.get("id")), parsed.data);
    revalidatePath(`/campaigns/${t.campaignId}`);
    revalidatePath("/fulfillment");
    return { ok: true, message: "작업 상태를 저장했습니다." };
  } catch (e) {
    return toActionError(e);
  }
}
