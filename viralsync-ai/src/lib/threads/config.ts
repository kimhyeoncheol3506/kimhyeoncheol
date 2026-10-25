import "server-only";

/** Threads 연동 설정 (서버 환경변수). 값 자체는 화면·로그에 노출하지 않는다. */
export function threadsConfig() {
  const appId = process.env.THREADS_APP_ID?.trim() || null;
  const appSecret = process.env.THREADS_APP_SECRET?.trim() || null;
  const redirectUri = process.env.THREADS_REDIRECT_URI?.trim() || null;
  const publicBaseUrl = process.env.PUBLIC_BASE_URL?.trim().replace(/\/+$/, "") || null;
  const encryptionKey = process.env.TOKEN_ENCRYPTION_KEY?.trim() || null;
  return { appId, appSecret, redirectUri, publicBaseUrl, encryptionKey };
}

/** Threads 서버가 이미지를 가져갈 수 있는 공개 https 주소인지 */
export function publicUrlProblem(base: string | null): string | null {
  if (!base) return "PUBLIC_BASE_URL 이 설정되지 않았습니다.";
  let u: URL;
  try {
    u = new URL(base);
  } catch {
    return "PUBLIC_BASE_URL 형식이 올바르지 않습니다.";
  }
  if (u.protocol !== "https:") return "PUBLIC_BASE_URL 은 https 주소여야 합니다.";
  if (/^(localhost|127\.|10\.|192\.168\.|0\.)/.test(u.hostname) || !u.hostname.includes(".")) return "PUBLIC_BASE_URL 이 외부에서 접속할 수 없는 주소입니다.";
  return null;
}

export { THREADS_API, THREADS_AUTH } from "./config.shared";
