import type { Prisma, Role } from "@prisma/client";
import { can, seesAllClients, type Permission } from "./permissions";

/** 서비스 계층에 전달되는 요청 컨텍스트 (테넌트 + 역할 + 접근 가능한 고객) */
export interface Ctx {
  userId: string;
  organizationId: string;
  role: Role;
  name: string;
  /** 관리자가 아닌 경우 접근 가능한 고객 id 목록 */
  clientIds: string[];
}

export class ForbiddenError extends Error {
  constructor(message = "이 작업을 수행할 권한이 없습니다.") {
    super(message);
    this.name = "ForbiddenError";
  }
}

export class NotFoundError extends Error {
  constructor(message = "대상을 찾을 수 없거나 접근 권한이 없습니다.") {
    super(message);
    this.name = "NotFoundError";
  }
}

export function assertCan(ctx: Ctx, permission: Permission): void {
  if (!can(ctx.role, permission)) throw new ForbiddenError();
}

/**
 * Client 조회 where 절 (조직 + 고객 배정 범위 + 미삭제)
 * 배정 범위는 AND 안에 두어 호출부가 `{ ...clientWhere(ctx), id }` 처럼 id 를 덧붙여도 범위가 덮어써지지 않게 한다.
 */
export function clientWhere(ctx: Ctx): Prisma.ClientWhereInput {
  return {
    organizationId: ctx.organizationId,
    deletedAt: null,
    AND: seesAllClients(ctx.role) ? [] : [{ id: { in: ctx.clientIds } }],
  };
}

/** Campaign 조회 where 절 */
export function campaignWhere(ctx: Ctx): Prisma.CampaignWhereInput {
  return {
    organizationId: ctx.organizationId,
    deletedAt: null,
    AND: seesAllClients(ctx.role) ? [] : [{ clientId: { in: ctx.clientIds } }],
  };
}

/** clientId 가 조직 소속이며 사용자 접근 범위인지 */
export function canAccessClient(ctx: Ctx, clientId: string): boolean {
  return seesAllClients(ctx.role) || ctx.clientIds.includes(clientId);
}
