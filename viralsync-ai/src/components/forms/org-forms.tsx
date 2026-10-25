"use client";
import type { ApprovalGate, RiskLevel, Role } from "@prisma/client";
import { useActionForm } from "@/components/ui/use-action-form";
import { deleteRuleAction, deleteTeamAction, saveRuleAction, saveTeamAction } from "@/app/actions/org";
import { APPROVAL_GATE_LABEL, RISK_LABEL, ROLE_LABEL } from "@/lib/labels";
import { FormMessage } from "@/components/ui/form-status";
import { SubmitButton } from "@/components/ui/submit-button";

export function TeamForm({ team, people }: { team?: { id: string; name: string; description: string; leadId: string | null }; people: { id: string; name: string; role: Role }[] }) {
  const { state, pending, onSubmit, formRef } = useActionForm(saveTeamAction, { resetOnSuccess: !team });
  const k = team?.id ?? "new";
  return (
    <form ref={formRef} method="post" onSubmit={onSubmit} className="grid gap-2 sm:grid-cols-[1fr_1fr_1.5fr_auto]" noValidate>
      {team && <input type="hidden" name="id" value={team.id} />}
      <label className="sr-only" htmlFor={`tn-${k}`}>팀 이름</label>
      <input id={`tn-${k}`} name="name" defaultValue={team?.name} placeholder="팀 이름" className="input" />
      <label className="sr-only" htmlFor={`tl-${k}`}>팀장</label>
      <select id={`tl-${k}`} name="leadId" defaultValue={team?.leadId ?? ""} className="input">
        <option value="">팀장 미지정</option>
        {people.map((p) => (
          <option key={p.id} value={p.id}>{p.name} ({ROLE_LABEL[p.role]})</option>
        ))}
      </select>
      <label className="sr-only" htmlFor={`td-${k}`}>설명</label>
      <input id={`td-${k}`} name="description" defaultValue={team?.description} placeholder="담당 업무" className="input" />
      <SubmitButton pending={pending} size="sm" pendingText="저장 중…">{team ? "저장" : "팀 만들기"}</SubmitButton>
      <div className="sm:col-span-4"><FormMessage state={state} /></div>
    </form>
  );
}

export function DeleteTeamButton({ id }: { id: string }) {
  const { pending, onSubmit, formRef } = useActionForm(deleteTeamAction);
  return (
    <form ref={formRef} method="post" onSubmit={onSubmit}>
      <input type="hidden" name="id" value={id} />
      <SubmitButton pending={pending} size="sm" variant="ghost" pendingText="…">팀 삭제</SubmitButton>
    </form>
  );
}

const STEP_ROLES: Role[] = ["REVIEWER", "CAMPAIGN_MANAGER", "ADMIN"];

export function RuleForm({ rule }: { rule?: { id: string; gate: ApprovalGate; name: string; minAmount: number | null; minRisk: RiskLevel | null; steps: Role[]; aiPrecheck: boolean; active: boolean } }) {
  const { state, pending, onSubmit, formRef } = useActionForm(saveRuleAction, { resetOnSuccess: !rule });
  const k = rule?.id ?? "new";
  return (
    <form ref={formRef} method="post" onSubmit={onSubmit} className="space-y-3" noValidate>
      {rule && <input type="hidden" name="id" value={rule.id} />}
      <div className="grid gap-3 sm:grid-cols-4">
        <div>
          <label className="label" htmlFor={`rg-${k}`}>업무</label>
          <select id={`rg-${k}`} name="gate" defaultValue={rule?.gate ?? "QUOTE"} className="input">
            {Object.entries(APPROVAL_GATE_LABEL).map(([g, l]) => <option key={g} value={g}>{l}</option>)}
          </select>
        </div>
        <div>
          <label className="label" htmlFor={`rn-${k}`}>규칙 이름</label>
          <input id={`rn-${k}`} name="name" defaultValue={rule?.name} className="input" placeholder="예: 300만원 이상 계약" />
        </div>
        <div>
          <label className="label" htmlFor={`ra-${k}`}>금액 조건 (원 이상)</label>
          <input id={`ra-${k}`} name="minAmount" inputMode="numeric" defaultValue={rule?.minAmount ?? ""} className="input" placeholder="비우면 금액 무관" />
        </div>
        <div>
          <label className="label" htmlFor={`rr-${k}`}>위험도 조건 (이상)</label>
          <select id={`rr-${k}`} name="minRisk" defaultValue={rule?.minRisk ?? ""} className="input">
            <option value="">위험도 무관</option>
            {Object.entries(RISK_LABEL).map(([r, l]) => <option key={r} value={r}>{l}</option>)}
          </select>
        </div>
      </div>
      <fieldset>
        <legend className="label">결재 라인 (순서대로, 비우면 결재 없음)</legend>
        <div className="flex flex-wrap items-center gap-2">
          {[0, 1, 2, 3].map((i) => (
            <span key={i} className="flex items-center gap-1">
              {i > 0 && <span className="text-slate-300">→</span>}
              <label className="sr-only" htmlFor={`rs-${k}-${i}`}>{i + 1}단계</label>
              <select id={`rs-${k}-${i}`} name="steps" defaultValue={rule?.steps[i] ?? ""} className="input w-auto py-1.5 text-sm">
                <option value="">{i + 1}단계 없음</option>
                {STEP_ROLES.map((r) => <option key={r} value={r}>{ROLE_LABEL[r]}</option>)}
              </select>
            </span>
          ))}
        </div>
      </fieldset>
      <div className="flex flex-wrap items-center gap-4 text-sm">
        <label className="flex items-center gap-1.5"><input type="checkbox" name="aiPrecheck" defaultChecked={rule?.aiPrecheck ?? true} /> AI 1차 검토 차단 시 승인 불가</label>
        {rule && <label className="flex items-center gap-1.5"><input type="checkbox" name="active" defaultChecked={rule.active} /> 사용</label>}
        <SubmitButton pending={pending} size="sm" pendingText="저장 중…">{rule ? "규칙 저장" : "규칙 추가"}</SubmitButton>
      </div>
      <FormMessage state={state} />
    </form>
  );
}

export function DeleteRuleButton({ id }: { id: string }) {
  const { pending, onSubmit, formRef } = useActionForm(deleteRuleAction);
  return (
    <form ref={formRef} method="post" onSubmit={onSubmit}>
      <input type="hidden" name="id" value={id} />
      <SubmitButton pending={pending} size="sm" variant="ghost" pendingText="…">삭제</SubmitButton>
    </form>
  );
}
