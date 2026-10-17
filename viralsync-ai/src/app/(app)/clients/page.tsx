import Link from "next/link";
import { requireCtx } from "@/lib/auth/current";
import { can } from "@/lib/auth/permissions";
import { listClients } from "@/lib/services/clients";
import { dateOnly, won } from "@/lib/format";
import { pageNum, str, type SP } from "@/lib/page";
import { PageHeader, Card } from "@/components/ui/card";
import { LinkButton } from "@/components/ui/button";
import { DemoBadge } from "@/components/ui/badge";
import { EmptyState, Pagination, Table } from "@/components/ui/misc";

export const metadata = { title: "고객관리" };

export default async function ClientsPage({ searchParams }: { searchParams: Promise<SP> }) {
  const ctx = await requireCtx();
  const sp = await searchParams;
  const q = str(sp, "q");
  const sort = str(sp, "sort");
  const data = await listClients(ctx, { q, sort, page: pageNum(sp) });
  const canWrite = can(ctx.role, "client:write");
  return (
    <>
      <PageHeader
        title="고객관리"
        description={`총 ${data.total}개 고객${ctx.role === "ADMIN" ? "" : " (배정된 고객만 표시)"}`}
        actions={canWrite && <LinkButton href="/clients/new">+ 고객 등록</LinkButton>}
      />
      <form className="mb-4 flex flex-wrap gap-2" role="search">
        <label htmlFor="cq" className="sr-only">고객 검색</label>
        <input id="cq" name="q" defaultValue={q} placeholder="고객명·담당자 검색" className="input max-w-xs" />
        <label htmlFor="csort" className="sr-only">정렬</label>
        <select id="csort" name="sort" defaultValue={sort ?? ""} className="input w-auto">
          <option value="">최근 등록순</option>
          <option value="name">이름순</option>
          <option value="budget">예산 높은순</option>
        </select>
        <button className="rounded-lg border border-slate-300 bg-white px-3 text-sm hover:bg-slate-50">검색</button>
      </form>
      {data.rows.length === 0 ? (
        <EmptyState title={q ? "검색 결과가 없습니다" : "등록된 고객이 없습니다"} description="고객을 등록하면 광고 의뢰를 접수할 수 있습니다." action={canWrite && <LinkButton href="/clients/new">고객 등록</LinkButton>} />
      ) : (
        <Card>
          <Table>
            <thead className="bg-slate-50">
              <tr>
                <th className="th">고객명</th>
                <th className="th">담당자</th>
                <th className="th">담당 직원</th>
                <th className="th text-right">예산</th>
                <th className="th">계약기간</th>
                <th className="th text-right">캠페인</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {data.rows.map((c) => (
                <tr key={c.id} className="hover:bg-slate-50">
                  <td className="td">
                    <Link href={`/clients/${c.id}`} className="link">{c.name}</Link> {c.isDemo && <DemoBadge />}
                  </td>
                  <td className="td">{c.contactName}</td>
                  <td className="td">{c.manager?.name ?? "-"}</td>
                  <td className="td text-right tabular-nums">{c.piiHidden ? <span className="text-slate-400">권한 없음</span> : won(c.budget)}</td>
                  <td className="td whitespace-nowrap text-xs">{c.piiHidden ? "-" : `${dateOnly(c.contractStart)} ~ ${dateOnly(c.contractEnd)}`}</td>
                  <td className="td text-right tabular-nums">{c._count.campaigns}</td>
                </tr>
              ))}
            </tbody>
          </Table>
        </Card>
      )}
      <Pagination page={data.page} pageCount={data.pageCount} basePath="/clients" params={{ q, sort }} />
    </>
  );
}
