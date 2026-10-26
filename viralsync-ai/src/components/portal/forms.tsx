"use client";
import { useActionForm } from "@/components/ui/use-action-form";
import { portalDecideAction, portalLinkAction, portalUploadAction } from "@/app/actions/portal";
import { FormMessage } from "@/components/ui/form-status";
import { SubmitButton } from "@/components/ui/submit-button";

export function PortalDecision({ token, contentId }: { token: string; contentId: string }) {
  const { pending, onSubmit, formRef } = useActionForm(portalDecideAction, { errorToast: true });
  return (
    <form ref={formRef} method="post" onSubmit={onSubmit} className="space-y-2">
      <input type="hidden" name="token" value={token} />
      <input type="hidden" name="contentId" value={contentId} />
      <label htmlFor={`cm-${contentId}`} className="sr-only">의견</label>
      <input id={`cm-${contentId}`} name="comment" placeholder="고칠 점 (수정 요청 시 필수)" className="input text-sm" />
      <div className="flex gap-2">
        <SubmitButton pending={pending} name="decision" value="APPROVED" pendingText="…">👍 이대로 올려 주세요</SubmitButton>
        <SubmitButton pending={pending} variant="secondary" name="decision" value="CHANGES_REQUESTED" pendingText="…">✏️ 수정 요청</SubmitButton>
      </div>
    </form>
  );
}

export function PortalUpload({ token }: { token: string }) {
  const { state, pending, onSubmit, formRef } = useActionForm(portalUploadAction, { resetOnSuccess: true });
  return (
    <form ref={formRef} method="post" onSubmit={onSubmit} encType="multipart/form-data" className="space-y-2" aria-label="사진 보내기">
      <input type="hidden" name="token" value={token} />
      <label htmlFor="photos" className="label">가게 사진 (JPG·PNG, 한 번에 10장까지)</label>
      <input id="photos" name="photos" type="file" accept="image/jpeg,image/png" multiple className="block w-full text-sm" />
      <label htmlFor="note" className="label">한마디 (선택)</label>
      <input id="note" name="note" placeholder="예: 이번 주 신메뉴예요" className="input" />
      <SubmitButton pending={pending} pendingText="보내는 중…">사진 보내기</SubmitButton>
      <FormMessage state={state} />
    </form>
  );
}

export function PortalLinkButton({ clientId, rotate, label }: { clientId: string; rotate?: boolean; label: string }) {
  const { pending, onSubmit, formRef } = useActionForm(portalLinkAction, { errorToast: true });
  return (
    <form ref={formRef} method="post" onSubmit={onSubmit}>
      <input type="hidden" name="clientId" value={clientId} />
      {rotate && <input type="hidden" name="rotate" value="1" />}
      <SubmitButton pending={pending} size="sm" variant={rotate ? "secondary" : "primary"} pendingText="…">{label}</SubmitButton>
    </form>
  );
}
