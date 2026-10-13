"use client";
import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import AuthGate from "@/components/AuthGate";
import Reveal from "@/components/Reveal";
import VoicePlayer from "@/components/VoicePlayer";
import ShareBar from "@/components/ShareBar";
import { ElementBars, PillarBoard } from "@/components/PillarBoard";
import { RESULT_KEY } from "@/lib/resultKey";
import type { ResultPayload } from "@/lib/reading/types";

export default function ResultPage() {
  return (
    <AuthGate>
      <Result />
    </AuthGate>
  );
}

const STRENGTH_KO = { strong: "신강", weak: "신약", neutral: "중화", undetermined: "판단 보류" } as const;

function Result() {
  const [data, setData] = useState<ResultPayload | null | undefined>(undefined);

  useEffect(() => {
    try {
      const raw = sessionStorage.getItem(RESULT_KEY);
      setData(raw ? (JSON.parse(raw) as ResultPayload) : null);
    } catch {
      setData(null);
    }
  }, []);

  const script = useMemo(() => {
    if (!data) return "";
    const r = data.reading;
    const who = data.name ? `${data.name}님의 결과를 읽어드릴게요.` : "당신의 결과를 읽어드릴게요.";
    return [
      who,
      `${r.headline}.`,
      r.summary,
      ...r.sections.flatMap((s) => [`${s.title.replace(/·/g, "와")}.`, ...s.body]),
      "마지막으로 당부드립니다.",
      ...r.advice,
      "본 결과는 오락과 참고용입니다. 좋은 하루 보내세요.",
    ].join(" ");
  }, [data]);

  if (data === undefined) return <div className="min-h-[70vh]" />;
  if (data === null) {
    return (
      <div className="mx-auto flex min-h-[70vh] max-w-page flex-col items-start justify-center px-5 md:px-10">
        <h1 className="text-headline font-black">결과가 없어요.</h1>
        <p className="mt-4 text-mute">결과는 이 브라우저 탭에만 잠시 보관되고, 탭을 닫으면 사라집니다.</p>
        <Link href="/analyze" className="btn-primary mt-10">
          새로 보기 →
        </Link>
      </div>
    );
  }

  const { saju, reading, common, face } = data;

  return (
    <article>
      {/* 헤드라인 */}
      <section className="-mt-16 bg-ink pt-16 text-paper">
        <div className="mx-auto max-w-page px-5 pb-20 pt-14 md:px-10 md:pb-28 md:pt-24">
          <Reveal>
            <p className="label !text-paper/50">
              {data.name ? `${data.name}님의 ` : ""}사주 × 관상 공통 의견
            </p>
            <h1 className="mt-6 text-headline font-black md:text-[clamp(3rem,7vw,7rem)]">{reading.headline}</h1>
          </Reveal>
          <Reveal delay={0.15}>
            <p className="mt-8 max-w-3xl text-lg leading-relaxed text-paper/75 md:text-2xl">{reading.summary}</p>
            <div className="mt-10 flex flex-wrap gap-2">
              {common.map((c) => (
                <span key={c.key} className="border border-paper/30 px-4 py-2 text-sm font-semibold">
                  {c.label}
                </span>
              ))}
            </div>
            <a href="#listen" className="mt-10 inline-flex items-center gap-3 text-sm font-bold text-paper hover:text-accent">
              <span className="flex h-10 w-10 items-center justify-center bg-accent">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" aria-hidden>
                  <path d="M7 4.5v15l12-7.5z" />
                </svg>
              </span>
              목소리로 듣기
            </a>
          </Reveal>
        </div>
      </section>

      {/* 사주팔자 */}
      <section className="mx-auto max-w-page px-5 py-20 md:px-10 md:py-28">
        <div className="grid gap-14 md:grid-cols-12">
          <Reveal className="md:col-span-7">
            <p className="label">Four pillars</p>
            <h2 className="mt-3 text-title font-black">사주팔자 한눈에</h2>
            <div className="mt-8">
              <PillarBoard saju={saju} />
            </div>
          </Reveal>
          <Reveal delay={0.1} className="md:col-span-5">
            <p className="label">Five elements</p>
            <h2 className="mt-3 text-title font-black">오행 분포</h2>
            <div className="mt-8">
              <ElementBars saju={saju} />
            </div>
            <dl className="mt-10 grid grid-cols-2 border-t border-ink">
              <Stat k="일간" v={`${saju.dayMaster.ko}${saju.dayMaster.element}`} />
              <Stat k="신강·신약" v={STRENGTH_KO[saju.strength]} />
              <Stat k="현재 대운" v={saju.currentDaeun ? saju.currentDaeun.ganzhi : "—"} />
              <Stat k="나를 돕는 기운" v={saju.yongsin.length ? saju.yongsin.join("·") : "—"} />
            </dl>
          </Reveal>
        </div>
      </section>

      {/* 공통 의견 */}
      <section className="bg-smoke">
        <div className="mx-auto max-w-page px-5 py-20 md:px-10 md:py-28">
          <Reveal>
            <p className="label">Where they agree</p>
            <h2 className="mt-3 text-headline font-black">
              {face ? "사주와 관상이" : "사주가"}
              <br />
              <span className="text-accent">동시에</span> 말하는 것
            </h2>
          </Reveal>
          <div className="mt-14 space-y-px bg-line">
            {common.map((c, i) => (
              <Reveal key={c.key} delay={i * 0.08} className="grid gap-6 bg-smoke py-8 md:grid-cols-12 md:py-10">
                <div className="md:col-span-5">
                  <span className="text-sm font-bold text-accent">{String(i + 1).padStart(2, "0")}</span>
                  <p className="mt-2 text-3xl font-black tracking-tight md:text-4xl">{c.label}</p>
                  {!c.strong && <p className="mt-2 text-xs text-mute">약하게 겹친 항목</p>}
                </div>
                <div className="grid grid-cols-2 gap-6 md:col-span-7">
                  <Evidence title="사주가 말하길" text={c.sajuReason} value={c.saju} />
                  {face && <Evidence title="관상이 말하길" text={c.faceReason} value={c.face} />}
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* 섹션별 해석 */}
      <section className="mx-auto max-w-page px-5 py-20 md:px-10 md:py-28">
        {reading.sections.map((s) => (
          <Reveal key={s.id} className="grid gap-6 border-t border-ink py-12 md:grid-cols-12 md:py-16">
            <div className="md:col-span-4">
              <p className="text-sm font-bold text-mute">{s.eyebrow}</p>
              <h3 className={`mt-2 text-title font-black ${s.id === "caution" ? "text-accent" : ""}`}>{s.title}</h3>
            </div>
            <div className="space-y-5 md:col-span-8">
              {s.body.map((p, i) => (
                <p key={i} className="text-lg leading-[1.75] md:text-xl">
                  {p}
                </p>
              ))}
            </div>
          </Reveal>
        ))}

        {/* 당부 */}
        <Reveal className="mt-6 bg-accent p-8 text-paper md:p-14">
          <p className="label !text-paper/70">A word for you</p>
          <h3 className="mt-3 text-title font-black">당부드립니다</h3>
          <ul className="mt-8 space-y-5">
            {reading.advice.map((a, i) => (
              <li key={i} className="flex gap-4 text-lg font-medium leading-relaxed md:text-xl">
                <span className="mt-[11px] inline-block h-2 w-2 shrink-0 bg-paper" />
                {a}
              </li>
            ))}
          </ul>
        </Reveal>
      </section>

      {/* 관상 부위별 */}
      {face && (
        <section className="border-t border-line">
          <div className="mx-auto max-w-page px-5 py-20 md:px-10 md:py-28">
            <Reveal>
              <p className="label">Face reading</p>
              <h2 className="mt-3 text-title font-black">관상 부위별 풀이</h2>
            </Reveal>
            <div className="mt-10 grid gap-px bg-line sm:grid-cols-2 lg:grid-cols-3">
              {face.features.map((f, i) => (
                <Reveal key={f.part} delay={(i % 3) * 0.06} className="bg-paper p-6 md:p-8">
                  <p className="label">{f.part}</p>
                  <p className="mt-3 text-xl font-bold tracking-tight">{f.observation}</p>
                  <p className="mt-3 leading-relaxed text-mute">{f.meaning}</p>
                </Reveal>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* 듣기 */}
      <section id="listen" className="scroll-mt-16 bg-ink text-paper">
        <div className="mx-auto max-w-page px-5 py-20 md:px-10 md:py-28">
          <p className="label !text-paper/50">Listen</p>
          <h2 className="mb-10 mt-3 text-title font-black">목소리로 전체 듣기</h2>
          <VoicePlayer script={script} />
        </div>
      </section>

      {/* 공유 */}
      <section className="mx-auto max-w-page px-5 py-20 md:px-10 md:py-24">
        <p className="label">Share</p>
        <h2 className="mb-8 mt-3 text-title font-black">친구에게도 알려 주세요</h2>
        <ShareBar result={data} />
        <div className="mt-14 flex flex-col gap-3 sm:flex-row">
          <Link href="/analyze" className="btn-primary">
            다른 사람 보기 →
          </Link>
        </div>

        <div className="mt-16 border-t border-line pt-8 text-xs leading-relaxed text-mute">
          <p className="font-semibold text-ink">
            본 서비스는 오락 및 참고용이며, 의학적·법적·재정적 조언이 아닙니다. 중요한 결정은 전문가와 상담하세요.
          </p>
        </div>
      </section>
    </article>
  );
}

function Stat({ k, v }: { k: string; v: string }) {
  return (
    <div className="border-b border-line py-4 pr-4">
      <dt className="label">{k}</dt>
      <dd className="mt-1 text-xl font-black tracking-tight">{v}</dd>
    </div>
  );
}

function Evidence({ title, text, value }: { title: string; text: string; value: number }) {
  return (
    <div>
      <p className="label">{title}</p>
      <div className="mt-3 h-1 w-full bg-line">
        <div className="h-full bg-ink" style={{ width: `${Math.round(value * 100)}%` }} />
      </div>
      <p className="mt-3 text-sm leading-relaxed md:text-base">{text}</p>
    </div>
  );
}
