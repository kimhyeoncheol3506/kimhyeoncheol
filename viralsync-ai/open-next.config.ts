import { defineCloudflareConfig } from "@opennextjs/cloudflare";

// 모든 화면이 로그인 후 동적으로 그려지므로 증분 캐시(R2)는 쓰지 않는다
export default defineCloudflareConfig({});
