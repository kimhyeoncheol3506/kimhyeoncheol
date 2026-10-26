import type { PlatformKey } from "@prisma/client";
import { prisma } from "@/lib/db";
import { assertCan, campaignWhere, NotFoundError, type Ctx } from "@/lib/auth/context";
import { can, seesAllClients } from "@/lib/auth/permissions";
import type { AIProvider } from "@/lib/ai/types";
import type { AiReview } from "@/lib/approval/ai-review";
import { CHANNEL_LABEL, CHANNEL_PACK } from "@/lib/company/channels";
import { won } from "@/lib/format";
import { audit } from "./audit";
import { generateContent, submitForReview } from "./content";
import { myInboxCount } from "./approvals";
import { aiBudgetStatus } from "./budget";

export interface ChannelPackResult {
  created: number;
  submitted: number;
  done: PlatformKey[];
  failed: { platform: PlatformKey; message: string } | null;
}

/**
 * ‘AI 팀에 맡기기’: 비서가 매체별로 카피라이터·숏폼 PD 에게 배정 → 초안 생성 → 검수·결재 요청까지.
 * 한 매체라도 실패하면 거기서 멈추고 보고한다 (비용이 드는 호출을 계속하지 않음).
 */
export async function runChannelPack(ctx: Ctx, campaignId: string, platforms: PlatformKey[], provider: AIProvider): Promise<ChannelPackResult> {
  assertCan(ctx, "content:generate");
  if (platforms.length === 0) throw new Error("홍보할 매체를 하나 이상 고르세요.");
  const c = await prisma.campaign.findFirst({ where: { ...campaignWhere(ctx), id: campaignId }, select: { id: true, name: true } });
  if (!c) throw new NotFoundError("캠페인을 찾을 수 없습니다.");

  const ids: string[] = [];
  const done: PlatformKey[] = [];
  let failed: ChannelPackResult["failed"] = null;
  for (const platform of platforms) {
    try {
      const r = await generateContent(ctx, { campaignId, platform, types: CHANNEL_PACK[platform] }, provider);
      if (!r.ok) {
        failed = { platform, message: r.errorMessage ?? "AI 생성 실패" };
        break;
      }
      ids.push(...r.ids);
      done.push(platform);
    } catch (e) {
      failed = { platform, message: e instanceof Error ? e.message : "알 수 없는 오류" };
      break;
    }
  }
  const submitted = ids.length && can(ctx.role, "content:edit") ? await submitForReview(ctx, ids) : 0;
  await audit(
    ctx,
    "company.channel_pack",
    "Campaign",
    c.id,
    `AI 팀 채널 패키지: ${done.map((p) => CHANNEL_LABEL[p]).join("·") || "없음"} — 초안 ${ids.length}건, 결재 요청 ${submitted}건${failed ? ` · ${CHANNEL_LABEL[failed.platform]}에서 멈춤` : ""}`,
    { platforms, failed },
  );
  return { created: ids.length, submitted, done, failed };
}

export type StageState = "done" | "active" | "waiting" | "blocked" | "todo";

export interface BoardStage {
  staff: string; // staff key 또는 captain
  label: string;
  state: StageState;
  detail: string;
}

export interface ChannelRow {
  platform: PlatformKey;
  drafts: number;
  pending: number;
  approved: number;
  published: number;
  failed: number;
  clicks: number;
  visits: number;
  conversions: number;
  measured: boolean;
}

