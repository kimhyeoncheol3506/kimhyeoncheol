import { afterEach, describe, expect, it, vi } from "vitest";
import { csvCell, toCsv } from "@/lib/csv";
import { getAdapter } from "@/lib/adapters/platforms";
import { contentHash, finalText, hasDisclosure } from "@/lib/services/publications";

describe("csv", () => {
  it("adds BOM, escapes quotes/commas/newlines and neutralises formulas", () => {
    const out = toCsv(["a", "b"], [["x,y", 'say "hi"'], ["=SUM(A1)", -5]]);
    expect(out.startsWith("﻿")).toBe(true);
    expect(out).toContain('"x,y"');
    expect(out).toContain('"say ""hi"""');
    expect(out).toContain("'=SUM(A1)");
    expect(out).toContain(",-5");
    expect(csvCell(null)).toBe("");
    expect(csvCell("+cmd")).toBe("'+cmd");
  });
});

describe("publication helpers", () => {
  it("appends the disclosure only when missing", () => {
    expect(finalText("본문 #광고", "[광고] x")).toBe("본문 #광고");
    expect(finalText("본문", "[광고] x")).toBe("본문\n\n[광고] x");
    expect(hasDisclosure("Sponsored post")).toBe(true);
    expect(hasDisclosure("그냥 글")).toBe(false);
  });
  it("hashes normalised text per platform and target", () => {
    expect(contentHash("A  b", "X", null)).toBe(contentHash("a b", "X", null));
    expect(contentHash("a b", "X", null)).not.toBe(contentHash("a b", "INSTAGRAM", null));
    expect(contentHash("a b", "X", "https://t.example/1")).not.toBe(contentHash("a b", "X", null));
  });
});

describe("platform adapters", () => {
  afterEach(() => vi.unstubAllEnvs());

  it("reports integration status honestly", () => {
    const x = getAdapter("X");
    vi.stubEnv("X_API_KEY", "");
    vi.stubEnv("X_API_SECRET", "");
    expect(x.status(null)).toBe("DEMO_ONLY");
    vi.stubEnv("X_API_KEY", "k");
    vi.stubEnv("X_API_SECRET", "s");
    expect(x.status(null)).toBe("API_READY");
    // 인증이 완료돼도 실제 게시 호출이 구현되지 않았으므로 '게시 가능'이 아니다
    expect(x.status({ status: "AUTHENTICATED" })).toBe("AUTHENTICATED");
    expect(x.status({ status: "AUTHENTICATED", lastError: "token expired" })).toBe("RESTRICTED");
  });

  it("never publishes for real in the MVP", async () => {
    vi.stubEnv("YOUTUBE_CLIENT_ID", "");
    const r = await getAdapter("YOUTUBE").publishLive({ text: "t", kind: "POST", attempt: 0, maxTextLength: 100 });
    expect(r.ok).toBe(false);
    expect(r.errorCode).toBe("NOT_CONFIGURED");
  });

  it("simulates deterministically and enforces text length", () => {
    const a = getAdapter("INSTAGRAM");
    const req = { text: "hello #광고", kind: "POST" as const, attempt: 0, maxTextLength: 2200 };
    expect(a.simulate(req)).toEqual(a.simulate(req));
    expect(a.simulate({ ...req, text: "x".repeat(300), maxTextLength: 280 }).errorCode).toBe("TEXT_TOO_LONG");
  });
});

describe("simulatedMetrics", () => {
  it("never produces negative or inconsistent numbers (regression: signed shift)", async () => {
    const { simulatedMetrics } = await import("@/lib/services/publications");
    for (let i = 0; i < 2000; i++) {
      const m = simulatedMetrics(`seed-${i}`);
      expect(m.clicks).toBeGreaterThan(0);
      expect(m.visits).toBeGreaterThanOrEqual(0);
      expect(m.conversions).toBeGreaterThanOrEqual(0);
      expect(m.visits).toBeLessThanOrEqual(m.clicks);
      expect(m.conversions).toBeLessThanOrEqual(m.visits);
    }
  });
});
