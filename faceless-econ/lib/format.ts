// 숫자·영상 형식 표시 유틸

import type { VideoFormat } from "./types";

export const NA = "수집 불가";

export function num(n: number | null | undefined): string {
  if (n == null || !Number.isFinite(n)) return NA;
  return Math.round(n).toLocaleString("ko-KR");
}

export function compact(n: number | null | undefined): string {
  if (n == null || !Number.isFinite(n)) return NA;
  if (n >= 1e8) return `${(n / 1e8).toFixed(1)}억`;
  if (n >= 1e4) return `${(n / 1e4).toFixed(1)}만`;
  return Math.round(n).toLocaleString("ko-KR");
}

export function pct(n: number | null | undefined, digits = 2): string {
  if (n == null || !Number.isFinite(n)) return NA;
  return `${(n * 100).toFixed(digits)}%`;
}

export function score(n: number | null | undefined): string {
  if (n == null || !Number.isFinite(n)) return "판정 보류";
  return n.toFixed(1);
}

export const FORMAT_LABELS: Record<VideoFormat, string> = { long: "롱폼", shorts: "쇼츠", other: "기타(라이브 등)" };

/**
 * 영상 형식 판별.
 * API는 쇼츠 여부를 직접 제공하지 않는다. 60초 이하는 쇼츠, 61~180초는 #shorts 표기 또는
 * /shorts/ 주소 확인 결과(있을 때)로 판별하고, 근거를 함께 반환한다.
 */
export function detectFormat(
  durationSec: number | null,
  title: string,
  description: string | null,
  liveContent: "none" | "live" | "upcoming" | "completed",
  shortsUrlCheck: boolean | null = null,
): { format: VideoFormat; evidence: string } {
  if (liveContent !== "none") return { format: "other", evidence: "라이브/예정 방송" };
  if (durationSec == null) return { format: "other", evidence: "영상 길이 수집 불가" };
  if (shortsUrlCheck === true && durationSec <= 180) return { format: "shorts", evidence: "/shorts/ 주소 확인" };
  if (durationSec <= 60) return { format: "shorts", evidence: "60초 이하" };
  if (durationSec <= 180) {
    if (/#shorts?\b/i.test(`${title} ${description ?? ""}`)) return { format: "shorts", evidence: "180초 이하 + #shorts 표기" };
    if (shortsUrlCheck === false) return { format: "long", evidence: "180초 이하지만 /shorts/ 주소 아님" };
    return { format: "shorts", evidence: "180초 이하 (쇼츠 추정 — 주소 확인 못함)" };
  }
  return { format: "long", evidence: "180초 초과" };
}