/** 캠페인 한 건의 AI 팀 진행판 — 단계별 담당·상태와 매체별 결과 */
export async function campaignBoard(ctx: Ctx, campaignId: string) {
  assertCan(ctx, "campaign:read");
  const c = await prisma.campaign.findFirst({
    where: { ...campaignWhere(ctx), id: campaignId },
    include: {
      brief: { select: { desiredPlatforms: true, scores: true } },
      contents: { select: { id: true, type: true, platform: true, status: true } },
      publications: { select: { id: true, platform: true, status: true } },
    },
  });
  if (!c) throw new NotFoundError();
  const contentIds = c.contents.map((x) => x.id);
  const [requests, metrics] = await Promise.all([
    prisma.approvalRequest.findMany({
      where: { organizationId: ctx.organizationId, entityType: "GeneratedContent", entityId: { in: contentIds }, status: "PENDING" },
      select: { aiReview: true },
    }),
    prisma.performanceMetric.findMany({
      where: { organizationId: ctx.organizationId, campaignId: c.id },
      select: { clicks: true, visits: true, conversions: true, source: true, publication: { select: { platform: true } } },
    }),
  ]);
  const blocked = requests.filter((r) => (r.aiReview as unknown as AiReview | null)?.passed === false).length;
  const n = (s: string) => c.contents.filter((x) => x.status === s).length;
  const shorts = c.contents.filter((x) => x.type === "SHORT_SCRIPT" || x.type === "SHORT_HOOK").length;
  const success = c.publications.filter((p) => p.status === "SUCCESS").length;
  const pubFailed = c.publications.filter((p) => p.status === "FAILED" || p.status === "BLOCKED").length;
  const totals = metrics.reduce((a, m) => ({ clicks: a.clicks + (m.clicks ?? 0), conversions: a.conversions + (m.conversions ?? 0) }), { clicks: 0, conversions: 0 });
  const onlySim = metrics.length > 0 && metrics.every((m) => m.source !== "VERIFIED");

  const stages: BoardStage[] = [
    { staff: "intake", label: "의뢰 접수", state: c.brief ? "done" : "todo", detail: c.brief ? `요청 매체 ${c.brief.desiredPlatforms.map((p) => CHANNEL_LABEL[p]).join("·") || "미지정"}` : "의뢰서 없음" },
    { staff: "strategist", label: "기획·분석", state: c.brief?.scores ? "done" : "todo", detail: c.brief?.scores ? "AI 분석 완료" : "AI 분석 실행 필요" },
    {
      staff: "copywriter",
      label: "콘텐츠 제작",
      state: c.contents.length ? "done" : "todo",
      detail: c.contents.length ? `문구 ${c.contents.length - shorts}건 · 숏폼 ${shorts}건` : "‘AI 팀에 맡기기’로 시작",
    },
    {
      staff: "compliance",
      label: "AI 1차 검토",
      state: blocked ? "blocked" : requests.length ? "active" : c.contents.length ? "done" : "todo",
      detail: blocked ? `차단 ${blocked}건 — 수정 필요` : requests.length ? `검토 완료 · 결재 대기 ${requests.length}건` : c.contents.length ? "대기 중인 검토 없음" : "-",
    },
    {
      staff: "captain",
      label: "결재",
      state: n("PENDING_REVIEW") ? "waiting" : n("APPROVED") ? "done" : "todo",
      detail: n("PENDING_REVIEW") ? `결재 대기 ${n("PENDING_REVIEW")}건` : `승인 ${n("APPROVED")}건 · 반려 ${n("REJECTED")}건`,
    },
    {
      staff: "publisher",
      label: "집행",
      state: pubFailed && !success ? "blocked" : success ? "done" : n("APPROVED") ? "active" : "todo",
      detail: `게시 성공 ${success}건${pubFailed ? ` · 실패/차단 ${pubFailed}건` : ""}${n("APPROVED") && !c.publications.length ? " · 승인분 집행 대기" : ""}`,
    },
    {
      staff: "analyst",
      label: "성과",
      state: metrics.length ? "done" : "todo",
      detail: metrics.length ? `클릭 ${totals.clicks.toLocaleString("ko-KR")} · 전환 ${totals.conversions.toLocaleString("ko-KR")}${onlySim ? " (모의·데모 수치)" : ""}` : "실적 없음",
    },
  ];

  const platforms = new Set<PlatformKey>([...(c.brief?.desiredPlatforms ?? []), ...c.contents.flatMap((x) => (x.platform ? [x.platform] : [])), ...c.publications.map((p) => p.platform)]);
  const channels: ChannelRow[] = [...platforms].map((platform) => {
    const cs = c.contents.filter((x) => x.platform === platform);
    const ps = c.publications.filter((p) => p.platform === platform);
    const ms = metrics.filter((m) => m.publication?.platform === platform);
    return {
      platform,
      drafts: cs.length,
      pending: cs.filter((x) => x.status === "PENDING_REVIEW").length,
      approved: cs.filter((x) => x.status === "APPROVED").length,
      published: ps.filter((p) => p.status === "SUCCESS").length,
      failed: ps.filter((p) => p.status === "FAILED" || p.status === "BLOCKED").length,
      clicks: ms.reduce((a, m) => a + (m.clicks ?? 0), 0),
      visits: ms.reduce((a, m) => a + (m.visits ?? 0), 0),
      conversions: ms.reduce((a, m) => a + (m.conversions ?? 0), 0),
      measured: ms.some((m) => m.source === "VERIFIED"),
    };
  });
  return { stages, channels, hasSimulatedOnly: onlySim };
}

