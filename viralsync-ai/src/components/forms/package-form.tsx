"use client";
import { useActionForm } from "@/components/ui/use-action-form";
import { savePackageAction } from "@/app/actions/packages";
import { CHANNEL_LABEL, SERVICE_CHANNELS } from "@/lib/inquiry/planner";
import { Field } from "@/components/ui/misc";
import { FormMessage } from "@/components/ui/form-status";
import { SubmitButton } from "@/components/ui/submit-button";

export interface PackageValues {
  id?: string;
  name?: string;
  channel?: string;
  description?: string;
  unitPrice?: number;
  unit?: string;
  deliverables?: string[];
  leadTimeDays?: number;
  mediaSpendSeparate?: boolean;
  active?: boolean;
}

export function PackageForm({ values = {} }: { values?: PackageValues }) {
  const { state, pending, onSubmit, formRef } = useActionForm(savePackageAction, { resetOnSuccess: !values.id });
  const e = state.errors ?? {};
  const k = values.id ?? "new";
  return (
    <form ref={formRef} method="post" onSubmit={onSubmit} className="grid gap-3 sm:grid-cols-6" noValidate>
      {values.id && <input type="hidden" name="id" value={values.id} />}
      <div className="sm:col-span-6"><FormMessage state={state} /></div>
      <div className="sm:col-span-2">
        <Field label="상품명" htmlFor={`pk-name-${k}`} error={e.name} required>
          <input id={`pk-name-${k}`} name="name" defaultValue={values.name} className="input" />
        </Field>
      </div>
      <Field label="매체" htmlFor={`pk-ch-${k}`} error={e.channel}>
        <select id={`pk-ch-${k}`} name="channel" defaultValue={values.channel ?? "BLOG"} className="input">
          {SERVICE_CHANNELS.map((c) => (
            <option key={c} value={c}>{CHANNEL_LABEL[c]}</option>
          ))}
        </select>
      </Field>
      <Field label="단가 (원)" htmlFor={`pk-price-${k}`} error={e.unitPrice}>
        <input id={`pk-price-${k}`} name="unitPrice" type="number" min={0} step={1000} defaultValue={values.unitPrice ?? 0} className="input" />
      </Field>
      <Field label="단위" htmlFor={`pk-unit-${k}`} error={e.unit}>
        <input id={`pk-unit-${k}`} name="unit" defaultValue={values.unit ?? "월"} className="input" />
      </Field>
      <Field label="소요일" htmlFor={`pk-lead-${k}`} error={e.leadTimeDays}>
        <input id={`pk-lead-${k}`} name="leadTimeDays" type="number" min={0} defaultValue={values.leadTimeDays ?? 7} className="input" />
      </Field>
      <div className="sm:col-span-3">
        <Field label="설명" htmlFor={`pk-desc-${k}`}>
          <input id={`pk-desc-${k}`} name="description" defaultValue={values.description} className="input" />
        </Field>
      </div>
      <div className="sm:col-span-3">
        <Field label="제공 내역" htmlFor={`pk-del-${k}`} hint="쉼표로 구분">
          <input id={`pk-del-${k}`} name="deliverables" defaultValue={values.deliverables?.join(", ")} className="input" />
        </Field>
      </div>
      <div className="flex flex-wrap items-center gap-4 sm:col-span-6">
        <label className="flex items-center gap-1.5 text-sm">
          <input type="checkbox" name="mediaSpendSeparate" defaultChecked={values.mediaSpendSeparate} /> 광고 매체비 별도
        </label>
        {values.id && (
          <label className="flex items-center gap-1.5 text-sm">
            <input type="checkbox" name="active" defaultChecked={values.active} /> 판매 중
          </label>
        )}
        <SubmitButton pending={pending} size="sm" pendingText="저장 중…">{values.id ? "수정 저장" : "상품 등록"}</SubmitButton>
      </div>
    </form>
  );
}
