// YouTube Data API v3 클라이언트 (서버 전용)
// - API 키는 환경변수 YOUTUBE_API_KEY에서만 읽고, 오류 메시지·로그·캐시 키에 포함하지 않는다.
// - 응답은 디스크 캐시(기본 6시간)로 재사용해 할당량을 아낀다.
// - 요청 간 최소 간격과 5xx 재시도(지수 백오프)를 적용한다.
// - 일일 할당량(태평양 시간 자정 초기화)을 추정 집계해 상한의 90%에서 중단한다.

import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { dataDir, loadStore, updateStore } from "../store";

const API = "https://www.googleapis.com/youtube/v3";
const MIN_INTERVAL_MS = 120;
const CACHE_TTL_MS = 6 * 3_600_000;

export type YtErrorKind = "no_key" | "quota" | "key_invalid" | "forbidden" | "not_found" | "network" | "http";

export class YouTubeError extends Error {
  constructor(
    public kind: YtErrorKind,
    message: string,
  ) {
    super(message);
  }
}

export function hasApiKey(): boolean {
  return !!process.env.YOUTUBE_API_KEY?.trim();
}

function apiKey(): string {
  const k = process.env.YOUTUBE_API_KEY?.trim();
  if (!k) throw new YouTubeError("no_key", "YOUTUBE_API_KEY가 설정되지 않았습니다. .env.local 파일을 확인하세요.");
  return k;
}

export function dailyQuota(): number {
  const n = Number(process.env.YOUTUBE_DAILY_QUOTA);
  return Number.isFinite(n) && n > 0 ? n : 10_000;
}

/** YouTube 할당량은 태평양 시간 자정에 초기화된다 */
export function quotaDay(now = new Date()): string {
  return new Intl.DateTimeFormat("en-CA", { timeZone: "America/Los_Angeles" }).format(now);
}

export function quotaUsedToday(): number {
  const q = loadStore().quota;
  return q.day === quotaDay() ? q.used : 0;
}

function addQuota(units: number) {
  const day = quotaDay();
  updateStore((d) => {
    if (d.quota.day !== day) d.quota = { day, used: 0 };
    d.quota.used += units;
  });
}

let lastCall = 0;
const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

function cacheFile(endpoint: string, params: Record<string, string>): string {
  const keyStr = endpoint + "?" + Object.keys(params).sort().map((k) => `${k}=${params[k]}`).join("&");
  const h = crypto.createHash("sha1").update(keyStr).digest("hex");
  return path.join(dataDir(), "cache", `${endpoint.replace(/\W/g, "_")}_${h}.json`);
}

export interface GetOptions {
  cost: number;
  useCache?: boolean;
}

