import Link from "next/link";
import type { ReactNode } from "react";
import type { AiReview } from "@/lib/approval/ai-review";
import { requestBrief } from "@/lib/approval/brief";
import type { RequestWithSteps } from "@/lib/services/approvals";
import { APPROVAL_GATE_LABEL, APPROVAL_STATUS_LABEL, ROLE_LABEL } from "@/lib/labels";
import { dateTime, won } from "@/lib/format";
import { Badge, type Tone } from "@/components/ui/badge";
import { RiskBadge } from "@/components/ui/status";

const STATUS_TONE: Record<RequestWithSteps["status"], Tone> = { PENDING: "amber", APPROVED: "green", REJECTED: "red", CHANGES_REQUESTED: "red", CANCELLED: "gray" };
const GATE_TONE: Record<RequestWithSteps["gate"], Tone> = { CONTENT: "indigo", QUOTE: "teal", CONTRACT: "purple" };

export function RequestCard({ req, preview, actions, blocker }: { req: RequestWithSteps; preview?: ReactNode; actions?: ReactNode; blocker?: string | null }) {
  const ai = req.aiReview as unknown as AiReview | null;
  const brief = requestBrief({ gate: req.gate, title: req.title, amount: req.amount, risk: req.risk, payload: req.payload, blocked: ai?.passed === false });
  return (
    <article className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm" aria-label={req.title}>
      <header className="flex flex-wrap items-center gap-2">
        <Badge tone={GATE_TONE[req.gate]}>{APPROVAL_GATE_LABEL[req.gate]}</Badge>
        <h3 className="text-sm font-semibold text-slate-900">{req.title}</h3>
        <Badge tone={STATUS_TONE[req.status]}>{APPROVAL_STATUS_LABEL[req.status]}</Badge>
        <RiskBadge level={req.risk} />
        {req.amount != null && <span className="text-sm font-semibold tabular-nums">{won(req.amount)}</span>}
      </header>
      <p className="mt-1 text-xs text-slate-500">
        요청 {req.requestedBy?.name ?? "-"} · {dateTime(req.createdAt)}
        {req.rule && ` · 규칙: ${req.rule.name}`}
        {req.gate !== "CONTENT" && (
          <>
            {" · "}
            <Link href={`/inquiries/${req.entityId}`} className="link">문의 보기</Link>
          </>
        )}
      </p>

      <details className="mt-2 rounded-lg bg-slate-50 px-3 py-2 text-xs" open={req.status === "PENDING"}>
        <summary className="cursor-pointer font-medium text-slate-700">결재 요청서</summary>
        <dl className="mt-1 grid gap-x-3 gap-y-0.5 sm:grid-cols-[5.5rem_1fr]">
          {([["대상", brief.target], ["변경 내용", brief.change], ["비용", brief.cost], ["위험", brief.risk], ["되돌리는 법", brief.undo]] as const).map(([k, v]) => (
            <div key={k} className="contents">
              <dt className="text-slate-500">{k}</dt>
              <dd className="text-slate-800">{v}</dd>
            </div>
          ))}
        </dl>
      </details>

      {/* 결재 라인 */}
      <ol className="mt-3 flex flex-wrap items-center gap-1 text-xs" aria-label="결재 라인">
        <li className="rounded-full bg-slate-100 px-2.5 py-1 text-slate-600">🛡️ AI 1차 검토 {ai ? (ai.passed ? "통과" : "차단") : "-"}</li>
        {req.steps.map((s) => {
          const current = req.status === "PENDING" && s.order === req.currentStep;
          const tone = s.decision === "APPROVED" ? "bg-emerald-100 text-emerald-800" : s.decision ? "bg-rose-100 text-rose-800" : current ? "bg-amber-100 text-amber-900 ring-1 ring-amber-300" : "bg-slate-100 text-slate-500";
          return (
            <li key={s.id} className="flex items-center gap-1">
              <span aria-hidden className="text-slate-300">→</span>
              <span className={`rounded-full px-2.5 py-1 ${tone}`} aria-current={current ? "step" : undefined}>
                {s.order + 1}. {ROLE_LABEL[s.requiredRole]}
                {s.decision ? ` · ${s.decision === "APPROVED" ? "승인" : s.decision === "REJECTED" ? "반려" : "수정 요청"} (${s.decidedBy?.name ?? "-"})` : current ? " · 대기" : ""}
              </span>
            </li>
          );
        })}
      </ol>
      {req.steps.filter((s) => s.comment).map((s) => (
        <p key={s.id} className="mt-1 text-xs text-slate-600">💬 {s.order + 1}단계: “{s.comment}”</p>
      ))}

      {ai && ai.findings.length > 0 && (
        <ul className="mt-3 space-y-1" aria-label="AI 1차 검토 결과">
          {ai.findings.map((f) => (
            <li key={f.message} className={`rounded px-2 py-1 text-xs ${f.severity === "block" ? "bg-rose-50 text-rose-800" : "bg-amber-50 text-amber-800"}`}>
              {f.severity === "block" ? "⛔ 차단" : "⚠ 주의"} — {f.message}
            </li>
          ))}
        </ul>
      )}

      {preview && <div className="mt-3">{preview}</div>}
      {actions ? <div className="mt-3 border-t border-slate-100 pt-3">{actions}</div> : blocker && req.status === "PENDING" ? <p className="mt-3 border-t border-slate-100 pt-3 text-xs text-slate-500">{blocker}</p> : null}
    </article>
  );
}
