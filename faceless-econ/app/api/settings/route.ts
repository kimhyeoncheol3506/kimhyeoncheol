import { NextResponse } from "next/server";
import { loadStore, updateStore } from "@/lib/store";
import type { FacelessClass, Settings, Weights } from "@/lib/types";
import { DEFAULT_WEIGHTS } from "@/lib/types";
import { YouTubeError, hasApiKey } from "@/lib/youtube/client";
import { resolveChannel } from "@/lib/youtube/collect";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

const CLASSES: FacelessClass[] = ["A", "B", "C", "D", "E", "U"];
const isId = (s: unknown): s is string => typeof s === "string" && /^UC[\w-]{22}$/.test(s);

export function GET() {
  return NextResponse.json(loadStore().settings);
}

export async function POST(req: Request) {
  const body = (await req.json()) as Record<string, unknown>;
  const errors: string[] = [];
  let resolved: { id: string; title: string } | null = null;

  if (typeof body.addChannel === "string" && body.addChannel.trim()) {
    if (!hasApiKey()) return NextResponse.json({ error: "채널 추가에는 API 키가 필요합니다." }, { status: 400 });
    try {
      resolved = await resolveChannel(body.addChannel);
      if (!resolved) return NextResponse.json({ error: "채널을 찾지 못했습니다. 핸들(@이름) 또는 채널 ID(UC…)를 확인하세요." }, { status: 404 });
    } catch (e) {
      return NextResponse.json({ error: e instanceof YouTubeError ? e.message : "채널 조회 실패" }, { status: 502 });
    }
  }

  const next = updateStore((d) => {
    const s: Settings = d.settings;
    if (body.resetWeights) s.weights = { ...DEFAULT_WEIGHTS };
    if (body.weights && typeof body.weights === "object") {
      const w = body.weights as Partial<Weights>;
      for (const k of Object.keys(DEFAULT_WEIGHTS) as (keyof Weights)[]) {
        const v = Number(w[k]);
        if (w[k] != null && Number.isFinite(v) && v >= 0 && v <= 100) s.weights[k] = v;
        else if (w[k] != null) errors.push(`가중치 ${k}는 0~100 사이 숫자여야 합니다.`);
      }
    }
    if (body.periodDays != null) {
      const n = Number(body.periodDays);
      if (Number.isInteger(n) && n >= 1 && n <= 60) s.periodDays = n;
      else errors.push("분석 기간은 1~60일 정수여야 합니다.");
    }
    if (body.peerWindowDays != null) {
      const n = Number(body.peerWindowDays);
      if (Number.isInteger(n) && n >= 14 && n <= 365) s.peerWindowDays = n;
      else errors.push("비교 기간은 14~365일 정수여야 합니다.");
    }
    if (body.dataMode === "auto" || body.dataMode === "demo" || body.dataMode === "real") s.dataMode = body.dataMode;
    if (Array.isArray(body.pinnedTop3)) {
      const ids = (body.pinnedTop3 as unknown[]).filter(isId).slice(0, 3);
      s.pinnedTop3 = [...new Set(ids)];
    }
    if (body.facelessOverride && typeof body.facelessOverride === "object") {
      const o = body.facelessOverride as { channelId?: unknown; cls?: unknown; confirmed?: unknown; note?: unknown; remove?: unknown };
      if (isId(o.channelId)) {
        if (o.remove) delete s.facelessOverrides[o.channelId];
        else if (CLASSES.includes(o.cls as FacelessClass))
          s.facelessOverrides[o.channelId] = { cls: o.cls as FacelessClass, confirmed: !!o.confirmed, note: String(o.note ?? "").slice(0, 300) };
      }
    }
    if (resolved && !s.extraChannelIds.includes(resolved.id)) s.extraChannelIds.push(resolved.id);
    if (isId(body.removeChannel)) s.extraChannelIds = s.extraChannelIds.filter((x) => x !== body.removeChannel);
  });
  return NextResponse.json({ settings: next.settings, errors, added: resolved });
}
