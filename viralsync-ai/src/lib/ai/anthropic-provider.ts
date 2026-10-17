import "server-only";
import Anthropic from "@anthropic-ai/sdk";
import type { ContentType } from "@prisma/client";
import { z } from "zod";
import { CONTENT_TYPE_LABEL } from "@/lib/labels";
import type { AIProvider, GenerationContext, GenerationResult } from "./types";

// USD per 1M tokens (Claude API 1st-party list price). 모델 추가 시 여기에 등록.
const PRICING: Record<string, { input: number; output: number }> = {
  "claude-opus-5-5": { input: 4, output: 20 },
  "claude-sonnet-5-5": { input: 2, output: 10 },
  "claude-haiku-5-5": { input: 0.1, output: 0.5 },
};

const SYSTEM = `당신은 한국어 광고 카피라이터입니다. 반드시 다음 원칙을 지킵니다.
- 광고임을 숨기지 않습니다. 모든 문구에 "광고" 또는 "유료 광고" 표시를 포함합니다.
- 일반 이용자인 척하거나, 직접 사용해 본 것처럼 쓰는 체험담·후기를 만들지 않습니다.
- 브랜드가 제공한 정보 외의 사실·수치·효과를 지어내지 않습니다. 과장·단정 표현(100%, 무조건, 보장, 최고 등)을 쓰지 않습니다.
- 금지 표현은 쓰지 않고, 필수 표현은 자연스럽게 포함합니다.
- 연결된 게시물의 문맥에 맞게, 짧고 정중하게 씁니다.
출력은 JSON 하나만: {"drafts":[{"type":"<TYPE>","body":"<문구>"}]}`;

const OutputSchema = z.object({
  drafts: z.array(z.object({ type: z.string(), body: z.string().min(1) })),
});

export class AnthropicProvider implements AIProvider {
  readonly id = "anthropic";
  readonly model: string;
  private client: Anthropic;

  constructor(apiKey: string, model: string) {
    this.model = model;
    this.client = new Anthropic({ apiKey, timeout: 60_000, maxRetries: 1 });
  }

  async generate(ctx: GenerationContext, types: ContentType[]): Promise<GenerationResult> {
    const base = { provider: this.id, model: this.model, drafts: [], costKrw: 0 };
    const user = buildPrompt(ctx, types);
    try {
      const res = await this.client.beta.messages.create({
        model: this.model,
        max_tokens: 4000,
        betas: ["server-side-fallback-2026-07-01"],
        fallbacks: "default",
        output_config: { effort: "low" },
        system: SYSTEM,
        messages: [{ role: "user", content: user }],
      });
      if (res.stop_reason === "refusal") {
        return { ...base, ok: false, errorCode: "AI_REFUSAL", errorMessage: "AI 가 요청 생성을 거절했습니다. 의뢰 내용을 확인하세요." };
      }
      const text = res.content
        .filter((b): b is Anthropic.Beta.BetaTextBlock => b.type === "text")
        .map((b) => b.text)
        .join("");
      const json = text.slice(text.indexOf("{"), text.lastIndexOf("}") + 1);
      const parsed = OutputSchema.safeParse(safeJson(json));
      if (!parsed.success) {
        return { ...base, ok: false, errorCode: "AI_BAD_OUTPUT", errorMessage: "AI 응답 형식을 해석하지 못했습니다." };
      }
      const allowed = new Set<string>(types);
      const drafts = parsed.data.drafts
        .filter((d) => allowed.has(d.type))
        .map((d) => ({ type: d.type as ContentType, body: d.body.trim() }));
      const inputTokens = res.usage.input_tokens;
      const outputTokens = res.usage.output_tokens;
      return {
        ok: drafts.length > 0,
        drafts,
        provider: this.id,
        model: res.model,
        inputTokens,
        outputTokens,
        costKrw: estimateKrw(res.model, inputTokens, outputTokens),
        ...(drafts.length ? {} : { errorCode: "AI_EMPTY", errorMessage: "AI 가 요청한 유형의 초안을 반환하지 않았습니다." }),
      };
    } catch (err) {
      // 오류 메시지에 키가 포함되지 않도록 상태 코드와 분류만 남긴다.
      if (err instanceof Anthropic.AuthenticationError)
        return { ...base, ok: false, errorCode: "AI_AUTH", errorMessage: "AI API 키 인증에 실패했습니다. 키를 확인하세요." };
      if (err instanceof Anthropic.RateLimitError)
        return { ...base, ok: false, errorCode: "AI_RATE_LIMIT", errorMessage: "AI API 호출 한도를 초과했습니다. 잠시 후 다시 시도하세요." };
      if (err instanceof Anthropic.APIConnectionError)
        return { ...base, ok: false, errorCode: "AI_NETWORK", errorMessage: "AI API 에 연결할 수 없습니다." };
      if (err instanceof Anthropic.APIError)
        return { ...base, ok: false, errorCode: `AI_HTTP_${err.status ?? "ERR"}`, errorMessage: "AI API 호출이 실패했습니다." };
      return { ...base, ok: false, errorCode: "AI_UNKNOWN", errorMessage: "AI 생성 중 알 수 없는 오류가 발생했습니다." };
    }
  }
}

function safeJson(s: string): unknown {
  try {
    return JSON.parse(s);
  } catch {
    return null;
  }
}

export function estimateKrw(model: string, input: number, output: number): number {
  const p = PRICING[model] ?? PRICING["claude-opus-5-5"];
  const usd = (input * p.input + output * p.output) / 1_000_000;
  const rate = Number(process.env.USD_KRW_RATE ?? 1400) || 1400;
  return Math.ceil(usd * rate);
}

function buildPrompt(c: GenerationContext, types: ContentType[]): string {
  return [
    `고객: ${c.clientName}`,
    `캠페인: ${c.campaignName} (목표: ${c.goal}, 대상 유형: ${c.targetType})`,
    `핵심 타깃: ${c.coreTarget || "미입력"}`,
    `키워드: ${c.keywords.join(", ") || "없음"}`,
    `금지 키워드/표현: ${[...c.bannedKeywords, ...c.brand.bannedPhrases].join(", ") || "없음"}`,
    `필수 표현: ${c.brand.requiredPhrases.join(", ") || "없음"}`,
    `브랜드 문체: ${c.brand.toneOfVoice || "정중하고 담백하게"}`,
    `회사 소개: ${c.brand.companyIntro || "없음"}`,
    `상품 설명: ${c.brand.productDescription || c.description || "없음"}`,
    c.targetUrl ? `홍보 URL: ${c.targetUrl}` : "",
    c.candidate
      ? `연결 게시물: [${c.candidate.platform}] ${c.candidate.accountName} — ${c.candidate.title}\n요약: ${c.candidate.summary}`
      : "연결 게시물: 없음 (자체 게시물용)",
    "",
    "다음 유형별로 1개씩 작성하세요 (type 값은 그대로 사용):",
    ...types.map((t) => `- ${t}: ${CONTENT_TYPE_LABEL[t]}`),
  ]
    .filter(Boolean)
    .join("\n");
}
