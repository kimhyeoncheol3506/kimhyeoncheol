"use client";
// 궁합 실행: 두 사람 사주 계산 + (있으면) 두 사람 관상. 사진은 브라우저 안에서만 쓰고 바로 지운다.
import { computeSaju } from "../saju/consensus";
import type { BirthInput } from "../saju/types";
import { detectFace } from "../face/landmarker";
import { measureFace } from "../face/measure";
import { scoreFeatures, type FeatureScores } from "../face/physiognomy";
import { NoFaceError } from "../analyze";
import { computeMatch, type MatchResult, type Relation } from "./compute";

export const MATCH_KEY = "match-result";

export type PersonInput = { name: string; birth: BirthInput; photo: File | null };

async function readFace(file: File): Promise<FeatureScores> {
  const url = URL.createObjectURL(file);
  const img = new Image();
  try {
    await new Promise<void>((res, rej) => {
      img.onload = () => res();
      img.onerror = () => rej(new Error("이미지를 읽을 수 없습니다."));
      img.src = url;
    });
    const pts = await detectFace(img);
    if (!pts) throw new NoFaceError("얼굴을 찾지 못했어요.");
    return scoreFeatures(measureFace(pts));
  } finally {
    URL.revokeObjectURL(url);
    img.src = "";
  }
}

export async function runMatch(me: PersonInput, partner: PersonInput, relation: Relation, worry: string, onStep: (t: string) => void): Promise<MatchResult> {
  onStep("두 사람의 사주를 계산하고 있어요");
  const sa = computeSaju(me.birth);
  const sb = computeSaju(partner.birth);
  let fa: FeatureScores | null = null;
  let fb: FeatureScores | null = null;
  if (me.photo && partner.photo) {
    onStep("두 사람의 얼굴을 읽고 있어요");
    const named = (n: string, fallback: string) => async (f: File) => {
      try {
        return await readFace(f);
      } catch (e) {
        if (e instanceof NoFaceError) throw new NoFaceError(n.trim() ? `${n.trim()}님` : fallback);
        throw e;
      }
    };
    fa = await named(me.name, "내")(me.photo);
    fb = await named(partner.name, "그 사람")(partner.photo);
  }
  onStep("두 사람의 궁합을 맞춰 보고 있어요");
  await new Promise((r) => setTimeout(r, 600));
  return computeMatch(
    { name: me.name.trim(), gender: me.birth.gender, saju: sa, face: fa },
    { name: partner.name.trim(), gender: partner.birth.gender, saju: sb, face: fb },
    relation,
    worry,
  );
}
