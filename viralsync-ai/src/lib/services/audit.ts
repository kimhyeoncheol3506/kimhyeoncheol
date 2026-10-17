import type { Prisma } from "@prisma/client";
import { prisma } from "@/lib/db";
import type { Ctx } from "@/lib/auth/context";

const SECRET_KEY = /(token|secret|password|apikey|api_key|authorization)/i;

/** 감사로그 meta 에서 비밀값으로 보이는 키를 제거한다 */
export function redact(meta: Record<string, unknown> | undefined): Record<string, unknown> | undefined {
  if (!meta) return undefined;
  const out: Record<string, unknown> = {};
  for (const [k, v] of Object.entries(meta)) out[k] = SECRET_KEY.test(k) ? "[REDACTED]" : v;
  return out;
}

export async function audit(
  ctx: Ctx,
  action: string,
  entityType: string,
  entityId: string | null,
  summary: string,
  meta?: Record<string, unknown>,
  tx: Prisma.TransactionClient = prisma,
) {
  await tx.auditLog.create({
    data: {
      organizationId: ctx.organizationId,
      actorId: ctx.userId,
      action,
      entityType,
      entityId,
      summary,
      meta: redact(meta) as Prisma.InputJsonValue | undefined,
    },
  });
}
