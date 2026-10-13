// 사주(두 엔진 합의) + 관상 결과로 '우리 의견'을 만든다. (API 키가 없어도 동작하는 규칙 기반 해석)
import { ELEMENTS, type Element } from "../saju/constants";
import type { SajuConsensus } from "../saju/types";
import type { FeatureScores, FeatureReading } from "../face/physiognomy";
import { faceThemes } from "../face/physiognomy";
import { THEMES, THEME_KEYS, sajuThemes, type ThemeKey } from "./themes";
import type { CommonTheme, Reading, Section } from "./types";

const DAY_MASTER: Record<string, string> = {
  甲: "당신은 곧게 뻗는 큰 나무 같은 사람입니다. 바르고 곧은 성품에 위로 성장하려는 욕구가 강합니다.",
  乙: "당신은 덩굴과 꽃 같은 사람입니다. 부드럽지만 질기고, 어떤 환경에도 적응하는 생명력이 있습니다.",
  丙: "당신은 하늘의 태양 같은 사람입니다. 밝고 화끈하며 주변을 환하게 비추는 존재감이 있습니다.",
  丁: "당신은 촛불과 등불 같은 사람입니다. 따뜻하고 섬세하며, 한 곳을 오래 밝히는 집중력이 있습니다.",
  戊: "당신은 큰 산 같은 사람입니다. 묵직하고 믿음직하며, 사람들이 기댈 수 있는 중심이 됩니다.",
  己: "당신은 기름진 논밭 같은 사람입니다. 포용력이 있고 사람과 일을 길러 내는 능력이 있습니다.",
  庚: "당신은 단단한 바위와 무쇠 같은 사람입니다. 결단력과 의리가 있고, 맺고 끊음이 분명합니다.",
  辛: "당신은 빛나는 보석 같은 사람입니다. 예리한 감각과 자존심, 완벽을 추구하는 기질이 있습니다.",
  壬: "당신은 큰 바다와 강 같은 사람입니다. 스케일이 크고 지혜로우며, 막히면 돌아가는 유연함이 있습니다.",
  癸: "당신은 비와 이슬 같은 사람입니다. 조용하지만 깊이 스며드는 힘, 뛰어난 직관과 기획력이 있습니다.",
};

const HEADLINE: Record<ThemeKey, string> = {
  leadership: "앞에 서야 빛나는 사람",
  wealth: "흐름을 읽고 재물을 모으는 사람",
  expression: "말과 표현으로 세상을 움직이는 사람",
  sensitivity: "남들이 못 보는 것을 보는 사람",
  stability: "시간이 지날수록 단단해지는 사람",
  intellect: "깊이 생각하고 멀리 보는 사람",
  sociability: "사람이 곧 복인 사람",
  willpower: "끝까지 가는 사람",
  independence: "스스로 길을 만드는 사람",
};

const YEAR_TEXT: Record<string, string> = {
  비견: "나와 비슷한 사람들이 모여드는 해입니다. 독립과 자기 주도의 기회가 오지만, 동업과 보증은 신중하세요.",
  겁재: "경쟁이 뜨거워지는 해입니다. 과감한 도전이 성과로 이어질 수 있지만, 돈이 새어 나가지 않게 지갑을 단단히 하세요.",
  식신: "재능이 꽃피고 생활이 넉넉해지는 해입니다. 새로운 취미나 창작을 시작하기 좋습니다.",
  상관: "표현하고 바꾸고 싶은 마음이 커지는 해입니다. 이직·전환의 기회가 있지만 말실수와 윗사람과의 마찰을 조심하세요.",
  편재: "큰 돈의 흐름이 보이는 해입니다. 사업·투자 기회가 오지만 무리한 확장은 피하세요.",
  정재: "꾸준한 수입과 안정이 찾아오는 해입니다. 저축과 자산 정리에 좋은 시기입니다.",
  편관: "책임과 압박이 커지는 시험대의 해입니다. 버텨 내면 한 단계 올라서지만, 과로와 건강 관리가 우선입니다.",
  정관: "인정과 명예가 따르는 해입니다. 승진·합격·계약·결혼처럼 공식적인 좋은 일이 생기기 쉽습니다.",
  편인: "공부와 자기 성찰의 해입니다. 자격증·전문성에 투자하기 좋지만, 생각만 많아지지 않게 실행을 챙기세요.",
  정인: "귀인의 도움과 문서운이 따르는 해입니다. 배움과 계약, 집과 관련된 일에 좋은 흐름입니다.",
};

