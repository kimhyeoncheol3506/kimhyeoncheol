import { describe, expect, it } from "vitest";
import { DEFAULT_WEIGHTS } from "../types";
import {
  HOUR_MS,
  DAY_MS,
  ageHours,
  combine,
  growthPerHour,
  inWindow,
  percentileRanks,
  rankScores,
  rate,
  relativePerformance,
  scoreChannels,
  scoreVideos,
  subscriberRatio,
  viewsAtMilestone,
  viewsPerHour,
  type ScoreSnapshot,
  type ScoreVideo,
} from "./viral";

const NOW = Date.UTC(2026, 9, 11, 0, 0, 0);

function vid(p: Partial<ScoreVideo> & { id: string }): ScoreVideo {
  return {
    channelId: "c1",
    format: "long",
    publishedAt: NOW - 48 * HOUR_MS,
    observedAt: NOW,
    views: 10_000,
    likes: 300,
    comments: 30,
    subscribers: 100_000,
    facelessCls: "A",
    facelessConfidence: "estimated",
    ...p,
  };
}

describe("기본 지표", () => {
  it("시간당 조회수", () => {
    expect(viewsPerHour(4800, 48)).toBe(100);
    expect(viewsPerHour(null, 48)).toBeNull();
    expect(viewsPerHour(100, null)).toBeNull();
    expect(viewsPerHour(100, 0)).toBeNull();
  });

  it("경과 시간: 게시 시각이 없거나 미래면 null", () => {
    expect(ageHours(NOW - 10 * HOUR_MS, NOW)).toBeCloseTo(10);
    expect(ageHours(null, NOW)).toBeNull();
    expect(ageHours(NOW + HOUR_MS, NOW)).toBeNull();
  });

  it("구독자 비공개(null)·0이면 구독자 대비 조회수를 계산하지 않음", () => {
    expect(subscriberRatio(5000, 10000)).toBe(0.5);
    expect(subscriberRatio(5000, null)).toBeNull();
    expect(subscriberRatio(5000, 0)).toBeNull();
  });

  it("좋아요·댓글 비공개 또는 조회수 0이면 결측", () => {
    expect(rate(50, 1000)).toBe(0.05);
    expect(rate(null, 1000)).toBeNull();
    expect(rate(10, 0)).toBeNull();
    // 좋아요 0개는 결측이 아니라 실제 0
    expect(rate(0, 1000)).toBe(0);
  });
});

describe("최근 14일 필터 (정확한 시각 기준)", () => {
  it("경계 포함, 경계 1ms 밖은 제외", () => {
    expect(inWindow(NOW - 14 * DAY_MS, NOW, 14)).toBe(true);
    expect(inWindow(NOW - 14 * DAY_MS - 1, NOW, 14)).toBe(false);
    expect(inWindow(NOW, NOW, 14)).toBe(true);
    expect(inWindow(NOW + 1, NOW, 14)).toBe(false);
    expect(inWindow(null, NOW, 14)).toBe(false);
  });
});

describe("백분위 정규화", () => {
  it("결측은 null 유지, 순위에서 제외", () => {
    expect(percentileRanks([10, null, 30, 20])).toEqual([0, null, 100, 50]);
  });
  it("동점은 평균 순위, 값 하나면 50", () => {
    expect(percentileRanks([5, 5])).toEqual([50, 50]);
    expect(percentileRanks([7])).toEqual([50]);
  });
});

describe("가중치 재조정 (결측 ≠ 0점)", () => {
  it("결측 지표를 빼고 남은 가중치 합으로 나눈다", () => {
    const r = combine({ velocity: 100, relative: null, subRatio: 50, likeRate: null, commentRate: null }, DEFAULT_WEIGHTS);
    // (30*100 + 20*50) / 50 = 80 — 결측을 0점으로 처리했다면 (3000+1000)/90 = 44.4
    expect(r.score).toBeCloseTo(80);
    expect(r.used).toEqual({ velocity: 60, subRatio: 40 });
    expect(r.coverage).toBeCloseTo(50 / 90);
  });
  it("모든 지표가 결측이면 점수 없음", () => {
    const r = combine({}, DEFAULT_WEIGHTS);
    expect(r.score).toBeNull();
    expect(r.coverage).toBe(0);
  });
});

describe("채널 내 상대 성과", () => {
  const target = vid({ id: "t", publishedAt: NOW - 48 * HOUR_MS, views: 9600 }); // 200/h
  const peers = [1, 2, 3].map((i) => vid({ id: `p${i}`, publishedAt: NOW - (10 + i) * DAY_MS }));

  it("비슷한 경과 시간의 스냅샷이 3개 이상이면 비율 계산", () => {
    const snaps = new Map<string, ScoreSnapshot[]>();
    peers.forEach((p, i) =>
      snaps.set(p.id, [{ videoId: p.id, at: p.publishedAt! + 50 * HOUR_MS, views: (i + 1) * 50 * 50 }]),
    );
    // 비교 영상 시간당 50, 100, 150 → 중앙값 100 → 대상 200/100 = 2
    const r = relativePerformance(target, [target, ...peers], snaps, 90);
    expect(r.peers).toBe(3);
    expect(r.value).toBeCloseTo(2);
  });

  it("경과 시간이 다른 스냅샷만 있으면 계산하지 않음", () => {
    const snaps = new Map<string, ScoreSnapshot[]>();
    peers.forEach((p) => snaps.set(p.id, [{ videoId: p.id, at: NOW, views: 99999 }])); // 10일 이상 경과
    const r = relativePerformance(target, [target, ...peers], snaps, 90);
    expect(r.value).toBeNull();
    expect(r.note).toContain("관측 시점 부족");
  });

  it("다른 형식(쇼츠)은 비교 대상에서 제외", () => {
    const shorts = peers.map((p) => ({ ...p, format: "shorts" as const }));
    const snaps = new Map<string, ScoreSnapshot[]>();
    shorts.forEach((p) => snaps.set(p.id, [{ videoId: p.id, at: p.publishedAt! + 48 * HOUR_MS, views: 1000 }]));
    expect(relativePerformance(target, [target, ...shorts], snaps, 90).value).toBeNull();
  });
});

