import { PLATFORM_LABEL, PLATFORMS, ROLE_LABEL } from "@/lib/labels";
import type { Role } from "@prisma/client";

export function ReportFilters({
  action,
  values,
  clients,
  staff,
}: {
  action: string;
  values: Record<string, string | undefined>;
  clients: { id: string; name: string }[];
  staff: { id: string; name: string; role: Role }[];
}) {
  return (
    <form action={action} className="no-print mb-5 grid gap-3 rounded-xl border border-slate-200 bg-white p-4 shadow-sm sm:grid-cols-2 lg:grid-cols-6" aria-label="실적 필터">
      <div>
        <label htmlFor="f-from" className="label">시작일</label>
        <input id="f-from" type="date" name="from" defaultValue={values.from} className="input" />
      </div>
      <div>
        <label htmlFor="f-to" className="label">종료일</label>
        <input id="f-to" type="date" name="to" defaultValue={values.to} className="input" />
      </div>
      <div>
        <label htmlFor="f-client" className="label">고객</label>
        <select id="f-client" name="clientId" defaultValue={values.clientId ?? ""} className="input">
          <option value="">전체 고객</option>
          {clients.map((c) => (
            <option key={c.id} value={c.id}>{c.name}</option>
          ))}
        </select>
      </div>
      <div>
        <label htmlFor="f-platform" className="label">플랫폼</label>
        <select id="f-platform" name="platform" defaultValue={values.platform ?? ""} className="input">
          <option value="">전체 플랫폼</option>
          {PLATFORMS.map((p) => (
            <option key={p} value={p}>{PLATFORM_LABEL[p]}</option>
          ))}
        </select>
      </div>
      <div>
        <label htmlFor="f-user" className="label">담당 직원</label>
        <select id="f-user" name="userId" defaultValue={values.userId ?? ""} className="input">
          <option value="">전체 직원</option>
          {staff.map((s) => (
            <option key={s.id} value={s.id}>{s.name} ({ROLE_LABEL[s.role]})</option>
          ))}
        </select>
      </div>
      <div className="flex items-end gap-2">
        <button type="submit" className="rounded-lg bg-brand-600 px-3.5 py-2 text-sm font-medium text-white hover:bg-brand-700">적용</button>
        <a href={action} className="rounded-lg border border-slate-300 px-3.5 py-2 text-sm text-slate-600 hover:bg-slate-50">초기화</a>
      </div>
    </form>
  );
}
