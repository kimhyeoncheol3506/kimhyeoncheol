import { requireCtx } from "@/lib/auth/current";
import { can } from "@/lib/auth/permissions";
import { campaignSummary, dashboard } from "@/lib/services/reports";
import { listClientOptions } from "@/lib/services/clients";
import { brand } from "@/config/brand";
import { PLATFORM_LABEL, PLATFORMS, METRIC_SOURCE_LABEL } from "@/lib/labels";
import { dateTime, won } from "@/lib/format";
import { str, type SP } from "@/lib/page";
import { Forbidden } from "@/components/ui/misc";
import { PrintButton } from "./print-button";

export const metadata = { title: "월간 보고서" };

export default async function MonthlyReportPage({ searchParams }: { searchParams: Promise<SP> }) {
  const ctx = await requireCtx();
  if (!can(ctx.role, "report:export")) return <Forbidden message="보고서 출력 권한이 없습니다." />;
  const sp = await searchParams;
  const monthStr = /^\d{4}-\d{2}$/.test(str(sp, "month") ?? "") ? str(sp, "month")! : new Date().toISOString().slice(0, 7);
  const [y, m] = monthStr.split("-").map(Number);
  const from = new Date(Date.UTC(y, m - 1, 1));
  const to = new Date(Date.UTC(y, m, 0, 23, 59, 59, 999));
  const clientId = str(sp, "clientId");
  const filter = { from, to, clientId };
  const [d, summary, clients] = await Promise.all([dashboard(ctx, filter), campaignSummary(ctx, filter), listClientOptions(ctx)]);
  const clientName = clients.find((c) => c.id === clientId)?.name ?? "전체 고객";
  const simulated = d.metrics.bySource.SIMULATED.records + d.metrics.bySource.DEMO_SEED.records;

  return (
    <div className="mx-auto max-w-4xl">
      <form className="no-print mb-6 flex flex-wrap items-end gap-2">
        <div>
          <label htmlFor="m-month" className="label">보고 월</label>
          <input id="m-month" type="month" name="month" defaultValue={monthStr} className="input" />
        </div>
        <div>
          <label htmlFor="m-client" className="label">고객</label>
          <select id="m-client" name="clientId" defaultValue={clientId ?? ""} className="input">
            <option value="">전체 고객</option>
            {clients.map((c) => (
              <option key={c.id} value={c.id}>{c.name}</option>
            ))}
          </select>
        </div>
        <button className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm">조회</button>
        <PrintButton />
      </form>
      <article className="rounded-xl border border-slate-200 bg-white p-8 shadow-sm print:border-0 print:shadow-none">
        <header className="border-b border-slate-200 pb-4">
          <p className="text-xs text-slate-500">{brand.name} 월간 캠페인 보고서</p>
          <h1 className="mt-1 text-2xl font-bold">{y}년 {m}월 · {clientName}</h1>
          <p className="mt-1 text-xs text-slate-500">생성 {dateTime(new Date())} · 작성자 {ctx.name}</p>
        </header>
        {simulated > 0 && (
          <p className="mt-4 rounded bg-violet-50 p-3 text-xs text-violet-800">
            ※ 본 보고서의 실적에는 {METRIC_SOURCE_LABEL.SIMULATED}/{METRIC_SOURCE_LABEL.DEMO_SEED}가 포함되어 있습니다. 실제 외부 플랫폼에서 수집·검증된 수치가 아닙니다.
          </p>
        )}
        <section className="mt-6">
          <h2 className="mb-2 font-semibold">1. 요약</h2>
          <table className="w-full text-sm">
            <tbody className="divide-y divide-slate-100">
              <tr><td className="py-1.5 text-slate-500">게시 완료</td><td className="py-1.5 text-right font-medium">{d.published}건 (실제 게시 {PLATFORMS.reduce((a, p) => a + d.perPlatform[p].live, 0)}건)</td></tr>
              <tr><td className="py-1.5 text-slate-500">클릭 / 방문 / 전환</td><td className="py-1.5 text-right font-medium">{d.metrics.clicks.toLocaleString()} / {d.metrics.visits.toLocaleString()} / {d.metrics.conversions.toLocaleString()}</td></tr>
              <tr><td className="py-1.5 text-slate-500">실행 실패 / 사전검사 차단</td><td className="py-1.5 text-right font-medium">{d.failed} / {d.blocked}</td></tr>
              {d.showCost && <tr><td className="py-1.5 text-slate-500">광고비 / AI 비용</td><td className="py-1.5 text-right font-medium">{won(d.adSpend)} / {won(d.aiCost)}</td></tr>}
            </tbody>
          </table>
        </section>
        <section className="mt-6">
          <h2 className="mb-2 font-semibold">2. 매체별 게시 횟수</h2>
          <table className="w-full text-sm">
            <thead><tr className="border-b text-left text-xs text-slate-500"><th className="py-1">플랫폼</th><th className="py-1 text-right">모의</th><th className="py-1 text-right">실제</th></tr></thead>
            <tbody className="divide-y divide-slate-100">
              {PLATFORMS.map((p) => (
                <tr key={p}><td className="py-1.5">{PLATFORM_LABEL[p]}</td><td className="py-1.5 text-right">{d.perPlatform[p].simulated}</td><td className="py-1.5 text-right">{d.perPlatform[p].live}</td></tr>
              ))}
            </tbody>
          </table>
        </section>
        <section className="mt-6">
          <h2 className="mb-2 font-semibold">3. 캠페인별 실적</h2>
          {summary.length === 0 ? (
            <p className="text-sm text-slate-500">해당 월 실행 기록이 없습니다.</p>
          ) : (
            <table className="w-full text-sm">
              <thead><tr className="border-b text-left text-xs text-slate-500"><th className="py-1">캠페인</th><th className="py-1 text-right">성공/실패</th><th className="py-1 text-right">클릭</th><th className="py-1 text-right">전환</th>{d.showCost && <th className="py-1 text-right">총비용</th>}</tr></thead>
              <tbody className="divide-y divide-slate-100">
                {summary.map((s) => (
                  <tr key={s.campaignId}>
                    <td className="py-1.5">{s.campaign}<span className="block text-xs text-slate-500">{s.client}</span></td>
                    <td className="py-1.5 text-right">{s.success}/{s.failed}</td>
                    <td className="py-1.5 text-right">{s.clicks.toLocaleString()}</td>
                    <td className="py-1.5 text-right">{s.conversions.toLocaleString()}</td>
                    {d.showCost && <td className="py-1.5 text-right">{won(s.totalCost)}</td>}
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </section>
      </article>
    </div>
  );
}
