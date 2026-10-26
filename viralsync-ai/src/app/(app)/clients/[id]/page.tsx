import Link from "next/link";
import { requireCtx } from "@/lib/auth/current";
import { can } from "@/lib/auth/permissions";
import { getClient } from "@/lib/services/clients";
import { staffOptions } from "@/lib/services/reports";
import { listTeams } from "@/lib/services/teams";
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
import { headers } from "next/headers";
import { clientCare, listClientAssets } from "@/lib/services/portal";
import { SUBSCRIPTION_STATUS_LABEL } from "@/lib/labels";
import { Badge } from "@/components/ui/badge";
import { CopyText } from "@/components/ui/copy-text";
import { PortalLinkButton } from "@/components/portal/forms";

export default async function ClientDetailPage({ params, searchParams }: { params: Promise<{ id: string }>; searchParams: Promise<{ created?: string }> }) {
  const ctx = await requireCtx();
  const { id } = await params;
  const { created } = await searchParams;
  const c = await orNotFound(getClient(ctx, id));
  const canWrite = can(ctx.role, "client:write");
  const bp = c.brandProfile;
  const [staff, teams] = canWrite ? await Promise.all([staffOptions(ctx), listTeams(ctx)]) : [[], []];
  const [care, assets] = await Promise.all([clientCare(ctx, c.id), listClientAssets(ctx, c.id)]);
  const h = await headers();
  const base = process.env.PUBLIC_BASE_URL?.trim().replace(/\/+$/, "") || `${h.get("x-forwarded-proto") ?? "http"}://${h.get("host")}`;
  const portalUrl = canWrite && c.portalToken ? `${base}/c/${c.portalToken}` : null;
  return (
    <>
      <PageHeader
        title={c.name}
        description={
          <span className="flex items-center gap-2">
            담당자 {c.contactName} · 담당 직원 {c.manager?.name ?? "-"} {c.isDemo && <DemoBadge />}
          </span>
        }
        actions={
          <>
            <LinkButton href={`/clients/${c.id}/report`} variant="secondary">월 보고서</LinkButton>
            {can(ctx.role, "campaign:write") && <LinkButton href={`/campaigns/new?clientId=${c.id}`}>+ 광고 의뢰 접수</LinkButton>}
          </>
        }
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
                  teams={teams.map((t) => ({ id: t.id, name: t.name }))}
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
                    teamId: c.teamId,
                    industry: c.industry,
                    ownAccount: c.ownAccount,
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
            <CardHeader
              title="단골 관리"
              description={c.ownAccount ? "본인 계정 운영대행 · 게시 전 사장님 승인 필수" : "제3자 홍보 고객"}
              action={care.subscription ? <Link className="link text-xs" href={`/subscriptions/${care.subscription.id}`}>{care.subscription.planName} · {SUBSCRIPTION_STATUS_LABEL[care.subscription.status]}</Link> : can(ctx.role, "sales:manage") && <Link className="link text-xs" href={`/subscriptions/new?clientId=${c.id}`}>월 정액 계약 만들기</Link>}
            />
            <CardBody className="space-y-4 text-sm">
              {care.signals.length > 0 ? (
                <Alert tone="warn" title="이탈 경고등">{care.signals.join(" · ")}</Alert>
              ) : (
                <p className="text-xs text-emerald-700">이탈 경고 없음</p>
              )}
              <p>사장님 승인 대기 <strong>{care.pendingApprovals}</strong>건{care.oldestPendingDays > 0 && ` (가장 오래된 것 ${care.oldestPendingDays}일)`}</p>
              <div className="space-y-2 rounded-lg bg-slate-50 p-3">
                <p className="text-xs font-semibold text-slate-700">사장님 링크 (로그인 없이 승인·사진 보내기·보고서)</p>
                {portalUrl ? (
                  <>
                    <p className="break-all text-xs"><a href={portalUrl} className="link" target="_blank" rel="noreferrer">{portalUrl}</a></p>
                    <PortalLinkButton clientId={c.id} rotate label="새 링크로 바꾸기" />
                  </>
                ) : canWrite ? (
                  <PortalLinkButton clientId={c.id} label="사장님 링크 만들기" />
                ) : (
                  <p className="text-xs text-slate-500">고객 수정 권한이 있는 사람만 볼 수 있습니다.</p>
                )}
                <p className="text-[11px] text-slate-500">마지막 열람 {c.portalViewedAt ? dateOnly(c.portalViewedAt) : "-"} · 보고서 열람 {c.reportViewedAt ? dateOnly(c.reportViewedAt) : "-"}</p>
              </div>
              {care.upsell.length > 0 && (
                <div>
                  <p className="text-xs font-semibold text-slate-700">이번 달 업셀 제안 (기존 고객이 새 고객보다 5배 쉽다)</p>
                  <ul className="mt-1 list-disc pl-5 text-xs">{care.upsell.map((u) => <li key={u.name}>{u.name} — {u.price}</li>)}</ul>
                </div>
              )}
              {care.referralReady && <p className="text-xs"><Badge tone="green">소개 안내</Badge> 3개월 유지 고객 — 주변 사장님 소개 시 양쪽 한 달 5만 원 할인</p>}
              <details>
                <summary className="cursor-pointer text-xs font-medium text-brand-600">주간 카톡 초안 (월 예정표 · 금 결과)</summary>
                <div className="mt-2 space-y-3">
                  <CopyText id={`mon-${c.id}`} label="월요일 — 이번 주 업로드 예정표" text={care.monday} rows={5} />
                  <CopyText id={`fri-${c.id}`} label="금요일 — 이번 주 결과 요약" text={care.friday} rows={5} />
                  <p className="text-[11px] text-slate-500">문의는 4시간 안에 답하기 — 헤어지는 이유 1위는 ‘연락이 안 되는 것’.</p>
                </div>
              </details>
            </CardBody>
          </Card>
          {assets.length > 0 && (
            <Card>
              <CardHeader title={`사장님이 보낸 사진 (${assets.length})`} />
              <CardBody>
                <ul className="grid grid-cols-3 gap-2">
                  {assets.map((a) => (
                    <li key={a.id}>
                      <a href={`/media/${a.fileName}`} target="_blank" rel="noreferrer">
                        {/* eslint-disable-next-line @next/next/no-img-element */}
                        <img src={`/media/${a.fileName}`} alt={a.note || "사장님이 보낸 사진"} className="aspect-square w-full rounded object-cover" />
                      </a>
                      <p className="mt-0.5 truncate text-[10px] text-slate-500">{dateOnly(a.createdAt)} {a.note}</p>
                    </li>
                  ))}
                </ul>
              </CardBody>
            </Card>
          )}
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
