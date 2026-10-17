import Link from "next/link";
import type { InquiryStatus } from "@prisma/client";
import { requireCtx } from "@/lib/auth/current";
import { can } from "@/lib/auth/permissions";
import { listInquiries } from "@/lib/services/inquiries";
import type { ParsedInquiry } from "@/lib/inquiry/parser";
import { BUSINESS_TYPE_LABEL } from "@/lib/inquiry/parser";
import { INQUIRY_SOURCE_LABEL, INQUIRY_STATUS_LABEL } from "@/lib/labels";
import { dateTime, won } from "@/lib/format";
import { pageNum, str, type SP } from "@/lib/page";
import { Card, PageHeader } from "@/components/ui/card";
import { LinkButton } from "@/components/ui/button";
import { Badge, DemoBadge } from "@/components/ui/badge";
import { InquiryStatusBadge } from "@/components/ui/status";
import { EmptyState, Forbidden, Pagination, Table } from "@/components/ui/misc";

export const metadata = { title: "문의 접수함" };

export default async function InquiriesPage({ searchParams }: { searchParams: Promise<SP> }) {
  const ctx = await requireCtx();
  if (!can(ctx.role, "inquiry:manage")) return <Forbidden />;
  const sp = await searchParams;
  const q = str(sp, "q");
  const sRaw = str(sp, "status");
  const status = sRaw && sRaw in INQUIRY_STATUS_LABEL ? (sRaw as InquiryStatus) : undefined;
  const data = await listInquiries(ctx, { q, status, page: pageNum(sp) });
  const tabs: [InquiryStatus | undefined, string][] = [[undefined, "전체"], ...(Object.entries(INQUIRY_STATUS_LABEL) as [InquiryStatus, string][])];
  return (
    <>
      <PageHeader
        title="문의 접수함"
        description="크몽 등에서 받은 광고 문의를 붙여넣으면 업종·요청 매체·질문을 분석해 추천 매체, 3안 견적, 답변 초안을 만들어 줍니다."
        actions={<LinkButton href="/inquiries/new">+ 문의 붙여넣기</LinkButton>}
      />
      <nav aria-label="상태별" className="mb-4 flex flex-wrap gap-2">
        {tabs.map(([k, label]) => {
          const n = k ? (data.byStatus[k] ?? 0) : Object.values(data.byStatus).reduce((a, b) => a + (b ?? 0), 0);
          const active = k === status;
          return (
            <Link key={label} href={k ? `/inquiries?status=${k}` : "/inquiries"} aria-current={active ? "page" : undefined} className={`rounded-full px-3 py-1 text-sm ${active ? "bg-brand-600 text-white" : "bg-white text-slate-600 ring-1 ring-slate-200 hover:bg-slate-50"}`}>
              {label} {n}
            </Link>
          );
        })}
      </nav>
      <form className="mb-4 flex gap-2" role="search">
        {status && <input type="hidden" name="status" value={status} />}
        <input name="q" defaultValue={q} placeholder="고객·문의 내용 검색" className="input max-w-xs" aria-label="문의 검색" />
        <button className="rounded-lg border border-slate-300 bg-white px-3 text-sm">검색</button>
      </form>
      {data.rows.length === 0 ? (
        <EmptyState title="문의가 없습니다" description="고객 메시지를 붙여넣어 첫 문의를 등록하세요." action={<LinkButton href="/inquiries/new">문의 붙여넣기</LinkButton>} />
      ) : (
        <Card>
          <Table minWidth={860}>
            <thead className="bg-slate-50">
              <tr>
                <th className="th">고객</th>
                <th className="th">경로</th>
                <th className="th">업종 · 브랜드</th>
                <th className="th">문의 요약</th>
                <th className="th">상태</th>
                <th className="th text-right">견적</th>
                <th className="th">접수</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {data.rows.map((r) => {
                const p = r.parsed as unknown as ParsedInquiry | null;
                return (
                  <tr key={r.id} className="hover:bg-slate-50">
                    <td className="td">
                      <Link href={`/inquiries/${r.id}`} className="link">{r.customerName}</Link> {r.isDemo && <DemoBadge />}
                    </td>
                    <td className="td"><Badge tone="teal">{INQUIRY_SOURCE_LABEL[r.source]}</Badge></td>
                    <td className="td text-xs">{p ? `${BUSINESS_TYPE_LABEL[p.businessType]}${p.brand ? ` · ${p.brand}` : ""}` : "-"}</td>
                    <td className="td max-w-xs text-xs text-slate-600"><span className="line-clamp-2">{r.rawText}</span></td>
                    <td className="td"><InquiryStatusBadge status={r.status} /></td>
                    <td className="td text-right tabular-nums">{r.quoteTotal != null ? won(r.quoteTotal) : "-"}</td>
                    <td className="td whitespace-nowrap text-xs">{dateTime(r.receivedAt)}</td>
                  </tr>
                );
              })}
            </tbody>
          </Table>
        </Card>
      )}
      <Pagination page={data.page} pageCount={data.pageCount} basePath="/inquiries" params={{ q, status }} />
    </>
  );
}
