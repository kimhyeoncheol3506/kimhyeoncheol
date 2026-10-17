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
  if (path === "/analyze") return null;

  return (
    <header className="sticky top-0 z-40 bg-paper/95 backdrop-blur">
      <div className="flex h-14 items-center justify-between px-5">
        {home ? (
          <Link href="/" className="flex items-center gap-2 text-[17px] font-bold tracking-tight">
            얼굴과 운명
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

export function Back() {
  return (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <path d="M15 5l-7 7 7 7" />
    </svg>
  );
}
