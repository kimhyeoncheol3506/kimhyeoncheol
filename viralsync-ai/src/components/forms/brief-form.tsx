"use client";
import { useActionForm } from "@/components/ui/use-action-form";
import { useState } from "react";
import { saveCampaign } from "@/app/actions/campaigns";
import { checkUrl } from "@/lib/validation/url";
import { GOAL_LABEL, PLATFORM_LABEL, PLATFORMS, TARGET_TYPE_LABEL } from "@/lib/labels";
import { Field } from "@/components/ui/misc";
import { FormMessage } from "@/components/ui/form-status";
import { SubmitButton } from "@/components/ui/submit-button";

export interface BriefFormValues {
  id?: string;
  clientId?: string;
  title?: string;
  targetUrl?: string | null;
  targetType?: string;
  goal?: string;
  coreTarget?: string;
  budget?: number;
  startDate?: string;
  endDate?: string;
  desiredPlatforms?: string[];
  keywords?: string[];
  bannedKeywords?: string[];
  description?: string;
}

export function BriefForm({ values = {}, clients }: { values?: BriefFormValues; clients: { id: string; name: string }[] }) {
  const { state, pending, onSubmit, formRef } = useActionForm(saveCampaign);
  const [url, setUrl] = useState(values.targetUrl ?? "");
  const e = state.errors ?? {};
  const urlResult = url.trim() ? checkUrl(url) : null;
  return (
    <form ref={formRef} method="post" onSubmit={onSubmit} className="space-y-6" noValidate>
      {values.id && <input type="hidden" name="id" value={values.id} />}
      <FormMessage state={state} />
      <div className="grid gap-4 sm:grid-cols-2">
        <Field label="고객" htmlFor="clientId" error={e.clientId} required>
          <select id="clientId" name="clientId" defaultValue={values.clientId ?? ""} className="input" required>
            <option value="">고객 선택</option>
            {clients.map((c) => (
              <option key={c.id} value={c.id}>{c.name}</option>
            ))}
          </select>
        </Field>
        <Field label="의뢰 제목" htmlFor="title" error={e.title} required>
          <input id="title" name="title" defaultValue={values.title} className="input" required />
        </Field>
        <div className="sm:col-span-2">
          <Field label="홍보 대상 URL" htmlFor="targetUrl" error={e.targetUrl}>
            <input
              id="targetUrl"
              name="targetUrl"
              type="url"
              value={url}
              onChange={(ev) => setUrl(ev.target.value)}
              placeholder="https://"
              className="input"
              aria-describedby="url-check"
            />
          </Field>
          <div id="url-check" aria-live="polite" className="mt-1 text-xs">
            {urlResult &&
              (urlResult.valid ? (
                <p className="text-emerald-700">
                  ✓ URL 형식 확인됨{urlResult.platformHint ? ` (${urlResult.platformHint})` : ""}. 외부 페이지 내용은 자동 분석하지 않으니 아래 상세 설명에 홍보 내용을 직접 입력해 주세요.
                </p>
              ) : (
                <p className="text-rose-600">✕ {urlResult.reason}</p>
              ))}
          </div>
        </div>
        <Field label="홍보 대상 유형" htmlFor="targetType" error={e.targetType} required>
          <select id="targetType" name="targetType" defaultValue={values.targetType ?? ""} className="input" required>
            <option value="">선택</option>
            {Object.entries(TARGET_TYPE_LABEL).map(([k, v]) => (
              <option key={k} value={k}>{v}</option>
            ))}
          </select>
        </Field>
        <Field label="주요 목표" htmlFor="goal" error={e.goal} required>
          <select id="goal" name="goal" defaultValue={values.goal ?? ""} className="input" required>
            <option value="">선택</option>
            {Object.entries(GOAL_LABEL).map(([k, v]) => (
              <option key={k} value={k}>{v}</option>
            ))}
          </select>
        </Field>
        <Field label="핵심 타깃" htmlFor="coreTarget" error={e.coreTarget}>
          <input id="coreTarget" name="coreTarget" defaultValue={values.coreTarget} className="input" placeholder="예: 운동을 시작하려는 30대 직장인" />
        </Field>
        <Field label="예산 (원)" htmlFor="budget" error={e.budget}>
          <input id="budget" name="budget" type="number" min={0} step={10000} defaultValue={values.budget ?? 0} className="input" />
        </Field>
        <Field label="캠페인 시작일" htmlFor="startDate" error={e.startDate}>
          <input id="startDate" name="startDate" type="date" defaultValue={values.startDate} className="input" />
        </Field>
        <Field label="캠페인 종료일" htmlFor="endDate" error={e.endDate}>
          <input id="endDate" name="endDate" type="date" defaultValue={values.endDate} className="input" />
        </Field>
      </div>
      <fieldset>
        <legend className="label">
          희망 SNS <span className="text-rose-500">*</span>
        </legend>
        <div className="flex flex-wrap gap-2">
          {PLATFORMS.map((p) => (
            <label key={p} className="flex cursor-pointer items-center gap-1.5 rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm has-[:checked]:border-brand-500 has-[:checked]:bg-brand-50">
              <input type="checkbox" name="desiredPlatforms" value={p} defaultChecked={values.desiredPlatforms?.includes(p)} className="accent-brand-600" />
              {PLATFORM_LABEL[p]}
            </label>
          ))}
        </div>
        {e.desiredPlatforms && <p className="mt-1 text-xs font-medium text-rose-600">{e.desiredPlatforms}</p>}
      </fieldset>
      <div className="grid gap-4 sm:grid-cols-2">
        <Field label="주요 키워드" htmlFor="keywords" hint="쉼표로 구분">
          <input id="keywords" name="keywords" defaultValue={values.keywords?.join(", ")} className="input" placeholder="예: 홈트, 운동, 다이어트" />
        </Field>
        <Field label="금지 키워드" htmlFor="bannedKeywords" hint="쉼표로 구분">
          <input id="bannedKeywords" name="bannedKeywords" defaultValue={values.bannedKeywords?.join(", ")} className="input" />
        </Field>
      </div>
      <Field label="의뢰 상세 설명" htmlFor="description" error={e.description} hint="URL 을 자동 분석하지 않으므로 홍보 대상의 내용·특징을 직접 입력해 주세요. 분석 정확도가 높아집니다.">
        <textarea id="description" name="description" rows={5} defaultValue={values.description} className="input" />
      </Field>
      <div className="flex justify-end">
        <SubmitButton pending={pending} pendingText="저장 중…">{values.id ? "의뢰 내용 저장" : "의뢰 접수"}</SubmitButton>
      </div>
    </form>
  );
}
