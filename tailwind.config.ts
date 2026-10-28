import type { Config } from "tailwindcss";

// 디자인 시스템: 토스 스타일 — 흰 배경, 진한 회색 글자, 포인트 청록 하나, 둥근 카드
const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#191F28", // 본문 글자
        sub: "#4E5968", // 보조 글자
        mute: "#8B95A1", // 흐린 글자
        line: "#E5E8EB", // 구분선
        smoke: "#F2F4F6", // 회색 배경·카드
        paper: "#FFFFFF",
        accent: "#06525C", // 포인트 청록 (한 화면에 한두 곳만)
        "accent-dark": "#043E46",
        "accent-soft": "#E3EEEC",
        warn: "#F04452",
      },
      fontFamily: {
        sans: ["Pretendard Variable", "Pretendard", "-apple-system", "system-ui", "sans-serif"],
      },
      fontSize: {
        display: ["32px", { lineHeight: "1.3", letterSpacing: "-0.02em" }],
        headline: ["26px", { lineHeight: "1.35", letterSpacing: "-0.02em" }],
        title: ["20px", { lineHeight: "1.4", letterSpacing: "-0.01em" }],
      },
      maxWidth: { app: "480px", page: "720px" },
      borderRadius: { card: "20px" },
    },
  },
  plugins: [],
};
export default config;
