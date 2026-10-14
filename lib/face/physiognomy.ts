// 전통 관상학 규칙을 얼굴 비율에 매핑한다.
// 기준값(BASE)은 MediaPipe '표준 얼굴 모델'(canonical face model)에서 직접 잰 평균 비율이다.
import type { FaceMetrics } from "./measure";
import type { ThemeKey } from "../reading/themes";

export const BASE: FaceMetrics = {
  upper: 0.1911, middle: 0.3948, lower: 0.4141, foreheadWidth: 0.6698, eyeSize: 0.169, eyeOpen: 0.2586,
  eyeGap: 1.4332, eyeTilt: 1.7419, noseWidth: 0.2078, noseLength: 0.3034, mouthWidth: 0.3205,
  lipThickness: 0.1109, mouthCurve: -0.0042, jawWidth: 0.7751, cheekbone: 1.3842, chinLength: 0.2286,
};

const clamp = (v: number) => Math.max(0, Math.min(1, v));
/** 기준 대비 얼마나 큰지 0~1 점수 (0.5 = 평균) */
const rel = (v: number, base: number, gain = 2.2) => clamp(0.5 + (v / base - 1) * gain);

export type FeatureScores = Record<
  "forehead" | "eyes" | "eyeGap" | "eyeTilt" | "nose" | "mouth" | "lips" | "smile" | "jaw" | "cheek" | "chin" | "upper" | "middle" | "lower",
  number
>;

export function scoreFeatures(m: FaceMetrics): FeatureScores {
  return {
    forehead: clamp((rel(m.upper, BASE.upper, 1.6) + rel(m.foreheadWidth, BASE.foreheadWidth, 2.5)) / 2),
    eyes: clamp((rel(m.eyeSize, BASE.eyeSize) + rel(m.eyeOpen, BASE.eyeOpen, 1.4)) / 2),
    eyeGap: rel(m.eyeGap, BASE.eyeGap, 2),
    eyeTilt: clamp(0.5 + (m.eyeTilt - BASE.eyeTilt) / 10),
    nose: clamp((rel(m.noseWidth, BASE.noseWidth) + rel(m.noseLength, BASE.noseLength, 1.8)) / 2),
    mouth: rel(m.mouthWidth, BASE.mouthWidth),
    lips: rel(m.lipThickness, BASE.lipThickness, 1.5),
    smile: clamp(0.5 + (m.mouthCurve - BASE.mouthCurve) / 0.03),
    jaw: rel(m.jawWidth, BASE.jawWidth, 3),
    cheek: rel(m.cheekbone, BASE.cheekbone, 3),
    chin: rel(m.chinLength, BASE.chinLength, 1.8),
    upper: rel(m.upper, BASE.upper, 1.6),
    middle: rel(m.middle, BASE.middle, 2),
    lower: rel(m.lower, BASE.lower, 2),
  };
}

/** 부위별 관상 풀이 (전통 관상학의 일반적인 해석) */
export type FeatureReading = { part: string; observation: string; meaning: string };

const pick = (s: number, hi: string, mid: string, lo: string) => (s >= 0.6 ? hi : s <= 0.4 ? lo : mid);

