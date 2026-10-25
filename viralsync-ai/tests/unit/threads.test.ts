import { describe, expect, it, vi } from "vitest";
import { decryptToken, encryptToken } from "@/lib/threads/crypto";
import { threadsLength, withAdDisclosure } from "@/lib/threads/text";
import { validateImage } from "@/lib/threads/storage";
import { publishImage, ThreadsApiError, type ThreadsDeps } from "@/lib/threads/client";

const PNG = new Uint8Array([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a, 1, 2, 3]);
const JPG = new Uint8Array([0xff, 0xd8, 0xff, 0xe0, 1, 2]);
const HEIC = new Uint8Array([0, 0, 0, 24, ...Buffer.from("ftypheic"), 0, 0]);

describe("token crypto", () => {
  it("round-trips and does not contain the plaintext", () => {
    const enc = encryptToken("THAA-secret-token-1234", "k".repeat(32));
    expect(enc).not.toContain("secret");
    expect(decryptToken(enc, "k".repeat(32))).toBe("THAA-secret-token-1234");
  });
  it("rejects a wrong key or tampered payload", () => {
    const enc = encryptToken("abc", "k".repeat(32));
    expect(() => decryptToken(enc, "x".repeat(32))).toThrow();
    expect(() => decryptToken(enc.slice(0, -4) + "AAAA", "k".repeat(32))).toThrow();
    expect(() => encryptToken("abc", "short")).toThrow("TOKEN_ENCRYPTION_KEY");
  });
});

describe("text rules", () => {
  it("counts emoji by UTF-8 bytes", () => {
    expect(threadsLength("안녕")).toBe(2);
    expect(threadsLength("👍")).toBe(4);
  });
  it("adds #광고 only when needed", () => {
    expect(withAdDisclosure("새 메뉴 출시", true)).toBe("새 메뉴 출시\n\n#광고");
    expect(withAdDisclosure("새 메뉴 #협찬", true)).toBe("새 메뉴 #협찬");
    expect(withAdDisclosure("일상", false)).toBe("일상");
    expect(withAdDisclosure("", true)).toBe("#광고");
  });
});

describe("validateImage", () => {
  it("accepts PNG/JPEG by signature and explains unsupported formats", () => {
    expect(validateImage(PNG)).toEqual({ ok: true, mime: "image/png" });
    expect(validateImage(JPG)).toEqual({ ok: true, mime: "image/jpeg" });
    const heic = validateImage(HEIC);
    expect(heic.ok).toBe(false);
    expect(!heic.ok && heic.message).toContain("HEIC");
    expect(validateImage(new TextEncoder().encode("hello")).ok).toBe(false);
    expect(validateImage(new Uint8Array(8 * 1024 * 1024 + 1).fill(0xff)).ok).toBe(false);
  });
});

function mockThreads(responses: Array<{ status?: number; body: unknown }>) {
  const calls: { url: string; init?: RequestInit }[] = [];
  const deps: ThreadsDeps = {
    fetch: vi.fn(async (url: string | URL | Request, init?: RequestInit) => {
      calls.push({ url: String(url), init });
      const r = responses.shift() ?? { body: {} };
      return new Response(JSON.stringify(r.body), { status: r.status ?? 200 });
    }) as unknown as typeof fetch,
    sleep: vi.fn(async () => {}),
  };
  return { deps, calls };
}

describe("publishImage", () => {
  it("creates a container, waits until FINISHED, publishes and reads the permalink", async () => {
    const { deps, calls } = mockThreads([
      { body: { id: "C1" } },
      { body: { status: "IN_PROGRESS" } },
      { body: { status: "FINISHED" } },
      { body: { id: "M1" } },
      { body: { permalink: "https://www.threads.com/@me/post/abc" } },
    ]);
    const r = await publishImage({ userId: "U1", token: "TOKEN", imageUrl: "https://app.example/media/x.png", text: "hello" }, deps, { pollMs: 10 });
    expect(r).toEqual({ containerId: "C1", mediaId: "M1", permalink: "https://www.threads.com/@me/post/abc" });
    expect(calls[0].url).toBe("https://graph.threads.com/v1.0/U1/threads");
    const body = new URLSearchParams(String(calls[0].init?.body));
    expect(body.get("media_type")).toBe("IMAGE");
    expect(body.get("image_url")).toBe("https://app.example/media/x.png");
    expect(body.get("text")).toBe("hello");
    expect(calls[1].url).toContain("/v1.0/C1?fields=status%2Cerror_message");
    expect(calls[3].url).toBe("https://graph.threads.com/v1.0/U1/threads_publish");
    expect(new URLSearchParams(String(calls[3].init?.body)).get("creation_id")).toBe("C1");
    expect(deps.sleep).toHaveBeenCalledTimes(1);
  });

  it("reports container errors and auth errors without leaking the token", async () => {
    const a = mockThreads([{ body: { id: "C1" } }, { body: { status: "ERROR", error_message: "image download failed" } }]);
    await expect(publishImage({ userId: "U", token: "SECRET_TOKEN", imageUrl: "https://x.example/a.png", text: "" }, a.deps)).rejects.toMatchObject({ code: "CONTAINER_ERROR" });
    const b = mockThreads([{ status: 400, body: { error: { message: "Invalid OAuth access token", code: 190 } } }]);
    const err = await publishImage({ userId: "U", token: "SECRET_TOKEN", imageUrl: "https://x.example/a.png", text: "" }, b.deps).catch((e) => e);
    expect(err).toBeInstanceOf(ThreadsApiError);
    expect(err.code).toBe("AUTH");
    expect(err.message).not.toContain("SECRET_TOKEN");
  });

  it("times out instead of waiting forever", async () => {
    const { deps } = mockThreads([{ body: { id: "C1" } }, ...Array.from({ length: 10 }, () => ({ body: { status: "IN_PROGRESS" } }))]);
    await expect(publishImage({ userId: "U", token: "T", imageUrl: "https://x.example/a.png", text: "" }, deps, { pollMs: 10, maxWaitMs: 30 })).rejects.toMatchObject({ code: "CONTAINER_TIMEOUT" });
  });
});
