"use client";
import Link from "next/link";
import { useEffect } from "react";
import { useStore } from "@/lib/store";

// 페이지가 통째로 멈추는 오류가 나면 이 화면이 대신 보입니다. 오류는 자동으로 기록됩니다.
export default function ErrorPage({ error, reset }: { error: Error; reset: () => void }) {
  const { logError } = useStore();

  useEffect(() => {
    logError({ title: "페이지 오류", message: error.message, stack: error.stack, severity: "high" });
  }, [error, logError]);

  return (
    <div className="card mx-auto mt-16 max-w-lg text-center">
      <p className="text-4xl">😵</p>
      <h1 className="mt-3 text-xl font-bold">이 화면에서 오류가 났어요</h1>
      <p className="mt-2 text-sm text-sub">
        오류 내용은 <b>오류 · 피드백 센터</b>에 자동으로 기록됐습니다.
        <br />
        거기서 &lsquo;클로드 코드용 복사&rsquo;를 눌러 붙여넣으면 고칠 수 있어요.
      </p>
      <pre className="mt-4 overflow-x-auto rounded-lg bg-canvas p-3 text-left text-xs text-rose-700">{error.message}</pre>
      <div className="mt-5 flex justify-center gap-2">
        <button className="btn" onClick={reset}>
          다시 시도
        </button>
        <Link href="/errors" className="btn-primary">
          오류 센터로 가기
        </Link>
      </div>
    </div>
  );
}
