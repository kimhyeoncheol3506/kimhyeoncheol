// Claude 로 자연스러운 한국어 해석을 만드는 서버 API.
// - ANTHROPIC_API_KEY 환경변수가 없으면 { disabled: true } 를 돌려주고, 화면은 규칙 기반 해석을 그대로 씁니다.
// - 사진과 생년월일은 받지 않습니다. 브라우저에서 계산된 '결과 요약'만 받고, 어디에도 저장하지 않습니다.
import Anthropic from "@anthropic-ai/sdk";
import { zodOutputFormat } from "@anthropic-ai/sdk/helpers/zod";
import { z } from "zod";

export const runtime = "nodejs";
export const maxDuration = 60;

const ReadingSchema = z.object({
  headline: z.string().describe("결과 페이지 최상단에 크게 들어갈 한 줄 (20자 이내, '~한 사람' 형태 권장)"),
  summary: z.string().describe("사주와 관상이 공통으로 말하는 핵심 2~3문장"),
  sections: z.array(
    z.object({
      id: z.enum(["week", "periods", "personality", "elements", "career", "love", "health", "life", "months", "luck", "caution"]),
      eyebrow: z.string(),
      title: z.string(),
      body: z.array(z.string()).describe("문단 2~4개"),
    }),
  ),
  advice: z.array(z.string()).describe("당부 3~4개, 각 한두 문장"),
});

const SYSTEM = `당신은 30년 경력의 명리학자이자 관상가이며, 따뜻하지만 군더더기 없는 문체로 글을 씁니다.
입력으로 '두 개의 사주 엔진이 공통으로 낸 결과'와 '관상 분석 결과', 그리고 둘이 겹친 '공통 테마', 규칙 기반 초안이 주어집니다.

규칙:
1. 반드시 입력에 있는 공통 결과만 근거로 쓰세요. 입력에 없는 신살·격국·합충 등을 새로 만들어 내지 마세요.
2. 사주와 관상이 같이 가리키는 공통 테마를 중심에 두고 "사주와 관상이 동시에 말하는 것"으로 표현하세요.
3. sections 는 초안(draft)에 있는 섹션을 같은 id·순서·제목으로 모두 유지하고, 각 섹션을 초안보다 더 풍부하게(문단 3~6개) 쓰세요. eyebrow 는 "01"부터 차례로.
4. week 는 초안의 날짜 그대로 '잘되는 일'·'조심할 일'·'가장 좋은 날'·'조심할 날'을 한 줄씩, periods 는 다음 주·이번 달·다음 달·올해·내년·지금의 10년을 한 줄씩 각각 좋은 일과 주의할 일을 함께 쓰세요. 오늘 이전의 날짜·달은 절대 쓰지 마세요. life 는 10년 단위 흐름을 나이대별로, months 는 초안의 달마다 한 줄씩 쓰세요. luck 의 색·방향·숫자는 초안 값을 그대로 쓰세요.
5. caution 과 advice 에는 앞으로의 주의사항과 당부를 실천 가능한 행동으로 쓰세요.
6. 건강은 오락용 참고임을 밝히고, 질병을 진단하거나 단정하지 마세요. 공포를 주는 표현, 죽음·사고 예언은 금지.
7. 한국어 존댓말, 짧고 리듬감 있는 문장. 소리 내어 읽기 좋게 한자와 괄호는 쓰지 마세요.
8. 십신·용신·대운·일간·재성·충 같은 명리학 용어는 쓰지 말고 '재물의 별', '10년 흐름', '나를 돕는 기운'처럼 쉬운 말로 풀어 쓰세요.
9. 막연한 말 대신 연도·계절·행동으로 구체적으로 쓰세요. 예: '2027년 봄, 이직 운이 가장 강해요'.`;

export async function POST(req: Request) {
  if (!process.env.ANTHROPIC_API_KEY) return Response.json({ disabled: true });

  let body: unknown;
  try {
    body = await req.json();
  } catch {
    return Response.json({ error: "bad request" }, { status: 400 });
  }
  const input = JSON.stringify(body);
  if (input.length > 20000) return Response.json({ error: "too large" }, { status: 413 });

  try {
    const client = new Anthropic();
    const response = await client.messages.parse({
      model: process.env.ANTHROPIC_MODEL || "claude-opus-5-5",
      max_tokens: 16000,
      system: SYSTEM,
      output_config: { format: zodOutputFormat(ReadingSchema), effort: "low" },
      messages: [{ role: "user", content: `다음 분석 결과로 해석을 작성해 주세요.\n\n${input}` }],
    });
    if (response.stop_reason === "refusal" || !response.parsed_output) {
      return Response.json({ error: "no output" }, { status: 502 });
    }
    return Response.json(response.parsed_output);
  } catch (e) {
    if (e instanceof Anthropic.APIError) {
      console.error("Claude API error", e.status, e.message);
      return Response.json({ error: "ai unavailable" }, { status: 502 });
    }
    console.error(e);
    return Response.json({ error: "server error" }, { status: 500 });
  }
}
