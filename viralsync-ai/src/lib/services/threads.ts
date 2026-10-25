import "server-only";
import { createHash } from "crypto";
import { prisma } from "@/lib/db";
import { assertCan, type Ctx } from "@/lib/auth/context";
import { publicUrlProblem, threadsConfig } from "@/lib/threads/config";
import { decryptToken, encryptToken, tokenHint } from "@/lib/threads/crypto";
import { exchangeCode, getMe, publishImage, refreshLongLived, ThreadsApiError, toLongLived, type ThreadsDeps } from "@/lib/threads/client";
import { saveImage, validateImage } from "@/lib/threads/storage";
import { threadsLength, THREADS_TEXT_LIMIT, withAdDisclosure } from "@/lib/threads/text";
import { audit } from "./audit";

const DAILY_LIMIT = 250; // Threads: 24시간 250건

async function liveAccount(organizationId: string) {
  return prisma.connectedAccount.findFirst({ where: { organizationId, platform: "THREADS", isDemo: false, encryptedToken: { not: null } } });
}

export async function threadsStatus(ctx: Ctx) {
  const cfg = threadsConfig();
  const account = await liveAccount(ctx.organizationId);
  const urlProblem = publicUrlProblem(cfg.publicBaseUrl);
  const problems: string[] = [];
  if (!account) problems.push("Threads 계정이 연결되지 않았습니다.");
  if (!cfg.encryptionKey) problems.push("TOKEN_ENCRYPTION_KEY 가 설정되지 않았습니다.");
  if (urlProblem) problems.push(urlProblem);
  return {
    account: account
      ? { username: account.accountName, tokenHint: account.tokenHint, expiresAt: account.tokenExpiresAt, lastError: account.lastError }
      : null,
    oauthReady: !!(cfg.appId && cfg.appSecret && cfg.redirectUri && cfg.encryptionKey),
    encryptionReady: !!cfg.encryptionKey,
    publicBaseUrl: urlProblem ? null : cfg.publicBaseUrl,
    canPublishLive: problems.length === 0,
    problems,
  };
}

async function storeToken(ctx: Ctx, token: string, expiresInSec: number | null, deps?: ThreadsDeps) {
  const cfg = threadsConfig();
  if (!cfg.encryptionKey) throw new Error("토큰을 안전하게 저장하려면 TOKEN_ENCRYPTION_KEY 환경변수를 먼저 설정하세요.");
  let me: { id: string; username?: string };
  try {
    me = await getMe(token, deps);
  } catch (e) {
    throw new Error(e instanceof ThreadsApiError && e.code === "AUTH" ? "토큰이 유효하지 않거나 만료되었습니다." : e instanceof Error ? e.message : "토큰 확인 실패");
  }
  const name = me.username ? `@${me.username}` : `Threads ${me.id}`;
  await prisma.$transaction([
    prisma.connectedAccount.deleteMany({ where: { organizationId: ctx.organizationId, platform: "THREADS", isDemo: false } }),
    prisma.connectedAccount.create({
      data: {
        organizationId: ctx.organizationId,
        platform: "THREADS",
        accountName: name,
        status: "AUTHENTICATED",
        encryptedToken: encryptToken(token, cfg.encryptionKey),
        tokenHint: tokenHint(token),
        tokenExpiresAt: expiresInSec ? new Date(Date.now() + expiresInSec * 1000) : null,
        externalUserId: String(me.id),
      },
    }),
  ]);
  await audit(ctx, "threads.connect", "ConnectedAccount", null, `Threads 계정 ${name} 연결`);
  return name;
}

/** 개발자 대시보드에서 발급한 토큰을 붙여넣어 연결 (가능하면 60일 토큰으로 교환) */
export async function connectWithToken(ctx: Ctx, rawToken: string, deps?: ThreadsDeps) {
  assertCan(ctx, "account:manage");
  const token = rawToken.trim();
  if (token.length < 20) throw new Error("액세스 토큰을 확인하세요.");
  const { appSecret } = threadsConfig();
  if (appSecret) {
    try {
      const ll = await toLongLived(appSecret, token, deps);
      return storeToken(ctx, ll.access_token, ll.expires_in, deps);
    } catch {
      // 이미 장기 토큰이거나 교환 불가 → 원래 토큰으로 진행
    }
  }
  return storeToken(ctx, token, null, deps);
}

/** OAuth 콜백: code → 단기 토큰 → 60일 토큰 */
export async function connectWithCode(ctx: Ctx, code: string, deps?: ThreadsDeps) {
  assertCan(ctx, "account:manage");
  const cfg = threadsConfig();
  if (!cfg.appId || !cfg.appSecret || !cfg.redirectUri) throw new Error("THREADS_APP_ID / THREADS_APP_SECRET / THREADS_REDIRECT_URI 를 설정하세요.");
  const short = await exchangeCode({ appId: cfg.appId, appSecret: cfg.appSecret, redirectUri: cfg.redirectUri, code }, deps);
  const ll = await toLongLived(cfg.appSecret, short.access_token, deps);
  return storeToken(ctx, ll.access_token, ll.expires_in, deps);
}

export async function disconnectThreads(ctx: Ctx) {
  assertCan(ctx, "account:manage");
  await prisma.connectedAccount.deleteMany({ where: { organizationId: ctx.organizationId, platform: "THREADS", isDemo: false } });
  await audit(ctx, "threads.disconnect", "ConnectedAccount", null, "Threads 계정 연결 해제");
}

