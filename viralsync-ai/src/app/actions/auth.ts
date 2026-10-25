"use server";
import bcrypt from "bcryptjs";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { z } from "zod";
import { prisma } from "@/lib/db";
import { SESSION_COOKIE, sessionCookieOptions, signSession } from "@/lib/auth/session";
import type { ActionState } from "@/lib/action-state";
import { demoAccountsUsable, demoLoginAllowed } from "@/lib/auth/demo";

const loginSchema = z.object({
  email: z.string().trim().toLowerCase().email("이메일 형식이 올바르지 않습니다."),
  password: z.string().min(1, "비밀번호를 입력하세요."),
});

async function startSession(userId: string, organizationId: string) {
  await prisma.user.update({ where: { id: userId }, data: { lastLoginAt: new Date() } });
  await prisma.auditLog.create({ data: { organizationId, actorId: userId, action: "auth.login", entityType: "User", entityId: userId, summary: "로그인" } });
  const store = await cookies();
  store.set(SESSION_COOKIE, await signSession(userId), sessionCookieOptions);
}

export async function login(_prev: ActionState, fd: FormData): Promise<ActionState> {
  const parsed = loginSchema.safeParse({ email: fd.get("email"), password: fd.get("password") });
  if (!parsed.success) return { ok: false, message: parsed.error.issues[0].message };
  try {
    const user = await prisma.user.findUnique({ where: { email: parsed.data.email } });
    // 계정 존재 여부를 노출하지 않도록 동일 메시지
    if (!user || !user.active || !(await bcrypt.compare(parsed.data.password, user.passwordHash)))
      return { ok: false, message: "이메일 또는 비밀번호가 올바르지 않습니다." };
    if (user.isDemo && !(await demoAccountsUsable()))
      return { ok: false, message: "데모 계정은 이 PC(localhost)에서만 사용할 수 있습니다. 직원·권한 화면에서 만든 본인 계정으로 로그인하세요." };
    await startSession(user.id, user.organizationId);
  } catch (e) {
    console.error(e);
    return { ok: false, message: "로그인 처리 중 오류가 발생했습니다. 데이터베이스 연결을 확인하세요." };
  }
  redirect("/dashboard");
}

/** 데모 모드 전용: 비밀번호 없이 데모 계정으로 로그인 */
export async function demoLogin(fd: FormData) {
  if (!(await demoLoginAllowed())) redirect("/login?error=demo_disabled");
  const email = String(fd.get("email") ?? "");
  const user = await prisma.user.findUnique({ where: { email } });
  if (!user || !user.isDemo || !user.active) redirect("/login?error=demo_missing");
  await startSession(user.id, user.organizationId);
  redirect("/dashboard");
}

export async function logout() {
  const store = await cookies();
  store.delete(SESSION_COOKIE);
  redirect("/login");
}
