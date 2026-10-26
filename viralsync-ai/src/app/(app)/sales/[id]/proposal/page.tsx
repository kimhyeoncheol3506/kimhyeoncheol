import Link from "next/link";
import { requireCtx } from "@/lib/auth/current";
import { can } from "@/lib/auth/permissions";
import { getProspect } from "@/lib/services/sales";
import { monthlyPlans } from "@/lib/services/subscriptions";
import { trialTerms } from "@/lib/business/playbook";
import { won } from "@/lib/format";
import { orNotFound } from "@/lib/page";
import { prisma } from "@/lib/db";
import { Forbidden } from "@/components/ui/misc";
import { PrintButton } from "@/components/print/print-button";

export const metadata = { title: "제안서" };

/** 제안서 3페이지 (PART 8-1): 진단 → 변화 계획 → 패키지·가격·무료 2주 */
export default async function ProposalPage({ params }: { params: Promise<{ id: string }> }) {
  const ctx = await requireCtx();
  if (!can(ctx.role, "sales:manage")) return <Forbidden />;
  const p = await orNotFound(getProspect(ctx, (await params).id));
  const [org, plans] = await Promise.all([
    prisma.organization.findUniqueOrThrow({ where: { id: ctx.organizationId }, select: { name: true, positioning: true } }),
    monthlyPlans(ctx),
  ]);
  const problems = p.diagnosis.split(/\r?\n/).map((l) => l.trim()).filter(Boolean).slice(0, 3);
  const page = "print-break mb-6 rounded-xl border border-slate-200 bg-white p-8 shadow-sm print:mb-0 print:min-h-[95vh] print:border-0 print:shadow-none";

  return (
    <>
      <div className="no-print mb-4 flex flex-wrap items-center justify-between gap-2">
        <Link href={`/sales/${p.id}`} className="link text-sm">← {p.name}</Link>
        <div className="flex items-center gap-3">
          {problems.length === 0 && <span className="text-xs text-amber-700">진단 메모(문제 3줄)를 먼저 적으면 1쪽이 채워집니다.</span>}
          <PrintButton />
        </div>
      </div>

      <section className={page} aria-label="1쪽 진단">
        <p className="text-xs text-slate-400">1 / 3 · {org.name}</p>
        <h1 className="mt-2 text-2xl font-bold">{p.name} 사장님께 드리는 SNS 진단</h1>
        {org.positioning && <p className="mt-1 text-sm text-slate-600">{org.positioning}</p>}
        <div className="mt-6 rounded-lg border border-dashed border-slate-300 p-6 text-center text-sm text-slate-400">
          현재 인스타그램 화면 스크린샷을 붙이는 자리 ({p.instagram ?? "계정"})
        </div>
        <h2 className="mt-6 font-semibold">지금 아쉬운 점 3가지</h2>
        <ol className="mt-2 list-decimal space-y-1 pl-5">
          {(problems.length ? problems : ["(진단 메모를 입력하세요)"]).map((x) => <li key={x}>{x}</li>)}
        </ol>
      </section>

      <section className={page} aria-label="2쪽 계획">
        <p className="text-xs text-slate-400">2 / 3</p>
        <h1 className="mt-2 text-2xl font-bold">이렇게 바꿔 드립니다</h1>
        <div className="mt-6 grid grid-cols-2 gap-4">
          <div className="rounded-lg border border-dashed border-slate-300 p-6 text-center text-sm text-slate-400">지금 (전)</div>
          <div className="rounded-lg border border-dashed border-brand-300 p-6 text-center text-sm text-brand-400">시안 (후) — 무료 시안 이미지</div>
        </div>
        <ul className="mt-6 list-disc space-y-1 pl-5">
          <li>매주 정해진 요일에 릴스·게시물이 꾸준히 올라갑니다</li>
          <li>사장님은 사진만 보내 주시면 됩니다 — 시안은 전담팀이 3개씩 만들어 드립니다</li>
          <li>올라가는 모든 게시물은 사장님이 먼저 보고 승인하십니다</li>
          <li>매주 월요일 예정표, 금요일 결과 요약, 매월 반 장짜리 보고서를 드립니다</li>
        </ul>
      </section>

      <section className={page} aria-label="3쪽 가격">
        <p className="text-xs text-slate-400">3 / 3</p>
        <h1 className="mt-2 text-2xl font-bold">패키지와 가격</h1>
        <table className="mt-6 w-full text-sm">
          <thead><tr className="border-b text-left"><th className="py-2">패키지</th><th>월 금액</th><th>포함 내역</th></tr></thead>
          <tbody>
            {plans.map((pl) => (
              <tr key={pl.name} className="border-b border-slate-100 align-top">
                <td className="py-2 font-medium">{pl.name}</td>
                <td className="py-2 tabular-nums">{won(pl.monthlyFee)}</td>
                <td className="py-2 text-slate-600">{pl.deliverables.join(" · ")}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <h2 className="mt-6 font-semibold">시작 조건</h2>
        <ul className="mt-2 list-disc space-y-1 pl-5">{trialTerms().map((t) => <li key={t}>{t}</li>)}</ul>
        <p className="mt-6 text-xs text-slate-500">부가세 별도 · 결제는 사업자 계좌로 · 결정은 2주 체험 후 천천히 하셔도 됩니다.</p>
      </section>
    </>
  );
}
