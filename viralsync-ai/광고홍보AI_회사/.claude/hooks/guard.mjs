#!/usr/bin/env node
// 회사 폴더 안전 훅 (gstack /careful·/freeze 를 회사 규칙에 맞게).
// - 쓰기는 03_결과/ · 04_기록/ 안에서만 (01_직원·05_매뉴얼은 자동 생성, 02_자료는 캡틴이 넣는 원본 사본)
// - 되돌리기 어려운 명령과 외부로 내보내는 명령(게시·발송)은 차단
import { dirname, relative, resolve, sep } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..", "..");
let input = "";
for await (const c of process.stdin) input += c;
let d;
try {
  d = JSON.parse(input);
} catch {
  process.exit(0);
}
const block = (why) => {
  process.stderr.write(`[회사 규칙] 차단: ${why}\n결재 대상이면 04_기록/결재대장.md 에 ‘대기’로 올리고 멈추세요.\n`);
  process.exit(2);
};
const tool = d.tool_name ?? "";
const ti = d.tool_input ?? {};
if (["Edit", "Write", "MultiEdit", "NotebookEdit"].includes(tool)) {
  const rel = relative(root, resolve(String(ti.file_path ?? ti.notebook_path ?? "")));
  const ok = ["03_결과", "04_기록"].some((dir) => rel === dir || rel.startsWith(dir + sep));
  if (!ok) block(`쓰기는 03_결과/·04_기록/ 안에서만 (${rel || "?"}). 지시서·매뉴얼은 viralsync-ai 의 원본을 고친 뒤 npm run staff:export`);
}
if (tool === "Bash") {
  const cmd = String(ti.command ?? "");
  const rules = [
    [/\brm\s+-[a-zA-Z]*[rf][a-zA-Z]*\b/, "파일 삭제 — 지우지 말고 결재 후 옮기기"],
    [/\bgit\s+(push|reset\s+--hard|clean)\b/, "git 푸시·되돌리기는 개발 폴더에서"],
    [/\b(curl|wget|http)\b[^;&|]*(-X\s*(POST|PUT|PATCH|DELETE)|--data|-d\s|--form|-F\s)/i, "외부로 보내기(게시·발송) — 결재 대상"],
    [/\b(sendmail|mail\s|mutt)\b/, "메일 발송 — 결재 대상"],
  ];
  for (const [re, why] of rules) if (re.test(cmd)) block(why);
}
process.exit(0);
