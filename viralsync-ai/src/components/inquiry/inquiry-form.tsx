"use client";
import { useActionForm } from "@/components/ui/use-action-form";
import { createInquiryAction } from "@/app/actions/inquiries";
import { INQUIRY_SOURCE_LABEL } from "@/lib/labels";
import { Field } from "@/components/ui/misc";
import { FormMessage } from "@/components/ui/form-status";
import { SubmitButton } from "@/components/ui/submit-button";

export function InquiryForm() {
  const { state, pending, onSubmit, formRef } = useActionForm(createInquiryAction);
  const e = state.errors ?? {};
  return (
    <form ref={formRef} method="post" onSubmit={onSubmit} className="space-y-4" noValidate>
      <FormMessage state={state} />
      <div className="grid gap-4 sm:grid-cols-3">
        <Field label="유입 경로" htmlFor="i-source" error={e.source}>
          <select id="i-source" name="source" defaultValue="KMONG" className="input">
            {Object.entries(INQUIRY_SOURCE_LABEL).map(([k, v]) => (
              <option key={k} value={k}>{v}</option>
            ))}
          </select>
        </Field>
        <Field label="고객 이름·닉네임" htmlFor="i-name" error={e.customerName} required>
          <input id="i-name" name="customerName" className="input" placeholder="크몽 닉네임 등" />
        </Field>
        <Field label="연락처 (선택)" htmlFor="i-contact" error={e.contactInfo} hint="플랫폼 정책상 외부 연락처 교환이 제한될 수 있습니다.">
          <input id="i-contact" name="contactInfo" className="input" />
        </Field>
      </div>
      <Field label="문의 원문" htmlFor="i-raw" error={e.rawText} required hint="고객이 보낸 메시지를 그대로 붙여넣으세요. 링크는 접속하지 않고 형식만 확인합니다.">
        <textarea id="i-raw" name="rawText" rows={10} className="input font-mono text-sm" placeholder={"예) 안녕하세요. 'OO샤브' 브랜드의 광고대행에 대해 문의드립니다.\n▶홈페이지 : https://...\n▶인스타그램 : https://instagram.com/...\n예산은 얼마정도로 잡아야 할지, 광고의 종류는 어떤 것들을 추천하는지 확인 부탁드립니다."} />
      </Field>
      <div className="flex justify-end">
        <SubmitButton pending={pending} pendingText="분석 중…">접수하고 자동 분석</SubmitButton>
      </div>
    </form>
  );
}
