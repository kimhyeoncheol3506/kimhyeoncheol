import Link from "next/link";
import type { ReactNode } from "react";

export function EmptyState({ title, description, action }: { title: string; description?: string; action?: ReactNode }) {
  return (
    <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-slate-300 bg-white px-6 py-12 text-center">
      <div className="mb-2 text-3xl" aria-hidden>
        📭
      </div>
      <p className="text-sm font-semibold text-slate-700">{title}</p>
      {description && <p className="mt-1 max-w-md text-xs text-slate-500">{description}</p>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}

export function Alert({ tone = "info", title, children }: { tone?: "info" | "warn" | "error" | "success"; title?: string; children?: ReactNode }) {
  const cls = {
    info: "border-sky-200 bg-sky-50 text-sky-900",
    warn: "border-amber-200 bg-amber-50 text-amber-900",
    error: "border-rose-200 bg-rose-50 text-rose-900",
    success: "border-emerald-200 bg-emerald-50 text-emerald-900",
  }[tone];
  return (
    <div role={tone === "error" ? "alert" : "status"} className={`rounded-lg border px-4 py-3 text-sm ${cls}`}>
      {title && <p className="font-semibold">{title}</p>}
      {children && <div className={title ? "mt-1" : ""}>{children}</div>}
    </div>
  );
}

export function Forbidden({ message = "이 화면을 볼 권한이 없습니다." }: { message?: string }) {
  return (
    <div className="mx-auto max-w-lg py-16">
      <Alert tone="error" title="접근 권한 없음">
        {message} 필요한 경우 관리자에게 권한을 요청하세요.
      </Alert>
    </div>
  );
}

/** 링크 기반 페이지네이션 — 현재 쿼리스트링을 유지 */
export function Pagination({ page, pageCount, basePath, params }: { page: number; pageCount: number; basePath: string; params: Record<string, string | undefined> }) {
  if (pageCount <= 1) return null;
  const href = (p: number) => {
    const sp = new URLSearchParams();
    for (const [k, v] of Object.entries(params)) if (v && k !== "page") sp.set(k, v);
    sp.set("page", String(p));
    return `${basePath}?${sp.toString()}`;
  };
  const pages = Array.from({ length: pageCount }, (_, i) => i + 1).filter((p) => p === 1 || p === pageCount || Math.abs(p - page) <= 2);
  return (
    <nav aria-label="페이지 이동" className="mt-4 flex flex-wrap items-center justify-center gap-1">
      {page > 1 && (
        <Link className="rounded-md px-2.5 py-1 text-sm text-slate-600 hover:bg-slate-100" href={href(page - 1)}>
          ‹ 이전
        </Link>
      )}
      {pages.map((p, i) => (
        <span key={p} className="flex items-center">
          {i > 0 && pages[i - 1] !== p - 1 && <span className="px-1 text-slate-400">…</span>}
          <Link
            href={href(p)}
            aria-current={p === page ? "page" : undefined}
            className={`rounded-md px-2.5 py-1 text-sm ${p === page ? "bg-brand-600 font-semibold text-white" : "text-slate-600 hover:bg-slate-100"}`}
          >
            {p}
          </Link>
        </span>
      ))}
      {page < pageCount && (
        <Link className="rounded-md px-2.5 py-1 text-sm text-slate-600 hover:bg-slate-100" href={href(page + 1)}>
          다음 ›
        </Link>
      )}
    </nav>
  );
}

export function Table({ children, minWidth = 640 }: { children: ReactNode; minWidth?: number }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full divide-y divide-slate-200" style={{ minWidth }}>
        {children}
      </table>
    </div>
  );
}

export function Field({ label, htmlFor, error, hint, children, required }: { label: string; htmlFor: string; error?: string; hint?: string; children: ReactNode; required?: boolean }) {
  return (
    <div>
      <label htmlFor={htmlFor} className="label">
        {label}
        {required && <span className="ml-0.5 text-rose-500" aria-hidden>*</span>}
      </label>
      {children}
      {hint && !error && <p className="mt-1 text-xs text-slate-500">{hint}</p>}
      {error && (
        <p id={`${htmlFor}-error`} className="mt-1 text-xs font-medium text-rose-600">
          {error}
        </p>
      )}
    </div>
  );
}

/** 수평 막대 차트 (SVG 없이 CSS) */
export function BarList({ items, unit = "", emptyText = "데이터 없음" }: { items: { label: string; value: number; sub?: string }[]; unit?: string; emptyText?: string }) {
  const max = Math.max(1, ...items.map((i) => i.value));
  if (items.every((i) => i.value === 0)) return <p className="py-4 text-center text-xs text-slate-400">{emptyText}</p>;
  return (
    <ul className="space-y-2.5">
      {items.map((i) => (
        <li key={i.label}>
          <div className="mb-1 flex justify-between text-xs">
            <span className="font-medium text-slate-700">{i.label}</span>
            <span className="tabular-nums text-slate-600">
              {i.value.toLocaleString("ko-KR")}
              {unit} {i.sub && <span className="text-slate-400">({i.sub})</span>}
            </span>
          </div>
          <div className="h-2.5 overflow-hidden rounded-full bg-slate-100" aria-hidden>
            <div className="h-full rounded-full bg-brand-500" style={{ width: `${(i.value / max) * 100}%` }} />
          </div>
        </li>
      ))}
    </ul>
  );
}
