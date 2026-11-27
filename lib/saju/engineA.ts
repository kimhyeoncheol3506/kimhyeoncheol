// 엔진 A: ssaju (golbin/ssaju, MIT License)
import { calculateSaju, type SajuResult } from "ssaju";
import { STEM_ELEMENT, type Element } from "./constants";
import type { BirthInput, EngineOutput, PillarKey } from "./types";

export function runEngineA(input: BirthInput, now?: Date): { out: EngineOutput; raw: SajuResult } {
  const raw = calculateSaju({
    year: input.year,
    month: input.month,
    day: input.day,
    hour: input.hour ?? 12,
    minute: input.hour == null ? 0 : input.minute,
    gender: input.gender,
    calendar: input.calendar,
    leap: input.leap,
    timezone: "Asia/Seoul",
    ...(now ? { now } : {}),
  });

  const keys: PillarKey[] = ["year", "month", "day", "hour"];
  const tenGods = {} as EngineOutput["tenGods"];
  for (const k of keys) tenGods[k] = { stem: raw.tenGods[k].stem, branch: raw.tenGods[k].branch };

  const yongsin = Array.from(
    new Set(raw.advanced.yongsin.map((s) => STEM_ELEMENT[s]).filter(Boolean)),
  ) as Element[];

  return {
    raw,
    out: {
      engine: "ssaju",
      pillars: { ...raw.pillars },
      tenGods,
      daeun: {
        startAge: raw.daeun.startAge,
        ganzhi: raw.daeun.list.map((d) => d.ganzhi),
        direction: raw.daeun.basis.direction,
      },
      strength: raw.advanced.dayStrength.strength,
      yongsinElements: yongsin,
    },
  };
}
