// 바이럴 점수 계산 모듈 (순수 함수만 포함 — 단위 테스트 대상)
//
// 원칙
// 1) 결측값은 0점으로 처리하지 않는다. 관측 가능한 지표의 가중치만 재조정한다.
// 2) 스냅샷이 없는 과거 시점의 조회수는 역산하지 않는다.
// 3) 롱폼·쇼츠·기타는 서로 다른 그룹에서 정규화·순위화한다.
// 4) '바이럴 성과 점수'와 '페이스리스 제작 적합성 점수'는 따로 계산하고, 마지막에만 결합한다.

import type { Confidence, FacelessClass, VideoFormat, Weights } from "../types";

export const HOUR_MS = 3_600_000;
export const DAY_MS = 24 * HOUR_MS;

/** 이 경과 시간 미만이면 시간당 조회수의 변동성이 크다는 경고를 붙인다. */
export const YOUNG_VIDEO_HOURS = 24;
/** 채널 내 상대 성과: 비교 영상의 경과 시간이 대상의 1/1.5 ~ 1.5배 안에 있어야 '비슷한 경과 시간'으로 본다. */
export const PEER_AGE_TOLERANCE = 1.5;
/** 채널 내 상대 성과를 계산하려면 최소 이만큼의 비교 영상이 필요하다. */
export const MIN_PEERS = 3;
/** 같은 형식 그룹의 영상이 이보다 적으면 정규화 순위가 의미 없으므로 판정 보류. */
export const MIN_GROUP_SIZE = 3;
/** 실제로 계산에 포함된 바이럴 지표 가중치가 설정 가중치의 이 비율 미만이면 판정 보류. */
export const MIN_WEIGHT_COVERAGE = 0.5;

export const MILESTONES = [
  { key: "h24", label: "24시간", hours: 24 },
  { key: "h72", label: "72시간", hours: 72 },
  { key: "d7", label: "7일", hours: 168 },
  { key: "d14", label: "14일", hours: 336 },
] as const;
export type MilestoneKey = (typeof MILESTONES)[number]["key"];
/** 스냅샷 경과 시간이 기준 시점의 ±20% 안이면 해당 시점의 관측값으로 인정 */
export const MILESTONE_TOLERANCE = 0.2;

export const VIRAL_METRICS = ["velocity", "relative", "subRatio", "likeRate", "commentRate"] as const;
export type ViralMetric = (typeof VIRAL_METRICS)[number];

export const METRIC_LABELS: Record<ViralMetric | "faceless", string> = {
  velocity: "시간당 조회수",
  relative: "채널 내 상대 성과",
  subRatio: "구독자 대비 조회수",
  likeRate: "좋아요율",
  commentRate: "댓글률",
  faceless: "페이스리스 재현 적합성",
};

export interface ScoreSnapshot {
  videoId: string;
  at: number; // epoch ms
  views: number | null;
}

export interface ScoreVideo {
  id: string;
  channelId: string;
  format: VideoFormat;
  publishedAt: number | null; // epoch ms
  observedAt: number; // 최신 관측 시각 epoch ms
  views: number | null;
  likes: number | null;
  comments: number | null;
  subscribers: number | null;
  facelessCls: FacelessClass;
  facelessConfidence: Confidence;
}

export interface MetricResult {
  raw: number | null;
  norm: number | null; // 0~100, 그룹 내 백분위
  included: boolean;
  note: string | null; // 미포함 사유 또는 경고
}

export interface VideoScore {
  videoId: string;
  channelId: string;
  format: VideoFormat;
  ageHours: number | null;
  metrics: Record<ViralMetric, MetricResult>;
  viralScore: number | null;
  viralStatus: "ok" | "hold";
  holdReason: string | null;
  /** 실제 계산에 사용된(재조정된) 가중치, 합 100 */
  weightsUsed: Partial<Record<ViralMetric, number>>;
  weightCoverage: number; // 0~1
  facelessScore: number | null;
  finalScore: number | null;
  finalWeightsUsed: { viral: number; faceless: number };
  warnings: string[];
  groupSize: number;
  growthPerHour: number | null;
  milestones: Record<MilestoneKey, number | null>;
}

