"use client";
import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import VoicePlayer from "@/components/VoicePlayer";
import SectionCard from "@/components/SectionCard";
import { RELATIONS, type MatchResult } from "@/lib/match/compute";
import { MATCH_KEY } from "@/lib/match/run";

export default function MatchResultPage() {
  const [data, setData] = useState<MatchResult | null>(null);
  const [missing, setMissing] = useState(false);

  useEffect(() => {
    try {
      const raw = sessionStorage.getItem(MATCH_KEY);
      if (raw) setData(JSON.parse(raw));
      else setMissing(true);
    } catch {
      setMissing(true);
    }
  }, []);

  const script = useMemo(() => {
    if (!data) return "";
    return [
      `${data.names[0]}님과 ${data.names[1]}님의 궁합을 읽어드릴게요.`,
      `궁합 점수는 100점 만점에 ${data.total}점, ${data.headline}입니다.`,
      data.summary,
      ...data.sections.flatMap((s) => [`${s.title}.`, ...(s.items?.length ? [s.body[0], ...s.items.map((i) => `${i.label}, ${i.title ?? i.rows[0]?.v ?? ""}.`)] : s.body)]),
      "본 결과는 오락과 참고용입니다.",
    ].join(" ");
  }, [data]);

  if (missing)
    return (
      <div className="px-5 pt-16 text-center">
        <p className="text-title font-bold">결과가 없어요</p>
        <p className="mt-2 text-[15px] text-mute">궁합을 처음부터 다시 봐 주세요.</p>
        <Link href="/match" className="btn-primary mt-8 w-full">
          궁합 보러 가기
        </Link>
      </div>
    );
  if (!data) return null;

  const rel = RELATIONS.find((r) => r.id === data.relation)?.label ?? "";

  return (
    <div className="pb-32">
      <section className="px-5 pt-4 text-center">
        <p className="text-[15px] font-semibold text-accent">{rel}</p>
        <h1 className="mt-2 text-title font-bold">
          {data.names[0]} <span className="text-mute">×</span> {data.names[1]}
        </h1>
        <p className="mt-6 text-[15px] text-mute">두 사람의 궁합</p>
        <motion.p className="mt-1 text-[72px] font-bold leading-none tracking-tight text-ink" initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }} transition={{ type: "spring", damping: 14 }}>
          {data.total}
          <span className="text-[22px] font-semibold text-mute"> / 100</span>
        </motion.p>
        <p className="mt-3 text-[20px] font-bold">{data.headline}</p>
        <div className="mt-5 flex flex-wrap justify-center gap-2">
          <span className="rounded-full bg-smoke px-4 py-2 text-[14px] font-semibold text-sub">주도권은 {data.leader}</span>
          {data.bestMonth && <span className="rounded-full bg-smoke px-4 py-2 text-[14px] font-semibold text-sub">가장 좋은 달 {data.bestMonth}</span>}
          {data.hasFace && <span className="rounded-full bg-accent-soft px-4 py-2 text-[14px] font-semibold text-accent">관상 궁합 포함</span>}
        </div>
        <p className="mt-5 text-[17px] leading-[1.7] text-sub">{data.summary}</p>
      </section>

      <div className="space-y-3 px-4 pt-6">
        <div className="card">
          <h2 className="text-title font-bold">항목별 점수</h2>
          <div className="mt-4 space-y-4">
            {data.scores.map((s, i) => (
              <div key={s.key}>
                <div className="flex items-baseline justify-between">
                  <p className="text-[16px] font-bold">{s.label}</p>
                  <p className="text-[15px] font-semibold text-accent">
                    {s.value}
                    <span className="text-mute"> / 20</span>
                  </p>
                </div>
                <div className="mt-2 h-2 overflow-hidden rounded-full bg-smoke">
                  <motion.div className="h-full rounded-full bg-accent" initial={{ width: 0 }} animate={{ width: `${(s.value / 20) * 100}%` }} transition={{ delay: 0.2 + i * 0.08, duration: 0.6 }} />
                </div>
                <p className="mt-1.5 text-[14px] text-mute">{s.note}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <VoicePlayer script={script} />
        </div>

        {data.sections.map((s) => (
          <SectionCard key={s.id} s={s} />
        ))}

        <p className="px-2 pt-2 text-center text-[13px] leading-relaxed text-mute">
          본 결과는 전통 궁합 이론을 바탕으로 한 오락·참고용이며, 관계의 미래를 단정하지 않습니다. 사진과 고민 내용은 서버로 보내거나 저장하지 않습니다.
        </p>
      </div>

      <div className="bottom-cta">
        <Link href="/match" className="btn-ghost w-full">
          다른 사람과도 보기
        </Link>
      </div>
    </div>
  );
}
