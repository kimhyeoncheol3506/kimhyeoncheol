import { createHash } from "crypto";
import type { PlatformKey, Prisma } from "@prisma/client";
import { prisma } from "@/lib/db";
import { assertCan, ForbiddenError, NotFoundError, type Ctx } from "@/lib/auth/context";
import { seesAllClients } from "@/lib/auth/permissions";
import { FAKE_EXPERIENCE_PATTERNS } from "@/lib/ai/guardrails";
import { getAdapter } from "@/lib/adapters/platforms";
import { fnv1a } from "@/lib/adapters/base";
import { PLATFORM_LABEL } from "@/lib/labels";
import { audit } from "./audit";
import { recomputeCampaignStatus } from "./campaigns";

const DISCLOSURE_MARKERS = ["광고", "협찬", "유료", "#ad", "sponsored", "paid partnership"];

export function hasDisclosure(text: string): boolean {
  const t = text.toLowerCase();
  return DISCLOSURE_MARKERS.some((m) => t.includes(m));
}

/** 실제 게시될 최종 문구: 본문에 광고 표시가 없으면 광고 표시 문구를 덧붙인다 */
export function finalText(body: string, disclosure: string): string {
  if (!disclosure || hasDisclosure(body)) return body;
  return `${body}\n\n${disclosure}`;
}

export function contentHash(text: string, platform: PlatformKey, targetUrl: string | null | undefined): string {
  const norm = text.replace(/\s+/g, " ").trim().toLowerCase();
  return createHash("sha256").update(`${platform}|${targetUrl ?? ""}|${norm}`).digest("hex");
}

function startOfDayKst(d = new Date()): Date {
  const kst = new Date(d.getTime() + 9 * 3600_000);
  kst.setUTCHours(0, 0, 0, 0);
  return new Date(kst.getTime() - 9 * 3600_000);
}

export interface CheckItem {
  key: string;
  label: string;
  passed: boolean;
  severity: "block" | "warn";
  detail: string;
}

export interface Precheck {
  ok: boolean;
  items: CheckItem[];
  text: string;
  hash: string;
  targetUrl: string | null;
  platform: PlatformKey;
}

function pubWhere(ctx: Ctx): Prisma.PublicationWhereInput {
  return {
    organizationId: ctx.organizationId,
    campaign: { deletedAt: null, ...(seesAllClients(ctx.role) ? {} : { clientId: { in: ctx.clientIds } }) },
  };
}

async function loadContent(ctx: Ctx, contentId: string) {
  const content = await prisma.generatedContent.findFirst({
    where: {
      id: contentId,
      organizationId: ctx.organizationId,
      campaign: { deletedAt: null, ...(seesAllClients(ctx.role) ? {} : { clientId: { in: ctx.clientIds } }) },
    },
    include: {
      candidate: true,
      campaign: { include: { brief: true, client: { include: { brandProfile: true } } } },
    },
  });
  if (!content) throw new NotFoundError();
  return content;
}

