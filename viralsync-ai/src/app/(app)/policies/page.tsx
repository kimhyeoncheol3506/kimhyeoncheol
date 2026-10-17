import Link from "next/link";
import { requireCtx } from "@/lib/auth/current";
import { can } from "@/lib/auth/permissions";
import { listPolicies, monthlySchedule } from "@/lib/services/policies";
import { PLATFORM_LABEL } from "@/lib/labels";
import { dateOnly } from "@/lib/format";
import { Card, CardBody, CardHeader, PageHeader } from "@/components/ui/card";
import { LinkButton } from "@/components/ui/button";
import { DemoBadge } from "@/components/ui/badge";
import { PolicyStatusBadge, RiskBadge } from "@/components/ui/status";
import { Alert, EmptyState, Table } from "@/components/ui/misc";

export const metadata = { title: "정책 관리 센터" };

export default async function PoliciesPage() {
  const ctx = await requireCtx();
  const rows = await listPolicies(ctx);
  const { overdue, thisMonth } = monthlySchedule(rows);
  return (
    <>
      <PageHeader
        title="정책 관리 센터"
        description="플랫폼별 광고·자동화 정책을 월 단위로 검토하고 변경 이력을 기록합니다."
        actions={can(ctx.role, "policy:write") && <LinkButton href="/policies/new">+ 정책 검토 등록</LinkButton>}
      />
      <div className="mb-6 space-y-3">
        <Alert tone="warn" title="자동 정책 확인: 비활성">
          매월 공식 정책 문서를 자동으로 수집·비교하는 기능은 스케줄러와 데이터 수집 연동이 구성되지 않아 비활성 상태입니다. 담당자가 공식 문서를 직접 확인하고 결과를 기록해야 하며, 확인하지 못한 항목은 ‘검토 미완료’로 표시됩니다.
        </Alert>
      </div>
      <div className="mb-6 grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader title={`검토 기한 경과 (${overdue.length})`} />
          <CardBody>
            {overdue.length === 0 ? <p className="text-sm text-slate-500">없음</p> : (
              <ul className="space-y-1 text-sm">
                {overdue.map((p) => (
                  <li key={p.id}><Link href={`/policies/${p.id}`} className="link">{PLATFORM_LABEL[p.platform]}</Link> — 예정일 {dateOnly(p.nextReviewAt)}</li>
                ))}
              </ul>
            )}
          </CardBody>
        </Card>
        <Card>
          <CardHeader title={`이번 달 검토 일정 (${thisMonth.length})`} />
          <CardBody>
            {thisMonth.length === 0 ? <p className="text-sm text-slate-500">없음</p> : (
              <ul className="space-y-1 text-sm">
                {thisMonth.map((p) => (
                  <li key={p.id}><Link href={`/policies/${p.id}`} className="link">{PLATFORM_LABEL[p.platform]}</Link> — {dateOnly(p.nextReviewAt)} · 담당 {p.owner?.name ?? "미지정"}</li>
                ))}
              </ul>
            )}
          </CardBody>
        </Card>
      </div>
      {rows.length === 0 ? (
        <EmptyState title="정책 검토 기록이 없습니다" />
      ) : (
        <Card>
          <Table minWidth={960}>
            <thead className="bg-slate-50">
              <tr>
                <th className="th">플랫폼</th>
                <th className="th">상태</th>
                <th className="th">위험</th>
                <th className="th">마지막 검토</th>
                <th className="th">다음 검토</th>
                <th className="th">담당자</th>
                <th className="th">영향 기능</th>
                <th className="th">공식 정책</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {rows.map((p) => (
                <tr key={p.id}>
                  <td className="td"><Link className="link" href={`/policies/${p.id}`}>{PLATFORM_LABEL[p.platform]}</Link> {p.isDemo && <DemoBadge />}</td>
                  <td className="td"><PolicyStatusBadge status={p.status} /></td>
                  <td className="td"><RiskBadge level={p.riskLevel} /></td>
                  <td className="td text-xs">{dateOnly(p.lastReviewedAt)}</td>
                  <td className={`td text-xs ${p.nextReviewAt < new Date() ? "font-semibold text-rose-600" : ""}`}>{dateOnly(p.nextReviewAt)}</td>
                  <td className="td text-xs">{p.owner?.name ?? "-"}</td>
                  <td className="td text-xs">{p.affectedFeatures.join(", ")}</td>
                  <td className="td text-xs"><a className="link break-all" href={p.policyUrl} target="_blank" rel="noreferrer noopener">문서 ↗</a></td>
                </tr>
              ))}
            </tbody>
          </Table>
        </Card>
      )}
    </>
  );
}
