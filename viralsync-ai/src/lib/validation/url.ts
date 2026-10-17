/**
 * 홍보 대상 URL 형식 검사.
 * 외부 사이트에 접속(크롤링)하지 않으며, analyzed 는 항상 false 입니다.
 */
export interface UrlCheckResult {
  valid: boolean;
  normalized?: string;
  host?: string;
  reason: string;
  /** 외부 콘텐츠를 실제로 분석했는지 여부 — MVP 는 크롤링하지 않으므로 항상 false */
  analyzed: false;
  platformHint?: string;
}

const PRIVATE_HOST = [
  /^localhost$/i,
  /^127\./,
  /^10\./,
  /^192\.168\./,
  /^172\.(1[6-9]|2\d|3[01])\./,
  /^169\.254\./,
  /^0\./,
  /^\[?::1\]?$/,
  /\.local$/i,
  /\.internal$/i,
];

const PLATFORM_HINTS: [RegExp, string][] = [
  [/(^|\.)youtube\.com$|(^|\.)youtu\.be$/i, "YouTube"],
  [/(^|\.)instagram\.com$/i, "Instagram"],
  [/(^|\.)tiktok\.com$/i, "TikTok"],
  [/(^|\.)(x|twitter)\.com$/i, "X"],
  [/(^|\.)facebook\.com$/i, "Facebook"],
  [/(^|\.)(blog\.naver\.com|tistory\.com|brunch\.co\.kr|medium\.com)$/i, "블로그"],
  [/(^|\.)(apps\.apple\.com|play\.google\.com)$/i, "앱 스토어"],
];

export function checkUrl(input: string | null | undefined): UrlCheckResult {
  const raw = (input ?? "").trim();
  if (!raw) return { valid: false, reason: "URL 이 입력되지 않았습니다.", analyzed: false };
  let u: URL;
  try {
    u = new URL(raw);
  } catch {
    return { valid: false, reason: "URL 형식이 올바르지 않습니다. https:// 로 시작하는 전체 주소를 입력하세요.", analyzed: false };
  }
  if (u.protocol !== "https:" && u.protocol !== "http:") {
    return { valid: false, reason: "http 또는 https 주소만 허용됩니다.", analyzed: false };
  }
  if (u.username || u.password) {
    return { valid: false, reason: "계정 정보가 포함된 URL 은 허용되지 않습니다.", analyzed: false };
  }
  const host = u.hostname;
  if (PRIVATE_HOST.some((r) => r.test(host)) || !host.includes(".")) {
    return { valid: false, reason: "내부망·로컬 주소는 등록할 수 없습니다.", analyzed: false };
  }
  const platformHint = PLATFORM_HINTS.find(([r]) => r.test(host))?.[1];
  return {
    valid: true,
    normalized: u.toString(),
    host,
    platformHint,
    reason:
      "URL 형식만 확인했습니다. 외부 페이지 내용은 자동 분석하지 않으므로 상품·콘텐츠 설명을 직접 입력해 주세요.",
    analyzed: false,
  };
}
