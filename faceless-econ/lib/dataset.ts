// 화면에서 사용하는 데이터셋 조립 (서버 전용)
// 실제 수집 데이터가 있으면 실제 데이터, 없으면 데모 데이터를 사용하고 출처를 명시한다. 두 데이터는 섞지 않는다.

import { channelShare, eligibleForBenchmark } from "./analysis/faceless";
import { DEMO_TOP3, generateDemo } from "./demo";
import { candidateById, CANDIDATES } from "./candidates";
import { DAY_MS, inWindow, rankScores, scoreChannels, scoreVideos, type ChannelScore, type ScoreSnapshot, type ScoreVideo, type VideoScore } from "./scoring/viral";
import { loadStore } from "./store";
import type { ChannelRecord, CollectionRun, DataSource, Settings, Snapshot, VideoAnnotation, VideoRecord } from "./types";
import { hasApiKey } from "./youtube/client";

export interface MissingSummary {
  videosTotal: number;
  likesHidden: number;
  commentsHidden: number;
  publishedUnknown: number;
  unavailable: number;
  subscribersHidden: number;
  facelessUnverified: number;
  viralHold: number;
  relativeMissing: number;
  failedRuns: number;
}

export interface ChannelView {
  channel: ChannelRecord;
  score: ChannelScore;
  recent: VideoRecord[];
  meanViews: number | null;
  medianViews: number | null;
  facelessRatio: number | null;
  eligible: boolean;
}

export interface Dataset {
  source: DataSource;
  sourceReason: string;
  apiKeyConfigured: boolean;
  now: number;
  periodStart: number;
  periodEnd: number;
  settings: Settings;
  channels: ChannelRecord[];
  channelMap: Map<string, ChannelRecord>;
  videos: VideoRecord[];
  videoMap: Map<string, VideoRecord>;
  recent: VideoRecord[];
  pastHits: VideoRecord[];
  snapshots: Snapshot[];
  scores: VideoScore[];
  scoreMap: Map<string, VideoScore>;
  channelViews: ChannelView[];
  pinnedTop3: string[];
  autoTop3: string[];
  runs: CollectionRun[];
  lastCollectedAt: string | null;
  missing: MissingSummary;
  annotations: Record<string, VideoAnnotation>;
}

function med(a: number[]): number | null {
  if (!a.length) return null;
  const s = [...a].sort((x, y) => x - y);
  const m = Math.floor(s.length / 2);
  return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2;
}

export function toScoreVideo(v: VideoRecord): ScoreVideo {
  return {
    id: v.id,
    channelId: v.channelId,
    format: v.format,
    publishedAt: v.publishedAt ? Date.parse(v.publishedAt) : null,
    observedAt: Date.parse(v.collectedAt),
    views: v.viewCount,
    likes: v.likeCount,
    comments: v.commentCount,
    subscribers: v.channelSubscriberCount,
    facelessCls: v.faceless.cls,
    facelessConfidence: v.faceless.confidence,
  };
}

