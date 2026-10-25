import Link from "next/link";
import { requireCtx } from "@/lib/auth/current";
import { can } from "@/lib/auth/permissions";
import { AI_AGENTS } from "@/lib/approval/agents";
import { agentActivity, listTeams, orgPeople } from "@/lib/services/teams";
import { listRules } from "@/lib/services/approvals";
import { prisma } from "@/lib/db";
import { APPROVAL_GATE_LABEL, ROLE_LABEL } from "@/lib/labels";
import { won } from "@/lib/format";
import { Card, CardBody, CardHeader, PageHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { DeleteTeamButton, TeamForm } from "@/components/forms/org-forms";

export const metadata = { title: "조직·AI 에이전트" };

export default async function OrganizationPage() {
  const ctx = await requireCtx();
  const isAdmin = can(ctx.role, "user:manage");
  const [org, teams, people, activity, rules] = await Promise.all([
    prisma.organization.findUniqueOrThrow({ where: { id: ctx.organizationId }, select: { name: true } }),
    listTeams(ctx),
    orgPeople(ctx),
    agentActivity(ctx),
    listRules(ctx),
  ]);
  const admins = people.filter((p) => p.role === "ADMIN");
  const unassigned = people.filter((p) => !p.teamId && p.role !== "ADMIN");

  return (
    <>
      <PageHeader
        title="조직·AI 에이전트"
        description="사람 조직(팀)과 AI 에이전트 조직이 함께 일합니다. AI 는 분석·초안까지만 만들고, 고객에게 나가는 견적·계약·게시물은 결재 규칙에 따라 사람이 결재합니다."
      />

      {/* 일하는 방식 */}
      <Card className="mb-6">
        <CardHeader title="일하는 흐름" />
        <CardBody>
          <ol className="flex flex-wrap items-center gap-2 text-sm" aria-label="업무 흐름">
            {["📥 문의 접수 (AI)", "🧭 매체·견적 초안 (AI)", "✍️ 문구 초안 (AI)", "🛡️ AI 1차 검토", "👤 사람 결재 (규칙별 1~4단계)", "🚀 집행 (승인된 것만)", "📈 리포트 (AI)"].map((s, i, a) => (
              <li key={s} className="flex items-center gap-2">
                <span className={`rounded-lg px-3 py-1.5 ${s.includes("사람") ? "bg-amber-100 font-semibold text-amber-900" : s.includes("1차") ? "bg-rose-50 text-rose-800" : "bg-slate-100 text-slate-700"}`}>{s}</span>
                {i < a.length - 1 && <span aria-hidden className="text-slate-300">→</span>}
              </li>
            ))}
          </ol>
        </CardBody>
      </Card>

      <div className="grid gap-6 xl:grid-cols-2">
        {/* 사람 조직 */}
        <Card>
          <CardHeader title={`사람 조직 — ${org.name}`} description="고객을 팀에 배정하면 팀원과 팀장이 그 고객을 담당합니다" action={isAdmin && <Link href="/settings/users" className="link text-xs">직원·권한 →</Link>} />
          <CardBody className="space-y-4">
            <div className="rounded-xl border border-brand-100 bg-brand-50 p-3">
              <p className="text-xs font-semibold text-brand-700">대표·관리자</p>
              <p className="text-sm">{admins.map((a) => a.name).join(", ") || "-"}</p>
              <p className="mt-1 text-xs text-slate-500">모든 고객 접근 · 모든 결재 단계 대결 가능 · 결재 규칙·가격·SNS 계정 관리</p>
            </div>
            <ul className="grid gap-3 md:grid-cols-2">
              {teams.map((t) => (
                <li key={t.id} className="rounded-xl border border-slate-200 p-3">
                  <div className="flex items-center justify-between">
                    <p className="font-semibold">{t.name}</p>
                    {isAdmin && <DeleteTeamButton id={t.id} />}
                  </div>
                  <p className="text-xs text-slate-500">{t.description || "담당 업무 미입력"}</p>
                  <p className="mt-2 text-xs">팀장: <strong>{t.lead?.name ?? "미지정"}</strong></p>
                  <p className="mt-1 text-xs text-slate-600">팀원: {t.members.map((m) => `${m.name}(${ROLE_LABEL[m.role]})`).join(", ") || "없음"}</p>
                  <p className="mt-1 text-xs text-slate-600">담당 고객: {t.clients.map((c) => c.name).join(", ") || "없음"}</p>
                  {isAdmin && (
                    <details className="mt-2">
                      <summary className="cursor-pointer text-xs text-brand-600">수정</summary>
                      <div className="mt-2"><TeamForm team={t} people={people} /></div>
                    </details>
                  )}
                </li>
              ))}
            </ul>
            {unassigned.length > 0 && <p className="text-xs text-slate-500">팀 미배정: {unassigned.map((u) => u.name).join(", ")}</p>}
            {isAdmin && (
              <div className="border-t border-slate-100 pt-3">
                <p className="mb-2 text-sm font-medium">새 팀</p>
                <TeamForm people={people} />
              </div>
            )}
          </CardBody>
        </Card>

        {/* AI 에이전트 조직 */}
        <Card>
          <CardHeader title="AI 에이전트 조직" description="각 에이전트의 임무와 권한 범위 · 최근 30일 활동 (감사 로그 기준)" />
          <CardBody>
            <ul className="grid gap-3 md:grid-cols-2">
              {AI_AGENTS.map((a) => (
                <li key={a.key} className="rounded-xl border border-slate-200 p-3">
                  <div className="flex items-center justify-between">
                    <Link href={a.href} className="font-semibold hover:underline">{a.emoji} {a.name}</Link>
                    <Badge tone="gray">30일 {activity[a.key] ?? 0}건</Badge>
                  </div>
                  <p className="mt-1 text-xs text-slate-700">{a.mission}</p>
                  <dl className="mt-2 space-y-0.5 text-[11px] text-slate-500">
                    <div><dt className="inline font-medium">입력: </dt><dd className="inline">{a.inputs}</dd></div>
                    <div><dt className="inline font-medium">결과: </dt><dd className="inline">{a.outputs}</dd></div>
                    <div><dt className="inline font-medium">권한: </dt><dd className="inline">{a.autonomy}</dd></div>
                  </dl>
                  {a.handsOffTo && <p className="mt-2"><Badge tone="amber">결재 연결: {APPROVAL_GATE_LABEL[a.handsOffTo]}</Badge></p>}
                </li>
              ))}
            </ul>
            <p className="mt-3 text-xs text-slate-400">현재 에이전트는 규칙 기반 엔진과(문구는) 데모/Anthropic Provider 로 동작합니다. 외부로 나가는 행동은 모두 결재·사전검사를 거칩니다.</p>
          </CardBody>
        </Card>
      </div>

      <Card className="mt-6">
        <CardHeader title="결재 규칙 요약" action={isAdmin && <Link href="/settings/approval-rules" className="link text-xs">결재 규칙 설정 →</Link>} />
        <CardBody>
          <ul className="space-y-1 text-sm">
            {rules.filter((r) => r.active).map((r) => (
              <li key={r.id}>
                <Badge tone="indigo">{APPROVAL_GATE_LABEL[r.gate]}</Badge> {r.name}
                <span className="text-xs text-slate-500">
                  {r.minAmount != null && ` · ${won(r.minAmount)} 이상`}
                  {r.minRisk && ` · 위험도 ${r.minRisk} 이상`} · {r.steps.length ? r.steps.map((s) => ROLE_LABEL[s]).join(" → ") : "결재 없음"}
                </span>
              </li>
            ))}
            {rules.length === 0 && <li className="text-slate-500">규칙 없음 — 홍보 문구는 기본으로 검토자 1단계 결재가 적용됩니다.</li>}
          </ul>
        </CardBody>
      </Card>
    </>
  );
}
