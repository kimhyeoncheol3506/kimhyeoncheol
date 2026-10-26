import Link from "next/link";
import type { PlatformKey } from "@prisma/client";
import { requireCtx } from "@/lib/auth/current";
import { can } from "@/lib/auth/permissions";
import { approvedNotScheduled, finalText, MAX_RETRIES, listPublications, precheck, type PublicationFilter } from "@/lib/services/publications";
import { platformStatuses } from "@/lib/services/platforms";
import { CONTENT_TYPE_LABEL, PLATFORM_LABEL, PLATFORMS, PUBLICATION_STATUS_LABEL } from "@/lib/labels";
import { dateTime, num } from "@/lib/format";
import { pageNum, str, type SP } from "@/lib/page";
import { Card, CardBody, CardHeader, PageHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { MetricSourceBadge, PublicationStatusBadge } from "@/components/ui/status";
import { Alert, EmptyState, Pagination, Table } from "@/components/ui/misc";
import { ExecuteForm, ScheduleForm } from "@/components/forms/publication-forms";

export const metadata = { title: "실행 관리" };

export default async function ExecutionsPage({ searchParams }: { searchParams: Promise<SP> }) {
  const ctx = await requireCtx();
  const sp = await searchParams;
  const statusRaw = str(sp, "status");
  const status = statusRaw && statusRaw in PUBLICATION_STATUS_LABEL ? (statusRaw as PublicationFilter["status"]) : undefined;
  const platformRaw = str(sp, "platform");
  const platform = platformRaw && (PLATFORMS as string[]).includes(platformRaw) ? (platformRaw as PlatformKey) : undefined;
  const canExec = can(ctx.role, "publication:execute");
  const [ready, pubs, statuses] = await Promise.all([
    canExec ? approvedNotScheduled(ctx) : Promise.resolve([]),
    listPublications(ctx, { status, platform, page: pageNum(sp) }),
    platformStatuses(ctx),
  ]);
  const prechecks = await Promise.all(ready.slice(0, 15).map((c) => precheck(ctx, c.id)));
  const liveOf = (p: PlatformKey) => statuses.find((s) => s.key === p)!;

  return (
    <>
      <PageHeader title="승인 및 캠페인 실행" description="승인된 문구만 실행할 수 있습니다. 기본값은 외부 SNS 에 게시하지 않는 모의 실행입니다." />
      <div className="mb-6">
        <Alert tone="info" title="모의 실행 모드">
          모의 실행은 외부 플랫폼을 호출하지 않고 성공·실패를 재현하며, 결과 실적은 ‘모의 실적’으로 기록됩니다. 실제 게시 버튼은 공식 API 설정과 계정 인증이 완료된 플랫폼에서만 나타납니다 (현재 게시 가능 플랫폼: {statuses.filter((s) => s.status === "PUBLISH_READY").length}개).
        </Alert>
      </div>

      {canExec && (
        <Card className="mb-6">
          <CardHeader title={`실행 준비 — 승인 완료 문구 (${ready.length})`} description="실행 전 미리보기와 사전검사(광고 표시·금지어·허위체험·글자 수·중복·일일 한도·정책 검토)" />
          <CardBody>
            {ready.length === 0 ? (
              <EmptyState title="실행 대기열에 올릴 승인 문구가 없습니다" description="승인 관리에서 문구를 승인하면 여기에 표시됩니다." />
            ) : (
              <div className="space-y-4">
                {ready.slice(0, 15).map((c, i) => {
                  const pc = prechecks[i];
                  const blocked = !pc.ok;
                  return (
                    <div key={c.id} className="grid gap-4 rounded-xl border border-slate-200 p-4 lg:grid-cols-2">
                      <div>
                        <p className="mb-1 text-xs text-slate-500">
                          {c.campaign.client.name} · <Link href={`/campaigns/${c.campaignId}`} className="link">{c.campaign.name}</Link> · {CONTENT_TYPE_LABEL[c.type]}
                        </p>
                        <p className="mb-1 text-xs font-semibold text-slate-600">실행 전 미리보기 ({PLATFORM_LABEL[pc.platform]}{pc.targetUrl ? " · 댓글 대상 게시물 연결" : " · 자체 게시물"})</p>
                        <pre className="max-h-48 overflow-auto whitespace-pre-wrap rounded-lg bg-slate-50 p-3 font-sans text-sm text-slate-800">{finalText(c.body, c.disclosure)}</pre>
                        {pc.targetUrl && <p className="mt-1 break-all text-xs text-slate-400">대상: {pc.targetUrl}</p>}
                      </div>
                      <div>
                        <ul className="space-y-1 text-xs" aria-label="사전검사 결과">
                          {pc.items.map((it) => (
                            <li key={it.key} className="flex gap-2">
                              <span aria-hidden>{it.passed ? "✅" : it.severity === "block" ? "⛔" : "⚠️"}</span>
                              <span>
                                <span className="font-medium">{it.label}</span> — <span className="text-slate-600">{it.detail}</span>
                              </span>
                            </li>
                          ))}
                        </ul>
                        <div className="mt-3">
                          {blocked && <p className="mb-2 text-xs font-medium text-rose-600">차단 항목이 있어 등록 시 ‘사전검사 차단’으로 기록됩니다.</p>}
                          <ScheduleForm contentId={c.id} platforms={PLATFORMS} defaultPlatform={pc.platform} />
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </CardBody>
        </Card>
      )}

      <Card>
        <CardHeader title={`실행 기록 (${pubs.total})`} />
        <CardBody>
          <form className="mb-4 flex flex-wrap gap-2">
            <select name="status" defaultValue={status ?? ""} className="input w-auto" aria-label="상태">
              <option value="">전체 상태</option>
              {Object.entries(PUBLICATION_STATUS_LABEL).map(([k, v]) => (
                <option key={k} value={k}>{v}</option>
              ))}
            </select>
            <select name="platform" defaultValue={platform ?? ""} className="input w-auto" aria-label="플랫폼">
              <option value="">전체 플랫폼</option>
              {PLATFORMS.map((p) => (
                <option key={p} value={p}>{PLATFORM_LABEL[p]}</option>
              ))}
            </select>
            <button className="rounded-lg border border-slate-300 bg-white px-3 text-sm hover:bg-slate-50">적용</button>
          </form>
          {pubs.rows.length === 0 ? (
            <EmptyState title="실행 기록이 없습니다" />
          ) : (
            <Table minWidth={1000}>
              <thead className="bg-slate-50">
                <tr>
                  <th className="th">캠페인 · 문구</th>
                  <th className="th">플랫폼</th>
                  <th className="th">상태</th>
                  <th className="th">실행</th>
                  <th className="th">실적</th>
                  <th className="th">오류 · 재시도</th>
                  {canExec && <th className="th">작업</th>}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {pubs.rows.map((p) => {
                  const m = p.metrics[0];
                  const ps = liveOf(p.platform);
                  return (
                    <tr key={p.id} className="align-top">
                      <td className="td max-w-xs">
                        <Link href={`/campaigns/${p.campaign.id}`} className="link">{p.campaign.name}</Link>
                        <p className="text-xs text-slate-500">{p.campaign.client.name} · {CONTENT_TYPE_LABEL[p.content.type]}</p>
                        <p className="mt-1 line-clamp-2 text-xs text-slate-600">{p.content.body}</p>
                      </td>
                      <td className="td">{PLATFORM_LABEL[p.platform]}</td>
                      <td className="td">
                        <PublicationStatusBadge status={p.status} />{" "}
                        {p.mode === "SIMULATED" ? <Badge tone="purple">모의</Badge> : <Badge tone="green">실제</Badge>}
                      </td>
                      <td className="td text-xs">
                        {dateTime(p.executedAt)}
                        <br />
                        {p.executedBy?.name ?? ""}
                      </td>
                      <td className="td text-xs">
                        {m ? (
                          <>
                            클릭 {num(m.clicks)} · 방문 {num(m.visits)} · 전환 {num(m.conversions)}
                            <br />
                            <MetricSourceBadge source={m.source} />
                          </>
                        ) : (
                          <span className="text-slate-400">미측정</span>
                        )}
                      </td>
                      <td className="td max-w-xs text-xs text-rose-600">
                        {p.errorCode && (
                          <>
                            <code>{p.errorCode}</code>
                            <p className="text-slate-600">{p.errorMessage}</p>
                          </>
                        )}
                        <p className="text-slate-500">재시도 {p.retryCount}회</p>
                      </td>
                      {canExec && (
                        <td className="td">
                          {p.status === "FAILED" && p.retryCount >= MAX_RETRIES ? (
                            <p className="text-xs text-rose-700">재시도 {MAX_RETRIES}회 초과 — 멈춤. 원인과 실제 게시 여부를 확인한 뒤 새로 등록하세요.</p>
                          ) : (p.status === "QUEUED" || p.status === "FAILED") && (
                            <ExecuteForm
                              id={p.id}
                              retry={p.status === "FAILED"}
                              liveAvailable={ps.status === "PUBLISH_READY"}
                              liveReason={ps.status === "DEMO_ONLY" ? "공식 API 자격증명 미설정" : ps.livePublishImplemented ? "계정 인증 미완료" : "실제 게시 연동 미구현"}
                            />
                          )}
                        </td>
                      )}
                    </tr>
                  );
                })}
              </tbody>
            </Table>
          )}
          <Pagination page={pubs.page} pageCount={pubs.pageCount} basePath="/executions" params={{ status, platform }} />
        </CardBody>
      </Card>
    </>
  );
}
