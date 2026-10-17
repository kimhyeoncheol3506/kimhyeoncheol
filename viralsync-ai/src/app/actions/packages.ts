"use server";
import { revalidatePath } from "next/cache";
import { requireCtx } from "@/lib/auth/current";
import { createPackage, updatePackage } from "@/lib/services/packages";
import { formToObject, packageSchema, zodErrors } from "@/lib/validation/schemas";
import { toActionError } from "@/lib/actions";
import type { ActionState } from "@/lib/action-state";

export async function savePackageAction(_prev: ActionState, fd: FormData): Promise<ActionState> {
  const ctx = await requireCtx();
  const id = String(fd.get("id") ?? "");
  const parsed = packageSchema.safeParse(formToObject(fd));
  if (!parsed.success) return { ok: false, message: "입력값을 확인하세요.", errors: zodErrors(parsed.error) };
  try {
    if (id) await updatePackage(ctx, id, { ...parsed.data, active: fd.get("active") === "on" });
    else await createPackage(ctx, parsed.data);
  } catch (e) {
    return toActionError(e);
  }
  revalidatePath("/services");
  return { ok: true, message: id ? "상품을 수정했습니다." : "상품을 등록했습니다." };
}
