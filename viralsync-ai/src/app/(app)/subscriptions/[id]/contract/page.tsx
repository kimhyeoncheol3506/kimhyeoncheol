import Link from "next/link";
import { requireCtx } from "@/lib/auth/current";
import { getSubscription } from "@/lib/services/subscriptions";
import { MONEY } from "@/lib/business/playbook";
import { dateOnly, won } from "@/lib/format";
import { orNotFound } from "@/lib/page";
import { prisma } from "@/lib/db";
import { PrintButton } from "@/components/print/print-button";

export const metadata = { title: "계약서" };

/** 월 정액 SNS 운영대행 계약서 (PART 4-3 최소 7개 조항 + 부록 A) */
export default async function ContractPage({ params }: { params: Promise<{ id: string }> }) {
  const ctx = await requireCtx();
  const s = await orNotFound(getSubscription(ctx, (await params).id));
  const org = await prisma.organization.findUniqueOrThrow({ where: { id: ctx.organizationId }, select: { name: true } });
  const blank = "＿＿＿＿＿＿＿＿";
  const clauses: [string, React.ReactNode][] = [
    ["제1조 (당사자)", <>갑(의뢰인): {s.client.name} (사업자등록번호 {blank}) / 을(운영대행자): {org.name} (사업자등록번호 {blank})</>],
    ["제2조 (서비스 내용)", <>을은 갑의 SNS 계정 운영을 대행하며, 월 납품 내역은 아래 별표 1과 같다.</>],
    [
      "제3조 (비용과 결제)",
      <>월 {won(s.monthlyFee)} ({s.vatIncluded ? "부가세 포함" : "부가세 별도"}), 매월 {s.billingDay}일까지 을의 사업자 계좌로 지급한다. 미납이 {MONEY.suspendAfterMissed}회가 되면 을은 서비스를 중지할 수 있으며, 15일 이상 미납 시 계약을 해지할 수 있다.{s.trialEnd && <> 무료 체험 기간은 {s.trialStart ? dateOnly(s.trialStart) : ""} ~ {dateOnly(s.trialEnd)} 이며, 유료 전환 첫 달은 {s.firstMonthDiscount}% 할인한다.</>}</>,
    ],
    ["제4조 (저작권)", <>납품물의 저작권은 착수 시 갑에게 귀속된다.{s.portfolioConsent ? " 을은 포트폴리오 목적의 사용권을 갖는다." : " 을은 갑의 별도 동의 없이 포트폴리오로 사용하지 않는다."}{s.caseStudyConsent && " 갑은 성과(조회수 성장 등)를 사례로 공개하는 데 동의한다."}</>],
    ["제5조 (사전 승인과 AI 보조 도구)", <>을은 AI 보조 도구를 사용할 수 있으며, 모든 게시물은 갑의 사전 승인 후 발행한다.</>],
    ["제6조 (오류와 책임 제한)", <>AI 도구 오류 등으로 명백한 오표기가 발생한 경우 을은 48시간 내 수정한다. 을의 고의 또는 중과실이 없는 한, 이를 넘어서는 간접 손해는 배상하지 않는다.</>],
    ["제7조 (해지)", <>계약 해지는 {s.noticeDays}일 전 서면(카카오톡 등 기록이 남는 메시지 포함)으로 통보한다. 중도 해지 시 비용은 일할 계산한다.</>],
    ["제8조 (분쟁 해결)", <>이 계약에 관한 분쟁은 을의 주소지 관할 법원으로 한다.</>],
  ];
  return (
    <>
      <div className="no-print mb-4 flex items-center justify-between">
        <Link href={`/subscriptions/${s.id}`} className="link text-sm">← 계약</Link>
        <PrintButton />
      </div>
      <article className="mx-auto max-w-3xl rounded-xl border border-slate-200 bg-white p-10 text-sm leading-relaxed shadow-sm print:border-0 print:p-0 print:shadow-none">
        <h1 className="text-center text-xl font-bold">SNS 운영대행 계약서 (월 정액)</h1>
        <div className="mt-6 space-y-3">
          {clauses.map(([t, b]) => (
            <section key={t}>
              <h2 className="font-semibold">{t}</h2>
              <p>{b}</p>
            </section>
          ))}
        </div>
        <h2 className="mt-6 font-semibold">별표 1 — 월 납품 내역 ({s.planName})</h2>
        <table className="mt-2 w-full border text-left">
          <thead><tr className="bg-slate-50"><th className="border px-2 py-1">항목</th><th className="border px-2 py-1">주기</th></tr></thead>
          <tbody>{s.deliverables.map((d) => <tr key={d}><td className="border px-2 py-1">{d}</td><td className="border px-2 py-1">월</td></tr>)}</tbody>
        </table>
        <div className="mt-10 grid grid-cols-2 gap-8">
          <p>갑: {s.client.name}<br />대표 {blank} (서명)</p>
          <p>을: {org.name}<br />대표 {blank} (서명)</p>
        </div>
        <p className="mt-8 text-xs text-slate-400 print:text-slate-500">이 양식은 책의 최소 조항을 옮긴 참고용이며 법률 자문이 아닙니다. 첫 계약 전 변호사·법률구조공단 상담으로 한 번 검토받기를 권합니다.</p>
      </article>
    </>
  );
}
