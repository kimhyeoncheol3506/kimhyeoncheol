import type { Config } from "tailwindcss";

// 디자인 시스템: 다크 그린 사이드바 + 흰 카드. 포인트 색은 brand 하나만 씁니다.
const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: "#166534", // 버튼·링크
          dark: "#0B3B2E", // 사이드바 배경
          deep: "#072A20", // 사이드바 선택 항목
          soft: "#E7F5EC", // 옅은 강조 배경
          line: "#BFE3CC",
        },
        ink: "#111827", // 본문 글자
        sub: "#4B5563", // 보조 글자
        mute: "#9CA3AF", // 흐린 글자
        line: "#E5E7EB", // 구분선
        canvas: "#F6F8F7", // 페이지 배경
      },
      fontFamily: {
        sans: ["Pretendard Variable", "Pretendard", "-apple-system", "system-ui", "sans-serif"],
      },
      borderRadius: { card: "16px" },
    },
  },
  plugins: [],
};
export default config;
