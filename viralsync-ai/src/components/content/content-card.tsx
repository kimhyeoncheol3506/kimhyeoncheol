import Link from "next/link";
import type { ReactNode } from "react";
import type { ContentStatus, ContentType, PlatformKey } from "@prisma/client";
import { CONTENT_TYPE_LABEL, PLATFORM_LABEL } from "@/lib/labels";
import { dateTime, won } from "@/lib/format";
import { Badge, DemoBadge } from "@/components/ui/badge";
import { ContentStatusBadge } from "@/components/ui/status";

export interface ContentCardData {
  id: string;
  type: ContentType;
  status: ContentStatus;
  platform: PlatformKey | null;
  body: string;
  disclosure: string;
  warnings: string[];
  model: string;
  provider: string;
  costKrw: number;
  createdAt: Date;
  isDemo: boolean;
  campaign?: { id: string; name: string; client?: { name: string } } | null;
  candidate?: { title: string; platform: PlatformKey; postUrl: string } | null;
  createdBy?: { name: string } | null;
  approvals?: { id?: string; decision: string; comment: string | null; createdAt: Date; reviewer: { name: string } }[];
  revisions?: { id: string; before: string; after: string; note: string | null; createdAt: Date; editor: { name: string } | null }[];
  revisionCount?: number;
}

export function ContentCard({ c, actions, showCost = false }: { c: ContentCardData; actions?: ReactNode; showCost?: boolean }) {
  return (
    <article className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm" aria-labelledby={`ct-${c.id}`}>
      <header className="mb-2 flex flex-wrap items-center gap-2">
        <h3 id={`ct-${c.id}`} className="text-sm font-semibold text-slate-900">{CONTENT_TYPE_LABEL[c.type]}</h3>
        <ContentStatusBadge status={c.status} />
        {c.platform && <Badge tone="blue">{PLATFORM_LABEL[c.platform]}</Badge>}
        <Badge tone="gray" title="AI 가 생성한 초안입니다. 사람이 작성한 문구로 표시하지 않습니다.">AI 초안</Badge>
        {c.isDemo && <DemoBadge />}
      </header>
      <p className="whitespace-pre-wrap rounded-lg bg-slate-50 p-3 text-sm leading-relaxed text-slate-800">{c.body}</p>
      <p className="mt-2 text-xs text-slate-500">
        <span className="font-medium text-slate-600">광고 표시:</span> {c.disclosure}
      </p>
      {c.warnings.length > 0 && (
        <ul className="mt-2 space-y-1" aria-label="안전 필터 경고">
          {c.warnings.map((w) => (
            <li key={w} className="rounded bg-amber-50 px-2 py-1 text-xs text-amber-800">⚠ {w}</li>
          ))}
        </ul>
      )}
      <dl className="mt-3 grid grid-cols-2 gap-x-4 gap-y-1 text-xs text-slate-500 sm:grid-cols-3">
        <div><dt className="inline">생성: </dt><dd className="inline">{dateTime(c.createdAt)}</dd></div>
        <div><dt className="inline">모델: </dt><dd className="inline">{c.provider}/{c.model}</dd></div>
        {c.createdBy && <div><dt className="inline">요청자: </dt><dd className="inline">{c.createdBy.name}</dd></div>}
        {c.campaign && (
          <div className="col-span-2 sm:col-span-1">
            <dt className="inline">캠페인: </dt>
            <dd className="inline"><Link className="link" href={`/campaigns/${c.campaign.id}`}>{c.campaign.name}</Link></dd>
          </div>
        )}
        {c.candidate && (
          <div className="col-span-2">
            <dt className="inline">연결 게시물: </dt>
            <dd className="inline">[{PLATFORM_LABEL[c.candidate.platform]}] {c.candidate.title}</dd>
          </div>
        )}
        {showCost && <div><dt className="inline">AI 비용: </dt><dd className="inline">{won(c.costKrw)}</dd></div>}
      </dl>
      {c.approvals && c.approvals.length > 0 && (
        <div className="mt-2 text-xs text-slate-600">
          {c.approvals.slice(0, 3).map((a, i) => (
            <p key={a.id ?? i}>
              <span className="font-medium">{a.decision === "APPROVED" ? "승인" : a.decision === "REJECTED" ? "반려" : "수정 요청"}</span> — {a.reviewer.name} · {dateTime(a.createdAt)}
              {a.comment && <span className="text-slate-500"> · “{a.comment}”</span>}
            </p>
          ))}
        </div>
      )}
      {c.revisions && c.revisions.length > 0 && (
        <details className="mt-2 text-xs">
          <summary className="cursor-pointer font-medium text-slate-600">수정 이력 {c.revisions.length}건</summary>
          <ol className="mt-2 space-y-2">
            {c.revisions.map((r) => (
              <li key={r.id} className="rounded border border-slate-100 p-2">
                <p className="text-slate-500">{r.editor?.name ?? "-"} · {dateTime(r.createdAt)} {r.note && `· ${r.note}`}</p>
                <p className="mt-1 line-through decoration-rose-400">{r.before.slice(0, 200)}</p>
                <p className="mt-1">{r.after.slice(0, 200)}</p>
              </li>
            ))}
          </ol>
        </details>
      )}
      {c.revisionCount != null && c.revisionCount > 0 && !c.revisions && <p className="mt-1 text-xs text-slate-500">수정 이력 {c.revisionCount}건</p>}
      {actions && <div className="mt-3 flex flex-wrap items-start gap-2 border-t border-slate-100 pt-3">{actions}</div>}
    </article>
  );
}
