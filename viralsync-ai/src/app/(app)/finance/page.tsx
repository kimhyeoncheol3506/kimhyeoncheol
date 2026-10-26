import { requireCtx } from "@/lib/auth/current";
import { can } from "@/lib/auth/permissions";
import { financeSummary } from "@/lib/services/business";
import { MONEY } from "@/lib/business/playbook";
import { won } from "@/lib/format";
import { Card, CardBody, CardHeader, PageHeader, StatCard } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Alert, Forbidden } from "@/components/ui/misc";
import { DeleteFixedCost, FixedCostForm } from "@/components/business/forms";

export const metadata = { title: "재무" };

export default async function FinancePage() {
  const ctx = await requireCtx();
  if (!can(ctx.role, "cost:read")) return <Forbidden />;
  const f = await financeSummary(ctx);
  const canEdit = can(ctx.role, "finance:manage");
  const max = Math.max(1, ...f.series.map((s) => s.revenue));
  return (
    <>
      <PageHeader title="재무" description="통장 3개 원칙 · 매월 1일 10분 현금흐름 확인. 매출은 ‘입금 확인’ 기준이며, 금액은 책의 대략치 규칙으로 계산한 참고값입니다 (세무사 확인 권장)." />
      {f.failure.length > 0 && (
        <div className="mb-4"><Alert tone="error" title="실패 신호">{f.failure.map((x) => <p key={x}>• {x}</p>)}</Alert></div>
      )}
      <div className="mb-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="월 정기 매출 (MRR)" value={won(f.mrr)} hint={`유료 단골 ${f.paying}명 / 목표 ${f.goal}명`} tone={f.paying >= 3 ? "good" : "default"} />
        <StatCard label="이번 달 입금" value={won(f.thisMonth.revenue)} hint={`미수금 ${won(f.receivable)} (${f.receivableCount}건)`} tone={f.receivableCount ? "warn" : "default"} />
        <StatCard label="월 고정비" value={won(f.fixedTotal)} hint={`도구·구독 ${won(f.toolTotal)} / 한도 ${won(MONEY.fixedCostLimit)}`} tone={f.toolOver ? "danger" : "default"} />
        <StatCard label="비상금 (고정비 3개월)" value={f.profile.cashReserveKrw == null ? "잔고 미입력" : `${won(f.profile.cashReserveKrw)} / ${won(f.reserveTarget)}`} hint={f.reserveOk ? "달성 — 시스템 투자 가능" : "달성 전엔 새 지출 금지"} tone={f.reserveOk ? "good" : "warn"} />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader title="통장 3개" description="PART 10-1" />
          <CardBody>
            <ol className="space-y-2 text-sm">
              <li><Badge tone="indigo">A 사업입금</Badge> 고객 돈만 들어오는 곳 — 이번 달 {won(f.thisMonth.revenue)}</li>
              <li><Badge tone="amber">세금 예치</Badge> 매출의 {MONEY.taxReservePct}% → 이번 달 <strong>{won(f.taxReserve)}</strong> (5월 종합소득세)</li>
              <li><Badge tone="gray">B 사업지출</Badge> 구독료·소모품만 — 월 고정비 {won(f.fixedTotal)}</li>
              <li><Badge tone="green">C 내 월급</Badge> 매출의 {MONEY.salaryCapPct}% 이하 → 이번 달 최대 <strong>{won(f.salaryCap)}</strong> (월 150만 원까지는 빨리 올리기)</li>
            </ol>
            <p className="mt-3 text-xs text-slate-500">수익 우선순위: ① 비상금 3개월 ② 세금 예치 ③ 내 월급 ④ 시스템 투자 ⑤ 남는 돈</p>
          </CardBody>
        </Card>

        <Card>
          <CardHeader title="최근 6개월 입금" description="막대 = 입금 · 이익 = 입금 − 고정비 − AI 비용 (내 월급 제외)" />
          <CardBody>
            <ul className="space-y-2 text-xs">
              {f.series.map((s) => (
                <li key={s.month}>
                  <div className="flex justify-between"><span>{s.month}</span><span className="tabular-nums">{won(s.revenue)} · 이익 <span className={s.profit < 0 ? "text-rose-600" : "text-emerald-700"}>{won(s.profit)}</span></span></div>
                  <div className="h-2 rounded bg-slate-100"><div className="h-2 rounded bg-brand-500" style={{ width: `${(s.revenue / max) * 100}%` }} /></div>
                </li>
              ))}
            </ul>
          </CardBody>
        </Card>

        <Card>
          <CardHeader title="앞으로 3개월 현금흐름" description="유료 계약이 그대로 유지된다고 볼 때" />
          <CardBody>
            <table className="w-full text-sm">
              <thead><tr className="text-left text-xs text-slate-500"><th className="py-1">월</th><th>들어올 돈</th><th>나갈 돈 (고정비+세금예치)</th><th>순현금</th></tr></thead>
              <tbody>
                {f.forecast.map((x) => (
                  <tr key={x.month} className="border-t border-slate-100">
                    <td className="py-1.5">{x.month}</td>
                    <td className="tabular-nums">{won(x.inflow)}</td>
                    <td className="tabular-nums">{won(x.outflow)}</td>
                    <td className={`tabular-nums ${x.inflow - x.outflow < 0 ? "text-rose-600" : ""}`}>{won(x.inflow - x.outflow)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            {f.newSpendingBlocked && <p className="mt-2 text-xs text-amber-700">비상금(고정비 3개월치)이 쌓이기 전까지 새 지출(장비·도구 업그레이드)은 하지 않습니다.</p>}
          </CardBody>
        </Card>

        <Card>
          <CardHeader title="월 고정비" description={`도구·구독은 월 ${won(MONEY.fixedCostLimit)} 이내 · 건강보험 등 지역가입자 보험료도 고정비로`} />
          <CardBody className="space-y-2">
            {f.toolOver && <Alert tone="warn">도구·구독 지출이 한도를 넘었습니다. 지출이 매출을 앞서면 망하기 시작합니다.</Alert>}
            {f.fixed.length === 0 && <p className="text-sm text-slate-500">등록된 고정비가 없습니다. AI 구독, 인터넷, 건강보험료 등을 적어 주세요.</p>}
            <ul className="space-y-2">
              {f.fixed.map((x) => (
                <li key={x.id} className="flex flex-wrap items-center gap-2">
                  {canEdit ? <FixedCostForm v={x} /> : <span className="text-sm">{x.name} · {x.category} · {won(x.monthlyKrw)}</span>}
                  {canEdit && <DeleteFixedCost id={x.id} />}
                </li>
              ))}
            </ul>
            {canEdit && <div className="border-t border-slate-100 pt-3"><FixedCostForm /></div>}
          </CardBody>
        </Card>
      </div>
    </>
  );
}
