"use client";
import { useActionForm } from "@/components/ui/use-action-form";
import { savePolicy } from "@/app/actions/policies";
import { PLATFORM_LABEL, PLATFORMS, POLICY_STATUS_LABEL, RISK_LABEL } from "@/lib/labels";
import { Field } from "@/components/ui/misc";
import { FormMessage } from "@/components/ui/form-status";
import { SubmitButton } from "@/components/ui/submit-button";

export interface PolicyFormValues {
  id?: string;
  platform?: string;
  policyUrl?: string;
  status?: string;
  lastReviewedAt?: string;
  nextReviewAt?: string;
  changeSummary?: string;
  affectedFeatures?: string[];
  riskLevel?: string;
  ownerId?: string | null;
  actionItems?: string;
  result?: string;
}

export function PolicyForm({ values = {}, users, readOnly }: { values?: PolicyFormValues; users: { id: string; name: string }[]; readOnly?: boolean }) {
  const { state, pending, onSubmit, formRef } = useActionForm(savePolicy);
  const e = state.errors ?? {};
  return (
    <form ref={formRef} method="post" onSubmit={onSubmit} className="space-y-4" noValidate>
      {values.id && <input type="hidden" name="id" value={values.id} />}
      <FormMessage state={state} />
      <fieldset disabled={readOnly} className="grid gap-4 sm:grid-cols-2">
        <Field label="플랫폼" htmlFor="p-platform" error={e.platform} required>
          <select id="p-platform" name="platform" defaultValue={values.platform ?? "INSTAGRAM"} className="input">
            {PLATFORMS.map((p) => (
              <option key={p} value={p}>{PLATFORM_LABEL[p]}</option>
            ))}
          </select>
        </Field>
        <Field label="공식 정책 URL" htmlFor="p-url" error={e.policyUrl} required>
          <input id="p-url" name="policyUrl" type="url" defaultValue={values.policyUrl} className="input" />
        </Field>
        <Field label="검토 상태" htmlFor="p-status" error={e.status} hint="공식 문서를 확인하지 못했다면 ‘검토 미완료’로 두세요.">
          <select id="p-status" name="status" defaultValue={values.status ?? "NOT_REVIEWED"} className="input">
            {Object.entries(POLICY_STATUS_LABEL).map(([k, v]) => (
              <option key={k} value={k}>{v}</option>
            ))}
          </select>
        </Field>
        <Field label="위험 수준" htmlFor="p-risk" error={e.riskLevel}>
          <select id="p-risk" name="riskLevel" defaultValue={values.riskLevel ?? "LOW"} className="input">
            {Object.entries(RISK_LABEL).map(([k, v]) => (
              <option key={k} value={k}>{v}</option>
            ))}
          </select>
        </Field>
        <Field label="마지막 검토일" htmlFor="p-last" error={e.lastReviewedAt}>
          <input id="p-last" name="lastReviewedAt" type="date" defaultValue={values.lastReviewedAt} className="input" />
        </Field>
        <Field label="다음 검토 예정일" htmlFor="p-next" error={e.nextReviewAt} required>
          <input id="p-next" name="nextReviewAt" type="date" defaultValue={values.nextReviewAt} className="input" />
        </Field>
        <Field label="담당자" htmlFor="p-owner" error={e.ownerId}>
          <select id="p-owner" name="ownerId" defaultValue={values.ownerId ?? ""} className="input">
            <option value="">미지정</option>
            {users.map((u) => (
              <option key={u.id} value={u.id}>{u.name}</option>
            ))}
          </select>
        </Field>
        <Field label="영향받는 기능" htmlFor="p-features" hint="쉼표로 구분">
          <input id="p-features" name="affectedFeatures" defaultValue={values.affectedFeatures?.join(", ")} className="input" />
        </Field>
        <Field label="정책 변경 내용" htmlFor="p-change" error={e.changeSummary}>
          <textarea id="p-change" name="changeSummary" rows={3} defaultValue={values.changeSummary} className="input" />
        </Field>
        <Field label="개선 조치" htmlFor="p-action" error={e.actionItems}>
          <textarea id="p-action" name="actionItems" rows={3} defaultValue={values.actionItems} className="input" />
        </Field>
        <div className="sm:col-span-2">
          <Field label="검토 결과" htmlFor="p-result" error={e.result} hint="‘검토 완료’ 저장 시 필수 — 공식 문서에서 확인한 내용을 기록하세요.">
            <textarea id="p-result" name="result" rows={3} defaultValue={values.result} className="input" />
          </Field>
        </div>
      </fieldset>
      {!readOnly && (
        <div className="flex justify-end">
          <SubmitButton pending={pending} pendingText="저장 중…">{values.id ? "검토 내용 저장" : "정책 검토 등록"}</SubmitButton>
        </div>
      )}
    </form>
  );
}
