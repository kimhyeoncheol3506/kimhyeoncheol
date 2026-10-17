import path from "node:path";
import { fileURLToPath } from "node:url";

/** @type {import('next').NextConfig} */
const nextConfig = {
  poweredByHeader: false,
  // Docker 이미지 빌드 시에만 standalone 출력 (next start 와 호환되지 않음)
  output: process.env.NEXT_OUTPUT === "standalone" ? "standalone" : undefined,
  // 상위 디렉터리에 다른 lockfile 이 있어도 이 프로젝트를 루트로 사용
  outputFileTracingRoot: path.dirname(fileURLToPath(import.meta.url)),
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          { key: "X-Frame-Options", value: "DENY" },
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
        ],
      },
    ];
  },
};
export default nextConfig;
