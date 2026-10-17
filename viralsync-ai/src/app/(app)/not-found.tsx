import Link from "next/link";
import { Alert } from "@/components/ui/misc";

export default function NotFound() {
  return (
    <div className="mx-auto max-w-lg space-y-4 py-16">
      <Alert tone="warn" title="대상을 찾을 수 없습니다">
        삭제되었거나 접근 권한이 없는 데이터입니다.
      </Alert>
      <Link href="/dashboard" className="link text-sm">대시보드로 돌아가기</Link>
    </div>
  );
}
