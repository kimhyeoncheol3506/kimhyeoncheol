"use client";
import { Alert } from "@/components/ui/misc";
import { Button } from "@/components/ui/button";

export default function ErrorPage({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return (
    <div className="mx-auto max-w-lg space-y-4 py-16">
      <Alert tone="error" title="화면을 불러오지 못했습니다">
        일시적인 오류이거나 데이터베이스 연결에 문제가 있을 수 있습니다.
        {error.digest && <span className="mt-1 block text-xs opacity-70">오류 코드: {error.digest}</span>}
      </Alert>
      <Button onClick={reset}>다시 시도</Button>
    </div>
  );
}
