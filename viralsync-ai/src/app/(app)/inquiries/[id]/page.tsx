import Link from "next/link";
import { requireCtx } from "@/lib/auth/current";
import { can } from "@/lib/auth/permissions";
import { getInquiry } from "@/lib/services/inquiries";
import { BUSINESS_TYPE_LABEL, LINK_KIND_LABEL, QUESTION_LABEL } from "@/lib/inquiry/parser";
import { CHANNEL_LABEL, type TierKey } from "@/lib/inquiry/planner";
import { INQUIRY_SOURCE_LABEL } from "@/lib/labels";
import { dateTime, won } from "@/lib/format";
import { orNotFound } from "@/lib/page";
import { Card, CardBody, CardHeader, PageHeader } from "@/components/ui/card";
import { Badge, DemoBadge } from "@/components/ui/badge";
import { InquiryStatusBadge } from "@/components/ui/status";
import { Alert, Forbidden } from "@/components/ui/misc";
import { OverrideForm } from "@/components/inquiry/override-form";
import { LostForm, QuotePanel } from "@/components/inquiry/quote-panel";

export default async function InquiryDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const ctx = await requireCtx();
  if (!can(ctx.role, "inquiry:manage")) return <Forbidden />;
  const { id } = await params;
  const q = await orNotFound(getInquiry(ctx, id));
  const p = q.parsedData;
  const plan = q.planData;
  const locked = q.status === "WON" || q.status === "LOST";

  return (
    <>
      <PageHeader
        title={`${q.customerName}님 문의`}
        description={
          <span className="flex flex-wrap items-center gap-2">
            <Badge tone="teal">{INQUIRY_SOURCE_LABEL[q.source]}</Badge>
            <InquiryStatusBadge status={q.status} />
            {q.isDemo && <DemoBadge />}
            <span className="text-xs text-slate-400">접수 {dateTime(q.receivedAt)} · 담당 {q.assignee?.name ?? "-"}</span>
          </span>
        }
      />
      {q.status === "WON" && q.campaign && (
        <div className="mb-4">
          <Alert tone="success" title="계약 전환 완료">
            고객 <Link className="link" href={`/clients/${q.client?.id}`}>{q.client?.name}</Link> · 캠페인 <Link className="link" href={`/campaigns/${q.campaign.id}`}>{q.campaign.name}</Link> ({won(q.quoteTotal)}) 로 생성되었습니다. 매체별 집행 작업은 캠페인 상세에서 관리하세요.
          </Alert>
        </div>
      )}
      {q.status === "LOST" && (
        <div className="mb-4"><Alert tone="warn" title="미계약 종료">{q.lostReason ?? "사유 없음"}</Alert></div>
      )}

      <div className="grid gap-6 lg:grid-cols-5">
        <div className="space-y-6 lg:col-span-2">
          <Card>
            <CardHeader title="문의 원문" />
            <CardBody>
              <pre className="whitespace-pre-wrap break-words font-sans text-sm leading-relaxed text-slate-800">{q.rawText}</pre>
              {q.contactInfo && <p className="mt-3 text-xs text-slate-500">연락처: {q.contactInfo}</p>}
            </CardBody>
          </Card>
          {p && (
            <Card>
              <CardHeader title="자동 분석 결과" description="규칙 기반 추출 · 틀린 부분은 아래에서 수정하세요" />
              <CardBody className="space-y-3 text-sm">
                <dl className="grid grid-cols-3 gap-x-3 gap-y-2">
                  <dt className="text-slate-500">브랜드</dt>
                  <dd className="col-span-2">{p.brand ?? <span className="text-slate-400">확인 필요</span>}</dd>
                  <dt className="text-slate-500">업종</dt>
                  <dd className="col-span-2">{BUSINESS_TYPE_LABEL[p.businessType]} <span className="text-xs text-slate-400">(분류: {p.category})</span></dd>
                  <dt className="text-slate-500">링크</dt>
                  <dd className="col-span-2 space-y-0.5">
                    {p.links.length === 0 ? <span className="text-slate-400">없음</span> : p.links.map((l) => (
                      <div key={l.url} className="break-all text-xs"><Badge tone="gray">{LINK_KIND_LABEL[l.kind]}</Badge> {l.url}</div>
                    ))}
                  </dd>
                  <dt className="text-slate-500">키워드</dt>
                  <dd className="col-span-2">{p.keywords.join(", ") || <span className="text-slate-400">없음</span>}</dd>
                  <dt className="text-slate-500">요청 매체</dt>
                  <dd className="col-span-2">{p.requestedChannels.map((c) => CHANNEL_LABEL[c]).join(", ") || <span className="text-slate-400">지정 없음 (추천 필요)</span>}{p.wantsFullPackage && <Badge tone="purple">종합대행 희망</Badge>}</dd>
                  <dt className="text-slate-500">고객 질문</dt>
                  <dd className="col-span-2 flex flex-wrap gap-1">{p.questions.length ? p.questions.map((x) => <Badge key={x} tone="amber">{QUESTION_LABEL[x]}</Badge>) : <span className="text-slate-400">없음</span>}</dd>
                  <dt className="text-slate-500">예산</dt>
                  <dd className="col-span-2">{p.budgetMentionedKrw != null ? won(p.budgetMentionedKrw) : <span className="text-slate-400">미언급</span>}</dd>
                  <dt className="text-slate-500">지역</dt>
                  <dd className="col-span-2">{p.region ?? <span className="text-slate-400">미언급</span>}</dd>
                </dl>
                {p.missingInfo.length > 0 && (
                  <div className="rounded-lg bg-amber-50 p-3 text-xs text-amber-900">
                    <p className="font-semibold">고객에게 더 물어볼 것</p>
                    <ul className="mt-1 list-inside list-disc">{p.missingInfo.map((m) => <li key={m}>{m}</li>)}</ul>
                  </div>
                )}
                {p.notes.map((n) => (
                  <p key={n} className="rounded bg-sky-50 px-2 py-1 text-xs text-sky-900">ℹ {n}</p>
                ))}
                {!locked && (
                  <details className="rounded-lg border border-slate-200 p-3">
                    <summary className="cursor-pointer text-sm font-medium text-brand-600">분석 결과 수정</summary>
                    <div className="mt-3">
                      <OverrideForm id={q.id} values={{ brand: p.brand, businessType: p.businessType, keywords: p.keywords, requestedChannels: p.requestedChannels, budget: p.budgetMentionedKrw }} />
                    </div>
                  </details>
                )}
                {!locked && (
                  <div className="border-t border-slate-100 pt-3">
                    <LostForm id={q.id} />
                  </div>
                )}
              </CardBody>
            </Card>
          )}
        </div>

        <div className="space-y-6 lg:col-span-3">
          {plan && (
            <Card>
              <CardHeader title="추천 광고 매체" description="고객 요청 매체 우선 · 업종별 기본 전략 · 판매 상품이 없는 매체는 제외" />
              <CardBody>
                <ol className="space-y-2 text-sm">
                  {plan.channels.map((c, i) => (
                    <li key={c.channel} className={`flex gap-3 ${c.available ? "" : "opacity-50"}`}>
                      <span className="flex h-6 w-6 flex-none items-center justify-center rounded-full bg-slate-100 text-xs font-semibold">{i + 1}</span>
                      <div>
                        <p className="font-medium">
                          {c.label} {c.requested && <Badge tone="blue">고객 요청</Badge>} {!c.available && <Badge tone="gray">판매 상품 없음</Badge>}
                        </p>
                        <p className="text-xs text-slate-600">{c.reason}</p>
                      </div>
                    </li>
                  ))}
                </ol>
              </CardBody>
            </Card>
          )}
          {plan && p && (
            <Card>
              <CardHeader title="견적 · 답변 초안" description="견적안을 고르면 답변이 자동으로 바뀝니다 (직접 수정한 뒤에는 유지)" />
              <CardBody>
                <QuotePanel
                  id={q.id}
                  customerName={q.customerName}
                  source={q.source}
                  parsed={p}
                  plan={plan}
                  initialTier={(q.selectedTier as TierKey | null) ?? plan.recommendedTier}
                  initialReply={q.replyDraft ?? ""}
                  canConvert={can(ctx.role, "client:write") && can(ctx.role, "campaign:write")}
                  locked={locked}
                />
              </CardBody>
            </Card>
          )}
          {plan && (
            <Card>
              <CardHeader title="준수 사항 · 견적 가정" />
              <CardBody className="space-y-2 text-xs">
                <ul className="list-inside list-disc space-y-1 text-slate-700">{plan.compliance.map((c) => <li key={c}>{c}</li>)}</ul>
                <ul className="list-inside list-disc space-y-1 text-slate-500">{plan.assumptions.map((c) => <li key={c}>{c}</li>)}</ul>
              </CardBody>
            </Card>
          )}
        </div>
      </div>
    </>
  );
}
