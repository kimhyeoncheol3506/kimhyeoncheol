import type { Metadata, Viewport } from "next";
import "./globals.css";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import { AuthProvider } from "@/lib/auth/AuthProvider";

const SITE = process.env.NEXT_PUBLIC_SITE_URL ?? "https://faceandfate.vercel.app";
// 구글 애드센스 게시자 ID (승인 전에는 자동광고만, 광고 단위는 아직 넣지 않음)
const ADSENSE_CLIENT = "ca-pub-6108302647873265";

export const metadata: Metadata = {
  metadataBase: new URL(SITE),
  title: { default: "얼굴과 운명 — 사주 × 관상 AI", template: "%s | 얼굴과 운명" },
  description: "생년월일과 얼굴 사진으로 보는 무료 사주 + 관상. 두 결과가 공통으로 말하는 것만 골라 AI가 봐드립니다.",
  openGraph: {
    title: "당신의 얼굴과 생년월일이 말하는 운명",
    description: "사주 × 관상, 한번쯤은 정확히 보셔야죠. 무료.",
    type: "website",
    locale: "ko_KR",
    images: [{ url: "/og.png", width: 1440, height: 756 }],
  },
  other: { "google-adsense-account": ADSENSE_CLIENT },
};

export const viewport: Viewport = { themeColor: "#FFFFFF", width: "device-width", initialScale: 1, viewportFit: "cover" };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <head>
        {/* Pretendard 폰트 (무료, 한국어 최적화) */}
        <link
          rel="stylesheet"
          href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css"
        />
        {/* 애드센스: 소유권 확인 크롤러가 읽을 수 있게 서버 HTML의 head에 그대로 넣음 (next/script는 data-nscript 속성 경고가 나서 일반 태그 사용) */}
        <script async src={`https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=${ADSENSE_CLIENT}`} crossOrigin="anonymous" />
      </head>
      <body>
        <AuthProvider>
          <div className="mx-auto min-h-screen w-full max-w-app bg-paper">
            <Header />
            <main>{children}</main>
            <Footer />
          </div>
        </AuthProvider>
      </body>
    </html>
  );
}
