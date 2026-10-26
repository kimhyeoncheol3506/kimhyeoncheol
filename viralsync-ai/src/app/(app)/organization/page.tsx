import Link from "next/link";
import { requireCtx } from "@/lib/auth/current";
import { can } from "@/lib/auth/permissions";
import { AI_STAFF, APPROVAL_TARGETS, CAPTAIN, FORBIDDEN_LINES, staffLabel } from "@/lib/company/staff";
import { agentActivity, listTeams, orgPeople } from "@/lib/services/teams";
import { listRules } from "@/lib/services/approvals";
import { aiBudgetStatus } from "@/lib/services/budget";
import { MAX_RETRIES } from "@/lib/services/publications";
import { prisma } from "@/lib/db";
import { APPROVAL_GATE_LABEL, ROLE_LABEL } from "@/lib/labels";
import { won } from "@/lib/format";
import { Card, CardBody, CardHeader, PageHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { BudgetForm, DeleteTeamButton, TeamForm } from "@/components/forms/org-forms";

export const metadata = { title: "AI 회사 조직도" };

const FLOW: [string, string][] = [
  ["sales", "영업"],
  ["intake", "의뢰 접수"],
  ["strategist", "기획·견적"],
  ["copywriter", "문구"],
  ["shortform", "숏폼 대본"],
  ["compliance", "AI 1차 검토"],
  ["captain", "결재"],
  ["publisher", "집행"],
  ["analyst", "성과"],
  ["success", "단골 관리"],
  ["finance", "청구·재무"],
  ["secretary", "5줄 보고"],
];

export default async function OrganizationPage() {
  const ctx = await requireCtx();
  const isAdmin = can(ctx.role, "user:manage");
  const [org, teams, people, activity, rules, budget] = await Promise.all([
    prisma.organization.findUniqueOrThrow({ where: { id: ctx.organizationId }, select: { name: true } }),
    listTeams(ctx),
    orgPeople(ctx),
    agentActivity(ctx),
    listRules(ctx),
    can(ctx.role, "cost:read") ? aiBudgetStatus(ctx) : Promise.resolve(null),
  ]);
  const admins = people.filter((p) => p.role === "ADMIN");
  const unassigned = people.filter((p) => !p.teamId && p.role !== "ADMIN");
  const [secretary, ...staff] = AI_STAFF;

  return (
    <>
      <PageHeader
        title="AI 회사 조직도"
        description="AI 를 한 사람의 직원으로 보고 꾸린 광고홍보 회사입니다. 용역 의뢰를 받으면 비서가 직원에게 배정하고, 직원은 지시서대로 초안까지 만들고, 외부로 나가는 일은 캡틴이 결재합니다."
      />

      <Card className="mb-6">
        <CardHeader title="일하는 흐름" description="영업 → 용역 의뢰 → 매체별(쓰레드·릴스·유튜브·페이스북·틱톡) 홍보 → 사장님 승인 → 결과 보고 → 단골 유지" />
        <CardBody>
          <ol className="flex flex-wrap items-center gap-2 text-sm" aria-label="업무 흐름">
            {FLOW.map(([k, label], i) => (
              <li key={k} className="flex items-center gap-2">
                <span className={`rounded-lg px-3 py-1.5 ${k === "captain" ? "bg-amber-100 font-semibold text-amber-900" : k === "compliance" ? "bg-rose-50 text-rose-800" : "bg-slate-100 text-slate-700"}`}>
                  {staffLabel(k).split(" ").slice(0, 2).join(" ")} · {label}
                </span>
                {i < FLOW.length - 1 && <span aria-hidden className="text-slate-300">→</span>}
              </li>
            ))}
          </ol>
          <p className="mt-3 text-xs text-slate-500">한 AI 가 역할을 순서대로 맡는 구성입니다. 직원 수가 계정 수나 동시 실행 수를 뜻하지 않습니다.</p>
        </CardBody>
      </Card>

      {/* 조직도 */}
      <Card className="mb-6">
        <CardHeader title="조직도" description="직원을 누르면 업무 지시서 전문과 최근 일한 기록을 볼 수 있습니다 · 활동은 최근 30일 감사 로그 기준" />
        <CardBody className="space-y-4">
          <div className="mx-auto max-w-xl rounded-xl border border-amber-200 bg-amber-50 p-3 text-center">
            <p className="text-sm font-semibold text-amber-900">{CAPTAIN.emoji} {CAPTAIN.name} — {CAPTAIN.title}</p>
            <p className="text-xs text-amber-800">{admins.map((a) => a.name).join(", ") || "-"}</p>
            <p className="mt-1 text-[11px] text-amber-700">{CAPTAIN.duty}</p>
          </div>
          <div className="text-center text-slate-300" aria-hidden>│</div>
          <Link href={`/organization/staff/${secretary.key}`} className="mx-auto block max-w-xl rounded-xl border border-brand-200 bg-brand-50 p-3 text-center hover:border-brand-400">
            <p className="text-sm font-semibold text-brand-800">{secretary.emoji} {secretary.name} — {secretary.title} <Badge tone="gray">30일 {activity[secretary.key] ?? 0}건</Badge></p>
            <p className="text-xs text-brand-700">{secretary.purpose}</p>
          </Link>
          <div className="text-center text-slate-300" aria-hidden>│</div>
          <ul className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
            {staff.map((a) => (
              <li key={a.key}>
                <Link href={`/organization/staff/${a.key}`} className="block h-full rounded-xl border border-slate-200 p-3 hover:border-brand-300 hover:shadow-sm">
                  <div className="flex items-start justify-between gap-2">
                    <p className="font-semibold">{a.emoji} {a.name} <span className="text-xs font-normal text-slate-500">{a.title}</span></p>
                    <Badge tone="gray">30일 {activity[a.key] ?? 0}건</Badge>
                  </div>
                  <p className="mt-1 text-xs text-slate-700">{a.purpose}</p>
                  <p className="mt-2 text-[11px] text-slate-500">말투: {a.personality}</p>
                  <p className="mt-1 text-[11px] text-slate-500">다음 담당: {staffLabel(a.next)}</p>
                  {a.handsOffTo && <p className="mt-2"><Badge tone="amber">결재 연결: {APPROVAL_GATE_LABEL[a.handsOffTo]}</Badge></p>}
                </Link>
              </li>
            ))}
          </ul>
        </CardBody>
      </Card>

      <div className="mb-6 grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader title="⛔ 금지선" description="결재를 받아도 하지 않는 일 — ‘실행 금지’" />
          <CardBody>
            <ul className="list-disc space-y-1 pl-5 text-sm text-rose-900">
              {FORBIDDEN_LINES.map((l) => <li key={l}>{l}</li>)}
            </ul>
          </CardBody>
        </Card>
        <Card>
          <CardHeader title="✋ 실행 전 결재 대상" description="결재 요청서(대상·변경 내용·비용·위험·되돌리는 법)를 보고 승인/반려/수정 요청" />
          <CardBody>
            <ul className="list-disc space-y-1 pl-5 text-sm text-amber-900">
              {APPROVAL_TARGETS.map((l) => <li key={l}>{l}</li>)}
            </ul>
            <p className="mt-2 text-xs text-slate-500">답이 없으면 대기합니다. 승인 뒤 내용이 바뀌면 다시 결재받습니다.</p>
          </CardBody>
        </Card>
      </div>

      <Card className="mb-6">
        <div id="rules" />
        <CardHeader title="회사 운영 규칙" action={isAdmin && <Link href="/settings/approval-rules" className="link text-xs">결재 규칙 설정 →</Link>} />
        <CardBody className="grid gap-6 lg:grid-cols-2">
          <div className="space-y-3 text-sm">
            <p><strong>보고</strong> — 비서 한결이 대시보드에 ‘한 일 → 결과 → 할 일’ 5줄 이내로 보고합니다.</p>
            <p><strong>실패 대응</strong> — 게시 실패 재시도는 최대 {MAX_RETRIES}회, 그 뒤엔 멈추고 원인을 보고합니다. 외부 게시 성공 여부가 불명확하면 자동으로 다시 올리지 않습니다.</p>
            <p><strong>비용</strong> — 유료 AI 호출 전에 월 상한을 확인하고, 상한에 닿으면 멈춥니다. 데모 엔진(0원)은 항상 허용됩니다.</p>
            {budget && (
              <div className="rounded-lg bg-slate-50 p-3">
                <p className="text-xs text-slate-600">이번 달 AI 운영비 <strong>{won(budget.used)}</strong> / 상한 <strong>{budget.cap == null ? "미설정" : won(budget.cap)}</strong>{budget.reached && <span className="ml-1 text-rose-700">— 상한 도달</span>}</p>
                {isAdmin && <div className="mt-2"><BudgetForm cap={budget.cap} /></div>}
              </div>
            )}
          </div>
          <div>
            <p className="mb-2 text-sm font-semibold">결재 라인</p>
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
          </div>
        </CardBody>
      </Card>

      {/* 사람 조직 */}
      <Card>
        <CardHeader title={`사람 조직 — ${org.name}`} description="사람 직원이 있다면 팀으로 묶어 고객을 배정합니다 · 팀원·팀장은 배정된 고객을 담당합니다" action={isAdmin && <Link href="/settings/users" className="link text-xs">직원·권한 →</Link>} />
        <CardBody className="space-y-4">
          <ul className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
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
    </>
  );
}