/** 실패 시 사람이 읽을 수 있는 이유를 담은 YouTubeError를 던진다 (키는 포함하지 않음) */
export async function ytGet<T>(endpoint: string, params: Record<string, string>, opts: GetOptions): Promise<T> {
  const useCache = opts.useCache ?? true;
  const cf = cacheFile(endpoint, params);
  if (useCache && fs.existsSync(cf) && Date.now() - fs.statSync(cf).mtimeMs < CACHE_TTL_MS) {
    return JSON.parse(fs.readFileSync(cf, "utf8")) as T;
  }
  const key = apiKey();
  if (quotaUsedToday() + opts.cost > dailyQuota() * 0.9) {
    throw new YouTubeError("quota", `오늘 추정 사용량이 일일 할당량(${dailyQuota()})의 90%에 도달해 수집을 중단했습니다.`);
  }

  const qs = new URLSearchParams({ ...params, key });
  let attempt = 0;
  for (;;) {
    const wait = lastCall + MIN_INTERVAL_MS - Date.now();
    if (wait > 0) await sleep(wait);
    lastCall = Date.now();
    let res: Response;
    try {
      res = await fetch(`${API}/${endpoint}?${qs}`, { headers: { Accept: "application/json" }, cache: "no-store" });
    } catch {
      if (attempt++ < 3) {
        await sleep(1000 * 2 ** attempt);
        continue;
      }
      throw new YouTubeError("network", `${endpoint} 요청 실패: 네트워크 오류`);
    }
    addQuota(opts.cost);
    if (res.ok) {
      const json = (await res.json()) as T;
      fs.mkdirSync(path.dirname(cf), { recursive: true });
      fs.writeFileSync(cf, JSON.stringify(json), "utf8");
      return json;
    }
    let reason = "";
    let msg = "";
    try {
      const body = (await res.json()) as { error?: { message?: string; errors?: { reason?: string }[] } };
      reason = body.error?.errors?.[0]?.reason ?? "";
      msg = (body.error?.message ?? "").replace(key, "***");
    } catch {
      /* 본문 없음 */
    }
    if (res.status >= 500 && attempt++ < 3) {
      await sleep(1000 * 2 ** attempt);
      continue;
    }
    if (reason === "quotaExceeded" || reason === "dailyLimitExceeded" || reason === "rateLimitExceeded")
      throw new YouTubeError("quota", "YouTube API 할당량을 초과했습니다. 태평양 시간 자정(한국 시간 오후 4~5시) 이후 다시 시도하세요.");
    if (reason === "keyInvalid" || (res.status === 400 && /API key/i.test(msg)))
      throw new YouTubeError("key_invalid", "API 키가 유효하지 않습니다. Google Cloud Console에서 키와 YouTube Data API v3 사용 설정을 확인하세요.");
    if (res.status === 403) throw new YouTubeError("forbidden", `접근 거부(${reason || 403}): ${msg}`);
    if (res.status === 404) throw new YouTubeError("not_found", `${endpoint}: 대상을 찾을 수 없음 (${reason})`);
    throw new YouTubeError("http", `${endpoint} HTTP ${res.status} ${reason} ${msg}`.trim());
  }
}

// ───────────── API 응답 타입 (필요한 필드만) ─────────────

export interface ApiChannel {
  id: string;
  snippet?: { title?: string; description?: string; customUrl?: string; thumbnails?: Record<string, { url: string }> };
  statistics?: { viewCount?: string; subscriberCount?: string; hiddenSubscriberCount?: boolean; videoCount?: string };
  contentDetails?: { relatedPlaylists?: { uploads?: string } };
  topicDetails?: { topicCategories?: string[] };
}

export interface ApiPlaylistItem {
  contentDetails?: { videoId?: string; videoPublishedAt?: string };
  snippet?: { publishedAt?: string; title?: string };
}

export interface ApiVideo {
  id: string;
  snippet?: {
    publishedAt?: string;
    channelId?: string;
    title?: string;
    description?: string;
    tags?: string[];
    liveBroadcastContent?: "none" | "live" | "upcoming";
    thumbnails?: Record<string, { url: string; width?: number; height?: number }>;
  };
  statistics?: { viewCount?: string; likeCount?: string; commentCount?: string };
  contentDetails?: { duration?: string };
  status?: { privacyStatus?: string; uploadStatus?: string };
  liveStreamingDetails?: { actualStartTime?: string };
}

export interface ApiList<T> {
  items?: T[];
  nextPageToken?: string;
  pageInfo?: { totalResults?: number };
}

export interface ApiSearchItem {
  id?: { channelId?: string; videoId?: string };
  snippet?: { title?: string; description?: string; channelId?: string; channelTitle?: string };
}

/** /shorts/ 주소가 리다이렉트 없이 열리면 쇼츠. 확인 실패 시 null */
export async function checkShortsUrl(videoId: string): Promise<boolean | null> {
  try {
    const res = await fetch(`https://www.youtube.com/shorts/${videoId}`, { method: "HEAD", redirect: "manual" });
    if (res.status === 200) return true;
    if (res.status >= 300 && res.status < 400) return false;
    return null;
  } catch {
    return null;
  }
}
