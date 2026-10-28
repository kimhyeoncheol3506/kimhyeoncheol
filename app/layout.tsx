import type { Metadata, Viewport } from "next";
import "./globals.css";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import Shell from "@/components/Shell";
import { AuthProvider } from "@/lib/auth/AuthProvider";

const SITE = process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000";

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
};

export const viewport: Viewport = { themeColor: "#F7F9F8", width: "device-width", initialScale: 1, viewportFit: "cover" };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <head>
        {/* Pretendard 폰트 (무료, 한국어 최적화) */}
        <link
          rel="stylesheet"
          href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css"
        />
        {/* 첫 화면의 명조체 (Noto Serif KR) */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@400;600;700&display=swap" />
      </head>
      <body>
        <AuthProvider>
          <Shell>
            <Header />
            <main>{children}</main>
            <Footer />
          </Shell>
        </AuthProvider>
      </body>
    </html>
  );
}
