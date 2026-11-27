"use client";
import { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";

export function Q({ title, sub }: { title: string; sub: string }) {
  return (
    <>
      <h1 className="text-headline font-bold">{title}</h1>
      <p className="mt-2 text-[15px] text-mute">{sub}</p>
    </>
  );
}

export function Select({
  value, onChange, options, suffix, label,
}: { value: number; onChange: (v: number) => void; options: number[]; suffix: string; label: string }) {
  // 값을 바꾸면 칸이 잠깐 금빛으로 빛나 "눌렸다"는 걸 바로 알려 줌
  const [flash, setFlash] = useState(false);
  const timer = useRef<ReturnType<typeof setTimeout>>();
  useEffect(() => () => clearTimeout(timer.current), []);
  return (
    <div className="relative">
      <select
        aria-label={label}
        className="field appearance-none pr-8"
        data-flash={flash}
        value={value}
        onChange={(e) => {
          onChange(Number(e.target.value));
          setFlash(true);
          clearTimeout(timer.current);
          timer.current = setTimeout(() => setFlash(false), 650);
        }}
      >
        {options.map((o) => (
          <option key={o} value={o}>
            {o}
            {suffix}
          </option>
        ))}
      </select>
      <svg className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-mute" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" aria-hidden>
        <path d="M6 9l6 6 6-6" />
      </svg>
    </div>
  );
}

/** 지금 고른 값을 한 줄로 보여 주고, 바뀐 글자만 아래에서 위로 갈아 끼움 */
export function Picked({ parts }: { parts: string[] }) {
  return (
    <p className="mt-5 flex flex-wrap items-baseline gap-x-1.5 border-l-2 border-accent/60 pl-3 font-serif text-[19px] font-semibold text-ink" aria-live="polite">
      {parts.map((t, i) => (
        <span key={i} className="relative inline-block overflow-hidden">
          <AnimatePresence mode="popLayout" initial={false}>
            <motion.span
              key={t}
              className="inline-block"
              initial={{ y: "100%", opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              exit={{ y: "-100%", opacity: 0 }}
              transition={{ duration: 0.28, ease: [0.16, 1, 0.3, 1] }}
            >
              {t}
            </motion.span>
          </AnimatePresence>
        </span>
      ))}
    </p>
  );
}

/** 분석 중 화면: 단계 목록이 하나씩 금빛으로 채워짐 */
export function Working({ text, steps, current }: { text: string; steps?: string[]; current?: number }) {
  const list = steps ?? [text];
  const at = current ?? Math.max(0, list.indexOf(text));
  return (
    <motion.div
      className="fixed inset-0 z-50 mx-auto flex max-w-app flex-col justify-center bg-paper px-8"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      <div className="relative h-16 w-16">
        <motion.svg className="absolute inset-0" viewBox="0 0 64 64" fill="none" animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 6, ease: "linear" }} aria-hidden>
          <circle cx="32" cy="32" r="30" stroke="#E6DDCC" strokeWidth="1" />
          <circle cx="32" cy="32" r="30" stroke="#A8823A" strokeWidth="1.4" strokeDasharray="34 155" strokeLinecap="round" />
        </motion.svg>
        <span className="absolute inset-0 flex items-center justify-center font-serif text-[22px] font-semibold text-accent" aria-hidden>
          命
        </span>
      </div>
      <AnimatePresence mode="wait">
        <motion.p key={text} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -8 }} className="mt-8 text-title font-bold">
          {text}
        </motion.p>
      </AnimatePresence>
      <p className="mt-1 text-[15px] text-mute">잠시만 기다려 주세요</p>

      {list.length > 1 && (
        <ol className="mt-8 space-y-3 border-t border-line pt-6">
          {list.map((s, i) => {
            const done = i < at;
            const now = i === at;
            return (
              <li key={s} className="flex items-center gap-3 text-[15px]">
                <span className={`relative flex h-5 w-5 shrink-0 items-center justify-center rounded-full ring-1 ring-inset transition-colors duration-300 ${done ? "bg-accent ring-accent" : now ? "ring-accent" : "ring-line"}`}>
                  {done && (
                    <motion.svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="#FAF6EE" strokeWidth="3.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
                      <motion.path d="M5 12.5l4.5 4.5L19 7" initial={{ pathLength: 0 }} animate={{ pathLength: 1 }} transition={{ duration: 0.35 }} />
                    </motion.svg>
                  )}
                  {now && <motion.span className="h-1.5 w-1.5 rounded-full bg-accent" animate={{ opacity: [1, 0.25, 1] }} transition={{ repeat: Infinity, duration: 1.2 }} />}
                </span>
                <span className={`transition-colors duration-300 ${done ? "text-sub" : now ? "font-semibold text-ink" : "text-mute"}`}>{s}</span>
              </li>
            );
          })}
        </ol>
      )}
    </motion.div>
  );
}
