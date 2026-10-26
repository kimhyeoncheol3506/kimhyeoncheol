import "server-only";
import { randomBytes } from "crypto";
import { mkdir, readFile, writeFile } from "fs/promises";
import path from "path";
import { getCloudflareContext } from "@opennextjs/cloudflare";
import { onWorkers } from "@/lib/db";

/** Cloudflare 에서는 디스크 대신 R2 버킷(MEDIA_BUCKET)에 저장 */
interface R2Like {
  put(key: string, value: Uint8Array, opts?: { httpMetadata?: { contentType?: string } }): Promise<unknown>;
  get(key: string): Promise<{ arrayBuffer(): Promise<ArrayBuffer> } | null>;
}

function bucket(): R2Like {
  const b = (getCloudflareContext().env as { MEDIA_BUCKET?: R2Like }).MEDIA_BUCKET;
  if (!b) throw new Error("R2 버킷(MEDIA_BUCKET)이 연결되지 않았습니다. wrangler.jsonc 의 r2_buckets 를 확인하세요.");
  return b;
}

/** Threads 가 지원하는 이미지 (공식: JPEG, PNG / 최대 8MB) */
export const MAX_IMAGE_BYTES = 8 * 1024 * 1024;

export function uploadDir(): string {
  return path.resolve(process.env.UPLOAD_DIR?.trim() || path.join(process.cwd(), "uploads"));
}

/** 파일 시그니처로 실제 형식을 확인 (확장자·MIME 만 믿지 않음) */
export function sniffImage(buf: Uint8Array): "image/jpeg" | "image/png" | "image/heic" | "image/webp" | "image/gif" | null {
  if (buf.length >= 3 && buf[0] === 0xff && buf[1] === 0xd8 && buf[2] === 0xff) return "image/jpeg";
  if (buf.length >= 8 && buf[0] === 0x89 && buf[1] === 0x50 && buf[2] === 0x4e && buf[3] === 0x47) return "image/png";
  const ascii = (a: number, b: number) => Buffer.from(buf.slice(a, b)).toString("latin1");
  if (buf.length >= 12 && ascii(0, 4) === "RIFF" && ascii(8, 12) === "WEBP") return "image/webp";
  if (buf.length >= 6 && ascii(0, 3) === "GIF") return "image/gif";
  if (buf.length >= 12 && ascii(4, 8) === "ftyp" && /hei|mif|heic|heix/.test(ascii(8, 12))) return "image/heic";
  return null;
}

export function validateImage(buf: Uint8Array): { ok: true; mime: "image/jpeg" | "image/png" } | { ok: false; message: string } {
  if (buf.length === 0) return { ok: false, message: "이미지를 선택하거나 붙여넣으세요." };
  if (buf.length > MAX_IMAGE_BYTES) return { ok: false, message: "이미지는 8MB 이하만 올릴 수 있습니다 (Threads 제한)." };
  const t = sniffImage(buf);
  if (t === "image/jpeg" || t === "image/png") return { ok: true, mime: t };
  if (t === "image/heic") return { ok: false, message: "HEIC(아이폰 사진) 형식은 Threads 가 지원하지 않습니다. JPG 로 내보내거나 스크린샷(PNG)으로 올려주세요." };
  if (t) return { ok: false, message: `${t.split("/")[1].toUpperCase()} 형식은 지원하지 않습니다. JPG 또는 PNG 로 올려주세요.` };
  return { ok: false, message: "이미지 파일이 아닙니다. JPG 또는 PNG 를 올려주세요." };
}

/** 추측할 수 없는 파일명으로 저장 (공개 주소로 노출되므로 목록·순서 추측 불가하게) */
export async function saveImage(buf: Uint8Array, mime: "image/jpeg" | "image/png"): Promise<string> {
  const name = `${randomBytes(24).toString("hex")}.${mime === "image/png" ? "png" : "jpg"}`;
  if (onWorkers) {
    await bucket().put(name, buf, { httpMetadata: { contentType: mime } });
    return name;
  }
  const dir = uploadDir();
  await mkdir(dir, { recursive: true });
  await writeFile(path.join(dir, name), buf);
  return name;
}

export const SAFE_NAME = /^[a-f0-9]{48}\.(png|jpg)$/;

export async function readImage(name: string): Promise<Buffer | null> {
  if (!SAFE_NAME.test(name)) return null;
  try {
    if (onWorkers) {
      const obj = await bucket().get(name);
      return obj ? Buffer.from(await obj.arrayBuffer()) : null;
    }
    return await readFile(path.join(uploadDir(), name));
  } catch {
    return null;
  }
}
