import { SCORE_LABELS } from "@/lib/match/share";

/** 궁합 점수 카드 (결과 화면·공유 화면·이미지 저장에 같이 씀) */
export default function MatchScoreCard({ names, relation, total, headline, scores, leader }: { names: [string, string]; relation: string; total: number; headline: string; scores: number[]; leader: string }) {
  return (
    <div className="gold-frame relative overflow-hidden px-6 py-7 text-center" style={{ background: "linear-gradient(160deg,#FBF7EF 0%,#F1E6CF 100%)" }}>
      <div className="pointer-events-none absolute inset-3 rounded-[1px] border border-accent/25" />
      <p className="relative font-display text-[11px] font-semibold uppercase tracking-[0.34em] text-accent">{relation}</p>
      <p className="relative mt-2 font-serif text-[22px] font-bold">
        {names[0]} <span className="text-mute">×</span> {names[1]}
      </p>
      <p className="relative mt-3 font-serif text-[72px] font-bold leading-none">
        <span className="gold-text">{total}</span>
        <span className="text-[20px] text-mute"> / 100</span>
      </p>
      <p className="relative mt-2 font-serif text-[18px] font-bold">{headline}</p>
      <div className="relative mt-5 grid grid-cols-5 gap-1">
        {SCORE_LABELS.map((l, i) => (
          <div key={l}>
            <p className="text-[12px] text-mute">{l}</p>
            <p className="font-serif text-[18px] font-bold">{scores[i]}</p>
          </div>
        ))}
      </div>
      <p className="relative mt-4 text-[13px] text-sub">주도권은 {leader}</p>
      <p className="relative mt-4 text-[11px] tracking-wider text-mute">얼굴과 운명 · faceandfate.vercel.app</p>
    </div>
  );
}
