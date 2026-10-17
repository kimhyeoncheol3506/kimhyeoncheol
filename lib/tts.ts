"use client";
// 목소리 낭독 엔진.
// - 기본: Microsoft 한국어 신경망 음성(남성 InJoon / 여성 SunHi)으로 읽습니다 (서버 /api/tts 경유, 무료).
// - 오류가 나면 브라우저 내장 Web Speech API(무료)로 자동 전환합니다.
// - 제목·요약·본문마다 말투(속도·높낮이)를 다르게 하고, 덩어리 사이에 쉼을 둡니다.
import type { Cue, CueKind } from "./narration";

export type VoiceId = "male" | "female";
export const VOICES: Record<VoiceId, { label: string; web: RegExp }> = {
  male: { label: "남성 목소리", web: /injoon|hyunsu|male|남/i },
  female: { label: "여성 목소리", web: /sunhi|yuna|sora|heami|female|여|google/i },
};

export interface TtsEngine {
  readonly supported: boolean;
  speak(cue: Cue, onEnd: () => void): void;
  stop(): void;
  prefetch?(cue: Cue): void;
  unlock?(): void;
  setVoice(v: VoiceId): void;
  setSpeed(x: number): void;
}

// 브라우저 목소리용 말투 (서버 목소리는 /api/tts 에서 같은 기준으로 처리)
const WEB_TONE: Record<CueKind, { rate: number; pitch: number }> = {
  title: { rate: 0.92, pitch: 0.95 },
  lead: { rate: 0.95, pitch: 1 },
  body: { rate: 0.98, pitch: 1 },
};

export class WebSpeechEngine implements TtsEngine {
  private voices: SpeechSynthesisVoice[] = [];
  private voiceId: VoiceId = "male";
  private speed = 1;
  readonly supported = typeof window !== "undefined" && "speechSynthesis" in window;

  constructor() {
    if (!this.supported) return;
    const load = () => (this.voices = speechSynthesis.getVoices().filter((v) => v.lang.toLowerCase().startsWith("ko")));
    load();
    speechSynthesis.addEventListener?.("voiceschanged", load);
  }
  setVoice(v: VoiceId) {
    this.voiceId = v;
  }
  setSpeed(x: number) {
    this.speed = x;
  }
  private pick() {
    const want = VOICES[this.voiceId].web;
    return this.voices.find((v) => want.test(v.name) && /natural|neural|online/i.test(v.name)) ?? this.voices.find((v) => want.test(v.name)) ?? this.voices[0] ?? null;
  }

  speak(cue: Cue, onEnd: () => void) {
    const u = new SpeechSynthesisUtterance(cue.text);
    u.lang = "ko-KR";
    const v = this.pick();
    if (v) u.voice = v;
    u.rate = WEB_TONE[cue.kind].rate * this.speed;
    u.pitch = WEB_TONE[cue.kind].pitch;
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
  private voiceId: VoiceId = "male";
  private speed = 1;

  setVoice(v: VoiceId) {
    this.voiceId = v;
    this.fallback.setVoice(v);
  }
  setSpeed(x: number) {
    this.speed = x;
    this.fallback.setSpeed(x);
    if (this.audio) this.audio.playbackRate = x;
  }

  private load(cue: Cue) {
    const key = `${this.voiceId}|${cue.kind}|${cue.text}`;
    let p = this.cache.get(key);
    if (!p) {
      p = fetch("/api/tts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: cue.text, kind: cue.kind, voice: this.voiceId }),
      }).then(async (r) => {
        if (!r.ok) throw new Error(`tts ${r.status}`);
        return URL.createObjectURL(await r.blob());
      });
      p.catch(() => this.cache.delete(key));
      this.cache.set(key, p);
    }
    return p;
  }

  prefetch(cue: Cue) {
    if (!this.failed) this.load(cue).catch(() => {});
  }

  unlock() {
    if (!this.audio) return;
    this.audio.src = silentWav();
    this.audio.play().catch(() => {});
  }

  speak(cue: Cue, onEnd: () => void) {
    if (this.failed || !this.audio) return this.fallback.speak(cue, onEnd);
    const my = ++this.token;
    const audio = this.audio;
    const toFallback = () => {
      if (my !== this.token) return;
      this.failed = true;
      this.fallback.speak(cue, onEnd);
    };
    this.load(cue)
      .then((url) => {
        if (my !== this.token) return;
        audio.onended = () => my === this.token && onEnd();
        audio.onerror = toFallback;
        audio.src = url;
        audio.playbackRate = this.speed;
        // @ts-expect-error 일부 브라우저 접두사 속성
        audio.preservesPitch = audio.webkitPreservesPitch = true;
        return audio.play();
      })
      .catch(toFallback);
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

/** 서버 목소리가 켜져 있으면 그것을, 아니면 브라우저 목소리 */
export async function createEngine(): Promise<TtsEngine> {
  try {
    const r = await fetch("/api/tts");
    if (r.ok && ((await r.json()) as { enabled?: boolean }).enabled) return new ServerVoiceEngine();
  } catch {
    /* 무시 */
  }
  return new WebSpeechEngine();
}
