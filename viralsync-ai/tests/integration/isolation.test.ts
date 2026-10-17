import { beforeAll, describe, expect, it } from "vitest";
import { ForbiddenError, NotFoundError } from "@/lib/auth/context";
import { createClient, getClient, listClients } from "@/lib/services/clients";
import { createCampaign, getCampaign, listCampaigns, runAnalysis } from "@/lib/services/campaigns";
import { generateContent } from "@/lib/services/content";
import { DemoProvider } from "@/lib/ai/demo-provider";
import { dashboard } from "@/lib/services/reports";
import { setClientAccess } from "@/lib/services/users";
import { clientSchema, briefSchema } from "@/lib/validation/schemas";
import { ctxOf, makeOrg } from "./helpers";

let A: Awaited<ReturnType<typeof makeOrg>>;
let B: Awaited<ReturnType<typeof makeOrg>>;
const ids: Record<string, string> = {};

const client = (name: string) => clientSchema.parse({ name, contactName: "담당", budget: "0" });
const brief = (clientId: string, title: string) =>
  briefSchema.parse({ clientId, title, targetType: "APP", goal: "INSTALLS", budget: "0", desiredPlatforms: ["X"], keywords: "앱", description: "앱 설치 캠페인 설명입니다." });

beforeAll(async () => {
  A = await makeOrg("iso-a");
  B = await makeOrg("iso-b");
  const adminA = await ctxOf(A.users.admin.id);
  const adminB = await ctxOf(B.users.admin.id);
  ids.a1 = (await createClient(adminA, client("A사 고객1"))).id;
  ids.a2 = (await createClient(adminA, client("A사 고객2"))).id;
  ids.b1 = (await createClient(adminB, client("B사 고객"))).id;
  ids.campA2 = (await createCampaign(adminA, brief(ids.a2, "A2 캠페인"))).id;
  ids.campB1 = (await createCampaign(adminB, brief(ids.b1, "B 캠페인"))).id;
  await setClientAccess(adminA, A.users.manager.id, [ids.a1]);
  await setClientAccess(adminA, A.users.writer.id, [ids.a1]);
});

describe("tenant isolation", () => {
  it("never exposes another organization's clients or campaigns", async () => {
    const adminA = await ctxOf(A.users.admin.id);
    await expect(getClient(adminA, ids.b1)).rejects.toBeInstanceOf(NotFoundError);
    await expect(getCampaign(adminA, ids.campB1)).rejects.toBeInstanceOf(NotFoundError);
    await expect(runAnalysis(adminA, ids.campB1)).rejects.toBeInstanceOf(NotFoundError);
    const list = await listClients(adminA, {});
    expect(list.rows.map((r) => r.id)).not.toContain(ids.b1);
    // 다른 조직 고객으로 의뢰 접수 시도
    await expect(createCampaign(adminA, brief(ids.b1, "침투"))).rejects.toBeInstanceOf(NotFoundError);
  });

  it("limits non-admin staff to assigned clients", async () => {
    const manager = await ctxOf(A.users.manager.id);
    const list = await listClients(manager, {});
    expect(list.rows.map((r) => r.id)).toEqual([ids.a1]);
    await expect(getClient(manager, ids.a2)).rejects.toBeInstanceOf(NotFoundError);
    await expect(getCampaign(manager, ids.campA2)).rejects.toBeInstanceOf(NotFoundError);
    expect((await listCampaigns(manager, {})).rows.map((c) => c.id)).not.toContain(ids.campA2);
    const writer = await ctxOf(A.users.writer.id);
    await expect(generateContent(writer, { campaignId: ids.campA2, types: ["COMMENT"] }, new DemoProvider())).rejects.toBeInstanceOf(NotFoundError);
    const d = await dashboard(manager, {});
    expect(d.clients).toBe(1);
  });

  it("enforces role permissions at the service layer", async () => {
    const viewer = await ctxOf(A.users.viewer.id);
    await expect(createClient(viewer, client("불가"))).rejects.toBeInstanceOf(ForbiddenError);
    const manager = await ctxOf(A.users.manager.id);
    await expect(setClientAccess(manager, A.users.viewer.id, [ids.a1])).rejects.toBeInstanceOf(ForbiddenError);
  });
});

describe("regression: id lookups keep the client scope", () => {
  it("does not let a manager create a campaign for an unassigned client", async () => {
    const manager = await ctxOf(A.users.manager.id);
    await expect(createCampaign(manager, brief(ids.a2, "미배정 고객 의뢰"))).rejects.toBeInstanceOf(NotFoundError);
  });
});

describe("regression: client filters cannot widen scope", () => {
  it("returns nothing when a manager filters by an unassigned client", async () => {
    const manager = await ctxOf(A.users.manager.id);
    expect((await listCampaigns(manager, { clientId: ids.a2 })).rows).toHaveLength(0);
    const d = await dashboard(manager, { clientId: ids.a2 });
    expect(d.clients).toBe(0);
    expect(d.activeCampaigns + d.monthRequestCount).toBe(0);
  });
});