export function getDataset(): Dataset {
  const store = loadStore();
  const settings = store.settings;
  const realVideos = Object.values(store.videos).filter((v) => v.source === "real");
  const hasReal = realVideos.length > 0;
  let source: DataSource;
  let sourceReason: string;
  if (settings.dataMode === "demo") {
    source = "demo";
    sourceReason = "설정에서 데모 모드를 선택했습니다.";
  } else if (settings.dataMode === "real" || hasReal) {
    source = "real";
    sourceReason = hasReal ? "YouTube Data API v3로 수집한 실제 데이터입니다." : "실제 모드지만 아직 수집된 데이터가 없습니다.";
  } else {
    source = "demo";
    sourceReason = hasApiKey()
      ? "API 키는 설정되었지만 아직 수집을 실행하지 않았습니다. '데이터 및 설정'에서 수집을 실행하세요."
      : "YOUTUBE_API_KEY가 없어 데모 데이터로 표시합니다.";
  }

  let channels: ChannelRecord[];
  let videos: VideoRecord[];
  let snapshots: Snapshot[];
  let now: number;
  if (source === "demo") {
    const d = generateDemo();
    channels = d.channels;
    videos = d.videos;
    snapshots = d.snapshots;
    now = Date.parse(d.generatedAt);
  } else {
    channels = Object.values(store.channels).filter((c) => c.source === "real");
    videos = realVideos;
    snapshots = store.snapshots.filter((s) => store.videos[s.videoId]?.source === "real");
    now = Date.now();
  }

  // 사용자의 페이스리스 수동 판정 반영 (영상 단위 > 채널 단위)
  if (source === "real") {
    channels = channels.map((c) => {
      const ov = settings.facelessOverrides[c.id];
      return ov
        ? { ...c, faceless: { cls: ov.cls, confidence: ov.confirmed ? "confirmed" : "estimated", evidence: [`사용자 입력: ${ov.note || "메모 없음"}`, ...c.faceless.evidence] } }
        : c;
    });
    videos = videos.map((v) => {
      const a = store.annotations[v.id]?.faceless;
      if (a) return { ...v, faceless: { cls: a.cls, confidence: a.confirmed ? "confirmed" : "estimated", evidence: ["사용자 영상 확인 입력"] } };
      return v;
    });
  }

  const available = videos.filter((v) => v.status === "available");
  const periodStart = now - settings.periodDays * DAY_MS;
  const recent = available.filter((v) => inWindow(v.publishedAt ? Date.parse(v.publishedAt) : null, now, settings.periodDays));
  const peers = available.filter((v) => inWindow(v.publishedAt ? Date.parse(v.publishedAt) : null, now, settings.peerWindowDays));
  const scoreSnaps: ScoreSnapshot[] = snapshots.map((s) => ({ videoId: s.videoId, at: Date.parse(s.collectedAt), views: s.viewCount }));
  const scores = scoreVideos(recent.map(toScoreVideo), peers.map(toScoreVideo), scoreSnaps, {
    weights: settings.weights,
    peerWindowDays: settings.peerWindowDays,
  });
  const scoreMap = new Map(scores.map((s) => [s.videoId, s]));
  const chScores = scoreChannels(scores, channels.map((c) => c.id));

  const channelViews: ChannelView[] = channels.map((c, i) => {
    const rv = recent.filter((v) => v.channelId === c.id);
    const views = rv.map((v) => v.viewCount).filter((x): x is number => x != null);
    const share = channelShare(rv.map((v) => v.faceless));
    const cls = c.faceless.cls;
    return {
      channel: c,
      score: chScores[i],
      recent: rv,
      meanViews: views.length ? views.reduce((a, b) => a + b, 0) / views.length : null,
      medianViews: med(views),
      facelessRatio: share.facelessRatio,
      eligible: eligibleForBenchmark(cls, cls === "E" ? share.facelessRatio : 1),
    };
  });

  const pinnedTop3 = source === "demo" ? DEMO_TOP3 : settings.pinnedTop3.filter((id) => channels.some((c) => c.id === id));
  const autoTop3 = channelViews
    .filter((cv) => cv.eligible && cv.score.status === "ok")
    .sort((a, b) => (b.score.medianFinal ?? 0) - (a.score.medianFinal ?? 0))
    .slice(0, 3)
    .map((cv) => cv.channel.id);

  const pastHits = available
    .filter((v) => v.publishedAt && Date.parse(v.publishedAt) < periodStart)
    .sort((a, b) => (b.viewCount ?? 0) - (a.viewCount ?? 0))
    .slice(0, 15);

  const runs = source === "real" ? store.runs : [];
  const missing: MissingSummary = {
    videosTotal: recent.length,
    likesHidden: recent.filter((v) => v.likeCount == null).length,
    commentsHidden: recent.filter((v) => v.commentCount == null).length,
    publishedUnknown: videos.filter((v) => v.publishedAt == null).length,
    unavailable: videos.filter((v) => v.status === "unavailable").length,
    subscribersHidden: channels.filter((c) => c.subscriberCount == null).length,
    facelessUnverified: recent.filter((v) => v.faceless.confidence !== "confirmed").length,
    viralHold: scores.filter((s) => s.viralStatus === "hold").length,
    relativeMissing: scores.filter((s) => s.metrics.relative.raw == null).length,
    failedRuns: runs.filter((r) => r.status === "failed").length,
  };

  return {
    source,
    sourceReason,
    apiKeyConfigured: hasApiKey(),
    now,
    periodStart,
    periodEnd: now,
    settings,
    channels,
    channelMap: new Map(channels.map((c) => [c.id, c])),
    videos,
    videoMap: new Map(videos.map((v) => [v.id, v])),
    recent,
    pastHits,
    snapshots,
    scores,
    scoreMap,
    channelViews,
    pinnedTop3,
    autoTop3,
    runs,
    lastCollectedAt: source === "demo" ? new Date(now).toISOString() : (store.runs[0]?.finishedAt ?? null),
    missing,
    annotations: source === "real" ? store.annotations : {},
  };
}

export function rankedRecent(ds: Dataset, format: "long" | "shorts" | "other", key: "viralScore" | "finalScore" = "finalScore") {
  return rankScores(ds.scores.filter((s) => s.format === format), key);
}

/**
 * 수집 대상 채널 ID: 초기 후보 + 교체 후보 전체(제외 판정 검증용 포함) + 사용자 고정 3개 + 슬롯3 후보 + 사용자 추가.
 * 채널 15개 기준 1회 수집 비용은 대략 50~150단위로 일일 할당량(10,000)에 비해 작다.
 */
export function targetChannelIds(settings: Settings): string[] {
  const ids = new Set<string>();
  for (const c of CANDIDATES) if (c.channelId) ids.add(c.channelId);
  for (const id of settings.pinnedTop3) ids.add(id);
  for (const id of settings.slot3Candidates) ids.add(id);
  for (const id of settings.extraChannelIds) ids.add(id);
  return [...ids];
}

export { candidateById };
