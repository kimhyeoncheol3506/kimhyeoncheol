import Link from "next/link";
import { requireCtx } from "@/lib/auth/current";
import { dashboard, parseReportFilter, staffOptions } from "@/lib/services/reports";
import { listClientOptions } from "@/lib/services/clients";
import { getProvider } from "@/lib/ai";
import { PLATFORM_LABEL, PLATFORMS, METRIC_SOURCE_LABEL } from "@/lib/labels";
import { dateTime, num, won } from "@/lib/format";
import { str, type SP } from "@/lib/page";
import { Card, CardBody, CardHeader, PageHeader, StatCard } from "@/components/ui/card";
import { Alert, BarList, EmptyState } from "@/components/ui/misc";
import { ReportFilters } from "@/components/reports/filters";
import { secretaryReport } from "@/lib/services/company";
import { SecretaryReport } from "@/components/company/secretary-report";

export const metadata = { title: "대시보드" };

export default async function DashboardPage({ searchParams }: { searchParams: Promise<SP> }) {
  const ctx = await requireCtx();
  const sp = await searchParams;
  const filter = parseReportFilter(sp);
  const [d, clients, staff, report] = await Promise.all([dashboard(ctx, filter), listClientOptions(ctx), staffOptions(ctx), secretaryReport(ctx)]);
  const { status: aiStatus } = getProvider();
  const m = d.metrics;
  const simulatedShare = m.bySource.SIMULATED.records + m.bySource.DEMO_SEED.records;

  return (
    <>
      <PageHeader title="대시보드" description="캠페인 운영 현황을 한눈에 확인합니다. 모든 실적은 출처(모의·데모·실측)를 구분해 표시합니다." />
      <SecretaryReport lines={report} />
      <ReportFilters
        action="/dashboard"
        values={{ from: str(sp, "from"), to: str(sp, "to"), clientId: filter.clientId, platform: filter.platform, userId: filter.userId }}
        clients={clients}
        staff={staff}
      />
      {!aiStatus.configured && (
        <div className="mb-4">
          <Alert tone="info" title="AI Provider: 데모 모드">{aiStatus.message}</Alert>
        </div>
      )}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="전체 고객 수" value={d.clients.toLocaleString("ko-KR")} />
        <StatCard label="진행 중인 캠페인" value={d.activeCampaigns.toLocaleString("ko-KR")} hint="분석 완료 ~ 실행 대기" />
        <StatCard
          label="이번 달 의뢰 금액"
          value={d.monthRequestAmount == null ? "권한 없음" : won(d.monthRequestAmount)}
          hint={`이번 달 의뢰 ${d.monthRequestCount}건`}
        />
        <StatCard label="게시 완료 건수" value={d.published.toLocaleString("ko-KR")} hint="모의 실행 포함 · 실제 게시 0건" tone="good" />
        <StatCard label="클릭 수" value={num(m.clicks)} hint={simulatedShare ? "모의·데모 실적 포함" : undefined} />
        <StatCard label="랜딩 방문 수" value={num(m.visits)} hint={simulatedShare ? "모의·데모 실적 포함" : undefined} />
        <StatCard label="전환 수" value={num(m.conversions)} hint={simulatedShare ? "모의·데모 실적 포함" : undefined} />
        <StatCard
          label="승인 대기 / 오류"
          value={
            <span>
              <Link href="/approvals" className="hover:underline">{d.pendingReview}</Link>
              <span className="mx-1 text-slate-300">/</span>
              <Link href="/executions?status=FAILED" className="text-rose-600 hover:underline">{d.failed + d.blocked}</Link>
            </span>
          }
          hint={`실행 실패 ${d.failed} · 사전검사 차단 ${d.blocked}`}
          tone={d.failed + d.blocked > 0 ? "warn" : "default"}
        />
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader title="매체별 게시 횟수" description="게시 완료(성공) 기준 · 모의 실행과 실제 게시를 구분" />
          <CardBody>
            <BarList
              items={PLATFORMS.map((p) => ({
                label: PLATFORM_LABEL[p],
                value: d.perPlatform[p].simulated + d.perPlatform[p].live,
                sub: `모의 ${d.perPlatform[p].simulated} · 실제 ${d.perPlatform[p].live}`,
              }))}
              unit="건"
              emptyText="게시 완료 기록이 없습니다."
            />
          </CardBody>
        </Card>
        <Card>
          <CardHeader title="실적 출처 구분" description="실제 수집하지 않은 수치는 실측으로 표시하지 않습니다" />
          <CardBody>
            <dl className="space-y-3 text-sm">
              {(["VERIFIED", "SIMULATED", "DEMO_SEED"] as const).map((s) => (
                <div key={s} className="flex items-center justify-between">
                  <dt className="text-slate-600">{METRIC_SOURCE_LABEL[s]}</dt>
                  <dd className="tabular-nums text-slate-800">
                    클릭 {m.bySource[s].clicks.toLocaleString()} · 전환 {m.bySource[s].conversions.toLocaleString()}
                  </dd>
                </div>
              ))}
              <div className="flex items-center justify-between">
                <dt className="text-slate-600">미측정 기록</dt>
                <dd className="tabular-nums text-slate-800">{m.unmeasured}건</dd>
              </div>
            </dl>
            {m.bySource.VERIFIED.records === 0 && (
              <p className="mt-3 rounded-lg bg-slate-50 p-2 text-xs text-slate-500">실측(검증된) 실적 수집 연동이 아직 없습니다. 위 수치는 모두 모의·데모 데이터입니다.</p>
            )}
          </CardBody>
        </Card>
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader title="비용 현황" description="AI 생성 비용 · 광고비 · 캠페인별 총비용" />
          <CardBody>
            {!d.showCost ? (
              <Alert tone="warn">비용 데이터 열람 권한이 없습니다.</Alert>
            ) : (
              <>
                <div className="mb-4 grid grid-cols-2 gap-3 text-sm">
                  <div className="rounded-lg bg-slate-50 p-3">
                    <p className="text-xs text-slate-500">AI 생성 비용</p>
                    <p className="text-lg font-bold">{won(d.aiCost)}</p>
                  </div>
                  <div className="rounded-lg bg-slate-50 p-3">
                    <p className="text-xs text-slate-500">광고비 (데모 샘플 포함)</p>
                    <p className="text-lg font-bold">{won(d.adSpend)}</p>
                  </div>
                </div>
                {d.campaignCosts.length === 0 ? (
                  <EmptyState title="비용 기록이 없습니다" />
                ) : (
                  <ul className="divide-y divide-slate-100 text-sm">
                    {d.campaignCosts.slice(0, 6).map((c) => (
                      <li key={c.id} className="flex items-center justify-between py-2">
                        <Link href={`/campaigns/${c.id}`} className="link truncate">{c.name}</Link>
                        <span className="ml-2 whitespace-nowrap tabular-nums text-slate-700">
                          {won(c.total)} <span className="text-xs text-slate-400">(AI {won(c.ai)})</span>
                        </span>
                      </li>
                    ))}
                  </ul>
                )}
              </>
            )}
          </CardBody>
        </Card>
        <Card>
          <CardHeader title="최근 활동 내역" description={ctx.role === "ADMIN" ? "조직 전체" : "내 활동"} action={ctx.role === "ADMIN" ? <Link href="/audit" className="link text-xs">전체 보기</Link> : undefined} />
          <CardBody>
            {d.recent.length === 0 ? (
              <EmptyState title="최근 활동이 없습니다" />
            ) : (
              <ol className="space-y-3">
                {d.recent.map((a) => (
                  <li key={a.id} className="flex gap-3 text-sm">
                    <span className="mt-1.5 h-2 w-2 flex-none rounded-full bg-brand-500" aria-hidden />
                    <div className="min-w-0">
                      <p className="truncate text-slate-800">{a.summary}</p>
                      <p className="text-xs text-slate-500">
                        {a.actor?.name ?? "시스템"} · {dateTime(a.createdAt)}
                      </p>
                    </div>
                  </li>
                ))}
              </ol>
            )}
          </CardBody>
        </Card>
      </div>
    </>
  );
}
