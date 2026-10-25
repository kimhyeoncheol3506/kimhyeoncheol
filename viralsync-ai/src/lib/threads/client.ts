import { THREADS_API } from "./config.shared";

/**
 * Threads Graph API 클라이언트 (공식 문서 기준: 컨테이너 생성 → 상태 확인 → 게시).
 * fetch·sleep 을 주입받아 테스트에서 실제 네트워크 없이 검증한다.
 */
export interface ThreadsDeps {
  fetch: typeof fetch;
  sleep: (ms: number) => Promise<void>;
}

export class ThreadsApiError extends Error {
  constructor(
    public code: string,
    message: string,
  ) {
    super(message);
    this.name = "ThreadsApiError";
  }
}

const defaultDeps: ThreadsDeps = { fetch: (...a) => fetch(...a), sleep: (ms) => new Promise((r) => setTimeout(r, ms)) };

async function call<T>(deps: ThreadsDeps, method: "GET" | "POST", path: string, params: Record<string, string>): Promise<T> {
  const body = new URLSearchParams(params);
  const url = method === "GET" ? `${THREADS_API}${path}?${body}` : `${THREADS_API}${path}`;
  let res: Response;
  try {
    res = await deps.fetch(url, method === "GET" ? { method } : { method, body, headers: { "Content-Type": "application/x-www-form-urlencoded" } });
  } catch {
    throw new ThreadsApiError("NETWORK", "Threads 서버에 연결할 수 없습니다.");
  }
  const json = (await res.json().catch(() => ({}))) as Record<string, unknown> & { error?: { message?: string; code?: number; type?: string } };
  if (!res.ok || json.error) {
    const e = json.error;
    const code = res.status === 401 || e?.code === 190 ? "AUTH" : res.status === 429 || e?.code === 4 ? "RATE_LIMIT" : `HTTP_${res.status}`;
    // 토큰이 포함될 수 있는 URL 은 메시지에 넣지 않는다
    throw new ThreadsApiError(code, e?.message ? `Threads 오류: ${e.message}` : `Threads API 오류 (HTTP ${res.status})`);
  }
  return json as T;
}

export async function getMe(token: string, deps: ThreadsDeps = defaultDeps) {
  return call<{ id: string; username?: string }>(deps, "GET", "/v1.0/me", { fields: "id,username", access_token: token });
}

export async function exchangeCode(p: { appId: string; appSecret: string; redirectUri: string; code: string }, deps: ThreadsDeps = defaultDeps) {
  return call<{ access_token: string; user_id: string | number }>(deps, "POST", "/oauth/access_token", {
    client_id: p.appId,
    client_secret: p.appSecret,
    code: p.code.replace(/#_$/, ""),
    grant_type: "authorization_code",
    redirect_uri: p.redirectUri,
  });
}

export async function toLongLived(appSecret: string, shortToken: string, deps: ThreadsDeps = defaultDeps) {
  return call<{ access_token: string; expires_in: number }>(deps, "GET", "/access_token", { grant_type: "th_exchange_token", client_secret: appSecret, access_token: shortToken });
}

export async function refreshLongLived(token: string, deps: ThreadsDeps = defaultDeps) {
  return call<{ access_token: string; expires_in: number }>(deps, "GET", "/refresh_access_token", { grant_type: "th_refresh_token", access_token: token });
}

export interface PublishResult {
  containerId: string;
  mediaId: string;
  permalink: string | null;
}

/** 이미지 1장 게시. 컨테이너가 FINISHED 될 때까지 확인한 뒤 게시한다 (최대 약 maxWaitMs). */
export async function publishImage(
  p: { userId: string; token: string; imageUrl: string; text: string },
  deps: ThreadsDeps = defaultDeps,
  opts: { pollMs?: number; maxWaitMs?: number } = {},
): Promise<PublishResult> {
  const pollMs = opts.pollMs ?? 3000;
  const maxWaitMs = opts.maxWaitMs ?? 60_000;
  const params: Record<string, string> = { media_type: "IMAGE", image_url: p.imageUrl, access_token: p.token };
  if (p.text) params.text = p.text;
  const { id: containerId } = await call<{ id: string }>(deps, "POST", `/v1.0/${p.userId}/threads`, params);

  let waited = 0;
  for (;;) {
    const st = await call<{ status?: string; error_message?: string }>(deps, "GET", `/v1.0/${containerId}`, { fields: "status,error_message", access_token: p.token });
    if (st.status === "FINISHED") break;
    if (st.status === "ERROR" || st.status === "EXPIRED")
      throw new ThreadsApiError(`CONTAINER_${st.status}`, `이미지 처리 실패: ${st.error_message ?? st.status} (이미지 주소가 외부에서 열리는지 확인하세요)`);
    if (waited >= maxWaitMs) throw new ThreadsApiError("CONTAINER_TIMEOUT", "이미지 처리가 지연되고 있습니다. 잠시 후 다시 시도하세요.");
    await deps.sleep(pollMs);
    waited += pollMs;
  }

  const { id: mediaId } = await call<{ id: string }>(deps, "POST", `/v1.0/${p.userId}/threads_publish`, { creation_id: containerId, access_token: p.token });
  let permalink: string | null = null;
  try {
    permalink = (await call<{ permalink?: string }>(deps, "GET", `/v1.0/${mediaId}`, { fields: "permalink", access_token: p.token })).permalink ?? null;
  } catch {
    // 링크 조회 실패는 게시 성공에 영향 없음
  }
  return { containerId, mediaId, permalink };
}