// ───────────────────────── 기본 지표 ─────────────────────────

export function ageHours(publishedAt: number | null, observedAt: number): number | null {
  if (publishedAt == null || !Number.isFinite(publishedAt)) return null;
  const h = (observedAt - publishedAt) / HOUR_MS;
  return h > 0 ? h : null;
}

/** A. 시간당 조회수 = 관측 조회수 ÷ 게시 후 경과 시간 */
export function viewsPerHour(views: number | null, hours: number | null): number | null {
  if (views == null || hours == null || hours <= 0) return null;
  return views / hours;
}

/** B. 구독자 대비 조회수. 구독자 비공개(null) 또는 0이면 계산하지 않음 */
export function subscriberRatio(views: number | null, subscribers: number | null): number | null {
  if (views == null || subscribers == null || subscribers <= 0) return null;
  return views / subscribers;
}

/** D. 참여 지표. 조회수가 0이거나 분자가 비공개면 결측 */
export function rate(numerator: number | null, views: number | null): number | null {
  if (numerator == null || views == null || views <= 0) return null;
  return numerator / views;
}

export function median(values: number[]): number | null {
  if (values.length === 0) return null;
  const s = [...values].sort((a, b) => a - b);
  const m = Math.floor(s.length / 2);
  return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2;
}

export function mean(values: number[]): number | null {
  if (values.length === 0) return null;
  return values.reduce((a, b) => a + b, 0) / values.length;
}

/** 게시 기간 필터: [기준시각 − days, 기준시각] 정확한 시각 기준 */
export function inWindow(publishedAt: number | null, now: number, days: number): boolean {
  if (publishedAt == null) return false;
  return publishedAt >= now - days * DAY_MS && publishedAt <= now;
}

/**
 * C. 채널 내 상대 성과
 * 같은 채널·같은 형식, 대상 관측 시각 기준 최근 peerWindowDays 안에 게시된 다른 영상들의 스냅샷 중
 * 경과 시간이 비슷한(1/1.5~1.5배) 관측치의 시간당 조회수 중앙값과 비교한다.
 * 비교 영상이 MIN_PEERS 미만이면 null (계산하지 않음).
 */
export function relativePerformance(
  target: ScoreVideo,
  channelVideos: ScoreVideo[],
  snapshotsByVideo: Map<string, ScoreSnapshot[]>,
  peerWindowDays: number,
): { value: number | null; peers: number; note: string | null } {
  const tAge = ageHours(target.publishedAt, target.observedAt);
  const tVph = viewsPerHour(target.views, tAge);
  if (tAge == null || tVph == null) return { value: null, peers: 0, note: "대상 영상의 경과 시간 또는 조회수 결측" };

  const peerVph: number[] = [];
  for (const p of channelVideos) {
    if (p.id === target.id || p.channelId !== target.channelId || p.format !== target.format) continue;
    if (p.publishedAt == null) continue;
    if (p.publishedAt < target.observedAt - peerWindowDays * DAY_MS) continue;
    const snaps = snapshotsByVideo.get(p.id) ?? [];
    let best: { diff: number; vph: number } | null = null;
    for (const s of snaps) {
      const a = ageHours(p.publishedAt, s.at);
      const v = viewsPerHour(s.views, a);
      if (a == null || v == null) continue;
      const ratio = a / tAge;
      if (ratio < 1 / PEER_AGE_TOLERANCE || ratio > PEER_AGE_TOLERANCE) continue;
      const diff = Math.abs(Math.log(ratio));
      if (!best || diff < best.diff) best = { diff, vph: v };
    }
    if (best) peerVph.push(best.vph);
  }
  if (peerVph.length < MIN_PEERS) {
    return {
      value: null,
      peers: peerVph.length,
      note: `비슷한 경과 시간의 비교 영상 ${peerVph.length}개 (최소 ${MIN_PEERS}개 필요) — 관측 시점 부족`,
    };
  }
  const med = median(peerVph)!;
  if (med <= 0) return { value: null, peers: peerVph.length, note: "비교 영상 중앙값이 0" };
  return { value: tVph / med, peers: peerVph.length, note: null };
}

