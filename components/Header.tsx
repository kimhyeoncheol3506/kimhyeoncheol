"use client";
import Link from "next/link";
import { useAuth } from "@/lib/auth/AuthProvider";

export default function Header() {
  const { user, enabled, signOut } = useAuth();
  return (
    <header className="sticky top-0 z-40 border-b border-line/60 bg-paper/95 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-page items-center justify-between px-5 md:px-10">
        <Link href="/" className="flex items-center gap-2 text-[15px] font-black tracking-tight">
          <span className="inline-block h-2.5 w-2.5 bg-accent" aria-hidden />
          얼굴과 운명
        </Link>
        <nav className="flex items-center gap-5 text-sm font-semibold">
          <Link href="/analyze" className="hidden hover:text-accent sm:block">
            무료로 보기
          </Link>
          {enabled &&
            (user ? (
              <button onClick={signOut} className="text-mute hover:text-ink">
                로그아웃
              </button>
            ) : (
              <Link href="/login" className="hover:text-accent">
                로그인
              </Link>
            ))}
        </nav>
      </div>
    </header>
  );
}
