"use client";
import { usePathname } from "next/navigation";

/** 첫 화면은 화면 전체 폭을 쓰고, 나머지 화면은 휴대폰 폭(480px) 안에 둔다 */
export default function Shell({ children }: { children: React.ReactNode }) {
  const wide = usePathname() === "/";
  return <div className={wide ? "min-h-screen w-full" : "mx-auto min-h-screen w-full max-w-app bg-paper"}>{children}</div>;
}
