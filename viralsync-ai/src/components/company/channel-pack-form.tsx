"use client";
import { useActionForm } from "@/components/ui/use-action-form";
import { channelPackAction } from "@/app/actions/company";
import { FormMessage } from "@/components/ui/form-status";
import { SubmitButton } from "@/components/ui/submit-button";

export function ChannelPackForm({ campaignId, channels }: { campaignId: string; channels: { key: string; label: string; types: string; checked: boolean }[] }) {
  const { state, pending, onSubmit, formRef } = useActionForm(channelPackAction);
  return (
    <form ref={formRef} method="post" onSubmit={onSubmit} className="space-y-3" aria-label="AI 팀에 맡기기">
      <input type="hidden" name="campaignId" value={campaignId} />
      <fieldset>
        <legend className="mb-2 text-sm font-medium text-slate-700">홍보할 매체</legend>
        <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-5">
          {channels.map((c) => (
            <label key={c.key} className="flex cursor-pointer items-start gap-2 rounded-lg border border-slate-200 p-2 text-sm has-[:checked]:border-brand-400 has-[:checked]:bg-brand-50">
              <input type="checkbox" name="platforms" value={c.key} defaultChecked={c.checked} className="mt-1" />
              <span>
                <span className="font-medium">{c.label}</span>
                <span className="block text-[11px] text-slate-500">{c.types}</span>
              </span>
            </label>
          ))}
        </div>
      </fieldset>
      <div className="flex flex-wrap items-center gap-3">
        <SubmitButton pending={pending} pendingText="AI 팀 작업 중…">AI 팀에 맡기기</SubmitButton>
        <p className="text-xs text-slate-500">초안 작성 → AI 1차 검토 → 결재 요청까지 합니다. 게시는 결재 후 실행 관리에서.</p>
      </div>
      <FormMessage state={state} />
    </form>
  );
}
