import "server-only";
import { Prisma } from "@prisma/client";
import { ForbiddenError, NotFoundError } from "@/lib/auth/context";
import type { ActionState } from "@/lib/action-state";

/** 서비스 오류를 사용자에게 보여 줄 메시지로 변환. 예상치 못한 오류는 상세를 숨긴다. */
export function toActionError(e: unknown): ActionState {
  if (e instanceof ForbiddenError || e instanceof NotFoundError) return { ok: false, message: e.message };
  if (e instanceof Prisma.PrismaClientKnownRequestError) {
    console.error("[db]", e.code);
    if (e.code === "P2002") return { ok: false, message: "이미 존재하는 값입니다 (중복)." };
    return { ok: false, message: "데이터베이스 처리 중 오류가 발생했습니다." };
  }
  if (e instanceof Prisma.PrismaClientInitializationError) return { ok: false, message: "데이터베이스에 연결할 수 없습니다. DATABASE_URL 설정을 확인하세요." };
  if (e instanceof Error && !(e instanceof Prisma.PrismaClientUnknownRequestError)) return { ok: false, message: e.message };
  console.error(e);
  return { ok: false, message: "알 수 없는 오류가 발생했습니다." };
}
