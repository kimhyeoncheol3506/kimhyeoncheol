"use client";
import { useState } from "react";
import { useActionForm } from "@/components/ui/use-action-form";
import { createSubscriptionAction, subscriptionOpAction } from "@/app/actions/subscriptions";
import { FormMessage } from "@/components/ui/form-status";
import { SubmitButton } from "@/components/ui/submit-button";

interface Plan { name: string; monthlyFee: number; deliverables: string[] }

export function SubscriptionForm({ clients, plans, clientId, today }: { clients: { id: string; name: string }[]; plans: Plan[]; clientId?: string; today: string }) {
  const { state, pending, onSubmit, formRef } = useActionForm(createSubscriptionAction);
  const [plan, setPlan] = useState<Plan>(plans[1] ?? plans[0]);
  return (
    <form ref={formRef} method="post" onSubmit={onSubmit} className="grid gap-3 sm:grid-cols-2" noValidate aria-label="월 정액 계약">
      <div className="sm:col-span-2"><FormMessage state={state} /></div>
      <div>
        <label htmlFor="sub-client" className="label">고객 *</label>
        <select id="sub-client" name="clientId" defaultValue={clientId ?? ""} className="input">
          <option value="">고객 선택</option>
          {clients.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
        </select>
      </div>
      <div>
        <label htmlFor="sub-plan" className="label">패키지</label>
        <select id="sub-plan" className="input" value={plan.name} onChange={(e) => setPlan(plans.find((p) => p.name === e.target.value) ?? plan)}>
          {plans.map((p) => <option key={p.name} value={p.name}>{p.name} — {p.monthlyFee.toLocaleString("ko-KR")}원</option>)}
        </select>
      </div>
      <input type="hidden" name="planName" value={plan.name} />
      <div>
        <label htmlFor="sub-fee" className="label">월 금액 (원) — 깎지 말고 양을 조절하세요</label>
        <input id="sub-fee" name="monthlyFee" key={plan.name} defaultValue={plan.monthlyFee} inputMode="numeric" className="input" />
      </div>
      <div>
        <label htmlFor="sub-day" className="label">매월 결제일</label>
        <input id="sub-day" name="billingDay" type="number" min={1} max={28} defaultValue={25} className="input" />
      </div>
      <div className="sm:col-span-2">
        <label htmlFor="sub-del" className="label">납품 내역 (한 줄에 하나 — 계약서 별표 1)</label>
        <textarea id="sub-del" name="deliverables" key={`d-${plan.name}`} defaultValue={plan.deliverables.join("\n")} rows={4} className="input" />
      </div>
      <div>
        <label htmlFor="sub-start" className="label">시작일</label>
        <input id="sub-start" name="startDate" type="date" defaultValue={today} className="input" />
      </div>
      <div>
        <label htmlFor="sub-ref" className="label">소개해 준 고객 (소개 할인 5만 원)</label>
        <select id="sub-ref" name="referredById" className="input" defaultValue="">
          <option value="">없음</option>
          {clients.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
        </select>
      </div>
      <fieldset className="space-y-1.5 text-sm sm:col-span-2">
        <legend className="label">조건</legend>
        <label className="flex items-center gap-2"><input type="checkbox" name="trial" defaultChecked /> 2주 무료 체험으로 시작 (유료 전환 첫 달 50% 할인)</label>
        <label className="flex items-center gap-2"><input type="checkbox" name="portfolioConsent" defaultChecked /> 결과물을 포트폴리오로 사용 (저작권은 고객에게)</label>
        <label className="flex items-center gap-2"><input type="checkbox" name="caseStudyConsent" /> 성과(조회수 성장) 사례 공개 동의</label>
        <label className="flex items-center gap-2"><input type="checkbox" name="vatIncluded" /> 부가세 포함 금액 (끄면 부가세 별도)</label>
      </fieldset>
      <div className="sm:col-span-2">
        <label htmlFor="sub-notes" className="label">메모</label>
        <input id="sub-notes" name="notes" className="input" />
      </div>
      <div><SubmitButton pending={pending} pendingText="만드는 중…">계약 만들기</SubmitButton></div>
    </form>
  );
}

export function OpButton({ id, op, label, paymentId, variant = "secondary", withReason }: { id: string; op: "paid" | "end" | "pay" | "unpay"; label: string; paymentId?: string; variant?: "primary" | "secondary" | "danger"; withReason?: boolean }) {
  const { pending, onSubmit, formRef } = useActionForm(subscriptionOpAction, { errorToast: true });
  return (
    <form ref={formRef} method="post" onSubmit={onSubmit} className="flex flex-wrap items-center gap-2">
      <input type="hidden" name="id" value={id} />
      <input type="hidden" name="op" value={op} />
      {paymentId && <input type="hidden" name="paymentId" value={paymentId} />}
      {withReason && (
        <>
          <label htmlFor={`reason-${id}`} className="sr-only">종료 사유</label>
          <input id={`reason-${id}`} name="reason" placeholder="종료 사유" className="input w-48 py-1 text-sm" />
        </>
      )}
      <SubmitButton pending={pending} size="sm" variant={variant} pendingText="처리 중…">{label}</SubmitButton>
    </form>
  );
}