/** 저장된 토큰을 꺼낸다. 만료 7일 이내면 갱신을 시도한다. */
async function usableToken(organizationId: string, deps?: ThreadsDeps) {
  const cfg = threadsConfig();
  const acc = await liveAccount(organizationId);
  if (!acc?.encryptedToken || !acc.externalUserId || !cfg.encryptionKey) return null;
  let token = decryptToken(acc.encryptedToken, cfg.encryptionKey);
  const soon = acc.tokenExpiresAt && acc.tokenExpiresAt.getTime() - Date.now() < 7 * 86_400_000;
  const oldEnough = Date.now() - acc.updatedAt.getTime() > 86_400_000;
  if (soon && oldEnough) {
    try {
      const r = await refreshLongLived(token, deps);
      token = r.access_token;
      await prisma.connectedAccount.update({
        where: { id: acc.id },
        data: { encryptedToken: encryptToken(token, cfg.encryptionKey), tokenHint: tokenHint(token), tokenExpiresAt: new Date(Date.now() + r.expires_in * 1000), lastError: null },
      });
    } catch {
      // 갱신 실패 시 기존 토큰으로 시도 (만료되었으면 게시 단계에서 오류 표시)
    }
  }
  return { token, userId: acc.externalUserId, accountId: acc.id };
}

export interface QuickPostInput {
  image: Uint8Array;
  caption: string;
  isAd: boolean;
  mode: "SIMULATED" | "LIVE";
}

export async function createQuickPost(ctx: Ctx, input: QuickPostInput, deps?: ThreadsDeps) {
  assertCan(ctx, "publication:execute");
  const img = validateImage(input.image);
  if (!img.ok) throw new Error(img.message);
  const text = withAdDisclosure(input.caption, input.isAd);
  const len = threadsLength(text);
  if (len > THREADS_TEXT_LIMIT) throw new Error(`문구가 너무 깁니다 (${len}/${THREADS_TEXT_LIMIT}자, 이모지는 더 많이 셉니다).`);

  if (input.mode === "LIVE") {
    const st = await threadsStatus(ctx);
    if (!st.canPublishLive) throw new Error(`실제 게시를 할 수 없습니다: ${st.problems.join(" ")}`);
    const since = new Date(Date.now() - 86_400_000);
    const recent = await prisma.quickPost.count({ where: { organizationId: ctx.organizationId, mode: "LIVE", status: "PUBLISHED", publishedAt: { gte: since } } });
    if (recent >= DAILY_LIMIT) throw new Error("Threads 24시간 게시 한도(250건)에 도달했습니다.");
  }

  const file = await saveImage(input.image, img.mime);
  const hash = createHash("sha256").update(input.image).digest("hex").slice(0, 12);
  const post = await prisma.quickPost.create({
    data: {
      organizationId: ctx.organizationId,
      createdById: ctx.userId,
      imageFile: file,
      imageMime: img.mime,
      imageBytes: input.image.length,
      caption: text,
      isAd: input.isAd,
      mode: input.mode,
      status: "PUBLISHING",
    },
  });

  if (input.mode === "SIMULATED") {
    const done = await prisma.quickPost.update({
      where: { id: post.id },
      data: { status: "PUBLISHED", externalId: `sim_threads_${hash}`, publishedAt: new Date() },
    });
    await audit(ctx, "threads.post.simulated", "QuickPost", post.id, "[모의] 스레드 이미지 게시");
    return done;
  }

  const t = await usableToken(ctx.organizationId, deps);
  if (!t) throw new Error("Threads 토큰을 불러올 수 없습니다. 계정을 다시 연결하세요.");
  const imageUrl = `${threadsConfig().publicBaseUrl}/media/${file}`;
  try {
    const r = await publishImage({ userId: t.userId, token: t.token, imageUrl, text }, deps);
    const done = await prisma.quickPost.update({
      where: { id: post.id },
      data: { status: "PUBLISHED", containerId: r.containerId, externalId: r.mediaId, permalink: r.permalink, publishedAt: new Date() },
    });
    await audit(ctx, "threads.post.live", "QuickPost", post.id, `스레드 게시 완료${r.permalink ? ` (${r.permalink})` : ""}`);
    return done;
  } catch (e) {
    const code = e instanceof ThreadsApiError ? e.code : "UNKNOWN";
    const message = e instanceof Error ? e.message : "알 수 없는 오류";
    const failed = await prisma.quickPost.update({ where: { id: post.id }, data: { status: "FAILED", errorCode: code, errorMessage: message } });
    if (code === "AUTH") await prisma.connectedAccount.update({ where: { id: t.accountId }, data: { lastError: "토큰 만료 또는 권한 없음 — 다시 연결하세요." } });
    await audit(ctx, "threads.post.failed", "QuickPost", post.id, `스레드 게시 실패 (${code})`);
    return failed;
  }
}

export async function listQuickPosts(ctx: Ctx) {
  assertCan(ctx, "campaign:read");
  return prisma.quickPost.findMany({
    where: { organizationId: ctx.organizationId },
    orderBy: { createdAt: "desc" },
    take: 30,
    include: { createdBy: { select: { name: true } } },
  });
}
