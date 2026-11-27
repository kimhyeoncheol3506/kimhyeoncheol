/** @type {import('next').NextConfig} */
const nextConfig = {
  // 배포(빌드) 때 코드 스타일 검사로 실패하지 않도록
  eslint: { ignoreDuringBuilds: true },
  experimental: {
    // 서버에서 그대로 실행할 라이브러리 (목소리: 웹소켓, PDF: 크롬)
    serverComponentsExternalPackages: ["msedge-tts", "ws", "@sparticuz/chromium", "puppeteer-core"],
    // PDF용 크롬 실행 파일을 배포 묶음에 포함
    outputFileTracingIncludes: { "/api/pdf": ["./node_modules/@sparticuz/chromium/bin/**"] },
  },
};

export default nextConfig;
