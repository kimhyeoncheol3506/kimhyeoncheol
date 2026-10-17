import Link from "next/link";
import { requireCtx } from "@/lib/auth/current";
import { listClients } from "@/lib/services/clients";
import { listCampaigns } from "@/lib/services/campaigns";
import { listCandidates } from "@/lib/services/candidates";
import { listContent } from "@/lib/services/content";
import { CONTENT_TYPE_LABEL, PLATFORM_LABEL } from "@/lib/labels";
import { str, type SP } from "@/lib/page";
import { Card, CardBody, CardHeader, PageHeader } from "@/components/ui/card";
import { CampaignStatusBadge, ContentStatusBadge } from "@/components/ui/status";
import { EmptyState } from "@/components/ui/misc";

export const metadata = { title: "검색" };

export default async function SearchPage({ searchParams }: { searchParams: Promise<SP> }) {
  const ctx = await requireCtx();
  const q = str(await searchParams, "q");
  if (!q) return <EmptyState title="검색어를 입력하세요" />;
  const [clients, campaigns, cands, contents] = await Promise.all([
    listClients(ctx, { q }),
    listCampaigns(ctx, { q }),
    listCandidates(ctx, { q }),
    listContent(ctx, { q }),
  ]);
  const total = clients.total + campaigns.total + cands.total + contents.total;
  return (
    <>
      <PageHeader title={`‘${q}’ 검색 결과`} description={`${total}건 (접근 권한 범위 내)`} />
      {total === 0 && <EmptyState title="검색 결과가 없습니다" />}
      <div className="grid gap-6 lg:grid-cols-2">
        {clients.total > 0 && (
          <Card><CardHeader title={`고객 (${clients.total})`} /><CardBody><ul className="space-y-1 text-sm">{clients.rows.map((c) => <li key={c.id}><Link className="link" href={`/clients/${c.id}`}>{c.name}</Link></li>)}</ul></CardBody></Card>
        )}
        {campaigns.total > 0 && (
          <Card><CardHeader title={`캠페인 (${campaigns.total})`} /><CardBody><ul className="space-y-1.5 text-sm">{campaigns.rows.map((c) => <li key={c.id} className="flex items-center gap-2"><Link className="link" href={`/campaigns/${c.id}`}>{c.name}</Link><CampaignStatusBadge status={c.status} /></li>)}</ul></CardBody></Card>
        )}
        {cands.total > 0 && (
          <Card><CardHeader title={`홍보 후보 (${cands.total})`} /><CardBody><ul className="space-y-1 text-sm">{cands.rows.map((c) => <li key={c.id}>[{PLATFORM_LABEL[c.platform]}] {c.title}</li>)}</ul><Link href={`/opportunities?q=${encodeURIComponent(q)}`} className="link mt-2 inline-block text-xs">홍보 기회 탐색에서 보기 →</Link></CardBody></Card>
        )}
        {contents.total > 0 && (
          <Card><CardHeader title={`문구 (${contents.total})`} /><CardBody><ul className="space-y-2 text-sm">{contents.rows.map((c) => <li key={c.id}><span className="flex items-center gap-2"><span className="text-xs text-slate-500">{CONTENT_TYPE_LABEL[c.type]}</span><ContentStatusBadge status={c.status} /></span><p className="line-clamp-2 text-slate-700">{c.body}</p></li>)}</ul><Link href={`/content?q=${encodeURIComponent(q)}`} className="link mt-2 inline-block text-xs">문구 목록에서 보기 →</Link></CardBody></Card>
        )}
      </div>
    </>
  );
}
