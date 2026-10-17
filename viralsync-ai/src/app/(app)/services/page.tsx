import { requireCtx } from "@/lib/auth/current";
import { can } from "@/lib/auth/permissions";
import { listPackages } from "@/lib/services/packages";
import { CHANNEL_LABEL } from "@/lib/inquiry/planner";
import { won } from "@/lib/format";
import { Card, CardBody, CardHeader, PageHeader } from "@/components/ui/card";
import { Badge, DemoBadge } from "@/components/ui/badge";
import { EmptyState, Forbidden } from "@/components/ui/misc";
import { PackageForm } from "@/components/forms/package-form";

export const metadata = { title: "서비스 상품" };

export default async function ServicesPage() {
  const ctx = await requireCtx();
  if (!can(ctx.role, "inquiry:manage") && !can(ctx.role, "service:manage")) return <Forbidden />;
  const rows = await listPackages(ctx);
  const canEdit = can(ctx.role, "service:manage");
  return (
    <>
      <PageHeader title="서비스 상품 · 가격표" description="문의 견적은 여기 등록된 판매 중 상품과 단가로 계산됩니다. 판매하지 않는 매체는 견적에서 자동 제외됩니다." />
      {canEdit && (
        <Card className="mb-6">
          <CardHeader title="새 상품 등록" />
          <CardBody><PackageForm /></CardBody>
        </Card>
      )}
      {rows.length === 0 ? (
        <EmptyState title="등록된 상품이 없습니다" description="상품을 등록해야 견적을 만들 수 있습니다." />
      ) : (
        <div className="space-y-3">
          {rows.map((p) => (
            <Card key={p.id} className={p.active ? "" : "opacity-60"}>
              <CardBody>
                <div className="mb-2 flex flex-wrap items-center gap-2">
                  <Badge tone="indigo">{CHANNEL_LABEL[p.channel]}</Badge>
                  <span className="font-semibold">{p.name}</span>
                  <span className="tabular-nums text-slate-700">{won(p.unitPrice)}/{p.unit}</span>
                  {p.mediaSpendSeparate && <Badge tone="amber">매체비 별도</Badge>}
                  {!p.active && <Badge tone="gray">판매 중지</Badge>}
                  {p.isDemo && <DemoBadge />}
                </div>
                {canEdit ? (
                  <details>
                    <summary className="cursor-pointer text-xs text-brand-600">수정</summary>
                    <div className="mt-3"><PackageForm values={p} /></div>
                  </details>
                ) : (
                  <p className="text-xs text-slate-600">{p.description} {p.deliverables.length > 0 && `· 제공: ${p.deliverables.join(", ")}`}</p>
                )}
              </CardBody>
            </Card>
          ))}
        </div>
      )}
    </>
  );
}
