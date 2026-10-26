"use client";
import type { ProspectStage } from "@prisma/client";
import { useActionForm } from "@/components/ui/use-action-form";
import { convertProspectAction, importProspectsAction, saveProspectAction, setStageAction } from "@/app/actions/sales";
import { FormMessage } from "@/components/ui/form-status";
import { SubmitButton } from "@/components/ui/submit-button";
import { PROSPECT_STAGE_LABEL } from "@/lib/labels";
import { TARGET_INDUSTRIES } from "@/lib/business/playbook";

export interface ProspectValues {
  id?: string;
  name?: string;
  industry?: string;
  region?: string;
  instagram?: string | null;
  followers?: number | null;
  lastPostAt?: string;
  postsPerMonth?: number | null;
  quality?: number | null;
  ownerName?: string | null;
  diagnosis?: string;
  notes?: string;
}

export function ProspectForm({ values = {}, defaultIndustry = "" }: { values?: ProspectValues; defaultIndustry?: string }) {
  const { state, pending, onSubmit, formRef } = useActionForm(saveProspectAction, { resetOnSuccess: !values.id });
  const k = values.id ?? "new";
  const f = (name: keyof ProspectValues, label: string, opts: { type?: string; placeholder?: string; list?: string } = {}) => (
    <div>
      <label htmlFor={`pr-${name}-${k}`} className="label">{label}</label>
      <input id={`pr-${name}-${k}`} name={name} type={opts.type ?? "text"} list={opts.list} defaultValue={(values[name] as string | number | null | undefined) ?? ""} placeholder={opts.placeholder} className="input" />
    </div>
  );
  return (
    <form ref={formRef} method="post" onSubmit={onSubmit} className="grid gap-3 sm:grid-cols-4" noValidate aria-label={values.id ? "가게 정보 수정" : "가게 추가"}>
      {values.id && <input type="hidden" name="id" value={values.id} />}
      {f("name", "가게 이름 *")}
      <div>
        <label htmlFor={`pr-industry-${k}`} className="label">업종</label>
        <input id={`pr-industry-${k}`} name="industry" list="industries" defaultValue={values.industry ?? defaultIndustry} className="input" />
        <datalist id="industries">{TARGET_INDUSTRIES.map((i) => <option key={i} value={i} />)}</datalist>
      </div>
      {f("region", "지역 (동네)", { placeholder: "예: 망원동" })}
      {f("instagram", "인스타 계정", { placeholder: "@가게계정" })}
      {f("followers", "팔로워", { type: "number" })}
      {f("lastPostAt", "마지막 게시일", { type: "date" })}
      {f("postsPerMonth", "월 게시 수", { type: "number" })}
      {f("quality", "게시물 품질 (1~5)", { type: "number" })}
      {f("ownerName", "사장님 성함 (후기 등에서 확인)")}
      <div className="sm:col-span-3">
        <label htmlFor={`pr-diagnosis-${k}`} className="label">진단 메모 (문제 3줄 — 제안서 1쪽에 들어감)</label>
        <textarea id={`pr-diagnosis-${k}`} name="diagnosis" defaultValue={values.diagnosis} rows={3} className="input" placeholder={"예: 3개월째 게시물 없음\n릴스 0개\n가격·위치 정보가 프로필에 없음"} />
      </div>
      <input type="hidden" name="notes" value={values.notes ?? ""} />
      <div className="flex items-end sm:col-span-4"><SubmitButton pending={pending} pendingText="저장 중…">{values.id ? "저장" : "리스트에 추가"}</SubmitButton></div>
      <div className="sm:col-span-4"><FormMessage state={state} /></div>
    </form>
  );
}

export function ImportForm() {
  const { state, pending, onSubmit, formRef } = useActionForm(importProspectsAction, { resetOnSuccess: true });
  return (
    <form ref={formRef} method="post" onSubmit={onSubmit} className="space-y-2" noValidate aria-label="일괄 붙여넣기">
      <label htmlFor="pr-import" className="label">스프레드시트에서 복사해 붙여넣기 (한 줄에 한 가게)</label>
      <textarea id="pr-import" name="text" rows={5} className="input font-mono text-xs" placeholder={"가게이름, 업종, 지역, 인스타, 팔로워, 마지막게시일(YYYY-MM-DD), 월게시수\n하늘 미용실, 미용실, 망원동, @haneul_hair, 820, 2026-07-02, 1"} />
      <SubmitButton pending={pending} size="sm" variant="secondary" pendingText="등록 중…">일괄 등록</SubmitButton>
      <FormMessage state={state} />
    </form>
  );
}

export function StageButtons({ id, current }: { id: string; current: ProspectStage }) {
  const { pending, onSubmit, formRef } = useActionForm(setStageAction, { errorToast: true });
  const next: ProspectStage[] = (["DM_SENT", "REPLIED", "MEETING", "TRIAL", "WON", "WAITLIST", "LOST"] as ProspectStage[]).filter((s) => s !== current);
  return (
    <form ref={formRef} method="post" onSubmit={onSubmit} className="flex flex-wrap gap-1" aria-label="단계 변경">
      <input type="hidden" name="id" value={id} />
      {next.map((s) => (
        <SubmitButton key={s} pending={pending} size="sm" variant={s === "DM_SENT" ? "primary" : "secondary"} name="stage" value={s} pendingText="…">
          {s === "DM_SENT" ? "DM 보냄 ✓" : PROSPECT_STAGE_LABEL[s]}
        </SubmitButton>
      ))}
    </form>
  );
}

export function ConvertButton({ id, label = "고객으로 등록 → 월 정액 계약" }: { id: string; label?: string }) {
  const { state, pending, onSubmit, formRef } = useActionForm(convertProspectAction);
  return (
    <form ref={formRef} method="post" onSubmit={onSubmit}>
      <input type="hidden" name="id" value={id} />
      <SubmitButton pending={pending} pendingText="등록 중…">{label}</SubmitButton>
      <FormMessage state={state} />
    </form>
  );
}
