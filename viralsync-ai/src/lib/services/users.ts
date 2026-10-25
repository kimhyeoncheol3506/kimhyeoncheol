import bcrypt from "bcryptjs";
import type { Role } from "@prisma/client";
import { prisma } from "@/lib/db";
import { assertCan, ForbiddenError, NotFoundError, type Ctx } from "@/lib/auth/context";
import { audit } from "./audit";

export async function listUsers(ctx: Ctx) {
  assertCan(ctx, "user:manage");
  return prisma.user.findMany({
    where: { organizationId: ctx.organizationId },
    orderBy: [{ active: "desc" }, { createdAt: "asc" }],
    select: {
      id: true,
      name: true,
      email: true,
      role: true,
      active: true,
      isDemo: true,
      lastLoginAt: true,
      teamId: true,
      clientAccess: { select: { clientId: true } },
    },
  });
}

export async function createUser(ctx: Ctx, input: { name: string; email: string; role: Role; password: string }) {
  assertCan(ctx, "user:manage");
  const exists = await prisma.user.findUnique({ where: { email: input.email } });
  if (exists) throw new Error("이미 사용 중인 이메일입니다.");
  const u = await prisma.user.create({
    data: {
      organizationId: ctx.organizationId,
      name: input.name,
      email: input.email,
      role: input.role,
      passwordHash: await bcrypt.hash(input.password, 10),
    },
  });
  await audit(ctx, "user.create", "User", u.id, `직원 '${u.name}' 등록 (${u.role})`);
  return u;
}

async function getOrgUser(ctx: Ctx, id: string) {
  const u = await prisma.user.findFirst({ where: { id, organizationId: ctx.organizationId } });
  if (!u) throw new NotFoundError();
  return u;
}

export async function updateUserRole(ctx: Ctx, id: string, role: Role, active: boolean) {
  assertCan(ctx, "user:manage");
  const u = await getOrgUser(ctx, id);
  if (u.id === ctx.userId && (role !== "ADMIN" || !active)) throw new ForbiddenError("본인의 관리자 권한은 해제할 수 없습니다.");
  await prisma.user.update({ where: { id }, data: { role, active } });
  await audit(ctx, "user.update", "User", id, `직원 '${u.name}' 권한 ${u.role} → ${role}${active ? "" : " (비활성)"}`);
}

export async function setClientAccess(ctx: Ctx, userId: string, clientIds: string[]) {
  assertCan(ctx, "user:manage");
  const u = await getOrgUser(ctx, userId);
  const valid = await prisma.client.findMany({ where: { organizationId: ctx.organizationId, id: { in: clientIds } }, select: { id: true } });
  await prisma.$transaction([
    prisma.clientAccess.deleteMany({ where: { userId } }),
    prisma.clientAccess.createMany({ data: valid.map((c) => ({ userId, clientId: c.id })) }),
  ]);
  await audit(ctx, "user.access", "User", userId, `직원 '${u.name}' 고객 접근 권한 ${valid.length}개로 변경`);
}
