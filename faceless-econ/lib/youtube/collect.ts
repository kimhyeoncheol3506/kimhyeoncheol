// 실제 데이터 수집 파이프라인
// 1) channels.list (1단위/50채널): 채널 정보·업로드 플레이리스트
// 2) playlistItems.list (1단위/50영상): 업로드 플레이리스트에서 최근 peerWindowDays(기본 90일) 영상 ID 수집
//    → search.list(100단위, 관련도·날짜 정렬 일부 결과)보다 저렴하고 누락이 적다.
//    단, 업로드 플레이리스트에도 멤버십 전용·예약 공개 영상 등은 빠질 수 있으므로 '전수'라고 단정하지 않는다.
// 3) videos.list (1단위/50영상): 조회수·좋아요·댓글·길이·상태
// 4) 같은 수집 시각으로 스냅샷 저장 (기존 스냅샷은 유지, 과거 조회수는 역산하지 않음)

import { candidateById } from "../candidates";
import { channelShare, judgeVideo } from "../analysis/faceless";
import { extractKeywords } from "../analysis/title";
import { detectFormat } from "../format";
import { addSnapshot, loadStore, updateStore, upsertVideo } from "../store";
import { parseIsoDuration } from "../time";
import type { ChannelRecord, CollectionRun, FacelessJudgement, Snapshot, VideoRecord } from "../types";
import {
  YouTubeError,
  checkShortsUrl,
  ytGet,
  type ApiChannel,
  type ApiList,
  type ApiPlaylistItem,
  type ApiSearchItem,
  type ApiVideo,
} from "./client";

const DAY = 86_400_000;
const MAX_PLAYLIST_PAGES = 10; // 채널당 최대 500개 영상까지 거슬러 올라감
const MAX_SHORTS_CHECKS = 60;

const chunk = <T,>(a: T[], n: number) => Array.from({ length: Math.ceil(a.length / n) }, (_, i) => a.slice(i * n, i * n + n));
const toNum = (s: string | undefined) => (s == null ? null : Number.isFinite(Number(s)) ? Number(s) : null);

function bestThumb(t?: Record<string, { url: string }>): string | null {
  if (!t) return null;
  return (t.maxres ?? t.standard ?? t.high ?? t.medium ?? t.default)?.url ?? null;
}

export function priorFor(channelId: string): FacelessJudgement {
  const ov = loadStore().settings.facelessOverrides[channelId];
  if (ov) return { cls: ov.cls, confidence: ov.confirmed ? "confirmed" : "estimated", evidence: [`사용자 입력: ${ov.note || "메모 없음"}`] };
  const c = candidateById(channelId);
  if (c) return { cls: c.priorClass, confidence: c.priorClass === "U" ? "unverified" : "estimated", evidence: [c.priorReason] };
  return { cls: "U", confidence: "unverified", evidence: ["사전 정보 없음"] };
}

export interface CollectOptions {
  channelIds: string[];
  peerWindowDays: number;
  checkShorts?: boolean;
}

