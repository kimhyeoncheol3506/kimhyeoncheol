import Link from "next/link";
import { requireCtx } from "@/lib/auth/current";
import { can } from "@/lib/auth/permissions";
import { listSubscriptions, subscriptionSummary } from "@/lib/services/subscriptions";
import { CLIENT_GOALS } from "@/lib/business/playbook";
import { SUBSCRIPTION_STATUS_LABEL } from "@/lib/labels";
import { dateOnly, won } from "@/lib/format";
import { Card, CardBody, CardHeader, PageHeader, StatCard } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Alert, EmptyState, Table } from "@/components/ui/misc";
import { LinkButton } from "@/components/ui/button";

export const metadata = { title: "월 정액 계약" };

export default async function SubscriptionsPage() {
  const ctx = await requireCtx();
  const subs = await listSubscriptions(ctx);
  const s = subscriptionSummary(subs);
  const goal = CLIENT_GOALS.find((g) => g > s.paying) ?? CLIENT_GOALS[CLIENT_GOALS.length - 1];
  const showMoney = can(ctx.role, "cost:read") || can(ctx.role, "sales:manage");
  return (
    <>
      <PageHeader
        title="월 정액 계약"
        description="SNS·숏폼 운영대행 단골 고객. 2주 무료 → 유료 전환(첫 달 50%) → 매월 청구, 미납 2회면 서비스가 자동 중지됩니다."
        actions={can(ctx.role, "sales:manage") && <LinkButton href="/subscriptions/new">새 계약</LinkButton>}
      />
      <div className="mb-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="유료 단골" value={`${s.paying}명 / 목표 ${goal}명`} hint="3명 → 6명 → 10명" tone={s.paying >= 3 ? "good" : "default"} />
        <StatCard label="월 정기 매출 (MRR)" value={showMoney ? won(s.mrr) : "권한 없음"} hint="유료 운영 중 계약 합계" />
        <StatCard label="무료 체험" value={`${s.trials}건`} hint={s.trialsEnding.length ? `3일 안에 끝남 ${s.trialsEnding.length}건` : "첫 3건은 조건부 무료"} tone={s.trialsEnding.length ? "warn" : "default"} />
        <StatCard label="미수금" value={showMoney ? won(s.receivableAmount) : "권한 없음"} hint={`${s.receivableCount}건 · 중지 ${s.suspended}건`} tone={s.receivableCount ? "danger" : "default"} />
      </div>
      {s.trialsEnding.length > 0 && (
        <div className="mb-4">
          <Alert tone="warn" title="무료 체험이 곧 끝나는 고객">
            {s.trialsEnding.map((t) => <span key={t.id} className="mr-3"><Link className="link" href={`/subscriptions/${t.id}`}>{t.client.name}</Link> ({t.trialEnd ? dateOnly(t.trialEnd) : "-"})</span>)}
            — 결과를 보여 드리고 유료 전환 여부를 여쭤보세요. 무료가 무기한이 되지 않게!
          </Alert>
        </div>
      )}
      <Card>
        <CardHeader title={`계약 (${subs.length})`} />
        <CardBody>
          {subs.length === 0 ? (
            <EmptyState title="아직 계약이 없습니다" description="영업 리스트에서 만남 후 ‘고객으로 등록 → 월 정액 계약’ 으로 시작하세요." action={<LinkButton href="/sales" variant="secondary">영업 리스트</LinkButton>} />
          ) : (
            <Table minWidth={720}>
              <thead>
                <tr className="text-left text-xs text-slate-500">{["고객", "패키지", "월 금액", "상태", "기간", "미납"].map((h) => <th key={h} className="th">{h}</th>)}</tr>
              </thead>
              <tbody>
                {subs.map((x) => {
                  const unpaid = x.payments.filter((p) => !p.paidAt && p.dueDate < new Date()).length;
                  return (
                    <tr key={x.id} className="border-t border-slate-100">
                      <td className="td"><Link href={`/subscriptions/${x.id}`} className="link font-medium">{x.client.name}</Link> <span className="text-xs text-slate-400">{x.client.industry}</span></td>
                      <td className="td text-sm">{x.planName}</td>
                      <td className="td tabular-nums">{showMoney ? won(x.monthlyFee) : "-"}</td>
                      <td className="td"><Badge tone={x.status === "ACTIVE" ? "green" : x.status === "TRIAL" ? "indigo" : x.status === "SUSPENDED" ? "red" : "gray"}>{SUBSCRIPTION_STATUS_LABEL[x.status]}</Badge></td>
                      <td className="td text-xs">{x.status === "TRIAL" ? `체험 ~${x.trialEnd ? dateOnly(x.trialEnd) : "-"}` : x.startDate ? `${dateOnly(x.startDate)}~${x.endDate ? dateOnly(x.endDate) : ""}` : "-"}</td>
                      <td className="td">{unpaid ? <Badge tone="red">{unpaid}회</Badge> : "-"}</td>
                    </tr>
                  );
                })}
              </tbody>
            </Table>
          )}
        </CardBody>
      </Card>
    </>
  );
}
