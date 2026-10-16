import type { FeatureReading } from "../face/physiognomy";
import type { SajuConsensus } from "../saju/types";
import type { ThemeKey } from "./themes";

export type CommonTheme = {
  key: ThemeKey;
  label: string;
  saju: number;
  face: number;
  sajuReason: string;
  faceReason: string;
  strong: boolean; // 두 쪽 모두 뚜렷하게 나타났는가
};

/** 화면·PDF에서 표처럼 보여 줄 항목 (예: 달별 카드, 행운 항목) */
export type SectionItem = { label: string; badge?: string; title?: string; rows: { k: string; v: string }[] };
export type Section = { id: string; title: string; eyebrow: string; body: string[]; items?: SectionItem[] };

export type Reading = {
  headline: string; // 큰 글씨 한 줄 요약
  summary: string; // 우리 의견 요약 (2~3문장)
  sections: Section[];
  advice: string[]; // 당부 (짧은 문장들)
  source: "rules" | "ai";
};

export type ResultPayload = {
  createdAt: string;
  name?: string;
  gender: "남" | "여";
  saju: SajuConsensus;
  face: { features: FeatureReading[] } | null;
  common: CommonTheme[];
  reading: Reading;
};
