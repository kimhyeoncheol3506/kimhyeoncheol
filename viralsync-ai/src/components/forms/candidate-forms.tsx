"use client";
import { useActionForm } from "@/components/ui/use-action-form";
import { createCandidateAction, linkCandidateAction, reviewCandidateAction } from "@/app/actions/candidates";
import { PLATFORM_LABEL, PLATFORMS, REVIEW_STATUS_LABEL } from "@/lib/labels";
import { Field } from "@/components/ui/misc";
import { FormMessage } from "@/components/ui/form-status";
import { SubmitButton } from "@/components/ui/submit-button";

export function CandidateCreateForm() {
  const { state, pending, onSubmit, formRef } = useActionForm(createCandidateAction, { resetOnSuccess: true });
  const e = state.errors ?? {};
  return (
    <form ref={formRef} method="post" onSubmit={onSubmit} className="grid gap-3 sm:grid-cols-2" noValidate>
      <div className="sm:col-span-2">
        <FormMessage state={state} />
      </div>
      <Field label="플랫폼" htmlFor="c-platform" error={e.platform} required>
        <select id="c-platform" name="platform" className="input" defaultValue="INSTAGRAM">
          {PLATFORMS.map((p) => (
            <option key={p} value={p}>{PLATFORM_LABEL[p]}</option>
          ))}
        </select>
      </Field>
      <Field label="계정명" htmlFor="c-account" error={e.accountName} required>
        <input id="c-account" name="accountName" className="input" placeholder="@account" />
      </Field>
      <Field label="공개 프로필 URL" htmlFor="c-profile" error={e.profileUrl}>
        <input id="c-profile" name="profileUrl" type="url" className="input" placeholder="https://" />
      </Field>
      <Field label="게시물 URL" htmlFor="c-post" error={e.postUrl} required>
        <input id="c-post" name="postUrl" type="url" className="input" placeholder="https://" />
      </Field>
      <Field label="게시물 제목" htmlFor="c-title" error={e.title} required>
        <input id="c-title" name="title" className="input" />
      </Field>
      <Field label="게시물 요약" htmlFor="c-summary" error={e.summary} hint="게시물을 직접 확인하고 요약을 입력하세요. 자동 수집하지 않습니다.">
        <input id="c-summary" name="summary" className="input" />
      </Field>
      <div className="sm:col-span-2 flex justify-end">
        <SubmitButton pending={pending} pendingText="등록 중…">후보 등록</SubmitButton>
      </div>
    </form>
  );
}

export function LinkCandidateButton({ candidateId, campaignId, linked }: { candidateId: string; campaignId: string; linked: boolean }) {
  const { state, pending, onSubmit, formRef } = useActionForm(linkCandidateAction);
  return (
    <form ref={formRef} method="post" onSubmit={onSubmit} className="space-y-1">
      <input type="hidden" name="candidateId" value={candidateId} />
      <input type="hidden" name="campaignId" value={campaignId} />
      <SubmitButton pending={pending} size="sm" variant={linked ? "secondary" : "primary"} pendingText="연결 중…">{linked ? "점수 갱신" : "캠페인에 연결"}</SubmitButton>
      {state.message && !state.ok && <p className="text-xs text-rose-600" role="alert">{state.message}</p>}
    </form>
  );
}

export function ReviewSelect({ candidateId, value }: { candidateId: string; value: string }) {
  const { state, pending, onSubmit, formRef } = useActionForm(reviewCandidateAction);
  return (
    <form ref={formRef} method="post" onSubmit={onSubmit} className="flex items-center gap-1">
      <input type="hidden" name="candidateId" value={candidateId} />
      <label htmlFor={`rv-${candidateId}`} className="sr-only">검토 상태</label>
      <select id={`rv-${candidateId}`} name="status" defaultValue={value} className="input w-auto py-1 text-xs">
        {Object.entries(REVIEW_STATUS_LABEL).map(([k, v]) => (
          <option key={k} value={k}>{v}</option>
        ))}
      </select>
      <SubmitButton pending={pending} size="sm" variant="ghost" pendingText="…">저장</SubmitButton>
      {state.message && !state.ok && <span className="text-xs text-rose-600">{state.message}</span>}
    </form>
  );
}
