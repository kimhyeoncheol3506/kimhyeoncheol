import type { SajuConsensus } from "@/lib/saju/types";
import { PILLAR_LABEL } from "@/lib/saju/types";
import { ELEMENTS } from "@/lib/saju/constants";

/** 사주팔자 네 기둥 (전통 순서: 시 · 일 · 월 · 년) */
export function PillarBoard({ saju }: { saju: SajuConsensus }) {
  const order = ["hour", "day", "month", "year"] as const;
  return (
    <div className="grid grid-cols-4 gap-1.5">
      {order.map((k) => {
        const p = saju.pillars.find((x) => x.key === k)!;
        const isDay = k === "day";
        return (
          <div key={k} className={`overflow-hidden rounded-2xl ${isDay ? "bg-accent text-paper" : "bg-smoke"}`}>
            <p className={`px-2 pt-3 text-center text-[12px] font-semibold ${isDay ? "text-paper/80" : "text-mute"}`}>
              {PILLAR_LABEL[k]}
              {isDay && <span className="ml-1">· 나</span>}
            </p>
            {p.unknown ? (
              <div className="flex h-[180px] flex-col items-center justify-center">
                <span className="text-4xl font-bold text-line">?</span>
                <span className="mt-2 text-[11px] text-mute">시간 모름</span>
              </div>
            ) : (
              <>
                <Cell char={p.stem} ko={p.stemKo} el={p.stemElement} god={p.stemTenGod} dark={isDay} />
                <Cell char={p.branch} ko={p.branchKo} el={p.branchElement} god={p.branchTenGod} dark={isDay} />
                {!p.agreed && <p className="pb-2 text-center text-[10px] font-semibold text-warn">판단 보류</p>}
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
    <div className="flex flex-col items-center py-3">
      <span className="text-[34px] font-bold leading-none">{char}</span>
      <span className={`mt-1.5 text-[12px] font-semibold ${dark ? "text-paper/80" : "text-sub"}`}>
        {ko} · {el}
      </span>
      <span className={`mt-0.5 text-[11px] ${dark ? "text-paper/70" : "text-mute"}`}>{god === "(일간)" ? "나" : god}</span>
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
            <span className="w-6 text-[15px] font-bold">{e}</span>
            <div className="relative h-3 flex-1 overflow-hidden rounded-full bg-smoke">
              <div
                className={`h-full rounded-full ${saju.yongsin.includes(e) ? "bg-accent" : "bg-mute"}`}
                style={{ width: `${(n / total) * 100}%`, minWidth: n ? 8 : 0 }}
              />
            </div>
            <span className="w-5 text-right text-[15px] font-semibold tabular-nums text-sub">{n}</span>
          </div>
        );
      })}
      <p className="pt-2 text-xs text-mute">
        <span className="mr-1 inline-block h-2 w-2 rounded-full bg-accent" />
        파란 막대 = 나를 돕는 기운
      </p>
    </div>
  );
}
