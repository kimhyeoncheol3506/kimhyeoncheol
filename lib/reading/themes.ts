// 사주와 관상을 같은 언어로 비교하기 위한 '공통 테마'
import type { Element } from "../saju/constants";
import type { SajuConsensus } from "../saju/types";

export type ThemeKey =
  | "leadership" | "wealth" | "expression" | "sensitivity" | "stability"
  | "intellect" | "sociability" | "willpower" | "independence";

export const THEMES: Record<ThemeKey, { label: string; short: string; trait: string; career: string; love: string }> = {
  leadership: {
    label: "추진력과 리더십", short: "리더십",
    trait: "사람들 앞에서 방향을 정하고 끌고 가는 힘이 있습니다. 결정이 필요할 때 망설임이 적습니다.",
    career: "조직을 이끄는 자리, 프로젝트 리드, 창업이나 영업처럼 결과로 말하는 일에서 빛납니다.",
    love: "관계에서도 주도권을 쥐는 편입니다. 상대의 속도에 맞춰 주면 훨씬 깊어집니다.",
  },
  wealth: {
    label: "재물 감각", short: "재물",
    trait: "돈의 흐름을 읽는 감각이 있고, 현실적인 판단이 빠릅니다.",
    career: "재무, 투자, 유통, 사업처럼 숫자와 가치가 오가는 분야와 인연이 깊습니다.",
    love: "상대에게 실질적으로 챙겨 주는 방식으로 애정을 표현합니다.",
  },
  expression: {
    label: "표현력과 말솜씨", short: "표현력",
    trait: "생각을 말과 글, 결과물로 풀어내는 재능이 있습니다. 아이디어가 많고 재치가 있습니다.",
    career: "콘텐츠, 마케팅, 교육, 방송, 디자인 등 자신을 드러내는 일에서 강점이 큽니다.",
    love: "감정 표현이 솔직해 매력이 큽니다. 다만 말이 앞서지 않도록 한 박자 쉬어 가세요.",
  },
  sensitivity: {
    label: "섬세한 감수성", short: "감수성",
    trait: "남들이 놓치는 분위기와 감정을 먼저 알아챕니다. 직관이 좋고 공감 능력이 뛰어납니다.",
    career: "예술, 기획, 상담, 연구처럼 깊이와 감각이 필요한 일에서 남다른 결과를 냅니다.",
    love: "상대의 마음을 잘 헤아리지만, 혼자 상처를 삭이기 쉽습니다. 서운함은 바로 말로 꺼내세요.",
  },
  stability: {
    label: "신중함과 안정감", short: "안정감",
    trait: "급하게 움직이기보다 충분히 따져 본 뒤 움직입니다. 믿음직하고 꾸준합니다.",
    career: "공공, 관리, 전문직처럼 원칙과 신뢰가 중요한 자리에서 오래 인정받습니다.",
    love: "천천히 마음을 열지만 한 번 맺은 인연은 오래 지킵니다.",
  },
  intellect: {
    label: "학습력과 지혜", short: "지혜",
    trait: "배우는 속도가 빠르고 생각이 깊습니다. 문제를 구조적으로 이해하는 힘이 있습니다.",
    career: "연구, 기획, 컨설팅, 교육, 전문 자격이 필요한 분야와 잘 맞습니다.",
    love: "대화가 통하는 사람에게 끌립니다. 머리로만 판단하지 말고 마음도 들어 보세요.",
  },
  sociability: {
    label: "인복과 대인관계", short: "인복",
    trait: "주변에 사람이 모이고, 도움을 주고받는 인연이 많습니다.",
    career: "서비스, 영업, 네트워크, 커뮤니티처럼 사람을 통해 기회가 오는 일에서 운이 열립니다.",
    love: "인연이 자연스럽게 찾아오는 편입니다. 모두에게 친절한 만큼 한 사람에게 집중하는 모습도 보여 주세요.",
  },
  willpower: {
    label: "끈기와 의지", short: "의지",
    trait: "한 번 정한 목표는 끝까지 가는 힘이 있습니다. 위기에서 오히려 강해집니다.",
    career: "장기 프로젝트, 기술직, 운동, 사업처럼 시간이 쌓일수록 결과가 커지는 일에 맞습니다.",
    love: "책임감 있는 연애를 합니다. 고집보다는 유연함을 보여 줄 때 관계가 편안해집니다.",
  },
  independence: {
    label: "독립심과 자존감", short: "독립심",
    trait: "남에게 기대기보다 스스로 해내는 것을 좋아합니다. 자기 기준이 분명합니다.",
    career: "프리랜서, 1인 사업, 전문가처럼 재량이 큰 환경에서 실력이 발휘됩니다.",
    love: "서로의 공간을 존중하는 관계가 잘 맞습니다. 가끔은 기대는 모습도 매력이 됩니다.",
  },
};

export const THEME_KEYS = Object.keys(THEMES) as ThemeKey[];

// 십신 → 테마 기여도
const TEN_GOD_THEME: Record<string, Partial<Record<ThemeKey, number>>> = {
  비견: { independence: 1, willpower: 0.5 },
  겁재: { independence: 0.7, leadership: 0.5, willpower: 0.5 },
  식신: { expression: 0.7, sociability: 0.5, stability: 0.3 },
  상관: { expression: 1, sensitivity: 0.5 },
  편재: { wealth: 1, sociability: 0.5 },
  정재: { wealth: 0.8, stability: 0.6 },
  편관: { leadership: 0.8, willpower: 0.8 },
  정관: { stability: 0.8, leadership: 0.4 },
  편인: { intellect: 0.7, sensitivity: 0.7 },
  정인: { intellect: 1, stability: 0.3 },
};
const ELEMENT_THEME: Record<Element, ThemeKey> = {
  화: "expression", 수: "intellect", 토: "stability", 금: "willpower", 목: "sociability",
};

export function sajuThemes(s: SajuConsensus): { score: Record<ThemeKey, number>; reasons: Record<ThemeKey, string[]> } {
  const raw = Object.fromEntries(THEME_KEYS.map((k) => [k, 0])) as Record<ThemeKey, number>;
  const reasons = Object.fromEntries(THEME_KEYS.map((k) => [k, [] as string[]])) as Record<ThemeKey, string[]>;

  for (const [god, n] of Object.entries(s.tenGodCounts)) {
    const map = TEN_GOD_THEME[god];
    if (!map) continue;
    for (const [k, w] of Object.entries(map) as [ThemeKey, number][]) {
      raw[k] += w * n;
      if (w >= 0.7) reasons[k].push(`${god} ${n}개`);
    }
  }
  for (const [e, n] of Object.entries(s.fiveElements) as [Element, number][]) {
    if (n >= 3) {
      raw[ELEMENT_THEME[e]] += 0.5;
      reasons[ELEMENT_THEME[e]].push(`${e} 기운 ${n}개로 강함`);
    }
  }
  if (s.strength === "strong") {
    raw.independence += 0.5;
    raw.willpower += 0.3;
    reasons.independence.push("신강한 일간");
  } else if (s.strength === "weak") {
    raw.sensitivity += 0.5;
    raw.sociability += 0.3;
    reasons.sensitivity.push("신약한 일간");
  }
  const score = Object.fromEntries(
    THEME_KEYS.map((k) => [k, Math.max(0, Math.min(1, 0.3 + raw[k] * 0.22))]),
  ) as Record<ThemeKey, number>;
  return { score, reasons };
}
