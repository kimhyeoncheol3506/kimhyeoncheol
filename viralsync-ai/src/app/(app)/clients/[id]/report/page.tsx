import Link from "next/link";
import { requireCtx } from "@/lib/auth/current";
import { getClient } from "@/lib/services/clients";
import { clientMonthlyReport, previousPeriod } from "@/lib/services/portal";
import { orNotFound, str, type SP } from "@/lib/page";
import { MonthlyReport } from "@/components/portal/monthly-report";
import { PrintButton } from "@/components/print/print-button";

export const metadata = { title: "월 보고서 (반 장)" };

export default async function ClientReportPage({ params, searchParams }: { params: Promise<{ id: string }>; searchParams: Promise<SP> }) {
  const ctx = await requireCtx();
  const c = await orNotFound(getClient(ctx, (await params).id));
  const raw = str(await searchParams, "month");
  const period = raw && /^\d{4}-\d{2}$/.test(raw) ? raw : previousPeriod();
  const r = await clientMonthlyReport(ctx.organizationId, c.id, period);
  return (
    <>
      <form className="no-print mb-4 flex flex-wrap items-end gap-2">
        <Link href={`/clients/${c.id}`} className="link mr-auto text-sm">← {c.name}</Link>
        <label htmlFor="month" className="label">월</label>
        <input id="month" name="month" type="month" defaultValue={period} className="input w-auto" />
        <button type="submit" className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm">보기</button>
        <PrintButton />
      </form>
      <div className="mx-auto max-w-2xl"><MonthlyReport r={r} clientName={c.name} /></div>
      <p className="no-print mx-auto mt-3 max-w-2xl text-xs text-slate-500">사장님 링크의 ‘지난달 보고서’ 에서도 같은 내용을 볼 수 있고, 열어 본 기록이 남습니다 (안 보면 이탈 경고).</p>
    </>
  );
}