/** E. 조회수 증가 속도: 같은 영상의 서로 다른 두 시점 스냅샷이 있을 때만 계산 */
export function growthPerHour(snaps: ScoreSnapshot[]): number | null {
  const valid = snaps.filter((s) => s.views != null).sort((a, b) => a.at - b.at);
  if (valid.length < 2) return null;
  const a = valid[valid.length - 2];
  const b = valid[valid.length - 1];
  const h = (b.at - a.at) / HOUR_MS;
  if (h <= 0) return null;
  return (b.views! - a.views!) / h;
}

/** 특정 경과 시점(24h/72h/7d/14d)의 조회수: 허용 오차 안의 실제 스냅샷만 사용, 없으면 null (역산 금지) */
export function viewsAtMilestone(
  snaps: ScoreSnapshot[],
  publishedAt: number | null,
  hours: number,
  tolerance = MILESTONE_TOLERANCE,
): number | null {
  if (publishedAt == null) return null;
  let best: { diff: number; views: number } | null = null;
  for (const s of snaps) {
    if (s.views == null) continue;
    const a = (s.at - publishedAt) / HOUR_MS;
    const diff = Math.abs(a - hours);
    if (diff > hours * tolerance) continue;
    if (!best || diff < best.diff) best = { diff, views: s.views };
  }
  return best ? best.views : null;
}

// ───────────────────────── 정규화 ─────────────────────────

/**
 * 백분위 순위 정규화 (0~100). 결측(null)은 순위 계산에서 제외하고 null로 남긴다.
 * 동점은 평균 순위. 값이 1개뿐이면 50.
 */
export function percentileRanks(values: (number | null)[]): (number | null)[] {
  const present = values.filter((v): v is number => v != null && Number.isFinite(v));
  const n = present.length;
  return values.map((v) => {
    if (v == null || !Number.isFinite(v)) return null;
    if (n === 1) return 50;
    let below = 0;
    let equal = 0;
    for (const p of present) {
      if (p < v) below++;
      else if (p === v) equal++;
    }
    return ((below + (equal - 1) / 2) / (n - 1)) * 100;
  });
}

// ───────────────────────── 점수 결합 ─────────────────────────

export function facelessScore(cls: FacelessClass): number | null {
  switch (cls) {
    case "A":
      return 100; // 내레이션+자료 화면: 초보도 재현 쉬움
    case "C":
      return 95; // 차트·스크린캐스트
    case "B":
      return 85; // 애니메이션: 제작 비용이 상대적으로 큼
    case "E":
      return 50; // 혼합형: 얼굴 노출이 적은 경우에 한해 참고
    case "D":
      return 0; // 진행자·출연자 노출
    case "U":
      return null; // 확인 불가 → 결측
  }
}

/** 가중 평균 (결측 지표 제외 후 가중치 재조정) */
export function combine(
  norms: Partial<Record<ViralMetric, number | null>>,
  weights: Weights,
): { score: number | null; used: Partial<Record<ViralMetric, number>>; coverage: number } {
  let totalConfigured = 0;
  let totalUsed = 0;
  let acc = 0;
  for (const m of VIRAL_METRICS) {
    const w = Math.max(0, weights[m]);
    totalConfigured += w;
    const v = norms[m];
    if (v == null || w === 0) continue;
    totalUsed += w;
    acc += w * v;
  }
  const used: Partial<Record<ViralMetric, number>> = {};
  if (totalUsed > 0) {
    for (const m of VIRAL_METRICS) {
      const v = norms[m];
      if (v != null && weights[m] > 0) used[m] = Math.round((weights[m] / totalUsed) * 1000) / 10;
    }
  }
  return {
    score: totalUsed > 0 ? acc / totalUsed : null,
    used,
    coverage: totalConfigured > 0 ? totalUsed / totalConfigured : 0,
  };
}

