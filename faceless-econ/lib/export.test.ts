import { describe, expect, it } from "vitest";
import { BOM, csvCell, toCsv } from "./export";
import { analyzeTitle } from "./analysis/title";
import { detectFormat } from "./format";
import { parseIsoDuration } from "./time";
import { channelShare, eligibleForBenchmark, judgeVideo } from "./analysis/faceless";

describe("CSV", () => {
  it("UTF-8 BOM + CRLF, 쉼표·따옴표 이스케이프", () => {
    const csv = toCsv(["제목", "값"], [["금리, 그리고 \"대출\"", 1]]);
    expect(csv.startsWith(BOM)).toBe(true);
    expect(csv).toContain('"금리, 그리고 ""대출"""');
    expect(csv.endsWith("\r\n")).toBe(true);
  });
  it("null은 빈 칸, NaN도 빈 칸", () => {
    expect(csvCell(null)).toBe("");
    expect(csvCell(NaN)).toBe("");
  });
});

describe("영상 형식·길이", () => {
  it("ISO 8601 기간 파싱", () => {
    expect(parseIsoDuration("PT8M30S")).toBe(510);
    expect(parseIsoDuration("PT1H")).toBe(3600);
    expect(parseIsoDuration("P1DT1S")).toBe(86401);
    expect(parseIsoDuration(undefined)).toBeNull();
  });
  it("쇼츠 판별", () => {
    expect(detectFormat(45, "a", null, "none").format).toBe("shorts");
    expect(detectFormat(120, "금리 #shorts", null, "none").format).toBe("shorts");
    expect(detectFormat(120, "금리", null, "none", false).format).toBe("long");
    expect(detectFormat(600, "a", null, "none").format).toBe("long");
    expect(detectFormat(600, "a", null, "live").format).toBe("other");
    expect(detectFormat(null, "a", null, "none").format).toBe("other");
  });
});

describe("제목 분석", () => {
  it("숫자·질문·프레임 감지", () => {
    const t = analyzeTitle("금리 내렸는데 내 대출이자는 왜 그대로일까? 3단계로 정리");
    expect(t.hasNumber).toBe(true);
    expect(t.types).toContain("질문형");
    expect(t.frames).toContain("호기심");
  });
  it("경고형·손실 회피", () => {
    const t = analyzeTitle("전세 폭락 경고, 지금 모르면 손해");
    expect(t.types).toContain("경고형");
    expect(t.frames).toEqual(expect.arrayContaining(["손실 회피", "긴급성"]));
  });
});

describe("페이스리스 판정", () => {
  const prior = { cls: "A" as const, confidence: "estimated" as const, evidence: [] };
  it("자동 판정은 '확정'을 부여하지 않는다", () => {
    expect(judgeVideo("금리 정리", null, "none", { ...prior, confidence: "confirmed" }).confidence).toBe("estimated");
  });
  it("인터뷰 신호 → 혼합/인물, 라이브 → D", () => {
    expect(judgeVideo("박사님 인터뷰", null, "none", prior).cls).toBe("E");
    expect(judgeVideo("시황", null, "completed", prior).cls).toBe("D");
  });
  it("채널 비중과 E형 조건부 포함", () => {
    const s = channelShare([
      { cls: "A", confidence: "estimated", evidence: [] },
      { cls: "A", confidence: "estimated", evidence: [] },
      { cls: "D", confidence: "estimated", evidence: [] },
      { cls: "U", confidence: "unverified", evidence: [] },
    ]);
    expect(s.facelessRatio).toBeCloseTo(2 / 3);
    expect(eligibleForBenchmark("E", 0.7)).toBe(true);
    expect(eligibleForBenchmark("E", 0.4)).toBe(false);
    expect(eligibleForBenchmark("D", 1)).toBe(false);
  });
});