export function readFeatures(f: FeatureScores): FeatureReading[] {
  return [
    {
      part: "이마",
      observation: pick(f.forehead, "넓고 시원한 이마", "균형 잡힌 이마", "아담하고 단정한 이마"),
      meaning: pick(
        f.forehead,
        "관상에서 이마는 초년운과 사고력을 봅니다. 생각의 폭이 넓고 배움이 빠른 상입니다.",
        "초년운이 무난하고 현실 감각과 사고력이 고르게 발달한 상입니다.",
        "스스로 길을 개척해 나가는 상으로, 경험을 통해 단단해지는 실전형입니다.",
      ),
    },
    {
      part: "눈",
      observation: pick(f.eyes, "크고 맑은 눈", "또렷한 눈", "가늘고 깊은 눈"),
      meaning: pick(
        f.eyes,
        "눈은 마음의 창입니다. 감수성이 풍부하고 감정 표현이 솔직한 상입니다.",
        "감정과 이성의 균형이 좋아 사람을 편안하게 하는 상입니다.",
        "속마음을 쉽게 드러내지 않고, 관찰력과 집중력이 뛰어난 상입니다.",
      ),
    },
    {
      part: "눈 사이",
      observation: pick(f.eyeGap, "넉넉한 미간", "적당한 미간", "가까운 미간"),
      meaning: pick(
        f.eyeGap,
        "마음이 너그럽고 포용력이 있어 사람이 모이는 상입니다.",
        "판단이 균형 잡혀 있어 대인관계가 안정적인 상입니다.",
        "한 가지에 몰입하는 힘이 강하고 꼼꼼한 상입니다.",
      ),
    },
    {
      part: "눈꼬리",
      observation: pick(f.eyeTilt, "살짝 올라간 눈꼬리", "수평에 가까운 눈꼬리", "부드럽게 내려간 눈꼬리"),
      meaning: pick(
        f.eyeTilt,
        "목표 의식과 승부욕이 강해 앞에 나서는 일이 잘 맞는 상입니다.",
        "차분하고 공정한 시선을 지닌 상입니다.",
        "온화하고 다정해 사람들에게 호감을 얻는 상입니다.",
      ),
    },
    {
      part: "코",
      observation: pick(f.nose, "콧방울이 듬직한 코", "반듯한 코", "날렵하고 오똑한 코"),
      meaning: pick(
        f.nose,
        "코는 재물궁입니다. 재물을 모으고 지키는 힘이 좋은 상입니다.",
        "재물운이 안정적이고 자존감이 건강한 상입니다.",
        "감각이 예리하고 자기 기준이 분명하며, 씀씀이 관리가 재물의 열쇠인 상입니다.",
      ),
    },
    {
      part: "입",
      observation: pick(f.mouth, "시원하게 큰 입", "균형 잡힌 입", "작고 단정한 입"),
      meaning: pick(
        f.mouth,
        "입은 말복과 식복을 봅니다. 표현력이 좋고 사람을 끄는 말솜씨가 있는 상입니다.",
        "말에 신뢰가 있어 인간관계가 무난한 상입니다.",
        "말을 아끼고 신중하며, 한 번 한 약속은 지키는 상입니다.",
      ),
    },
    {
      part: "입꼬리",
      observation: pick(f.smile, "올라간 입꼬리", "편안한 입꼬리", "단단히 다문 입꼬리"),
      meaning: pick(
        f.smile,
        "긍정적이고 밝은 기운으로 인복을 부르는 상입니다.",
        "감정 기복이 적고 안정감을 주는 상입니다.",
        "책임감이 강하고 진지한 상입니다. 자주 웃으면 복이 더 들어옵니다.",
      ),
    },
    {
      part: "광대",
      observation: pick(f.cheek, "또렷한 광대", "부드러운 광대", "평평한 광대"),
      meaning: pick(
        f.cheek,
        "광대는 사회적 힘과 명예를 봅니다. 추진력과 리더십이 드러나는 상입니다.",
        "사회성과 협동심이 조화로운 상입니다.",
        "앞에 나서기보다 뒤에서 조율하는 참모형의 상입니다.",
      ),
    },
    {
      part: "턱",
      observation: pick(f.jaw, "넓고 단단한 턱", "균형 잡힌 턱선", "갸름한 턱선"),
      meaning: pick(
        f.jaw,
        "턱은 말년운과 의지를 봅니다. 끈기가 있고 말년이 든든한 상입니다.",
        "꾸준함이 있어 시간이 갈수록 안정되는 상입니다.",
        "감각적이고 섬세한 상으로, 체력과 기반을 꾸준히 다지면 말년이 편안합니다.",
      ),
    },
    {
      part: "입술",
      observation: pick(f.lips, "도톰한 입술", "적당한 두께의 입술", "얇고 단정한 입술"),
      meaning: pick(
        f.lips,
        "정이 많고 베푸는 상입니다. 먹을 복과 사람 복이 함께 따릅니다.",
        "감정과 이성이 균형을 이뤄 말에 신뢰가 실리는 상입니다.",
        "말이 정확하고 냉철한 상입니다. 판단력이 좋아 실수가 적습니다.",
      ),
    },
    {
      part: "턱끝",
      observation: pick(f.chin, "길고 또렷한 턱끝", "균형 잡힌 턱끝", "짧고 동그란 턱끝"),
      meaning: pick(
        f.chin,
        "턱끝은 아랫사람과 집안의 복을 봅니다. 따르는 사람이 많고 노년에 집안이 든든한 상입니다.",
        "가정운이 무난하고 주변과의 관계가 안정된 상입니다.",
        "친근하고 귀여운 인상으로 사람들이 편하게 다가오는 상입니다.",
      ),
    },
    {
      part: "얼굴 삼등분",
      observation:
        f.upper >= Math.max(f.middle, f.lower)
          ? "이마 쪽(상정)이 가장 넓은 얼굴"
          : f.middle >= f.lower
            ? "눈썹~코끝(중정)이 가장 긴 얼굴"
            : "코끝~턱(하정)이 가장 긴 얼굴",
      meaning:
        f.upper >= Math.max(f.middle, f.lower)
          ? "관상에서 상정은 초년(15~30세)을 봅니다. 젊을 때부터 배움과 기회가 따르는 상입니다."
          : f.middle >= f.lower
            ? "관상에서 중정은 중년(31~50세)을 봅니다. 한창 일할 나이에 가장 크게 꽃피는 상입니다."
            : "관상에서 하정은 말년(51세 이후)을 봅니다. 시간이 갈수록 복이 쌓여 노년이 넉넉한 상입니다.",
    },
  ];
}

/** 관상 점수를 공통 테마 점수(0~1)로 변환 */
export function faceThemes(f: FeatureScores): Record<ThemeKey, number> {
  const avg = (...v: number[]) => clamp(v.reduce((a, b) => a + b, 0) / v.length);
  return {
    intellect: avg(f.forehead, f.forehead, f.upper),
    sensitivity: avg(f.eyes, f.eyes, 1 - f.jaw),
    expression: avg(f.mouth, f.mouth, f.eyes, f.lips),
    sociability: avg(f.eyeGap, f.smile, f.lips),
    wealth: avg(f.nose, f.nose, f.middle),
    leadership: avg(f.cheek, f.cheek, f.eyeTilt),
    willpower: avg(f.jaw, f.jaw, f.chin, f.nose),
    stability: avg(f.lower, f.jaw, 1 - f.eyes),
    independence: avg(f.cheek, f.eyeTilt, 1 - f.eyeGap),
  };
}
