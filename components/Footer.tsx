import Link from "next/link";

export default function Footer() {
  return (
    <footer className="bg-ink text-paper">
      <div className="mx-auto max-w-page px-5 py-14 md:px-10">
        <p className="text-2xl font-black tracking-tight md:text-3xl">얼굴과 운명</p>
        <p className="mt-3 max-w-xl text-sm leading-relaxed text-paper/60">
          본 서비스는 오락 및 참고용이며, 의학적·법적·재정적 조언이 아닙니다. 중요한 결정은 전문가와 상담하세요.
          사진과 생년월일은 서버에 저장되지 않습니다.
        </p>
        <div className="mt-10 flex flex-wrap gap-x-6 gap-y-3 text-sm text-paper/70">
          <Link href="/disclaimer" className="hover:text-paper">면책조항</Link>
          <Link href="/privacy" className="hover:text-paper">개인정보처리방침</Link>
          <Link href="/open-source" className="hover:text-paper">오픈소스 고지</Link>
        </div>
        <p className="mt-10 text-xs text-paper/40">© {new Date().getFullYear()} 얼굴과 운명</p>
      </div>
    </footer>
  );
}
