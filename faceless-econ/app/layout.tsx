import type { Metadata } from "next";
import "./globals.css";
import { Nav } from "@/components/Nav";
import { getDataset } from "@/lib/dataset";
import { kst } from "@/lib/time";

export const metadata: Metadata = {
  title: "페이스리스 경제채널 분석실",
  description: "국내 페이스리스 경제·재테크 유튜브 바이럴 분석 및 30일 콘텐츠 출시 시스템",
};

export const dynamic = "force-dynamic";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const ds = getDataset();
  const demo = ds.source === "demo";
  return (
    <html lang="ko">
      <head>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable.min.css" />
      </head>
      <body className="min-h-screen font-sans antialiased">
        <div
          className={`sticky top-0 z-20 border-b px-4 py-2 text-sm ${demo ? "border-amber-300 bg-amber-100 text-amber-900" : "border-emerald-300 bg-emerald-50 text-emerald-900"}`}
        >
          <div className="mx-auto flex max-w-[1500px] flex-wrap items-center gap-x-4 gap-y-1">
            <strong>{demo ? "■ 데모 데이터 표시 중" : "■ 실제 수집 데이터"}</strong>
            <span>{ds.sourceReason}</span>
            <span className="ml-auto">
              분석 기간: {kst(ds.periodStart)} ~ {kst(ds.periodEnd)} ({ds.settings.periodDays}일)
            </span>
          </div>
        </div>
        <div className="mx-auto flex max-w-[1500px] flex-col gap-6 px-4 py-6 lg:flex-row">
          <aside className="lg:w-52 lg:shrink-0">
            <div className="mb-4 hidden lg:block">
              <div className="text-lg font-black leading-tight">페이스리스<br />경제채널 분석실</div>
              <div className="mt-1 text-xs text-neutral-500">바이럴 분석 → 30일 출시</div>
            </div>
            <div className="lg:sticky lg:top-14">
              <Nav />
            </div>
          </aside>
          <main className="min-w-0 flex-1">{children}</main>
        </div>
      </body>
    </html>
  );
}
