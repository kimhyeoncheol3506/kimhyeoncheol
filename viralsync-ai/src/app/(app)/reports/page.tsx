import Link from "next/link";
import { requireCtx } from "@/lib/auth/current";
import { can } from "@/lib/auth/permissions";
import { campaignSummary, dashboard, parseReportFilter, publicationRows, staffOptions } from "@/lib/services/reports";
import { listClientOptions } from "@/lib/services/clients";
import { CONTENT_TYPE_LABEL, PLATFORM_LABEL, PLATFORMS } from "@/lib/labels";
import { dateTime, num, won } from "@/lib/format";
import { str, type SP } from "@/lib/page";
import { Card, CardBody, CardHeader, PageHeader, StatCard } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { MetricSourceBadge, PublicationStatusBadge } from "@/components/ui/status";
import { BarList, EmptyState, Table } from "@/components/ui/misc";
import { ReportFilters } from "@/components/reports/filters";

export const metadata = { title: "실적·보고서" };

export default async function ReportsPage({ searchParams }: { searchParams: Promise<SP> }) {
  const ctx = await requireCtx();
  const sp = await searchParams;
  const filter = parseReportFilter(sp);
  const raw = { from: str(sp, "from"), to: str(sp, "to"), clientId: filter.clientId, platform: filter.platform, userId: filter.userId };
  const qs = new URLSearchParams(Object.entries(raw).filter((e): e is [string, string] => !!e[1])).toString();
  const [d, rows, summary, clients, staff] = await Promise.all([
    dashboard(ctx, filter),
    publicationRows(ctx, filter),
    campaignSummary(ctx, filter),
    listClientOptions(ctx),
    staffOptions(ctx),
  ]);
  const canExport = can(ctx.role, "report:export");
  const showCost = d.showCost;
  const success = rows.filter((r) => r.status === "SUCCESS").length;
  const failed = rows.filter((r) => r.status === "FAILED").length;
  const month = new Date().toISOString().slice(0, 7);

  return (
    <>
      <PageHeader
        title="실적 및 분석"
        description="게시 완료·클릭·방문·전환을 서로 다른 지표로 집계합니다. 모의·데모 실적은 실측과 구분해 표시합니다."
        actions={
          canExport && (
            <>
              <a href={`/api/export/publications?${qs}`} className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm hover:bg-slate-50">실행 이력 CSV</a>
              <a href={`/api/export/campaigns?${qs}`} className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm hover:bg-slate-50">캠페인 실적 CSV</a>
              <Link href={`/reports/monthly?month=${month}${filter.clientId ? `&clientId=${filter.clientId}` : ""}`} className="rounded-lg bg-brand-600 px-3 py-2 text-sm font-medium text-white hover:bg-brand-700">월간 보고서</Link>
            </>
          )
        }
      />
      <ReportFilters action="/reports" values={raw} clients={clients} staff={staff} />
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
        <StatCard label="실행 성공" value={success} tone="good" />
        <StatCard label="실행 실패" value={failed} tone={failed ? "danger" : "default"} />
        <StatCard label="클릭" value={num(d.metrics.clicks)} />
        <StatCard label="방문" value={num(d.metrics.visits)} />
        <StatCard label="전환" value={num(d.metrics.conversions)} />
      </div>
      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader title="플랫폼별 게시 횟수" />
          <CardBody>
            <BarList items={PLATFORMS.map((p) => ({ label: PLATFORM_LABEL[p], value: d.perPlatform[p].simulated + d.perPlatform[p].live, sub: `모의 ${d.perPlatform[p].simulated} · 실제 ${d.perPlatform[p].live}` }))} unit="건" />
          </CardBody>
        </Card>
        <Card>
          <CardHeader title="캠페인별 클릭·전환" />
          <CardBody>
            <BarList items={summary.slice(0, 8).map((s) => ({ label: s.campaign, value: s.clicks, sub: `전환 ${s.conversions}` }))} unit=" 클릭" />
          </CardBody>
        </Card>
      </div>

      <Card className="mt-6">
        <CardHeader title="캠페인별 실적·비용" />
        {summary.length === 0 ? (
          <CardBody><EmptyState title="해당 조건의 실적이 없습니다" /></CardBody>
        ) : (
          <Table minWidth={900}>
            <thead className="bg-slate-50">
              <tr>
                <th className="th">고객 · 캠페인</th>
                <th className="th">담당자</th>
                <th className="th text-right">성공</th>
                <th className="th text-right">실패</th>
                <th className="th text-right">클릭</th>
                <th className="th text-right">방문</th>
                <th className="th text-right">전환</th>
                <th className="th">출처</th>
                {showCost && <th className="th text-right">광고비</th>}
                {showCost && <th className="th text-right">AI 비용</th>}
                {showCost && <th className="th text-right">총비용</th>}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {summary.map((s) => (
                <tr key={s.campaignId}>
                  <td className="td">
                    <Link className="link" href={`/campaigns/${s.campaignId}`}>{s.campaign}</Link>
                    <p className="text-xs text-slate-500">{s.client}</p>
                  </td>
                  <td className="td text-xs">{s.owner}</td>
                  <td className="td text-right tabular-nums">{s.success}</td>
                  <td className="td text-right tabular-nums">{s.failed}</td>
                  <td className="td text-right tabular-nums">{s.clicks.toLocaleString()}</td>
                  <td className="td text-right tabular-nums">{s.visits.toLocaleString()}</td>
                  <td className="td text-right tabular-nums">{s.conversions.toLocaleString()}</td>
                  <td className="td text-xs">{s.sources.split("/").map((x) => (x === "-" ? "-" : <MetricSourceBadge key={x} source={x as "SIMULATED"} />))}</td>
                  {showCost && <td className="td text-right tabular-nums">{won(s.adSpend)}</td>}
                  {showCost && <td className="td text-right tabular-nums">{won(s.aiCost)}</td>}
                  {showCost && <td className="td text-right font-semibold tabular-nums">{won(s.totalCost)}</td>}
                </tr>
              ))}
            </tbody>
          </Table>
        )}
      </Card>

      <Card className="mt-6">
        <CardHeader title={`실행 이력 (${rows.length})`} description="모든 캠페인 실행 이력 (최대 2000건)" />
        {rows.length === 0 ? (
          <CardBody><EmptyState title="실행 이력이 없습니다" /></CardBody>
        ) : (
          <Table minWidth={1100}>
            <thead className="bg-slate-50">
              <tr>
                <th className="th">고객 · 캠페인</th>
                <th className="th">플랫폼 · 유형</th>
                <th className="th">담당자 / 승인자</th>
                <th className="th">실행 일시</th>
                <th className="th">결과</th>
                <th className="th text-right">클릭</th>
                <th className="th text-right">방문</th>
                <th className="th text-right">전환</th>
                <th className="th">출처</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {rows.slice(0, 100).map((r) => (
                <tr key={r.id}>
                  <td className="td">{r.campaign}<p className="text-xs text-slate-500">{r.client}</p></td>
                  <td className="td text-xs">{PLATFORM_LABEL[r.platform]} · {CONTENT_TYPE_LABEL[r.contentType as keyof typeof CONTENT_TYPE_LABEL]}</td>
                  <td className="td text-xs">{r.owner} / {r.approver}</td>
                  <td className="td whitespace-nowrap text-xs">{dateTime(r.executedAt)}</td>
                  <td className="td">
                    <PublicationStatusBadge status={r.status as "SUCCESS"} /> {r.mode === "SIMULATED" && <Badge tone="purple">모의</Badge>}
                  </td>
                  <td className="td text-right tabular-nums">{num(r.clicks)}</td>
                  <td className="td text-right tabular-nums">{num(r.visits)}</td>
                  <td className="td text-right tabular-nums">{num(r.conversions)}</td>
                  <td className="td"><MetricSourceBadge source={r.metricSource} /></td>
                </tr>
              ))}
            </tbody>
          </Table>
        )}
      </Card>
    </>
  );
}
