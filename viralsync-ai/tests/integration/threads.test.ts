import { mkdtempSync } from "fs";
import os from "os";
import path from "path";
import { afterEach, beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { prisma } from "@/lib/db";
import { ForbiddenError } from "@/lib/auth/context";
import { connectWithToken, createQuickPost, listQuickPosts, threadsStatus } from "@/lib/services/threads";
import { readImage } from "@/lib/threads/storage";
import type { ThreadsDeps } from "@/lib/threads/client";
import { ctxOf, makeOrg } from "./helpers";

const PNG = new Uint8Array([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a, 9, 9, 9]);
let A: Awaited<ReturnType<typeof makeOrg>>;
let B: Awaited<ReturnType<typeof makeOrg>>;

function fakeThreads(script: Record<string, unknown>[]): ThreadsDeps & { urls: string[]; bodies: string[] } {
  const urls: string[] = [];
  const bodies: string[] = [];
  return {
    urls,
    bodies,
    fetch: (async (u: string | URL | Request, init?: RequestInit) => {
      urls.push(String(u));
      bodies.push(String(init?.body ?? ""));
      const next = script.shift() ?? {};
      const status = typeof next.__status === "number" ? next.__status : 200;
      return new Response(JSON.stringify(next), { status });
    }) as unknown as typeof fetch,
    sleep: async () => {},
  };
}

beforeAll(async () => {
  A = await makeOrg("th-a");
  B = await makeOrg("th-b");
});
beforeEach(() => {
  vi.stubEnv("UPLOAD_DIR", mkdtempSync(path.join(os.tmpdir(), "vs-uploads-")));
  vi.stubEnv("TOKEN_ENCRYPTION_KEY", "test-encryption-key-0123456789abcdef");
  vi.stubEnv("THREADS_APP_SECRET", "");
});
afterEach(() => vi.unstubAllEnvs());

describe("스레드 바로 올리기", () => {
  it("simulated posting works without any connection", async () => {
    vi.stubEnv("PUBLIC_BASE_URL", "");
    const m = await ctxOf(A.users.manager.id);
    const p = await createQuickPost(m, { image: PNG, caption: "협찬 받은 신메뉴", isAd: true, mode: "SIMULATED" });
    expect(p.status).toBe("PUBLISHED");
    expect(p.mode).toBe("SIMULATED");
    expect(p.caption).toBe("협찬 받은 신메뉴");
    expect(await readImage(p.imageFile)).not.toBeNull();
  });

  it("blocks live posting until account + public URL exist", async () => {
    vi.stubEnv("PUBLIC_BASE_URL", "http://localhost:3100");
    const m = await ctxOf(A.users.manager.id);
    const st = await threadsStatus(m);
    expect(st.canPublishLive).toBe(false);
    expect(st.problems.join(" ")).toContain("https");
    await expect(createQuickPost(m, { image: PNG, caption: "", isAd: false, mode: "LIVE" })).rejects.toThrow("실제 게시를 할 수 없습니다");
  });

  it("only admins connect; the token is stored encrypted", async () => {
    const deps = fakeThreads([{ id: "777", username: "aimax_ad" }]);
    await expect(connectWithToken(await ctxOf(A.users.manager.id), "THAA" + "x".repeat(40), deps)).rejects.toBeInstanceOf(ForbiddenError);
    const name = await connectWithToken(await ctxOf(A.users.admin.id), "THAA" + "x".repeat(40), deps);
    expect(name).toBe("@aimax_ad");
    const acc = await prisma.connectedAccount.findFirstOrThrow({ where: { organizationId: A.org.id, platform: "THREADS", isDemo: false } });
    expect(acc.encryptedToken).toBeTruthy();
    expect(acc.encryptedToken).not.toContain("THAA");
    expect(acc.tokenHint).toBe("****xxxx");
    expect(acc.externalUserId).toBe("777");
  });

  it("publishes live with the public image URL and records the permalink", async () => {
    vi.stubEnv("PUBLIC_BASE_URL", "https://ad.example.com");
    const m = await ctxOf(A.users.manager.id);
    expect((await threadsStatus(m)).canPublishLive).toBe(true);
    const deps = fakeThreads([{ id: "C9" }, { status: "FINISHED" }, { id: "M9" }, { permalink: "https://www.threads.com/@aimax_ad/post/xyz" }]);
    const p = await createQuickPost(m, { image: PNG, caption: "오늘의 스샷", isAd: false, mode: "LIVE" }, deps);
    expect(p.status).toBe("PUBLISHED");
    expect(p.permalink).toBe("https://www.threads.com/@aimax_ad/post/xyz");
    expect(deps.urls[0]).toBe("https://graph.threads.com/v1.0/777/threads");
    expect(new URLSearchParams(deps.bodies[0]).get("image_url")).toBe(`https://ad.example.com/media/${p.imageFile}`);
    expect(new URLSearchParams(deps.bodies[0]).get("access_token")).toBe("THAA" + "x".repeat(40)); // 복호화된 토큰으로 호출
  });

  it("records failures and flags the account on auth errors", async () => {
    vi.stubEnv("PUBLIC_BASE_URL", "https://ad.example.com");
    const m = await ctxOf(A.users.manager.id);
    const deps = fakeThreads([{ __status: 400, error: { message: "Error validating access token", code: 190 } }]);
    const p = await createQuickPost(m, { image: PNG, caption: "", isAd: false, mode: "LIVE" }, deps);
    expect(p.status).toBe("FAILED");
    expect(p.errorCode).toBe("AUTH");
    const acc = await prisma.connectedAccount.findFirstOrThrow({ where: { organizationId: A.org.id, platform: "THREADS", isDemo: false } });
    expect(acc.lastError).toContain("다시 연결");
  });

  it("rejects non-images, over-long text and other roles; isolates organizations", async () => {
    const m = await ctxOf(A.users.manager.id);
    await expect(createQuickPost(m, { image: new TextEncoder().encode("not image"), caption: "", isAd: false, mode: "SIMULATED" })).rejects.toThrow("이미지");
    await expect(createQuickPost(m, { image: PNG, caption: "가".repeat(501), isAd: false, mode: "SIMULATED" })).rejects.toThrow("너무 깁니다");
    await expect(createQuickPost(await ctxOf(A.users.writer.id), { image: PNG, caption: "", isAd: false, mode: "SIMULATED" })).rejects.toBeInstanceOf(ForbiddenError);
    expect(await listQuickPosts(await ctxOf(B.users.admin.id))).toHaveLength(0);
    expect((await listQuickPosts(m)).length).toBeGreaterThan(0);
  });
});
