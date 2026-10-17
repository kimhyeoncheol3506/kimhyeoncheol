import { describe, expect, it } from "vitest";
import { can, seesAllClients } from "@/lib/auth/permissions";
import { campaignWhere, clientWhere, type Ctx } from "@/lib/auth/context";

describe("RBAC matrix", () => {
  it("restricts cost, credentials and approvals to the right roles", () => {
    expect(can("ADMIN", "cost:read")).toBe(true);
    expect(can("CAMPAIGN_MANAGER", "cost:read")).toBe(true);
    expect(can("CONTENT_WRITER", "cost:read")).toBe(false);
    expect(can("REVIEWER", "cost:read")).toBe(false);
    expect(can("VIEWER", "cost:read")).toBe(false);
    expect(can("VIEWER", "client:pii")).toBe(false);
    expect(can("CAMPAIGN_MANAGER", "account:manage")).toBe(false);
    expect(can("ADMIN", "account:manage")).toBe(true);
    expect(can("REVIEWER", "approval:decide")).toBe(true);
    expect(can("CONTENT_WRITER", "approval:decide")).toBe(false);
    expect(can("CONTENT_WRITER", "publication:execute")).toBe(false);
    expect(can("VIEWER", "content:generate")).toBe(false);
  });
  it("scopes non-admin queries to assigned clients and own organization", () => {
    const ctx: Ctx = { userId: "u", organizationId: "org1", role: "CAMPAIGN_MANAGER", name: "x", clientIds: ["c1"] };
    expect(clientWhere(ctx)).toMatchObject({ organizationId: "org1", deletedAt: null, AND: [{ id: { in: ["c1"] } }] });
    // id 를 덧붙여도 배정 범위가 유지되어야 한다 (회귀 방지)
    expect({ ...clientWhere(ctx), id: "c2" }).toMatchObject({ id: "c2", AND: [{ id: { in: ["c1"] } }] });
    expect({ ...campaignWhere(ctx), clientId: "c2" }).toMatchObject({ organizationId: "org1", clientId: "c2", AND: [{ clientId: { in: ["c1"] } }] });
    const admin: Ctx = { ...ctx, role: "ADMIN" };
    expect(clientWhere(admin)).toEqual({ organizationId: "org1", deletedAt: null, AND: [] });
    expect(seesAllClients("ADMIN")).toBe(true);
    expect(seesAllClients("REVIEWER")).toBe(false);
  });
});
