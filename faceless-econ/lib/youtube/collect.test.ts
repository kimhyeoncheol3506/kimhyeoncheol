import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

const KEY = "TEST_SECRET_KEY_123";
const CH = "UCzjmNt4AViR0rQpP6n99ZxA";
const now = Date.now();
const iso = (hAgo: number) => new Date(now - hAgo * 3_600_000).toISOString();

function json(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } });
}

function mockApi(opts: { quotaOnVideos?: boolean } = {}) {
  return vi.fn(async (input: string | URL | Request) => {
    const url = new URL(String(input));
    if (url.hostname === "www.youtube.com") return new Response(null, { status: 303 }); // /shorts/ 확인: 쇼츠 아님
    const ep = url.pathname.split("/").pop();
    if (ep === "channels")
      return json({
        items: [
          {
            id: CH,
            snippet: { title: "경제의 시작", description: "d", customUrl: "@firstecon" },
            statistics: { viewCount: "1000000", hiddenSubscriberCount: true, videoCount: "50" },
            contentDetails: { relatedPlaylists: { uploads: "UUzjmNt4AViR0rQpP6n99ZxA" } },
          },
        ],
      });
    if (ep === "playlistItems")
      return json({
        items: [
          { contentDetails: { videoId: "vid_new", videoPublishedAt: iso(30) } },
          { contentDetails: { videoId: "vid_gone", videoPublishedAt: iso(60) } },
          { contentDetails: { videoId: "vid_short", videoPublishedAt: iso(80) } },
          { contentDetails: { videoId: "vid_old", videoPublishedAt: iso(24 * 200) } }, // 비교 기간 밖 → 중단
        ],
        nextPageToken: "NEXT",
      });
    if (ep === "videos") {
      if (opts.quotaOnVideos) return json({ error: { message: `quota for key=${KEY}`, errors: [{ reason: "quotaExceeded" }] } }, 403);
      return json({
        items: [
          {
            id: "vid_new",
            snippet: { publishedAt: iso(30), channelId: CH, title: "금리가 내리면 내 대출은? 3가지", description: "", liveBroadcastContent: "none", thumbnails: { high: { url: "https://i.ytimg.com/x.jpg" } } },
            statistics: { viewCount: "3000", commentCount: "12" }, // 좋아요 비공개
            contentDetails: { duration: "PT9M10S" },
          },
          {
            id: "vid_short",
            snippet: { publishedAt: iso(80), channelId: CH, title: "금리 1분", description: "" },
            statistics: { viewCount: "500", likeCount: "20", commentCount: "1" },
            contentDetails: { duration: "PT45S" },
          },
        ],
      });
    }
    return json({}, 404);
  });
}

let dir: string;
beforeEach(() => {
  dir = fs.mkdtempSync(path.join(os.tmpdir(), "fe-"));
  process.env.DATA_DIR = dir;
  process.env.YOUTUBE_API_KEY = KEY;
  vi.resetModules();
});
afterEach(() => {
  vi.unstubAllGlobals();
  fs.rmSync(dir, { recursive: true, force: true });
});

describe("collect (모의 API)", () => {
  it("결측·삭제·형식을 처리하고 키를 저장하지 않는다", async () => {
    vi.stubGlobal("fetch", mockApi());
    const { collect } = await import("./collect");
    const { loadStore } = await import("../store");
    const run = await collect({ channelIds: [CH], peerWindowDays: 90 });
    expect(run.status).toBe("success");
    const s = loadStore();
    expect(s.channels[CH].subscriberCount).toBeNull();
    expect(s.channels[CH].subscriberHidden).toBe(true);
    expect(s.videos.vid_new.likeCount).toBeNull();
    expect(s.videos.vid_new.commentCount).toBe(12);
    expect(s.videos.vid_new.format).toBe("long");
    expect(s.videos.vid_short.format).toBe("shorts");
    expect(s.videos.vid_short.url).toContain("/shorts/");
    expect(s.videos.vid_old).toBeUndefined();
    expect(s.videos.vid_gone).toBeUndefined(); // API가 돌려주지 않은 새 영상은 저장하지 않음
    expect(run.messages.some((m) => m.text.includes("조회되지 않음"))).toBe(true);
    expect(s.snapshots).toHaveLength(2);
    expect(JSON.stringify(s)).not.toContain(KEY);
    const cacheFiles = fs.readdirSync(path.join(dir, "cache"));
    for (const f of cacheFiles) expect(fs.readFileSync(path.join(dir, "cache", f), "utf8")).not.toContain(KEY);

    // 두 번째 수집: 영상은 중복 저장되지 않고 스냅샷만 추가
    await new Promise((r) => setTimeout(r, 5));
    await collect({ channelIds: [CH], peerWindowDays: 90 });
    const s2 = loadStore();
    expect(Object.keys(s2.videos)).toHaveLength(2);
    expect(s2.snapshots).toHaveLength(4);
    expect(s2.videos.vid_new.firstSeenAt).toBe(s.videos.vid_new.firstSeenAt);
  });

  it("할당량 초과 시 부분 저장하고 키를 메시지에 노출하지 않는다", async () => {
    vi.stubGlobal("fetch", mockApi({ quotaOnVideos: true }));
    const { collect } = await import("./collect");
    const { loadStore } = await import("../store");
    const run = await collect({ channelIds: [CH], peerWindowDays: 90 });
    expect(run.status).toBe("failed");
    expect(run.messages.map((m) => m.text).join()).toContain("할당량");
    expect(JSON.stringify(loadStore())).not.toContain(KEY);
    expect(loadStore().channels[CH]).toBeDefined(); // 채널 정보는 저장됨
  });

  it("API 키가 없으면 수집하지 않는다", async () => {
    delete process.env.YOUTUBE_API_KEY;
    const f = mockApi();
    vi.stubGlobal("fetch", f);
    const { collect } = await import("./collect");
    const run = await collect({ channelIds: [CH], peerWindowDays: 90 });
    expect(run.status).toBe("failed");
    expect(run.messages[0].text).toContain("YOUTUBE_API_KEY");
    expect(f).not.toHaveBeenCalled();
  });
});
