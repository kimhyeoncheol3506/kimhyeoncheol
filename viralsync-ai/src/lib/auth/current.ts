import "server-only";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { cache } from "react";
import { prisma } from "@/lib/db";
import { SESSION_COOKIE, verifySession } from "./session";
import type { Ctx } from "./context";

export const getCtx = cache(async (): Promise<Ctx | null> => {
  const store = await cookies();
  const userId = await verifySession(store.get(SESSION_COOKIE)?.value);
  if (!userId) return null;
  const user = await prisma.user.findUnique({
    where: { id: userId },
    include: { clientAccess: { select: { clientId: true } } },
  });
  if (!user || !user.active) return null;
  return {
    userId: user.id,
    organizationId: user.organizationId,
    role: user.role,
    name: user.name,
    clientIds: user.clientAccess.map((a) => a.clientId),
  };
});

export async function requireCtx(): Promise<Ctx> {
  const ctx = await getCtx();
  if (!ctx) redirect("/login");
  return ctx;
}
