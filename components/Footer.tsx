"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

export default function Footer() {
  const path = usePathname();
  if (path === "/analyze") return null;
  return (
    <footer className="mt-6 border-t border-line px-5 pb-36 pt-10 text-[13px] leading-relaxed text-mute">
      <p className="font-serif text-[15px] font-semibold text-sub">얼굴과 운명</p>
      <p className="mt-1 font-display text-[10px] font-semibold uppercase tracking-[0.34em] text-accent/80">Face &amp; Fate</p>
      <p className="mt-2">
        본 서비스는 오락 및 참고용이며, 의학적·법적·재정적 조언이 아닙니다. 중요한 결정은 전문가와 상담하세요. 사진과 생년월일은
        서버에 저장되지 않습니다.
      </p>
      <div className="mt-5 flex flex-wrap gap-x-4 gap-y-2 font-medium text-sub">
        <Link href="/disclaimer">면책조항</Link>
        <Link href="/privacy">개인정보처리방침</Link>
        <Link href="/open-source">오픈소스 고지</Link>
      </div>
      <p className="mt-5">© {new Date().getFullYear()} 얼굴과 운명</p>
    </footer>
  );
}
