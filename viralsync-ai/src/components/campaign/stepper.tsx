import type { CampaignStatus } from "@prisma/client";
import { CAMPAIGN_STATUS_LABEL, CAMPAIGN_STATUS_ORDER } from "@/lib/labels";

export function StatusStepper({ status }: { status: CampaignStatus }) {
  const effective: CampaignStatus = status === "CHANGES_REQUESTED" ? "PENDING_REVIEW" : status === "FAILED" ? "COMPLETED" : status;
  const idx = CAMPAIGN_STATUS_ORDER.indexOf(effective);
  return (
    <ol className="flex flex-wrap gap-y-2 text-xs" aria-label="캠페인 진행 단계">
      {CAMPAIGN_STATUS_ORDER.map((s, i) => {
        const done = i < idx || (i === idx && status === "COMPLETED");
        const current = i === idx;
        let label = CAMPAIGN_STATUS_LABEL[s];
        if (s === "COMPLETED") label = status === "FAILED" ? "실행 실패" : "실행 완료 / 실패";
        if (s === "PENDING_REVIEW" && status === "CHANGES_REQUESTED") label = "수정 요청됨";
        const tone =
          current && (status === "FAILED" || status === "CHANGES_REQUESTED")
            ? "bg-rose-600 text-white"
            : done || current
              ? "bg-brand-600 text-white"
              : "bg-slate-200 text-slate-500";
        return (
          <li key={s} className="flex items-center" aria-current={current ? "step" : undefined}>
            <span className={`rounded-full px-2.5 py-1 font-medium ${tone}`}>{label}</span>
            {i < CAMPAIGN_STATUS_ORDER.length - 1 && <span className="mx-1 text-slate-300" aria-hidden>→</span>}
          </li>
        );
      })}
    </ol>
  );
}