export interface ReportLine {
  label: string;
  text: string;
  href?: string;
}

/** 비서 한결의 5줄 보고: 한 일 → 결과 → 캡틴이 할 일 (+ 집행·예산) */
export async function secretaryReport(ctx: Ctx): Promise<ReportLine[]> {
  const since = new Date(Date.now() - 86_400_000);
  const scope = seesAllClients(ctx.role) ? {} : { clientId: { in: ctx.clientIds } };
  const [acts, pendingReqs, failedPubs, inbox, overdue, openTasks, budget] = await Promise.all([
    prisma.auditLog.groupBy({ by: ["action"], where: { organizationId: ctx.organizationId, createdAt: { gte: since } }, _count: { _all: true } }),
    prisma.approvalRequest.findMany({
      where: { organizationId: ctx.organizationId, status: "PENDING", ...(seesAllClients(ctx.role) ? {} : { OR: [{ clientId: null }, { clientId: { in: ctx.clientIds } }] }) },
      select: { aiReview: true },
    }),
    prisma.publication.count({ where: { organizationId: ctx.organizationId, status: "FAILED", campaign: { deletedAt: null, ...scope } } }),
    can(ctx.role, "approval:decide") ? myInboxCount(ctx) : Promise.resolve(0),
    prisma.fulfillmentTask.count({ where: { organizationId: ctx.organizationId, status: { not: "DONE" }, dueDate: { lt: new Date() }, campaign: scope } }),
    prisma.fulfillmentTask.count({ where: { organizationId: ctx.organizationId, status: { in: ["TODO", "IN_PROGRESS"] }, campaign: scope } }),
    can(ctx.role, "cost:read") ? aiBudgetStatus(ctx) : Promise.resolve(null),
  ]);
  const a = new Map(acts.map((x) => [x.action, x._count._all]));
  const g = (...k: string[]) => k.reduce((s, x) => s + (a.get(x) ?? 0), 0);
  const blocked = pendingReqs.filter((r) => (r.aiReview as unknown as AiReview | null)?.passed === false).length;
  const you = ctx.role === "ADMIN" ? "캡틴" : `${ctx.name}님`;

  const lines: ReportLine[] = [
    {
      label: "한 일",
      text: `최근 24시간 — 문의 분석 ${g("inquiry.create", "inquiry.reanalyze")} · 견적 ${g("inquiry.quote")} · 문구 생성 ${g("content.generate")}회(숏폼 ${g("content.generate.shortform")}) · 게시 ${g("publication.success", "threads.post.live")}건`,
    },
    {
      label: "결과",
      text: `결재 대기 ${pendingReqs.length}건${blocked ? ` (AI 차단 ${blocked}건 — 수정 필요)` : ""} · 실행 실패 ${failedPubs}건`,
      href: failedPubs ? "/executions?status=FAILED" : "/approvals?tab=pending",
    },
    {
      label: `${you}이 할 일`,
      text: inbox ? `지금 ${you} 차례인 결재 ${inbox}건이 있습니다.` : "지금 결재할 건은 없습니다.",
      href: inbox ? "/approvals" : undefined,
    },
    {
      label: "집행",
      text: `진행 중 작업 ${openTasks}건${overdue ? ` · 마감 지난 작업 ${overdue}건` : ""}`,
      href: overdue ? "/fulfillment" : undefined,
    },
  ];
  if (budget)
    lines.push({
      label: "예산",
      text: `이번 달 AI 운영비 ${won(budget.used)} / 상한 ${budget.cap == null ? "미설정" : won(budget.cap)}${budget.reached ? " — 상한 도달, 유료 AI 호출 멈춤" : ""}`,
      href: "/organization#rules",
    });
  return lines.slice(0, 5);
}
