// 사주 계산에 공통으로 쓰는 기본 표 (천간·지지·오행·십신)
// 이 표는 전통 명리학의 공개 지식이며, 특정 프로그램의 코드를 복사한 것이 아닙니다.

export const STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"] as const;
export const BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"] as const;

export const STEM_KO: Record<string, string> = {
  甲: "갑", 乙: "을", 丙: "병", 丁: "정", 戊: "무", 己: "기", 庚: "경", 辛: "신", 壬: "임", 癸: "계",
};
export const BRANCH_KO: Record<string, string> = {
  子: "자", 丑: "축", 寅: "인", 卯: "묘", 辰: "진", 巳: "사", 午: "오", 未: "미", 申: "신", 酉: "유", 戌: "술", 亥: "해",
};

export type Element = "목" | "화" | "토" | "금" | "수";
export const ELEMENTS: Element[] = ["목", "화", "토", "금", "수"];

export const STEM_ELEMENT: Record<string, Element> = {
  甲: "목", 乙: "목", 丙: "화", 丁: "화", 戊: "토", 己: "토", 庚: "금", 辛: "금", 壬: "수", 癸: "수",
};
export const BRANCH_ELEMENT: Record<string, Element> = {
  子: "수", 丑: "토", 寅: "목", 卯: "목", 辰: "토", 巳: "화", 午: "화", 未: "토", 申: "금", 酉: "금", 戌: "토", 亥: "수",
};
/** 지지의 정기(본기) — 지지 십신을 정할 때 사용 */
export const BRANCH_MAIN_STEM: Record<string, string> = {
  子: "癸", 丑: "己", 寅: "甲", 卯: "乙", 辰: "戊", 巳: "丙", 午: "丁", 未: "己", 申: "庚", 酉: "辛", 戌: "戊", 亥: "壬",
};

/** 상생: key가 생(生)하는 오행 */
export const GENERATES: Record<Element, Element> = { 목: "화", 화: "토", 토: "금", 금: "수", 수: "목" };
/** 상극: key가 극(剋)하는 오행 */
export const CONTROLS: Record<Element, Element> = { 목: "토", 토: "수", 수: "화", 화: "금", 금: "목" };

export const isYangStem = (s: string) => STEMS.indexOf(s as (typeof STEMS)[number]) % 2 === 0;

export type TenGod =
  | "비견" | "겁재" | "식신" | "상관" | "편재" | "정재" | "편관" | "정관" | "편인" | "정인";

/** 일간 기준으로 다른 천간의 십신을 구한다 */
export function tenGodOf(dayStem: string, other: string): TenGod {
  const me = STEM_ELEMENT[dayStem];
  const it = STEM_ELEMENT[other];
  const same = isYangStem(dayStem) === isYangStem(other);
  if (me === it) return same ? "비견" : "겁재";
  if (GENERATES[me] === it) return same ? "식신" : "상관";
  if (CONTROLS[me] === it) return same ? "편재" : "정재";
  if (CONTROLS[it] === me) return same ? "편관" : "정관";
  return same ? "편인" : "정인"; // it 이 나를 생함
}

export const ELEMENT_COLOR_NAME: Record<Element, string> = {
  목: "나무", 화: "불", 토: "흙", 금: "쇠", 수: "물",
};
