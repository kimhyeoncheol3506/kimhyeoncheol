import { describe, expect, it } from "vitest";
import { briefSchema, clientSchema } from "@/lib/validation/schemas";

describe("briefSchema", () => {
  const base = { clientId: "c1", title: "의뢰", targetType: "APP", goal: "INSTALLS", budget: "1000", desiredPlatforms: ["X"], keywords: "a, b,\nc" };
  it("parses lists and numbers", () => {
    const r = briefSchema.parse(base);
    expect(r.keywords).toEqual(["a", "b", "c"]);
    expect(r.budget).toBe(1000);
  });
  it("requires at least one platform and a valid url", () => {
    expect(briefSchema.safeParse({ ...base, desiredPlatforms: [] }).success).toBe(false);
    expect(briefSchema.safeParse({ ...base, targetUrl: "http://localhost" }).success).toBe(false);
    expect(briefSchema.safeParse({ ...base, startDate: "2026-02-01", endDate: "2026-01-01" }).success).toBe(false);
  });
});

describe("clientSchema", () => {
  it("validates email and contract dates", () => {
    const ok = clientSchema.safeParse({ name: "A", contactName: "B", budget: "0" });
    expect(ok.success).toBe(true);
    expect(clientSchema.safeParse({ name: "A", contactName: "B", budget: "0", contactEmail: "nope" }).success).toBe(false);
    expect(clientSchema.safeParse({ name: "", contactName: "B", budget: "0" }).success).toBe(false);
  });
});
