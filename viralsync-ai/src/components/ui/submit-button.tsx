"use client";
import { useEffect, useState, type ComponentProps } from "react";
import { useFormStatus } from "react-dom";
import { Button } from "./button";

/**
 * pending 을 넘기지 않으면 useFormStatus 상태를 사용.
 * 하이드레이션 전에는 비활성화하여 JS 없이 폼이 기본 제출되는 것을 막는다.
 */
export function SubmitButton({ children, pendingText = "처리 중…", pending, ...props }: ComponentProps<typeof Button> & { pendingText?: string; pending?: boolean }) {
  const status = useFormStatus();
  const [hydrated, setHydrated] = useState(false);
  useEffect(() => setHydrated(true), []);
  const busy = pending ?? status.pending;
  return (
    <Button type="submit" disabled={!hydrated || busy || props.disabled} aria-busy={busy} {...props}>
      {busy ? (
        <>
          <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-current border-t-transparent" aria-hidden />
          {pendingText}
        </>
      ) : (
        children
      )}
    </Button>
  );
}
