import React from "react";
import { AbsoluteFill, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
// 테스트: 숫자 카운트업 + 막대 성장 (인포그래픽 장면 예시)
const font = `@font-face{font-family:PX;src:url(${staticFile("Pretendard-Bold.otf")})}`;
export const Hello: React.FC = () => {
  const f = useCurrentFrame(); const { fps } = useVideoConfig();
  const v = Math.round(interpolate(f, [15, 75], [10000, 5500], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }));
  const w = spring({ frame: f - 20, fps, config: { damping: 18 } });
  return (
    <AbsoluteFill style={{ background: "#0D0E11", color: "#F2EDE3", fontFamily: "PX", justifyContent: "center", alignItems: "center" }}>
      <style>{font}</style>
      <div style={{ fontSize: 60, color: "#D6B26E", letterSpacing: 8 }}>REMOTION TEST · 부시리</div>
      <div style={{ fontSize: 200, fontVariantNumeric: "tabular-nums" }}>{v.toLocaleString("en-US")}원</div>
      <div style={{ width: 1200, height: 30, background: "#ffffff15" }}><div style={{ width: `${55 * w}%`, height: "100%", background: "#5FB7A6" }} /></div>
    </AbsoluteFill>
  );
};
