"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth/AuthProvider";

/** 토스식 상단 바: 첫 화면은 이름, 나머지는 뒤로가기 */
export default function Header() {
  const { user, enabled, signOut } = useAuth();
  const path = usePathname();
  const router = useRouter();
  const home = path === "/";
  // Vercel 이 자동으로 넣어 주는 브랜치 이름. main(데모 버전)이 아니면 '개발 버전' 표시
  const branch = process.env.NEXT_PUBLIC_VERCEL_GIT_COMMIT_REF;
  const isDev = Boolean(branch && branch !== "main");
  // 입력 화면은 자체 상단 바를 씀
  if (path === "/analyze" || path === "/match") return null;

  return (
    <header className="sticky top-0 z-40 border-b border-line/60 bg-paper/75 backdrop-blur-md">
      <div className="flex h-14 items-center justify-between px-5">
        {home ? (
          <Link href="/" className="flex items-center gap-2.5">
            <Seal />
            <span className="flex flex-col leading-none">
              <span className="font-serif text-[17px] font-semibold tracking-[0.02em]">얼굴과 운명</span>
              <span className="mt-1 font-display text-[10px] font-semibold uppercase tracking-[0.34em] text-accent">Face &amp; Fate</span>
            </span>
            {isDev && <span className="rounded-full bg-warn px-2 py-0.5 text-[11px] font-bold text-paper">개발 버전</span>}
          </Link>
        ) : (
          <button onClick={() => (history.length > 1 ? router.back() : router.push("/"))} aria-label="뒤로" className="-ml-2 p-2">
            <Back />
          </button>
        )}
        {enabled &&
          (user ? (
            <button onClick={signOut} className="text-[15px] font-medium text-mute">
              로그아웃
            </button>
          ) : (
            <Link href="/login" className="text-[15px] font-medium text-sub">
              로그인
            </Link>
          ))}
      </div>
    </header>
  );
}

/** 금색 원형 인장 로고 */
export function Seal({ size = 30 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 32 32" fill="none" aria-hidden>
      <defs>
        <linearGradient id="seal-g" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#F3E3B8" />
          <stop offset="1" stopColor="#B48F45" />
        </linearGradient>
      </defs>
      <circle cx="16" cy="16" r="15" stroke="url(#seal-g)" strokeWidth="1" />
      <circle cx="16" cy="16" r="11.5" stroke="url(#seal-g)" strokeWidth="0.6" opacity="0.6" />
      {/* 초승달 + 별 */}
      <path d="M19.5 9.5a7 7 0 1 0 0 13 5.6 5.6 0 1 1 0-13z" fill="url(#seal-g)" />
      <path d="M21.5 12.2l.6 1.5 1.5.6-1.5.6-.6 1.5-.6-1.5-1.5-.6 1.5-.6z" fill="url(#seal-g)" />
    </svg>
  );
}

export function Back() {
  return (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <path d="M15 5l-7 7 7 7" />
    </svg>
  );
}
