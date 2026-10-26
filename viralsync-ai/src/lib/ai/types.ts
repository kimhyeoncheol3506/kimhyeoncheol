import type { ContentType, PlatformKey } from "@prisma/client";

export interface GenerationContext {
  clientName: string;
  campaignName: string;
  goal: string;
  targetType: string;
  coreTarget: string;
  keywords: string[];
  bannedKeywords: string[];
  description: string;
  targetUrl?: string | null;
  brand: {
    companyIntro: string;
    productDescription: string;
    toneOfVoice: string;
    bannedPhrases: string[];
    requiredPhrases: string[];
  };
  candidate?: {
    platform: PlatformKey;
    accountName: string;
    title: string;
    summary: string;
  } | null;
  platform?: PlatformKey | null;
  /** 고객(가게) 본인 계정에 올리는 글 — 광고 태그 불필요, 손님·후기인 척 금지 */
  ownAccount?: boolean;
}

export interface GeneratedDraft {
  type: ContentType;
  body: string;
}

export interface GenerationResult {
  ok: boolean;
  drafts: GeneratedDraft[];
  provider: string;
  model: string;
  /** 원화 환산 추정 비용 */
  costKrw: number;
  inputTokens?: number;
  outputTokens?: number;
  errorCode?: string;
  errorMessage?: string;
}

export interface AIProvider {
  readonly id: string;
  readonly model: string;
  generate(ctx: GenerationContext, types: ContentType[]): Promise<GenerationResult>;
}

export interface ProviderStatus {
  active: string;
  model: string;
  configured: boolean;
  message: string;
}
