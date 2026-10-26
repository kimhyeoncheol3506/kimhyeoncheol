import type { Prisma } from "@prisma/client";
import { prisma } from "@/lib/db";
import { assertCan, canAccessClient, clientWhere, NotFoundError, type Ctx } from "@/lib/auth/context";
import { can } from "@/lib/auth/permissions";
import type { ClientInput } from "@/lib/validation/schemas";
import { audit } from "./audit";

export const PAGE_SIZE = 10;

export async function listClients(ctx: Ctx, opts: { q?: string; page?: number; sort?: string } = {}) {
  assertCan(ctx, "client:read");
  const page = Math.max(1, opts.page ?? 1);
  const where: Prisma.ClientWhereInput = {
    ...clientWhere(ctx),
    ...(opts.q ? { OR: [{ name: { contains: opts.q, mode: "insensitive" } }, { contactName: { contains: opts.q, mode: "insensitive" } }] } : {}),
  };
  const orderBy: Prisma.ClientOrderByWithRelationInput =
    opts.sort === "name" ? { name: "asc" } : opts.sort === "budget" ? { budget: "desc" } : { createdAt: "desc" };
  const [total, rows] = await Promise.all([
    prisma.client.count({ where }),
    prisma.client.findMany({
      where,
      orderBy,
      skip: (page - 1) * PAGE_SIZE,
      take: PAGE_SIZE,
      include: {
        manager: { select: { name: true } },
        _count: { select: { campaigns: { where: { deletedAt: null } } } },
      },
    }),
  ]);
  const showPii = can(ctx.role, "client:pii");
  return {
    total,
    page,
    pageCount: Math.max(1, Math.ceil(total / PAGE_SIZE)),
    rows: rows.map((c) => maskClient(c, showPii)),
  };
}

/** 개인정보·계약 정보 권한이 없으면 마스킹 */
function maskClient<T extends { contactEmail: string | null; contactPhone: string | null; budget: number; contractStart: Date | null; contractEnd: Date | null }>(
  c: T,
  showPii: boolean,
): T & { piiHidden: boolean } {
  if (showPii) return { ...c, piiHidden: false };
  return { ...c, contactEmail: null, contactPhone: null, budget: 0, contractStart: null, contractEnd: null, piiHidden: true };
}

export async function getClient(ctx: Ctx, id: string) {
  assertCan(ctx, "client:read");
  const c = await prisma.client.findFirst({
    where: { ...clientWhere(ctx), id },
    include: {
      brandProfile: true,
      manager: { select: { id: true, name: true } },
      campaigns: { where: { deletedAt: null }, orderBy: { createdAt: "desc" }, include: { brief: { select: { title: true, targetType: true } } } },
    },
  });
  if (!c) throw new NotFoundError();
  const out = maskClient(c, can(ctx.role, "client:pii"));
  // 사장님 링크는 고객 수정 권한이 있는 사람에게만
  return can(ctx.role, "client:write") ? out : { ...out, portalToken: null };
}

export async function listClientOptions(ctx: Ctx) {
  return prisma.client.findMany({ where: clientWhere(ctx), select: { id: true, name: true, isDemo: true }, orderBy: { name: "asc" } });
}

async function assertManagerInOrg(ctx: Ctx, managerId?: string, teamId?: string) {
  if (teamId && !(await prisma.team.findFirst({ where: { id: teamId, organizationId: ctx.organizationId } }))) throw new NotFoundError("팀을 찾을 수 없습니다.");
  if (!managerId) return;
  const u = await prisma.user.findFirst({ where: { id: managerId, organizationId: ctx.organizationId } });
  if (!u) throw new NotFoundError("담당 직원을 찾을 수 없습니다.");
}

function brandData(input: ClientInput) {
  return {
    companyIntro: input.companyIntro,
    productDescription: input.productDescription,
    coreTarget: input.coreTarget,
    bannedPhrases: input.bannedPhrases,
    requiredPhrases: input.requiredPhrases,
    toneOfVoice: input.toneOfVoice,
  };
}

export async function createClient(ctx: Ctx, input: ClientInput) {
  assertCan(ctx, "client:write");
  await assertManagerInOrg(ctx, input.managerId, input.teamId);
  return prisma.$transaction(async (tx) => {
    const c = await tx.client.create({
      data: {
        organizationId: ctx.organizationId,
        name: input.name,
        contactName: input.contactName,
        contactEmail: input.contactEmail ?? null,
        contactPhone: input.contactPhone || null,
        promoUrl: input.promoUrl ?? null,
        budget: input.budget,
        contractStart: input.contractStart ?? null,
        contractEnd: input.contractEnd ?? null,
        managerId: input.managerId ?? null,
        teamId: input.teamId ?? null,
        industry: input.industry,
        ownAccount: input.ownAccount,
        brandProfile: { create: brandData(input) },
      },
    });
    // 관리자가 아닌 등록자는 자신이 만든 고객에 자동 배정
    if (ctx.role !== "ADMIN") await tx.clientAccess.create({ data: { userId: ctx.userId, clientId: c.id } });
    if (input.managerId && input.managerId !== ctx.userId)
      await tx.clientAccess.upsert({
        where: { userId_clientId: { userId: input.managerId, clientId: c.id } },
        create: { userId: input.managerId, clientId: c.id },
        update: {},
      });
    await audit(ctx, "client.create", "Client", c.id, `고객 '${c.name}' 등록`, undefined, tx);
    return c;
  });
}

export async function updateClient(ctx: Ctx, id: string, input: ClientInput) {
  assertCan(ctx, "client:write");
  if (!canAccessClient(ctx, id)) throw new NotFoundError();
  const existing = await prisma.client.findFirst({ where: { ...clientWhere(ctx), id } });
  if (!existing) throw new NotFoundError();
  await assertManagerInOrg(ctx, input.managerId, input.teamId);
  return prisma.$transaction(async (tx) => {
    const c = await tx.client.update({
      where: { id },
      data: {
        name: input.name,
        contactName: input.contactName,
        contactEmail: input.contactEmail ?? null,
        contactPhone: input.contactPhone || null,
        promoUrl: input.promoUrl ?? null,
        budget: input.budget,
        contractStart: input.contractStart ?? null,
        contractEnd: input.contractEnd ?? null,
        managerId: input.managerId ?? null,
        teamId: input.teamId ?? null,
        industry: input.industry,
        ownAccount: input.ownAccount,
        brandProfile: { upsert: { create: brandData(input), update: brandData(input) } },
      },
    });
    await audit(ctx, "client.update", "Client", id, `고객 '${c.name}' 정보 수정`, undefined, tx);
    return c;
  });
}

export async function softDeleteClient(ctx: Ctx, id: string) {
  assertCan(ctx, "client:write");
  const existing = await prisma.client.findFirst({ where: { ...clientWhere(ctx), id } });
  if (!existing) throw new NotFoundError();
  await prisma.client.update({ where: { id }, data: { deletedAt: new Date() } });
  await audit(ctx, "client.delete", "Client", id, `고객 '${existing.name}' 삭제(보관)`);
}
