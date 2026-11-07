import type { Config } from "tailwindcss";

// 디자인 시스템: 미드나잇 & 골드 — 깊은 밤색 배경, 아이보리 글자, 샴페인 골드 포인트, 명조 제목
const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#F2EBDD", // 본문 글자 (아이보리)
        sub: "#C4BBA9", // 보조 글자
        mute: "#8A8374", // 흐린 글자
        line: "#2C2A33", // 구분선
        smoke: "#16151C", // 카드 배경
        paper: "#0B0A0F", // 페이지 배경 (미드나잇)
        accent: "#D4B26A", // 샴페인 골드
        "accent-dark": "#B8964E",
        "accent-soft": "#221D14",
        gold: "#E9D3A0",
        warn: "#E58A7E",
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