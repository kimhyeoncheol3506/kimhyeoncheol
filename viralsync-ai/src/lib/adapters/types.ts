import type { IntegrationStatus, PlatformKey } from "@prisma/client";

export interface PublishRequest {
  text: string;
  targetUrl?: string | null;
  kind: "POST" | "COMMENT";
  /** 재시도 횟수 — 모의 실행 결과 결정에 사용 */
  attempt: number;
  maxTextLength: number;
}

export interface PublishResult {
  ok: boolean;
  externalId?: string;
  errorCode?: string;
  errorMessage?: string;
  retryable?: boolean;
}

export interface AccountLike {
  status: IntegrationStatus;
  lastError?: string | null;
}

export interface PlatformAdapter {
  readonly key: PlatformKey;
  readonly name: string;
  /** 실제 연동에 필요한 서버 환경변수 이름 (값은 절대 노출하지 않음) */
  readonly requiredEnv: string[];
  readonly docsUrl: string;
  /** 공식 API 로 가능한 범위에 대한 메모 — 실제 연동 전 공식 문서로 재확인해야 함 */
  readonly apiNotes: string;
  /** 이 MVP 에 실제 게시 호출이 구현되어 있는지 */
  readonly livePublishImplemented: boolean;
  envConfigured(): boolean;
  missingEnv(): string[];
  status(account: AccountLike | null): IntegrationStatus;
  publishLive(req: PublishRequest): Promise<PublishResult>;
  simulate(req: PublishRequest): PublishResult;
}
