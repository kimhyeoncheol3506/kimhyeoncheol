import { prisma } from "@/lib/db";
import { assertCan, NotFoundError, type Ctx } from "@/lib/auth/context";
import { AI_AGENTS } from "@/lib/approval/agents";
import { audit } from "./audit";

export async function listTeams(ctx: Ctx) {
  return prisma.team.findMany({
    where: { organizationId: ctx.organizationId },
    orderBy: { createdAt: "asc" },
    include: {
      lead: { select: { id: true, name: true, role: true } },
      members: { where: { active: true }, select: { id: true, name: true, role: true }, orderBy: { name: "asc" } },
      clients: { where: { deletedAt: null }, select: { id: true, name: true }, orderBy: { name: "asc" } },
    },
  });
}

export async function orgPeople(ctx: Ctx) {
  return prisma.user.findMany({
    where: { organizationId: ctx.organizationId, active: true },
    select: { id: true, name: true, role: true, teamId: true },
    orderBy: { name: "asc" },
  });
}

export async function saveTeam(ctx: Ctx, id: string | null, input: { name: string; description: string; leadId: string | null }) {
  assertCan(ctx, "user:manage");
  if (!input.name.trim()) throw new Error("팀 이름을 입력하세요.");
  if (input.leadId) {
    const u = await prisma.user.findFirst({ where: { id: input.leadId, organizationId: ctx.organizationId } });
    if (!u) throw new NotFoundError("팀장을 찾을 수 없습니다.");
  }
  const dup = await prisma.team.findFirst({ where: { organizationId: ctx.organizationId, name: input.name.trim(), ...(id ? { NOT: { id } } : {}) } });
  if (dup) throw new Error("같은 이름의 팀이 있습니다.");
  const data = { name: input.name.trim(), description: input.description.trim(), leadId: input.leadId };
  const team = id
    ? await prisma.team.update({ where: { id: (await getTeam(ctx, id)).id }, data })
    : await prisma.team.create({ data: { ...data, organizationId: ctx.organizationId } });
  // 팀장은 자동으로 팀원
  if (input.leadId) await prisma.user.update({ where: { id: input.leadId }, data: { teamId: team.id } });
  await audit(ctx, id ? "team.update" : "team.create", "Team", team.id, `팀 ‘${team.name}’ ${id ? "수정" : "생성"}`);
  return team;
}

async function getTeam(ctx: Ctx, id: string) {
  const t = await prisma.team.findFirst({ where: { id, organizationId: ctx.organizationId } });
  if (!t) throw new NotFoundError();
  return t;
}

export async function deleteTeam(ctx: Ctx, id: string) {
  assertCan(ctx, "user:manage");
  const t = await getTeam(ctx, id);
  await prisma.team.delete({ where: { id } });
  await audit(ctx, "team.delete", "Team", id, `팀 ‘${t.name}’ 삭제 (소속 직원·고객은 미배정으로 변경)`);
}

export async function setUserTeam(ctx: Ctx, userId: string, teamId: string | null) {
  assertCan(ctx, "user:manage");
  if (teamId) await getTeam(ctx, teamId);
  const u = await prisma.user.findFirst({ where: { id: userId, organizationId: ctx.organizationId } });
  if (!u) throw new NotFoundError();
  if (u.teamId !== teamId) await prisma.user.update({ where: { id: userId }, data: { teamId } });
}

/** AI 에이전트별 최근 30일 활동 수 (감사 로그 기준) */
export async function agentActivity(ctx: Ctx) {
  const since = new Date(Date.now() - 30 * 86_400_000);
  const counts = await prisma.auditLog.groupBy({
    by: ["action"],
    where: { organizationId: ctx.organizationId, createdAt: { gte: since } },
    _count: { _all: true },
  });
  const by = new Map(counts.map((c) => [c.action, c._count._all]));
  return Object.fromEntries(AI_AGENTS.map((a) => [a.key, a.auditActions.reduce((n, act) => n + (by.get(act) ?? 0), 0)]));
}
