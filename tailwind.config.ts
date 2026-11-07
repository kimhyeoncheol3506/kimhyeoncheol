import type { Config } from "tailwindcss";

// 디자인 시스템: 아이보리 & 골드 — 아이보리 배경, 먹색 글자, 샴페인 골드 포인트, 명조 제목
const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#1C1A17", // 본문 글자 (먹색)
        sub: "#4F4941", // 보조 글자
        mute: "#8E867A", // 흐린 글자
        line: "#E6DDCC", // 구분선
        smoke: "#FFFFFF", // 카드 배경
        paper: "#FAF6EE", // 페이지 배경 (아이보리)
        accent: "#A8823A", // 샴페인 골드
        "accent-dark": "#8C6A2C",
        "accent-soft": "#F3EAD7",
        gold: "#7F5F25",
        warn: "#C2493D",
      },
      fontFamily: {
        sans: ["Pretendard Variable", "Pretendard", "-apple-system", "system-ui", "sans-serif"],
        serif: ["Noto Serif KR", "Nanum Myeongjo", "serif"],
        display: ["Cormorant Garamond", "Noto Serif KR", "serif"],
      },
      fontSize: {
        display: ["34px", { lineHeight: "1.32", letterSpacing: "-0.02em" }],
        headline: ["26px", { lineHeight: "1.4", letterSpacing: "-0.02em" }],
        title: ["20px", { lineHeight: "1.45", letterSpacing: "-0.01em" }],
      },
      maxWidth: { app: "480px", page: "720px" },
      borderRadius: { card: "20px" },
    },
  },
  plugins: [],
};
export default config;