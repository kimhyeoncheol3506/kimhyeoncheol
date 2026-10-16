"use client";
import { computeSaju } from "./saju/consensus";
import type { BirthInput } from "./saju/types";
import { detectFace } from "./face/landmarker";
import { measureFace } from "./face/measure";
import { readFeatures, scoreFeatures } from "./face/physiognomy";
import { cosmeticAdvice } from "./face/cosmetic";
import { composeReading, findCommon } from "./reading/compose";
import type { Reading, ResultPayload } from "./reading/types";

export { RESULT_KEY } from "./resultKey";

export type Step = "saju" | "face" | "common" | "ai" | "done";

export class NoFaceError extends Error {}

/** 사진을 이미지 요소로 읽기 (브라우저 메모리 안에서만) */
function loadImage(file: File): Promise<{ img: HTMLImageElement; release: () => void }> {
  return new Promise((resolve, reject) => {
    const url = URL.createObjectURL(file);
    const img = new Image();
    img.onload = () => resolve({ img, release: () => URL.revokeObjectURL(url) });
    img.onerror = () => {
      URL.revokeObjectURL(url);
      reject(new Error("이미지를 읽을 수 없습니다."));
    };
    img.src = url;
  });
}

export async function analyze(
  birth: BirthInput,
  photo: File | null,
  onStep: (s: Step) => void,
  name?: string,
): Promise<ResultPayload> {
  onStep("saju");
  const saju = computeSaju(birth);

  let features: ReturnType<typeof scoreFeatures> | null = null;
  let featureReadings: ReturnType<typeof readFeatures> = [];
  if (photo) {
    onStep("face");
    const { img, release } = await loadImage(photo);
    try {
      const pts = await detectFace(img);
      if (!pts) throw new NoFaceError("얼굴을 찾지 못했어요.");
      features = scoreFeatures(measureFace(pts));
      featureReadings = readFeatures(features);
    } finally {
      // 분석이 끝나면 사진 데이터를 즉시 해제
      release();
      img.src = "";
    }
  }

  onStep("common");
  const common = findCommon(saju, features, featureReadings);
  let reading: Reading = composeReading(saju, common, Boolean(features), birth.gender);

  // AI 해석 (서버에 API 키가 설정된 경우에만). 사진·생년월일은 보내지 않고, 계산된 결과만 보냅니다.
  onStep("ai");
  try {
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), 45000);
    const res = await fetch("/api/interpret", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        gender: birth.gender,
        age: saju.age,
        hourKnown: birth.hour != null,
        saju: {
          pillars: saju.pillars.filter((p) => p.agreed).map((p) => ({
            key: p.key, ganzhi: p.ganzhi, stemTenGod: p.stemTenGod, branchTenGod: p.branchTenGod,
          })),
          dayMaster: saju.dayMaster,
          fiveElements: saju.fiveElements,
          tenGodCounts: saju.tenGodCounts,
          strength: saju.strength,
          yongsin: saju.yongsin,
          currentDaeun: saju.currentDaeun,
          years: saju.years,
          relations: saju.relations,
        },
        face: featureReadings,
        common,
        draft: reading,
      }),
      signal: ctrl.signal,
    });
    clearTimeout(timer);
    if (res.ok) {
      const ai = (await res.json()) as Reading | { disabled: true };
      // 날짜·별점이 들어간 표 항목은 두 엔진이 합의한 규칙 기반 값을 그대로 유지합니다.
      if ("sections" in ai) {
        const draft = reading;
        reading = {
          ...ai,
          sections: ai.sections.map((s) => {
            const d = draft.sections.find((x) => x.id === s.id);
            return d?.items ? { ...s, body: d.body, items: d.items } : s;
          }),
          source: "ai",
        };
      }
    }
  } catch {
    // AI 실패 시 규칙 기반 해석을 그대로 사용
  }

  onStep("done");
  return {
    createdAt: new Date().toISOString(),
    name: name?.trim() || undefined,
    gender: birth.gender,
    saju,
    face: features ? { features: featureReadings, cosmetic: cosmeticAdvice(features, birth.gender, saju.age) } : null,
    common,
    reading,
  };
}
