"use client";
import { useEffect } from "react";
import { useStore } from "@/lib/store";

// 화면에서 예상치 못한 오류가 나면 자동으로 '오류 · 피드백 센터'에 기록합니다.
// CEO는 거기서 '클로드 코드용 복사' 버튼만 눌러 붙여넣으면 됩니다.
export function ErrorCatcher() {
  const { logError } = useStore();

  useEffect(() => {
    const onError = (ev: ErrorEvent) => {
      logError({
        title: "화면 오류 자동 감지",
        message: ev.message || "알 수 없는 오류",
        stack: ev.error?.stack,
        severity: "high",
      });
    };
    const onRejection = (ev: PromiseRejectionEvent) => {
      const r = ev.reason;
      logError({
        title: "처리 실패 자동 감지",
        message: r?.message ?? String(r),
        stack: r?.stack,
        severity: "medium",
      });
    };
    window.addEventListener("error", onError);
    window.addEventListener("unhandledrejection", onRejection);
    return () => {
      window.removeEventListener("error", onError);
      window.removeEventListener("unhandledrejection", onRejection);
    };
  }, [logError]);

  return null;
}
