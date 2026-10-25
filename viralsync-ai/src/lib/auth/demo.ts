import "server-only";
import { headers } from "next/headers";

/**
 * 데모 원클릭 로그인 허용 여부.
 * Threads 이미지 게시를 위해 앱을 외부 주소(터널·배포)로 열면 누구나 관리자로 로그인할 수 있게 되므로,
 * 기본적으로 이 PC(localhost)에서 접속할 때만 허용한다. 외부에서도 허용하려면 DEMO_ALLOW_REMOTE=true.
 */
export async function demoLoginAllowed(): Promise<boolean> {
  if (process.env.DEMO_MODE !== "true") return false;
  return demoAccountsUsable();
}

/** 데모 계정(비밀번호가 공개됨)은 로컬 접속에서만 로그인 가능 */
export async function demoAccountsUsable(): Promise<boolean> {
  if (process.env.DEMO_ALLOW_REMOTE === "true") return true;
  const h = await headers();
  // 터널·프록시를 거친 요청은 Host 가 localhost 여도 외부 접속으로 본다.
  // (Next 서버는 로컬 요청에도 x-forwarded-for 에 루프백 주소를 넣으므로 IP 값으로 판단)
  if (h.get("cf-connecting-ip") || h.get("x-real-ip")) return false;
  const ips = (h.get("x-forwarded-for") ?? "").split(",").map((x) => x.trim()).filter(Boolean);
  if (ips.some((ip) => !/^(127\.|::1$|::ffff:127\.)/.test(ip))) return false;
  const host = (h.get("x-forwarded-host") ?? h.get("host") ?? "").split(",")[0].trim().toLowerCase();
  return /^(localhost|127\.0\.0\.1|\[::1\])(:\d+)?$/.test(host);
}
