"use server";
import type { Role } from "@prisma/client";
import { revalidatePath } from "next/cache";
import { requireCtx } from "@/lib/auth/current";
import { createUser, setClientAccess, updateUserRole } from "@/lib/services/users";
import { formToObject, userSchema, zodErrors } from "@/lib/validation/schemas";
import { toActionError } from "@/lib/actions";
import type { ActionState } from "@/lib/action-state";

const ROLES: Role[] = ["ADMIN", "CAMPAIGN_MANAGER", "CONTENT_WRITER", "REVIEWER", "VIEWER"];

export async function createUserAction(_prev: ActionState, fd: FormData): Promise<ActionState> {
  const ctx = await requireCtx();
  const parsed = userSchema.safeParse(formToObject(fd));
  if (!parsed.success) return { ok: false, message: "입력값을 확인하세요.", errors: zodErrors(parsed.error) };
  try {
    await createUser(ctx, parsed.data);
    revalidatePath("/settings/users");
    return { ok: true, message: "직원을 등록했습니다." };
  } catch (e) {
    return toActionError(e);
  }
}

export async function updateUserAction(_prev: ActionState, fd: FormData): Promise<ActionState> {
  const ctx = await requireCtx();
  const role = String(fd.get("role")) as Role;
  if (!ROLES.includes(role)) return { ok: false, message: "잘못된 역할입니다." };
  try {
    const userId = String(fd.get("userId"));
    await updateUserRole(ctx, userId, role, fd.get("active") === "on");
    await setClientAccess(ctx, userId, fd.getAll("clientIds").map(String));
    revalidatePath("/settings/users");
    return { ok: true, message: "저장했습니다." };
  } catch (e) {
    return toActionError(e);
  }
}
