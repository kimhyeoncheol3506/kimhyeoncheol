// 터미널 수집: npm run collect
// .env.local 의 YOUTUBE_API_KEY 를 읽어 수집을 1회 실행한다. (작업 스케줄러/cron 으로 매일 실행 가능)
import fs from "node:fs";
import path from "node:path";

for (const f of [".env.local", ".env"]) {
  const p = path.join(process.cwd(), f);
  if (!fs.existsSync(p)) continue;
  for (const line of fs.readFileSync(p, "utf8").split(/\r?\n/)) {
    const m = line.match(/^\s*([A-Z_][A-Z0-9_]*)\s*=\s*(.*?)\s*$/);
    if (m && !process.env[m[1]]) process.env[m[1]] = m[2].replace(/^["']|["']$/g, "");
  }
}

async function main() {
  const { hasApiKey } = await import("../lib/youtube/client");
  const { collect } = await import("../lib/youtube/collect");
  const { targetChannelIds } = await import("../lib/dataset");
  const { loadStore } = await import("../lib/store");
  if (!hasApiKey()) {
    console.error("YOUTUBE_API_KEY가 없습니다. .env.local 파일을 확인하세요.");
    process.exit(1);
  }
  const s = loadStore().settings;
  const ids = targetChannelIds(s);
  console.log(`채널 ${ids.length}개 수집 시작…`);
  const run = await collect({ channelIds: ids, peerWindowDays: s.peerWindowDays });
  for (const m of run.messages) console.log(`[${m.level}] ${m.text}`);
  console.log(`결과: ${run.status} · 영상 ${run.videosCollected}개 · 할당량 약 ${run.quotaUsed}단위`);
  process.exit(run.status === "failed" ? 1 : 0);
}
main();
