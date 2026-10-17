import type { ContentStatus, ContentType } from "@prisma/client";
import { requireCtx } from "@/lib/auth/current";
import { can } from "@/lib/auth/permissions";
import { getProvider } from "@/lib/ai";
import { listContent } from "@/lib/services/content";
import { listCampaignOptions } from "@/lib/services/campaigns";
import { candidateOptionsFor } from "@/lib/services/candidates";
import { CONTENT_STATUS_LABEL, CONTENT_TYPE_LABEL } from "@/lib/labels";
import { pageNum, str, type SP } from "@/lib/page";
import { Card, CardBody, CardHeader, PageHeader } from "@/components/ui/card";
import { Alert, EmptyState, Pagination } from "@/components/ui/misc";
import { ContentCard } from "@/components/content/content-card";
import { EditContentForm, SubmitForReviewButton } from "@/components/content/content-actions";
import { GenerateForm } from "@/components/forms/generate-form";

export const metadata = { title: "AI 문구 생성" };

export default async function ContentPage({ searchParams }: { searchParams: Promise<SP> }) {
  const ctx = await requireCtx();
  const sp = await searchParams;
  const campaignId = str(sp, "campaignId");
  const statusRaw = str(sp, "status");
  const status = statusRaw && statusRaw in CONTENT_STATUS_LABEL ? (statusRaw as ContentStatus) : undefined;
  const typeRaw = str(sp, "type");
  const type = typeRaw && typeRaw in CONTENT_TYPE_LABEL ? (typeRaw as ContentType) : undefined;
  const q = str(sp, "q");
  const canGenerate = can(ctx.role, "content:generate");
  const canEdit = can(ctx.role, "content:edit");
  const [data, campaigns, candidates] = await Promise.all([
    listContent(ctx, { campaignId, status, type, q, page: pageNum(sp) }),
    listCampaignOptions(ctx),
    canGenerate ? candidateOptionsFor(ctx) : Promise.resolve([]),
  ]);
  const { status: ai } = getProvider();

  return (
    <>
      <PageHeader title="AI 홍보 문구 생성" description="캠페인과 홍보 대상 게시물 문맥에 맞는 문구 초안을 생성합니다. 모든 초안은 AI 생성물로 표시되며 사람의 검토·승인이 필요합니다." />
      <div className="mb-4">
        <Alert tone={ai.configured ? "success" : "info"} title={`AI Provider: ${ai.active} (${ai.model})`}>{ai.message}</Alert>
      </div>
      {canGenerate && (
        <Card className="mb-6">
          <CardHeader title="새 문구 생성" />
          <CardBody>
            <GenerateForm campaigns={campaigns} candidates={candidates} defaultCampaignId={campaignId} />
          </CardBody>
        </Card>
      )}
      <form className="mb-4 flex flex-wrap gap-2" role="search">
        <select name="campaignId" defaultValue={campaignId ?? ""} className="input w-auto" aria-label="캠페인">
          <option value="">전체 캠페인</option>
          {campaigns.map((c) => (
            <option key={c.id} value={c.id}>{c.name}</option>
          ))}
        </select>
        <select name="status" defaultValue={status ?? ""} className="input w-auto" aria-label="상태">
          <option value="">전체 상태</option>
          {Object.entries(CONTENT_STATUS_LABEL).map(([k, v]) => (
            <option key={k} value={k}>{v}</option>
          ))}
        </select>
        <select name="type" defaultValue={type ?? ""} className="input w-auto" aria-label="유형">
          <option value="">전체 유형</option>
          {Object.entries(CONTENT_TYPE_LABEL).map(([k, v]) => (
            <option key={k} value={k}>{v}</option>
          ))}
        </select>
        <input name="q" defaultValue={q} placeholder="문구 검색" className="input max-w-xs" aria-label="문구 검색" />
        <button className="rounded-lg border border-slate-300 bg-white px-3 text-sm hover:bg-slate-50">검색</button>
      </form>
      <p className="mb-3 text-sm text-slate-500">총 {data.total}건</p>
      {data.rows.length === 0 ? (
        <EmptyState title="생성된 문구가 없습니다" description="위에서 캠페인을 선택해 문구를 생성하세요." />
      ) : (
        <div className="grid gap-4 lg:grid-cols-2">
          {data.rows.map((c) => (
            <ContentCard
              key={c.id}
              c={{ ...c, revisionCount: c._count.revisions }}
              showCost={can(ctx.role, "cost:read")}
              actions={
                canEdit && c.status !== "PENDING_REVIEW" ? (
                  <>
                    {(c.status === "DRAFT" || c.status === "CHANGES_REQUESTED") && <SubmitForReviewButton ids={[c.id]} />}
                    <EditContentForm id={c.id} body={c.body} />
                  </>
                ) : undefined
              }
            />
          ))}
        </div>
      )}
      <Pagination page={data.page} pageCount={data.pageCount} basePath="/content" params={{ campaignId, status, type, q }} />
    </>
  );
}