const DAEUN_TEXT: Record<string, string> = {
  비견: "자립의 10년", 겁재: "경쟁과 도전의 10년", 식신: "재능과 여유의 10년", 상관: "변화와 표현의 10년",
  편재: "기회와 확장의 10년", 정재: "축적과 안정의 10년", 편관: "시련 속 성장의 10년", 정관: "명예와 인정의 10년",
  편인: "탐구와 전환의 10년", 정인: "배움과 귀인의 10년",
};

const HEALTH: Record<Element, string> = {
  목: "간·눈·근육과 관절",
  화: "심장·혈압·혈액순환",
  토: "위장과 소화 기능",
  금: "폐·호흡기·피부",
  수: "신장·방광, 몸의 냉기",
};

const BOOST: Record<Element, string> = {
  목: "초록색 소품, 아침 산책, 식물 기르기",
  화: "따뜻한 색감, 햇볕 쬐기, 땀 흘리는 운동",
  토: "베이지·노란 계열, 규칙적인 식사, 흙을 밟는 시간",
  금: "흰색·메탈 소품, 공간 정리정돈, 호흡 운동",
  수: "검정·남색 계열, 물 자주 마시기, 충분한 수면",
};

const FEATURE_PART: Record<keyof FeatureScores, string> = {
  forehead: "이마", eyes: "눈", eyeGap: "눈 사이", eyeTilt: "눈꼬리", nose: "코", mouth: "입", lips: "입술",
  smile: "입꼬리", jaw: "턱", cheek: "광대", chin: "턱끝", upper: "상정", middle: "중정", lower: "하관",
};
const THEME_FEATURES: Record<ThemeKey, (keyof FeatureScores)[]> = {
  intellect: ["forehead"],
  sensitivity: ["eyes"],
  expression: ["mouth", "eyes", "lips"],
  sociability: ["eyeGap", "smile", "lips"],
  wealth: ["nose"],
  leadership: ["cheek", "eyeTilt"],
  willpower: ["jaw", "chin", "nose"],
  stability: ["jaw", "lower"],
  independence: ["cheek", "eyeTilt"],
};

/** 사주와 관상에서 '같이' 높게 나온 테마만 고른다 */
export function findCommon(saju: SajuConsensus, features: FeatureScores | null, readings: FeatureReading[]): CommonTheme[] {
  const s = sajuThemes(saju);
  const f = features ? faceThemes(features) : null;
  const obs = (part: string) => readings.find((r) => r.part === part)?.observation;

  const rows = THEME_KEYS.map((k) => {
    const faceScore = f ? f[k] : s.score[k];
    const feats = features
      ? THEME_FEATURES[k].filter((x) => features[x] >= 0.55).map((x) => obs(FEATURE_PART[x]) ?? FEATURE_PART[x])
      : [];
    return {
      key: k,
      label: THEMES[k].label,
      saju: s.score[k],
      face: faceScore,
      sajuReason: s.reasons[k].length ? s.reasons[k].slice(0, 2).join(", ") : "원국 전반에 고르게 깔림",
      faceReason: feats.length ? feats.slice(0, 2).join(", ") : "얼굴 전체의 균형에서 드러남",
      strong: s.score[k] >= 0.55 && faceScore >= 0.55,
    } satisfies CommonTheme;
  }).sort((a, b) => Math.min(b.saju, b.face) - Math.min(a.saju, a.face) || b.saju + b.face - (a.saju + a.face));

  const strong = rows.filter((r) => r.strong);
  return strong.length >= 3 ? strong.slice(0, 4) : rows.slice(0, 3);
}

