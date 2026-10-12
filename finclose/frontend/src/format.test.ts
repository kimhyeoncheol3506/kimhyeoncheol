import { describe, expect, it } from "vitest";
import { fmtAmount, fmtRate } from "./format";

describe("fmtAmount", () => {
  it("천단위 구분, 부동소수 오차 없음", () => {
    expect(fmtAmount("175509301000")).toBe("175,509,301,000");
    expect(fmtAmount("12345678901234567890.10")).toBe("12,345,678,901,234,567,890.1");
    expect(fmtAmount("-1000.00")).toBe("-1,000");
    expect(fmtAmount("0.1")).toBe("0.1");
  });
  it("빈 값과 비숫자", () => {
    expect(fmtAmount(null)).toBe("-");
    expect(fmtAmount("abc")).toBe("abc");
  });
});

describe("fmtRate", () => {
  it("특수 상태는 백분율로 표시하지 않음", () => {
    expect(fmtRate(null, "N/A_ZERO_BASE")).toBe("산정불가(0기준)");
    expect(fmtRate(null, "SIGN_CHANGE")).toBe("부호전환");
    expect(fmtRate("0.1234", "RATE")).toBe("+12.34%");
    expect(fmtRate("-0.05", "RATE")).toBe("-5.00%");
  });
});
