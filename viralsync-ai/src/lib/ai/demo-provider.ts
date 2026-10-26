import type { ContentType } from "@prisma/client";
import type { AIProvider, GeneratedDraft, GenerationContext, GenerationResult } from "./types";

/**
 * 데모 Provider — 외부 API 없이 템플릿으로 초안을 만든다.
 * 체험담·가짜 반응을 만들지 않고, 브랜드가 제공한 설명만 인용한다.
 */
export class DemoProvider implements AIProvider {
  readonly id = "demo";
  readonly model = "demo-template-v1";

  async generate(ctx: GenerationContext, types: ContentType[]): Promise<GenerationResult> {
    const drafts: GeneratedDraft[] = types.map((type) => ({ type, body: render(type, ctx) }));
    return { ok: true, drafts, provider: this.id, model: this.model, costKrw: 0 };
  }
}

function pick<T>(arr: T[], seed: string): T {
  let h = 0;
  for (const c of seed) h = (h * 31 + c.charCodeAt(0)) >>> 0;
  return arr[h % arr.length];
}

function render(type: ContentType, c: GenerationContext): string {
  const product = firstSentence(c.brand.productDescription) || c.description.slice(0, 60) || c.campaignName;
  const kw = c.keywords.slice(0, 3);
  const tags = kw.map((k) => `#${k.replace(/\s+/g, "")}`).join(" ");
  const topic = c.candidate?.title ?? c.campaignName;
  const required = c.brand.requiredPhrases.join(" ");
  const link = c.targetUrl ? `\n자세히 보기: ${c.targetUrl}` : "";
  const ad = "#광고";
  const seed = `${c.campaignName}-${type}-${topic}`;

  switch (type) {
    case "COMMENT":
      return pick(
        [
          `'${topic}' 내용 잘 봤습니다. 관련해서 ${c.clientName}에서 ${product} 정보를 정리해 두었는데, 필요하신 분들께 참고가 될 것 같아 공유드려요. ${required} (${c.clientName} 광고)`,
          `${kw[0] ?? "이 주제"} 관심 있으신 분들 많으시네요. ${c.clientName}의 ${product} 소개 자료가 있어 함께 남깁니다. ${required} (유료 광고)`,
        ],
        seed,
      );
    case "REPLY":
      return `좋은 질문이에요! 이 부분은 ${c.clientName} 공식 안내에 따르면 "${product}"라고 합니다. 세부 조건은 공식 페이지에서 확인해 보세요. ${required} (${c.clientName} 광고)`;
    case "INFORMATIVE":
      return `[정보] ${c.clientName} — ${product}\n• 이런 분께: ${c.coreTarget || "관련 정보를 찾는 분"}\n• 핵심: ${kw.join(", ") || c.campaignName}\n※ 브랜드가 제공한 정보를 바탕으로 작성되었습니다. ${required}${link}\n${ad}`;
    case "QUESTION":
      return `${kw[0] ?? "이 분야"} 고민하실 때 어떤 기준으로 고르시나요? ${c.clientName}은(는) "${product}"를 내세우고 있는데, 여러분이 중요하게 보는 점도 궁금합니다. ${required} ${ad}`;
    case "EMPATHY":
      return `${c.coreTarget || "많은 분들"}이 ${kw[0] ?? "이 문제"} 때문에 고민이 많다는 이야기를 자주 접합니다. ${c.clientName}은(는) 그런 고민을 위해 ${product}를 준비했다고 소개하고 있어요. ${required} ${ad}`;
    case "SNS_POST":
      return `✨ ${c.campaignName}\n\n${product}\n\n${c.coreTarget ? `👉 ${c.coreTarget}에게 추천하는 이유를 확인해 보세요.` : "👉 자세한 내용을 확인해 보세요."}${link}\n\n${tags} ${required} ${ad} #유료광고`;
    case "YOUTUBE_META":
      return `제목: ${kw[0] ? `${kw[0]} 고민이라면` : c.campaignName} | ${c.clientName} ${truncate(product, 30)} 소개 (유료 광고 포함)\n\n설명:\n이 영상은 ${c.clientName}으로부터 제작비를 지원받은 유료 광고를 포함하고 있습니다.\n${product}${link}\n\n${tags} ${required}`;
    case "SHORT_HOOK":
      return pick(
        [
          `${kw[0] ?? "이것"}, 아직도 어렵게 하고 계신가요? 15초 만에 ${c.clientName} 방식 정리해 드립니다. ${required} (광고)`,
          `${c.coreTarget || "여러분"}이 꼭 알아야 할 ${kw[0] ?? "정보"} 한 가지! — ${c.clientName} 협찬 ${required} (광고)`,
        ],
        seed,
      );
    case "SHORT_SCRIPT": {
      const where = c.platform === "TIKTOK" ? "틱톡" : c.platform === "YOUTUBE" ? "유튜브 쇼츠" : c.platform === "INSTAGRAM" ? "인스타 릴스" : "숏폼";
      return [
        `[${where} 대본 · 세로 9:16 · 약 20초] ${c.campaignName}`,
        `#1 (0~3초) 후킹 — 자막: "${kw[0] ?? c.coreTarget ?? "이것"}, 이렇게 고르세요" / 화면 우측 상단 '광고' 표시 고정`,
        `#2 (3~10초) 소개 — 화면: 제품·서비스 화면 / 내레이션: "${c.clientName}의 ${product}"`,
        `#3 (10~17초) 핵심 — 자막: ${kw.length ? kw.map((k) => `✔ ${k}`).join("  ") : "✔ 브랜드 제공 핵심 장점"}`,
        `#4 (17~20초) 행동 유도 — 자막: "${c.targetUrl ? "프로필 링크에서 확인" : "자세한 내용은 프로필에서"}" ${required}`.trim(),
        `캡션: ${c.campaignName} ${tags} ${ad} #유료광고`,
        "※ 출연자가 직접 사용한 것처럼 말하지 않습니다 (브랜드 제공 정보만 사용). 촬영·편집·업로드는 사람 또는 공식 API 몫입니다.",
      ].join("\n");
    }
    case "BLOG_COPY":
      return `## ${c.campaignName}\n\n> 이 글은 ${c.clientName}으로부터 원고료를 지원받아 작성된 광고 콘텐츠입니다.\n\n${c.brand.companyIntro || `${c.clientName}을(를) 소개합니다.`}\n\n### 어떤 서비스인가요?\n${c.brand.productDescription || c.description}\n\n### 이런 분께 추천합니다\n${c.coreTarget || "관련 정보를 찾는 분"}\n\n### 핵심 키워드\n${kw.join(", ")}\n\n※ 위 내용은 브랜드 제공 자료를 바탕으로 작성했으며, 개인 체험담이 아닙니다. ${required}${link}`;
    case "AD_DISCLOSURE":
      return `[광고] 이 콘텐츠는 ${c.clientName}의 유료 광고를 포함하고 있습니다. #광고 #유료광고 #협찬 ${required}`.trim();
  }
}

function firstSentence(s: string): string {
  const t = s.trim();
  if (!t) return "";
  const m = t.match(/^(.+?[.!?。]|.+?(다|요)\.?)(\s|$)/);
  return truncate((m?.[1] ?? t).trim(), 80);
}

function truncate(s: string, n: number): string {
  return s.length > n ? `${s.slice(0, n - 1)}…` : s;
}
