// ElevenLabs 음성 합성 API (서버에서만 키를 사용합니다)
// - ELEVENLABS_API_KEY 가 없으면 { enabled: false } → 화면은 무료 브라우저 목소리로 읽습니다.
// - ELEVENLABS_VOICE_ID 가 없으면 내 계정의 목소리 중 한국어 목소리를 자동으로 고릅니다.
// - ELEVENLABS_MODEL 이 없으면 최신 모델(eleven_v4)부터 시도하고, 안 되면 v3 → multilingual_v2 로 자동 전환합니다.

export const runtime = "nodejs";
export const maxDuration = 30;

const API = process.env.ELEVENLABS_API_BASE || "https://api.elevenlabs.io/v1";
const MAX_CHARS = 1200; // 한 번에 합성할 최대 글자 수 (비용·남용 방지)

const key = () => process.env.ELEVENLABS_API_KEY;
const MODELS = () =>
  process.env.ELEVENLABS_MODEL ? [process.env.ELEVENLABS_MODEL] : ["eleven_v4", "eleven_v3", "eleven_multilingual_v2"];

let cachedVoice: string | null = null;
let workingModel: string | null = null;

type Voice = { voice_id: string; name: string; labels?: Record<string, string>; verified_languages?: { language?: string }[] };

/** 계정의 목소리 목록에서 한국어 목소리를 찾는다 */
async function pickVoice(): Promise<string> {
  if (process.env.ELEVENLABS_VOICE_ID) return process.env.ELEVENLABS_VOICE_ID;
  if (cachedVoice) return cachedVoice;
  const res = await fetch(`${API}/voices`, { headers: { "xi-api-key": key()! } });
  if (!res.ok) throw new Error(`voices ${res.status}`);
  const { voices = [] } = (await res.json()) as { voices?: Voice[] };
  const isKo = (v: Voice) =>
    /korean|ko\b|한국/i.test(JSON.stringify(v.labels ?? {})) ||
    (v.verified_languages ?? []).some((l) => l.language === "ko") ||
    /korean|한국/i.test(v.name);
  const voice = voices.find(isKo) ?? voices[0];
  if (!voice) throw new Error("no voices");
  cachedVoice = voice.voice_id;
  return cachedVoice;
}

export async function GET() {
  return Response.json({ enabled: Boolean(key()) });
}

export async function POST(req: Request) {
  if (!key()) return Response.json({ enabled: false }, { status: 404 });

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
    const voiceId = await pickVoice();
    const models = workingModel ? [workingModel] : MODELS();
    let last = "";
    for (const model of models) {
      for (const withLang of [true, false]) {
        const res = await fetch(`${API}/text-to-speech/${voiceId}?output_format=mp3_44100_128`, {
          method: "POST",
          headers: { "xi-api-key": key()!, "Content-Type": "application/json", Accept: "audio/mpeg" },
          body: JSON.stringify({
            text,
            model_id: model,
            ...(withLang ? { language_code: "ko" } : {}),
            voice_settings: { stability: 0.5, similarity_boost: 0.8, style: 0.2, use_speaker_boost: true },
          }),
        });
        if (res.ok) {
          workingModel = model;
          return new Response(res.body, {
            headers: { "Content-Type": "audio/mpeg", "Cache-Control": "private, max-age=3600" },
          });
        }
        last = `${model} ${res.status} ${(await res.text()).slice(0, 200)}`;
        // 인증·잔액 문제는 다른 모델로 바꿔도 소용없으니 바로 중단
        if (res.status === 401 || res.status === 402 || res.status === 429) throw new Error(last);
      }
    }
    throw new Error(last);
  } catch (e) {
    console.error("ElevenLabs TTS error:", e);
    return new Response("tts failed", { status: 502 });
  }
}
