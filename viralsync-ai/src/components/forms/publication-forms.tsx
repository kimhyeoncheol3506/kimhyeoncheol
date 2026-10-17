"use client";
import { useActionForm } from "@/components/ui/use-action-form";
import { executeAction, scheduleAction } from "@/app/actions/publications";
import { PLATFORM_LABEL } from "@/lib/labels";
import { FormMessage } from "@/components/ui/form-status";
import { SubmitButton } from "@/components/ui/submit-button";

export function ScheduleForm({ contentId, platforms, defaultPlatform, disabled }: { contentId: string; platforms: string[]; defaultPlatform: string; disabled?: boolean }) {
  const { state, pending, onSubmit, formRef } = useActionForm(scheduleAction);
  return (
    <form ref={formRef} method="post" onSubmit={onSubmit} className="space-y-2">
      <input type="hidden" name="contentId" value={contentId} />
      <div className="flex flex-wrap items-center gap-2">
        <label htmlFor={`pf-${contentId}`} className="text-xs text-slate-600">플랫폼</label>
        <select id={`pf-${contentId}`} name="platform" defaultValue={defaultPlatform} className="input w-auto py-1 text-sm">
          {platforms.map((p) => (
            <option key={p} value={p}>{PLATFORM_LABEL[p as keyof typeof PLATFORM_LABEL]}</option>
          ))}
        </select>
        <SubmitButton pending={pending} size="sm" disabled={disabled} pendingText="등록 중…">실행 대기 등록</SubmitButton>
      </div>
      <FormMessage state={state} />
    </form>
  );
}

export function ExecuteForm({ id, retry, liveAvailable, liveReason }: { id: string; retry: boolean; liveAvailable: boolean; liveReason: string }) {
  const { pending, onSubmit, formRef } = useActionForm(executeAction, { errorToast: true });
  return (
    <form ref={formRef} method="post" onSubmit={onSubmit} className="space-y-1.5">
      <input type="hidden" name="id" value={id} />
      <div className="flex flex-wrap gap-1.5">
        <SubmitButton pending={pending} size="sm" name="mode" value="SIMULATED" pendingText="실행 중…">{retry ? "모의 재시도" : "모의 실행"}</SubmitButton>
        {liveAvailable && (
          <SubmitButton pending={pending} size="sm" variant="danger" name="mode" value="LIVE" pendingText="게시 중…">실제 게시</SubmitButton>
        )}
      </div>
      {!liveAvailable && <p className="text-[11px] text-slate-400">실제 게시 불가: {liveReason}</p>}
    </form>
  );
}
