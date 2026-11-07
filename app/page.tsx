import Link from "next/link";
import HeroArt from "@/components/HeroArt";

// 이모지 대신 금색 선 아이콘 (고급스러운 인상)
const ICONS = {
  overlap: (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.4" aria-hidden>
      <circle cx="9" cy="12" r="6" />
      <circle cx="15" cy="12" r="6" />
    </svg>
  ),
  voice: (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" aria-hidden>
      <path d="M4 10v4M8 7v10M12 4v16M16 7v10M20 10v4" />
    </svg>
  ),
  lock: (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" aria-hidden>
      <rect x="5" y="10.5" width="14" height="10" rx="2.5" />
      <path d="M8 10.5V8a4 4 0 0 1 8 0v2.5" />
    </svg>
  ),
  heart: (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round" aria-hidden>
      <path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z" />
    </svg>
  ),
};

const POINTS = [
  { icon: ICONS.overlap, t: "사주와 관상이 같이 말하는 것만", d: "두 가지가 겹치는 이야기만 골라 드려요" },
  { icon: ICONS.voice, t: "목소리로 들려드려요", d: "버튼 하나면 처음부터 끝까지 읽어 줘요" },
  { icon: ICONS.lock, t: "사진은 내 폰에서만 분석해요", d: "서버로 보내지도, 저장하지도 않아요" },
];

function Chevron() {
  return (
    <svg className="text-accent" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden>
      <path d="M9 5l7 7-7 7" />
    </svg>
  );
}

export default function Landing() {
  return (
    <div className="px-5">
      <section className="pt-10 text-center">
        <p className="eyebrow">Saju × Physiognomy</p>
        <h1 className="mt-4 text-display">
          한번쯤은
          <br />
          <span className="gold-text">정확히</span> 보셔야죠
        </h1>
        <div className="divider-gold mt-5" />
        <p className="mt-5 text-[16px] leading-relaxed text-sub">
          생년월일과 얼굴 사진만 있으면
          <br />
          3분이면 끝나요.
        </p>
      </section>

      <div className="gold-frame mt-9 overflow-hidden">
        {/* 액자 안쪽 가는 금선 */}
        <div className="pointer-events-none absolute inset-3 rounded-[14px] border border-accent/15" />
        <div
          className="pointer-events-none absolute inset-0"
          style={{ background: "radial-gradient(60% 55% at 50% 45%, rgba(168,130,58,0.10), transparent 70%)" }}
        />
        <HeroArt className="relative mx-auto h-[300px] w-full max-w-[320px] py-6" color="#4E412B" keyColor="#A8823A" blend="multiply" />
      </div>

      <ul className="mt-10 space-y-6">
        {POINTS.map((p) => (
          <li key={p.t} className="flex items-start gap-4">
            <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full text-accent ring-1 ring-inset ring-accent/40">
              {p.icon}
            </span>
            <div>
              <p className="text-[17px] font-semibold">{p.t}</p>
              <p className="mt-0.5 text-[15px] text-mute">{p.d}</p>
            </div>
          </li>
        ))}
      </ul>

      <Link href="/match" className="gold-frame mt-12 flex items-center gap-4 p-5 transition active:scale-[0.99]">
        <span className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-accent-soft text-gold ring-1 ring-inset ring-accent/40">
          {ICONS.heart}
        </span>
        <span className="flex-1">
          <span className="block font-display text-[12px] font-semibold uppercase tracking-[0.3em] text-accent">New</span>
          <span className="mt-0.5 block font-serif text-[18px] font-semibold">그 사람과 나, 궁합 보기</span>
          <span className="mt-0.5 block text-[14px] text-sub">사주로 보는 궁합 점수, 사진을 넣으면 관상 궁합까지</span>
        </span>
        <Chevron />
      </Link>

      <div className="h-28" />
      <div className="bottom-cta">
        <Link href="/analyze" className="btn-primary w-full">
          무료로 시작하기
        </Link>
      </div>
    </div>
  );
}
