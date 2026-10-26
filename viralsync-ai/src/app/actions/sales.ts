"use server";
import type { ProspectStage } from "@prisma/client";
import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { requireCtx } from "@/lib/auth/current";
import { convertProspect, createProspect, importProspects, setStage, STAGE_ORDER, updateProspect, type ProspectInput } from "@/lib/services/sales";
import { toActionError } from "@/lib/actions";
import type { ActionState } from "@/lib/action-state";

const n = (v: FormDataEntryValue | null) => {
  const s = String(v ?? "").replace(/[^\d]/g, "");
  return s ? Number(s) : null;
};

function fromForm(fd: FormData): ProspectInput {
  const d = String(fd.get("lastPostAt") ?? "");
  return {
    name: String(fd.get("name") ?? ""),
    industry: String(fd.get("industry") ?? ""),
    region: String(fd.get("region") ?? ""),
    instagram: String(fd.get("instagram") ?? ""),
    followers: n(fd.get("followers")),
    lastPostAt: d ? new Date(`${d}T00:00:00+09:00`) : null,
    postsPerMonth: n(fd.get("postsPerMonth")),
    quality: n(fd.get("quality")),
    ownerName: String(fd.get("ownerName") ?? ""),
    diagnosis: String(fd.get("diagnosis") ?? ""),
    notes: String(fd.get("notes") ?? ""),
  };
}

export async function saveProspectAction(_p: ActionState, fd: FormData): Promise<ActionState> {
  const ctx = await requireCtx();
  const id = String(fd.get("id") ?? "");
  try {
    if (id) await updateProspect(ctx, id, fromForm(fd));
    else await createProspect(ctx, fromForm(fd));
  } catch (e) {
    return toActionError(e);
  }
  revalidatePath("/sales");
  return { ok: true, message: id ? "저장했습니다." : "리스트에 추가했습니다." };
}

export async function importProspectsAction(_p: ActionState, fd: FormData): Promise<ActionState> {
  const ctx = await requireCtx();
  try {
    const r = await importProspects(ctx, String(fd.get("text") ?? ""));
    revalidatePath("/sales");
    return { ok: true, message: `${r.created}곳을 추가했습니다${r.skipped ? ` (이미 있는 ${r.skipped}곳 제외)` : ""}.${r.errors.length ? ` 확인: ${r.errors.join(" / ")}` : ""}` };
  } catch (e) {
    return toActionError(e);
  }
}

export async function setStageAction(_p: ActionState, fd: FormData): Promise<ActionState> {
  const ctx = await requireCtx();
  const stage = String(fd.get("stage")) as ProspectStage;
  if (!STAGE_ORDER.includes(stage)) return { ok: false, message: "단계를 고르세요." };
  try {
    await setStage(ctx, String(fd.get("id")), stage);
  } catch (e) {
    return toActionError(e);
  }
  revalidatePath("/sales");
  revalidatePath(`/sales/${fd.get("id")}`);
  return { ok: true, message: stage === "DM_SENT" ? "DM 보냄으로 기록했습니다." : "단계를 바꿨습니다." };
}

export async function convertProspectAction(_p: ActionState, fd: FormData): Promise<ActionState> {
  const ctx = await requireCtx();
  let clientId: string;
  try {
    clientId = (await convertProspect(ctx, String(fd.get("id")))).clientId;
  } catch (e) {
    return toActionError(e);
  }
  redirect(`/subscriptions/new?clientId=${clientId}`);
}
