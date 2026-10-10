import type { Config } from "tailwindcss";

// 디자인 시스템: 흑백 + 포인트 컬러 1개 (나이키 스타일)
const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#0A0A0A", // 메인 검정
        paper: "#FFFFFF", // 메인 흰색
        mute: "#757575", // 보조 텍스트
        line: "#E5E5E5", // 구분선
        smoke: "#F5F5F5", // 옅은 배경
        accent: "#E11D48", // 포인트 컬러 (로즈 레드) — 한 화면에 한두 번만
      },
      fontFamily: {
        sans: ["Pretendard Variable", "Pretendard", "-apple-system", "system-ui", "sans-serif"],
      },
      fontSize: {
        // 큰 제목용 반응형 크기
        display: ["clamp(3rem, 11vw, 9.5rem)", { lineHeight: "0.92", letterSpacing: "-0.045em" }],
        headline: ["clamp(2.25rem, 6.5vw, 5rem)", { lineHeight: "1", letterSpacing: "-0.04em" }],
        title: ["clamp(1.75rem, 4vw, 2.75rem)", { lineHeight: "1.1", letterSpacing: "-0.03em" }],
      },
      letterSpacing: { label: "0.18em" },
      maxWidth: { page: "1440px" },
    },
  },
  plugins: [],
};
export default config;
