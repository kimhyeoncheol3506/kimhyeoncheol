import { prisma } from "@/lib/db";
import type { Ctx } from "./context";

/**
 * 사용자 → 요청 컨텍스트. 접근 가능한 고객 = 개인 배정(ClientAccess) ∪ 소속 팀의 고객 ∪ 본인이 팀장인 팀의 고객.
 */
export async function loadCtx(userId: string): Promise<Ctx | null> {
  const user = await prisma.user.findUnique({
    where: { id: userId },
    include: { clientAccess: { select: { clientId: true } }, leadsTeams: { select: { id: true } } },
  });
  if (!user || !user.active) return null;
  const teamIds = [...new Set([user.teamId, ...user.leadsTeams.map((t) => t.id)].filter((x): x is string => !!x))];
  const teamClients = teamIds.length
    ? await prisma.client.findMany({ where: { organizationId: user.organizationId, teamId: { in: teamIds } }, select: { id: true } })
    : [];
  return {
    userId: user.id,
    organizationId: user.organizationId,
    role: user.role,
    name: user.name,
    clientIds: [...new Set([...user.clientAccess.map((a) => a.clientId), ...teamClients.map((c) => c.id)])],
  };
}
