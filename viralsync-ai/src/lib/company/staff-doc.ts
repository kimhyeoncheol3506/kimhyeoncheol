import { AI_STAFF, APPROVAL_TARGETS, FORBIDDEN_LINES, staffLabel, type StaffDef } from "./staff";

/** 광고홍보AI_회사/ 폴더 기준 상대 경로 */
export function staffFilePath(s: StaffDef): string {
  const i = AI_STAFF.indexOf(s);
  return `01_직원/${String(i).padStart(2, "0")}_${s.title.replace(/[·\s]/g, "")}_${s.name}.md`;
}

const list = (xs: string[]) => xs.map((x) => `- ${x}`).join("\n");

/** 직원 업무 지시서 (Claude Code 가 그대로 읽고 따르는 형식) */
export function renderStaffDoc(s: StaffDef): string {
  return `<!-- 자동 생성: viralsync-ai/src/lib/company/staff.ts 를 고친 뒤 npm run staff:export 로 다시 만드세요. 이 파일을 직접 고치지 마세요. -->
# ${s.emoji} ${s.name} — ${s.title} 업무 지시서

## 목적
${s.purpose}

## 성격·보고 말투
${s.personality}

## 할 일
${list(s.does)}

## 안 할 일
${list(s.doesNot)}

## 도구
- 웹 앱(ViralSync AI): ${s.tools.join(", ")}
- 이 폴더에서 일할 때: \`02_자료/\` 읽기, \`03_결과/\` 쓰기, \`04_기록/\` 쓰기만 허용

## 입력
${s.input}

## 처리 순서
${s.steps.map((x, i) => `${i + 1}. ${x}`).join("\n")}

## 출력
${s.output}
- 이 폴더에서 일할 때: \`03_결과/<업무번호>_${s.name}_<내용>.md\` 로 저장

## 완료 기준
${s.doneWhen}

## 다음 담당
${staffLabel(s.next)}

## 결재
${s.approval}

## 실패 대응
${s.onFailure}

## 수정 담당
이 직원만 고치는 결과물: ${s.owns}
`;
}

/** Claude Code 서브에이전트 정의 (.claude/agents/*.md) — 쓰기 범위는 결과·기록 폴더, 외부 도구 없음 */
export function renderSubagent(s: StaffDef): string {
  return `---
name: ${s.key}
description: ${s.name} ${s.title} — ${s.purpose}
tools: Read, Glob, Grep, Write, Edit
---
<!-- 자동 생성: npm run staff:export -->
당신은 광고홍보 AI 회사의 ${s.title} '${s.name}'입니다.
먼저 \`CLAUDE.md\` 와 \`${staffFilePath(s)}\` 를 읽고 그 지시서대로만 일합니다.
- 읽기: \`02_자료/\`, \`03_결과/\` / 쓰기: \`03_결과/\`, \`04_기록/\` 만.
- 금지선: ${FORBIDDEN_LINES.join(" / ")}
- 결재 대상(${APPROVAL_TARGETS.join(", ")})은 실행하지 말고 \`04_기록/결재대장.md\` 에 ‘결재 대기’로 적고 멈춥니다.
- 끝나면 한 일 → 결과 → 다음 담당(${staffLabel(s.next)})을 3줄로 남깁니다.
`;
}

export function staffFiles(): Record<string, string> {
  const files: Record<string, string> = {};
  for (const s of AI_STAFF) {
    files[staffFilePath(s)] = renderStaffDoc(s);
    files[`.claude/agents/${s.key}.md`] = renderSubagent(s);
  }
  return files;
}
