"use client";
import { useState } from "react";
import type { InquirySource } from "@prisma/client";
import { useActionForm } from "@/components/ui/use-action-form";
import { convertInquiryAction, markLostAction, saveQuoteAction } from "@/app/actions/inquiries";
import { buildReply } from "@/lib/inquiry/reply";
import type { ParsedInquiry } from "@/lib/inquiry/parser";
import { CHANNEL_LABEL, type MediaPlan, type TierKey } from "@/lib/inquiry/planner";
import { won } from "@/lib/format";
import { FormMessage } from "@/components/ui/form-status";
import { SubmitButton } from "@/components/ui/submit-button";
import { Button } from "@/components/ui/button";

export function QuotePanel({
  id,
  customerName,
  source,
  parsed,
  plan,
  initialTier,
  initialReply,
  canConvert,
  locked,
}: {
  id: string;
  customerName: string;
  source: InquirySource;
  parsed: ParsedInquiry;
  plan: MediaPlan;
  initialTier: TierKey;
  initialReply: string;
  canConvert: boolean;
  locked: boolean;
}) {
  const [tier, setTier] = useState<TierKey>(initialTier);
  const [reply, setReply] = useState(initialReply);
  const [edited, setEdited] = useState(false);
  const [copied, setCopied] = useState(false);
  const quote = useActionForm(saveQuoteAction);
  const convert = useActionForm(convertInquiryAction);

  const pickTier = (t: TierKey) => {
    setTier(t);
    // 담당자가 직접 고친 답변은 덮어쓰지 않는다
    if (!edited) setReply(buildReply({ customerName, source, parsed, plan, selectedTier: t }));
  };
  const copy = async () => {
    try {
      await navigator.clipboard.writeText(reply);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      setCopied(false);
    }
  };

  return (
    <div className="space-y-5">
      <fieldset disabled={locked}>
        <legend className="mb-2 text-sm font-semibold text-slate-900">견적안 선택</legend>
        <div className="grid gap-3 md:grid-cols-3">
          {plan.tiers.map((t) => (
            <label
              key={t.key}
              className={`cursor-pointer rounded-xl border p-4 transition ${tier === t.key ? "border-brand-500 bg-brand-50 ring-2 ring-brand-100" : "border-slate-200 bg-white hover:border-slate-300"}`}
            >
              <input type="radio" name="tier-pick" value={t.key} checked={tier === t.key} onChange={() => pickTier(t.key)} className="sr-only" />
              <div className="flex items-center justify-between">
                <span className="font-semibold">{t.label}</span>
                {plan.recommendedTier === t.key && <span className="rounded-full bg-brand-600 px-2 py-0.5 text-xs text-white">추천</span>}
              </div>
              <p className="mt-1 text-xl font-bold tabular-nums">{won(t.total)}</p>
              {t.items.length === 0 ? (
                <p className="mt-2 text-xs text-rose-600">카탈로그에 해당 상품이 없습니다.</p>
              ) : (
                <ul className="mt-2 space-y-1 text-xs text-slate-600">
                  {t.items.map((i) => (
                    <li key={i.packageId}>
                      · {i.name}
                      {i.quantity > 1 && ` × ${i.quantity}`} <span className="text-slate-400">({won(i.subtotal)}/{i.unit})</span>
                    </li>
                  ))}
                  {t.mediaSpend && <li className="text-amber-700">+ 매체비 별도 월 {won(t.mediaSpend.min)}~{won(t.mediaSpend.max)} 권장</li>}
                </ul>
              )}
              <p className="mt-2 text-[11px] text-slate-400">{[...new Set(t.items.map((i) => CHANNEL_LABEL[i.channel]))].join(" · ")}</p>
            </label>
          ))}
        </div>
      </fieldset>

      <form ref={quote.formRef} method="post" onSubmit={quote.onSubmit} className="space-y-2">
        <input type="hidden" name="id" value={id} />
        <input type="hidden" name="tier" value={tier} />
        <div className="flex items-end justify-between">
          <label htmlFor="replyDraft" className="label">고객 답변 초안 {edited && <span className="text-xs font-normal text-slate-400">(직접 수정됨)</span>}</label>
          <Button type="button" variant="secondary" size="sm" onClick={copy}>{copied ? "복사됨 ✓" : "답변 복사"}</Button>
        </div>
        <textarea
          id="replyDraft"
          name="replyDraft"
          rows={18}
          value={reply}
          onChange={(e) => {
            setReply(e.target.value);
            setEdited(true);
          }}
          className="input font-sans text-sm leading-relaxed"
          disabled={locked}
        />
        <FormMessage state={quote.state} />
        {!locked && (
          <SubmitButton pending={quote.pending} variant="secondary" pendingText="저장 중…">견적·답변 저장 (견적 발송 처리)</SubmitButton>
        )}
      </form>

      {canConvert && !locked && (
        <form ref={convert.formRef} method="post" onSubmit={convert.onSubmit} className="rounded-xl border border-emerald-200 bg-emerald-50 p-4">
          <input type="hidden" name="id" value={id} />
          <input type="hidden" name="tier" value={tier} />
          <p className="text-sm font-semibold text-emerald-900">계약이 확정되었나요?</p>
          <p className="mt-1 text-xs text-emerald-800">
            선택한 {plan.tiers.find((t) => t.key === tier)?.label} 기준으로 고객·브랜드 프로필·캠페인·매체별 집행 작업이 자동 생성되고 AI 분석이 실행됩니다.
          </p>
          <FormMessage state={convert.state} />
          <div className="mt-3">
            <SubmitButton pending={convert.pending} variant="success" pendingText="전환 중…">계약 전환 (캠페인 생성)</SubmitButton>
          </div>
        </form>
      )}
    </div>
  );
}

export function LostForm({ id }: { id: string }) {
  const { state, pending, onSubmit, formRef } = useActionForm(markLostAction);
  return (
    <form ref={formRef} method="post" onSubmit={onSubmit} className="space-y-2">
      <input type="hidden" name="id" value={id} />
      <label htmlFor="lost-reason" className="sr-only">미계약 사유</label>
      <input id="lost-reason" name="reason" placeholder="미계약 사유 (예: 예산 부족)" className="input" />
      <FormMessage state={state} />
      <SubmitButton pending={pending} size="sm" variant="ghost" pendingText="처리 중…">미계약으로 종료</SubmitButton>
    </form>
  );
}
