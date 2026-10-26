import { describe, expect, it } from "vitest";
import { requestBrief } from "@/lib/approval/brief";
import { CHANNEL_PACK, PACK_CHANNELS, packStaff } from "@/lib/company/channels";
import { AI_STAFF } from "@/lib/company/staff";
import { renderStaffDoc, staffFilePath, staffFiles } from "@/lib/company/staff-doc";
import { staleFiles } from "../../scripts/export-staff";

describe("채널 패키지", () => {
  it("gives every short-form channel a scene script and routes it to the short-form PD", () => {
    for (const p of ["INSTAGRAM", "YOUTUBE", "TIKTOK"] as const) {
      expect(CHANNEL_PACK[p]).toContain("SHORT_SCRIPT");
      expect(packStaff(p)).toContain("shortform");
    }
    expect(packStaff("THREADS")).toEqual(["copywriter"]);
    expect(PACK_CHANNELS).toEqual(["THREADS", "INSTAGRAM", "YOUTUBE", "FACEBOOK", "TIKTOK"]);
  });
});

describe("결재 요청서", () => {
  it("states target, change, cost, risk and how to undo for every gate", () => {
    for (const gate of ["CONTENT", "QUOTE", "CONTRACT"] as const) {
      const b = requestBrief({ gate, title: "t", amount: 1_200_000, risk: "MEDIUM", payload: { tier: "PREMIUM" }, blocked: false });
      for (const v of Object.values(b)) expect(v.length).toBeGreaterThan(0);
    }
    expect(requestBrief({ gate: "QUOTE", title: "t", amount: 1_200_000, risk: "LOW", blocked: false }).cost).toContain("1,200,000원");
    expect(requestBrief({ gate: "CONTRACT", title: "t", amount: 1, risk: "LOW", payload: { tier: "PREMIUM" }, blocked: false }).change).toContain("집중형");
    expect(requestBrief({ gate: "CONTENT", title: "t", amount: null, risk: "HIGH", blocked: true }).risk).toContain("승인 불가");
  });
});

describe("직원 지시서 (Claude Code 회사 폴더)", () => {
  it("renders every required section without placeholders", () => {
    for (const s of AI_STAFF) {
      const doc = renderStaffDoc(s);
      for (const h of ["목적", "할 일", "안 할 일", "도구", "입력", "처리 순서", "출력", "완료 기준", "다음 담당", "결재", "실패 대응"]) expect(doc).toContain(`## ${h}`);
      expect(doc).not.toMatch(/TODO|\[경로 입력\]|나중에 채우세요|undefined/);
    }
    expect(new Set(AI_STAFF.map(staffFilePath)).size).toBe(AI_STAFF.length);
    expect(Object.keys(staffFiles())).toHaveLength(AI_STAFF.length * 2 + 10);
  });

  it("the committed folder matches the roster (run `npm run staff:export` after editing staff.ts)", () => {
    expect(staleFiles()).toEqual([]);
  });
});
