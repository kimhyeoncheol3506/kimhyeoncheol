import { NextResponse } from "next/server";
import { readImage, SAFE_NAME } from "@/lib/threads/storage";

/**
 * 게시용 이미지 공개 주소. Threads 서버가 로그인 없이 이 주소에서 이미지를 가져간다.
 * 파일명은 48자리 무작위 값이라 추측할 수 없고, 목록 조회 기능은 없다.
 */
export async function GET(_req: Request, { params }: { params: Promise<{ file: string }> }) {
  const { file } = await params;
  if (!SAFE_NAME.test(file)) return new NextResponse("Not found", { status: 404 });
  const buf = await readImage(file);
  if (!buf) return new NextResponse("Not found", { status: 404 });
  return new NextResponse(new Uint8Array(buf), {
    headers: {
      "Content-Type": file.endsWith(".png") ? "image/png" : "image/jpeg",
      "Cache-Control": "public, max-age=31536000, immutable",
      "X-Robots-Tag": "noindex",
    },
  });
}
