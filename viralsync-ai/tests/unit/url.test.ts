import { describe, expect, it } from "vitest";
import { checkUrl } from "@/lib/validation/url";

describe("checkUrl", () => {
  it("accepts https URLs and never claims analysis", () => {
    const r = checkUrl("https://www.youtube.com/watch?v=abc");
    expect(r.valid).toBe(true);
    expect(r.analyzed).toBe(false);
    expect(r.platformHint).toBe("YouTube");
  });
  it("rejects malformed, non-http, credentials and private hosts", () => {
    expect(checkUrl("not a url").valid).toBe(false);
    expect(checkUrl("ftp://example.com/x").valid).toBe(false);
    expect(checkUrl("javascript:alert(1)").valid).toBe(false);
    expect(checkUrl("https://user:pw@example.com").valid).toBe(false);
    expect(checkUrl("http://localhost:3000").valid).toBe(false);
    expect(checkUrl("http://192.168.0.1/admin").valid).toBe(false);
    expect(checkUrl("http://10.0.0.5").valid).toBe(false);
    expect(checkUrl("").valid).toBe(false);
  });
});
