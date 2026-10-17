"use client";
import { useState } from "react";
import type { ErrorReport } from "@/lib/types";

// 오류 내용을 클로드 코드에 그대로 붙여넣을 수 있는 문장으로 만들어 복사합니다.
export function errorToPrompt(e: ErrorReport): string {
  return [
    "[AIMAX OS 오류 보고]",
    `제목: ${e.title}`,
    `발생 페이지: ${e.page || "-"}`,
    `발생 시각: ${e.createdAt}`,
    `오류 내용: ${e.message}`,
    e.stack ? `상세 기록:\n${e.stack}` : "",
    e.feedback ? `CEO 메모: ${e.feedback}` : "",
    "",
    "aimax-os 폴더의 코드에서 위 오류의 원인을 찾아 고쳐 주세요. 무엇을 바꿨는지 쉬운 말로 설명해 주세요.",
  ]
    .filter(Boolean)
    .join("\n");
}

export function CopyForClaude({ error }: { error: ErrorReport }) {
  const [done, setDone] = useState(false);
  const copy = async () => {
    await navigator.clipboard.writeText(errorToPrompt(error));
    setDone(true);
    setTimeout(() => setDone(false), 1500);
  };
  return (
    <button className="btn" onClick={copy}>
      {done ? "✅ 복사됨" : "📋 클로드 코드용 복사"}
    </button>
  );
}
