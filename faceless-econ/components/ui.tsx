import type { ReactNode } from "react";
import { CLASS_LABELS, CONFIDENCE_LABELS } from "@/lib/analysis/faceless";
import type { Confidence, DataSource, FacelessClass } from "@/lib/types";

export function PageTitle({ title, desc, children }: { title: string; desc?: string; children?: ReactNode }) {
  return (
    <div className="mb-6 flex flex-wrap items-end justify-between gap-3">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">{title}</h1>
        {desc && <p className="mt-1 text-sm text-neutral-600">{desc}</p>}
      </div>
      {children}
    </div>
  );
}

export function Card({ title, children, className = "", right }: { title?: ReactNode; children: ReactNode; className?: string; right?: ReactNode }) {
  return (
    <section className={`rounded-xl border border-neutral-200 bg-white p-5 ${className}`}>
      {title && (
        <div className="mb-3 flex items-center justify-between gap-2">
          <h2 className="text-base font-bold">{title}</h2>
          {right}
        </div>
      )}
      {children}
    </section>
  );
}

export function Stat({ label, value, sub }: { label: string; value: ReactNode; sub?: ReactNode }) {
  return (
    <div className="rounded-xl border border-neutral-200 bg-white p-4">
      <div className="text-xs font-medium text-neutral-500">{label}</div>
      <div className="mt-1 text-2xl font-bold tabular-nums">{value}</div>
      {sub && <div className="mt-1 text-xs text-neutral-500">{sub}</div>}
    </div>
  );
}

const TONES = {
  green: "bg-emerald-50 text-emerald-700 ring-emerald-200",
  amber: "bg-amber-50 text-amber-800 ring-amber-200",
  red: "bg-rose-50 text-rose-700 ring-rose-200",
  blue: "bg-sky-50 text-sky-700 ring-sky-200",
  gray: "bg-neutral-100 text-neutral-600 ring-neutral-200",
  violet: "bg-violet-50 text-violet-700 ring-violet-200",
} as const;

export function Badge({ tone = "gray", children, title }: { tone?: keyof typeof TONES; children: ReactNode; title?: string }) {
  return (
    <span title={title} className={`inline-flex items-center whitespace-nowrap rounded-md px-2 py-0.5 text-xs font-medium ring-1 ring-inset ${TONES[tone]}`}>
      {children}
    </span>
  );
}

const CLASS_TONE: Record<FacelessClass, keyof typeof TONES> = { A: "green", B: "green", C: "green", D: "red", E: "amber", U: "gray" };

export function ClassBadge({ cls, confidence }: { cls: FacelessClass; confidence?: Confidence }) {
  return (
    <span className="inline-flex flex-wrap gap-1">
      <Badge tone={CLASS_TONE[cls]}>{CLASS_LABELS[cls]}</Badge>
      {confidence && <Badge tone={confidence === "confirmed" ? "blue" : "gray"}>{CONFIDENCE_LABELS[confidence]}</Badge>}
    </span>
  );
}

export function SourceBadge({ source }: { source: DataSource }) {
  return source === "demo" ? <Badge tone="amber">데모 데이터</Badge> : <Badge tone="green">실제 수집 데이터</Badge>;
}

export function Kind({ kind }: { kind: "관측" | "가설" | "검증되지 않음" | "추정" }) {
  const tone = kind === "관측" ? "blue" : kind === "가설" || kind === "추정" ? "violet" : "gray";
  return <Badge tone={tone}>{kind}</Badge>;
}

export function NA({ children = "수집 불가" }: { children?: ReactNode }) {
  return <span className="text-neutral-400">{children}</span>;
}

export function ScoreBar({ value }: { value: number | null }) {
  if (value == null) return <Badge tone="gray">판정 보류</Badge>;
  return (
    <span className="inline-flex items-center gap-2">
      <span className="relative h-1.5 w-16 overflow-hidden rounded bg-neutral-100">
        <span className="absolute inset-y-0 left-0 rounded" style={{ width: `${value}%`, background: "var(--series-1)" }} />
      </span>
      <span className="tabular-nums font-semibold">{value.toFixed(1)}</span>
    </span>
  );
}

export function Thumb({ url, alt, label, className = "" }: { url: string | null; alt: string; label?: string; className?: string }) {
  if (url) {
    // eslint-disable-next-line @next/next/no-img-element
    return <img src={url} alt={alt} referrerPolicy="no-referrer" className={`aspect-video w-full rounded-lg object-cover bg-neutral-200 ${className}`} />;
  }
  return (
    <div className={`flex aspect-video w-full items-center justify-center rounded-lg bg-gradient-to-br from-slate-700 to-slate-900 p-2 text-center text-xs font-bold text-white/90 ${className}`}>
      {label ?? "썸네일 없음"}
    </div>
  );
}
