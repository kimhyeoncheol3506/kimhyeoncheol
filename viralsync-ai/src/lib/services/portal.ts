import { randomBytes } from "crypto";
import type { Prisma } from "@prisma/client";
import { prisma } from "@/lib/db";
import { assertCan, clientWhere, NotFoundError, type Ctx } from "@/lib/auth/context";
import { churnSignals, fridayMessage, mondayMessage, UPSELLS } from "@/lib/business/playbook";
import { saveImage, validateImage } from "@/lib/threads/storage";
import { CONTENT_TYPE_LABEL, PLATFORM_LABEL } from "@/lib/labels";
import { audit } from "./audit";
import { recomputeCampaignStatus } from "./campaigns";
import { overdueCount } from "./subscriptions";

/**
 * 사장님 링크 — 로그인 없이 쓰는 고객 전용 화면 (PART 8-3 “사장님이 승인한 것만 올라갑니다”, PART 3-1 “사장님은 사진만 전송”).
 * 링크는 추측할 수 없는 토큰이며, 새로 만들면 이전 링크는 바로 못 쓴다.
 */

export const TOKEN_RE = /^[A-Za-z0-9_-]{32}$/;

export async function ensurePortalToken(ctx: Ctx, clientId: string, rotate = false) {
  assertCan(ctx, "client:write");
  const c = await prisma.client.findFirst({ where: { ...clientWhere(ctx), id: clientId } });
  if (!c) throw new NotFoundError();
  if (c.portalToken && !rotate) return c.portalToken;
  const token = randomBytes(24).toString("base64url");
  await prisma.client.update({ where: { id: c.id }, data: { portalToken: token } });
  await audit(ctx, "portal.link", "Client", c.id, `${c.name}: 사장님 링크 ${rotate && c.portalToken ? "새로 발급 (이전 링크 사용 중지)" : "발급"}`);
  return token;
}

async function clientByToken(token: string) {
  if (!TOKEN_RE.test(token)) return null;
  return prisma.client.findFirst({ where: { portalToken: token, deletedAt: null }, include: { organization: { select: { name: true } } } });
}

function portalAudit(c: { id: string; organizationId: string; name: string }, action: string, entityType: string, entityId: string | null, summary: string, tx: Prisma.TransactionClient = prisma) {
  return tx.auditLog.create({ data: { organizationId: c.organizationId, actorId: null, action, entityType, entityId, summary: `[사장님 링크] ${c.name}: ${summary}` } });
}

function monthRange(period: string) {
  const [y, m] = period.split("-").map(Number);
  return { from: new Date(y, m - 1, 1), to: new Date(y, m, 1) };
}

export function currentPeriod(d = new Date()) {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
}

export function previousPeriod(d = new Date()) {
  return currentPeriod(new Date(d.getFullYear(), d.getMonth() - 1, 1));
}

/** 월 보고서 반 장 (부록 C): 요약 한 줄 · 게시물별 조회수 · 베스트 · 다음 달 제안 · 계약 안내 */
export async function clientMonthlyReport(organizationId: string, clientId: string, period: string) {
  const { from, to } = monthRange(period);
  const pubs = await prisma.publication.findMany({
    where: { organizationId, status: "SUCCESS", executedAt: { gte: from, lt: to }, campaign: { clientId } },
    include: { content: { select: { type: true, body: true } }, metrics: { select: { views: true, clicks: true, source: true } } },
    orderBy: { executedAt: "asc" },
  });
  const posts = pubs.map((p) => {
    const views = p.metrics.reduce((a, m) => a + (m.views ?? 0), 0);
    return {
      id: p.id,
      label: `${PLATFORM_LABEL[p.platform]} · ${CONTENT_TYPE_LABEL[p.content.type]}`,
      title: p.content.body.split("\n").find((l) => l.trim())?.slice(0, 40) ?? "",
      date: p.executedAt,
      views,
      clicks: p.metrics.reduce((a, m) => a + (m.clicks ?? 0), 0),
      simulated: p.mode === "SIMULATED" || p.metrics.some((m) => m.source !== "VERIFIED"),
    };
  });
  const totalViews = posts.reduce((a, p) => a + p.views, 0);
  const best = [...posts].sort((a, b) => b.views - a.views)[0] ?? null;
  const sub = await prisma.subscription.findFirst({ where: { clientId, status: { in: ["TRIAL", "ACTIVE", "SUSPENDED"] } }, include: { payments: true } });
  const contractNote = !sub
    ? null
    : sub.status === "TRIAL"
      ? `무료 체험이 ${sub.trialEnd?.toLocaleDateString("ko-KR")} 에 끝납니다. 계속 진행 여부를 알려 주세요.`
      : overdueCount(sub.payments) > 0
        ? "확인이 필요한 결제가 있습니다. 담당자에게 문의해 주세요."
        : null;
  return {
    period,
    summary: posts.length ? `이번 달 게시물 ${posts.length}개, 조회수 합계 ${totalViews.toLocaleString("ko-KR")}회${best ? ` — 가장 반응 좋은 건 ‘${best.title}’` : ""}` : "이번 달 올라간 게시물이 아직 없습니다.",
    posts,
    totalViews,
    best,
    suggestion: best ? `반응이 좋았던 ‘${best.label}’ 형식으로 다음 달 2편 더 만들어 보겠습니다. 리뷰 이벤트 릴스도 제안드려요.` : "가게 사진을 보내 주시면 첫 릴스부터 만들어 드리겠습니다.",
    contractNote,
    simulated: posts.some((p) => p.simulated),
  };
}

