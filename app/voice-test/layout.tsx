import type { Metadata } from "next";

// 운영자용 발음 점검 페이지 (검색에 노출하지 않음)
export const metadata: Metadata = { title: "목소리 발음 테스트", robots: { index: false, follow: false } };

export default function Layout({ children }: { children: React.ReactNode }) {
  return children;
}
