import type { Metadata, Viewport } from "next";
import "./globals.css";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import { AuthProvider } from "@/lib/auth/AuthProvider";

const SITE = process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000";

export const metadata: Metadata = {
  metadataBase: new URL(SITE),
  title: { default: "얼굴과 운명 — 사주 × 관상 AI", template: "%s | 얼굴과 운명" },
  description: "생년월일과 얼굴 사진으로 보는 무료 사주 + 관상. 두 결과가 공통으로 말하는 것만 골라 AI가 봐드립니다.",
  openGraph: {
    title: "당신의 얼굴과 생년월일이 말하는 운명",
    description: "사주 × 관상, AI가 봐드립니다. 무료.",
    type: "website",
    locale: "ko_KR",
    images: [{ url: "/og.png", width: 1440, height: 756 }],
  },
};

export const viewport: Viewport = { themeColor: "#0A0A0A", width: "device-width", initialScale: 1 };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <head>
        {/* Pretendard 폰트 (무료, 한국어 최적화) */}
        <link
          rel="stylesheet"
          href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css"
        />
      </head>
      <body>
        <AuthProvider>
          <Header />
          <main className="min-h-screen">{children}</main>
          <Footer />
        </AuthProvider>
      </body>
    </html>
  );
}