/** 실행 전 사전 검사 (승인·광고표시·금지어·허위체험·글자수·중복·일일한도·희망SNS·정책검토) */
export async function precheck(ctx: Ctx, contentId: string, platformArg?: PlatformKey): Promise<Precheck> {
  const content = await loadContent(ctx, contentId);
  const platform = platformArg ?? content.platform ?? content.candidate?.platform ?? content.campaign.brief?.desiredPlatforms[0] ?? "INSTAGRAM";
  const sp = await prisma.socialPlatform.findUniqueOrThrow({ where: { key: platform } });
  const text = finalText(content.body, content.disclosure);
  const targetUrl = content.candidate?.postUrl ?? null;
  const hash = contentHash(text, platform, targetUrl);
  const items: CheckItem[] = [];
  const bp = content.campaign.client.brandProfile;

  items.push({
    key: "approved",
    label: "담당자 승인",
    passed: content.status === "APPROVED",
    severity: "block",
    detail: content.status === "APPROVED" ? "승인 완료된 문구입니다." : "승인되지 않은 문구는 실행할 수 없습니다.",
  });
  const own = content.campaign.client.ownAccount;
  items.push({
    key: "disclosure",
    label: "광고 표시",
    passed: own || hasDisclosure(text),
    severity: "block",
    detail: own ? "고객 본인 계정 게시 — 가게가 자기 가게를 알리는 글이라 광고 표시가 필요 없습니다." : hasDisclosure(text) ? "광고·협찬 표시가 포함됩니다." : "광고 표시 문구가 없습니다.",
  });
  if (own)
    items.push({
      key: "clientApproval",
      label: "사장님 승인",
      passed: content.clientStatus === "APPROVED",
      severity: "block",
      detail: content.clientStatus === "APPROVED" ? "사장님이 승인했습니다." : content.clientStatus === "CHANGES_REQUESTED" ? `사장님 수정 요청: ${content.clientComment ?? ""}` : "사장님 링크에서 승인을 받아야 올릴 수 있습니다.",
    });
  const banned = [...(bp?.bannedPhrases ?? []), ...(content.campaign.brief?.bannedKeywords ?? [])].filter(
    (p) => p && text.toLowerCase().includes(p.toLowerCase()),
  );
  items.push({
    key: "banned",
    label: "금지 표현",
    passed: banned.length === 0,
    severity: "block",
    detail: banned.length ? `금지 표현 포함: ${banned.join(", ")}` : "금지 표현이 없습니다.",
  });
  const fake = FAKE_EXPERIENCE_PATTERNS.filter((p) => text.includes(p));
  items.push({
    key: "fake",
    label: "허위 체험담·위장 표현",
    passed: fake.length === 0,
    severity: "block",
    detail: fake.length ? `의심 표현: ${fake.join(", ")}` : "의심 표현이 없습니다.",
  });
  items.push({
    key: "length",
    label: `${PLATFORM_LABEL[platform]} 글자 수 제한`,
    passed: text.length <= sp.maxTextLength,
    severity: "block",
    detail: `${text.length} / ${sp.maxTextLength}자`,
  });
  const dup = await prisma.publication.findFirst({
    where: { organizationId: ctx.organizationId, contentHash: hash, status: { in: ["QUEUED", "SUCCESS"] } },
  });
  items.push({
    key: "duplicate",
    label: "중복 게시 검사",
    passed: !dup,
    severity: "block",
    detail: dup ? "같은 플랫폼·대상에 동일한 문구가 이미 예약 또는 게시되었습니다." : "중복 없음",
  });
  const today = await prisma.publication.count({
    where: { organizationId: ctx.organizationId, platform, status: { in: ["QUEUED", "SUCCESS", "FAILED"] }, createdAt: { gte: startOfDayKst() } },
  });
  items.push({
    key: "dailyLimit",
    label: "플랫폼별 일일 실행 한도",
    passed: today < sp.dailyLimit,
    severity: "block",
    detail: `오늘 ${today} / ${sp.dailyLimit}건`,
  });
  const desired = content.campaign.brief?.desiredPlatforms ?? [];
  items.push({
    key: "desired",
    label: "희망 SNS 일치",
    passed: desired.includes(platform),
    severity: "warn",
    detail: desired.includes(platform) ? "의뢰서의 희망 SNS 입니다." : "의뢰서의 희망 SNS 가 아닙니다.",
  });
  const policy = await prisma.policyReview.findFirst({
    where: { organizationId: ctx.organizationId, platform },
    orderBy: { updatedAt: "desc" },
  });
  const policyOk = !!policy && policy.status === "COMPLETED" && policy.nextReviewAt > new Date();
  items.push({
    key: "policy",
    label: "플랫폼 정책 검토",
    passed: policyOk,
    severity: "warn",
    detail: !policy
      ? "정책 검토 기록이 없습니다."
      : policyOk
        ? `검토 완료 (위험도 ${policy.riskLevel})`
        : policy.status !== "COMPLETED"
          ? "정책 검토가 완료되지 않았습니다."
          : "정책 재검토 예정일이 지났습니다.",
  });
  return { ok: items.every((i) => i.passed || i.severity === "warn"), items, text, hash, targetUrl, platform };
}

