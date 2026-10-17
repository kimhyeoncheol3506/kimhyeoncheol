import type { PlatformKey, ReviewStatus } from "@prisma/client";
import { requireCtx } from "@/lib/auth/current";
import { can } from "@/lib/auth/permissions";
import { listCandidates, scoreCandidatesFor } from "@/lib/services/candidates";
import { listCampaignOptions } from "@/lib/services/campaigns";
import { PLATFORM_LABEL, PLATFORMS, REVIEW_STATUS_LABEL } from "@/lib/labels";
import { dateTime } from "@/lib/format";
import { pageNum, str, type SP } from "@/lib/page";
import { Card, CardBody, CardHeader, PageHeader } from "@/components/ui/card";
import { Badge, DemoBadge } from "@/components/ui/badge";
import { ReviewBadge, ScoreBar } from "@/components/ui/status";
import { Alert, EmptyState, Pagination, Table } from "@/components/ui/misc";
import { CandidateCreateForm, LinkCandidateButton, ReviewSelect } from "@/components/forms/candidate-forms";

export const metadata = { title: "홍보 기회 탐색" };

export default async function OpportunitiesPage({ searchParams }: { searchParams: Promise<SP> }) {
  const ctx = await requireCtx();
  const sp = await searchParams;
  const q = str(sp, "q");
  const platformRaw = str(sp, "platform");
  const platform = platformRaw && (PLATFORMS as string[]).includes(platformRaw) ? (platformRaw as PlatformKey) : undefined;
  const reviewRaw = str(sp, "review");
  const review = reviewRaw && reviewRaw in REVIEW_STATUS_LABEL ? (reviewRaw as ReviewStatus) : undefined;
  const sort = str(sp, "sort") === "relevance" ? "relevance" : "recent";
  const campaignId = str(sp, "campaignId");
  const [data, campaigns] = await Promise.all([listCandidates(ctx, { q, platform, review, sort, page: pageNum(sp) }), listCampaignOptions(ctx)]);
  const selected = campaigns.find((c) => c.id === campaignId);
  let live: Awaited<ReturnType<typeof scoreCandidatesFor>> = {};
  let scoreError: string | null = null;
  if (selected) {
    try {
      live = await scoreCandidatesFor(ctx, selected.id, data.rows.map((r) => r.id));
    } catch (e) {
      scoreError = e instanceof Error ? e.message : "점수 계산 실패";
    }
  }
  const canWrite = can(ctx.role, "candidate:write");

  return (
    <>
      <PageHeader
        title="홍보 기회 탐색"
        description="인플루언서·공개 SNS 게시물 후보를 등록하고 캠페인 적합도를 평가합니다. 게시물 자동 수집은 하지 않으며, 허용된 API·라이선스 데이터 또는 직접 입력한 정보만 사용합니다."
      />
      <form className="mb-4 grid gap-2 rounded-xl border border-slate-200 bg-white p-3 shadow-sm sm:grid-cols-2 lg:grid-cols-6" role="search">
        <div className="lg:col-span-2">
          <label htmlFor="op-campaign" className="label">평가 기준 캠페인</label>
          <select id="op-campaign" name="campaignId" defaultValue={campaignId ?? ""} className="input">
            <option value="">캠페인 선택 (실시간 점수 계산)</option>
            {campaigns.map((c) => (
              <option key={c.id} value={c.id}>{c.client.name} — {c.name}</option>
            ))}
          </select>
        </div>
        <div>
          <label htmlFor="op-q" className="label">검색</label>
          <input id="op-q" name="q" defaultValue={q} placeholder="제목·계정·요약" className="input" />
        </div>
        <div>
          <label htmlFor="op-platform" className="label">플랫폼</label>
          <select id="op-platform" name="platform" defaultValue={platform ?? ""} className="input">
            <option value="">전체</option>
            {PLATFORMS.map((p) => (
              <option key={p} value={p}>{PLATFORM_LABEL[p]}</option>
            ))}
          </select>
        </div>
        <div>
          <label htmlFor="op-review" className="label">검토 상태</label>
          <select id="op-review" name="review" defaultValue={review ?? ""} className="input">
            <option value="">전체</option>
            {Object.entries(REVIEW_STATUS_LABEL).map(([k, v]) => (
              <option key={k} value={k}>{v}</option>
            ))}
          </select>
        </div>
        <div className="flex items-end gap-2">
          <select name="sort" defaultValue={sort} className="input" aria-label="정렬">
            <option value="recent">최근 등록순</option>
            <option value="relevance">저장된 관련성순</option>
          </select>
          <button className="rounded-lg bg-brand-600 px-3 py-2 text-sm font-medium text-white">적용</button>
        </div>
      </form>
      {scoreError && <div className="mb-4"><Alert tone="error">{scoreError}</Alert></div>}
      {selected && !scoreError && (
        <div className="mb-4">
          <Alert tone="info">
            ‘{selected.name}’ 기준 점수를 실시간 계산했습니다. ‘캠페인에 연결’을 누르면 점수·근거가 저장됩니다.
          </Alert>
        </div>
      )}

      {data.rows.length === 0 ? (
        <EmptyState title="후보 게시물이 없습니다" description="아래에서 후보를 직접 등록하세요." />
      ) : (
        <Card>
          <Table minWidth={1000}>
            <thead className="bg-slate-50">
              <tr>
                <th className="th">게시물</th>
                <th className="th">분류</th>
                <th className="th">타깃 일치도</th>
                <th className="th">관련성</th>
                <th className="th">적합 여부 · 근거</th>
                <th className="th">검토</th>
                <th className="th">마지막 확인</th>
                {selected && canWrite && <th className="th">연결</th>}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {data.rows.map((r) => {
                const s = live[r.id];
                const target = s?.targetMatch ?? r.targetMatch;
                const rel = s?.relevanceScore ?? r.relevanceScore;
                const suitable = s ? s.suitable : r.suitable;
                const note = s?.note ?? r.suitabilityNote;
                return (
                  <tr key={r.id} className="align-top hover:bg-slate-50">
                    <td className="td max-w-xs">
                      <div className="flex flex-wrap items-center gap-1">
                        <Badge tone="blue">{PLATFORM_LABEL[r.platform]}</Badge>
                        {r.isDemo && <DemoBadge />}
                      </div>
                      <p className="mt-1 font-medium text-slate-800">{r.title}</p>
                      <p className="text-xs text-slate-500">{r.accountName}</p>
                      <p className="mt-1 text-xs text-slate-600">{r.summary}</p>
                      <p className="mt-1 break-all text-xs text-slate-400">{r.postUrl}</p>
                      {r.campaign && <p className="mt-1 text-xs">연결: <a className="link" href={`/campaigns/${r.campaign.id}`}>{r.campaign.name}</a></p>}
                    </td>
                    <td className="td text-xs">{r.category ?? "-"}</td>
                    <td className="td">{target == null ? <span className="text-xs text-slate-400">캠페인 선택 필요</span> : <ScoreBar value={target} />}</td>
                    <td className="td">{rel == null ? <span className="text-xs text-slate-400">캠페인 선택 필요</span> : <ScoreBar value={rel} />}</td>
                    <td className="td max-w-xs text-xs">
                      {suitable == null ? <span className="text-slate-400">미평가</span> : suitable ? <Badge tone="green">적합</Badge> : <Badge tone="red">부적합</Badge>}
                      {note && <p className="mt-1 text-slate-600">{note}</p>}
                      {s && <p className="mt-1 text-slate-400">(실시간 계산 · 미저장)</p>}
                    </td>
                    <td className="td">{canWrite ? <ReviewSelect candidateId={r.id} value={r.reviewStatus} /> : <ReviewBadge status={r.reviewStatus} />}</td>
                    <td className="td whitespace-nowrap text-xs">{dateTime(r.lastCheckedAt)}</td>
                    {selected && canWrite && (
                      <td className="td">
                        <LinkCandidateButton candidateId={r.id} campaignId={selected.id} linked={r.campaign?.id === selected.id} />
                      </td>
                    )}
                  </tr>
                );
              })}
            </tbody>
          </Table>
        </Card>
      )}
      <Pagination page={data.page} pageCount={data.pageCount} basePath="/opportunities" params={{ q, platform, review, sort, campaignId }} />
      {canWrite && (
        <Card className="mt-6">
          <CardHeader title="후보 게시물 직접 등록" description="공개 게시물 정보를 확인한 뒤 입력하세요. 분류는 제목·요약으로 자동 산출됩니다." />
          <CardBody>
            <CandidateCreateForm />
          </CardBody>
        </Card>
      )}
    </>
  );
}
