import { NextResponse } from "next/server";
import { YouTubeError, hasApiKey } from "@/lib/youtube/client";
import { searchChannels } from "@/lib/youtube/collect";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

export async function POST(req: Request) {
  if (!hasApiKey()) return NextResponse.json({ error: "검색에는 API 키가 필요합니다." }, { status: 400 });
  const { q } = (await req.json()) as { q?: string };
  if (!q?.trim()) return NextResponse.json({ error: "검색어를 입력하세요." }, { status: 400 });
  try {
    const results = await searchChannels(q.trim().slice(0, 80));
    return NextResponse.json({ results, note: "search.list 관련도 정렬 상위 일부 결과입니다(100단위 소모). 전체 모집단이 아닙니다." });
  } catch (e) {
    return NextResponse.json({ error: e instanceof YouTubeError ? e.message : "검색 실패" }, { status: 502 });
  }
}
