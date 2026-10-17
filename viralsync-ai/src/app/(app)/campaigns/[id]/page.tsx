import Link from "next/link";
import { requireCtx } from "@/lib/auth/current";
import { can } from "@/lib/auth/permissions";
import { getCampaign } from "@/lib/services/campaigns";
import type { AnalysisResult } from "@/lib/analysis/engine";
import type { UrlCheckResult } from "@/lib/validation/url";
import { GOAL_LABEL, PLATFORM_LABEL, TARGET_TYPE_LABEL } from "@/lib/labels";
import { dateOnly, dateTime, won } from "@/lib/format";
import { orNotFound } from "@/lib/page";
import { deleteCampaign } from "@/app/actions/campaigns";
import { Card, CardBody, CardHeader, PageHeader } from "@/components/ui/card";
import { Badge, DemoBadge } from "@/components/ui/badge";
import { CampaignStatusBadge, PublicationStatusBadge, ReviewBadge, ScoreBar } from "@/components/ui/status";
import { Button, LinkButton } from "@/components/ui/button";
import { Alert, EmptyState, Table } from "@/components/ui/misc";
import { StatusStepper } from "@/components/campaign/stepper";
import { AnalyzeButton } from "@/components/campaign/analyze-button";
import { AnalysisView } from "@/components/campaign/analysis-view";
import { ContentCard } from "@/components/content/content-card";
import { EditContentForm, SubmitForReviewButton } from "@/components/content/content-actions";
import { listTasks, taskProgress } from "@/lib/services/tasks";
import { staffOptions } from "@/lib/services/reports";
import { TasksTable } from "@/components/inquiry/tasks-table";

