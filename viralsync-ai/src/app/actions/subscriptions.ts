"use server";
import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { requireCtx } from "@/lib/auth/current";
import { createSubscription, endSubscription, markPaid, startPaid } from "@/lib/services/subscriptions";
import { toActionError } from "@/lib/actions";
import type { ActionState } from "@/lib/action-state";

export async function createSubscriptionAction(_p: ActionState, fd: FormData): Promise<ActionState> {
  const ctx = await requireCtx();
  const start = String(fd.get("startDate") ?? "");
  let id: string;
  try {
    id = (
      await createSubscription(ctx, {
        clientId: String(fd.get("clientId") ?? ""),
        planName: String(fd.get("planName") ?? ""),
        monthlyFee: Number(String(fd.get("monthlyFee") ?? "").replace(/[^\d]/g, "")) || 0,
        deliverables: String(fd.get("deliverables") ?? "").split(/\r?\n|,/).map((x) => x.trim()).filter(Boolean),
        vatIncluded: fd.get("vatIncluded") === "on",
        billingDay: Number(fd.get("billingDay") ?? 25),
        trial: fd.get("trial") === "on",
        startDate: start ? new Date(`${start}T09:00:00+09:00`) : new Date(),
        portfolioConsent: fd.get("portfolioConsent") === "on",
        caseStudyConsent: fd.get("caseStudyConsent") === "on",
        referredById: String(fd.get("referredById") ?? "") || null,
        notes: String(fd.get("notes") ?? ""),
      })
    ).id;
  } catch (e) {
    return toActionError(e);
  }
  redirect(`/subscriptions/${id}?created=1`);
}

export async function subscriptionOpAction(_p: ActionState, fd: FormData): Promise<ActionState> {
  const ctx = await requireCtx();
  const op = String(fd.get("op"));
  const id = String(fd.get("id"));
  try {
    if (op === "paid") await startPaid(ctx, id);
    else if (op === "end") await endSubscription(ctx, id, String(fd.get("reason") ?? ""));
    else if (op === "pay" || op === "unpay") await markPaid(ctx, String(fd.get("paymentId")), op === "pay");
    else return { ok: false, message: "잘못된 요청입니다." };
  } catch (e) {
    return toActionError(e);
  }
  revalidatePath("/subscriptions", "layout");
  revalidatePath("/finance");
  return { ok: true, message: { paid: "유료로 전환하고 첫 달 청구서를 만들었습니다.", end: "계약 종료를 기록했습니다.", pay: "입금을 기록했습니다.", unpay: "입금 기록을 취소했습니다." }[op] };
}
