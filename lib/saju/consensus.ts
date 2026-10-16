// 두 엔진을 동시에 돌리고, "둘이 같은 값을 낸 부분"만 채택한다.
import { runEngineA } from "./engineA";
import { runEngineB } from "./engineB";
import { Solar } from "lunar-javascript";
import {
  BRANCHES,
  BRANCH_ELEMENT,
  BRANCH_KO,
  BRANCH_MAIN_STEM,
  ELEMENTS,
  STEMS,
  STEM_ELEMENT,
  STEM_KO,
  tenGodOf,
  type Element,
} from "./constants";
import { PILLAR_KEYS, type BirthInput, type PillarView, type SajuConsensus } from "./types";

const yearGanzhi = (y: number) => STEMS[(((y - 4) % 10) + 10) % 10] + BRANCHES[(((y - 4) % 12) + 12) % 12];

export function computeSaju(input: BirthInput, now = new Date()): SajuConsensus {
  const { out: a, raw } = runEngineA(input);
  const b = runEngineB(input);
  const hourKnown = input.hour != null;

  const notes: string[] = [];
  let total = 0;
  let agreed = 0;
  const check = (ok: boolean, note: string) => {
    total++;
    if (ok) agreed++;
    else notes.push(note);
    return ok;
  };

  // 1) 네 기둥
  const pillars: PillarView[] = PILLAR_KEYS.map((k) => {
    const g = a.pillars[k];
    const unknown = k === "hour" && !hourKnown;
    const same = unknown
      ? false
      : check(a.pillars[k] === b.pillars[k], `${k} 기둥: 엔진 간 차이 (${a.pillars[k]} / ${b.pillars[k]})`);
    const tgSame =
      unknown ||
      check(
        a.tenGods[k].stem === b.tenGods[k].stem && a.tenGods[k].branch === b.tenGods[k].branch,
        `${k} 십신: 엔진 간 차이`,
      );
    return {
      key: k,
      ganzhi: g,
      stem: g[0],
      branch: g[1],
      stemKo: STEM_KO[g[0]],
      branchKo: BRANCH_KO[g[1]],
      stemElement: STEM_ELEMENT[g[0]],
      branchElement: BRANCH_ELEMENT[g[1]],
      stemTenGod: a.tenGods[k].stem,
      branchTenGod: a.tenGods[k].branch,
      agreed: !unknown && same && tgSame,
      unknown,
    };
  });

  const used = pillars.filter((p) => p.agreed);
  const dayStem = a.pillars.day[0];

  // 2) 오행 분포 (합의된 기둥만)
  const fiveElements = Object.fromEntries(ELEMENTS.map((e) => [e, 0])) as Record<Element, number>;
  for (const p of used) {
    fiveElements[p.stemElement]++;
    fiveElements[p.branchElement]++;
  }

  // 3) 십신 개수 (일간 제외, 합의된 기둥만)
  const tenGodCounts: Record<string, number> = {};
  for (const p of used) {
    if (p.key !== "day") tenGodCounts[p.stemTenGod] = (tenGodCounts[p.stemTenGod] ?? 0) + 1;
    tenGodCounts[p.branchTenGod] = (tenGodCounts[p.branchTenGod] ?? 0) + 1;
  }

  // 4) 신강/신약 · 용신 — 두 엔진이 같을 때만
  const strengthSame = check(a.strength === b.strength, `신강약 판단: ${a.strength} / ${b.strength}`);
  const strength = strengthSame ? a.strength : "undetermined";
  const yongsin = a.yongsinElements.filter((e) => b.yongsinElements.includes(e));
  check(yongsin.length > 0, "용신: 공통 후보 없음");

  // 5) 대운 — 순행/역행·간지 순서·시작나이(±1년)가 맞을 때만
  const daeunAgreed = check(
    a.daeun.direction === b.daeun.direction &&
      Math.abs(a.daeun.startAge - b.daeun.startAge) <= 1 &&
      a.daeun.ganzhi.slice(0, 8).join() === b.daeun.ganzhi.slice(0, 8).join(),
    "대운: 엔진 간 차이",
  );
  const cur = raw.daeun.current;
  const currentDaeun =
    daeunAgreed && cur
      ? { ganzhi: cur.ganzhi, startAge: cur.startAge, stemTenGod: cur.stemTenGod, branchTenGod: cur.branchTenGod }
      : null;

  const daeunList = daeunAgreed
    ? raw.daeun.list.slice(0, 9).map((d) => ({
        startAge: d.startAge,
        ganzhi: d.ganzhi,
        stemTenGod: d.stemTenGod,
        current: cur ? d.startAge === cur.startAge : false,
      }))
    : [];

  // 6-1) 이번 달부터 12개월 — ssaju 월운(올해·내년)과 lunar-javascript 절기 월주가 같은 달만
  const y0 = now.getFullYear();
  const nextRaw = runEngineA(input, new Date(y0 + 1, 5, 15)).raw;
  const allMonths = [raw, nextRaw].flatMap((r, yi) =>
    r.wolun.slice(0, 12).map((w, i) => {
      const y = y0 + yi + (i === 11 ? 1 : 0);
      const m = i === 11 ? 1 : i + 2;
      let check = "";
      try {
        check = Solar.fromYmdHms(y, m, 20, 12, 0, 0).getLunar().getMonthInGanZhiExact();
      } catch {
        /* 확인 실패 시 제외 */
      }
      return { y, m, w, ok: check === w.ganzhi };
    }),
  );
  let todayMonth = "";
  try {
    todayMonth = Solar.fromYmdHms(y0, now.getMonth() + 1, now.getDate(), 12, 0, 0).getLunar().getMonthInGanZhiExact();
  } catch {
    /* 무시 */
  }
  const startIdx = Math.max(0, allMonths.findIndex((x) => x.w.ganzhi === todayMonth));
  const months = allMonths
    .slice(startIdx, startIdx + 12)
    .filter((x) => x.ok)
    .map((x) => ({
      label: `${x.y}년 ${x.m}월`,
      year: x.y,
      month: x.m,
      ganzhi: x.w.ganzhi,
      tenGod: x.w.stemTenGod,
      branchTenGod: x.w.branchTenGod,
    }));

  // 6-2) 오늘부터 14일 일진 — lunar-javascript 와 율리우스일 공식이 같은 날만
  const dayBranchIdx = BRANCHES.indexOf(a.pillars.day[1] as (typeof BRANCHES)[number]);
  const days = Array.from({ length: 14 }, (_, k) => {
    const d = new Date(now.getFullYear(), now.getMonth(), now.getDate() + k);
    const yy = d.getFullYear(), mm = d.getMonth() + 1, dd = d.getDate();
    const jdn = Math.floor(Date.UTC(yy, mm - 1, dd) / 864e5) + 2440588;
    const idx = (jdn + 49) % 60;
    const formula = STEMS[idx % 10] + BRANCHES[idx % 12];
    let lj = "";
    try {
      lj = Solar.fromYmd(yy, mm, dd).getLunar().getDayInGanZhi();
    } catch {
      /* 무시 */
    }
    if (lj !== formula) return null;
    return {
      date: `${yy}-${String(mm).padStart(2, "0")}-${String(dd).padStart(2, "0")}`,
      weekday: d.getDay(),
      ganzhi: formula,
      tenGod: tenGodOf(dayStem, formula[0]),
      branchTenGod: tenGodOf(dayStem, BRANCH_MAIN_STEM[formula[1]]),
      clash: Math.abs(BRANCHES.indexOf(formula[1] as (typeof BRANCHES)[number]) - dayBranchIdx) === 6,
    };
  }).filter(Boolean) as SajuConsensus["days"];

  // 6) 앞으로 3년 세운 — ssaju 값과 독립 계산값이 같을 때만
  const thisYear = now.getFullYear();
  const years = [thisYear, thisYear + 1, thisYear + 2]
    .map((y) => {
      const g = yearGanzhi(y);
      const fromA = raw.seyun.find((s) => s.year === y)?.ganzhi;
      if (fromA && fromA !== g) return null;
      return {
        year: y,
        ganzhi: g,
        tenGod: tenGodOf(dayStem, g[0]),
        branchTenGod: tenGodOf(dayStem, BRANCH_MAIN_STEM[g[1]]),
      };
    })
    .filter(Boolean) as SajuConsensus["years"];

  // 7) 지지 충 — 직접 계산 + ssaju 결과에 모두 있을 때만
  const relations: string[] = [];
  const aChung = Object.values(raw.branchRelations["충"] ?? {}).join(" ");
  for (let i = 0; i < used.length; i++)
    for (let j = i + 1; j < used.length; j++) {
      const bi = BRANCHES.indexOf(used[i].branch as (typeof BRANCHES)[number]);
      const bj = BRANCHES.indexOf(used[j].branch as (typeof BRANCHES)[number]);
      if (Math.abs(bi - bj) === 6) {
        const pair = used[i].branch + used[j].branch;
        const pairR = used[j].branch + used[i].branch;
        if (aChung.includes(pair) || aChung.includes(pairR)) relations.push(`${used[i].key}-${used[j].key} 충`);
      }
    }

  return {
    pillars,
    dayMaster: { stem: dayStem, ko: STEM_KO[dayStem], element: STEM_ELEMENT[dayStem] },
    fiveElements,
    tenGodCounts,
    strength,
    yongsin,
    currentDaeun,
    daeunAgreed,
    daeunList,
    months,
    days,
    years,
    relations,
    agreement: { total, agreed, notes },
    age: raw.currentAge,
  };
}
