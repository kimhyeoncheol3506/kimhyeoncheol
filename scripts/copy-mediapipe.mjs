// 얼굴 분석 엔진(MediaPipe WASM)을 public 폴더로 복사해서, 외부 CDN 없이 우리 사이트에서 직접 내려주도록 합니다.
// npm install / npm run build 때 자동 실행됩니다.
import { cpSync, existsSync, mkdirSync } from "node:fs";

const src = "node_modules/@mediapipe/tasks-vision/wasm";
const dst = "public/mediapipe/wasm";
if (existsSync(src)) {
  mkdirSync(dst, { recursive: true });
  for (const f of ["vision_wasm_internal.js", "vision_wasm_internal.wasm", "vision_wasm_nosimd_internal.js", "vision_wasm_nosimd_internal.wasm"]) {
    cpSync(`${src}/${f}`, `${dst}/${f}`);
  }
  console.log("MediaPipe wasm copied →", dst);
}
