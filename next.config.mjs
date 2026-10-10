/** @type {import('next').NextConfig} */
const nextConfig = {
  // 배포(빌드) 때 코드 스타일 검사로 실패하지 않도록
  eslint: { ignoreDuringBuilds: true },
};

export default nextConfig;
