// 해설 글 목록: 주제 글 + 일간 10종 글을 같은 모양으로 묶는다.
import { ELEMENT_COLOR_NAME, tenGodOf, type Element } from "../saju/constants";
import { ILGAN, type Ilgan } from "./ilgan";
import { TOPICS, type Topic } from "./topics";

export type GuidePage = Topic & { kind: "topic" | "ilgan"; ilgan?: Ilgan };

// 2027년 정미년(丁未)의 천간 丁 이 각 일간에게 어떤 별인지에 따른 한 해 흐름 (일간마다 다름)
const YEAR_2027: Record<string, string> = {
  비견: "나와 같은 불 기운이 들어오는 해라, 비슷한 사람들이 모여들고 독립과 자기 주도의 기회가 커진다고 봅니다. 다만 동업이나 보증처럼 돈이 얽힌 약속은 한 번 더 따져 보는 것이 좋습니다.",
  겁재: "경쟁과 자극이 커지는 해로 풀이합니다. 과감한 도전이 성과로 이어지기 쉽지만, 충동적인 지출과 돈 거래는 조심하는 편이 좋습니다.",
  식신: "재능을 드러내고 생활의 여유를 찾기 좋은 해로 봅니다. 새 취미나 창작을 시작하거나, 좋아하는 일을 작게라도 일로 만들어 보기에 어울립니다.",
  상관: "표현하고 바꾸고 싶은 마음이 커지는 해로 봅니다. 아이디어와 말솜씨가 빛나지만, 윗사람과의 마찰이나 말실수는 한 번 더 조심하면 좋습니다.",
  편재: "돈과 기회가 활발히 움직이는 해로 풀이합니다. 거래·영업·부수입에 좋은 흐름이지만, 한 번에 크게 거는 결정은 피하는 편이 안전합니다.",
  정재: "꾸준히 해 온 일이 결실로 돌아오는 해로 봅니다. 저축과 자산 정리, 생활 기반을 다지기에 좋은 흐름입니다.",
  편관: "책임과 압박이 커지는 시험대의 해로 풀이합니다. 버텨 내면 실력이 한 단계 오르지만, 과로하지 않도록 건강을 먼저 챙기세요.",
  정관: "인정과 공식적인 좋은 일이 생기기 쉬운 해로 봅니다. 승진·합격·계약처럼 반듯한 기회를 잡기 좋은 흐름입니다.",
  편인: "공부와 전환의 해로 풀이합니다. 새로운 분야를 익히거나 방향을 다시 잡기 좋지만, 생각만 많아지지 않게 작은 실천을 함께 챙기세요.",
  정인: "도와주는 사람과 문서운이 따르는 해로 봅니다. 배움, 자격, 계약, 집과 관련된 일에서 좋은 흐름을 기대해 볼 만합니다.",
};
const BODY_CARE: Record<Element, string> = {
  목: "나무 기운은 전통적으로 간·눈·근육과 관절에 연결해 봅니다. 오래 앉아 있기보다 자주 몸을 펴 주고, 눈을 쉬게 하는 습관이 좋다고 풀이합니다.",
  화: "불 기운은 심장·혈압·혈액순환에 연결해 봅니다. 감정이 달아오를 때 잠시 쉬어 가고, 땀 흘리는 운동과 충분한 휴식을 함께 챙기는 것이 좋습니다.",
  토: "흙 기운은 위장과 소화에 연결해 봅니다. 끼니를 거르지 않고 일정한 시간에 먹는 습관이 몸과 마음의 중심을 잡아 준다고 풀이합니다.",
  금: "쇠 기운은 폐·호흡기·피부에 연결해 봅니다. 깊은 호흡과 환기, 건조하지 않은 환경을 챙기는 것이 좋다고 풀이합니다.",
  수: "물 기운은 신장·방광과 몸의 냉기에 연결해 봅니다. 물을 자주 마시고 몸을 따뜻하게 하며, 잠을 충분히 자는 것이 좋다고 풀이합니다.",
};

function fromIlgan(il: Ilgan, i: number): GuidePage {
  const prev = ILGAN[(i + 9) % 10];
  const next = ILGAN[(i + 1) % 10];
  const partner = ILGAN.find((x) => x.stem === il.partner.stem)!;
  return {
    kind: "ilgan",
    ilgan: il,
    slug: il.slug,
    title: `${il.ko}(${il.stem}) 일간: ${il.image} 같은 사람의 성격과 적성`,
    description: `${il.ko} 일간은 ${il.summary}으로 풀이합니다. ${il.ko}의 성격, 강점과 조심할 점, 잘 맞는 일과 연애 스타일, 기운을 살리는 생활 습관을 정리했습니다.`,
    lead: `${il.ko}(${il.stem})은 ${ELEMENT_COLOR_NAME[il.element]} 기운의 ${il.yang ? "양" : "음"} 일간으로, 흔히 ‘${il.image}’에 비유합니다. 태어난 날의 천간이 ${il.stem}인 사람의 일반적인 성향을 정리했습니다.`,
    sections: [
      { h: `${il.image}에 비유하는 이유`, body: [il.nature] },
      { h: "성격", body: [il.character] },
      { h: "강점", body: [`${il.ko} 일간에게서 자주 보이는 강점은 다음과 같습니다.`], list: il.strengths },
      { h: "조심하면 좋은 점", body: ["강점의 그림자처럼 따라오기 쉬운 부분입니다. 알고 있으면 충분히 다스릴 수 있습니다."], list: il.cautions },
      { h: "일과 적성", body: [il.work] },
      { h: "연애와 인간관계", body: [il.love] },
      { h: "기운을 살리는 생활 습관", body: [il.growth] },
      { h: `잘 맞는 짝: ${il.partner.ko}(${il.partner.stem})`, body: [il.partner.text] },
      {
        h: `2027년 정미년, ${il.ko}에게는`,
        body: [
          `2027년은 정미(丁未)년, 붉은 양의 해입니다. 해의 천간 정화(丁)는 ${il.ko} 일간에게 ‘${tenGodOf(il.stem, "丁")}’에 해당합니다. ${YEAR_2027[tenGodOf(il.stem, "丁")]}`,
          "다만 실제 한 해의 흐름은 나머지 일곱 글자와 10년 흐름에 따라 크게 달라지니, 정확한 흐름은 내 사주로 직접 확인해 보세요.",
        ],
      },
      { h: "건강 관리 포인트", body: [`${BODY_CARE[il.element]} 건강에 관한 풀이는 전통 해석일 뿐 의학적 판단이 아니므로, 불편한 증상이 있다면 꼭 전문의와 상담하세요.`] },
    ],
    related: [partner.slug, prev.slug, next.slug, "ilgan-overview", "ohaeng"],
  };
}

export const GUIDES: GuidePage[] = [
  ...TOPICS.map((t) => ({ ...t, kind: "topic" as const })),
  ...ILGAN.map(fromIlgan),
];

export const guideBySlug = (slug: string) => GUIDES.find((g) => g.slug === slug);

/** 본문 글자 수 (공백 제외) — 얇은 글 방지 점검용 */
export const guideLength = (g: GuidePage) =>
  [g.lead, ...g.sections.flatMap((s) => [s.h, ...s.body, ...(s.list ?? [])])].join("").replace(/\s/g, "").length;
