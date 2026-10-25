import { NextResponse, type NextRequest } from "next/server";
import { SESSION_COOKIE, verifySession } from "@/lib/auth/session";

// /media: Threads 서버가 로그인 없이 게시 이미지를 가져가는 공개 경로
const PUBLIC = ["/login", "/media/"];

export async function middleware(req: NextRequest) {
  const { pathname } = req.nextUrl;
  if (PUBLIC.some((p) => pathname.startsWith(p))) return NextResponse.next();
  const userId = await verifySession(req.cookies.get(SESSION_COOKIE)?.value);
  if (!userId) {
    if (pathname.startsWith("/api/")) return NextResponse.json({ error: "인증이 필요합니다." }, { status: 401 });
    const url = req.nextUrl.clone();
    url.pathname = "/login";
    url.search = "";
    return NextResponse.redirect(url);
  }
  return NextResponse.next();
}

export const config = { matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"] };
