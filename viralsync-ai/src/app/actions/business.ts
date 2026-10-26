"use server";
import { revalidatePath } from "next/cache";
import { requireCtx } from "@/lib/auth/current";
import { deleteFixedCost, saveBusinessProfile, saveFixedCost, toggleRoadmap } from "@/lib/services/business";
import { toActionError } from "@/lib/actions";
import type { ActionState } from "@/lib/action-state";

const num = (v: FormDataEntryValue | null) => {
  const s = String(v ?? "").replace(/[^\d]/g, "");
  return s === "" ? null : Number(s);
};

export async function saveProfileAction(_p: ActionState, fd: FormData): Promise<ActionState> {
  const ctx = await requireCtx();
  const d = String(fd.get("businessStartDate") ?? "");
  try {
    await saveBusinessProfile(ctx, {
      positioning: String(fd.get("positioning") ?? ""),
      targetIndustry: String(fd.get("targetIndustry") ?? ""),
      businessStartDate: d ? new Date(`${d}T00:00:00+09:00`) : null,
      cashReserveKrw: num(fd.get("cashReserveKrw")),
    });
  } catch (e) {
    return toActionError(e);
  }
  revalidatePath("/", "layout");
  return { ok: true, message: "저장했습니다." };
}

export async function saveFixedCostAction(_p: ActionState, fd: FormData): Promise<ActionState> {
  const ctx = await requireCtx();
  const id = String(fd.get("id") ?? "") || null;
  try {
    await saveFixedCost(ctx, id, { name: String(fd.get("name") ?? ""), category: String(fd.get("category") ?? "기타"), monthlyKrw: num(fd.get("monthlyKrw")) ?? 0, active: fd.get("active") !== "off" });
  } catch (e) {
    return toActionError(e);
  }
  revalidatePath("/finance");
  return { ok: true, message: id ? "수정했습니다." : "고정비를 추가했습니다." };
}

export async function deleteFixedCostAction(_p: ActionState, fd: FormData): Promise<ActionState> {
  const ctx = await requireCtx();
  try {
    await deleteFixedCost(ctx, String(fd.get("id")));
  } catch (e) {
    return toActionError(e);
  }
  revalidatePath("/finance");
  return { ok: true, message: "삭제했습니다." };
}

export async function toggleRoadmapAction(_p: ActionState, fd: FormData): Promise<ActionState> {
  const ctx = await requireCtx();
  const done = fd.get("done") === "1";
  try {
    await toggleRoadmap(ctx, String(fd.get("key")), done);
  } catch (e) {
    return toActionError(e);
  }
  revalidatePath("/roadmap");
  return { ok: true, message: done ? "완료로 표시했습니다." : "완료 표시를 취소했습니다." };
}
