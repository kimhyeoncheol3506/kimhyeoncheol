// 2027 정미년 신년운세: 두 엔진이 합의한 사주(2027년 기준으로 계산)에 기존 규칙 기반 문장 자원을 붙여 리포트를 만든다.
import { BRANCH_ELEMENT, CONTROLS, STEM_ELEMENT, tenGodOf, type Element } from "../saju/constants";
import type { SajuConsensus } from "../saju/types";
import {
  BAD, ELEMENT_TRAIT, GOOD, HEALTH, MONTH_DETAIL, SCORE, YEAR_TEXT, clashes, dayBranchOf, monthItem, monthScore, stars, withItems,
} from "../reading/compose";
import type { Section, SectionItem } from "../reading/types";

export const NEWYEAR = { year: 2027, ganzhi: "丁未", ko: "정미년", animal: "양", color: "붉은" } as const;
/** 2027년 리포트용 기준 시각: 입춘(2/4) 직후라 '2027년 2월~2028년 1월' 열두 달이 나온다 */
export const NEWYEAR_NOW = () => new Date(2027, 1, 15, 12);

export type MonthLine = { label: string; stars: string; theme: string; good: string; bad: string };
export type NewYearReport = {
  createdAt: string;
  name?: string;
  gender: "남" | "여";
  headline: string;
  summary: string;
  overall: string; // ★★★★☆
  keywords: string[];
  free: Section[]; // 무료 요약: 총운
  monthLines: MonthLine[]; // 무료 요약: 달마다 한 줄
  detail: Section[]; // 상세: 월별 상세·재물·연애·직장·건강·조심할 점
  advice: string[];
  source: "rules" | "ai";
};

const YEAR_HEADLINE: Record<string, string> = {
  비견: "내 편이 모여드는 독립의 해",
  겁재: "승부가 붙는 도전의 해",
  식신: "재능이 꽃피는 여유의 해",
  상관: "아이디어가 터지는 변화의 해",
  편재: "기회와 돈이 움직이는 해",
  정재: "차곡차곡 결실을 거두는 해",
  편관: "버티면 한 단계 오르는 해",
  정관: "인정받고 자리 잡는 해",
  편인: "배우고 방향을 다시 잡는 해",
  정인: "귀인이 돕는 문서운의 해",
};

const LOVE_STAR = (g: "남" | "여") => (g === "남" ? ["정재", "편재"] : ["정관", "편관"]);
const WORK_STAR = ["정관", "편관", "정인", "편인"];
const MONEY_STAR = ["정재", "편재", "식신"];
const SAMJAE_NAL = ["亥", "卯", "未"]; // 2027 未년이 '날삼재'인 띠: 돼지·토끼·양
const ANIMAL: Record<string, string> = { 子: "쥐", 丑: "소", 寅: "호랑이", 卯: "토끼", 辰: "용", 巳: "뱀", 午: "말", 未: "양", 申: "원숭이", 酉: "닭", 戌: "개", 亥: "돼지" };