/** 고객 화면용: 이탈 경고·업셀·주간 메시지 초안 */
export async function clientCare(ctx: Ctx, clientId: string) {
  assertCan(ctx, "client:read");
  const c = await prisma.client.findFirst({ where: { ...clientWhere(ctx), id: clientId }, include: { subscriptions: { include: { payments: true }, orderBy: { createdAt: "desc" }, take: 1 } } });
  if (!c) throw new NotFoundError();
  const now = new Date();
  const [pending, upcoming, week] = await Promise.all([
    prisma.generatedContent.findMany({ where: { organizationId: ctx.organizationId, campaign: { clientId }, clientStatus: "PENDING" }, select: { updatedAt: true }, orderBy: { updatedAt: "asc" } }),
    prisma.generatedContent.findMany({
      where: { organizationId: ctx.organizationId, campaign: { clientId }, status: "APPROVED", publications: { none: { status: "SUCCESS" } } },
      select: { type: true, platform: true, clientStatus: true },
      take: 7,
      orderBy: { updatedAt: "desc" },
    }),
    prisma.publication.findMany({
      where: { organizationId: ctx.organizationId, status: "SUCCESS", executedAt: { gte: new Date(now.getTime() - 7 * 86_400_000) }, campaign: { clientId } },
      include: { metrics: { select: { views: true } }, content: { select: { body: true } } },
    }),
  ]);
  const sub = c.subscriptions[0] ?? null;
  const oldestPendingDays = pending.length ? Math.floor((now.getTime() - pending[0].updatedAt.getTime()) / 86_400_000) : 0;
  const signals = c.ownAccount || sub ? churnSignals({ reportViewedAt: c.reportViewedAt, pendingClientApprovals: pending.length, oldestPendingDays, missedPayments: sub ? overdueCount(sub.payments, now) : 0 }, now) : [];
  const days = ["월", "화", "수", "목", "금", "토", "일"];
  const weekViews = week.reduce((a, p) => a + p.metrics.reduce((b, m) => b + (m.views ?? 0), 0), 0);
  const best = [...week].sort((a, b) => b.metrics.reduce((x, m) => x + (m.views ?? 0), 0) - a.metrics.reduce((x, m) => x + (m.views ?? 0), 0))[0];
  // 3개월 넘게 유지된 유료 고객에게 업셀·소개 안내
  const tenureMonths = sub?.startDate ? Math.floor((now.getTime() - sub.startDate.getTime()) / (30 * 86_400_000)) : 0;
  return {
    pendingApprovals: pending.length,
    oldestPendingDays,
    signals,
    subscription: sub ? { id: sub.id, status: sub.status, planName: sub.planName } : null,
    upsell: sub?.status === "ACTIVE" ? UPSELLS : [],
    referralReady: sub?.status === "ACTIVE" && tenureMonths >= 3,
    monday: mondayMessage(c.name, upcoming.map((u, i) => ({ day: days[i % 5], title: `${u.platform ? PLATFORM_LABEL[u.platform] : ""} ${CONTENT_TYPE_LABEL[u.type]}${u.clientStatus === "PENDING" ? " (승인 부탁드려요)" : ""}`.trim() }))),
    friday: fridayMessage(c.name, { posts: week.length, views: week.length ? weekViews : null, best: best?.content.body.split("\n")[0]?.slice(0, 30) ?? null }),
  };
}

