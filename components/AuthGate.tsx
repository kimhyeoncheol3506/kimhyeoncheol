"use client";
import { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth/AuthProvider";

/** 회원 전용 페이지를 감싸는 컴포넌트. 로그인 기능이 꺼져 있으면 그냥 통과합니다. */
export default function AuthGate({ children }: { children: React.ReactNode }) {
  const { user, loading, enabled } = useAuth();
  const router = useRouter();
  const path = usePathname();

  useEffect(() => {
    if (enabled && !loading && !user) router.replace(`/login?next=${encodeURIComponent(path)}`);
  }, [enabled, loading, user, router, path]);

  if (enabled && (loading || !user)) {
    return (
      <div className="flex min-h-[70vh] items-center justify-center">
        <span className="label">확인 중</span>
      </div>
    );
  }
  return <>{children}</>;
}
