import type { Element, TenGod } from "./constants";

export type PillarKey = "year" | "month" | "day" | "hour";
export const PILLAR_KEYS: PillarKey[] = ["year", "month", "day", "hour"];
export const PILLAR_LABEL: Record<PillarKey, string> = { year: "년주", month: "월주", day: "일주", hour: "시주" };

export type BirthInput = {
  year: number;
  month: number;
  day: number;
  hour: number | null; // null = 시간 모름
  minute: number;
  calendar: "solar" | "lunar";
  leap: boolean;
  gender: "남" | "여";
};

/** 엔진 하나가 낸 결과를 같은 모양으로 맞춘 것 */
export type EngineOutput = {
  engine: string;
  pillars: Record<PillarKey, string>; // 예: "庚寅"
  tenGods: Record<PillarKey, { stem: string; branch: string }>;
  daeun: { startAge: number; ganzhi: string[]; direction: "forward" | "backward" };
  strength: "strong" | "weak" | "neutral";
  yongsinElements: Element[];
};

export type PillarView = {
  key: PillarKey;
  ganzhi: string;
  stem: string;
  branch: string;
  stemKo: string;
  branchKo: string;
  stemElement: Element;
  branchElement: Element;
  stemTenGod: string;
  branchTenGod: string;
  agreed: boolean; // 두 엔진이 같은 값을 냈는가
  unknown?: boolean; // 시간 모름
};

export type YearFlow = { year: number; ganzhi: string; tenGod: TenGod; branchTenGod: TenGod };

export type SajuConsensus = {
  pillars: PillarView[];
  dayMaster: { stem: string; ko: string; element: Element };
  fiveElements: Record<Element, number>;
  tenGodCounts: Record<string, number>;
  strength: "strong" | "weak" | "neutral" | "undetermined";
  yongsin: Element[];
  currentDaeun: { ganzhi: string; startAge: number; stemTenGod: string; branchTenGod: string } | null;
  daeunAgreed: boolean;
  years: YearFlow[]; // 올해부터 3년
  relations: string[]; // 충·형 등 주의 관계
  agreement: { total: number; agreed: number; notes: string[] };
  age: number;
};