const josa = (word: string, withBatchim: string, without: string) => {
  const c = word.charCodeAt(word.length - 1);
  if (c < 0xac00 || c > 0xd7a3) return word + without;
  return word + ((c - 0xac00) % 28 ? withBatchim : without);
};

export function composeReading(saju: SajuConsensus, common: CommonTheme[], hasFace: boolean, gender: "남" | "여"): Reading {
  const top = common[0];
  const both = hasFace ? "사주와 관상이 동시에" : "사주가";
  const labels = common.map((c) => THEMES[c.key].short);

  const fe = saju.fiveElements;
  const maxN = Math.max(...ELEMENTS.map((e) => fe[e]));
  const strongEls = ELEMENTS.filter((e) => fe[e] >= 3 && fe[e] === maxN);
  const missing = ELEMENTS.filter((e) => fe[e] === 0);

  const sections: Section[] = [];

  sections.push({
    id: "personality",
    eyebrow: "01",
    title: "성격 · 강점",
    body: [
      DAY_MASTER[saju.dayMaster.stem],
      ...common.slice(0, 3).map((c) => `${THEMES[c.key].trait}${hasFace && c.faceReason !== "얼굴 전체의 균형에서 드러남" ? ` 관상에서도 ${c.faceReason}에 이 기질이 보여요.` : ""}`),
    ],
  });

  const wealthCount = (saju.tenGodCounts["편재"] ?? 0) + (saju.tenGodCounts["정재"] ?? 0);
  sections.push({
    id: "career",
    eyebrow: "02",
    title: "재물 · 직업",
    body: [
      THEMES[top.key].career,
      common[1] ? THEMES[common[1].key].career : "",
      wealthCount >= 2
        ? "사주에 재물의 별이 뚜렷해 돈을 다루는 감각이 좋습니다. 수입원을 둘 이상으로 나누면 재물이 더 안정됩니다."
        : wealthCount === 1
          ? "재물의 별이 적당히 자리 잡고 있어 꾸준히 쌓는 방식이 가장 잘 맞습니다."
          : "사주에 재물의 별이 드러나지 않아 큰돈을 쫓기보다 실력과 이름값을 먼저 키우면 재물이 따라오는 구조입니다.",
    ].filter(Boolean),
  });

  const spouseStar = gender === "남" ? ["편재", "정재"] : ["편관", "정관"];
  const spouseCount = spouseStar.reduce((a, g) => a + (saju.tenGodCounts[g] ?? 0), 0);
  sections.push({
    id: "love",
    eyebrow: "03",
    title: "연애 · 인간관계",
    body: [
      THEMES[top.key].love,
      common.some((c) => c.key === "sociability")
        ? "사람을 통해 운이 들어오는 구조입니다. 오래된 인연을 소중히 하세요."
        : "넓은 관계보다 깊은 소수의 관계에서 힘을 얻는 편입니다.",
      spouseCount >= 2
        ? "배우자 자리의 기운이 여럿 보여 인연의 기회가 많습니다. 선택의 기준을 분명히 하세요."
        : spouseCount === 1
          ? "인연의 별이 하나 또렷하게 자리 잡고 있어, 한 사람과 깊이 가는 연애가 잘 맞습니다."
          : "인연은 서두르지 않을 때 찾아옵니다. 일과 생활이 안정될 때 좋은 사람이 나타나는 흐름입니다.",
    ],
  });

  const healthBody: string[] = [];
  if (strongEls.length) healthBody.push(`${strongEls.join("·")} 기운이 강해 ${strongEls.map((e) => HEALTH[e]).join(", ")} 쪽에 무리가 가지 않도록 리듬을 조절하세요.`);
  if (missing.length) healthBody.push(`${missing.join("·")} 기운이 비어 있어 ${missing.map((e) => HEALTH[e]).join(", ")} 관리가 평소 포인트입니다.`);
  if (!healthBody.length) healthBody.push("오행이 비교적 고르게 분포해 큰 약점은 드러나지 않습니다. 생활 리듬만 지키면 건강운이 무난합니다.");
  healthBody.push("건강 내용은 오락용 참고이며, 몸에 이상이 있다면 반드시 의료 전문가와 상담하세요.");
  sections.push({ id: "health", eyebrow: "04", title: "건강", body: healthBody });

  const future: string[] = [];
  if (saju.currentDaeun) {
    future.push(
      `지금은 ${saju.currentDaeun.startAge}세부터 시작된 ‘${DAEUN_TEXT[saju.currentDaeun.stemTenGod] ?? "흐름이 바뀌는 10년"}’ 속에 있습니다.`,
    );
  }
  for (const y of saju.years) future.push(`${y.year}년 — ${YEAR_TEXT[y.tenGod]}`);
  sections.push({ id: "future", eyebrow: "05", title: "앞으로 다가올 일", body: future });

  const caution: string[] = [];
  if (saju.relations.length)
    caution.push("타고난 기운 중에 서로 부딪치는 것이 있어 이사·이직·관계의 변동이 잦을 수 있습니다. 큰 결정은 한 번 더 점검하세요.");
  const shadows: Partial<Record<ThemeKey, string>> = {
    leadership: "추진력이 강한 만큼 독단으로 보이지 않게 주변 의견을 한 번 더 들으세요.",
    wealth: "돈 냄새를 잘 맡는 만큼 한 번에 크게 거는 투자는 피하세요.",
    expression: "말이 무기인 만큼 말이 화살이 되지 않게 감정적인 순간에는 말을 아끼세요.",
    sensitivity: "예민함이 피로로 쌓이기 쉽습니다. 혼자 정리하는 시간을 꼭 확보하세요.",
    stability: "신중함이 지나치면 기회를 놓칩니다. 70% 확신이면 움직여 보세요.",
    intellect: "생각이 많아 실행이 늦어질 수 있습니다. 작게라도 먼저 시작하세요.",
    sociability: "사람에게 쓰는 에너지와 돈이 새지 않도록 경계를 정하세요.",
    willpower: "고집이 기회를 막지 않도록, 방향이 틀렸다면 빠르게 수정하는 용기도 필요합니다.",
    independence: "혼자 다 짊어지려 하지 마세요. 도움을 청하는 것도 실력입니다.",
  };
  for (const c of common.slice(0, 2)) if (shadows[c.key]) caution.push(shadows[c.key]!);
  const hardYear = saju.years.find((y) => ["편관", "겁재", "상관"].includes(y.tenGod));
  if (hardYear) caution.push(`${hardYear.year}년은 무리하기 쉬운 해입니다. 계약서·건강검진·인간관계를 꼼꼼히 챙기세요.`);
  sections.push({ id: "caution", eyebrow: "06", title: "주의사항", body: caution });

  const advice: string[] = [];
  if (saju.yongsin.length) {
    advice.push(`나를 돕는 기운은 ${saju.yongsin.join("·")}입니다. ${saju.yongsin.map((e) => BOOST[e]).join(" / ")}이 운을 보탭니다.`);
  }
  advice.push(`당신의 무기는 ${labels.join(", ")}입니다. 이 강점을 숨기지 말고 드러내세요.`);
  advice.push("운은 흐름일 뿐, 결정은 당신이 합니다. 좋은 시기엔 과감하게, 조심할 시기엔 차분하게.");

  return {
    headline: HEADLINE[top.key],
    summary: `${both} 말하는 당신의 핵심은 ‘${labels.join(" · ")}’입니다. ${josa(
      THEMES[top.key].label,
      "이",
      "가",
    )} 가장 뚜렷하게 겹쳤습니다.`,
    sections,
    advice,
    source: "rules",
  };
}
