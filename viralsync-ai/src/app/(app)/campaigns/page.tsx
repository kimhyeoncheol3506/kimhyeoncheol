import Link from "next/link";
import type { CampaignStatus } from "@prisma/client";
import { requireCtx } from "@/lib/auth/current";
import { can } from "@/lib/auth/permissions";
import { listCampaigns } from "@/lib/services/campaigns";
import { listClientOptions } from "@/lib/services/clients";
import { CAMPAIGN_STATUS_LABEL, GOAL_LABEL, PLATFORM_LABEL, TARGET_TYPE_LABEL } from "@/lib/labels";
import { dateOnly, won } from "@/lib/format";
import { pageNum, str, type SP } from "@/lib/page";
import { Card, PageHeader } from "@/components/ui/card";
import { LinkButton } from "@/components/ui/button";
import { DemoBadge } from "@/components/ui/badge";
import { CampaignStatusBadge } from "@/components/ui/status";
import { EmptyState, Pagination, Table } from "@/components/ui/misc";

export const metadata = { title: "광고 의뢰·캠페인" };

export default async function CampaignsPage({ searchParams }: { searchParams: Promise<SP> }) {
  const ctx = await requireCtx();
  const sp = await searchParams;
  const q = str(sp, "q");
  const statusRaw = str(sp, "status");
  const status = statusRaw && statusRaw in CAMPAIGN_STATUS_LABEL ? (statusRaw as CampaignStatus) : undefined;
  const clientId = str(sp, "clientId");
  const [data, clients] = await Promise.all([listCampaigns(ctx, { q, status, clientId, page: pageNum(sp) }), listClientOptions(ctx)]);
  const showCost = can(ctx.role, "cost:read");
  return (
    <>
      <PageHeader
        title="광고 의뢰·캠페인"
        description={`총 ${data.total}건`}
        actions={can(ctx.role, "campaign:write") && <LinkButton href="/campaigns/new">+ 광고 의뢰 접수</LinkButton>}
      />
      <form className="mb-4 flex flex-wrap gap-2" role="search">
        <label htmlFor="q" className="sr-only">검색</label>
        <input id="q" name="q" defaultValue={q} placeholder="캠페인·고객명 검색" className="input max-w-xs" />
        <label htmlFor="status" className="sr-only">상태</label>
        <select id="status" name="status" defaultValue={status ?? ""} className="input w-auto">
          <option value="">전체 상태</option>
          {Object.entries(CAMPAIGN_STATUS_LABEL).map(([k, v]) => (
            <option key={k} value={k}>{v}</option>
          ))}
        </select>
        <label htmlFor="clientId" className="sr-only">고객</label>
        <select id="clientId" name="clientId" defaultValue={clientId ?? ""} className="input w-auto">
          <option value="">전체 고객</option>
          {clients.map((c) => (
            <option key={c.id} value={c.id}>{c.name}</option>
          ))}
        </select>
        <button className="rounded-lg border border-slate-300 bg-white px-3 text-sm hover:bg-slate-50">검색</button>
      </form>
      {data.rows.length === 0 ? (
        <EmptyState title="캠페인이 없습니다" description="광고 의뢰를 접수하면 캠페인이 생성됩니다." />
      ) : (
        <Card>
          <Table minWidth={860}>
            <thead className="bg-slate-50">
              <tr>
                <th className="th">캠페인</th>
                <th className="th">고객</th>
                <th className="th">상태</th>
                <th className="th">유형·목표</th>
                <th className="th">분류</th>
                <th className="th">희망 SNS</th>
                {showCost && <th className="th text-right">예산</th>}
                <th className="th text-right">문구/실행</th>
                <th className="th">접수일</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {data.rows.map((c) => (
                <tr key={c.id} className="hover:bg-slate-50">
                  <td className="td">
                    <Link href={`/campaigns/${c.id}`} className="link">{c.name}</Link> {c.isDemo && <DemoBadge />}
                  </td>
                  <td className="td">{c.client.name}</td>
                  <td className="td"><CampaignStatusBadge status={c.status} /></td>
                  <td className="td text-xs">{c.brief ? `${TARGET_TYPE_LABEL[c.brief.targetType]} · ${GOAL_LABEL[c.brief.goal]}` : "-"}</td>
                  <td className="td text-xs">{c.brief?.category ?? <span className="text-slate-400">미분석</span>}</td>
                  <td className="td text-xs">{c.brief?.desiredPlatforms.map((p) => PLATFORM_LABEL[p]).join(", ")}</td>
                  {showCost && <td className="td text-right tabular-nums">{won(c.budget)}</td>}
                  <td className="td text-right tabular-nums">{c._count.contents} / {c._count.publications}</td>
                  <td className="td whitespace-nowrap text-xs">{dateOnly(c.createdAt)}</td>
                </tr>
              ))}
            </tbody>
          </Table>
        </Card>
      )}
      <Pagination page={data.page} pageCount={data.pageCount} basePath="/campaigns" params={{ q, status, clientId }} />
    </>
  );
}