export interface ScoreOptions {
  weights: Weights;
  peerWindowDays: number;
}

/**
 * 영상 집합의 점수를 계산한다.
 * @param ranked 순위 대상 영상 (보통 최근 14일 게시)
 * @param allVideos 상대 성과 비교용 전체 영상 (최근 90일 포함)
 */
export function scoreVideos(
  ranked: ScoreVideo[],
  allVideos: ScoreVideo[],
  snapshots: ScoreSnapshot[],
  opts: ScoreOptions,
): VideoScore[] {
  const snapsBy = new Map<string, ScoreSnapshot[]>();
  for (const s of snapshots) {
    const arr = snapsBy.get(s.videoId) ?? [];
    arr.push(s);
    snapsBy.set(s.videoId, arr);
  }
  const byChannel = new Map<string, ScoreVideo[]>();
  for (const v of allVideos) {
    const arr = byChannel.get(v.channelId) ?? [];
    arr.push(v);
    byChannel.set(v.channelId, arr);
  }

  // 1단계: 원시 지표
  const rows = ranked.map((v) => {
    const age = ageHours(v.publishedAt, v.observedAt);
    const rel = relativePerformance(v, byChannel.get(v.channelId) ?? [], snapsBy, opts.peerWindowDays);
    const raw: Record<ViralMetric, number | null> = {
      velocity: viewsPerHour(v.views, age),
      relative: rel.value,
      subRatio: subscriberRatio(v.views, v.subscribers),
      likeRate: rate(v.likes, v.views),
      commentRate: rate(v.comments, v.views),
    };
    const notes: Record<ViralMetric, string | null> = {
      velocity: age == null ? "게시 시각 확인 불가" : v.views == null ? "조회수 수집 불가" : null,
      relative: rel.note,
      subRatio: v.subscribers == null ? "구독자 수 비공개 또는 수집 불가" : v.subscribers <= 0 ? "구독자 0" : null,
      likeRate: v.likes == null ? "좋아요 수 비공개" : null,
      commentRate: v.comments == null ? "댓글 비활성 또는 비공개" : null,
    };
    return { v, age, raw, notes };
  });

  // 2단계: 형식(롱폼/쇼츠/기타)별 백분위 정규화
  const out: VideoScore[] = [];
  const formats: VideoFormat[] = ["long", "shorts", "other"];
  for (const f of formats) {
    const group = rows.filter((r) => r.v.format === f);
    if (group.length === 0) continue;
    const normsByMetric = {} as Record<ViralMetric, (number | null)[]>;
    for (const m of VIRAL_METRICS) normsByMetric[m] = percentileRanks(group.map((r) => r.raw[m]));

    group.forEach((r, i) => {
      const metrics = {} as Record<ViralMetric, MetricResult>;
      const norms: Partial<Record<ViralMetric, number | null>> = {};
      for (const m of VIRAL_METRICS) {
        const norm = normsByMetric[m][i];
        norms[m] = norm;
        metrics[m] = { raw: r.raw[m], norm, included: norm != null && opts.weights[m] > 0, note: r.notes[m] };
      }
      const c = combine(norms, opts.weights);
      const warnings: string[] = [];
      if (r.age != null && r.age < YOUNG_VIDEO_HOURS)
        warnings.push(`게시 후 ${r.age.toFixed(1)}시간 — 시간당 조회수 변동성이 큼`);
      if (group.length < 5) warnings.push(`같은 형식 영상이 ${group.length}개뿐 — 백분위 정규화 신뢰도 낮음`);

      let holdReason: string | null = null;
      if (r.v.publishedAt == null) holdReason = "게시 시각 확인 불가";
      else if (group.length < MIN_GROUP_SIZE) holdReason = `같은 형식 영상 ${group.length}개 (최소 ${MIN_GROUP_SIZE}개 필요)`;
      else if (c.coverage < MIN_WEIGHT_COVERAGE)
        holdReason = `관측 가능한 지표 가중치 ${(c.coverage * 100).toFixed(0)}% (최소 ${MIN_WEIGHT_COVERAGE * 100}% 필요)`;

      const viralScore = holdReason ? null : c.score;
      const fScore = facelessScore(r.v.facelessCls);
      const wv = VIRAL_METRICS.reduce((a, m) => a + Math.max(0, opts.weights[m]), 0);
      const wf = Math.max(0, opts.weights.faceless);
      let finalScore: number | null = null;
      let finalW = { viral: 0, faceless: 0 };
      if (viralScore != null) {
        if (fScore != null && wv + wf > 0) {
          finalScore = (wv * viralScore + wf * fScore) / (wv + wf);
          finalW = { viral: (wv / (wv + wf)) * 100, faceless: (wf / (wv + wf)) * 100 };
        } else {
          finalScore = viralScore;
          finalW = { viral: 100, faceless: 0 };
          if (fScore == null) warnings.push("페이스리스 확인 불가(U) — 최종 우선순위는 바이럴 점수만 반영");
        }
      }
      if (r.v.facelessConfidence !== "confirmed" && fScore != null)
        warnings.push("페이스리스 판정이 '추정' 수준 — 영상 직접 확인 필요");

      const snaps = snapsBy.get(r.v.id) ?? [];
      const milestones = {} as Record<MilestoneKey, number | null>;
      for (const ms of MILESTONES) milestones[ms.key] = viewsAtMilestone(snaps, r.v.publishedAt, ms.hours);

      out.push({
        videoId: r.v.id,
        channelId: r.v.channelId,
        format: f,
        ageHours: r.age,
        metrics,
        viralScore,
        viralStatus: holdReason ? "hold" : "ok",
        holdReason,
        weightsUsed: c.used,
        weightCoverage: c.coverage,
        facelessScore: fScore,
        finalScore,
        finalWeightsUsed: finalW,
        warnings,
        groupSize: group.length,
        growthPerHour: growthPerHour(snaps),
        milestones,
      });
    });
  }
  return out;
}

