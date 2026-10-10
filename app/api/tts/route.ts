// 목소리 낭독 API — Microsoft 한국어 남성 음성 'InJoon'(ko-KR-InJoonNeural)
// 1) AZURE_SPEECH_KEY + AZURE_SPEECH_REGION 이 있으면: Azure 공식 API (무료 등급 F0 = 매월 50만 자 무료, 안정적)
// 2) 없으면: Microsoft Edge '소리내어 읽기' 서비스 (키 없이 무료, 단 비공식이라 예고 없이 막힐 수 있음)
// 어느 쪽이든 실패하면 화면은 자동으로 브라우저 내장 목소리로 읽습니다.
import { MsEdgeTTS, OUTPUT_FORMAT } from "msedge-tts";

export const runtime = "nodejs";
export const maxDuration = 30;

const VOICE = process.env.TTS_VOICE || "ko-KR-InJoonNeural";
const MAX_CHARS = 1200; // 한 번에 합성할 최대 글자 수 (남용 방지)
const disabled = () => process.env.TTS_PROVIDER === "off";
const azure = () => (process.env.AZURE_SPEECH_KEY && process.env.AZURE_SPEECH_REGION ? true : false);

const escapeXml = (s: string) =>
  s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&apos;");

/** Azure 공식 API */
async function synthAzure(text: string): Promise<ArrayBuffer> {
  const ssml = `<speak version="1.0" xml:lang="ko-KR"><voice name="${VOICE}"><prosody rate="-3%">${escapeXml(text)}</prosody></voice></speak>`;
  const res = await fetch(
    `https://${process.env.AZURE_SPEECH_REGION}.tts.speech.microsoft.com/cognitiveservices/v1`,
    {
      method: "POST",
      headers: {
        "Ocp-Apim-Subscription-Key": process.env.AZURE_SPEECH_KEY!,
        "Content-Type": "application/ssml+xml",
        "X-Microsoft-OutputFormat": "audio-24khz-48kbitrate-mono-mp3",
        "User-Agent": "fate-site",
      },
      body: ssml,
    },
  );
  if (!res.ok) throw new Error(`azure ${res.status} ${(await res.text()).slice(0, 200)}`);
  return res.arrayBuffer();
}

/** Microsoft Edge 소리내어 읽기 (무료·비공식) */
async function synthEdge(text: string): Promise<Buffer> {
  const tts = new MsEdgeTTS();
  try {
    await tts.setMetadata(VOICE, OUTPUT_FORMAT.AUDIO_24KHZ_48KBITRATE_MONO_MP3);
    const { audioStream } = tts.toStream(escapeXml(text), { rate: "-3%" });
    const chunks: Buffer[] = [];
    await new Promise<void>((resolve, reject) => {
      const timer = setTimeout(() => reject(new Error("edge timeout")), 20000);
      audioStream.on("data", (d: Buffer) => chunks.push(d));
      audioStream.on("close", () => {
        clearTimeout(timer);
        resolve();
      });
      audioStream.on("error", (e: Error) => {
        clearTimeout(timer);
        reject(e);
      });
    });
    const buf = Buffer.concat(chunks);
    if (!buf.length) throw new Error("edge empty audio");
    return buf;
  } finally {
    tts.close();
  }
}

export async function GET() {
  return Response.json({ enabled: !disabled(), provider: azure() ? "azure" : "edge", voice: VOICE });
}

export async function POST(req: Request) {
  if (disabled()) return Response.json({ enabled: false }, { status: 404 });

  // 다른 사이트에서 이 API를 몰래 쓰지 못하게 같은 사이트 요청만 허용
  const origin = req.headers.get("origin");
  const host = req.headers.get("host");
  if (origin && host && new URL(origin).host !== host) return new Response("forbidden", { status: 403 });

  let text = "";
  try {
    text = String(((await req.json()) as { text?: unknown }).text ?? "").trim();
  } catch {
    /* 아래에서 처리 */
  }
  if (!text) return new Response("empty", { status: 400 });
  if (text.length > MAX_CHARS) return new Response("too long", { status: 413 });

  try {
    let audio: ArrayBuffer | Buffer;
    if (azure()) {
      try {
        audio = await synthAzure(text);
      } catch (e) {
        console.error("Azure TTS error, trying Edge:", e);
        audio = await synthEdge(text);
      }
    } else {
      audio = await synthEdge(text);
    }
    return new Response(new Uint8Array(audio), {
      headers: { "Content-Type": "audio/mpeg", "Cache-Control": "private, max-age=3600" },
    });
  } catch (e) {
    console.error("TTS error:", e);
    return new Response("tts failed", { status: 502 });
  }
}
