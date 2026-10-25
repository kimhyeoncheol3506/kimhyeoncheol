"use client";
import { useActionForm } from "@/components/ui/use-action-form";
import { connectThreadsTokenAction, disconnectThreadsAction } from "@/app/actions/threads";
import { FormMessage } from "@/components/ui/form-status";
import { SubmitButton } from "@/components/ui/submit-button";

export function TokenConnectForm() {
  const { state, pending, onSubmit, formRef } = useActionForm(connectThreadsTokenAction, { resetOnSuccess: true });
  return (
    <form ref={formRef} method="post" onSubmit={onSubmit} className="space-y-2" noValidate>
      <label htmlFor="th-token" className="label">Threads 액세스 토큰 붙여넣기</label>
      <input id="th-token" name="token" type="password" autoComplete="off" className="input font-mono" placeholder="THAA…" />
      <p className="text-xs text-slate-500">토큰은 암호화해서 서버에만 저장되며 화면에는 끝 4자리만 표시됩니다.</p>
      <FormMessage state={state} />
      <SubmitButton pending={pending} size="sm" pendingText="확인 중…">토큰 확인 후 연결</SubmitButton>
    </form>
  );
}

export function DisconnectForm() {
  const { state, pending, onSubmit, formRef } = useActionForm(disconnectThreadsAction);
  return (
    <form ref={formRef} method="post" onSubmit={onSubmit}>
      <SubmitButton pending={pending} size="sm" variant="ghost" pendingText="해제 중…">연결 해제</SubmitButton>
      <FormMessage state={state} />
    </form>
  );
}
