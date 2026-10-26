import type { ContentType, PlatformKey } from "@prisma/client";

/** 매체별로 AI 팀이 만드는 콘텐츠 묶음 (채널 패키지) */
export const CHANNEL_PACK: Record<PlatformKey, ContentType[]> = {
  THREADS: ["SNS_POST"],
  INSTAGRAM: ["SHORT_SCRIPT", "SNS_POST"],
  YOUTUBE: ["SHORT_SCRIPT", "YOUTUBE_META"],
  FACEBOOK: ["SNS_POST"],
  TIKTOK: ["SHORT_SCRIPT", "SHORT_HOOK"],
  X: ["SNS_POST"],
  BLOG: ["BLOG_COPY"],
};

/** 용역 홍보 기본 매체 — 쓰레드·릴스·유튜브·페이스북·틱톡 */
export const PACK_CHANNELS: PlatformKey[] = ["THREADS", "INSTAGRAM", "YOUTUBE", "FACEBOOK", "TIKTOK"];

export const CHANNEL_LABEL: Record<PlatformKey, string> = {
  THREADS: "쓰레드",
  INSTAGRAM: "인스타 릴스",
  YOUTUBE: "유튜브 (쇼츠·영상)",
  FACEBOOK: "페이스북",
  TIKTOK: "틱톡",
  X: "X",
  BLOG: "블로그",
};

/** 패키지에 포함되는 담당 직원 (숏폼 대본이 있으면 숏폼 PD 참여) */
export function packStaff(platform: PlatformKey): string[] {
  const types = CHANNEL_PACK[platform];
  return [
    ...(types.some((t) => t !== "SHORT_SCRIPT" && t !== "SHORT_HOOK") ? ["copywriter"] : []),
    ...(types.some((t) => t === "SHORT_SCRIPT" || t === "SHORT_HOOK") ? ["shortform"] : []),
  ];
}
