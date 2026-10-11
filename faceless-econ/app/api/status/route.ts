import { NextResponse } from "next/server";
import { loadStore } from "@/lib/store";
import { dailyQuota, hasApiKey, quotaUsedToday } from "@/lib/youtube/client";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

export function GET() {
  const s = loadStore();
  return NextResponse.json({
    apiKeyConfigured: hasApiKey(), // 키 값 자체는 절대 반환하지 않음
    quotaUsedToday: quotaUsedToday(),
    dailyQuota: dailyQuota(),
    realVideos: Object.values(s.videos).filter((v) => v.source === "real").length,
    snapshots: s.snapshots.length,
    lastRun: s.runs[0] ?? null,
  });
}
