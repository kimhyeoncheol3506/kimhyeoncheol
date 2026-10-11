// CSV·JSON 내보내기
// Excel이 한글을 올바르게 인식하도록 UTF-8 BOM을 붙이고 줄바꿈은 CRLF를 사용한다.
// 결측값은 빈 칸이 아니라 '수집 불가'/'판정 보류' 등 명시적 문자열로 내보낸다.

import type { Dataset } from "./dataset";
import { METRIC_LABELS, VIRAL_METRICS } from "./scoring/viral";
import { kst } from "./time";

export const BOM = "﻿";

export function csvCell(v: unknown): string {
  if (v == null) return "";
  const s = typeof v === "string" ? v : typeof v === "number" ? (Number.isFinite(v) ? String(v) : "") : JSON.stringify(v);
  return /[",\r\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
}

export function toCsv(header: string[], rows: unknown[][]): string {
  return BOM + [header, ...rows].map((r) => r.map(csvCell).join(",")).join("\r\n") + "\r\n";
}

const orNA = (v: number | null | undefined, label = "수집 불가") => (v == null ? label : v);

export function videosCsv(ds: Dataset): string {
  const header = [
    "데이터출처", "순위대상(최근기간)", "영상ID", "영상URL", "채널ID", "채널명", "제목", "게시시각(UTC)", "게시시각(KST)", "형식", "형식판별근거",
    "길이(초)", "조회수", "좋아요", "댓글", "구독자(관측당시)", "수집시각(UTC)", "썸네일URL", "제목키워드", "페이스리스분류", "페이스리스확인수준", "상태",
    ...VIRAL_METRICS.flatMap((m) => [`${METRIC_LABELS[m]}_원본`, `${METRIC_LABELS[m]}_정규화`, `${METRIC_LABELS[m]}_비고`]),
    "바이럴성과점수", "판정상태", "보류사유", "사용가중치", "가중치반영률", "페이스리스적합성점수", "최종벤치마킹우선순위", "최종결합가중치", "경고", "정규화방식", "결측처리",
  ];
  const recentIds = new Set(ds.recent.map((v) => v.id));
  const rows = ds.videos.map((v) => {
    const s = ds.scoreMap.get(v.id);
    return [
      v.source === "demo" ? "데모" : "실제", recentIds.has(v.id) ? "예" : "아니오", v.id, v.url, v.channelId, ds.channelMap.get(v.channelId)?.title ?? "", v.title,
      v.publishedAt ?? "확인 불가", kst(v.publishedAt), v.format, v.formatEvidence, orNA(v.durationSec), orNA(v.viewCount), orNA(v.likeCount, "비공개/수집 불가"),
      orNA(v.commentCount, "비활성/수집 불가"), orNA(v.channelSubscriberCount, "비공개/수집 불가"), v.collectedAt, v.thumbnailUrl ?? "수집 불가", v.keywords.join(" "),
      v.faceless.cls, v.faceless.confidence, v.status,
      ...VIRAL_METRICS.flatMap((m) => (s ? [orNA(s.metrics[m].raw, "결측"), orNA(s.metrics[m].norm, "결측"), s.metrics[m].note ?? ""] : ["", "", "순위 대상 아님"])),
      s ? orNA(s.viralScore, "판정 보류") : "", s?.viralStatus ?? "", s?.holdReason ?? "", s ? JSON.stringify(s.weightsUsed) : "", s ? s.weightCoverage : "",
      s ? orNA(s.facelessScore, "확인 불가") : "", s ? orNA(s.finalScore, "판정 보류") : "", s ? JSON.stringify(s.finalWeightsUsed) : "", s?.warnings.join(" | ") ?? "",
      "형식(롱폼/쇼츠/기타)별 백분위 순위(0~100, 동점 평균)", "결측 지표 제외 후 가중치 재조정(0점 처리 안 함)",
    ];
  });
  return toCsv(header, rows);
}

export function channelsCsv(ds: Dataset): string {
  const header = ["데이터출처", "채널ID", "채널명", "채널URL", "구독자", "누적조회수", "공개영상수", "최근기간영상수", "평균조회수", "중앙조회수", "채널바이럴점수(중앙값)", "최종우선순위(중앙값)", "판정상태", "페이스리스분류", "확인수준", "판정근거", "수집시각"];
  const rows = ds.channelViews.map((cv) => [
    cv.channel.source === "demo" ? "데모" : "실제", cv.channel.id, cv.channel.title, cv.channel.url, orNA(cv.channel.subscriberCount, "비공개/수집 불가"), orNA(cv.channel.viewCount),
    orNA(cv.channel.videoCount), cv.recent.length, orNA(cv.meanViews), orNA(cv.medianViews), orNA(cv.score.medianViral, "판정 보류"), orNA(cv.score.medianFinal, "판정 보류"),
    cv.score.holdReason ?? "정상", cv.channel.faceless.cls, cv.channel.faceless.confidence, cv.channel.faceless.evidence.join(" | "), cv.channel.collectedAt ?? "",
  ]);
  return toCsv(header, rows);
}

export function snapshotsCsv(ds: Dataset): string {
  return toCsv(
    ["영상ID", "수집시각(UTC)", "조회수", "좋아요", "댓글"],
    ds.snapshots.map((s) => [s.videoId, s.collectedAt, orNA(s.viewCount), orNA(s.likeCount), orNA(s.commentCount)]),
  );
}

export function datasetJson(ds: Dataset) {
  return {
    source: ds.source,
    sourceNote: ds.sourceReason,
    exportedAt: new Date().toISOString(),
    period: { startUtc: new Date(ds.periodStart).toISOString(), endUtc: new Date(ds.periodEnd).toISOString(), days: ds.settings.periodDays },
    settings: ds.settings,
    method: {
      normalization: "형식(롱폼/쇼츠/기타)별 백분위 순위(0~100, 동점 평균)",
      missing: "결측 지표는 계산에서 제외하고 관측 가능한 지표의 가중치를 재조정. 설정 가중치의 50% 미만만 관측되면 판정 보류",
      relative: "같은 채널·형식, 최근 90일 영상 중 경과 시간 1/1.5~1.5배 스냅샷의 시간당 조회수 중앙값 대비. 비교 영상 3개 미만이면 미계산",
      milestones: "24h/72h/7d/14d 시점 ±20% 안의 실제 스냅샷만 사용, 역산하지 않음",
    },
    channels: ds.channels,
    videos: ds.videos,
    scores: ds.scores,
    snapshots: ds.snapshots,
  };
}
