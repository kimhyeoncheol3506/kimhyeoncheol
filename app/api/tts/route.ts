// 목소리 낭독 API — 기본 목소리는 '여의도여자'(Qwen3-TTS 한국어 여성 목소리 'Sohee')
// 1) DASHSCOPE_API_KEY 가 있으면: 알리바바 Model Studio(싱가포르) qwen3-tts-flash, 목소리 Sohee = 여의도여자
//    (1만 자당 약 $0.1, 싱가포르 리전은 처음 무료 사용량 있음)
// 2) AZURE_SPEECH_KEY + AZURE_SPEECH_REGION 이 있으면: Azure 공식 API (한국어 여성 SunHi)
// 3) 둘 다 없거나 실패하면: Microsoft Edge '소리내어 읽기' (키 없이 무료, 한국어 여성 SunHi)
// 모두 실패하면 화면은 자동으로 브라우저 내장 목소리로 읽습니다.
import { MsEdgeTTS, OUTPUT_FORMAT } from "msedge-tts";

export const runtime = "nodejs";
export const maxDuration = 30;

const VOICE = process.env.TTS_VOICE || "ko-KR-SunHiNeural"; // Microsoft 쪽 보조 목소리 (여성)
const QWEN_VOICE = process.env.QWEN_TTS_VOICE || "Sohee"; // 여의도여자
const QWEN_MODEL = process.env.QWEN_TTS_MODEL || "qwen3-tts-flash";
const QWEN_BASE = process.env.DASHSCOPE_BASE_URL || "https://dashscope-intl.aliyuncs.com/api/v1";
const qwen = () => Boolean(process.env.DASHSCOPE_API_KEY);
const MAX_CHARS = 1200; // 한 번에 합성할 최대 글자 수 (남용 방지)
const disabled = () => process.env.TTS_PROVIDER === "off";
const azure = () => (process.env.AZURE_SPEECH_KEY && process.env.AZURE_SPEECH_REGION ? true : false);

const escapeXml = (s: string) =>
  s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&apos;");

/** 여의도여자 — Qwen3-TTS (알리바바 Model Studio). 한 번에 최대 600자, 결과는 WAV 파일 주소로 옵니다 */
async function synthQwen(text: string): Promise<ArrayBuffer> {
  const res = await fetch(`${QWEN_BASE}/services/aigc/multimodal-generation/generation`, {
    method: "POST",
    headers: { Authorization: `Bearer ${process.env.DASHSCOPE_API_KEY}`, "Content-Type": "application/json" },
    body: JSON.stringify({ model: QWEN_MODEL, input: { text: text.slice(0, 600), voice: QWEN_VOICE, language_type: "Korean" } }),
  });
  if (!res.ok) throw new Error(`qwen ${res.status} ${(await res.text()).slice(0, 200)}`);
  const j = (await res.json()) as { output?: { audio?: { url?: string } } };
  const url = j.output?.audio?.url;
  if (!url) throw new Error("qwen no audio url");
  const audio = await fetch(url);
  if (!audio.ok) throw new Error(`qwen audio ${audio.status}`);
  return audio.arrayBuffer();
}

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
  return Response.json({
    enabled: !disabled(),
    provider: qwen() ? "qwen" : azure() ? "azure" : "edge",
    voice: qwen() ? `여의도여자(${QWEN_VOICE})` : VOICE,
  });
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
    let audio: ArrayBuffer | Buffer | null = null;
    let type = "audio/mpeg";
    if (qwen()) {
      try {
        audio = await synthQwen(text);
        type = "audio/wav";
      } catch (e) {
        console.error("Qwen TTS error, falling back:", e);
      }
    }
    if (audio) {
      /* 여의도여자 성공 */
    } else if (azure()) {
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
      headers: { "Content-Type": type, "Cache-Control": "private, max-age=3600" },
    });
  } catch (e) {
    console.error("TTS error:", e);
    return new Response("tts failed", { status: 502 });
  }
}
