"use server";
import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { requireCtx } from "@/lib/auth/current";
import { createPolicy, updatePolicy } from "@/lib/services/policies";
import { formToObject, policySchema, zodErrors } from "@/lib/validation/schemas";
import { toActionError } from "@/lib/actions";
import type { ActionState } from "@/lib/action-state";

export async function savePolicy(_prev: ActionState, fd: FormData): Promise<ActionState> {
  const ctx = await requireCtx();
  const id = String(fd.get("id") ?? "");
  const parsed = policySchema.safeParse(formToObject(fd));
  if (!parsed.success) return { ok: false, message: "입력값을 확인하세요.", errors: zodErrors(parsed.error) };
  let newId: string | null = null;
  try {
    if (id) await updatePolicy(ctx, id, parsed.data);
    else newId = (await createPolicy(ctx, parsed.data)).id;
  } catch (e) {
    return toActionError(e);
  }
  revalidatePath("/policies");
  if (newId) redirect(`/policies/${newId}`);
  revalidatePath(`/policies/${id}`);
  return { ok: true, message: "정책 검토 내용을 저장했습니다. 변경 이력에 기록되었습니다." };
}
