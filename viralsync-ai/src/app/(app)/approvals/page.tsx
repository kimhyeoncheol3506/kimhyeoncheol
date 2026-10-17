import { requireCtx } from "@/lib/auth/current";
import { can } from "@/lib/auth/permissions";
import { listContent } from "@/lib/services/content";
import { pageNum, type SP } from "@/lib/page";
import { PageHeader } from "@/components/ui/card";
import { Alert, EmptyState, Pagination } from "@/components/ui/misc";
import { ContentCard } from "@/components/content/content-card";
import { DecisionForm } from "@/components/content/content-actions";

export const metadata = { title: "승인 관리" };

export default async function ApprovalsPage({ searchParams }: { searchParams: Promise<SP> }) {
  const ctx = await requireCtx();
  const sp = await searchParams;
  const canDecide = can(ctx.role, "approval:decide");
  const data = await listContent(ctx, { status: "PENDING_REVIEW", page: pageNum(sp) });
  return (
    <>
      <PageHeader title="승인 관리" description={`검토 대기 ${data.total}건 · 승인자와 승인 시각이 기록되며, 본인이 생성 요청한 문구는 직접 승인할 수 없습니다.`} />
      {!canDecide && (
        <div className="mb-4">
          <Alert tone="warn">검토 권한이 없어 조회만 가능합니다. 승인·반려는 검토자 또는 관리자만 할 수 있습니다.</Alert>
        </div>
      )}
      {data.rows.length === 0 ? (
        <EmptyState title="검토 대기 중인 문구가 없습니다" description="콘텐츠 작성자가 ‘검토 요청’한 문구가 여기에 표시됩니다." />
      ) : (
        <div className="grid gap-4 lg:grid-cols-2">
          {data.rows.map((c) => (
            <ContentCard
              key={c.id}
              c={{ ...c, revisionCount: c._count.revisions }}
              actions={
                canDecide ? (
                  c.createdBy && c.createdById === ctx.userId ? (
                    <p className="text-xs text-amber-700">본인이 생성 요청한 문구는 다른 검토자가 승인해야 합니다.</p>
                  ) : (
                    <DecisionForm id={c.id} />
                  )
                ) : undefined
              }
            />
          ))}
        </div>
      )}
      <Pagination page={data.page} pageCount={data.pageCount} basePath="/approvals" params={{}} />
    </>
  );
}