export async function collect(opts: CollectOptions): Promise<CollectionRun> {
  const now = new Date();
  const collectedAt = now.toISOString();
  const run: CollectionRun = {
    id: `run_${now.getTime()}`,
    startedAt: collectedAt,
    finishedAt: null,
    status: "running",
    quotaUsed: 0,
    channelsOk: 0,
    channelsFailed: 0,
    videosCollected: 0,
    messages: [],
  };
  const log = (level: "info" | "warn" | "error", text: string) => run.messages.push({ level, text });
  const quotaStart = loadStore().quota.used;

  const channels: ChannelRecord[] = [];
  const videos: VideoRecord[] = [];
  const snapshots: Snapshot[] = [];
  const unavailable: string[] = [];
  let fatal = false;

  try {
    // 1) 채널 정보
    const ids = [...new Set(opts.channelIds)];
    const found = new Map<string, ApiChannel>();
    for (const part of chunk(ids, 50)) {
      const r = await ytGet<ApiList<ApiChannel>>(
        "channels",
        { part: "snippet,statistics,contentDetails,topicDetails", id: part.join(","), maxResults: "50" },
        { cost: 1, useCache: false },
      );
      for (const c of r.items ?? []) found.set(c.id, c);
    }
    for (const id of ids) {
      const c = found.get(id);
      if (!c) {
        run.channelsFailed++;
        log("error", `채널 ID ${id}: 조회 실패 (삭제·비공개 또는 잘못된 ID)`);
        continue;
      }
      const hidden = !!c.statistics?.hiddenSubscriberCount;
      if (hidden) log("warn", `${c.snippet?.title}: 구독자 수 비공개 — 구독자 대비 조회수 계산 제외`);
      channels.push({
        id,
        title: c.snippet?.title ?? id,
        handle: c.snippet?.customUrl ?? null,
        url: `https://www.youtube.com/channel/${id}`,
        subscriberCount: hidden ? null : toNum(c.statistics?.subscriberCount),
        subscriberHidden: hidden,
        viewCount: toNum(c.statistics?.viewCount),
        videoCount: toNum(c.statistics?.videoCount),
        description: c.snippet?.description ?? null,
        topicCategories: (c.topicDetails?.topicCategories ?? []).map((u) => decodeURIComponent(u.split("/").pop() ?? u)),
        uploadsPlaylistId: c.contentDetails?.relatedPlaylists?.uploads ?? null,
        thumbnailUrl: bestThumb(c.snippet?.thumbnails),
        collectedAt,
        source: "real",
        faceless: priorFor(id),
      });
    }

    // 2) 업로드 플레이리스트 → 최근 영상 ID
    const cutoff = now.getTime() - opts.peerWindowDays * DAY;
    const store = loadStore();
    const videoIds = new Set<string>();
    for (const ch of channels) {
      if (!ch.uploadsPlaylistId) {
        log("warn", `${ch.title}: 업로드 플레이리스트 없음`);
        continue;
      }
      let token: string | undefined;
      let pages = 0;
      let count = 0;
      let reachedCutoff = false;
      do {
        const r = await ytGet<ApiList<ApiPlaylistItem>>(
          "playlistItems",
          { part: "contentDetails,snippet", playlistId: ch.uploadsPlaylistId, maxResults: "50", ...(token ? { pageToken: token } : {}) },
          { cost: 1, useCache: false },
        );
        for (const it of r.items ?? []) {
          const vid = it.contentDetails?.videoId;
          const pub = it.contentDetails?.videoPublishedAt ?? it.snippet?.publishedAt;
          if (!vid) continue;
          if (pub && Date.parse(pub) < cutoff) {
            reachedCutoff = true;
            continue;
          }
          videoIds.add(vid);
          count++;
        }
        token = r.nextPageToken;
        pages++;
      } while (token && !reachedCutoff && pages < MAX_PLAYLIST_PAGES);
      if (!reachedCutoff && token) log("warn", `${ch.title}: 최대 ${MAX_PLAYLIST_PAGES}페이지까지만 확인 — 일부 영상 누락 가능`);
      log("info", `${ch.title}: 최근 ${opts.peerWindowDays}일 업로드 ${count}개 확인 (업로드 플레이리스트 기준)`);
      run.channelsOk++;
      // 이전에 저장된 같은 채널 영상도 다시 조회해 삭제·비공개 전환을 감지
      for (const v of Object.values(store.videos))
        if (v.channelId === ch.id && v.source === "real" && v.publishedAt && Date.parse(v.publishedAt) >= cutoff) videoIds.add(v.id);
    }

    // 3) 영상 상세
    const chMap = new Map(channels.map((c) => [c.id, c]));
    const returned = new Set<string>();
    let shortsChecks = 0;
    for (const part of chunk([...videoIds], 50)) {
      const r = await ytGet<ApiList<ApiVideo>>(
        "videos",
        { part: "snippet,statistics,contentDetails,status,liveStreamingDetails", id: part.join(","), maxResults: "50" },
        { cost: 1, useCache: false },
      );
      for (const v of r.items ?? []) {
        returned.add(v.id);
        const ch = chMap.get(v.snippet?.channelId ?? "");
        if (!ch) continue;
        const title = v.snippet?.title ?? "(제목 없음)";
        const desc = v.snippet?.description ?? null;
        const live: VideoRecord["liveContent"] =
          v.snippet?.liveBroadcastContent && v.snippet.liveBroadcastContent !== "none"
            ? v.snippet.liveBroadcastContent
            : v.liveStreamingDetails?.actualStartTime
              ? "completed"
              : "none";
        const dur = parseIsoDuration(v.contentDetails?.duration);
        let shortsCheck: boolean | null = null;
        if (opts.checkShorts !== false && dur != null && dur > 60 && dur <= 180 && shortsChecks < MAX_SHORTS_CHECKS) {
          shortsChecks++;
          shortsCheck = await checkShortsUrl(v.id);
        }
        const fmt = detectFormat(dur, title, desc, live, shortsCheck);
        const views = toNum(v.statistics?.viewCount);
        const likes = toNum(v.statistics?.likeCount);
        const comments = toNum(v.statistics?.commentCount);
        if (!v.snippet?.publishedAt) log("warn", `${v.id}: 게시 시각 확인 불가 — 순위에서 제외`);
        const prev = store.videos[v.id];
        videos.push({
          id: v.id,
          url: fmt.format === "shorts" ? `https://www.youtube.com/shorts/${v.id}` : `https://www.youtube.com/watch?v=${v.id}`,
          channelId: ch.id,
          title,
          description: desc,
          publishedAt: v.snippet?.publishedAt ?? null,
          durationSec: dur,
          format: fmt.format,
          formatEvidence: fmt.evidence,
          thumbnailUrl: bestThumb(v.snippet?.thumbnails),
          tags: v.snippet?.tags ?? [],
          viewCount: views,
          likeCount: likes,
          commentCount: comments,
          channelSubscriberCount: ch.subscriberCount,
          collectedAt,
          firstSeenAt: prev?.firstSeenAt ?? collectedAt,
          status: "available",
          liveContent: live,
          keywords: extractKeywords(title),
          faceless: judgeVideo(title, desc, live, ch.faceless),
          source: "real",
        });
        snapshots.push({ videoId: v.id, collectedAt, viewCount: views, likeCount: likes, commentCount: comments });
      }
    }
    for (const id of videoIds) if (!returned.has(id)) unavailable.push(id);
    if (unavailable.length) log("warn", `영상 ${unavailable.length}개가 조회되지 않음 — 삭제 또는 비공개 전환으로 표시`);
    run.videosCollected = videos.length;

    // 채널 단위 페이스리스 비중 갱신
    for (const ch of channels) {
      const share = channelShare(videos.filter((v) => v.channelId === ch.id).map((v) => v.faceless));
      ch.faceless = {
        ...ch.faceless,
        evidence: [
          ...ch.faceless.evidence,
          `영상별 간접 판정: 페이스리스(A/B/C) ${share.facelessCount} · 혼합(E) ${share.mixedCount} · 인물(D) ${share.faceCount} · 불가(U) ${share.unknownCount}`,
        ],
      };
    }
  } catch (e) {
    fatal = true;
    const msg = e instanceof YouTubeError ? e.message : `알 수 없는 오류: ${(e as Error).message}`;
    log("error", msg);
    if (e instanceof YouTubeError && e.kind === "quota") log("warn", "할당량 초과 전까지 수집된 데이터는 저장했습니다.");
  }

  run.finishedAt = new Date().toISOString();
  run.status = fatal ? (videos.length > 0 ? "partial" : "failed") : run.channelsFailed > 0 ? "partial" : "success";

  updateStore((d) => {
    for (const c of channels) d.channels[c.id] = c;
    for (const v of videos) upsertVideo(d, v);
    for (const s of snapshots) addSnapshot(d, s);
    for (const id of unavailable) if (d.videos[id]) d.videos[id].status = "unavailable";
    run.quotaUsed = d.quota.used - quotaStart;
    d.runs.unshift(run);
    d.runs = d.runs.slice(0, 50);
  });
  return run;
}

