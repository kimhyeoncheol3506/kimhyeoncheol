"use client";
import Link, { useLinkStatus } from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { brand } from "@/config/brand";
import type { NavItem } from "./nav";

export function Sidebar({ items, pendingReview }: { items: NavItem[]; pendingReview: number }) {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);
  const nav = (
    <nav aria-label="주 메뉴" className="flex-1 space-y-0.5 overflow-y-auto px-3 py-3">
      {items.map((i) => {
        const active = pathname === i.href || pathname.startsWith(`${i.href}/`);
        return (
          <Link
            key={i.href}
            href={i.href}
            onClick={() => setOpen(false)}
            aria-current={active ? "page" : undefined}
            className={`flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm font-medium transition ${
              active ? "bg-brand-600 text-white" : "text-slate-300 hover:bg-slate-800 hover:text-white"
            }`}
          >
            <span aria-hidden>{i.icon}</span>
            <span className="flex-1">{i.label}</span>
            <NavPending />
            {i.href === "/approvals" && pendingReview > 0 && (
              <span className="rounded-full bg-amber-400 px-1.5 text-xs font-bold text-slate-900" aria-label={`검토 대기 ${pendingReview}건`}>
                {pendingReview}
              </span>
            )}
          </Link>
        );
      })}
    </nav>
  );
  const logo = (
    <Link href="/dashboard" className="flex items-center gap-2 px-5 py-4">
      <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-500 font-bold text-white">V</span>
      <span className="text-base font-bold text-white">{brand.name}</span>
    </Link>
  );
  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        className="fixed left-3 top-3 z-40 rounded-lg bg-slate-900 px-2.5 py-1.5 text-sm text-white shadow lg:hidden no-print"
        aria-label="메뉴 열기"
        aria-expanded={open}
      >
        ☰
      </button>
      <aside className="no-print fixed inset-y-0 left-0 z-30 hidden w-60 flex-col bg-slate-900 lg:flex">
        {logo}
        {nav}
      </aside>
      {open && (
        <div className="fixed inset-0 z-50 flex lg:hidden" role="dialog" aria-modal="true" aria-label="메뉴">
          <div className="flex w-64 flex-col bg-slate-900">
            <div className="flex items-center justify-between pr-3">
              {logo}
              <button type="button" onClick={() => setOpen(false)} className="text-xl text-slate-300" aria-label="메뉴 닫기">
                ×
              </button>
            </div>
            {nav}
          </div>
          <button type="button" className="flex-1 bg-black/40" onClick={() => setOpen(false)} aria-label="메뉴 닫기" />
        </div>
      )}
    </>
  );
}

/** 링크 이동이 진행 중일 때 표시 (Link 의 하위에서만 동작) */
function NavPending() {
  const { pending } = useLinkStatus();
  return pending ? <span className="h-3 w-3 animate-spin rounded-full border-2 border-current border-t-transparent" role="status" aria-label="이동 중" /> : null;
}
