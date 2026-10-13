"use client";
import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { AnimatePresence, motion } from "framer-motion";
import AuthGate from "@/components/AuthGate";
import VoicePlayer from "@/components/VoicePlayer";
import ShareBar from "@/components/ShareBar";
import { ElementBars, PillarBoard } from "@/components/PillarBoard";
import { RESULT_KEY } from "@/lib/resultKey";
import type { ResultPayload, Section } from "@/lib/reading/types";

const UNLOCK_KEY = "fate-unlocked";
const PRICE = "3,900원";
// 무료로 보여 주는 섹션 (나머지는 잠금)
const FREE_SECTIONS = ["personality"];

export default function ResultPage() {
  return (
    <AuthGate>
      <Result />
    </AuthGate>
  );
}

function Result() {
  const [data, setData] = useState<ResultPayload | null | undefined>(undefined);
  const [unlocked, setUnlocked] = useState(false);
  const [sheet, setSheet] = useState(false);
  const [detail, setDetail] = useState(false);

  useEffect(() => {
    try {
      const raw = sessionStorage.getItem(RESULT_KEY);
      setData(raw ? (JSON.parse(raw) as ResultPayload) : null);
      setUnlocked(sessionStorage.getItem(UNLOCK_KEY) === raw?.length.toString());
    } catch {
      setData(null);
    }
  }, []);

  const unlock = () => {
    // 1단계에서 실제 결제로 바뀝니다. 지금은 출시 전 미리보기라 무료로 엽니다.
    try {
      sessionStorage.setItem(UNLOCK_KEY, String(sessionStorage.getItem(RESULT_KEY)?.length ?? ""));
    } catch {
      /* 무시 */
    }
    setUnlocked(true);
    setSheet(false);
  };

  const script = useMemo(() => {
    if (!data) return "";
    const r = data.reading;
    const visible = r.sections.filter((s) => unlocked || FREE_SECTIONS.includes(s.id));
    return [
      "당신의 결과를 읽어드릴게요.",
      `${r.headline}.`,
      r.summary,
      ...visible.flatMap((s) => [`${s.title.replace(/·/g, "와")}.`, ...s.body]),
      ...(unlocked ? ["마지막으로 당부드립니다.", ...r.advice] : []),
      "본 결과는 오락과 참고용입니다.",
    ].join(" ");
  }, [data, unlocked]);

  if (data === undefined) return <div className="min-h-[70vh]" />;
  if (data === null) {
    return (
      <div className="flex min-h-[70vh] flex-col justify-center px-5">
        <h1 className="text-headline font-bold">결과가 없어요</h1>
        <p className="mt-2 text-[15px] text-mute">결과는 이 화면에만 잠시 보관되고, 창을 닫으면 사라져요.</p>
        <div className="bottom-cta">
          <Link href="/analyze" className="btn-primary w-full">
            새로 보기
          </Link>
        </div>
      </div>
    );
  }

  const { saju, reading, common, face } = data;
  const free = reading.sections.filter((s) => FREE_SECTIONS.includes(s.id));
  const paid = reading.sections.filter((s) => !FREE_SECTIONS.includes(s.id));

  return (
    <div className="bg-smoke pb-40">
      {/* 한 문장 요약 */}
      <section className="bg-paper px-5 pb-8 pt-4">
        <p className="text-[15px] font-semibold text-accent">사주와 관상이 같이 말하는 나</p>
        <h1 className="mt-2 text-display font-bold">{reading.headline}</h1>
        <div className="mt-5 flex flex-wrap gap-2">
          {common.map((c) => (
            <span key={c.key} className="rounded-full bg-accent-soft px-3 py-1.5 text-[14px] font-semibold text-accent">
              {c.label}
            </span>
          ))}
        </div>
        <p className="mt-5 text-[17px] leading-[1.7] text-sub">{reading.summary}</p>
      </section>

      <div className="space-y-3 px-4 pt-3">
        {/* 목소리 */}
        <div className="card">
          <VoicePlayer script={script} />
        </div>

        {/* 무료 섹션 */}
        {free.map((s) => (
          <SectionCard key={s.id} s={s} />
        ))}

        {/* 유료 섹션 */}
        {unlocked ? (
          <>
            {paid.map((s) => (
              <SectionCard key={s.id} s={s} />
            ))}
            <div className="card bg-accent text-paper">
              <p className="text-[15px] font-semibold text-paper/80">당부드려요</p>
              <ul className="mt-3 space-y-3">
                {reading.advice.map((a, i) => (
                  <li key={i} className="text-[17px] font-medium leading-relaxed">
                    {a}
                  </li>
                ))}
              </ul>
            </div>
            {face && (
              <div className="card">
                <h2 className="text-title font-bold">관상 부위별 풀이</h2>
                <div className="mt-4 divide-y divide-line">
                  {face.features.map((f) => (
                    <div key={f.part} className="py-4">
                      <p className="text-[13px] font-semibold text-mute">{f.part}</p>
                      <p className="mt-1 text-[17px] font-semibold">{f.observation}</p>
                      <p className="mt-1 text-[15px] leading-relaxed text-sub">{f.meaning}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        ) : (
          <div className="card">
            <h2 className="text-title font-bold">더 깊은 이야기가 남았어요</h2>
            <ul className="mt-4 space-y-4">
              {paid.map((s) => (
                <li key={s.id}>
                  <p className="text-[17px] font-semibold">{s.title}</p>
                  <p className="mt-1 select-none text-[15px] leading-relaxed text-sub blur-[5px]" aria-hidden>
                    {s.body[0]}
                  </p>
                </li>
              ))}
              {face && (
                <li>
                  <p className="text-[17px] font-semibold">관상 부위별 풀이 {face.features.length}가지</p>
                  <p className="mt-1 select-none text-[15px] text-sub blur-[5px]" aria-hidden>
                    {face.features[0]?.meaning}
                  </p>
                </li>
              )}
            </ul>
            <button className="btn-primary mt-6 w-full" onClick={() => setSheet(true)}>
              전체 풀이 보기 · {PRICE}
            </button>
          </div>
        )}

        {/* 자세히 (사주표) */}
        <div className="card">
          <button className="flex w-full items-center justify-between" onClick={() => setDetail((v) => !v)} aria-expanded={detail}>
            <span className="text-[17px] font-semibold">내 사주팔자 자세히 보기</span>
            <svg className={`text-mute transition ${detail ? "rotate-180" : ""}`} width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" aria-hidden>
              <path d="M6 9l6 6 6-6" />
            </svg>
          </button>
          {detail && (
            <div className="mt-5 space-y-6">
              <PillarBoard saju={saju} />
              <ElementBars saju={saju} />
            </div>
          )}
        </div>

        {/* 공유 */}
        <div className="card">
          <h2 className="text-title font-bold">친구에게도 알려 주세요</h2>
          <p className="mt-1 text-[15px] text-mute">생일이나 사진은 공유되지 않아요.</p>
          <div className="mt-5">
            <ShareBar result={data} />
          </div>
        </div>

        <p className="px-2 pt-2 text-[13px] leading-relaxed text-mute">
          본 서비스는 오락 및 참고용이며, 의학적·법적·재정적 조언이 아닙니다. 중요한 결정은 전문가와 상담하세요.
          {reading.source === "ai" && " 이 풀이는 AI가 작성했습니다."}
        </p>
      </div>

      <div className="bottom-cta">
        {unlocked ? (
          <Link href="/analyze" className="btn-ghost w-full">
            다른 사람도 보기
          </Link>
        ) : (
          <button className="btn-primary w-full" onClick={() => setSheet(true)}>
            전체 풀이 보기 · {PRICE}
          </button>
        )}
      </div>

      <AnimatePresence>{sheet && <PaySheet onClose={() => setSheet(false)} onUnlock={unlock} />}</AnimatePresence>
    </div>
  );
}

function SectionCard({ s }: { s: Section }) {
  return (
    <div className="card">
      <h2 className={`text-title font-bold ${s.id === "caution" ? "text-warn" : ""}`}>{s.title}</h2>
      <div className="mt-3 space-y-3">
        {s.body.map((p, i) => (
          <p key={i} className="text-[17px] leading-[1.7] text-sub">
            {p}
          </p>
        ))}
      </div>
    </div>
  );
}

/** 결제 바텀시트 — 1단계에서 실제 결제(토스페이)로 연결 */
function PaySheet({ onClose, onUnlock }: { onClose: () => void; onUnlock: () => void }) {
  return (
    <motion.div className="fixed inset-0 z-50 mx-auto max-w-app" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
      <button className="absolute inset-0 bg-ink/40" aria-label="닫기" onClick={onClose} />
      <motion.div
        className="absolute inset-x-0 bottom-0 rounded-t-[24px] bg-paper px-5 pb-[max(20px,env(safe-area-inset-bottom))] pt-3"
        initial={{ y: "100%" }}
        animate={{ y: 0 }}
        exit={{ y: "100%" }}
        transition={{ type: "spring", damping: 30, stiffness: 300 }}
      >
        <div className="mx-auto h-1 w-10 rounded-full bg-line" />
        <h2 className="mt-6 text-title font-bold">전체 풀이 {PRICE}</h2>
        <ul className="mt-4 space-y-2 text-[15px] text-sub">
          <li>· 재물·직업, 연애, 건강 상세 풀이</li>
          <li>· 앞으로 3년 흐름과 주의할 점</li>
          <li>· 관상 부위별 풀이 전체</li>
          <li>· 전체 내용을 목소리로 듣기</li>
        </ul>
        <p className="mt-5 rounded-2xl bg-accent-soft px-4 py-3 text-[14px] font-medium text-accent">
          정식 출시 전이라 지금은 무료로 전체를 보여 드려요.
        </p>
        <button className="btn-primary mt-4 w-full" onClick={onUnlock}>
          무료로 전체 보기
        </button>
        <button className="mt-2 h-12 w-full text-[15px] font-medium text-mute" onClick={onClose}>
          다음에 할게요
        </button>
      </motion.div>
    </motion.div>
  );
}
