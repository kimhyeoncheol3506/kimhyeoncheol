import Link from "next/link";
import HeroArt from "@/components/HeroArt";
import { pageMeta } from "@/lib/site";
import { GUIDES } from "@/lib/guide";

export const metadata = pageMeta({
  title: "얼굴과 운명 — 무료 사주 × 관상 풀이",
  absoluteTitle: true,
  ogTitle: "당신의 얼굴과 생년월일이 말하는 운명",
  description: "생년월일과 얼굴 사진으로 보는 무료 사주·관상 풀이. 두 엔진이 함께 계산한 사주와 얼굴 비율로 본 관상이 공통으로 말하는 성격·재물·연애·올해 흐름을 쉬운 말로 정리해 드립니다.",
  path: "/",
});

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

// 자주 묻는 질문 (서버 HTML 에 그대로 들어가 검색엔진도 읽을 수 있음)
const FAQ: { q: string; a: string; link?: { href: string; label: string } }[] = [
  { q: "정말 무료인가요?", a: "네. 사주·관상 풀이, 궁합, 운명첩 PDF까지 지금은 모두 무료입니다. 앞으로 일부 상세 리포트가 유료가 되더라도, 결제 전에 무료로 볼 수 있는 미리보기를 먼저 보여 드립니다." },
  { q: "얼굴 사진은 어디에 저장되나요?", a: "어디에도 저장되지 않습니다. 사진은 서버로 보내지 않고 이용자의 휴대폰(브라우저) 안에서만 얼굴 비율을 잰 뒤 바로 지웁니다. 사진 없이 사주만 볼 수도 있습니다.", link: { href: "/privacy", label: "개인정보처리방침" } },
  { q: "태어난 시간을 몰라도 볼 수 있나요?", a: "볼 수 있습니다. ‘시간을 몰라요’를 누르면 시간 기둥을 빼고 세 기둥으로 계산합니다. 성격과 오행의 큰 틀은 그대로 볼 수 있지만, 세밀한 부분은 정확도가 조금 낮아집니다." },
  { q: "1월생인데 띠가 다르게 나와요.", a: "사주에서는 해가 1월 1일이 아니라 입춘(2월 4일 무렵)에 바뀌기 때문입니다. 예를 들어 1990년 1월 1일생은 사주상 1989년 기사년에 속해 뱀띠로 봅니다.", link: { href: "/guide/tti-ipchun", label: "띠와 입춘 해설" } },
  { q: "‘사주와 관상이 같이 말하는 것’은 무슨 뜻인가요?", a: "사주는 서로 다른 두 계산 엔진이 같은 답을 낸 값만 쓰고, 관상은 얼굴 비율로 성향을 봅니다. 그다음 두 결과가 같은 방향을 가리키는 성향만 골라 강조합니다. 한쪽에서만 나온 이야기는 약하게 다룹니다." },
  { q: "결과는 얼마나 정확한가요?", a: "사주와 관상은 전통적인 해석 체계일 뿐 과학적으로 증명된 예측이 아닙니다. 자신을 돌아보고 조심할 점을 생각해 보는 재미와 참고용으로 봐 주세요. 건강·법률·재정 같은 중요한 결정은 전문가와 상담하세요.", link: { href: "/disclaimer", label: "면책조항" } },
  { q: "궁합은 어떻게 계산하나요?", a: "두 사람의 일간이 합을 이루는지, 배우자 자리가 잘 어울리는지, 서로 부족한 기운을 채워 주는지, 띠가 맞는지, 앞으로의 흐름이 함께 좋은지를 각각 20점씩 100점 만점으로 계산합니다.", link: { href: "/guide/gunghap", label: "궁합 보는 법" } },
  { q: "결과를 나중에 다시 볼 수 있나요?", a: "결과는 개인정보 보호를 위해 서버에 저장하지 않고 지금 쓰는 브라우저 창에만 잠시 보관됩니다. 오래 간직하려면 결과 화면의 ‘운명첩 PDF 받기’로 저장해 두세요." },
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
      <section className="pt-10">
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
        <div className="pointer-events-none absolute inset-3 rounded-[1px] border border-accent/15" />
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

      <Link href="/newyear" className="card mt-3 flex items-center gap-4 !p-5 transition active:scale-[0.99]">
        <span className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full font-serif text-[20px] font-bold text-accent ring-1 ring-inset ring-accent/40" aria-hidden>
          未
        </span>
        <span className="flex-1">
          <span className="block font-display text-[12px] font-semibold uppercase tracking-[0.3em] text-accent">2027</span>
          <span className="mt-0.5 block font-serif text-[18px] font-semibold">2027 정미년 신년운세</span>
          <span className="mt-0.5 block text-[14px] text-sub">한 해 총운과 달마다 한 줄 운세, 무료로 먼저 보기</span>
        </span>
        <Chevron />
      </Link>

      {/* 해설 글 */}
      <section className="mt-14">
        <p className="eyebrow">Guide</p>
        <h2 className="mt-2 font-serif text-[22px] font-bold">사주·관상, 쉽게 알고 보기</h2>
        <ul className="mt-4 divide-y divide-line border-y border-line">
          {["saju-palja", "ohaeng", "tti-ipchun", "ilgan-overview", "gwansang-parts", "gunghap"].map((slug) => {
            const g = GUIDES.find((x) => x.slug === slug)!;
            return (
              <li key={slug}>
                <Link href={`/guide/${slug}`} className="flex items-center justify-between gap-3 py-3.5 text-[15px] font-medium">
                  <span>{g.title}</span>
                  <Chevron />
                </Link>
              </li>
            );
          })}
        </ul>
        <Link href="/guide" className="mt-3 inline-block text-[14px] font-semibold text-accent">
          해설 {GUIDES.length}편 모두 보기 ›
        </Link>
      </section>

      {/* 자주 묻는 질문 */}
      <section className="mt-14">
        <p className="eyebrow">FAQ</p>
        <h2 className="mt-2 font-serif text-[22px] font-bold">자주 묻는 질문</h2>
        <div className="mt-4 space-y-2">
          {FAQ.map((f) => (
            <details key={f.q} className="card group !p-0">
              <summary className="flex cursor-pointer list-none items-center justify-between gap-3 px-5 py-4 text-[16px] font-semibold">
                {f.q}
                <span className="text-accent transition group-open:rotate-90" aria-hidden>
                  ›
                </span>
              </summary>
              <div className="px-5 pb-4 text-[15px] leading-[1.75] text-sub">
                {f.a}
                {f.link && (
                  <Link href={f.link.href} className="mt-2 block font-semibold text-accent">
                    {f.link.label} ›
                  </Link>
                )}
              </div>
            </details>
          ))}
        </div>
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              "@context": "https://schema.org",
              "@type": "FAQPage",
              mainEntity: FAQ.map((f) => ({ "@type": "Question", name: f.q, acceptedAnswer: { "@type": "Answer", text: f.a } })),
            }),
          }}
        />
      </section>

      <div className="h-28" />
      <div className="bottom-cta">
        <Link href="/analyze" className="btn-primary w-full">
          무료로 시작하기
        </Link>
      </div>
    </div>
  );
}
