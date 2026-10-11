import { NextResponse } from "next/server";
import { targetChannelIds } from "@/lib/dataset";
import { loadStore } from "@/lib/store";
import { hasApiKey } from "@/lib/youtube/client";
import { collect } from "@/lib/youtube/collect";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";
export const maxDuration = 300;

let running = false;

export async function POST() {
  if (!hasApiKey())
    return NextResponse.json({ error: "YOUTUBE_API_KEY가 없습니다. .env.local에 키를 넣고 서버를 다시 시작하세요. 그동안은 데모 모드로 확인할 수 있습니다." }, { status: 400 });
  if (running) return NextResponse.json({ error: "이미 수집이 진행 중입니다." }, { status: 409 });
  running = true;
  try {
    const s = loadStore().settings;
    const run = await collect({ channelIds: targetChannelIds(s), peerWindowDays: s.peerWindowDays });
    return NextResponse.json({ run });
  } catch (e) {
    return NextResponse.json({ error: (e as Error).message }, { status: 500 });
  } finally {
    running = false;
  }
}
