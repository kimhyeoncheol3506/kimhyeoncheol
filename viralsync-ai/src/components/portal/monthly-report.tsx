import type { clientMonthlyReport } from "@/lib/services/portal";

type Report = Awaited<ReturnType<typeof clientMonthlyReport>>;

/** 월 보고서 반 장 (부록 C) — 고객 화면·사장님 링크에서 같이 쓴다 */
export function MonthlyReport({ r, clientName }: { r: Report; clientName: string }) {
  const max = Math.max(1, ...r.posts.map((p) => p.views));
  return (
    <article className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm print:border-0 print:shadow-none" aria-label="월 보고서">
      <p className="text-xs text-slate-400">{r.period} 월 보고서 · {clientName}</p>
      <h2 className="mt-1 text-lg font-bold">① {r.summary}</h2>
      <h3 className="mt-4 text-sm font-semibold">② 게시물별 조회수</h3>
      {r.posts.length === 0 ? (
        <p className="mt-1 text-sm text-slate-500">아직 집계할 게시물이 없습니다.</p>
      ) : (
        <ul className="mt-2 space-y-1.5">
          {r.posts.map((p) => (
            <li key={p.id} className="text-xs">
              <div className="flex justify-between gap-2"><span className="truncate">{p.title || p.label}</span><span className="tabular-nums">{p.views.toLocaleString("ko-KR")}</span></div>
              <div className="h-2 rounded bg-slate-100"><div className="h-2 rounded bg-brand-500" style={{ width: `${(p.views / max) * 100}%` }} /></div>
            </li>
          ))}
        </ul>
      )}
      {r.best && <p className="mt-4 text-sm"><strong>③ 베스트</strong> — {r.best.title} ({r.best.views.toLocaleString("ko-KR")}회 · {r.best.label})</p>}
      <p className="mt-2 text-sm"><strong>④ 다음 달 제안</strong> — {r.suggestion}</p>
      {r.contractNote && <p className="mt-2 text-sm"><strong>⑤ 안내</strong> — {r.contractNote}</p>}
      {r.simulated && <p className="mt-3 text-[11px] text-slate-400">일부 수치는 모의 실행·데모 값입니다 (실측 연결 전).</p>}
    </article>
  );
}
