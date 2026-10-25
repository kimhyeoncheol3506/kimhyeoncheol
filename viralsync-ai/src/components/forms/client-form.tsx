"use client";
import { useActionForm } from "@/components/ui/use-action-form";
import { saveClient } from "@/app/actions/clients";
import { Field } from "@/components/ui/misc";
import { FormMessage } from "@/components/ui/form-status";
import { SubmitButton } from "@/components/ui/submit-button";

export interface ClientFormValues {
  id?: string;
  name?: string;
  contactName?: string;
  contactEmail?: string | null;
  contactPhone?: string | null;
  promoUrl?: string | null;
  budget?: number;
  contractStart?: string;
  contractEnd?: string;
  managerId?: string | null;
  teamId?: string | null;
  companyIntro?: string;
  productDescription?: string;
  coreTarget?: string;
  bannedPhrases?: string[];
  requiredPhrases?: string[];
  toneOfVoice?: string;
}

export function ClientForm({ values = {}, managers, teams = [] }: { values?: ClientFormValues; managers: { id: string; name: string }[]; teams?: { id: string; name: string }[] }) {
  const { state, pending, onSubmit, formRef } = useActionForm(saveClient);
  const e = state.errors ?? {};
  const aria = (k: string) => (e[k] ? { "aria-invalid": true, "aria-describedby": `${k}-error` } : {});
  return (
    <form ref={formRef} method="post" onSubmit={onSubmit} className="space-y-6" noValidate>
      {values.id && <input type="hidden" name="id" value={values.id} />}
      <FormMessage state={state} />
      <fieldset className="grid gap-4 sm:grid-cols-2">
        <legend className="mb-2 text-sm font-semibold text-slate-900">기본 정보</legend>
        <Field label="고객명" htmlFor="name" error={e.name} required>
          <input id="name" name="name" defaultValue={values.name} className="input" required {...aria("name")} />
        </Field>
        <Field label="고객사 담당자" htmlFor="contactName" error={e.contactName} required>
          <input id="contactName" name="contactName" defaultValue={values.contactName} className="input" required {...aria("contactName")} />
        </Field>
        <Field label="담당자 이메일" htmlFor="contactEmail" error={e.contactEmail}>
          <input id="contactEmail" name="contactEmail" type="email" defaultValue={values.contactEmail ?? ""} className="input" {...aria("contactEmail")} />
        </Field>
        <Field label="담당자 연락처" htmlFor="contactPhone" error={e.contactPhone}>
          <input id="contactPhone" name="contactPhone" defaultValue={values.contactPhone ?? ""} className="input" />
        </Field>
        <Field label="홍보 대상 URL" htmlFor="promoUrl" error={e.promoUrl} hint="URL 형식만 검사하며 외부 페이지는 자동 분석하지 않습니다.">
          <input id="promoUrl" name="promoUrl" type="url" defaultValue={values.promoUrl ?? ""} placeholder="https://" className="input" {...aria("promoUrl")} />
        </Field>
        <Field label="담당 직원" htmlFor="managerId" error={e.managerId}>
          <select id="managerId" name="managerId" defaultValue={values.managerId ?? ""} className="input">
            <option value="">선택 안 함</option>
            {managers.map((m) => (
              <option key={m.id} value={m.id}>{m.name}</option>
            ))}
          </select>
        </Field>
        <Field label="담당 팀" htmlFor="teamId" error={e.teamId} hint="팀에 배정하면 팀원·팀장이 이 고객을 담당합니다.">
          <select id="teamId" name="teamId" defaultValue={values.teamId ?? ""} className="input">
            <option value="">팀 없음</option>
            {teams.map((t) => (
              <option key={t.id} value={t.id}>{t.name}</option>
            ))}
          </select>
        </Field>
        <Field label="캠페인 예산 (원)" htmlFor="budget" error={e.budget}>
          <input id="budget" name="budget" type="number" min={0} step={10000} defaultValue={values.budget ?? 0} className="input" {...aria("budget")} />
        </Field>
        <div className="grid grid-cols-2 gap-3">
          <Field label="계약 시작일" htmlFor="contractStart" error={e.contractStart}>
            <input id="contractStart" name="contractStart" type="date" defaultValue={values.contractStart} className="input" />
          </Field>
          <Field label="계약 종료일" htmlFor="contractEnd" error={e.contractEnd}>
            <input id="contractEnd" name="contractEnd" type="date" defaultValue={values.contractEnd} className="input" {...aria("contractEnd")} />
          </Field>
        </div>
      </fieldset>
      <fieldset className="grid gap-4 sm:grid-cols-2">
        <legend className="mb-2 text-sm font-semibold text-slate-900">브랜드 프로필</legend>
        <Field label="회사 및 브랜드 소개" htmlFor="companyIntro" error={e.companyIntro}>
          <textarea id="companyIntro" name="companyIntro" rows={3} defaultValue={values.companyIntro} className="input" />
        </Field>
        <Field label="상품 또는 서비스 설명" htmlFor="productDescription" error={e.productDescription} hint="AI 문구는 이 설명 범위 안에서만 작성됩니다.">
          <textarea id="productDescription" name="productDescription" rows={3} defaultValue={values.productDescription} className="input" />
        </Field>
        <Field label="핵심 타깃" htmlFor="coreTarget" error={e.coreTarget}>
          <input id="coreTarget" name="coreTarget" defaultValue={values.coreTarget} className="input" placeholder="예: 홈카페를 즐기는 20~40대 직장인" />
        </Field>
        <Field label="브랜드 문체" htmlFor="toneOfVoice" error={e.toneOfVoice}>
          <input id="toneOfVoice" name="toneOfVoice" defaultValue={values.toneOfVoice} className="input" placeholder="예: 따뜻하고 차분한 말투" />
        </Field>
        <Field label="금지 표현" htmlFor="bannedPhrases" hint="쉼표 또는 줄바꿈으로 구분">
          <textarea id="bannedPhrases" name="bannedPhrases" rows={2} defaultValue={values.bannedPhrases?.join(", ")} className="input" />
        </Field>
        <Field label="필수 표현" htmlFor="requiredPhrases" hint="쉼표 또는 줄바꿈으로 구분 (예: #브랜드명)">
          <textarea id="requiredPhrases" name="requiredPhrases" rows={2} defaultValue={values.requiredPhrases?.join(", ")} className="input" />
        </Field>
      </fieldset>
      <div className="flex justify-end">
        <SubmitButton pending={pending} pendingText="저장 중…">{values.id ? "변경사항 저장" : "고객 등록"}</SubmitButton>
      </div>
    </form>
  );
}
