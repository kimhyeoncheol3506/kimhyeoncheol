import Link from "next/link";
import { notFound } from "next/navigation";
import { requireCtx } from "@/lib/auth/current";
import { can } from "@/lib/auth/permissions";
import { staffByKey, staffLabel } from "@/lib/company/staff";
import { staffFilePath } from "@/lib/company/staff-doc";
import { prisma } from "@/lib/db";
import { APPROVAL_GATE_LABEL } from "@/lib/labels";
import { dateTime } from "@/lib/format";
import { Card, CardBody, CardHeader, PageHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { EmptyState } from "@/components/ui/misc";
import { LinkButton } from "@/components/ui/button";

export async function generateMetadata({ params }: { params: Promise<{ key: string }> }) {
  const s = staffByKey((await params).key);
  return { title: s ? `${s.name} ${s.title}` : "AI 직원" };
}

export default async function StaffPage({ params }: { params: Promise<{ key: string }> }) {
  const ctx = await requireCtx();
  const s = staffByKey((await params).key);
  if (!s) notFound();
  const showLog = can(ctx.role, "audit:read");
  const logs = showLog
    ? await prisma.auditLog.findMany({
        where: { organizationId: ctx.organizationId, action: { in: s.auditActions } },
        orderBy: { createdAt: "desc" },
        take: 15,
        include: { actor: { select: { name: true } } },
      })
    : [];

  const sections: [string, React.ReactNode][] = [
    ["목적", s.purpose],
    ["할 일", <ul key="d" className="list-disc pl-5">{s.does.map((x) => <li key={x}>{x}</li>)}</ul>],
    ["안 할 일", <ul key="n" className="list-disc pl-5 text-rose-800">{s.doesNot.map((x) => <li key={x}>{x}</li>)}</ul>],
    ["도구", s.tools.join(", ")],
    ["입력", s.input],
    ["처리 순서", <ol key="s" className="list-decimal pl-5">{s.steps.map((x) => <li key={x}>{x}</li>)}</ol>],
    ["출력", s.output],
    ["완료 기준", s.doneWhen],
    ["다음 담당", s.next === "captain" ? staffLabel(s.next) : s.next ? <Link key="x" className="link" href={`/organization/staff/${s.next}`}>{staffLabel(s.next)}</Link> : "-"],
    ["결재", s.approval],
    ["실패 대응", s.onFailure],
    ["수정 담당", `이 직원만 고치는 결과물: ${s.owns}`],
  ];

  return (
    <>
      <PageHeader
        title={`${s.emoji} ${s.name} — ${s.title}`}
        description={<span>{s.personality} <Link href="/organization" className="link ml-2 text-xs">← 조직도</Link></span>}
        actions={<LinkButton href={s.href} variant="secondary">일하는 화면 열기</LinkButton>}
      />
      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader title="업무 지시서" description={<>Claude Code 회사 폴더의 <code className="text-xs">광고홍보AI_회사/{staffFilePath(s)}</code> 와 같은 내용입니다</>} action={s.handsOffTo && <Badge tone="amber">결재 연결: {APPROVAL_GATE_LABEL[s.handsOffTo]}</Badge>} />
          <CardBody>
            <dl className="divide-y divide-slate-100 text-sm">
              {sections.map(([k, v]) => (
                <div key={k} className="grid gap-1 py-2 sm:grid-cols-[7rem_1fr]">
                  <dt className="font-medium text-slate-500">{k}</dt>
                  <dd className="text-slate-800">{v}</dd>
                </div>
              ))}
            </dl>
          </CardBody>
        </Card>
        <Card>
          <CardHeader title="최근 일한 기록" description="감사 로그 기준 최근 15건" />
          <CardBody>
            {!showLog ? (
              <p className="text-sm text-slate-500">감사 로그 열람 권한이 있는 사람만 볼 수 있습니다.</p>
            ) : logs.length === 0 ? (
              <EmptyState title="아직 기록이 없습니다" />
            ) : (
              <ul className="space-y-2 text-sm">
                {logs.map((l) => (
                  <li key={l.id} className="border-b border-slate-100 pb-2 last:border-0">
                    <p className="text-slate-800">{l.summary}</p>
                    <p className="text-xs text-slate-400">{dateTime(l.createdAt)} · 실행 {l.actor?.name ?? "시스템"}</p>
                  </li>
                ))}
              </ul>
            )}
          </CardBody>
        </Card>
      </div>
    </>
  );
}
