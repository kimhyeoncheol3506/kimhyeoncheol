// 두 엔진을 동시에 돌리고, "둘이 같은 값을 낸 부분"만 채택한다.
import { runEngineA } from "./engineA";
import { runEngineB } from "./engineB";
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
    years,
    relations,
    agreement: { total, agreed, notes },
    age: raw.currentAge,
  };
}