/** 순위 정렬: 판정 보류는 맨 뒤 */
export function rankScores(scores: VideoScore[], key: "viralScore" | "finalScore" = "finalScore"): VideoScore[] {
  return [...scores].sort((a, b) => {
    const av = a[key];
    const bv = b[key];
    if (av == null && bv == null) return 0;
    if (av == null) return 1;
    if (bv == null) return -1;
    return bv - av;
  });
}

export interface ChannelScore {
  channelId: string;
  recentCount: number;
  scoredCount: number;
  medianViral: number | null;
  medianFinal: number | null;
  topVideoId: string | null;
  status: "ok" | "hold";
  holdReason: string | null;
}

/** 채널 순위: 최근 기간 영상의 바이럴 점수 중앙값. 점수가 계산된 영상이 2개 미만이면 판정 보류 */
export function scoreChannels(scores: VideoScore[], channelIds: string[]): ChannelScore[] {
  return channelIds.map((cid) => {
    const mine = scores.filter((s) => s.channelId === cid);
    const ok = mine.filter((s) => s.viralScore != null);
    const top = rankScores(ok, "finalScore")[0];
    const hold = ok.length < 2;
    return {
      channelId: cid,
      recentCount: mine.length,
      scoredCount: ok.length,
      medianViral: hold ? null : median(ok.map((s) => s.viralScore!)),
      medianFinal: hold ? null : median(ok.map((s) => s.finalScore!).filter((x) => x != null)),
      topVideoId: top?.videoId ?? null,
      status: hold ? "hold" : "ok",
      holdReason: hold ? `점수 계산된 최근 영상 ${ok.length}개 (최소 2개 필요)` : null,
    };
  });
}
