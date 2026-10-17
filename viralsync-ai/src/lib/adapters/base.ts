import type { IntegrationStatus, PlatformKey } from "@prisma/client";
import type { AccountLike, PlatformAdapter, PublishRequest, PublishResult } from "./types";

function hash(s: string): number {
  let h = 2166136261;
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 16777619) >>> 0;
  }
  return h;
}

export abstract class BaseAdapter implements PlatformAdapter {
  abstract readonly key: PlatformKey;
  abstract readonly name: string;
  abstract readonly requiredEnv: string[];
  abstract readonly docsUrl: string;
  abstract readonly apiNotes: string;
  readonly livePublishImplemented: boolean = false;

  missingEnv(): string[] {
    return this.requiredEnv.filter((k) => !process.env[k]?.trim());
  }

  envConfigured(): boolean {
    return this.missingEnv().length === 0;
  }

  /**
   * 1 데모 전용 → 2 API 연동 준비(환경변수 설정) → 3 인증 완료(계정 OAuth 완료)
   * → 4 게시 가능(실제 게시 호출 구현 + 인증) / 5 제한·오류
   */
  status(account: AccountLike | null): IntegrationStatus {
    if (account?.status === "RESTRICTED" || account?.lastError) return "RESTRICTED";
    if (!this.envConfigured()) return "DEMO_ONLY";
    if (!account || (account.status !== "AUTHENTICATED" && account.status !== "PUBLISH_READY")) return "API_READY";
    return this.livePublishImplemented ? "PUBLISH_READY" : "AUTHENTICATED";
  }

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  async publishLive(_req: PublishRequest): Promise<PublishResult> {
    if (!this.envConfigured())
      return {
        ok: false,
        errorCode: "NOT_CONFIGURED",
        errorMessage: `${this.name} 공식 API 자격증명이 설정되지 않았습니다 (${this.missingEnv().join(", ")}).`,
        retryable: false,
      };
    return {
      ok: false,
      errorCode: "LIVE_NOT_IMPLEMENTED",
      errorMessage: `${this.name} 실제 게시 호출은 아직 구현되지 않았습니다. 공식 API 심사·권한 확보 후 별도 단계에서 구현합니다.`,
      retryable: false,
    };
  }

  /** 외부 호출 없이 결과를 결정적으로 만들어 내는 모의 실행 */
  simulate(req: PublishRequest): PublishResult {
    if (req.text.length > req.maxTextLength)
      return {
        ok: false,
        errorCode: "TEXT_TOO_LONG",
        errorMessage: `${this.name} 최대 글자 수(${req.maxTextLength}자)를 초과했습니다.`,
        retryable: false,
      };
    const h = hash(`${this.key}|${req.text}|${req.targetUrl ?? ""}|${req.attempt}`);
    if (h % 7 === 0)
      return {
        ok: false,
        errorCode: "SIM_RATE_LIMITED",
        errorMessage: "[모의] 플랫폼 호출 한도 초과 상황을 재현했습니다. 재시도할 수 있습니다.",
        retryable: true,
      };
    if (h % 11 === 0)
      return {
        ok: false,
        errorCode: "SIM_TARGET_UNAVAILABLE",
        errorMessage: "[모의] 대상 게시물이 비공개/삭제된 상황을 재현했습니다.",
        retryable: true,
      };
    return { ok: true, externalId: `sim_${this.key.toLowerCase()}_${h.toString(36)}` };
  }
}

export { hash as fnv1a };