export default async function CampaignDetailPage({ params, searchParams }: { params: Promise<{ id: string }>; searchParams: Promise<{ saved?: string; converted?: string }> }) {
  const ctx = await requireCtx();
  const { id } = await params;
  const { saved, converted } = await searchParams;
  const c = await orNotFound(getCampaign(ctx, id));
  const [tasks, staff] = await Promise.all([listTasks(ctx, { campaignId: c.id }), staffOptions(ctx)]);
  const prog = taskProgress(tasks);
  const b = c.brief;
  const analysis = (b?.scores ?? null) as AnalysisResult | null;
  const urlCheck = (b?.urlCheck ?? null) as UrlCheckResult | null;
  const canEdit = can(ctx.role, "content:edit");
  const drafts = c.contents.filter((x) => x.status === "DRAFT" || x.status === "CHANGES_REQUESTED");
  const showCost = can(ctx.role, "cost:read");

  return (
    <>
      <PageHeader
        title={c.name}
        description={
          <span className="flex flex-wrap items-center gap-2">
            <Link href={`/clients/${c.clientId}`} className="link">{c.client.name}</Link>
            <CampaignStatusBadge status={c.status} />
            {c.isDemo && <DemoBadge />}
            <span className="text-xs text-slate-400">담당 {c.owner?.name ?? "-"} · 접수 {dateOnly(c.createdAt)}</span>
          </span>
        }
        actions={
          <>
            {can(ctx.role, "content:generate") && <LinkButton href={`/content?campaignId=${c.id}`} variant="secondary">문구 생성</LinkButton>}
            {can(ctx.role, "campaign:write") && <LinkButton href={`/campaigns/${c.id}/edit`} variant="secondary">의뢰 수정</LinkButton>}
          </>
        }
      />
      {saved && (
        <div className="mb-4">
          <Alert tone="success">광고 의뢰가 저장되었습니다. ‘AI 분석 실행’으로 분류와 적합도를 확인하세요.</Alert>
        </div>
      )}
      {converted && (
        <div className="mb-4">
          <Alert tone="success" title="문의가 계약 전환되었습니다">
            고객·캠페인·매체별 집행 작업이 생성되고 AI 분석이 실행되었습니다. 아래 ‘매체별 집행 작업’에서 담당자와 진행 상태를 관리하세요.
          </Alert>
        </div>
      )}
      <Card className="mb-6">
        <CardBody>
          <StatusStepper status={c.status} />
        </CardBody>
      </Card>
      {tasks.length > 0 && (
        <Card className="mb-6">
          <CardHeader title={`매체별 집행 작업 (${prog.done}/${prog.total} 완료)`} description="계약한 상품별 실제 작업 — 결과물 URL 이나 작업 내용을 기록해야 완료 처리됩니다" action={<Link href="/fulfillment" className="link text-xs">전체 작업 →</Link>} />
          <CardBody>
            <div className="mb-3 h-2 overflow-hidden rounded-full bg-slate-100" role="progressbar" aria-valuenow={prog.pct} aria-valuemin={0} aria-valuemax={100} aria-label="집행 진행률">
              <div className="h-full bg-emerald-500" style={{ width: `${prog.pct}%` }} />
            </div>
            <TasksTable tasks={tasks} staff={staff} canEdit={can(ctx.role, "task:update")} showCost={showCost} />
          </CardBody>
        </Card>
      )}

      <div className="grid gap-6 lg:grid-cols-3">
        <Card>
          <CardHeader title="의뢰 내용" />
          <CardBody>
            {!b ? (
              <EmptyState title="의뢰 정보가 없습니다" />
            ) : (
              <dl className="space-y-2 text-sm">
                <Item k="유형 · 목표" v={`${TARGET_TYPE_LABEL[b.targetType]} · ${GOAL_LABEL[b.goal]}`} />
                <Item k="핵심 타깃" v={b.coreTarget || "미입력"} />
                <Item k="희망 SNS" v={b.desiredPlatforms.map((p) => PLATFORM_LABEL[p]).join(", ")} />
                <Item k="키워드" v={b.keywords.join(", ") || "-"} />
                <Item k="금지 키워드" v={b.bannedKeywords.join(", ") || "-"} />
                {showCost && <Item k="예산" v={won(c.budget)} />}
                <Item k="기간" v={`${dateOnly(c.startDate)} ~ ${dateOnly(c.endDate)}`} />
                <div>
                  <dt className="text-xs text-slate-500">홍보 대상 URL</dt>
                  <dd className="break-all text-slate-800">{b.targetUrl ?? "-"}</dd>
                  {urlCheck && (
                    <dd className="mt-1 text-xs text-slate-500">
                      {urlCheck.valid ? "✓ 형식 확인" : "✕ 형식 오류"} · 외부 콘텐츠 자동 분석: <strong>하지 않음</strong>
                    </dd>
                  )}
                </div>
                <Item k="상세 설명" v={b.description || "미입력"} />
              </dl>
            )}
          </CardBody>
        </Card>
        <Card className="lg:col-span-2">
          <CardHeader
            title="AI 분석"
            description={b?.analyzedAt ? `분석 시각 ${dateTime(b.analyzedAt)}` : "아직 분석하지 않았습니다"}
            action={b && can(ctx.role, "analysis:run") && <AnalyzeButton id={c.id} analyzed={!!b.analyzedAt} />}
          />
          <CardBody>{analysis ? <AnalysisView result={analysis} /> : <EmptyState title="분석 결과가 없습니다" description="‘AI 분석 실행’을 누르면 대분류·소분류와 6가지 점수를 산출합니다." />}</CardBody>
        </Card>
      </div>

      <Card className="mt-6">
        <CardHeader title={`연결된 홍보 후보 (${c.candidates.length})`} action={<Link href="/opportunities" className="link text-xs">홍보 기회 탐색 →</Link>} />
        <CardBody>
          {c.candidates.length === 0 ? (
            <EmptyState title="연결된 후보가 없습니다" description="홍보 기회 탐색에서 후보 게시물을 이 캠페인에 연결하세요." />
          ) : (
            <Table>
              <thead>
                <tr>
                  <th className="th">게시물</th>
                  <th className="th">타깃 일치도</th>
                  <th className="th">관련성</th>
                  <th className="th">적합</th>
                  <th className="th">근거</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {c.candidates.map((x) => (
                  <tr key={x.id}>
                    <td className="td">
                      <Badge tone="blue">{PLATFORM_LABEL[x.platform]}</Badge> {x.title}
                      <p className="text-xs text-slate-500">{x.accountName}</p>
                    </td>
                    <td className="td"><ScoreBar value={x.targetMatch} /></td>
                    <td className="td"><ScoreBar value={x.relevanceScore} /></td>
                    <td className="td">
                      {x.suitable == null ? "-" : x.suitable ? <Badge tone="green">적합</Badge> : <Badge tone="red">부적합</Badge>} <ReviewBadge status={x.reviewStatus} />
                    </td>
                    <td className="td max-w-sm text-xs text-slate-600">{x.suitabilityNote}</td>
                  </tr>
                ))}
              </tbody>
            </Table>
          )}
        </CardBody>
      </Card>

      <Card className="mt-6">
        <CardHeader
          title={`생성된 문구 (${c.contents.length})`}
          action={canEdit && drafts.length > 0 && <SubmitForReviewButton ids={drafts.map((d) => d.id)} campaignId={c.id} label={`초안 ${drafts.length}건 검토 요청`} />}
        />
        <CardBody>
          {c.contents.length === 0 ? (
            <EmptyState title="생성된 문구가 없습니다" action={can(ctx.role, "content:generate") && <LinkButton href={`/content?campaignId=${c.id}`}>문구 생성하기</LinkButton>} />
          ) : (
            <div className="grid gap-4 lg:grid-cols-2">
              {c.contents.map((x) => (
                <ContentCard
                  key={x.id}
                  c={x}
                  showCost={showCost}
                  actions={canEdit && x.status !== "PENDING_REVIEW" ? <EditContentForm id={x.id} body={x.body} /> : undefined}
                />
              ))}
            </div>
          )}
        </CardBody>
      </Card>

      <Card className="mt-6">
        <CardHeader title={`실행 이력 (${c.publications.length})`} action={<Link href="/executions" className="link text-xs">실행 관리 →</Link>} />
        <CardBody>
          {c.publications.length === 0 ? (
            <EmptyState title="실행 이력이 없습니다" />
          ) : (
            <Table>
              <thead>
                <tr>
                  <th className="th">플랫폼</th>
                  <th className="th">모드</th>
                  <th className="th">상태</th>
                  <th className="th">실행자</th>
                  <th className="th">실행 일시</th>
                  <th className="th">오류</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {c.publications.map((p) => (
                  <tr key={p.id}>
                    <td className="td">{PLATFORM_LABEL[p.platform]}</td>
                    <td className="td">{p.mode === "SIMULATED" ? <Badge tone="purple">모의</Badge> : <Badge tone="green">실제</Badge>}</td>
                    <td className="td"><PublicationStatusBadge status={p.status} /></td>
                    <td className="td">{p.executedBy?.name ?? "-"}</td>
                    <td className="td text-xs">{dateTime(p.executedAt)}</td>
                    <td className="td text-xs text-rose-600">{p.errorCode ? `${p.errorCode} (재시도 ${p.retryCount})` : ""}</td>
                  </tr>
                ))}
              </tbody>
            </Table>
          )}
        </CardBody>
      </Card>
      {can(ctx.role, "campaign:write") && (
        <form action={deleteCampaign} className="mt-6">
          <input type="hidden" name="id" value={c.id} />
          <Button type="submit" variant="secondary" size="sm">캠페인 보관(삭제)</Button>
        </form>
      )}
    </>
  );
}

function Item({ k, v }: { k: string; v: string }) {
  return (
    <div>
      <dt className="text-xs text-slate-500">{k}</dt>
      <dd className="whitespace-pre-wrap break-words text-slate-800">{v}</dd>
    </div>
  );
}
