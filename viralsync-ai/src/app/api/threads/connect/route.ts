import { randomBytes } from "crypto";
import { NextResponse } from "next/server";
import { getCtx } from "@/lib/auth/current";
import { can } from "@/lib/auth/permissions";
import { THREADS_AUTH, threadsConfig } from "@/lib/threads/config";

/** Threads 로그인(OAuth) 시작 */
export async function GET(req: Request) {
  const ctx = await getCtx();
  if (!ctx) return NextResponse.redirect(new URL("/login", req.url));
  if (!can(ctx.role, "account:manage")) return NextResponse.redirect(new URL("/threads?error=forbidden", req.url));
  const cfg = threadsConfig();
  if (!cfg.appId || !cfg.redirectUri) return NextResponse.redirect(new URL("/threads?error=not_configured", req.url));
  const state = randomBytes(16).toString("hex");
  const url = new URL(THREADS_AUTH);
  url.searchParams.set("client_id", cfg.appId);
  url.searchParams.set("redirect_uri", cfg.redirectUri);
  url.searchParams.set("scope", "threads_basic,threads_content_publish");
  url.searchParams.set("response_type", "code");
  url.searchParams.set("state", state);
  const res = NextResponse.redirect(url);
  res.cookies.set("vs_threads_state", state, { httpOnly: true, sameSite: "lax", secure: process.env.NODE_ENV === "production", path: "/", maxAge: 600 });
  return res;
}
