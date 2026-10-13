import type { SajuConsensus } from "@/lib/saju/types";
import { PILLAR_LABEL } from "@/lib/saju/types";
import { ELEMENTS } from "@/lib/saju/constants";

/** 사주팔자 네 기둥 (전통 순서: 시 · 일 · 월 · 년) */
export function PillarBoard({ saju }: { saju: SajuConsensus }) {
  const order = ["hour", "day", "month", "year"] as const;
  return (
    <div className="grid grid-cols-4 border-l border-t border-ink">
      {order.map((k) => {
        const p = saju.pillars.find((x) => x.key === k)!;
        const isDay = k === "day";
        return (
          <div key={k} className={`border-b border-r border-ink ${isDay ? "bg-ink text-paper" : ""}`}>
            <p className={`border-b px-2 py-2 text-center text-[11px] font-semibold tracking-widest ${isDay ? "border-paper/20 text-paper/60" : "border-line text-mute"}`}>
              {PILLAR_LABEL[k]}
              {isDay && <span className="ml-1 text-accent">●</span>}
            </p>
            {p.unknown ? (
              <div className="flex h-[188px] flex-col items-center justify-center md:h-[236px]">
                <span className="text-5xl font-black text-line">?</span>
                <span className="mt-2 text-[11px] text-mute">시간 모름</span>
              </div>
            ) : (
              <>
                <Cell char={p.stem} ko={p.stemKo} el={p.stemElement} god={p.stemTenGod} dark={isDay} />
                <Cell char={p.branch} ko={p.branchKo} el={p.branchElement} god={p.branchTenGod} dark={isDay} />
                {!p.agreed && <p className="pb-2 text-center text-[10px] font-semibold text-accent">판단 보류</p>}
              </>
            )}
          </div>
        );
      })}
    </div>
  );
}

function Cell({ char, ko, el, god, dark }: { char: string; ko: string; el: string; god: string; dark: boolean }) {
  return (
    <div className="flex flex-col items-center py-3 md:py-5">
      <span className="text-[44px] font-black leading-none md:text-6xl">{char}</span>
      <span className={`mt-2 text-xs font-semibold ${dark ? "text-paper/70" : "text-mute"}`}>
        {ko} · {el}
      </span>
      <span className={`mt-1 text-[11px] ${dark ? "text-paper/50" : "text-mute"}`}>{god === "(일간)" ? "나" : god}</span>
    </div>
  );
}

export function ElementBars({ saju }: { saju: SajuConsensus }) {
  const total = ELEMENTS.reduce((a, e) => a + saju.fiveElements[e], 0) || 1;
  return (
    <div className="space-y-3">
      {ELEMENTS.map((e) => {
        const n = saju.fiveElements[e];
        return (
          <div key={e} className="flex items-center gap-4">
            <span className="w-8 text-lg font-black">{e}</span>
            <div className="relative h-7 flex-1 bg-smoke">
              <div
                className={`h-full ${saju.yongsin.includes(e) ? "bg-accent" : "bg-ink"}`}
                style={{ width: `${(n / total) * 100}%`, minWidth: n ? 8 : 0 }}
              />
            </div>
            <span className="w-6 text-right font-bold tabular-nums">{n}</span>
          </div>
        );
      })}
      <p className="pt-2 text-xs text-mute">
        <span className="mr-1 inline-block h-2 w-2 bg-accent" />
        빨간 막대 = 나를 돕는 기운(용신)
      </p>
    </div>
  );
}