/** 핸들(@name) 또는 채널 ID를 채널 ID로 변환 (1단위) */
export async function resolveChannel(input: string): Promise<{ id: string; title: string } | null> {
  const s = input.trim();
  const idMatch = s.match(/UC[\w-]{22}/);
  const params: Record<string, string> = { part: "snippet" };
  if (idMatch) params.id = idMatch[0];
  else {
    const h = s.match(/@[^/?\s]+/)?.[0] ?? (s.startsWith("@") ? s : `@${s}`);
    params.forHandle = decodeURIComponent(h);
  }
  const r = await ytGet<ApiList<ApiChannel>>("channels", params, { cost: 1 });
  const c = r.items?.[0];
  return c ? { id: c.id, title: c.snippet?.title ?? c.id } : null;
}

/** 교체 후보 채널 검색 (search.list, 100단위). 관련도 정렬의 일부 결과임을 표시해야 한다. */
export async function searchChannels(q: string): Promise<{ id: string; title: string; description: string }[]> {
  const r = await ytGet<ApiList<ApiSearchItem>>(
    "search",
    { part: "snippet", q, type: "channel", regionCode: "KR", relevanceLanguage: "ko", maxResults: "15" },
    { cost: 100 },
  );
  return (r.items ?? [])
    .filter((i) => i.id?.channelId)
    .map((i) => ({ id: i.id!.channelId!, title: i.snippet?.title ?? "", description: i.snippet?.description ?? "" }));
}
