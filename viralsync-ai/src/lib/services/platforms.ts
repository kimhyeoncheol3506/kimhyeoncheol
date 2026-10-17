import type { IntegrationStatus, PlatformKey } from "@prisma/client";
import { prisma } from "@/lib/db";
import { allAdapters } from "@/lib/adapters/platforms";
import type { Ctx } from "@/lib/auth/context";
import { can } from "@/lib/auth/permissions";

export interface PlatformStatusRow {
  key: PlatformKey;
  name: string;
  status: IntegrationStatus;
  docsUrl: string;
  apiNotes: string;
  livePublishImplemented: boolean;
  /** account:manage 권한이 있을 때만 채워짐 (변수명만, 값은 절대 포함하지 않음) */
  missingEnv: string[] | null;
  accounts: { id: string; accountName: string; status: IntegrationStatus; tokenHint: string | null; isDemo: boolean; lastError: string | null }[];
  maxTextLength: number;
  dailyLimit: number;
  policyUrl: string;
}

export async function platformStatuses(ctx: Ctx): Promise<PlatformStatusRow[]> {
  const showSecrets = can(ctx.role, "account:manage");
  const [platforms, accounts] = await Promise.all([
    prisma.socialPlatform.findMany(),
    prisma.connectedAccount.findMany({ where: { organizationId: ctx.organizationId } }),
  ]);
  return allAdapters().map((a) => {
    const sp = platforms.find((p) => p.key === a.key);
    const acc = accounts.filter((x) => x.platform === a.key);
    const primary = acc.find((x) => !x.isDemo) ?? acc[0] ?? null;
    return {
      key: a.key,
      name: a.name,
      status: a.status(primary && !primary.isDemo ? primary : null),
      docsUrl: a.docsUrl,
      apiNotes: a.apiNotes,
      livePublishImplemented: a.livePublishImplemented,
      missingEnv: showSecrets ? a.missingEnv() : null,
      accounts: acc.map((x) => ({
        id: x.id,
        accountName: x.accountName,
        status: x.status,
        tokenHint: showSecrets ? x.tokenHint : null,
        isDemo: x.isDemo,
        lastError: x.lastError,
      })),
      maxTextLength: sp?.maxTextLength ?? 0,
      dailyLimit: sp?.dailyLimit ?? 0,
      policyUrl: sp?.policyUrl ?? "",
    };
  });
}
