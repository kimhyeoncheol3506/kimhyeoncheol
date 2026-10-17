"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { useStore } from "@/lib/store";

// 왼쪽 메뉴. 메뉴를 추가하려면 아래 MENU 배열에 한 줄 추가하고 app/ 폴더에 페이지를 만드세요.
const MENU = [
  { href: "/", label: "운영자 콘솔", icon: "📊" },
  { href: "/staff", label: "직원 목록 · 상태", icon: "🧑‍💼" },
  { href: "/missions", label: "미션 보드", icon: "🎯" },
  { href: "/errors", label: "오류 · 피드백 센터", icon: "🚨" },
  { href: "/orders", label: "주문 · 연동 관리", icon: "🛒" },
  { href: "/accounts", label: "계정 · 권한", icon: "🔐" },
];

export function Sidebar() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);
  const { data } = useStore();
  const openErrors = data.errors.filter((e) => e.status !== "resolved").length;

  const isActive = (href: string) => (href === "/" ? pathname === "/" : pathname.startsWith(href));

  return (
    <>
      {/* 휴대폰 화면 상단 바 */}
      <div className="sticky top-0 z-30 flex items-center justify-between bg-brand-dark px-4 py-3 text-white lg:hidden">
        <span className="font-bold">AIMAX OS</span>
        <button onClick={() => setOpen(!open)} className="rounded px-2 py-1 text-xl" aria-label="메뉴 열기">
          ☰
        </button>
      </div>

      <aside
        className={`fixed inset-y-0 left-0 z-40 w-64 transform bg-brand-dark text-white transition lg:translate-x-0 ${
          open ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="px-6 py-6">
          <p className="text-lg font-bold tracking-tight">AIMAX OS</p>
          <p className="text-xs text-emerald-200/70">Admin & Staff Console</p>
        </div>
        <nav className="space-y-1 px-3">
          {MENU.map((m) => (
            <Link
              key={m.href}
              href={m.href}
              onClick={() => setOpen(false)}
              className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm ${
                isActive(m.href) ? "bg-brand-deep font-semibold text-white" : "text-emerald-50/80 hover:bg-white/5"
              }`}
            >
              <span>{m.icon}</span>
              <span className="flex-1">{m.label}</span>
              {m.href === "/errors" && openErrors > 0 && (
                <span className="rounded-full bg-rose-500 px-1.5 text-xs font-semibold">{openErrors}</span>
              )}
            </Link>
          ))}
        </nav>
        <div className="absolute bottom-0 w-full border-t border-white/10 px-6 py-4 text-xs text-emerald-100/60">
          광고대행 · 영상제작
          <br />
          AI 직원 {data.staff.length}명 운영 중
        </div>
      </aside>

      {open && <div className="fixed inset-0 z-30 bg-black/40 lg:hidden" onClick={() => setOpen(false)} />}
    </>
  );
}
