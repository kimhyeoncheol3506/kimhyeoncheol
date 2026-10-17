import { requireCtx } from "@/lib/auth/current";
import { can } from "@/lib/auth/permissions";
import { prisma } from "@/lib/db";
import { dateTime } from "@/lib/format";
import { pageNum, str, type SP } from "@/lib/page";
import { Card, PageHeader } from "@/components/ui/card";
import { EmptyState, Forbidden, Pagination, Table } from "@/components/ui/misc";

export const metadata = { title: "감사 로그" };

export default async function AuditPage({ searchParams }: { searchParams: Promise<SP> }) {
  const ctx = await requireCtx();
  if (!can(ctx.role, "audit:read")) return <Forbidden />;
  const sp = await searchParams;
  const q = str(sp, "q");
  const page = pageNum(sp);
  const where = { organizationId: ctx.organizationId, ...(q ? { OR: [{ summary: { contains: q, mode: "insensitive" as const } }, { action: { contains: q } }] } : {}) };
  const [total, rows] = await Promise.all([
    prisma.auditLog.count({ where }),
    prisma.auditLog.findMany({ where, orderBy: { createdAt: "desc" }, skip: (page - 1) * 30, take: 30, include: { actor: { select: { name: true } } } }),
  ]);
  return (
    <>
      <PageHeader title="감사 로그" description={`총 ${total}건 · 비밀값(토큰·키)은 기록하지 않습니다.`} />
      <form className="mb-4 flex gap-2" role="search">
        <input name="q" defaultValue={q} placeholder="내용·액션 검색" className="input max-w-xs" aria-label="감사 로그 검색" />
        <button className="rounded-lg border border-slate-300 bg-white px-3 text-sm">검색</button>
      </form>
      {rows.length === 0 ? <EmptyState title="기록이 없습니다" /> : (
        <Card>
          <Table>
            <thead className="bg-slate-50"><tr><th className="th">시각</th><th className="th">사용자</th><th className="th">액션</th><th className="th">내용</th></tr></thead>
            <tbody className="divide-y divide-slate-100">
              {rows.map((r) => (
                <tr key={r.id}>
                  <td className="td whitespace-nowrap text-xs">{dateTime(r.createdAt)}</td>
                  <td className="td text-xs">{r.actor?.name ?? "시스템"}</td>
                  <td className="td"><code className="text-xs">{r.action}</code></td>
                  <td className="td text-sm">{r.summary}</td>
                </tr>
              ))}
            </tbody>
          </Table>
        </Card>
      )}
      <Pagination page={page} pageCount={Math.max(1, Math.ceil(total / 30))} basePath="/audit" params={{ q }} />
    </>
  );
}
