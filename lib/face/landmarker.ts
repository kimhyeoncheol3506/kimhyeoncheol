"use client";
// 브라우저 안에서만 얼굴 랜드마크를 추출한다. 사진은 서버로 전송되지 않는다.
import type { FaceLandmarker } from "@mediapipe/tasks-vision";
import type { Pt } from "./measure";

const WASM = "/mediapipe/wasm";
const MODEL = "/models/face_landmarker.task";

let instance: Promise<FaceLandmarker> | null = null;

function load() {
  if (!instance) {
    instance = (async () => {
      const { FaceLandmarker, FilesetResolver } = await import("@mediapipe/tasks-vision");
      const files = await FilesetResolver.forVisionTasks(WASM);
      const make = (delegate: "GPU" | "CPU") =>
        FaceLandmarker.createFromOptions(files, {
          baseOptions: { modelAssetPath: MODEL, delegate },
          runningMode: "IMAGE",
          numFaces: 1,
        });
      try {
        return await make("GPU");
      } catch {
        return await make("CPU");
      }
    })();
    instance.catch(() => (instance = null));
  }
  return instance;
}

/** 미리 모델을 내려받아 두기 (입력 페이지 진입 시 호출) */
export const preloadLandmarker = () => {
  load().catch(() => {});
};

export async function detectFace(img: HTMLImageElement): Promise<Pt[] | null> {
  const lm = await load();
  const res = lm.detect(img);
  const face = res.faceLandmarks?.[0];
  if (!face) return null;
  // 정규화 좌표 → 실제 픽셀 비율로 (가로세로 비율 보정)
  return face.map((p) => ({ x: p.x * img.naturalWidth, y: p.y * img.naturalHeight }));
}
