"use client";
import { useActionForm } from "@/components/ui/use-action-form";
import { overrideInquiryAction } from "@/app/actions/inquiries";
import { BUSINESS_TYPE_LABEL } from "@/lib/inquiry/parser";
import { CHANNEL_LABEL, SERVICE_CHANNELS } from "@/lib/inquiry/planner";
import { Field } from "@/components/ui/misc";
import { FormMessage } from "@/components/ui/form-status";
import { SubmitButton } from "@/components/ui/submit-button";

export function OverrideForm({
  id,
  values,
}: {
  id: string;
  values: { brand: string | null; businessType: string; keywords: string[]; requestedChannels: string[]; budget: number | null };
}) {
  const { state, pending, onSubmit, formRef } = useActionForm(overrideInquiryAction);
  const e = state.errors ?? {};
  return (
    <form ref={formRef} method="post" onSubmit={onSubmit} className="space-y-3" noValidate>
      <input type="hidden" name="id" value={id} />
      <FormMessage state={state} />
      <div className="grid gap-3 sm:grid-cols-2">
        <Field label="브랜드(상호)" htmlFor="o-brand" error={e.brand}>
          <input id="o-brand" name="brand" defaultValue={values.brand ?? ""} className="input" />
        </Field>
        <Field label="업종" htmlFor="o-type" error={e.businessType}>
          <select id="o-type" name="businessType" defaultValue={values.businessType} className="input">
            {Object.entries(BUSINESS_TYPE_LABEL).map(([k, v]) => (
              <option key={k} value={k}>{v}</option>
            ))}
          </select>
        </Field>
        <Field label="키워드" htmlFor="o-kw" hint="쉼표로 구분">
          <input id="o-kw" name="keywords" defaultValue={values.keywords.join(", ")} className="input" />
        </Field>
        <Field label="월 예산 (원, 선택)" htmlFor="o-budget" error={e.budget}>
          <input id="o-budget" name="budget" inputMode="numeric" defaultValue={values.budget ?? ""} className="input" placeholder="예: 1000000" />
        </Field>
      </div>
      <fieldset>
        <legend className="label">고객이 요청한 매체</legend>
        <div className="flex flex-wrap gap-2">
          {SERVICE_CHANNELS.filter((c) => c !== "PACKAGE").map((c) => (
            <label key={c} className="flex cursor-pointer items-center gap-1.5 rounded-lg border border-slate-300 bg-white px-2.5 py-1 text-xs has-[:checked]:border-brand-500 has-[:checked]:bg-brand-50">
              <input type="checkbox" name="requestedChannels" value={c} defaultChecked={values.requestedChannels.includes(c)} className="accent-brand-600" />
              {CHANNEL_LABEL[c]}
            </label>
          ))}
        </div>
      </fieldset>
      <SubmitButton pending={pending} size="sm" pendingText="재분석 중…">수정 내용으로 다시 견적</SubmitButton>
    </form>
  );
}
