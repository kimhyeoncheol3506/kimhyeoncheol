import Link from "next/link";
import type { ApprovalGate } from "@prisma/client";
import { requireCtx } from "@/lib/auth/current";
import { can } from "@/lib/auth/permissions";
import { prisma } from "@/lib/db";
import { decideBlocker, listRequests } from "@/lib/services/approvals";
import { APPROVAL_GATE_LABEL } from "@/lib/labels";
import { str, type SP } from "@/lib/page";
import { PageHeader } from "@/components/ui/card";
import { Alert, EmptyState } from "@/components/ui/misc";
import { ContentCard } from "@/components/content/content-card";
import { DecisionForm } from "@/components/content/content-actions";
import { RequestCard } from "@/components/approval/request-card";

export const metadata = { title: "결재함" };

const TABS = [
  ["mine", "내 결재 차례"],
  ["pending", "진행 중 전체"],
  ["done", "완료"],
] as const;

export default async function ApprovalsPage({ searchParams }: { searchParams: Promise<SP> }) {
  const ctx = await requireCtx();
  const sp = await searchParams;
  const tab = (TABS.find(([k]) => k === str(sp, "tab"))?.[0] ?? (can(ctx.role, "approval:decide") ? "mine" : "pending")) as (typeof TABS)[number][0];
  const gRaw = str(sp, "gate");
  const gate = gRaw && gRaw in APPROVAL_GATE_LABEL ? (gRaw as ApprovalGate) : undefined;
  const rows =
    tab === "done"
      ? (await listRequests(ctx, { gate })).filter((r) => r.status !== "PENDING").slice(0, 40)
      : await listRequests(ctx, { gate, status: "PENDING", mine: tab === "mine" });
  const mineCount = can(ctx.role, "approval:decide") ? (await listRequests(ctx, { status: "PENDING", mine: true })).length : 0;

  const contentIds = rows.filter((r) => r.gate === "CONTENT").map((r) => r.entityId);
  const contents = contentIds.length
    ? await prisma.generatedContent.findMany({
        where: { id: { in: contentIds }, organizationId: ctx.organizationId },
        include: {
          campaign: { select: { id: true, name: true, client: { select: { name: true } } } },
          candidate: { select: { title: true, platform: true, postUrl: true } },
          createdBy: { select: { name: true } },
        },
      })
    : [];
  const inquiryIds = rows.filter((r) => r.gate !== "CONTENT").map((r) => r.entityId);
  const inquiries = inquiryIds.length ? await prisma.inquiry.findMany({ where: { id: { in: inquiryIds }, organizationId: ctx.organizationId }, select: { id: true, replyDraft: true } }) : [];

  return (
    <>
      <PageHeader
        title="결재함"
        description="AI 에이전트가 만든 문구·견적·계약은 컴플라이언스 에이전트의 1차 검토 후, 결재 규칙에 정해진 순서대로 사람이 결재합니다. 요청자 본인과 같은 사람의 2단계 결재는 허용되지 않습니다."
        actions={can(ctx.role, "user:manage") && <Link href="/settings/approval-rules" className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm hover:bg-slate-50">결재 규칙 설정</Link>}
      />
      <nav aria-label="결재함 구분" className="mb-3 flex flex-wrap gap-2">
        {TABS.map(([k, label]) => (
          <Link key={k} href={`/approvals?tab=${k}${gate ? `&gate=${gate}` : ""}`} aria-current={tab === k ? "page" : undefined} className={`rounded-full px-3 py-1 text-sm ${tab === k ? "bg-brand-600 text-white" : "bg-white text-slate-600 ring-1 ring-slate-200"}`}>
            {label}
            {k === "mine" && ` ${mineCount}`}
          </Link>
        ))}
        <span className="mx-1 text-slate-300">|</span>
        {([undefined, "CONTENT", "QUOTE", "CONTRACT"] as const).map((g) => (
          <Link key={g ?? "all"} href={`/approvals?tab=${tab}${g ? `&gate=${g}` : ""}`} className={`rounded-full px-3 py-1 text-xs ${gate === g ? "bg-slate-800 text-white" : "bg-white text-slate-600 ring-1 ring-slate-200"}`}>
            {g ? APPROVAL_GATE_LABEL[g] : "전체 업무"}
          </Link>
        ))}
      </nav>
      {!can(ctx.role, "approval:decide") && (
        <div className="mb-4"><Alert tone="warn">결재 권한이 없어 조회만 가능합니다.</Alert></div>
      )}
      {rows.length === 0 ? (
        <EmptyState title={tab === "mine" ? "지금 결재할 건이 없습니다" : "해당하는 결재가 없습니다"} description="AI 에이전트가 만든 결과물이 결재 요청되면 여기에 나타납니다." />
      ) : (
        <div className="grid gap-4 lg:grid-cols-2">
          {rows.map((r) => {
            const blocker = can(ctx.role, "approval:decide") ? decideBlocker(ctx, r) : "결재 권한이 없습니다.";
            const content = contents.find((c) => c.id === r.entityId);
            const reply = inquiries.find((i) => i.id === r.entityId)?.replyDraft;
            return (
              <RequestCard
                key={r.id}
                req={r}
                blocker={blocker}
                actions={r.status === "PENDING" && !blocker ? <DecisionForm id={r.id} /> : undefined}
                preview={
                  content ? (
                    <ContentCard c={content} />
                  ) : r.gate === "QUOTE" && reply ? (
                    <details className="rounded-lg bg-slate-50 p-3 text-xs">
                      <summary className="cursor-pointer font-medium text-slate-700">고객에게 보낼 답변 보기</summary>
                      <pre className="mt-2 whitespace-pre-wrap font-sans text-slate-700">{reply}</pre>
                    </details>
                  ) : undefined
                }
              />
            );
          })}
        </div>
      )}
    </>
  );
}
