// 공통 타입 정의. 시각은 모두 UTC ISO 문자열로 저장하고, 화면에서만 KST로 변환한다.

export type DataSource = "real" | "demo";

/** 페이스리스 분류: A 내레이션+자료화면 / B 애니메이션 / C 차트·스크린캐스트 / D 인물 노출 / E 혼합 / U 확인 불가 */
export type FacelessClass = "A" | "B" | "C" | "D" | "E" | "U";

/** 판정 확인 수준: 확정(사용자가 영상을 직접 확인) / 추정(설명·제목 등 간접 근거) / 확인 필요(근거 부족) */
export type Confidence = "confirmed" | "estimated" | "unverified";

export type VideoFormat = "long" | "shorts" | "other";

export interface FacelessJudgement {
  cls: FacelessClass;
  confidence: Confidence;
  evidence: string[];
}

export interface ChannelRecord {
  id: string;
  title: string;
  handle: string | null;
  url: string;
  subscriberCount: number | null; // null = 비공개 또는 수집 불가
  subscriberHidden: boolean;
  viewCount: number | null;
  videoCount: number | null;
  description: string | null;
  topicCategories: string[];
  uploadsPlaylistId: string | null;
  thumbnailUrl: string | null;
  collectedAt: string | null;
  source: DataSource;
  /** 채널 단위 페이스리스 판정 (영상별 판정 비중으로 갱신됨) */
  faceless: FacelessJudgement;
}

export interface VideoRecord {
  id: string;
  url: string;
  channelId: string;
  title: string;
  description: string | null;
  publishedAt: string | null; // null = 게시 시각 확인 불가
  durationSec: number | null;
  format: VideoFormat;
  formatEvidence: string;
  thumbnailUrl: string | null;
  tags: string[];
  /** 최신 관측값 (가장 최근 스냅샷과 동일) */
  viewCount: number | null;
  likeCount: number | null; // null = 비공개/수집 불가
  commentCount: number | null; // null = 댓글 비활성/비공개/수집 불가
  /** 관측 당시 채널 구독자 수 */
  channelSubscriberCount: number | null;
  collectedAt: string;
  firstSeenAt: string;
  status: "available" | "unavailable"; // 삭제·비공개 전환 시 unavailable
  liveContent: "none" | "live" | "upcoming" | "completed";
  keywords: string[];
  faceless: FacelessJudgement;
  source: DataSource;
}

export interface Snapshot {
  videoId: string;
  collectedAt: string;
  viewCount: number | null;
  likeCount: number | null;
  commentCount: number | null;
}

export interface CollectionRun {
  id: string;
  startedAt: string;
  finishedAt: string | null;
  status: "running" | "success" | "partial" | "failed";
  quotaUsed: number;
  channelsOk: number;
  channelsFailed: number;
  videosCollected: number;
  messages: { level: "info" | "warn" | "error"; text: string }[];
}

export interface Weights {
  velocity: number; // 게시 후 경과 시간 대비 조회 속도
  relative: number; // 채널 내 유사 경과 시간 영상 대비 성과
  subRatio: number; // 구독자 대비 조회수
  likeRate: number;
  commentRate: number;
  faceless: number; // 페이스리스 재현 적합성 (최종 우선순위에만 사용)
}

export const DEFAULT_WEIGHTS: Weights = {
  velocity: 30,
  relative: 25,
  subRatio: 20,
  likeRate: 10,
  commentRate: 5,
  faceless: 10,
};

export interface CandidateChannel {
  key: string;
  name: string;
  channelId: string | null;
  handle: string | null;
  url: string | null;
  /** 2026-10-11 YouTube 공개 검색에서 확인한 구독자 표기 (참고용, API 값이 아님) */
  verifiedNote: string;
  list: "initial" | "replacement";
  priorClass: FacelessClass;
  priorReason: string;
  decision: "selected" | "excluded" | "pending";
  decisionReason: string;
  userPick: boolean;
  description: string;
}

export interface VideoAnnotation {
  videoId: string;
  updatedAt: string;
  /** 사용자가 직접 확인한 항목만 verified=true */
  thumbnail: {
    verified: boolean;
    text: string;
    faceVisible: "yes" | "no" | "unknown";
    elements: string[]; // 차트, 숫자, 화살표 등
    contrast: "high" | "medium" | "low" | "unknown";
    layout: string;
  };
  structure: {
    verified: boolean;
    hook: string;
    firstInfoSec: number | null;
    flow: string;
    cta: string;
  };
  visual: {
    verified: boolean;
    style: string;
    cutsPerMinute: number | null;
    subtitleDensity: "high" | "medium" | "low" | "unknown";
    notes: string;
  };
  faceless?: { cls: FacelessClass; confirmed: boolean };
}

export interface Settings {
  weights: Weights;
  periodDays: number; // 기본 14
  peerWindowDays: number; // 기본 90
  dataMode: "auto" | "demo" | "real";
  /** 정밀 분석 대상으로 고정한 채널 ID (사용자 선택) */
  pinnedTop3: string[];
  /** 3번째 슬롯(경제·기업사 애니메이션 채널) 확정 전 후보 */
  slot3Candidates: string[];
  facelessOverrides: Record<string, { cls: FacelessClass; confirmed: boolean; note: string }>;
  extraChannelIds: string[];
}
