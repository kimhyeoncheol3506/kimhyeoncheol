/** @type {import('next').NextConfig} */
const nextConfig = {
  // 배포(빌드) 때 코드 스타일 검사로 실패하지 않도록
  eslint: { ignoreDuringBuilds: true },
  // 목소리 라이브러리는 서버에서 그대로 실행 (웹소켓 사용)
  experimental: { serverComponentsExternalPackages: ["msedge-tts", "ws"] },
};

export default nextConfig;
