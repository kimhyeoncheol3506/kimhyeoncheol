// 데모 데이터 생성기
// - API 키 없이 화면과 분석 기능을 확인하기 위한 가상 데이터다. 실제 채널명·수치를 사용하지 않는다.
//   (실존 채널 이름에 가짜 수치를 붙이면 실제 데이터로 오인될 수 있으므로 모든 이름에 [데모]를 붙인다.)
// - 매일 1회 수집했다고 가정한 스냅샷을 포함해 상대 성과·24h/72h/7d/14d 비교 기능을 시연한다.
// - 결측 처리 시연용으로 구독자 비공개 채널, 좋아요 비공개 영상, 댓글 비활성 영상을 일부 포함한다.

import { extractKeywords } from "./analysis/title";
import { judgeVideo } from "./analysis/faceless";
import type { ChannelRecord, FacelessClass, Snapshot, VideoRecord } from "./types";

function mulberry32(seed: number) {
  return () => {
    seed |= 0;
    seed = (seed + 0x6d2b79f5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const H = 3_600_000;
const D = 24 * H;

interface DemoChannelDef {
  id: string;
  title: string;
  cls: FacelessClass;
  subs: number | null;
  uploadEveryDays: number;
  shortsPerWeek: number;
  hitRate: number; // 바이럴 확률
  baseRatio: number; // 구독자 대비 평균 조회 비율
  themes: string[];
}

const TOPICS = [
  "기준금리", "주담대 금리", "전세", "아파트값", "환율", "미국 국채", "배당주", "ETF", "연금저축", "ISA",
  "반도체", "2차전지", "부동산 PF", "가계부채", "물가", "청약", "예금자보호", "신용점수", "코스피", "엔화",
];
const TEMPLATES = [
  "{t}이 오르면 내 지갑에 생기는 일 3가지",
  "{t}, 지금 모르면 손해 보는 이유",
  "왜 {t}만 오를까? 데이터로 보면 보이는 것",
  "{t} vs 예금, 10년 뒤 차이는?",
  "알고 보니 {t}의 진짜 원인은 따로 있었다",
  "{t} 쉽게 정리: 초보자를 위한 7분 설명",
  "한 기업의 몰락으로 보는 {t}의 미래",
  "{t} 폭락 경고, 정말일까?",
  "2027년 {t} 전망, 시나리오 3개",
  "{t}의 역사 — 50년 흐름 한 번에",
];
const SHORT_TEMPLATES = ["{t} 1분 요약", "{t} 이거 모르면 손해 #shorts", "{t}이 뭐길래? #shorts"];

const DEMO_CHANNELS: DemoChannelDef[] = [
  { id: "DEMO_CH_ANIM", title: "[데모] 애니메이션 경제채널", cls: "B", subs: 13_000, uploadEveryDays: 5, shortsPerWeek: 2, hitRate: 0.25, baseRatio: 0.9, themes: ["기업", "경기"] },
  { id: "DEMO_CH_NARR", title: "[데모] 재테크 내레이션채널", cls: "E", subs: 1_280_000, uploadEveryDays: 1, shortsPerWeek: 4, hitRate: 0.12, baseRatio: 0.05, themes: ["주식", "부동산"] },
  { id: "DEMO_CH_CORP", title: "[데모] 기업사 애니메이션채널", cls: "B", subs: 92_000, uploadEveryDays: 4, shortsPerWeek: 1, hitRate: 0.2, baseRatio: 0.4, themes: ["기업"] },
  { id: "DEMO_CH_CHART", title: "[데모] 차트 해설채널", cls: "C", subs: 210_000, uploadEveryDays: 2, shortsPerWeek: 3, hitRate: 0.1, baseRatio: 0.12, themes: ["주식"] },
  { id: "DEMO_CH_STORY", title: "[데모] 경제 스토리채널", cls: "A", subs: 53_000, uploadEveryDays: 3, shortsPerWeek: 2, hitRate: 0.15, baseRatio: 0.3, themes: ["경제"] },
  { id: "DEMO_CH_HIDDEN", title: "[데모] 구독자 비공개 채널", cls: "A", subs: null, uploadEveryDays: 4, shortsPerWeek: 0, hitRate: 0.1, baseRatio: 0.2, themes: ["경제"] },
  { id: "DEMO_CH_MIX", title: "[데모] 혼합형 시황채널", cls: "E", subs: 400_000, uploadEveryDays: 2, shortsPerWeek: 2, hitRate: 0.08, baseRatio: 0.06, themes: ["시황"] },
  { id: "DEMO_CH_COMIC", title: "[데모] 만화 경제채널", cls: "B", subs: 1_440_000, uploadEveryDays: 7, shortsPerWeek: 1, hitRate: 0.2, baseRatio: 0.15, themes: ["경제"] },
  { id: "DEMO_CH_SMALL", title: "[데모] 신생 페이스리스채널", cls: "A", subs: 2_100, uploadEveryDays: 6, shortsPerWeek: 3, hitRate: 0.15, baseRatio: 1.2, themes: ["재테크"] },
  { id: "DEMO_CH_TALK", title: "[데모] 인터뷰 채널 (제외 예시)", cls: "D", subs: 2_000_000, uploadEveryDays: 1, shortsPerWeek: 0, hitRate: 0.1, baseRatio: 0.04, themes: ["인터뷰"] },
];

export const DEMO_TOP3 = ["DEMO_CH_ANIM", "DEMO_CH_NARR", "DEMO_CH_CORP"];

export interface DemoData {
  generatedAt: string;
  channels: ChannelRecord[];
  videos: VideoRecord[];
  snapshots: Snapshot[];
}

let memo: { key: number; data: DemoData } | null = null;

/** 기준 시각(정시 단위)마다 동일한 결과를 낸다 */
export function generateDemo(nowMs = Date.now()): DemoData {
  const now = Math.floor(nowMs / H) * H;
  if (memo && memo.key === now) return memo.data;
  const rnd = mulberry32(20261011);
  const lognormal = (mu: number, sigma: number) => {
    const u = Math.max(1e-9, rnd());
    const v = rnd();
    return Math.exp(mu + sigma * Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v));
  };
  const nowIso = new Date(now).toISOString();
  const channels: ChannelRecord[] = [];
  const videos: VideoRecord[] = [];
  const snapshots: Snapshot[] = [];
  let seq = 0;

  for (const c of DEMO_CHANNELS) {
    const subs = c.subs;
    const effSubs = subs ?? 150_000;
    channels.push({
      id: c.id,
      title: c.title,
      handle: null,
      url: "#demo",
      subscriberCount: subs,
      subscriberHidden: subs == null,
      viewCount: Math.round(effSubs * 180),
      videoCount: Math.round(120 + rnd() * 900),
      description: "데모용 가상 채널입니다. 실제 채널이 아닙니다.",
      topicCategories: ["Society", "Knowledge"],
      uploadsPlaylistId: null,
      thumbnailUrl: null,
      collectedAt: nowIso,
      source: "demo",
      faceless: { cls: c.cls, confidence: "estimated", evidence: ["데모 데이터 — 가상 판정"] },
    });

    const posts: { at: number; shorts: boolean }[] = [];
    for (let t = now - 2 * H - rnd() * D; t > now - 95 * D; t -= c.uploadEveryDays * D * (0.6 + rnd() * 0.8)) posts.push({ at: t, shorts: false });
    if (c.shortsPerWeek > 0)
      for (let t = now - rnd() * D; t > now - 95 * D; t -= (7 / c.shortsPerWeek) * D * (0.5 + rnd())) posts.push({ at: t, shorts: true });

    for (const p of posts) {
      seq++;
      const topic = TOPICS[Math.floor(rnd() * TOPICS.length)];
      const tpl = p.shorts ? SHORT_TEMPLATES[Math.floor(rnd() * SHORT_TEMPLATES.length)] : TEMPLATES[Math.floor(rnd() * TEMPLATES.length)];
      const title = `[데모] ${tpl.replace("{t}", topic)}`;
      const hit = rnd() < c.hitRate;
      const finalViews = effSubs * c.baseRatio * (p.shorts ? 1.6 : 1) * lognormal(0, 0.6) * (hit ? 4 + rnd() * 8 : 1);
      const tau = (p.shorts ? 30 : 60) * H * (0.6 + rnd() * 0.8);
      const viewsAt = (t: number) => Math.max(0, Math.round(finalViews * (1 - Math.exp(-(t - p.at) / tau))));
      const likeRate = 0.015 + rnd() * 0.03;
      const commentRate = 0.001 + rnd() * 0.005;
      const likesHidden = rnd() < 0.05;
      const commentsOff = rnd() < 0.05;
      const dur = p.shorts ? Math.round(20 + rnd() * 40) : Math.round(360 + rnd() * 900);
      const desc = c.cls === "D" ? "오늘은 전문가를 모시고 인터뷰를 진행했습니다. (데모)" : "데모용 가상 영상 설명입니다. 자료 출처: 데모";
      const id = `DEMO_V${String(seq).padStart(4, "0")}`;
      const v: VideoRecord = {
        id,
        url: "#demo",
        channelId: c.id,
        title,
        description: desc,
        publishedAt: new Date(p.at).toISOString(),
        durationSec: dur,
        format: p.shorts ? "shorts" : "long",
        formatEvidence: p.shorts ? "60초 이하 (데모)" : "180초 초과 (데모)",
        thumbnailUrl: null,
        tags: [],
        viewCount: viewsAt(now),
        likeCount: likesHidden ? null : Math.round(viewsAt(now) * likeRate),
        commentCount: commentsOff ? null : Math.round(viewsAt(now) * commentRate),
        channelSubscriberCount: subs,
        collectedAt: nowIso,
        firstSeenAt: nowIso,
        status: "available",
        liveContent: "none",
        keywords: extractKeywords(title.replace("[데모]", "")),
        faceless: { cls: c.cls, confidence: "estimated", evidence: [] },
        source: "demo",
      };
      v.faceless = judgeVideo(title, desc, "none", { cls: c.cls, confidence: "estimated", evidence: ["데모 채널 판정"] });
      videos.push(v);
      // 매일 09:00 KST(00:00 UTC) 수집을 가정한 스냅샷 (최근 30일만) + 현재 시각
      const dayStart = Math.floor(now / D) * D;
      for (let s = dayStart; s > now - 30 * D; s -= D) {
        if (s <= p.at) continue;
        const vs = viewsAt(s);
        snapshots.push({
          videoId: id,
          collectedAt: new Date(s).toISOString(),
          viewCount: vs,
          likeCount: likesHidden ? null : Math.round(vs * likeRate),
          commentCount: commentsOff ? null : Math.round(vs * commentRate),
        });
      }
      if (now !== dayStart)
        snapshots.push({ videoId: id, collectedAt: nowIso, viewCount: v.viewCount, likeCount: v.likeCount, commentCount: v.commentCount });
    }
  }
  const data = { generatedAt: nowIso, channels, videos, snapshots };
  memo = { key: now, data };
  return data;
}
