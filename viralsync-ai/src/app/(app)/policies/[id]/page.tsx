import { requireCtx } from "@/lib/auth/current";
import { can } from "@/lib/auth/permissions";
import { getPolicy, policyHistory } from "@/lib/services/policies";
import { staffOptions } from "@/lib/services/reports";
import { PLATFORM_LABEL } from "@/lib/labels";
import { dateInput, dateTime } from "@/lib/format";
import { orNotFound } from "@/lib/page";
import { Card, CardBody, CardHeader, PageHeader } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/misc";
import { PolicyForm } from "@/components/forms/policy-form";

export default async function PolicyDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const ctx = await requireCtx();
  const { id } = await params;
  const [p, history, users] = await Promise.all([orNotFound(getPolicy(ctx, id)), policyHistory(ctx, id), staffOptions(ctx)]);
  return (
    <>
      <PageHeader title={`${PLATFORM_LABEL[p.platform]} 정책 검토`} />
      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardBody>
            <PolicyForm
              users={users}
              readOnly={!can(ctx.role, "policy:write")}
              values={{
                id: p.id,
                platform: p.platform,
                policyUrl: p.policyUrl,
                status: p.status,
                lastReviewedAt: dateInput(p.lastReviewedAt),
                nextReviewAt: dateInput(p.nextReviewAt),
                changeSummary: p.changeSummary,
                affectedFeatures: p.affectedFeatures,
                riskLevel: p.riskLevel,
                ownerId: p.ownerId,
                actionItems: p.actionItems,
                result: p.result,
              }}
            />
          </CardBody>
        </Card>
        <Card>
          <CardHeader title="변경 이력" />
          <CardBody>
            {history.length === 0 ? (
              <EmptyState title="기록된 변경 이력이 없습니다" />
            ) : (
              <ol className="space-y-3 text-sm">
                {history.map((h) => (
                  <li key={h.id}>
                    <p className="text-slate-800">{h.summary}</p>
                    <p className="text-xs text-slate-500">{h.actor?.name ?? "-"} · {dateTime(h.createdAt)}</p>
                    {h.meta && typeof h.meta === "object" && "changeSummary" in h.meta && h.meta.changeSummary ? (
                      <p className="mt-1 rounded bg-slate-50 p-1.5 text-xs text-slate-600">{String(h.meta.changeSummary)}</p>
                    ) : null}
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
