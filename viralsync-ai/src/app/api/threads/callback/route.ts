import { NextResponse, type NextRequest } from "next/server";
import { getCtx } from "@/lib/auth/current";
import { connectWithCode } from "@/lib/services/threads";

/** Threads OAuth 콜백: state 검증 → 토큰 교환·암호화 저장 */
export async function GET(req: NextRequest) {
  const ctx = await getCtx();
  if (!ctx) return NextResponse.redirect(new URL("/login", req.url));
  const sp = req.nextUrl.searchParams;
  const back = (q: string) => {
    const res = NextResponse.redirect(new URL(`/threads?${q}`, req.url));
    res.cookies.delete("vs_threads_state");
    return res;
  };
  if (sp.get("error")) return back("error=denied");
  const code = sp.get("code");
  const state = sp.get("state");
  if (!code || !state || state !== req.cookies.get("vs_threads_state")?.value) return back("error=state");
  try {
    await connectWithCode(ctx, code);
  } catch (e) {
    console.error("[threads] connect failed:", e instanceof Error ? e.message : e);
    return back("error=connect");
  }
  return back("connected=1");
}
