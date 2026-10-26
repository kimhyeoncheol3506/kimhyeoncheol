import Link from "next/link";
import type { financeSummary } from "@/lib/services/business";
import { won } from "@/lib/format";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

type F = Awaited<ReturnType<typeof financeSummary>>;

/** 대시보드 경영 신호: 단골 목표 · 실패 신호 · 가격 인상 · 분사 조건 */
export function HealthCard({ f }: { f: F }) {
  return (
    <Card className="mb-6">
      <CardHeader title="경영 신호" description="매월 마지막 주 금요일 ‘전략의 날’ 에 1시간 리뷰" action={<Link href="/finance" className="link text-xs">재무 →</Link>} />
      <CardBody className="grid gap-4 text-sm md:grid-cols-3">
        <div>
          <p className="text-xs text-slate-500">유료 단골</p>
          <p className="text-xl font-bold tabular-nums">{f.paying}명 <span className="text-sm font-normal text-slate-500">/ 목표 {f.goal}명</span></p>
          <p className="text-xs text-slate-500">MRR {won(f.mrr)} · 무료 체험 {f.trials}건</p>
        </div>
        <div>
          <p className="text-xs text-slate-500">실패 신호</p>
          {f.failure.length === 0 ? <p className="text-emerald-700">없음</p> : <ul className="list-disc pl-4 text-rose-700">{f.failure.map((x) => <li key={x}>{x}</li>)}</ul>}
          {f.priceRaise && <p className="mt-1 text-amber-700">💡 {f.priceRaise}</p>}
        </div>
        <div>
          <p className="text-xs text-slate-500">분사 조건 ({f.spinoff.filter((s) => s.ok).length}/3) — 억지 분사 금지</p>
          <ul className="space-y-0.5 text-xs">{f.spinoff.map((s) => <li key={s.label}>{s.ok ? "✅" : "⬜"} {s.label}</li>)}</ul>
        </div>
      </CardBody>
    </Card>
  );
}
