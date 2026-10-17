import Link from "next/link";
import HeroArt from "@/components/HeroArt";

const POINTS = [
  { icon: "🔮", t: "사주와 관상이 같이 말하는 것만", d: "두 가지가 겹치는 이야기만 골라 드려요" },
  { icon: "🎧", t: "목소리로 들려드려요", d: "버튼 하나면 처음부터 끝까지 읽어 줘요" },
  { icon: "🔒", t: "사진은 내 폰에서만 분석해요", d: "서버로 보내지도, 저장하지도 않아요" },
];

export default function Landing() {
  return (
    <div className="px-5">
      <section className="pt-6">
        <p className="text-[15px] font-semibold text-accent">사주 × 관상</p>
        <h1 className="mt-2 text-display font-bold">
          한번쯤은
          <br />
          정확히 보셔야죠
        </h1>
        <p className="mt-3 text-[17px] leading-relaxed text-sub">생년월일과 얼굴 사진만 있으면 3분이면 끝나요.</p>
      </section>

      <div className="mt-8 overflow-hidden rounded-card bg-smoke">
        <HeroArt className="mx-auto h-[300px] w-full max-w-[320px] py-6" color="#6B7684" keyColor="#3182F6" />
      </div>

      <ul className="mt-8 space-y-6">
        {POINTS.map((p) => (
          <li key={p.t} className="flex items-start gap-4">
            <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-smoke text-[22px]" aria-hidden>
              {p.icon}
            </span>
            <div>
              <p className="text-[17px] font-semibold">{p.t}</p>
              <p className="mt-0.5 text-[15px] text-mute">{p.d}</p>
            </div>
          </li>
        ))}
      </ul>

      <Link href="/match" className="mt-10 flex items-center gap-4 rounded-card bg-accent-soft p-5 active:scale-[0.99]">
        <span className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-paper text-[24px]" aria-hidden>
          💞
        </span>
        <span className="flex-1">
          <span className="block text-[13px] font-semibold text-accent">NEW</span>
          <span className="block text-[17px] font-bold">그 사람과 나, 궁합 보기</span>
          <span className="block text-[14px] text-sub">사주로 보는 궁합 점수, 사진을 넣으면 관상 궁합까지</span>
        </span>
        <svg className="text-accent" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" aria-hidden>
          <path d="M9 5l7 7-7 7" />
        </svg>
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