export function composeNewYear(saju: SajuConsensus, gender: "남" | "여", name?: string): NewYearReport {
  const me = name?.trim() ? `${name.trim()}님` : "당신";
  const ds = saju.dayMaster.stem;
  const tg = tenGodOf(ds, "丁"); // 해의 윗글자 (상반기 성격이 강하다고 봄)
  const btg = tenGodOf(ds, "己"); // 未 의 본기 己 (하반기)
  const yearEls: Element[] = [STEM_ELEMENT["丁"], BRANCH_ELEMENT["未"]];
  const helpEl = saju.yongsin.find((e) => yearEls.includes(e));
  const pressEl = !helpEl ? saju.yongsin.find((e) => yearEls.some((y) => CONTROLS[y] === e)) : undefined;
  const yearBranch = saju.pillars.find((p) => p.key === "year" && p.agreed)?.branch ?? "";
  const dayClash = clashes("未", dayBranchOf(saju));
  const ttiClash = yearBranch === "丑";
  const samjae = SAMJAE_NAL.includes(yearBranch);

  const score = 3 + ((SCORE[tg] ?? 0) + (SCORE[btg] ?? 0)) / 2 + (helpEl ? 1 : 0) - (dayClash ? 1 : 0);
  const months = saju.months;
  const ranked = [...months].sort((a, b) => monthScore(saju, b) - monthScore(saju, a));
  const best = ranked.slice(0, 2);
  const worst = [...ranked].reverse().slice(0, 2);

  // ── 총운 (무료) ──
  const total: string[] = [
    `2027년은 ${NEWYEAR.ko}, ${NEWYEAR.color} ${NEWYEAR.animal}의 해입니다. 해의 기운 정화(불)는 ${me}에게 ‘${tg}’에 해당하는 별로, ${YEAR_TEXT[tg]}`,
    `해의 아랫자리인 미토(흙)까지 보면, 한 해 후반으로 갈수록 ${GOOD[btg]} 쪽으로 기운이 옮겨 갑니다. ${btg === tg ? "앞뒤가 같은 결이라 한 해의 흐름이 비교적 일정합니다." : `상반기와 하반기의 결이 달라, 계절이 바뀔 때 계획을 한 번 점검해 보세요.`}`,
  ];
  if (helpEl) total.push(`올해 들어오는 ${ELEMENT_TRAIT[helpEl].name} 기운은 ${me}에게 필요한 ‘나를 돕는 기운’입니다. 새로운 시작에 힘이 붙는 해로 봅니다.`);
  else if (pressEl) total.push(`올해의 불·흙 기운은 ${me}에게 필요한 ${ELEMENT_TRAIT[pressEl].name} 기운을 누르는 편이라, 생활 습관으로 부족한 기운을 따로 채우면 좋습니다.`);
  if (best.length) total.push(`특히 ${best.map((m) => m.label).join("과 ")}이 흐름이 가장 좋은 달이고, ${worst.map((m) => m.label).join("과 ")}은 한 박자 쉬어 가면 좋은 달입니다.`);
  const free: Section[] = [{ id: "ny-total", eyebrow: "01", title: "2027년 총운", body: total }];

  const monthLines: MonthLine[] = months.map((m) => ({
    label: m.label,
    stars: stars(monthScore(saju, m)),
    theme: MONTH_DETAIL[m.tenGod]?.theme ?? "평온한 달",
    good: GOOD[m.tenGod] ?? "",
    bad: BAD[m.tenGod] ?? "",
  }));

  // ── 상세 (잠글 수 있는 부분) ──
  const pick = (stars: string[]) => months.filter((m) => stars.includes(m.tenGod) || stars.includes(m.branchTenGod)).slice(0, 3);
  const monthList = (ms: typeof months) => (ms.length ? ms.map((m) => m.label).join(", ") : "");
  const area = (id: string, title: string, lead: string, half: [string, string], monthsTitle: string, ms: typeof months, extra?: string): Section => {
    const items: SectionItem[] = [
      { label: "상반기 (2~7월)", title: half[0], rows: [] },
      { label: "하반기 (8월~2028년 1월)", title: half[1], rows: [] },
    ];
    if (ms.length) items.push({ label: monthsTitle, title: monthList(ms), rows: [{ k: "이렇게", v: "중요한 일은 이 달들에 맞춰 계획해 보세요" }] });
    return withItems(id, title, extra ? `${lead} ${extra}` : lead, items);
  };
  const D = (k: string) => MONTH_DETAIL[k] ?? MONTH_DETAIL.비견;

  const detail: Section[] = [
    withItems("ny-months", "2027년 월별 상세", "사주의 한 해는 입춘(2월 4일 무렵)부터 시작합니다. 2027년 2월부터 2028년 1월까지 달마다 자세히 풀었습니다.", months.map((m) => monthItem(saju, m))),
    area("ny-money", "재물운", `${me}의 2027년 돈의 흐름입니다.`, [D(tg).money, D(btg).money], "재물 흐름이 좋은 달", pick(MONEY_STAR)),
    area(
      "ny-love",
      "연애·인간관계",
      `${me}의 2027년 사람과 사랑의 흐름입니다.`,
      [D(tg).people, D(btg).people],
      "인연이 들어오기 쉬운 달",
      pick(LOVE_STAR(gender)),
      dayClash ? "배우자 자리가 올해의 기운과 부딪쳐 관계에 변화가 생기기 쉬우니, 중요한 약속은 서두르지 마세요." : "",
    ),
    area("ny-work", "직장·일", `${me}의 2027년 일과 자리의 흐름입니다.`, [D(tg).work, D(btg).work], "승진·이직·시험에 힘이 붙는 달", pick(WORK_STAR)),
    area(
      "ny-health",
      "건강",
      `${me}의 타고난 기운으로 보면 ${HEALTH[saju.dayMaster.element]} 쪽을 꾸준히 챙기면 좋습니다. 건강 풀이는 참고용이며 증상이 있으면 꼭 전문의와 상담하세요.`,
      [D(tg).body, D(btg).body],
      "무리하지 말아야 할 달",
      months.filter((m) => m.tenGod === "편관" || m.tenGod === "겁재").slice(0, 3),
    ),
  ];

  const caution: string[] = [];
  if (samjae)
    caution.push(`전통적으로 ${ANIMAL[yearBranch]}띠는 2027년을 삼재가 끝나는 ‘날삼재’로 봅니다. 겁먹을 일은 아니고, 지난 2년간 벌인 일을 차분히 마무리하라는 정도로 받아들이면 충분합니다.`);
  if (ttiClash) caution.push("소띠는 양의 해와 띠가 부딪치는 자리라 이사·이직처럼 환경이 바뀌는 일이 생기기 쉽다고 봅니다. 큰 결정은 한 번 더 따져 보세요.");
  if (dayClash) caution.push("배우자 자리가 올해의 기운과 부딪쳐, 가까운 관계에서 오해가 생기기 쉽습니다. 서운한 일은 그날 안에 짧게 말하세요.");
  caution.push(`올해 가장 조심할 일은 ‘${BAD[tg]}’입니다.`);
  if (worst.length) caution.push(`${worst.map((m) => m.label).join("과 ")}에는 큰 계약·투자·감정적인 결정을 미루세요.`);
  detail.push({ id: "ny-caution", eyebrow: "", title: "2027년 조심할 점", body: caution });
  detail.forEach((s, i) => (s.eyebrow = String(i + 2).padStart(2, "0")));

  const advice = [
    `2027년의 열쇠는 ‘${GOOD[tg]}’입니다. 연초에 이 방향으로 작은 계획 하나를 세워 보세요.`,
    best[0] ? `${best[0].label}은 한 해 중 기운이 가장 좋은 달입니다. 미뤄 둔 중요한 일을 이때 꺼내세요.` : "좋은 달에 씨앗을 뿌리고, 조심할 달에는 뿌리를 다지세요.",
    "운은 흐름일 뿐, 결정은 당신이 합니다. 이 리포트는 재미와 참고용으로 봐 주세요.",
  ];

  return {
    createdAt: new Date().toISOString(),
    name: name?.trim() || undefined,
    gender,
    headline: YEAR_HEADLINE[tg] ?? "흐름을 타는 해",
    summary: `${me}의 2027년은 ‘${YEAR_HEADLINE[tg]}’입니다. ${GOOD[tg]}에 힘을 싣고, ${BAD[tg]}은 조심하세요.`,
    overall: stars(score),
    keywords: [YEAR_HEADLINE[tg], best[0] ? `최고의 달 ${best[0].label.replace("2027년 ", "")}` : "", helpEl ? "나를 돕는 기운이 들어오는 해" : ""].filter(Boolean),
    free,
    monthLines,
    detail,
    advice,
    source: "rules",
  };
}
