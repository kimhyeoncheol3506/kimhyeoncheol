import type { Metadata } from "next";
import "./globals.css";
import { StoreProvider } from "@/lib/store";
import { Sidebar } from "@/components/Sidebar";
import { ErrorCatcher } from "@/components/ErrorCatcher";

export const metadata: Metadata = {
  title: "AIMAX OS",
  description: "AI 직원 기반 광고대행·영상제작 회사 경영관리 시스템",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <body>
        <StoreProvider>
          <ErrorCatcher />
          <Sidebar />
          <main className="min-h-screen px-4 py-6 lg:ml-64 lg:px-10 lg:py-8">
            <div className="mx-auto max-w-6xl">{children}</div>
          </main>
        </StoreProvider>
      </body>
    </html>
  );
}
