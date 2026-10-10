"use client";
// 목소리 낭독.
// - 기본: Microsoft 한국어 음성 'InJoon'으로 읽습니다 (서버 /api/tts 경유, 무료).
// - 오류가 나면 브라우저 내장 Web Speech API(무료)로 자동 전환합니다.

export interface TtsEngine {
  readonly supported: boolean;
  speak(text: string, onEnd: () => void): void;
  stop(): void;
  /** 다음 문단을 미리 준비 (선택) */
  prefetch?(text: string): void;
  /** 모바일에서 첫 터치 때 소리 재생 권한을 얻기 (선택) */
  unlock?(): void;
}

/** 문장들을 적당한 길이의 문단으로 묶기 (자연스러운 억양 + API 호출 횟수 절약) */
export function chunkSentences(sentences: string[], max = 280): string[] {
  const out: string[] = [];
  let cur = "";
  for (const s of sentences) {
    if (cur && (cur + " " + s).length > max) {
      out.push(cur);
      cur = s;
    } else cur = cur ? `${cur} ${s}` : s;
  }
  if (cur) out.push(cur);
  return out;
}

/** 문장 단위로 쪼개기 (자연스러운 끊어 읽기를 위해) */
export function splitSentences(text: string): string[] {
  return text
    .replace(/\s+/g, " ")
    .split(/(?<=[.!?…])\s+/)
    .map((s) => s.trim())
    .filter(Boolean);
}

/** 한자·기호를 소리 내 읽기 좋게 다듬기 */
export function speakable(s: string) {
  return s
    .replace(/\([^)]*[一-鿿][^)]*\)/g, "") // 한자가 든 괄호 제거
    .replace(/\([^)]*\)/g, "") // 괄호 속 근거 표기는 소리 내 읽지 않음
    .replace(/[一-鿿]+/g, "")
    .replace(/·/g, ", ")
    .replace(/—/g, ", ")
    .replace(/[‘’“”]/g, "")
    .replace(/\s+/g, " ")
    .trim();
}

export class WebSpeechEngine implements TtsEngine {
  private voice: SpeechSynthesisVoice | null = null;
  readonly supported = typeof window !== "undefined" && "speechSynthesis" in window;

  constructor() {
    if (!this.supported) return;
    const choose = () => {
      const voices = speechSynthesis.getVoices().filter((v) => v.lang.toLowerCase().startsWith("ko"));
      // 더 자연스러운 음성을 우선 선택
      this.voice =
        voices.find((v) => /injoon/i.test(v.name)) ??
        voices.find((v) => /google|natural|neural|yuna|sora|heami|sunhi/i.test(v.name)) ?? voices[0] ?? null;
    };
    choose();
    speechSynthesis.addEventListener?.("voiceschanged", choose);
  }

  speak(text: string, onEnd: () => void) {
    const u = new SpeechSynthesisUtterance(text);
    u.lang = "ko-KR";
    if (this.voice) u.voice = this.voice;
    u.rate = 0.98;
    u.pitch = 1;
    u.onend = onEnd;
    u.onerror = (e) => {
      if (e.error !== "interrupted" && e.error !== "canceled") onEnd();
    };
    speechSynthesis.speak(u);
  }

  stop() {
    if (this.supported) speechSynthesis.cancel();
  }
}

// 아주 짧은 무음 WAV (모바일 자동재생 잠금 해제용)
function silentWav() {
  const n = 800; // 0.1초 @ 8kHz
  const buf = new ArrayBuffer(44 + n);
  const v = new DataView(buf);
  const w = (o: number, t: string) => { for (let i = 0; i < t.length; i++) v.setUint8(o + i, t.charCodeAt(i)); };
  w(0, "RIFF"); v.setUint32(4, 36 + n, true); w(8, "WAVE"); w(12, "fmt ");
  v.setUint32(16, 16, true); v.setUint16(20, 1, true); v.setUint16(22, 1, true);
  v.setUint32(24, 8000, true); v.setUint32(28, 8000, true); v.setUint16(32, 1, true); v.setUint16(34, 8, true);
  w(36, "data"); v.setUint32(40, n, true);
  for (let i = 0; i < n; i++) v.setUint8(44 + i, 128);
  let bin = "";
  new Uint8Array(buf).forEach((b) => (bin += String.fromCharCode(b)));
  return `data:audio/wav;base64,${btoa(bin)}`;
}

export class ServerVoiceEngine implements TtsEngine {
  readonly supported = typeof window !== "undefined";
  private audio = typeof window !== "undefined" ? new Audio() : null;
  private cache = new Map<string, Promise<string>>();
  private fallback = new WebSpeechEngine();
  private failed = false;
  private token = 0;

  private load(text: string) {
    let p = this.cache.get(text);
    if (!p) {
      p = fetch("/api/tts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      }).then(async (r) => {
        if (!r.ok) throw new Error(`tts ${r.status}`);
        return URL.createObjectURL(await r.blob());
      });
      p.catch(() => this.cache.delete(text));
      this.cache.set(text, p);
    }
    return p;
  }

  prefetch(text: string) {
    if (!this.failed) this.load(text).catch(() => {});
  }

  unlock() {
    if (!this.audio) return;
    this.audio.src = silentWav();
    this.audio.play().catch(() => {});
  }

  speak(text: string, onEnd: () => void) {
    if (this.failed || !this.audio) return this.fallback.speak(text, onEnd);
    const my = ++this.token;
    const audio = this.audio;
    this.load(text)
      .then((url) => {
        if (my !== this.token) return;
        audio.onended = () => my === this.token && onEnd();
        audio.onerror = () => {
          // 재생이 안 되면 다음 문단으로 건너뛰지 말고 브라우저 목소리로 전환 (불필요한 API 호출 방지)
          if (my !== this.token) return;
          this.failed = true;
          this.fallback.speak(text, onEnd);
        };
        audio.src = url;
        return audio.play();
      })
      .catch(() => {
        // 서버 목소리 실패 시 브라우저 목소리로 전환
        if (my !== this.token) return;
        this.failed = true;
        this.fallback.speak(text, onEnd);
      });
  }

  stop() {
    this.token++;
    if (this.audio) {
      this.audio.onended = null;
      this.audio.pause();
    }
    this.fallback.stop();
  }
}

/** 서버 목소리(InJoon)가 켜져 있으면 그것을, 아니면 브라우저 목소리 */
export async function createEngine(): Promise<TtsEngine> {
  try {
    const r = await fetch("/api/tts");
    if (r.ok && ((await r.json()) as { enabled?: boolean }).enabled) return new ServerVoiceEngine();
  } catch {
    /* 무시 */
  }
  return new WebSpeechEngine();
}
