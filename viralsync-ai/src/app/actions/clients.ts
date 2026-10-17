"use server";
import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { requireCtx } from "@/lib/auth/current";
import { createClient, softDeleteClient, updateClient } from "@/lib/services/clients";
import { clientSchema, formToObject, zodErrors } from "@/lib/validation/schemas";
import { toActionError } from "@/lib/actions";
import type { ActionState } from "@/lib/action-state";

export async function saveClient(_prev: ActionState, fd: FormData): Promise<ActionState> {
  const ctx = await requireCtx();
  const id = String(fd.get("id") ?? "");
  const parsed = clientSchema.safeParse(formToObject(fd));
  if (!parsed.success) return { ok: false, message: "입력값을 확인하세요.", errors: zodErrors(parsed.error) };
  let newId: string | null = null;
  try {
    if (id) await updateClient(ctx, id, parsed.data);
    else newId = (await createClient(ctx, parsed.data)).id;
  } catch (e) {
    return toActionError(e);
  }
  revalidatePath("/clients");
  if (newId) redirect(`/clients/${newId}?created=1`);
  revalidatePath(`/clients/${id}`);
  return { ok: true, message: "고객 정보가 저장되었습니다." };
}

export async function deleteClient(fd: FormData) {
  const ctx = await requireCtx();
  await softDeleteClient(ctx, String(fd.get("id")));
  revalidatePath("/clients");
  redirect("/clients");
}