/** 실행 대기열 등록. 사전검사 차단 시 BLOCKED 기록을 남기고 등록하지 않는다. */
export async function schedulePublication(ctx: Ctx, contentId: string, platform?: PlatformKey) {
  assertCan(ctx, "publication:execute");
  const pc = await precheck(ctx, contentId, platform);
  const content = await loadContent(ctx, contentId);
  return prisma.$transaction(async (tx) => {
    const failed = pc.items.filter((i) => !i.passed && i.severity === "block");
    const pub = await tx.publication.create({
      data: {
        organizationId: ctx.organizationId,
        campaignId: content.campaignId,
        contentId,
        platform: pc.platform,
        targetUrl: pc.targetUrl,
        mode: "SIMULATED",
        status: failed.length ? "BLOCKED" : "QUEUED",
        // BLOCKED 기록은 중복검사 대상이 아니므로 해시를 구분
        contentHash: failed.length ? `blocked:${pc.hash}:${Date.now()}` : pc.hash,
        errorCode: failed.length ? `PRECHECK_${failed[0].key.toUpperCase()}` : null,
        errorMessage: failed.length ? failed.map((f) => `${f.label}: ${f.detail}`).join(" / ") : null,
      },
    });
    await recomputeCampaignStatus(tx, content.campaignId);
    await audit(
      ctx,
      failed.length ? "publication.blocked" : "publication.schedule",
      "Publication",
      pub.id,
      failed.length ? `실행 차단: ${failed.map((f) => f.label).join(", ")}` : `${PLATFORM_LABEL[pc.platform]} 실행 대기 등록`,
      undefined,
      tx,
    );
    return { publication: pub, precheck: pc };
  });
}

/** 결정적 모의 실적 — 실제 수집값이 아님(source=SIMULATED) */
export function simulatedMetrics(seed: string) {
  const h = fnv1a(seed);
  const clicks = 20 + (h % 280);
  const visits = Math.round(clicks * (0.45 + ((h >>> 8) % 30) / 100));
  const conversions = Math.round(visits * (0.02 + ((h >>> 16) % 8) / 100));
  const views = clicks * (8 + ((h >>> 4) % 13));
  return { views, clicks, visits, conversions };
}

export const MAX_RETRIES = 2;

