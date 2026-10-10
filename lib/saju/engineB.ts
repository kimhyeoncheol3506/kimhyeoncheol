// 엔진 B: lunar-javascript (6tail, MIT License) 의 만세력 + 이 프로젝트가 직접 구현한 신강/용신 규칙.
// orrery(AGPL)의 코드는 복사하지 않았습니다. 독립 구현으로 교차 검증만 합니다.
import { Lunar, Solar } from "lunar-javascript";
import {
  BRANCH_ELEMENT,
  CONTROLS,
  ELEMENTS,
  GENERATES,
  STEM_ELEMENT,
  type Element,
} from "./constants";
import type { BirthInput, EngineOutput, PillarKey } from "./types";

const CN_TEN_GOD: Record<string, string> = {
  比肩: "비견", 劫财: "겁재", 食神: "식신", 伤官: "상관", 偏财: "편재",
  正财: "정재", 七杀: "편관", 正官: "정관", 偏印: "편인", 正印: "정인", 日主: "(일간)",
};
const ko = (s: string) => CN_TEN_GOD[s] ?? s;

/** 이 프로젝트 고유의 신강·신약 판정: 월령 가중치를 둔 단순 점수제 */
export function judgeStrength(pillars: Record<PillarKey, string>, includeHour: boolean) {
  const me = STEM_ELEMENT[pillars.day[0]];
  const mother = (Object.keys(GENERATES) as Element[]).find((e) => GENERATES[e] === me)!;
  const helps = (e: Element) => e === me || e === mother;

  const items: [Element, number][] = [
    [STEM_ELEMENT[pillars.year[0]], 1],
    [BRANCH_ELEMENT[pillars.year[1]], 1],
    [STEM_ELEMENT[pillars.month[0]], 1],
    [BRANCH_ELEMENT[pillars.month[1]], 3], // 월령
    [BRANCH_ELEMENT[pillars.day[1]], 1.5],
  ];
  if (includeHour) {
    items.push([STEM_ELEMENT[pillars.hour[0]], 1], [BRANCH_ELEMENT[pillars.hour[1]], 1]);
  }
  const total = items.reduce((a, [, w]) => a + w, 0);
  const support = items.reduce((a, [e, w]) => a + (helps(e) ? w : 0), 0);
  const ratio = support / total;
  const strength: EngineOutput["strength"] = ratio >= 0.55 ? "strong" : ratio <= 0.42 ? "weak" : "neutral";

  // 용신 후보: 신강이면 설기·재·관, 신약이면 인성·비겁, 중화면 가장 부족한 오행
  let yongsin: Element[];
  if (strength === "strong") {
    yongsin = [GENERATES[me], CONTROLS[me], (Object.keys(CONTROLS) as Element[]).find((e) => CONTROLS[e] === me)!];
  } else if (strength === "weak") {
    yongsin = [mother, me];
  } else {
    const count = Object.fromEntries(ELEMENTS.map((e) => [e, 0])) as Record<Element, number>;
    for (const [e, w] of items) count[e] += w;
    const min = Math.min(...ELEMENTS.map((e) => count[e]));
    yongsin = ELEMENTS.filter((e) => count[e] === min);
  }
  return { strength, yongsin, ratio };
}

export function runEngineB(input: BirthInput): EngineOutput {
  const hour = input.hour ?? 12;
  const minute = input.hour == null ? 0 : input.minute;
  const solar =
    input.calendar === "lunar"
      ? Lunar.fromYmdHms(input.year, input.leap ? -input.month : input.month, input.day, hour, minute, 0).getSolar()
      : Solar.fromYmdHms(input.year, input.month, input.day, hour, minute, 0);
  const ec = solar.getLunar().getEightChar();

  const pillars: Record<PillarKey, string> = {
    year: ec.getYear(),
    month: ec.getMonth(),
    day: ec.getDay(),
    hour: ec.getTime(),
  };
  const tenGods: EngineOutput["tenGods"] = {
    year: { stem: ko(ec.getYearShiShenGan()), branch: ko(ec.getYearShiShenZhi()[0]) },
    month: { stem: ko(ec.getMonthShiShenGan()), branch: ko(ec.getMonthShiShenZhi()[0]) },
    day: { stem: "(일간)", branch: ko(ec.getDayShiShenZhi()[0]) },
    hour: { stem: ko(ec.getTimeShiShenGan()), branch: ko(ec.getTimeShiShenZhi()[0]) },
  };

  const yun = ec.getYun(input.gender === "남" ? 1 : 0);
  const list = yun.getDaYun().filter((d: { getGanZhi: () => string }) => d.getGanZhi());
  // lunar-javascript 는 세는나이(虛歲)를 쓰므로 만 나이로 1 낮춘다
  const startAge = list.length ? list[0].getStartAge() - 1 : 0;

  const { strength, yongsin } = judgeStrength(pillars, input.hour != null);

  return {
    engine: "lunar-javascript + 자체 규칙",
    pillars,
    tenGods,
    daeun: {
      startAge,
      ganzhi: list.map((d: { getGanZhi: () => string }) => d.getGanZhi()),
      direction: yun.isForward() ? "forward" : "backward",
    },
    strength,
    yongsinElements: yongsin,
  };
}