describe("스냅샷 기반 지표 (역산 금지)", () => {
  const pub = NOW - 10 * DAY_MS;
  it("기준 시점 ±20% 안의 스냅샷만 인정", () => {
    const snaps: ScoreSnapshot[] = [
      { videoId: "v", at: pub + 26 * HOUR_MS, views: 1000 },
      { videoId: "v", at: pub + 240 * HOUR_MS, views: 9000 },
    ];
    expect(viewsAtMilestone(snaps, pub, 24)).toBe(1000);
    expect(viewsAtMilestone(snaps, pub, 72)).toBeNull(); // 72h 스냅샷 없음 → 만들지 않음
    expect(viewsAtMilestone(snaps, pub, 336)).toBeNull();
  });
  it("증가 속도는 스냅샷이 2개 이상일 때만", () => {
    expect(growthPerHour([{ videoId: "v", at: NOW, views: 100 }])).toBeNull();
    expect(
      growthPerHour([
        { videoId: "v", at: NOW - 10 * HOUR_MS, views: 100 },
        { videoId: "v", at: NOW, views: 600 },
      ]),
    ).toBe(50);
  });
});

describe("scoreVideos 통합", () => {
  const vids = [
    vid({ id: "a", views: 50_000 }),
    vid({ id: "b", views: 20_000, likes: null }), // 좋아요 비공개
    vid({ id: "c", views: 5_000 }),
    vid({ id: "d", views: 8_000, subscribers: null }), // 구독자 비공개
    vid({ id: "s1", format: "shorts", views: 100_000 }),
    vid({ id: "s2", format: "shorts", views: 1_000 }),
  ];
  const scores = scoreVideos(vids, vids, [], { weights: DEFAULT_WEIGHTS, peerWindowDays: 90 });
  const get = (id: string) => scores.find((s) => s.videoId === id)!;

  it("롱폼과 쇼츠를 분리해 정규화한다", () => {
    expect(get("a").groupSize).toBe(4);
    expect(get("s1").groupSize).toBe(2);
  });

  it("쇼츠 그룹이 3개 미만이면 판정 보류", () => {
    expect(get("s1").viralStatus).toBe("hold");
    expect(get("s1").viralScore).toBeNull();
  });

  it("결측 지표는 0점이 아니라 계산에서 제외되고, 사용된 가중치가 기록된다", () => {
    const b = get("b");
    expect(b.metrics.likeRate.raw).toBeNull();
    expect(b.metrics.likeRate.included).toBe(false);
    expect(b.weightsUsed.likeRate).toBeUndefined();
    const sum = Object.values(b.weightsUsed).reduce((x, y) => x + (y ?? 0), 0);
    expect(sum).toBeCloseTo(100, 0);
    const d = get("d");
    expect(d.metrics.subRatio.raw).toBeNull();
    expect(d.metrics.subRatio.note).toContain("비공개");
  });

  it("조회 속도가 가장 높은 롱폼이 1위", () => {
    const longs = rankScores(scores.filter((s) => s.format === "long"), "viralScore");
    expect(longs[0].videoId).toBe("a");
  });

  it("바이럴 점수와 페이스리스 점수는 분리되고 최종 점수만 결합된다", () => {
    const a = get("a");
    expect(a.facelessScore).toBe(100);
    expect(a.viralScore).not.toBeNull();
    // 기본 가중치: 바이럴 90 : 페이스리스 10
    expect(a.finalScore!).toBeCloseTo((90 * a.viralScore! + 10 * 100) / 100);
    expect(a.finalWeightsUsed.faceless).toBeCloseTo(10);
  });

  it("페이스리스 확인 불가(U)는 최종 점수에서 0점 처리하지 않는다", () => {
    const u = [vid({ id: "x", facelessCls: "U" }), vid({ id: "y" }), vid({ id: "z" })];
    const s = scoreVideos(u, u, [], { weights: DEFAULT_WEIGHTS, peerWindowDays: 90 }).find((r) => r.videoId === "x")!;
    expect(s.facelessScore).toBeNull();
    expect(s.finalScore).toBe(s.viralScore);
  });

  it("게시 24시간 미만 영상에 변동성 경고", () => {
    const y = [vid({ id: "y1", publishedAt: NOW - 3 * HOUR_MS }), vid({ id: "y2" }), vid({ id: "y3" })];
    const s = scoreVideos(y, y, [], { weights: DEFAULT_WEIGHTS, peerWindowDays: 90 });
    expect(s.find((r) => r.videoId === "y1")!.warnings.join()).toContain("변동성");
  });

  it("가중치를 바꾸면 결과가 바뀐다", () => {
    const w = { ...DEFAULT_WEIGHTS, velocity: 0, subRatio: 0, likeRate: 100 };
    const s = scoreVideos(vids, vids, [], { weights: w, peerWindowDays: 90 });
    expect(s.find((r) => r.videoId === "a")!.weightsUsed).toEqual({ likeRate: 95.2, commentRate: 4.8 });
  });

  it("채널 점수: 점수 있는 영상 2개 미만이면 판정 보류", () => {
    const ch = scoreChannels(scores, ["c1", "none"]);
    expect(ch[0].status).toBe("ok");
    expect(ch[1].status).toBe("hold");
  });
});
