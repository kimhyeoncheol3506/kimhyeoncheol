import Link from "next/link";
import type { ReportLine } from "@/lib/services/company";
import { AI_STAFF } from "@/lib/company/staff";

export function SecretaryReport({ lines }: { lines: ReportLine[] }) {
  const s = AI_STAFF[0];
  return (
    <section aria-label="비서 보고" className="mb-6 rounded-xl border border-brand-100 bg-gradient-to-r from-brand-50 to-white p-4">
      <p className="text-sm font-semibold text-brand-800">
        {s.emoji} <Link href={`/organization/staff/${s.key}`} className="hover:underline">{s.name} {s.title}</Link>의 보고
      </p>
      <ol className="mt-2 space-y-1 text-sm">
        {lines.map((l) => (
          <li key={l.label} className="flex gap-2">
            <span className="w-24 shrink-0 text-xs font-medium leading-5 text-slate-500">{l.label}</span>
            {l.href ? <Link href={l.href} className="text-slate-800 hover:underline">{l.text}</Link> : <span className="text-slate-800">{l.text}</span>}
          </li>
        ))}
      </ol>
    </section>
  );
}
