import { notFound } from "next/navigation";
import { getPortal } from "@/lib/services/portal";
import { CONTENT_TYPE_LABEL, PLATFORM_LABEL } from "@/lib/labels";
import { ToastProvider } from "@/components/ui/toast";
import { PortalDecision, PortalUpload } from "@/components/portal/forms";
import { MonthlyReport } from "@/components/portal/monthly-report";

export const metadata = { title: "사장님 전용 화면", robots: { index: false, follow: false } };
export const dynamic = "force-dynamic";

export default async function PortalPage({ params, searchParams }: { params: Promise<{ token: string }>; searchParams: Promise<{ tab?: string }> }) {
  const { token } = await params;
  const tab = (await searchParams).tab === "report" ? "report" : "home";
  const p = await getPortal(token, { report: tab === "report" });
  if (!p) notFound();
  return (
    <ToastProvider>
      <main className="mx-auto max-w-2xl space-y-6 px-4 py-8">
        <header>
          <p className="text-xs text-slate-500">{p.orgName}</p>
          <h1 className="text-xl font-bold">{p.client.name} 사장님 전용 화면</h1>
          <nav className="mt-3 flex gap-2 text-sm" aria-label="메뉴">
            <a href={`/c/${token}`} aria-current={tab === "home" ? "page" : undefined} className={`rounded-full px-3 py-1 ${tab === "home" ? "bg-brand-600 text-white" : "bg-white ring-1 ring-slate-200"}`}>승인·사진</a>
            <a href={`/c/${token}?tab=report`} aria-current={tab === "report" ? "page" : undefined} className={`rounded-full px-3 py-1 ${tab === "report" ? "bg-brand-600 text-white" : "bg-white ring-1 ring-slate-200"}`}>지난달 보고서</a>
          </nav>
        </header>

        {tab === "report" && p.report ? (
          <MonthlyReport r={p.report} clientName={p.client.name} />
        ) : (
          <>
            <section aria-label="승인 기다리는 게시물" className="space-y-3">
              <h2 className="font-semibold">승인 기다리는 게시물 ({p.pending.length})</h2>
              <p className="text-xs text-slate-500">사장님이 승인한 것만 올라갑니다.</p>
              {p.pending.length === 0 && <p className="rounded-lg bg-white p-4 text-sm text-slate-500 ring-1 ring-slate-200">지금은 승인할 게시물이 없어요.</p>}
              {p.pending.map((c) => (
                <article key={c.id} className="space-y-3 rounded-xl bg-white p-4 shadow-sm ring-1 ring-slate-200" aria-label={`${CONTENT_TYPE_LABEL[c.type]} 승인`}>
                  <p className="text-xs text-slate-500">{c.platform ? PLATFORM_LABEL[c.platform] : ""} · {CONTENT_TYPE_LABEL[c.type]}</p>
                  <p className="whitespace-pre-line text-sm">{c.body}</p>
                  <PortalDecision token={token} contentId={c.id} />
                </article>
              ))}
            </section>
            {p.decided.length > 0 && (
              <section aria-label="최근 처리">
                <h2 className="mb-2 font-semibold">최근 처리한 것</h2>
                <ul className="space-y-1 text-sm">
                  {p.decided.map((d) => (
                    <li key={d.id}>{d.clientStatus === "APPROVED" ? "👍 승인" : "✏️ 수정 요청"} · {d.platform ? PLATFORM_LABEL[d.platform] : ""} {CONTENT_TYPE_LABEL[d.type]}{d.clientComment ? ` — ${d.clientComment}` : ""}</li>
                  ))}
                </ul>
              </section>
            )}
            <section className="rounded-xl bg-white p-4 shadow-sm ring-1 ring-slate-200">
              <h2 className="mb-2 font-semibold">사진 보내기</h2>
              <p className="mb-3 text-xs text-slate-500">사장님은 사진만 보내 주세요. 영상·글은 저희가 만들어 승인 요청드립니다.</p>
              <PortalUpload token={token} />
              {p.assets.length > 0 && <p className="mt-3 text-xs text-slate-500">지금까지 보낸 사진 {p.assets.length}장 (최근 기준)</p>}
            </section>
          </>
        )}
        <p className="text-center text-[11px] text-slate-400">이 링크는 사장님 전용입니다. 다른 분께 공유하지 마세요.</p>
      </main>
    </ToastProvider>
  );
}
