#!/usr/bin/env node
// gstack 의 /careful · /freeze 를 옮긴 안전 훅 (PreToolUse).
// - Bash: 되돌리기 어려운 명령을 막는다 (exit 2 = 차단, 이유는 stderr 로 Claude 에게 전달)
// - Edit/Write: .claude/freeze 파일에 적힌 폴더 밖의 수정을 막는다 (/freeze, /unfreeze)
import { existsSync, readFileSync } from "node:fs";
import { dirname, resolve, sep } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..", "..");
let input = "";
for await (const chunk of process.stdin) input += chunk;
let data;
try {
  data = JSON.parse(input);
} catch {
  process.exit(0);
}
const tool = data.tool_name ?? "";
const ti = data.tool_input ?? {};
const block = (why) => {
  process.stderr.write(`[guard] 차단: ${why}\n정말 필요하면 캡틴(사용자)에게 이유를 설명하고 직접 실행을 요청하세요.\n`);
  process.exit(2);
};

if (tool === "Bash") {
  const cmd = String(ti.command ?? "");
  const rules = [
    [/\brm\s+(-[a-zA-Z]*r[a-zA-Z]*f|-[a-zA-Z]*f[a-zA-Z]*r)\b[^;&|]*\s(\/|~|\$HOME|\.\.?)(\s|$|\/\s|\/\*)/, "루트·홈·현재 폴더 전체 삭제 (rm -rf)"],
    [/\bgit\s+push\b[^;&|]*\s(--force(?!-with-lease)|-f)\b/, "강제 푸시 (git push --force) — 필요하면 --force-with-lease, 기본 브랜치는 금지"],
    [/\bgit\s+reset\s+--hard\b/, "작업 내용 버리기 (git reset --hard)"],
    [/\bgit\s+clean\s+-[a-zA-Z]*f/, "추적 안 되는 파일 전부 삭제 (git clean -f)"],
    [/prisma\s+(db\s+push\b[^;&|]*--force-reset|migrate\s+reset)/, "DB 초기화 (prisma --force-reset / migrate reset) — 데모만 지우려면 npm run db:reset"],
    [/\b(DROP\s+(TABLE|DATABASE|SCHEMA)|TRUNCATE\s+TABLE)\b/i, "테이블·DB 삭제 SQL"],
    [/\bwrangler\s+(delete|r2\s+bucket\s+delete|secret\s+delete)\b/, "Cloudflare Worker·버킷·비밀값 삭제"],
    [/\bwrangler\s+(deploy|versions\s+deploy)\b|opennextjs-cloudflare\s+deploy|npm\s+run\s+cf:deploy/, "운영 배포 — 배포는 캡틴이 직접 (docs/DEPLOY_CLOUDFLARE.md)"],
  ];
  // 테스트 전용 DB 의 --accept-data-loss 는 허용, 그 밖은 차단
  if (/db\s+push\b[^;&|]*--accept-data-loss/.test(cmd) && !/viralsync_(test|e2e)\b/.test(cmd) && !/global-setup/.test(cmd))
    block("데이터 손실을 허용하는 db push — 운영·개발 DB 에서는 캡틴 확인 후");
  for (const [re, why] of rules) if (re.test(cmd)) block(why);
}

if (["Edit", "Write", "MultiEdit", "NotebookEdit"].includes(tool)) {
  const freezeFile = resolve(root, ".claude", "freeze");
  if (existsSync(freezeFile)) {
    const allowed = resolve(root, readFileSync(freezeFile, "utf8").trim());
    const target = resolve(String(ti.file_path ?? ti.notebook_path ?? ""));
    if (target !== allowed && !target.startsWith(allowed + sep))
      block(`/freeze 중 — 수정은 ${allowed} 안에서만. 풀려면 /unfreeze`);
  }
}
process.exit(0);
