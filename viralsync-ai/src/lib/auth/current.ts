import "server-only";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { cache } from "react";
import { loadCtx } from "./load-ctx";
import { SESSION_COOKIE, verifySession } from "./session";
import type { Ctx } from "./context";

export const getCtx = cache(async (): Promise<Ctx | null> => {
  const store = await cookies();
  const userId = await verifySession(store.get(SESSION_COOKIE)?.value);
  if (!userId) return null;
  return loadCtx(userId);
});

export async function requireCtx(): Promise<Ctx> {
  const ctx = await getCtx();
  if (!ctx) redirect("/login");
  return ctx;
}
