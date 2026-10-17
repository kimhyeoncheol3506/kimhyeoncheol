import type { Role } from "@prisma/client";

export const PERMISSIONS = [
  "client:read",
  "client:pii", // 담당자 연락처·계약·예산 등 고객 상세정보
  "client:write",
  "campaign:read",
  "campaign:write",
  "analysis:run",
  "candidate:write",
  "content:generate",
  "content:edit",
  "approval:decide",
  "publication:execute",
  "cost:read",
  "account:manage", // SNS 계정 인증정보
  "policy:write",
  "user:manage",
  "report:export",
  "audit:read",
  "inquiry:manage", // 문의 접수·견적·답변·전환
  "service:manage", // 서비스 상품·가격 관리
  "task:update", // 매체별 집행 작업 진행 기록
] as const;

export type Permission = (typeof PERMISSIONS)[number];

const MATRIX: Record<Role, readonly Permission[]> = {
  ADMIN: PERMISSIONS,
  CAMPAIGN_MANAGER: [
    "client:read",
    "client:pii",
    "client:write",
    "campaign:read",
    "campaign:write",
    "analysis:run",
    "candidate:write",
    "content:generate",
    "content:edit",
    "publication:execute",
    "cost:read",
    "report:export",
    "inquiry:manage",
    "task:update",
  ],
  CONTENT_WRITER: [
    "client:read",
    "campaign:read",
    "analysis:run",
    "candidate:write",
    "content:generate",
    "content:edit",
    "task:update",
  ],
  REVIEWER: ["client:read", "campaign:read", "approval:decide", "policy:write", "report:export"],
  VIEWER: ["client:read", "campaign:read"],
};

export function can(role: Role, permission: Permission): boolean {
  return MATRIX[role].includes(permission);
}

export function permissionsOf(role: Role): readonly Permission[] {
  return MATRIX[role];
}

/** 관리자는 조직 내 모든 고객, 그 외 역할은 배정된 고객만 볼 수 있다. */
export function seesAllClients(role: Role): boolean {
  return role === "ADMIN";
}
