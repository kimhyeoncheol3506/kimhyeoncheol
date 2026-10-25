import type { CampaignStatus, ContentStatus, IntegrationStatus, MetricSource, PublicationStatus, ReviewStatus, RiskLevel, PolicyReviewStatus } from "@prisma/client";
import {
  CAMPAIGN_STATUS_LABEL,
  CONTENT_STATUS_LABEL,
  INTEGRATION_STATUS_LABEL,
  METRIC_SOURCE_LABEL,
  POLICY_STATUS_LABEL,
  PUBLICATION_STATUS_LABEL,
  REVIEW_STATUS_LABEL,
  RISK_LABEL,
  INQUIRY_STATUS_LABEL,
  TASK_STATUS_LABEL,
} from "@/lib/labels";
import { Badge, type Tone } from "./badge";

const CAMPAIGN_TONE: Record<CampaignStatus, Tone> = {
  DRAFT: "gray",
  ANALYZED: "blue",
  PENDING_REVIEW: "amber",
  CHANGES_REQUESTED: "red",
  APPROVED: "indigo",
  READY_TO_RUN: "purple",
  COMPLETED: "green",
  FAILED: "red",
};
export const CampaignStatusBadge = ({ status }: { status: CampaignStatus }) => <Badge tone={CAMPAIGN_TONE[status]}>{CAMPAIGN_STATUS_LABEL[status]}</Badge>;

const CONTENT_TONE: Record<ContentStatus, Tone> = { DRAFT: "gray", PENDING_REVIEW: "amber", APPROVED: "green", REJECTED: "red", CHANGES_REQUESTED: "red" };
export const ContentStatusBadge = ({ status }: { status: ContentStatus }) => <Badge tone={CONTENT_TONE[status]}>{CONTENT_STATUS_LABEL[status]}</Badge>;

const PUB_TONE: Record<PublicationStatus, Tone> = { QUEUED: "purple", SUCCESS: "green", FAILED: "red", BLOCKED: "amber" };
export const PublicationStatusBadge = ({ status }: { status: PublicationStatus }) => <Badge tone={PUB_TONE[status]}>{PUBLICATION_STATUS_LABEL[status]}</Badge>;

const INTEGRATION_TONE: Record<IntegrationStatus, Tone> = { DEMO_ONLY: "gray", API_READY: "blue", AUTHENTICATED: "indigo", PUBLISH_READY: "green", RESTRICTED: "red" };
export const IntegrationBadge = ({ status }: { status: IntegrationStatus }) => <Badge tone={INTEGRATION_TONE[status]}>{INTEGRATION_STATUS_LABEL[status]}</Badge>;

const SOURCE_TONE: Record<MetricSource, Tone> = { SIMULATED: "purple", DEMO_SEED: "purple", VERIFIED: "green", NOT_MEASURED: "gray" };
export const MetricSourceBadge = ({ source }: { source: MetricSource }) => <Badge tone={SOURCE_TONE[source]}>{METRIC_SOURCE_LABEL[source]}</Badge>;

const REVIEW_TONE: Record<ReviewStatus, Tone> = { UNREVIEWED: "gray", SUITABLE: "green", UNSUITABLE: "red", ON_HOLD: "amber" };
export const ReviewBadge = ({ status }: { status: ReviewStatus }) => <Badge tone={REVIEW_TONE[status]}>{REVIEW_STATUS_LABEL[status]}</Badge>;

const RISK_TONE: Record<RiskLevel, Tone> = { LOW: "green", MEDIUM: "amber", HIGH: "red" };
export const RiskBadge = ({ level }: { level: RiskLevel }) => <Badge tone={RISK_TONE[level]}>위험 {RISK_LABEL[level]}</Badge>;

const POLICY_TONE: Record<PolicyReviewStatus, Tone> = { NOT_REVIEWED: "red", IN_PROGRESS: "amber", COMPLETED: "green" };
export const PolicyStatusBadge = ({ status }: { status: PolicyReviewStatus }) => <Badge tone={POLICY_TONE[status]}>{POLICY_STATUS_LABEL[status]}</Badge>;

export function ScoreBar({ value, invert = false }: { value: number | null; invert?: boolean }) {
  if (value == null) return <span className="text-xs font-medium text-slate-400">분석 불가</span>;
  const good = invert ? value < 35 : value >= 60;
  const mid = invert ? value < 60 : value >= 40;
  const color = good ? "bg-emerald-500" : mid ? "bg-amber-500" : "bg-rose-500";
  return (
    <div className="flex items-center gap-2" role="meter" aria-valuenow={value} aria-valuemin={0} aria-valuemax={100}>
      <div className="h-2 w-24 overflow-hidden rounded-full bg-slate-100">
        <div className={`h-full ${color}`} style={{ width: `${value}%` }} />
      </div>
      <span className="text-xs font-semibold tabular-nums text-slate-700">{value}</span>
    </div>
  );
}

const INQUIRY_TONE: Record<import("@prisma/client").InquiryStatus, Tone> = { NEW: "blue", PENDING_APPROVAL: "purple", QUOTED: "amber", WON: "green", LOST: "gray" };
export const InquiryStatusBadge = ({ status }: { status: import("@prisma/client").InquiryStatus }) => (
  <Badge tone={INQUIRY_TONE[status]}>{INQUIRY_STATUS_LABEL[status]}</Badge>
);

const TASK_TONE: Record<import("@prisma/client").TaskStatus, Tone> = { TODO: "gray", IN_PROGRESS: "blue", DONE: "green", BLOCKED: "red" };
export const TaskStatusBadge = ({ status }: { status: import("@prisma/client").TaskStatus }) => <Badge tone={TASK_TONE[status]}>{TASK_STATUS_LABEL[status]}</Badge>;
