"use client";
// AI 목소리 낭독. 기본은 브라우저 내장 Web Speech API (무료).
// 나중에 ElevenLabs 등을 붙이려면 TtsEngine 인터페이스를 구현한 클래스를 하나 더 만들면 됩니다.

export interface TtsEngine {
  readonly supported: boolean;
  speak(text: string, onEnd: () => void): void;
  stop(): void;
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
        voices.find((v) => /google|natural|neural|yuna|sora|heami|sunhi|injoon/i.test(v.name)) ?? voices[0] ?? null;
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
