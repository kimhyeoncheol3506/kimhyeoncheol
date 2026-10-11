// 로컬 저장소 (JSON 파일)
//
// SQLite + Prisma 대신 JSON 파일을 선택한 이유:
// - Prisma는 설치 시 쿼리 엔진 바이너리를 별도로 내려받아야 하고, better-sqlite3 같은 네이티브 모듈은
//   Windows에서 빌드 도구가 없으면 설치가 실패할 수 있다. 초보 제작자가 `npm install` 한 번으로 실행할 수 있게
//   의존성 없는 파일 저장소를 사용한다.
// - 데이터 규모(채널 10~20개, 영상 수백~수천 개, 하루 1~수회 스냅샷)는 JSON 파일로 충분하다.
// - 영상은 ID를 키로 하는 객체에 저장해 중복을 막고, 스냅샷은 (영상 ID, 수집 시각) 쌍으로 중복을 막는다.
// - 쓰기는 임시 파일에 기록 후 rename 하는 원자적 방식으로 처리한다.

import fs from "node:fs";
import path from "node:path";
import type {
  ChannelRecord,
  CollectionRun,
  Settings,
  Snapshot,
  VideoAnnotation,
  VideoRecord,
} from "./types";
import { DEFAULT_WEIGHTS } from "./types";
import { SLOT3, USER_PICKS } from "./candidates";

export interface StoreData {
  version: 1;
  settings: Settings;
  channels: Record<string, ChannelRecord>;
  videos: Record<string, VideoRecord>;
  snapshots: Snapshot[];
  runs: CollectionRun[];
  annotations: Record<string, VideoAnnotation>;
  quota: { day: string; used: number };
}

export function defaultSettings(): Settings {
  return {
    weights: { ...DEFAULT_WEIGHTS },
    periodDays: 14,
    peerWindowDays: 90,
    dataMode: "auto",
    pinnedTop3: USER_PICKS.filter((x): x is string => !!x),
    slot3Candidates: [...SLOT3.candidateIds],
    facelessOverrides: {},
    extraChannelIds: [],
  };
}

function emptyStore(): StoreData {
  return {
    version: 1,
    settings: defaultSettings(),
    channels: {},
    videos: {},
    snapshots: [],
    runs: [],
    annotations: {},
    quota: { day: "", used: 0 },
  };
}

export function dataDir(): string {
  return path.resolve(process.env.DATA_DIR || path.join(process.cwd(), "data"));
}

function storePath(): string {
  return path.join(dataDir(), "store.json");
}

let cache: { mtime: number; data: StoreData } | null = null;

export function loadStore(): StoreData {
  const p = storePath();
  if (!fs.existsSync(p)) return emptyStore();
  const mtime = fs.statSync(p).mtimeMs;
  if (cache && cache.mtime === mtime) return cache.data;
  const raw = JSON.parse(fs.readFileSync(p, "utf8")) as Partial<StoreData>;
  const base = emptyStore();
  const data: StoreData = {
    ...base,
    ...raw,
    settings: { ...base.settings, ...(raw.settings ?? {}), weights: { ...base.settings.weights, ...(raw.settings?.weights ?? {}) } },
  } as StoreData;
  cache = { mtime, data };
  return data;
}

export function saveStore(data: StoreData): void {
  const dir = dataDir();
  fs.mkdirSync(dir, { recursive: true });
  const p = storePath();
  const tmp = `${p}.${process.pid}.tmp`;
  fs.writeFileSync(tmp, JSON.stringify(data, null, 1), "utf8");
  fs.renameSync(tmp, p);
  cache = { mtime: fs.statSync(p).mtimeMs, data };
}

export function updateStore(fn: (d: StoreData) => void): StoreData {
  const d = structuredClone(loadStore());
  fn(d);
  saveStore(d);
  return d;
}

/** 영상 upsert: 같은 ID는 덮어쓰되 최초 발견 시각은 유지 */
export function upsertVideo(d: StoreData, v: VideoRecord): void {
  const prev = d.videos[v.id];
  d.videos[v.id] = prev ? { ...v, firstSeenAt: prev.firstSeenAt } : v;
}

/** 스냅샷 추가: 같은 영상·같은 수집 시각이면 중복 저장하지 않음 */
export function addSnapshot(d: StoreData, s: Snapshot): boolean {
  if (d.snapshots.some((x) => x.videoId === s.videoId && x.collectedAt === s.collectedAt)) return false;
  d.snapshots.push(s);
  return true;
}
