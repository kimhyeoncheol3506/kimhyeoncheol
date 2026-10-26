import { PrismaClient } from "@prisma/client";
import { PrismaPg } from "@prisma/adapter-pg";
import { getCloudflareContext } from "@opennextjs/cloudflare";

/** Cloudflare Workers(workerd) 에서 실행 중인지 */
export const onWorkers = typeof navigator !== "undefined" && navigator.userAgent === "Cloudflare-Workers";

const globalForPrisma = globalThis as unknown as { prisma?: PrismaClient };

function nodeClient(): PrismaClient {
  globalForPrisma.prisma ??= new PrismaClient({ log: ["error"] });
  return globalForPrisma.prisma;
}

/**
 * Workers 는 요청끼리 DB 연결을 공유할 수 없어 요청마다 클라이언트를 만든다 (드라이버 어댑터 + 연결 1회용).
 * 같은 요청 안에서는 하나를 재사용한다.
 */
const perRequest = new WeakMap<object, PrismaClient>();

function workersClient(): PrismaClient {
  const { ctx, env } = getCloudflareContext();
  let c = perRequest.get(ctx);
  if (!c) {
    const url = (env as { HYPERDRIVE?: { connectionString: string } }).HYPERDRIVE?.connectionString ?? process.env.DATABASE_URL;
    if (!url) throw new Error("DATABASE_URL 이 설정되지 않았습니다.");
    c = new PrismaClient({ adapter: new PrismaPg({ connectionString: url, maxUses: 1 }), log: ["error"] });
    perRequest.set(ctx, c);
  }
  return c;
}

function client(): PrismaClient {
  return onWorkers ? workersClient() : nodeClient();
}

/** 기존 코드는 그대로 `prisma.x` 를 쓰고, 실제 클라이언트는 실행 환경에 맞게 고른다 */
export const prisma = new Proxy({} as PrismaClient, {
  get(_t, prop) {
    const c = client();
    const v = Reflect.get(c, prop);
    return typeof v === "function" ? v.bind(c) : v;
  },
});
