import { NextResponse } from "next/server";
import { loadStore, updateStore } from "@/lib/store";
import type { VideoAnnotation } from "@/lib/types";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

const clip = (s: unknown, n = 500) => String(s ?? "").slice(0, n);

export async function POST(req: Request) {
  const a = (await req.json()) as VideoAnnotation;
  const v = loadStore().videos[a?.videoId];
  if (!v || v.source !== "real") return NextResponse.json({ error: "실제 수집된 영상에만 확인 내용을 저장할 수 있습니다." }, { status: 400 });
  const clean: VideoAnnotation = {
    videoId: a.videoId,
    updatedAt: new Date().toISOString(),
    thumbnail: {
      verified: !!a.thumbnail?.verified,
      text: clip(a.thumbnail?.text, 100),
      faceVisible: (["yes", "no", "unknown"] as const).includes(a.thumbnail?.faceVisible) ? a.thumbnail.faceVisible : "unknown",
      elements: Array.isArray(a.thumbnail?.elements) ? a.thumbnail.elements.map((x) => clip(x, 20)).slice(0, 10) : [],
      contrast: (["high", "medium", "low", "unknown"] as const).includes(a.thumbnail?.contrast) ? a.thumbnail.contrast : "unknown",
      layout: clip(a.thumbnail?.layout, 200),
    },
    structure: {
      verified: !!a.structure?.verified,
      hook: clip(a.structure?.hook),
      firstInfoSec: Number.isFinite(Number(a.structure?.firstInfoSec)) && a.structure?.firstInfoSec != null ? Number(a.structure.firstInfoSec) : null,
      flow: clip(a.structure?.flow),
      cta: clip(a.structure?.cta, 200),
    },
    visual: {
      verified: !!a.visual?.verified,
      style: clip(a.visual?.style, 100),
      cutsPerMinute: Number.isFinite(Number(a.visual?.cutsPerMinute)) && a.visual?.cutsPerMinute != null ? Number(a.visual.cutsPerMinute) : null,
      subtitleDensity: (["high", "medium", "low", "unknown"] as const).includes(a.visual?.subtitleDensity) ? a.visual.subtitleDensity : "unknown",
      notes: clip(a.visual?.notes),
    },
    faceless: a.faceless && ["A", "B", "C", "D", "E"].includes(a.faceless.cls) ? { cls: a.faceless.cls, confirmed: true } : undefined,
  };
  updateStore((d) => {
    d.annotations[clean.videoId] = clean;
  });
  return NextResponse.json({ ok: true });
}
