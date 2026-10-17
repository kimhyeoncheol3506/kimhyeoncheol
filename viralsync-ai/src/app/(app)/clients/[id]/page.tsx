import Link from "next/link";
import { requireCtx } from "@/lib/auth/current";
import { can } from "@/lib/auth/permissions";
import { getClient } from "@/lib/services/clients";
import { staffOptions } from "@/lib/services/reports";
import { TARGET_TYPE_LABEL } from "@/lib/labels";
import { dateInput, dateOnly, won } from "@/lib/format";
import { orNotFound } from "@/lib/page";
import { deleteClient } from "@/app/actions/clients";
import { Card, CardBody, CardHeader, PageHeader } from "@/components/ui/card";
import { DemoBadge } from "@/components/ui/badge";
import { CampaignStatusBadge } from "@/components/ui/status";
import { LinkButton, Button } from "@/components/ui/button";
import { Alert, EmptyState } from "@/components/ui/misc";
import { ClientForm } from "@/components/forms/client-form";

export default async function ClientDetailPage({ params, searchParams }: { params: Promise<{ id: string }>; searchParams: Promise<{ created?: string }> }) {
  const ctx = await requireCtx();
  const { id } = await params;
  const { created } = await searchParams;
  const c = await orNotFound(getClient(ctx, id));
  const canWrite = can(ctx.role, "client:write");
  const bp = c.brandProfile;
  const staff = canWrite ? await staffOptions(ctx) : [];
  return (
    <>
      <PageHeader
        title={c.name}
        description={
          <span className="flex items-center gap-2">
            담당자 {c.contactName} · 담당 직원 {c.manager?.name ?? "-"} {c.isDemo && <DemoBadge />}
          </span>
        }
        actions={can(ctx.role, "campaign:write") && <LinkButton href={`/campaigns/new?clientId=${c.id}`}>+ 광고 의뢰 접수</LinkButton>}
      />
      {created && (
        <div className="mb-4">
          <Alert tone="success">고객이 등록되었습니다. 이제 광고 의뢰를 접수할 수 있습니다.</Alert>
        </div>
      )}
      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <Card>
            <CardHeader title={`고객별 캠페인 (${c.campaigns.length})`} />
            <CardBody>
              {c.campaigns.length === 0 ? (
                <EmptyState title="캠페인이 없습니다" />
              ) : (
                <ul className="divide-y divide-slate-100">
                  {c.campaigns.map((cp) => (
                    <li key={cp.id} className="flex items-center justify-between gap-2 py-2.5">
                      <div className="min-w-0">
                        <Link href={`/campaigns/${cp.id}`} className="link">{cp.name}</Link>
                        <p className="text-xs text-slate-500">
                          {cp.brief ? TARGET_TYPE_LABEL[cp.brief.targetType] : "-"} · {dateOnly(cp.createdAt)}
                        </p>
                      </div>
                      <CampaignStatusBadge status={cp.status} />
                    </li>
                  ))}
                </ul>
              )}
            </CardBody>
          </Card>
          {canWrite ? (
            <Card>
              <CardHeader title="고객 정보 수정" />
              <CardBody>
                <ClientForm
                  managers={staff}
                  values={{
                    id: c.id,
                    name: c.name,
                    contactName: c.contactName,
                    contactEmail: c.contactEmail,
                    contactPhone: c.contactPhone,
                    promoUrl: c.promoUrl,
                    budget: c.budget,
                    contractStart: dateInput(c.contractStart),
                    contractEnd: dateInput(c.contractEnd),
                    managerId: c.managerId,
                    companyIntro: bp?.companyIntro,
                    productDescription: bp?.productDescription,
                    coreTarget: bp?.coreTarget,
                    bannedPhrases: bp?.bannedPhrases,
                    requiredPhrases: bp?.requiredPhrases,
                    toneOfVoice: bp?.toneOfVoice,
                  }}
                />
              </CardBody>
            </Card>
          ) : null}
        </div>
        <div className="space-y-6">
          <Card>
            <CardHeader title="계약 정보" />
            <CardBody>
              {c.piiHidden ? (
                <Alert tone="warn">연락처·예산·계약 정보 열람 권한이 없습니다.</Alert>
              ) : (
                <dl className="space-y-2 text-sm">
                  <Row k="이메일" v={c.contactEmail ?? "-"} />
                  <Row k="연락처" v={c.contactPhone ?? "-"} />
                  <Row k="예산" v={won(c.budget)} />
                  <Row k="계약기간" v={`${dateOnly(c.contractStart)} ~ ${dateOnly(c.contractEnd)}`} />
                  <Row k="홍보 URL" v={c.promoUrl ?? "-"} />
                </dl>
              )}
            </CardBody>
          </Card>
          <Card>
            <CardHeader title="브랜드 프로필" />
            <CardBody>
              <dl className="space-y-2 text-sm">
                <Row k="소개" v={bp?.companyIntro || "-"} />
                <Row k="상품 설명" v={bp?.productDescription || "-"} />
                <Row k="핵심 타깃" v={bp?.coreTarget || "-"} />
                <Row k="문체" v={bp?.toneOfVoice || "-"} />
                <Row k="금지 표현" v={bp?.bannedPhrases.join(", ") || "-"} />
                <Row k="필수 표현" v={bp?.requiredPhrases.join(", ") || "-"} />
              </dl>
            </CardBody>
          </Card>
          {canWrite && (
            <form action={deleteClient}>
              <input type="hidden" name="id" value={c.id} />
              <Button variant="secondary" size="sm" type="submit">고객 보관(삭제)</Button>
              <p className="mt-1 text-xs text-slate-500">삭제 시 목록에서 숨겨지며 기록은 보존됩니다.</p>
            </form>
          )}
        </div>
      </div>
    </>
  );
}

function Row({ k, v }: { k: string; v: string }) {
  return (
    <div>
      <dt className="text-xs text-slate-500">{k}</dt>
      <dd className="break-words text-slate-800">{v}</dd>
    </div>
  );
}
