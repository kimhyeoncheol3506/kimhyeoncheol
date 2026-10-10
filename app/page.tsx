import Link from "next/link";
import HeroArt from "@/components/HeroArt";
import Reveal from "@/components/Reveal";

const STEPS = [
  { n: "01", t: "생년월일 입력", d: "양력·음력, 태어난 시간까지. 시간을 몰라도 괜찮습니다." },
  { n: "02", t: "얼굴 사진 한 장", d: "정면 사진을 올리거나 바로 촬영하세요. 사진은 내 기기 안에서만 분석됩니다." },
  { n: "03", t: "읽고, 듣기", d: "사주와 관상이 함께 말하는 것만 골라 정리하고, 목소리로 읽어드립니다." },
];

export default function Landing() {
  return (
    <>
      {/* HERO */}
      <section className="relative -mt-16 overflow-hidden bg-ink pt-16 text-paper">
        <div className="mx-auto grid min-h-[100svh] max-w-page grid-cols-1 items-center px-5 pb-16 pt-10 md:grid-cols-12 md:px-10">
          <div className="relative z-10 md:col-span-7">
            <Reveal>
              <p className="label !text-paper/60">Saju × Gwansang · Free</p>
            </Reveal>
            <Reveal delay={0.1}>
              <h1 className="mt-6 text-headline font-black md:text-[clamp(3rem,6.2vw,6.25rem)]">
                당신의 얼굴과
                <br />
                생년월일이 말하는
                <br />
                <span className="text-accent">운명</span>
              </h1>
            </Reveal>
            <Reveal delay={0.2}>
              <p className="mt-7 text-lg font-medium text-paper/75 md:text-2xl">사주 × 관상, AI가 봐드립니다.</p>
            </Reveal>
            <Reveal delay={0.3}>
              <div className="mt-10 flex flex-col gap-4 sm:flex-row sm:items-center">
                <Link href="/analyze" className="btn-accent w-full text-lg sm:w-auto sm:px-12">
                  지금 바로 무료로 보기
                  <Arrow />
                </Link>
              </div>
              <p className="mt-6 flex items-center gap-2 text-xs text-paper/50">
                <Lock /> 개인정보는 서버에 저장되지 않습니다
              </p>
            </Reveal>
          </div>
          <HeroArt className="pointer-events-none absolute inset-y-0 right-[-18%] w-[95%] opacity-60 md:relative md:right-0 md:col-span-5 md:h-[78vh] md:w-full md:opacity-100" />
        </div>
      </section>

      {/* HOW */}
      <section className="mx-auto max-w-page px-5 py-24 md:px-10 md:py-36">
        <Reveal>
          <p className="label">How it works</p>
          <h2 className="mt-4 text-headline font-black">
            3분이면
            <br />
            충분합니다.
          </h2>
        </Reveal>
        <div className="mt-16 grid gap-px bg-line md:grid-cols-3">
          {STEPS.map((s, i) => (
            <Reveal key={s.n} delay={i * 0.1} className="bg-paper py-10 md:px-8 md:py-12">
              <p className="text-6xl font-black tracking-tighter text-ink md:text-7xl">{s.n}</p>
              <p className="mt-8 text-2xl font-bold tracking-tight">{s.t}</p>
              <p className="mt-3 leading-relaxed text-mute">{s.d}</p>
            </Reveal>
          ))}
        </div>
      </section>

      {/* CONSENSUS */}
      <section className="bg-smoke">
        <div className="mx-auto grid max-w-page gap-16 px-5 py-24 md:grid-cols-2 md:px-10 md:py-36">
          <Reveal>
            <p className="label">Our method</p>
            <h2 className="mt-4 text-title font-black md:text-headline">
              서로 다른 셋이
              <br />
              같은 말을 할 때,
              <br />
              <span className="text-accent">우리는 믿습니다.</span>
            </h2>
            <p className="mt-8 max-w-md leading-relaxed text-mute">
              두 개의 오픈소스 사주 엔진을 동시에 돌리고, 얼굴 랜드마크로 전통 관상을 읽습니다. 그리고 모두가 공통으로
              가리키는 결과만 ‘우리 의견’으로 정리합니다.
            </p>
          </Reveal>
          <div className="flex flex-col justify-center">
            {[
              ["사주 엔진 A", "ssaju · 만세력 / 십성 / 대운"],
              ["사주 엔진 B", "lunar-javascript + 자체 규칙"],
              ["관상", "얼굴 랜드마크 478점 · 전통 관상 규칙"],
            ].map(([a, b], i) => (
              <Reveal key={a} delay={i * 0.12}>
                <div className="flex items-baseline justify-between border-t border-ink py-6">
                  <span className="text-2xl font-black tracking-tight md:text-3xl">{a}</span>
                  <span className="text-right text-sm text-mute">{b}</span>
                </div>
              </Reveal>
            ))}
            <Reveal delay={0.4}>
              <div className="flex items-baseline justify-between bg-ink px-5 py-7 text-paper">
                <span className="text-2xl font-black tracking-tight md:text-3xl">= 우리 의견</span>
                <span className="text-sm text-paper/60">공통 결과만</span>
              </div>
            </Reveal>
          </div>
        </div>
      </section>

      {/* LISTEN */}
      <section className="mx-auto max-w-page px-5 py-24 md:px-10 md:py-36">
        <Reveal>
          <div className="flex flex-col items-start gap-10 md:flex-row md:items-end md:justify-between">
            <h2 className="text-display font-black">
              읽지 말고,
              <br />
              들으세요.
            </h2>
            <div className="max-w-sm">
              <div className="flex h-20 w-20 items-center justify-center bg-accent text-paper">
                <svg width="26" height="26" viewBox="0 0 24 24" fill="currentColor" aria-hidden>
                  <path d="M7 4.5v15l12-7.5z" />
                </svg>
              </div>
              <p className="mt-6 leading-relaxed text-mute">
                플레이 버튼 하나면 목소리가 당신의 운명을 처음부터 끝까지 읽어드립니다. 출근길에, 잠들기 전에.
              </p>
            </div>
          </div>
        </Reveal>
      </section>

      {/* CTA */}
      <section className="bg-ink text-paper">
        <div className="mx-auto flex max-w-page flex-col items-start gap-10 px-5 py-24 md:flex-row md:items-end md:justify-between md:px-10 md:py-32">
          <Reveal>
            <h2 className="text-headline font-black">
              지금,
              <br />
              확인해 보세요.
            </h2>
          </Reveal>
          <Reveal delay={0.1} className="w-full md:w-auto">
            <Link href="/analyze" className="btn-accent w-full text-lg md:w-auto md:px-14">
              무료로 시작하기 <Arrow />
            </Link>
          </Reveal>
        </div>
      </section>
    </>
  );
}

function Arrow() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" aria-hidden>
      <path d="M5 12h14M13 5l7 7-7 7" />
    </svg>
  );
}
function Lock() {
  return (
    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden>
      <rect x="4" y="11" width="16" height="10" />
      <path d="M8 11V7a4 4 0 0 1 8 0v4" />
    </svg>
  );
}
