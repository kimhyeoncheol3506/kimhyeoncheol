import Link from "next/link";
import { requireCtx } from "@/lib/auth/current";
import { can } from "@/lib/auth/permissions";
import { getSubscription, refreshSubscription } from "@/lib/services/subscriptions";
import { MONEY, TRIAL } from "@/lib/business/playbook";
import { SUBSCRIPTION_STATUS_LABEL } from "@/lib/labels";
import { dateOnly, won } from "@/lib/format";
import { orNotFound } from "@/lib/page";
import { Card, CardBody, CardHeader, PageHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Alert, Table } from "@/components/ui/misc";
import { LinkButton } from "@/components/ui/button";
import { OpButton } from "@/components/subscriptions/forms";

export default async function SubscriptionPage({ params, searchParams }: { params: Promise<{ id: string }>; searchParams: Promise<{ created?: string }> }) {
  const ctx = await requireCtx();
  const { id } = await params;
  const { created } = await searchParams;
  await orNotFound(getSubscription(ctx, id));
  const { missed } = await refreshSubscription(ctx, id);
  const s = await getSubscription(ctx, id);
  const canEdit = can(ctx.role, "sales:manage");
  const now = new Date();
  return (
    <>
      <PageHeader
        title={`${s.client.name} · ${s.planName}`}
        description={
          <span className="flex flex-wrap items-center gap-2">
            <Badge tone={s.status === "ACTIVE" ? "green" : s.status === "TRIAL" ? "indigo" : s.status === "SUSPENDED" ? "red" : "gray"}>{SUBSCRIPTION_STATUS_LABEL[s.status]}</Badge>
            <span className="tabular-nums">{won(s.monthlyFee)}/월 ({s.vatIncluded ? "부가세 포함" : "부가세 별도"}) · 매월 {s.billingDay}일</span>
            <Link href="/subscriptions" className="link text-xs">← 계약 목록</Link>
          </span>
        }
        actions={
          <>
            <LinkButton href={`/clients/${s.clientId}`} variant="secondary">고객 화면</LinkButton>
            <LinkButton href={`/subscriptions/${s.id}/contract`} variant="secondary">계약서</LinkButton>
          </>
        }
      />
      {created && <div className="mb-4"><Alert tone="success">계약을 만들었습니다. ‘계약서’ 를 인쇄해 서명받으세요.</Alert></div>}
      {s.status === "SUSPENDED" && <div className="mb-4"><Alert tone="error" title={`미납 ${missed}회 — 서비스 중지 중`}>게시·제작을 멈추세요. 독촉은 카톡 등 서면으로 남기고, 입금이 확인되면 자동으로 재개됩니다. 끊을 때도 인사는 하고 끊으세요.</Alert></div>}

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader title="청구·입금 기록" description={`기한이 지났는데 입금이 없으면 미수금 · ${MONEY.suspendAfterMissed}회면 자동 중지`} />
          <CardBody>
            {s.payments.length === 0 ? (
              <p className="text-sm text-slate-500">{s.status === "TRIAL" ? "무료 체험 중이라 청구서가 없습니다. 유료로 전환하면 첫 달 청구서가 만들어집니다." : "청구서가 없습니다."}</p>
            ) : (
              <Table minWidth={560}>
                <thead><tr className="text-left text-xs text-slate-500">{["월", "금액", "기한", "입금", ""].map((h) => <th key={h} className="th">{h}</th>)}</tr></thead>
                <tbody>
                  {s.payments.map((p) => {
                    const overdue = !p.paidAt && p.dueDate < now;
                    return (
                      <tr key={p.id} className="border-t border-slate-100">
                        <td className="td">{p.period}</td>
                        <td className="td tabular-nums">{won(p.amount)} {p.note && <span className="text-xs text-slate-400">{p.note}</span>}</td>
                        <td className="td text-xs">{dateOnly(p.dueDate)}</td>
                        <td className="td">{p.paidAt ? <Badge tone="green">입금 {dateOnly(p.paidAt)}</Badge> : overdue ? <Badge tone="red">미납</Badge> : <Badge tone="gray">대기</Badge>}</td>
                        <td className="td">{canEdit && (p.paidAt ? <OpButton id={s.id} op="unpay" paymentId={p.id} label="입금 취소" /> : <OpButton id={s.id} op="pay" paymentId={p.id} label="입금 확인" variant="primary" />)}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </Table>
            )}
          </CardBody>
        </Card>
        <Card>
          <CardHeader title="계약 내용" />
          <CardBody className="space-y-3 text-sm">
            <ul className="list-disc pl-5">{s.deliverables.map((d) => <li key={d}>{d}</li>)}</ul>
            {s.status === "TRIAL" && <p>무료 체험 {s.trialStart ? dateOnly(s.trialStart) : "-"} ~ <strong>{s.trialEnd ? dateOnly(s.trialEnd) : "-"}</strong> ({TRIAL.days}일) · 전환 시 첫 달 {s.firstMonthDiscount}% 할인</p>}
            {s.startDate && <p>유료 시작 {dateOnly(s.startDate)}{s.endDate && ` · 종료 ${dateOnly(s.endDate)}`}</p>}
            <p className="text-xs text-slate-500">포트폴리오 사용 {s.portfolioConsent ? "동의" : "미동의"} · 사례 공개 {s.caseStudyConsent ? "동의" : "미동의"}{s.referredBy && ` · 소개: ${s.referredBy.name}`}</p>
            {s.notes && <p className="whitespace-pre-line text-xs text-slate-600">{s.notes}</p>}
            {canEdit && (
              <div className="space-y-2 border-t border-slate-100 pt-3">
                {s.status === "TRIAL" && <OpButton id={s.id} op="paid" label="유료로 전환" variant="primary" />}
                {s.status !== "ENDED" && <OpButton id={s.id} op="end" label={`계약 종료 (${s.noticeDays}일 통보)`} variant="danger" withReason />}
              </div>
            )}
          </CardBody>
        </Card>
      </div>
    </>
  );
}
