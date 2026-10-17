"use client";
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
  return (
    <div className="relative">
      <select aria-label={label} className="field appearance-none pr-8" value={value} onChange={(e) => onChange(Number(e.target.value))}>
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

export function Working({ text }: { text: string }) {
  return (
    <motion.div
      className="fixed inset-0 z-50 mx-auto flex max-w-app flex-col items-center justify-center bg-paper px-8 text-center"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      <motion.div
        className="h-14 w-14 rounded-full border-[5px] border-accent-soft border-t-accent"
        animate={{ rotate: 360 }}
        transition={{ repeat: Infinity, duration: 0.9, ease: "linear" }}
      />
      <AnimatePresence mode="wait">
        <motion.p
          key={text}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -8 }}
          className="mt-8 text-title font-bold"
        >
          {text}
        </motion.p>
      </AnimatePresence>
      <p className="mt-2 text-[15px] text-mute">잠시만 기다려 주세요</p>
    </motion.div>
  );
}
