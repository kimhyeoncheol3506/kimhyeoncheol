// API 클라이언트. 사용자/역할은 데모용 전환값이며 인증이 아니다.
export type Role = "admin" | "preparer" | "reviewer" | "approver" | "viewer";

export const ROLE_LABELS: Record<Role, string> = {
  admin: "관리자", preparer: "업무 담당자", reviewer: "검토자", approver: "승인자", viewer: "조회 전용",
};

const KEY = "finclose.identity";

export function getIdentity(): { user: string; role: Role } {
  try {
    const v = JSON.parse(localStorage.getItem(KEY) || "");
    if (v && v.user && v.role) return v;
  } catch { /* 저장소 사용 불가 시 기본값 */ }
  return { user: "이담당", role: "preparer" };
}

export function setIdentity(user: string, role: Role) {
  try { localStorage.setItem(KEY, JSON.stringify({ user, role })); } catch { /* 무시 */ }
}

export class ApiError extends Error {
  status: number;
  payload: any;
  constructor(status: number, payload: any) {
    super(payload?.detail || `요청 실패 (${status})`);
    this.status = status;
    this.payload = payload;
  }
}

function headers(json = true): Record<string, string> {
  const id = getIdentity();
  const h: Record<string, string> = { "X-FinClose-User": encodeURIComponent(id.user), "X-FinClose-Role": id.role };
  if (json) h["Content-Type"] = "application/json";
  return h;
}

async function handle(res: Response) {
  const text = await res.text();
  let body: any = null;
  try { body = text ? JSON.parse(text) : null; } catch { body = { detail: text }; }
  if (!res.ok) throw new ApiError(res.status, body);
  return body;
}

export const api = {
  get: (p: string) => fetch(p, { headers: headers(false) }).then(handle),
  post: (p: string, body: unknown) => fetch(p, { method: "POST", headers: headers(), body: JSON.stringify(body) }).then(handle),
  put: (p: string, body: unknown) => fetch(p, { method: "PUT", headers: headers(), body: JSON.stringify(body) }).then(handle),
  upload: (files: File[]) => {
    const fd = new FormData();
    files.forEach((f) => fd.append("files", f, f.name));
    return fetch("/api/files", { method: "POST", headers: headers(false), body: fd }).then(handle);
  },
  fileUrl: (runId: string, name: string) => {
    const id = getIdentity();
    return `/api/runs/${encodeURIComponent(runId)}/files/${encodeURIComponent(name)}?u=${encodeURIComponent(id.user)}&r=${id.role}`;
  },
};
