"use client";
import { motion } from "framer-motion";
import type { SajuConsensus } from "@/lib/saju/types";
import { PILLAR_LABEL } from "@/lib/saju/types";
import { ELEMENTS } from "@/lib/saju/constants";

/** 사주팔자 네 기둥 (전통 순서: 시 · 일 · 월 · 년) */
export function PillarBoard({ saju }: { saju: SajuConsensus }) {
  const order = ["hour", "day", "month", "year"] as const;
  return (
    <div className="grid grid-cols-4 gap-1.5">
      {order.map((k, i) => {
        const p = saju.pillars.find((x) => x.key === k)!;
        const isDay = k === "day";
        return (
          // 네 기둥이 패를 뒤집듯 차례로 돌아섬
          <motion.div
            key={k}
            className={`overflow-hidden rounded-[6px] ring-1 ring-inset ${isDay ? "bg-ink text-paper ring-accent/60" : "bg-paper ring-line"}`}
            style={{ transformPerspective: 800 }}
            initial={{ rotateY: -90, opacity: 0 }}
            animate={{ rotateY: 0, opacity: 1 }}
            transition={{ delay: 0.08 + i * 0.12, duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
          >
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
          </motion.div>
        );
      })}
    </div>
  );
}

function Cell({ char, ko, el, god, dark }: { char: string; ko: string; el: string; god: string; dark: boolean }) {
  return (
    <div className="flex flex-col items-center py-3">
      <span className={`font-serif text-[34px] font-bold leading-none ${dark ? "text-[#E9D29A]" : ""}`}>{char}</span>
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
      {ELEMENTS.map((e, i) => {
        const n = saju.fiveElements[e];
        return (
          <div key={e} className="flex items-center gap-4">
            <span className="w-6 font-serif text-[16px] font-bold">{e}</span>
            <div className="relative h-[6px] flex-1 overflow-hidden rounded-[1px] bg-line/60">
              {/* 화면에 보이면 왼쪽부터 차오름 */}
              <motion.div
                className={`h-full ${saju.yongsin.includes(e) ? "bg-gradient-to-r from-[#C9A45C] to-accent" : "bg-mute/70"}`}
                style={{ minWidth: n ? 8 : 0 }}
                initial={{ width: 0 }}
                whileInView={{ width: `${(n / total) * 100}%` }}
                viewport={{ once: true }}
                transition={{ delay: 0.1 + i * 0.08, duration: 0.9, ease: [0.16, 1, 0.3, 1] }}
              />
            </div>
            <span className="w-5 text-right text-[15px] font-semibold tabular-nums text-sub">{n}</span>
          </div>
        );
      })}
      <p className="pt-2 text-xs text-mute">
        <span className="mr-1 inline-block h-2 w-2 rounded-full bg-accent" />
        금색 막대 = 나를 돕는 기운
      </p>
    </div>
  );
}
