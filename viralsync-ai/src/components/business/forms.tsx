"use client";
import { useActionForm } from "@/components/ui/use-action-form";
import { deleteFixedCostAction, saveFixedCostAction, saveProfileAction, toggleRoadmapAction } from "@/app/actions/business";
import { FormMessage } from "@/components/ui/form-status";
import { SubmitButton } from "@/components/ui/submit-button";
import { DEFAULT_POSITIONING, TARGET_INDUSTRIES } from "@/lib/business/playbook";

export const COST_CATEGORIES = ["도구·구독", "보험·세금", "통신", "기타"];

export function ProfileForm({ v, canEdit }: { v: { positioning: string; targetIndustry: string; businessStartDate: string; cashReserveKrw: number | null }; canEdit: boolean }) {
  const { state, pending, onSubmit, formRef } = useActionForm(saveProfileAction);
  return (
    <form ref={formRef} method="post" onSubmit={onSubmit} className="grid gap-3 sm:grid-cols-2" noValidate aria-label="사업 기본값">
      <div className="sm:col-span-2">
        <label htmlFor="positioning" className="label">포지셔닝 한 문장 (DM·제안서 첫 문장)</label>
        <input id="positioning" name="positioning" defaultValue={v.positioning} placeholder={DEFAULT_POSITIONING} className="input" disabled={!canEdit} />
      </div>
      <div>
        <label htmlFor="targetIndustry" className="label">집중 업종 (1개)</label>
        <input id="targetIndustry" name="targetIndustry" list="biz-industries" defaultValue={v.targetIndustry} className="input" disabled={!canEdit} />
        <datalist id="biz-industries">{TARGET_INDUSTRIES.map((i) => <option key={i} value={i} />)}</datalist>
      </div>
      <div>
        <label htmlFor="businessStartDate" className="label">실행표 시작일 (1주차)</label>
        <input id="businessStartDate" name="businessStartDate" type="date" defaultValue={v.businessStartDate} className="input" disabled={!canEdit} />
      </div>
      <div>
        <label htmlFor="cashReserveKrw" className="label">사업 통장 잔고 (원, 비상금 계산용)</label>
        <input id="cashReserveKrw" name="cashReserveKrw" inputMode="numeric" defaultValue={v.cashReserveKrw ?? ""} className="input" disabled={!canEdit} />
      </div>
      {canEdit && <div className="flex items-end"><SubmitButton pending={pending} pendingText="저장 중…">저장</SubmitButton></div>}
      <div className="sm:col-span-2"><FormMessage state={state} /></div>
    </form>
  );
}

export function FixedCostForm({ v }: { v?: { id: string; name: string; category: string; monthlyKrw: number; active: boolean } }) {
  const { state, pending, onSubmit, formRef } = useActionForm(saveFixedCostAction, { resetOnSuccess: !v });
  const k = v?.id ?? "new";
  return (
    <form ref={formRef} method="post" onSubmit={onSubmit} className="flex flex-wrap items-end gap-2" noValidate aria-label={v ? `${v.name} 수정` : "고정비 추가"}>
      {v && <input type="hidden" name="id" value={v.id} />}
      <div>
        <label htmlFor={`fc-n-${k}`} className="sr-only">항목</label>
        <input id={`fc-n-${k}`} name="name" defaultValue={v?.name} placeholder="항목 (예: AI 구독)" className="input w-40 py-1.5 text-sm" />
      </div>
      <div>
        <label htmlFor={`fc-c-${k}`} className="sr-only">분류</label>
        <select id={`fc-c-${k}`} name="category" defaultValue={v?.category ?? "도구·구독"} className="input w-auto py-1.5 text-sm">{COST_CATEGORIES.map((c) => <option key={c}>{c}</option>)}</select>
      </div>
      <div>
        <label htmlFor={`fc-m-${k}`} className="sr-only">월 금액</label>
        <input id={`fc-m-${k}`} name="monthlyKrw" inputMode="numeric" defaultValue={v?.monthlyKrw} placeholder="월 금액" className="input w-28 py-1.5 text-sm" />
      </div>
      {v && (
        <select name="active" defaultValue={v.active ? "on" : "off"} className="input w-auto py-1.5 text-sm" aria-label="사용 여부">
          <option value="on">사용</option>
          <option value="off">중지</option>
        </select>
      )}
      <SubmitButton pending={pending} size="sm" variant={v ? "secondary" : "primary"} pendingText="…">{v ? "저장" : "추가"}</SubmitButton>
      <FormMessage state={state} />
    </form>
  );
}

export function DeleteFixedCost({ id }: { id: string }) {
  const { pending, onSubmit, formRef } = useActionForm(deleteFixedCostAction, { errorToast: true });
  return (
    <form ref={formRef} method="post" onSubmit={onSubmit}>
      <input type="hidden" name="id" value={id} />
      <SubmitButton pending={pending} size="sm" variant="ghost" pendingText="…">삭제</SubmitButton>
    </form>
  );
}

export function RoadmapToggle({ itemKey, done, label }: { itemKey: string; done: boolean; label: string }) {
  const { pending, onSubmit, formRef } = useActionForm(toggleRoadmapAction, { errorToast: true });
  return (
    <form ref={formRef} method="post" onSubmit={onSubmit}>
      <input type="hidden" name="key" value={itemKey} />
      <input type="hidden" name="done" value={done ? "0" : "1"} />
      <button type="submit" disabled={pending} aria-pressed={done} aria-label={`${label} ${done ? "완료 취소" : "완료"}`} className={`flex h-5 w-5 shrink-0 items-center justify-center rounded border text-xs ${done ? "border-emerald-500 bg-emerald-500 text-white" : "border-slate-300 bg-white"}`}>
        {done ? "✓" : ""}
      </button>
    </form>
  );
}
