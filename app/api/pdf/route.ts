// 운명첩 PDF 만들기 (서버에서 Chromium으로 인쇄)
// - 사진과 생년월일은 받지 않습니다. 화면에 보이는 결과 문장만 받아 PDF로 만들고, 저장하지 않습니다.
// - Vercel 에서는 @sparticuz/chromium, 내 컴퓨터에서는 CHROME_PATH 의 크롬을 씁니다.
import { writeFile, unlink } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { randomUUID } from "node:crypto";
import { renderReport } from "@/lib/report/template";
import type { ResultPayload } from "@/lib/reading/types";

export const runtime = "nodejs";
export const maxDuration = 60;

async function launch() {
  const puppeteer = (await import("puppeteer-core")).default;
  if (process.env.CHROME_PATH) {
    return puppeteer.launch({ executablePath: process.env.CHROME_PATH, headless: true, args: ["--no-sandbox"] });
  }
  const chromium = (await import("@sparticuz/chromium")).default;
  return puppeteer.launch({
    args: await puppeteer.defaultArgs({ args: chromium.args, headless: "shell" }),
    executablePath: await chromium.executablePath(),
    headless: "shell",
  });
}

/** 개발용: 인터넷 없이 시험할 때 로컬 글꼴 폴더(@fontsource)를 쓰도록 */
function localFontHead() {
  const dir = process.env.PDF_LOCAL_FONTS_DIR;
  if (!dir) return undefined;
  return ["nanum-myeongjo/400", "nanum-myeongjo/700", "nanum-myeongjo/800", "noto-serif-kr/700", "noto-serif-kr/900", "nanum-brush-script/index", "song-myung/index"]
    .map((f) => `<link rel="stylesheet" href="file://${dir}/${f}.css">`)
    .join("");
}

export async function POST(req: Request) {
  const origin = req.headers.get("origin");
  const host = req.headers.get("host");
  if (origin && host && new URL(origin).host !== host) return new Response("forbidden", { status: 403 });

  const raw = await req.text();
  if (raw.length > 300_000) return new Response("too large", { status: 413 });
  let result: ResultPayload;
  let name: string | undefined;
  try {
    const body = JSON.parse(raw) as { result: ResultPayload; name?: string };
    result = body.result;
    name = body.name?.trim().slice(0, 20) || undefined;
    if (!result?.reading?.sections || !result?.saju?.pillars) throw new Error("bad");
  } catch {
    return new Response("bad request", { status: 400 });
  }

  const html = renderReport(result, { name, fontHead: localFontHead() });
  const file = join(tmpdir(), `report-${randomUUID()}.html`);
  let browser: Awaited<ReturnType<typeof launch>> | null = null;
  try {
    await writeFile(file, html, "utf8");
    browser = await launch();
    const page = await browser.newPage();
    await page.goto(`file://${file}`, { waitUntil: "networkidle0", timeout: 30_000 });
    await page.waitForSelector("body[data-ready]", { timeout: 20_000 });
    const pdf = await page.pdf({ format: "A4", printBackground: true, preferCSSPageSize: true });
    return new Response(new Uint8Array(pdf), {
      headers: {
        "Content-Type": "application/pdf",
        "Content-Disposition": `attachment; filename="myeongsangcheop.pdf"; filename*=UTF-8''${encodeURIComponent("운명첩.pdf")}`,
        "Cache-Control": "no-store",
      },
    });
  } catch (e) {
    console.error("PDF error:", e);
    return new Response("pdf failed", { status: 502 });
  } finally {
    await browser?.close().catch(() => {});
    await unlink(file).catch(() => {});
  }
}
