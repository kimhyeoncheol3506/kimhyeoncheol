"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const ITEMS = [
  { href: "/", label: "A. 요약 대시보드" },
  { href: "/channels", label: "B. 채널 탐색" },
  { href: "/ranking", label: "C. 바이럴 랭킹" },
  { href: "/videos", label: "D. 영상 정밀 분석" },
  { href: "/compare", label: "E. 상위 3개 비교" },
  { href: "/plan", label: "F. 내 첫 영상 제작" },
  { href: "/settings", label: "G. 데이터 및 설정" },
];

export function Nav() {
  const path = usePathname();
  return (
    <nav className="flex gap-1 overflow-x-auto lg:flex-col">
      {ITEMS.map((it) => {
        const active = it.href === "/" ? path === "/" : path.startsWith(it.href);
        return (
          <Link
            key={it.href}
            href={it.href}
            className={`whitespace-nowrap rounded-lg px-3 py-2 text-sm font-medium ${active ? "bg-neutral-900 text-white" : "text-neutral-700 hover:bg-neutral-100"}`}
          >
            {it.label}
          </Link>
        );
      })}
    </nav>
  );
}
