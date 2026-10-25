import { createCipheriv, createDecipheriv, createHash, randomBytes } from "crypto";

/** 액세스 토큰 암호화 (AES-256-GCM). 키는 TOKEN_ENCRYPTION_KEY 에서 SHA-256 으로 파생 */
function key(secret: string): Buffer {
  if (!secret || secret.length < 16) throw new Error("TOKEN_ENCRYPTION_KEY 가 없거나 16자 미만입니다.");
  return createHash("sha256").update(secret).digest();
}

export function encryptToken(plain: string, secret: string): string {
  const iv = randomBytes(12);
  const c = createCipheriv("aes-256-gcm", key(secret), iv);
  const enc = Buffer.concat([c.update(plain, "utf8"), c.final()]);
  return ["v1", iv.toString("base64"), c.getAuthTag().toString("base64"), enc.toString("base64")].join(".");
}

export function decryptToken(payload: string, secret: string): string {
  const [v, iv, tag, data] = payload.split(".");
  if (v !== "v1" || !iv || !tag || !data) throw new Error("저장된 토큰 형식이 올바르지 않습니다.");
  const d = createDecipheriv("aes-256-gcm", key(secret), Buffer.from(iv, "base64"));
  d.setAuthTag(Buffer.from(tag, "base64"));
  return Buffer.concat([d.update(Buffer.from(data, "base64")), d.final()]).toString("utf8");
}

export function tokenHint(token: string): string {
  return `****${token.slice(-4)}`;
}
