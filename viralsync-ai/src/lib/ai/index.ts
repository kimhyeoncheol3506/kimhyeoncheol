import "server-only";
import { AnthropicProvider } from "./anthropic-provider";
import { DemoProvider } from "./demo-provider";
import type { AIProvider, ProviderStatus } from "./types";

/** 환경변수에 따라 AI Provider 를 선택한다. 키는 서버에서만 읽는다. */
export function getProvider(): { provider: AIProvider; status: ProviderStatus } {
  const wanted = (process.env.AI_PROVIDER ?? "demo").toLowerCase();
  const key = process.env.ANTHROPIC_API_KEY?.trim();
  const model = process.env.ANTHROPIC_MODEL?.trim() || "claude-opus-5-5";

  if (wanted === "anthropic") {
    if (key) {
      return {
        provider: new AnthropicProvider(key, model),
        status: { active: "anthropic", model, configured: true, message: `Anthropic API (${model}) 사용 중` },
      };
    }
    const demo = new DemoProvider();
    return {
      provider: demo,
      status: {
        active: "demo",
        model: demo.model,
        configured: false,
        message: "AI_PROVIDER=anthropic 이지만 ANTHROPIC_API_KEY 가 설정되지 않아 데모 템플릿 Provider 로 생성합니다.",
      },
    };
  }
  const demo = new DemoProvider();
  return {
    provider: demo,
    status: {
      active: "demo",
      model: demo.model,
      configured: false,
      message: "데모 모드: 외부 AI API 를 호출하지 않고 템플릿으로 초안을 생성합니다 (비용 0원).",
    },
  };
}
