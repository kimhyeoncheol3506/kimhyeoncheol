import "server-only";
import { CONTENT_TYPE_LABEL, METRIC_SOURCE_LABEL, PLATFORM_LABEL, PUBLICATION_STATUS_LABEL } from "@/lib/labels";
import { toCsv } from "@/lib/csv";
import type { CampaignSummaryRow, PublicationRow } from "@/lib/services/reports";

export function publicationsCsv(rows: PublicationRow[], showCost: boolean): string {
  const headers = ["고객명", "캠페인명", "플랫폼", "게시물 유형", "연결 콘텐츠 URL", "담당자", "승인자", "실행 일시", "실행 모드", "실행 결과", "오류 코드", "재시도", "클릭", "방문", "전환", "실적 출처", ...(showCost ? ["AI 비용(원)"] : [])];
  const data = rows.map((r) => [
    r.client,
    r.campaign,
    PLATFORM_LABEL[r.platform],
    CONTENT_TYPE_LABEL[r.contentType as keyof typeof CONTENT_TYPE_LABEL] ?? r.contentType,
    r.targetUrl ?? "",
    r.owner,
    r.approver,
    r.executedAt ? r.executedAt.toISOString() : "",
    r.mode === "SIMULATED" ? "모의" : "실제",
    PUBLICATION_STATUS_LABEL[r.status as keyof typeof PUBLICATION_STATUS_LABEL] ?? r.status,
    r.errorCode ?? "",
    r.retryCount,
    r.clicks ?? "미측정",
    r.visits ?? "미측정",
    r.conversions ?? "미측정",
    METRIC_SOURCE_LABEL[r.metricSource],
    ...(showCost ? [r.aiCost ?? 0] : []),
  ]);
  return toCsv(headers, data);
}

export function campaignsCsv(rows: CampaignSummaryRow[], showCost: boolean): string {
  const headers = ["고객명", "캠페인명", "담당자", "성공 건수", "실패 건수", "클릭", "방문", "전환", "실적 출처", ...(showCost ? ["광고비(원)", "AI 비용(원)", "총비용(원)"] : [])];
  const data = rows.map((r) => [
    r.client,
    r.campaign,
    r.owner,
    r.success,
    r.failed,
    r.clicks,
    r.visits,
    r.conversions,
    r.sources
      .split("/")
      .map((s) => METRIC_SOURCE_LABEL[s as keyof typeof METRIC_SOURCE_LABEL] ?? s)
      .join("/"),
    ...(showCost ? [r.adSpend ?? 0, r.aiCost ?? 0, r.totalCost ?? 0] : []),
  ]);
  return toCsv(headers, data);
}
