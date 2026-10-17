"use client";
import { useActionForm } from "@/components/ui/use-action-form";
import { analyzeCampaign } from "@/app/actions/analysis";
import { FormMessage } from "@/components/ui/form-status";
import { SubmitButton } from "@/components/ui/submit-button";

export function AnalyzeButton({ id, analyzed }: { id: string; analyzed: boolean }) {
  const { state, pending, onSubmit, formRef } = useActionForm(analyzeCampaign);
  return (
    <form ref={formRef} method="post" onSubmit={onSubmit} className="space-y-2">
      <input type="hidden" name="id" value={id} />
      <SubmitButton pending={pending} size="sm" pendingText="분석 중…">{analyzed ? "다시 분석" : "AI 분석 실행"}</SubmitButton>
      <FormMessage state={state} />
    </form>
  );
}
