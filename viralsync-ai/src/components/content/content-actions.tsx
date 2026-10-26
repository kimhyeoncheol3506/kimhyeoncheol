"use client";
import { useActionForm } from "@/components/ui/use-action-form";
import { decideRequestAction, editContentAction, submitAction } from "@/app/actions/content";
import { FormMessage } from "@/components/ui/form-status";
import { SubmitButton } from "@/components/ui/submit-button";
import { QC_CHECKLIST } from "@/lib/business/playbook";

export function EditContentForm({ id, body }: { id: string; body: string }) {
  const { state, pending, onSubmit, formRef } = useActionForm(editContentAction, { resetOnSuccess: true });
  return (
    <details className="w-full">
      <summary className="cursor-pointer text-xs font-medium text-brand-600">문구 수정</summary>
      <form ref={formRef} method="post" onSubmit={onSubmit} className="mt-2 space-y-2">
        <input type="hidden" name="id" value={id} />
        <label htmlFor={`body-${id}`} className="sr-only">문구</label>
        <textarea id={`body-${id}`} name="body" defaultValue={body} rows={5} className="input" />
        <label htmlFor={`note-${id}`} className="sr-only">수정 메모</label>
        <input id={`note-${id}`} name="note" placeholder="수정 사유 (선택)" className="input" />
        <FormMessage state={state} />
        <SubmitButton pending={pending} size="sm" pendingText="저장 중…">수정 저장</SubmitButton>
      </form>
    </details>
  );
}

export function SubmitForReviewButton({ ids, campaignId, label = "검토 요청" }: { ids: string[]; campaignId?: string; label?: string }) {
  const { state, pending, onSubmit, formRef } = useActionForm(submitAction);
  return (
    <form ref={formRef} method="post" onSubmit={onSubmit} className="space-y-2">
      {ids.map((id) => (
        <input key={id} type="hidden" name="ids" value={id} />
      ))}
      {campaignId && <input type="hidden" name="campaignId" value={campaignId} />}
      <SubmitButton pending={pending} size="sm" variant="secondary" pendingText="요청 중…">{label}</SubmitButton>
      <FormMessage state={state} />
    </form>
  );
}

export function DecisionForm({ id, qc = false }: { id: string; qc?: boolean }) {
  const { pending, onSubmit, formRef } = useActionForm(decideRequestAction, { errorToast: true });
  return (
    <form ref={formRef} method="post" onSubmit={onSubmit} className="w-full space-y-2">
      <input type="hidden" name="id" value={id} />
      {qc && (
        <fieldset className="rounded-lg border border-slate-200 p-2">
          <legend className="px-1 text-xs font-medium text-slate-600">검수 체크리스트 — 승인 전 7개 모두 확인</legend>
          <div className="grid gap-1 sm:grid-cols-2">
            {QC_CHECKLIST.map((q) => (
              <label key={q.key} className="flex items-start gap-1.5 text-xs">
                <input type="checkbox" name="checklist" value={q.key} className="mt-0.5" />
                {q.label}
              </label>
            ))}
          </div>
        </fieldset>
      )}
      <label htmlFor={`comment-${id}`} className="sr-only">결재 의견</label>
      <input id={`comment-${id}`} name="comment" placeholder="결재 의견 (반려·수정 요청 시 필수)" className="input" />
      <div className="flex flex-wrap gap-2">
        <SubmitButton pending={pending} size="sm" variant="success" name="decision" value="APPROVED" pendingText="처리 중…">승인</SubmitButton>
        <SubmitButton pending={pending} size="sm" variant="secondary" name="decision" value="CHANGES_REQUESTED" pendingText="처리 중…">수정 요청</SubmitButton>
        <SubmitButton pending={pending} size="sm" variant="danger" name="decision" value="REJECTED" pendingText="처리 중…">반려</SubmitButton>
      </div>
    </form>
  );
}