/** 사장님 링크 화면 데이터. 열람 시각을 남긴다 (이탈 경고등) */
export async function getPortal(token: string, opts: { report?: boolean } = {}) {
  const c = await clientByToken(token);
  if (!c) return null;
  const now = new Date();
  await prisma.client.update({ where: { id: c.id }, data: { portalViewedAt: now, ...(opts.report ? { reportViewedAt: now } : {}) } });
  const [pending, decided, assets, report] = await Promise.all([
    prisma.generatedContent.findMany({
      where: { organizationId: c.organizationId, campaign: { clientId: c.id }, status: "APPROVED", clientStatus: "PENDING" },
      select: { id: true, type: true, platform: true, body: true, updatedAt: true },
      orderBy: { updatedAt: "asc" },
    }),
    prisma.generatedContent.findMany({
      where: { organizationId: c.organizationId, campaign: { clientId: c.id }, clientStatus: { in: ["APPROVED", "CHANGES_REQUESTED"] }, clientDecidedAt: { gte: new Date(now.getTime() - 30 * 86_400_000) } },
      select: { id: true, type: true, platform: true, clientStatus: true, clientComment: true, clientDecidedAt: true },
      orderBy: { clientDecidedAt: "desc" },
      take: 10,
    }),
    prisma.clientAsset.findMany({ where: { clientId: c.id }, orderBy: { createdAt: "desc" }, take: 12 }),
    opts.report ? clientMonthlyReport(c.organizationId, c.id, previousPeriod(now)) : Promise.resolve(null),
  ]);
  return { client: { id: c.id, name: c.name }, orgName: c.organization.name, pending, decided, assets, report };
}

export async function portalDecide(token: string, contentId: string, decision: "APPROVED" | "CHANGES_REQUESTED", comment: string) {
  const c = await clientByToken(token);
  if (!c) throw new NotFoundError("링크가 만료되었거나 올바르지 않습니다.");
  if (decision === "CHANGES_REQUESTED" && !comment.trim()) throw new Error("어떻게 고치면 좋을지 한 줄만 적어 주세요.");
  const content = await prisma.generatedContent.findFirst({ where: { id: contentId, organizationId: c.organizationId, campaign: { clientId: c.id }, status: "APPROVED", clientStatus: "PENDING" } });
  if (!content) throw new Error("이미 처리되었거나 승인할 수 없는 게시물입니다.");
  await prisma.$transaction(async (tx) => {
    await tx.generatedContent.update({
      where: { id: contentId },
      data:
        decision === "APPROVED"
          ? { clientStatus: "APPROVED", clientDecidedAt: new Date(), clientComment: comment.trim() || null }
          : { clientStatus: "CHANGES_REQUESTED", status: "CHANGES_REQUESTED", clientDecidedAt: new Date(), clientComment: comment.trim() },
    });
    await recomputeCampaignStatus(tx, content.campaignId);
    await portalAudit(c, decision === "APPROVED" ? "portal.approve" : "portal.changes", "GeneratedContent", contentId, decision === "APPROVED" ? "게시 승인" : `수정 요청 — ${comment.trim()}`, tx);
  });
}

export async function portalUpload(token: string, buf: Uint8Array, note: string) {
  const c = await clientByToken(token);
  if (!c) throw new NotFoundError("링크가 만료되었거나 올바르지 않습니다.");
  const v = validateImage(buf);
  if (!v.ok) throw new Error(v.message);
  const recent = await prisma.clientAsset.count({ where: { clientId: c.id, createdAt: { gte: new Date(Date.now() - 86_400_000) } } });
  if (recent >= 30) throw new Error("하루에 사진은 30장까지 보낼 수 있습니다.");
  const fileName = await saveImage(buf, v.mime);
  await prisma.clientAsset.create({ data: { organizationId: c.organizationId, clientId: c.id, fileName, note: note.trim().slice(0, 200) } });
  await portalAudit(c, "portal.upload", "ClientAsset", null, "사진 1장 전송");
}

export async function listClientAssets(ctx: Ctx, clientId: string) {
  assertCan(ctx, "client:read");
  return prisma.clientAsset.findMany({ where: { clientId, client: clientWhere(ctx) }, orderBy: { createdAt: "desc" }, take: 24 });
}
