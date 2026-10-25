"use client";
import { useActionForm } from "@/components/ui/use-action-form";
import { createUserAction, updateUserAction } from "@/app/actions/users";
import { ROLE_LABEL } from "@/lib/labels";
import { Field } from "@/components/ui/misc";
import { FormMessage } from "@/components/ui/form-status";
import { SubmitButton } from "@/components/ui/submit-button";

export function CreateUserForm() {
  const { state, pending, onSubmit, formRef } = useActionForm(createUserAction, { resetOnSuccess: true });
  const e = state.errors ?? {};
  return (
    <form ref={formRef} method="post" onSubmit={onSubmit} className="grid gap-3 sm:grid-cols-5" noValidate>
      <div className="sm:col-span-5"><FormMessage state={state} /></div>
      <Field label="이름" htmlFor="u-name" error={e.name} required><input id="u-name" name="name" className="input" /></Field>
      <Field label="이메일" htmlFor="u-email" error={e.email} required><input id="u-email" name="email" type="email" className="input" /></Field>
      <Field label="역할" htmlFor="u-role" error={e.role}>
        <select id="u-role" name="role" className="input" defaultValue="VIEWER">
          {Object.entries(ROLE_LABEL).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
        </select>
      </Field>
      <Field label="초기 비밀번호" htmlFor="u-pw" error={e.password} required><input id="u-pw" name="password" type="password" autoComplete="new-password" className="input" /></Field>
      <div className="flex items-end"><SubmitButton pending={pending} pendingText="등록 중…">직원 등록</SubmitButton></div>
    </form>
  );
}

export function UserRow({
  user,
  clients,
  teams,
  self,
}: {
  user: { id: string; name: string; email: string; role: string; active: boolean; isDemo: boolean; clientIds: string[]; teamId: string | null };
  clients: { id: string; name: string }[];
  teams: { id: string; name: string }[];
  self: boolean;
}) {
  const { state, pending, onSubmit, formRef } = useActionForm(updateUserAction);
  return (
    <form ref={formRef} method="post" onSubmit={onSubmit} className="grid gap-3 rounded-xl border border-slate-200 bg-white p-4 shadow-sm lg:grid-cols-4">
      <input type="hidden" name="userId" value={user.id} />
      <div>
        <p className="font-medium text-slate-800">{user.name} {self && <span className="text-xs text-slate-400">(나)</span>}</p>
        <p className="text-xs text-slate-500">{user.email}</p>
        <label className="mt-2 flex items-center gap-1.5 text-xs">
          <input type="checkbox" name="active" defaultChecked={user.active} disabled={self} /> 활성
          {self && <input type="hidden" name="active" value="on" />}
        </label>
      </div>
      <div>
        <label htmlFor={`role-${user.id}`} className="label">역할</label>
        <select id={`role-${user.id}`} name="role" defaultValue={user.role} className="input" disabled={self}>
          {Object.entries(ROLE_LABEL).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
        </select>
        {self && <input type="hidden" name="role" value={user.role} />}
        <label htmlFor={`team-${user.id}`} className="label mt-2">소속 팀</label>
        <select id={`team-${user.id}`} name="teamId" defaultValue={user.teamId ?? ""} className="input">
          <option value="">팀 없음</option>
          {teams.map((t) => <option key={t.id} value={t.id}>{t.name}</option>)}
        </select>
      </div>
      <fieldset className="lg:col-span-1">
        <legend className="label">개별 배정 고객 {user.role === "ADMIN" ? <span className="text-xs font-normal text-slate-400">(관리자는 전체)</span> : <span className="text-xs font-normal text-slate-400">(소속 팀 고객은 자동 포함)</span>}</legend>
        <div className="max-h-28 space-y-1 overflow-y-auto text-xs">
          {clients.map((c) => (
            <label key={c.id} className="flex items-center gap-1.5">
              <input type="checkbox" name="clientIds" value={c.id} defaultChecked={user.clientIds.includes(c.id)} /> {c.name}
            </label>
          ))}
        </div>
      </fieldset>
      <div className="flex flex-col items-start justify-end gap-2">
        <SubmitButton pending={pending} size="sm" pendingText="저장 중…">저장</SubmitButton>
        <FormMessage state={state} />
      </div>
    </form>
  );
}