export async function executePublication(ctx: Ctx, publicationId: string, mode: "SIMULATED" | "LIVE" = "SIMULATED") {
  assertCan(ctx, "publication:execute");
  const pub = await prisma.publication.findFirst({ where: { ...pubWhere(ctx), id: publicationId }, include: { content: true } });
  if (!pub) throw new NotFoundError();
  if (pub.status !== "QUEUED" && pub.status !== "FAILED") throw new Error("실행 대기 또는 실패 상태만 실행할 수 있습니다.");
  if (pub.content.status !== "APPROVED") throw new Error("승인이 취소된 문구는 실행할 수 없습니다.");

  const adapter = getAdapter(pub.platform);
  const sp = await prisma.socialPlatform.findUniqueOrThrow({ where: { key: pub.platform } });
  const account = await prisma.connectedAccount.findFirst({ where: { organizationId: ctx.organizationId, platform: pub.platform } });
  if (mode === "LIVE" && adapter.status(account) !== "PUBLISH_READY")
    throw new ForbiddenError(`${adapter.name} 은(는) 공식 API 설정·인증이 완료되지 않아 실제 게시를 할 수 없습니다.`);

  // 재시도는 최대 2회 — 그 이상은 원인을 확인한 뒤 새로 등록 (외부 게시의 중복 위험 방지)
  if (pub.status === "FAILED" && pub.retryCount >= MAX_RETRIES)
    throw new Error(`재시도 ${MAX_RETRIES}회를 넘겨 멈췄습니다. 실패 원인(${pub.errorCode ?? "미상"})을 확인하고, 매체에 실제로 올라갔는지 먼저 확인하세요.`);
  const attempt = pub.status === "FAILED" ? pub.retryCount + 1 : pub.retryCount;
  const req = {
    text: finalText(pub.content.body, pub.content.disclosure),
    targetUrl: pub.targetUrl,
    kind: pub.targetUrl ? ("COMMENT" as const) : ("POST" as const),
    attempt,
    maxTextLength: sp.maxTextLength,
  };
  const res = mode === "LIVE" ? await adapter.publishLive(req) : adapter.simulate(req);
  const now = new Date();

  return prisma.$transaction(async (tx) => {
    const updated = await tx.publication.update({
      where: { id: pub.id },
      data: {
        mode,
        status: res.ok ? "SUCCESS" : "FAILED",
        externalId: res.externalId ?? null,
        errorCode: res.ok ? null : res.errorCode,
        errorMessage: res.ok ? null : res.errorMessage,
        retryCount: attempt,
        executedById: ctx.userId,
        executedAt: now,
      },
    });
    if (res.ok) {
      const m = mode === "SIMULATED" ? simulatedMetrics(`${pub.id}|${res.externalId}`) : null;
      await tx.performanceMetric.create({
        data: {
          organizationId: ctx.organizationId,
          campaignId: pub.campaignId,
          publicationId: pub.id,
          date: now,
          views: m?.views ?? null,
          clicks: m?.clicks ?? null,
          visits: m?.visits ?? null,
          conversions: m?.conversions ?? null,
          // 실제 게시 실적은 수집 연동 전까지 미측정
          source: mode === "SIMULATED" ? "SIMULATED" : "NOT_MEASURED",
        },
      });
    }
    await recomputeCampaignStatus(tx, pub.campaignId);
    await audit(
      ctx,
      res.ok ? "publication.success" : "publication.failed",
      "Publication",
      pub.id,
      `${mode === "SIMULATED" ? "[모의] " : ""}${adapter.name} 실행 ${res.ok ? "성공" : `실패 (${res.errorCode})`}`,
      { attempt },
      tx,
    );
    return { publication: updated, result: res };
  });
}

export interface PublicationFilter {
  status?: "QUEUED" | "SUCCESS" | "FAILED" | "BLOCKED";
  platform?: PlatformKey;
  page?: number;
}

export async function listPublications(ctx: Ctx, f: PublicationFilter = {}) {
  assertCan(ctx, "campaign:read");
  const page = Math.max(1, f.page ?? 1);
  const where: Prisma.PublicationWhereInput = { ...pubWhere(ctx), ...(f.status ? { status: f.status } : {}), ...(f.platform ? { platform: f.platform } : {}) };
  const [total, rows] = await Promise.all([
    prisma.publication.count({ where }),
    prisma.publication.findMany({
      where,
      orderBy: { updatedAt: "desc" },
      skip: (page - 1) * 15,
      take: 15,
      include: {
        campaign: { select: { id: true, name: true, client: { select: { name: true } } } },
        content: { select: { id: true, type: true, body: true, disclosure: true } },
        executedBy: { select: { name: true } },
        metrics: true,
      },
    }),
  ]);
  return { total, page, pageCount: Math.max(1, Math.ceil(total / 15)), rows };
}

/** 실행 가능한 승인 문구 (아직 대기열에 없는 것) */
export async function approvedNotScheduled(ctx: Ctx) {
  return prisma.generatedContent.findMany({
    where: {
      organizationId: ctx.organizationId,
      status: "APPROVED",
      campaign: { deletedAt: null, ...(seesAllClients(ctx.role) ? {} : { clientId: { in: ctx.clientIds } }) },
      publications: { none: { status: { in: ["QUEUED", "SUCCESS"] } } },
    },
    include: { campaign: { select: { name: true, client: { select: { name: true } } } }, candidate: { select: { title: true, platform: true } } },
    orderBy: { updatedAt: "desc" },
    take: 50,
  });
}
