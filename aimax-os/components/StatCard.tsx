import Link from "next/link";

// 대시보드 숫자 카드
export function StatCard({
  label,
  value,
  hint,
  href,
  alert,
}: {
  label: string;
  value: string | number;
  hint?: string;
  href?: string;
  alert?: boolean;
}) {
  const body = (
    <div className={`card h-full transition hover:border-brand-line ${alert ? "border-rose-200 bg-rose-50/40" : ""}`}>
      <p className="text-xs font-medium text-sub">{label}</p>
      <p className={`mt-2 text-2xl font-bold sm:text-3xl tracking-tight ${alert ? "text-rose-600" : ""}`}>{value}</p>
      {hint && <p className="mt-1 text-xs text-mute">{hint}</p>}
    </div>
  );
  return href ? <Link href={href}>{body}</Link> : body;
}
